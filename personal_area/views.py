from rest_framework import status, viewsets
from rest_framework.response import Response
from .pagination import ChangePagination
from elink_index.models import LinkRegUser, InfoLink
#from .decorators import cache_stat
from .serializers import StatSerializer
from elink.settings import REDIS_BASE_FOR_STAT as cache_base
from django.core.cache import cache

"""class RedisCache:

    def cache_stat(self, request):
        if request.user.id in cache_base.keys():
            queryset = cache_base.get(request.user.id)
            return """



class PersonalStat(viewsets.ViewSet):


    def get_full_stat(self, request):
        cache.clear()
        old_data = cache.get(f'{self.request.user.id}')
        if old_data:
            return Response(old_data)
        queryset = LinkRegUser.objects.filter(author=self.request.user)
        serializer = StatSerializer(queryset, many=True)
        data = serializer.data
        cache.set(f'{request.user.id}', data, 10000)
        return Response(data)
