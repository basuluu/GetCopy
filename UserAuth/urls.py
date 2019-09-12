from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views


urlpatterns = [
    url(r'^login/$', views.login_v),
    url(r'^logout/$', views.logout_v),
    url(r'^signup/$', views.signup),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^recovery/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.change_password, name='recovery'),
    url(r'^recovery/', views.recovery),
]