from django.urls import path
from .views import PostlinkViewset

name_space = "elink_index"

urlpatterns = [
    path(
        "/<str:short_code>/password-check",
        PostlinkViewset.as_view({"get": "open_link_pass"}),
        name="pass_check",
    ),
    path(
        "fastlink/<str:site>/<str:long_code>",
    )
    path(
        "/links",
        PostlinkViewset.as_view(
            {   
                #"get": "fast_link",
                "post": "create_link",
                "delete": "delete_link",
                "patch": "update_description",
            }
        ),
    ),
]
