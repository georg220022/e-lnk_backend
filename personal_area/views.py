from rest_framework import status, viewsets
from rest_framework.response import Response
from .pagination import ChangePagination
from elink_index.models import LinkRegUser
from django.contrib.auth.decorators import login_required


class PersonalStat(viewsets.ModelViewSet):

    def get_pagination(self):
        return ChangePagination.for_all_stat(self)

    #@login_required
    def all_stat(self, request):
        data = LinkRegUser.objects.filter(author=request.user)
        print(data)
        return Response(data, status=status.HTTP_200_OK)

    def one_link_stat(self, request):
        pass