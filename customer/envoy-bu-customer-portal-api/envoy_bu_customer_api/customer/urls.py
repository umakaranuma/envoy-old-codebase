from django.urls import path
from envoy_bu_customer_api.customer.controllers import (
   customer_controller,
)
from envoy_bu_customer_api.customer.controllers import common_controller
from envoy_bu_customer_api.customer.controllers.common_controller import *
from envoy_bu_customer_api.customer.controllers.form_controller import *
from envoy_bu_customer_api.customer.controllers.policy_controller import *
from envoy_bu_customer_api.customer.controllers.claim_controller import *
from envoy_bu_customer_api.customer.controllers.product_controller import *


urlpatterns = [
    #Add the common urls from other portals in here
    path('insurer-product-by-type', get_vendor_products_by_risk_type, name="get_vendor_products_by_risk_type"), 
    path("opportunity-types", opportunity_type, name='opportunity_type'),
    path('vendor-products', get_vendor_products_by_risk_type, name='get_vendor_products_by_risk_type'),
    path('templates/<int:id>', template_detail, name='get-template'),
    # General Ledger URLs
    path("customer/verify-invitation", customer_controller.accept_invitations, name="accept_invitations"),
    path('customer/quotations', customer_controller.quotations, name='quotations'),
    path('customer/quotations/<int:quotation_id>/send-quotations', customer_controller.get_generate_document_forms, name='get_generate_document_forms'),
    path('customer/send-quotations/<int:send_quotation_id>', customer_controller.get_single_generate_document_forms, name='get_single_generate_document_forms'),
    path('customer/send-quotations/<int:vendor_quotation_id>/confirm', customer_controller.get_single_generate_document_confirm, name='get_single_generate_document_confirm'),
    path('customer/quotations/<int:quotation_id>/details', customer_controller.quotations_details, name='quotations_details'),
    path('customer/policies', customer_controller.get_all_issued_policies, name='get_all_issued_policies'),
    # path('customer/policies', customer_controller.get_policy_details, name='get_policy_details'),
    path('customer/policies/<int:id>', customer_controller.policy_details_single, name='policy_details_single'),
    # path('customer/claims', customer_controller.claims_details, name='claims_details'),
    # path('customer/claims/<int:id>', customer_controller.get_claims_detail, name='get_claims_detail'),
    path('customer/quotations/<int:quotation_id>', customer_controller.quotations_details, name='quotations_details'),
    # path('customer/policies', customer_controller.get_policy_details, name='get_policy_details'),
    path('customer/policies/<int:policy_id>', customer_controller.policy_details_single, name='policy_details_single'),
    # path('customer/claims', customer_controller.claims_details, name='claims_details'),
    # path('customer/claims/<int:id>', customer_controller.get_claims_detail, name='get_claims_detail'),
    path('customer/all-notifications', customer_controller.all_notifications, name='all_notifications'),
    # path('customer/read-notifications', customer_controller.read_notifications, name='read_notifications'),
    # path('customer/unread-notifications', customer_controller.unread_notifications, name='unread_notifications'),
    path('customer/read-notifications/<ids>', customer_controller.change_notifications_status, name='change_notifications_status'),
    path('customer/notifications/<int:id>', customer_controller.single_notifications, name='single_notifications'),
    path("customer/<int:risk_type_id>/template", customer_controller.get_template_by_risk_type_and_type, name="get_claim_template_by_risk_type"),

    # path('customer/profile/info', customer_controller.single_notifications, name='single_notifications'),
    path('customer/profile/personal-info', customer_controller.personal_info, name='personal_info'),
    path('customer/profile/contact-email', customer_controller.contact_email, name='contact_email'),
    path('customer/policy/<int:id>/invoices', customer_controller.policy_invoices, name='policy_invoices'), 
    path('customer/policy-settlement', customer_controller.policy_settlement, name='policy_settlement'), #need to do
    path('customer/policy/<int:id>/policy-settlement', customer_controller.policy_based_settlement, name='policy_based_settlement'), #need to do
    path('customer/policy/<int:id>/bankinfo', customer_controller.policy_bankinfo, name='policy_bankinfo'), 
    path('customer/login-history/<int:id>', customer_controller.login_history_details, name='login_history_details'), 
    path('customer/login-history', customer_controller.login_history, name='login_history'), 
    path('customer/notification-settings', customer_controller.notification_settings, name='notification_settings'), 




    # --------------------------------------------------------------------------------------------------
    path("customer/form-submission", submit_generic_form, name="submit_generic_form"),
    path("customer/create_request", bulk_submit_customer_requests, name="create_request"),
    path("customer/requests", list_customer_requests, name="list_customer_requests"),
    path("customer/policy-holder", create_policy_holder, name="create_policy_holder"),
    path("customer/policy-holder/<int:request_id>", get_policy_holder_by_request, name="get_policy_holder_by_request"),


    path("customer/coverage-types", get_coverage_types, name="get_coverage_types"),

    path("customer/me", customer_controller.get_myself, name="get_myself"),

    # path("customer/vendor-product-documents", get_product_documents_by_vendor, name="get_product_documents_by_vendor"),
    path("customer/request-documents", store_customer_request_documents, name="store_customer_request_documents"),
    # path("customer/request-documents/<int:request_id>", get_customer_request_documents),
    path("customer/vendor-product-documents/<int:request_id>", get_product_documents_with_values),

    path("customer/risk-document", store_customer_risk_document, name="store-risk-document"),
    path("customer/risk-document/<int:request_id>", get_customer_risk_documents, name="get-risk-documents"),


    path("customer/request-coverage", store_customer_request_policy_details, name="store_customer_request_policy_details"),
    path("customer/request-coverage/<int:request_id>", get_customer_request_policy_details, name="get_customer_request_policy_details"),

    path("customer/request-payment-details", store_customer_request_payment_details),
    path("customer/request-payment-details/<int:request_id>", get_customer_request_payment_details),
    path(
    "customer/terms-conditions/<int:customer_request_id>",
    get_entity_documents_by_customer_request,
    name="get_entity_documents_by_customer_request"
    ),


    # path("customer/vendor-product-coverages", get_product_coverages_by_vendor, name="get_product_coverages_by_vendor"),
    # path("customer/request-coverages", store_customer_request_coverages, name="store_customer_request_coverages"),
    # path("customer/request-coverages/<int:request_id>", get_customer_request_coverages, name="get_customer_request_coverages"),
    path("customer/request-details/<int:request_id>", get_customer_request_full_details, name="get_customer_request_full_details"),
    path("customer/finalize-request/<int:request_id>", finalize_customer_request, name="finalize_customer_request"),


    path("customer/<int:policy_id>/policy-info", get_template_by_policy),
    path("customer/issued-policies", get_customer_policies, name="get_policies_by_customer"),
    path("customer/claims", claim, name="create-claim"),
    path("customer/claims/<int:claim_id>", claim_details, name="get-claim-by-id"),
    path("customer/claims/<int:claim_id>/evaluation-info", claim_evaluation_details, name="create-claim-incident-info"),
    path("customer/excel-exporter", export_risks_to_excel, name="export_risks_to_excel"),
    path("customer/products-filters", get_vendor_products_and_groups_by_risk_type),
    path("customer/insurer-products/<int:id>/documents-enhanced", product_documents_enhanced, name="product_documents_enhanced"),
    path("customer/quotations/<int:quotation_id>/vendor-responses", customer_controller.get_vendor_responses, name='get_vendor_responses'),
    path("customer/policy-base/<int:policy_base_id>/risk-types", get_risk_types_by_policy_base, name="get_risk_types_by_policy_base"),
    path("customer/risk-values/<int:risk_type_id>", get_risks_by_type_and_customer, name="get_risk_details_by_lead"),

  
]