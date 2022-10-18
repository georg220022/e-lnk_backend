import base64
import logging
import json
from django.http import HttpRequest
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import BlacklistMixin, RefreshToken
from rest_framework import status, viewsets, permissions, generics
from elink_index.throttle import RegistrationAnonymousThrottle
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from elink.settings import REDIS_FOR_ACTIVATE
from service.cache_module import CacheModule
from service.send_mail import RegMail
from service.generator_code import GeneratorCode as GeneratorId
from .models import User
from service.server_stat import ServerStat
from django.core.cache import cache
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes
from .serializers import (
    RegistrationSerializer,
    ChangePasswordSerializer,
    ChangeSettingsSerializer,
)

logger = logging.getLogger(__name__)


class CustomRefresh(viewsets.ViewSet, BlacklistMixin):
    def get_permissions(self):
        return (permissions.AllowAny(),)

    @extend_schema(
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за регистрацию, timezone от '-12' до '+12' включительно, в видестроки"
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS"}),
        ],
    )
    def get_token(self, request: HttpRequest) -> Response:
        err_data = {
            "error": (
                "Токен обновления доступа не прошел"
                + "проверку, попробуйте войти снова."
            )
        }
        old_token = request.COOKIES.get("refresh", False)
        if old_token:
            if isinstance(old_token, str):
                RefreshToken(old_token)
                old_token = old_token[old_token.find(".") + 1 : old_token.rfind(".")]
                base64_message = old_token
                base64_bytes = base64_message.encode("ascii")
                message_bytes = base64.b64decode(base64_bytes + b"===")
                message = message_bytes.decode("ascii")
                message = json.loads(message)
                public_key = message.get("user_id", False)
                if not public_key:
                    return Response(err_data, status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(err_data, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({"error": "гостевой режим"}, status=status.HTTP_200_OK)
        user = get_object_or_404(User, public_key=public_key)
        refresh = RefreshToken.for_user(user)
        data = {
            "email": str(user.email),
            "access": str(refresh.access_token),
        }
        response = Response(data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="refresh",
            value=str(refresh),
            expires=5184000,
            secure=True,  # серв нет поддержки шифрования
            httponly=True,
        )
        cache.incr("server_refresh_tokens")
        return response


class ChangePasswordView(generics.UpdateAPIView):

    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request: HttpRequest, *args, **kwargs) -> Response:
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=False):
            if not self.object.check_password(serializer.data.get("old_password")):
                data = {"error": "Пароль не подошел"}
                cache.incr("server_bad_change_pass")
                logger.warning(f"Request: {request}, Self: {self}")
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.public_key = str(self.object.id) + str(GeneratorId.public_id())
            self.object.save()
            cache.incr("server_good_change_pass")
            return Response(status=status.HTTP_200_OK)
        data = {"error": serializer.errors}
        return Response(data, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        return token


class RegistrationAPIView(APIView):

    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer
    throttle_classes = [
        RegistrationAnonymousThrottle,
    ]

    @extend_schema(
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за регистрацию, timezone от '-12' до '+12' включительно, в видестроки"
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS"}),
        ],
    )
    def post(self, request: HttpRequest) -> Response:
        if cache.get("registrations_on_site"):
            eml_obj = request.data.get("email", False)
            if eml_obj:
                if User.objects.filter(email=eml_obj).exists():
                    msg = "Email уже зарегестрирован"
                    return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
            if request.user.is_anonymous:
                serializer = self.serializer_class(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save()
                    user_instance = serializer.instance
                    refresh = MyTokenObtainPairSerializer.get_token(user_instance)
                    data = {
                        "email": str(user_instance),
                        "access": str(refresh.access_token),
                    }
                    data = Response(data, status=status.HTTP_200_OK)
                    data.set_cookie(
                        key="refresh",
                        value=str(refresh),
                        expires=5184000,
                        secure=True,  # рансервер не поддерживает https
                        httponly=True,
                    )
                    data.set_cookie("registration_elink", max_age=2592000)
                    id_email_user = {"id": user_instance.id, "email": user_instance.email}
                    RegMail.send_code.delay(id_email_user)
                    cache.incr("server_new_users")
                    return data
            if serializer.errors.get("email", False):
                msg = {"error": "Пользователь с таким email уже существует"}
            else:
                ServerStat.reported(
                    "RegistrationAPIView_129", f"Ошибка регистрации: {serializer.errors}"
                )
                msg = {"error": "Ошибка регистрации, обратитесь в поддержку"}
                cache.incr("server_error_register")
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        msg = {"error": "Извините, регистрация временно приостановлена"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

class EntersOnSite(viewsets.ViewSet):
    def get_permissions(self):
        return (permissions.AllowAny(),)

    @extend_schema(
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за регистрацию, timezone от '-12' до '+12' включительно, в видестроки"
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS"}),
        ],
    )
    def get_logout(self, request):
        data = Response(status=status.HTTP_200_OK)
        # data.set_cookie("refresh", '1', max_age=0)
        data.delete_cookie("refresh")
        cache.incr("server_logout_account")
        return data

    @extend_schema(
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за регистрацию, timezone от '-12' до '+12' включительно, в видестроки"
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS"}),
        ],
    )
    def get_enter(self, request: HttpRequest) -> Response:
        if len(request.data) == 2:
            email = request.data.get("email", False)
            pswrd = request.data.get("password", False)
            if (email and pswrd) is not False:
                try:
                    user = User.objects.get(email=str(email))
                except ObjectDoesNotExist:
                    msg = "Email не найден в базе"
                    cache.incr("server_enter_notfound_email")
                    return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
                status_login = user.check_password(str(pswrd))
                if status_login is True:
                    refresh = RefreshToken.for_user(user)
                    data = {
                        "email": user.email,
                        "access": str(refresh.access_token),
                    }
                    new_resp = Response(data, status=status.HTTP_200_OK)
                    new_resp.set_cookie(
                        key="refresh",
                        value=refresh,
                        expires=5184000,
                        secure=True,  # Изменить на сервере
                        httponly=True,
                    )
                    cache.incr("server_good_enter")
                    return new_resp
                # else:
                cache.incr("server_bad_enter")
                msg = {"error": "Не верный емейл или пароль"}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        msg = {"error": "Неудалось войти, код ошибки #usvi_199"}
        cache.incr("server_bad_enter")
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccount(viewsets.ViewSet):
    def get_permissions(self):
        return (permissions.AllowAny(),)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="password",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Пароль от аккаунта",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Пароль",
                    # description="Пароль от аккаунта",
                    value="pass_you_account"
                    ),
                ],
            ),
        ],
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за удаление аккаунта",
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS"}),
        ],
    )
    def get_activation(
        self, request: HttpRequest, id=None, activation_code=None
    ) -> Response:
        check_cookies = request.COOKIES.get("registration_elink", False)
        #check_cookies = True
        if check_cookies is not False:
            if (id and activation_code) is not None:
                user = get_object_or_404(User, id=id)
                if user.is_active is False:
                    obj = REDIS_FOR_ACTIVATE.get(id)
                    if obj.decode("utf-8") == str(activation_code):
                        user.is_active = True
                        user.send_stat_email = True
                        user.save()
                        REDIS_FOR_ACTIVATE.delete(id)
                        response = redirect("https://e-lnk.ru")
                        response.delete_cookie("registration_elink")
                        cache.incr("server_activated")
                        return response
        cache.incr("server_bad_try_activated")
        return redirect("https://e-lnk.ru/404")


class UserSettings(viewsets.ViewSet):
    def get_permissions(self):
        return (permissions.IsAuthenticated(),)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="password",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Пароль от аккаунта",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Пароль",
                    # description="Пароль от аккаунта",
                    value="pass_you_account"
                    ),
                ],
            ),
            OpenApiParameter(
                name="email",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
                description="Почта от аккаунта",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Email",
                    # description="Пароль от аккаунта",
                    value="email_you_account"
                    ),
                ],
            ),
            OpenApiParameter(
                name="newPassword",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
                description="Новый пароль от аккаунта",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Новый пароль",
                    #description="Пароль от аккаунта",
                    value="new_pass_you_account"
                    ),
                ],
            ),
            OpenApiParameter(
                name="sendStat",
                type=bool,
                required=False,
                location=OpenApiParameter.QUERY,
                description="Отправка ежедневной статистики на почту",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Обновить параметр",
                    #description="Пароль от аккаунта",
                    value="true or false"
                    ),
                ],
            ),
            OpenApiParameter(
                name="timezone",
                type=str,
                required=False,
                location=OpenApiParameter.QUERY,
                description="Смещение UTC от '-12' до '+12' включительно",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Смещение UTC",
                    #description="Пароль от аккаунта",
                    value="+3"
                    ),
                ],
            ),
        ],
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за редактирование настроек аккаунта пользователя, отправлять поля только которые собираетесь менять",
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS", "timezone": "+3"}),
            OpenApiExample(
                "Смена email",
                value = {"password": "YOU_PASS", "email": "NEW_YOUR_EMAIL"}),
            OpenApiExample( 
                "Смена нескольких настроек",
                value = {"password": "YOU_PASS", "timezone": "+3", "email": "NEW_YOUR_EMAIL", "sendStat": True}
           ),
        ],
    )
    def get_cahnge_settings(self, request: HttpRequest) -> Response:
        instance = User.objects.get(id=request.user.id)
        serializer = ChangeSettingsSerializer(
            data=request.data, instance=instance, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if "email" in request.data:
            RegMail.change_mail.delay(
                None, serializer.data.get("email", "help@e-lnk.ru"), instance.id
            )
        if "timezone" in request.data:
            CacheModule.remove_stat_link(instance.id)
        data = Response(status=status.HTTP_200_OK)
        data.set_cookie("registration_elink", max_age=2592000)
        return data

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="password",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Пароль от аккаунта",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Пароль",
                    # description="Пароль от аккаунта",
                    value="pass_you_account"
                    ),
                ],
            ),
        ],
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за удаление аккаунта",
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS"}),
        ],
    )
    def get_delete_acc(self, request: HttpRequest) -> Response:
        user = User.objects.get(id=request.user.id)
        user_pass = request.data.get("password", False)
        if isinstance(user_pass, str):
            if user.check_password(user_pass):
                user.delete()
                CacheModule.remove_stat_link(user.id)
                return Response(status=status.HTTP_200_OK)
            else:
                msg = "Пароль не верный"
        else:
            msg = "Пароль должен быть строкой"
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за регистрацию, timezone от '-12' до '+12' включительно, в видестроки",
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS"}),
        ],
    )
    def get_settings(self, request: HttpRequest) -> Response:
        user = User.objects.get(id=request.user.id)
        obj = {
            "timezone": user.my_timezone,
            "email": user.email,
            "sendStat": user.send_stat_email,
        }
        return Response(obj, status=status.HTTP_200_OK)


class ResetUserInfo(viewsets.ViewSet):
    def get_permissions(self):
        return (permissions.AllowAny(),)
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="email",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Email от аккаунта",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Почта",
                    # description="Пароль от аккаунта",
                    value="email_you_account"
                    ),
                ],
            ),
        ],
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за сброс пароля",
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS", "timezone": "+3"})
        ],
    )
    def send_code_reset_pass(self, request):
        emails = request.data.get("email", False)
        if emails:
            if not cache.has_key(f"wait_{emails}"):
                if User.objects.filter(email=emails).exists():
                    cache.set(f"wait_{emails}", "ok", 900)
                    reset_pass_key = GeneratorId.reset_pass_key()
                    cache.set(f"reset_pass_{emails}", reset_pass_key, 86400)
                    RegMail.change_pass(emails, reset_pass_key)
                    return Response(status=status.HTTP_200_OK)
                msg = {"error": "Почты не существует на сервисе"}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            msg = {
                "error": "Запрос восстановления пароля не чаще 1 раза в 15 минут, иногда письмо приходит не моментально, так же проверьте во входящих 'спам' или 'рассылки'"
            }
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        msg = {"error": "Поле email обязательно"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="email",
                type=str,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Email от аккаунта",
                examples=[
                    OpenApiExample(
                    "Пример 1",
                    summary="Почта",
                    # description="Пароль от аккаунта",
                    value="email_you_account"
                    ),
                ],
            ),
        ],
        responses={
                200: OpenApiResponse(),
                400: OpenApiResponse(description="{'error': Тут будет сообщение об ошибке}"),
            },
        request=OpenApiTypes.OBJECT,
        description="API отвечающий за сброс пароля",
        auth=None,
        operation_id=False,
        operation=None,
        examples=[
            OpenApiExample(
                "Смена timezone",
                value = {"password": "YOU_PASS", "timezone": "+3"})
        ],
    )
    def reset_pass(self, request, email=False, reset_code=False):
        if email and reset_code:
            if cache.has_key(f"reset_pass_{email}"):
                original_code = cache.get(f"reset_pass_{email}")
                if original_code == reset_code:
                    user = get_object_or_404(User, email=email)
                    new_pass = GeneratorId.public_id()
                    user.set_password(new_pass)
                    user.save()
                    cache.delete(f"reset_pass_{email}")
                    RegMail.change_pass(email, False, new_pass)
                    return redirect("https://e-lnk.ru/change_ok")
        return redirect("https://e-lnk.ru/404")
