# API Tasks: Service Provider Management — Requirements Document

## 3.1 Create Service Provider
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

- [ ] Ensure API supports: Users can upload a **logo** image for the service provider. Logo is optional.
- [ ] Ensure API supports: **Partner name** is a required field.
- [ ] Ensure API supports: **Email** is a required field. The system must validate it is in a valid email format.
- [ ] Ensure API supports: **Contact number** is a required field. It includes a country code selector (flag + dial code) and the number.
- [ ] Ensure API supports: **Fax number** is an optional field.
- [ ] Ensure API supports: **Address** is a required field.
- [ ] Ensure API supports: **Website** is an optional field.
- [ ] Ensure API supports: A service provider supports two contact persons — **Primary** and **Secondary**.
- [ ] Ensure API supports: **Contact type** is a required field and is fixed to either `Primary` or `Secondary`.
- [ ] Ensure API supports: **Salutation** is a required field for each contact person (e.g. Mr., Mrs., Ms., Dr.).
- [ ] Ensure API supports: **Contact person name** is a required field.
- [ ] Ensure API supports: **Contact number** is a required field for each contact person. It includes a country code selector and the number.
- [ ] Ensure API supports: **Role** is an optional field for each contact person.
- [ ] Ensure API supports: **Email** is an optional field for each contact person.
- [ ] Ensure API supports: **Remarks** is an optional field for each contact person.
- [ ] Ensure API supports: **Account holder name** is an optional field.
- [ ] Ensure API supports: **Bank name** is an optional field.
- [ ] Ensure API supports: **Account number** is an optional field.
- [ ] Ensure API supports: **Bank branch** is an optional field.
- [ ] Ensure API supports: **IBAN / Swift code** is an optional field (for international use).
- [ ] Ensure API supports: **Payment gateway URL** is an optional field.
## 3.2 View Service Providers
- [x] Create GET endpoint (list) with filters.
- [x] Implement permission checks for viewing.

- [x] Ensure API supports: Users can view a list of all active service providers showing partner name, email, and contact number.
- [x] Ensure API supports: The service provider list supports search by partner name and email.
- [x] Ensure API supports: Users can view the full detail of a single service provider including all three sections.
- [x] Ensure API supports: Soft-deleted service providers are hidden from the default list view.
## 3.3 Service Provider Detail — Insurer Products
- [ ] Implement API logic for 3.3 Service Provider Detail — Insurer Products.

- [ ] Ensure API supports: The service provider detail view includes an **Insurer Products** section listing all active insurer products linked to that service provider.
- [ ] Ensure API supports: Each insurer product entry displays: product name, risk type, coverage level, currency, and last update date.
- [ ] Ensure API supports: If no insurer products are linked to the service provider, the section displays an empty state message.
- [ ] Ensure API supports: The insurer products list within the detail view supports search by product name.
- [ ] Ensure API supports: Soft-deleted insurer products are not shown in this list.
- [ ] Ensure API supports: Each insurer product entry in the list links to the full insurer product detail view.
## 3.4 Edit Service Provider
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit all fields across the general information, contact persons, and bank account info sections.
- [ ] Ensure API supports: All mandatory field rules from creation apply during edit.
- [ ] Ensure API supports: Soft-deleted service providers cannot be edited.
## 3.5 Duplicate Service Provider
- [ ] Implement API logic for 3.5 Duplicate Service Provider.

- [ ] Ensure API supports: Users can duplicate an existing service provider to create an independent copy.
- [ ] Ensure API supports: The duplicate copies all fields across all three sections, with the partner name suffixed to indicate it is a copy.
- [ ] Ensure API supports: The duplicate is a fully independent record — changes to it do not affect the original.
## 3.6 Delete Service Provider
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete a service provider.
- [ ] Ensure API supports: Soft-deleted service providers are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure API supports: Hard deletion is not supported.
## General Information
- [ ] Implement API logic for General Information.

## Contact Person (Primary & Secondary)
- [ ] Implement API logic for Contact Person (Primary & Secondary).

## Bank Account Info
- [ ] Implement API logic for Bank Account Info.

- [ ] Register permission: `service_provider.create` (Create new service providers)
- [ ] Register permission: `service_provider.view` (View service provider list and details)
- [ ] Register permission: `service_provider.edit` (Edit an existing service provider)
- [ ] Register permission: `service_provider.duplicate` (Duplicate an existing service provider)
- [ ] Register permission: `service_provider.delete` (Soft-delete a service provider)
- [ ] Ensure API supports: All create, edit, duplicate, and delete actions must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure API supports: Uploaded logo images must be validated for file type (JPG, PNG) and size limits.
- [ ] Ensure API supports: Soft-deleted service providers must be retained indefinitely for audit purposes.
- [ ] Ensure API supports: Contact number fields must support international formats via country code selector.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
