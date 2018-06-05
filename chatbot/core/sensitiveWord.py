import pickle
import pathlib
from data_admin.models import Sensitive
from chatbot.settings import BASE_DIR
from chatbot.settings import PICKLE_DIR


if __name__ == '__main__':
    print(PICKLE_DIR)


class Node(object):
    def __init__(self):
        self.children = None
        self.badword = None
        # self.isEnd = None


def add_word(root_node, word):
    node = root_node
    for i in range(len(word)):
        if node.children is None:
            node.children = {word[i]: Node()}
        elif word[i] not in node.children:
            node.children[word[i]] = Node()
        node = node.children[word[i]]
    node.badword = word
    # node.isEnd = 1


# 初始化节点
def init():
    root_node = Node()
    # result = u"卧槽\n尼玛\n"
    '''#-------------------------------------------
    #从数据库中读取
    db = DBUtils.DBUtils('localhost','root','4521','test')
    db.set_table("base_badwords")
    result = db.select(['words'])
    for line in result:
       #只匹配中文/英文/数字
      #li = ''.join(re.findall(re.compile(u'[a-zA-Z0-9\u4e00-\u9fa5]'),line[0]))
       #if li:
       #    add_word(root,li.lower())
       add_word(root,line[0].lower())
    return root
    '''

    # 从文件中读取
    for sensitive in Sensitive.objects.all():
        sensitive_word = sensitive.word
        add_word(root_node, sensitive_word.strip().lower())
    data = pickle.dumps(obj=root_node)
    with open(PICKLE_DIR/'sensitive.pickle', mode='wb') as fp:
        fp.write(data)


def is_contain(message):
    for i in range(len(message)):
        f = open(PICKLE_DIR/"sensitive.pickle", "rb+")
        p = pickle.load(f)
        j = i
        while j < len(message) and p.children is not None and message[j] in p.children:
            p = p.children[message[j]]
            j = j + 1
        if p.badword == message[i:j]:
            # print '--word--',p.badword,'-->',message
            yield p.badword
            # if p.isEnd:
            # return message[i:j]
    return 0

