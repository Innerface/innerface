# Author: YuYuE (1019303381@qq.com) 2018.02.01
from Pinyin2Hanzi import DefaultHmmParams
from Pinyin2Hanzi import viterbi
from Pinyin2Hanzi import DefaultDagParams
from Pinyin2Hanzi import dag
from pypinyin import pinyin, lazy_pinyin, Style
from Pinyin2Hanzi import all_pinyin
from Pinyin2Hanzi import simplify_pinyin
from Pinyin2Hanzi import is_pinyin

# 初始化
hmmparams = DefaultHmmParams()
dagparams = DefaultDagParams()


# 根据拼音转汉字 HMM模式 sets = ['ni', 'zhi', 'bu', 'zhi', 'dao']
def transfer_pinyin_to_hanzi_by_hmm(sets):
    """
    HMM模式拼音转汉字
    :param sets:
    :return:
    """
    try:
        result = viterbi(hmm_params=hmmparams, observations=sets, path_num=1, log=True)
        path = ''
        for item in result:
            path = item.path
    except Exception as error:
        raise Exception('error:', error)
    else:
        return path


# 根据拼音转汉字 DAG模式 sets = ['ni', 'zhi', 'bu', 'zhi', 'dao']
def transfer_pinyin_to_hanzi_by_dag(sets):
    """
    DAG模式拼音转汉字
    :param sets:
    :return:
    """
    try:
        result = dag(dagparams, sets, path_num=1, log=True)
        path = ''
        for item in result:
            path = item.path
    except Exception as error:
        raise Exception('error:', error)
    else:
        return path


# 列举所有规范拼音
def show_all_standard_pinyin_list():
    return all_pinyin()


# 拼音规范化
def pinyin_standardization(param):
    """
    拼音规范化
    :param param:
    :return:
    """
    if not pinyin_decide(param):
        param = simplify_pinyin(param)
    return param


# 判断拼音是否规范
def pinyin_decide(param):
    """
    是否规范拼音
    :param param:
    :return:
    """
    return is_pinyin(param)


# 中文转拼音 model=lazy 不考虑多音字，style拼音风格，默认为首字母
def transfer_hanzi_to_pinyin(param, model='lazy', style=Style.FIRST_LETTER):
    """
    汉字转拼音
    :param param:
    :param model:
    :param style:
    :return:
    """
    try:
        if param.strip() == '':
            raise Exception('invalid param')
        if model == 'lazy':
            result = lazy_pinyin(param)
        else:
            result = pinyin(param, style=style)
    except Exception as error:
        raise Exception('error:', error)
    else:
        return result


# 判断一个unicode是否是汉字
def is_chinese(uchar):
    """
    判断字符是否汉字
    :param uchar:
    :return:
    """
    if u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False


# 判断一个unicode是否是英文字母
def is_alphabet(uchar):
    """
    判断字符是否字符
    :param uchar:
    :return:
    """
    if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
        return True
    else:
        return False


# 判断一个unicode是否是数字
def is_number(uchar):
    """
    判断字符是否数字
    :param uchar:
    :return:
    """
    if u'\u0030' <= uchar <= u'\u0039':
        return True
    else:
        return False


# 判断是否非汉字，数字和英文字符
def is_other(uchar):
    """
    判断字符是否非汉字数字英文
    :param uchar:
    :return:
    """
    if not (is_chinese(uchar) or is_number(uchar) or is_alphabet(uchar)):
        return True
    else:
        return False


# 别字拼音纠正法
def correct_hanzi_by_pinyin_transfer(param, model='dag'):
    """
    中文别字转拼音纠错
    :param param:
    :param model:
    :return:
    """
    try:
        if param.strip() == '':
            raise Exception('invalid param')
        # if re.match(r"[\u4e00-\u9fa5]+",param) == "None":
        if is_alphabet(param):
            return param
        else:
            pinyin = transfer_hanzi_to_pinyin(param)
            if model == 'dag':
                result = transfer_pinyin_to_hanzi_by_dag(pinyin)
            else:
                result = transfer_pinyin_to_hanzi_by_hmm(pinyin)
    except Exception as error:
        raise Exception('error:', error)
    else:
        return result


# 单声母表
def gengerate_single_shengmu_list():
    list_ = ['b', 'p', 'm', 'f', 'd', 't', 'n', 'l', 'g', 'k', 'h', 'j', 'q', 'x', 'r', 'z', 'c', 's', 'y', 'w']
    return list_


# 双拼声母表
def gengerate_double_shengmu_list():
    list_ = ['zh', 'ch', 'sh']
    return list_


# 独立韵母
def generate_single_yunmu():
    return ['a', 'o', 'e', 'an', 'en', 'ang', 'ai', 'ei', 'ou']


# 韵母表
def gengerate_yunmu_list():
    return ['a', 'o', 'e', 'ai', 'ei', 'ao', 'ou', 'an', 'en', 'ang', 'eng', 'ong', 'i', 'u', 'v', 'ua', 'uo', 'ia',
            'ie', 'in', 'iang', 'ing', 'iong', 've', 'uai', 'ui', 'iao', 'iu', 'ian', 'uan', 'uang', 'ueng', 'un']


# 全拼切分
def transfer_continue_pinyin_to_hanzi(param, model='dag'):
    """
    全拼音按音节切分后转汉字
    :param param:
    :param model:
    :return:
    """
    try:
        if param.strip() == '':
            raise Exception('invalid param')
        if is_chinese(param):
            return param
        else:
            pinyin = continue_pinyin_split(param)
            print(pinyin)
            # print(pinyin)
            if model == 'dag':
                result = transfer_pinyin_to_hanzi_by_dag(pinyin)
            else:
                result = transfer_pinyin_to_hanzi_by_hmm(pinyin)
    except Exception as error:
        raise Exception('error:', error)
    else:
        return result


def continue_pinyin_split(param):
    # for i in range(len(param)):
    """
    全拼音按音节切分
    :param param:
    :return:
    """
    temp = []
    shengm_ = shengmu_split(param)
    single_ = single_yunmu_split(param)
    if shengm_ and len(single_) == 0:
        temp = shengm_
    elif single_:
        temp.append(single_)
        temp.extend(shengm_)
    return temp


def shengmu_split(param):
    """
    声母切分
    :param param:
    :return:
    """
    result = []
    shengmu_list = gengerate_single_shengmu_list()
    double_shengmu_list = gengerate_double_shengmu_list()
    yunmu_list = gengerate_yunmu_list()
    count = 0
    for unit in param:
        count += 1
        if unit in shengmu_list and param[count - 1:count + 1] not in double_shengmu_list:
            for i in [4, 3, 2, 1]:
                # 截取i位字符
                temp = param[count:count + i]
                if temp in yunmu_list:
                    result.append(param[count - 1:count + i])
                    # result = param[count - 1:count + i]
                    break
        elif param[count - 1:count + 1] in double_shengmu_list:
            for i in [4, 3, 2, 1]:
                # 截取i位字符
                temp = param[count + 1:count + 1 + i]
                if temp in yunmu_list:
                    result.append(param[count - 1:count + 1 + i])
                    # result = param[count - 1:count + i]
                    count += i
                    break
    return result


def double_shengmu_dection(param):
    """
    双音节声母判断
    :param param:
    :return:
    """
    double_shengmu_list = gengerate_double_shengmu_list()
    result = False
    for shengmu_ in double_shengmu_list:
        if shengmu_ in param:
            result = True
            break
    return result


def single_yunmu_split(param):
    """
    单音节声母
    :param param:
    :return:
    """
    result = []
    yunmu_list = gengerate_yunmu_list()
    for i in [3, 2, 1]:
        # 截取i位字符
        temp = param[0:i]
        if temp in yunmu_list and len(temp) > 0:
            # result.append(param[0:i])
            result = param[0:i]
            break
    return result


class SpellTool(object):
    def __init__(self):
        # 初始化
        self.hmmparams = DefaultHmmParams()
        self.dagparams = DefaultDagParams()
        self.result = ''
        self.shengmu = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n', 'p', 'q', 'r', 's', 't', 'w', 'x', 'y',
                        'z', 'ch', 'sh', 'zh']
        self.yy = ['a', 'ai', 'an', 'ang', 'ao', 'e', 'en', 'eng', 'er', 'o', 'ou', 'ong']
        self.ym_b = ["a", "ai", "an", "ang", "ao", "ei", "en", "eng", "i", "ian", "iao", "ie", "in", "ing", "o", "u"]
        self.ym_c = ["a", "ai", "an", "ang", "ao", "e", "en", "eng", "i", "ong", "ou", "u", "uan", "ui", "un", "uo"]
        self.ym_d = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ia", "ian", "iao", "ie", "ing", "iu",
                     "ong", "ou", "u", "uan", "ui", "un", "uo"]
        self.ym_f = ["a", "an", "ang", "ei", "en", "eng", "iao", "o", "ou", "u"]
        self.ym_g = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "ong", "ou", "u", "uai", "uan", "uang", "ui",
                     "un", "uo"]
        self.ym_h = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "ong", "ou", "u", "ua", "uai", "uan", "uang",
                     "ui", "un", "uo"]
        self.ym_j = ["i", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iong", "iu", "u", "uan", "ue", "un"]
        self.ym_k = ["a", "ai", "an", "ang", "ao", "e", "en", "eng", "ong", "ou", "u", "ui", "un", "uo"]
        self.ym_l = ["a", "ai", "an", "ang", "ao", "e", "ei", "eng", "i", "ia", "ian", "iao", "ie", "in", "ing", "iu",
                     "o", "ong", "ou", "u", "uan", "un", "uo", "v", "ve"]
        self.ym_m = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ian", "iao", "ie", "in", "ing", "iu",
                     "o", "ou", "u"]
        self.ym_n = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ian", "iang", "iao", "ie", "in", "ing",
                     "iu", "ong", "ou", "u", "uan", "un", "uo", "v", "ve"]
        self.ym_p = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ian", "iao", "ie", "in", "ing", "o",
                     "ou", "u"]
        self.ym_q = ["i", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iong", "iu", "u", "uan", "ue", "un"]
        self.ym_r = ["an", "ang", "ao", "e", "en", "eng", "i", "ong", "ou", "u", "ua", "uan", "ui", "un", "uo"]
        self.ym_s = ["a", "ai", "an", "ang", "ao", "e", "en", "eng", "i", "ong", "ou", "u", "uan", "ui", "un", "uo"]
        self.ym_t = ["a", "ai", "an", "ang", "ao", "e", "ei", "eng", "i", "ian", "iao", "ie", "ing", "ong", "ou", "u",
                     "uan", "ui", "un", "uo"]
        self.ym_w = ["a", "ai", "an", "ang", "ei", "en", "eng", "o", "u"]
        self.ym_x = ["i", "ia", "ian", "iang", "iao", "ie", "in", "ing", "iong", "iu", "u", "uan", "ue", "un"]
        self.ym_y = ["a", "an", "ang", "ao", "e", "i", "in", "ing", "o", "ong", "ou", "u", "uan", "ue", "un"]
        self.ym_z = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ong", "ou", "u", "uan", "ui", "un",
                     "uo"]
        self.ym_ch = ["a", "ai", "an", "ang", "ao", "e", "en", "eng", "i", "ong", "ou", "u", "ua", "uai", "uan", "uang",
                      "ui", "un", "uo"]
        self.ym_sh = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ou", "u", "ua", "uai", "uan", "uang",
                      "ui", "un", "uo"]
        self.ym_zh = ["a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "i", "ong", "ou", "u", "ua", "uai", "uan",
                      "uang", "ui", "un", "uo"]
        self.ym = [self.yy, self.ym_b, self.ym_c, self.ym_d, self.ym_f, self.ym_g, self.ym_h, self.ym_j, self.ym_k,
                   self.ym_l, self.ym_m, self.ym_n, self.ym_p, self.ym_q, self.ym_r, self.ym_s, self.ym_t, self.ym_w,
                   self.ym_x, self.ym_y, self.ym_z, self.ym_ch, self.ym_sh, self.ym_zh
                   ]

    # 找声母
    def findsm(self, pinyin):
        temp = 0
        index = 0
        for i, sm in enumerate(self.shengmu):
            py2 = ''
            for py in pinyin:
                py2 += py
                if py2 == sm:
                    temp = len(sm)
                    index = i + 1
                    break

        if temp:
            self.result = self.result + pinyin[0:temp]
            pinyin = pinyin[temp:]
        if len(pinyin):
            return self.findym(pinyin, index)
        else:
            return pinyin

    # 找韵母
    def findym(self, pinyin, index):
        temp = 0
        for ym_value in self.ym[index]:
            py2 = ''
            for py in pinyin:
                py2 += py
                if py2 == ym_value:
                    temp = len(ym_value)
                    break
        if temp:
            self.result += pinyin[0:temp] + " "
            pinyin = pinyin[temp:]
        return pinyin

    # 根据分号
    def trimSpell(self, spell):
        round = len(spell)*2
        s = spell
        for i in range(round):
            if not s:
                break
            s = self.findym(s, 0)
            s = self.findsm(s)
        sets = self.result.split(' ')[:-1]
        return sets


if __name__ == '__main__':
    param = '旅行'
    pinyin = transfer_hanzi_to_pinyin(param)
    print(pinyin)
    hmm_ = transfer_pinyin_to_hanzi_by_hmm(pinyin)
    print(hmm_)
    dag_ = transfer_pinyin_to_hanzi_by_dag(pinyin)
    print(dag_)
    param = '新用卡'
    result = correct_hanzi_by_pinyin_transfer(param)
    print(result)
    pinyin = 'xinyongkabanli'
    result = transfer_continue_pinyin_to_hanzi(pinyin)
    print(''.join(result))
    pinyin = 'guozhai'
    result = transfer_continue_pinyin_to_hanzi(pinyin)
    print(result)

