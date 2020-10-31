FROM python:3.8-alpine
MAINTAINER Galen Guyer <galen@galenguyer.com>

RUN mkdir /app

ADD requirements.txt /app

WORKDIR /app

RUN pip install -r requirements.txt

ADD . /app

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["gunicorn", "poller:APP", "--bind=0.0.0.0:8080", "--access-logfile=-"]
