# Service Type Management — Requirements Document

**Module:** Core
**Feature:** Service Type Management
**Version:** 1.0
**Status:** Draft

---

## 1. Overview

The Service Type Management feature allows authorized users to create and manage service types within the system. A service type defines a category of service with a title, description, and standard fee. Service type records are backed by a shared entity table that stores audit metadata (timestamps and acting user), with the resulting entity ID stored as a foreign key on the service type record.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform service type management actions.

---

## 2. Key Rules

- A service type record holds: **title**, **description**, **standard fee**, and a foreign key reference to an **entity record** (`entity_id`).
- Title is **mandatory** when creating a service type.
- Standard fee is **mandatory** and must be a non-negative numeric value.
- Description is **optional**.
- On creation, an entity record is created first in the `core_entity` table (storing `created_at`, `updated_at`, `created_by`, `updated_by`). The resulting `entity_id` is then stored on the `core_service_type` record.
- Service types are **soft-deleted** — deactivated but not permanently removed.
- Service type titles should be unique; duplicate titles are flagged with a warning (not a hard block).

---

## 3. Data Model

### 3.1 `core_entity` Table

Stores shared audit metadata for entities across the system.

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID / BigInt (PK) | Yes | Auto-generated primary key |
| `created_at` | DateTime | Yes | Timestamp when the record was created |
| `updated_at` | DateTime | Yes | Timestamp of the last update |
| `created_by` | FK → User | Yes | The user who created the record |
| `updated_by` | FK → User | No | The user who last updated the record |

---

### 3.2 `core_service_type` Table

Stores the service type data with a reference to its entity record.

| Column | Type | Required | Notes |
|---|---|---|---|
| `id` | UUID / BigInt (PK) | Yes | Auto-generated primary key |
| `entity_id` | FK → `core_entity.id` | Yes | Reference to the associated entity audit record |
| `title` | VARCHAR | Yes | Name of the service type |
| `description` | TEXT | No | Optional description of the service type |
| `standard_fee` | DECIMAL | Yes | Default fee for this service type; must be ≥ 0 |
| `is_deleted` | Boolean | Yes | Soft delete flag; default `false` |
| `deleted_at` | DateTime | No | Timestamp of soft deletion, null if active |

---

## 4. Functional Requirements

### 4.1 Create Service Type

| # | Requirement | Permission |
|---|---|---|
| 4.1.1 | Users can create a new service type by providing a title, standard fee, and an optional description. | `service_type.create` |
| 4.1.2 | Title is a required field; the form cannot be submitted without it. | `service_type.create` |
| 4.1.3 | Standard fee is a required field; the form cannot be submitted without it. | `service_type.create` |
| 4.1.4 | Standard fee must be a non-negative numeric value (0 or greater). | `service_type.create` |
| 4.1.5 | Description is an optional field. | `service_type.create` |
| 4.1.6 | Duplicate service type titles should be flagged with a warning, but creation may still proceed (not a hard block). | `service_type.create` |
| 4.1.7 | On creation, a `core_entity` record is created first with `created_at`, `updated_at`, and `created_by` populated. The generated `entity_id` is stored on the `core_service_type` record. | `service_type.create` |

---

### 4.2 View Service Types

| # | Requirement | Permission |
|---|---|---|
| 4.2.1 | Users can view a paginated list of all active service types showing title, description, and standard fee. | `service_type.view` |
| 4.2.2 | The service type list supports search by title. | `service_type.view` |
| 4.2.3 | Soft-deleted service types are hidden from the default list view. | `service_type.view` |
| 4.2.4 | Users can view the full detail of a single service type. | `service_type.view` |

---

### 4.3 Edit Service Type

| # | Requirement | Permission |
|---|---|---|
| 4.3.1 | Users can edit the title, description, and standard fee of an existing service type. | `service_type.edit` |
| 4.3.2 | Title remains mandatory during edit; it cannot be cleared. | `service_type.edit` |
| 4.3.3 | Standard fee remains mandatory during edit; it cannot be cleared or set to a negative value. | `service_type.edit` |
| 4.3.4 | On update, the associated `core_entity` record's `updated_at` and `updated_by` fields are updated. | `service_type.edit` |
| 4.3.5 | Soft-deleted service types cannot be edited. | — |

---

### 4.4 Delete Service Type

| # | Requirement | Permission |
|---|---|---|
| 4.4.1 | Users can soft-delete a service type. | `service_type.delete` |
| 4.4.2 | Soft-deleted service types are deactivated and hidden from the default list but retained in the system. | — |
| 4.4.3 | Hard deletion is not supported. | — |
| 4.4.4 | A confirmation dialog is shown before soft deletion. | — |

---

## 5. UI Requirements

### 5.1 List View

- Displays a paginated table of all active service types.
- Columns: **Title**, **Description**, **Standard Fee**, **Created By**, **Created At**, **Actions**.
- Actions column includes **Edit** and **Delete** buttons, shown only to users with the respective permissions.
- Search bar for filtering by title.

### 5.2 Create / Edit Form

- Modal or dedicated page with fields: **Title** (required), **Standard Fee** (required), **Description** (optional).
- Inline validation — required fields highlighted on submit attempt.
- Duplicate title warning displayed without blocking submission.
- Cancel and Save buttons.

### 5.3 Delete Confirmation

- A confirmation dialog is shown before soft deletion:
  > *"Are you sure you want to delete [Title]? This action will deactivate the service type."*
- Confirm and Cancel buttons.

---

## 6. Permission Reference Table

| Permission Key | Description |
|---|---|
| `service_type.create` | Create new service types |
| `service_type.view` | View the service type list and individual details |
| `service_type.edit` | Edit an existing service type's title, description, and standard fee |
| `service_type.delete` | Soft-delete a service type |

---

## 7. Non-Functional Requirements

| # | Requirement |
|---|---|
| 7.1 | All create, edit, and delete actions must be recorded in the audit log with the acting user and timestamp. |
| 7.2 | Entity record creation and service type record creation must be atomic — either both succeed or neither is persisted. |
| 7.3 | Soft-deleted service types must be retained indefinitely for audit purposes. |
| 7.4 | Standard fee must be stored as a decimal type with sufficient precision for currency values. |
| 7.5 | All inputs must be validated on both the client and server side. |

---

## 8. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create a service type with a title, standard fee, and description | I can define the types of services offered in the system |
| US-02 | Authorized user | Edit a service type's title, fee, or description | I can keep service type definitions accurate and up to date |
| US-03 | Authorized user | Search for a service type by title | I can quickly find the service type I need |
| US-04 | Authorized user | Soft-delete a service type | I can retire service types no longer in use without losing the audit trail |
| US-05 | Authorized user | View a list of all active service types with their details | I have a clear overview of all configured service types |

---

## 9. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | What fields does a service type have? | Title (required), description (optional), standard fee (required). |
| RD-02 | How is audit metadata stored? | A `core_entity` record is created first; its `id` is stored as `entity_id` on the service type record. Entity holds `created_at`, `updated_at`, `created_by`, `updated_by`. |
| RD-03 | Is entity + service type creation atomic? | Yes — both records must be persisted together or not at all. |
| RD-04 | What happens when a service type is deleted? | Soft delete only — `is_deleted` is set to `true` and `deleted_at` is stamped. The record is retained. |
| RD-05 | Is title uniqueness a hard block? | No — duplicate titles trigger a warning but creation is not blocked. |

---

## 10. Out of Scope

- Assigning service types to specific claims, policies, or other records — handled by the respective modules.
- Pricing rules or fee overrides per customer or policy.
- Bulk import of service types.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*
