FROM python:3

WORKDIR /app

COPY requirements.txt ./

RUN pip install --upgrade pip &&\
    pip install -r requirements.txt

COPY ./src/ ./src/
COPY .env entrypoint.sh ./
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT [ "/app/entrypoint.sh" ]
