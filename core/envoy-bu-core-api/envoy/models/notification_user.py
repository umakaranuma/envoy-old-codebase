from django.db import models

class NotificationUser(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True )
    notification_id = models.BigIntegerField(null=True, blank=True)  
    user_id = models.BigIntegerField(null=True, blank=True)
    customer_id = models.BigIntegerField(null=True, blank=True)
    is_read = models.BooleanField(null=True, blank=True)
    is_clear = models.BooleanField(null=True, blank=True)
    read_at = models.DateTimeField(null=True, blank=True)


    class Meta:
        db_table = 'core_notification_users'
        verbose_name = 'Notification User'
        verbose_name_plural = 'Notification Users'

    def __str__(self):
        return f"NotificationUser user_id={self.user_id} customer_id={self.customer_id}"