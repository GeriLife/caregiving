from django.urls import path
from django.utils.translation import gettext_lazy as _
from .views import LoginView, SignUpView

urlpatterns = [
    path(_("signup/"), SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
]
