from service.send_mail import RegMail
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

CHOICES_TIME_ZONE = (
        ("-12", "-12"),
        ("-11", "-11"),
        ("-10", "-10"),
        ("-9", "-9"),
        ("-8", "-8"),
        ("-7", "-7"),
        ("-6", "-6"),
        ("-5", "-5"),
        ("-4", "-4"),
        ("-3", "-3"),
        ("-2", "-2"),
        ("-1", "-1"),
        ("+0", "+0"),
        ("+1", "+1"),
        ("+2", "+2"),
        ("+3", "+3"),
        ("+4", "+4"),
        ("+5", "+5"),
        ("+6", "+6"),
        ("+7", "+7"),
        ("+8", "+8"),
        ("+9", "+9"),
        ("+10", "+10"),
        ("+11", "+11"),
        ("+12", "+12"),
    )

class ChangeSettingsSerializer(serializers.Serializer):
    utc = serializers.ChoiceField(choices=CHOICES_TIME_ZONE, required=False)
    sendStat = serializers.BooleanField(required=False)
    email = serializers.EmailField(required=False)
    password = serializers.CharField()
    new_password = serializers.CharField(required=False)
    
    class Meta:
        model = User
        read_only_fields = ["id"]
        fields = (
            "send_stat_email",
            "password",
            "new_password",
            "id",
            "my_timezone",
            "utc",
            "email",
            "sendStat",
        )

    def update(self, instance, validated_data):
        psswd = validated_data.pop("password", False)
        if psswd:
            if instance.check_password(psswd):
                timezone = validated_data.get("utc", False)
                if timezone:
                    instance.my_timezone = str(timezone)
                instance.send_stat_email = validated_data.get("sendStat", instance.send_stat_email)
                new_pass = validated_data.get("new_password", False)
                if new_pass:
                    instance.set_password(new_pass)
                    instance.public_key = str(instance.id) + str(GeneratorId.public_id())
                emails = validated_data.get("email", False)
                if emails:
                    if instance.email != emails:
                        if not User.objects.filter(email=emails).exists():
                            RegMail.change_mail.delay(instance.email, emails, None, True)
                            instance.email = emails
                            instance.is_active = False
                        else:
                            msg = "Данная почта уже зарегестрирована"
                            raise serializers.ValidationError(msg)
                    else:
                        msg = "Это и так ваша текущая почта"
                        raise serializers.ValidationError(msg)
                    instance.save()
                    return instance

                
        msg = "Пароль не верный! Настройки не были изменены."
        raise serializers.ValidationError(msg)
