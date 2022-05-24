from django.contrib import admin


from .models import Residency, Resident

@admin.register(Resident)
class ResidentAdmin(admin.ModelAdmin):
    pass

@admin.register(Residency)
class ResidencyAdmin(admin.ModelAdmin):
    pass
