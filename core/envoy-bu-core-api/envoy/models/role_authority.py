from django.db import models
from .role import Role
from .action import Action


class RoleAuthority(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE,null=False,blank=False)
    action = models.ForeignKey(Action, on_delete=models.CASCADE,null=False,blank=False)

    class Meta:
        db_table = "core_role_authorities"

    def __str__(self):
        return f"{self.role_id.name} - {self.action_id.action}"
