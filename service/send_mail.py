import os

from datetime import datetime
from celery import shared_task
from django.core.cache import cache
from django.template.loader import get_template
from django.core.mail import EmailMessage

from elink.settings import REDIS_FOR_ACTIVATE
from .generator_code import GeneratorCode as Generator_activation_code


class RegMail:
    @shared_task
    def change_pass(email, reset_key=False, passwd=False) -> None:
        if reset_key:
            reset_link = f"https://e-lnk.ru/change/{email}/{reset_key}"
            message = get_template("reset_pass.html").render({"reset_link": reset_link})
        else:
            message = get_template("reset_pass.html").render({"passwd": passwd})
        msg = EmailMessage(
            "Информирование E-LNK.RU",
            message,
            "info@e-lnk.ru",
            [str(email)],
        )
        msg.content_subtype = "html"
        msg.send()

    @shared_task
    def change_mail(
        old_email: str, new_email: str, user_id=None, old_msg=False
    ) -> None:
        if old_msg:
            context = {"old_email": old_email, "new_email": new_email}
            message = get_template("change_email.html").render(context=context)
            msg = EmailMessage(
                "Информирование E-LNK.RU",
                message,
                "info@e-lnk.ru",
                [str(old_email)],
            )
        else:
            activation_code = Generator_activation_code.public_id()
            activate_link = (
                "https://e-lnk.ru/activate" + f"/{user_id}/{activation_code}"
            )
            context = {"activate_link": activate_link}
            message = get_template("change_email.html").render(context=context)
            msg = EmailMessage(
                "Информирование E-LNK.RU",
                message,
                "info@e-lnk.ru",
                [str(new_email)],
            )
            REDIS_FOR_ACTIVATE.set(user_id, activation_code, 2600000)
        msg.content_subtype = "html"
        msg.send()
        cache.incr("server_send_msg_email")

    @shared_task
    def send_code(data_user: dict) -> None:
        """Отправка кода регистрации"""
        activation_code = Generator_activation_code.public_id()
        activate_link = (
            "https://e-lnk.ru/activate" + f"/{data_user['id']}/{activation_code}"
        )
        message = get_template("reg-confirm-email.html").render(
            {"activate_link": activate_link}
        )
        msg = EmailMessage(
            "Регистрация E-LNK.RU",
            message,
            "info@e-lnk.ru",
            [str(data_user["email"])],
        )
        msg.content_subtype = "html"
        msg.send()
        REDIS_FOR_ACTIVATE.set(data_user["id"], activation_code, 2600000)
        cache.incr("server_send_msg_email")

    @staticmethod
    def send_stat_pdf(yesterday: datetime) -> None:
        """Отправка статистики пользователям"""
        list_mail = os.listdir("pdf_storage")
        for email_user in list_mail:
            message = get_template("links-info-email.html").render(
                {"date_stat": yesterday.strftime("%Y-%m-%d")}
            )
            msg = EmailMessage(
                f"Отчет за прошедший день - {yesterday.strftime('%Y-%m-%d')}",
                message,
                "info@e-lnk.ru",
                [str(email_user[:-4])],
            )
            msg.content_subtype = "html"
            msg.attach_file(f"pdf_storage/{email_user}")
            msg.send()
        """Безопасно удаляем все файлы с расширением .pdf"""
        filelist = [files for files in list_mail if files.endswith(".pdf")]
        [
            os.remove(os.path.join("pdf_storage", files))
            for files in filelist
            if os.path.isfile(os.path.join("pdf_storage", files))
        ]
