import sys

sys.path.append("..")
from config import DEFAULT_TABLE
from util import commen_util


def do_load(table, milvus_client, mysql_cli):
    """
    循环调用上传
    :param table:
    :param milvus_client:
    :param mysql_cli:
    :return:
    """
    table_name = table
    if not table_name:
        table_name = DEFAULT_TABLE
    while True:
        do_load_once(table_name, milvus_client, mysql_cli)


def do_load_once(table_name, milvus_client, mysql_cli):
    """
    调用一次更新
    将特征更新到milvus中
    :param table_name:
    :param milvus_client:
    :param mysql_cli:
    :return:
    """
    #  0     1       2     3     4
    # id,milvus_id,tags,brief,feature
    ms_data = mysql_cli.search_by_update_status(table_name, 0, 100)
    if len(ms_data) == 0:
        raise Exception("ok")
    ids = []
    for item in ms_data:
        try:
            if item[1] is not None:
                milvus_client.delete(table_name, "id in [%s]" % item[1])
            feat = commen_util.obj_decode(item[4])
            ids = milvus_client.insert(table_name, [feat])
            mysql_cli.update_status(table_name, (ids[0], 1, item[0]))
        except Exception as e:
            if len(ids) > 0:
                milvus_client.delete(table_name, "id in [%s]" % ids[0])
            raise e
