import os
import django
import pandas as pd

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from datasync.excel_utils import obter_dados_excel, extract_digits

from proagua_api import models

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()


class Command(BaseCommand):
    help = 'Seed data for the application'

    def create_parametros_referencia(self):
        referencia, created = models.ParametrosReferencia.objects.get_or_create(
            min_temperatura=9.5,
            max_temperatura=10.5,
            min_cloro_residual_livre=0.2,
            max_cloro_residual_livre=5.0,
            max_turbidez=5.0
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                "Parâmetros de referência criados com sucesso."))
        else:
            self.stdout.write("Parâmetros de referência já existentes.")

    def create_edificacao(self, cronograma, codigo, nome, campus):
        if campus == 'Leste':
            campus = 'LE'
        elif campus == 'Oeste':
            campus = 'OE'
        codigo = codigo.strip() if codigo else codigo
        cronograma_str = str(cronograma)
        cronograma = extract_digits(cronograma_str)

        edificacao, created = models.Edificacao.objects.get_or_create(
            codigo=codigo,
            defaults={'cronograma': cronograma, 'nome': nome, 'campus': campus}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Edificação de código {codigo} criada com sucesso."))
        else:
            self.stdout.write(f"Dados já existentes para código {codigo}")
        return edificacao

    def create_ponto(self, tipo, localizacao, tombo, edificacao):
        tipo = 0 if 'bebedouro' in tipo else 1
        tombo = extract_digits(tombo)
        tombo = tombo.strip() if tombo else tombo
        localizacao = localizacao.strip() if localizacao else localizacao

        ponto, created = models.PontoColeta.objects.get_or_create(
            tipo=tipo,
            localizacao=localizacao,
            tombo=tombo,
            edificacao=edificacao
        )

        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Ponto de Coleta de tipo {tipo} e localização {localizacao} da edificação {edificacao} criado com sucesso."))
        else:
            self.stdout.write(
                f"Dados já existentes para ponto de coleta de tipo {tipo} e localização {localizacao} da edificação {edificacao}.")
        return ponto

    def create_responsavel(self, nome):
        DEFAULT_PASSWORD = '12345678'
        user, created = User.objects.get_or_create(
            username=nome, password=DEFAULT_PASSWORD, is_superuser=True)
        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Usuário {nome} criado com sucesso."))
        else:
            self.stdout.write(f"Usuário {nome} já existe.")
        return user

    def create_responsaveis(self, responsaveis):
        responsaveis_str = responsaveis
        if pd.notna(responsaveis_str) and responsaveis_str.lower() != 'nan':
            responsaveis = responsaveis_str.replace(
                ',', ' ').replace(' e ', ' ').replace('.', '')
            responsaveis = [responsavel.strip()
                            for responsavel in responsaveis.split()]
            responsaveis = [self.create_responsavel(
                responsavel) for responsavel in responsaveis]

            return responsaveis
        return []

    def create_sequencia(self, amostragem, ponto):
        amostragem = 1 if amostragem == 'Primeira' else 2

        sequencia, created = models.SequenciaColetas.objects.get_or_create(
            amostragem=amostragem, ponto=ponto)
        if created:
            self.stdout.write(self.style.SUCCESS(
                f"Sequência de amostragem {amostragem} criada com sucesso."))
        else:
            self.stdout.write(
                f"Sequência de amostragem {amostragem} já existe.")
        return sequencia

    def create_coleta(self, sequencia, ponto, responsaveis, temperatura, cloro_residual_livre, turbidez, coliformes_totais, escherichia, cor, data, ordem):
        coliformes_totais = True if coliformes_totais == 'PRESENÇA' else False
        escherichia = True if escherichia == 'PRESENÇA' else False

        coleta = models.Coleta.objects.create(
            sequencia=sequencia,
            ponto=ponto,
            temperatura=temperatura,
            cloro_residual_livre=cloro_residual_livre,
            turbidez=turbidez,
            coliformes_totais=coliformes_totais,
            escherichia=escherichia,
            cor=cor,
            data=data,
            ordem=ordem
        )
        coleta.responsavel.set(responsaveis)
        if coleta:
            self.stdout.write(self.style.SUCCESS(
                f"Coleta criada com sucesso: {coleta}"))
        else:
            self.stdout.write(self.style.ERROR("Erro ao criar coleta."))

    def seed_data(self):
        df = obter_dados_excel()

        referencia = self.create_parametros_referencia()

        for indice, linha in df.iloc[5:].iterrows():
            cronograma = linha.iloc[2]
            codigo = linha.iloc[3]
            nome = linha.iloc[4]
            campus = linha.iloc[5]

            edificacao = self.create_edificacao(
                cronograma, codigo, nome, campus)

            tipo = linha.iloc[6]
            localizacao = linha.iloc[7]
            tombo = linha.iloc[8]

            if pd.isna(tipo) or pd.isna(localizacao):
                continue
            ponto = self.create_ponto(tipo, localizacao, tombo, edificacao)

            amostragem = linha.iloc[0]

            sequencia = self.create_sequencia(amostragem, ponto)

            responsaveis = linha.iloc[11]
            responsaveis = self.create_responsaveis(responsaveis)

            data = linha.iloc[9]
            hora = linha.iloc[10]
            temperatura = linha.iloc[12]
            cloro_residual_livre = linha.iloc[13]
            turbidez = linha.iloc[14]
            coliformes_totais = linha.iloc[15]
            escherichia = linha.iloc[16]
            cor = linha.iloc[17]

            if pd.isna(data) or pd.isna(hora) or pd.isna(temperatura) or pd.isna(cloro_residual_livre) or pd.isna(turbidez) or pd.isna(coliformes_totais) or pd.isna(escherichia) or pd.isna(cor):
                continue

            coleta = self.create_coleta(
                sequencia,
                ponto,
                responsaveis,
                temperatura,
                cloro_residual_livre,
                turbidez,
                coliformes_totais,
                escherichia,
                cor,
                data,
                ordem=1
            )

    def handle(self, *args, **options):
        self.seed_data()
        self.stdout.write(self.style.SUCCESS(
            'Seed data created successfully.'))


if __name__ == '__main__':
    command = Command()
    command.handle()
