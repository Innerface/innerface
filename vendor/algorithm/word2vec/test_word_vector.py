# Author: YuYuE (1019303381@qq.com) 2018.02.09
import warnings

warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
import gensim
import sys

# 导入模型
# model = gensim.models.Word2Vec.load("./bank_hs.model")
# model = gensim.models.Word2Vec.load("./weixin_word2vec/word2vec_wx")
model = gensim.models.Word2Vec.load("./model/baike_1.jieba.split.model")
print("请输入任意词语：")
sys.stdout.write("> ")
sys.stdout.flush()
input_seq = sys.stdin.readline()
if input_seq == 'exit\n':
    print('see you!')
    exit()
while input_seq:

    res = model.most_similar(positive=[input_seq[:-1]])
    print(model[input_seq[:-1]])
    if len(res):
        print('simi:')
        for each in res:
            print(each[0], each[1])
        print('score:', str(model.score([model[input_seq[:-1]]])))
    else:
        print('no response')

    sys.stdout.write("> ")
    sys.stdout.flush()
    input_seq = sys.stdin.readline()
    if input_seq == 'exit\n':
        print('see you!')
        exit()
