from django.db import IntegrityError
from django.utils import timezone
from rest_framework import serializers

from elink.settings import SITE_NAME
from service.generator_code import GeneratorCode as GeneratorShortCode
from service.qr_generator import QrGenerator
from service.server_stat import ServerStat

from .models import LinkRegUser


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
    #qr = serializers.Serializer
    #linkStartDate = serializers.DateTimeField(source='start_link')
    #linkCreatedDate = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S%z', source='date_add')#, input_formats=None

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
        data.pop("longLink")
        data["short_code"] = GeneratorShortCode.for_postgresql()
        data["date_add"] = timezone.now()
        data["description"] = data.pop("linkName", "")
        data["limited_link"] = data.pop("linkLimit", -1)
        data["secure_link"] = data.pop("linkPassword", "")
        data["start_link"] = data.pop("linkStartDate", None)
        data["date_stop"] = data.pop("linkEndDate", None)
        data["long_link"] = self.context["long_link"]
        data["author_id"] = self.context["user_id"]
        return data

    def create(self, validated_data):
        try:
            short_link = SITE_NAME + validated_data["short_code"]
            qr = QrGenerator.qr_base64(short_link)
            return LinkRegUser.objects.create(**validated_data, qr=qr)
        except IntegrityError as e:
            ServerStat.reported(
                "LinkAuthSerializer_76",
                "создался уже существующий short_code!"
                + f"текст ошибки IntegrityError: {e}",
            )
            validated_data.pop("short_code", None)
            short_code = GeneratorShortCode.for_postgresql() * 6
            return LinkRegUser.objects.create(**validated_data, short_code=short_code)

    def get_short_link(self, obj) -> str:
        short_link = SITE_NAME + obj.short_code
        return short_link

    """def get_qr(self, obj: LinkRegUser) -> str:
        short_link = SITE_NAME + obj.short_code
        qr_code_base64 = QrGenerator.qr_base64(short_link)
        return qr_code_base64
"""