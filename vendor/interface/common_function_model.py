# -*- coding: utf-8 -*-
# Author: YuYuE (1019303381@qq.com) 2018.01.18
import re


# 去除标点符号
def remove_special_tags(str_):
    r = '[’!"#$%&\'()*+,-./:;<=>?？。！￥……【】、，：；‘’”“@[\\]^_`{|}~]+'
    result = re.sub(r, '', str_)
    return result
