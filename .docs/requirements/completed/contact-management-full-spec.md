# Contact & Contact Group Management — Full Specification

**Module:** Core  
**Feature:** Contact Management + Contact Group Management  
**Version:** 2.0  
**Status:** Ready for Development  
**Last Updated:** 2026-03-24  

---

## Table of Contents

1. [Overview](#1-overview)
2. [Data Models](#2-data-models)
3. [Database Tables & Columns](#3-database-tables--columns)
4. [API Endpoints](#4-api-endpoints)
5. [Contact CRUD — Functional Requirements](#5-contact-crud--functional-requirements)
6. [Contact Group CRUD — Functional Requirements](#6-contact-group-crud--functional-requirements)
7. [Merge Contacts — Functional Requirements](#7-merge-contacts--functional-requirements)
8. [UI Screens & Task Breakdown](#8-ui-screens--task-breakdown)
9. [Permission Reference](#9-permission-reference)
10. [Non-Functional Requirements](#10-non-functional-requirements)
11. [User Stories](#11-user-stories)
12. [Resolved Decisions](#12-resolved-decisions)
13. [Out of Scope](#13-out-of-scope)

---

## 1. Overview

The Contact & Contact Group Management feature allows authorized users to:

- **Create, view, edit, and soft-delete contacts** — individuals linked to one or more customer accounts.
- **Merge duplicate contacts** — collapsing multiple contact records into one surviving record while preserving all customer linkages.
- **Organize contacts into groups** — named collections of contacts used for categorization and filtering.
- **Manage group membership** — adding and removing contacts from groups without affecting the contact records themselves.

Both features are entirely **permission-driven**. All actions are audited.

---

## 2. Data Models

### 2.1 Contact Model

```python
# Table: core_contacts
class Contact(models.Model):
    id                 = models.AutoField(primary_key=True, unique=True)
    name               = models.CharField(max_length=255, blank=False, null=False)   # Required
    email              = models.CharField(max_length=255, blank=True, null=True)
    contact_email      = models.CharField(max_length=255, blank=True, null=True)
    address            = models.CharField(max_length=255, blank=True, null=True)
    primary_contact    = models.CharField(max_length=20, blank=False, null=False)    # Required
    secondary_contact  = models.CharField(max_length=20, blank=True, null=True)
    remarks            = models.TextField(blank=True, null=True)
    picture            = models.TextField(blank=True, null=True)
    duplicated_contact = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="duplicates"
    )
    website_url        = models.TextField(blank=True, null=True)
    show_in_list       = models.BooleanField(default=True)   # False = soft-deleted / merged
```

### 2.2 ContactGroup Model

```python
# Table: core_contact_groups
class ContactGroup(models.Model):
    id          = models.AutoField(primary_key=True)
    name        = models.CharField(max_length=255, null=False, blank=False)   # Required
    description = models.TextField(blank=True, null=True)
```

### 2.3 GroupContact (Junction) Model

```python
# Table: core_group_contacts
class GroupContact(models.Model):
    id      = models.AutoField(primary_key=True)
    group   = models.ForeignKey(ContactGroup, on_delete=models.CASCADE, blank=False)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, blank=False)
```

### 2.4 Model Relationships

```
Contact ──< GroupContact >── ContactGroup
   │
   └── duplicated_contact (self-FK)
         Used to track merge lineage.
         Non-surviving contacts point to the surviving record.
         contact.duplicates.all() → all contacts merged into this one.
```

---

## 3. Database Tables & Columns

### 3.1 `core_contacts`

| Column              | Type         | Nullable | Default | Description                                                                 |
|---------------------|--------------|----------|---------|-----------------------------------------------------------------------------|
| `id`                | INT (PK)     | No       | auto    | Primary key, auto-increment                                                  |
| `name`              | VARCHAR(255) | No       | —       | Full name — single field, no first/last split. Required.                    |
| `email`             | VARCHAR(255) | Yes      | NULL    | Primary email. Format-validated on save. Duplicate triggers soft warning.   |
| `contact_email`     | VARCHAR(255) | Yes      | NULL    | Secondary/alternate email address.                                          |
| `address`           | VARCHAR(255) | Yes      | NULL    | Free-text address. Optional.                                                 |
| `primary_contact`   | VARCHAR(20)  | No       | —       | Primary phone number including country code. Required.                      |
| `secondary_contact` | VARCHAR(20)  | Yes      | NULL    | Secondary phone number including country code. Optional.                    |
| `remarks`           | TEXT         | Yes      | NULL    | Free-text notes. Optional. UI enforces 500-char soft limit.                 |
| `picture`           | TEXT         | Yes      | NULL    | Base64 or URL of profile image. Fallback to initials if NULL.              |
| `duplicated_contact`| INT (FK)     | Yes      | NULL    | Self-FK → `core_contacts.id`. Set on non-surviving contacts after a merge.  |
| `website_url`       | TEXT         | Yes      | NULL    | Optional URL.                                                                |
| `show_in_list`      | BOOLEAN      | No       | TRUE    | `TRUE` = active. `FALSE` = soft-deleted or merged. Drives all list filters. |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX idx_contacts_email (email)` — supports duplicate check and search
- `INDEX idx_contacts_name (name)` — supports search
- `INDEX idx_contacts_show_in_list (show_in_list)` — supports default filter
- `INDEX idx_contacts_duplicated (duplicated_contact)` — supports merge lineage queries

---

### 3.2 `core_contact_groups`

| Column        | Type         | Nullable | Default | Description                                                                  |
|---------------|--------------|----------|---------|------------------------------------------------------------------------------|
| `id`          | INT (PK)     | No       | auto    | Primary key, auto-increment                                                   |
| `name`        | VARCHAR(255) | No       | —       | Group name. Required. Should be unique — duplicates trigger a soft warning.  |
| `description` | TEXT         | Yes      | NULL    | Optional description of the group's purpose.                                 |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX idx_group_name (name)` — supports search and duplicate detection

---

### 3.3 `core_group_contacts`

| Column       | Type     | Nullable | Default | Description                                                     |
|--------------|----------|----------|---------|-----------------------------------------------------------------|
| `id`         | INT (PK) | No       | auto    | Primary key, auto-increment                                      |
| `group_id`   | INT (FK) | No       | —       | FK → `core_contact_groups.id`. CASCADE on group delete.         |
| `contact_id` | INT (FK) | No       | —       | FK → `core_contacts.id`. CASCADE on contact hard-delete.        |

**Constraints:**
- `UNIQUE (group_id, contact_id)` — a contact can appear in a group only once
- `FOREIGN KEY (group_id) REFERENCES core_contact_groups(id) ON DELETE CASCADE`
- `FOREIGN KEY (contact_id) REFERENCES core_contacts(id) ON DELETE CASCADE`

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX idx_gc_group (group_id)`
- `INDEX idx_gc_contact (contact_id)`

> **Note:** When a contact is soft-deleted (`show_in_list = FALSE`), their `core_group_contacts` rows are **not** removed. The group still retains the membership record. The UI should filter the member list to only show active contacts (`show_in_list = TRUE`) by default.

---

## 4. API Endpoints

### 4.1 Contact Endpoints

| Method   | Endpoint                          | Permission Required    | Description                                                          |
|----------|-----------------------------------|------------------------|----------------------------------------------------------------------|
| `GET`    | `/api/contacts/`                  | `contact.view`         | List all active contacts. `?show_inactive=true` includes soft-deleted (requires `contact.view_inactive`). Supports `?search=`, `?page=`, `?page_size=`. |
| `POST`   | `/api/contacts/`                  | `contact.create`       | Create a new contact.                                                |
| `GET`    | `/api/contacts/{id}/`             | `contact.view`         | Retrieve a single contact with linked accounts and merged children.  |
| `PUT`    | `/api/contacts/{id}/`             | `contact.edit`         | Full update of a contact. Blocked if `show_in_list = FALSE`.         |
| `PATCH`  | `/api/contacts/{id}/`             | `contact.edit`         | Partial update of a contact. Blocked if `show_in_list = FALSE`.      |
| `DELETE` | `/api/contacts/{id}/`             | `contact.delete`       | Soft-delete: sets `show_in_list = FALSE`. Hard delete not supported. |
| `POST`   | `/api/contacts/merge/`            | `contact.merge`        | Merge multiple contacts into one surviving record (atomic).          |
| `GET`    | `/api/contacts/{id}/accounts/`    | `contact.view`         | List all customer accounts linked to this contact with designations. |
| `GET`    | `/api/contacts/{id}/merged/`      | `contact.view`         | List all contacts merged into this record (`duplicates` reverse FK). |

#### `POST /api/contacts/` — Request Body

```json
{
  "name": "Sarah Johnson",
  "email": "sarah@acme.com",
  "primary_contact": "+94712345678",
  "secondary_contact": "+94711222333",
  "address": "Colombo 03, Sri Lanka",
  "remarks": "Key enterprise contact"
}
```

#### `POST /api/contacts/merge/` — Request Body

```json
{
  "primary_id": 1,
  "contact_ids": [1, 2, 3, 21, 22]
}
```
> `contact_ids` includes ALL candidates (selected contacts + their child contacts). `primary_id` must be one of `contact_ids`. The backend sets all non-primary contacts to `show_in_list = FALSE` and `duplicated_contact = primary_id`, then transfers all customer linkages to the primary.

#### `GET /api/contacts/` — Query Parameters

| Parameter      | Type    | Description                                                        |
|----------------|---------|--------------------------------------------------------------------|
| `search`       | string  | Filters on `name` and `email` (case-insensitive ILIKE)            |
| `show_inactive`| boolean | `true` includes `show_in_list=FALSE` records. Requires `contact.view_inactive`. |
| `page`         | int     | Page number (1-based)                                              |
| `page_size`    | int     | Records per page (default 20, max 100)                             |

---

### 4.2 Contact Group Endpoints

| Method   | Endpoint                                    | Permission Required       | Description                                                             |
|----------|---------------------------------------------|---------------------------|-------------------------------------------------------------------------|
| `GET`    | `/api/contact-groups/`                      | `contact_group.view`      | List all groups with `id`, `name`, `description`, `member_count`. Supports `?search=`. |
| `POST`   | `/api/contact-groups/`                      | `contact_group.create`    | Create a new contact group with optional initial member list.           |
| `GET`    | `/api/contact-groups/{id}/`                 | `contact_group.view`      | Retrieve a group with full member contact list.                         |
| `PUT`    | `/api/contact-groups/{id}/`                 | `contact_group.edit`      | Full update of group name, description, and member list.                |
| `PATCH`  | `/api/contact-groups/{id}/`                 | `contact_group.edit`      | Partial update (e.g., name or description only).                        |
| `DELETE` | `/api/contact-groups/{id}/`                 | `contact_group.delete`    | Hard-delete the group. Member contacts are NOT deleted.                 |
| `POST`   | `/api/contact-groups/{id}/members/`         | `contact_group.edit`      | Add one or more contacts to the group.                                  |
| `DELETE` | `/api/contact-groups/{id}/members/{cid}/`   | `contact_group.edit`      | Remove a single contact from the group.                                 |
| `GET`    | `/api/contact-groups/{id}/members/`         | `contact_group.view`      | List all active member contacts of a group.                             |

#### `POST /api/contact-groups/` — Request Body

```json
{
  "name": "Enterprise Clients",
  "description": "High-value corporate accounts",
  "contact_ids": [1, 3, 5]
}
```
> `contact_ids` is optional — an empty group is allowed.

#### `POST /api/contact-groups/{id}/members/` — Request Body

```json
{
  "contact_ids": [2, 4, 6]
}
```

#### `GET /api/contact-groups/` — Query Parameters

| Parameter  | Type   | Description                                       |
|------------|--------|---------------------------------------------------|
| `search`   | string | Filters on `name` (case-insensitive ILIKE)        |
| `page`     | int    | Page number (1-based)                             |
| `page_size`| int    | Records per page (default 20, max 100)            |

---

## 5. Contact CRUD — Functional Requirements

### 5.1 Create Contact

| #     | Requirement                                                                                                       | Permission         |
|-------|-------------------------------------------------------------------------------------------------------------------|--------------------|
| 5.1.1 | Users can create a new contact via a modal popup.                                                                 | `contact.create`   |
| 5.1.2 | **Contact Person Name** is a required field. Form cannot be submitted without it. Maps to `name`.                | `contact.create`   |
| 5.1.3 | `name` is stored as a single full-name field — no first/last split.                                              | `contact.create`   |
| 5.1.4 | **Email Address** is optional but must be in a valid format if provided. Maps to `email`.                        | `contact.create`   |
| 5.1.5 | If a duplicate email exists in the system, display a soft warning (amber). Creation may still proceed.           | `contact.create`   |
| 5.1.6 | **Address** is optional. Maps to `address`.                                                                      | `contact.create`   |
| 5.1.7 | **Remarks** is optional. Maps to `remarks`. UI enforces a 500-character limit with a live counter.               | `contact.create`   |
| 5.1.8 | **Primary Contact Number** is required. Includes a country-code selector + number field. Maps to `primary_contact`. | `contact.create` |
| 5.1.9 | **Secondary Contact Number** is optional. Includes its own country-code selector. Maps to `secondary_contact`.   | `contact.create`   |
| 5.1.10| On successful creation, close the modal, refresh the list, and display a success toast.                           | `contact.create`   |

---

### 5.2 View Contacts (List)

| #     | Requirement                                                                                                       | Permission                |
|-------|-------------------------------------------------------------------------------------------------------------------|---------------------------|
| 5.2.1 | Display all contacts where `show_in_list = TRUE` in a paginated table.                                            | `contact.view`            |
| 5.2.2 | Table columns: checkbox (merge select), Name + avatar, Email, Primary Phone, Linked Accounts, Status, Actions.   | `contact.view`            |
| 5.2.3 | Search by `name` and `email`. Debounced (300 ms), server-side. Results within 2 seconds.                          | `contact.view`            |
| 5.2.4 | "Show merged / inactive" toggle reveals `show_in_list = FALSE` contacts with dimmed Merged styling.              | `contact.view_inactive`   |
| 5.2.5 | Contacts where `show_in_list = FALSE` have: dimmed row (opacity 0.6), struck-through name, disabled checkbox.    | `contact.view`            |
| 5.2.6 | Name cell shows a "N child contact(s)" sub-line if `contact.duplicates.count() > 0`.                             | `contact.view`            |

---

### 5.3 View Contact (Single)

| #     | Requirement                                                                                                       | Permission         |
|-------|-------------------------------------------------------------------------------------------------------------------|--------------------|
| 5.3.1 | Display a contact detail page with hero section + tabbed content.                                                 | `contact.view`     |
| 5.3.2 | Hero: avatar/initials, full name, email, status badges, summary badges (linked accounts count, merged count).     | `contact.view`     |
| 5.3.3 | Detail grid: Primary Phone, Secondary Phone, Address. Empty fields show `—`.                                     | `contact.view`     |
| 5.3.4 | **Tab — Linked Accounts**: card grid of all customer accounts this contact is linked to, each showing account name, type, and designation badge (Primary / Secondary / None). | `contact.view` |
| 5.3.5 | **Tab — Merged Contacts**: card grid of all contacts merged into this record (`contact.duplicates.all()`), each showing struck-through name, email, merged date, and surviving-record reference. | `contact.view` |
| 5.3.6 | **Tab — Interactions**: placeholder tab with empty state. Reserved for CRM module.                                | `contact.view`     |
| 5.3.7 | Tab count badges reflect the actual record counts.                                                                | `contact.view`     |

---

### 5.4 Edit Contact

| #     | Requirement                                                                                                       | Permission       |
|-------|-------------------------------------------------------------------------------------------------------------------|------------------|
| 5.4.1 | Users can edit: `name`, `email`, `address`, `remarks`, `primary_contact`, `secondary_contact`.                   | `contact.edit`   |
| 5.4.2 | Edit form pre-populates with existing values.                                                                     | `contact.edit`   |
| 5.4.3 | `name` remains required during edit; cannot be cleared.                                                           | `contact.edit`   |
| 5.4.4 | `email` format validation applies on edit. Duplicate warning (soft) if email matches another record.              | `contact.edit`   |
| 5.4.5 | `primary_contact` remains required during edit; cannot be cleared.                                                | `contact.edit`   |
| 5.4.6 | Edit is blocked for contacts with `show_in_list = FALSE`. Edit button hidden for merged contacts.                 | —                |

---

### 5.5 Delete Contact

| #     | Requirement                                                                                                       | Permission         |
|-------|-------------------------------------------------------------------------------------------------------------------|--------------------|
| 5.5.1 | Soft-delete: sets `show_in_list = FALSE`. Hard deletion is not supported.                                         | `contact.delete`   |
| 5.5.2 | Show a confirmation dialog before deleting.                                                                       | `contact.delete`   |
| 5.5.3 | If the contact is linked to one or more customer accounts, display a warning in the confirmation dialog before allowing deletion. | `contact.delete` |
| 5.5.4 | Soft-deleted contacts are hidden from the default list but retained in the database for audit.                    | —                  |
| 5.5.5 | The contact's `core_group_contacts` membership rows are retained (not deleted) when soft-deleted.                 | —                  |

---

## 6. Contact Group CRUD — Functional Requirements

### 6.1 Create Contact Group

| #     | Requirement                                                                                                       | Permission              |
|-------|-------------------------------------------------------------------------------------------------------------------|-------------------------|
| 6.1.1 | Users can create a new contact group via a modal popup.                                                           | `contact_group.create`  |
| 6.1.2 | **Group Name** is required. Maps to `core_contact_groups.name`. Form cannot be submitted without it.             | `contact_group.create`  |
| 6.1.3 | If a group with the same name already exists, show a soft warning (amber). Creation may still proceed.            | `contact_group.create`  |
| 6.1.4 | **Description** is optional. Maps to `core_contact_groups.description`.                                          | `contact_group.create`  |
| 6.1.5 | The modal includes a searchable, multi-select contact picker listing all active contacts (`show_in_list = TRUE`). | `contact_group.create`  |
| 6.1.6 | Selected contacts are displayed as removable chips below the search field.                                        | `contact_group.create`  |
| 6.1.7 | Creating a group without any contacts is allowed — empty groups are valid.                                        | `contact_group.create`  |
| 6.1.8 | On save: create the `core_contact_groups` record, then bulk-insert `core_group_contacts` rows for each selected contact. | `contact_group.create` |
| 6.1.9 | On successful creation, close the modal, refresh the group list, and show a success toast.                        | `contact_group.create`  |

---

### 6.2 View Contact Groups (List)

| #     | Requirement                                                                                                       | Permission             |
|-------|-------------------------------------------------------------------------------------------------------------------|------------------------|
| 6.2.1 | Display all contact groups in a paginated table.                                                                  | `contact_group.view`   |
| 6.2.2 | Table columns: Group Name, Description (truncated), Member Count, Actions (View, Edit, Delete).                  | `contact_group.view`   |
| 6.2.3 | Member Count is computed from `core_group_contacts` — only counts contacts where `show_in_list = TRUE`.           | `contact_group.view`   |
| 6.2.4 | Groups with zero members display a "0 members" badge (empty groups are valid and must be shown).                  | `contact_group.view`   |
| 6.2.5 | Search by group `name`. Debounced (300 ms), server-side.                                                         | `contact_group.view`   |
| 6.2.6 | "New Group" button is visible only to users with `contact_group.create` permission.                               | `contact_group.create` |

---

### 6.3 View Contact Group (Single / Detail)

| #     | Requirement                                                                                                       | Permission           |
|-------|-------------------------------------------------------------------------------------------------------------------|----------------------|
| 6.3.1 | Display group name, description, and member count in a header section.                                            | `contact_group.view` |
| 6.3.2 | Display the full list of active member contacts as a table or card grid.                                          | `contact_group.view` |
| 6.3.3 | Each member row/card shows: avatar/initials, full name, email, primary phone, and a Remove button.                | `contact_group.view` |
| 6.3.4 | Remove button on each member deletes that `core_group_contacts` row (does NOT delete the contact record).         | `contact_group.edit` |
| 6.3.5 | Soft-deleted contacts (`show_in_list = FALSE`) are excluded from the member list in this view.                    | `contact_group.view` |
| 6.3.6 | If all members are removed, show an "empty group" state — the group itself is not deleted.                        | `contact_group.view` |

---

### 6.4 Edit Contact Group

| #     | Requirement                                                                                                       | Permission           |
|-------|-------------------------------------------------------------------------------------------------------------------|----------------------|
| 6.4.1 | Users can edit the group `name` and `description`.                                                                | `contact_group.edit` |
| 6.4.2 | `name` remains required during edit; cannot be cleared.                                                           | `contact_group.edit` |
| 6.4.3 | Duplicate name warning (soft) applies during edit.                                                                | `contact_group.edit` |
| 6.4.4 | Users can add new contacts to the group using the same searchable multi-select picker as in creation.             | `contact_group.edit` |
| 6.4.5 | Users can remove existing members by clicking the × on their chip or via the Remove button in the detail view.   | `contact_group.edit` |
| 6.4.6 | Adding a contact already in the group is a no-op (handled by the `UNIQUE` constraint — return 200, no error).    | `contact_group.edit` |
| 6.4.7 | Edit form pre-populates name, description, and existing member chips.                                             | `contact_group.edit` |

---

### 6.5 Delete Contact Group

| #     | Requirement                                                                                                       | Permission              |
|-------|-------------------------------------------------------------------------------------------------------------------|-------------------------|
| 6.5.1 | Users can delete a contact group. This is a **hard delete** of the `core_contact_groups` record.                  | `contact_group.delete`  |
| 6.5.2 | Deleting a group cascades to delete all `core_group_contacts` rows for that group (FK CASCADE is already defined). | —                       |
| 6.5.3 | Contact records themselves are **not affected** — only the group and its membership rows are removed.             | —                       |
| 6.5.4 | Show a confirmation dialog clearly stating: "Deleting this group will not delete the contacts within it."        | `contact_group.delete`  |
| 6.5.5 | On successful deletion, refresh the group list and show a success toast.                                          | `contact_group.delete`  |

---

## 7. Merge Contacts — Functional Requirements

### 7.1 Selection (List View)

| #     | Requirement                                                                                                       | Permission       |
|-------|-------------------------------------------------------------------------------------------------------------------|------------------|
| 7.1.1 | Each active contact row has a checkbox. Checkboxes are hidden/disabled if the user lacks `contact.merge`.         | `contact.merge`  |
| 7.1.2 | Merged/soft-deleted contacts (`show_in_list = FALSE`) cannot be selected — their checkboxes are disabled.         | —                |
| 7.1.3 | The merge selection bar appears when **≥ 2** contacts are selected; it is hidden when < 2 are selected.          | `contact.merge`  |
| 7.1.4 | The bar shows: selection count, a chip per selected contact (with × remove), the "Merge Contacts" button, and a "Clear" link. | `contact.merge` |
| 7.1.5 | Removing a chip deselects the contact and unchecks its row. If count drops to < 2, the bar hides.               | `contact.merge`  |

### 7.2 Merge Modal — Step 1: Build Candidate List & Select Primary

| #     | Requirement                                                                                                       | Permission       |
|-------|-------------------------------------------------------------------------------------------------------------------|------------------|
| 7.2.1 | On modal open, build the full candidate list from: (a) the selected contacts, plus (b) all contacts where `duplicated_contact IN (selected_ids)`. | `contact.merge` |
| 7.2.2 | Display the flat list. Group by parent: show parent contact, then their child contacts indented beneath with a dashed border and a "Child contacts of {Parent Name}" section label. | `contact.merge` |
| 7.2.3 | If any child contacts are found, display a warning: "Some selected contacts have existing merged (child) contacts. They are included and eligible to be selected as the primary." | `contact.merge` |
| 7.2.4 | Each candidate row shows: avatar, name, email, linked account count. A radio selector on the right indicates primary selection. | `contact.merge` |
| 7.2.5 | Primary selection is mutually exclusive (one radio at a time). "Next: Review →" is disabled until a primary is chosen. | `contact.merge` |
| 7.2.6 | Any candidate — including child contacts — can be selected as the primary surviving record.                       | `contact.merge`  |

### 7.3 Merge Modal — Step 2: Confirmation

| #     | Requirement                                                                                                       | Permission       |
|-------|-------------------------------------------------------------------------------------------------------------------|------------------|
| 7.3.1 | Display an atomic-operation warning: "N contacts will be soft-deleted. All customer linkages transfer to {primary name}. This cannot be undone." | `contact.merge` |
| 7.3.2 | "Surviving Record" section: primary contact row with a "Survives" brand badge.                                    | `contact.merge`  |
| 7.3.3 | "Will Be Soft-Deleted" section: all non-primary candidates with struck-through names and a "Deactivated" danger badge. | `contact.merge` |
| 7.3.4 | "What Transfers" summary: a table of all customer linkages being transferred (account name + designation). Shows "No linkages to transfer" if none. | `contact.merge` |
| 7.3.5 | "Execute Merge" button calls `POST /api/contacts/merge/`. On success: close modal, clear selection, refresh list, show success toast. | `contact.merge` |
| 7.3.6 | "Back" returns to Step 1 preserving the primary selection.                                                        | `contact.merge`  |

### 7.4 Merge — Backend Logic (Atomic Transaction)

| #     | Requirement                                                                                                       |
|-------|-------------------------------------------------------------------------------------------------------------------|
| 7.4.1 | All operations run inside a single database transaction. Any failure rolls back all changes.                       |
| 7.4.2 | For each non-primary contact in `contact_ids`: set `show_in_list = FALSE`, set `duplicated_contact = primary_id`. |
| 7.4.3 | Transfer all customer-contact linkages from non-primary contacts to the primary. Preserve `designation` (Primary / Secondary) on each transferred link. |
| 7.4.4 | If a transferred link conflicts (primary already linked to the same customer), skip the duplicate rather than error. |
| 7.4.5 | Write an audit log entry: `action = "contact_merge"`, actor = request user, payload = `{ primary_id, merged_ids, timestamp }`. |
| 7.4.6 | Return 200 with the surviving contact's serialized data. Return 400 with error detail on validation failure.       |

---

## 8. UI Screens & Task Breakdown

### 8.1 Screen: Contact List (`/contacts/`)

#### Tasks

| Task ID | Component                  | Description                                                                                                     | Permission Guard       |
|---------|----------------------------|-----------------------------------------------------------------------------------------------------------------|------------------------|
| L-01    | Page header                | Title "Contacts" + total active count. "New Contact" button (gated).                                           | `contact.create`       |
| L-02    | Merge selection bar        | Appears at ≥2 checked contacts. Chips, count, "Merge Contacts" button, "Clear" link. Slides in with animation. | `contact.merge`        |
| L-03    | Search bar                 | Debounced input, searches `name` + `email`. Hits `GET /api/contacts/?search=`.                                  | `contact.view`         |
| L-04    | "Show merged" toggle       | Calls `GET /api/contacts/?show_inactive=true`. Reveals soft-deleted rows. Hide toggle if no permission.         | `contact.view_inactive`|
| L-05    | Contacts table             | Columns: checkbox, name+avatar+children badge, email (mono), primary phone, linked accounts, status, actions.   | `contact.view`         |
| L-06    | Row checkbox               | Toggling adds/removes from selection set. Disabled for `show_in_list=FALSE` rows.                               | `contact.merge`        |
| L-07    | Row click → single view    | Clicking a row (not the checkbox) navigates to `/contacts/{id}/`.                                               | `contact.view`         |
| L-08    | Row actions                | View (eye icon always shown), Edit (hidden if `contact.edit` absent or contact is merged), no Delete in row.    | `contact.edit`         |
| L-09    | Pagination                 | Server-side. Shows "Showing X–Y of Z". Default page_size = 20.                                                  | `contact.view`         |

---

### 8.2 Screen: Contact Single View (`/contacts/{id}/`)

#### Tasks

| Task ID | Component                  | Description                                                                                                     | Permission Guard   |
|---------|----------------------------|-----------------------------------------------------------------------------------------------------------------|--------------------|
| S-01    | Back breadcrumb            | "← Back to Contacts" navigates to list.                                                                         | —                  |
| S-02    | Hero: Avatar               | 56 px circle. Shows `picture` if set, else 2-letter initials from `name`. Color derived from `id`.             | `contact.view`     |
| S-03    | Hero: Name + email         | Full name as heading. Email in monospace below.                                                                  | `contact.view`     |
| S-04    | Hero: Status badges        | Active/Merged badge + "N linked accounts" + "N merged contacts" (only if N > 0).                                | `contact.view`     |
| S-05    | Hero: Edit button          | Opens edit modal pre-populated. Hidden if `contact.edit` absent OR `show_in_list = FALSE`.                      | `contact.edit`     |
| S-06    | Hero: Delete button        | Opens delete confirmation dialog. Hidden if `contact.delete` absent OR `show_in_list = FALSE`.                  | `contact.delete`   |
| S-07    | Detail grid                | 3-column grid: Primary Phone / Secondary Phone / Address. Empty = "—".                                          | `contact.view`     |
| S-08    | Tab: Linked Accounts       | Card grid from `GET /api/contacts/{id}/accounts/`. Each card: logo, name, type, designation badge.              | `contact.view`     |
| S-09    | Tab: Merged Contacts       | Card grid from `GET /api/contacts/{id}/merged/`. Shows struck-through name, email, merge date, surviving ref.   | `contact.view`     |
| S-10    | Tab: Interactions          | Placeholder empty state. "Available in CRM module." No actions.                                                  | `contact.view`     |
| S-11    | Tab count badges           | Each tab label shows a count badge from the actual record count.                                                 | `contact.view`     |

---

### 8.3 Screen: Contact Groups List (`/contacts/groups/`)

#### Tasks

| Task ID | Component                  | Description                                                                                                     | Permission Guard         |
|---------|----------------------------|-----------------------------------------------------------------------------------------------------------------|--------------------------|
| G-01    | Page header                | Title "Contact Groups" + total group count. "New Group" button (gated).                                         | `contact_group.create`   |
| G-02    | Search bar                 | Debounced search on group `name`. Hits `GET /api/contact-groups/?search=`.                                       | `contact_group.view`     |
| G-03    | Groups table               | Columns: Group Name, Description (truncated, max 80 chars), Member Count, Actions (View, Edit, Delete).         | `contact_group.view`     |
| G-04    | Member Count               | Computed: `SELECT COUNT(*) FROM core_group_contacts gc JOIN core_contacts c ON c.id = gc.contact_id WHERE gc.group_id = ? AND c.show_in_list = TRUE` | `contact_group.view` |
| G-05    | Empty group indicator      | Groups with 0 members show a "0 members" neutral badge — not hidden.                                            | `contact_group.view`     |
| G-06    | Row: Edit action           | Opens Edit Group modal pre-populated. Gated by permission.                                                       | `contact_group.edit`     |
| G-07    | Row: Delete action         | Opens confirmation dialog (warns contacts are not affected). Calls `DELETE /api/contact-groups/{id}/`.          | `contact_group.delete`   |
| G-08    | Row click → group detail   | Navigates to `/contacts/groups/{id}/`.                                                                           | `contact_group.view`     |
| G-09    | Pagination                 | Server-side. Default page_size = 20.                                                                             | `contact_group.view`     |

---

### 8.4 Screen: Contact Group Detail (`/contacts/groups/{id}/`)

#### Tasks

| Task ID | Component                  | Description                                                                                                     | Permission Guard         |
|---------|----------------------------|-----------------------------------------------------------------------------------------------------------------|--------------------------|
| GD-01   | Group header               | Group name (heading), description, member count badge. Edit and Delete buttons (gated).                         | `contact_group.view`     |
| GD-02   | "Add Contacts" button      | Opens the member-picker modal. Gated by `contact_group.edit`.                                                    | `contact_group.edit`     |
| GD-03   | Members list               | Table or card grid. Shows avatar, name, email, primary phone, Remove button per row.                            | `contact_group.view`     |
| GD-04   | Remove member button       | Calls `DELETE /api/contact-groups/{id}/members/{contact_id}/`. Removes `GroupContact` row only — contact not deleted. | `contact_group.edit` |
| GD-05   | Filtered member display    | Only contacts where `show_in_list = TRUE` are shown. Soft-deleted members are hidden.                           | `contact_group.view`     |
| GD-06   | Empty group state          | Shows "No contacts in this group" with an "Add Contacts" call-to-action.                                        | `contact_group.view`     |

---

### 8.5 Modal: Create Contact

| Task ID | Component                  | Description                                                                                                     |
|---------|----------------------------|-----------------------------------------------------------------------------------------------------------------|
| MC-01   | Modal trigger              | "New Contact" button on list page. Opens a 520 px modal.                                                        |
| MC-02   | Live preview row           | At the top of the modal: avatar (initials updating as name is typed) + name + email.                            |
| MC-03   | Section: Basic Info        | Fields: Contact Person Name* (→ `name`), Email Address (→ `email`), Address (→ `address`), Remarks (→ `remarks`) |
| MC-04   | Section: Contact Numbers   | Primary Contact Number* (country-code dropdown + number → `primary_contact`), Secondary Contact Number (→ `secondary_contact`) |
| MC-05   | Name validation            | Required. Cannot submit without it. Error: "Contact person name is required."                                    |
| MC-06   | Email validation           | Format check (regex). Invalid = hard block (red border + error). Duplicate = soft warning (amber border + warning) — form can still be submitted. |
| MC-07   | Phone validation           | Primary is required. Format check: 5–15 numeric chars. Error if invalid.                                        |
| MC-08   | Remarks counter            | Live character counter below the textarea. Turns amber at > 430/500 chars.                                      |
| MC-09   | Submit                     | Calls `POST /api/contacts/`. On success: close modal, refresh list, toast "Contact created."                    |
| MC-10   | Shake animation            | If required fields are empty on submit, modal shakes and focuses the first invalid field.                        |

---

### 8.6 Modal: Create / Edit Contact Group

| Task ID | Component                  | Description                                                                                                     |
|---------|----------------------------|-----------------------------------------------------------------------------------------------------------------|
| MG-01   | Modal trigger              | "New Group" button (create) or "Edit" row action (edit). Opens a 560 px modal.                                  |
| MG-02   | Group Name field*          | Required. Maps to `core_contact_groups.name`. Duplicate name shows amber warning — not a hard block.           |
| MG-03   | Description field          | Optional. Maps to `core_contact_groups.description`. Textarea, no character limit in DB.                        |
| MG-04   | Contact picker search      | Text input that searches active contacts (`show_in_list = TRUE`) via `GET /api/contacts/?search=`. Debounced.  |
| MG-05   | Contact picker results     | Dropdown list showing matching contacts: avatar, name, email. Click to add to selection.                        |
| MG-06   | Selected contacts chips    | Each selected contact shown as a chip with avatar initials, name, and × remove button below the search field.   |
| MG-07   | Empty group allowed        | A group can be saved with zero contacts selected. Hint text: "You can add contacts later."                      |
| MG-08   | Edit pre-population        | In edit mode: pre-fill name, description, and render existing members as chips.                                  |
| MG-09   | Duplicate prevention       | The `UNIQUE(group_id, contact_id)` constraint prevents double-adding. UI should grey out already-added contacts in the picker results. |
| MG-10   | Submit (Create)            | Calls `POST /api/contact-groups/`. Body: `{ name, description, contact_ids }`. Toast "Group created."          |
| MG-11   | Submit (Edit)              | Calls `PUT /api/contact-groups/{id}/` with full updated payload. Handles member diff server-side.               |
| MG-12   | Delete confirmation        | Separate confirmation dialog. Message: "Deleting this group will not delete the contacts within it."            |

---

## 9. Permission Reference

| Permission Key           | Description                                                      | Absent: UI Behavior                                          |
|--------------------------|------------------------------------------------------------------|--------------------------------------------------------------|
| `contact.view`           | View contact list and single contact details                     | Redirect / 403 on all contact screens                        |
| `contact.view_inactive`  | View soft-deleted / merged contacts                              | Hide "Show merged / inactive" toggle entirely                |
| `contact.create`         | Create new contact records                                       | Hide "New Contact" button                                    |
| `contact.edit`           | Edit existing contact records                                    | Hide Edit button in row and single view                      |
| `contact.delete`         | Soft-delete a contact                                            | Hide Delete button in single view                            |
| `contact.link`           | Link a contact to a customer and set designation                 | Managed in Customer module, not Contact screens              |
| `contact.merge`          | Merge two or more contacts into one                              | Hide row checkboxes and merge bar entirely                   |
| `contact_group.view`     | View contact groups list and group detail                        | Hide the Groups section / tab entirely                       |
| `contact_group.create`   | Create new contact groups                                        | Hide "New Group" button                                      |
| `contact_group.edit`     | Edit group name, description, and member list                    | Hide Edit action; hide Add / Remove member buttons           |
| `contact_group.delete`   | Delete a contact group                                           | Hide Delete action on group row and group detail             |

---

## 10. Non-Functional Requirements

| #    | Requirement                                                                                                              |
|------|--------------------------------------------------------------------------------------------------------------------------|
| NFR-01 | All create, edit, merge, and delete actions must be recorded in the audit log with the acting user's ID and timestamp. |
| NFR-02 | Contact search (`name`, `email`) must return results within 2 seconds for datasets up to 10,000 records.               |
| NFR-03 | Soft-deleted contacts (`show_in_list = FALSE`) must be retained indefinitely and never purged by automated processes.  |
| NFR-04 | Merge operations must be atomic — use a database transaction. Either all changes succeed or none are applied.           |
| NFR-05 | The `core_contact_groups.name` column must be indexed to support fast search and duplicate detection.                  |
| NFR-06 | The `UNIQUE(group_id, contact_id)` constraint on `core_group_contacts` must be enforced at the database level.         |
| NFR-07 | All permission checks must be enforced at both the frontend (UI visibility) and backend (API authorization) levels.    |
| NFR-08 | Contact group delete must cascade-delete `core_group_contacts` rows but must never cascade-delete contact records.     |
| NFR-09 | API responses must include appropriate HTTP status codes: 200 OK, 201 Created, 400 Bad Request, 403 Forbidden, 404 Not Found. |
| NFR-10 | The contact picker in the group modal must support real-time debounced search (300 ms delay) against the contacts API. |

---

## 11. User Stories

| ID    | As a…            | I want to…                                                                 | So that…                                                                 |
|-------|------------------|----------------------------------------------------------------------------|--------------------------------------------------------------------------|
| US-01 | Authorized user  | Create a contact with name, email, address, remarks, and phone numbers     | I can store contact information in the system                            |
| US-02 | Authorized user  | See a live preview of the contact's avatar and name while filling the form | I can verify I'm entering the correct details                            |
| US-03 | Authorized user  | Edit a contact's details                                                   | I can keep contact information accurate and up to date                   |
| US-04 | Authorized user  | Soft-delete a contact with a confirmation dialog                           | I can retire outdated records without permanently losing them            |
| US-05 | Authorized user  | Search contacts by name or email                                           | I can quickly find the contact I need                                    |
| US-06 | Authorized user  | View all customer accounts a contact is linked to in one place             | I understand the full scope of a contact's relationships                 |
| US-07 | Authorized user  | View all contacts that have been merged into a surviving record             | I have a full audit trail of duplicate resolution                        |
| US-08 | Authorized user  | Select 2 or more contacts and merge them via a guided modal                | I can consolidate duplicate records without losing any customer linkages |
| US-09 | Authorized user  | See child contacts (from prior merges) included in the merge candidate list| I don't accidentally leave behind already-merged duplicates              |
| US-10 | Authorized user  | Select any candidate — including a child — as the surviving primary        | I have full control over which contact record's data is retained         |
| US-11 | Authorized user  | See a clear summary before executing a merge                               | I know exactly what will be soft-deleted and what will be transferred    |
| US-12 | Authorized user  | Create a contact group with a name, description, and initial members       | I can organize contacts into meaningful categories                       |
| US-13 | Authorized user  | Search and multi-select contacts from a picker when creating a group       | I can quickly find and add the right contacts without leaving the modal  |
| US-14 | Authorized user  | Create a group with zero contacts                                          | I can set up the group structure before adding members                   |
| US-15 | Authorized user  | Add contacts to an existing group at any time                              | I can grow a group's membership as new contacts are created              |
| US-16 | Authorized user  | Remove a contact from a group without deleting the contact                 | I can adjust group membership without affecting the contact record       |
| US-17 | Authorized user  | Delete a contact group with a clear confirmation that contacts are unaffected | I can remove unused groups without fear of losing contact data         |
| US-18 | Authorized user  | Search contact groups by name                                              | I can quickly find the group I need                                      |

---

## 12. Resolved Decisions

| #     | Question                                                                      | Decision                                                                                                  |
|-------|-------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| RD-01 | Is email mandatory on contact creation?                                       | No — email is optional. If provided, it must be a valid format. Duplicates trigger a soft warning only.   |
| RD-02 | Is phone mandatory on contact creation?                                       | Yes — `primary_contact` (primary phone) is required. `secondary_contact` is optional.                    |
| RD-03 | How is a contact's name stored?                                                | Single full-name field (`name`). No first/last split.                                                     |
| RD-04 | How are soft-deleted contacts identified?                                      | `show_in_list = FALSE`. This is the single soft-delete flag.                                              |
| RD-05 | How is merge lineage tracked?                                                  | `duplicated_contact` FK on the Contact model. Non-surviving contacts point to the surviving record.       |
| RD-06 | Can a child contact (from a prior merge) be selected as the primary in a new merge? | Yes — any candidate in the merge list, including child contacts, can be the primary.               |
| RD-07 | What happens to group memberships when a contact is soft-deleted?             | `core_group_contacts` rows are NOT removed. The group retains the row; the UI filters out inactive contacts. |
| RD-08 | Is deleting a contact group a hard delete or soft delete?                     | Hard delete. The group and its `core_group_contacts` rows are permanently removed. Contacts are unaffected. |
| RD-09 | Can a group have zero members?                                                 | Yes — empty groups are permitted and must appear in the list with a "0 members" badge.                    |
| RD-10 | Can a contact belong to multiple groups?                                       | Yes — the `core_group_contacts` junction table allows a contact to appear in multiple groups.             |
| RD-11 | What happens to group membership when a contact is hard-deleted?              | The `FOREIGN KEY ON DELETE CASCADE` on `core_group_contacts.contact_id` removes the membership rows automatically. |
| RD-12 | Is group name uniqueness a hard constraint?                                    | No — it's a soft warning in the UI. No `UNIQUE` constraint is applied at the database level for group names. |

---

## 13. Out of Scope

- Importing contacts in bulk via CSV or external integrations.
- Sending emails or making calls directly from a contact record.
- Contact activity timeline or interaction history (reserved for the CRM module).
- Restoring / un-merging soft-deleted (merged) contacts.
- Assigning contacts to customers directly from the Contact screens (handled in the Customer module via `contact.link` permission).
- Contact group permission scoping (groups are visible to all users with `contact_group.view` — no per-group access control).
- Versioning or changelog for contact record edits.

---

---

## Task Status Summary

| Phase | Description | Status |
|-------|-------------|--------|
| Backend | Model/Controller/URLs | ✅ Completed |
| Frontend | UI/API-Services/Types | ✅ Completed |
| Features | Merge/Groups/Soft-Delete | ✅ Completed |
| UI Refactor | Terminology/Tabbed View | ✅ Completed |
| Popup UI | Modal Contact Creation (+94) | ✅ Completed |
| Verification | Manual/Audit review | ✅ Completed |
