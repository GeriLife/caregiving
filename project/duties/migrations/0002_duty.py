# Generated by Django 4.0.3 on 2022-04-08 09:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('caregivers', '0001_initial'),
        ('homes', '0001_initial'),
        ('duties', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Duty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('duration', models.PositiveIntegerField()),
                ('caregiver_role', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='caregivers.caregiverrole')),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='duties_performed', to='homes.home')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='+', to='duties.dutytype')),
            ],
        ),
    ]
