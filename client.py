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
        self.connections = connections.connect("default", host="localhost", port="19530")

        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1000)
        ]

        schema = CollectionSchema(fields, "VSearch Database")
        self.collection = Collection("VSearch", schema)

        index = {
            "index_type": "IVF_FLAT",
            "metric_type": "L2",
            "params": {"nlist": 128}
        }
        self.collection.create_index("vector", index)

    def insert(self, id, vector):
        data = [
            [id],
            [vector]
        ]

        self.collection.insert(data)

    def delete(self, id):
        pass

    def update(self, id, vector):
        pass

    def search(self, vector):
        pass

