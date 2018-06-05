import hashlib
import json
import os
import xml.etree.ElementTree as et
import time, random, string

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
import chatbot.core.generate_model as gm
import configparser
import json
from chatbot.core.generate_model import best_ansewer
from chatbot.core.generate_system_filter import sensitive_filter
from chatbot.core.sensitiveWord import is_contain
from tools.utils import wechat_rec_deal
from vendor.interface.api_of_turing import generate_sensitive_reply
from vendor.optimization.keywords_sorted import default_synonyms
from django.views.decorators.csrf import csrf_exempt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = configparser.ConfigParser()
config.read(os.path.join(BASE_DIR, 'chatbot.conf'))
token = config.get("crypto", "token")


def index(request):
    question_auto = []
    keywords = ''
    best_answer = ''
    question = ''
    if request.method == 'POST':
        question = request.form['question']
        question = gm.question_correct(question)
        keywords = gm.generate_keywords(question)
        search_keywords = gm.generate_search_keywords(question, keywords)
        question_auto = gm.generate_answer_by_mode(question, search_keywords)
        ip = request.remote_addr
        best_answer = gm.generate_best_answer(question_auto, question, ip)
    else:
        print('GET')
    return HttpResponse(question_auto=question_auto, keywords=keywords, best_answer=best_answer,
                        question=question, )


def chat(request):
    """
    客服处理引擎主入口,这里只是问答核心，不涉及不同平台信息补全以及整合
    请求方式：post
    请求参数：
    :param question    问题输入,文本，语音，图片，表情等
    :param type        输入类型，文本类 0，语音类 1，图片 2，表情 3，默认文本
    :param cache       前置对话缓存，如没有则置空
    :param platform    访问渠道，web端 0，微信端 1，电话端 2，短信端 3，智能硬件端 4，默认web端
    :param version     只允许使用已对外开放的版本，默认版本为被请求方设置
    :param client_code  问题源头用户编码，此参数依赖渠道类型，可留白
    :param client_info  问题源头用户信息，时间，地点，ip，电话等
    :param system_code  发出请求的系统编码，用于设备校验，日志记录以及数据统计
    :param user_id      API授权用户ID
    :param secret_key   对应用户授权密钥
    :return json格式 {
                "code":200,//返回码，是否操作成功
                "data":{
                    "answer":"This is the answer!",//最佳答案
                    "pre_question":[{1},{2},{3}],//推荐问题
                    "pre_answer":[{1},{2},{3}],//推荐答案
                    "pre_keywords":[{1},{2},{3}],//推荐关键字
                    "type":"consult",//问答类型
                    }},
                "cache":"DFGHJKRTYUIGHJKFGHJ"//当前对话的缓存编码，如有下文携带返回，同时存放服务器用户绑定缓存中，设定生命周期
                "error":""//错误信息输出
                }
    步骤：
    1.前置信息校验，是否有权限请求，是否合法请求，是否信息完整，是否包含敏感词等 pre_system_filter()
    2.查找更新用户及时对话日志或更新存储用户对话日志 recover_or_record_dialog()
    3.客服问答引擎处理 artificial_intelligence_customer_service AI_customer_service()
    4.添加回复信息日志以及缓存标记 update_client_dialog_info()
    5.根据渠道或者问题类型整合回复内容 transfer_result_to_response()
    """
    if request.method == 'POST':
        post_value = {
            'question': request.values.get('question', type=str, default=None),
            'type': request.values.get('type', type=str, default='0'),
            'cache': request.values.get('cache', type=str, default=None),
            'platform': request.values.get('platform', type=str, default='0'),
            'version': request.values.get('version', type=str, default=None),
            'client_code': request.values.get('client_code', type=str, default=None),
            'client_info': request.values.get('client_info', type=str, default=None),
            'system_code': request.values.get('system_code', type=str, default=None),
            'user_id': request.values.get('user_id', type=str, default=None),
            'secret_key': request.values.get('secret_key', type=str, default=None),
        }
        value_filter = gm.pre_system_filter(post_value)
        dialog_info = gm.recover_or_record_dialog(value_filter)
        service_output = gm.AI_customer_service(post_value['question'], dialog_info)
        dialog_new_info = gm.update_client_dialog_info(service_output, dialog_info)
        result = gm.transfer_result_to_response(post_value['question'], service_output, dialog_new_info)
    else:
        result = {
            "code": 401,
            "data": [],
            "cache": "",
            "error": "GET method is not safe,plz try POST"
        }
    return json.dumps(result)


def home(request):
    msg = "Welcome To QArobot!"
    context = {
        'msg': msg
    }
    return render(request, 'home.html', context)


def verify_cookie(request):
    cookie = request.COOKIES
    user = request.session.get('user')
    if user:
        return user
    elif cookie:
        return cookie['csrftoken']
    else:
        user = ''.join(random.choices(string.ascii_letters + string.digits, k=15))
        request.session['user'] = user
        return user


def ask(request):
    ans = ''
    try:
        question = request.GET.get('question', '')
        user = verify_cookie(request)
        # ans = best_ansewer(question, True)
        # import chatbot.core.generate_business_model as bs_model
        # ans = bs_model.siphon_reference_business_operation(False, '信用卡销卡')
        params = {
            'question': question,
            'system_code': 'system',
            'user_id': '001',
            'secret_key': 'yuyue',
            'customer_id': user
        }
        print(time.time())
        # ans = gm.QA_kernel(params)
        print(time.time())
        ans = best_ansewer(question, True, user)
        print(time.time())
        print(ans)
    except Exception as error:
        print('Exception', error)
    else:
        pass
    return HttpResponse(ans)


@csrf_exempt
def robot_ask(request):
    """
    :param request:
    {
        "robot": {
            "device_id": "dd8d4cf8-29e4-4e1a-ad3b-29d6efd80addI",
            "device_type_id": "dd8d4cf8-29e4-4e1a-ad3b-29d6efd80addI",
            "sub_system_id": "dd8d4cf8-29e4-4e1a-ad3b-29d6efd80addI",
            "position": "深圳建设银行高新园支行"
        },
        "user": {
            "user_id": "522627198009070043",
            "name": "刘建",
            "sex": "男",
            "age": "38",
            "emotion": "smail"
        },
        "request": {
            "type": "voice",
            "isflow": false,
            "request_id": "dd8d4cf8-29e4-4e1a-ad3b-29d6efd80add",
            "user_input": {
                "type": "text",
                "content": "你好",
                "intent": "chat"
            }
        },
        "session_id": "337a891a-f7a7-40b5-8e06-a0312a065f7f",
        "channel":0,
        "timestamp": "2017-10-12 03:27:56",
        "version": "1.0"
    }

    :return:{
           "session_id": "337a891a-f7a7-40b5-8e06-a0312a065f7f",
           "device_id": "d8d4cf8-29e4-4e1a-ad3b-29d6efd80addI",
           "response": {
               "request_id": "dd8d4cf8-29e4-4e1a-ad3b-29d6efd80add",
               "response_id": "337a891a-f7a7-40b5-8e06-a0312a065f7f",
               "intent": "chat",
               "from": "system",
               "type": "Text",
               "output": {
                   "score": 90,
                   "tts": "你好，有什么可以帮助您的？",
                   "recQuestion":[],
                   "recAnswer":[]
               },
               "show_card": {}
           },
           "timestamp": "2017-10-12 03:27:56",
           "error_code": "0",
           "error_msg": "执行成功",
           "version": "1.0"
       }
    """

    body = request.body
    params = json.loads(body.decode())
    user = verify_cookie(request)
    question = params["request"]["user_input"]["content"]
    if list(is_contain(question)):
        answer = generate_sensitive_reply()
        recQuestion = ''
    else:
        answer_obj = best_ansewer(question, True, user)
        answer = answer_obj[0][:500]
        recQuestion = answer_obj[1]
        recQuestion = wechat_rec_deal(recQuestion)
    recAnswer = []
    robot_response = {
        "session_id": params["session_id"],
        "device_id": params["robot"]["device_id"],
        "response": {
            "request_id": params["request"]["request_id"],
            "response_id": params["session_id"],
            "intent": params["request"]["user_input"]["intent"],
            "from": "system",
            "type": params["request"]["user_input"]["type"],
            "output": {
                "score": 90,
                "tts": answer,
                "recQuestion": recQuestion,
                "recAnswer": []
            },
            "show_card": {}
        },
        "timestamp": params["session_id"],
        "error_code": "0",
        "error_msg": "执行成功",
        "version": params["version"]
    }
    return JsonResponse(robot_response)


@csrf_exempt
def check_signature(request):
    if request.method == 'POST':
        text = '<xml><ToUserName><![CDATA[{0}]]></ToUserName><FromUserName><![CDATA[{1}]]></FromUserName>' \
               '<CreateTime>{2}</CreateTime><MsgType><![CDATA[{3}]]></MsgType><Content><![CDATA[{4}]]></Content></xml>'
        str_xml = request.body
        xml_rec = et.fromstring(str_xml)
        ToUserName = xml_rec.find('ToUserName').text
        fromUser = xml_rec.find('FromUserName').text
        CreateTime = xml_rec.find('CreateTime').text
        MsgType = xml_rec.find('MsgType').text
        if MsgType == 'text':
            Content = xml_rec.find('Content').text.encode().decode('unicode-escape').encode('latin-1').decode()
            if list(is_contain(Content)):
                reply = generate_sensitive_reply()
            else:
                bestansewer = best_ansewer(Content, True, fromUser)
                suggestion = wechat_rec_deal(bestansewer[1])
                reply = bestansewer[0][:500] + '\n' + suggestion
            if not reply:
                reply = '嘛哩嘛哩哄'
        else:
            MsgType = 'text'
            reply = '暂时不回答此类问题'
        print(text.format(fromUser, ToUserName, CreateTime, MsgType, reply))
        return HttpResponse(text.format(fromUser, ToUserName, CreateTime, MsgType, reply))
    else:
        try:
            timestamp = request.GET.get('timestamp', '')
            nonce = request.GET.get('nonce', '')
            signature = request.GET.get('signature', '')
            echostr = request.GET.get('echostr', '')
            L = [timestamp, nonce, token]
            L.sort()
            s = L[0] + L[1] + L[2]
            hashcode = hashlib.sha1(s.encode('utf-8')).hexdigest()
            if hashcode == signature:
                return HttpResponse(str(echostr))
            else:
                return ""
        except Exception as e:
            return ""


def test_is_contain(request):
    msg = '含家产, 丢雷楼某sdfh缴纳水电费阿三地方吗顶你个肺'
    results = sensitive_filter(msg)
    results = default_synonyms()
    # l = []
    # for r in results:
    #     l.append(r)
    return HttpResponse(str(results))


def test_mongo(request):
    from chatbot.settings import MongoConn
    my_conn = MongoConn()
    res = my_conn.db['fx'].find()
    l = []
    for k in res:
        l.append(k['name'])
    # user = {"name": "cui", "age": "10"}
    # # 添加单条数据到集合中
    # my_conn.db['fx'].insert(user)
    # 同时添加多条数据到集合中
    users = [{"name": "cui", "age": "9"}, {"name": "cui", "age": "11"}]
    my_conn.db['fx'].insert(users)
    # 查询单条记录
    print(my_conn.db['fx'].find_one())

    # 查询所有记录
    for data in my_conn.db['fx'].find():
        print(data)

        # 查询此集合中数据条数
    print(my_conn.db['fx'].count())

    # 简单参数查询
    for data in my_conn.db['fx'].find({"name": "1"}):
        print(data)

        # 使用find_one获取一条记录
    print(my_conn.db['fx'].find_one({"name": "1"}))

    # 高级查询
    print("__________________________________________")
    print('''''collection.find({"age":{"$gt":"10"}})''')
    print("__________________________________________")
    for data in my_conn.db['fx'].find({"age": {"$gt": "10"}}).sort("age"):
        print(data)

        # 查看db下的所有集合
    print(my_conn.db['fx'])
    for k in res:
        print(k)

    my_conn.db['fx'].delete_many({"name": "cui"})
    return HttpResponse(str(l))


def test_redis(request):
    gm.update_keywords_from_question()
    exit()
    from chatbot.settings import RedisConn
    redisConn = RedisConn()
    r = redisConn.redis_conn
    res = r.get('bing')
    print(res)
    return HttpResponse(str(res))
