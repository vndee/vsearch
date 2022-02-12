import numpy as np
from loguru import logger
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)


class MilvusClient(object):
    def __init__(self):
        self.connections = connections.connect("default", host="milvus-standalone", port="19530")
        logger.info("Successfully create Milvus connection")

        fields = [
            FieldSchema(name="product_id", dtype=DataType.INT64),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1000),
            FieldSchema(name="uuid", dtype=DataType.INT64),
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        ]

        schema = CollectionSchema(fields, "VSearch Database")
        self.collection = Collection("VSearch", schema)

        index = {
            "index_type": "FLAT",
            "metric_type": "IP",
            "params": {"nlist": 128}
        }
        self.collection.create_index("vector", index)
        self.collection.load()

    def insert(self, id, vector, _uuid):
        data = [
            [id],
            [vector],
            [_uuid]
        ]

        ids = self.collection.insert(data)
        return ids

    def delete(self, id):
        search_param = {
            "data": [np.random.rand(1000)],
            "anns_field": "vector",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": 16}
            },
            "limit": 10
        }

        removed_ids = list()
        item = self.collection.search(**search_param, expr=f"product_id == {id}", output_fields=["product_id"])
        for i in range(len(item[0])):
            removed_ids.append(item[0][i].id)

        expr = "id in " + "[" + ", ".join([str(x) for x in removed_ids]) + "]"
        self.collection.delete(expr)

    def update(self, id, vector):
        pass

    def search(self, vector):
        _TOP_K = 10
        search_param = {
            "data": [vector],
            "anns_field": "vector",
            "param": {
                "metric_type": "IP",
                "params": {"nprobe": 16}
            },
            "limit": _TOP_K,
        }

        response = list()
        results = self.collection.search(**search_param, output_fields=["product_id", "uuid"])
        for i in range(min(_TOP_K, len(results[0]))):
            response.append([results[0][i].entity.product_id, results[0][i].distance, results[0][i].entity.uuid])

        return response
