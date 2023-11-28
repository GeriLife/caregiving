from django.urls import path
from django.utils.translation import gettext_lazy as _
from .views import SignUpView

urlpatterns = [
    path(_("signup/"), SignUpView.as_view(), name="signup"),
]
