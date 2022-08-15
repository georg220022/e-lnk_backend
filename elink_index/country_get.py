import geoip2.database
from elink.settings import BASE_DIR

reader = geoip2.database.Reader(f'{BASE_DIR}/data.mmdb')


class DetectCountry():

    def get_client_ip(request):
        ip = request.META.get('HTTP_REAL_IP')
        try:
            response = reader.country(ip)
            obj = response.country.name
        except:
            obj = 'Unknown'
        return obj
