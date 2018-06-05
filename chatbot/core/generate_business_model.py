# Author: YuYuE (1019303381@qq.com) 2018.03.16
from data_admin.models import Business_structure
from data_admin.models import Business_production
from data_admin.models import Business_operation
from data_admin.models import Business_formula
from data_admin.models import Business_keywords
from chatbot.settings import PICKLE_DIR
import pickle


def siphon_business_structure(name, bank=None, area=None, like=False, field='name'):
    """
    抽取业务信息，业务id，业务名称，上级业务id  tzinfo报错
    :param name:
    :param bank:
    :param area:
    :param like
    :param field
    :return:
    """
    result = {}
    if bank and area:
        business_structure = Business_structure.objects.filter(name=name, bank=bank, area=area)[:10]
    elif bank and area is None:
        business_structure = Business_structure.objects.filter(name=name, bank=bank)[:10]
    elif bank is None and area:
        business_structure = Business_structure.objects.filter(name=name, area=area)[:10]
    elif like:
        business_structure = Business_structure.objects.filter(name__contains=name)[:10]
    else:
        business_structure = Business_structure.objects.filter(name=name)[:10]
    cnt = business_structure.count()
    if cnt == 1:
        result['business_id'] = business_structure[0].id
        result['business_name'] = business_structure[0].name
        result['parent_id'] = business_structure[0].parent_id
        return [business_structure[0].name]
    elif cnt > 1:
        if field:
            fields = []
            for business in business_structure:
                if business.name not in fields:
                    fields.append(business.name)
            return fields
    else:
        pass
    # print(result)
    return result


def siphon_same_level_business(id=False, name=None):
    """
    取同级业务数据
    :param id:
    :param name:
    :return:
    """
    business_sets = business_sets_ = []
    if id and name is None:
        business_sets_ = Business_structure.objects.filter(parent_id=id)
    elif id is False and name:
        business_structure = siphon_business_structure(name)
        business_sets_ = Business_structure.objects.filter(parent_id=business_structure['parent_id'])
    else:
        pass
    if business_sets_:
        for business in business_sets_:
            business_sets.append(business.name)
    # print(business_sets)
    return business_sets


def siphon_business_type(question, ners=False):
    """
    业务分类，咨询类，流程类，计算类
    :param question:
    :return:
    """
    type_ = ''
    if question.find('是什么') != -1 or question.find('什么是') != -1:
        type_ = 'production'
    elif question.find('怎么') != -1 or question.find('怎样') != -1:
        type_ = 'operation'
    elif question.find('怎么计算') != -1 or question.find('怎么算') != -1 or question.find('是多少') != -1:
        type_ = 'formula'
    else:
        is_operation = siphon_business_operation(False, ners)
        if is_operation:
            type_ = 'operation'
        else:
            type_ = 'production'
    return type_


def siphon_business_production(id=False, product=None):
    """
    获取业务相关产品信息 tzinfo报错  create_time字段导致
    :param id:
    :param product:
    :param same:
    :return:
    """
    business_sets_ = []
    if id and product is None:
        business_sets_ = Business_production.objects.filter(id=id)[:10]
    elif id is False and product:
        business_sets_ = Business_production.objects.filter(product=product)[:10]
    else:
        pass
    return business_sets_


def siphon_business_operation(id=False, name=None, same=False):
    """
    获取业务相关操作流程
    :param id:
    :param name:
    :param same:
    :return:
    """
    business_sets = {}
    business_sets_ = []
    if id and name is None:
        business_sets_ = Business_operation.objects.filter(id=id)
    elif id is False and name:
        business_sets_ = Business_operation.objects.filter(name=name)
    else:
        pass
    # 取最佳匹配
    if len(business_sets_) == 1:
        business_sets['operation_id'] = business_sets_[0].id
        business_sets['operation_name'] = business_sets_[0].name
        business_sets['item'] = business_sets_[0].item
        business_sets['description'] = business_sets_[0].description
    elif len(business_sets_) > 1:
        pass
    else:
        pass
    business_sets_ = []
    # 取同级信息
    if business_sets and same is False:
        return business_sets
    elif business_sets and same:
        same_business = Business_operation.objects.filter(item=business_sets['item'])
        if same_business:
            for same_ in same_business:
                business_sets_.append(same_.name)
        return business_sets_
    return business_sets


def siphon_linked_operation(item):
    business_sets_ = []
    if item:
        same_business = Business_operation.objects.filter(item=item)
        if same_business:
            for same_ in same_business:
                business_sets_.append(same_.name)
    return business_sets_


def siphon_reference_business_operation(id=False, name=None, num=2):
    """
    获取流程相关操作
    :param id:
    :param name:
    :param num:
    :return:
    """
    business_sets = siphon_business_operation(id, name)
    if business_sets:
        business_sets_ = Business_operation.objects.filter(business_id=business_sets['business_id']).order_by('id')
        if business_sets_:
            cnt = len(business_sets_)
            min_step = business_sets_[0].id
            max_step = business_sets_[cnt - 1].id
            if business_sets['operation_id'] == min_step:
                business_sets['position'] = 'first'
                reference = []
                for business in business_sets_:
                    if (business.id < min_step + num + 1) and business.id > business_sets['operation_id']:
                        reference.append(business.name)
                business_sets['reference'] = reference
            elif business_sets['operation_id'] == max_step:
                business_sets['position'] = 'last'
                reference = []
                for business in business_sets_:
                    if (business.id > max_step - num - 1) and business.id < business_sets['operation_id']:
                        reference.append(business.name)
                business_sets['reference'] = reference
            else:
                business_sets['position'] = 'mid'
                reference = []
                min_temp = business_sets['operation_id'] - num / 2 - 1
                max_temp = business_sets['operation_id'] + num / 2 + 1
                for business in business_sets_:
                    if (business.id > min_temp) and (business.id < max_temp) and \
                                    business.id != business_sets['operation_id']:
                        reference.append(business.name)
                business_sets['reference'] = reference
    # print(business_sets)
    return business_sets


def siphon_business_formula(id=False, name=None, same=False):
    """
    获取业务相关计算公式
    :param id:
    :param name:
    :param same:
    :return:
    """
    business_sets = {}
    business_sets_ = []
    if id and name is None:
        business_sets_ = Business_formula.objects.filter(id=id)
    elif id is False and name:
        business_sets_ = Business_formula.objects.filter(name=name)
    else:
        pass
    # 取最佳匹配
    if len(business_sets_) == 1:
        business_sets['formula_id'] = business_sets_[0].id
        business_sets['formula_name'] = business_sets_[0].name
        business_sets['formula_params'] = business_sets_[0].params
        business_sets['formula'] = business_sets_[0].formula
        business_sets['business_id'] = business_sets_[0].business_id
    elif len(business_sets_) > 1:
        pass
    else:
        pass
    business_sets_ = []
    # 取同级信息
    if business_sets and same is False:
        return business_sets
    elif business_sets and same:
        same_business = Business_formula.objects.filter(business_id=business_sets['business_id'])
        if same_business:
            for same_ in same_business:
                business_sets_.append(same_.name)
        return business_sets_
    return business_sets


def detect_business_scene(inp, ners):
    result = {}
    business_type = siphon_business_type(inp, ners)
    if business_type == 'production':
        references = siphon_same_level_business(False, ners)
    elif business_type == 'operation':
        references = siphon_reference_business_operation(False, ners)
    else:
        references = siphon_business_formula(False, ners)
    result['type'] = business_type
    result['reference'] = references
    return result


def siphon_business_keywords(name):
    """
    抽取业务信息，业务id，业务名称，上级业务id
    :param name:
    :param bank:
    :param area:
    :return:
    """
    result = {}
    business_keywords = []
    if name:
        business_keywords = Business_keywords.objects.filter(keyword=name)
    if len(business_keywords) == 1:
        result['type_id'] = business_keywords[0].type_id
        result['type_name'] = business_keywords[0].type_name
    elif len(business_keywords) > 1:
        pass
    else:
        pass
    # print(result)
    return result


def encode_ontology_pickle():
    keywords = []
    business_keywords = Business_keywords.objects.values("keyword").filter(type_id=1)
    if business_keywords:
        for business_keyword in business_keywords:
            if business_keyword['keyword'] not in keywords:
                keywords.append(business_keyword['keyword'])
    fp = open(PICKLE_DIR / 'ontology_keywords.pickle', 'wb')
    pickle.dump(keywords, fp, True)


def decode_ontology_pickle():
    f = open(PICKLE_DIR / 'ontology_keywords.pickle', "rb+")
    keywords = pickle.load(f)
    return keywords


def encode_attr_pickle():
    keywords = []
    business_keywords = Business_keywords.objects.values("keyword").filter(type_id__gt=1)
    if business_keywords:
        for business_keyword in business_keywords:
            if business_keyword['keyword'] not in keywords:
                keywords.append(business_keyword['keyword'])
    fp = open(PICKLE_DIR / 'attr_keywords.pickle', 'wb')
    pickle.dump(keywords, fp, True)


def decode_attr_pickle():
    f = open(PICKLE_DIR / 'attr_keywords.pickle', "rb+")
    keywords = pickle.load(f)
    return keywords


if __name__ == "__main__":
    bs = siphon_business_keywords("信用卡")
    for b in len(bs):
        print(b)
