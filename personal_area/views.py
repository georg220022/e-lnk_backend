from rest_framework import viewsets
from rest_framework.response import Response
from elink_index.models import LinkRegUser, InfoLink
from .serializers import StatSerializer
from django.core.cache import cache
from elink.settings import CACHE_TABLE


class PersonalStat(viewsets.ViewSet):

    def get_full_stat(self, request):
        # cache.clear()
        old_data = cache.get(f'{self.request.user.id}')
        if old_data:
            return Response(old_data)
        queryset = LinkRegUser.objects.filter(author=self.request.user)
        query_context = InfoLink.objects.filter(link_check__in=queryset)
        serializer = StatSerializer(queryset, context=query_context, many=True)
        data = serializer.data
        cache.set(f'{request.user.id}', data, CACHE_TABLE)
        return Response(data)
