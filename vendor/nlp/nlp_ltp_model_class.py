# Author: YuYuE (1019303381@qq.com) 2018.01.18
from pyltp import *
import os
import hashlib


class NlpLtpModel(object):
    """docstring for NlpLtpModel"""

    def __init__(self):
        # ltp默认路径配置
        self.ltp_path = os.path.dirname(os.path.abspath(__file__)) + "/data/ltp_data/"
        # ltp相关数据文件配置
        self.cws_model = self.ltp_path + "cws.model"
        self.ner_model = self.ltp_path + "ner.model"
        self.parser_model = self.ltp_path + "parser.model"
        self.pisrl_model = self.ltp_path + "pisrl.model"
        self.pos_model = self.ltp_path + "pos.model"
        # 待解析文本默认设置
        self.sentence = "请输入需要解析的文本"
        # 分词结果
        self.segment_result = {}
        # 词性标注结果
        self.postag_result = {}
        # 命名实体识别结果
        self.recognize_result = {}
        # 依存句法分析结果
        self.parse_result = {}

    # 路径配置接口
    def set_ltp_path(self, path):
        """

        :param path:
        :return:
        """
        if len(path) > 1:
            self.ltp_path = path

    # 提供方法初始化待分析文本
    def set_sentence(self, strs):
        """

        :param strs:
        :return:
        """
        if len(strs) > 1:
            self.sentence = strs
        else:
            print("待分析文本不能为空")
            exit()

    # 分词输出
    def get_segment_result(self):
        """

        :return:
        """
        segmentor = Segmentor()
        segmentor.load(self.cws_model)
        segment_result = segmentor.segment(self.sentence)
        self.segment_result = " ".join(segment_result)
        return self.segment_result

    # 词性标注输出
    def get_postag_result(self):
        """

        :return:
        """
        segment_result = self.segment_result.split(" ")
        # 词性标注
        postagger = Postagger()
        postagger.load(self.pos_model)
        self.postag_result = postagger.postag(segment_result)
        return self.postag_result

    # 命名实体识别输出
    def get_recongnize_result(self):
        """

        :return:
        """
        segment_result = self.segment_result.split(" ")
        recognizer = NamedEntityRecognizer()
        recognizer.load(self.ner_model)
        self.recognize_result = recognizer.recognize(segment_result, self.postag_result)
        return self.recognize_result

    # 依存句法输出
    def get_parse_result(self):
        """

        :return:
        """
        segment_result = self.segment_result.split(" ")
        parser = Parser()
        parser.load(self.parser_model)
        self.parse_result = parser.parse(segment_result, self.postag_result)
        return self.parse_result

    # 文件的命名实体提取
    def get_file_recognize_result(self, file_path):
        """

        :param file_path:
        :return:
        """
        if os.path.exists(file_path) == False:
            print("文件不存在")
        else:
            # md5_str = self.md5_encode(file_path)
            # out_file="../data/" + md5_str + ".txt"
            file_open = open(file_path, 'r', encoding='utf-8');
            contents = file_open.read()
            # file_out = open(out_file,'w',encoding='utf-8')
            # 导入分词模型数据
            segmentor = Segmentor()
            segmentor.load(self.cws_model)
            # 导入词性标注模型数据
            postagger = Postagger()
            postagger.load(self.pos_model)
            # 导入命名实体识别模型参数
            recognizer = NamedEntityRecognizer()
            recognizer.load(self.ner_model)
            words = segmentor.segment(contents)
            postags = postagger.postag(words)
            nertags = recognizer.recognize(words, postags)
            # 写入命名实体
            ner = []
            _temp = ''
            _tag = ''
            for word, nertag in zip(words, nertags):
                # file_out.write(word + "/" + nertag + "\n")
                if nertag.find("S-Ni") != -1:
                    ner.append([word, nertag])
                elif nertag.find("B-Ni") != -1:
                    _temp = word
                    _tag = nertag
                elif nertag.find("I-Ni") != -1:
                    _temp = _temp + word
                    _tag = _tag + "+" + nertag
                elif nertag.find("E-Ni") != -1:
                    _temp = _temp + word
                    _tag = _tag + "+" + nertag
                    ner.append([_temp, _tag])
                    _temp = ''
                    _tag = ''
                # print(word + "/" + nertag + "")
            print(ner)
            for ner_ in ner:
                print(ner_[0] + "\t" + ner_[1])

    def md5_encode(self, str_):
        md = hashlib.md5()
        md.update(str_.encode('utf-8'))
        return md.hexdigest()
