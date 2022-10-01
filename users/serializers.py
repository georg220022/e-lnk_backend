from xml.dom import ValidationErr
from rest_framework import serializers
from .models import User
from service.generator_code import GeneratorCode as GeneratorId


class ChangePasswordSerializer(serializers.Serializer):
    model = User
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.public_key = str(user.id) + str(GeneratorId.public_id())
        user.save()
        return user


class ChangeSettingsSerializer(serializers.Serializer):
    model = User
    fields = (
        "utc",
        "email",
        "send_stat",
    )

    def validate(self, obj):

        user_id = self.context["user_id"]
        user = User.objects.get(id=user_id)
        data = {
            "id": user_id,
            "usr_obj": user,
        }
        old_pass = obj.pop("password", False)
        if old_pass:
            if not user.check_password(str(old_pass)):
                msg = "Пароль не верный! Настройки не были изменены."
                raise ValidationErr(msg)
        else:
            msg = "Введите ваш текущий пароль что бы внести изменения"
            raise ValidationErr(msg)
        utc = obj.pop("utc", False)
        if utc:
            if isinstance(utc, int):
                if utc != user.my_timezone:
                    if utc < 12 and utc > -12:
                        data["my_timezone"] = utc
                    else:
                        msg = "масильное смещение по UTC от -12 до +12"
                        raise ValidationErr(msg)
                else:
                    msg = "Это ваше текущее время UTC, введите другое смещение либо оставьте поле пустым. Настройки не изменились"
                    raise ValidationErr(msg)
            else:
                msg = "UTC должно быть числом"
                raise ValidationErr(msg)
        send_stat = obj.pop("sendStat", "None")
        if isinstance(send_stat, bool):
            if user.subs_type != "REG":
                data["send_stat_email"] = send_stat
            else:
                msg = "Ваш тип подписки не позволяет получать PDF файл статистики на почту"
                raise ValidationErr(msg)
        new_pass = obj.pop("newPass", False)
        if new_pass:
            if len(new_pass) > 7 and len(new_pass) < 17:
                if isinstance(utc, str):
                    user.set_password(new_pass)
                else:
                    msg = "Пароль должен быть строкой"
                    raise ValidationErr(msg)
            else:
                msg = "Минимальная длинна пароля 8, максимальная 16 симолов"
                raise ValidationErr(msg)
        return data

    def update(self, data):
        usr_obj = data["usr_obj"]
        data["public_key"] = str(usr_obj.id) + str(GeneratorId.public_id())
        usr_obj.update(**data)
        return usr_obj.save()
