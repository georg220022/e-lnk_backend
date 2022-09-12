import logging
from rest_framework import viewsets
from rest_framework.response import Response
from elink_index.models import LinkRegUser, InfoLink
from .serializers import StatSerializer
from elink_index.models import InfoLink
from django.core.cache import cache
from rest_framework import status
from django.http import HttpRequest

logger = logging.getLogger(__name__)



class PersonalStat(viewsets.ViewSet):
    def get_full_stat(self, request: HttpRequest) -> Response:
        logger.warning("Проверка отправки!")
        old_data = cache.get(request.user.id)
        if old_data:
            cache.incr("server_get_stat_in_cache")
            old_data.append({"ttl": cache.ttl(request.user.id)})
            return Response(old_data)
        query_list = list(
            InfoLink.objects.select_related("link_check")
            .only("author_id")
            .filter(link_check__author_id=request.user)
            .values()
        )
        context = {
            "query_list": query_list,
            "action": self.action,
            "user_tz": request.user.my_timezone
        }
        serializer = StatSerializer(
            LinkRegUser.objects.filter(author=request.user),
            context=context,
            many=True,
        )
        data = serializer.data
        fake_day = {"day": {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}}
        if request.user.subs_type != "REG":
            days_data = cache.get(f"week_{request.user.id}")
            if days_data:
                days_data = {"day": days_data}
                data.append(days_data)
            else:
                data.append(fake_day)
        else:
            data.append(fake_day)
        cache.set(f"{request.user.id}", data, int(cache.get("live_cache")))
        data.append({"ttl": cache.ttl(request.user.id)})
        cache.incr("server_get_stat_in_serializer")
        return Response(data, status=status.HTTP_200_OK)
