from django.urls import path
#from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegistrationAPIView, EntersOnSite, ChangePasswordView, CustomRefresh, ActivateAccount

app_name = 'authentication'

urlpatterns = [
    path('/registration', RegistrationAPIView.as_view()),
    path('/change_pass', ChangePasswordView.as_view()),
    path('/refresh', CustomRefresh.as_view({'post': 'get_token'})),
    path('/login', EntersOnSite.as_view({'post': 'get_enter'})),
    path('/activate/<int:id>/<str:activation_code>', ActivateAccount.as_view({'get': 'get_activation'}))
]