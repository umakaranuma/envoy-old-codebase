from django.db import models

class Country(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = "core_countries"
        ordering = ['name']

    def __str__(self):
        return self.name
