from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView


from .views import RegistrationAPIView, EntersOnSite, LoginOnSite, ChangePasswordView

app_name = 'authentication'
urlpatterns = [
    #path('/blacklist', TokenBlacklistView.as_view(), name="logout"),
    path('/registration', RegistrationAPIView.as_view()),
    #path('/logout', RegistrationAPIView.as_view()),
    path('/change_pass', ChangePasswordView.as_view()),
    #path('/change_email', ChangeUserInfo.as_view({'put': 'change_email'})),
    #path('/refresh1', TokenRefreshView.as_view(), name='token_refresh'),
    path('/login', EntersOnSite.as_view({'post': 'get_enter'})),
    path('/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    #path('/token', TokenObtainPairView.as_view(), name='token_obtain_pair')
    #path('/login', LoginOnSite, name='logins'),
    #path('/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    #path('/refresh', TokenRefreshView.as_view(), name='token_refresh'),
]