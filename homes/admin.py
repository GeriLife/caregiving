from django.contrib import admin

from .models import Home, HomeGroup


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    pass


# register the HomeGroup model
@admin.register(HomeGroup)
class HomeGroupAdmin(admin.ModelAdmin):
    pass