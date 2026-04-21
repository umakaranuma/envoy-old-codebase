from django.db import models


class CustomerSettings(models.Model):
    id = models.BigAutoField(primary_key=True, unique=True,)
    setting_key = models.BigIntegerField(blank=True,null=True)
    customer_id = models.BigIntegerField(blank=True,null=True)  # or models.ForeignKey(Customer, ...) if you have a Customer model
    value = models.TextField(null=True, blank=True)  # <-- long text


    class Meta:
        db_table = "cus_settings"


    def __str__(self):
        return f"{self.customer_id} - {self.setting_key.name}: {self.value}"
