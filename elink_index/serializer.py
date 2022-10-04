from django.db import IntegrityError
from rest_framework import serializers
from datetime import datetime

from service.generator_code import GeneratorCode as GeneratorShortCode
from service.qr_generator import QrGenerator
from service.server_stat import ServerStat

from .models import LinkRegUser

SITE_NAME = "e-lnk.ru/"


class LinkAuthSerializer(serializers.ModelSerializer):
    qr = serializers.CharField(read_only=True)
    shortLink = serializers.SerializerMethodField("get_short_link")
    linkId = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("id")
    )
    longLink = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("long_link")
    )
    linkName = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("description")
    )
    linkLimit = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("limited_link")
    )
    linkPassword = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("secure_link")
    )
    linkStartDate = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("start_link")
    )
    linkEndDate = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("date_stop")
    )
    linkCreatedDate = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("date_add")
    )
    clicked = serializers.ModelField(
        required=False, model_field=LinkRegUser()._meta.get_field("how_many_clicked")
    )
    repeatedClicked = serializers.ModelField(
        required=False,
        model_field=LinkRegUser()._meta.get_field("again_how_many_clicked"),
    )

    class Meta:
        model = LinkRegUser
        read_only_fields = (
            "shortLink",
            "short_code",
            "date_add",
        )
        exclude = (
            "short_code",
            "long_link",
            "start_link",
            "secure_link",
            "date_stop",
            "author",
            "date_add",
            "public_stat_full",
            "public_stat_small",
            "again_how_many_clicked",
            "how_many_clicked",
            "limited_link",
            "description",
            "id",
        )

    def validate(self, data):
        """Делаем из CamelCase питонячий snake_case + валидируем данные"""
        data.pop("longLink", False)
        data["short_code"] = GeneratorShortCode.for_postgresql()
        data["date_add"] = datetime.utcnow()
        data["description"] = data.pop("linkName", "")
        if len(data["description"]) > 30:
            data = {"error": "Максимальная длинна имени ссылки - 30 символов"}
            raise serializers.ValidationError(data)
        data["limited_link"] = data.pop("linkLimit", -1)
        if data["limited_link"] > 999999:
            data = {"error": "Максимальное значение лимита переходов 999999"}
            raise serializers.ValidationError(data)
        data["secure_link"] = data.pop("linkPassword", "")
        if data["secure_link"] != "":
            if len(data["secure_link"]) > 16:
                data = {"error": "Максимальная длинна пароля - 16 символов"}
                raise serializers.ValidationError(data)
        data["start_link"] = data.pop("linkStartDate", None)
        data["date_stop"] = data.pop("linkEndDate", None)
        data["author_id"] = self.context["user_id"]
        data["long_link"] = self.context["long_link"]
        return data

    def create(self, validated_data: dict) -> dict:
        """Создаем QR и запись в БД"""
        short_link = SITE_NAME + validated_data["short_code"]
        qr = QrGenerator.qr_base64(short_link)
        try:
            return LinkRegUser.objects.create(**validated_data, qr=qr)
        except IntegrityError as e:
            ServerStat.reported(
                "LinkAuthSerializer_76",
                "создался уже существующий short_code!"
                + f"текст ошибки IntegrityError: {e}",
            )
            validated_data.pop("short_code", None)
            short_code = GeneratorShortCode.for_postgresql()
            short_link = SITE_NAME + short_code
            qr = QrGenerator.qr_base64(short_link)
            return LinkRegUser.objects.create(
                **validated_data, qr=qr, short_code=short_code
            )
        except:
            data = {"error": "Пожалуйста, пересоздайте ссылку"}
            return data

    def get_short_link(self, obj) -> str:
        short_link = SITE_NAME + obj.short_code
        return short_link
