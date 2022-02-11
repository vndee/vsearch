
from pymilvus import (
    connections,
    utility,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
)


if __name__ == "__main__":
    connections = connections.connect("default", host="localhost", port="19530")

    cursor = Collection("VSearch")
    cursor.drop()

