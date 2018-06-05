# Author: YuYuE (1019303381@qq.com) 2018.01.23
import vendor.optimization.keywords_sorted as mdoks
import vendor.interface.api_of_turing as turing_interface
import vendor.interface.common_function_model as common_interface
import chatbot.core.generate_ai_customer_service as mgaics
import chatbot.core.generate_multi_round_answer as mgmra
import chatbot.core.generate_dialog_model as mgdm
import chatbot.core.generate_system_filter as mgsf
import vendor.algorithm.word2vec.generate_word_vector as agwv
import vendor.nlp.nlp_jieba_model as jieba_nlp
import vendor.nlp.nlp_ltp_model as ltp_nlp
import vendor.nlp.nlp_pinyin_hanzi_transfer as phtransfer_nlp
from data_admin.models import Question_auto, Synonym_sentence, Question_t
from chatbot.settings import ONTOLOGY
from chatbot.settings import ATTR
import copy
import time


# 问题别字纠错以及拼音识别
def question_correct(question):
    """拼音识别"""
    result = ''
    question = common_interface.remove_special_tags(question)
    if phtransfer_nlp.is_alphabet(question):
        words = phtransfer_nlp.transfer_continue_pinyin_to_hanzi(question)
        if len(words) > 0:
            result = ''.join(words)
    else:
        result = question
    return result


# 提取关键词
def generate_keywords(question):
    # 去停用词
    if question:
        keywords = jieba_nlp.remove_stop_words_by_jieba(str(question))
    else:
        keywords = ''
    # print(keywords)
    return keywords


# 组装查询条件
def generate_search_keywords(question, keywords):
    # 取前两个关键词模糊匹配并按点赞数排序
    # 如果去停用词后，关键词超过两个，则只取前两个
    if len(keywords) == 2:
        keywords = ''.join(keywords)
    elif len(keywords) > 2:
        keywords = keywords[0] + keywords[1]
    elif len(keywords) == 1:
        keywords = keywords[0]
    else:
        keywords = question
    return keywords


# 数据库操作剥离，捕捉异常并添加事务回滚
def generate_qa_data_by_question(value='hi', like=False):
    try:
        data = []
        if value.strip() == '':
            return data
        if like:
            data = Question_auto.query.filter(Question_auto.question.like("%" + value + "%")).order_by('-agrees').limit(
                10)
        else:
            data = Question_auto.query.filter_by(question=value)
    except Exception as error:
        Question_auto.roll_back()
        return str(error)
    else:
        return data


# 获取答案，固定jieba分词
def generate_answers(question, keywords):
    if keywords == question and len(question) > 5:
        question_auto = generate_qa_data_by_question(question)
    else:
        question_auto = generate_qa_data_by_question(keywords, True)
    # 如果查询不到结果
    if question_auto.count() < 1:
        question_auto = generate_qa_data_by_question(question, True)
    # 问答相似度计算
    question_origin = question
    question = common_interface.remove_special_tags(question)
    for i in range(question_auto.count()):
        if question_auto[i].question:
            # print(question_auto[i].question)
            ques_ = common_interface.remove_special_tags(question_auto[i].question)
            # print(ques_)
            try:
                simi = agwv.generate_sentence_simi(question, ques_)
            except Exception as error:
                # words = str(error).split('\'')
                if question_origin == question_auto[i].question:
                    question_auto[i].simi = '1'
                else:
                    question_auto[i].simi = '0'
                continue
            else:
                question_auto[i].simi = str(simi)[0:5]
                del simi
                del ques_
                agwv.clear_mem()
    agwv.clear_mem()
    question_auto = sorted(question_auto, key=lambda qa: qa.simi, reverse=True)
    return question_auto


# 获取最佳答案
def generate_best_answer(question_auto, question, ip='0.0.0.0', user='none'):
    if len(question_auto) > 0:
        best_answer = question_auto[0].answer
    else:
        best_answer = generate_turing_response(question, ip, user)
    return best_answer


# 范围外问题对接图灵机器人
def generate_turing_response(question, loc, user):
    print('turing+', question)
    result = turing_interface.generate_turing_response(question, loc, user)
    return result


# 获取答案，分词工具模式可选
def generate_answer_by_mode(question, keywords, mode='jieba'):
    if keywords == question and len(question) > 5:
        question_auto = generate_qa_data_by_question(question)
    else:
        question_auto = generate_qa_data_by_question(keywords, True)
    # 如果查询不到结果
    if question_auto.count() < 1:
        question_auto = generate_qa_data_by_question(question, True)
    # 问答相似度计算
    question_origin = question
    if mode == 'ltp':
        ques = ltp_nlp.generate_segment_after_remove_stop_words(question)
        ques = remove_special_tags(ques)
    elif mode == 'jieba':
        ques = jieba_nlp.generate_jieba_cut(question)
        ques = remove_special_tags(ques)
    # ques = model.nlp_jieba_model.generate_jieba_cut(question)
    # ques = remove_special_tags(ques)
    for i in range(question_auto.count()):
        if question_auto[i].question:
            if mode == 'ltp':
                ques_ = ltp_nlp.generate_segment_after_remove_stop_words(question_auto[i].question)
                ques_ = remove_special_tags(ques_)
            elif mode == 'jieba':
                ques_ = jieba_nlp.generate_jieba_cut(question_auto[i].question)
                ques_ = remove_special_tags(ques_)
            # ques_ = model.nlp_jieba_model.generate_jieba_cut(question_auto[i].question)
            # ques_ = remove_special_tags(ques_)
            # print(ques_)
            try:
                simi = agwv.generate_sets_simi(ques, ques_)
            # simi = model.generate_word_vector.generate_sets_simi_by_self(ques, ques_)
            except Exception as error:
                # print(error)
                # words = str(error).split('\'')
                if question_origin == question_auto[i].question:
                    question_auto[i].simi = '1'
                else:
                    question_auto[i].simi = '0'
                continue
            # raise Exception("Exception:", error)
            else:
                question_auto[i].simi = str(simi)[0:5]
                del simi
                del ques_
    agwv.clear_mem()
    question_auto = sorted(question_auto, key=lambda qa: qa.simi, reverse=True)
    return question_auto


# 剔除特殊字符
def remove_special_tags(sets):
    try:
        # if len(sets) < 1:
        # 	raise Exception("input invaild")
        result = []
        for s in sets:
            temp = common_interface.remove_special_tags(s)
            if temp.strip() != '':
                result.append(temp)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 给出最佳答案
def best_ansewer(question, mode=False, user='system'):
    best_answer = ''
    suggestion = ''
    try:
        if mode is False:
            keywords = generate_keywords(question)
            search_keywords = generate_search_keywords(question, keywords)
            question_auto = generate_answer_by_mode(question, search_keywords)
            # ip = request.remote_addr
            best_answer = generate_best_answer(question_auto, question)
        else:
            params = {
                'success': True,
                'data': {
                    'question': question,
                    'customer_id': user
                }
            }
            dialog_info = recover_or_record_dialog(params)
            print(dialog_info)
            if 'relations' in dialog_info['data']:
                ref = len(dialog_info['data']['relations'])
                if ref and phtransfer_nlp.is_number(question) and int(question) in range(ref):
                    question = dialog_info['data']['relations'][int(question)]
            answer = AI_customer_service(question, dialog_info)
            print(answer)
            if answer['success'] and answer['answer']:
                best_answer = answer['answer']
                if 'suggestion' in answer:
                    suggestion = answer['suggestion']
        if best_answer == '':
            best_answer = generate_turing_response(question, '深圳市', user)
    except Exception as error:
        # raise Exception('Exception:', error)
        print('Exception:', error)
        best_answer = generate_turing_response(question, '深圳市', user)
        return best_answer, ''
    else:
        return best_answer, suggestion


def QA_kernel(params):
    """
    QA_kernel问答引擎入口
    :param params:应包含参数如下
        question    问题输入,文本，语音，图片，表情等
        type        输入类型，文本类 0，语音类 1，图片 2，表情 3，默认文本
        cache       前置对话缓存，如没有则置空
        platform    访问渠道，web端 0，微信端 1，电话端 2，短信端 3，智能硬件端 4，默认web端
        version     只允许使用已对外开放的版本，默认版本为被请求方设置
        client_code  问题源头用户编码，此参数依赖渠道类型，可留白
        client_info  问题源头用户信息，时间，地点，ip，电话等
        system_code  发出请求的系统编码，用于设备校验，日志记录以及数据统计
        user_id      API授权用户ID
        secret_key   对应用户授权密钥
    :return:
    """
    value_filter = pre_system_filter(params)
    if value_filter['success'] is False:
        return value_filter
    dialog_info = recover_or_record_dialog(value_filter)
    if dialog_info['success'] is False:
        return dialog_info
    if 'relations' in dialog_info['data']:
        ref = len(dialog_info['data']['relations'])
        if ref and phtransfer_nlp.is_number(params['question']) and int(params['question']) in range(ref):
            params['question'] = dialog_info['data']['relations'][int(params['question'])]
    service_output = AI_customer_service(params['question'], dialog_info)
    if "is_flow" in service_output and service_output["is_flow"]:
        return service_output
    if service_output['success'] is False:
        return service_output
    dialog_new_info = update_client_dialog_info(service_output, dialog_info)
    if dialog_new_info['success'] is False:
        return dialog_new_info
    result = transfer_result_to_response(params['question'], service_output, dialog_new_info)
    return result


def pre_system_filter(params):
    """
    任务：
    1.参数检测，是否缺失必要参数 param_filter
    2.信息校验，是否授权请求 auth_filter
    3.过滤违规敏感词，或者拦截 sensitive_filter
    4.用户黑名单拦截，ip电话等，防恶意攻击 black_list_filter
    :param inp: 请求参数
    :return: dic {
                "success":True,//返回码，是否操作成功
                "data":data
                "error":""//错误信息输出
                }
    """
    after_param_filter = mgsf.param_filter(params)
    if after_param_filter['success'] is False:
        return after_param_filter
    after_black_filter = mgsf.black_list_filter(after_param_filter)
    if after_black_filter['success'] is False:
        return after_black_filter
    after_auth_filter = mgsf.auth_filter(after_black_filter)
    if after_auth_filter['success'] is False:
        return after_auth_filter
    after_sensitive_filter = mgsf.sensitive_filter(after_auth_filter)
    return after_sensitive_filter


def recover_or_record_dialog(params):
    """
    任务：
    1.检测是否存在前置对话记录 is_dialog_set
    2.若存在，则从中恢复对话环境，若不存在，则初始化对话环境 recover_dialog_model/record_dialog_model
    3.整合用户画像，或者对话环境
    :param inp:
    :return:dic {
                "success":True,//返回码，是否操作成功
                "data":data
                "error":""//错误信息输出
                }
    """
    try:
        dialog_set = mgdm.is_dialog_set(params)
        if dialog_set:
            model_dialog_info = mgdm.recover_dialog_model(params, dialog_set)
        else:
            model_dialog_info = params
    except Exception as error:
        raise Exception('Exception:', error)
    else:
        return model_dialog_info


def AI_customer_service(question, dia=None):
    """
    任务：
    1.文本去噪，去除无意义字词
    2.关键字，命名实体识别
    3.实体关系发现
    4.区分问题类型，信息咨询类还是业务办理类
    5.如果是信息咨询类，进行FAQ语义距离计算，抽取最接近FQA
    6.若无相关FAQ，则进入图谱查找答案，图谱未完成阶段，此步骤跳过
    7.图谱答案不佳，则追溯文档资料
    8.如果有较匹配答案，则推出答案时，并推出推荐主题相关问题或者答案，若没有，则学习中……
    9.如果是业务办理类，则需要还原问题所在的业务流程步骤
    10.重复5，6，7步骤查找详细答案，如果找到较匹配答案，则推出答案，并附带业务流程相关的信息推荐
    11.不管哪种类型，均附带推送平行相关关键词
    12.格式化恢复信息并输出
    :param inp:
    :param dia:
    :return:dic {
                "success":True,//返回码，是否操作成功
                "data":data
                "error":""//错误信息输出
                }
    """
    response = {
        'success': False
    }
    answer = ''
    if dia:
        dialog_copy = copy.deepcopy(dia)
        response_ = mgmra.multi_round_service(dialog_copy)
        if response_['success']:
            response_["is_flow"] = True
    if "time_stamp" not in dia["data"]:
        t2 = -1
    else:
        t2 = float(dia['data']['time_stamp'])
    t1 = mgmra.get_last_round_time(dia)

    if (t1 == -1 or t1 >= t2)  and response_['success']:
        mgmra.save_time_to_redis(dia)
        mgmra.delete_round_redis(dia,mode="QA")
        return response_


    mgmra.delete_round_redis(dia)
    main_sent = mgaics.remove_useless_and_correction(question)
    is_origin = is_origin_question(question)
    print('is_origin ===>', is_origin)
    if is_origin:
        response['success'] = True
        response['reference'] = ''
        response['answer'] = is_origin
        return response
    print('main_sent ===>', main_sent)
    # 同义句查询
    answer = synonymous_sentence_matching(main_sent)
    if answer:
        response['success'] = True
        response['answer'] = answer
        response['suggestion'] = ''
        return response
    ners = []
    word_dict = {}

    if main_sent in ONTOLOGY or main_sent in ATTR:
        word_dict[main_sent] = 'n'
        ners.append(main_sent)
    else:
        print('not keywords ===>1', main_sent)
        main_sent = mgaics.corrected_sentence_by_pinyin(main_sent)
        if main_sent.find('转帐') != -1 and question.find('转账') != -1:
            main_sent = main_sent.replace('转帐', '转账')
        if main_sent.find('语带集卡') != -1 and question.find('与贷记卡') != -1:
            main_sent = main_sent.replace('语带集卡', '与贷记卡')
        if main_sent.find('面授') != -1 and question.find('免收') != -1:
            main_sent = main_sent.replace('面授', '免收')
        if main_sent.find('道长') != -1 and question.find('到账') != -1:
            main_sent = main_sent.replace('道长', '到账')
        if main_sent.find('见面') != -1 and question.find('减免') != -1:
            main_sent = main_sent.replace('见面', '减免')
        print('not keywords ===>2', main_sent)
        word_dict = mgaics.split_sentence_to_words(main_sent, method='method', mode='HMM')
        ners = mgaics.siphon_ners_by_nlp(main_sent, word_dict, method='method', mode='HMM')
    references = complete_business_dialog(dia, ners, main_sent)
    print('references ===>', references)
    if references:
        dia['data']['references'] = references

    type_ = mgaics.text_classification(main_sent, word_dict, references)
    print('type_ ===>', type_)
    if type_:
        dia['data']['type'] = type_
    relations = mgdm.siphon_relations_by_nlp(references, ners, type_)
    print('relation ===>', relations)
    if relations:
        if 'description' in relations:
            response['answer'] = relations['description']
        if 'suggestion' in relations:
            dia['data']['relations'] = relations['suggestion']
            response['suggestion'] = ' '.join(relations['suggestion'])
    if 'answer' not in response:
        keywords = mgaics.siphon_keywords_by_grammar(main_sent)
        print('keywords ===>', keywords)
        response['answer'] = generate_response(main_sent, keywords, ners, relations, type_)
    if 'answer' in response:
        response['success'] = True
        response['reference'] = references
    dia['data']['time_stamp'] = time.time()
    print('dia', dia['data'])
    mgdm.record_dialog_model(dia)
    return response


def complete_business_dialog(params, ners, main_sent):
    """
    补全业务场景参数
    :param params:
    :param ners:
    :return:
    """
    business_info = mgdm.init_business_dialog(ners, main_sent)
    if business_info:
        if ('scenario' not in business_info) and 'scenario' in params['data']:
            business_info['scenario'] = params['data']['scenario']
        elif (('scenario' not in business_info)
              and ('scenario' not in params['data'])
              and 'pre_question'in params['data']):
            question = params['data']['pre_question']
            main_sent = mgaics.remove_useless_and_correction(question)
            word_dict = mgaics.split_sentence_to_words(main_sent, method='method', mode='HMM')
            new_ners = mgaics.siphon_ners_by_nlp(main_sent, word_dict, method='method', mode='HMM')
            new_business_info = mgdm.init_business_dialog(new_ners, main_sent)
            if 'scenario' in new_business_info:
                business_info['scenario'] = new_business_info['scenario']
        if 'scenario' in business_info:
            params['data']['scenario'] = business_info['scenario']
        if 'operation' in business_info:
            params['data']['type'] = business_info['type']
            params['data']['operation'] = business_info['operation']
    # mgdm.record_dialog_model(params)
    return business_info


def update_client_dialog_info(inp, dia):
    """
    任务：
    1.客服核心返回的答案信息+用户数据，编码生成区分用户和平台的唯一性id
    2.绑定缓存唯一性id和回复信息
    3.输出绑定唯一性缓存id
    :param inp:
    :param dia:
    :return:dic {
                "success":True,//返回码，是否操作成功
                "data":data
                "error":""//错误信息输出
                }
    """
    cache_id = mgdm.update_dialog_model(inp, dia)
    response = mgdm.compose_response(inp, cache_id)
    return response


def transfer_result_to_response(inp, response, dia):
    """
    任务：
    1.从客服引擎返回的答案数据取必要数据，并格式化
    2.组合用户对话唯一性缓存id，推送返回
    :param inp:
    :param dia:
    :return:dic {
                "success":True,//返回码，是否操作成功
                "data":data
                "error":""//错误信息输出
                }
    """
    if 'answer' in response and response['answer'] == '':
        response['answer'] = turing_interface.generate_turing_response(inp)
    response_ = mgdm.transfer_response(inp, response, dia)
    return response_


def continue_to_go_or_not(inp):
    if inp['success']:
        return True
    else:
        return False


def generate_response(main_sent, keywords, ners, relations, type):
    """
    答案抽取
    :param main_sent:
    :param keywords:
    :param ners:
    :param relations:
    :param type:
    :return:
    第一步：FAQ主题词精确匹配
    第二步：匹配中的候选问答评分
    若
    """
    main_keywords_set = ''
    best_answer = ''
    if main_sent:
        main_keywords_set = jieba_nlp.generate_jieba_cut(main_sent)
        main_keywords_set = ' '.join(main_keywords_set)
        main_keywords_set = main_keywords_set.split()
        synonyms_words = mgaics.siphon_synonyms_words(main_keywords_set)
    if keywords:
        like_is = True
        if main_sent == keywords:
            like_is = False
        sets = fetch_sets_by_words(keywords, like_is)
        if sets:
            for i in range(len(list(sets))):
                if sets[i].question:
                    ques_ = mgaics.remove_partial_and_special(sets[i].question)
                    try:
                        ques_keywords_set = jieba_nlp.generate_jieba_cut(ques_)
                        ques_keywords_set = ' '.join(ques_keywords_set)
                        ques_keywords_set = ques_keywords_set.split()
                        ques_keywords_set = mgaics.replace_synonyms_words(main_keywords_set, ques_keywords_set,
                                                                          synonyms_words)
                        simi = agwv.generate_sets_simi(ques_keywords_set, main_keywords_set)
                    except Exception as error:
                        if main_sent == ques_:
                            sets[i].simi = '1'
                        else:
                            sets[i].simi = '0'
                        continue
                    else:
                        sets[i].simi = str(simi)[0:5]
                        del simi
                        del ques_
                        agwv.clear_mem()
                        # print(sets[i].question, sets[i].simi)
            agwv.clear_mem()
            sets = sorted(sets, key=lambda qa: qa.simi, reverse=True)
            best_answer = generate_best_answer(sets, main_sent)
    if best_answer is None and ners:
        sets = fetch_sets_by_words(ners, False)
        if sets:
            for i in range(len(list(sets))):
                if sets[i].question:
                    ques_ = mgaics.remove_partial_and_special(sets[i].question)
                    try:
                        ques_keywords_set = jieba_nlp.generate_jieba_cut(ques_)
                        ques_keywords_set = ' '.join(ques_keywords_set)
                        ques_keywords_set = ques_keywords_set.split()
                        ques_keywords_set = mgaics.replace_synonyms_words(main_keywords_set, ques_keywords_set,
                                                                          synonyms_words)
                        simi = agwv.generate_sets_simi(ques_keywords_set, main_keywords_set)
                    except Exception as error:
                        if main_sent == ques_:
                            sets[i].simi = '1'
                        else:
                            sets[i].simi = '0'
                        continue
                    else:
                        sets[i].simi = str(simi)[0:5]
                        del simi
                        del ques_
                        agwv.clear_mem()
                        # print(sets[i].question, sets[i].simi)
            agwv.clear_mem()
            sets = sorted(sets, key=lambda qa: qa.simi, reverse=True)
            best_answer = generate_best_answer(sets, main_sent)
    return best_answer


def fetch_sets_by_words(keywords, like=False):
    """
    关键词匹配
    :param keywords:
    :return:
    """
    try:
        if isinstance(keywords, list):
            keywords = ','.join(keywords)
        data = []
        if keywords.strip() == '':
            return data
        if like:
            data = Question_auto.objects.filter(words__startswith=keywords)[:10]
        else:
            data = Question_auto.objects.filter(words=keywords)[:10]
            # print(keywords,data)
    except Exception as error:
        # Question_auto.roll_back()
        return str(error)
    else:
        return data


def update_keywords_from_question(keywords=''):
    questions = Question_auto.objects.filter(words=keywords).values("id", "question")[:40]
    while questions:
        for question in questions:
            sent = question['question']
            main_sent = mgaics.remove_useless_and_correction(sent)
            keywords_ = mgaics.siphon_keywords_by_grammar(main_sent)
            # print('keywords', keywords_)
            Question_auto.objects.filter(id=question['id']).update(**{'words': ','.join(keywords_)})
        # exit()
        questions = Question_auto.objects.filter(words=keywords).values("id", "question")[:40]
    return 'success'


def synonymous_sentence_matching(ques):
    """"""
    # 进行同义句匹配，若是匹配上，直接返回答案
    # same_sen = Mysql()
    result = Synonym_sentence.objects.filter(sentence=ques)
    answer_value = ''
    # if
    # for ele in result:
    #     if abs(len(ques) - len(ele.sentence))
    # same_sen.dispose()
    if result:
        if result[0].type == 1:
            result_answer = Question_t.objects.filter(qid=result[0].qid)
            # same_sen.dispose()
            if len(result_answer):
                answer_value = result_answer[0].answer
        else:
            result_an = Synonym_sentence.objects.get(id=result[0].rel_sentence_id)
            # same_sen.dispose()
            result_ans = Question_t.objects.filter(qid=result_an.qid)
            # same_sen.dispose()
            if len(result_ans):
                answer_value = result_ans[0].answer
    result = Synonym_sentence.objects.filter(sentence__contains=ques)
    if not result or len(ques) < 6:
        return answer_value
    else:
        if abs(len(ques) - len(result[0].sentence))<2:
            if result[0].type == 1:
                result_answer = Question_t.objects.filter(qid=result[0].qid)
                # same_sen.dispose()
                if len(result_answer):
                    answer_value = result_answer[0].answer
            else:
                result_an = Synonym_sentence.objects.get(id=result[0].rel_sentence_id)
                # same_sen.dispose()
                result_ans = Question_t.objects.filter(qid=result_an.qid)
                # same_sen.dispose()
                if len(result_ans):
                    answer_value = result_ans[0].answer

    return answer_value


def is_origin_question(question):
    if question:
        data = Question_auto.objects.filter(question=question)[:1]
        if data:
            return data[0].answer
    return None
