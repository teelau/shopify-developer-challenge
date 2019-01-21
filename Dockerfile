FROM ubuntu:latest


ADD waitForMySQL.sh /root/
RUN chmod +x /root/waitForMySQL.sh

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

RUN flake8 --ignore E501

ENTRYPOINT [ "python" ]

CMD [ "app.py" ]