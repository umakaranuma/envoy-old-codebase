from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    title = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=80, null=True)
    last_name = models.CharField(max_length=80, null=True)
    display_name = models.CharField(max_length=80, blank=False)
    email = models.EmailField(max_length=254, blank=False)
    contact_no = models.CharField(max_length=80, null=True)
    picture = models.TextField(max_length=300, null=True)
    idp_user_id = models.CharField(max_length=255)
    role = models.ForeignKey("envoy.Role", on_delete=models.RESTRICT, blank=False, related_name="users")
    entity = models.ForeignKey(
        "envoy.Entity", on_delete=models.RESTRICT
    )
    status=models.ForeignKey("envoy.Status",on_delete=models.RESTRICT,blank=False,  null=True,related_name="user_status")
    code = models.CharField(max_length=100, unique=True,null=True)
    cover_pic = models.TextField(max_length=300, null=True)
    street_address = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    postal_code = models.CharField(max_length=20, null=True)
    county = models.CharField(max_length=100, null=True)

    @property
    def is_authenticated(self):
        return True

    class Meta:
        db_table = "core_users"

    @property
    def is_active(self):
        """Pretend is_active is always True."""
        return True

    def __str__(self):
        return self.first_name
