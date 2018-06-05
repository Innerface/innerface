import json

import Levenshtein

from chatbot.settings import RedisConn, MySQLConn

conn_instance = MySQLConn()


def get_new_engine(response, params):
    sentence = params['data']['question']

    node = fetch_start_node(sentence)
    if node:
        # 精确匹配到engin_node_info的节点时，返回提示信息以及下一步的操作列表
        tts = node[-1]
        next_option, next_option_p = fetch_next_option(node[0])
        response['answer'] = tts if tts else "完成后，请直接回复下面操作序号"
        response['suggestion'] = next_option_p
        data = params["data"]
        if next_option:
            data['next_option'] = next_option
            save_context_to_redis(data, True)
        else:
            delete_round_redis(params)
        save_time_to_redis(params)

    else:
        # 模糊匹配engin_node_info的节点操作，待做
        # tmp_dict = {}
        # for key in word_dict.keys():
        synonyms_origin = fetch_proper_root(sentence)
        if synonyms_origin is None:
            response['success'] = False
            return response
        else:
            tts = synonyms_origin[-1]

            next_option, next_option_p = fetch_next_option(synonyms_origin[0])
            response['answer'] = tts if tts else "完成后，请直接回复下面操作序号"
            response['suggestion'] = next_option_p
            data = params["data"]
            if next_option:
                data['next_option'] = next_option
                save_context_to_redis(data, True)
            else:
                delete_round_redis(params)
    return response


def multi_round_service(params):
    response = {
        'success': True
    }
    sentence = params['data']['question']
    # 判断多轮流程是否已经存在，来自redis
    context_ = fetch_context_from_redis(params["data"])
    # 不若存在，如下操作
    if context_ is None:
        resp = get_new_engine(response, params)
        return resp

    # 若存在则先获取上下文，得到当前的流程进度，
    else:
        context_list = json.loads(context_)
        context = context_list[-1]
        next_option = context['next_option']
        if not next_option:
            response["success"] = False

        else:
            if is_number(params['data']['question'] ):
                idx = next_option[int(params['data']['question'])-1]
                mid_node = fetch_mid_node(idx[0])
                tts = mid_node[-1]
                next_option, next_option_p = fetch_next_option(mid_node[0])
                response['answer'] = tts if tts else "完成后，请直接回复下面操作序号"
                response['suggestion'] = next_option_p
                data = params["data"]
                if next_option:
                    data['next_option'] = next_option
                    save_context_to_redis(data, True)
                else:
                    delete_round_redis(params)
                return response
            for option in next_option:
                if change_syn(params['data']['question']) in option[1]:
                    mid_node = fetch_mid_node(option[0])
                    tts = mid_node[-1]
                    next_option, next_option_p = fetch_next_option(mid_node[0])
                    response['answer'] = tts if tts else "完成后，请直接回复下面操作序号"
                    response['suggestion'] = next_option_p
                    data = params["data"]
                    if next_option:
                        data['next_option'] = next_option
                        save_context_to_redis(data, True)
                    else:
                        delete_round_redis(params)
                    return response
            res = get_new_engine(response, params)
            if res["success"]:
                return res
            response["success"] = False
        return response


def delete_round_redis(params, mode="multi_process"):
    try:

        customer_id = params['data']['customer_id']
        redisConn = RedisConn()
        redis_ = redisConn.redis_conn
        # a = json.dumps([params])
        redis_.delete(customer_id + mode)
    except Exception as e:
        return None



def is_number(params):
    try:
        x = int(params)
        return True

    except Exception as e:
        return False

def fetch_mid_node(id):
    res = []

    cursor = conn_instance.cursor()
    result = None
    sql = 'select * from data_admin_business_engine where id=%s  ' % id
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        print(e)

    if len(result) > 0:
        return result[0]
    else:
        return None


def fetch_next_option(pre_node):
    res = []
    res_p = ''
    cursor = conn_instance.cursor()
    result = None
    sql = 'select * from data_admin_business_engine where preNodeId=%s  order by id' % pre_node
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        print(e)
    if len(result) > 0:
        for index, ele in enumerate(result):
            res.append((ele[0], ele[-2]))
            res_p = " {} {}".format(res_p, ele[-2])
        return res, res_p.strip()
    else:
        return None, None


def fetch_start_node(sentence):
    cursor = conn_instance.cursor()
    result = None
    sql = 'select * from data_admin_business_engine where nodeName="%s" and isStart = 1' % sentence
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        print(e)
    if len(result) > 0:
        return result[0]
    else:
        return None


def fetch_all_root():
    cursor = conn_instance.cursor()
    result = None
    sql = 'select id ,nodeName,nextHint from data_admin_business_engine where isStart=1 '
    try:
        cursor.execute(sql)
        result = cursor.fetchall()
    except Exception as e:
        print(e)
    return result


def fetch_proper_root(word):
    all_node = fetch_all_root()
    distance_list = []
    for id, node_name, hint in all_node:
        distance = Levenshtein.ratio(word, node_name)
        distance_list.append((id, distance, node_name, hint))
    sorted_distance = sorted(distance_list, key=lambda k: -k[1])
    if sorted_distance[0][1] >= 0.9:
        return sorted_distance[0]
    else:
        return None


def fetch_context_from_redis(params, mode="multi_process"):
    try:
        customer_id = params['customer_id']
        redisConn = RedisConn()
        redis_ = redisConn.redis_conn
        value = redis_.get(customer_id + mode)
        return value
    except Exception as e:
        return None


def save_time_to_redis(params,  mode="multi_process",):

    redisConn = RedisConn()
    redis_ = redisConn.redis_conn
    import time
    t = time.time()
    redis_.set("{}_{}_timestamp".format(params["data"]['customer_id'],mode), t)

def save_context_to_redis(params, init_flag=False, mode="multi_process", del_flag=False):

    if params["next_option"] is None:
        delete_round_redis(params)
        return None

    redisConn = RedisConn()
    redis_ = redisConn.redis_conn
    if init_flag:
        try:

            customer_id = params['customer_id']

            redis_.set(customer_id + mode, json.dumps([params]))
        except Exception as e:
            return None

    else:
        try:
            customer_id = params['customer_id']

            value = json.loads(redis_.get(customer_id + mode))
            value.append(params)
            redis_.set(customer_id + mode, json.dumps(value))


        except Exception as e:
            return None

def get_last_round_time(params,mode="multi_process"):
    try:
        redisConn = RedisConn()
        redis_ = redisConn.redis_conn
        t  = redis_.get("{}_{}_timestamp".format(params["data"]['customer_id'],mode))
        return float(t)
    except Exception as e:
        return -1

def change_syn(question):
    redisConn = RedisConn()
    redis_ = redisConn.redis_conn
    ws =[str(i.decode()) for i in redis_.lrange("synormy_of_next",0,-1)]
    if question.strip() in ws:
        return "下一步"
    else:
        return question


def redis_push():
    redisConn = RedisConn()
    redis_ = redisConn.redis_conn
    l = ["go on","GO ON","继续","下一步","接着下一步","接下来","接着，下一步","next","next step","go","go to next"]
    for e in l :
        redis_.lpush("synormy_of_next",str(e))


if __name__ == '__main__':
    redis_push()
    # rs = multi_round_service(None, {'开通': 'v', '龙支付': 'n'}, "办理龙支付")
    # print(rs)
