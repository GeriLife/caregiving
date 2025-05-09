from typing import Any

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse

from django.utils.translation import gettext as _
from django.views.generic.edit import FormView
from django.views.generic.detail import DetailView
from django.views.generic.base import TemplateView

from homes.forms import AddCaregiverForm

from .charts import (
    prepare_activity_counts_by_resident_and_activity_type_chart,
    prepare_daily_work_percent_by_caregiver_role_and_type_chart,
    prepare_monthly_activity_hours_by_caregiver_role_chart,
    prepare_monthly_activity_hours_by_type_chart,
    prepare_work_by_caregiver_role_and_type_charts,
    prepare_work_by_caregiver_role_chart,
    prepare_work_by_type_chart,
)
from .models import Home, HomeUserRelation

user_model = get_user_model()


def regroup_homes_by_home_group(homes):
    # group homes with group by group name
    home_groups_with_homes = {}

    for home in homes:
        if home.home_group.name not in home_groups_with_homes:
            home_groups_with_homes[home.home_group.name] = []

        home_groups_with_homes[home.home_group.name].append(home)

    # Restructure home_groups_with_homes to a list of tuples
    # to make it easier to iterate over in the template
    home_groups_with_homes = [
        {"group_name": name, "homes": homes}
        for name, homes in home_groups_with_homes.items()
    ]

    return home_groups_with_homes


class HomeGroupListView(LoginRequiredMixin, TemplateView):
    template_name = "homes/home_group_list.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        user = self.request.user

        if not user.is_authenticated:
            return context

        if user.is_superuser:
            context["homes_without_group"] = Home.objects.filter(
                home_group__isnull=True,
            )

            context["homes_with_group"] = Home.objects.filter(
                home_group__isnull=False,
            )
        else:
            context["homes_without_group"] = self.request.user.homes.filter(
                home_group__isnull=True,
            )

            context["homes_with_group"] = self.request.user.homes.filter(
                home_group__isnull=False,
            )

        home_groups_with_homes = regroup_homes_by_home_group(
            context["homes_with_group"],
        )

        context["home_groups_with_homes"] = home_groups_with_homes

        return context


# user should be logged in


class HomeDetailView(LoginRequiredMixin, DetailView):
    model = Home
    context_object_name = "home"

    def get_object(self, queryset=None):
        if queryset is None:
            queryset = self.get_queryset()

        url_uuid = self.kwargs.get("url_uuid")  # Get the url_uuid from the URL

        if url_uuid is not None:
            queryset = queryset.filter(
                url_uuid=url_uuid,
            )  # Filter the queryset based on url_uuid

        home = get_object_or_404(
            queryset,
        )  # Get the object or return a 404 error if not found

        # ensure the user has access to the home
        if not home.has_access(user=self.request.user):
            raise PermissionDenied

        return home

    def prepare_activity_charts(self, context):
        """Prepare activity charts and add them to the template context."""
        home = context["home"]

        context["activity_counts_by_resident_and_activity_type_chart"] = (
            prepare_activity_counts_by_resident_and_activity_type_chart(home)
        )

        context["monthly_activity_hours_by_type_chart"] = (
            prepare_monthly_activity_hours_by_type_chart(home)
        )

        context["monthly_activity_hours_by_caregiver_role_chart"] = (
            prepare_monthly_activity_hours_by_caregiver_role_chart(home)
        )

        return context

    def prepare_work_charts(self, context):
        """Prepare work charts and add them to the template context."""
        home = context["home"]

        context["work_by_type_chart"] = prepare_work_by_type_chart(home)

        context["work_by_caregiver_role_chart"] = prepare_work_by_caregiver_role_chart(
            home,
        )

        context["daily_work_percent_by_caregiver_role_and_type_chart"] = (
            prepare_daily_work_percent_by_caregiver_role_and_type_chart(home)
        )

        context = prepare_work_by_caregiver_role_and_type_charts(context)

        return context

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add charts and permissions to the template context."""
        context = super().get_context_data(**kwargs)

        home = context["home"]

        # Check if user can manage the home
        context["user_can_manage"] = home.user_can_manage(self.request.user)

        # Check if work has been recorded
        # by selecting one record
        context["work_has_been_recorded"] = home.work_performed.exists()
        context["activity_has_been_recorded"] = home.activity_performed.exists()

        # Only prepare charts if work has been recorded
        if context["work_has_been_recorded"]:
            context = self.prepare_work_charts(context)
        if context["activity_has_been_recorded"]:
            context = self.prepare_activity_charts(context)
        return context


class HomeUserRelationListView(LoginRequiredMixin, FormView):
    form_class = AddCaregiverForm  # Use form_class instead of form
    template_name = "homes/home_user_relation_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        home = get_object_or_404(Home, url_uuid=self.kwargs.get("url_uuid"))

        # ensure the user can manage the home
        if not home.user_can_manage(user=self.request.user):
            raise PermissionDenied

        context["home"] = home
        context["home_user_relations"] = HomeUserRelation.objects.filter(home=home)

        return context

    def form_valid(self, form):
        email = form.cleaned_data["email"]

        user_exists = user_model.objects.filter(email=email).exists()

        if not user_exists:
            # TODO: Send an invitation email
            error_message = _("User does not exist")
            form.add_error("email", error_message)

            return self.form_invalid(form)

        user = user_model.objects.get(email=email)

        home = get_object_or_404(Home, url_uuid=self.kwargs.get("url_uuid"))

        home_user_exists = HomeUserRelation.objects.filter(
            home=home,
            user=user,
        ).exists()

        if home_user_exists:
            error_message = _("User is already a caregiver in this home")
            form.add_error("email", error_message)

            return self.form_invalid(form)

        try:
            HomeUserRelation.objects.create(
                home=home,
                user=user,
            )
        except Exception:
            error_message = _("Something went wrong")
            messages.error(self.request, error_message)

            return self.form_invalid(form)

        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to current page after successful form submission."""
        # Get the current view name
        view_name = self.request.resolver_match.view_name
        # Get the current URL parameters
        kwargs = self.request.resolver_match.kwargs
        # Construct the success URL
        success_url = reverse(view_name, kwargs=kwargs)

        return success_url
