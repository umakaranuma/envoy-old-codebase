# UI Tasks: Product Category (Risk Type) Management — Requirements Document

## 3.1 Create Product Category
- [x] Build form component for creating record.
- [x] Implement form validation rules.
- [x] Integrate POST API and handle success/error states.

- [x] Ensure UI supports: Users can create a new product category by providing a title and an optional description.
- [x] Ensure UI supports: Title is a required field; the form cannot be submitted without it.
- [x] Ensure UI supports: Title must be unique; a duplicate title is a hard block and cannot be saved.
- [x] Ensure UI supports: Description is an optional field.
## 3.2 View Product Categories
- [x] Build data table/list view component.
- [x] Implement search/filtering/pagination UI.
- [x] fetch data from GET API.

- [x] Ensure UI supports: Users can view a list of all active product categories showing title and description.
- [x] Ensure UI supports: The product category list supports search by title.
- [x] Ensure UI supports: Users can view the full detail of a single product category including its assigned templates per assignment type.
- [x] Ensure UI supports: Soft-deleted product categories are hidden from the default list view.
## 3.3 Edit Product Category
- [x] Build edit form component.
- [x] Integrate PUT/PATCH API and handle success/error states.

- [x] Ensure UI supports: Users can edit the title and description of an existing product category.
- [x] Ensure UI supports: Title remains mandatory and unique during edit; it cannot be cleared or set to a duplicate value.
- [x] Ensure UI supports: Soft-deleted product categories cannot be edited.
## 3.4 Delete Product Category
- [x] Build deletion confirmation modal.
- [x] Integrate DELETE API and handle success/error states.

- [x] Ensure UI supports: Users can soft-delete a product category.
- [x] Ensure UI supports: Soft-deleted product categories are deactivated and hidden from the default list but retained in the system.
- [x] Ensure UI supports: Hard deletion is not supported.
## 3.5 Template Assignment
- [x] Implement UI for 3.5 Template Assignment.

- [x] Ensure UI supports: After a product category is created, users can assign templates to it for each seeded assignment type.
- [x] Ensure UI supports: The seeded assignment types are: `ONBOARDING`, `CLAIM`, and `CLAIM_EVALUATION`. These types are system-managed and cannot be added, edited, or removed by users.
- [x] Ensure UI supports: For each assignment type, only **one template** can be assigned to a product category at a time.
- [x] Ensure UI supports: Any active template from the Template Management section can be selected for assignment.
- [x] Ensure UI supports: If an assignment type already has a template assigned, assigning a new template replaces the existing one.
- [x] Ensure UI supports: Users can remove a template assignment from an assignment type, leaving that type unassigned.
- [x] Ensure UI supports: The product category detail view displays all three assignment types and their currently assigned template (or unassigned if none).
- [x] Ensure UI supports: Template assignment and removal actions are recorded in the audit log.
- [x] Ensure UI supports: All create, edit, delete, and template assignment actions must be recorded in the audit log with the acting user and timestamp.
- [x] Ensure UI supports: Title uniqueness must be enforced at the database level.
- [x] Ensure UI supports: Seeded assignment types must be pre-loaded at system initialisation and protected from modification or deletion.
- [x] Ensure UI supports: Soft-deleted product categories must be retained indefinitely for audit purposes.
- [x] Ensure UI supports: Only active (non-soft-deleted) templates must appear in the template selection dropdown during assignment.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Antigravity | Implemented full CRUD and unified stacked detail view for form configurations. |
| Testing | Completed | Antigravity | Verified unified layout and assignments. |
