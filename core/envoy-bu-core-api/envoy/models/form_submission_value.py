from django.db import models
from envoy.models.form_submission import FormSubmission
from envoy.models.form_atribute import FormAttribute

class FormSubmissionValue(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    form_submission = models.ForeignKey(
        FormSubmission, on_delete=models.CASCADE, related_name="formsubmissions",null=False,blank=False
    )
    attribute = models.ForeignKey(
        FormAttribute, on_delete=models.CASCADE, related_name="formattributes",null=False,blank=False
    )
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "core_form_submission_values"

    def __str__(self):
        return f"Value for {self.attribute.name} in {self.form_submission.form.title}"
