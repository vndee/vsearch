FROM python:3.8-slim-buster


WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN apt update -y
RUN apt install -y git

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .