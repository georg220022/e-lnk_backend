from django.urls import path

from .views import open_link, unlock_pass

app_name = "elink_redirect"

urlpatterns = [
    path("<str:short_code>", open_link, name="open_link"),
    path("api/v1/unlock", unlock_pass, name="unlock_pass"),
]
