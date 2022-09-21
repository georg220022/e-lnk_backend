import os
from datetime import datetime
from elink.settings import REDIS_FOR_ACTIVATE
from django.core.cache import cache
from django.template.loader import get_template
from django.core.mail import EmailMessage
from users.models import User
from .generator_code import GeneratorCode as Generator_activation_code
from .server_stat import ServerStat


class RegMail:
    @staticmethod
    def send_code(user_instance: User) -> None:
        """Отправка кода регистрации"""
        activation_code = Generator_activation_code.public_id()
        activate_link = (
            "https://e-lnk.ru/api/v1/activate"
            + f"/{user_instance.id}/{activation_code}"
        )
        message = get_template("reg-confirm-email.html").render({"activate_link": activate_link})
        msg = EmailMessage(
            "Регистрация E-LNK.RU",
            message,
            "info@e-lnk.ru",
            [str(user_instance)],
        )
        msg.content_subtype = "html"
        msg.send()
        REDIS_FOR_ACTIVATE.set(user_instance.id, activation_code, 2600000)
        cache.incr("server_send_msg_email")

    @staticmethod
    def send_stat_pdf(yesterday: datetime) -> None:
        """Отправка статистики пользователям"""
        list_mail = os.listdir("pdf_storage")
        for email_user in list_mail:
            try:
                message = get_template("links-info-email.html").render({"date_stat": yesterday})
                msg = EmailMessage(
                    f"Отчет за прошедший день - {yesterday}",
                    message,
                    "info@e-lnk.ru",
                    [str(email_user[:-4])],
                )
                msg.attach_file(f"pdf_storage/{email_user}")
                msg.send()
            except:
                cache.incr("server_bad_send_pdf_day_stat")
                ServerStat.reported(
                    f"send_stat_{email_user}",
                    f"Не удалось отправить статистику {email_user}",
                )
        """Безопасно удаляем все файлы с расширением .pdf"""
        filelist = [files for files in list_mail if files.endswith(".pdf")]
        [
            os.remove(os.path.join("pdf_storage", files))
            for files in filelist
            if os.path.isfile(os.path.join("pdf_storage", files))
        ]
