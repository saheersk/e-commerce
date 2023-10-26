FROM python:3.8-buster

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /fashion

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .