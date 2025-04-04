#!/bin/sh

echo "Running migrations..."

echo $(ls src)

python3 src/manage.py makemigrations
python3 src/manage.py makemigrations proagua_api
python3 src/manage.py migrate

echo "Starting server..."
python3 src/manage.py runserver 0.0.0.0:8000