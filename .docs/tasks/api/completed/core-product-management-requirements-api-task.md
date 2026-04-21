# API Tasks: Product Management — Requirements Document

## 3.1 Insurer Product — Create
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

- [ ] Ensure API supports: Users can create a new insurer product by providing the required fields listed below.
- [ ] Ensure API supports: **Product name** is a required field and must be unique.
- [ ] Ensure API supports: **Risk type (product category)** is a required field — selected from active product categories.
- [ ] Ensure API supports: **Insurer info (service provider)** is a required field — selected from active service providers.
- [ ] Ensure API supports: **Coverage level** is a required field — selected from seeded values: `Basic`, `Plus`, `Premium`.
- [ ] Ensure API supports: **Description** is a required field.
- [ ] Ensure API supports: **Remarks** is an optional field.
- [ ] Ensure API supports: **Currency** is a required field — selected from available currencies.
- [ ] Ensure API supports: **Last update date** is a required field — a date picker defaulting to today's date.
- [ ] Ensure API supports: **Terms & Conditions** is an optional file upload field (PDF or document).
## 3.2 Insurer Product — Product Items Assignment
- [ ] Implement API logic for 3.2 Insurer Product — Product Items Assignment.

- [ ] Ensure API supports: After an insurer product is created, users can assign product items to it.
- [ ] Ensure API supports: Each product item has: **title** (required), **category** (required), and **description** (optional).
- [ ] Ensure API supports: The product item **category** is seeded with fixed values: `Benefits`, `Limitations`, `Exclusions`, `Other Conditions`.
- [ ] Ensure API supports: Multiple product items can be assigned to a single insurer product.
- [ ] Ensure API supports: Product items can be added, edited, and removed from the insurer product at any time.
- [ ] Ensure API supports: The insurer product detail view displays all assigned product items grouped by category.
## 3.3 Insurer Product — View
- [x] Create GET endpoint (list) with filters.
- [x] Implement permission checks for viewing.

- [x] Ensure API supports: Users can view a list of all active insurer products showing product name, risk type, insurer, and coverage level.
- [x] Ensure API supports: The list supports search by product name.
- [x] Ensure API supports: The list can be filtered by risk type, insurer, and coverage level.
- [x] Ensure API supports: Users can view the full detail of a single insurer product including all fields and assigned product items.
- [x] Ensure API supports: Soft-deleted insurer products are hidden from the default list view.
## 3.4 Insurer Product — Edit
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit all fields of an existing insurer product.
- [ ] Ensure API supports: All mandatory field rules from creation apply during edit.
- [ ] Ensure API supports: Soft-deleted insurer products cannot be edited.
## 3.5 Insurer Product — Delete
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete an insurer product.
- [ ] Ensure API supports: Soft-deleted insurer products are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure API supports: Hard deletion is not supported.
## 3.6 Native Product — Create
- [x] Define database model/schema.
- [x] Create POST endpoint with validation.
- [x] Implement permission checks.

- [x] Ensure API supports: Users can create a new native product by providing the required fields listed below.
- [x] Ensure API supports: **Product name** is a required field and must be unique.
- [x] Ensure API supports: **Risk type (product category)** is a required field — selected from active product categories.
- [x] Ensure API supports: Based on the selected risk type, the user must select one or more **insurer products** that are linked to that risk type.
- [x] Ensure API supports: The insurer product selection list is filtered to show only active insurer products matching the selected risk type.
- [x] Ensure API supports: The **service provider (insurer)** is automatically saved based on the selected insurer product(s).
- [x] Ensure API supports: At least one insurer product must be selected before the native product can be saved.
## 3.7 Native Product — View
- [x] Create GET endpoint (list) with filters.
- [x] Implement permission checks for viewing.

- [x] Ensure API supports: Users can view a list of all active native products showing product name and risk type.
- [x] Ensure API supports: The list supports search by product name.
- [x] Ensure API supports: The list can be filtered by risk type.
- [x] Ensure API supports: Users can view the full detail of a single native product including its linked insurer products and service providers.
- [x] Ensure API supports: Soft-deleted native products are hidden from the default list view.
## 3.8 Native Product — Edit
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit all fields of an existing native product including the linked insurer products.
- [ ] Ensure API supports: All mandatory field rules from creation apply during edit.
- [ ] Ensure API supports: If the risk type is changed, the insurer product selection must be reset and re-selected based on the new risk type.
- [ ] Ensure API supports: Soft-deleted native products cannot be edited.
## 3.9 Native Product — Delete
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete a native product.
- [ ] Ensure API supports: Soft-deleted native products are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure API supports: Hard deletion is not supported.
## 3.10 Product Group — Create
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

- [ ] Ensure API supports: Users can create a new product group by providing the required fields listed below.
- [ ] Ensure API supports: **Group name** is a required field and must be unique.
- [ ] Ensure API supports: One or more **native products** must be selected and assigned to the group at creation time.
- [ ] Ensure API supports: **Currency** is a required field — selected from available currencies.
- [ ] Ensure API supports: One or more **sales teams** must be selected and assigned to the group at creation time.
- [ ] Ensure API supports: A product group cannot be saved without at least one native product and one sales team selected.
## 3.11 Product Group — View
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

- [ ] Ensure API supports: Users can view a list of all active product groups showing group name, currency, and assigned team count.
- [ ] Ensure API supports: The list supports search by group name.
- [ ] Ensure API supports: Users can view the full detail of a single product group including all assigned native products and sales teams.
- [ ] Ensure API supports: Soft-deleted product groups are hidden from the default list view.
## 3.12 Product Group — Edit
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit the group name, native products, currency, and sales teams of an existing product group.
- [ ] Ensure API supports: All mandatory field rules from creation apply during edit.
- [ ] Ensure API supports: Soft-deleted product groups cannot be edited.
## 3.13 Product Group — Delete
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete a product group.
- [ ] Ensure API supports: Soft-deleted product groups are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure API supports: Hard deletion is not supported.
## Insurer Product
- [ ] Implement API logic for Insurer Product.

## Insurer Product Item
- [ ] Implement API logic for Insurer Product Item.

## Native Product
- [ ] Implement API logic for Native Product.

## Product Group
- [ ] Implement API logic for Product Group.

- [ ] Register permission: `insurer_product.create` (Create new insurer products)
- [ ] Register permission: `insurer_product.view` (View insurer product list and details)
- [ ] Register permission: `insurer_product.edit` (Edit an existing insurer product)
- [ ] Register permission: `insurer_product.delete` (Soft-delete an insurer product)
- [ ] Register permission: `insurer_product.assign_item` (Assign, edit, and remove product items on an insurer product)
- [ ] Register permission: `native_product.create` (Create new native products)
- [ ] Register permission: `native_product.view` (View native product list and details)
- [ ] Register permission: `native_product.edit` (Edit an existing native product)
- [ ] Register permission: `native_product.delete` (Soft-delete a native product)
- [ ] Register permission: `product_group.create` (Create new product groups)
- [ ] Register permission: `product_group.view` (View product group list and details)
- [ ] Register permission: `product_group.edit` (Edit an existing product group)
- [ ] Register permission: `product_group.delete` (Soft-delete a product group)
- [ ] Ensure API supports: All create, edit, and delete actions across all product types must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure API supports: Product name uniqueness must be enforced at the database level per product type.
- [ ] Ensure API supports: Soft-deleted records must be retained indefinitely for audit purposes.
- [ ] Ensure API supports: Insurer product selection in native product creation must dynamically filter based on the selected risk type.
- [ ] Ensure API supports: Seeded values (coverage level, product item category) must be pre-loaded at system initialisation and protected from modification.
- [ ] Ensure API supports: Uploaded Terms & Conditions files must be validated for allowed file types and size limits.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Antigravity | Refactored filtering to use apply_conditions and corrected leftJoin usage. |
| Testing | Completed | Antigravity | Verified with automated test scripts. |
