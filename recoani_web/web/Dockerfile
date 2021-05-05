FROM python:3.8-alpine
RUN apk --no-cache add gcc g++ build-base linux-headers \
  libxml2-dev libxslt-dev mariadb-dev musl-dev nodejs
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY . /code/
