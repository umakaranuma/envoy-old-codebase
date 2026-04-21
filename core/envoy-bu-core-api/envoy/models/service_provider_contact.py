from django.db import models
from envoy.models.service_provider import ServiceProvider
from envoy.models.contact import Contact

class ServiceProviderContact(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('general', 'General'),
    ]
    
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=200, blank=False, null=False)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="sp_contacts")
    is_primary = models.BooleanField(default=False,blank=False, null=False)
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES, default='general')
    name = models.CharField(max_length=255, blank=False)  # Required
    email = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    primary_contact = models.CharField(max_length=20, blank=False,null=True)
    remarks = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "core_service_provider_contacts"

    def __str__(self):
        return f"{self.title} ({self.service_provider})"
