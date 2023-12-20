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
    # 图片去除背景,将图片变成固定尺寸
    image_url_r = img_path+"_r"
    resize_image(img_path,image_url_r,448,448)
    # os.remove(img_path)
    return image_url_r

import rembg

def remove_bg(input_image_path,output_image_path):
    """
    去除图片背景
    :param input_image_path: 输入图片地址
    :param output_image_path: 输出图片地址
    :return:
    """
    with open(input_image_path, 'rb') as i:
        with open(output_image_path, 'wb') as o:
            input = i.read()
            output = rembg.remove(input)
            o.write(output) 

from PIL import Image

# 将图片缩放到指定的画布中，不对原有的图片进行缩放
# max_width 最大宽度
# max_height 最大高度
# 将图片转换为宽高比  7.5:10 10：7.5
def resize_image(input_path:str, output_path:str, max_width:int, max_height:int):
    # Open the image file
    original_image = Image.open(input_path)
    # Get the dimensions of the original image
    original_width, original_height = original_image.size
    if (original_width>original_height):
        target_width = max_width
        target_height= max_height
        # target_height = int(max_height*0.75)
        # 10:7.5 宽度大于高度
    else:
        # target_width = int(max_width*0.75)
        target_width = max_width
        target_height = max_height
        # 7.5:10 高度大于宽度
    scaleW = target_width/original_width
    scaleH = target_height/original_height
    # 获取缩放比例
    scale = scaleW if scaleW<scaleH else scaleH
    # Resize the image without stretching
    resized_image = original_image.resize(
        (int(original_image.width * scale), int(original_image.height * scale))
    )

    # # Calculate scaling factors
    # scale_x = target_width / original_image.width
    # scale_y = target_height / original_image.height

    # Calculate the coordinates to crop the center portion
    left = (resized_image.width- target_width) / 2
    top = (resized_image.height - target_height) / 2
    right = (resized_image.width + target_width) / 2
    bottom = (resized_image.height + target_height) / 2

    # Crop the image
    resized_image = resized_image.crop((left, top, right, bottom))
    # 去除背景
    resized_image = rembg.remove(resized_image)
    # resized_image = Image.open(io.BytesIO(output))
     # Convert the image to JPEG format
    resized_image = resized_image.convert("RGB")

    # Save the result as a JPEG image
    resized_image.save(output_path, "JPEG")
