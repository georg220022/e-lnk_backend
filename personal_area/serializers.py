import datetime

from rest_framework import serializers
from service.cache_module import CacheModule
from service.user_time_now import UserTime
from service.statistic_link import StatLink

from elink_index.models import LinkRegUser

SITE_NAME = "https://e-lnk.ru/"


class StatSerializer(serializers.ModelSerializer):

    statistics = serializers.SerializerMethodField(read_only=True)
    lock = serializers.SerializerMethodField(read_only=True)
    linkId = serializers.ModelField(model_field=LinkRegUser()._meta.get_field("id"))
    shortLink = serializers.SerializerMethodField("get_short_link")
    longLink = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("long_link")
    )
    linkName = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("description")
    )
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
        fields = ("qr",)
        read_only_fields = ("__all__",)

    def to_representation(self, instance):
        """
        Если запрос пришел из панели или из фоновых задач celery
            изменить время под UTC пользователя указанное в настройках
        """
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

    def get_short_link(self, obj: LinkRegUser) -> str:
        short_link = SITE_NAME + obj.short_code
        return short_link

    def get_statistics(self, obj: LinkRegUser) -> dict:
        obj_lnk = self.context["query_list"]
        user_tz = self.context["user_tz"]
        day_week = UserTime.day_week_now(user_tz, need_day_week=True)
        data = [
            obj_lnk.pop(obj_lnk.index(info_lnk))
            for info_lnk in obj_lnk
            if info_lnk["link_check_id"] == obj.id
        ]
        hour, device, countrys = StatLink.per_24_hour(data, user_tz)
        re_clicked_today, clicked_today = CacheModule.get_today_click_link(obj)
        data_obj = {
            "country": countrys,
            "device": device,
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
                1: device[1],
                2: device[2],
                3: device[3],
                4: device[4],
                5: device[5],
                6: device[6],
                7: device[7],
            }
            device = {
                "1": device[1] + device[3] + device[4],
                "2": device[2] + device[5] + device[6],
                "3": device[7],
            }
            data_obj["days"] = days
            data_obj["os"] = os
        else:
            clicked = {
                "mobile": device[1] + device[3] + device[4],
                "pc": device[2] + device[5] + device[6],
                "other": device[7],
            }
            data_obj["clicks"] = clicked
        return data_obj

    def get_lock(self, obj):
        if len(obj.secure_link) > 0:
            return True
        return False


"""exclude = (
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
        )"""
