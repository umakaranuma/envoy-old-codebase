from django.db import models

class TeamUser(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    team_id = models.BigIntegerField(blank=False, null=False)
    user_id = models.BigIntegerField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "core_team_users"

    def __str__(self):
        return f"TeamUser {self.id} - Team {self.team_id} - User {self.user_id}"    