FROM python:3.8-alpine
MAINTAINER Galen Guyer <galen@galenguyer.com>

RUN apk add tzdata && \
    cp /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo 'America/New_York' > /etc/timezone && \
    apk del tzdata

WORKDIR /app

ADD requirements.txt /app

RUN pip install -r requirements.txt

ADD . /app

CMD ["gunicorn", "poller:APP", "--bind=0.0.0.0:8080", "--access-logfile=-"]
