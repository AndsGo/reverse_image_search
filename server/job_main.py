import sys

from logs import LOGGER
from milvus_helpers import MilvusHelper
from mysql_helpers import MySQLHelper
from operations.load import do_load,do_load_once

MILVUS_CLI = MilvusHelper()
MYSQL_CLI = MySQLHelper()


def load_images(table: str):
    if table is None:
        return "table is null"
    # Insert the upload image to Milvus/MySQL
    try:
        # Save the upload image to server.
        do_load(table, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info(f"Successfully load_images all ok")
        return {'code': 10000, 'message': 'Successfully'}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


if __name__ == '__main__':
    if len(sys.argv) > 1:
        table = sys.argv[1]
        if MILVUS_CLI.has_collection(table):
            if len(sys.argv) > 2:
                print(load_images(table=table))
            elif MILVUS_CLI.has_collection(table):
                print(do_load_once(table, MILVUS_CLI, MYSQL_CLI))
        else:
            print("table 不存在")
    else:
        print("缺少参数")
