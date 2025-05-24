
def checar_limite(valor, minimo, maximo, nome, unidade=""):
    if valor is None:
        return "", True  # Considera como válido se não há valor

    if maximo is not None and valor > maximo:
        return f"{nome} acima do limite ({valor} > {maximo}{unidade})", False
    if minimo is not None and valor < minimo:
        return f"{nome} abaixo do limite ({valor} < {minimo}{unidade})", False
    return "", True


def avaliar_registro(item, parametros):
    if not item.ultima_coleta:
        item.status = False
        item.status_message = "Registro sem coleta recente."
        return item

    mensagens = []
    status_geral = True

    # Avaliação dos parâmetros
    turbidez_msg, ok_turbidez = checar_limite(
        item.ultima_coleta_turbidez,
        parametros.min_turbidez,
        parametros.max_turbidez,
        "Turbidez",
        " uT"
    )
    cloro_msg, ok_cloro = checar_limite(
        item.ultima_coleta_cloro,
        parametros.min_cloro_residual_livre,
        parametros.max_cloro_residual_livre,
        "Cloro residual livre"
    )

    if turbidez_msg:
        mensagens.append(turbidez_msg)
    if cloro_msg:
        mensagens.append(cloro_msg)

    if item.ultima_coleta_coliformes:
        mensagens.append("Presença de coliformes")
        status_geral = False

    if item.ultima_coleta_escherichia:
        mensagens.append("Presença de Escherichia coli")
        status_geral = False

    if not ok_turbidez or not ok_cloro:
        status_geral = False

    item.status = status_geral

    if item.quantidade_coletas == 0:
        item.status_message = "Não há coletas registradas para esta sequência."
    elif not status_geral:
        item.status_message = ". ".join(mensagens)
    else:
        item.status_message = "Todos os parâmetros estão dentro dos limites."

    return item


def avaliar_lista(qs, parametros):
    qs = list(qs)
    return [avaliar_registro(item, parametros) for item in qs]
