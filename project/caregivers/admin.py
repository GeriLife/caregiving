from django.contrib import admin

from .models import CaregiverRole

@admin.register(CaregiverRole)
class CaregiverRoleAdmin(admin.ModelAdmin):
    pass
