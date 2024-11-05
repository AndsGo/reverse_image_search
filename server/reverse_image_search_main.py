# -*- coding: utf-8 -*-
# @file   : reverse_image_search_main.py
# @author : songxulin
# @date   : 2022:10:16 11:00:00
# @version: 1.0
# @desc   : 程序主入口
import os
import json
from typing import Optional, List, Optional, Any

import uvicorn
from encode import Resnet50
from fastapi import FastAPI
from logs import LOGGER
from milvus_helpers import MilvusHelper
from operations.count import do_count
from operations.create import do_create
from operations.drop import do_drop
from operations.get import do_get
from operations.search import do_search
from operations.update import do_update
from operations.upload import do_upload
from operations.delete import do_delete
from pydantic import BaseModel, Json
from starlette.middleware.cors import CORSMiddleware
from util import image_util
from fastapi import Response

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

class UploadImagesModel(BaseModel):
    collection: str
    fileid: int
    itemid: int
    # （data:image/jpg;base64,） （和url二选一，image优先级更高）
    image: Optional[str] = ""
    url: Optional[str] = ""
    # 标识
    tags : Optional[List[str]] = None
    brief : Optional[Json[Any]] = None

@app.post('/milvus/img/add')
async def upload_images(imagesModel: UploadImagesModel):
    # Insert the upload image to Milvus
    if not MILVUS_CLI.has_collection(imagesModel.collection):
        return {'code': 10100, 'message': 'collection does not exist, please call "/milvus/img/collection" first'}
    try:
        # Save the upload image to server.
        img_path = image_util.down_image(imagesModel.image, imagesModel.url)

        ms_id = do_upload(imagesModel, img_path, MODEL, MILVUS_CLI)
        LOGGER.info(f"Successfully uploaded data, vector fileid: {ms_id}")
        return {'code': 10000, 'message': 'Successfully', 'data': str(ms_id)}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


class UpdateImagesModel(BaseModel):
    collection: str
    fileid: int
    itemid: Optional[int] = None
    # （data:image/jpg;base64,） （和url二选一，image优先级更高）
    image: Optional[str] = None
    url: Optional[str] = None
    # 标识
    tags : Optional[List[str]] = None
    brief : Optional[Json[Any]] = None

@app.post('/milvus/img/update')
async def update_images(imagesModel: UpdateImagesModel):
    # Update the image to Milvus
    if not MILVUS_CLI.has_collection(imagesModel.collection):
        return {'code': 10100, 'message': 'collection does not exist, please call "/milvus/img/collection" first'}
    try:
        # Save the upload image to server.
        if imagesModel.fileid is None:
            return {'code': 10100, 'message': 'fileid are required'}

        img_path = None
        if (imagesModel.image is not None ) or (imagesModel.url is not None):
            img_path = image_util.down_image(imagesModel.image, imagesModel.url)

        ms_id = do_update(imagesModel, img_path, MODEL, MILVUS_CLI)
        LOGGER.info(f"Successfully updated data, vector fileid: {ms_id}")
        return {'code': 10000, 'message': 'Successfully', 'data': str(ms_id)}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


@app.post('/milvus/img/delete')
async def delete_images(fileid: int, collection: str):
    # Delete the upload image
    if not MILVUS_CLI.has_collection(collection):
        return {'code': 10100, 'message': 'collection does not exist, please call "/milvus/img/collection" first'}
    try:
        # Save the upload image to server.
        if fileid is None:
            return {'code': 10100, 'message': 'fileid are required'}

        ms_id = do_delete(fileid, collection, MILVUS_CLI)
        LOGGER.info(f"Successfully delete data,  fileid: {ms_id}")
        return {'code': 10000, 'message': 'Successfully'}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


class GetModel(BaseModel):
    collection: str
    fileid: Optional[int] = None
    itemid: Optional[int] = None
@app.post('/milvus/img/get')
async def get_images(getModel: GetModel):
    # Delete the upload image
    if not MILVUS_CLI.has_collection(getModel.collection):
        return {'code': 10100, 'message': 'collection does not exist, please call "/milvus/img/collection" first'}
    try:
        # Save the upload image to server.
        if ((getModel.fileid is None) and (getModel.itemid is None)):
            return {'code': 10100, 'message': 'fileid or itemid are required'}

        hit = do_get(getModel.fileid, getModel.itemid, getModel.collection, MILVUS_CLI)
        if hit is None:
            return {'code': 10100, 'message': 'Failed to get vector'}

        LOGGER.info(f"Successfully get data,  fileid: {getModel.fileid}")
        d={'code': 10000, 'message': 'Successfully', 'data': hit}
        json_str = json.dumps(d, indent=4, default=str)
        return Response(content=json_str, media_type='application/json')
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}

class SearchItem(BaseModel):
    collection: str
    image: Optional[str] = None
    url: Optional[str] = None
    limit: Optional[int] = 10
    offset: Optional[int] = 0
    filter: Optional[str] = None


@app.post('/milvus/img/search')
async def search_images(item: SearchItem):
    # Search the upload image in Milvus
    if not MILVUS_CLI.has_collection(item.collection):
        return {'code': 10100, 'message': 'collection does not exist, please call "/milvus/img/collection" first'}
    try:
        # Save the upload image to server.
        img_path = image_util.down_image(item.image, item.url)
        paths = do_search(item, img_path, MODEL, MILVUS_CLI)
        res = sorted(paths, key=lambda item: item['distance'])
        LOGGER.info(f"Successfully searched similar images!,{res}")
        d={'code': 10000, 'message': 'Successfully', 'data': res}
        json_str = json.dumps(d, indent=4, default=str)
        return Response(content=json_str, media_type='application/json')
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


@app.get('/milvus/img/count')
async def count_images(collection: str):
    # Returns the total number of images in the system
    if not MILVUS_CLI.has_collection(collection):
        return {'code': 10100, 'message': 'collection does not exist, please call "/milvus/img/collection" first'}
    try:
        num = do_count(collection, MILVUS_CLI)
        LOGGER.info("Successfully count the number of images!")
        return {'code': 10000, 'message': 'Successfully', 'data': num}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}


@app.post('/milvus/collection/drop')
async def drop_collection(collection: str):
    # Delete the collection of Milvus
    if not MILVUS_CLI.has_collection(collection):
        return {'code': 10100, 'message': 'collection does not exist, please call "/milvus/img/collection" first'}
    try:
        status = do_drop(collection, MILVUS_CLI)
        LOGGER.info("Successfully drop collections in Milvus!")
        return {'code': 10000, 'message': 'Successfully', 'data': status}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}

@app.post('/milvus/collection/create')
async def create_collection(collection: str):
    # Create the collection of Milvus
    if MILVUS_CLI.has_collection(collection):
        LOGGER.info("Failed create exists collection in Milvus!")
        return {'code': 10100, 'message': 'Failed'}
    try:
        status = do_create(collection, MILVUS_CLI)
        LOGGER.info("Successfully create collection in Milvus!")
        return {'code': 10000, 'message': 'Successfully'}
    except Exception as e:
        LOGGER.error(e)
        return {'code': 10100, 'message': str(e)}

if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=5000)
