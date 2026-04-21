# API Tasks: Product Item Management — Requirements Document

## 3.1 Create Product Item
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

- [ ] Ensure API supports: Users can create a new product item by providing a title, selecting a category, and optionally providing a description.
- [ ] Ensure API supports: **Title** is a required field; the form cannot be submitted without it.
- [ ] Ensure API supports: **Category** is a required field — selected from seeded values: `Benefits`, `Limitations`, `Exclusions`, `Other Conditions`.
- [ ] Ensure API supports: **Description** is an optional field.
- [ ] Ensure API supports: Duplicate titles within the same category should be flagged with a warning, but creation may still proceed (not a hard block).
## 3.2 View Product Items
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

- [ ] Ensure API supports: Users can view a list of all active product items showing title, category, and description.
- [ ] Ensure API supports: The product item list supports search by title.
- [ ] Ensure API supports: The product item list can be filtered by category.
- [ ] Ensure API supports: Soft-deleted product items are hidden from the default list view.
## 3.3 Edit Product Item
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit the title, category, and description of an existing product item.
- [ ] Ensure API supports: Title remains mandatory during edit; it cannot be cleared.
- [ ] Ensure API supports: Category remains mandatory during edit; it cannot be cleared.
- [ ] Ensure API supports: Soft-deleted product items cannot be edited.
## 3.4 Delete Product Item
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete a product item.
- [ ] Ensure API supports: Soft-deleted product items are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure API supports: Hard deletion is not supported.
- [ ] Register permission: `product_item.create` (Create new product items)
- [ ] Register permission: `product_item.view` (View product item list and details)
- [ ] Register permission: `product_item.edit` (Edit an existing product item's title, category, and description)
- [ ] Register permission: `product_item.delete` (Soft-delete a product item)
- [ ] Ensure API supports: All create, edit, and delete actions must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure API supports: Soft-deleted product items must be retained indefinitely for audit purposes.
- [ ] Ensure API supports: Category seeded values (`Benefits`, `Limitations`, `Exclusions`, `Other Conditions`) must be pre-loaded at system initialisation and protected from modification.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
