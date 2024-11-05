import sys

sys.path.append("..")

def do_get(fileid, itemid, collection, milvus_client):
    if fileid is not None:
        return milvus_client.get(collection, "fileid in [%s]" % fileid)
    elif itemid is not None:
        return milvus_client.get(collection, "itemid in [%s]" % itemid)
    else:
        return None
