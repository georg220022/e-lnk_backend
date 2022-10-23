import datetime

from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.http import HttpRequest
from django.core.cache import cache
from typing import Dict, Union

from elink_index.models import LinkRegUser


class CheckLink:
    @staticmethod
    def get_long_url(request_data: Dict, fast_link=False) -> bool | str:
        """Проверка максимальной длинны ссылки для postgres'a и redis'a"""
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
        """Проверка имеется ли лимит у ссылки"""
        if not secure:
            limited_link = obj.limited_link
            ids = obj.id
        else:
            limited_link = obj["limited_link"]
            ids = obj["id"]
        if limited_link <= -1:
            return True
        elif limited_link >= 1:
            value = limited_link - 1
            LinkRegUser.objects.filter(id=ids).update(limited_link=value)
            return True
        else:
            return False

    @staticmethod
    def check_pass(obj: LinkRegUser) -> bool:
        """Имеется ли пароль у ссылки"""
        if str(obj.secure_link) == "":
            return True
        cache.incr("server_check_pass")
        return False

    @staticmethod
    def check_date_link(obj: LinkRegUser) -> bool | str:
        start = obj.start_link
        stop = obj.date_stop
        if not (start or stop) == "":
            now = timezone.now()  # datetime.datetime.now(datetime.timezone.utc)
            """Проверка ограничина ли дата использования ссылки"""
            if isinstance(start, datetime.datetime) and bool(start > now):
                cache.incr("server_open_bad_time")
                return "bad_date_start"
            if isinstance(stop, datetime.datetime):
                if stop < now:
                    cache.incr("server_open_bad_time")
                    return "bad_date_end"
        return False

    def description_or_pass(request_obj: HttpRequest) -> Union[bool, LinkRegUser]:
        """Проверка прав редактирования описания ссылки"""
        obj_id = request_obj.data.get("shortLink", False)
        if obj_id:
            obj_id = obj_id[9:]
        link_obj = get_object_or_404(LinkRegUser, short_code=obj_id)
        if request_obj.user.id == link_obj.author.id:
            if "linkName" in request_obj.data:
                return link_obj
            if "linkPassword" in request_obj.data:
                return link_obj
        cache.incr("server_bad_edit_descrip")
        return False


# Походу придется выкинуть этот код
"""class CheckSettings:
    @staticmethod
    def validate(user_id, obj):
        user = User.objects.get(id=user_id)
        data = {
            "id": user_id,
        }
        old_pass = obj.pop("password", False)
        if old_pass:
            if not user.check_password(str(old_pass)):
                msg = "Пароль не верный! Настройки не были изменены."
                return msg
        else:
            msg = {"error": "Введите ваш текущий пароль что бы внести изменения"}
            return msg
        utc = obj.pop("utc", False)
        if utc:
            if isinstance(utc, int):
                if utc != user.my_timezone:
                    if utc < 12 and utc > -12:
                        data["my_timezone"] = utc
                    else:
                        msg = "масильное смещение по UTC от -12 до +12"
                        return msg
                else:
                    msg = "Это ваше текущее время UTC, введите другое смещение либо оставьте поле пустым. Настройки не изменились"
                    return msg
            else:
                msg = "UTC должно быть числом"
                return msg
        send_stat = obj.pop("sendStat", "None")
        if isinstance(send_stat, bool):
            if user.subs_type != "REG":
                data["send_stat_email"] = send_stat
            else:
                msg = "Ваш тип подписки не позволяет получать PDF файл статистики на почту"
                return msg
        new_pass = obj.pop("newPass", False)
        if new_pass:
            if len(new_pass) > 7 and len(new_pass) < 17:
                if isinstance(utc, str):
                    user.set_password(new_pass)
                else:
                    msg = "Пароль должен быть строкой"
                    return msg
            else:
                msg = "Минимальная длинна пароля 8, максимальная 16 симолов"
                return msg
        return data
"""
