from django.core.mail import send_mail
from .public_id_generator import GeneratorId as Generator_activation_code
from elink.settings import REDIS_FOR_ACTIVATE


class RegMail:
    def send_code(user_instance):
        activation_code = Generator_activation_code.public_id()
        activate_link = f'https://e-lnk.ru/api/v1/activate/{user_instance.id}/{activation_code}'
        subject = 'Подтверждение регистрации'
        message = ('Остался один шаг! Завершите регистрацию на сайте, пройдя по данной ссылке: \n' + f'{activate_link}' + '\n' + 
                    'Обращаем Ваше внимание, что активировать учетную запись можно только с того устройства и браузера, на которых происходила регистрация. '+ '\n\n' +
                    'В случае возникновения вопросов обращайтесь на адрес help@e-lnk.ru. '+ '\n\n' +
                    'С уважением, команда e-lnk. '+ '\n\n\n\n' +
                    'Данное письмо сгенерировано автоматически и на него не нужно отвечать. '+ 
                    'Если Вы не регистрировались на сервисе e-lnk.ru, просто проигнорируйте это сообщение.')
        from_email = 'registration@e-lnk.ru'
        recipient_list = [str(user_instance)]
        REDIS_FOR_ACTIVATE.set(user_instance.id, activation_code, 2600000)
        send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
