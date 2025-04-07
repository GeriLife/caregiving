"""Core URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import TemplateView

urlpatterns = [
    path(
        "__debug__/",
        include("debug_toolbar.urls"),
    ),
    path("admin/", admin.site.urls),
    path(
        "i18n/",
        include("django.conf.urls.i18n"),
    ),
    path(
        "activities/",
        include("activities.urls"),
    ),
    path(
        "accounts/",
        include("accounts.urls"),
    ),
    path(
        "accounts/",
        include("django.contrib.auth.urls"),
    ),
    path(
        "homes/",
        include("homes.urls"),
    ),
    path(
        "residents/",
        include("residents.urls"),
    ),
    path(
        "work/",
        include("work.urls"),
    ),
    path(
        "",
        TemplateView.as_view(
            template_name="home.html",
        ),
        name="home",
    ),
    path("__reload__/", include("django_browser_reload.urls")),
]
