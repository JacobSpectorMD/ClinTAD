from django.conf.urls import url, include
from django.contrib import admin
from config import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'', include('home.urls')),
    url(r'^user/', include('user.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)