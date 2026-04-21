from django.db import models

class CoreJobTitle(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=250, null=True, blank=True)

    created_by = models.ForeignKey(
        "envoy.User",
        on_delete=models.RESTRICT,
        related_name="job_title_created",
        null=True,
        blank=True,
        default=None
    )
    updated_by = models.ForeignKey(
        "envoy.User",
        on_delete=models.RESTRICT,
        related_name="job_title_updated", 
        null=True,
        blank=True,
        default=None
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = "core_job_titles"

    def __str__(self):
        return f"{self.title}"
