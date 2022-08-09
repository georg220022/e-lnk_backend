import geoip2.database
from elink.settings import BASE_DIR

reader = geoip2.database.Reader(f'{BASE_DIR}/data.mmdb')

class DetectCountry():

    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        try:
            obj = reader.country(ip)
        except:
            obj = 'UNKNOWN'
        return obj
