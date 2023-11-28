from django.contrib import admin

from .models import Home


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    pass
