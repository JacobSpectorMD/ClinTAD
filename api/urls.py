from posixpath import basename
from django.urls import path
import api.views as views
from home.models import Gene
from rest_framework import routers
from django.conf.urls import include

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
] 