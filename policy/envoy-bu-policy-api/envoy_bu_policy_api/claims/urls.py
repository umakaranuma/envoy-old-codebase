from django.urls import path
from envoy_bu_policy_api.claims.controllers.claim_controller import *

urlpatterns = [
   path("claims", claim, name="create-claim"),
   path("claims/<int:claim_id>", claim_details, name="get-claim-by-id"),
   path("claims/<int:claim_id>/evaluation-form", get_template_by_claim, name="get-claim-evaluation-form"),
   path("claims/<int:claim_id>/evaluation", submit_claim_evaluation, name="create-claim-evaluation"),
   path("claims/<int:claim_id>/evaluation-info", claim_evaluation_details, name="create-claim-incident-info"),
   path("claims/customers", get_all_customers, name="claim-customer"),
   path("claims/send-email", send_claim_emails, name="claim-customer-by-id"),
   path("claims/<int:policy_id>/policy-info", get_template_by_policy),
   path("claims/customers/<int:customer_id>/policies", get_customer_policies, name="claim-policies-by-customer"),
   path("claims/change-status", bulk_update_claim_status, name="bulk-change-claim-status"),
]