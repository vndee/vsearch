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
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=1000)
    ]

    schema = CollectionSchema(fields, "VSearch Database")
    cursor = Collection("VSearch", schema)

    index = {
        "index_type": "IVF_FLAT",
        "metric_type": "L2",
        "params": { "nlist": 128 }
    }
    cursor.create_index("vector", index)

