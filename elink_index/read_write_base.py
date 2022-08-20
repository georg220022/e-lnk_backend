from elink.settings import SITE_NAME, REDIS_BASE_FOR_LINK as REDIS_BASE
from django.core.cache import cache
from elink.server_stat import ServerStat
from django.core.exceptions import ObjectDoesNotExist
from .generator_code import GeneratorShortCode
from .qr_generator import QrGenerator
from .models import LinkRegUser


class RedisLink:

    @classmethod
    def writer(cls, long_link: str) -> dict:
        short_code = GeneratorShortCode.for_redis()           # Генератор кода короткой ссылки для Redis.
        REDIS_BASE.set(short_code,                            # Запишем в Redis ключ это код_короткой ссылки,
                       long_link)                             # редис удалит самые не используемые при нехватке памяти(настроено в redis.conf)
        short_link = SITE_NAME + short_code                   # 'https://site.tu/' + 'P12cfQsasjB', как пример.
        qr_code_base64 = QrGenerator.qr_base64(short_link)    # Генератор QR кода, вернет картинку в base64
        data = {                                              # значение - это полная ссылка отправленная авторизованным юзером.
            'longLink':  long_link,
            'shortLink': short_link,
            'qr': qr_code_base64,
            }
        return data

    @classmethod
    def reader(cls, short_code: str):
        if 'r' not in short_code:
            return False
        try:
            long_link = REDIS_BASE.get(short_code).decode('UTF-8')
            data = {
                'short_code': short_code,
                'long_link': long_link
            }
            return data
        except AttributeError as e:
            ServerStat.reported(f'Redis_reader_38_short_code={short_code}', f'текст ошибки AttributeError: {e}')
            return False
        except IndexError as e:
            ServerStat.reported(f'Redis_reader_41_short_code={short_code}', f'текст ошибки IndexError: {e}')
            return False


class PostgresLink:

    def reader(request, short_code=None):
        if 'p' in str(short_code):
            try:
                obj = LinkRegUser.objects.get(short_code=short_code)
            except ObjectDoesNotExist as e:
                ServerStat.reported(f'Postgres_reader_52_short_code={short_code}', f'Попытка взять из базы не существующий short_code {e}')
                return False
            return obj
        return False
