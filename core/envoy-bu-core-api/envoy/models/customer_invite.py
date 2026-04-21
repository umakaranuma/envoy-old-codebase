from django.db import models
import uuid


class CustomerInvitation(models.Model):
    uid = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False, blank=False
    )
    name = models.CharField(max_length=80, blank=False)
    email = models.EmailField(max_length=254, blank=False)
    contact_no = models.IntegerField( null=True, blank=True)
    customer_id = models.IntegerField( blank=True, null=True)

    class Meta:
        db_table = "core_customer_invitations"

    def __str__(self):
        return self.name
