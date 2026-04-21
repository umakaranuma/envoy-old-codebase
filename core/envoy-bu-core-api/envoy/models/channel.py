from django.db import models


class Channel(models.Model):
    name = models.CharField(max_length=255,blank=False, null=False)
    description = models.TextField(blank=True, null=True) 

    class Meta:
        db_table = "core_channels"

    def __str__(self):
        return self.name
