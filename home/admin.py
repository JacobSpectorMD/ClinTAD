from django.contrib import admin
from django.contrib.admin.sites import AdminSite

from home.models import SingleViewer

class CaseAdminSite(AdminSite):
    fields = ['name_text', 'email_text', 'coordinates_text', 'phenotypes_text', 'comments_text', 'pub_date']

case_admin_site = CaseAdminSite(name="case_admin")

admin.site.register(SingleViewer)
