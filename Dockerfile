FROM ubuntu:latest

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev && \
    apt-get install -y mysql-client

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD chmod +x ./wait-for-mysql.sh && ./wait-for-mysql.sh && python app.py