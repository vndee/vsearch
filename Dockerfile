FROM python:3.8-slim-buster


WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

RUN apt update -y
RUN apt install -y git

RUN pip3 install numpy torch torchvision fastapi streamlit loguru uvicorn pymilvus Pillow

COPY . .