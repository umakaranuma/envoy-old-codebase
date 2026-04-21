from django.db import models
from envoy.models import Entity
from envoy.models import Action


class Role(models.Model):
    id = models.AutoField(primary_key=True,unique=True)
    entity = models.ForeignKey(
        Entity, on_delete=models.RESTRICT, null=False, blank=False,
    )
    name = models.CharField(max_length=255,null=False,blank=False)
    description = models.CharField(max_length=320, null=True, blank=True)
    system_role = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "core_roles"


    def __str__(self):
        return self.name

    def get_permissions(self):
        return Action.objects.filter(roleauthority__role_id=self.id).select_related("roleauthority")



