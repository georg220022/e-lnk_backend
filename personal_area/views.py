import logging
from collections import OrderedDict
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from elink_index.models import LinkRegUser, InfoLink
from .serializers import StatSerializer
from elink_index.models import InfoLink
from django.core.cache import cache
from rest_framework import status
from django.http import HttpRequest
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes

logger = logging.getLogger(__name__)


class PersonalStat(viewsets.ViewSet):
    def get_permissions(self):
        return (permissions.IsAuthenticated(),)
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="email",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Email от аккаунта",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Почта",
                    # description="Пароль от аккаунта",
                    value="email_you_account"
                    ),
                ],
            ),
        ],
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за сброс пароля",
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS", "timezone": "+3"})
        ],
    )
    def get_full_stat(self, request: HttpRequest) -> Response:
        old_data = cache.get(request.user.id)
        if old_data:
            cache.incr("server_get_stat_in_cache")
            if len(old_data[0]) > 0:
                old_data[0].update({"ttl": cache.ttl(request.user.id)})
            else:
                old_data = []
            return Response(old_data)
        queryset = (
            InfoLink.objects.select_related("link_check")
            .only("author_id")
            .filter(link_check__author_id=request.user)
        )
        query_list = list(queryset.values())
        delete_id = [obj["id"] for obj in query_list]
        queryset.filter(id__in=delete_id).delete()
        context = {
            "query_list": query_list,
            "action": self.action,
            "user_tz": request.user.my_timezone,
            "optimize_panel": False,
        }
        serializer = StatSerializer(
            LinkRegUser.objects.filter(author=request.user),
            context=context,
            many=True,
        )
        data = serializer.data
        cache.set(f"{request.user.id}", data, int(cache.get("live_cache")))
        if len(data) > 0:
            data[0].update({"ttl": cache.ttl(request.user.id)})
        cache.set(
            f"count_infolink_{request.user.id}", 0, 200000
        )  # Пользователь обращался к панели, значит у него нет не подсчитанных данных
        cache.incr("server_get_stat_in_serializer")
        return Response(data, status=status.HTTP_200_OK)
