from django.conf.urls import url, include
from user.views import *
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    path(r'', include('django.contrib.auth.urls')),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    # url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^tracks/$', tracks, name='tracks'),
    url(r'^new_track/$', new_track, name='new_track'),
    url(r'^edit_track/$', edit_track, name='edit_track'),
    url(r'^delete_track/$', delete_track, name='delete_track'),
    url(r'^default_enhancers/$', default_enhancers, name='default_enhancers'),
    url(r'^default_tads/$', default_tads, name='default_tads'),
    url(r'^default_cnvs/$', default_cnvs , name='default_cnvs')
]