from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from .drf_spectacular import urlpatterns as data_url


urlpatterns = [
    path("admin_dash", admin.site.urls),
    path("", include("elink_redirect.urls")),
    path("api/v1", include("elink_index.urls")),
    path("api/v1", include("users.urls")),
    path("api/v1/panel", include("personal_area.urls")),
]

urlpatterns += data_url

handler404 = "service.handlers.handler404"
# handler500 = "service.handlers.handler500"
handler403 = "service.handlers.handler403"
handler400 = "service.handlers.handler400"

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
