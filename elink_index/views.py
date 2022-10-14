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
from service.validators import CheckLink
from .permissions import Permissons


class PostlinkViewset(viewsets.ViewSet):
    def get_permissions(self):
        return Permissons.choices_methods(self.action)

    def get_throttles(self):
        return Throttle.choices_methods(self.action)

    def create_link(self, request: HttpRequest) -> Response:
        """Создание ссылки со всеми сопутствующими проверками"""
        long_link = CheckLink.get_long_url(
            request.data
        )  # Валидируем длинную ссылку не в сериализаторе так как она понадобится в т.ч для Redis'a если юзер гость
        if long_link:
            if request.user.is_anonymous:
                data = RedisLink.writer(
                    long_link
                )  # Если пользователь гость - записываем ссылку в Redis
                cache.incr("server_guest_link")
                return Response(data, status=status.HTTP_201_CREATED)
            elif (
                request.user.is_active is False
            ):  # Проверка активации внутри контроллеров в связи с особенностями функционала сервиса
                msg = {
                    "error": "Учетная запись не активирована. Перейдите по ссылке которая была отправлена по почте при регистрации."
                }
                cache.incr("server_bad_try_create_user_link")
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            else:
                limit = UserLimit.create_link(
                    request.user
                )  # Проверяем тип подписки на аккаунте пользователя, для ограничения количества ссылок
                if isinstance(limit, str) #limit is not True:
                    return Response(limit, status=status.HTTP_400_BAD_REQUEST)
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
        ServerStat.reported(
            f"PostlinkViewset_54_{request.user}",
            "Скорее одно из полей не пришло(или не валидно)",
        )
        data = {
            "error": "Длинная ссылка обязательна! Ее длинна не может привышать 5000 символов"
        }
        return Response(data, status=status.HTTP_400_BAD_REQUEST)

    def delete_link(self, request: HttpRequest) -> Response:
        """Удаляем ссылки из базы и так же записи о них из кеша"""
        short_links = request.data.get("shortLinks", False)
        if short_links is not False and len(short_links) > 0:
            short_codes = [
                str(obj[9:]) for obj in short_links
            ]  # Собираем все short_code из приходящего массива
            author = self.request.user
            query_values = (
                list(  # Проверяем пришедший массив short_code на авторство отправителя
                    LinkRegUser.objects.filter(
                        Q(author=author) & Q(short_code__in=short_codes)
                    ).values_list("short_code", flat=True)
                )
            )
            len_query = len(query_values)
            if len_query > 0:
                LinkRegUser.objects.filter(
                    short_code__in=query_values
                ).delete()  # Все short_code которые принадлежат юзеру, будут удалены
                CacheModule.deleter(author.id, query_values)
                cache.incr(
                    f"link_limit_{request.user.id}", int(-len_query)
                )  # Уменьшаем количество ссылок пользователя на количество удаленных объектов
                cache.incr("server_delete_link")
                msg = {"msg": "Успешно"}
                return Response(msg, status=status.HTTP_200_OK)
        cache.incr("server_bad_delete_link")
        msg = {"error": "Вы не владелец ссылки либо объекта(ов) не существует"}
        ServerStat.reported(
            f"PostlinkViewset_79_{request.user.email}", "Попытка удалить не свою ссылку"
        )
        return Response(msg, status=status.HTTP_403_FORBIDDEN)

    def update_descrip_or_pass_lnk(self, request: HttpRequest) -> Response:
        """Обновление описания и/или пароля(так же обновляется в кеше для правильного отображения, если есть кешированные данные)"""
        obj = CheckLink.description_or_pass(
            request
        )  # Модуль проверки прав на редактирование описания
        if obj:
            if "linkName" in request.data:
                lnk_name_obj = request.data.get("linkName")
                if len(lnk_name_obj) == 0:
                    description = ""
                else:
                    description = lnk_name_obj
                obj.description = description
            else:
                description = False
            if "linkPassword" in request.data:
                passwd = request.data.get("linkPassword")
                if len(passwd) == 0:
                    passwd = ""
                obj.secure_link = passwd
            else:
                passwd = False
            obj.save()
            CacheModule.editor(
                request.user.id, obj, description, passwd
            )  # Модуль редактирования информации в кеше (если такая имеется)
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
    def get_throttles(self):
        return Throttle.choices_methods(self.action)

    def get_permissions(self):
        return Permissons.choices_methods(self.action)

    def create_link(self, request: HttpRequest, site: str) -> Response:
        """Создание быстрой ссылки через 'ee' на ali, ozon, wildberries"""
        long_code = request.META.get("HTTP_MY_URL", False)
        if long_code and len(long_code) < 5001:
            long_link = "https://" + site + ".ru" + long_code
            data = RedisLink.writer(long_link, fast_link=True)
            cache.incr("server_guest_link")
            context = {"short_link": data, "long_link": long_link}
            return render(request, "fast_redirect.html", context=context)
        return redirect("https://e-lnk.ru/404")
