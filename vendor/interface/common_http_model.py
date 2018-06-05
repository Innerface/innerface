# Author: YuYuE (1019303381@qq.com) 2018.01.25
import requests
import json


def get(url, para, headers):
    try:
        r = requests.get(url, params=para, headers=headers)
        json_r = r.json()
        result = {'code': r.status_code, 'data': json_r}
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


def post(url, para, headers):
    try:
        r = requests.post(url, data=para, headers=headers)
        json_r = r.json()
        result = {'code': r.status_code, 'data': json_r}
    except BaseException as error:
        raise Exception("Exception:", error)
    else:
        return result


def post_json(url, para, headers):
    try:
        data = para
        data = json.dumps(data)  # python数据类型转化为json数据类型
        r = requests.post(url, data=data, headers=headers)
        json_r = r.json()
        result = {'code': r.status_code, 'data': json_r}
    except BaseException as error:
        raise Exception("Exception:", error)
    else:
        return result
