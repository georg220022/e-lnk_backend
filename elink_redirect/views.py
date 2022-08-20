from elink_index.read_write_base import RedisLink, PostgresLink
from django.shortcuts import redirect
from elink.settings import SITE_NAME, TIME_SAVE_COOKIE
from elink_index.validators import CheckLink
#from django.http import HttpResponse
#from django.shortcuts import render
from django.template.response import TemplateResponse
from django.shortcuts import render


def open_link(request, short_code):
    if len(str(short_code)) == 11 or len(str(short_code)) == 66:
        object_redis = RedisLink.reader(short_code)
        if object_redis:
            return redirect(object_redis['long_link'])
        object_postgres = PostgresLink.reader(request, short_code)
        if object_postgres is not False:
            if not CheckLink.check_date_link(object_postgres):
                return render(request, '404.html')#redirect(SITE_NAME + '/badtime')
            if not CheckLink.check_pass(object_postgres):
                return redirect(SITE_NAME +
                                f'/password-check?short_code={short_code}')
            else:
                if not CheckLink.check_limited(object_postgres):
                    return redirect(SITE_NAME + '/end_limit')
                CheckLink.collect_stats(request, object_postgres)
                response = redirect(object_postgres.long_link)
                response.set_cookie(f"{object_postgres.short_code}",
                                    max_age=int(TIME_SAVE_COOKIE))
                return response
    return render(request, '404.html')
