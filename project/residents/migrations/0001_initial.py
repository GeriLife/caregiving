# Generated by Django 4.0.4 on 2022-05-23 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Resident',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_initial', models.CharField(max_length=1)),
                ('on_hiatus', models.BooleanField(default=False)),
            ],
        ),
    ]
