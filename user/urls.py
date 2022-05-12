from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.urls import path

from user.views import *

urlpatterns = [
    # path(r'', include('django.contrib.auth.urls')),
    path('activate/<str:uidb64>/<str:token>/', activate, name='activate'),
    url(r'^login/$', login_view, name='login'),
    url(r'^logout/$', logout_view, name='logout'),
    url(r'^register/$', register, name='register'),
    url(r'^registration_sent/$', registration_sent, name='registration_sent'),

    # Tracks
    url(r'^add_track/$', add_track, name='add_track'),
    url(r'^delete_track/$', delete_track, name='delete_track'),
    url(r'^edit_track/$', edit_track, name='edit_track'),
    url(r'^new_track/$', new_track, name='new_track'),
    url(r'^tracks/$', tracks, name='tracks'),
    url(r'^update_user_track/$', update_user_track, name='update_user_track'),


    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'),
        {'extra_context': {'navbar': 'reset'}}, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
        {'extra_context': {'navbar': 'reset'}}, name='password_reset_done'),
    path('password_reset_confirm/<str:uidb64>/<str:token>/',
        auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
        {'extra_context': {'navbar': 'reset'}}, name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
        {'extra_context': {'navbar': 'reset'}}, name='password_reset_complete'),
]
