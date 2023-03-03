# -*- coding: utf-8 -*-
# @file   : commen_util.py
# @author : songxulin
# @date   : 2022:06:20 14:00:00
# @version: 1.0
# @desc   : 公共方法util
import base64
import datetime
import pickle
import sys

sys.path.append('..')
from config import DATE_FORMAT

'''
    获取sql 执行时间取消
'''
def get_sql_time_interval(startTimeStr, MYSQL_CLI, days):
    startTime = datetime.datetime.strptime(startTimeStr, DATE_FORMAT)
    endTime = startTime + datetime.timedelta(days=days)
    dbNowStr = MYSQL_CLI.get_time_now()
    dbNow = datetime.datetime.strptime(dbNowStr[0], DATE_FORMAT)
    if endTime.timestamp() > dbNow.timestamp():
        endTime = dbNow
    return startTime, endTime

'''
    对象转 str
'''
def obj_encode(obj):
    return base64.b64encode(pickle.dumps(obj)).decode()

'''
    str 转对象
'''
def obj_decode(objStr):
    return pickle.loads(base64.b64decode(objStr))
