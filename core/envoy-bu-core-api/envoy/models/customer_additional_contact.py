from django.db import models
from envoy.models.customer import Customer
from envoy.models.contact import Contact

class CustomerAdditionalContact(models.Model):
    id = models.AutoField(primary_key=True, unique=True,blank=False,null=False)
    title = models.CharField(max_length=200, blank=False, null=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="additional_contacts")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="customer_contacts")
    is_primary = models.BooleanField(default=False,blank=False, null=False)

    class Meta:
        db_table = "core_customer_contacts"

    def __str__(self):
        return f"{self.title} ({self.customer})"
