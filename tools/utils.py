from django.core.paginator import Paginator, EmptyPage, InvalidPage


def pages(post_objects, request, context, page_num=15):
    """
    page public function , return page's object tuple
    分页公用函数，返回分页的对象元组
    """
    paginator = Paginator(post_objects, page_num)
    try:
        current_page = int(request.GET.get('page', '1'))
    except ValueError:
        current_page = 1

    page_range = page_list_return(len(paginator.page_range), current_page)

    try:
        page_objects = paginator.page(current_page)
    except (EmptyPage, InvalidPage):
        page_objects = paginator.page(paginator.num_pages)

    if current_page >= 5:
        show_first = 1
    else:
        show_first = 0

    if current_page <= (len(paginator.page_range) - 3):
        show_end = 1
    else:
        show_end = 0

    context['p'] = paginator
    context['obj'] = page_objects
    context['page_range'] = page_range
    context['current_page'] = current_page
    context['show_first'] = show_first
    context['show_end'] = show_end

    # 所有对象，    分页器，   本页对象，   所有页码，   本页页码，    是否显示第一页，是否显示最后一页
    return context


def page_list_return(total, current=1):
    """
    page
    分页，返回本次分页的最小页数到最大页数列表
    """
    min_page = current - 2 if current - 4 > 0 else 1
    max_page = min_page + 4 if min_page + 4 < total else total

    return range(min_page, max_page + 1)


def wechat_rec_deal(rec):
    result = ''
    if not rec:
        return  ''
    _l = rec.split()
    print(_l)
    n = 0
    for v in _l:
        if len(v) <= 25:
            n += 1
            result = result+str(n)+'、'+v+'\n'
    return result
