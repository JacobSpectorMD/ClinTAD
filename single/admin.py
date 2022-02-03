from django.contrib import admin
from single.models import Case
from home.admin import case_admin_site
# class EventAdminSite(AdminSite):
#     site_header = "UMSRA Events Admin"
#     site_title = "UMSRA Events Admin Portal"
#     index_title = "Welcome to UMSRA Researcher Events Portal"

# class CaseAdminSite(admin.AdminSite):
#     fields = ['name_text', 'email_text', 'coordinates_text', 'phenotypes_text', 'comments_text', 'pub_date']

# case_admin_site = CaseAdminSite(name='case-admin')

case_admin_site.register(Case)