from django.db import models

class Notification(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    customer_id = models.BigIntegerField(null=True, blank=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    type_id = models.IntegerField( blank=True, null=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return self.title or self.type_id