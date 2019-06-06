FROM python:3

LABEL maintainer="FastoGT Maintainers <support@fastogt.com>"

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

EXPOSE 8080
CMD [ "python", "server.py" ]
