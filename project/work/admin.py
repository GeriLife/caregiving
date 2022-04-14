from django.contrib import admin

from .models import Work, WorkType

@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    pass


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
    pass