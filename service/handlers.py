import logging
from telegram import Bot
from django.shortcuts import redirect
from elink.settings import TG_CHAT_DATA, TELEGRAM_TOKEN

bot = Bot(token=TELEGRAM_TOKEN)
logger = logging.getLogger(__name__)


def handler404(request, exception):
    logger.info(f"Request: {request}, Except: {exception}")
    return redirect("https://e-lnk.ru/404")


def handler403(request, exception):
    logger.info(f"Request: {request}, Except: {exception}")
    return redirect("https://e-lnk.ru/404")


def handler400(request, exception):
    logger.info(f"Request: {request}, Except: {exception}")
    return redirect("https://e-lnk.ru/404")


def handler500(request, exception):
    [bot.send_message(key, f"Сервер ошибка 500 - {exception}") for key in TG_CHAT_DATA]
    logger.warning(f"Request: {request}, Except: {exception}")
    return redirect("https://e-lnk.ru/404")
