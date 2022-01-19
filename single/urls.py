from django.conf.urls import url, include
import single.views as views

urlpatterns = [
    url(r'^$', views.single, name="single"),
    url(r'^get_genes/', views.get_genes, name='get_genes'),
    url(r'^get_one_variant/$', views.get_variant, name='get_variant'),
    url(r'^get_variants/$', views.get_variants, name='get_variants'),
    url(r'^get_phenotypes/', views.get_phenotypes, name='get_phenotypes'),
    url(r'^hide_feedback/', views.hide_feedback, name='hide_feedback'),
    url(r'^statistics/$', views.statistics, name='statistics'),
    url(r'^submit_query/$', views.submit_query, name='submit_query'),
    url(r'^zoom/$', views.zoom, name='zoom'),
]
