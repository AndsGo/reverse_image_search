"""
    数据库实体模型
"""


class MSDataModel:

    def __init__(self):
        self.id = None
        self.milvus_id = None
        # 标识
        self.tags = None
        self.brief = None
        self.feature = None

    def init(self, id, milvus_id, tags, brief):
        self.feature = id
        self.milvus_id = milvus_id
        self.tags = tags
        self.brief = brief

    def set_feature(self, feature):
        self.feature = feature

    def to_dict(self):
        d = {}
        if self.milvus_id is not None:
            d['milvus_id'] = self.milvus_id
        if self.brief is not None:
            d['brief'] = self.brief
        if self.tags is not None:
            d['tags'] = self.tags
        if self.feature is not None:
            d['feature'] = self.feature
        return d
