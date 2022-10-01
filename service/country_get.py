import geoip2.database
from django.http import HttpRequest
from django.core.cache import cache

from elink.settings import BASE_DIR

from .server_stat import ServerStat


reader = geoip2.database.Reader(f"{BASE_DIR}/data.mmdb")


class DetectCountry:
    def get_client_ip(request: HttpRequest) -> str:
        ip = request.META.get("HTTP_REAL_IP")
        if not ip:
            ip = request.META.get("HTTP_X_FORWARDED_FOR")
        if not ip:
            obj = "Не определено"
            return obj
        try:
            response = reader.country(ip)
            data_country = response.country.names
            obj = data_country.get("ru", "Нет русского перевода страны")
        except ValueError:
            cache.incr("server_unknown_coutry")
            obj = "Не определено"
            ServerStat.reported(
                f"cntry_get_ip={ip}", "Не удалось найти ip адрес в базе"
            )
        return obj
