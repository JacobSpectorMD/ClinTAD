from django.conf.urls import url
import single.views as views

from single.admin import case_admin_site

urlpatterns = [
    url(r'^$', views.single, name="single"),
    url(r'admin/', case_admin_site.urls, name='admin'),
    url(r'^submit_case/', views.submit_case, name='submit_case'),
    url(r'^submitted_case/', views.submitted_case, name='submitted_case'),
    url(r'^get_genes/', views.get_genes, name='get_genes'),
    url(r'^get_one_variant/$', views.get_variant, name='get_variant'),
    url(r'^get_variants/$', views.get_variants, name='get_variants'),
    url(r'^get_phenotypes/', views.get_phenotypes, name='get_phenotypes'),
    url(r'^hide_feedback/', views.hide_feedback, name='hide_feedback'),
    url(r'^statistics/$', views.statistics, name='statistics'),
    url(r'^submit_query/$', views.submit_query, name='submit_query'),
    url(r'^zoom/$', views.zoom, name='zoom'),
]
