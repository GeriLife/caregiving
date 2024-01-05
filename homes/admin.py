from django.contrib import admin

from .models import Home, HomeGroup, HomeUserRelation


@admin.register(Home)
class HomeAdmin(admin.ModelAdmin):
    pass


# register the HomeUserRelation model
@admin.register(HomeUserRelation)
class HomeUserRelationAdmin(admin.ModelAdmin):
    pass


# register the HomeGroup model
@admin.register(HomeGroup)
class HomeGroupAdmin(admin.ModelAdmin):
    pass
