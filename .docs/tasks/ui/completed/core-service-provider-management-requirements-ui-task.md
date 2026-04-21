# UI Tasks: Service Provider Management — Requirements Document

## 3.1 Create Service Provider
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can upload a **logo** image for the service provider. Logo is optional.
- [ ] Ensure UI supports: **Partner name** is a required field.
- [ ] Ensure UI supports: **Email** is a required field. The system must validate it is in a valid email format.
- [ ] Ensure UI supports: **Contact number** is a required field. It includes a country code selector (flag + dial code) and the number.
- [ ] Ensure UI supports: **Fax number** is an optional field.
- [ ] Ensure UI supports: **Address** is a required field.
- [ ] Ensure UI supports: **Website** is an optional field.
- [ ] Ensure UI supports: A service provider supports two contact persons — **Primary** and **Secondary**.
- [ ] Ensure UI supports: **Contact type** is a required field and is fixed to either `Primary` or `Secondary`.
- [ ] Ensure UI supports: **Salutation** is a required field for each contact person (e.g. Mr., Mrs., Ms., Dr.).
- [ ] Ensure UI supports: **Contact person name** is a required field.
- [ ] Ensure UI supports: **Contact number** is a required field for each contact person. It includes a country code selector and the number.
- [ ] Ensure UI supports: **Role** is an optional field for each contact person.
- [ ] Ensure UI supports: **Email** is an optional field for each contact person.
- [ ] Ensure UI supports: **Remarks** is an optional field for each contact person.
- [ ] Ensure UI supports: **Account holder name** is an optional field.
- [ ] Ensure UI supports: **Bank name** is an optional field.
- [ ] Ensure UI supports: **Account number** is an optional field.
- [ ] Ensure UI supports: **Bank branch** is an optional field.
- [ ] Ensure UI supports: **IBAN / Swift code** is an optional field (for international use).
- [ ] Ensure UI supports: **Payment gateway URL** is an optional field.
## 3.2 View Service Providers
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active service providers showing partner name, email, and contact number.
- [ ] Ensure UI supports: The service provider list supports search by partner name and email.
- [ ] Ensure UI supports: Users can view the full detail of a single service provider including all three sections.
- [ ] Ensure UI supports: Soft-deleted service providers are hidden from the default list view.
## 3.3 Service Provider Detail — Insurer Products
- [ ] Implement UI for 3.3 Service Provider Detail — Insurer Products.

- [ ] Ensure UI supports: The service provider detail view includes an **Insurer Products** section listing all active insurer products linked to that service provider.
- [ ] Ensure UI supports: Each insurer product entry displays: product name, risk type, coverage level, currency, and last update date.
- [ ] Ensure UI supports: If no insurer products are linked to the service provider, the section displays an empty state message.
- [ ] Ensure UI supports: The insurer products list within the detail view supports search by product name.
- [ ] Ensure UI supports: Soft-deleted insurer products are not shown in this list.
- [ ] Ensure UI supports: Each insurer product entry in the list links to the full insurer product detail view.
## 3.4 Edit Service Provider
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit all fields across the general information, contact persons, and bank account info sections.
- [ ] Ensure UI supports: All mandatory field rules from creation apply during edit.
- [ ] Ensure UI supports: Soft-deleted service providers cannot be edited.
## 3.5 Duplicate Service Provider
- [ ] Implement UI for 3.5 Duplicate Service Provider.

- [ ] Ensure UI supports: Users can duplicate an existing service provider to create an independent copy.
- [ ] Ensure UI supports: The duplicate copies all fields across all three sections, with the partner name suffixed to indicate it is a copy.
- [ ] Ensure UI supports: The duplicate is a fully independent record — changes to it do not affect the original.
## 3.6 Delete Service Provider
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete a service provider.
- [ ] Ensure UI supports: Soft-deleted service providers are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure UI supports: Hard deletion is not supported.
## General Information
- [ ] Implement UI for General Information.

## Contact Person (Primary & Secondary)
- [ ] Implement UI for Contact Person (Primary & Secondary).

## Bank Account Info
- [ ] Implement UI for Bank Account Info.

- [ ] Ensure UI supports: All create, edit, duplicate, and delete actions must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure UI supports: Uploaded logo images must be validated for file type (JPG, PNG) and size limits.
- [ ] Ensure UI supports: Soft-deleted service providers must be retained indefinitely for audit purposes.
- [ ] Ensure UI supports: Contact number fields must support international formats via country code selector.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
