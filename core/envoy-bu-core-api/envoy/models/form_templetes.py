from django.db import models


class CoreTemplate(models.Model):
    TYPE_CHOICES = [
        ('single_form', 'Single Form'),
        ('multi_step_form', 'Multi Step Form'),
    ]
    title = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "core_templates"