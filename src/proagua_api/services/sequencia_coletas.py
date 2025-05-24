def write_message(qs, parametros):
    # Primeiro, busque todos os objetos no queryset sem o annotate
    qs = list(qs) 

    min_turbidez = parametros.min_turbidez if parametros.min_turbidez else float('-inf')
    max_turbidez = parametros.max_turbidez if parametros.max_turbidez else float('inf')

    min_cloro_residual_livre = parametros.min_cloro_residual_livre if parametros.min_cloro_residual_livre else float('-inf')
    max_cloro_residual_livre = parametros.max_cloro_residual_livre if parametros.max_cloro_residual_livre else float('inf')

    # Itera sobre cada item do queryset e cria as mensagens manualmente
    for item in qs:
        if item.ultima_coleta is not None:
            # Verifica e cria a mensagem de turbidez
            if item.ultima_coleta_turbidez > max_turbidez:
                item.mensagem_turbidez = f"Turbidez está {item.ultima_coleta_turbidez - parametros.max_turbidez} uT acima do limite máximo"
            elif item.ultima_coleta_turbidez < min_turbidez:
                item.mensagem_turbidez = f"Turbidez está {parametros.min_turbidez - item.ultima_coleta_turbidez} uT abaixo do limite mínimo"
            else:
                item.mensagem_turbidez = ""
            
            # Verifica e cria a mensagem de cloro
            if item.ultima_coleta_cloro > max_cloro_residual_livre:
                item.mensagem_cloro = f"Cloro está {item.ultima_coleta_cloro - parametros.max_cloro_residual_livre} acima do limite máximo"
            elif item.ultima_coleta_cloro < min_cloro_residual_livre:
                item.mensagem_cloro = f"Cloro está {parametros.min_cloro_residual_livre - item.ultima_coleta_cloro} abaixo do limite mínimo"
            else:
                item.mensagem_cloro = ""

            # Verifica e cria a mensagem para coliformes
            if item.ultima_coleta_coliformes:
                item.mensagem_coliformes = "Presença de coliformes"    
            else:
                item.mensagem_coliformes = ""

            # Verifica e cria a mensagem para escherichia coli
            if item.ultima_coleta_escherichia:
                item.mensagem_escherichia = "Presença de escherichia coli"
            else:
                item.mensagem_escherichia = ""
        else:
            item.mensagem_turbidez = ""
            item.mensagem_cloro = ""
            item.mensagem_coliformes = ""
            item.mensagem_escherichia = ""

        # Compondo a mensagem final de status
        if item.quantidade_coletas == 0:
            item.status_message = "Não há coletas registradas para esta sequência."
        elif (
            not item.status_turbidez
            or not item.status_cloro
            or item.ultima_coleta_escherichia
            or item.ultima_coleta_coliformes
        ):
            item.status_message = ". ".join(
                filter(None, [
                    item.mensagem_turbidez,
                    item.mensagem_cloro,
                    item.mensagem_coliformes,
                    item.mensagem_escherichia
                ])
            )
        else:
            item.status_message = "Todos os parâmetros estão dentro dos limites."
    
    return qs


def set_status(qs, parametros):
    # Primeiro, busque todos os objetos no queryset sem o annotate
    qs = list(qs)  # Converte o queryset para uma lista para processar individualmente.

    min_turbidez = parametros.min_turbidez if parametros.min_turbidez else float('-inf')
    max_turbidez = parametros.max_turbidez if parametros.max_turbidez else float('inf')

    min_cloro_residual_livre = parametros.min_cloro_residual_livre if parametros.min_cloro_residual_livre else float('-inf')
    max_cloro_residual_livre = parametros.max_cloro_residual_livre if parametros.max_cloro_residual_livre else float('inf')

    # Itera sobre cada item do queryset e define os campos de status manualmente
    for item in qs:
        item.status_turbidez = None
        item.status_cloro = None

        if item.ultima_coleta is not None:
            # Verifica o status de turbidez
            item.status_turbidez = min_turbidez <= item.ultima_coleta_turbidez <= max_turbidez

            # Verifica o status de cloro
            item.status_cloro = min_cloro_residual_livre <= item.ultima_coleta_cloro <= max_cloro_residual_livre

            # Verifica o status geral (True se todas as condições forem atendidas)
            item.status = (
                item.status_turbidez
                and item.status_cloro
                and not item.ultima_coleta_escherichia
                and not item.ultima_coleta_coliformes
            )
        else:
            item.status = None
    
    return qs
