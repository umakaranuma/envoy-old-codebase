from django.db import models


class Form(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=255, unique=True,null=False,blank=False)
    description = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=100,default="crm")

    class Meta:
        db_table = "core_forms"

    def __str__(self):
        return self.title