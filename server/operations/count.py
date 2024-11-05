import sys

sys.path.append("..")
from logs import LOGGER
def do_count(collection, milvus_cli):
    try:
        if not milvus_cli.has_collection(collection):
            return None
        return milvus_cli.count(collection)
    except Exception as e:
        LOGGER.error(f"Error with count collection {e}")
        raise e
