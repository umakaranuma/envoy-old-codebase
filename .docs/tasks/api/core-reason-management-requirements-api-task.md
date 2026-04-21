# API Tasks: Reason Management — Requirements Document

## 3.1 Reason Type — Create
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

- [ ] Ensure API supports: Users can create a new reason type by providing a name and an optional description.
- [ ] Ensure API supports: Name is a required field; the form cannot be submitted without it.
- [ ] Ensure API supports: Description is an optional field.
- [ ] Ensure API supports: Duplicate reason type names should be flagged with a warning, but creation may still proceed (not a hard block).
## 3.2 Reason Type — View
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

- [ ] Ensure API supports: Users can view a list of all active reason types showing name and description.
- [ ] Ensure API supports: The reason type list supports search by name.
- [ ] Ensure API supports: Seeded (system) reason types are visually distinguished from user-created types (e.g. a "System" badge).
- [ ] Ensure API supports: Soft-deleted reason types are hidden from the default list view.
## 3.3 Reason Type — Edit
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit the name and description of a user-created reason type.
- [ ] Ensure API supports: Seeded (system) reason types cannot be edited.
- [ ] Ensure API supports: Name remains mandatory during edit; it cannot be cleared.
- [ ] Ensure API supports: Soft-deleted reason types cannot be edited.
## 3.4 Reason Type — Delete
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete a user-created reason type.
- [ ] Ensure API supports: Seeded (system) reason types cannot be deleted.
- [ ] Ensure API supports: If a reason type has active reasons linked to it, the system must warn the user before allowing deletion.
- [ ] Ensure API supports: Soft-deleted reason types are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure API supports: Hard deletion is not supported.
## 3.5 Reason — Create
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

- [ ] Ensure API supports: Users can create a new reason by providing a reason text, selecting a reason type, toggling allow customer reason, and optionally providing a description.
- [ ] Ensure API supports: Reason text is a required field; the form cannot be submitted without it.
- [ ] Ensure API supports: Reason type is a required field; a reason cannot be created without selecting a type.
- [ ] Ensure API supports: Only active reason types are available for selection when creating a reason.
- [ ] Ensure API supports: The **allow customer reason** toggle defaults to off (disabled) at creation time.
- [ ] Ensure API supports: Description is an optional field.
- [ ] Ensure API supports: Reason text must be unique within the selected reason type; a duplicate within the same type is a hard block.
## 3.6 Reason — View
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

- [ ] Ensure API supports: Users can view a list of all active reasons showing reason text, reason type, allow customer reason status, and description.
- [ ] Ensure API supports: The reason list supports search by reason text.
- [ ] Ensure API supports: The reason list can be filtered by reason type.
- [ ] Ensure API supports: The reason list can be filtered by allow customer reason (yes / no).
- [ ] Ensure API supports: Soft-deleted reasons are hidden from the default list view.
## 3.7 Reason — Edit
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit the reason text, reason type, allow customer reason toggle, and description of an existing reason.
- [ ] Ensure API supports: Reason text remains mandatory during edit; it cannot be cleared.
- [ ] Ensure API supports: Reason type remains mandatory during edit; it cannot be cleared.
- [ ] Ensure API supports: If the reason type is changed, the uniqueness check is re-applied against the new type.
- [ ] Ensure API supports: Soft-deleted reasons cannot be edited.
## 3.8 Reason — Delete
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete a reason.
- [ ] Ensure API supports: Soft-deleted reasons are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure API supports: Hard deletion is not supported.
- [ ] Register permission: `reason_type.create` (Create new reason types)
- [ ] Register permission: `reason_type.view` (View reason types list and details)
- [ ] Register permission: `reason_type.edit` (Edit user-created reason type name and description)
- [ ] Register permission: `reason_type.delete` (Soft-delete a user-created reason type)
- [ ] Register permission: `reason.create` (Create new reasons)
- [ ] Register permission: `reason.view` (View reasons list and details)
- [ ] Register permission: `reason.edit` (Edit an existing reason)
- [ ] Register permission: `reason.delete` (Soft-delete a reason)
- [ ] Ensure API supports: All create, edit, and delete actions on both reason types and reasons must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure API supports: Seeded reason types must be pre-loaded at system initialisation and protected from modification or deletion.
- [ ] Ensure API supports: Soft-deleted reason types and reasons must be retained indefinitely for audit purposes.
- [ ] Ensure API supports: Reason text uniqueness must be enforced at the database level within each reason type.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
