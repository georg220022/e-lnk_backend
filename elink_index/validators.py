from django.utils import timezone
from django.shortcuts import get_object_or_404
from service.server_stat import ServerStat
from datetime import datetime
from .models import LinkRegUser
from typing import Dict, Union
from django.http import HttpRequest
from django.core.cache import cache


class CheckLink:
    @staticmethod  # Класс метод под вопросом
    def get_long_url(request_data: Dict, fast_link=False) -> Union[bool, str]:
        long_link = request_data.get("longLink", False)
        if long_link and len(long_link) < 5001:
            if "https://" == long_link[0:8] or "http://" == long_link[0:7]:
                return long_link
            else:
                long_link = "http://" + long_link
                return long_link
        cache.incr("server_no_long_link")
        return False

    @staticmethod
    def check_limited(obj: LinkRegUser, secure=False) -> bool:
        if not secure:
            limited_link = obj.limited_link
        else:
            limited_link = obj["limited_link"]
        if limited_link <= -1:
            return True
        elif limited_link >= 1:
            obj.limited_link = obj.limited_link - 1
            obj.save()
            return True
        else:
            return False

    @staticmethod
    def check_pass(obj: LinkRegUser) -> bool:
        if str(obj.secure_link) == "":
            return True
        cache.incr("server_check_pass")
        return False

    @staticmethod
    def check_date_link(obj: LinkRegUser) -> bool:
        now = timezone.now()
        start = obj.start_link
        stop = obj.date_stop
        if (isinstance(start, datetime) and start > now) or (
            isinstance(stop, datetime) and stop > now
        ):
            cache.incr("server_open_bad_time")
            return False
        return True

    @staticmethod
    def check_request(obj: LinkRegUser) -> Union[bool, dict]:
        try:
            len_code = len(str(obj["shortCode"]))
            len_pass = len(str(obj["linkPassword"]))
            if (len_code and len_pass) < 17 and (len_code and len_pass) > 0:
                data = {
                    "shortCode": str(obj["shortCode"]),
                    "linkPassword": str(obj["linkPassword"]),
                }
                return data
            return False
        except KeyError as e:
            ServerStat.reported(
                "CheckLink_79",
                "Не получен один из требуемых объектов"
                + f" obj={obj}, текст ошибки: {e}",
            )
            cache.incr("server_bad_data")
            return False

    def description(request_obj: HttpRequest) -> Union[bool, LinkRegUser]:
        obj_id = request_obj.data.get("shortLink", False)
        if obj_id:
            obj_id = obj_id[17:]
        print(obj_id)
        link_obj = get_object_or_404(LinkRegUser, short_code=obj_id)
        if request_obj.user.id == link_obj.author.id:
            if "linkName" in request_obj.data:
                return link_obj
            if "linkPassword" in request_obj.data:
                return link_obj
        cache.incr("server_bad_edit_descrip")
        return False
