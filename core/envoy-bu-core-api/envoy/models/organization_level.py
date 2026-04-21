from django.db import models
class CoreOrganizationLevel(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=200, unique=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    level_order = models.PositiveIntegerField()
    created_by = models.ForeignKey(
        "User", on_delete=models.RESTRICT, related_name="created_levels",null=True,blank=True,default=None
    )
    updated_by = models.ForeignKey(
        "User", on_delete=models.RESTRICT, related_name="updated_levels",null=True,blank=True,default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "core_organization_levels"