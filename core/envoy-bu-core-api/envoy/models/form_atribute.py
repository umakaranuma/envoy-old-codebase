from django.db import models

from envoy.models.form import Form

class FormAttribute(models.Model):
    TEXT = "TEXT"
    TYPE_CHOICES = [
        (TEXT, "Text"),
    ]

    id = models.AutoField(primary_key=True, unique=True,null=False,blank=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="attributes",null=False,blank=False)
    title = models.CharField(max_length=255,unique=True, blank=False, null=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,blank=False, null=False)
    attribute_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "core_form_attributes"

    def __str__(self):
        return f"{self.form.title} - {self.title}"