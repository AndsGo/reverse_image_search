import sys

sys.path.append("..")
from config import DEFAULT_TABLE


def do_create(table, milvus_client, mysql_cli):
    table_name = table
    if not table_name:
        table_name = DEFAULT_TABLE
    try:
        mysql_cli.create_mysql_table(table_name)
        milvus_client.create_collection(table_name)
        milvus_client.create_index(table_name)
    except Exception as e:
        raise e
