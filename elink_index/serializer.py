import base64
from .generator_code import GeneratorShortCode
from .qr_generator import QrGenerator
from .models import LinkRegUser
from django.db import IntegrityError
from users.models import User
from django.utils import timezone
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from elink.settings import SITE_NAME
from django.core.cache import cache
from elink.server_stat import ServerStat

NoneType = type(None)


class LinkAuthSerializer(serializers.ModelSerializer):
    qr = serializers.SerializerMethodField()
    shortLink = serializers.SerializerMethodField('get_short_link')
    linkId = serializers.ModelField(required=False, model_field=LinkRegUser(
                                    )._meta.get_field('id'))
    longLink = serializers.ModelField(required=False,
                                      model_field=LinkRegUser(
                                      )._meta.get_field('long_link'))
    linkDescription = serializers.ModelField(required=False,
                                             model_field=LinkRegUser(
                                             )._meta.get_field('description'))
    linkLimit = serializers.ModelField(required=False,
                                       model_field=LinkRegUser(
                                       )._meta.get_field('limited_link'))
    linkPassword = serializers.ModelField(required=False,
                                          model_field=LinkRegUser(
                                          )._meta.get_field('secure_link'))
    linkStartDate = serializers.ModelField(required=False,
                                           model_field=LinkRegUser(
                                           )._meta.get_field('start_link'))
    linkEndDate = serializers.ModelField(required=False,
                                         model_field=LinkRegUser(
                                         )._meta.get_field('date_stop'))
    linkCreatedDate = serializers.ModelField(required=False,
                                             model_field=LinkRegUser(
                                             )._meta.get_field('date_add'))
    clicked = serializers.ModelField(required=False,
                                     model_field=LinkRegUser(
                                     )._meta.get_field('how_many_clicked'))
    repeatedClicked = serializers.ModelField(required=False,
                                             model_field=LinkRegUser(
                                             )._meta.get_field(
                                              'again_how_many_clicked'))

    class Meta:
        model = LinkRegUser
        read_only_fields = ('shortLink', 'short_code', 'date_add', )
        exclude = ('short_code', 'long_link', 'start_link', 'secure_link',
                   'date_stop', 'author', 'date_add', 'public_stat_full',
                   'public_stat_small', 'again_how_many_clicked',
                   'how_many_clicked', 'limited_link', 'description', 'id')

    def validate(self, data):
        data.pop('longLink')
        data['short_code'] = GeneratorShortCode.for_postgresql()
        data['date_add'] = timezone.now()
        data['description'] = data.pop('linkDescription', '')
        data['limited_link'] = data.pop('linkLimit', -1)
        data['secure_link'] = data.pop('linkPassword', '')
        data['start_link'] = data.pop('linkStartDate', None)
        data['date_stop'] = data.pop('linkEndDate', None)
        data['long_link'] = self.context['long_link']#
        data['author'] = get_object_or_404(User, id=int(self.context['user_id']))
        return data

    def create(self, validated_data):
        try:                                                                # P.s этот метод гораздо лучше чем проверять каждый раз короткий код на уникальность
            obj = LinkRegUser.objects.create(**validated_data)         # short_code (шанс 1 на 1 000 000 000)
        except IntegrityError as e:
            ServerStat.reported('LinkAuthSerializer_76', f'создался уже существующий short_code! текст ошибки IntegrityError: {e}')
            validated_data.pop('short_code', None)
            short_code = (GeneratorShortCode.for_postgresql() * 6)          # Только тогда выбросим исключение уникальности поля БД
            obj = LinkRegUser.objects.create(**validated_data,              # и сгенерируем новый short_code с бОльшей длинной....             # тут уже скорее вселенная схлопнется нежели совпадут 2 строки
                                             short_code=short_code)
            ServerStat.reported('LinkAuthSerializer_81', f'Конфликтующий ключ заменен успешно {short_code}, id={obj.id}')
        obj.save()
        return obj

    def get_short_link(self, obj) -> str:
        short_link = SITE_NAME + obj.short_code
        return short_link

    def get_qr(self, obj) -> base64:
        short_link = SITE_NAME + obj.short_code
        qr_code_base64 = QrGenerator.qr_base64(short_link)
        return qr_code_base64
