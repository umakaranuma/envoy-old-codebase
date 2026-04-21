from django.db import models

class crmf_update_history(models.Model):
    """
    Model for storing mapping update history
    """
    id = models.AutoField(primary_key=True)
    payment_id = models.IntegerField(null=True, blank=True)
    commission_setup_id = models.IntegerField(null=True, blank=True)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    version = models.CharField(max_length=255,null=True, blank=True) 
    uploaded_by = models.IntegerField(null=True, blank=True) # file_name will be stored here
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crmf_update_histories'
        verbose_name = 'Mapping Update'
        verbose_name_plural = 'Mapping Updates'

    def __str__(self):
        return self