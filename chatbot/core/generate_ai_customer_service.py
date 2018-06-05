# Author: YuYuE (1019303381@qq.com) 2018.03.16
import re
from itertools import groupby

from vendor.optimization import keywords_sorted as doks
from vendor.algorithm.word2vec import generate_word_vector as vectormodel
from vendor.nlp import nlp_pinyin_hanzi_transfer as phtransfer
from vendor.nlp import nlp_stanford_by_java_model as stanford_java
from vendor.nlp import nlp_jieba_model as jieba_nlp
from vendor.nlp import nlp_ltp_model as ltp_nlp
from vendor.nlp import nlp_chinese_grammar as chinese_nlp


def remove_special_tags(str_):
    """
    特殊字符处理,可选择性配置
    :param str_:
    :return:
    """
    r = '[’!"#$%&\'()*+,-./:;<=>?？。！￥……【】、，：；‘’”“@[\\]^_`{|}~]+'
    result = re.sub(r, '', str_)
    return result


def remove_modal_particle(str_):
    """
    语气助词处理，可选择性配置
    :param str_:
    :return:
    """
    modal_particle = ['阿', '啊', '呃', '欸', '哇', '呀', '哦', '耶', '哟', '欤', '呕', '噢', '呦', '吧', '罢', '呗', '啵', '嘞', '哩',
                      '咧', '咯', '啰', '喽', '吗', '嘛', '呢', '呐', '噻', '嘢']
    for particle in modal_particle:
        if str_.find(particle) != -1:
            str_ = str_.replace(particle, '')
    return str_


def remove_partial_and_special(sent):
    sent = remove_special_tags(sent)
    sent = remove_modal_particle(sent)
    return sent


def replace_synonyms_words(main_sent_set, words, synonyms_words=False):
    """
    同义词替换
    :param main_sent_set:
    :param words:
    :param synonyms_words:
    :return:
    """
    if words and main_sent_set and synonyms_words:
        words_str = ' '.join(words)
        main_sent_set_str = ' '.join(main_sent_set)
        synonyms = doks.default_synonyms()
        if synonyms:
            for key in synonyms.keys():
                if main_sent_set_str.find(key) != -1 and words_str.find(synonyms[key]) != -1:
                    words_str = words_str.replace(synonyms[key], key)

            words = words_str.split()
    return words


def siphon_synonyms_words(main_sent_set):
    """
    根据问题找到可能的同义词，较上一个方法效率
    :param main_sent_set:
    :return:
    """
    synonyms_words = False
    if main_sent_set:
        main_sent_set_str = ' '.join(main_sent_set)
        synonyms = doks.default_synonyms()
        if synonyms:
            for key in synonyms.keys():
                if main_sent_set_str.find(key) != -1:
                    synonyms_words = True
    return synonyms_words


def groupby_subscript(lst):
    """
    连续下标分组
    :param lst:
    :return:
    """
    groups = []
    fun = lambda x: x[1] - x[0]
    for k, g in groupby(enumerate(lst), fun):
        groups.append([v for i, v in g])
    return groups


def remove_useless_and_correction(inp):
    """
    去除与语义无关的杂项，并做中文纠正
    1.去除多余标点符号
    2.拼音识别
    3.拼音转换
    4.去语气助词
    :param inp:
    :return:
    """
    step_one_str = remove_special_tags(inp)
    is_with_alphabet = False
    inner_alphabet = ''
    pos_alphabet = []
    i = 0
    for vchar in step_one_str:
        if phtransfer.is_alphabet(vchar):
            is_with_alphabet = True
            inner_alphabet += vchar
            pos_alphabet.append(i)
        i += 1
    if is_with_alphabet:
        groups = groupby_subscript(pos_alphabet)
        if len(groups) > 1:
            increase_or_decrease = 0
            for group in groups:
                item = ''
                for index in group:
                    item += step_one_str[index - increase_or_decrease]
                item_to_hanzi = phtransfer.transfer_continue_pinyin_to_hanzi(item)
                item_to_hanzi_ = ''.join(item_to_hanzi)
                eval_item = vectormodel.words_evaluation(item, item_to_hanzi_)
                if eval_item is not None and eval_item != item:
                    step_one_str = step_one_str.replace(item, item_to_hanzi_)
                    increase_or_decrease = len(item) - len(''.join(item_to_hanzi))
        else:
            alphabet_to_hanzi = phtransfer.transfer_continue_pinyin_to_hanzi(inner_alphabet)
            alphabet_to_hanzi_ = ''.join(alphabet_to_hanzi)
            eval_item = vectormodel.words_evaluation(inner_alphabet, alphabet_to_hanzi_)
            if eval_item is not None and inner_alphabet != eval_item:
                step_one_str = step_one_str.replace(inner_alphabet, eval_item)
    else:
        pass
    step_two_str = remove_modal_particle(step_one_str)
    return step_two_str


def split_sentence_to_words(sentence, method='method', mode='HMM'):
    if sentence:
        word_dict = ltp_nlp.siphon_words_with_tags(sentence)
    else:
        word_dict = None
    return word_dict


def corrected_sentence_by_pinyin(sentence):
    sentence_temp = phtransfer.correct_hanzi_by_pinyin_transfer(sentence)
    return ''.join(sentence_temp)


def siphon_keywords_by_grammar(sentence):
    return doks.siphon_keywords_and_sort(sentence)


def siphon_ners_by_nlp(sentence, word_dict, method='method', mode='HMM'):
    if sentence and word_dict:
        ners = ltp_nlp.siphon_ners_by_nlp(sentence, word_dict)
    else:
        ners = None
    return ners


def siphon_type_by_grammar(word_dict, mode='ltp'):
    type_ = 'status'
    if word_dict:
        pronoum = ''
        human_pronoun = chinese_nlp.default_human_pronoun()
        instruction_pronoum = chinese_nlp.default_instruction_pronoum()
        for (word, tag) in word_dict.items():
            if mode == 'ltp':
                if tag == 'r' and (word not in human_pronoun) and (word not in instruction_pronoum):
                    pronoum = word
            elif mode == 'stanford':
                if tag == 'PN' and (word not in human_pronoun) and (word not in instruction_pronoum):
                    pronoum = word
            else:
                pronoum = ''
        if pronoum:
            type_operation = chinese_nlp.default_operation_interrogative_pronoum()
            if pronoum in type_operation:
                type_ = 'operation'
            else:
                type_ = 'status'
        else:
            if 'n' in word_dict.values() and 'v' in word_dict.values():
                type_ = 'operation'
            else:
                type_ = 'status'
    return type_


def text_classification(sentence, word_dict=None, references=None):
    if references:
        if 'type' in references and references['type'] in ['操作', '业务']:
            type_ = 'operation'
        else:
            type_ = 'status'
    else:
        if word_dict:
            type_ = siphon_type_by_grammar(word_dict)
        else:
            type_ = 'status'
    return type_


def generate_response(sentence, keywords='', ners=None, relations=None, type=None):
    """
    答案抽取模块，基本流程
    1.FAQ匹配
    2.知识图谱
    3.文档
    4.互联网资源
    :param words_split:
    :param keywords:
    :param ners:
    :param relations:
    :param type:
    :return:
    """
    response = faq_search(keywords, sentence)
    return response


def faq_search(keywords, sentence):
    return sentence
