from config import MILVUS_HOST, MILVUS_PORT, VECTOR_DIMENSION, METRIC_TYPE
from logs import LOGGER
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility

class MilvusHelper:
    """
    Say something about the ExampleCalass...

    Args:
        args_0 (`type`):
        ...
    """
    def __init__(self):
        try:
            self.collection = None
            connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
            LOGGER.debug(f"Successfully connect to Milvus with IP:{MILVUS_HOST} and PORT:{MILVUS_PORT}")
        except Exception as e:
            LOGGER.error(f"Failed to connect Milvus: {e}")
            # sys.exit(1)
            raise e

    def set_collection(self, collection_name):
        try:
            if self.has_collection(collection_name):
                self.collection = Collection(name=collection_name)
            else:
                raise Exception(f"There is no collection named:{collection_name}")
        except Exception as e:
            LOGGER.error(f"Failed to load data to Milvus: {e}")
            raise e

    def has_collection(self, collection_name):
        # Return if Milvus has the collection
        try:
            return utility.has_collection(collection_name)
        except Exception as e:
            LOGGER.error(f"Failed to load data to Milvus: {e}")
            raise e

    def create_collection(self, collection_name):
        # Create milvus collection if not exists
        try:
            if not self.has_collection(collection_name):
                fields = [
                        FieldSchema(name="fileid", dtype=DataType.INT64, descrition="int64", is_primary=True),
                        FieldSchema(name="vectors", dtype=DataType.FLOAT_VECTOR, descrition="float vector", dim=VECTOR_DIMENSION, is_primary=False),
                        FieldSchema(name="itemid", dtype=DataType.INT64),
                        FieldSchema(name="tags", dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=10, max_length=240),
                        FieldSchema(name="brief", dtype=DataType.JSON)
                        ]
                schema = CollectionSchema(fields, description="collection description")
                self.collection = Collection(name=collection_name, schema=schema)
                LOGGER.debug(f"Create Milvus collection: {collection_name}")
            else:
                self.set_collection(collection_name)
            return "OK"
        except Exception as e:
            LOGGER.error(f"Failed to load data to Milvus: {e}")
            raise e

    def insert(self, collection_name, vectors):
        # Batch insert vectors to milvus collection
        self.set_collection(collection_name)
        data = [vectors]
        mr = self.collection.upsert(data)
        ids = mr.primary_keys
        LOGGER.debug(f"Insert vectors to Milvus in collection: {collection_name} with {len(data)} rows")
        return ids[0]

    def update(self, collection_name, vectors, feat):
        # Batch update vectors to milvus collection
        self.set_collection(collection_name)
        data = self.collection.query(expr=("fileid=="+str(vectors['fileid'])), limit=1, output_fields=["fileid","itemid","tags","brief","vectors"])
        if len(data) == 0:
            return 0
        if vectors['tags'] is not None:
            data[0]['tags'] = vectors['tags']
        if vectors['itemid'] is not None:
            data[0]['itemid'] = vectors['itemid']
        if vectors['brief'] is not None:
            data[0]['brief'] = vectors['brief']
        if feat is not None:
            data[0]['vectors'] = feat

        mr = self.collection.upsert(data)
        ids = mr.primary_keys
        LOGGER.debug(f"Update Milvus in collection: {collection_name} with {len(data)} rows, data is{data}, pre data is{vectors}")
        return ids[0]

    def create_index(self, collection_name):
        # Create IVF_FLAT index on milvus collection
        try:
            self.set_collection(collection_name)
            if self.collection.has_index():
                return None
            default_index = {"index_type": "IVF_SQ8", "metric_type": METRIC_TYPE, "params": {"nlist": 16384}}
            self.collection.create_index(field_name="itemid")
            status = self.collection.create_index(field_name="vectors", index_params=default_index, timeout=60)
            if not status.code:
                LOGGER.debug(
                    f"Successfully create index in collection:{collection_name} with param:{default_index}")
                return status
            else:
                raise Exception(status.message)
        except Exception as e:
            LOGGER.error(f"Failed to create index: {e}")
            # sys.exit(1)
            raise e

    def delete_collection(self, collection_name):
        # Delete Milvus collection
        try:
            self.set_collection(collection_name)
            self.collection.drop()
            LOGGER.debug("Successfully drop collection!")
            return "ok"
        except Exception as e:
            LOGGER.error(f"Failed to drop collection: {e}")
            #  # sys.exit(1)
            raise e

    def search_vectors(self, item, vectors):
        # Search vector in milvus collection
        try:
            # NotExist = 0, NotLoad = 1, Loading = 2, Loaded = 3
            state = utility.load_state(collection_name=item.collection)
            if state == 1:
                LOGGER.debug(f"Collection not loaded and loading: {state}")
                self.collection.load()
                utility.wait_for_loading_complete(collection_name=item.collection);
                LOGGER.debug(f"Loaded collection")

            self.set_collection(item.collection)
            search_params = {"metric_type": METRIC_TYPE, "params": {"nprobe": 16}, "offset": item.offset}
            res = self.collection.search(vectors, anns_field="vectors", param=search_params, limit=item.limit, expr=item.filter, output_fields=["fileid","itemid","tags","brief"])
            LOGGER.debug(f"Successfully search in collection: {search_params}, {res}")
            return res
        except Exception as e:
            LOGGER.error(f"Failed to search vectors in Milvus: {e}")
            raise e


    def count(self, collection_name):
        # Get the number of milvus collection
        try:
            self.set_collection(collection_name)
            num = self.collection.num_entities
            LOGGER.debug(f"Successfully get the num:{num} of the collection:{collection_name}")
            return num
        except Exception as e:
            LOGGER.error(f"Failed to count vectors in Milvus: {e}")
            raise e

    def delete(self, collection_name, expr):
        # Get the number of milvus collection
        self.set_collection(collection_name)
        num = self.collection.delete(expr)
        LOGGER.info(f"Successfully delete the expr:{expr} of the collection:{collection_name}")
        return num

    def get(self, collection_name, expr):
        # Get the number of milvus collection
        self.set_collection(collection_name)
        data = self.collection.query(expr=expr, limit=1, output_fields=["fileid","itemid","tags","brief","vectors"])
        if len(data) == 0:
            return None
        return data[0]
