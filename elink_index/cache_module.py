from django.core.cache import cache
from collections import OrderedDict

class Cache_module:

    def writer(user_id, serializer_data):
        old_data = cache.get(user_id)
        if old_data:
            fake_data = serializer_data
            fake_data['date_check'] = {
                '0': 0, '1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0,
                '7': 0, '8': 0, '9': 0, '10': 0, '11': 0, '12': 0, '13': 0,
                '14': 0, '15': 0, '16': 0, '17': 0, '18': 0, '19': 0, '20': 0,
                '21': 0, '22': 0, '23': 0
            }
            fake_data['country_check_id'] = {
                'Russia': 0,
                'Ukraine': 0,
                'Belarus': 0
            }
            fake_data['device_id'] = {
                'PC': 0,
                'phone': 0,
                'other': 0
            }
            old_data.append(OrderedDict(fake_data))
            timer = int(cache.ttl(user_id))
            cache.set(user_id, old_data, timer)

    def editor(user_id, link_id, description):
        old_data = cache.get(user_id)
        if old_data:
            for obj in old_data:
                print(obj)
                print(link_id)
                if obj['id'] == link_id:
                    obj['description'] = description
                    #old_data.remove(obj)
                    #print(old_data)
                    #old_data.obj['linkDescription'] = description
                    print(old_data)
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
