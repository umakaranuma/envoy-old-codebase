import random
from django.db import models
from envoy.models.entity import Entity
from envoy.models.flex_value import FlexValue
from envoy.models.contact import Contact  

class Customer(models.Model):
    CORPORATE = "Corporate"
    PERSONAL = "Personal"
    ACCOUNT_TYPE_CHOICES = [(CORPORATE, "Corporate"), (PERSONAL, "Personal")]

    id = models.AutoField(primary_key=True, unique=True, blank=False,null=False)
    code = models.CharField(max_length=80, unique=True, blank=False,null=False)  # Required, Auto-generated 6-digit code
    type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES,blank=False,null=False)
    name = models.CharField(max_length=200,blank=False,null=False)
    logo = models.TextField(blank=True, null=True) 
    remarks = models.TextField(blank=True, null=True) 
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children"
    )
    primary_contact = models.ForeignKey(
        Contact, on_delete=models.RESTRICT, null=False, related_name="primary_accounts"
    )
    
    entity = models.ForeignKey(Entity, on_delete=models.RESTRICT, null=True, related_name="customers")

    idp_customer_id = models.CharField(max_length=255, null=True, blank=True)

    portal_id = models.IntegerField( null=True, blank=True,unique=True)
    is_enrolled = models.BooleanField(default=False, null=True, blank=True)
    class Meta:
        db_table = "core_customers"

    def save(self, *args, **kwargs):
        """ Generate a unique 6-digit code before saving"""
        if not self.code:
            self.code = self.generate_unique_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_code():
        """ Generates a unique 6-digit code"""
        while True:
            new_code = str(random.randint(100000, 999999))  # Generates a 6-digit number
            if not Customer.objects.filter(code=new_code).exists():
                return new_code


    def __str__(self):
        return self.name
