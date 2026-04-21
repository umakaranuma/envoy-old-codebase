from django.db import models

class CoreOrganizationalNode(models.Model):
    code = models.CharField(max_length=100, unique=True)
    physical_address = models.CharField(max_length=250)
    email = models.EmailField(max_length=255)
    contact_no = models.CharField(max_length=80, null=True, blank=True)
    branch_name = models.CharField(max_length=100, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    name = models.CharField(max_length=80)
    parent_node = models.ForeignKey(
        "self",
        on_delete=models.RESTRICT,
        blank=True,   
        null=True     
    )
    level = models.ForeignKey(
        "envoy.CoreOrganizationLevel",
        on_delete=models.RESTRICT,
        blank=False,
        null=False,
        related_name="organization_nodes"
    )

    created_by = models.ForeignKey(
        "User", on_delete=models.RESTRICT, related_name="created_nodes",null=True,blank=True,default=None
    )
    updated_by = models.ForeignKey(
        "User", on_delete=models.RESTRICT, related_name="updated_nodes",null=True,blank=True,default=None
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_organizational_nodes"

    def __str__(self):
        return self.name
