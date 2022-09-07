from datetime import datetime

from django.core.cache import cache


class ServerStat:
    @staticmethod
    def reported(key=None, value=None) -> None:
        now_moment = datetime.now().strftime("%b %d %Y %H:%M:%S")
        data = cache.get_or_set("reporteds", [], None)
        if key not in data:
            data[key] = [value, 0, now_moment]
        else:
            data[key][1] += 1
            data[key][2] = now_moment
        cache.set("reporteds", data, None)
