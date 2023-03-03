import sys

sys.path.append("..")
from config import DEFAULT_TABLE


def do_search(table_name, img_path, top_k, model, milvus_client, mysql_cli):
    if not table_name:
        table_name = DEFAULT_TABLE
    feat = model.resnet50_extract_feat(img_path)
    vectors = milvus_client.search_vectors(table_name, [feat], top_k)
    res = []
    if len(vectors[0]) == 0:
        return []
    vectors_dict = {}
    for x in vectors[0]:
        vectors_dict[x.id] = x.distance
    paths = mysql_cli.search_by_milvus_ids(list(vectors_dict.keys()), table_name)

    for i in range(len(paths)):
        data = {}
        data['id'] = paths[i][0]
        data['tags'] = paths[i][2]
        data['brief'] = paths[i][3]
        data['distance'] = vectors_dict.get(int(paths[i][1]))
        res.append(data)
    return res
