from django.db import models

class ContactGroup(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255,null=False,blank=False)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "core_contact_groups"

    def __str__(self):
        return self.name
