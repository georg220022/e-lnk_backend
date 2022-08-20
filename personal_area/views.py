from rest_framework import viewsets
from rest_framework.response import Response
from elink_index.models import LinkRegUser, InfoLink
from .serializers import StatSerializer
from elink.settings import CACHE_TABLE
from django.core.cache import cache


class PersonalStat(viewsets.ViewSet):

    def get_full_stat(self, request):
        # print(ServerStat.today())
        #time2 = 12
        #ServerStat.reported(f'psnl_vie2w_{time2}', 'отправлено из фоновых задач')
        # cache.set(f'{self.request.user.id}')
        old_data = cache.get(f'{self.request.user.id}')
        if old_data:
            return Response(old_data)
        queryset = LinkRegUser.objects.filter(author=self.request.user)
        query_context = InfoLink.objects.filter(link_check__in=queryset)
        serializer = StatSerializer(queryset, context=query_context, many=True)
        data = serializer.data
        fake_day = {
                    'day': {1: 0, 2: 0, 3: 0, 4: 0,
                            5: 0, 6: 0, 7: 0},
                    }
        if request.user.subs_type != 'REG':
            days_data = cache.get(f'week_{request.user.id}')
            if days_data:
                days_data = {'day': days_data}
                data.append(days_data)
            else:
                data.append(fake_day)
        else:
            data.append(fake_day)
        cache.set(f'{request.user.id}', data, int(CACHE_TABLE))
        return Response(data)
