from django.urls import path
from .views import PersonalStat


urlpatterns = [
    path('', PersonalStat.as_view({'get': 'all_stat'})),
    path('/detail', PersonalStat.as_view({'get': 'one_link'}))
]