"""
URL configuration for envoy project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from envoy.controllers.account_additional_controller import *
from envoy.controllers.approval_controller import *
from envoy.controllers.roles_controller import (
    get_roles,
    role_detail,
    count_role_privileges,
    count_role_users,
    get_actions,
    role_permissions,
)
from envoy.controllers.user_controller import (
    create_invitations,
    accept_invitations,
    get_users,
    user_detail,
)
from envoy.controllers.invitation_controller import get_user_invitations
from envoy.controllers.invitation_controller import (
    resend_user_invitation,
    cancel_invitation,
    cancel_invitation_by_email,
)
from envoy.controllers.contact_controller import (
    get_contacts,
    contact_detail,
    get_contact_interaction,
    get_contact_interactions,get_contact_ids,
    merge_contact_api,
get_contact_relations,
)

from envoy.controllers.common_controller import (
    channels,          
    channel_detail,    
    get_currencies,
    get_currency_by_id, 
    all_notifications,
    notification_unread_count,
    notification_stream,
    read_notifications,
    get_notification_detail,
)
from envoy.controllers.user_controller import create_invitations,accept_invitations
from envoy.controllers.group_controller import *
from envoy.controllers.account_controller import *
from envoy.controllers.form_controller import *
from .controllers.settings_controller import *
from .controllers.common_controller import *
from .controllers.note_controller import *
from .controllers.product_controller import *
from .controllers.product_item_controller import (
    product_item_view,
    product_item_detail,
)
from .controllers.documents_controller import *
from .controllers.flex_field_controller import *
from .controllers.reason_controller import *
from .controllers.entity_controller import *
from .controllers.form_template_controller import *
from .controllers.form_template_submission_controller import *
from .controllers.job_title_controller import*
from .controllers.service_type_controller import *
from .controllers.organization_level_controller import *
from .controllers.organizational_node_controller import *
from .controllers.team_controller import *
from .controllers.sales_target_controller import *
from .controllers.user_bank_detail_controller import*
from .controllers.team_user_controller import*
from .controllers.service_provider_controller import*
from .controllers.service_provider_contact_controller import *
from .controllers.chat_controller import *
from .controllers.chatmail_controller import (
    send_chatmail_message,
    get_chatmail_messages,
    get_chatmail_conversations,
    sync_gmail_thread,
    mark_conversation_seen,
    download_attachment,
    get_attachment_info,
    gmail_push_webhook,
    gmail_webhook,
)
from envoy.controllers import mail_controller as ctl
from envoy.controllers.export_controller import export_receipts_excel
urlpatterns = [
    path("api/login", include("accounts.urls")),
    path("api/permissions", get_actions),
    path("api/roles", get_roles, name="get_roles"),
    path("api/roles/<int:role_id>", role_detail, name="role_detail"),
    path("api/roles/privileges", count_role_privileges, name="count_role_privileges"),
    path("api/roles/assigned-users", count_role_users, name="count_role_users"),
    path("api/roles/<int:role_id>/permissions", role_permissions, name="get_role_permissions"),
    path("api/groups", get_groups),
    path("api/groups/<int:id>", get_single_group),
    path("api/groups/<int:id>/contacts", get_group_contact),
    path("api/groups/<int:id>/assignable-contacts" , get_assignable_contacts),
    path("api/users/invite", create_invitations, name="get_invitations"),
    path("api/verify-invitation", accept_invitations, name="accept_invitations"),
    path("api/users", get_users, name="get_users"),
    path("api/users/<int:user_id>", user_detail, name="user_detail"),
    path(
        "api/invitations",
        get_user_invitations,
        name="get_user_invitations",
    ),
    path(
        "api/invitations/<str:uid>/resend",
        resend_user_invitation,
        name="resend_user_invitation",
    ),
    path(
        "api/invitations/<str:uid>/cancel",
        cancel_invitation,
        name="cancel_user_invitation",
    ),
    path("api/invitations/cancel", cancel_invitation_by_email, name="cancel_invitation_by_email"),
    path("api/contacts", get_contacts, name="get_contacts"),
    path(
        "api/contacts/<int:contact_id>/interactions/<int:interaction_id>",
        get_contact_interaction,
        name="get_contact_interaction",
    ),
    path("api/contacts/<int:id>", contact_detail, name="get_contact"),
    path(
        "api/contacts/<int:contact_id>/interactions",
        get_contact_interactions,
        name="get_contact_interactions",
    ),
    path("api/contacts/relations", get_contact_ids),
    path("api/contacts/merge-contacts", merge_contact_api),
    path("api/contacts/<int:id>/relations", get_contact_relations),
    path("api/customers", get_accounts),
   # ----------------------------------------------------------------------------
    path("api/customers/<int:id>/email", account_email_detail),
    path("api/customers/configure", account_configuration),
    
    path("api/customers/hierarchies", get_account_hierarchies),
    path("api/customers/<int:id>", account_detail),
    path("api/customers/<int:id>/contacts", get_customer_contact),
    path("api/customers/<int:id>/contacts/<int:contact_id>",delete_customer_contact),
    path("api/customers/<int:id>/hierarchies", account_hierarchy),
    path("api/customers/<int:customer_id>/overview", customer_account_overview, name="customer_overview"),

    path("api/customers/<int:customer_id>/leads", get_customer_leads, name="customer_leads"),
    path("api/customers/<int:customer_id>/interactions", get_customer_interactions, name="customer_interactions"),
    path("api/customers/<int:customer_id>/notes", get_customer_notes, name="customer_notes"),
    path("api/customers/<int:customer_id>/policies", get_customer_policies, name="customer_policies"),
    path("api/customer-payments", get_customer_payments, name="customer_payments"),
    path("api/customer-payments/confirm", confirm_customer_payment, name="confirm_customer_payment"),
    path("api/customers/<int:customer_id>/interested-products", get_customer_interested_products, name="customer_interested_products"),
    path("api/customer-requests/by-type", get_customer_requests_by_type, name="customer_requests_by_type"),
    path("api/customer-requests/<int:request_id>", get_customer_request_full_details, name="customer_request_full_details"),
    path("api/customer-requests/<int:request_id>/confirm", confirm_customer_request, name="customer_request_confirm"),

    path("api/forms", forms_view),
    path("api/forms/<int:id>", form_detail),
    path("api/forms/<int:id>/attributes", form_attributes_view),
    path("api/forms/<int:id>/attributes/<int:attribute_id>", form_attribute_detail),
    path("api/settings/<str:key>", fetch_settings, name="fetch_setting"),
    path("api/settings", get_multiple_settings, name="get_multiple_settings"),
    path("api/channels", channels, name="channels"),  
    path("api/channels/<int:id>", channel_detail, name="channel_detail"),  
    path("api/currencies", get_currencies, name="get_currencies"),
    path("api/statuses", get_statuses, name="get_statuses"),
    path("api/base-currency", get_base_currency, name="get_base_currency"),
    path("api/countries", get_all_countries, name="get_all_countries"),
    path("api/countries/<int:id>", get_country_by_id, name="get_country_by_id"),

    path("api/currencies/<int:id>", get_currency_by_id, name="get_currency_by_id"),
    path("api/entities/<int:id>/notes", entity_notes, name="entity_notes"),
    path("api/entities/<int:id>/notes/<int:notes_id>", entity_note_detail, name="entity_note_detail"),
    path("api/products", get_all_products, name="get_all_products"),
    path("api/flags", flag_get, name = "flags_get"),
    path("api/flags/<int:id>", flag_detail , name="flag_detail"),
    path("api/entities/<int:id>/documents", entity_documents, name="entity_documents"),
    path("api/entities/<int:id>/documents/<int:doc_id>", entity_document_detail, name="entity_document_detail"),
    path("api/flex-fields/config/<str:entity>", get_flex_fields_by_entity, name="flex-field-config"),
    path("api/customers/<int:id>/contacts/<int:contact_id>/primary", update_primary_contact, name="update-primary-contact"),
    path("api/reasons", reasons_view),
    path("api/reasons/<int:id>", reason_detail),
    path("api/customers/primary-contact-person/many", get_primary_contacts_by_customer_ids, name="get-primary-contacts-by-customer-ids"),
    path("api/contacts/<int:id>/customers", get_customers_by_contact_id, name="get_customers_by_contact_id"),

    path("api/entities/<int:id>", get_entity_with_details),
    path("api/entities/<int:id>/activities", entity_activities, name="entity_activities"),
    path("api/entities/<int:id>/activities/<int:activity_id>", entity_activity_detail, name="entity_activity_detail"),
    path("api/entities/<int:id>/flags", entity_flags, name="entity_flags"),
    path("api/entities/<int:id>/flags/<int:flag_id>", entity_flag_detail, name="entity_flag_detail"),
    path("api/me", get_current_user , name="get_current_user"),
    path("api/my-permissions", get_user_permissions , name="get_user_permissions"),
    path('api/entities', get_entities, name='entities.get'),

    # -------------------------------Service providers----------------------------------
    # path("api/service-providers", service_providers, name='service_providers'),
    # path("api/service-providers/<int:id>", manage_service_provider, name='manage_service_provider'),


    # Templates
    path('api/templates', template_list, name='create-template'),  # POST
    path('api/templates/<int:id>', template_detail, name='get-template'),  

    # Form Steps
    path('api/forms/<int:id>/steps', form_steps, name='create-form-step'),  # POST
    path('api/forms/<int:id>/steps/<int:step_id>', form_step_detail, name='update-form-step'),  # PUT

    # Form Panels
    path('api/forms/<int:id>/panels', create_form_panel, name='create-form-panel'),  # POST
    path('api/forms/<int:id>/steps/<int:step_id>/panels', list_form_panels_by_step, name='get-form-panel'),  # GET
    path('api/forms/<int:id>/panels/<int:panel_id>',form_panel_detail, name='update-form-panel'),  # PUT
    path('api/forms/<int:id>/panels/<int:panel_id>/duplicate',duplicate_form_panel, name='duplicate-form-panel'),  # PUT

    # Form Elements
    path('api/forms/<int:id>/elements', form_element, name='create-form-element'),  # POST
    path('api/forms/<int:id>/elements/<int:element_id>', form_element_detail, name='update-form-element'),  # PUT

    # List all base form elements
    path('api/templates/form-elements', list_form_elements_grouped, name='list-form-elements'),  # GET


    # path('api/form-submissions', form_submission_list, name='submit-form-values'),  # GET ALL & POST
    # path('api/form-submissions/<int:id>', form_submission_detail, name='update-submited-form-values'),  # PUT

    path('api/all-notifications', all_notifications, name='all_notifications'),  # GET
    path('api/notifications-unread-count', notification_unread_count, name='notification_unread_count'),  # GET – for live polling
    path('api/notifications/stream', notification_stream, name='notification_stream'),  # GET – SSE for real-time push
    path('api/read-notifications/<ids>', read_notifications, name='read_notifications'),  # POST
    path('api/notifications/<int:notification_id>', get_notification_detail, name='get_notification_detail'),  # GET

# -------------------------------Products ----------------------------------
    path("api/insurer-products", insurer_products, name="insurer_products"),
    path("api/insurer-products/<int:id>/coverage", product_coverage, name="product_coverage"),
    path("api/product-categories", product_categories, name="product_categories"),
    path("api/product-items", product_item_view, name="product_items"),
    path("api/product-items/<int:id>", product_item_detail, name="product_item_detail"),
    path("api/insurer-products/<int:id>/documents", product_documents, name="product_documents"),
    path("api/insurer-products/<int:id>/documents-enhanced", product_documents_enhanced, name="product_documents_enhanced"),
    path("api/insurer-product-documents", insurer_product_documents, name="insurer_product_documents"),
    path("api/insurer-products/<int:id>/policy-documents", policy_product_documents, name="policy_product_documents"),
    path("api/insurer-products/<int:id>/risk-documents", risk_product_documents, name="risk_product_documents"),
    path('api/insurer-product-by-type', get_vendor_products_by_risk_type, name='get_vendor_products_by_risk_type'),
    path('api/native-product-by-type', get_native_products_by_risk_type, name='get_native_products_by_risk_type'),
    path('api/product-document/<int:id>', product_document_detail, name='product_document_detail'),
    path('api/product-coverage/<int:id>', product_coverage_detail, name='product_coverage_detail'),

    path("api/insurer-products/<int:id>", product_detail, name="product_detail"),
    path("api/native-products", native_products, name="native_products"),
    path("api/native-products/<int:id>/products", native_vendor_products, name="native_vendor_products"),
    path("api/native-products/<int:id>", native_product_detail, name="native_product_detail"),
    path("api/opportunity-type/<int:id>/products", opportunity_products, name="opportunity_products"),
    path("api/opportunity-type/<int:id>/vendors", opportunity_type_vendors, name="opportunity_type_vendors"),
    path("api/opportunity-type/<int:id>/vendors/<int:vendor_id>/products", opportunity_type_vendor_product, name="opportunity_type_vendor_product"),
    path("api/product-groups", product_groups, name="product_groups"),
    path("api/product-groups/<int:id>", product_group_detail, name="product_group_detail"),
    path("api/coverage-levels", coverage_levels, name="coverage_levels"),
    path("api/native-product/<int:id>/insurer-product/<int:vendor_product_id>/remove", unlink_native_product, name="unlink_native_product"),
    path("api/product-groups/<int:id>/teams", product_group_teams, name="product_group_teams"),
    path("api/product-groups/<int:id>/products", product_group_product_add, name="product_group_product_add"),
    path("api/product-groups/<int:id>/teams/<int:team_id>", delete_product_group_teams, name="delete_product_group_teams"),
    path("api/product-groups/<int:id>/products/<int:product_id>", delete_product_group_products, name="delete_product_group_products"),
    path("api/product/<int:id>/add-insurer-products", add_insurer_product, name="add_insurer_product"),
    path("api/insurer-product/<int:id>/native-product-mapping", native_product_mapping, name="native_product_mapping"),

    path("api/product-groups/<int:id>/add-products", add_product_in_group, name="add_product_in_group"),
    path("api/opportunity-types", opportunity_type, name='opportunity_type'),
    path("api/risk-types", risk_types, name='risk_types'),
    # path("api/service-providers", get_all_service_providers, name='service_providers'),

    # path("api/coverage-types", coverage_types, name="coverage_types"),

    path("api/job-titles", job_title_view),
    path("api/job-titles/<int:id>", job_title_detail),

    path("api/service-types", service_type_view),
    path("api/service-types/<int:id>",service_type_detail),
    
    path("api/organization-levels", organization_level_view),
    path("api/organization-levels/<int:id>", organization_level_detail),

    path("api/organizational-nodes",organizational_node_view),
    path("api/organizational-nodes/<int:id>", organizational_node_detail),
    path("api/organizational-hierarchy",organizational_node_hierarchy_view),

    path("api/teams",team_view),
    path("api/teams/<int:id>",team_detail),
    path("api/teams/account-managers",get_account_managers),
    path("api/teams/sales-agents",get_sales_agents),

    path("api/teams/<int:team_id>/users",team_user_view),
    path("api/team-users/<int:id>",team_user_detail),
    path("api/non-team-users",list_users_not_in_any_team),
    
    path("api/sales-targets",sales_target_view),
    path("api/sales-targets/<int:id>",sales_target_details),
    path('api/user-sales-targets',get_sales_targets_by_user_ids),
    path('api/user-sales-target-graph',list_sales_target_graph),
    path('api/sales-target-single',get_sales_target_by_user_and_month),
    path('api/year-sales-target',get_yearly_sales_targets),

    path("api/user-bank-details",user_bank_detail_view),
    path("api/user-bank-details/<int:id>",user_bank_detail),

    path("api/service-providers",service_provider_view),
    path("api/service-providers/<int:id>",service_provider_detail),
    path("api/service-provider-quotations",get_received_quotations),
    path('api/service-providers-type', get_service_providers_by_category),

    path("api/service-provider/<int:sp_id>/contacts",service_provider_contacts_view),
    path("api/service-provider/<int:sp_id>/contacts/<int:id>",service_provider_contact_detail),
    path("api/service-provider/<int:sp_id>/products",sp_products, name="sp_products"),
    path("api/service-provider/<int:sp_id>/quotations",sp_quotation, name="sp_quotation"),

    path("api/product/<int:product_id>/teams", product_teams, name="assign_team_to_product"),
    path("api/product/<int:product_id>/teams/<int:team_id>", delete_product_team, name="delete_team_from_assigned_product"),
    path("api/product/<int:product_id>/coverages", get_product_coverages, name="assign_team_to_product"),
    path("api/product/<int:product_id>/documents", get_product_document_types, name="assign_team_to_product"),
    # path("api/product/<int:product_id>/vendor-product/<int:vendor_product_id>", delete_product_vendor_product, name="assign_team_to_product"),

    # Approval endpoints
    path("api/approvals", quotation_approval, name="quotation_approval"),
    path("api/approvals/<int:id>", handle_quotation_approval, name="handle_quotation_approval"),
    path("api/approvals/<int:id>/changes", quotation_approval_changes, name="quotation_changes"),
    path("api/approvals/send-email", quotation_approval_send_email, name="quotation_approval_send_email"),
    path("api/approvals/entity-check/<int:id>", entity_check, name="entity_check"),
    path("api/approvals/<int:approval_id>/risk-details", approval_risk_details),
    path("api/risk-values/<int:risk_type_id>", get_risks_by_type_and_customer, name="get_risk_details_by_lead"),
    path("api/service-providers", service_providers, name='service_providers'),#-------------------------


    path("api/auth-google-start/<mail_address>", ctl.auth_google_start, name="auth-google-start"),
    path("api/auth-google-callback", ctl.auth_google_callback, name="auth-google-callback"),
    path("api/gmail/status", ctl.gmail_status, name="gmail-status"),
    path("api/gmail/messages", ctl.gmail_messages, name="gmail-messages"),
    path("api/gmail/send", ctl.send_email, name="send-email"),
    path("api/gmail/history", ctl.email_history, name="email-history"),
    path("api/gmail/thread-replies", ctl.email_thread_replies, name="email-thread-replies"),
    path("api/oauth/debug", ctl.test_oauth_debug, name="oauth-debug"),
    path("api/send-message", ctl.send_message, name="send-message"),

    #chat related apis
    path("api/user-mail-config", user_mail_config, name="user_mail_config"),
    path("api/user/<int:user_id>/mail-config/<int:config_id>", delete_user_specific_mail_config, name="delete_user_specific_mail_config"),
    path("api/<int:quotation_id>/chat/<str:insurer_id>", quotation_insurer_chat_messages, name="quotation_insurer_chat_messages"),
    path("api/quotation-thread-messages/<int:quotation_id>", ctl.quotation_thread_messages, name="quotation_insurer_chat_messages"),

    # Chatmail endpoints
    path("api/chatmail/send", send_chatmail_message, name="send_chatmail_message"),
    path("api/chatmail/messages", get_chatmail_messages, name="get_chatmail_messages"),
    path("api/chatmail/conversations", get_chatmail_conversations, name="get_chatmail_conversations"),
    path("api/chatmail/sync-thread", sync_gmail_thread, name="sync_gmail_thread"),
    path("api/chatmail/mark-conversation-seen", mark_conversation_seen, name="mark_conversation_seen"),
    path("api/chatmail/download-attachment", download_attachment, name="download_attachment"),
    path("api/chatmail/attachment-info", get_attachment_info, name="get_attachment_info"),
    path("api/chatmail/gmail-webhook", gmail_webhook, name="gmail_webhook"),
    path("api/gmail/push-webhook", gmail_push_webhook, name="gmail_push_webhook"),
    
    # Quotation chat messages endpoint
    path("api/<int:quotation_id>/chat-messages/<str:insurer_id>", quotation_chat_messages, name="quotation_chat_messages"),
    # Quotation sync conversations endpoint
    path("api/quotation/<int:quotation_id>/sync-conversations", quotation_sync_conversations, name="quotation_sync_conversations"),
    
    # Policy chat messages endpoint
    path("api/policy/<int:policy_id>/chat-messages", policy_chat_messages, name="policy_chat_messages"),
    # Policy sync conversations endpoint
    path("api/policy/<int:policy_id>/sync-conversations", policy_sync_conversations, name="policy_sync_conversations"),
    # Policy sync conversations endpoint (new with endorsement request logic)
    path("api/policy/<int:policy_id>/sync-endorsement-requests", policy_sync_conversations_new, name="policy_sync_conversations_new"),
    path("api/products-filters", get_vendor_products_by_risk_type),
    path("api/insurers", request_insurers, name="request_insurers"),
    path("api/endorsement-types", endorsement_types, name="endorsement_types"),
    # Get documents for a specific endorsement
    path("api/endorsement/<int:endorsement_id>/documents", get_endorsement_documents, name="get_endorsement_documents"),
    
    # Export receipts to Excel
    path("api/export/receipts-excel", export_receipts_excel, name="export_receipts_excel"),

]

# Add media URL configuration for serving uploaded files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
