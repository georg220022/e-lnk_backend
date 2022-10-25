import datetime
import psutil

from telegram import Bot
from django.db.models import Q
from django.core.cache import cache

from elink.celery import app
from service.user_time_now import UserTime
from elink_index.models import InfoLink, LinkRegUser
from elink.settings import TG_CHAT_DATA, TELEGRAM_TOKEN, stat_data
from users.models import User
from .tg_model_send import TelegramStat
from .send_mail import RegMail
from .creator_stat_pdf import StatCreate
from .write_stat import WriteStat


bot = Bot(token=TELEGRAM_TOKEN)


@app.task()
def saver_info() -> None:
    import time

    time.sleep(  # Вынужденная мера, что бы убрать рассинхрон по времени крона и питонячей либы datetime
        5
    )
    """Ежечасно собираем данные по кликам из кеша и записываем в базу,
    попутно удаляем из кеша обработанную информацию"""
    start = datetime.datetime.now()
    if int(cache.get("count_cache_infolink")) > 0:
        WriteStat.one_hour()
        [bot.send_message(key, f"Сохранено") for key in TG_CHAT_DATA]
    else:
        [bot.send_message(key, "Сохранять нечего") for key in TG_CHAT_DATA]
    # Берем список избранных юзеров для подсчета статистики
    user_list = list(
        User.objects.filter(
            Q(banned=False) & Q(trust_rating__gt=1) & Q(is_active=True)
        ).values_list("my_timezone", "send_stat_email", "email", "id", "subs_type")
    )
    for usr in user_list:
        user_hours = UserTime.day_week_now(int(usr[0]), need_day_week=False)
        if user_hours.strftime("%H") == "00":
            """Если у пользователя полночь (00:00) по его местному времени,
            высчитываем статистику за прошедший день для недельной статистики"""
            day_week = user_hours.isoweekday()
            # Если у пользователя статус не дефолтного пользователя - считаем ему статистику
            if usr[4] != "REG":
                WriteStat.one_week(day_week, usr)
                # Если не дефолтный юзер включил отправку статистики на емейл
                if usr[1] is True:
                    queryset = InfoLink.objects.select_related("link_check").filter(
                        Q(link_check__author_id=int(usr[3]))
                    )
                    # Часть кода в приватном репозитории
                    if cache.has_key("dt_now"):
                        cache.delete("dt_now")
                    cache.set("dt_now", user_hours, None)
                    """Если пользователь указал в своем профиле присылать ему статистику на почту"""
                    StatCreate.every_day_stat(usr, query_list)
            # Если пользователь стандартный - только прибавляем в БД количество переходов за день
            else:
                WriteStat.end_day(False, usr)
            # Очищаем счетчики переходов по ссылкам за сутки
            cache.set(f"count_infolink_{usr[3]}", 0, 200000)
            cache.delete_pattern(f"calculated_{usr[3]}_*")
            ####################################
            # Часть кода в приватном репозитории
            ####################################
    # Удаляем статистику переходов из базы, у пользователей для которых произвели рассчет
    time_service = datetime.datetime.now() - start
    data_service_time = cache.get("time_service")
    data_service_time[start] = time_service
    cache.set("time_service", data_service_time, None)
    cache.set("count_cache_infolink", 0, None)
    stop = datetime.datetime.now() - start
    time_generate = cache.get("server_time_generate_all_pdf")
    time_generate.append(f"{datetime.datetime.now()}: {stop}")
    cache.set("server_time_generate_all_pdf", time_generate, None)
    start_2 = datetime.datetime.now()
    yesterday = cache.get("dt_now") - datetime.timedelta(hours=1)
    RegMail.send_stat_pdf(yesterday)
            ####################################
            # Часть кода в приватном репозитории
            ####################################


@app.task
def send_admin_stat_tg() -> None:
    cache.set("send_critical_msg", "No", None)
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)
    # Начало бота
    data_string = TelegramStat.server_stat_day(yesterday)
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
        # если осталась малая часть большого отчета - доотправляем ее
        [bot.send_message(key, data_string[start_str:]) for key in TG_CHAT_DATA]
    else:
        [bot.send_message(key, data_string) for key in TG_CHAT_DATA]
    cache.incr("no_reload_day")  # Дни без перезагрузки сервиса
    cache.delete_pattern(
        "server_*"
    )  # Удаляем отчеты об ошибках/исключениях за прошедший день
    cache.set_many(stat_data, None)
    cache.set("send_critical_msg", "No", None)
    if cache.has_key("reporteds"):
        cache.set("reporteds", [], None)


@app.task
def cleaner_db() -> None:
    # Если каким-то образом в БД есть старые данные - удаляем
    today = datetime.date.today()
    day_ago_4 = today - datetime.timedelta(days=4)
    InfoLink.objects.filter(date_check__date__lt=day_ago_4).delete()


@app.task
def optimize_ttl_and_perfomance() -> None:
    # Автоопределение жизни кеша в зависимости от нагрузки на ядро процессора
    time_live = int(cache.get("live_cache"))
    if int(psutil.cpu_percent()) > 30:
        if time_live < 3600:
            time_live += 10
            cache.set("live_cache", time_live, None)
        else:
            ####################################
            # Часть кода в приватном репозитории
            ####################################
    else:
        if time_live != 10:
            time_live -= 10
            cache.set("live_cache", time_live, None)

    keys = cache.keys("count_infolink_*")
    data_info_link_users = cache.get_many(keys)
    user_list_id_over_infolink = [
        int(obj[15:]) for obj, values in data_info_link_users.items() if values >= 5000
    ]
    if len(user_list_id_over_infolink) > 0:
        for user_id in user_list_id_over_infolink:
            user = User.objects.get(id=user_id)
            user_tz = user.my_timezone
            ####################################
            # Часть кода в приватном репозитории
            ####################################
            for key, ids in obj_lnk_id[0].items():
                ids = int(ids)
                delete_id.append(ids)
                data = [
                    info_lnk for info_lnk in obj_lnk if info_lnk["link_check_id"] == ids
                ]
                device = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0}
                countrys = {}
                hour = {
                    0: 0,
                    1: 0,
                    2: 0,
                    3: 0,
                    4: 0,
                    5: 0,
                    6: 0,
                    7: 0,
                    8: 0,
                    9: 0,
                    10: 0,
                    11: 0,
                    12: 0,
                    13: 0,
                    14: 0,
                    15: 0,
                    16: 0,
                    17: 0,
                    18: 0,
                    19: 0,
                    20: 0,
                    21: 0,
                    22: 0,
                    23: 0,
                }
                for objs in data:
                    device[objs["device_id"]] += 1
                    if objs["country"] in countrys:
                        countrys[objs["country"]] += 1
                    else:
                        countrys[objs["country"]] = 1
                    tz_key = int(objs["date_check"].strftime("%H")) + int(user_tz)
                    if tz_key in hour.keys():
                        hour[tz_key] += 1
                    else:
                        if tz_key > 23:
                            new_key = tz_key - 24
                        else:
                            new_key = 23 + tz_key
                        hour[new_key] += 1
                if cache.has_key(f"calculated_{user_id}_{ids}"):
                    data_calculated_info = cache.get(f"calculated_{user_id}_{ids}")
                    cache_hour = data_calculated_info[0]
                    cache_device = data_calculated_info[1]
                    cache_countrys = data_calculated_info[2]
                    for nums in range(23):
                        hour[nums] += cache_hour[nums]
                    for nums in range(1, 8):
            ####################################
            # Часть кода в приватном репозитории
            ####################################
                        else:
                            countrys[obj] = cache_countrys[obj]
                data_calculated_info = [hour, device, countrys]
                cache.set(f"calculated_{user_id}_{ids}", data_calculated_info, 180000)
            cache.set(f"count_infolink_{user_id}", 0, 200000)
