import sys
import json

sys.path.append("..")

def do_upload(uploadImagesModel, img_path, model, milvus_client):
    """
    解析图片特征并入口
    :param uploadImagesModel:
    :param img_path:
    :param model:
    :param milvus_client:
    :return:
    """
    feat = model.resnet50_extract_feat(img_path)
    record = {
            'vectors': feat,
            'fileid': uploadImagesModel.fileid,
            'itemid': uploadImagesModel.itemid,
            'tags': uploadImagesModel.tags,
            'brief': uploadImagesModel.brief,
            }
    if uploadImagesModel.tags is None:
        record['tags'] = []
    if uploadImagesModel.brief is None:
        record['brief'] = {}
            
    try:
        return milvus_client.insert(uploadImagesModel.collection, record)
    except Exception as e:
        raise e
