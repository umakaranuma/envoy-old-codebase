from django.urls import path
from envoy_bu_crm_api.policy.controllers import issued_policy_controller
from envoy_bu_crm_api.policy.controllers import request_policy_controller
from envoy_bu_crm_api.policy.controllers import endorsement_request_controller
from envoy_bu_crm_api.policy.controllers import endorsement_details_controller
from envoy_bu_crm_api.policy.controllers import (
    confirmed_leads_with_qualified_stage_controller,
)
from envoy_bu_crm_api.policy.controllers import policy_approval_controller
from envoy_bu_crm_api.policy.controllers.policy_list_data import (
    request_policy_insurers,
    request_policy_risk_types,
    request_policy_coverage_types,
    request_policy_statuses,
    request_types,
    payment_plans,
    request_reason_codes_by_type,
    request_endorsement_types,
)
from envoy_bu_crm_api.policy.controllers import payment_controller, invoice_controller
from envoy_bu_crm_api.policy.controllers.notes_controller import (
    policy_note_list,
    policy_note_detail,
    policy_note_create,
)
from envoy_bu_crm_api.policy.controllers import crmp_doc_upload_controller
from envoy_bu_crm_api.policy.controllers import (
    policy_risk_info_controller,
    request_policy_risk_info_controller,
)
# from envoy_bu_crm_api.claims.controllers.claim_controller import get_form_by_type

urlpatterns = [
    path(
        "issued-policy",
        issued_policy_controller.issued_policy_handler,
        name="issued_policy",
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
]
