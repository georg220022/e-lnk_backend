from django.urls import path
from .views import PersonalStat


urlpatterns = [
    path('', PersonalStat.as_view({'get': 'get_full_stat'})),
]
