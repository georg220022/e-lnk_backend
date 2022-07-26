from django.utils import timezone
from elink_index.models import LinkRegUser, InfoLink
from .country_get import DetectCountry
import validators
import time

NoneType = type(None)

class CheckLink:

    @classmethod #Класс метод под вопросом
    def get_long_url(cls, request_data) -> bool:
        long_link = request_data.data.get('longLink', False)
        if long_link and len(long_link) < 5001:
            if '://' in long_link:
                #print('da')
                return long_link
            else:
                #print('net')
                long_link = 'http://' + long_link
                return long_link
            #if validators.url(long_link, public=False):
            #    print('CERF')
                                              # Если ссылка отправленная пользователем прошла проверку - вернем ее.
        return False                                                          # Иначе вернем False.


    def check_limited(obj) -> bool:                                                   # Проверка лимитов по ссылке
        if obj.limited_link <= -1:
            return True
        elif obj.limited_link >= 1:
            obj.limited_link = obj.limited_link - 1
            obj.save()
            return True
        else:
            return False


    def check_device(request_meta):                                           # Определяем девайс открывшего ссылку
        device_name = request_meta['HTTP_USER_AGENT']
        if ('Windows' or 'Linux' or 'Macintosh' or 'Dos') in device_name:
            return 'COMPUTER'
        elif ('Android' or 'ios') in device_name:
            return 'PHONE'
        else:
            return 'UNKNOWN'
    
    def check_date_link(obj):                                                 # Проверяем даты открытия-закрытия доступа к ссылке
        now = timezone.now()
        start = obj.start_link
        stop = obj.date_stop
        if ((type(start) == type(now) and start > now) or
            (type(stop) == type(now) and stop < now)):
            return False
        return True

    def check_pass(obj):                                                       # Стоит ли пароль на ссылке
        if str(obj.secure_link) == '':# or (str(obj.secure_link) == str(data['linkPassword'])):
            return True
        return False
    
    def check_request(obj):
        try:
            len_code = len(str(obj['shortCode']))
            len_pass = len(str(obj['linkPassword']))
            if (len_code and len_pass) < 15 and (len_code and len_pass) > 0:
                data = {
                    "shortCode": str(obj['shortCode']),
                    "linkPassword": str(obj['linkPassword'])
                    }
                return data
            return False
        except KeyError:
            return False
    
    def collect_stats(request_obj, obj):
        date_check = time.strftime("%Y-%m-%d %H:%M")
        device_id = CheckLink.check_device(request_obj.META)
        country = DetectCountry.get_client_ip(request_obj)
        if f'{obj.short_code}' in request_obj.COOKIES:
            obj.how_many_clicked += 1
            obj.again_how_many_clicked += 1
        else:
            obj.how_many_clicked += 1
        InfoLink.objects.create(link_check=obj,
                                country_check_id=country,
                                date_check=date_check,
                                device_id=device_id)
        obj.save()

