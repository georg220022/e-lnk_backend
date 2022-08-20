from datetime import datetime, timedelta
from django.core.cache import cache


class ServerStat:

    def reported(key=None, value=None):
        now_moment = datetime.now().strftime("%b %d %Y %H:%M:%S")
        data = cache.get('reporteds')
        if key not in data:
            data[key] = [value, 0, now_moment]
        else:
            data[key][1] += 1
            data[key][2] = now_moment
        data
        cache.set('reporteds', data)
        print(cache.get('reporteds'))


"""    danger_data = {}

    data = {
        'New_users': 0,
        'Guest_link': 0,
        'Reg_link': 0,
        'Redirect': 0,
        }

    time_cache = ''

    @classmethod
    def today(cls, key=None, second_cache=None):
        if second_cache is not None:
            cls.time_cache = second_cache
        if key is not None:
            cls.data[key] += 1
        else:
            yesterday = datetime.now() - timedelta(hours=24)
            
            cache.set('data_string', data_string)

    @classmethod
    def reported(cls, key=None, value=None):
        if (key and value) is not None:
            obj = cls.danger_data.get(key, False)
            if obj is False:
                now_moment = datetime.now().strftime("%b %d %Y %H:%M:%S")
                cls.danger_data[key] = [value, 0, now_moment]
            else:
                cls.danger_data[key][1] += 1
    
    def saver(self):
        pass"""
