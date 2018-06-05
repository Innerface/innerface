# Author: YuYuE (1019303381@qq.com) 2018.03.


def default_human_pronoun():
    return ['我', '我们', '你', '你们', '他', '他们', '她', '她们', '它', '它们', '自己', '咱们', '人家', '别人', '大家']


def default_interrogative_pronoum():
    return ['谁', '什么', '哪儿', '多会儿', '怎么', '怎样', '几', '多少', '多么', '如何', '哪', '啥', '怎么样', '何', '怎的', '怎么着', '为什么']


def default_instruction_pronoum():
    return ['这', '这里', '这么', '这样', '这么些', '那', '那里', '那么', '那样', '那么些']


def default_status_interrogative_pronoum():
    return ['谁', '何', '什么', '哪儿', '哪里', '几时', '几', '多少', '哪']


def default_operation_interrogative_pronoum():
    return ['怎', '怎么', '怎的', '怎样', '怎么样', '怎么着', '如何', '为什么']


def default_sentence_end():
    return ['。']


def special_sentence_end():
    return ['？', '！', '?', '!']


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


def generate_possible_action():
    return ['能', '能够', '会', '可', '可以', '可能', '得以']


def generate_willingness_action():
    return ['愿意', '乐意', '情愿', '肯', '要', '愿', '想要', '要想', '敢', '敢于', '乐于']


def generate_necessary_action():
    return ['应', '应该', '应当', '得', '该', '当', '必须', '理当', '须', '需要', '需']


def generate_valuation_action():
    return ['值得', '便于', '难于', '难以', '易于']


def generate_incline_action():
    return ['上', '下', '进', '出', '回', '开', '过', '起', '来', '上来', '下来', '进来',
            '出来', '回来', '开来', '过来', '起来', '去', '上去', '下去', '进去', '出去', '回去', '开去', '过去']


def predicate_transfer(word):
    if word == '办':
        word = '办理'
    elif word == '查':
        word = '查询'
    elif word == '卡':
        word = '信用卡'
    return word


def generate_greet_word_dict(index):
    _greet_word_dict = {0: '小M还在学习中，请耐心赐教哦。', 1: '小M暂时还答不出来，不过我会努力学习的。',
                        2: '您这个问题真是把小M问住了，要不要换个问法试试。',
                        3: '您这个问题把我难住了，小M正飞奔在学习的路上', 4: '这个...我得去请教下我老师'}
    return _greet_word_dict[index]


def generate_sensitive_reply_dict(index):
    _greet_word_dict = {0: '小M识别到敏感词语，请注意措辞', 1: '请注意不要使用敏感词语',
                        2: '请检查问题是否包含词语，再问一遍试试',
                        3: '喂喂喂，请问是110吗', 4: '识别到敏感词语，换种问法再试试'}
    return _greet_word_dict[index]
