from django.utils import timezone
from elink_index.models import LinkRegUser, InfoLink
from .country_get import DetectCountry
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from elink.server_stat import ServerStat
from datetime import datetime
import time


class CheckLink:

    @classmethod  # Класс метод под вопросом
    def get_long_url(cls, request_data) -> bool:
        long_link = request_data.data.get('longLink', False)
        if long_link and len(long_link) < 5001:
            if 'https://' == long_link[0:8] or 'http://' == long_link[0:7]:
                return long_link
            else:
                long_link = 'http://' + long_link
                return long_link
        return False

    def check_limited(obj) -> bool:
        if obj.limited_link <= -1:
            return True
        elif obj.limited_link >= 1:
            obj.limited_link = obj.limited_link - 1
            obj.save()
            return True
        else:
            return False

    def check_device(request_meta):
        device_name = request_meta['HTTP_USER_AGENT'].lower()
        if 'android' in device_name:
            return 1
        elif 'windows' in device_name:
            return 2
        elif 'iphone' in device_name:
            return 3
        elif ('mac' and 'pad') in device_name:
            return 4
        elif 'linux' in device_name:
            return 5
        elif 'mac' in device_name:
            return 6
        else:
            ServerStat.reported('CheckLink_50', f'Определение устройства не удалось obj={device_name}')
            return 7

    def check_date_link(obj):                                                 # Проверяем даты открытия-закрытия доступа к ссылке
        now = timezone.now()
        start = obj.start_link
        stop = obj.date_stop
        if ((isinstance(start, datetime) and start > now) or
           (isinstance(stop, datetime) and stop > now)):
            return False
        return True

    def check_pass(obj):
        if str(obj.secure_link) == '':
            return True
        return False

    def check_request(obj):
        try:
            len_code = len(str(obj['shortCode']))
            len_pass = len(str(obj['linkPassword']))
            if (len_code and len_pass) < 17 and (len_code and len_pass) > 0:
                data = {
                    "shortCode": str(obj['shortCode']),
                    "linkPassword": str(obj['linkPassword'])
                    }
                return data
            return False
        except KeyError as e:
            ServerStat.reported('CheckLink_79', f'Не получен один из требуемых объектов obj={obj}, текст ошибки: {e}')
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
                                country=country,
                                date_check=date_check,
                                device_id=device_id)
        obj.save()

    def description(request):
        obj_id = request.data.get('shortCodes', False)
        link_obj = get_object_or_404(LinkRegUser, short_code=obj_id)
        if request.user.id == link_obj.author.id:
            obj_descrip = request.data.get('linkDescription', False)
            if obj_descrip is not False:
                if len(obj_descrip) > 0 and len(obj_descrip) <= 1000:
                    return link_obj
        return False
