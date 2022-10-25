from collections import OrderedDict

from django.core.cache import cache
from django.db.models import F

from elink_index.models import InfoLink, LinkRegUser


class WriteStat:
    @staticmethod
    def one_week(day_week: int, usr: list) -> None:
        """Получение количества кликов по всем ссылкам пользователя"""
        if day_week != 1:
            day_week -= 1
            obj_stat_today = cache.get_many(cache.keys(f"statx_click_{usr[3]}_*"))
            week_stat = {
                f"week_{day_week}_{key}": values
                for (key, values) in obj_stat_today.items()
            }
            cache.set_many(week_stat, 1500000)
            WriteStat.end_day(obj_stat_today, usr)
        else:
            for nums in range(1, 8):
                # Часть кода в приватном репозитории
            WriteStat.end_day(False, usr)

    @staticmethod
    def one_hour() -> None:
        """Записываем информацию по кликам пользователей по ссылкам 1-м большим запросом
        за 1 час либо по достижению 1000 запмсей в кеше"""
        keys_cache_info_link = cache.keys("statx_info_*")
        InfoLink.objects.bulk_create(
            # Часть кода в приватном репозитории
        )
        cache.delete_many(
            keys_cache_info_link
        )  # Из за отправки статистики по повторным нажатиям, перенести эту хуету на 00-00 очистку
        cache.set("count_cache_infolink", 0, None)  # Эту строку в самый низ

    @staticmethod
    def end_day(obj_stat_today=False, usr=False) -> None:
        """Функция вызывается в фоновом процессе Celery если у пользователя его
        местное время 00-00 и очищает кешированную информацию за уже прошедший день.
        В новый день со свежей инфой! :)"""
        if obj_stat_today and usr:
            # Часть кода в приватном репозитории
            again_clicks = OrderedDict(
                cache.get_many(cache.keys(f"statx_aclick_{usr[3]}_*"))
            )
        else:
            clicks = OrderedDict(cache.get_many(cache.keys(f"statx_click_{usr[3]}*")))
            again_clicks = OrderedDict(
                cache.get_many(cache.keys(f"statx_aclick_{usr[3]}_*"))
            )
        result = {
            key: (
                int(key[int(key.rfind("_") + 1) :]),
                clicks[key],
                again_clicks[
                    f"statx_aclick_{usr[3]}_{int(key[int(key.rfind('_') + 1):])}"
                ],
            )
            for key in clicks
        }
        data = [
            LinkRegUser(
                id=id,
                # Часть кода в приватном репозитории
                again_how_many_clicked=F("again_how_many_clicked") + re_click,
            )
            for id, click, re_click in result.values()
        ]
        LinkRegUser.objects.bulk_update(
            data, ["how_many_clicked", "again_how_many_clicked"]
        )
