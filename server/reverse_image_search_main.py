# -*- coding: utf-8 -*-
# @file   : reverse_image_search_main.py
# @author : songxulin
# @date   : 2022:10:16 11:00:00
# @version: 1.0
# @desc   : 程序主入口
import os
from typing import Optional

import uvicorn
from config import UPLOAD_PATH
from encode import Resnet50
from fastapi import FastAPI
from logs import LOGGER
from milvus_helpers import MilvusHelper
from mysql_helpers import MySQLHelper
from operations.count import do_count
from operations.create import do_create
from operations.drop import do_drop
from operations.search import do_search
from operations.load import do_load
from operations.update import do_update
from operations.upload import do_upload
from operations.delete import do_delete
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from util import image_util

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)
MODEL = Resnet50()
MILVUS_CLI = MilvusHelper()
MYSQL_CLI = MySQLHelper()

# Mkdir '/tmp/search-images'
if not os.path.exists(UPLOAD_PATH):
    os.makedirs(UPLOAD_PATH)
    LOGGER.info(f"mkdir the path:{UPLOAD_PATH}")


class UploadImagesModel(BaseModel):
    id: Optional[int] = None
    # （data:image/jpg;base64,） （和url二选一，image优先级更高）
    image: Optional[str] = None
    url: Optional[str] = None
    # 标识
    tags: Optional[str] = ""
    brief: Optional[str] = ""
    table: Optional[str] = None

@app.post('/milvus/img/load')
async def load_images(table: str):
    # Insert the upload image to Milvus/MySQL
    try:
        do_create(table, MILVUS_CLI, MYSQL_CLI)
        # Save the upload image to server.
        ms_id = do_load(table , MILVUS_CLI, MYSQL_CLI)
        LOGGER.info(f"Successfully load_images data, vector id: {ms_id}")
        return {'code': 10000, 'message': 'Successfully', 'data': str(ms_id)}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}

@app.post('/milvus/img/add')
async def upload_images(imagesModel: UploadImagesModel):
    # Insert the upload image to Milvus/MySQL
    if not MILVUS_CLI.has_collection(imagesModel.table):
        return {'code': 10100, 'message': 'table does not exist, please call "/milvus/img/table" first'}
    try:
        # Save the upload image to server.
        img_path = image_util.down_image(imagesModel.image, imagesModel.url, UPLOAD_PATH)

        ms_id = do_upload(imagesModel, img_path, MODEL, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info(f"Successfully uploaded data, vector id: {ms_id}")
        return {'code': 10000, 'message': 'Successfully', 'data': str(ms_id)}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


@app.post('/milvus/img/update')
async def update_images(imagesModel: UploadImagesModel):
    # Insert the upload image to Milvus/MySQL
    if not MILVUS_CLI.has_collection(imagesModel.table):
        return {'code': 10100, 'message': 'table does not exist, please call "/milvus/img/table" first'}
    try:
        # Save the upload image to server.
        if imagesModel.id is None:
            return {'code': 10100, 'message': 'id are required'}

        img_path = image_util.down_image(imagesModel.image, imagesModel.url, UPLOAD_PATH)

        ms_id = do_update(imagesModel, img_path, MODEL, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info(f"Successfully uploaded data, vector id: {ms_id}")
        return {'code': 10000, 'message': 'Successfully', 'data': str(ms_id)}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


@app.post('/milvus/img/delete')
async def delete_images(id: int, table: str):
    # Insert the upload image to Milvus/MySQL
    if not MILVUS_CLI.has_collection(table):
        return {'code': 10100, 'message': 'table does not exist, please call "/milvus/img/table" first'}
    try:
        # Save the upload image to server.
        if id is None:
            return {'code': 10100, 'message': 'id are required'}

        ms_id = do_delete(id, table, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info(f"Successfully delete data,  id: {ms_id}")
        return {'code': 10000, 'message': 'Successfully'}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


class SearchItem(BaseModel):
    image: Optional[str] = None
    url: Optional[str] = None
    topk: Optional[int] = 10
    table: Optional[str] = None


@app.post('/milvus/img/search')
async def search_images(item: SearchItem):
    # Search the upload image in Milvus/MySQL
    if not MILVUS_CLI.has_collection(item.table):
        return {'code': 10100, 'message': 'table does not exist, please call "/milvus/img/table" first'}
    try:
        # Save the upload image to server.
        img_path = image_util.down_image(item.image, item.url, UPLOAD_PATH)
        paths = do_search(item.table, img_path, item.topk, MODEL, MILVUS_CLI, MYSQL_CLI)
        res = sorted(paths, key=lambda item: item['distance'])
        LOGGER.info("Successfully searched similar images!")
        return {'code': 10000, 'message': 'Successfully', 'data': res}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


@app.get('/milvus/img/count')
async def count_images(table: str):
    # Returns the total number of images in the system
    if not MILVUS_CLI.has_collection(table):
        return {'code': 10100, 'message': 'table does not exist, please call "/milvus/img/table" first'}
    try:
        num = do_count(table, MILVUS_CLI)
        LOGGER.info("Successfully count the number of images!")
        return {'code': 10000, 'message': 'Successfully', 'data': num}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


@app.post('/milvus/img/drop')
async def drop_tables(table: str):
    # Delete the collection of Milvus and MySQL
    if not MILVUS_CLI.has_collection(table):
        return {'code': 10100, 'message': 'table does not exist, please call "/milvus/img/table" first'}
    try:
        status = do_drop(table, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info("Successfully drop tables in Milvus and MySQL!")
        return {'code': 10000, 'message': 'Successfully', 'data': status}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}

@app.post('/milvus/img/table')
async def create_tables(table: str):
    # Delete the collection of Milvus and MySQL
    try:
        status = do_create(table, MILVUS_CLI, MYSQL_CLI)
        LOGGER.info("Successfully drop tables in Milvus and MySQL!")
        return {'code': 10000, 'message': 'Successfully', 'data': status}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}

if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=5000)
