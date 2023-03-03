import os
import uuid
from base64 import urlsafe_b64decode
from urllib.request import urlretrieve

def down_image(base64_image, url, upload_path):
    """
    将图片下载获取本地地址
    :param base64_image: base64 image   不包含头信息
    :param url: https:
    :param upload_path: 上传地址目录
    :return:
    """
    if base64_image is not None:
        if base64_image.startswith("data"):
            raise Exception('需要去掉头部如 data:image/jpg;base64,')
        img_path = os.path.join(upload_path, uuid.uuid4().__str__())
        with open(img_path, "wb+") as f:
            f.write(urlsafe_b64decode(base64_image))
    elif url is not None:
        img_path = os.path.join(upload_path, os.path.basename(url))
        if not os.path.exists(img_path):
            img_path = os.path.join(upload_path, os.path.basename(url))
        urlretrieve(url, img_path)
    else:
        raise Exception('Image and url are required')

    return img_path
