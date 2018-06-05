# Author: YuYuE (1019303381@qq.com) 2018.03.16
import pickle
from chatbot.settings import PICKLE_DIR


def required_param():
    """
    聊天接口必要参数接口，暂时代码写死，后期方便改成配置
    :return:
    """
    return ['question', 'system_code', 'user_id', 'secret_key', 'customer_id']


def authorization(user_id):
    """
    授权校验部分，暂时写死授权，后期方便改成配置
    :return:
    """
    auths = {
        "001": {
            "system_code": "system",
            "secret_key": "yuyue"
        },
        "002": {
            "system_code": "system",
            "secret_key": "yuyue"
        }
    }
    if user_id in auths:
        return auths[user_id]
    else:
        return False


def param_filter(inp):
    """
    参数判断，缺少关键参数则直接过滤
    :param inp:
    :return: dic {
                "success":True,//返回码，是否操作成功
                "data":data
                "error":""//错误信息输出
                }
    """
    response = {
        "success": True,
        "data": inp,
        "error": ''
    }
    required_params = required_param()
    errors = []
    if required_params:
        for param in required_params:
            if param not in inp.keys():
                errors.append("param '" + param + "' is required")
    if errors:
        response['success'] = False
        response['error'] = ','.join(errors)
    return response


def auth_filter(inp):
    """
    授权校验
    :param inp:
    :return:
    """
    response = inp
    user_id = inp['data']['user_id']
    secret_key = inp['data']['secret_key']
    system_code = inp['data']['system_code']
    auths = authorization(user_id)
    if auths and secret_key == auths['secret_key'] and system_code == auths['system_code']:
        response['success'] = True
    else:
        response['success'] = False
        response['error'] = 'authorization failed,plz contact your mananger.'
    return response


def sensitive_filter(params):
    if 'data' in params:
        message = params['data']['question']
    else:
        message = ''
    for i in range(len(message)):
        f = open(PICKLE_DIR/"sensitive.pickle", "rb+")
        p = pickle.load(f)
        j = i
        while j < len(message) and p.children is not None and message[j] in p.children:
            p = p.children[message[j]]
            j = j + 1
        if p.badword == message[i:j]:
            # yield p.badword
            params['success'] = False
    return params


def black_list_filter(inp):
    return inp
