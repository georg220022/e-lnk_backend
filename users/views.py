import base64
import json
from elink_index.throttle import RegistrationAnonymousThrottle
from elink.settings import REDIS_FOR_ACTIVATE, SITE_NAME
from .send_mail import RegMail
from .public_id_generator import GeneratorId
from .models import User
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegistrationSerializer, ChangePasswordSerializer, ChangePasswordSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import BlacklistMixin, RefreshToken
from django.shortcuts import redirect

class CustomRefresh(viewsets.ViewSet, BlacklistMixin):

    def get_permissions(self):
       return (permissions.AllowAny(),)

    def get_token(self, request):
        try:
            old_token = request.COOKIES.get('refresh', False)
            RefreshToken(old_token).blacklist()
            old_token = old_token[old_token.find('.') + 1: old_token.rfind('.')]
            base64_message = old_token
            base64_bytes = base64_message.encode('ascii')
            message_bytes = base64.b64decode(base64_bytes + b'===')
            message = message_bytes.decode('ascii')
            message = json.loads(message)
            public_key = message.get('user_id', 'юзера_нет')
        except:
            data = {"error": "Токен обновления доступа не прошел проверку, попробуйте войти снова."}
            return Response(data, status=status.HTTP_401_UNAUTHORIZED)
        user = get_object_or_404(User, public_key=public_key)
        refresh = RefreshToken.for_user(user)
        data = {
            'email': str(user.email),
            'access': str(refresh.access_token),
            }
        response = Response(data, status=status.HTTP_200_OK)
        response.set_cookie(
                key = 'refresh', 
                value = str(refresh),
                expires = 5184000,
                secure = False, # Изменить на сервере!! рансервер не поддерживает https
                httponly = True,
                        )
        
        return response


class ChangePasswordView(generics.UpdateAPIView):

        serializer_class = ChangePasswordSerializer
        model = User
        permission_classes = (permissions.IsAuthenticated(),)

        def get_object(self, queryset=None):
            obj = self.request.user
            return obj

        def update(self, request, *args, **kwargs):
            self.object = self.get_object()
            serializer = self.get_serializer(data=request.data)
            if serializer.is_valid(raise_exception=False):
                if not self.object.check_password(serializer.data.get("old_password")):
                    data = {"error": "Пароль не подошел"}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                self.object.set_password(serializer.data.get("new_password"))
                self.object.public_key = str(self.object.id) + str(GeneratorId.public_id())
                self.object.save()
                return Response(status=status.HTTP_200_OK)
            data = {"error": serializer.errors}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        return token

class RegistrationAPIView(APIView):

    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer
    throttle_classes = [RegistrationAnonymousThrottle, ]

    def post(self, request):
        if request.user.is_anonymous:
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=False):
                serializer.save()
                user_instance = serializer.instance
                refresh = MyTokenObtainPairSerializer.get_token(user_instance)#RefreshToken.for_user(serializer.instance)
                data = {
                    'email': str(user_instance),
                    'access': str(refresh.access_token),
                }
                data =  Response(data, status=status.HTTP_200_OK)
                data.set_cookie(
                    key = 'refresh', 
                    value = str(refresh),
                    expires = 5184000,
                    secure = False, # Изменить на сервере!! рансервер не поддерживает https
                    httponly = True,
                            )
                data.set_cookie('registration_elink', max_age=2592000)
                RegMail.send_code(user_instance)
                return data
        return Response({'error': 'Ошибка регистрации'}, status=status.HTTP_400_BAD_REQUEST)

class EntersOnSite(viewsets.ViewSet):

    def get_permissions(self):
        return (permissions.AllowAny(),)

    def get_enter(self, request):
        if len(request.data) == 2:
            email = request.data.get('email', False)
            pswrd = request.data.get('password', False)
            if (email and pswrd) is not False:
                user = get_object_or_404(User, email=str(email))
                status_login = user.check_password(str(pswrd))
                if status_login is True:
                    refresh = RefreshToken.for_user(user)#MyTokenObtainPairSerializer.get_token(user)
                    data = {
                        'email': user.email,
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)
                        }
                    new_resp = Response(data, status=status.HTTP_200_OK)
                    new_resp.set_cookie(
                            key = 'refresh', 
                            value = refresh,
                            expires = 5184000,
                            secure = False, # Изменить на сервере!! рансервер не поддерживает https
                            httponly = True,
                        )
                    return new_resp
        msg = {"error": "Ошибка входа, обратитесь в поддержку"}
        return Response(msg, status=status.HTTP_400_BAD_REQUEST)

class ActivateAccount(viewsets.ViewSet):

    def get_permissions(self):
        return (permissions.AllowAny(),)
    
    def get_activation(self, request, id=None, activation_code=None):
        check_cookies = request.COOKIES.get('registration_elink', False)
        if check_cookies is not False:
            if (id and activation_code) is not None:
                user = get_object_or_404(User, id=id)
                if user.is_active is False:
                    obj = REDIS_FOR_ACTIVATE.get(id)
                    if obj.decode('utf-8') == str(activation_code):
                        user.is_active = True
                        user.save()
                        REDIS_FOR_ACTIVATE.delete(id)
                        data = Response('Аккаунт активирован!', status=status.HTTP_200_OK)
                        data.set_cookie('registration_elink', max_age=1)
                        return data
        return redirect(SITE_NAME + '404.html')
