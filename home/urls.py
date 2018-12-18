from django.conf.urls import url, include
from home.views import *
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^$', home.as_view(), name='home'),
    url(r'^single/', include("single.urls")),
    url(r'^multiple/$', multiple.as_view(), name='multiple'),
    url(r'^about/$', about.as_view(), name='about'),
    url(r'^contact/', contact.as_view(), name='contact'),
    url(r'^api/clear_data/', clear_data, name='clear_data'),
    url(r'^favicon.ico$', RedirectView.as_view(url=staticfiles_storage.url('/admin/img/favicon.ico'),
                                               permanent=False), name="favicon"),
    url(r'^demonstration/$', demonstration.as_view(), name="demonstration")
]