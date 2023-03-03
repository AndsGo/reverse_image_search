## 以图搜图服务快速搭建

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

### 1.创建数据库

不同数据库对应不同的图片数据集合

#### Request

- Method: **POST**
- URL:  ```/milvus/img/table?table={tablename}```
  - 创建test数据集:  ```/milvus/img/table?table=test```
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



### 2.新增图片

新增图片支持 base64 和url新增

#### Request

- Method: **POST**
- URL:  ```/milvus/img/add```
  - test 数据集新增图片数据:  ```/milvus/img/add```
- Headers: Content-Type:application/json
- Body:

```json
{
	"tags": "风景|标签",
	"table": "test",
    "brief":"{\"title\":\"hello world\"} 这里存一些属性",
	"image": "base64（和url二选一，image优先级更高） ",
    "url":"http:///xxx.jpp"
}
```

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully",
    "data": "8  返回数据id"
}
```

### 3.更新图片

更新图片支持 base64 和url，根据id进行更新

#### Request

- Method: **POST**
- URL:  ```/milvus/img/update```
- Headers: Content-Type:application/json
- Body:

```json
{
    "id":"1 必填",
	"tags": "风景|标签",
	"table": "test",
    "brief":"{\"title\":\"hello world\"} 这里存一些属性",
	"image": "base64（和url二选一，image优先级更高） ",
    "url":"http:///xxx.jpp"
}
```

#### Response

- Body

```json
{
    "code": 10000,
    "message": "Successfully",
    "data": "8  返回数据id"
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
	"TOP_K": "2 查询多少个相似图",
	"table": "test",
	"url": "https://img.kakaclo.com/image%2FFSZW09057%2FFSZW09057_R_S_NUB%2F336bd601dfec33925ba1c581908b6c1e.jpg",
    "image": "base64（和url二选一，image优先级更高） ",
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
            "id": 513552,
            "tags": "",
            "brief": "",
            "distance": 0.00015275638725142926
        },
        {
            "id": 93,
            "tags": "",
            "brief": "",
            "distance": 0.0001584545971127227
        }
    ]
}
```

distance 越小相似度越高。

### 5.删除图片

根据id删除

#### Request

- Method: **POST**
- URL:  ```/milvus/img/delete?id={id}&table={table}```
  - 删除test表id为6的数据  ```/milvus/img/delete?id=6&table=test```
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

### 6.删除整个数据集

删除milvus的和mysql的表，这个接口慎用，mysql和milvus数据会全部清除。

#### Request

- Method: **POST**
- URL:  ```/milvus/img/drop?table={table}```
  - 删除test数据集：  ```/milvus/img/drop?table=test```
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

### 7.重新加载已经解析出特征的数据到milvus

这个在milvus升级、迁移和milvus数据损坏的情况下使用

可以将数据集对应的mysql表upload_status更新为0进行重新入milvus。

#### Request

- Method: **POST**
- URL:  ```/milvus/img/load?table={table}```
  - 将test mysql笔中upload_status为0的数据重新加载到milvus中：  ```/milvus/img/load??table=test```
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

### 环境安装

首先我们先有如下环境 python3，mysql，Milvus 

python3，mysql就不多说了

Milvus  参考 https://milvus.io/docs/v2.1.x/install_standalone-docker.md

### 源码

https://github.com/AndsGo/reverse_image_search

### 配置

找到config.py

替换对应的 MILVUS 配置T 和 MYSQL配置

```python
import os

############### Milvus Configuration ###############
MILVUS_HOST = os.getenv("MILVUS_HOST", "127.0.0.1")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "2048"))
INDEX_FILE_SIZE = int(os.getenv("INDEX_FILE_SIZE", "1024"))
METRIC_TYPE = os.getenv("METRIC_TYPE", "L2")
DEFAULT_TABLE = os.getenv("DEFAULT_TABLE", "milvus_img_search")
TOP_K = int(os.getenv("TOP_K", "10"))

############### MySQL Configuration ###############
MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PWD = os.getenv("MYSQL_PWD", "123456")
MYSQL_DB = os.getenv("MYSQL_DB", "milvus")
ERP_MYSQL_TABLE = os.getenv("ERP_MYSQL_TABLE", "milvus_img_search")

############### Data Path ###############
UPLOAD_PATH = os.getenv("UPLOAD_PATH", "tmp/search-images")

DATE_FORMAT = os.getenv("DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

############### Number of log files ###############
LOGS_NUM = int(os.getenv("logs_num", "0"))

```

数据库表结构 ，表是自动生成的

```sql
CREATE TABLE `test` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `milvus_id` bigint(20) DEFAULT NULL COMMENT 'milvus 数据id',
  `tags` varchar(32) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '标识',
  `brief` varchar(500) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '图片摘要',
  `upload_status` tinyint(2) DEFAULT '0' COMMENT '0 待上传到milvus 1成功上传到milvus',
  `feature` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin COMMENT '图片特征向量',
  `create_date` datetime(3) DEFAULT CURRENT_TIMESTAMP(3) COMMENT '创建时间',
  `modify_date` datetime(3) DEFAULT CURRENT_TIMESTAMP(3) ON UPDATE CURRENT_TIMESTAMP(3) COMMENT '修改时间',
  PRIMARY KEY (`id`),
  KEY `idx_tags` (`tags`) USING BTREE,
  KEY `idx_milvus_id` (`milvus_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='图片上传记录表';
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
