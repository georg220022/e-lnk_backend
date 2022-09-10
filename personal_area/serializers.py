from typing import Dict
import datetime

from django.core.cache import cache
from rest_framework import serializers

from elink.settings import SITE_NAME
from elink_index.models import LinkRegUser


class GetStatSerializer(serializers.Serializer):
    pass


class StatSerializer(serializers.ModelSerializer):

    statistics = serializers.SerializerMethodField(read_only=True)
    linkId = serializers.ModelField(model_field=LinkRegUser()._meta.get_field("id"))
    shortLink = serializers.SerializerMethodField("get_short_link")
    longLink = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("long_link")
    )
    linkDescription = serializers.ModelField(
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
    #linkCreatedDate = serializers.ModelField(
    #    model_field=LinkRegUser()._meta.get_field("date_add")
    #)
    clicked = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("how_many_clicked")
    )
    repeatedClicked = serializers.ModelField(
        model_field=LinkRegUser()._meta.get_field("again_how_many_clicked")
    )
    linkStartDate = serializers.DateTimeField(format="%Y-%m-%dT%H:%MZ", source="start_link", read_only=True) # format="%Y-%m-%dT%H:%M:%S%z",  format="%Y-%m-%dT%H:%M:%S%Z", 
    linkCreatedDate = serializers.DateTimeField(format="%Y-%m-%dT%H:%MZ", source="date_add", read_only=True)# input_formats=None format="%Y-%m-%dT%H:%M:%S",
    linkEndDate = serializers.DateTimeField(format="%Y-%m-%dT%H:%MZ", source="date_stop", read_only=True)
    qr = serializers.CharField(read_only=True)

    class Meta:
        model = LinkRegUser
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
        read_only_fields = ("__all__",)

    def to_representation(self, instance):
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
            print('huy')
            
            #instance.remove('date_stop')
            print(instance)
        data = super(StatSerializer, self).to_representation(instance)
        return data

    def get_short_link(self, obj: LinkRegUser) -> str:
        short_link = SITE_NAME + obj.short_code
        return short_link

    def get_statistics(self, obj: LinkRegUser) -> dict:
        obj_lnk = self.context["query_list"]
        user_tz = self.context["user_tz"]
        data = [
            obj_lnk.pop(obj_lnk.index(info_lnk))
            for info_lnk in obj_lnk
            if info_lnk["link_check_id"] == obj.id
        ]
        device = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
        hour = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
            7: 0,
            8: 0,
            9: 0,
            10: 0,
            11: 0,
            12: 0,
            13: 0,
            14: 0,
            15: 0,
            16: 0,
            17: 0,
            18: 0,
            19: 0,
            20: 0,
            21: 0,
            22: 0,
            23: 0,
        }
        countrys: Dict = {}
        for objs in data:
            device[objs["device_id"]] += 1
            if objs["country"] in countrys:
                countrys[objs["country"]] += 1
            else:
                countrys[objs["country"]] = 1
            objs["device"] = device
            tz_key = int(objs["date_check"].strftime("%H")) + int(user_tz)
            if tz_key in hour.keys():
                hour[tz_key] += 1
            else:
                if tz_key > 23:
                    new_key = (tz_key - 23)
                else:
                    new_key = (23 + tz_key)
                hour[new_key] += 1
        clicked = {
            "mobile": device[1] + device[3] + device[4],
            "pc": device[2] + device[5] + device[6],
            "other": device[7],
        }
        re_clicked_today = cache.get(
            f"statx_aclick_{obj.author_id}_{obj.id}"                   #  {obj_lnk[0].get("link_check_id", "unknown")}"
        )
        print(cache.get(f"statx_aclick_{obj.author_id}_{obj.id}"))
        clicked_today = cache.get(
            f"statx_click_{obj.author_id}_{obj.id}"                   #  {obj_lnk[0].get("link_check_id", "unknown")}"
        )
        if not isinstance(re_clicked_today, int):
            re_clicked_today = 0
        if not isinstance(clicked_today, int):
            clicked_today = 0
        hour.update({24: 0})
        #if self.context["action"] == "task_celery":
        #    cache.delete(f"statx_click_{obj.id}")
        #    cache.delete(f"statx_aclick_{obj.id}")
        return {
            "country": countrys,
            "device": device,
            "hours": hour,
            "clicks": clicked,
            "reClickedToday": int(re_clicked_today),
            "clickedToday": int(clicked_today)
        }
