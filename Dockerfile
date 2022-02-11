FROM python:3.8-slim-buster


WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

COPY requirements.txt requirements.txt
RUN apt update -y
RUN apt install -y git
RUN pip3 install -r requirements.txt

COPY . .