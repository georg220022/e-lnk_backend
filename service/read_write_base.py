
from typing import Union
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache

from elink.settings import SITE_NAME, REDIS_BASE_FOR_LINK as REDIS_BASE
from elink_index.models import LinkRegUser

from .generator_code import GeneratorCode as GeneratorShortCode
from .qr_generator import QrGenerator
from .server_stat import ServerStat


class RedisLink:
    @staticmethod
    def writer(long_link: str) -> dict:
        short_code = (
            GeneratorShortCode.for_redis()
        )  # Генератор кода короткой ссылки для Redis.
        REDIS_BASE.set(
            short_code, long_link  # Запишем в Redis ключ это код_короткой ссылки,
        )  # редис удалит самые не используемые при нехватке памяти(настроено в redis.conf)
        short_link = (
            SITE_NAME + short_code
        )  # "https://site.tu/" + "P12cfQsasjB", как пример.
        qr_code_base64 = QrGenerator.qr_base64(
            short_link
        )  # Генератор QR кода, вернет картинку в base64
        data = {  # значение - это полная ссылка отправленная авторизованным юзером.
            "longLink": long_link,
            "shortLink": short_link,
            "qr": qr_code_base64,
        }
        return data

    @staticmethod
    def reader(short_code: str) -> Union[dict, bool]:
        if "r" not in short_code:
            return False
        try:
            long_link = REDIS_BASE.get(short_code)  # .decode("UTF-8")
            data = {"short_code": short_code, "long_link": long_link}
            return data
        except AttributeError:
            cache.incr("server_redis_atribute_error")
            ServerStat.reported(
                f"Redis_reader_38_short_code={short_code}",
                "текст ошибки AttributeError",
            )
            return False
        except IndexError:
            cache.incr("server_redis_index_error")
            ServerStat.reported(
                f"Redis_reader_41_short_code={short_code}", "текст ошибки IndexError"
            )
            return False


class PostgresLink:
    @staticmethod
    def reader(short_code=None) -> dict:
        if "p" in str(short_code):
            try:
                """obj = LinkRegUser.objects.defer(
                    "description",
                    "how_many_clicked",
                    "again_how_many_clicked",
                    "public_stat_small",
                    "public_stat_full",
                    "author_id",
                    "qr"
                ).get(short_code=short_code)"""
                obj = LinkRegUser.objects.only(
                    "short_code",
                    "long_link",
                    "secure_link",
                    "limited_link",
                    "start_link",
                    "date_stop"
                ).get(short_code=short_code)
            except ObjectDoesNotExist:
                cache.incr("server_pstgrs_obj_doesnt_exist")
                ServerStat.reported(
                    f"Postgres_reader_52_short_code={short_code}",
                    "Попытка взять из базы не существующий short_code",
                )
                return False
            return obj
        return False
