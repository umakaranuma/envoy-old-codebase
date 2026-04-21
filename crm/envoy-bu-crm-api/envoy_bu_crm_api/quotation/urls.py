from django.urls import path
from envoy_bu_crm_api.quotation.Controllers import QuotationController
from envoy_bu_crm_api.quotation.Controllers import QuotationFormController
from envoy_bu_crm_api.quotation.Controllers import QuotationTriggerController
from envoy_bu_crm_api.quotation.Controllers import QuotationApprovalController


urlpatterns = [
    path("quotations", QuotationController.quotation, name='quotation'),#-----------------------------------
    path("quotations-status", QuotationController.quotation_status, name='quotation_status'),
            # path("quotations/", quotation, name='quotation'),
    path("quotations/<int:id>", QuotationController.single_quotation, name='single_quotation'),
    path("quotations/<int:id>/revert", QuotationController.revert_quotation, name='revert_quotation'),
    path("quotations/<int:id>/basic-info", QuotationController.quotation_basic_info, name='quotation_basic_info'),#----------------
    # path("opportunity-types", QuotationController.risk_type, name='risk_type'),
    path("service-providers", QuotationController.service_providers, name='service_providers'),#-------------------------
    path("quotations/<int:id>/service-providers", QuotationController.quotation_service_providers, name='quotation_service_providers'),#-------------
    path("quotations/<int:id>/service-providers/<int:service_provider_id>", QuotationController.single_service_provider, name='single_service_provider'),
    path("quotations/form-attributes", QuotationController.get_all_form_attributes, name='get_all_form_attributes'),
    path("service-provider/<int:id>", QuotationController.manage_service_provider, name='manage_service_provider'),
    path("service-provider/<int:id>", QuotationController.manage_service_provider, name='manage_service_provider'),
    path('service-providers-type', QuotationController.get_service_providers_by_category),
    


    path("quotations/vendor-responses", QuotationFormController.create_vendor_response, name='create_form_submission_value'),#-----------------
    path("quotations/related-fields", QuotationFormController.get_vendor_response_columns, name='get_quotation_table_columns'),#-------------------
    path("quotations/<int:id>/forms", QuotationFormController.get_all_quotation_form, name='get_all_quotation_form'),
    path("quotations/vendor-responses/<int:vendor_response_id>", QuotationFormController.single_vendor_response, name='single_vendor_response'),
    # path("quotations/vendor-quotation/<int:vendor_quotation_id>/delete", QuotationFormController.delete_quotation_form, name='delete_quotation_form'),
    path("quotations/vendor-quotation/<str:vendor_quotation_ids>/compare", QuotationFormController.get_form_compare, name='get_form_compare'), 
    # path("quotations/<int:id>/service-provider/<int::service_provider_id>/shortlist", QuotationFormController.shortlist_quotation_form, name='shortlist_quotation_form'),
    path("quotations/vendor-responses/<int:vendor_quotation_id>/shortlist", QuotationFormController.shortlist_quotation_form, name='shortlist_quotation_form'),#--------------------------
    path("quotations/<int:quotation_id>/vendor-responses", QuotationFormController.get_vendor_responses, name='get_vendor_responses'),#-------------------
    path("document-data-extract/<int:document_id>", QuotationFormController.extract_document_data, name='extract_document_data'),#-------------------
    # path("quotations/vendor/<int:id>", QuotationFormController.get_receive_quotation_form, name='get_receive_quotation_form'),
    path("quotations/<int:id>/shortlist-forms", QuotationFormController.get_shortlist_quotation_form, name='get_shortlist_quotation_form'),
    # path("vendor-quotation/<int:vendor_quotation_id>/update", QuotationFormController.update_quotation_form, name='update_quotation_form'),
# ---------------------------------------------------
    path("quotations/<int:id>/service-provider/<str:service_provider_id>/forms/draft", QuotationFormController.draft_quotation_form, name='draft_quotation_form'),
    path("quotations/<int:id>/service-provider/<str:service_provider_id>/forms/send", QuotationFormController.send_quotation_form, name='send_quotation_form'),
# -------------------------------------------------------
    # path("quotations/<int:quotation_id>/generated-documents", QuotationFormController.get_generate_document_forms, name='get_draft_generate_document_form'),
    # path("quotations/<int:id>/sent-forms", QuotationFormController.get_send_generate_document_form, name='get_send_generate_document_form'),

    path("quotations/<int:quotation_id>/generate-document", QuotationFormController.generate_document, name='generate_document'),
    path("generate-document/<int:doc_id>/update", QuotationFormController.update_generate_document, name="manage_generate_document"),
    path("generate-document/upload", QuotationFormController.upload_docs, name="upload_docs"),
    path("generate-document/<int:id>", QuotationFormController.generate_doc_single_view, name="generate_doc_single_view"),
    path("quotations/<str:ids>/generate-doc-version", QuotationFormController.get_doc_version, name="get_doc_version"),



    path("quotations/<int:quotation_id>/generate-document-preview", QuotationFormController.preview_document, name='preview_document'),
    path("quotations/<int:id>/comments", QuotationFormController.quotation_comments, name='quotation_comments'),
    path("quotations/<int:quotation_id>/preview-data", QuotationFormController.preview_data, name="get_form_generate"),
    path("quotations/<int:quotation_id>/generate-document-form/<int:vendor_quotation_id>", QuotationFormController.get_single_form_generate, name="get_generate_document"),
    path("quotations/<int:quotation_id>/generate-document-forms", QuotationFormController.get_all_form_generate, name="get_generate_document"),
    path("quotations/send-email",QuotationFormController.send_email_customers_quotation, name="quotation_send_email"),
    # path("quotations/send-email",QuotationFormController.quotation_send_email, name="quotation_send_email"),
    path("quotations/export-html-to-pdf/<int:send_quotation_id>", QuotationFormController.html_to_pdf_export, name="export-html-to-pdf"),
    path("quotations/generate-document/<int:vendor_quotation_id>/confirm", QuotationFormController.get_single_generate_document_confirm, name="get_single_generate_document_confirm"),

    path("send_approval", QuotationTriggerController.quotation_trigger, name="quotation_trigger"),#---------------------------

    path("quotation-approval", QuotationApprovalController.quotation_approval, name="quotation_approval"),
    path("quotation-approval/<int:id>", QuotationApprovalController.handle_quotation_approval, name="quotation_approval_changes"),
    path("quotation-approval/quotation-changes/<int:id>", QuotationApprovalController.quotation_changes, name="quotation_changes"),
    path("quotation-approval/send-email", QuotationApprovalController.quotation_approval_send_email, name="quotation_approval_send_email"),
    path("quotation-approval/entity/<int:id>", QuotationApprovalController.entity_check, name="entity_check"),
    path("quotations/<int:quotation_id>/risk-details",QuotationController.get_risk_details_by_quotation,name="quotation-risk-details"),
    path("quotations/<int:quotation_id>/risk-export",QuotationController.export_risks_for_quotation,name="export_risks_for_quotation"),
    path("quotations/download-exported-file/<str:file_name>", QuotationController.download_exported_file, name="download_exported_file"),
    path("quotations/<int:quotation_id>/risks", QuotationController.get_risks_by_quotation_id, name="get_risks_by_quotation_id"),

    path("all-notifications", QuotationController.all_notifications, name="all_notifications"),

    
    

]
