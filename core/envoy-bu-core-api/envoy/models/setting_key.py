from django.db import models

class SettingKey(models.Model):
    id = models.AutoField(primary_key=True, unique=True,blank=False,null=False)
    name = models.CharField(max_length=200, unique=True, blank=False, null=False)  # Unique
    description = models.CharField(max_length=200, blank=True, null=True)
    attribute_name = models.CharField(max_length=200, unique=True, blank=True, null=True)  # Unique

    class Meta:
        db_table = "core_setting_keys"

    def __str__(self):
        return self.name
