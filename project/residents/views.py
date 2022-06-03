from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView

from .models import Resident


class ResidentDetailView(LoginRequiredMixin,DetailView):
    model = Resident
    context_object_name = "resident"
    template_name = "residents/resident_detail.html"


class ResidentListView(ListView):
    model = Resident
    context_object_name = "residents"
