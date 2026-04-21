from django.db import models
from django.contrib.auth import get_user_model

from envoy.models.setting_key import SettingKey

User = get_user_model()

class UserSetting(models.Model):
    id = models.AutoField(primary_key=True, unique=True,blank=False,null=False)
    setting_key = models.ForeignKey(SettingKey, on_delete=models.CASCADE, related_name="user_settings",blank=False,null=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="settings",blank=False,null=False)
    value = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "core_setting_users"

    def __str__(self):
        return f"{self.user.username} - {self.setting_key.name}"
