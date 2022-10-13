from collections import OrderedDict
from elink_index.models import LinkRegUser

from django.core.cache import cache


class CacheModule:
    @staticmethod
    def writer(user_id: int, serializer_data: dict) -> None:
        """Модуль записи свежей информации в кеш для пользователя"""
        old_data = cache.get(user_id)
        if old_data:
            name_lnk = serializer_data.get("linkName", False)
            if isinstance(name_lnk, str):
                if len(name_lnk) == 0:
                    bad_word = [
                        "https://www.",
                        "http://www.",
                        "https://",
                        "http://",
                        "wwww.",
                    ]
                    obj_long_lnk = serializer_data.get("longLink")
                    for objs in bad_word:
                        len_objs = len(objs)
                        if objs == obj_long_lnk[0:len_objs]:
                            name_lnk = obj_long_lnk[len(objs) :]
                            break
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
            if name_lnk:
                fake_data["linkName"] = name_lnk
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
            old_data.insert(0, OrderedDict(fake_data))
            # old_data.append(OrderedDict(fake_data))
            timer = int(cache.ttl(user_id))
            cache.set(user_id, old_data, timer)

    @staticmethod
    def editor(
        user_id: int, link: OrderedDict, description=False, passwd=False
    ) -> None:
        """Модуль редактирования информации в кеше (отображаемый пароль и имя ссылки в панели)"""
        old_data = cache.get(user_id)
        if old_data:
            for obj in old_data:
                short_code = obj["shortLink"][9:]
                if short_code == link.short_code:
                    if isinstance(description, str):
                        if description:
                            obj["linkName"] = description
                        else:
                            bad_word = [
                                "https://www.",
                                "http://www.",
                                "https://",
                                "http://",
                                "wwww.",
                            ]
                            obj_long_lnk = obj["longLink"]
                            for objs in bad_word:
                                len_objs = len(objs)
                                if objs == obj_long_lnk[0:len_objs]:
                                    obj["linkName"] = obj_long_lnk[len(objs) :]
                                    break
                    if isinstance(passwd, str):
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
        key_delete_data = []
        if old_data and len(id_data) > 0:
            for data in old_data:
                short_link = data["shortLink"][9:]
                if short_link in id_data:
                    ids = data["linkId"]
                    key_delete_data.append(f"statx_click_{user_id}_{ids}")
                    key_delete_data.append(f"statx_aclick_{user_id}_{ids}")
                    key_delete_data += cache.keys(f"statx_info_{ids}_*")
                else:
                    new_data.append(data)
            if old_data:
                timer = int(cache.ttl(user_id))
                cache.set(user_id, new_data, timer)
            else:
                cache.delete(user_id)
            if len(key_delete_data) > 0:
                cache.delete_many(key_delete_data)

    @staticmethod
    def count_lnk(user_id) -> bool:
        """Записываем количество ссылок пользователя в кеш"""
        if cache.has_key(f"link_limit_{user_id}"):
            return int(cache.get(f"link_limit_{user_id}"))
        count_lnk = LinkRegUser.objects.filter(author_id=user_id).count()
        cache.set(f"link_limit_{user_id}", count_lnk, 2700000)
        return int(cache.get(f"link_limit_{user_id}"))

    @staticmethod
    def get_days_click_link(day_week, obj_id, obj_author_id):
        """Модуль получения статистики переходов за текущую неделю по ссылке"""
        if not cache.has_key(f"ready_week_{day_week}_{obj_author_id}_{obj_id}"):
            days = {}
            for number in range(1, 8):
                obj_day = cache.get(
                    f"week_{number}_statx_click_{obj_author_id}_{obj_id}"
                )
                if isinstance(obj_day, int):
                    days[number] = obj_day
                else:
                    days[number] = 0
            cache.set(f"ready_week_{day_week}_{obj_author_id}_{obj_id}", days, 60000)
        else:
            days = cache.get(f"ready_week_{day_week}_{obj_author_id}_{obj_id}")
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

    @staticmethod
    def get_save_and_remove_infolink(obj, hour, device_id, countrys):
        data_calculated_info = cache.get(f"calculated_{obj.author_id}_{obj.id}")
        cache_hour = data_calculated_info[0]
        cache_device = data_calculated_info[1]
        cache_countrys = data_calculated_info[2]
        for nums in range(23):
            hour[nums] += int(cache_hour[nums])
        for nums in range(1, 8):
            device_id[nums] += cache_device[nums]
        for obj in cache_countrys:
            if obj in countrys:
                countrys[obj] += cache_countrys[obj]
            else:
                countrys[obj] = cache_countrys[obj]
        return hour, device_id, countrys

    @staticmethod
    def remove_stat_link(user_id):
        cache.delete_pattern(f"statx_aclick_{user_id}_*")
        cache.delete_pattern(f"statx_click_{user_id}_*")
        cache.delete_pattern(f"calculated_{user_id}_*")
