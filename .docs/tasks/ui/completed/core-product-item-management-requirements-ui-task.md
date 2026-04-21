# UI Tasks: Product Item Management — Requirements Document

## 3.1 Create Product Item
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can create a new product item by providing a title, selecting a category, and optionally providing a description.
- [ ] Ensure UI supports: **Title** is a required field; the form cannot be submitted without it.
- [ ] Ensure UI supports: **Category** is a required field — selected from seeded values: `Benefits`, `Limitations`, `Exclusions`, `Other Conditions`.
- [ ] Ensure UI supports: **Description** is an optional field.
- [ ] Ensure UI supports: Duplicate titles within the same category should be flagged with a warning, but creation may still proceed (not a hard block).
## 3.2 View Product Items
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active product items showing title, category, and description.
- [ ] Ensure UI supports: The product item list supports search by title.
- [ ] Ensure UI supports: The product item list can be filtered by category.
- [ ] Ensure UI supports: Soft-deleted product items are hidden from the default list view.
## 3.3 Edit Product Item
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit the title, category, and description of an existing product item.
- [ ] Ensure UI supports: Title remains mandatory during edit; it cannot be cleared.
- [ ] Ensure UI supports: Category remains mandatory during edit; it cannot be cleared.
- [ ] Ensure UI supports: Soft-deleted product items cannot be edited.
## 3.4 Delete Product Item
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete a product item.
- [ ] Ensure UI supports: Soft-deleted product items are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure UI supports: Hard deletion is not supported.
- [ ] Ensure UI supports: All create, edit, and delete actions must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure UI supports: Soft-deleted product items must be retained indefinitely for audit purposes.
- [ ] Ensure UI supports: Category seeded values (`Benefits`, `Limitations`, `Exclusions`, `Other Conditions`) must be pre-loaded at system initialisation and protected from modification.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Antigravity | Redesigned to Vanguard X standards |
| Testing | Completed | Antigravity | Verified creation, listing, editing, and deletion |
