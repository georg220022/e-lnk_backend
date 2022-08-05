from os import lseek
from django import views
from .models import User
from django.conf import settings
from rest_framework import generics
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .serializers import RegistrationSerializer, ChangePasswordSerializer, ChangePasswordSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.models import TokenUser
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


class ChangePasswordView(generics.UpdateAPIView):
        serializer_class = ChangePasswordSerializer
        model = User
        permission_classes = (permissions.IsAuthenticated,)

        def get_object(self, queryset=None):
            obj = self.request.user
            print(obj)
            return obj

        def update(self, request, *args, **kwargs):
            self.object = self.get_object()
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid(raise_exception=True):
                # Check old password
                if not self.object.check_password(serializer.data.get("old_password")):
                    return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
                # set_password also hashes the password that the user will get
                self.object.set_password(serializer.data.get("new_password"))
                self.object.save()
                response = {
                    'status': 'success',
                    'code': status.HTTP_200_OK,
                    'message': 'Password updated successfully',
                    'data': []
                }
                return Response(response)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairSerializer(TokenObtainPairSerializer, ):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        #token.blacklist()
        print(token.__dict__)
        return token

class RegistrationAPIView(APIView):

    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=False):
            serializer.save()
            refresh = MyTokenObtainPairSerializer.get_token(serializer.instance)#RefreshToken.for_user(serializer.instance)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
            return Response(data, status=status.HTTP_201_CREATED)
        return Response({'error': 'Ошибка регистрации'})

class EntersOnSite(viewsets.ViewSet):

    def get_permissions(self):
        return (permissions.AllowAny(),)
    
    def get_enter(self, request):

        #print(se__dict__)
        if len(request.data) == 2:
            email = request.data.get('email', False)
            pswrd = request.data.get('password', False)
            if (email and pswrd) is not False:
                user = get_object_or_404(User, email=str(email))
                status_login = user.check_password(str(pswrd))
                if status_login is True:
                    """print(TokenObtainPairView.__dict__)
                    token = TokenObtainPairView.token_obtain_pair(user)
                    data = {
                        'refresh': str(token),
                        'access': str(token.access_token),
                        }"""
                    #access = AccessToken.for_user(user)
                    #print(refresh.__dict__)
                    #refresh = RefreshToken.for_user(user)
                    refresh = RefreshToken.for_user(user)#MyTokenObtainPairSerializer.get_token(user)
                    print(refresh)
                    #print(refresh.__dict__)#{'z' : f'refresh="{str(refresh)}; path=/; max-age=5184000; secure;" HttpOnly'}
                    #new_resp = Response.set_cookie(key='Set-Cookie', refresh="c84f18a2-c6c7-4850-be15-93f9cbaef3b3", path='/', max_age=5184000)
                    data = {
                        'access': str(refresh.access_token),
                        }
                    new_resp = Response(data, status=status.HTTP_200_OK)
                    new_resp.set_cookie(
                            key = 'refresh', 
                            value = data["access"],
                            expires = 5184000,
                            secure = False,
                            httponly = True,
                        )
                    #x = TokenUser(user.id)
                    #print(x)
                    return new_resp
        return Response('низя(((')

@csrf_exempt 
class LoginOnSite(TokenObtainPairSerializer):

    def get_validate(self, attr):
        data = super().validate(attr)
        token = self.get_token(self.user)
        data['user'] = str(self.user)
        data['id'] = self.user.id
        user_obj = User.objects.get(user=self.user)
        data['employeeRole'] = user_obj.employeeRole
        return data