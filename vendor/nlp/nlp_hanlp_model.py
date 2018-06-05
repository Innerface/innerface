# Author: YuYuE (1019303381@qq.com) 2018.05.
from jpype import *
import os
from chatbot.settings import BASE_DIR


hanlp_path = os.path.join(BASE_DIR, 'vendor\\hanlp-1.3.4-release')
jar_path = os.path.join(hanlp_path, 'hanlp-1.3.4.jar')

JVMsetting = f"-Djava.class.path={jar_path};{hanlp_path}"
startJVM(getDefaultJVMPath(),
         JVMsetting,
         "-Xms1g",
         "-Xmx1g")  # 启动JVM，Linux需替换分号;为冒号:


def hanlp_segment(sentence, mode=''):
    """

    :param sentence:
    :param mode:
    :return:
    """
    if mode == 'Standard':
        HanLP = JClass('com.hankcs.hanlp.tokenizer.StandardTokenizer')
        result = HanLP.segment(sentence)
    elif mode == 'NLP':
        HanLP = JClass('com.hankcs.hanlp.tokenizer.NLPTokenizer')
        result = HanLP.segment(sentence)
    elif mode == 'Index':
        HanLP = JClass('com.hankcs.hanlp.tokenizer.IndexTokenizer')
        result = HanLP.segment(sentence)
    elif mode == 'Traditional':
        HanLP = JClass('com.hankcs.hanlp.tokenizer.TraditionalChineseTokenizer')
        result = HanLP.segment(sentence)
    elif mode == 'Speed':
        HanLP = JClass('com.hankcs.hanlp.tokenizer.SpeedTokenizer')
        result = HanLP.segment(sentence)
    elif mode == 'Notional':
        HanLP = JClass('com.hankcs.hanlp.tokenizer.NotionalTokenizer')
        result = HanLP.segment(sentence)
    elif mode == 'URL':
        HanLP = JClass('com.hankcs.hanlp.tokenizer.URLTokenizer')
        result = HanLP.segment(sentence)
    elif mode == 'NShort':
        NShortSegment = JClass('com.hankcs.hanlp.seg.NShort.NShortSegment')
        segment = NShortSegment()
        result = segment.seg(sentence)
    elif mode == 'Viterbi':
        ViterbiSegment = JClass('com.hankcs.hanlp.seg.Viterbi.ViterbiSegment')
        segment = ViterbiSegment()
        result = segment.seg(sentence)
    elif mode == 'CRF':
        CRFSegment = JClass('com.hankcs.hanlp.seg.CRF.CRFSegment')
        segment = CRFSegment()
        result = segment.seg(sentence)
    elif mode == 'HMM':
        HMMSegment = JClass('com.hankcs.hanlp.seg.HMM.HMMSegment')
        segment = HMMSegment()
        result = segment.seg(sentence)
    elif mode == 'Dijkstra':
        DijkstraSegment = JClass('com.hankcs.hanlp.seg.Dijkstra.DijkstraSegment')
        segment = DijkstraSegment()
        result = segment.seg(sentence)
    else:
        HanLP = JClass('com.hankcs.hanlp.HanLP')
        result = HanLP.segment(sentence)
    return result


def hanlp_dict(words):
    """

    :param words:
    :return:
    """
    CustomDictionary = JClass('com.hankcs.hanlp.dictionary.CustomDictionary')
    if isinstance(words, 'list'):
        for word in words:
            CustomDictionary.add(word)
    elif isinstance(words, 'string'):
        CustomDictionary.add(words)
    else:
        return False
    return True


def hanlp_keywords(corpus, num):
    """

    :param corpus:
    :param num:
    :return:
    """
    HanLP = JClass('com.hankcs.hanlp.HanLP')
    keywords = HanLP.extractKeyword(corpus, num)
    return keywords


def hanlp_summary(corpus, num):
    """

    :param corpus:
    :param num:
    :return:
    """
    HanLP = JClass('com.hankcs.hanlp.HanLP')
    summary = HanLP.extractSummary(corpus, num)
    return summary


def hanlp_dependency(corpus):
    """

    :param corpus:
    :return:
    """
    HanLP = JClass('com.hankcs.hanlp.HanLP')
    dependency = HanLP.parseDependency(corpus)
    return dependency


def hanlp_phrase(corpus, num):
    """

    :param corpus:
    :param num:
    :return:
    """
    HanLP = JClass('com.hankcs.hanlp.HanLP')
    phrase = HanLP.extractPhrase(corpus, num)
    return phrase


def hanlp_recongnize(corpus, mode='place'):
    """

    :param corpus:
    :param mode:
    :return:
    """
    HanLP = JClass('com.hankcs.hanlp.HanLP')
    if mode == 'place':
        HanLP.newSegment().enablePlaceRecognize(True)
    elif mode == 'person':
        HanLP.newSegment().enableNameRecognize(True)
    elif mode == 'trans':
        HanLP.newSegment().enableTranslatedNameRecognize(True)
    elif mode == 'japan':
        HanLP.newSegment().enableJapaneseNameRecognize(True)
    elif mode == 'org':
        HanLP.newSegment().enableOrganizationRecognize(True)
    else:
        pass
    result = HanLP.segment(corpus)
    return result


if __name__ == "__main__":
    corpus = '撒旦飞洒发黄金发稿费发放给个结果发货就'
    print(hanlp_segment(corpus, mode='CRF'))
