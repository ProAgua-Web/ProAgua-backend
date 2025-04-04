# Instalação local
Para instalar as bibliotecas necessárias, abra a pasta do projeto e execute o seguinte comando no terminal:

```sh
pip3 install -r requirements.txt
```

## Configuração
1. Instale o PostgreSQL v16.3 em sua máquina.
2. Crie um banco de dados chamado "proagua".
3. Crie um arquivo chamado ".env" na raiz do projeto e preencha as seguintes variáveis de ambiente:

```sh	
DB_NAME = 'proagua'
DB_HOST = ''
DB_PORT = ''
DB_USER = ''
DB_PASSWORD = ''
```

## Executar o servidor
Para garantir a integridade do Banco de Dados, execute o seguinte comando:
```sh
python3 src/manage.py config
```
Para iniciar o servidor, utilize o comando:
```sh
python3 src/manage.py runserver
```

## Limpar o Banco de Dados
Se precisar limpar o banco de dados, execute o seguinte comando:
```sh
python3 src/manage.py clear
```

## Criar superuser padrão
Se precisar criar um superuser padrão, execute o seguinte comando:
```sh
python3 src/manage.py createadmin
```

## Popular o Banco de Dados
Para popular o banco de dados com dados de teste, siga os passos abaixo:

Coloque o arquivo Excel "ProAgua SIMASP.xlsm" na pasta "src/datasync".

Execute um dos seguintes comandos:

Para apenas popular o banco de dados:

```sh
python3 src/manage.py seed
```
Para limpar e popular o banco de dados:

```sh
python3 src/manage.py rebuild
```

# Executar com docker
Antes de qualquer coisa, configure as variáveis de ambiente a partir do seguinte modelo:
```sh
DB_NAME = '<nome-do-db>'
DB_HOST = 'database' # Não alterar
DB_PORT = '5432'     # Porta padrão do postgresql
DB_USER = '<user-name>'
DB_PASSWORD = '<user-password>'
```

Para rodar o servidor usando docker basta executar os seguintes comandos:

Para criar os containeres:
```sh
docker compose up -d
```

Para popular o banco de dados:
```sh
docker exec -it proagua-backend python3 src/manage.py seed
```

Para criar um novo superuser:
```sh
docker exec -it proagua-backend python3 src/manage.py createsuperuser
```
