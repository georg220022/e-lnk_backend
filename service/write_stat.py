from collections import OrderedDict

from django.core.cache import cache
from django.db.models import Count, F

from elink_index.models import InfoLink, LinkRegUser


class WriteStat:
    @staticmethod
    def one_week(day_week, usr) -> None:
        data_weeks = OrderedDict(
            InfoLink.objects.only("date_check", "link_check")
            .select_related("link_check")
            .only("author_id")
            .filter(link_check__author_id=int(usr[3]))
            .only("link_check")
            .values_list("link_check__author_id")
            .annotate(Count("link_check"))
        )
        if int(day_week) == 1:
            new_week_data = {
                1: 0,
                2: 0,
                3: 0,
                4: 0,
                5: 0,
                6: 0,
                7: 0,
            }
            cache.set(f"week_{int(usr[3])}", new_week_data, None)
        [
            cache.set(f"week_{int(usr[3])}", {day_week: value}, None)
            for _, value in data_weeks.items()
        ]

    @staticmethod
    def one_hour() -> dict:
        InfoLink.objects.bulk_create(
            [*OrderedDict(cache.get_many(cache.keys("statx_info_*"))).values()]
        )
        clicks = OrderedDict(cache.get_many(cache.keys("statx_click_*")))
        again_clicks = OrderedDict(cache.get_many(cache.keys("statx_aclick_*")))
        result = {
            key: (int(key[12:]), clicks[key], again_clicks[f"statx_aclick_{key[12:]}"])
            for key in clicks
        }
        data = [
            LinkRegUser(
                id=id,
                how_many_clicked=F("how_many_clicked") + click,
                again_how_many_clicked=F("again_how_many_clicked") + re_click,
            )
            for id, click, re_click in result.values()
        ]
        LinkRegUser.objects.bulk_update(
            data, ["how_many_clicked", "again_how_many_clicked"]
        )
        cache.delete_pattern(
            "statx_*"
        )  # Из за отправки статистики по повторным нажатиям, перенести эту хуету на 00-00 очистку
        cache.set("count_cache_infolink", 0, None)  # Эту строку в самый низ
        return result
