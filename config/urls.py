from django.conf.urls import url, include
from django.contrib import admin
from config import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import path
from single.admin import case_admin_site


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    #url(r'^case_admin_site/', case_admin_site.urls),
    url(r'', include('home.urls')),
    url(r'^user/', include('user.urls')),
    url(r'^password_reset/$',
      auth_views.PasswordResetView.as_view(template_name='password_reset_form.html'),
      name='password_reset'),
    url(r'^password_reset/done/$',
      auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
      name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
      auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
      name='password_reset_confirm'),
    url(r'^reset/done/$',
      auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
      name='password_reset_complete'),
    url(r'^api/', include('api.urls')), 
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)