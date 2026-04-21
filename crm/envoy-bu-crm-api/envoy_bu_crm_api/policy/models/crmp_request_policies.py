from django.db import models

class RequestPolicy(models.Model):
    policy_request_id = models.CharField(max_length=255,unique=True)
    policy_request_date = models.DateField(auto_now_add=True)
    status=models.ForeignKey("sales.Status",related_name="request_policy_status",on_delete=models.CASCADE,default=1)
    entity = models.ForeignKey("sales.Entity", related_name='request_entity', on_delete=models.CASCADE,default=1)
    policy_base=models.ForeignKey("policy.PolicyBase", related_name='policy_reqyst_base', on_delete=models.CASCADE)
    class Meta:
        db_table = "crmp_request_policies"

    def __str__(self):
        return f"Policy {self.policy_request_id} "






