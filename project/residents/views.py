from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import UpdateView
from django.views.generic.list import ListView

from .models import Resident


class ResidentCreateView(CreateView):
    model = Resident
    fields = ["first_name", "last_initial", "on_hiatus"]


class ResidentDetailView(LoginRequiredMixin, DetailView):
    model = Resident
    context_object_name = "resident"
    template_name = "residents/resident_detail.html"


class ResidentUpdateView(LoginRequiredMixin, UpdateView):
    model = Resident
    fields = ["first_name", "last_initial", "on_hiatus"]


class ResidentListView(ListView):
    model = Resident
    context_object_name = "residents"
