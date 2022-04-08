from django.contrib import admin

from .models import Duty, DutyType

@admin.register(Duty)
class DutyAdmin(admin.ModelAdmin):
    pass


@admin.register(DutyType)
class DutyTypeAdmin(admin.ModelAdmin):
    pass