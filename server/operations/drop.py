import sys

sys.path.append("..")
from config import DEFAULT_TABLE


def do_drop(table_name, milvus_cli, mysql_cli):
    if not table_name:
        table_name = DEFAULT_TABLE
    if not milvus_cli.has_collection(table_name):
        return f"Milvus doesn't have a collection named {table_name}"
    status = milvus_cli.delete_collection(table_name)
    mysql_cli.delete_table(table_name)
    return status
