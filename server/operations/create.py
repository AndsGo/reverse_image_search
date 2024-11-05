import sys

sys.path.append("..")

def do_create(collection, milvus_client):
    try:
        milvus_client.create_collection(collection)
        milvus_client.create_index(collection)
    except Exception as e:
        raise e
