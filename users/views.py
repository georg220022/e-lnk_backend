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
from .serializers import (
    RegistrationSerializer,
    ChangePasswordSerializer,
    ChangeSettingsSerializer,
)

logger = logging.getLogger(__name__)


class CustomRefresh(viewsets.ViewSet, BlacklistMixin):
    def get_permissions(self):
        return (permissions.AllowAny(),)

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
            return Response(err_data, status=status.HTTP_401_UNAUTHORIZED)
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
    permission_classes = (permissions.IsAuthenticated(),)

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

    def post(self, request: HttpRequest) -> Response:
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
                RegMail.send_code.delay(user_instance)
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


class EntersOnSite(viewsets.ViewSet):
    def get_permissions(self):
        return (permissions.AllowAny(),)

    def get_logout(self, request):
        data = Response("ты вышел", status=status.HTTP_200_OK)
        data.delete_cookie("refresh")
        cache.incr("server_logout_account")
        return data

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
            else:
                cache.incr("server_bad_enter")
                msg = {"error": "Не верный емейл или пароль"}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        msg = {"error": "Неудалось войти, код ошибки #usvi_199"}
        cache.incr("server_bad_enter")
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)


class ActivateAccount(viewsets.ViewSet):
    def get_permissions(self):
        return (permissions.AllowAny(),)

    def get_activation(
        self, request: HttpRequest, id=None, activation_code=None
    ) -> Response:
        check_cookies = request.COOKIES.get("registration_elink", False)
        check_cookies = True
        if check_cookies is not False:
            if (id and activation_code) is not None:
                user = get_object_or_404(User, id=id)
                if user.is_active is False:
                    obj = REDIS_FOR_ACTIVATE.get(id)
                    if obj.decode("utf-8") == str(activation_code):
                        user.is_active = True
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

    def get_cahnge_settings(self, request: HttpRequest) -> Response:
        instance = User.objects.get(id=request.user.id)
        serializer = ChangeSettingsSerializer(data=request.data, instance=instance, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if "email" in request.data:
            RegMail.change_mail.delay(None, serializer.data.get("email", "help@e-lnk.ru"), instance.id)
        if "utc" in request.data:
            CacheModule.remove_stat_link(instance.id)
        data = Response(status=status.HTTP_200_OK)
        data.set_cookie("registration_elink", max_age=2592000)
        return data

    def get_delete_acc(self, request: HttpRequest) -> Response:
        user = User.objects.get(id=request.user.id)
        user_pass = request.data.get("password", False)
        if isinstance(user_pass, str):
            if user.check_password(user_pass):
                user.delete()
                CacheModule.remove_stat_link(user.id)
                response = Response
                response.delete_cookie()
                response.status_code(status.HTTP_200_OK)
                return response
            else:
                msg = "Пароль не верный"
        else:
            msg = "Пароль должен быть строкой"
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

    def get_settings(self, request: HttpRequest) -> Response:
        user = User.objects.get(id=request.user.id)
        obj = {
            "utc": user.my_timezone,
            "email": user.email,
            "sendStat": user.send_stat_email,
        }
        data = json.dumps(obj)
        return Response(data, status=status.HTTP_200_OK)

class ResetUserInfo(viewsets.ViewSet):
    def get_permissions(self):
        return (permissions.AllowAny(),)
    
    def send_code_reset_pass(self, request):
        emails = request.data.get("email", False)
        if emails:
            if not cache.has_key(f"wait_{emails}"):                          
                if User.objects.filter(email=emails).exists():
                    cache.set(f"wait_{emails}", "ok", 300)
                    reset_pass_key = GeneratorId.reset_pass_key()
                    cache.set(f"reset_pass_{emails}", reset_pass_key, 86400)
                    RegMail.change_pass(emails, reset_pass_key)
                    return Response(status=status.HTTP_200_OK)
                msg = {"error": "Почты не существует на сервисе"}
                return Response(msg, status=status.HTTP_400_BAD_REQUEST)
            msg = {"error": "Запрос восстановления пароля не чаще 1 раза в 5 минут"}
            return Response(msg, status=status.HTTP_400_BAD_REQUEST)
        msg = {"error": "Поле email обязательно"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

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
                    return redirect("https://e-lnk.ru/pass_reset")
        return redirect("https://e-lnk.ru/404")
