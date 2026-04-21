from django.db import models
from core_models.core_models import ServiceProvider
from .crmf_commision_setup import CommissionSetup

class CommissionSetupServiceProvider(models.Model):
    id = models.AutoField(primary_key=True)
    commission_setup = models.ForeignKey(CommissionSetup, on_delete=models.CASCADE, db_column='commission_setup_id')
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, db_column='service_provider_id')

    class Meta:
        db_table = 'crmf_commission_setup_service_providers'
        verbose_name = 'Commission Setup Service Provider'
        verbose_name_plural = 'Commission Setup Service Providers'