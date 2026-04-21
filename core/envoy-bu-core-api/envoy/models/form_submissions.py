from django.db import models

from envoy.models.customer import Customer
from envoy.models.form_templetes import CoreTemplate
from envoy.models.user import User

class CoreFormSubmission(models.Model):
    form = models.ForeignKey(CoreTemplate, on_delete=models.CASCADE, db_column='form_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id',null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id', null=True, blank=True)

    class Meta:
        db_table = "core_form_submissionss"