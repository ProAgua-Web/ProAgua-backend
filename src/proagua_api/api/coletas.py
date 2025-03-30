from typing import List
from io import BytesIO
from io import StringIO

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import FileResponse
from ninja import Router, Query
import pandas as pd

from .exceptions.invalid_reference import InvalidReferenceException

from .schemas.coleta import *
from .schemas.usuario import UsuarioOut
from .schemas import ResponseSchema, PaginatedResponseSchema
from .. import models
from .pagination.pagination import paginate
from .pagination.custom_paginator import CustomPaginator
from .utils import response

router = Router(tags=["Coletas"])

@router.get("", response=PaginatedResponseSchema[ColetaOut])
@paginate(CustomPaginator)
def list_coleta(request, filter: Query[FilterColeta]) -> List[ColetaOut]:
    qs = models.Coleta.objects
    qs = qs.select_related("ponto", "ponto__edificacao")
    qs = qs.prefetch_related("ponto__imagens", "ponto__edificacao__imagens", "responsavel")
    qs = filter.filter(qs).order_by("data")
    return qs # type: ignore


@router.get("/csv")
def get_coletas_csv(request, filter: Query[FilterColeta]):
    coletas = filter.filter(models.Coleta.objects.all().order_by("data"))
    csv_headers = [
        "id", "temperatura", "cloro_residual_livre", "turbidez", "coliformes_totais",
        "escherichia", "cor", "data", "responsaveis", "ordem", "sequencia_id", "ponto_id"
    ]
    csv_file = StringIO()
    csv_file.write(",".join(csv_headers) + "\n")
    for coleta in coletas:
        csv_file.write(
            f"{coleta.id},{coleta.temperatura},{coleta.cloro_residual_livre},{coleta.turbidez},{coleta.coliformes_totais},{coleta.escherichia},{coleta.cor},{coleta.data},{'/'.join([str(r.username) for r in coleta.responsavel.all()])},{coleta.ordem},{coleta.sequencia.id},{coleta.ponto.id}\n"
        )
    csv_file.seek(0)
    return FileResponse(BytesIO(csv_file.getvalue().encode()), as_attachment=True, filename="coletas.csv")


@router.get("/excel")
def get_coletas_excel(request, filter: Query[FilterColeta]):
    coletas = filter.filter(models.Coleta.objects.all().order_by("data"))
    df = pd.DataFrame(list(coletas.values()))
    # Remove timezone information from the "data" column
    df["data"] = df["data"].dt.tz_localize(None)
    def rename(x): return "Presença" if x else "Ausência"
    df["escherichia"] = df["escherichia"].apply(rename)
    df["coliformes_totais"] = df["coliformes_totais"].apply(rename)

    df = df.rename(columns={
        "id": "ID",
        "temperatura": "Temperatura (°C)",
        "cloro_residual_livre": "Cloro Residual Livre (mg/L)",
        "turbidez": "Turbidez (uT)",
        "coliformes_totais": "Coliformes Totais (/100mL)",
        "escherichia": "Escherichia coli (/100mL)",
        "cor": "Cor Aparente (uH)",
        "data": "Data",
        "ordem": "Ordem",
        "sequencia_id": "ID Sequência",
        "ponto_id": "ID Ponto",
        "status": "Status",
        "status_message": "Mensagem de Status"
    })

    # Criar colunas de Edificacao

    df.insert(1, "Código da Edificação", "DEFAULT")
    df.insert(2, "Nome da Edificação", "DEFAULT")
    df.insert(3, "Campus", "DEFAULT")

    # Criar colunas de Ponto
    df.insert(4, "Tipo", "DEFAULT")
    df.insert(5, "Localização", "DEFAULT")
    df.insert(6, "Tombo", "DEFAULT")

    # Inserindo os valores correspondentes nas colunas criadas
    for index, row in df.iterrows():
        ponto = models.PontoColeta.objects.filter(id=row["ID Ponto"]).first()
        if ponto:
            edificacao = models.Edificacao.objects.filter(
                id=ponto.edificacao_id).first()
            if edificacao:
                df.at[index, "Código da Edificação"] = str(
                    edificacao.codigo)  # Explicitly convert to string
                df.at[index, "Nome da Edificação"] = str(
                    edificacao.nome)  # Explicitly convert to string
                df.at[index, "Campus"] = edificacao.campus
            df.at[index, "Tipo"] = ponto.get_tipo_display()
            df.at[index, "Localização"] = ponto.localizacao
            df.at[index, "Tombo"] = ponto.tombo

    # Renomeando campus
    def rename_campus(x): return "Leste" if str(
        x) == "LE" else "Oeste" if str(x) == "OE" else "Null"
    df["Campus"] = df["Campus"].apply(rename_campus)

    # Removendo as colunas ID Sequência e ID Ponto
    df = df.drop(columns=["ID Sequência", "ID Ponto",
                 "Status", "Mensagem de Status"])

    excel_file = BytesIO()
    writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
    df.to_excel(writer, sheet_name="Coletas", index=False)

    # Ajustando a largura das colunas
    for column in df:
        if column != "ID":
            column_min_width = 10
        else:
            column_min_width = 5
        column_length = max(df[column].astype(str).map(
            len).max(), len(column), column_min_width)
        col_idx = df.columns.get_loc(column)
        writer.sheets['Coletas'].set_column(col_idx, col_idx, column_length)

    writer.close()
    excel_file.seek(0)
    return FileResponse(excel_file, as_attachment=True, filename="coletas.xlsx")


@router.get("/{id_coleta}", response=ResponseSchema[ColetaOut])
def get_coleta(request, id_coleta: int):
    qs = get_object_or_404(models.Coleta, id=id_coleta)
    return response(data=qs)


@router.post("", response=ResponseSchema[ColetaOut])
def create_coleta(request, payload: ColetaIn):
    data_dict = payload.dict()
    responsavel_ids = data_dict.get("responsavel", [])

    # Removendo a lista de responsáveis do dicionário para criar a instância da Coleta
    del data_dict["responsavel"]

    sequencia = models.SequenciaColetas.objects.filter(pk=data_dict.get("sequencia_id")).first()

    # Verificar se a sequencia com id informado existe no banco de dados
    if sequencia is None:
        raise InvalidReferenceException(
            ref_name='Sequencia',
            ref_id=payload.sequencia_id, 
            field='sequencia_id'
        )
    
    data_dict["status"] = None
    data_dict["status_message"] = None

    # Criando a instância da Coleta sem os responsáveis
    coleta = models.Coleta.objects.create(**data_dict, sequencia=sequencia)

    # Use o método set para adicionar os responsáveis após a criação
    for responsavel_id in responsavel_ids:
        user = User.objects.filter(id=responsavel_id).first()
        if user:
            coleta.responsavel.add(user)

    return response(data=coleta)


@router.put("/{id_coleta}", response=ResponseSchema[ColetaOut])
def update_coleta(request, id_coleta: int, payload: ColetaIn):
    coleta = get_object_or_404(models.Coleta, id=id_coleta)
    data_dict = payload.dict()
    responsavel_ids = data_dict.get("responsavel", [])

    # Removendo a lista de responsáveis do dicionário
    del data_dict["responsavel"]

    # Iterando sobre os campos no payload e atualizar os valores correspondentes na instância
    for attr, value in data_dict.items():
        setattr(coleta, attr, value)

    # Atualizando os responsáveis
    coleta.responsavel.clear()
    for responsavel_id in responsavel_ids:
        user = User.objects.filter(id=responsavel_id).first()
        if user:
            coleta.responsavel.add(user)

    coleta.save()

    return response(data=coleta)


@router.delete("/{id_coleta}", response=ResponseSchema[ColetaOut])
def delete_coleta(request, id_coleta: int):
    obj_coleta = get_object_or_404(models.Coleta, id=id_coleta)
    obj_coleta.delete()
    return response(data=obj_coleta, errors=[])


@router.get("/{id_coleta}/responsaveis", response=List[UsuarioOut])
def get_responsaveis_coleta(request, id_coleta: int):
    coleta = get_object_or_404(models.Coleta, id=id_coleta)
    return response(data=coleta.responsavel)
