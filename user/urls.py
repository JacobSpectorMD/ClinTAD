from django.conf.urls import url, include
from user.views import *
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path

urlpatterns = [
    # path(r'', include('django.contrib.auth.urls')),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        activate, name='activate'),
    url(r'^register/$', register, name='register'),
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^tracks/$', tracks, name='tracks'),
    url(r'^new_track/$', new_track, name='new_track'),
    url(r'^edit_track/$', edit_track, name='edit_track'),
    url(r'^delete_track/$', delete_track, name='delete_track'),
    url(r'^default_enhancers/$', default_enhancers, name='default_enhancers'),
    url(r'^default_tads/$', default_tads, name='default_tads'),
    url(r'^default_cnvs/$', default_cnvs, name='default_cnvs'),
    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'), name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView, name='password_reset_complete'),
]
