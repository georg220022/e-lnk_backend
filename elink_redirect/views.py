from typing import Union
from django.shortcuts import redirect
from django.http import HttpRequest
from django.core.cache import cache

from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, throttle_classes, permission_classes

from service.read_write_base import RedisLink, PostgresLink
from service.stat_get import StatisticGet
from elink.settings import TIME_SAVE_COOKIE
from service.validators import CheckLink

from .throttle import PassAnonymousThrottle, PassLinkUserThrottle


def open_link(request: HttpRequest, short_code: str) -> Union[Response, redirect]:
    """Модуль открытия ссылки по короткой ссылке"""
    if len(str(short_code)) == 11:
        object_redis = RedisLink.reader(short_code)
        if object_redis:
            cache.incr("server_redis_redirect")
            return redirect(object_redis["long_link"])
        object_postgres = PostgresLink.reader(short_code)
        if object_postgres is not False:
            time_lnk = CheckLink.check_date_link(object_postgres)
            if time_lnk:
                if time_lnk == "bad_date_end":
                    return redirect("https://e-lnk.ru/bad_date_end")
                return redirect("https://e-lnk.ru/bad_date_start")
            if not CheckLink.check_pass(object_postgres):
                data = {
                    "short_code": object_postgres.short_code,
                    "long_link": object_postgres.long_link,
                    "password": object_postgres.secure_link,
                    "limited_link": object_postgres.limited_link,
                    "id": object_postgres.id,
                    "author_id": object_postgres.author_id,
                }
                cache.set(f"open_{object_postgres.short_code}", data, 1200)
                return redirect(
                    f"https://e-lnk.ru/password-check.html?open_{short_code}"
                )
            else:
                if not CheckLink.check_limited(object_postgres):
                    return redirect("https://e-lnk.ru/end_limit")
                StatisticGet.collect_stats(request, object_postgres)
                response = redirect(object_postgres.long_link)
                response.set_cookie(
                    f"{object_postgres.short_code}", max_age=int(TIME_SAVE_COOKIE)
                )
                return response
    cache.incr("server_open_bad_link")
    return redirect("https://e-lnk.ru/404")


@api_view(["POST"])
@permission_classes([AllowAny])
@throttle_classes([PassLinkUserThrottle, PassAnonymousThrottle])
def unlock_pass(request: HttpRequest) -> Response:
    """Если ссылка запаролена"""
    short_code = request.data.get("shortCode", False)
    passwd = request.data.get("password", False)
    if passwd and short_code:
        obj = cache.get(short_code)
        if obj:
            if str(obj["password"]) == passwd:
                if not CheckLink.check_limited(obj, secure=True):
                    datas = {"longLink": "https://e-lnk.ru/end_limit"}
                    response = Response(datas)
                    return response  # redirect("https://e-lnk.ru/end_limit")
                StatisticGet.collect_stats(request, obj, secure=True)
                datas = {"longLink": obj["long_link"]}
                response = Response(datas)
                response.set_cookie(obj["short_code"], max_age=int(TIME_SAVE_COOKIE))
                cache.incr("server_good_input_pass")
                return response
            data = {"error": "Пароль не верный"}
        else:
            data = {
                "error": "Вермя ввода пароля истекло, откроте изначальную ссылку вновь"
            }
            cache.incr("server_bad_input_pass")
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
    cache.incr("server_empty_pass_open_lnk")
    data = {"error": "Отсутствует поле или получено пустое значение"}
    return Response(data, status=status.HTTP_400_BAD_REQUEST)
