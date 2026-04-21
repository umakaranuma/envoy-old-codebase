# UI Tasks: Reason Management — Requirements Document

## 3.1 Reason Type — Create
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can create a new reason type by providing a name and an optional description.
- [ ] Ensure UI supports: Name is a required field; the form cannot be submitted without it.
- [ ] Ensure UI supports: Description is an optional field.
- [ ] Ensure UI supports: Duplicate reason type names should be flagged with a warning, but creation may still proceed (not a hard block).
## 3.2 Reason Type — View
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active reason types showing name and description.
- [ ] Ensure UI supports: The reason type list supports search by name.
- [ ] Ensure UI supports: Seeded (system) reason types are visually distinguished from user-created types (e.g. a "System" badge).
- [ ] Ensure UI supports: Soft-deleted reason types are hidden from the default list view.
## 3.3 Reason Type — Edit
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit the name and description of a user-created reason type.
- [ ] Ensure UI supports: Seeded (system) reason types cannot be edited.
- [ ] Ensure UI supports: Name remains mandatory during edit; it cannot be cleared.
- [ ] Ensure UI supports: Soft-deleted reason types cannot be edited.
## 3.4 Reason Type — Delete
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete a user-created reason type.
- [ ] Ensure UI supports: Seeded (system) reason types cannot be deleted.
- [ ] Ensure UI supports: If a reason type has active reasons linked to it, the system must warn the user before allowing deletion.
- [ ] Ensure UI supports: Soft-deleted reason types are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure UI supports: Hard deletion is not supported.
## 3.5 Reason — Create
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can create a new reason by providing a reason text, selecting a reason type, toggling allow customer reason, and optionally providing a description.
- [ ] Ensure UI supports: Reason text is a required field; the form cannot be submitted without it.
- [ ] Ensure UI supports: Reason type is a required field; a reason cannot be created without selecting a type.
- [ ] Ensure UI supports: Only active reason types are available for selection when creating a reason.
- [ ] Ensure UI supports: The **allow customer reason** toggle defaults to off (disabled) at creation time.
- [ ] Ensure UI supports: Description is an optional field.
- [ ] Ensure UI supports: Reason text must be unique within the selected reason type; a duplicate within the same type is a hard block.
## 3.6 Reason — View
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active reasons showing reason text, reason type, allow customer reason status, and description.
- [ ] Ensure UI supports: The reason list supports search by reason text.
- [ ] Ensure UI supports: The reason list can be filtered by reason type.
- [ ] Ensure UI supports: The reason list can be filtered by allow customer reason (yes / no).
- [ ] Ensure UI supports: Soft-deleted reasons are hidden from the default list view.
## 3.7 Reason — Edit
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit the reason text, reason type, allow customer reason toggle, and description of an existing reason.
- [ ] Ensure UI supports: Reason text remains mandatory during edit; it cannot be cleared.
- [ ] Ensure UI supports: Reason type remains mandatory during edit; it cannot be cleared.
- [ ] Ensure UI supports: If the reason type is changed, the uniqueness check is re-applied against the new type.
- [ ] Ensure UI supports: Soft-deleted reasons cannot be edited.
## 3.8 Reason — Delete
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete a reason.
- [ ] Ensure UI supports: Soft-deleted reasons are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure UI supports: Hard deletion is not supported.
- [ ] Ensure UI supports: All create, edit, and delete actions on both reason types and reasons must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure UI supports: Seeded reason types must be pre-loaded at system initialisation and protected from modification or deletion.
- [ ] Ensure UI supports: Soft-deleted reason types and reasons must be retained indefinitely for audit purposes.
- [ ] Ensure UI supports: Reason text uniqueness must be enforced at the database level within each reason type.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Agent | Built Reason and ReasonType management. |
| Testing | Pending |  | |
