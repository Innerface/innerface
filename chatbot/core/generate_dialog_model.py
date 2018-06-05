# Author: YuYuE (1019303381@qq.com) 2018.03.16
import hashlib
from chatbot.core import generate_business_model as business_model
from chatbot.settings import RedisConn
import json


def is_dialog_set(params, mode='QA'):
    """
    是否存在对话缓存
    :param params:
    :param mode:
    :return:
    """
    if params['success'] is False:
        return params
    param = params['data']
    customer_id = param['customer_id']
    redisConn = RedisConn()
    redis_ = redisConn.redis_conn
    value = redis_.get(customer_id + mode)
    return value


def recover_dialog_model(params, dialog_set):
    """
    恢复对话缓存，并校验矫正缺省项
    :param params:
    :param dialog_set:
    :return:
    """
    try:
        if params['success'] is False:
            return params
        dialog_info = json.loads(dialog_set)
        param = params['data']
        if dialog_info['customer_id'] != param['customer_id']:
            return params
        if 'question' in dialog_info:
            params['data']['pre_question'] = dialog_info['question']
        if 'scenario' in dialog_info:
            params['data']['scenario'] = dialog_info['scenario']
        if 'type' in dialog_info:
            params['data']['type'] = dialog_info['type']
        if 'operation' in dialog_info:
            params['data']['operation'] = dialog_info['operation']
        if 'references' in dialog_info:
            params['data']['references'] = dialog_info['references']
        if 'relations' in dialog_info:
            params['data']['relations'] = dialog_info['relations']
        if 'time_stamp' in dialog_info:
            params['data']['time_stamp'] = dialog_info['time_stamp']
        else:
            params['data']['time_stamp'] = -1
    except Exception as error:
        raise Exception('Exception:', error)
    else:
        return params


def record_dialog_model(params, mode='QA'):
    """
    保存对话缓存
    :param params:
    :param mode:
    :return:
    """
    try:
        if params['success'] is False:
            return params
        param = params['data']
        customer_id = param['customer_id']
        redisConn = RedisConn()
        redis_ = redisConn.redis_conn
        value = redis_.set(customer_id + mode, json.dumps(param), 3600)
    except Exception as error:
        raise Exception('Exception:', error)
    else:
        return value


def update_dialog_model(inp, dia):
    return inp


def compose_response(inp, cache_id):
    return inp


def transfer_response(inp, response, dia):
    hl = hashlib.md5()
    hl.update(response['answer'].encode(encoding='utf-8'))
    md5_ = hl.hexdigest()
    result = {
        "code": 200,
        "data": {
            'reference': response['reference'],
            'answer': response['answer'],
            'suggestion': response['suggestion'] if 'suggestion' in response else ''
        },
        "cache": md5_,
        "error": ""
    }
    return result


def init_business_dialog(ners, main_sent):
    params = {}
    if ners:
        for ner in ners:
            type_ = business_model.siphon_business_keywords(ner)
            if 'type_id' in type_ and type_['type_id'] == 1:
                params['scenario'] = ner
            elif 'type_id' in type_ and type_['type_id'] is not None:
                params['type'] = type_['type_name']
                params['operation'] = ner
            else:
                pass
    if 'scenario' not in params:
        new_type = business_model.siphon_business_keywords(main_sent)
        if 'type_id' in new_type and new_type['type_id'] == 1:
            params['scenario'] = main_sent
        elif 'type_id' in new_type and new_type['type_id'] is not None:
            params['type'] = new_type['type_name']
            params['operation'] = main_sent
        else:
            pass
    # record_dialog_model(params)
    return params


def siphon_relations_by_nlp(references, ners, type_):
    relation = {}
    if type_ == 'status':
        description = ''
        relations = []
        if 'scenario' in references:
            infos = business_model.siphon_business_production(False, references['scenario'])
            relations = business_model.siphon_business_structure(references['scenario'], None, None, True)
            if len(infos) > 1:
                for inf in infos:
                    if ('operation' in references) and inf.name == references['operation']:
                        description = inf.description
            elif len(infos) == 1:
                description = infos[0].description
            else:
                description = ''
        if description is None:
            pass
        if description:
            relation['description'] = description
        if relations:
            relation['suggestion'] = relations
    else:
        description = ''
        relations = []
        if 'scenario' in references and 'operation' in references:
            infos = business_model.siphon_business_operation(False, references['scenario']+references['operation'])
            if infos:
                if 'item' in infos:
                    item = infos['item']
                    relations = business_model.siphon_linked_operation(item)
                    relations.remove(references['scenario']+references['operation'])
                if 'description' in infos:
                    description = infos['description']
            else:
                relations = business_model.siphon_business_structure(references['scenario'], None, None, True)
        if description:
            relation['description'] = description
        if relations:
            relation['suggestion'] = relations
    return relation
