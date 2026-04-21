# Channel Management — Requirements Document

**Module:** Core
**Feature:** Channel Management
**Version:** 1.0
**Status:** Draft

---

## 1. Overview

The Channel Management feature allows authorized users to create and manage communication or sales channels within the system. A channel is defined by a name and an optional description, and can be used across other modules (e.g. CRM, leads) to identify the source or medium through which a customer or lead was acquired or engaged.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform channel management actions.

---

## 2. Key Rules

- A channel record holds: **name** and **description**.
- Name is **mandatory** when creating a channel.
- Description is **optional**.
- Channel names should be unique; duplicate names are flagged with a warning.
- Channels are **soft-deleted** — they are deactivated but not permanently removed.

---

## 3. Functional Requirements

### 3.1 Create Channel

| # | Requirement | Permission |
|---|---|---|
| 3.1.1 | Users can create a new channel by providing a name and an optional description. | `channel.create` |
| 3.1.2 | Name is a required field; the form cannot be submitted without it. | `channel.create` |
| 3.1.3 | Description is an optional field. | `channel.create` |
| 3.1.4 | Duplicate channel names should be flagged with a warning, but creation may still proceed (not a hard block). | `channel.create` |

---

### 3.2 View Channels

| # | Requirement | Permission |
|---|---|---|
| 3.2.1 | Users can view a list of all active channels showing name and description. | `channel.view` |
| 3.2.2 | The channel list supports search by name. | `channel.view` |
| 3.2.3 | Soft-deleted channels are hidden from the default list view. | `channel.view` |

---

### 3.3 Edit Channel

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | Users can edit the name and description of an existing channel. | `channel.edit` |
| 3.3.2 | Name remains mandatory during edit; it cannot be cleared. | `channel.edit` |
| 3.3.3 | Soft-deleted channels cannot be edited. | — |

---

### 3.4 Delete Channel

| # | Requirement | Permission |
|---|---|---|
| 3.4.1 | Users can soft-delete a channel. | `channel.delete` |
| 3.4.2 | Soft-deleted channels are deactivated and hidden from the default list but retained in the system. | — |
| 3.4.3 | Hard deletion is not supported. | — |

---

## 4. Permission Reference Table

| Permission Key | Description |
|---|---|
| `channel.create` | Create new channels |
| `channel.view` | View the channel list and individual channel details |
| `channel.edit` | Edit an existing channel's name and description |
| `channel.delete` | Soft-delete a channel |

---

## 5. Non-Functional Requirements

| # | Requirement |
|---|---|
| 5.1 | All create, edit, and delete actions must be recorded in the audit log with the acting user and timestamp. |
| 5.2 | Soft-deleted channels must be retained indefinitely for audit purposes. |

---

## 6. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create a channel with a name and description | I can define the communication or acquisition channels used in the system |
| US-02 | Authorized user | Edit a channel's name or description | I can keep channel definitions accurate and up to date |
| US-03 | Authorized user | Search for a channel by name | I can quickly find the channel I need |
| US-04 | Authorized user | Soft-delete a channel | I can retire channels that are no longer in use without losing the audit trail |

---

## 7. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | What fields does a channel have? | Name (required) and description (optional). |
| RD-02 | What happens when a channel is deleted? | Soft delete only — the channel is deactivated but not permanently removed. |

---

## 8. Out of Scope

- Assigning channels to specific records (e.g. leads, customers) — this is handled by the respective module that uses channels.
- Channel performance tracking, analytics, or reporting.
- Integration with external communication platforms.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*
