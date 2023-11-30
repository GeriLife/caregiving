from django.contrib import admin


from .models import ResidentActivity


@admin.register(ResidentActivity)
class ResidentActivityAdmin(admin.ModelAdmin):
    pass
