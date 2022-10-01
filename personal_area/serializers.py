from collections import OrderedDict
import datetime
from django.core.cache import cache
from rest_framework import serializers
from service.cache_module import CacheModule
from service.user_time_now import UserTime
from service.statistic_link import StatLink

from elink_index.models import LinkRegUser

SITE_NAME = "e-lnk.ru/"


class StatSerializer(serializers.ModelSerializer):

    statistics = serializers.SerializerMethodField(read_only=True)
    lock = serializers.SerializerMethodField(read_only=True)
    linkId = serializers.ModelField(model_field=LinkRegUser()._meta.get_field("id"))
    shortLink = serializers.SerializerMethodField("get_short_link")
    longLink = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("long_link")
    )
    linkName = serializers.SerializerMethodField("get_description")
    linkLimit = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("limited_link")
    )
    linkPassword = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("secure_link")
    )
    linkStartDate = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("start_link")
    )
    clicked = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("how_many_clicked")
    )
    repeatedClicked = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("again_how_many_clicked")
    )
    linkStartDate = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M", source="start_link", read_only=True
    )
    linkCreatedDate = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M", source="date_add", read_only=True
    )
    linkEndDate = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M", source="date_stop", read_only=True
    )
    qr = serializers.CharField(read_only=True)

    class Meta:
        model = LinkRegUser
        read_only_fields = ("__all__",)
        exclude = (
            "short_code",
            "long_link",
            "start_link",
            "secure_link",
            "date_stop",
            "author",
            "date_add",
            "public_stat_full",
            "public_stat_small",
            "again_how_many_clicked",
            "how_many_clicked",
            "limited_link",
            "description",
            "id",
        )

    def to_representation(self, instance):
        """
        Если запрос пришел из панели или из фоновых задач celery
            изменить время под UTC пользователя указанное в настройках
        """
        if self.context["action"] == "get_full_stat":
            if cache.has_key(f"statx_click_{instance.author_id}_{instance.id}"):
                click_cache = cache.get(
                    f"statx_click_{instance.author_id}_{instance.id}"
                )
                instance.how_many_clicked = instance.how_many_clicked + click_cache
            if cache.has_key(f"statx_aclick_{instance.author_id}_{instance.id}"):
                aclick_cache = cache.get(
                    f"statx_aclick_{instance.author_id}_{instance.id}"
                )
                instance.again_how_many_clicked = (
                    instance.again_how_many_clicked + aclick_cache
                )
        if self.context["action"] == "get_full_stat" or "task_celery":
            user_tz = datetime.timedelta(hours=int(self.context["user_tz"]))
            if isinstance(instance.start_link, datetime.datetime):
                instance.start_link = instance.start_link + user_tz
            else:
                instance.start_link = instance.date_add + user_tz
            if isinstance(instance.date_stop, datetime.datetime):
                instance.date_stop = instance.date_stop + user_tz
            else:
                instance.date_stop = "-1"
            instance.date_add = instance.date_add + user_tz
        data = super(StatSerializer, self).to_representation(instance)
        return data

    def get_description(self, obj: LinkRegUser) -> str:
        if obj.description == "":
            bad_word = ["https://www.", "http://www.", "https://", "http://", "wwww."]
            for objs in bad_word:
                len_objs = len(objs)
                if objs == obj.long_link[0:len_objs]:
                    if self.context["action"] == "get_full_stat":
                        return obj.long_link[len(objs) :]
                    if self.context["action"] == "task_celery":
                        name_lnk = obj.long_link[len(objs) :]
                        return name_lnk[:24]
            if self.context["action"] == "get_full_stat":
                return obj.long_link
            if self.context["action"] == "task_celery":
                return obj.long_link[:24]
        return obj.description

    def get_short_link(self, obj: LinkRegUser) -> str:
        short_link = SITE_NAME + obj.short_code
        return short_link

    def get_statistics(self, obj: LinkRegUser) -> dict:
        obj_lnk = self.context["query_list"]
        user_tz = self.context["user_tz"]
        user_id = obj.author_id
        day_week = UserTime.day_week_now(user_tz, need_day_week=True)
        data = [info_lnk for info_lnk in obj_lnk if info_lnk["link_check_id"] == obj.id]
        hour, device_id, countrys = StatLink.per_24_hour(data, user_tz)
        re_clicked_today, clicked_today = CacheModule.get_today_click_link(obj)
        keys_cache_info_link = cache.keys(f"statx_info_{obj.id}*")
        click_cache = list(
            OrderedDict(
                cache.get_many(keys_cache_info_link)
            ).values()  # Получаем информацию о всех кликах в кеше (их не больше 1000, так как при достижении 1000 запией происходить запись в БД и лчистка данных из кеша)
        )
        if len(click_cache) > 0:
            user_tz = int(
                UserTime.day_week_now(user_tz, need_day_week=False).strftime("%H")
            )
            (
                hour_cache,
                device_cache,
                countrys_cache,
            ) = StatLink.real_time_stat_from_cache(
                click_cache, user_tz, device_id, countrys, hour, obj.id
            )
            hour, device_id, countrys = hour_cache, device_cache, countrys_cache
        if cache.has_key(f"calculated_{user_id}_{obj.id}"):
            hour, device_id, countrys = CacheModule.get_save_and_remove_infolink(
                obj, hour, device_id, countrys
            )
        data_calculated_info = [hour, device_id, countrys]
        cache.set(f"calculated_{user_id}_{obj.id}", data_calculated_info, 180000)
        cache.delete_many(keys_cache_info_link)
        if self.context["optimize_panel"]:
            return "ok"
        if len(obj_lnk) > 0:
            self.context["queryset"].delete()
        data_obj = {
            "country": countrys,
            "device": device_id,
            "hours": hour,
            "reClickedToday": re_clicked_today,
            "clickedToday": clicked_today,
        }
        """
        Если запрос пришел из панели управления
            отдаем полную информацию за сегодняшний день.
        В ином случае полная статистика не нужна, достаточно 
            с каких устройств и сколько раз перешли
        """
        if self.context["action"] == "get_full_stat":
            days = CacheModule.get_days_click_link(day_week, obj)
            actual_click_today = days[day_week] + clicked_today
            days[day_week] = actual_click_today
            os = {
                1: device_id[1],
                2: device_id[2],
                3: device_id[3],
                4: device_id[4],
                5: device_id[5],
                6: device_id[6],
                7: device_id[7],
            }
            device = {
                "1": device_id[1] + device_id[3] + device_id[4],
                "2": device_id[2] + device_id[5] + device_id[6],
                "3": device_id[7],
            }
            data_obj["days"] = days
            data_obj["os"] = os
            data_obj["device"] = device
            if len(data_obj["country"]) == 0:
                data_obj["country"] = {"Страны": 0}
            # если список стран больше 9, тогда собираем самые мелкие в категорию <<Другие>>
            elif len(data_obj["country"]) >= 10:
                sorted_country = sorted(
                    data_obj["country"].items(), key=lambda item: item[1]
                )
                list_country = sorted_country[:-10:-1]
                ready_country = {"Другие": sum(list(zip(*sorted_country[:-10]))[1])}
                for obj in list_country:
                    ready_country[obj[0]] = obj[1]
                data_obj["country"] = ready_country
            data_obj["hours"].update(
                {24: 0}
            )  # Фронтендер сказал добавить "24", что бы JS адекватно сработал
        else:
            clicked = {
                "mobile": device_id[1] + device_id[3] + device_id[4],
                "pc": device_id[2] + device_id[5] + device_id[6],
                "other": device_id[7],
            }
            data_obj["clicks"] = clicked
        if self.context["optimize_panel"]:
            return True
        return data_obj

    def get_lock(self, obj):
        if len(obj.secure_link) > 0:
            return True
        return False
