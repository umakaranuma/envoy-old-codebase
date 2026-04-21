from django.db import models

class LoginHistory(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True,)
    user_id = models.BigIntegerField(null=True, blank=True)
    customer_id = models.BigIntegerField(null=True, blank=True)
    login_time = models.TimeField(null=True, blank=True)
    device = models.TextField(null=True, blank=True)
    ip = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    module = models.CharField(max_length=255, null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'core_login_histories'
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'

    def __str__(self):
        return f"LoginHistory {self.id}"