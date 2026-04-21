# Reason Management — Requirements Document

**Module:** Core
**Feature:** Reason Management
**Version:** 1.0
**Status:** Draft

---

## 1. Overview

The Reason Management feature allows authorized users to create and manage reasons and reason types within the system. Reasons are used across other modules (e.g. CRM, Policy, Claims) to record why a particular action or outcome occurred. Each reason belongs to a reason type, and can optionally be made available to customers through the customer portal via the **allow customer reason** toggle.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform reason and reason type management actions.

---

## 2. Key Rules

- A **reason type** holds: **name** and **description**.
- A **reason** holds: **reason** (the reason text), **reason type**, **description**, and **allow customer reason** (yes/no toggle).
- Reason type name is **mandatory**.
- Reason text is **mandatory**.
- Reason type is **mandatory** when creating a reason — it must be selected from existing active reason types.
- Description is **optional** on both reason types and reasons.
- The **allow customer reason** toggle controls whether the reason is visible and selectable in the customer portal. It defaults to off.
- Reason names must be **unique within a reason type** — the same reason text can exist under different types.
- Both reason types and reasons are **soft-deleted** — deactivated but not permanently removed.
- Seeded reason types are pre-loaded by the system and cannot be deleted, but users can create additional custom reason types.

---

## 3. Functional Requirements

### 3.1 Reason Type — Create

| # | Requirement | Permission |
|---|---|---|
| 3.1.1 | Users can create a new reason type by providing a name and an optional description. | `reason_type.create` |
| 3.1.2 | Name is a required field; the form cannot be submitted without it. | `reason_type.create` |
| 3.1.3 | Description is an optional field. | `reason_type.create` |
| 3.1.4 | Duplicate reason type names should be flagged with a warning, but creation may still proceed (not a hard block). | `reason_type.create` |

---

### 3.2 Reason Type — View

| # | Requirement | Permission |
|---|---|---|
| 3.2.1 | Users can view a list of all active reason types showing name and description. | `reason_type.view` |
| 3.2.2 | The reason type list supports search by name. | `reason_type.view` |
| 3.2.3 | Seeded (system) reason types are visually distinguished from user-created types (e.g. a "System" badge). | `reason_type.view` |
| 3.2.4 | Soft-deleted reason types are hidden from the default list view. | `reason_type.view` |

---

### 3.3 Reason Type — Edit

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | Users can edit the name and description of a user-created reason type. | `reason_type.edit` |
| 3.3.2 | Seeded (system) reason types cannot be edited. | — |
| 3.3.3 | Name remains mandatory during edit; it cannot be cleared. | `reason_type.edit` |
| 3.3.4 | Soft-deleted reason types cannot be edited. | — |

---

### 3.4 Reason Type — Delete

| # | Requirement | Permission |
|---|---|---|
| 3.4.1 | Users can soft-delete a user-created reason type. | `reason_type.delete` |
| 3.4.2 | Seeded (system) reason types cannot be deleted. | — |
| 3.4.3 | If a reason type has active reasons linked to it, the system must warn the user before allowing deletion. | `reason_type.delete` |
| 3.4.4 | Soft-deleted reason types are deactivated and hidden from the default list but retained in the system. | — |
| 3.4.5 | Hard deletion is not supported. | — |

---

### 3.5 Reason — Create

| # | Requirement | Permission |
|---|---|---|
| 3.5.1 | Users can create a new reason by providing a reason text, selecting a reason type, toggling allow customer reason, and optionally providing a description. | `reason.create` |
| 3.5.2 | Reason text is a required field; the form cannot be submitted without it. | `reason.create` |
| 3.5.3 | Reason type is a required field; a reason cannot be created without selecting a type. | `reason.create` |
| 3.5.4 | Only active reason types are available for selection when creating a reason. | `reason.create` |
| 3.5.5 | The **allow customer reason** toggle defaults to off (disabled) at creation time. | `reason.create` |
| 3.5.6 | Description is an optional field. | `reason.create` |
| 3.5.7 | Reason text must be unique within the selected reason type; a duplicate within the same type is a hard block. | `reason.create` |

---

### 3.6 Reason — View

| # | Requirement | Permission |
|---|---|---|
| 3.6.1 | Users can view a list of all active reasons showing reason text, reason type, allow customer reason status, and description. | `reason.view` |
| 3.6.2 | The reason list supports search by reason text. | `reason.view` |
| 3.6.3 | The reason list can be filtered by reason type. | `reason.view` |
| 3.6.4 | The reason list can be filtered by allow customer reason (yes / no). | `reason.view` |
| 3.6.5 | Soft-deleted reasons are hidden from the default list view. | `reason.view` |

---

### 3.7 Reason — Edit

| # | Requirement | Permission |
|---|---|---|
| 3.7.1 | Users can edit the reason text, reason type, allow customer reason toggle, and description of an existing reason. | `reason.edit` |
| 3.7.2 | Reason text remains mandatory during edit; it cannot be cleared. | `reason.edit` |
| 3.7.3 | Reason type remains mandatory during edit; it cannot be cleared. | `reason.edit` |
| 3.7.4 | If the reason type is changed, the uniqueness check is re-applied against the new type. | `reason.edit` |
| 3.7.5 | Soft-deleted reasons cannot be edited. | — |

---

### 3.8 Reason — Delete

| # | Requirement | Permission |
|---|---|---|
| 3.8.1 | Users can soft-delete a reason. | `reason.delete` |
| 3.8.2 | Soft-deleted reasons are deactivated and hidden from the default list but retained in the system. | — |
| 3.8.3 | Hard deletion is not supported. | — |

---

## 4. Permission Reference Table

| Permission Key | Description |
|---|---|
| `reason_type.create` | Create new reason types |
| `reason_type.view` | View reason types list and details |
| `reason_type.edit` | Edit user-created reason type name and description |
| `reason_type.delete` | Soft-delete a user-created reason type |
| `reason.create` | Create new reasons |
| `reason.view` | View reasons list and details |
| `reason.edit` | Edit an existing reason |
| `reason.delete` | Soft-delete a reason |

---

## 5. Non-Functional Requirements

| # | Requirement |
|---|---|
| 5.1 | All create, edit, and delete actions on both reason types and reasons must be recorded in the audit log with the acting user and timestamp. |
| 5.2 | Seeded reason types must be pre-loaded at system initialisation and protected from modification or deletion. |
| 5.3 | Soft-deleted reason types and reasons must be retained indefinitely for audit purposes. |
| 5.4 | Reason text uniqueness must be enforced at the database level within each reason type. |

---

## 6. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create a custom reason type with a name and description | I can group related reasons under a meaningful category |
| US-02 | Authorized user | Create a reason under a specific reason type | I can define the specific reasons used when recording outcomes in the system |
| US-03 | Authorized user | Toggle allow customer reason on a reason | I can control which reasons are visible and selectable by customers in the portal |
| US-04 | Authorized user | Filter reasons by type or customer visibility | I can quickly find the reasons relevant to a specific context |
| US-05 | Authorized user | Edit a reason's text, type, or description | I can keep reason definitions accurate as requirements change |
| US-06 | Authorized user | Soft-delete a reason or reason type | I can retire entries that are no longer needed without losing the audit trail |

---

## 7. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | Are reason types fixed/seeded only? | No — seeded types are pre-loaded by the system but users can also create custom reason types. |
| RD-02 | What is "allow customer reason"? | A yes/no toggle on each individual reason record that controls whether the reason is visible in the customer portal. Defaults to off. |
| RD-03 | What happens when a reason is deleted? | Soft delete only — deactivated but not permanently removed. |
| RD-04 | What happens when a reason type is deleted? | Soft delete only — deactivated but not permanently removed. Seeded types cannot be deleted. |
| RD-05 | Are reason names unique? | Yes — reason text must be unique within the same reason type. The same text can exist under a different type. |

---

## 8. Out of Scope

- Assigning reasons to specific records (e.g. lost leads, cancelled policies, claims) — handled by the respective modules that consume reasons.
- Bulk import of reason types or reasons.
- Reason analytics or reporting.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*

---

## 9. Task Summary Table

| Task Name | Status | Date Completed |
|---|---|---|
| Core Reason Management Implementation | **Completed** | 2026-03-23 |
