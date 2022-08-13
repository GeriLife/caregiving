"""core URL Configuration

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
from django.utils.translation import gettext_lazy as _
from django.views.generic.base import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path(_("admin/"), admin.site.urls),
    path("i18n/", include("django.conf.urls.i18n")),
    path(_("accounts/"), include("accounts.urls")),
    path(_("accounts/"), include("django.contrib.auth.urls")),
    path(_("homes/"), include("homes.urls")),
    path(_("residents/"), include("residents.urls")),
    path(_("work/"), include("work.urls")),
]
