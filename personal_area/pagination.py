from secrets import choice
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class PanelPagination(PageNumberPagination):

    page_size = 250
    page_size_query_param = 'page_size'
    max_page_size = 250

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


class ChangePagination:

    def for_all_stat(obj_self):
        if obj_self.action == 'all_stat':
            pagination_class = [PanelPagination]
            return [paginator() for paginator in pagination_class]
