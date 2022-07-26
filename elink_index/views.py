from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from django.shortcuts import redirect
from elink.settings import SITE_NAME
from .read_write_base import RedisLink, PostgresLink
from .throttle import Throttle_create_link
from .serializer import LinkAuthSerializer
from .validators import CheckLink


class PostlinkViewset(viewsets.ModelViewSet):


    permission_classes = [permissions.AllowAny]

    def get_throttles(self):
        return Throttle_create_link.choices_throttle_methods(self)

    def create_link(self, request):
        long_link = CheckLink.get_long_url(request)                       # Вернет ссылку или False
        if long_link is not False:
            if request.user.is_anonymous:
                data = RedisLink.writer(long_link)                        # Если пользователь не авторизован - пишем в Redis
                return Response(data, status=status.HTTP_201_CREATED)
            else:
                context = {
                    'user_id': request.user.id,
                    'long_link': long_link
                }
                serializer = LinkAuthSerializer(data=request.data,        # Если юзер авторизован - отправляем на сериализацию
                                                context=context)  # с последующей записью в PostgreSQL
                if serializer.is_valid(raise_exception=False):
                    serializer.save()
                    return Response(serializer.data,
                                    status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        data = {'msg': 'Ссылка не прошла проверку или поле не заполнено'}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return redirect(SITE_NAME + 'bad_values')

    def open_link_pass(self, request, short_code):
        obj = CheckLink.check_request(request.data)
        if obj:
            object_postgres = PostgresLink.reader(request, obj)
            if object_postgres is not False:
                return Response(object_postgres, status=status.HTTP_200_OK)
        return redirect(SITE_NAME) # НАПИСАТЬ ВОЗВРАЩЕНИЕ НЕ ВЕРНО ПАРОЛЯ ЕСЛИ ЧЕЛ ШАЛИТ
