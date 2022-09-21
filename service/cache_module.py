from collections import OrderedDict
from elink_index.models import LinkRegUser

from django.core.cache import cache


class CacheModule:
    @staticmethod
    def writer(user_id: int, serializer_data: dict) -> None:
        """Модуль записи свежей информации в кеш для пользователя"""
        old_data = cache.get(user_id)
        if old_data:
            lnk_id = serializer_data.get("linkId")
            stop_date = serializer_data.get("linkEndDate")
            if isinstance(stop_date, type(None)):
                serializer_data["linkEndDate"] = "-1"
            re_clicked_today = cache.get(f"statx_aclick_{user_id}_{lnk_id}")
            clicked_today = cache.get(f"statx_click_{user_id}_{lnk_id}")
            if not isinstance(re_clicked_today, int):
                re_clicked_today = 0
            if not isinstance(clicked_today, int):
                clicked_today = 0
            fake_data = serializer_data
            start = fake_data.get("linkStartDate")
            create = fake_data.get("linkCreatedDate")
            formated_time = create.strftime("%Y-%m-%dT%H:%M")
            if isinstance(start, type(None)):
                fake_data["linkStartDate"] = formated_time
            fake_data["linkCreatedDate"] = formated_time
            if len(fake_data.get("linkPassword")) > 0:
                fake_data["lock"] = True
            else:
                fake_data["lock"] = False
            fake_data["statistics"] = {
                "country": {},
                "device": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                },
                "hours": {
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
                    24: 0,
                },
                "reClickedToday": re_clicked_today,
                "clickedToday": clicked_today,
            }
            old_data.append(OrderedDict(fake_data))
            timer = int(cache.ttl(user_id))
            cache.set(user_id, old_data, timer)

    @staticmethod
    def editor(
        user_id: int, link: OrderedDict, description: str, passwd: bool | str
    ) -> None:
        """Модуль редактирования информации в кеше (отображаемый пароль и имя ссылки в панели)"""
        old_data = cache.get(user_id)
        if old_data:
            for obj in old_data:
                short_code = obj["shortLink"][17:]
                if short_code == link.short_code:
                    obj["linkName"] = description
                    if passwd:
                        obj["lock"] = True
                        obj["linkPassword"] = passwd
                    else:
                        obj["lock"] = False
                        obj["linkPassword"] = ""
            timer = int(cache.ttl(user_id))
            cache.set(user_id, old_data, timer)

    @staticmethod
    def deleter(user_id: int, id_data: list) -> None:
        """Модуль удаления информации из кеша, для правильного отображения кешированной информации в панели"""
        old_data = cache.get(user_id)
        new_data = []
        if old_data and len(id_data) > 0:
            for data in old_data:
                short_link = data["shortLink"][17:]
                if short_link in id_data:
                    pass
                else:
                    new_data.append(data)
            if old_data:
                timer = int(cache.ttl(user_id))
                cache.set(user_id, new_data, timer)
            else:
                cache.delete(user_id)

    @staticmethod
    def count_lnk(user_id) -> bool:
        """Записываем количество ссылок пользователя в кеш"""
        if cache.has_key(f"link_limit_{user_id}"):
            return int(cache.get(f"link_limit_{user_id}"))
        count_lnk = LinkRegUser.objects.filter(author_id=user_id).count()
        cache.set(f"link_limit_{user_id}", count_lnk, 2700000)
        return int(cache.get(f"link_limit_{user_id}"))

    @staticmethod
    def get_days_click_link(day_week, obj):
        """Модуль получения статистики переходов за текущую неделю по ссылке"""
        if not cache.has_key(f"ready_week_{day_week}_{obj.author_id}_{obj.id}"):
            days = {}
            for number in range(1, 8):
                obj_day = cache.get(f"week_{number}_{obj.id}")
                if isinstance(obj_day, int):
                    days[number] = obj
                else:
                    days[number] = 0
            cache.set(f"ready_week_{day_week}_{obj.author_id}_{obj.id}", days, 60000)
        else:
            days = cache.get(f"ready_week_{day_week}_{obj.author_id}_{obj.id}")
        return days

    @staticmethod
    def get_today_click_link(obj):
        """Модуль получения статистики переходов за сегодняшний день в реальном времени"""
        re_clicked_today = cache.get(f"statx_aclick_{obj.author_id}_{obj.id}")
        clicked_today = cache.get(f"statx_click_{obj.author_id}_{obj.id}")
        if not isinstance(re_clicked_today, int):
            re_clicked_today = 0
        if not isinstance(clicked_today, int):
            clicked_today = 0
        return re_clicked_today, clicked_today
