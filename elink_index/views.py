from django.core.cache import cache
from django.db.models import Q
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response

from elink_index.models import LinkRegUser
from service.read_write_base import RedisLink
from service.cache_module import CacheModule
from service.server_stat import ServerStat
from service.user_limit import UserLimit

from .throttle import Throttle_create_link as Throttle
from .serializer import LinkAuthSerializer
from .validators import CheckLink
from .permissions import Permissons


class PostlinkViewset(viewsets.ViewSet):
    def get_permissions(self):
        return Permissons.choices_methods(self.action)

    def get_throttles(self):
        return Throttle.choices_methods(self.action)

    def create_link(self, request: HttpRequest) -> Response:
        long_link = CheckLink.get_long_url(request.data)
        if long_link: # is not False
            if request.user.is_anonymous:
                data = RedisLink.writer(long_link)
                cache.incr("server_guest_link")
                return Response(data, status=status.HTTP_201_CREATED)
            elif request.user.is_active is False:
                msg = {"error": "Активируйте учетную запись"}
                cache.incr("server_bad_try_create_user_link")
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            else:
                limit = UserLimit.create_link(request.user)
                if limit is not True:
                    return Response(limit, status=status.HTTP_423_LOCKED)
                context = {
                    "user_id": request.user.id,
                    "long_link": long_link,
                }
                serializer = LinkAuthSerializer(data=request.data, context=context)
                if serializer.is_valid(raise_exception=False):
                    serializer.save()
                    cache.incr(f"link_limit_{request.user.id}")
                    CacheModule.writer(self.request.user.id, serializer.data)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                cache.incr("server_bad_valid_serializer_create_link")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                # data = {"error": "Учетная запись не активирована. Перейдите по ссылке которая была отправлена по почте при регистрации."}
                # return Response(data, status=status.HTTP_400_BAD_REQUEST)
        ServerStat.reported(
            f"PostlinkViewset_54_{request.user}",
            "Скорее одно из полей не пришло(или не валидно)",
        )
        data = {"msg": "Ссылка не прошла проверку или поле не заполнено"}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def delete_link(self, request: HttpRequest) -> Response:
        short_links = request.data.get("shortLinks", False)
        if short_links is not False and len(short_links) > 0:
            short_codes = [str(obj[17:]) for obj in short_links]  # 9 для e-lnk.ru
            author = self.request.user
            query_values = list(
                LinkRegUser.objects.filter(
                    Q(author=author) & Q(short_code__in=short_codes)
                ).values_list("short_code", flat=True)
            )
            len_query = len(query_values)
            if len_query > 0:
                LinkRegUser.objects.filter(short_code__in=query_values).delete()
                CacheModule.deleter(author.id, query_values)
                cache.incr(f"link_limit_{request.user.id}", int(-len_query))
                cache.incr("server_delete_link")
                msg = {"msg": "Успешно"}
                return Response(msg, status=status.HTTP_200_OK)
        cache.incr("server_bad_delete_link")
        msg = {"error": "Вы не владелец ссылки либо объекта(ов) не существует"}
        ServerStat.reported(
            f"PostlinkViewset_79_{request.user.email}", "Попытка удалить не свою ссылку"
        )
        return Response(msg, status=status.HTTP_403_FORBIDDEN)

    def update_description(self, request: HttpRequest) -> Response:
        obj = CheckLink.description(request)
        if obj: #  is not False
            description = request.data.get("linkName", False)
            if description:
                obj.description = description
            else:
                obj.description = ""
                description = ""
            passwd = request.data.get("linkPassword", False)
            if passwd:
                obj.secure_link = passwd
            else:
                obj.secure_link = ""
                passwd = ""
            obj.save()
            CacheModule.editor(request.user.id, obj, description, passwd)
            cache.incr("server_update_desrip_link")
            return Response(status=status.HTTP_200_OK)
        cache.incr("server_bad_update_desrip_link")
        msg = {
            "error": "Ошибка реактирования, макс длинна"
            + "описания 1000 символов. Либо вы не владелец объекта"
        }
        ServerStat.reported(
            f"PostlinkViewset_92_{request.user.email}",
            "неудачная попытка изменения поля description",
        )
        return Response(msg, status=status.HTTP_403_FORBIDDEN)


class FastlinkViewset(viewsets.ViewSet):
    def get_permissions(self):
        return Permissons.choices_methods(self.action)

    def create_link(self, request: HttpRequest, site: str) -> Response:
        long_code = request.META.get("HTTP_MY_URL", False)
        if long_code and len(long_code) < 5001:
            long_link = "https://" + site + ".ru" + long_code
            data = RedisLink.writer(long_link, fast_link=True)
            cache.incr("server_guest_link")
            context = {"short_link": data, "long_link": long_link}
            return render(
                request, "fast_redirect.html", context=context
            )
        return redirect("https://e-lnk.ru/404")

    def handler404(request, exception):
        return render(request, "email.html")
