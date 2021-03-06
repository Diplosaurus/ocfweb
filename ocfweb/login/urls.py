from django.conf.urls import url

from ocfweb.login.calnet import login as calnet_login
from ocfweb.login.calnet import logout as calnet_logout
from ocfweb.login.ocf import login
from ocfweb.login.ocf import logout


urlpatterns = [
    url(r'^login/$', login, name='login'),
    url(r'^logout/$', logout, name='logout'),

    url(r'^calnet/login/$', calnet_login, name='calnet_login'),
    url(r'^calnet/logout/$', calnet_logout, name='calnet_logout'),
]
