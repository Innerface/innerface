# Author: YuYuE (1019303381@qq.com) 2018.01.22
from pyltp import *
import os
from nltk.tree import Tree
from nltk.grammar import DependencyGrammar
from nltk.parse import *
from chatbot.settings import BASE_DIR
import vendor.nlp.nlp_jieba_model as jieba_nlp
from chatbot.settings import ONTOLOGY
from chatbot.settings import ATTR
import vendor.nlp.nlp_chinese_grammar as chinese_grammar

ltp_path = BASE_DIR + "/vendor/dataset/ltp_data/"
# ltp相关数据文件配置
cws_model = ltp_path + "cws.model"
ner_model = ltp_path + "ner.model"
parser_model = ltp_path + "parser.model"
pisrl_model = ltp_path + "pisrl.model"
pos_model = ltp_path + "pos.model"


# 分词
def generate_segement(sentence):
    """
    ltp分词
    :param sentence:
    :return:
    """
    segmentor = Segmentor()
    segmentor.load(cws_model)
    segment_result = segmentor.segment(sentence)
    segmentor.release()
    return segment_result


# 词性标注
def generate_postag(sentence, segment_result=False):
    """
    ltp词性标注
    :param sentence:
    :param segment_result:
    :return:
    """
    if segment_result is False:
        segment_result = generate_segement(sentence)
    # 词性标注
    postagger = Postagger()
    postagger.load(pos_model)
    postag_result = postagger.postag(segment_result)
    postagger.release()
    return postag_result


# 命名实体识别
def generate_recongnize(sentence, segment_result=False, postag_result=False):
    """
    ner识别
    :param sentence:
    :param segment_result:
    :param postag_result:
    :return:
    """
    if segment_result is False:
        segment_result = generate_segement(sentence)
    if postag_result is False:
        postag_result = generate_postag(sentence)
    recognizer = NamedEntityRecognizer()
    recognizer.load(ner_model)
    recognize_result = recognizer.recognize(segment_result, postag_result)
    recognizer.release()
    return recognize_result


# 依存句法分析
def generate_parse(sentence, segment_result=False, postag_result=False):
    """
    依存成分分析
    :param sentence:
    :param segment_result:
    :param postag_result:
    :return:
    """
    if segment_result is False:
        segment_result = generate_segement(sentence)
    if postag_result is False:
        postag_result = generate_postag(sentence)
    parser = Parser()
    parser.load(parser_model)
    parse_result = parser.parse(segment_result, postag_result)
    parser.release()  # 释放模型
    return parse_result


def generate_dependency_graph(sentence, segment_result=False, postag_result=False, parse_result=False):
    """
    依存树
    :param sentence:
    :param segment_result:
    :param postag_result:
    :param parse_result:
    :return:
    """
    if segment_result is False:
        segment_result = generate_segement(sentence)
    if postag_result is False:
        postag_result = generate_postag(sentence)
    if parse_result is False:
        parse_result = generate_parse(sentence, segment_result, postag_result)
    arclen = len(parse_result)
    conll = ""
    for i in range(arclen):
        if parse_result[i].head == 0:
            parse_result[i].relation = "ROOT"
        conll += "\t" + segment_result[i] + "(" + postag_result[i] + ")" + "\t" + postag_result[i] + "\t" + str(
            parse_result[i].head) + "\t" + parse_result[
                     i].relation + "\n"
    conlltree = DependencyGraph(conll)
    tree = conlltree.tree()
    # tree.draw()
    return tree


def generate_sementic_role(sentence, segment_result=False, postag_result=False, recognize_result=False,
                           parse_result=False):
    """
    语义角色
    :param sentence:
    :param segment_result:
    :param postag_result:
    :param recognize_result:
    :param parse_result:
    :return:
    """
    if segment_result is False:
        segment_result = generate_segement(sentence)
    if postag_result is False:
        postag_result = generate_postag(sentence)
    if parse_result is False:
        parse_result = generate_parse(sentence, segment_result, postag_result)
    if recognize_result is False:
        recognize_result = generate_recongnize(sentence, segment_result, postag_result)
    labeller = SementicRoleLabeller()
    labeller.load(os.path.join(ltp_path, 'srl/'))
    roles = labeller.label(segment_result, postag_result, recognize_result, parse_result)
    wordlist = list(segment_result)
    relations = {}
    i = 0
    for role in roles:
        temp = {}
        # print("rel:", wordlist[role.index])
        temp['rel'] = wordlist[role.index]
        for arg in role.arguments:
            if arg.range.start != arg.range.end:
                # print(arg.name, " ".join(wordlist[arg.range.start:arg.range.end]))
                temp[arg.name] = " ".join(wordlist[arg.range.start:arg.range.end])
            else:
                # print(arg.name, wordlist[arg.range.start])
                temp[arg.name] = wordlist[arg.range.start]
        relations[i] = temp
        i += 1
    labeller.release()
    return relations


# 去停用词分词
def generate_segment_after_remove_stop_words(sentence, path=False, segment_result=False):
    """
    去除停用词的分词
    :param sentence:
    :param path:
    :param segment_result:
    :return:
    """
    if path is False:
        path = BASE_DIR + "/vendor/dataset/chinese/stopwords.dat"
    stopwords = fetch_stop_words(path)
    if segment_result is False:
        segment_result = generate_segement(sentence)
    result = []
    for seg in segment_result:
        seg = chinese_grammar.predicate_transfer(seg)
        if seg not in stopwords:
            result.append(seg)
    return result


# 获取停用词
def fetch_stop_words(path="../data/chinese/stopwords.dat"):
    """
    组装停用词
    :param path:
    :return:
    """
    try:
        if os.path.exists(path) is False:
            raise Exception("file not exists")
        infile = open(path, 'r', encoding='utf-8')
        stopwordslist = []
        for str in infile.read().split('\n'):
            if str not in stopwordslist:
                stopwordslist.append(str)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return stopwordslist


def siphon_words_with_tags(sentence, keywords=None):
    word_dict = {}
    if keywords is None:
        keywords_ = jieba_nlp.generate_jieba_cut(sentence, False, True)
        keywords_ = " ".join(keywords_)
        keywords = keywords_.split()
    postag = generate_postag(sentence, keywords)
    i = 0
    for keyword, pos in zip(keywords, postag):
        if keyword and pos:
            keyword = chinese_grammar.predicate_transfer(keyword)
            if keyword in word_dict:
                i += 1
                if keyword + pos in word_dict:
                    word_dict[keyword + pos * i] = pos
                else:
                    word_dict[keyword + pos] = pos
            else:
                word_dict[keyword] = pos
    return word_dict


def default_named_type():
    return ['n', 'nh', 'ni', 'nl', 'ns', 'nt', 'nz']


def focal_type_with_weight():
    return {
        'n': 3,
        'v': 2,
        'r': 0.9,
        'd': 0.1
    }


def siphon_ners_by_nlp(sentence, word_dict=None, keywords=None):
    ners = []
    if word_dict:
        word_dict = siphon_words_with_tags(sentence, keywords)
    previous = ''
    ner_type = default_named_type()
    if word_dict:
        for (word, tag) in word_dict.items():
            if tag in ner_type:
                if previous in ner_type:
                    word = word.replace(tag, '')
                    if word in ONTOLOGY or word in ATTR:
                        ners.append(word)
                    else:
                        temp = ners.pop()
                        ners.append(temp + word)
                else:
                    word = word.replace(tag, '')
                    ners.append(word)
            previous = tag
    return ners


if __name__ == "__main__":
    sentence = "据悉，2013年4月，农行先后与湖南、重庆、四川、云南等省市签署城镇化与金融服务的战略合作备忘录。"
    ners = siphon_ners_by_nlp(sentence)
    print(ners)
    exit()
    segment = generate_segement(sentence)
    postag = generate_postag(sentence, segment)
    for seg, pos in zip(segment, postag):
        print(seg, pos)
    nostop = generate_segment_after_remove_stop_words(sentence, False, segment)
    print(nostop)
    recognize_result = generate_recongnize(sentence, segment, postag)
    for seg, reco in zip(segment, recognize_result):
        print(seg, reco)
    # print(recognize_result)
    par = generate_parse(sentence, segment, postag)
    result = generate_dependency_graph(sentence, segment, postag, par)
    print(result)
    result = generate_sementic_role(sentence, segment, postag, recognize_result, par)
    print(result)
