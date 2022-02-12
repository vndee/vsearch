FROM pytorch/pytorch:latest


WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"
ENV NO_CUDA=1

RUN apt update -y
RUN apt install -y git

RUN pip3 install numpy torchvision fastapi streamlit loguru uvicorn pymilvus Pillow python-multipart

COPY . .