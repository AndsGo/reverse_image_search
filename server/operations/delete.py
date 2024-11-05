import sys

sys.path.append("..")

def do_delete(fileid, collection, milvus_client):
    milvus_client.delete(collection, "fileid in [%s]" % fileid)
    return "ok"
