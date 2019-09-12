from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'download/(?P<file_path>.*)$', views.download_zip),
    url(r'^get_history', views.get_history, name='get_history')
]