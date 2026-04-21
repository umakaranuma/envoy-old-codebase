from django.db import models
from envoy_bu_policy_api.policy.models.crmp_request_policies import RequestPolicy

class RequestPolicyDocument(models.Model):
    request_policy = models.ForeignKey(RequestPolicy, db_column='request_policy_id', blank=True, null=True, on_delete=models.CASCADE)
    type = models.CharField(max_length=255, blank=True, null=True)
    document_url = models.TextField(blank=True, null=True)
    document_name = models.CharField(max_length=255, blank=True, null=True)
    document_type = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data_analysis = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "crmp_request_policy_docs"

    def __str__(self):
        return f"{self.request_policy.policy_request_id}"

