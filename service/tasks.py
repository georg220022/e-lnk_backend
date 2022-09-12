import datetime
from telegram import Bot
from django.db.models import Q
from django.core.cache import cache
from elink.celery import app
from elink_index.models import InfoLink
from elink.settings import TG_CHAT_DATA, TELEGRAM_TOKEN, stat_data
from users.models import User
from .tg_model_send import TelegramStat
from .send_mail import RegMail
from .creator_stat_pdf import StatCreate
from .write_stat import WriteStat


bot = Bot(token=TELEGRAM_TOKEN)


@app.task
def saver_info() -> None:
    """Ежечасно собираем данные по кликам из кеша и записываем в базу,
    попутно удаляем из кеша обработанную информацию"""
    start = datetime.datetime.now()
    if int(cache.get("count_cache_infolink")) > 0:
        WriteStat.one_hour()
        [bot.send_message(key, f"Сохранено") for key in TG_CHAT_DATA]
    else:
        [bot.send_message(key, "Сохранять нечего") for key in TG_CHAT_DATA]
    utc_now = datetime.datetime.now(datetime.timezone.utc)
    yesterday = utc_now - datetime.timedelta(days=1)
    # Берем список избранных юзеров для подсчета статистики
    user_list = list(
        User.objects.filter(Q(banned=False) & Q(trust_rating__gt=1) #Q(subs_type__in=["MOD", "BTEST"]) & 
        ).values_list("my_timezone", "send_stat_email", "email", "id", "subs_type")
    )
    data_id = []
    for usr in user_list:
        # Если этот пользователь не менял свой часовой пояс в настройках (UTC)
        if not cache.get(
            f"edit_utc_{usr[3]}"
        ):
            user_hours = utc_now + datetime.timedelta(hours=int(usr[0]))
            if user_hours.strftime("%H") == "00":
                """Если у пользователя полночь (00:00) по его часовому поясу,
                высчитываем статистику за прошедший день для недельной статистики"""
                data_id.append(int(usr[3]))
                day_week = user_hours.isoweekday()
                # Если у пользователя статус не дефолтного пользователя - считаем ему статистику
                if usr[4] != "REG":
                    WriteStat.one_week(day_week, usr)
                    # Если не дефолтный юзер включил отправку статистики на емейл
                    if usr[1] is True:
                        """Если пользователь указал в своем профиле присылать ему статистику на почту"""
                        StatCreate.every_day_stat(usr)
                        RegMail.send_stat_pdf(yesterday)
                # Очищаем счетчики переходов по ссылкам за сутки
                cache.delete_pattern(f"statx_aclick_{usr[3]}_*")
                cache.delete_pattern(f"statx_click_{usr[3]}_*")
    # Удаляем статистику переходов из базы, у пользователей для которых произвели рассчет
    InfoLink.objects.filter(link_check__author_id__in=data_id).delete()
    time_service = datetime.datetime.now() - start
    data_service_time = cache.get("time_service")
    data_service_time[start] = time_service
    cache.set("time_service", data_service_time, None)
    cache.set("count_cache_infolink", 0, None)

@app.task
def send_admin_stat_tg() -> None:
    cache.set("send_critical_msg", "No", None)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    # Начало бота
    data_string = TelegramStat.server_stat_day(yesterday)
    """Максимальное количество символов в сообщении телеграм - 4000 символов,
    если отчет более 4000 символом - отправляем частями"""
    if len(data_string) > 4000:
        end_str = 4000
        start_str = 0
        while len(data_string[start_str:]) > 4000:
            [
                bot.send_message(key, data_string[start_str:end_str])
                for key in TG_CHAT_DATA
            ]
            start_str += 4000
            end_str += 4000
        [bot.send_message(key, data_string[start_str:]) for key in TG_CHAT_DATA]
    else:
        [bot.send_message(key, data_string) for key in TG_CHAT_DATA]
    cache.incr("no_reload_day")
    cache.delete_pattern('server_*')
    cache.set_many(stat_data)
    cache.set("send_critical_msg", "No", None)

@app.task
def cleaner_db() -> None:
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
    from rest_framework_simplejwt.utils import aware_utcnow

    """Очищаем устаревшие данные, удаляем протухшие токены из черного листа"""
    today = datetime.date.today()
    day_ago_4 = today - datetime.timedelta(days=4)
    OutstandingToken.objects.filter(expires_at__lte=aware_utcnow()).delete()
    InfoLink.objects.filter(date_check__date__lt=day_ago_4).delete()

@app.task
def optimize_live_time_cache() -> None:
    import psutil
    time_live = int(cache.get("live_cache"))
    """Если нагрузка на ядро более 50%, увеличиваем жизнь кеша на 10 сек
    иначе если время жизни кеша не 10 сек(это минимум) - уменьшаем на 10"""
    if int(psutil.cpu_percent()) > 50:
        if time_live < 3600:
            time_live += 10
            cache.set("live_cache", time_live, None)
        else:
            #Только 1 раз в день отправляем это сообщение
            sends = str(cache.get("send_critical_msg"))
            if sends == "No":
                [bot.send_message(key, "Ядро не справляется") for key in TG_CHAT_DATA]
                cache.set("send_critical_msg", "Yes", None)
    else:
        if time_live != 10:
            time_live -= 10
            cache.set("live_cache", time_live, None)
