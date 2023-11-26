from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
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

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        url_uuid = self.kwargs.get("url_uuid")  # Get the url_uuid from the URL

        if url_uuid is not None:
            queryset = queryset.filter(
                url_uuid=url_uuid,
            )  # Filter the queryset based on url_uuid

        obj = get_object_or_404(
            queryset,
        )  # Get the object or return a 404 error if not found

        return obj


class ResidentUpdateView(LoginRequiredMixin, UpdateView):
    model = Resident
    fields = ["first_name", "last_initial", "on_hiatus"]

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        url_uuid = self.kwargs.get("url_uuid")  # Get the url_uuid from the URL

        if url_uuid is not None:
            queryset = queryset.filter(
                url_uuid=url_uuid,
            )  # Filter the queryset based on url_uuid

        obj = get_object_or_404(
            queryset,
        )  # Get the object or return a 404 error if not found

        return obj


class ResidentListView(ListView):
    model = Resident
    context_object_name = "residents"
