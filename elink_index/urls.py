from django.urls import path
from .views import PostlinkViewset

name_space = 'elink_index'

urlpatterns = [
    path('/<str:short_code>/password-check', PostlinkViewset.as_view({'get': 'open_link_pass'}), name='pass_check'),
    path('/links', PostlinkViewset.as_view({'post': 'create_link'})),
]
