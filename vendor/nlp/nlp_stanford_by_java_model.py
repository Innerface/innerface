# Author: YuYuE (1019303381@qq.com) 2018.01.18
import os
from nltk.tree import Tree
from chatbot.settings import BASE_DIR
import vendor.nlp.nlp_jieba_model as jieba_nlp
import platform


if platform.system() == 'Windows':
    symbol = ";"
    segment_script = 'segment.bat '
else:
    symbol = ":"
    segment_script = 'segment.sh '


# BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# 基础引用类
class StanfordCoreNLP():
    """docstring for StanfordCoreNLP"""

    def __init__(self, jarpath):
        self.root = jarpath
        self.tempsrcpath = BASE_DIR + "/vendor/dataset/temp/tempin"
        self.jarlist = ["ejml-0.23.jar", "javax.json.jar", "jollyday.jar", "joda-time.jar", "protobuf.jar",
                        "slf4j-api.jar", "slf4j-simple.jar", "stanford-corenlp-3.8.0.jar", "xom.jar"]
        self.jarpath = ""
        self.buildjars()

    def buildjars(self):
        for jar in self.jarlist:
            self.jarpath += self.root + jar + symbol

    def savefile(self, path, sent):
        fp = open(path, 'w', encoding='utf-8')
        fp.write(sent)
        fp.close()

    def delfile(self, path):
        os.remove(path)


# 分词
class StanfordSegment(StanfordCoreNLP):
    """docstring for StanfordSegment"""

    def __init__(self, path):
        StanfordCoreNLP.__init__(self, jarpath='')
        self.classfier = "edu.stanford.nlp.pipeline.ChineseSegmenterAnnotator"
        self.__buildcmd(path)

    def __buildcmd(self, path):
        self.cmdline = path + segment_script

    def tagfile(self, words, model='pku', outpath='tempout'):
        self.savefile(self.tempsrcpath, words)
        os.system(self.cmdline + model + ' ' + self.tempsrcpath + ' UTF-8 0 > ' + outpath)
        self.delfile(self.tempsrcpath)
        result = open(outpath, 'r', encoding='utf-8').read()
        return result


# 词性标注
class StanfordPOSTagger(StanfordCoreNLP):
    """docstring for StanfordPOSTagger"""

    def __init__(self, jarpath, modelpath):
        StanfordCoreNLP.__init__(self, jarpath)
        self.modelpath = modelpath
        self.classfier = "edu.stanford.nlp.tagger.maxent.MaxentTagger"
        self.delimiter = "/"
        self.__buildcmd()

    def __buildcmd(self):
        self.cmdline = 'java -mx1g -cp "' + self.jarpath + '" ' + self.classfier + ' -model "' + self.modelpath + '" -tagSeparator ' + self.delimiter

    # 字节流异常
    def tag(self, sent):
        self.savefile(self.tempsrcpath, sent)
        tagtxt = os.popen(self.cmdline + " -textFile " + self.tempsrcpath, 'r').read()
        self.delfile(self.tempsrcpath)
        return tagtxt

    def tagfile(self, words, outpath='tempout'):
        self.savefile(self.tempsrcpath, words)
        os.system(self.cmdline + ' -textFile ' + self.tempsrcpath + ' > ' + outpath)
        self.delfile(self.tempsrcpath)
        result = open(outpath, 'r', encoding='utf-8').read()
        return result


# 命名实体识别
class StanfordNERTagger(StanfordCoreNLP):
    """docstring for StanfordNERTagger"""

    def __init__(self, jarpath, modelpath):
        StanfordCoreNLP.__init__(self, jarpath)
        self.modelpath = modelpath
        self.classfier = "edu.stanford.nlp.ie.crf.CRFClassifier"
        self.__buildcmd()

    def __buildcmd(self):
        self.cmdline = 'java -mx1g -cp "' + self.jarpath + '" ' + self.classfier + ' -loadClassifier "' + self.modelpath + '"'

    def tag(self, sent):
        self.savefile(self.tempsrcpath, sent)
        tagtxt = os.popen(self.cmdline + ' -textFile ' + self.tempsrcpath, 'r').read()
        self.delfile(self.tempsrcpath)
        return tagtxt

    def tagfile(self, words, outpath='tempout'):
        self.savefile(self.tempsrcpath, words)
        os.system(self.cmdline + ' -textFile ' + self.tempsrcpath + ' > ' + outpath)
        self.delfile(self.tempsrcpath)
        result = open(outpath, 'r', encoding='utf-8').read()
        return result


# 句法分析
class StanfordParser(StanfordCoreNLP):
    """docstring for StanfordParser"""

    def __init__(self, modelpath, jarpath, opttype):
        StanfordCoreNLP.__init__(self, jarpath)
        self.modelpath = modelpath
        self.classfier = "edu.stanford.nlp.parser.lexparser.LexicalizedParser"
        self.opttype = opttype
        self.__buildcmd()

    def __buildcmd(self):
        self.cmdline = 'java -mx500m -cp "' + self.jarpath + '" ' + self.classfier + ' -outputFormat "' + self.opttype + '" ' + self.modelpath + ' '

    def parse(self, sent):
        self.savefile(self.tempsrcpath, sent)
        tagtxt = os.popen(self.cmdline + self.tempsrcpath, "r").read()
        self.delfile(self.tempsrcpath)
        return tagtxt

    def tagfile(self, words, outpath='tempout'):
        self.savefile(self.tempsrcpath, words)
        os.system(self.cmdline + self.tempsrcpath + ' > ' + outpath)
        self.delfile(self.tempsrcpath)
        result = open(outpath, 'r', encoding='utf-8').read()
        return result


def generate_segment(sent):
    """
    分词
    :param sent:
    :return:
    """
    base_path = BASE_DIR
    root = base_path + "/vendor/dataset/stanford/stanford-segmenter-2017-06-09/"
    stanford_seg = StanfordSegment(root)
    seg_tag = stanford_seg.tagfile(sent, 'ctb')
    return seg_tag


def generate_postag(segment):
    """
    词性标注
    :param segment:
    :return:
    """
    pos_root = BASE_DIR + "/vendor/dataset/stanford/stanford-corenlp-full-2017-06-09/"
    pos_model = pos_root + "models/pos-tagger/chinese-distsim/chinese-distsim.tagger"
    stanford_pos = StanfordPOSTagger(pos_root, pos_model)
    pos_tag = stanford_pos.tagfile(segment)
    return pos_tag


def generate_ner(segment):
    """
    命名实体识别
    :param segment:
    :return:
    """
    pos_root = BASE_DIR + "/vendor/dataset/stanford/stanford-corenlp-full-2017-06-09/"
    ner_model = pos_root + "models/ner/chinese.misc.distsim.crf.ser.gz"
    stanford_ner = StanfordNERTagger(pos_root, ner_model)
    ner_tag = stanford_ner.tag(segment)
    return ner_tag


def generate_partial(segment):
    """
    短语树拆分
    :param segment:
    :return:
    """
    pos_root = BASE_DIR + "/vendor/dataset/stanford/stanford-corenlp-full-2017-06-09/"
    par_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'penn'
    parser = StanfordParser(par_model, pos_root, opttype)
    par_tag = parser.tagfile(segment)
    tree = Tree.fromstring(par_tag)
    return tree


def generate_partial_productions(segment):
    """
    短语树拆分
    :param segment:
    :return:
    """
    pos_root = BASE_DIR + "/vendor/dataset/stanford/stanford-corenlp-full-2017-06-09/"
    par_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'penn'
    parser = StanfordParser(par_model, pos_root, opttype)
    par_tag = parser.tagfile(segment)
    tree = Tree.fromstring(par_tag)
    pros = tree.productions()
    return pros


def generate_typed_dependencies(segment):
    """
    依存句法分析
    :param segment:
    :return:
    """
    pos_root = BASE_DIR + "/vendor/dataset/stanford/stanford-corenlp-full-2017-06-09/"
    pars_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'typedDependencies'
    parser = StanfordParser(pars_model, pos_root, opttype)
    result = parser.tagfile(segment)
    return result


def siphon_words_with_tags(sentence=False, keywords=None, tags=None):
    """
    词性标注，输出dict
    :param sentence:
    :param keywords:
    :param tags:
    :return:
    """
    word_dict = {}
    if sentence is False and keywords:
        if isinstance(keywords, list):
            keywords = ' '.join(keywords)
        if tags is None:
            tags = generate_postag(keywords)
        if tags:
            word_tags = tags.split()
            i = 0
            for word_tag in word_tags:
                if word_tag.find("/") != -1:
                    temp = word_tag.split("/")
                    if temp[0] in word_dict:
                        i += 1
                        if temp[0] + temp[1] in word_dict:
                            word_dict[temp[0] + temp[1] * i] = temp[1]
                        else:
                            word_dict[temp[0] + temp[1]] = temp[1]
                    else:
                        word_dict[temp[0]] = temp[1]
    elif sentence and keywords is False:
        keywords = jieba_nlp.generate_jieba_cut(sentence, False, True)
        keywords = ' '.join(keywords)
        tags = generate_postag(keywords)
        if tags:
            word_tags = tags.split()
            i = 0
            for word_tag in word_tags:
                if word_tag.find("/") != -1:
                    temp = word_tag.split("/")
                    if temp[0] in word_dict:
                        i += 1
                        if temp[0] + temp[1] in word_dict:
                            word_dict[temp[0] + temp[1] * i] = temp[1]
                        else:
                            word_dict[temp[0] + temp[1]] = temp[1]
                    else:
                        word_dict[temp[0]] = temp[1]
    return word_dict


def siphon_ners_by_nlp(inp, keywords=None, tags=None, mode='HMM'):
    ners = []
    word_dict = siphon_words_with_tags(inp, keywords, tags)
    # print('word_dict', word_dict)
    previous = ''
    for (word, tag) in word_dict.items():
        if tag == 'NN' or tag == 'NR' or tag == 'NT':
            if previous == 'NN' or previous == 'NR' or tag == 'NT':
                word = word.replace(tag, '')
                temp = ners.pop() if ners else ''
                ners.append(temp + word)
            else:
                word = word.replace(tag, '')
                ners.append(word)
        previous = tag
    ners = ' '.join(ners)
    return ners


def siphon_ners_by_ner(inp, keywords=None):
    if keywords is None:
        keywords = generate_segment(inp)
    ners_tag = generate_ner(keywords)
    ners_dict = {}
    i = 0
    ners_tag = ners_tag.split()
    for word_tag in ners_tag:
        if word_tag.find("/") != -1:
            temp = word_tag.split("/")
            if temp[0] in ners_dict:
                i += 1
                if temp[0] + temp[1] in ners_dict:
                    ners_dict[temp[0] + temp[1] * i] = temp[1]
                else:
                    ners_dict[temp[0] + temp[1]] = temp[1]
            else:
                ners_dict[temp[0]] = temp[1]
    ners = []
    # print('ners_dict', ners_dict)
    if ners_dict:
        previous = ''
        for (word, tag) in ners_dict.items():
            if tag != 'O':
                if previous == tag:
                    word = word.replace(tag, '')
                    temp = ners.pop()
                    ners.append(temp + word)
                else:
                    word = word.replace(tag, '')
                    ners.append(word)
            previous = tag
        ners = ' '.join(ners)
    return ners


if __name__ == "__main__":
    import platform
    print(platform.system())
    sent = '银行，是依法成立的经营货币信贷业务的金融机构，是商品货币经济发展到一定阶段的产物。'
    # sent = '个人贷款'
    ners = siphon_ners_by_ner(sent)
    print(ners)
    keywords = generate_segment(sent)
    ners = siphon_ners_by_nlp(False, keywords)
    print(ners)
    # exit()
    # base_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.abspath(os.path.dirname(os.getcwd()) + os.path.sep + "..")
    # 分词
    seg_root = base_path + "/vendor/dataset/stanford/stanford-segmenter-2017-06-09/"
    stanford_seg = StanfordSegment(seg_root)
    # sent = u"长城环球通多币借记卡是中国银行发行的银联品牌、具有人民币账户及美元、澳门元、欧元、港币等多种外币账户的白金卡,是中国银行为便利客户在境内外取现和消费而提供的现代化金融支付工具。"
    # sent = u"银行是金融机构之一，银行按类型分为：中央银行，政策性银行，商业银行，投资银行，世界银行，它们的职责各不相同"
    print(sent)
    seg_tag = stanford_seg.tagfile(sent, 'ctb')
    print(seg_tag)
    import jieba
    import jieba.posseg as pseg

    word_list = jieba.cut_for_search(sent)
    print(' '.join(word_list))
    words = pseg.cut(sent)
    word_str = ''
    for word, flag in words:
        word_str += word + ' '
    seg_tag = word_str
    print(word_str)
    # 词性标注
    pos_root = base_path + "/vendor/dataset/stanford/stanford-corenlp-full-2017-06-09/"
    pos_model = pos_root + "models/pos-tagger/chinese-distsim/chinese-distsim.tagger"
    stanford_pos = StanfordPOSTagger(pos_root, pos_model)
    pos_tag = stanford_pos.tagfile(seg_tag)
    print(pos_tag)
    # 命名实体识别
    ner_model = pos_root + "models/ner/chinese.misc.distsim.crf.ser.gz"
    stanford_ner = StanfordNERTagger(pos_root, ner_model)
    ner_tag = stanford_ner.tag(seg_tag)
    print(ner_tag)
    # 短语结构树
    par_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'penn'
    parser = StanfordParser(par_model, pos_root, opttype)
    par_tag = parser.tagfile(seg_tag)
    print(par_tag)
    tree = Tree.fromstring(par_tag)
    print(tree)
    tree.draw()
    # 依存句法
    pars_model = pos_root + "models/lexparser/chinesePCFG.ser.gz"
    opttype = 'typedDependencies'
    parser = StanfordParser(pars_model, pos_root, opttype)
    result = parser.tagfile(seg_tag)
    print('YuYuE')
    print(result)
    result = generate_partial(seg_tag)
    print(result)
