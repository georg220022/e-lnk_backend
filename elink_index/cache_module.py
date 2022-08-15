from django.core.cache import cache
from collections import OrderedDict


class Cache_module:

    def writer(user_id, serializer_data):
        old_data = cache.get(user_id)
        if old_data:
            fake_data = serializer_data
            fake_data['statistic'] = {
                "country": None,
                "device": {
                        "0": 0, "1": 0, "2": 0, "3": 0,
                        "4": 0, "5": 0, "6": 0, "7": 0,
                        },
                "hours": {
                        "00": 0, "01": 0, "02": 0, "03": 0, "04": 0,
                        "05": 0, "06": 0, "07": 0, "08": 0, "09": 0,
                        "10": 0, "11": 0, "12": 0, "13": 0, "14": 0,
                        "15": 0, "16": 0, "17": 0, "18": 0, "19": 0,
                        "20": 0, "21": 0, "22": 0, "23": 0,
                        },
                }
            old_data.append(OrderedDict(fake_data))
            timer = int(cache.ttl(user_id))
            cache.set(user_id, old_data, timer)

    def editor(user_id, link_id, description):
        old_data = cache.get(user_id)
        if old_data:
            for obj in old_data:
                if obj['id'] == link_id:
                    obj['description'] = description
            timer = int(cache.ttl(user_id))
            cache.set(user_id, old_data, timer)

    def deleter(user_id, id_data):
        old_data = cache.get(user_id)
        if old_data and len(id_data) > 0:
            for data in old_data:
                if data['id'] in id_data[0].values():
                    old_data.remove(data)
            timer = int(cache.ttl(user_id))
            cache.set(user_id, old_data, timer)
