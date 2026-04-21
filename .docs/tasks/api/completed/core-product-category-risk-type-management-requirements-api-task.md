# API Tasks: Product Category (Risk Type) Management — Requirements Document

## 3.1 Create Product Category
- [x] Define database model/schema.
- [x] Create POST endpoint with validation.
- [x] Implement permission checks.

- [x] Ensure API supports: Users can create a new product category by providing a title and an optional description.
- [x] Ensure API supports: Title is a required field; the form cannot be submitted without it.
- [x] Ensure API supports: Title must be unique; a duplicate title is a hard block and cannot be saved.
- [x] Ensure API supports: Description is an optional field.
## 3.2 View Product Categories
- [x] Create GET endpoint (list) with filters.
- [x] Implement permission checks for viewing.

- [x] Ensure API supports: Users can view a list of all active product categories showing title and description.
- [x] Ensure API supports: The product category list supports search by title.
- [x] Ensure API supports: Users can view the full detail of a single product category including its assigned templates per assignment type.
- [x] Ensure API supports: Soft-deleted product categories are hidden from the default list view.
## 3.3 Edit Product Category
- [x] Create PUT/PATCH endpoint with validation.
- [x] Implement permission checks for editing.

- [x] Ensure API supports: Users can edit the title and description of an existing product category.
- [x] Ensure API supports: Title remains mandatory and unique during edit; it cannot be cleared or set to a duplicate value.
- [x] Ensure API supports: Soft-deleted product categories cannot be edited.
## 3.4 Delete Product Category
- [x] Create DELETE endpoint.
- [x] Implement permission checks for deletion.

- [x] Ensure API supports: Users can soft-delete a product category.
- [x] Ensure API supports: Soft-deleted product categories are deactivated and hidden from the default list but retained in the system.
- [x] Ensure API supports: Hard deletion is not supported.
## 3.5 Template Assignment
- [x] Implement API logic for 3.5 Template Assignment.

- [x] Ensure API supports: After a product category is created, users can assign templates to it for each seeded assignment type.
- [x] Ensure API supports: The seeded assignment types are: `ONBOARDING`, `CLAIM`, and `CLAIM_EVALUATION`. These types are system-managed and cannot be added, edited, or removed by users.
- [x] Ensure API supports: For each assignment type, only **one template** can be assigned to a product category at a time.
- [x] Ensure API supports: Any active template from the Template Management section can be selected for assignment.
- [x] Ensure API supports: If an assignment type already has a template assigned, assigning a new template replaces the existing one.
- [x] Ensure API supports: Users can remove a template assignment from an assignment type, leaving that type unassigned.
- [x] Ensure API supports: The product category detail view displays all three assignment types and their currently assigned template (or unassigned if none).
- [x] Ensure API supports: Template assignment and removal actions are recorded in the audit log.
- [x] Register permission: `onboarding` (Template used during customer or policy onboarding for this risk type)
- [x] Register permission: `claim` (Template used when a claim is submitted for this risk type)
- [x] Register permission: `claim_evaluation` (Template used during the evaluation of a claim for this risk type)
- [x] Register permission: `risk_type.create` (Create new product categories)
- [x] Register permission: `risk_type.view` (View product category list and details including template assignments)
- [x] Register permission: `risk_type.edit` (Edit an existing product category's title and description)
- [x] Register permission: `risk_type.delete` (Soft-delete a product category)
- [x] Register permission: `risk_type.assign_template` (Assign or remove templates on a product category)
- [x] Ensure API supports: All create, edit, delete, and template assignment actions must be recorded in the audit log with the acting user and timestamp.
- [x] Ensure API supports: Title uniqueness must be enforced at the database level.
- [x] Ensure API supports: Seeded assignment types must be pre-loaded at system initialisation and protected from modification or deletion.
- [x] Ensure API supports: Soft-deleted product categories must be retained indefinitely for audit purposes.
- [x] Ensure API supports: Only active (non-soft-deleted) templates must appear in the template selection dropdown during assignment.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Antigravity | Implemented full CRUD and unified form configuration system. |
| Testing | Completed | Antigravity | Verified migrations, endpoints, and frontend integration. |
