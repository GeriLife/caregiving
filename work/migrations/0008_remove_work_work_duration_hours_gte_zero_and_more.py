# Generated by Django 5.0 on 2024-01-09 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('work', '0007_alter_work_caregiver_role_alter_work_date_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='work',
            name='work_duration_hours_gte_zero',
        ),
        migrations.RemoveField(
            model_name='work',
            name='duration_hours',
        ),
    ]
