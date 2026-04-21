from django.db import models
from django.utils import timezone

class ServiceProvider(models.Model):
    user = models.ForeignKey('envoy.User', on_delete=models.CASCADE, related_name='service_provider')
    name = models.CharField(max_length=255)
    logo = models.TextField(blank=True, null=True) 
    address = models.TextField()
    contact_no = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    fax_no = models.CharField(max_length=20, blank=True, null=True)

    # Audit fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.ForeignKey("envoy.Status",on_delete=models.CASCADE,blank=True,  null=True,related_name="service_provider_status")
    description = models.CharField(max_length=200, null=True)
    created_by = models.ForeignKey(
        'envoy.User',
        on_delete=models.SET_NULL,
        related_name='service_provider_created',
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        'envoy.User',
        on_delete=models.SET_NULL,
        related_name='service_provider_updated',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "core_service_providers"
