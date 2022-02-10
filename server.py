import os
import io
import uuid
import uvicorn
import torchvision
import numpy as np
from PIL import Image
from loguru import logger
from client import MilvusClient
from torchvision import transforms
from fastapi import FastAPI, Form, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


class SearchServiceServer(object):
    server: FastAPI = FastAPI(title="Search Service Server",
                              contact={
                                  "name": "Duy Huynh",
                                  "email": "vndee.huynh@gmail.com",
                              })

    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=["*"],
        allow_methods=["*"],
        allow_headers=["*"]
    )

    IMAGE_DIR = "static/"
    server.mount("/static", StaticFiles(directory=IMAGE_DIR), name="static")

    model = torchvision.models.resnet50(pretrained=True)

    functional_transforms = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize(224),
        transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))
    ])

    milvus_client = MilvusClient()

    @staticmethod
    @server.on_event("startup")
    async def startup_event():
        """
        SearchServiceServer start-up event
        :return:
        """

        SearchServiceServer.model.eval()
        logger.info("Search Service Server live now!!!")

        if not os.path.exists(SearchServiceServer.IMAGE_DIR):
            os.makedirs(SearchServiceServer.IMAGE_DIR)

    @staticmethod
    @server.get("/healthcheck/")
    async def healthcheck():
        logger.info("Healthcheck request: alive")
        return {
            "status": "alive"
        }

    @staticmethod
    @server.post("/index/")
    async def index(image: bytes = File(...),
                    id: str = Form(...)):
        logger.info(f"Received index request for item id: {id}")

        try:
            _uuid = uuid.uuid4().int & (1 << 32) - 1
            with open(os.path.join(SearchServiceServer.IMAGE_DIR, f"{_uuid}.jpg"), "wb+") as stream:
                stream.write(image)

            image = Image.open(io.BytesIO(image))
            image = SearchServiceServer.functional_transforms(image).unsqueeze(0)
            vector = SearchServiceServer.model(image).detach().numpy()
            vector = vector / np.linalg.norm(vector, axis=1)[:, None]

            SearchServiceServer.milvus_client.insert(int(id), vector[0], _uuid)

            return {
                "status": "success",
                "index_id": id
            }
        except Exception as ex:
            logger.exception(ex)
            return {
                "status": "error",
            }

    @staticmethod
    @server.post("/search/")
    async def search(image: bytes = File(...)):
        request_id = str(uuid.uuid4())
        logger.info(f"Received search request {request_id}")

        try:
            image = Image.open(io.BytesIO(image))
            image = SearchServiceServer.functional_transforms(image).unsqueeze(0)
            vector = SearchServiceServer.model(image).detach().numpy()
            vector = vector / np.linalg.norm(vector, axis=1)[:, None]
            results = SearchServiceServer.milvus_client.search(vector[0])

            results = [[x[0], x[1], f"static/{x[2]}.jpg"] for x in results]

            return {
                "status": "success",
                "results": results
            }
        except Exception as ex:
            logger.exception(ex)
            return {
                "status": "error",
            }

    @staticmethod
    @server.post("/update/")
    async def update(image: bytes = File(...),
                     id: str = Form(...)):
        logger.info(f"Received index request for item id: {id}")

        try:
            _uuid = uuid.uuid4().int & (1 << 32) - 1
            with open(os.path.join(SearchServiceServer.IMAGE_DIR, f"{_uuid}.jpg"), "wb+") as stream:
                stream.write(image)

            image = Image.open(io.BytesIO(image))
            image = SearchServiceServer.functional_transforms(image).unsqueeze(0)
            vector = SearchServiceServer.model(image).detach().numpy()
            vector = vector / np.linalg.norm(vector, axis=1)[:, None]

            SearchServiceServer.milvus_client.insert(int(id), vector[0], _uuid)

            return {
                "status": "success",
                "index_id": id
            }
        except Exception as ex:
            logger.exception(ex)
            return {
                "status": "error",
            }

    @staticmethod
    @server.get("/delete/")
    async def delete(id: str):
        request_id = str(uuid.uuid4())
        logger.info(f"Received delete request {request_id}")

        try:
            results = SearchServiceServer.milvus_client.delete(int(id))

            return {
                "status": "success",
                "results": results
            }
        except Exception as ex:
            logger.exception(ex)
            return {
                "status": "error",
            }

    @staticmethod
    def execute(host: str = "0.0.0.0", port: int = 8000):
        uvicorn.run(app=SearchServiceServer.server, host=host, port=port)


if __name__ == "__main__":
    instance = SearchServiceServer()
    instance.execute()
