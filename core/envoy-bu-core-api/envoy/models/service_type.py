from django.db import models

class CoreServiceType(models.Model):
    title = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    standardfee = models.DecimalField(
    max_digits=20, decimal_places=2, null=True, blank=True, default=0.00
    )
    created_by = models.ForeignKey(
        "envoy.User",
        on_delete=models.RESTRICT,
        related_name="service_type_created",
        null=True,
        blank=True,
        default=None
    )
    updated_by = models.ForeignKey(
        "envoy.User",
        on_delete=models.RESTRICT,
        related_name="service_type_updated", 
        null=True,
        blank=True,
        default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_service_types"

    def __str__(self):
        return f"{self.title}"