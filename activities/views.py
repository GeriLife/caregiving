import uuid

from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView

from metrics.models import ResidentActivity
from residents.models import Residency, Resident
from metrics.forms import ResidentActivityForm


class ResidentActivityListView(LoginRequiredMixin, ListView):
    template_name = "activities/resident_activity_list.html"
    queryset = ResidentActivity.objects.all()
    context_object_name = "activities"
    paginate_by = 100
    ordering = ["-activity_date"]


class ResidentActivityFormView(LoginRequiredMixin, FormView):
    template_name = "activities/resident_activity_form.html"
    form_class = ResidentActivityForm
    success_url = reverse_lazy("activity-list-view")

    def get_form_kwargs(self):
        """Override the get_form_kwargs method to pass the user to the form.

        This will allow the form to filter the residents by the user's
        homes or the superuser to filter by all homes.
        """

        kwargs = super().get_form_kwargs()

        kwargs["user"] = self.request.user

        return kwargs

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Override the post method to add the resident activity in the same
        transaction as the activity."""
        form = self.get_form()
        is_form_valid = form.is_valid()

        if is_form_valid:
            # create a resident activity for each resident in the form
            residents_field_errors = []

            resident_ids = form.cleaned_data["residents"]

            # generate group activity ID based on current epoch time
            group_activity_id = uuid.uuid4()

            for resident_id in resident_ids:
                try:
                    resident = Resident.objects.get(id=resident_id)
                    _create_resident_activity(resident, group_activity_id, form)
                except Resident.DoesNotExist:
                    transaction.set_rollback(True)

                    error_message = f"Resident ID {resident_id} does not exist."

                    is_form_valid = False
                    residents_field_errors.append(error_message)
                except Residency.DoesNotExist:
                    transaction.set_rollback(True)

                    error_message = (
                        f"Resident {resident} is not currently residing in a home."
                    )

                    is_form_valid = False
                    residents_field_errors.append(error_message)

            if residents_field_errors:
                form.add_error("residents", residents_field_errors)

        return self.form_valid(form) if is_form_valid else self.form_invalid(form)


def _create_resident_activity(
    resident: Resident,
    group_activity_id: uuid.UUID,
    form: ResidentActivityForm,
):
    """Create a resident activity for the given resident and form."""

    try:
        residency = Residency.objects.get(
            resident=resident,
            move_out__isnull=True,
        )
    except Residency.DoesNotExist:
        raise

    home = residency.home
    activity_type = form.cleaned_data["activity_type"]
    activity_minutes = form.cleaned_data["activity_minutes"]
    caregiver_role = form.cleaned_data["caregiver_role"]
    activity_date = form.cleaned_data["activity_date"]

    resident_activity = ResidentActivity.objects.create(
        resident=resident,
        residency=residency,
        home=home,
        activity_type=activity_type,
        activity_minutes=activity_minutes,
        caregiver_role=caregiver_role,
        activity_date=activity_date,
        group_activity_id=group_activity_id,
    )

    resident_activity.save()
