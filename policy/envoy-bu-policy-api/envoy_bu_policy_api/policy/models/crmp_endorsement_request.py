from django.db import models
from envoy_bu_policy_api.policy.models.crmp_issued_policies import IssuedPolicy

class EndorsementType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
            db_table = "crmp_endorsement_types"
class ReasonCode(models.Model):
    code = models.CharField(max_length=50)
    description = models.TextField()
    endorsement_type = models.ForeignKey(EndorsementType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.code} - {self.description}"
    
    class Meta:
        db_table = "crmp_endorsement_reason_codes"
    
class EndorsementRequest(models.Model):
    endorsement_request = models.CharField(max_length=255)
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2,blank=True,null=True)
    entity = models.ForeignKey("core_models.Entity", related_name='en_req_entity', on_delete=models.CASCADE,default=1)
    endorsement_type = models.ForeignKey(EndorsementType, on_delete=models.CASCADE,default=2)
    reason_code = models.ForeignKey(ReasonCode, on_delete=models.CASCADE,default=1)
    cover_value = models.DecimalField(max_digits=12, decimal_places=2,default=0)
    credit_period = models.IntegerField(blank=True, null=True, help_text="Credit period in days")
    mail_status = models.BooleanField(default=False)
    issued_policy = models.ForeignKey(IssuedPolicy, related_name="endorsement_requests", on_delete=models.CASCADE,default=1)
    def __str__(self):
        return f"Endorsement Request {self.endorsement_request_id}"
        
    class Meta:
            db_table = "crmp_endorsement_requests"
            

# class ReasonCodes(models.Model):
#     code = models.CharField(max_length=50)
#     description = models.TextField()
#     endorsement_type = models.ForeignKey(EndorsementType, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"{self.code} - {self.description}"
    
#     class Meta:
#         db_table = "crmp_endorsement_reason_codes"