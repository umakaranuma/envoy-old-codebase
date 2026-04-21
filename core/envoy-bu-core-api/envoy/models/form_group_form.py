from django.db import models

from envoy.models.form import Form
from envoy.models.form_group import FormGroup

class FormGroupForm(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    group = models.ForeignKey(FormGroup, on_delete=models.CASCADE, related_name="forms",null=False,blank=False)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="groups",null=False,blank=False)

    class Meta:
        db_table = "core_form_group_forms"

    def __str__(self):
        return f"{self.group.title} - {self.form.title}"