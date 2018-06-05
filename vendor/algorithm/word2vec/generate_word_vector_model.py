# Author: YuYuE (1019303381@qq.com) 2018.01.18
import logging
import os
import sys
import multiprocessing
import vendor.nlp.nlp_jieba_model as jieba_nlp
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence


# 词向量模型训练
def train_word_vector_model(input):
    try:
        # 进程进度日志输出
        program = os.path.basename(__file__)
        logger = logging.getLogger(program)
        logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
        logging.root.setLevel(level=logging.INFO)
        logger.info("running %s" % ' '.join(sys.argv))
        # 检查文件是否存在
        if not os.path.exists(input):
            raise Exception("file not exists")
        # 模型文件存储
        #  file_name = os.path.basename(input)
        outp1 = input + ".model"
        outp2 = input + ".vector"
        # 训练模型
        model = Word2Vec(LineSentence(input), size=200, window=5, min_count=5, workers=multiprocessing.cpu_count())
        # 保存模型数据
        model.save(outp1)
        # 保存向量数据
        model.wv.save_word2vec_format(outp2, binary=False)
    except Exception as error:
        raise Exception("Exception:" + str(error))
    else:
        return [outp1, outp2]


# 使用模型数据
def word_vector_model_for_product(word, file):
    try:
        if not os.path.exists(file):
            raise Exception("file not exists")
        model = Word2Vec.load(file + ".model")
        result = model.most_similar(positive=[word])
    except Exception as error:
        raise Exception("Exception:" + str(error))
    else:
        for res in result:
            print(res)


# 对原始语料做jieba分词处理
def split_word_by_jieba(file):
    output = jieba_nlp.generate_jieba_cut_file(file)
    return output


# 样例使用
if __name__ == "__main__":
    # file = "../static/data/resource/bank.txt"
    # output = split_word_by_jieba(file)
    # result = train_word_vector_model(output)
    file = r"F:\pythonproject\chatbot\vendor\dataset\resource\bank.txt"
    result = word_vector_model_for_product('银行', file)
    print(result)
