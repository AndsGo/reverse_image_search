import os
import uuid
import rembg
from base64 import urlsafe_b64decode
from urllib.request import urlretrieve
from PIL import Image

def down_image(base64_image, url):
    """
    将图片下载获取本地地址
    :param base64_image: base64 image   不包含头信息
    :param url: https:
    :return:
    """
    upload_path = "/tmp"
    img_base = os.path.join(upload_path, uuid.uuid4().__str__()) 
    img_path = img_base + ".jpeg"
    img_path_r = img_base + ".r.jpeg"

    if base64_image is not None:
        if base64_image.startswith("data"):
            raise Exception('需要去掉头部如 data:image/jpg;base64,')
        with open(img_path, "wb+") as f:
            f.write(urlsafe_b64decode(base64_image))
    elif url is not None:
        urlretrieve(url, img_path)
    else:
        raise Exception('Image and url are required')
    # 图片去除背景,将图片变成固定尺寸
    resize_image(img_path,img_path_r,800,800)
    os.remove(img_path)
    return img_path_r

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

    # Calculate the coordinates to crop the center portion
    left = (resized_image.width- target_width) / 2
    top = (resized_image.height - target_height) / 2
    right = (resized_image.width + target_width) / 2
    bottom = (resized_image.height + target_height) / 2
    # Crop the image
    resized_image = resized_image.crop((left, top, right, bottom))
    # 去除背景
    resized_image = rembg.remove(resized_image)
    # 
    resized_image = resized_image.convert("RGB");
    # PNG
    resized_image.save(output_path, "JPEG", quality=95)
