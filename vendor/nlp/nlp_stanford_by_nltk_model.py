# Author: YuYuE (1019303381@qq.com) 2018.01.18
from nltk.parse.stanford import StanfordParser
from nltk.tokenize import StanfordSegmenter
from nltk.tokenize import StanfordTokenizer
from nltk.tag import StanfordNERTagger
from nltk.tag import StanfordPOSTagger
from nltk.parse.stanford import StanfordParser
from nltk.parse.stanford import StanfordDependencyParser
import vendor.nlp.nlp_jieba_model as jieba_nlp
from chatbot.settings import BASE_DIR
import os

java_path = "C:/Program Files (x86)/Java/jdk1.8.0_144/bin/java.exe"
os.environ['JAVAHOME'] = java_path
stanford_root = BASE_DIR + "/vendor/dataset/stanford/stanford-corenlp-full-2017-06-09/"


def generate_stanford_parser(sentence, path=stanford_root):
    """
    词性标注
    :param sentence:
    :param path:
    :return:
    """
    parser = StanfordParser(
        model_path="edu/stanford/nlp/models/lexparser/chinesePCFG.ser.gz",
        path_to_models_jar=path + "stanford-parser-3.8.0-models.jar",
        path_to_jar=path + "stanford-parser.jar")
    result = parser.raw_parse(sentence)
    return result


def generate_stanford_segmenter(sentence, path=stanford_root):
    """
    分词
    :param sentence:
    :param path:
    :return:
    """
    segmenter = StanfordSegmenter(
        path_to_jar=path + "stanford-segmenter-3.8.0.jar",
        path_to_slf4j=path + "slf4j-api.jar",
        path_to_sihan_corpora_dict=path + "segmenter/data",
        path_to_model=path + "segmenter/data/pku.gz",
        path_to_dict=path + "segmenter/data/dict-chris6.ser.gz")
    result = segmenter.segment(sentence)
    return result


def generate_stanford_tokenizer(sentence, path=stanford_root):
    tokenizer = StanfordTokenizer(path_to_jar=path + "stanford-parser.jar")
    result = tokenizer.tokenize(sentence)
    return result


def generate_stanford_ner(sentence, path=stanford_root):
    chi_tagger = StanfordNERTagger(
        model_filename=path + r'models/ner/chinese.misc.distsim.crf.ser.gz',
        path_to_jar=path + 'stanford-ner.jar')
    segment = jieba_nlp.generate_jieba_cut(sentence, False, True)
    segment = ' '.join(segment)
    result = chi_tagger.tag(segment.split())
    return result


def generate_stanford_pos(sentence, path=stanford_root):
    tagger = StanfordPOSTagger(
        model_filename=path + r'models/pos-tagger/chinese-distsim/chinese-distsim.tagger',
        path_to_jar=path + r'stanford-postagger.jar')
    segment = jieba_nlp.generate_jieba_cut(sentence, False, True)
    segment = ' '.join(segment)
    result = tagger.tag(segment.split())
    return result


def generate_stanford_parser_(sentence, path=stanford_root):
    parser = StanfordParser(
        path + r"stanford-parser.jar",
        path + r"stanford-parser-3.6.0-models.jar",
        path + r"models/lexparser/chinesePCFG.ser.gz")
    segment = jieba_nlp.generate_jieba_cut(sentence, False, True)
    segment = ' '.join(segment)
    result = parser.parse(segment.split())
    return result


def generate_stanford_denpendency(sentence, path=stanford_root):
    parser = StanfordDependencyParser(
        path + r"stanford-parser.jar",
        path + r"stanford-parser-3.6.0-models.jar",
        path + r"models/lexparser/chinesePCFG.ser.gz")
    segment = jieba_nlp.generate_jieba_cut(sentence, False, True)
    segment = ' '.join(segment)
    result = parser.parse(segment.split())
    return result


if __name__ == "__main__":
    sentence = "长城钻石信用卡 与 长城世界之极信用卡，重塑 奢华 定义，再创 顶级之作。八 大 极致 尊荣 服务，只 为 给 您 最 极致 的 礼遇，与 您 共同 镌刻 一生 的 回忆 与 经历。"
    result = generate_stanford_parser(sentence)
    for res in result:
        print(res)
    sentence = "长城钻石信用卡与长城世界之极信用卡，重塑奢华定义，再创顶级之作。八大极致尊荣服务，只为给您最极致的礼遇，与您共同镌刻一生的回忆与经历。"
    # result = generate_stanford_tokenizer(sentence)
    # print(result)
    # result = generate_stanford_segmenter(sentence)
    # result = jieba_nlp.generate_jieba_cut(sentence, False, True)
    # print(' '.join(result))
    result = generate_stanford_pos(sentence)
    print(result)
    # for res in result:
    #     print(res)
