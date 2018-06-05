# Author: YuYuE (1019303381@qq.com) 2018.03.16
import vendor.nlp.nlp_pinyin_hanzi_transfer as ph_transfer
import vendor.nlp.nlp_jieba_model as jieba_model
import vendor.nlp.nlp_stanford_by_java_model as stanford_model
import vendor.nlp.nlp_ltp_model as ltp_model
from chatbot.settings import SYNONYMS
from data_admin.models import Question_auto


def default_VP():
    return ['是啥', '是什么', '什么是', '是什么意思']


def default_CC():
    return ['的', '和', '与', '跟']


def default_synonyms():
    return SYNONYMS


def keywords_sort(words):
    """
    关键词统一按音节排序
    :param words:
    :return:
    """
    word_sort = []
    if words:
        words_p = []
        for word in words:
            hp_ = ph_transfer.transfer_hanzi_to_pinyin(word)
            if hp_:
                words_p.append(hp_)
        words_p_s = sorted(words_p)
        for word_p in words_p_s:
            index = words_p.index(word_p)
            word_sort.append(words[index])
    return word_sort


def siphon_keywords_and_sort(sent, method='jieba'):
    """
    抽取关键词，并作排序
    :param sent:
    :param method:
    :return:
    """
    keywords_sorted = []
    if sent:
        if method == 'jieba':
            keywords = jieba_model.remove_stop_words_by_jieba(sent, True)
        else:
            keywords = ltp_model.generate_segment_after_remove_stop_words(sent)
        # print('inner', keywords)
        if keywords:
            keywords_sorted = keywords_sort(keywords)
        else:
            inner_vp = ''
            vps = default_VP()
            for vp in vps:
                if sent.find(vp) != -1:
                    inner_vp = vp
            if inner_vp:
                infos = sent.split(inner_vp)
                if infos:
                    len_temp = 0
                    for info in infos:
                        if len(info) > len_temp:
                            keywords_sorted = info
                            len_temp = len(info)
            else:
                keywords_sorted = sent
    return keywords_sorted


def siphon_sentence_patial(sent):
    """
    句子成分抽取
    :param sent:
    :return:
    """
    if sent:
        segment = jieba_model.generate_jieba_cut(sent)
        print(segment)
        segment = ' '.join(segment)
        ner = stanford_model.generate_ner(segment)
    return ner


def encode_question_into_pickle(keywords=''):
    questions = Question_auto.objects.filter(words=keywords).values("id", "question")[:40]
    while questions:
        for question in questions:
            sent = question['question']
        questions = Question_auto.objects.filter(words=keywords).values("id", "question")[:40]
    return
