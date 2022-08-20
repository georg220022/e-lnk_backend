from elink.celery import app
from elink_index.serializer import NoneType
from users.models import User
from elink_index.models import InfoLink
from django.db.models import Q
from django.core.cache import cache
from elink.settings import TG_CHAT_DATA, TELEGRAM_TOKEN
from telegram import Bot
import datetime
from datetime import date
from elink.server_stat import ServerStat

bot = Bot(token=TELEGRAM_TOKEN)

@app.task
def updater_week_stat():
    today = date.today()
    yesterday = today - datetime.timedelta(days=1)
    day_week = yesterday.isoweekday()
    start = datetime.datetime.now()
    prem_user = User.objects.exclude(subs_type__contains="REG").values('id')
    data_info = InfoLink.objects.filter(
        Q(link_check_id__author_id__in=prem_user) &
        Q(date_check__date=yesterday))
    for usr in prem_user:
        sum_click_day = data_info.filter(
            link_check_id__author_id=usr['id']).count()
        data_week = cache.get(f'week_{usr["id"]}')
        if isinstance(data_week, NoneType):
            data_week = {
                1: 0, 2: 0, 3: 0, 4: 0,
                5: 0, 6: 0, 7: 0
            }
        data_week[day_week] = sum_click_day
        cache.set(f'week_{usr["id"]}', data_week, 700000)
    stop = datetime.datetime.now()
    time_cache = stop - start
    ru_lang = ['Новых пользователей',
               'Отправлено кодов активации',
               'Активированно аккаунтов',
               'Создано ссылок гостями',
               'Созданно ссылок пользователями',
               'Перенаправлений',
               'Обновлено токенов',
               'Удачных входов в аккаунт',
               'Неудачных входов',
               'Неудачных активаций аккаунта']
    data_stat = cache.get_many([
        'new_users',
        'send_msg_email',
        'activated',
        'guest_link',
        'reg_link',
        'redirect',
        'refresh_tokens',
        'good_enter',
        'bad_enter',
        'bad_try_activated'
    ])
    data_reports = cache.get('reporteds')
    if isinstance(data_reports, type(None)):
        data_reports = ''
    data_string = (f'______________________E-LNK.RU___________|отчет за {yesterday}|\n\n' +
                    f'Непредвиденных ситуаций -> {len(data_reports)} \n\n' +
                    f'Статистика за день:\n')
    counts = 0
    for key, value in data_stat.items():
        data_string += f'| {ru_lang[counts]} -> {value}\n'
        counts += 1
    data_string += '\n\n Сообщения сервера за день:\n'
    if len(data_reports) > 0:
        for key, value in data_reports.items():
            data_string += (' _______________________________________' +
                            f'__________________\n| Где и кто -> {key}\n| Опи' +
                            f'сание ситуации -> {value[0]}\n| Количество повторов о' +
                            f'шибки -> {value[1]}\n| Время последней ошибки -> ' +
                            f'{value[2]}\n|____' +
                            '_____________________________________________________\n')
    else:
        data_string += '| Замечаний нет.\n'
    data_string += f'\n Кеширование данных заняло -> {time_cache}'
    if len(data_string) > 4000:
        end_str = 4000
        start_str = 0
        while len(data_string[start_str:]) > 4000:
            [bot.send_message(key, data_string[start_str:end_str]) for key in TG_CHAT_DATA]
            start_str += 4000
            end_str += 4000
        [bot.send_message(key, data_string[start_str:]) for key in TG_CHAT_DATA]
    else:
        [bot.send_message(key, data_string) for key in TG_CHAT_DATA]
    cache.incr('no_reload_day')
