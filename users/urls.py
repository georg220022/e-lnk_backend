from django.urls import path
from .views import (
                    RegistrationAPIView,
                    EntersOnSite,
                    ChangePasswordView,
                    CustomRefresh,
                    ActivateAccount,
                    )

app_name = 'authentication'

urlpatterns = [
    path('/registration', RegistrationAPIView.as_view()),
    path('/change_pass', ChangePasswordView.as_view()),
    path('/refresh', CustomRefresh.as_view({'post': 'get_token'})),
    path('/login', EntersOnSite.as_view({'post': 'get_enter'})),
    path('/logout', EntersOnSite.as_view({'post': 'get_logout'})),
    path('/activate/<int:id>/<str:activation_code>',
         ActivateAccount.as_view({'get': 'get_activation'}))
]