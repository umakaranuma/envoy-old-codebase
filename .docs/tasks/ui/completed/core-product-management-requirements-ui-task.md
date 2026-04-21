# UI Tasks: Product Management — Requirements Document

## 3.1 Insurer Product — Create
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can create a new insurer product by providing the required fields listed below.
- [ ] Ensure UI supports: **Product name** is a required field and must be unique.
- [ ] Ensure UI supports: **Risk type (product category)** is a required field — selected from active product categories.
- [ ] Ensure UI supports: **Insurer info (service provider)** is a required field — selected from active service providers.
- [ ] Ensure UI supports: **Coverage level** is a required field — selected from seeded values: `Basic`, `Plus`, `Premium`.
- [ ] Ensure UI supports: **Description** is a required field.
- [ ] Ensure UI supports: **Remarks** is an optional field.
- [ ] Ensure UI supports: **Currency** is a required field — selected from available currencies.
- [ ] Ensure UI supports: **Last update date** is a required field — a date picker defaulting to today's date.
- [ ] Ensure UI supports: **Terms & Conditions** is an optional file upload field (PDF or document).
## 3.2 Insurer Product — Product Items Assignment
- [ ] Implement UI for 3.2 Insurer Product — Product Items Assignment.

- [ ] Ensure UI supports: After an insurer product is created, users can assign product items to it.
- [ ] Ensure UI supports: Each product item has: **title** (required), **category** (required), and **description** (optional).
- [ ] Ensure UI supports: The product item **category** is seeded with fixed values: `Benefits`, `Limitations`, `Exclusions`, `Other Conditions`.
- [ ] Ensure UI supports: Multiple product items can be assigned to a single insurer product.
- [ ] Ensure UI supports: Product items can be added, edited, and removed from the insurer product at any time.
- [ ] Ensure UI supports: The insurer product detail view displays all assigned product items grouped by category.
## 3.3 Insurer Product — View
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active insurer products showing product name, risk type, insurer, and coverage level.
- [ ] Ensure UI supports: The list supports search by product name.
- [ ] Ensure UI supports: The list can be filtered by risk type, insurer, and coverage level.
- [ ] Ensure UI supports: Users can view the full detail of a single insurer product including all fields and assigned product items.
- [ ] Ensure UI supports: Soft-deleted insurer products are hidden from the default list view.
## 3.4 Insurer Product — Edit
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit all fields of an existing insurer product.
- [ ] Ensure UI supports: All mandatory field rules from creation apply during edit.
- [ ] Ensure UI supports: Soft-deleted insurer products cannot be edited.
## 3.5 Insurer Product — Delete
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete an insurer product.
- [ ] Ensure UI supports: Soft-deleted insurer products are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure UI supports: Hard deletion is not supported.
## 3.6 Native Product — Create
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can create a new native product by providing the required fields listed below.
- [ ] Ensure UI supports: **Product name** is a required field and must be unique.
- [ ] Ensure UI supports: **Risk type (product category)** is a required field — selected from active product categories.
- [ ] Ensure UI supports: Based on the selected risk type, the user must select one or more **insurer products** that are linked to that risk type.
- [ ] Ensure UI supports: The insurer product selection list is filtered to show only active insurer products matching the selected risk type.
- [ ] Ensure UI supports: The **service provider (insurer)** is automatically saved based on the selected insurer product(s).
- [ ] Ensure UI supports: At least one insurer product must be selected before the native product can be saved.
## 3.7 Native Product — View
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active native products showing product name and risk type.
- [ ] Ensure UI supports: The list supports search by product name.
- [ ] Ensure UI supports: The list can be filtered by risk type.
- [ ] Ensure UI supports: Users can view the full detail of a single native product including its linked insurer products and service providers.
- [ ] Ensure UI supports: Soft-deleted native products are hidden from the default list view.
## 3.8 Native Product — Edit
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit all fields of an existing native product including the linked insurer products.
- [ ] Ensure UI supports: All mandatory field rules from creation apply during edit.
- [ ] Ensure UI supports: If the risk type is changed, the insurer product selection must be reset and re-selected based on the new risk type.
- [ ] Ensure UI supports: Soft-deleted native products cannot be edited.
## 3.9 Native Product — Delete
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete a native product.
- [ ] Ensure UI supports: Soft-deleted native products are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure UI supports: Hard deletion is not supported.
## 3.10 Product Group — Create
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can create a new product group by providing the required fields listed below.
- [ ] Ensure UI supports: **Group name** is a required field and must be unique.
- [ ] Ensure UI supports: One or more **native products** must be selected and assigned to the group at creation time.
- [ ] Ensure UI supports: **Currency** is a required field — selected from available currencies.
- [ ] Ensure UI supports: One or more **sales teams** must be selected and assigned to the group at creation time.
- [ ] Ensure UI supports: A product group cannot be saved without at least one native product and one sales team selected.
## 3.11 Product Group — View
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active product groups showing group name, currency, and assigned team count.
- [ ] Ensure UI supports: The list supports search by group name.
- [ ] Ensure UI supports: Users can view the full detail of a single product group including all assigned native products and sales teams.
- [ ] Ensure UI supports: Soft-deleted product groups are hidden from the default list view.
## 3.12 Product Group — Edit
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit the group name, native products, currency, and sales teams of an existing product group.
- [ ] Ensure UI supports: All mandatory field rules from creation apply during edit.
- [ ] Ensure UI supports: Soft-deleted product groups cannot be edited.
## 3.13 Product Group — Delete
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete a product group.
- [ ] Ensure UI supports: Soft-deleted product groups are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure UI supports: Hard deletion is not supported.
## Insurer Product
- [ ] Implement UI for Insurer Product.

## Insurer Product Item
- [ ] Implement UI for Insurer Product Item.

## Native Product
- [ ] Implement UI for Native Product.

## Product Group
- [ ] Implement UI for Product Group.

- [ ] Ensure UI supports: All create, edit, and delete actions across all product types must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure UI supports: Product name uniqueness must be enforced at the database level per product type.
- [ ] Ensure UI supports: Soft-deleted records must be retained indefinitely for audit purposes.
- [ ] Ensure UI supports: Insurer product selection in native product creation must dynamically filter based on the selected risk type.
- [ ] Ensure UI supports: Seeded values (coverage level, product item category) must be pre-loaded at system initialisation and protected from modification.
- [ ] Ensure UI supports: Uploaded Terms & Conditions files must be validated for allowed file types and size limits.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Antigravity | Full UI implementation with list, forms, and API integration. |
| Testing | Completed | Antigravity | Manual verification of UI components and flow. |
