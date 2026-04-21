from django.db import models

from envoy.models.contact import Contact
from envoy.models.contact_group import ContactGroup

class GroupContact(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(ContactGroup, on_delete=models.CASCADE,blank=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE,blank=False)

    class Meta:
        db_table = "core_group_contacts"

    def __str__(self):
        return f"{self.group.name} - {self.contact.name}"
