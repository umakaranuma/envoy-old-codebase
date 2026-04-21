from django.db import models

class NotificationType(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=200, default='#6B7280')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_notification_types'
        verbose_name = 'Notification Type'
        verbose_name_plural = 'Notification Types'

    def __str__(self):
        return self.name