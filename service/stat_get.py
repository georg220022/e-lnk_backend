from typing import Union

from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpRequest
from datetime import datetime as dt

from elink_index.models import LinkRegUser, InfoLink
from service.country_get import DetectCountry
from service.server_stat import ServerStat
from .write_stat import WriteStat


class StatisticGet:
    @staticmethod
    def check_device(request_meta: dict) -> int:
        device_name = request_meta["HTTP_USER_AGENT"].lower()
        if "android" in device_name:
            return 1
        elif "windows" in device_name:
            return 2
        elif "iphone" in device_name:
            return 3
        elif ("mac" and "pad") in device_name:
            return 4
        elif "linux" in device_name:
            return 5
        elif "mac" in device_name:
            return 6
        else:
            ServerStat.reported(
                "CheckLink_50", f"Определение устройства не удалось obj={device_name}"
            )
            return 7

    @staticmethod
    def collect_stats(
        request_obj: HttpRequest, obj: Union[LinkRegUser, dict], secure=False
    ) -> None:
        date_check = (
            timezone.now()
        )  # по идее мне нужно время голого utc  # time.strftime("%Y-%m-%d %H:%M") было так и джанго жаловался на наивное время
        device_id = StatisticGet.check_device(request_obj.META)
        country = DetectCountry.get_client_ip(request_obj)
        if cache.get("count_cache_infolink") > 1000:
            WriteStat.one_hour()
            cache.incr("server_need_clear_cache")
        if not secure:
            short_code = obj.short_code
            ids = obj.id
            author_id = obj.author_id
        else:
            short_code = obj["short_code"]
            ids = obj["id"]
            author_id = obj["author_id"]
        if not cache.has_key(f"statx_click_{author_id}_{ids}"):
            cache.set(f"statx_click_{author_id}_{ids}", 0, 180000)
        cache.incr(f"statx_click_{author_id}_{ids}")
        if short_code in request_obj.COOKIES:
            if not cache.has_key(f"statx_aclick_{author_id}_{ids}"):
                cache.set(f"statx_aclick_{author_id}_{ids}", 0, 180000)
            cache.incr(f"statx_aclick_{author_id}_{ids}")
        data = InfoLink(
            date_check=date_check,
            country=country,
            device_id=device_id,
            link_check_id=ids,
        )
        cache.set(f"statx_info_{dt.now()}", data, 180000)
        cache.incr("count_cache_infolink")

    @staticmethod
    def description(request: HttpRequest) -> Union[LinkRegUser, bool]:
        obj_id = request.data.get("shortCodes", False)
        link_obj = get_object_or_404(LinkRegUser, short_code=obj_id)
        if request.user.id == link_obj.author.id:
            obj_descrip = request.data.get("linkDescription", False)
            if obj_descrip is not False:
                if len(obj_descrip) > 0 and len(obj_descrip) <= 1000:
                    return link_obj
        return False
