from django.contrib import admin
from django.db import models
from pagedown.widgets import AdminPagedownWidget

from .models import CompanyInfo, Featured

class CompanyInfoAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': AdminPagedownWidget },
    }

admin.site.register(CompanyInfo, CompanyInfoAdmin)
admin.site.register(Featured)
