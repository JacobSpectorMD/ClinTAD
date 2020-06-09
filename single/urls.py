from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^$', single, name="single"),
    url(r'^get_genes/', get_genes, name='get_genes'),
    url(r'^get_one_variant/$', get_variant, name='get_variant'),
    url(r'^get_variants/$', get_variants, name='get_variants'),
    url(r'^get_phenotypes/', get_phenotypes, name='get_phenotypes'),
    url(r'^hide_feedback/', hide_feedback, name='hide_feedback'),
    url(r'^statistics/$', statistics, name='statistics'),
]
