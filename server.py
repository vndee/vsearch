import io
import uuid
import uvicorn
import torchvision
from PIL import Image
from loguru import logger
from client import MilvusClient
from torchvision import transforms
from fastapi import FastAPI, Form, File
from fastapi.middleware.cors import CORSMiddleware


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
            image = Image.open(io.BytesIO(image))
            image = SearchServiceServer.functional_transforms(image).unsqueeze(0)
            vector = SearchServiceServer.model(image).detach().numpy()

            SearchServiceServer.milvus_client.insert(int(id), vector[0])

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

        vector = SearchServiceServer.model(image)
        print(vector.shape)

    @staticmethod
    @server.post("/update/")
    async def update(id: str = Form(...),
                     image: bytes = File(...)):
        pass

    @staticmethod
    @server.get("/delete/")
    async def delete(id: str):
        pass

    @staticmethod
    def execute(host: str = "0.0.0.0", port: int = 8000):
        uvicorn.run(app=SearchServiceServer.server, host=host, port=port)


if __name__ == "__main__":
    instance = SearchServiceServer()
    instance.execute()
