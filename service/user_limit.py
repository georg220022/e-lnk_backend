from django.core.cache import cache

from users.models import User
from .cache_module import CacheModule


class UserLimit:
    @staticmethod
    def create_link(request_user: User) -> bool | dict:
        if request_user.banned is False:
            cnt_lnk = CacheModule.count_lnk(request_user.id)
            if request_user.subs_type == "REG":
                if int(cnt_lnk) < 75:
                    return True
                cache.incr("server_user_reg_limit_lnk")
                return {"error": "Лимит 75 ссылок, удалите не нужные"}
            elif request_user.subs_type == "BTEST":
                if cnt_lnk < 150:
                    return True
                cache.incr("server_user_btest_limit_lnk")
                return {
                    "error": "Для участников бета-тестирования" + "лимит 150 ссылок"
                }
            elif request_user.subs_type == "MOD":
                return True
            cache.incr("server_try_create_lnk_ban_usr")
        else:
            return {"error": "Учетная запись заблокирована"}
