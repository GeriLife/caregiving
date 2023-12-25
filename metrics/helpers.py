from activities.models import Activity
from metrics.models import ResidentActivity
from residents.models import Residency


def add_resident_activity(activity: Activity):
    for resident in activity.residents.all():
        activity = activity
        try:
            residency = Residency.objects.get(
                resident=resident,
                move_out__isnull=True,
            )
        except Residency.DoesNotExist:
            print("Residency doesn't exist")

            raise

        home = residency.home
        activity_type = activity.activity_type
        activity_minutes = activity.duration_minutes
        caregiver_role = activity.caregiver_role
        activity_date = activity.date

        resident_activity = ResidentActivity.objects.create(
            resident=resident,
            activity=activity,
            residency=residency,
            home=home,
            activity_type=activity_type,
            activity_minutes=activity_minutes,
            caregiver_role=caregiver_role,
            activity_date=activity_date,
        )
        resident_activity.save()