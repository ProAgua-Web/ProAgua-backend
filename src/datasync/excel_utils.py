import pandas as pd
import os

def obter_dados_excel(file_name = 'SI para PowerBi atualizada.xlsm', sheet_name = 'Banco de Dados'):
    address = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(address, file_name)
    pd.set_option('display.max_columns', None)
    df = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
    return df
