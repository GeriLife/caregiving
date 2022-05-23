from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView

from .models import Resident


class ResidentDetailView(LoginRequiredMixin,DetailView):
    model = Resident
    context_object_name = "resident"
    template_name = "residents/resident_detail.html"
