# Author: YuYuE (1019303381@qq.com) 2018.03.22
import os
import jieba
import pickle
from chatbot.settings import PICKLE_DIR
import vendor.nlp.nlp_stanford_by_java_model as stanford_java
import vendor.nlp.nlp_ltp_model as ltp_handle
import vendor.nlp.nlp_jieba_model as jieba_nlp
import vendor.nlp.nlp_pinyin_hanzi_transfer as transfer_nlp
from gensim import corpora, similarities, models
from chatbot.settings import BASE_DIR
import gensim
from chatbot.settings import WORD2VECMODEL


def set_defaul_model(mode='faq'):
    if mode == 'faq':
        model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/faq/faq_origin.model")
    elif mode == 'baike':
        model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/baike_1.jieba.split.model")
    elif mode == 'wiki':
        model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/wiki.zh.jieba.model")
    else:
        model = WORD2VECMODEL
    return model


model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/baike_1.jieba.split.model")


def siphon_word_dist_by_model(word1, word2, model=None):
    try:
        # if mode == 'faq':
        #     model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/faq/faq_origin.model")
        # elif mode == 'baike':
        #     model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/baike_1.jieba.split.model")
        # elif mode == 'wiki':
        #     model = gensim.models.Word2Vec.load(BASE_DIR + "/vendor/dataset/wordVec/wiki.zh.jieba.model")
        # else:
        #     model = WORD2VECMODEL
        result = model.similarity(word1, word2)
    except Exception as error:
        result = 0
    else:
        return result


def default_sentence_end():
    return ['。']


def special_sentence_end():
    return ['？', '！', '?', '!']


def combina_corpus(str_):
    """
    整合语料
    :param str_:
    :return:
    """
    return str_


def serialize_corpus(str_):
    """
    序列化语料
    :param str_:
    :return:
    """
    sents = []
    if os.path.exists(str_):
        file_handle = open(str_, 'r', encoding='utf-8')
        file_str = file_handle.read()
        sentence_end = default_sentence_end()
        temp_str = ''
        if file_str:
            if file_str.find("\n") != -1 or file_str.find("\r") != -1:
                temp_str = file_str.replace("\n", '')
                temp_str = temp_str.replace("\r", '')
            else:
                temp_str = file_str
            if temp_str != '':
                sents.append(temp_str)
            if sentence_end:
                for end_ in sentence_end:
                    for sent in sents:
                        if sent.find(end_) != -1:
                            temp_sent = sent.split(end_)
                            sents.remove(sent)
                            sents.extend(temp_sent)
    return sents


def structure_corpus(str_):

    """
    结构化处理语料
    :param str_:
    :return:
    """
    splits = jieba.cut(str_, cut_all=False, HMM=True)
    splits_ = ' '.join(splits)
    print(splits_)
    tree = stanford_java.generate_partial(splits_)
    pros = stanford_java.generate_partial_productions(splits_)
    segment = splits_.split(' ')
    postag = ltp_handle.generate_postag(str_, segment)
    recognize_result = ltp_handle.generate_recongnize(sentence, segment, postag)
    parse_result = ltp_handle.generate_parse(sentence, segment, postag)
    role = ltp_handle.generate_sementic_role(str_, segment, postag, recognize_result, parse_result)
    print(role)
    return


def siphon_file_names(file_dir):
    names = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.txt':
                # names.append(os.path.join(root, file))
                name = file.replace('.txt', '')
                if (len(name) > 1) and (len(name) < 7) and transfer_nlp.is_chinese(name):
                    for na in name:
                        if transfer_nlp.is_chinese(na) is False:
                            break
                    names.append(name)
    return names


def siphon_file_contents(file_dir, output):
    contents = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.txt':
                contents.append(os.path.join(root, file))
                file_path = os.path.join(root, file)
                file_out = os.path.join(output, file)
                print(file_path)
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    # print(lines)
                with open(file_out, "w", encoding="utf-8") as f_w:
                    for line in lines:
                        # if line.find('，') == -1 and line.find('、') == -1 and line.find('。') == -1 and len(line)<18:
                        # continue
                        f_w.write(line)
                    # exit()
    return contents


def batch_split_with_jieba(file_path, output=None):
    f1 = open(file_path, encoding="utf8")
    if output is None:
        output = file_path + '.jieba.txt'
    f2 = open(output, 'a', encoding="utf8")
    lines = f1.readlines()
    for line in lines:
        if line.strip() == '':
            continue
        line.replace('\t', '').replace('\n', '').replace(' ', '')
        seg_list = jieba_nlp.generate_jieba_cut(line, False, False)
        str_ = " ".join(seg_list)
        str_ = str_.replace('：', '').replace(':', '').replace('、', '').replace('。', '').replace('，', '').replace('(',
                                                                                                                 '').replace(
            ')', '').replace(';', '').replace('《', '').replace('》', '').replace('/', '')
        f2.write(str_)
    f1.close()
    f2.close()


def init_corpus(path, type_='file'):
    rows = []
    if type_ == 'file':
        rows = serialize_corpus(path)
    elif type_ == 'path':
        names = siphon_file_names(path)
        if names:
            for name in names:
                name = path + '/' + name
                temp = serialize_corpus(name)
                if temp:
                    rows.extend(temp)
    if rows:
        fp = open(PICKLE_DIR / 'rows.pickle', 'wb')
        pickle.dump(rows, fp, True)
    return rows


def init_corpus_model(rows):
    corpora_documents = []
    for row in rows:
        item = list(jieba_nlp.generate_jieba_cut(row))
        corpora_documents.append(item)
    dictionary = corpora.Dictionary(corpora_documents)
    # save dictionary
    dictionary.save(BASE_DIR + '/vendor/dataset/gensim/dict.txt')
    corpus = [dictionary.doc2bow(text) for text in corpora_documents]
    # save corpus
    corpora.MmCorpus.serialize(BASE_DIR + '/vendor/dataset/gensim/corpuse.mm', corpus)
    tfidf_model = models.TfidfModel(corpus)
    # save model
    tfidf_model.save(BASE_DIR + "/vendor/dataset/gensim/data.tfidf")
    corpus_tfidf = tfidf_model[corpus]
    return corpus_tfidf


def train_gensim_model(path, type_='file'):
    rows = init_corpus(path, type_)
    if rows:
        tfidf = init_corpus_model(rows)
    else:
        tfidf = None
    return tfidf


def gensim_tfidf_simi(sentence, features=400, best=2):
    """
    文本相似度匹配，存在未数据未对齐异常
    :param sentence:
    :param features:
    :param best:
    :return:
    """
    rows = decode_rows_pickle()
    corpora_documents = []
    for row in rows:
        item = list(jieba_nlp.generate_jieba_cut(row))
        corpora_documents.append(item)
    dictionary = corpora.Dictionary(corpora_documents)
    dictionary.compactify()
    corpus = [dictionary.doc2bow(text) for text in corpora_documents]
    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]
    similarity = similarities.Similarity(BASE_DIR + '/vendor/dataset/gensim/Similarity-tfidf-index',
                                         corpus_tfidf,
                                         num_features=features,
                                         num_best=best)
    cut_raw = list(jieba_nlp.generate_jieba_cut(sentence))
    test_corpus = dictionary.doc2bow(cut_raw)
    test_corpus_tfidf = tfidf_model[test_corpus]
    return similarity[test_corpus_tfidf]


def simlarity_tfidf(sentence):
    fenci = list(jieba_nlp.generate_jieba_cut(sentence))
    dictionary = corpora.Dictionary.load(BASE_DIR + '/vendor/dataset/gensim/dict.txt')
    corpus = corpora.MmCorpus(BASE_DIR + '/vendor/dataset/gensim/corpuse.mm')  # 加载
    tfidf = models.TfidfModel.load(BASE_DIR + "/vendor/dataset/gensim/data.tfidf")
    corpus_tfidf = tfidf[corpus]
    vec_bow = dictionary.doc2bow(fenci)
    vec_tfidf = tfidf[vec_bow]
    index = similarities.MatrixSimilarity(corpus_tfidf)
    sims = index[vec_tfidf]
    similarity = list(sims)
    simi_sets = {}
    if similarity:
        rows = decode_rows_pickle()
        simi_sets = {}
        i = 0
        temp_simi = 0
        for simi in similarity:
            if simi > temp_simi:
                temp = {
                    'index': i,
                    'simi': simi,
                    'text': rows[i]
                }
                simi_sets.update(temp)
                temp_simi = simi
            i += 1
    return simi_sets


def gensim_lsi_simi(sentence, features=600, best=2):
    """
    文本相似度匹配，支持大数据
    :param sentence:
    :param features:
    :param best:
    :return:
    """
    dictionary = corpora.Dictionary.load(BASE_DIR + '/vendor/dataset/gensim/dict.txt')
    corpus = corpora.MmCorpus(BASE_DIR + '/vendor/dataset/gensim/corpuse.mm')
    tfidf_model = models.TfidfModel.load(BASE_DIR + "/vendor/dataset/gensim/data.tfidf")
    corpus_tfidf = tfidf_model[corpus]
    lsi = models.LsiModel(corpus_tfidf)
    corpus_lsi = lsi[corpus_tfidf]
    similarity_lsi = similarities.Similarity(BASE_DIR + '/vendor/dataset/gensim/Similarity-LSI-index',
                                             corpus_lsi,
                                             num_features=features,
                                             num_best=best)
    test_cut_raw = list(jieba_nlp.generate_jieba_cut(sentence))  # 1.分词
    test_corpus = dictionary.doc2bow(test_cut_raw)  # 2.转换成bow向量
    test_corpus_tfidf = tfidf_model[test_corpus]  # 3.计算tfidf值
    test_corpus_lsi = lsi[test_corpus_tfidf]  # 4.计算lsi值
    # lsi.add_documents(test_corpus_lsi_3) #更新LSI的值
    simi_sets = similarity_lsi[test_corpus_lsi]
    reponse = {}
    if simi_sets:
        rows = decode_rows_pickle()
        temp_simi = 0
        for simi_set in simi_sets:
            if simi_set[1] > temp_simi:
                reponse['index'] = simi_set[0]
                reponse['simi'] = simi_set[1]
                reponse['text'] = rows[simi_set[0]]
                temp_simi = simi_set[1]
    return reponse


def decode_rows_pickle():
    f = open(PICKLE_DIR / 'rows.pickle', "rb+")
    rows = pickle.load(f)
    return rows


def siphon_best_match_from_set(sentence, set):
    corpora_documents = []
    for item_text in set:
        item_seg = list(jieba_nlp.generate_jieba_cut(item_text))
        corpora_documents.append(item_seg)
    dictionary = corpora.Dictionary(corpora_documents)
    corpus = [dictionary.doc2bow(text) for text in corpora_documents]
    tfidf_model = models.TfidfModel(corpus)
    corpus_tfidf = tfidf_model[corpus]
    similarity = similarities.Similarity(BASE_DIR + '/vendor/dataset/gensim/Similarity-tfidf-index',
                                         corpus_tfidf,
                                         num_features=600)
    test_cut_raw_1 = list(jieba_nlp.generate_jieba_cut(sentence))
    test_corpus_1 = dictionary.doc2bow(test_cut_raw_1)
    similarity.num_best = 2
    test_corpus_tfidf_1 = tfidf_model[test_corpus_1]
    tfidf_simi = similarity[test_corpus_tfidf_1]
    lsi = models.LsiModel(corpus_tfidf)
    corpus_lsi = lsi[corpus_tfidf]
    similarity_lsi = similarities.Similarity(BASE_DIR + '/vendor/dataset/gensim/Similarity-LSI-index',
                                             corpus_lsi,
                                             num_features=400, num_best=2)
    test_cut_raw_3 = list(jieba_nlp.generate_jieba_cut(sentence))
    test_corpus_3 = dictionary.doc2bow(test_cut_raw_3)
    test_corpus_tfidf_3 = tfidf_model[test_corpus_3]
    test_corpus_lsi_3 = lsi[test_corpus_tfidf_3]
    # lsi.add_documents(test_corpus_lsi_3) #更新LSI的值
    lsi_simi = similarity_lsi[test_corpus_lsi_3]
    return {'tfidf': tfidf_simi, 'lsi_simi': lsi_simi}


def calculate_simi_with_ltp_weight(sentence1, sentence2):
    word_dict1 = word_dict2 = {}
    if sentence1:
        word_dict1 = ltp_handle.siphon_words_with_tags(sentence1)
        print(word_dict1)
    if sentence2:
        word_dict2 = ltp_handle.siphon_words_with_tags(sentence2)
        print(word_dict2)
    focal_types = ltp_handle.focal_type_with_weight()
    dist = cnt = 0
    for types in focal_types:
        temp1 = []
        temp2 = []
        for (word1, tag1) in word_dict1.items():
            if tag1 == types:
                word1 = word1.replace(tag1, '')
                temp1.append(word1)
        for (word2, tag2) in word_dict2.items():
            if tag2 == types:
                word2 = word2.replace(tag2, '')
                temp2.append(word2)
        if temp1 and temp2:
            simi = model.n_similarity(temp1, temp2)
        else:
            simi = 0
        dist += simi * focal_types[types]
        cnt += focal_types[types]
    return dist/cnt


if __name__ == "__main__":
    # import time
    # print(time.time())
    # set = [
    #     '办理信用卡必须本人吗',  # 0
    #     '已有信用卡，是否办理其他银行的信用卡就会方便一些呢？',  # 1
    #     '18岁可以办理什么银行的信用卡',  # 2
    #     '在网上申请信用卡和去银行办理有什么不同？',  # 3
    #     'VISA信用卡怎么办理？卡的性质是什么？',  # 4
    #     '办理visa信用卡需要多久',  # 5
    #     '信用卡未办理成功会影响以后办理信用卡么？',  # 6
    #     '办理信用卡有哪些注意事项？',  # 7
    #     '信用卡报停怎么办理？',  # 8
    #     '怎么办理VISA信用卡',  # 9
    #     '怎样办理信用卡',  # 10
    #     '第一次办理信用卡需要什么手续?',  # 12
    #     '月收入多少可以办理信用卡？',  # 13
    #     '我不知道我的信用卡是哪个支行办理的怎么查呀',  # 14
    #     '信用卡办理进度在哪儿查',  # 15
    #     '个人信用卡是否可由他人代为办理分期',  # 16
    #     '个人信用卡如何办理分期业务',  # 17
    #     '如何办理信用卡',  # 18
    #     '信用卡办理需要什么资料',  # 19
    #     '信用卡分期如何办理'  # 20
    # ]
    # sentence = '怎么办理信用卡'
    # dict_simi = siphon_best_match_from_set(sentence, set)
    # print(dict_simi)
    # print(time.time())
    # for se in set:
    #     simi = calculate_simi_with_ltp_weight(sentence, se)
    #     print(simi)
    # exit()
    # path = "E:/WWW/spider_for_news/file_set/file_set/银行.txt"
    path = "E:/WWW/spider_for_news/file_set/file_set/"
    names = siphon_file_names(path)
    model = set_defaul_model('baike')
    for name in names:
        print(name)
        # simi = siphon_word_dist_by_model(name, '经济', model)
        # if simi is not None and float(simi) >= 0.27:
        #     print(name, simi)
    exit()
    sent = '中国通商银行'
    result = simlarity_tfidf(sent)
    print(result)
    result = gensim_lsi_simi(sent)
    print(result)
    exit()
    result = train_gensim_model(path, 'file')
    print(result)
    exit()
    sentences = serialize_corpus(path)
    print(sentences)
    exit()
    # f_out = open('out.txt','w',encoding='utf-8')
    for sentence in sentences:
        print(sentence)
        # f_out.write(sentence+'\n')
        structure_corpus(sentence)
        exit()
