from rest_framework import routers
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path
from django.conf.urls import include

import api.views as views
from home.models import Gene


router = routers.DefaultRouter()
router.register(r'chromosome', views.ChromosomeViewSet)
router.register(r'gene', views.GeneViewSet, basename=Gene)
router.register(r'hpo', views.HPOViewSet)
router.register(r'tad', views.TADViewSet) 
router.register(r'enhancer', views.EnhancerViewSet)
router.register(r'track', views.TrackViewSet) 
router.register(r'element', views.ElementViewSet) 
router.register(r'ut', views.UTViewSet) 
router.register(r'variant', views.VariantViewSet) 

urlpatterns = [
    # path('chromosome/', views.ChromosomeViewSet, name='chromosome'),
    path('', include(router.urls)),
    path('auth/', TokenObtainPairView.as_view(), name='auth'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='auth_refresh'),
    path('schema/', SpectacularAPIView.as_view(), name="schema"),
    path(
        'docs/',
        SpectacularSwaggerView.as_view(
            template_name="swagger-ui.html", url_name="schema"
        ),
        name="swagger-ui",
    ),
]
