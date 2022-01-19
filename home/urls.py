from django.conf.urls import url, include
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

import home.views as views

urlpatterns = [
    url(r'^$', views.home.as_view(), name='home'),
    url(r'^single/', include("single.urls")),
    url(r'^multiple/$', views.multiple.as_view(), name='multiple'),
    url(r'^multiple_submit/$', views.multiple_submit, name='multiple_submit'),
    url(r'^about/$', views.about.as_view(), name='about'),
    url(r'^contact/', views.contact.as_view(), name='contact'),
    url(r'^api/clear_data/', views.clear_data, name='clear_data'),
    url(r'^favicon.ico$', RedirectView.as_view(url=staticfiles_storage.url('/admin/img/favicon.ico'),
                                               permanent=False), name="favicon"),
    url(r'^demonstration/$', views.demonstration.as_view(), name="demonstration")
]