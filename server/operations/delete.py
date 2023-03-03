import sys

sys.path.append("..")
from config import DEFAULT_TABLE


def do_delete(id, table_name, milvus_client, mysql_cli):
    if not table_name:
        table_name = DEFAULT_TABLE
    # 删除原有milvus 数据
    ms_data = mysql_cli.search_by_ids([id], table_name)
    if len(ms_data) == 0:
        raise Exception("id not exist")
    milvus_client.delete(table_name, "id in [%s]" % ms_data[0][1])
    mysql_cli.delete_by_id(table_name, id)
    return "ok"
