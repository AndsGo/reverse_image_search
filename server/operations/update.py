import sys
import json

sys.path.append("..")

def do_update(uploadImagesModel, img_path, model, milvus_client):

    feat = None
    if img_path is not None:
        feat = model.resnet50_extract_feat(img_path)

    record = {
            'fileid': uploadImagesModel.fileid,
            'itemid': uploadImagesModel.itemid,
            'tags': uploadImagesModel.tags,
            'brief': uploadImagesModel.brief,
            }
    try:
        return milvus_client.update(uploadImagesModel.collection, record, feat)
    except Exception as e:
        raise e
