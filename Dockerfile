FROM python:3.8-alpine
MAINTAINER Galen Guyer <galen@galenguyer.com>

RUN mkdir /opt/demo

ADD requirements.txt /opt/demo

WORKDIR /opt/demo

RUN pip install -r requirements.txt

ADD . /opt/demo

RUN ln -sf /usr/share/zoneinfo/America/New_York /etc/localtime

CMD ["gunicorn", "demo:APP", "--bind=0.0.0.0:8080", "--access-logfile=-"]
