from elink_index.models import LinkRegUser
from datetime import datetime, timedelta
from rest_framework import serializers
from elink.settings import SITE_NAME


class StatSerializer(serializers.ModelSerializer):

    statistics = serializers.SerializerMethodField(read_only=True)
    linkId = serializers.ModelField(model_field=LinkRegUser(
                                    )._meta.get_field('id'))
    shortLink = serializers.SerializerMethodField('get_short_link')
    longLink = serializers.ModelField(model_field=LinkRegUser(
                                      )._meta.get_field('long_link'))
    linkDescription = serializers.ModelField(model_field=LinkRegUser(
                                             )._meta.get_field('description'))
    linkLimit = serializers.ModelField(model_field=LinkRegUser(
                                       )._meta.get_field('limited_link'))
    linkPassword = serializers.ModelField(model_field=LinkRegUser(
                                          )._meta.get_field('secure_link'))
    linkStartDate = serializers.ModelField(model_field=LinkRegUser(
                                           )._meta.get_field('start_link'))
    linkEndDate = serializers.ModelField(model_field=LinkRegUser(
                                         )._meta.get_field('date_stop'))
    linkCreatedDate = serializers.ModelField(model_field=LinkRegUser(
                                             )._meta.get_field('date_add'))
    clicked = serializers.ModelField(model_field=LinkRegUser(
                                     )._meta.get_field('how_many_clicked'))
    repeatedClicked = serializers.ModelField(model_field=LinkRegUser(
                                             )._meta.get_field(
                                              'again_how_many_clicked'))

    class Meta:
        model = LinkRegUser
        exclude = ('short_code', 'long_link', 'start_link', 'secure_link',
                   'date_stop', 'author', 'date_add', 'public_stat_full',
                   'public_stat_small', 'again_how_many_clicked',
                   'how_many_clicked', 'limited_link', 'description', 'id')
        read_only_fields = ('__all__',)

    def get_short_link(self, obj) -> str:
        short_link = SITE_NAME + obj.short_code
        return short_link

    def get_statistics(self, obj):
        queryset = self.context.filter(link_check__id=obj.id)
        device = {
                1: 0, 2: 0, 3: 0,
                4: 0, 5: 0, 6: 0,
                7: 0,
            }
        for obj in queryset:
            if obj.device_id in device:
                device[obj.device_id] += 1
            else:
                device[obj.device_id] = 1

        def clicked():
            clicked = {
                'mobile': int(device[1])+int(device[3])+int(device[4]),
                'pc': int(device[2])+int(device[5])+int(device[6]),
                'other': int(device[7])
            }
            return clicked

        def country(obj, queryset):
            countrys = {}
            for obj in queryset:
                if obj.country in countrys:
                    countrys[obj.country] += 1
                else:
                    countrys[obj.country] = 1

            if len(countrys) > 9:
                other = 0
                while len(countrys) > 9:
                    min_id = min(countrys)
                    other += countrys[min_id]
                    del countrys[min_id]
                if other > 0:
                    countrys['other'] = other
            elif len(countrys) == 0:
                return None
            return countrys

        def devices():
            return device

        def hours(obj, queryset):
            one_day = (datetime.now() -
                       timedelta(hours=24))  # использую наивную дату
            queryset = queryset.filter(date_check__gte=one_day)
            hour = {
                '00': 0, '01': 0, '02': 0, '03': 0, '04': 0, '05': 0,
                '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0,
                '12': 0, '13': 0, '14': 0, '15': 0, '16': 0, '17': 0,
                '18': 0, '19': 0, '20': 0, '21': 0, '22': 0, '23': 0,
            }
            for obj in queryset:
                hour[str(obj.date_check.strftime("%H"))] += 1
            return hour

        return {
            'country': country(obj, queryset),
            'device': devices(),
            'hours': hours(obj, queryset),
            'clicks': clicked()
        }
