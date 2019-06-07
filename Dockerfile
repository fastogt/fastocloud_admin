FROM python:3

LABEL maintainer="Alexandr Topilski <support@fastogt.com>"

COPY . /app
COPY docker/db_config.py /app/app/config/
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8080
CMD [ "python", "server.py" ]
