import email
import os
from datetime import datetime
from elink.settings import REDIS_FOR_ACTIVATE
from django.core.cache import cache
from django.template.loader import get_template
from django.core.mail import EmailMessage
from users.models import User
from .generator_code import GeneratorCode as Generator_activation_code
from .server_stat import ServerStat
from celery import shared_task


class RegMail:
    @shared_task
    def change_pass(email, reset_key=False, passwd=False):
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
    def change_mail(old_email, new_email, user_id=None, old_msg=False):
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
        list_bad_mail = []
        list_mail = os.listdir("pdf_storage")
        for email_user in list_mail:
            try:
                message = get_template("links-info-email.html").render(
                    {"date_stat": yesterday}
                )
                msg = EmailMessage(
                    f"Отчет за прошедший день - {yesterday}",
                    message,
                    "info@e-lnk.ru",
                    [str(email_user[:-4])],
                )
                msg.content_subtype = "html"
                msg.attach_file(f"pdf_storage/{email_user}")
                msg.send()
            except:
                cache.incr("server_bad_send_pdf_day_stat")
                ServerStat.reported(
                    f"send_stat_{email_user}",
                    f"Не удалось отправить статистику {email_user}",
                )
                list_bad_mail.append(email_user)
                #data = cache.get("bad_try_send_mail")
                #data.append(email_user)
                #cache.set("bad_try_send_mail", data, None)
        """Безопасно удаляем все файлы с расширением .pdf"""
        filelist = [files for files in list_mail if files.endswith(".pdf")]
        [
            os.remove(os.path.join("pdf_storage", files))
            for files in filelist
            if os.path.isfile(os.path.join("pdf_storage", files))
        ]
        if len(list_bad_mail) > 0:
            User.objects.filter(email__in=list_bad_mail).update(send_stat_email=False)
