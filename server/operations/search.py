import sys

sys.path.append("..")

def do_search(item, img_path, model, milvus_client):
    feat = model.resnet50_extract_feat(img_path)
    vectors = milvus_client.search_vectors(item, [feat])
    res = []
    if len(vectors[0]) == 0:
        return []
    vectors_dict = {}
    for hits in vectors:
        for hit in hits:
            data = {}
            data['distance'] = hit.distance

            data['fileid'] = hit.get("fileid")
            data['itemid'] = hit.get("itemid")
            data['tags'] = hit.get("tags")
            data['brief'] = hit.get("brief")
            res.append(data)
    return res
