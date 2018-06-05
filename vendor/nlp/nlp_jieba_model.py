# Author: YuYuE (1019303381@qq.com) 2018.01.18
import jieba
import jieba.posseg as pseg
import os
from jieba import analyse
from chatbot.settings import BASE_DIR
import vendor.nlp.nlp_chinese_grammar as chinese_grammar


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# import common_function_model
# 标准分词，cut_all是否采用全模式，hmm是否采用hmm模型
def generate_jieba_cut(sentence, cut_all=False, hmm=False):
    """
    cut分词，标准模式分词
    :param sentence:
    :param cut_all: 是否全模式
    :param hmm: 是否开启新词发现
    :return:
    """
    try:
        if len(sentence) < 1:
            raise Exception("please input something to me!")
        result = jieba.cut(sentence, cut_all=cut_all, HMM=hmm)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 搜索式分词，hmm是否采用hmm模型
def generate_jieba_cut_search(sentence, hmm=False):
    """
    搜索模式分词
    :param sentence:
    :param hmm: 是否开启新词发现
    :return:
    """
    try:
        if len(sentence) < 1:
            raise Exception("please input something to me!")
        result = jieba.cut_for_search(sentence, HMM=hmm)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 直接文件分词
def generate_jieba_cut_file(file, cut_all=False, hmm=False, search=False):
    """
    以文件作为分词处理对象
    :param file:
    :param cut_all: 是否全模式
    :param hmm: 是否开启新词发现
    :param search: 是否搜索模式
    :return:
    """
    try:
        if not os.path.exists(file):
            raise Exception("file not exists")
        file_open = open(file, 'r', encoding='utf-8')
        contents = file_open.read()
        if not search:
            result = jieba.cut(contents, cut_all=cut_all, HMM=hmm)
        else:
            result = jieba.cut_for_search(contents, HMM=hmm)
        output = file + ".jieba.out"
        file_out = open(output, 'w', encoding='utf-8')
        file_out.write(" ".join(result))
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return output


# 对输入语句去停用词操作
def remove_stop_words_by_jieba(sentence, hmm=True):
    """
    分词标注并剔除停用词操作，注意这里的停用词数量上来之后，循环加载将带来低效
    :param sentence:
    :return:
    """
    try:
        if len(sentence) < 1:
            raise Exception("please input something to me!")
        # sentence = common_function_model.remove_special_tags(sentence)
        result = pseg.cut(sentence, HMM=hmm)
        path = BASE_DIR + "/vendor/dataset/chinese/stopwords.dat"
        stopwords = fetch_stop_words(path)  # 这里加载停用词的路径
        outstr = []
        for word, flag in result:
            # print(word + ',' + flag)
            if word not in stopwords:
                # if word != '\t' and flag == 'n':
                word = chinese_grammar.predicate_transfer(word)
                if len(word) > 1 and (flag == 'vn' or flag == 'n' or flag == 'v' or flag == 'nr'):
                    outstr.append(word)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return outstr


# 获取停用词
def fetch_stop_words(path="./data/chinese/stopwords.dat"):
    """
    组装停用词
    :param path:
    :return:
    """
    try:
        if os.path.exists(path) == False:
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


# 同义词词林

# TF-IDF关键词抽取
def generate_tf_idf_keywords(sentence):
    """
    tfidf关键词提取
    :param sentence:
    :return:
    """
    try:
        if len(sentence) < 1:
            raise Exception("sentence empty")
        tfidf = analyse.extract_tags
        keywords = tfidf(sentence)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return keywords


# TextRank抽取关键词
def generate_text_rank_keywords(sentence):
    """
    textrank抽取关键词
    :param sentence:
    :return:
    """
    try:
        if len(sentence) < 1:
            raise Exception("sentence empty")
        textrank = analyse.textrank
        keywords = textrank(sentence)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return keywords


def load_userdic():
    jieba.load_userdict(BASE_DIR + "/vendor/dataset/chinese/candidatesAll.txt")


def sreach_mode_and_calibration(sent):
    """
    极端搜索模式分词，再根据原句做筛选校验
    :param sent:
    :return:
    """
    keywords = []
    if sent:
        segment = generate_jieba_cut_search(sent, hmm=True)
        if segment:
            min_len = 0
            segment = segment.sort()
            for seg in segment:
                if len(seg) > min_len:
                    pass
    return


# 样例测试
if __name__ == "__main__":
    sentence = "银行汇票和银行本票的区别有那些"
    sentence = '信用卡办理'
    result = pseg.cut(sentence, True)
    for word, tag in result:
        print(word, tag)
    result = generate_jieba_cut(sentence)
    print(' '.join(result))
    result = generate_jieba_cut_search(sentence)
    print(' '.join(result))
    result = generate_tf_idf_keywords(sentence)
    print(result)
    result = generate_text_rank_keywords(sentence)
    print(result)
