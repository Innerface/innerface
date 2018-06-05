# Author: YuYuE (1019303381@qq.com) 2018.01.18
import warnings

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim
from gensim import matutils
import jieba
import os
import re
import gc
import time
import numpy as np
import pathlib
from gensim.models.word2vec import LineSentence
import multiprocessing
from chatbot.settings import BASE_DIR
from chatbot.settings import WORD2VECMODEL


# print("加载model：",time.time())
# model = gensim.models.Word2Vec.load(str(pathlib.Path(BASE_DIR)/"dataset"/"wordVec"/"baike_1.jieba.split.model"))
# model = gensim.models.Word2Vec.load(os.path.dirname(os.path.abspath(__file__)) + "/data/wordVec/wiki.zh.jieba.model")
# model = gensim.models.Word2Vec.load(BASE_DIR+"/vendor/dataset/wordVec/faq/faq_origin.model")
# model.init_sims(replace=True)
model = WORD2VECMODEL


def set_default_model(mode):
    if mode == 'faq':
        model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/faq/faq_origin.model")
    elif mode == 'baike':
        model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/baike_1.jieba.split.model")
    else:
        model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/wiki.zh.jieba.model")
    return model


# 获取词语向量
def generate_vec(word):
    try:
        if len(word) < 1:
            raise Exception("参数错误")
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return model[word]


# 获取词语近义词
def generate_posit(word):
    try:
        if len(word) < 1:
            raise Exception("参数错误")
        result = model.most_similar(positive=[word])
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 获取词语反义词
def generate_nagat(word):
    try:
        if len(word) < 1:
            raise Exception("参数错误")
        result = model.most_similar(negative=[word])
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 获取词语之间相似度
def generate_words_simi(word1, word2):
    try:
        if len(word1) < 1:
            raise Exception("para1 参数错误")
        if len(word1) < 1:
            raise Exception("para2 参数错误")
        result = model.similarity(word1, word2)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 计算两个集合之间的余弦相似度
def generate_sets_simi(set1, set2):
    try:
        if len(set1) < 1:
            raise Exception("para1 参数错误")
        if len(set2) < 1:
            raise Exception("para2 参数错误")
        result = model.n_similarity(set1, set2)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 直接计算语句相似度
def generate_sentence_simi(sentence1, sentence2):
    try:
        if len(sentence1) < 1:
            raise Exception("para1 参数错误")
        if len(sentence2) < 1:
            raise Exception("para2 参数错误")
        sentence1 = remove_special_tags(sentence1)
        set1 = jieba.cut(str(sentence1))
        set1 = ' '.join(set1)
        set1 = set1.split()
        sentence2 = remove_special_tags(sentence2)
        set2 = jieba.cut(str(sentence2))
        set2 = ' '.join(set2)
        set2 = set2.split()
        result = model.n_similarity(set1, set2)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 获取集合中不同类的词语
def choose_diff_member(sets):
    try:
        if len(sets) < 1:
            raise Exception("para1 参数错误")
        result = model.doesnt_match(sets)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 自行封装句子相似度计算方法
def generate_sets_simi_by_self(set1, set2):
    try:
        if len(set1) < 1:
            raise Exception("para1 参数错误")
        if len(set2) < 1:
            raise Exception("para2 参数错误")
        v1 = v2 = []
        for set1_ in set1:
            v1.append(model[set1_])
            del set1_
        for set2_ in set2:
            v2.append(model[set2_])
            del set2_
        result = np.dot(matutils.unitvec(np.array(v1).mean(axis=0)), matutils.unitvec(np.array(v2).mean(axis=0)))
        del v1
        del v2
        del set1
        del set2
        gc.collect()
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return result


# 余弦相似度计算句子相似度,基于字
def generate_sentence_simi_with_cos_by_unit(sentence1, sentence2):
    try:
        if len(sentence1) < 1 or len(sentence2) < 1:
            raise Exception("Exception: param 参数错误")
        sentence_vector1 = generate_sentence_vector_by_unit_vector(sentence1)
        sentence_vector2 = generate_sentence_vector_by_unit_vector(sentence2)
        num = float(np.sum(sentence_vector1 * sentence_vector2))
        denom = np.linalg.norm(sentence_vector1) * np.linalg.norm(sentence_vector2)
        cos = num / denom
    except Exception as error:
        raise Exception('Exception:', error)
    else:
        return cos


# 通过字向量组装句向量,直接将句分解成字
def generate_sentence_vector_by_unit_vector(sentence):
    try:
        if len(sentence) < 1:
            raise Exception("para1 参数错误")
        sentence_unit_str = ' '.join(sentence)
        sentence_units = sentence_unit_str.split()
        sentence_vector = np.zeros([1, 200])
        for unit in sentence_units:
            sentence_vector += model[unit]
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return sentence_vector


# 通过已经完成切分的词的向量组装句向量,word_set为数组或者list
def generate_sentence_vector_by_word_vector(word_set):
    try:
        if len(word_set) < 1:
            raise Exception("para1 参数错误")
        sentence_vector = np.zeros([1, 200])
        for word in word_set:
            sentence_vector += model[word]
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return sentence_vector


# 去除标点符号
def remove_special_tags(str_):
    r = '[’!"#$%&\'()*+,-./:;<=>?？，。！@[\\]^_`{|}~]+'
    result = re.sub(r, '', str_)
    return result


# 释放内存
def clear_mem():
    # del model
    gc.collect()


def words_evaluation(words1, words2, eval_='银行'):
    """
    评估转换前后词的合理性，若转换前更合理，则不做转换
    :param words1:
    :param words2:
    :param eval_:
    :return:
    """
    if words1 not in model and words2 in model:
        result = words2
    elif words1 in model and words2 not in model:
        result = words1
    elif words1 not in model and words2 not in model:
        result = None
    else:
        simi1 = generate_words_simi(words1, eval_)
        simi2 = generate_words_simi(words2, eval_)
        if simi1 > simi2:
            result = words1
        else:
            result = words2
    return result


def train_word_vector_with_file(file_path, model_=None, vector_=None, width=200, window=5, min_count=1):
    try:
        model = gensim.models.Word2Vec(LineSentence(file_path), size=width, window=window, min_count=min_count,
                     workers=multiprocessing.cpu_count())
        model.save(model_)
        model.wv.save_word2vec_format(vector_, binary=False)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return 'operation successfully'


def update_word_vector_with_file(file_path, model_=None, vector_=None):
    try:
        model = gensim.models.Word2Vec.load(model_)
        more_sentences = LineSentence(file_path)
        model.build_vocab(more_sentences, update=True)
        model.train(more_sentences, total_examples=model.corpus_count, epochs=model.iter)
        model.save(model_)
        model.wv.save_word2vec_format(vector_, binary=False)
    except Exception as error:
        raise Exception("Exception:", error)
    else:
        return 'operation successfully'


# 调用样例
if __name__ == "__main__":
    try:
        print('银行' in WORD2VECMODEL)
        # exit()
        # result = generate_vec('银行')
        # print (result)
        # result = generate_posit('胜利')
        # for res in result:
        # 	print (res)
        # result = generate_nagat('失败')
        # for res in result:
        # 	print (res)
        # result = generate_words_simi('足球','看球')
        # print (result)

        # sentences = [u"怎么办理中国银行信用卡",u"怎么办理借记卡",u"怎么提升信用卡额度",u"怎么办理信用卡",u"怎么办理宽带",u"怎么去香港",u"我想吃海鲜"]
        # question = u"怎么办理信用卡"
        # set1 = jieba.cut(question)
        # set1 = ' '.join(set1)
        # set1 = set1.split()
        # for sentence in sentences:
        # 	set2 = jieba.cut(sentence)
        # 	set2 = ' '.join(set2)
        # 	set2 = set2.split()
        # 	result = generate_sets_simi(set1,set2)
        # 	print (question+"====>"+sentence+"\r\n  相似度：" + str(result))

        # result = choose_diff_member(['爸爸','足球','篮球','排球'])
        # print (result)
        sentence1 = "我要办中国银行信用卡"
        sentence2 = "怎么办理中国银行信用卡"
        # result = generate_sentence_simi_with_cos_by_unit(sentence1, sentence2)
        # print(result)
        # result = generate_sentence_simi(sentence1,sentence2)
        word1 = "信用卡"
        word2 = "额度"
        result = generate_sentence_simi_with_cos_by_unit(word1, word2)
        print(result)
        result = generate_words_simi(word1, word2)
        print(result)
    except Exception as error:
        print("Exception:", error)
