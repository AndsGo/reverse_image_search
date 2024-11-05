import sys

sys.path.append("..")

def do_drop(collection, milvus_cli):
    if not milvus_cli.has_collection(collection):
        return f"Milvus doesn't have a collection named {collection}"
    status = milvus_cli.delete_collection(collection)
    return status
