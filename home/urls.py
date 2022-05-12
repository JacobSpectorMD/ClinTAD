from django.conf.urls import url, include
from django.contrib.staticfiles.storage import staticfiles_storage
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView

import home.views as views

urlpatterns = [
    url(r'^$', views.home.as_view(), name='home'),
    url(r'^cases/$', views.cases, name='cases'),
    url(r'^single/', include("single.urls")),
    url(r'^multiple/$', views.multiple.as_view(), name='multiple'),
    url(r'^multiple_submit/$', views.multiple_submit, name='multiple_submit'),
    url(r'^about/$', views.about.as_view(), name='about'),
    url(r'^api/clear_data/', views.clear_data, name='clear_data'),
    url(r'^favicon.ico$', RedirectView.as_view(url=staticfiles_storage.url('/admin/img/favicon.ico'),
                                               permanent=False), name="favicon"),
    url(r'^set_announcement/$', views.set_announcement, name='set_announcement'),
    url(r'^demonstration/$', views.demonstration.as_view(), name="demonstration")
]