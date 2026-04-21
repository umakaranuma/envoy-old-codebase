from django.db import models

class FormGroup(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=255, unique=True,blank=False, null=False)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "core_form_groups"

    def __str__(self):
        return self.title