import base64
from elink_index.generator_code import GeneratorShortCode
from elink_index.qr_generator import QrGenerator
from elink_index.models import LinkRegUser
from django.db import IntegrityError
from users.models import User
from django.utils import timezone
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from elink.settings import SITE_NAME
from elink_index.models import LinkRegUser, InfoLink

class InfoLinkSerializer(serializers.ModelSerializer):

    class Meta:
        model = InfoLink
        fields = '__all__'


class StatSerializer(serializers.ModelSerializer):

    #statz = InfoLinkSerializer(many=True, read_only=True)

    #stats = serializers.SerializerMethodField()
    link_check = serializers.SerializerMethodField()    
    country_check_id = serializers.SerializerMethodField()
    device_id = serializers.SerializerMethodField()
    linkId = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('id'))
    #qr = serializers.SerializerMethodField()
    shortLink = serializers.SerializerMethodField('get_short_link')
    #shortLink = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('short_code'))
    longLink = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('long_link'))
    linkDescription = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('description'))
    linkLimit = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('limited_link'))
    linkPassword = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('secure_link'))
    linkStartDate = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('start_link'))
    linkEndDate = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('date_stop'))
    linkCreatedDate = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('date_add'))
    clicked = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('how_many_clicked'))
    repeatedClicked = serializers.ModelField(model_field=LinkRegUser()._meta.get_field('again_how_many_clicked'))

    class Meta:
        model = LinkRegUser
        exclude = ('short_code', 'long_link', 'start_link', 'secure_link',
                    'date_stop', 'author', 'date_add','public_stat_full',
                    'public_stat_small', 'again_how_many_clicked',
                    'how_many_clicked', 'limited_link', 'description')
        read_only_fields = ('__all__',)
        """read_only_fields = ('short_code', 'long_link', 'start_link', 'secure_link',
                            'date_stop', 'author', 'date_add', 'public_stat_full',
                            'public_stat_small', 'again_how_many_clicked',
                            'how_many_clicked', 'limited_link', 'id', 'link_check', 'country_check_id', 'device_id',)"""

    def get_short_link(self, obj) -> str:
        short_link = SITE_NAME + obj.short_code
        #print(short_link)
        return short_link
    
    def get_queryset(self, obj):
        return InfoLink.objects.filter(link_check = obj.id)

    def get_link_check(self, obj):
        #print(self.get_queryset)
        return 1

    def get_country_check_id(self, obj):
        return 1#InfoLink.objects.filter(link_check = obj.id)

    def get_device_id(self, obj):
        return 1#InfoLink.objects.filter(link_check = obj.id)