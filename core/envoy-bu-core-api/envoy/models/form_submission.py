from django.db import models

from envoy.models.form import Form
from envoy.models.form_atribute import FormAttribute

class FormSubmission(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="submissions",null=False,blank=False)
    # attribute = models.ForeignKey(FormAttribute, on_delete=models.CASCADE, related_name="submissions")
    # value = models.TextField()

    class Meta:
        db_table = "core_form_submissions"

    def __str__(self):
        return f"Submission for {self.form.title}"