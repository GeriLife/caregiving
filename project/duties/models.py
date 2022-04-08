from django.db import models

class DutyType(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self) -> str:
        return self.name
