from django.db import models

class Team(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    leader_id = models.BigIntegerField(blank=True, null=True)
    manager_id = models.BigIntegerField(blank=True, null=True)
    detector_id = models.BigIntegerField(blank=True, null=True)
    status = models.ForeignKey("envoy.Status", on_delete=models.RESTRICT, blank=True, null=True, related_name="team_status")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "core_teams"

    def __str__(self):
        return self.name
