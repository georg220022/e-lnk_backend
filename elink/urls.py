from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('elink_redirect.urls')),
    path('api/v1', include('elink_index.urls')),
    path('api/v1', include('users.urls')),
    path('api/v1/panel', include('personal_area.urls')),
]
