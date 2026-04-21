from django.db import models
from envoy.models.flex_value import FlexValue

class Contact(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null= False)  # Required
    email = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    primary_contact = models.CharField(max_length=20, blank=False,null=False)  # Required
    secondary_contact = models.CharField(max_length=20, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    picture = models.TextField(blank=True, null=True)

    duplicated_contact = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="duplicates"
    )
    website_url = models.TextField(blank=True, null=True)
    show_in_list = models.BooleanField(default=True)


    class Meta:
        db_table = "core_contacts"

    
    def __str__(self):
        return self.name
