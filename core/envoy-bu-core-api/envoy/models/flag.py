from django.db import models

class Flag(models.Model):
    """Model representing flags with name, description, and color."""
    
    name = models.CharField(max_length=255, unique=True) 
    description = models.TextField(blank=True, null=True) 
    color = models.CharField(max_length=100, default="#eeeeef", blank=False, null=False)  

    class Meta:
        db_table = "core_flags"  

    def __str__(self):
        return f"{self.name} ({self.color})"
