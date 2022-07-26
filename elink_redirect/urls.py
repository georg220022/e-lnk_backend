from django.urls import path
from .views import open_link#, index
from django.views.generic import TemplateView

app_name = 'elink_redirect'

urlpatterns = [
    path('<str:short_code>', open_link, name='open_link'),
    path('', TemplateView.as_view(template_name='index.html'))
]
