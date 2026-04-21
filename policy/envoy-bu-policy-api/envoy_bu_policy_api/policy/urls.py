from django.urls import path
from envoy_bu_policy_api.policy.controllers import issued_policy_controller
from envoy_bu_policy_api.policy.controllers import request_policy_controller
from envoy_bu_policy_api.policy.controllers import endorsement_request_controller
from envoy_bu_policy_api.policy.controllers import endorsement_details_controller
from envoy_bu_policy_api.policy.controllers import (
    confirmed_leads_with_qualified_stage_controller,
)
from envoy_bu_policy_api.policy.controllers import policy_approval_controller
from envoy_bu_policy_api.policy.controllers.policy_list_data import (
    request_policy_insurers,
    request_policy_risk_types,
    request_policy_coverage_types,
    request_policy_statuses,
    request_types,
    payment_plans,
    request_reason_codes_by_type,
    request_endorsement_types,
)
from envoy_bu_policy_api.policy.controllers import  invoice_controller
from envoy_bu_policy_api.policy.controllers.notes_controller import (
    policy_note_list,
    policy_note_detail,
    policy_note_create,
)
from envoy_bu_policy_api.policy.controllers import crmp_doc_upload_controller
from envoy_bu_policy_api.policy.controllers import (
    policy_risk_info_controller,
    request_policy_risk_info_controller,
)
# from envoy_bu_policy_api.claims.controllers.claim_controller import get_form_by_type
from envoy_bu_policy_api.finance.controllers import payment_controller
from envoy_bu_policy_api.policy.controllers.risk_management_controlller import *

urlpatterns = [
    path(
        "issued-policy",
        issued_policy_controller.issued_policy_handler,
        name="issued_policy",
    ),
    path(
        "issued-policies/all",
        issued_policy_controller.get_all_issued_policies_simple,
        name="get_all_issued_policies_simple",
    ),
    path(
        "policy-requests/<int:request_id>/issued-policy",
        issued_policy_controller.issued_policy_create_from_request,
        name="issued_policy",
    ),
    path(
        "policy-request",
        request_policy_controller.request_policy_list,
        name="request_policy",
    ),
    path(
        "policy-approval",
        request_policy_controller.policy_trigger,
        name="send_approval",
    ),
    path(
        "issued-policy/<int:policy_id>",
        issued_policy_controller.issued_policy_detail,
        name="get_issued_policy",
    ),
    path(
        "issued-policy-renewal/<int:policy_id>",
        issued_policy_controller.issued_policy_renewal,
        name="renewal_issued_policy_put",
    ),
    path(
        "issued-policy/<int:policy_id>/issued-policy-renewal",
        issued_policy_controller.get_all_inheritance_history,
        name="renewal_issued_policy_get",
    ),
    path(
        "policy-request/<int:policy_id>",
        request_policy_controller.request_policy_detail,
        name="get_request_policy",
    ),
    path(
        "draft-policies",
        request_policy_controller.draft_policies_list,
        name="draft_policies_list",
    ),
    path(
        "draft-policies/<int:policy_base_id>",
        request_policy_controller.draft_policy_detail,
        name="draft_policy_detail",
    ),
    path(
        "draft-policies/<int:policy_base_id>/delete",
        request_policy_controller.delete_draft_policy,
        name="delete_draft_policy",
    ),
    path(
        "endorsement-requests",
        endorsement_request_controller.endorsement_request_list,
        name="endorsement_request_list",
    ),
    path(
        "issued-policy/<int:policy_id>/endorsement-requests",
        endorsement_request_controller.endorsement_request_list_by_policy,
        name="endorsement_request_list_by_policy",
    ),
    path(
        "endorsement-requests/<int:request_id>",
        endorsement_request_controller.endorsement_request_detail,
        name="endorsement_request_detail",
    ),
    path(
        "endorsement-details",
        endorsement_details_controller.endorsement_list,
        name="endorsement_list",
    ),
    path(
        "issued-policy/<int:policy_id>/endorsement-details",
        endorsement_details_controller.endorsement_list,
        name="endorsement_list",
    ),
    path(
        "endorsement-details/<int:endorsement_id>",
        endorsement_details_controller.endorsement_detail,
        name="endorsement_detail",
    ),
    path(
        "customers/<customer_id>/confirmed-qualified-leads",
        confirmed_leads_with_qualified_stage_controller.get_confirmed_leads_with_qualified_stage,
        name="request_policy",
    ),
    path(
        "policy-request-approvals",
        policy_approval_controller.get_all_policy_approvals,
        name="get_all_request_policies",
    ),
    path(
        "policy-request-approvals/<int:policy_id>",
        policy_approval_controller.get_all_policy_approvals,
        name="get_request_policies",
    ),
    path(
        "send-approval",
        policy_approval_controller.send_approval_email,
        name="send_approval_email",
    ),
    path(
        "send-endorsement-request",
        endorsement_request_controller.send_endorsement_email,
        name="send_approval_request",
    ),
    path("policy-request/<int:policy_id>/fetch-messages", endorsement_request_controller.policy_sync_conversations),
    path("policy-endorsement/<int:endorsement_id>/chat", request_policy_controller.endorsement_chat_messages, name="endorsement_chat_messages"),
    path(
        "payments",
        payment_controller.payment_list,
        name="payment_list",
    ),
    path(
        "issued-policy/<int:policy_id>/payments",
        payment_controller.payment_list,
        name="payment_list",
    ),
    path("insurers", request_policy_insurers),
    path("risk-types", request_policy_risk_types),
    path("coverage-types", request_policy_coverage_types),
    path("statuses", request_policy_statuses),
    path("request-types", request_types),
    path("payment-plans", payment_plans),
    path("issued-policy/<int:policy_id>/notes", policy_note_list),
    path("issued-policy-notes/<int:note_id>", policy_note_detail),
    path("issued-policy-notes", policy_note_create),
    path("endorsement-types", request_endorsement_types, name="endorsement-types"),
    path(
        "endorsement-types/<int:type_id>/reason-codes",
        request_reason_codes_by_type,
        name="reason-codes-by-type",
    ),
    path(
        "issued-policy/<str:policy_id>/form-configs/<str:config_id>/info",
        policy_risk_info_controller.get_form_config_info,
        name="policy-form-config-info",
    ),
    path(
        "issued-policy/<str:policy_id>/form-configs/<str:config_id>/info/<str:info_id>",
        policy_risk_info_controller.get_single_form_config_info,
        name="single-policy-form-config-info",
    ),
    path(
        "issued-policy/<str:policy_id>/opportunity-configs",
        policy_risk_info_controller.clone_oppo_submissions,
        name="single-policy-form-config-info",
    ),
    path(
        "request-policy/<str:policy_request_id>/opportunity-configs",
        request_policy_risk_info_controller.clone_oppo_submissions,
        name="single-policy-form-config-info",
    ),
    path(
        "crm-opportunity-configs/<str:config_id>/info",
        request_policy_risk_info_controller.getAll_existing_risk,
        name="single-policy-form-config-info",
    ),
    path(
        "request-policy/<str:policy_request_id>/form-configs/<str:config_id>/info",
        request_policy_risk_info_controller.get_form_config_info,
        name="policy-form-config-info",
    ),
    path(
        "request-policy/<str:policy_request_id>/form-configs/<str:config_id>/info/<str:info_id>",
        request_policy_risk_info_controller.get_single_form_config_info,
        name="single-policy-form-config-info",
    ),
    path(
        "issued-policy/<int:policy_id>/documents",
        crmp_doc_upload_controller.policy_document_list,
        name="issued-policy-documents-list",
    ),
    # Filter by category
    path(
        "docs/<str:category>",
        crmp_doc_upload_controller.documents_by_category,
        name="documents-by-category",
    ),
    # Single‐doc create/update/delete under issued-policy
    path(
        "issued-policy/documents",
        crmp_doc_upload_controller.policy_document_create,
        name="issued-policy-document-create",
    ),
    # Bulk upload under issued-policy
    path(
        "issued-policy/documents/bulk-create",
        crmp_doc_upload_controller.policy_documents_bulk_create,
        name="issued-policy-documents-bulk-create",
    ),
    path(
        "issued-policy/<int:policy_id>/documents/<str:category>",
        crmp_doc_upload_controller.documents_by_policy_and_category,
        name="documents-by-policy-and-category",
    ),
    path(
        "issued-policy/<int:issued_policy_id>/category-documents",
        crmp_doc_upload_controller.documents_by_issued_policy_id,
        name="documents-by-issued-policy-id",
    ),
    path(
        "request-policy/documents",
        crmp_doc_upload_controller.request_policy_document_create,
        name="request-request-policy-document-create",
    ),
    path(
        "<str:policy_type>-policy/documents/<int:document_id>",
        crmp_doc_upload_controller.request_policy_document,
        name="request-request-policy-document-delete",
    ),
    path(
        "request-policy/documents/bulk-create",
        crmp_doc_upload_controller.request_policy_documents_bulk_create,
        name="request-request-policy-documents-bulk-create",
    ),
    path(
        "request-policy/<int:request_policy_id>/documents/<str:category>",
        crmp_doc_upload_controller.request_documents_by_policy_and_category,
        name="documents-by-request-policy-and-category",
    ),
    path(
        "issued-policy/<int:policy_id>/invoices",
        invoice_controller.invoice_list,
        name="payment_list",
    ),
    # path("policy/forms-by-type", get_form_by_type, name="get_form_by_type"),
    path(
        "policy/opportunities-policy-details",
        issued_policy_controller.get_opportunities_with_policy_details,
        name="get_opportunities_with_policy_details",
    ),
    path(
        "policy/qualified-opportunities",
        issued_policy_controller.get_qualified_opportunities,
        name="get_qualified_opportunities",
    ),
    path(
        "policy/approved-policies",
        issued_policy_controller.get_approved_policies_with_details,
        name="get_approved_policies_with_details",
    ),

    # Notification List
    path("all-notifications",issued_policy_controller.all_notifications,name="all_notifications"),

    


#----------------------------
# by uma
#----------------------------
    path("policy/risk-form/<int:risk_type_id>", get_risk_form_template_detail, name="get-risk-form-template-detail"),
    path("policy/risk-detail/<int:risk_detail_id>", get_risk_detail_template_with_values),
    path("policy/risk-detail/<int:risk_detail_id>/versions", get_risk_detail_versions),
    path("policy/risk/<int:risk_id>/submission-values", get_risk_submission_values),
    path("policy/risk/<int:risk_type_id>", get_risks_by_type_and_customer, name="get_risk_details_by_lead"), #policy/risk-details?lead_id=1
    # path("policy/risk-update/<int:risk_id>", update_risk_detail, name="update_risk_detail"),
    path("policy/risk", risk, name="create_risk"),
    path("policy/lead-by-customer/<int:customer_id>", get_opportunities_by_customer, name="get_opportunities_by_customer"),
    path("policy/opportunities/<int:opportunity_id>/risk-types", get_risk_types_by_opportunity, name="get_risk_types_by_opportunity"),
    path("policy/policy-base/<int:policy_base_id>/risk-types", get_risk_types_by_policy_base, name="get_risk_types_by_policy_base"),
    path("policy/risk-details", get_risk_details_by_lead_and_types, name="get_risk_details_by_lead_and_types"), #policy/risk-details?lead_id=1&risk_type_ids=1,2
    path("policy/products", get_vendor_products_by_risk_type),
    path("policy-base/<int:policy_base_id>/product-documents", issued_policy_controller.policy_product_documents, name="policy_product_documents"),
    path("policy-base/<int:policy_base_id>/export-risks", issued_policy_controller.export_risks_for_policy_base, name="export_risks_for_policy_base"),
    path("policy/risk-export", export_risks_by_type_ids, name="export_risks_by_type_ids"),
    path("policy/process-risk-excel", process_uploaded_risk_excel, name="process_uploaded_risk_excel"),

#----------------------------------Data Analyzer------------------------------------
    path("policy/request-policy/<int:request_policy_id>/download-docs", request_policy_controller.request_policy_download_docs, name="request_policy_download_docs"),
    path("policy/request-policy/<int:request_policy_id>/data-analysis", request_policy_controller.request_policy_data_analysis, name="request_policy_data_analysis"),

]


