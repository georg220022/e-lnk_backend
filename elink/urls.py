from django.contrib import admin
from django.urls import path, include
from django.conf import settings



urlpatterns = [
    #path('grappelli/', include('grappelli.urls')),
    path("admin_dash", admin.site.urls),
    path("", include("elink_redirect.urls")),
    path("api/v1", include("elink_index.urls")),
    path("api/v1", include("users.urls")),
    path("api/v1/panel", include("personal_area.urls")),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
