from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import views as auth_views
from .forms import LoginForm, CustomUserCreationForm


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("home")
    template_name = "registration/signup.html"


class LoginView(auth_views.LoginView):
    form_class = LoginForm
    template_name = "registration/login.html"
