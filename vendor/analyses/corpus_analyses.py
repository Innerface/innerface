# Author: YuYuE (1019303381@qq.com) 2018.05.
from sklearn.feature_extraction.text import TfidfVectorizer
from chatbot.settings import BASE_DIR
import vendor.nlp.nlp_stanford_by_java_model as stanford_java


def sklearn_tfidf(res1, res2, stpwrdlst=None):
    if stpwrdlst is None:
        stp_content = open(BASE_DIR + "/vendor/dataset/chinese/stopwords.dat", 'r', encoding='utf-8').read()
        stpwrdlst = stp_content.splitlines()
    corpus = [res1, res2]
    vector = TfidfVectorizer(stop_words=stpwrdlst)
    tfidf = vector.fit_transform(corpus)
    return tfidf


def siphon_ner(sent):
    """
    :param sent:
    :return:
    """
    words = stanford_java.generate_segment(sent)
    print(words)
    postags = stanford_java.generate_postag(words)
    print(postags)
    ners = stanford_java.generate_ner(words)
    print(ners)
    # partial = stanford_java.generate_partial(words)
    # print(partial)
    # pros = stanford_java.generate_partial_productions(words)
    # print(pros)
    # depend = stanford_java.generate_typed_dependencies(words)
    # print(depend)
    words = words.split()
    # print(words)
    ners_ = stanford_java.siphon_ners_by_nlp(False, words, postags)
    print(ners_)
    return sent


def siphon_relation(sent):
    """
    :param sent:
    :return:
    """
    return sent


if __name__ == "__main__":
    sentence = "汉语的历史叫做汉语史，包括汉语语音史、汉语语法史、汉语词汇史三大块，汉语史是研究汉语现象及其内部规律的一门科学，包括语音、语法、词汇现象及其历史演变规律。"
    path = "E:/Personal/银行.txt"
    sentence = open(path, 'r', encoding='utf-8').read()
    siphon_ner(sentence)
    exit()
    sentence1 = "沙瑞金 赞叹 易学习 的 胸怀 ， " \
                "是 金山 的 百姓 有福 ， " \
                "可是 这件 事对 李达康 的 触动 很大 。 " \
                "易学习 又 回忆起 他们 三人 分开 的 前一晚 ， " \
                "大家 一起 喝酒 话别 ， " \
                "易学习 被 降职 到 道口 县当 县长 ， " \
                "王大路 下海经商 ， " \
                "李达康 连连 赔礼道歉 ，" \
                " 觉得 对不起 大家 ， " \
                "他 最 对不起 的 是 王大路 ， " \
                "就 和 易学习 一起 给 王大路 凑 了 5 万块 钱 ， " \
                "王大路 自己 东挪西撮 了 5 万块 ， 开始 下海经商 。 " \
                "没想到 后来 王大路 竟然 做 得 风生水 起 。 " \
                "沙瑞金 觉得 他们 三人 ， " \
                "在 困难 时期 还 能 以沫 相助 ， " \
                "很 不 容易 。"
    sentence2 = "沙瑞金 向 毛娅 打听 他们 家 在 京州 的 别墅 ， " \
                "毛娅 笑 着 说 ， " \
                "王大路 事业有成 之后 ， " \
                "要 给 欧阳 菁 和 她 公司 的 股权 ， " \
                "她们 没有 要 ， " \
                "王大路 就 在 京州 帝豪园 买 了 三套 别墅 ， " \
                "可是 李达康 和 易学习 都 不要 ， " \
                "这些 房子 都 在 王大路 的 名下 ， " \
                "欧阳 菁 好像 去 住 过 ， " \
                "毛娅 不想 去 ， " \
                "她 觉得 房子 太大 很 浪费 ， " \
                "自己 家住 得 就 很 踏实 "
    result = sklearn_tfidf(sentence1, sentence2)
    print(result)