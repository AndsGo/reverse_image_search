import sys

sys.path.append("..")
from config import DEFAULT_TABLE
from util import commen_util

def do_update(uploadImagesModel, img_path, model, milvus_client, mysql_cli):
    table_name = uploadImagesModel.table
    if not table_name:
        table_name = DEFAULT_TABLE
    # 删除原有milvus 数据
    ms_data = mysql_cli.search_by_ids( [uploadImagesModel.id],table_name)
    if len(ms_data) == 0:
        raise Exception("id not exist")
    milvus_client.delete(table_name, "id in [%s]" % ms_data[0][1])

    feat = model.resnet50_extract_feat(img_path)
    ids = milvus_client.insert(table_name, [feat])
    # milvus_client.create_index(table_name)

    try:
        # mysql_cli.create_mysql_table(table_name)
        return mysql_cli.update(table_name, (ids[0], uploadImagesModel.tags, uploadImagesModel.brief,commen_util.obj_encode(feat),uploadImagesModel.id))
    except Exception as e:
        milvus_client.delete(table_name, "id in [%s]" % ids[0])
        raise e
