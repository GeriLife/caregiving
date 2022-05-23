from django.contrib import admin


from .models import Resident

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    pass
