from rest_framework import status, viewsets
from rest_framework.response import Response
from django.shortcuts import redirect
from elink.settings import SITE_NAME
from elink_index.models import LinkRegUser
from .read_write_base import RedisLink, PostgresLink
from .throttle import Throttle_create_link as Throttle
from .serializer import LinkAuthSerializer
from .validators import CheckLink
from .user_limit import UserLimit
from .permissions import Permissons
from django.db.models import Q
from .cache_module import Cache_module


class PostlinkViewset(viewsets.ModelViewSet):

    def get_permissions(self):
        return Permissons.choices_methods(self)

    def get_throttles(self):
        return Throttle.choices_methods(self)

    def create_link(self, request):
        long_link = CheckLink.get_long_url(request)                       # Вернет ссылку или False
        if long_link is not False:
            if request.user.is_anonymous:
                data = RedisLink.writer(long_link)                        # Если пользователь не авторизован - пишем в Redis
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                limit = UserLimit.create_link(request.user)
                if request.user.is_active:
                    if limit is not True:
                        return Response(limit, status=status.HTTP_423_LOCKED)
                    context = {
                        'user_id': request.user.id,
                        'long_link': long_link
                    }
                    serializer = LinkAuthSerializer(data=request.data,        # Если юзер авторизован - отправляем на сериализацию
                                                    context=context)  # с последующей записью в PostgreSQL
                    if serializer.is_valid(raise_exception=False):
                        serializer.save()
                        request.user.link_count += 1
                        request.user.save()
                        Cache_module.writer(self.request.user.id, serializer.data)
                        return Response(serializer.data,
                                        status=status.HTTP_201_CREATED)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                data = {'error': 'Учетная запись не активирована. Перейдите по ссылке которая была отправлена по почте при регистрации.'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        data = {'msg': 'Ссылка не прошла проверку или поле не заполнено'}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def open_link_pass(self, request, short_code):
        obj = CheckLink.check_request(request.data)
        if obj:
            object_postgres = PostgresLink.reader(request, obj)
            if object_postgres is not False:
                return Response(object_postgres, status=status.HTTP_200_OK)
        return redirect(SITE_NAME) # НАПИСАТЬ ВОЗВРАЩЕНИЕ НЕ ВЕРНО ПАРОЛЯ ЕСЛИ ЧЕЛ ШАЛИТ

    def delete_link(self, request):
        short_codes = request.data.get('shortCodes', False)
        if len(short_codes) > 0 and short_codes is not False:
            author = self.request.user
            queryset = LinkRegUser.objects.filter(Q(author=author) & Q(short_code__in=short_codes))
            if len(queryset) > 0:
                id_data = [id for id in queryset.values('id')]
                queryset.delete()
                Cache_module.deleter(author.id, id_data)
                return Response(status=status.HTTP_200_OK)
        msg = {'error': 'Вы не владелец ссылки, либо объекта(ов) не существует'}
        return Response(msg, status=status.HTTP_403_FORBIDDEN)

    def update_description(self, request):
        obj = CheckLink.description(request)
        if obj is not False:
            description = request.data['linkDescription']
            obj.description = description
            obj.save()
            Cache_module.editor(request.user.id, obj.id, description)
            return Response(status=status.HTTP_200_OK)
        msg = {'error': 'Ошибка реактирования, макс длинна' +
                        'описания 1000 символов. Либо вы не владелец объекта'}
        return Response(msg, status=status.HTTP_403_FORBIDDEN)
