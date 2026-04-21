# Envoy BU Core API – Endpoints Documentation

This document describes all API endpoints in the Envoy Business Unit Core API: how they are implemented, which database tables they use, and their main functionality.

---

## Table of Contents

1. [Application Overview](#application-overview)
2. [Authentication & Login](#authentication--login)
3. [Roles & Permissions](#roles--permissions)
4. [Users & Invitations](#users--invitations)
5. [Groups](#groups)
6. [Contacts](#contacts)
7. [Customers (Accounts)](#customers-accounts)
8. [Forms & Form Builder](#forms--form-builder)
9. [Settings](#settings)
10. [Common / Reference Data](#common--reference-data)
11. [Entities, Notes, Documents, Flags, Activities](#entities-notes-documents-flags-activities)
12. [Products & Insurer Products](#products--insurer-products)
13. [Product Items, Categories, Coverage](#product-items-categories-coverage)
14. [Job Titles, Service Types, Organization](#job-titles-service-types-organization)
15. [Teams & Team Users](#teams--team-users)
16. [Sales Targets](#sales-targets)
17. [User Bank Details](#user-bank-details)
18. [Service Providers & Contacts](#service-providers--contacts)
19. [Approvals](#approvals)
20. [Gmail / Mail](#gmail--mail)
21. [Chat & Chatmail](#chat--chatmail)
22. [Export](#export)
23. [Database Tables Reference](#database-tables-reference)

---

## Application Overview

- **Stack:** Django REST Framework, JWT (Simple JWT), custom `QueryBuilderService` for filtering/sorting/pagination.
- **Pattern:** Controllers in `envoy/controllers/`; models in `envoy/models/`; URLs in `envoy/urls.py` and `accounts/urls.py`.
- **Response format:** Centralized via `ResponseService.response(status, result, message)`.

---

## Authentication & Login

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| POST | `/api/login` | `accounts.views.LoginView` | `core_users` | External IDP login: validates `idp_access_token` against external API, finds user by `idp_user_id`, returns JWT and user payload. Optionally calls external `/api/access`. |

**Key values:** Request: `idp_access_token`. Response: `access_token`, `user` (id, first_name, display_name, email, role, entity), `DB_DATABASE`.

---

## Roles & Permissions

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/permissions` | `get_actions` (roles_controller) | `core_actions` | List all actions (permissions) or create a new action. |
| GET, POST | `/api/roles` | `get_roles` | `core_roles` | List roles (paginated, filter/search/sort via QueryBuilderService) or create a role. |
| GET, PUT, DELETE | `/api/roles/<role_id>` | `role_detail` | `core_roles`, `core_role_authorities` | Get, update, or delete a role; manage role–action links. |
| GET | `/api/roles/privileges` | `count_role_privileges` | `core_roles`, `core_role_authorities` | Count privileges per role. |
| GET | `/api/roles/assigned-users` | `count_role_users` | `core_roles`, `core_users` | Count users assigned to each role. |
| GET, POST | `/api/roles/<role_id>/permissions` | `role_permissions` | `core_role_authorities`, `core_actions` | Get or set permissions (actions) for a role. |

**Key values:** Roles: `name`, `description`, `system_role`. Permissions are stored as role–action relations in `core_role_authorities`.

---

## Users & Invitations

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET | `/api/users` | `get_users` (user_controller) | `core_users` (with role/entity) | List users with pagination, filters, search. |
| GET, PUT, DELETE | `/api/users/<user_id>` | `user_detail` | `core_users`, `core_roles`, `core_entities` | Get, update, or soft-delete a user (e.g. role_id, entity). |
| POST | `/api/users/invite` | `create_invitations` | `core_user_invitations`, `core_roles` | Create invitation (name, email, role_id), send email. |
| POST | `/api/verify-invitation` | `accept_invitations` | `core_user_invitations`, `core_users`, `core_entities`, `core_roles` | Accept invitation with `idp_access_token` + `invitation` uid; create or link user. |
| GET | `/api/invitations` | `get_user_invitations` (invitation_controller) | `core_user_invitations`, `core_roles` | List invitations with pagination and search. |
| POST | `/api/invitations/<uid>/resend` | `resend_user_invitation` | `core_user_invitations` | Resend invitation email by uid. |
| POST | `/api/invitations/<uid>/cancel` | `cancel_invitation` | `core_user_invitations` | Cancel invitation by uid. |
| POST | `/api/invitations/cancel` | `cancel_invitation_by_email` | `core_user_invitations` | Cancel invitation by email. |

**Key values:** Invitations: `uid`, `name`, `email`, `role_id`. User: `idp_user_id`, `email`, `role_id`, `entity_id`, `display_name`, `code`.

---

## Groups

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/groups` | `get_groups` (group_controller) | `core_contact_groups` | List or create contact groups. |
| GET, PUT, DELETE | `/api/groups/<id>` | `get_single_group` | `core_contact_groups` | Get, update, or delete a group. |
| GET, POST, DELETE | `/api/groups/<id>/contacts` | `get_group_contact` | `core_contact_groups`, `core_group_contacts`, `core_contacts` | List, add, or remove contacts in a group. |
| GET | `/api/groups/<id>/assignable-contacts` | `get_assignable_contacts` | `core_contact_groups`, `core_group_contacts`, `core_contacts` | Get contacts that can be assigned to the group (e.g. not already in it). |

**Key values:** Group: `name`, `description`. Group–contact link: `core_group_contacts` (group_id, contact_id).

---

## Contacts

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/contacts` | `get_contacts` (contact_controller) | `core_contacts` | List contacts (filter/search/sort/paginate) or create a contact. |
| GET, PUT, DELETE | `/api/contacts/<id>` | `contact_detail` | `core_contacts`, `core_customers`, `core_group_contacts`, `core_intractions` | Get, update, or delete contact; checks usage before delete. |
| GET | `/api/contacts/<contact_id>/interactions` | `get_contact_interactions` | `core_intractions`, `core_contacts`, `core_channels` | List interactions for a contact. |
| GET | `/api/contacts/<contact_id>/interactions/<interaction_id>` | `get_contact_interaction` | `core_intractions` | Get single interaction detail. |
| GET | `/api/contacts/relations` | `get_contact_ids` | `core_contacts` | Get contact IDs (e.g. for relation/merge UI). |
| POST, DELETE | `/api/contacts/merge-contacts` | `merge_contact_api` | `core_contacts`, `core_customer_contacts` (customer_additional_contact) | Merge contacts (set `duplicated_contact_id`) or unmerge. |
| GET | `/api/contacts/<id>/relations` | `get_contact_relations` | `core_contacts`, `core_customers`, `core_contact_groups` | Get related accounts and groups for a contact. |
| GET | `/api/contacts/<id>/customers` | `get_customers_by_contact_id` | `core_customers`, `core_contacts` | List customers linked to a contact (e.g. primary or additional). |

**Key values:** Contact: `name`, `email`, `address`, `primary_contact`, `secondary_contact`, `remarks`, `picture`, `website_url`, `duplicated_contact_id`.

---

## Customers (Accounts)

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/customers` | `get_accounts` (account_controller) | `core_customers`, `core_contacts` (primary) | List or create customers; filters (type, name), search, pagination. |
| GET, PUT, DELETE | `/api/customers/<id>` | `account_detail` | `core_customers`, `core_contacts` | Get, update, or delete customer. |
| GET | `/api/customers/<id>/email` | `account_email_detail` | `core_customers`, `core_contacts` | Get email-related details for customer. |
| POST | `/api/customers/configure` | `account_configuration` | `core_customers`, `core_contacts`, `core_customer_invitations`, `core_gmailcredential` | Configure customer (portal signup/invite, Gmail linking). |
| GET | `/api/customers/hierarchies` | `get_account_hierarchies` | `core_customers` | Get customer hierarchy tree. |
| GET, POST, DELETE | `/api/customers/<id>/contacts` | `get_customer_contact` | `core_customers`, `core_contacts`, `core_customer_contacts` | List, add, or remove additional contacts for customer. |
| DELETE | `/api/customers/<id>/contacts/<contact_id>` | `delete_customer_contact` | `core_customer_contacts` | Remove contact from customer. |
| GET, POST, DELETE | `/api/customers/<id>/hierarchies` | `account_hierarchy` | `core_customers` (parent_id) | Get, add, or remove hierarchy links. |
| PATCH | `/api/customers/<id>/contacts/<contact_id>/primary` | `update_primary_contact` | `core_customers`, `core_contacts` | Set contact as primary for customer. |
| GET | `/api/customers/primary-contact-person/many` | `get_primary_contacts_by_customer_ids` | `core_customers`, `core_contacts` | Bulk primary contact info by customer IDs. |
| GET | `/api/customers/<customer_id>/overview` | `customer_account_overview` (account_additional_controller) | `core_customers`, `crm_opportunities`, `core_intractions`, `core_entity_notes`, `crmp_policy_base`, `crm_oppor_interested_products` | Customer overview: leads, interactions, notes, policies, interested products. |
| GET | `/api/customers/<customer_id>/leads` | `get_customer_leads` | `core_customers`, `crm_opportunities` | Paginated leads (opportunities) for customer. |
| GET | `/api/customers/<customer_id>/interactions` | `get_customer_interactions` | `core_intractions`, `core_contacts`, `core_channels`, `core_users` | Interactions for customer. |
| GET | `/api/customers/<customer_id>/notes` | `get_customer_notes` | `core_entity_notes`, `core_entities`, `core_customers` | Notes for customer’s entity. |
| GET | `/api/customers/<customer_id>/policies` | `get_customer_policies` | `crmp_policy_base`, `core_products` | Policies for customer. |
| GET | `/api/customer-payments` | `get_customer_payments` | Payment-related tables | List customer payments. |
| POST | `/api/customer-payments/confirm` | `confirm_customer_payment` | Payment-related tables | Confirm a payment. |
| GET | `/api/customers/<customer_id>/interested-products` | `get_customer_interested_products` | `crm_oppor_interested_products`, `core_products`, `crm_opportunities` | Interested products linked to opportunities. |
| GET | `/api/customer-requests/by-type` | `get_customer_requests_by_type` | `cus_requests`, `core_status`, `cus_request_risk_types`, `crm_opportunity_types`, `cus_request_vendor_products`, `core_vendor_products`, `core_product_groups`, `core_customers` | Customer requests grouped/filtered by type. |
| GET | `/api/customer-requests/<request_id>` | `get_customer_request_full_details` | Same + form submissions | Full details of a customer request. |
| POST | `/api/customer-requests/<request_id>/confirm` | `confirm_customer_request` | Request/status tables | Confirm customer request. |

**Key values:** Customer: `name`, `type`, `primary_contact_id`, `entity_id`, `portal_id`, `is_enrolled`. Hierarchy via `parent_id` on `core_customers`.

---

## Forms & Form Builder

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/forms` | `forms_view` (form_controller) | `core_forms` | List or create forms (title, description). |
| GET, PUT, DELETE | `/api/forms/<id>` | `form_detail` | `core_forms` | Get, update, or delete form. |
| GET, POST | `/api/forms/<id>/attributes` | `form_attributes_view` | `core_form_attributes` | List or create form attributes. |
| GET, PUT, DELETE | `/api/forms/<id>/attributes/<attribute_id>` | `form_attribute_detail` | `core_form_attributes` | Get, update, or delete form attribute. |
| GET, POST | `/api/forms/<id>/steps` | `form_steps` | `core_form_custom_form_steps` | List or create form steps. |
| GET, PUT, DELETE | `/api/forms/<id>/steps/<step_id>` | `form_step_detail` | `core_form_custom_form_steps` | Get, update, or delete step. |
| GET | `/api/forms/<id>/steps/<step_id>/panels` | `list_form_panels_by_step` | `core_form_custom_form_panels` | List panels for a step. |
| GET, POST | `/api/forms/<id>/panels` | `create_form_panel` | `core_form_custom_form_panels` | List or create panels. |
| GET, PUT | `/api/forms/<id>/panels/<panel_id>` | `form_panel_detail` | `core_form_custom_form_panels` | Get or update panel. |
| POST | `/api/forms/<id>/panels/<panel_id>/duplicate` | `duplicate_form_panel` | `core_form_custom_form_panels` | Duplicate a panel. |
| GET, POST | `/api/forms/<id>/elements` | `form_element` | `core_form_custom_form_elements` (and options) | List or create form elements. |
| GET, PUT | `/api/forms/<id>/elements/<element_id>` | `form_element_detail` | `core_form_custom_form_elements` | Get or update element. |
| GET | `/api/templates/form-elements` | `list_form_elements_grouped` | `core_form_elements` | List base form elements (for builder). |
| GET, POST | `/api/templates` | `template_list` (form_template_controller) | `core_templates` | List or create form templates (single/multi-step). |
| GET, PUT, DELETE | `/api/templates/<id>` | `template_detail` | `core_templates` | Get, update, or delete template. |

**Key values:** Form: `title`, `description`. Template: `title`, `type` (single_form, multi_step_form), `description`. Steps, panels, and elements define the form structure; submissions store in `core_form_submissions` / `core_form_submission_valuess`.

---

## Settings

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, PATCH | `/api/settings/<key>` | `fetch_settings` (settings_controller) | `core_setting_keys`, `core_setting_global` | Get or update a global setting by key. |
| GET | `/api/settings` | `get_multiple_settings` | `core_setting_keys`, `core_setting_global` | Get multiple settings (e.g. by list of keys). |

**Key values:** Setting key name → `core_setting_keys.id` → `core_setting_global.value`.

---

## Common / Reference Data

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET | `/api/channels` | `channels` (common_controller) | `core_channels` | List channels (e.g. for interactions). |
| GET | `/api/channels/<id>` | `channel_detail` | `core_channels` | Get channel by id. |
| GET | `/api/currencies` | `get_currencies` | `core_currencies` | List currencies. |
| GET | `/api/currencies/<id>` | `get_currency_by_id` | `core_currencies` | Get currency by id. |
| GET | `/api/statuses` | `get_statuses` | `core_status` | List statuses (module + name). |
| GET | `/api/base-currency` | `get_base_currency` | `core_currencies` / settings | Get base currency. |
| GET | `/api/countries` | `get_all_countries` | `core_countries` | List countries. |
| GET | `/api/countries/<id>` | `get_country_by_id` | `core_countries` | Get country by id. |
| GET | `/api/all-notifications` | `all_notifications` | `core_notifications`, `core_notification_users` | List notifications for user. |
| GET | `/api/notifications-unread-count` | `notification_unread_count` | `core_notifications` | Unread notification count. |
| GET | `/api/notifications/stream` | `notification_stream` | `core_notifications` | SSE stream for real-time notifications. |
| POST | `/api/read-notifications/<ids>` | `read_notifications` | `core_notification_users` / notifications | Mark notifications as read. |
| GET | `/api/notifications/<notification_id>` | `get_notification_detail` | `core_notifications` | Get single notification. |
| GET | `/api/me` | `get_current_user` | `core_users`, `core_roles`, `core_entities` | Current authenticated user. |
| GET | `/api/my-permissions` | `get_user_permissions` | `core_users`, `core_roles`, `core_role_authorities`, `core_actions` | Current user’s permissions. |
| GET | `/api/products` | `get_all_products` (product_controller) | `core_products` | List native products (id, name, code). |
| GET | `/api/flags` | `flag_get` | `core_flags` | List flags. |
| GET, PUT, DELETE | `/api/flags/<id>` | `flag_detail` | `core_flags` | Get, update, or delete flag. |
| GET | `/api/reasons` | `reasons_view` (reason_controller) | `core_reasons` | List reasons. |
| GET, PUT, DELETE | `/api/reasons/<id>` | `reason_detail` | `core_reasons` | Get, update, or delete reason. |

---

## Entities, Notes, Documents, Flags, Activities

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET | `/api/entities` | `get_entities` (entity_controller) | `core_entities`, `core_users` | Get entities by comma-separated `ids`. |
| GET | `/api/entities/<id>` | `get_entity_with_details` | `core_entities`, `core_entity_notes`, `core_entity_docs`, `core_entity_flags`, `core_entity_activities` | Get entity with optional `attri` (notes, documents, flags, activities). |
| GET, POST | `/api/entities/<id>/notes` | `entity_notes` (note_controller) | `core_entity_notes`, `core_users` | List or create notes for entity. |
| GET, PUT, DELETE | `/api/entities/<id>/notes/<notes_id>` | `entity_note_detail` | `core_entity_notes` | Get, update, or delete note. |
| GET, POST | `/api/entities/<id>/documents` | `entity_documents` (documents_controller) | `core_entities`, `core_entity_docs` | List or upload documents for entity. |
| GET, PUT, DELETE | `/api/entities/<id>/documents/<doc_id>` | `entity_document_detail` | `core_entity_docs` | Get, update, or delete document. |
| GET | `/api/flex-fields/config/<entity>` | `get_flex_fields_by_entity` (flex_field_controller) | `core_flex_fields`, `core_flex_field_options` | Flex field config for entity type. |
| GET, POST | `/api/entities/<id>/activities` | `entity_activities` | `core_entity_activities` | List or create activities. |
| GET, PUT, DELETE | `/api/entities/<id>/activities/<activity_id>` | `entity_activity_detail` | `core_entity_activities` | Get, update, or delete activity. |
| POST | `/api/entities/<id>/flags` | `entity_flags` | `core_entity_flags`, `core_flags` | Add flag to entity. |
| PUT, DELETE | `/api/entities/<id>/flags/<flag_id>` | `entity_flag_detail` | `core_entity_flags` | Update or remove flag from entity. |

**Key values:** Entity: `type`, `created_by_id`, `updated_by_id`. Notes: `notes`, `added_by_id`. Documents: `doc`, `name`, `type`. Activities and flags link entity to activity/flag records.

---

## Products & Insurer Products

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/insurer-products` | `insurer_products` (product_controller) | `core_vendor_products`, `core_currencies`, `crm_opportunity_types`, `core_service_providers`, `core_users`, `core_entity_docs` | List or create insurer (vendor) products. |
| GET | `/api/insurer-products/<id>` | `product_detail` | Same + `core_product_vendor_products`, `core_products` | Get insurer product; include native product mapping if any. |
| GET | `/api/insurer-products/<id>/coverage` | `product_coverage` | `core_product_coverages` | Get coverage for product. |
| GET, PUT, DELETE | `/api/product-coverage/<id>` | `product_coverage_detail` | `core_product_coverages` | Get, update, or delete coverage. |
| GET | `/api/insurer-products/<id>/documents` | `product_documents` | `core_entity_docs`, entity linkage | Documents for insurer product. |
| GET | `/api/insurer-products/<id>/documents-enhanced` | `product_documents_enhanced` | Same | Enhanced document list. |
| GET | `/api/insurer-product-documents` | `insurer_product_documents` | `core_entity_docs` | List insurer product documents. |
| GET | `/api/insurer-products/<id>/policy-documents` | `policy_product_documents` | Policy/document tables | Policy documents for product. |
| GET | `/api/insurer-products/<id>/risk-documents` | `risk_product_documents` | Risk/document tables | Risk documents for product. |
| GET | `/api/product-document/<id>` | `product_document_detail` | `core_entity_docs` | Get single product document. |
| GET | `/api/insurer-product-by-type` | `get_vendor_products_by_risk_type` | `core_vendor_products`, risk/type tables | Vendor products by risk type. |
| GET | `/api/native-product-by-type` | `get_native_products_by_risk_type` | `core_products` | Native products by risk type. |
| GET | `/api/native-products` | `native_products` | `core_products` | List native products. |
| GET | `/api/native-products/<id>` | `native_product_detail` | `core_products` | Get native product. |
| GET | `/api/native-products/<id>/products` | `native_vendor_products` | `core_products`, `core_vendor_products`, `core_product_vendor_products` | Vendor products linked to native product. |
| GET | `/api/opportunity-type/<id>/products` | `opportunity_products` | Opportunity/product tables | Products for opportunity type. |
| GET | `/api/opportunity-type/<id>/vendors` | `opportunity_type_vendors` | Vendors by opportunity type | Vendors for opportunity type. |
| GET | `/api/opportunity-type/<id>/vendors/<vendor_id>/products` | `opportunity_type_vendor_product` | Vendor products | Products for vendor in opportunity type. |
| GET, POST | `/api/product-groups` | `product_groups` | `core_product_groups` | List or create product groups. |
| GET, PUT, DELETE | `/api/product-groups/<id>` | `product_group_detail` | `core_product_groups` | Get, update, or delete product group. |
| GET | `/api/product-groups/<id>/teams` | `product_group_teams` | `core_product_group_teams`, `core_teams` | Teams in product group. |
| GET, POST | `/api/product-groups/<id>/products` | `product_group_product_add` | `core_product_group_products` | List or add products to group. |
| DELETE | `/api/product-groups/<id>/teams/<team_id>` | `delete_product_group_teams` | `core_product_group_teams` | Remove team from group. |
| DELETE | `/api/product-groups/<id>/products/<product_id>` | `delete_product_group_products` | `core_product_group_products` | Remove product from group. |
| POST | `/api/product/<id>/add-insurer-products` | `add_insurer_product` | `core_product_vendor_products`, `core_vendor_products` | Link insurer product to native product. |
| GET, POST | `/api/insurer-product/<id>/native-product-mapping` | `native_product_mapping` | `core_product_vendor_products`, `core_products` | Get or set native product mapping. |
| POST | `/api/product-groups/<id>/add-products` | `add_product_in_group` | `core_product_group_products` | Add products to group. |
| GET | `/api/opportunity-types` | `opportunity_type` | `crm_opportunity_types` | List opportunity types. |
| GET | `/api/risk-types` | `risk_types` | Risk type table | List risk types. |
| GET, POST | `/api/product/<product_id>/teams` | `product_teams` | `core_product_teams`, `core_teams` | List or assign teams to product. |
| DELETE | `/api/product/<product_id>/teams/<team_id>` | `delete_product_team` | `core_product_teams` | Remove team from product. |
| GET | `/api/product/<product_id>/coverages` | `get_product_coverages` | `core_product_coverages` | Coverages for product. |
| GET | `/api/product/<product_id>/documents` | `get_product_document_types` | `core_product_document_types` | Document types for product. |
| POST | `/api/native-product/<id>/insurer-product/<vendor_product_id>/remove` | `unlink_native_product` | `core_product_vendor_products` | Unlink insurer product from native. |
| GET | `/api/products-filters` | `get_vendor_products_by_risk_type` | Same as insurer-product-by-type | Alias/filter for vendor products by risk type. |
| GET | `/api/insurers` | `request_insurers` | `core_service_providers` | List insurers (service providers). |
| GET | `/api/endorsement-types` | `endorsement_types` | Endorsement type table | List endorsement types. |
| GET | `/api/endorsement/<endorsement_id>/documents` | `get_endorsement_documents` | Endorsement/document tables | Documents for endorsement. |

---

## Product Items, Categories, Coverage

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/product-items` | `product_item_view` (product_item_controller) | `core_product_items` | List or create product items. |
| GET, PUT, DELETE | `/api/product-items/<id>` | `product_item_detail` | `core_product_items` | Get, update, or delete product item. |
| GET | `/api/product-categories` | `product_categories` | `core_product_categories` | List product categories. |
| GET | `/api/coverage-levels` | `coverage_levels` | Coverage table | List coverage levels. |

---

## Job Titles, Service Types, Organization

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/job-titles` | `job_title_view` (job_title_controller) | `core_job_titles` | List or create job titles. |
| GET, PUT, DELETE | `/api/job-titles/<id>` | `job_title_detail` | `core_job_titles` | Get, update, or delete job title. |
| GET, POST | `/api/service-types` | `service_type_view` | `core_service_types` | List or create service types. |
| GET, PUT, DELETE | `/api/service-types/<id>` | `service_type_detail` | `core_service_types` | Get, update, or delete service type. |
| GET, POST | `/api/organization-levels` | `organization_level_view` | `core_organization_levels` | List or create organization levels. |
| GET, PUT, DELETE | `/api/organization-levels/<id>` | `organization_level_detail` | `core_organization_levels` | Get, update, or delete level. |
| GET, POST | `/api/organizational-nodes` | `organizational_node_view` | `core_organizational_nodes` | List or create org nodes. |
| GET, PUT, DELETE | `/api/organizational-nodes/<id>` | `organizational_node_detail` | `core_organizational_nodes` | Get, update, or delete node. |
| GET | `/api/organizational-hierarchy` | `organizational_node_hierarchy_view` | `core_organizational_nodes` | Full org hierarchy tree. |

---

## Teams & Team Users

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/teams` | `team_view` (team_controller) | `core_teams` | List or create teams. |
| GET, PUT, DELETE | `/api/teams/<id>` | `team_detail` | `core_teams` | Get, update, or delete team. |
| GET | `/api/teams/account-managers` | `get_account_managers` | `core_users` (by role/type) | List account managers. |
| GET | `/api/teams/sales-agents` | `get_sales_agents` | `core_users` | List sales agents. |
| GET, POST | `/api/teams/<team_id>/users` | `team_user_view` (team_user_controller) | `core_team_users`, `core_users` | List or add users to team. |
| GET, PUT, DELETE | `/api/team-users/<id>` | `team_user_detail` | `core_team_users` | Get, update, or delete team–user assignment. |
| GET | `/api/non-team-users` | `list_users_not_in_any_team` | `core_users`, `core_team_users` | Users not in any team. |

---

## Sales Targets

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/sales-targets` | `sales_target_view` (sales_target_controller) | `core_sales_targets` | List or create sales targets. |
| GET, PUT, DELETE | `/api/sales-targets/<id>` | `sales_target_details` | `core_sales_targets` | Get, update, or delete target. |
| GET | `/api/user-sales-targets` | `get_sales_targets_by_user_ids` | `core_sales_targets` | Targets by user IDs. |
| GET | `/api/user-sales-target-graph` | `list_sales_target_graph` | `core_sales_targets` | Data for target vs achievement graph. |
| GET | `/api/sales-target-single` | `get_sales_target_by_user_and_month` | `core_sales_targets` | Single target by user and month. |
| GET | `/api/year-sales-target` | `get_yearly_sales_targets` | `core_sales_targets` | Yearly targets. |

---

## User Bank Details

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/user-bank-details` | `user_bank_detail_view` (user_bank_detail_controller) | `core_user_bank_details` | List or create user bank details. |
| GET, PUT, DELETE | `/api/user-bank-details/<id>` | `user_bank_detail` | `core_user_bank_details` | Get, update, or delete record. |

---

## Service Providers & Contacts

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/service-providers` | `service_provider_view` / `service_providers` | `core_service_providers` | List or create service providers (insurers/vendors). |
| GET, PUT, DELETE | `/api/service-providers/<id>` | `service_provider_detail` | `core_service_providers` | Get, update, or delete provider. |
| GET | `/api/service-provider-quotations` | `get_received_quotations` | Quotation tables | Quotations received from providers. |
| GET | `/api/service-providers-type` | `get_service_providers_by_category` | `core_service_providers` | Providers by category/type. |
| GET, POST | `/api/service-provider/<sp_id>/contacts` | `service_provider_contacts_view` | `core_service_provider_contacts` | List or add contacts for provider. |
| GET, PUT, DELETE | `/api/service-provider/<sp_id>/contacts/<id>` | `service_provider_contact_detail` | `core_service_provider_contacts` | Get, update, or delete provider contact. |
| GET | `/api/service-provider/<sp_id>/products` | `sp_products` | `core_vendor_products` | Products for service provider. |
| GET | `/api/service-provider/<sp_id>/quotations` | `sp_quotation` | Quotation tables | Quotations for provider. |

---

## Approvals

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET | `/api/approvals` | `quotation_approval` (approval_controller) | `core_entity_approvals`, `crmq_quotations`, `crmp_request_policies`, `core_entities`, `crm_opportunity_types`, `core_customers`, `core_users` | List approvals (quotations/policy requests) with status filter (open, pending, approved, rejected). |
| GET, PUT | `/api/approvals/<id>` | `handle_quotation_approval` | `core_entity_approvals`, quotation/policy tables | Get or process (approve/reject) approval. |
| GET | `/api/approvals/<id>/changes` | `quotation_approval_changes` | Approval change log | Get change history for approval. |
| POST | `/api/approvals/send-email` | `quotation_approval_send_email` | Mail/notification | Send approval email. |
| GET | `/api/approvals/entity-check/<id>` | `entity_check` | `core_entities`, approval rules | Check entity approval rules. |
| GET | `/api/approvals/<approval_id>/risk-details` | `approval_risk_details` | Risk/approval tables | Risk details for approval. |
| GET | `/api/risk-values/<risk_type_id>` | `get_risks_by_type_and_customer` | Risk/value tables | Risk values by type and customer. |

---

## Gmail / Mail

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET | `/api/auth-google-start/<mail_address>` | `auth_google_start` (mail_controller) | `core_gmailcredential` | Start OAuth for Gmail; store/link credential. |
| GET | `/api/auth-google-callback` | `auth_google_callback` | `core_gmailcredential` | OAuth callback; complete Gmail linking. |
| GET | `/api/gmail/status` | `gmail_status` | `core_gmailcredential` | Gmail connection status for user. |
| GET | `/api/gmail/messages` | `gmail_messages` | `core_email_messages`, Gmail API | List messages. |
| POST | `/api/gmail/send` | `send_email` | `core_email_messages`, Gmail API | Send email via Gmail. |
| GET | `/api/gmail/history` | `email_history` | `core_email_messages` | Email history. |
| GET | `/api/gmail/thread-replies` | `email_thread_replies` | `core_email_messages` | Replies in a thread. |
| GET | `/api/oauth/debug` | `test_oauth_debug` | - | Debug OAuth. |
| POST | `/api/send-message` | `send_message` | Mail tables / Gmail | Send message (generic). |

---

## Chat & Chatmail

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET, POST | `/api/user-mail-config` | `user_mail_config` (chat_controller) | `core_gmailcredential` | Get or create/update user mail (Gmail) config. |
| DELETE | `/api/user/<user_id>/mail-config/<config_id>` | `delete_user_specific_mail_config` | `core_gmailcredential` | Delete user mail config. |
| GET | `/api/<quotation_id>/chat/<insurer_id>` | `quotation_insurer_chat_messages` | `core_chat_conversations`, `core_email_messages` | Chat messages for quotation–insurer. |
| GET | `/api/quotation-thread-messages/<quotation_id>` | `quotation_thread_messages` (mail_controller) | `core_email_messages` | Thread messages for quotation. |
| POST | `/api/chatmail/send` | `send_chatmail_message` (chatmail_controller) | `core_chat_conversations`, `core_email_messages`, `core_email_attachments`, Gmail API | Send chatmail; create/update conversation and message; optional attachments. |
| GET | `/api/chatmail/messages` | `get_chatmail_messages` | `core_email_messages`, `core_chat_conversations` | Messages for a conversation (with pagination). |
| GET | `/api/chatmail/conversations` | `get_chatmail_conversations` | `core_chat_conversations`, `core_email_messages`, `core_service_providers` | List conversations (e.g. by quotation, insurer). |
| POST | `/api/chatmail/sync-thread` | `sync_gmail_thread` | `core_chat_conversations`, `core_email_messages`, Gmail API | Sync Gmail thread into app. |
| POST | `/api/chatmail/mark-conversation-seen` | `mark_conversation_seen` | `core_chat_conversations` | Mark conversation as seen. |
| GET | `/api/chatmail/download-attachment` | `download_attachment` | `core_email_attachments` | Download attachment by id. |
| GET | `/api/chatmail/attachment-info` | `get_attachment_info` | `core_email_attachments` | Attachment metadata. |
| POST | `/api/chatmail/gmail-webhook` | `gmail_webhook` | `core_chat_conversations`, `core_email_messages` | Webhook for Gmail push (process new mail). |
| POST | `/api/gmail/push-webhook` | `gmail_push_webhook` | Same | Gmail push webhook (history sync, notifications). |
| GET | `/api/<quotation_id>/chat-messages/<insurer_id>` | `quotation_chat_messages` | Chat/conversation tables | Chat messages for quotation–insurer. |
| GET | `/api/quotation/<quotation_id>/sync-conversations` | `quotation_sync_conversations` | `core_chat_conversations` | Sync conversations for quotation. |
| GET | `/api/policy/<policy_id>/chat-messages` | `policy_chat_messages` | Policy/chat tables | Chat messages for policy. |
| GET | `/api/policy/<policy_id>/sync-conversations` | `policy_sync_conversations` | Same | Sync conversations for policy. |
| GET | `/api/policy/<policy_id>/sync-endorsement-requests` | `policy_sync_conversations_new` | Same + endorsement | Sync with endorsement request logic. |

---

## Export

| Method | Path | Controller | Tables | Purpose |
|--------|------|------------|--------|---------|
| GET | `/api/export/receipts-excel` | `export_receipts_excel` (export_controller) | Receipt/payment tables | Export receipts to Excel. |

---

## Database Tables Reference

Core tables used by the API (Django model `db_table`):

| Table | Purpose |
|-------|---------|
| `core_users` | Users (idp_user_id, email, role_id, entity_id, display_name, code). |
| `core_roles` | Roles (name, description, system_role). |
| `core_actions` | Permission actions. |
| `core_role_authorities` | Role–action (permission) mapping. |
| `core_entities` | Generic entity (type, created_by_id, updated_by_id). |
| `core_user_invitations` | Invitations (uid, name, email, role_id). |
| `core_contacts` | Contacts (name, email, address, primary_contact, secondary_contact, duplicated_contact_id). |
| `core_contact_groups` | Contact groups. |
| `core_group_contacts` | Group–contact many-to-many. |
| `core_customers` | Customers/accounts (name, type, primary_contact_id, entity_id, parent_id). |
| `core_customer_contacts` | Customer additional contacts (customer_additional_contact). |
| `core_customer_invitations` | Customer portal invitations. |
| `core_forms` | Forms (title, description). |
| `core_form_attributes` | Form attributes. |
| `core_templates` | Form templates (single/multi-step). |
| `core_form_custom_form_steps` | Form steps. |
| `core_form_custom_form_panels` | Form panels. |
| `core_form_custom_form_elements` | Form elements. |
| `core_form_elements` | Base form elements. |
| `core_form_submissions` / `core_form_submissionss` | Form submissions. |
| `core_form_submission_valuess` | Submission values. |
| `core_setting_keys` | Setting key names. |
| `core_setting_global` | Global setting values. |
| `core_channels` | Interaction channels. |
| `core_currencies` | Currencies. |
| `core_status` | Status (module + name). |
| `core_countries` | Countries. |
| `core_products` | Native products. |
| `core_flags` | Flags (name, color). |
| `core_reasons` | Reasons. |
| `core_entity_notes` | Entity notes. |
| `core_entity_docs` | Entity documents. |
| `core_entity_flags` | Entity–flag link. |
| `core_entity_activities` | Entity activities. |
| `core_flex_fields` | Flex field definitions. |
| `core_flex_field_options` | Flex field options. |
| `core_vendor_products` | Insurer/vendor products. |
| `core_product_vendor_products` | Native–vendor product mapping. |
| `core_product_groups` | Product groups. |
| `core_product_group_products` | Product group–product link. |
| `core_product_group_teams` | Product group–team link. |
| `core_product_teams` | Product–team assignment. |
| `core_product_coverages` | Product coverage. |
| `core_product_document_types` | Product document types. |
| `core_product_items` | Product items. |
| `core_product_categories` | Product categories. |
| `core_job_titles` | Job titles. |
| `core_service_types` | Service types. |
| `core_organization_levels` | Organization levels. |
| `core_organizational_nodes` | Org hierarchy nodes. |
| `core_teams` | Teams. |
| `core_team_users` | Team–user assignment. |
| `core_sales_targets` | Sales targets. |
| `core_user_bank_details` | User bank details. |
| `core_service_providers` | Service providers (insurers/vendors). |
| `core_service_provider_contacts` | Provider contacts. |
| `core_entity_approvals` | Entity approvals (quotation/policy). |
| `core_gmailcredential` | Gmail OAuth credentials. |
| `core_email_messages` | Email/chat messages. |
| `core_email_attachments` | Email attachments. |
| `core_chat_conversations` | Chat conversations (quotation/policy/insurer). |
| `core_notifications` | Notifications. |
| `core_notification_users` | Notification–user read state. |
| `core_intractions` | Interactions (contact, customer, channel). |

External/CRM tables referenced in controllers (e.g. account_additional, approvals, customer requests): `crm_opportunities`, `crm_opportunity_types`, `crmq_quotations`, `crmp_policy_base`, `crmp_request_policies`, `crm_oppor_interested_products`, `cus_requests`, `cus_request_risk_types`, `cus_request_vendor_products`, etc.

---

*Generated from Envoy BU Core API codebase. Controllers live in `envoy/controllers/`; models in `envoy/models/`; URL routing in `envoy/urls.py` and `accounts/urls.py`.*
