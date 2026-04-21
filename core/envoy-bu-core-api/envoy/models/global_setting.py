from django.db import models

from envoy.models.setting_key import SettingKey

class GlobalSetting(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    setting_key = models.ForeignKey(SettingKey, on_delete=models.CASCADE, related_name="global_settings")
    value = models.TextField( blank=True, null=True)

    class Meta:
        db_table = "core_setting_global"

    def __str__(self):
        return f"{self.setting_key.name} - {self.value}"
