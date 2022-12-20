from django.core.paginator import Paginator

LENGHT_LIST = 10


def get_paginator(query_list, request):
    paginator = Paginator(query_list, LENGHT_LIST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
