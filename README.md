## 更新列表
**2024/09/01**
1. 支持gpu计算
2. 复用model，提升性能，降低内存占用，避免加载model时候的网络响应
3. 图片宽高设置为800*800
4. 优化load逻辑，只有查询的时候才需要加载

**2024/08/17** 
1. 取消mysql的依赖，数据全存在milvus里
2. 图片增加支持fileid和itemid，支持itemid有多张图片
3. 搜索增加分页和过滤选项k

**2023/12/20** 增加 图片去除背景，图片转换为448*448尺寸

## 以图搜图服务快速搭建

如果只需要获取图片的向量值，另外存储的话，可以用这个 https://github.com/hetao29/image_to_vector

电商公司，管理的商品少则几千，多则上百万。如何帮助用户从多如牛毛的商品中找到类似的商品就成了问题。

以图搜图就可以很好的帮助解决这个问题，通过 Towhee（resnet50 模型） + Milvus 如何实现本地环境搭建以图搜图。

Towhee 负责解析图片的特征向量，Milvus 负责存储特征向量然后进行向量查询。

Milvus Bootcamp 提供了很多解决方案 ，https://milvus.io/bootcamp/
![在这里插入图片描述](https://img-blog.csdnimg.cn/7d17e8ee1ab6484886aa10bb5759c9a9.png#pic_center)

其中就包含以图搜图的解决方案，根据图片相视度解决方案demo，这里实现了比较时候适合公司前后的分离环境的开箱即用的api实现。

配合前端大致效果如下：
![在这里插入图片描述](https://img-blog.csdnimg.cn/a390800e3db64143855d139183fcc1fa.png#pic_center)

包含如下接口

## API接口

### 1.创建集合

不同集合对应不同的图片数据集合，类似数据库中的“表”的概念

#### Request

- Method: **POST**
- URL:  ```/milvus/collection/create?collection={collectionname}```
- Headers：

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully",
    "data": null
}
```



### 2.新增或替换图片

根据fileid新增图片，支持 base64 和url，相同fileid已经在，则会替换数据

参数说明：
* collection string 必须，集合，类似mysql中的表，add前请先创建
* fileid int 必须，主键，如果milvus里存在相同的值，则再次Add会完全覆盖
* itemid int 可选，物品ID,一个物品ID可以包含多张图片(fileid),搜索的时候，会过滤重复的
* image string base64的图片数据，和url二选一，image优先级更高
* url string 
* tags Array 可选，自定义标签，可以用于filter
* brief Dict 可选，自定义属性，可以用于filter

#### Request

- Method: **POST**
- URL:  ```/milvus/img/add```
- Headers: Content-Type:application/json
- Body:

```json
{
 "collection": "test",
 "fileid":0,
 "itemid":0,
 "image": "base64数据"
 "url":"http:///xxx.jpp",
 "tags": ["String"],
 "brief":{},
}
```

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully",
    "data": 8, //返回fileid"
}
```

### 3.部分更新图片或其它字段信息

根据fileid，更新图片(支持 base64 和url)，itemid，tags，brief

注意：可选字段如果不传，则不会更新数据，保留之前的

参数说明：
* collection string 必须，集合，类似mysql中的表，add前请先创建
* fileid int 必须，主键，如果更新时，fileid不存在，则会返回0
* itemid int 可选，是否更新itemid
* image/url string 可选，是否更新图片矢量信息(详细说明见上面的add参数说明)
* tags Array 可选
* brief Dict 可选

#### Request

- Method: **POST**
- URL:  ```/milvus/img/update```
- Headers: Content-Type:application/json
- Body:

```json
{
 "collection": "test",
 "fileid":0,
 "itemid":0,
 "image": "base64数据",
 "url":"http:///xxx.jpp",
 "tags": ["String"],
 "brief":{},
}
```

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully",
    "data": 8 //返回fileid"
}
```

### 4.以图搜图

根据图片搜索相似图片

#### Request

- Method: **POST**
- URL:  ```/milvus/img/search```
- Headers: Content-Type:application/json
- Body:

```json
{
 "collection": "test",//必须
 "limit": 10,//int，可选，默认10
 "offset":20,//int，可选，默认0
 "url": "https://img.kakaclo.com/image%2FFSZW09057%2FFSZW09057_R_S_NUB%2F336bd601dfec33925ba1c581908b6c1e.jpg",
 "image": "base64（和url二选一，image优先级更高） ",
 "filter":"",//string 过滤条件，用于tags和brief的filter，见 https://milvus.io/docs/boolean.md",
}
```

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully",
    "data": [
        {
            "fileid": 513552,
            "itemid": 513552,
            "tags": [],
            "brief": {},
            "distance": 0.00015275638725142926
        },
    ]
}
```

distance 越小相似度越高。

### 4.获取单个数据

根据fileid或者itemid获取单个图片的相关数据，包括向量数据

#### Request

- Method: **POST**
- URL:  ```/milvus/img/get```
- Headers: Content-Type:application/json
- Body:

```json
{
 "collection": "test",
 "fileid":0,
 "itemid":0
}
```

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully",
    "data": [
        {
            "fileid": 513552,
            "itemid": 513552,
            "tags": [],
            "brief": {},
            "vectors": {},
        },
    ]
}
```


### 6.计算总数


#### Request

- Method: **POST**
- URL:  ```/milvus/img/count?collection={collection}```
- Headers: 
- Body:

#### Response

- Body

```json
{
	"code": 10000,
	"message": "Successfully",
	"data": 3
}
```

### 7.删除图片

根据fileid删除

#### Request

- Method: **POST**
- URL:  ```/milvus/img/delete?fileid={fileid}&collection={collection}```
- Headers: 
- Body:

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully"
}
```

### 8.删除整个数据集

删除milvus集合，这个接口慎用，数据会全部清除。

#### Request

- Method: **POST**
- URL:  ```/milvus/collection/drop?collection={collection}```
- Headers: 
- Body:

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully"
}
```

## 快速实践


### 安装Miluvs

首先安装 Miluvs ，可以参考 https://milvus.io/docs/v2.1.x/install_standalone-docker.md

### 安装本系统

可以参考 https://github.com/hetao29/reverse-image-search 进行Docker部署安装

### 源码

https://github.com/AndsGo/reverse_image_search

### 配置

找到config.py

替换对应的 MILVUS 配置

```python
import os

############### Milvus Configuration ###############
MILVUS_HOST = os.getenv("MILVUS_HOST", "127.0.0.1")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "2048"))
METRIC_TYPE = os.getenv("METRIC_TYPE", "L2")

```

### 启动

```
sh start_server.sh
```
### Attu

https://milvus.io/docs/attu.md

Attu是 Milvus 的高效开源管理工具，提供了GUI显示

![img](https://img-blog.csdnimg.cn/img_convert/bca9a38acd70b62831ebd8453c32447a.png)
原文: https://blog.csdn.net/AndCo/article/details/129316873?spm=1001.2014.3001.5501

更多文章可以关注 **海鸥技术部落**公众号
