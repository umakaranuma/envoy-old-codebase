from django.db import models
import uuid
from envoy.models import Role

class UserInvitation(models.Model):
    uid = models.UUIDField(
        default=uuid.uuid4, unique=True, primary_key=True, editable=False, blank=False
    )
    name = models.CharField(max_length=255, blank=False,null=False)
    email = models.EmailField(max_length=320, blank=False,null=False)
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, blank=False, default=1)

    class Meta:
        db_table = "core_user_invitations"

    def __str__(self):
        return self.name
