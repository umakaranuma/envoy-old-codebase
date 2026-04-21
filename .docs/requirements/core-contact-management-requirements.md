# Contact Management — Requirements Document

**Module:** Core
**Feature:** Contact Management
**Version:** 1.1
**Status:** Draft

---

## 1. Overview

The Contact Management feature allows authorized users to create, manage, and organize contacts within the system. Contacts represent individuals who can be associated with one or more customers. The system supports merging duplicate contacts into a single unified record, designating a primary contact per customer relationship, and organizing contacts into named groups for easier categorization and management.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform contact management actions.

---

## 2. Key Rules

- A contact record holds: full name, address, email address, and remarks.
- Email address is **mandatory** when creating a contact.
- Full name is stored as a **single field** (not split into first/last).
- A single contact can be linked to **multiple customers**.
- Each customer can have one contact designated as their **primary contact** and one as their **secondary contact** — these are relationship-level designations, not fields on the contact record itself.
- Multiple contacts can be **merged** into one; the user selects which contact becomes the primary (surviving) record.
- Non-primary contacts involved in a merge are **soft-deleted** (deactivated), not permanently removed.
- Soft-deleted (merged) contacts are retained in the system for audit and traceability purposes.
- Contacts can be organized into **contact groups**; each group has a name, description, and a list of member contacts.
- A contact can belong to **multiple groups** simultaneously.
- A group can exist with **zero contacts** (empty groups are allowed).
- Deleting a group only removes the group — the contacts within it are **not affected**.

---

## 3. Functional Requirements

### 3.1 Create Contact

| # | Requirement | Permission |
|---|---|---|
| 3.1.1 | Users can create a new contact by providing full name, address, email address, and remarks. | `contact.create` |
| 3.1.2 | Email address is a required field; the form cannot be submitted without it. | `contact.create` |
| 3.1.3 | Full name is stored as a single text field. | `contact.create` |
| 3.1.4 | Address and remarks are optional fields. | `contact.create` |
| 3.1.5 | The system must validate that the email address is in a valid format. | `contact.create` |
| 3.1.6 | Duplicate email addresses should be flagged with a warning, but creation may still proceed (not a hard block). | `contact.create` |

---

### 3.2 View Contacts

| # | Requirement | Permission |
|---|---|---|
| 3.2.1 | Users can view a list of all active contacts. | `contact.view` |
| 3.2.2 | The contact list supports search by name and email address. | `contact.view` |
| 3.2.3 | Users can view the full detail of a single contact, including all customers the contact is linked to. | `contact.view` |
| 3.2.4 | Soft-deleted (merged) contacts are hidden from the default list view. | `contact.view` |
| 3.2.5 | Users with appropriate permission can view merged/deactivated contacts via a filter or separate view. | `contact.view_inactive` |

---

### 3.3 Edit Contact

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | Users can edit the full name, address, email address, and remarks of an existing contact. | `contact.edit` |
| 3.3.2 | Email address remains mandatory during edit; it cannot be cleared. | `contact.edit` |
| 3.3.3 | Soft-deleted contacts cannot be edited. | — |

---

### 3.4 Delete Contact

| # | Requirement | Permission |
|---|---|---|
| 3.4.1 | Users can soft-delete a contact that is not linked to any customer. | `contact.delete` |
| 3.4.2 | If a contact is linked to one or more customers, the system must warn the user before allowing deletion. | `contact.delete` |
| 3.4.3 | Hard deletion is not supported; all deletions are soft deletes. | — |

---

### 3.5 Link Contact to Customer

| # | Requirement | Permission |
|---|---|---|
| 3.5.1 | A contact can be linked to multiple customers. | `contact.link` |
| 3.5.2 | When linking a contact to a customer, the user can designate the contact as the **primary contact** or **secondary contact** for that customer. | `contact.link` |
| 3.5.3 | Each customer can have at most one primary contact and one secondary contact at any time. | `contact.link` |
| 3.5.4 | Assigning a new primary contact to a customer automatically removes the primary designation from the previously assigned primary contact (demotes it, does not unlink). | `contact.link` |
| 3.5.5 | A contact can hold primary or secondary designations across different customers simultaneously. | — |

---

### 3.6 Merge Contacts

| # | Requirement | Permission |
|---|---|---|
| 3.6.1 | Users can select two or more contacts to merge into a single record. | `contact.merge` |
| 3.6.2 | During the merge process, the user must designate one contact as the **primary (surviving) contact**. | `contact.merge` |
| 3.6.3 | The data of the selected primary contact is retained on the surviving record. | `contact.merge` |
| 3.6.4 | Non-primary contacts involved in the merge are **soft-deleted** (deactivated) after the merge is complete. | `contact.merge` |
| 3.6.5 | All customer linkages from the non-primary (merged) contacts are transferred to the surviving primary contact. | `contact.merge` |
| 3.6.6 | If a merged (non-primary) contact was designated as a primary or secondary contact for a customer, that designation is transferred to the surviving contact automatically. | `contact.merge` |
| 3.6.7 | The system must display a clear confirmation summary before executing the merge, listing which contact will survive and which will be deactivated. | `contact.merge` |
| 3.6.8 | A merge action is recorded in the audit log, referencing all involved contact IDs. | `contact.merge` |
| 3.6.9 | Soft-deleted contacts created by a merge retain a reference to the surviving contact for traceability. | — |

---

### 3.7 Contact Groups

| # | Requirement | Permission |
|---|---|---|
| 3.7.1 | Users can create a contact group by providing a group name and an optional description. | `contact_group.create` |
| 3.7.2 | Group name is a required field; a group cannot be created without one. | `contact_group.create` |
| 3.7.3 | Description is an optional field. | `contact_group.create` |
| 3.7.4 | During group creation or editing, users can search for and select one or more contacts to add to the group. | `contact_group.create` / `contact_group.edit` |
| 3.7.5 | A contact can be a member of multiple groups simultaneously. | — |
| 3.7.6 | A group can exist with zero contacts; empty groups are permitted. | — |
| 3.7.7 | Users can view a list of all contact groups, showing group name, description, and member count. | `contact_group.view` |
| 3.7.8 | Users can view the detail of a single group, including the full list of contacts within it. | `contact_group.view` |
| 3.7.9 | Users can edit a group's name, description, and member contacts. | `contact_group.edit` |
| 3.7.10 | Users can remove one or more contacts from a group without deleting the group or the contacts. | `contact_group.edit` |
| 3.7.11 | Users can delete a contact group. Deleting a group does not affect the contacts within it. | `contact_group.delete` |
| 3.7.12 | Group name should be unique; duplicate group names should be flagged with a warning. | `contact_group.create` / `contact_group.edit` |
| 3.7.13 | All group create, edit, and delete actions must be recorded in the audit log. | — |

---

## 4. Permission Reference Table

| Permission Key | Description |
|---|---|
| `contact.create` | Create new contact records |
| `contact.view` | View active contacts and their details |
| `contact.view_inactive` | View soft-deleted / merged contacts |
| `contact.edit` | Edit existing contact records |
| `contact.delete` | Soft-delete a contact |
| `contact.link` | Link a contact to a customer and set primary/secondary designation |
| `contact.merge` | Merge two or more contacts into one |
| `contact_group.create` | Create new contact groups |
| `contact_group.view` | View contact groups and their members |
| `contact_group.edit` | Edit group details and manage member contacts |
| `contact_group.delete` | Delete a contact group |

---

## 5. Non-Functional Requirements

| # | Requirement |
|---|---|
| 5.1 | All create, edit, merge, and delete actions must be recorded in the audit log with the acting user and timestamp. |
| 5.2 | Contact search results should return within 2 seconds for datasets up to 10,000 records. |
| 5.3 | Soft-deleted contacts must be retained indefinitely for audit and traceability purposes. |
| 5.4 | Merge operations must be atomic — either all changes succeed or none are applied. |
| 5.5 | Contact group names should be indexed to support fast search and duplicate detection. |

---

## 6. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create a contact with a name, email, address, and remarks | I can store contact information in the system |
| US-02 | Authorized user | Link a contact to multiple customers | I can reuse the same contact across different customer records |
| US-03 | Authorized user | Designate a primary and secondary contact per customer | The customer record clearly identifies the key points of contact |
| US-04 | Authorized user | Merge duplicate contacts | I can clean up duplicates while preserving all customer linkages |
| US-05 | Authorized user | Choose which contact survives a merge | I have control over which record's data is retained |
| US-06 | Authorized user | Search for contacts by name or email | I can quickly find the contact I need |
| US-07 | Authorized user | View all customers a contact is linked to | I understand the full scope of a contact's relationships |
| US-08 | Authorized user | Create a contact group with a name and description | I can categorize and organize contacts into meaningful groups |
| US-09 | Authorized user | Add multiple contacts to a group | I can group related contacts together for easier reference |
| US-10 | Authorized user | Remove a contact from a group without deleting it | I can adjust group membership without losing contact data |
| US-11 | Authorized user | Delete a contact group | I can remove groups that are no longer needed without affecting the contacts |

---

## 7. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | What fields make up a contact's name? | Single full name field — no salutation or split first/last name. |
| RD-02 | What are primary and secondary contact? | Relationship-level designations — a contact is marked as primary or secondary when linked to a specific customer, not a field on the contact record itself. |
| RD-03 | What happens to non-primary contacts after a merge? | They are soft-deleted (deactivated). Data is retained for audit purposes. |
| RD-04 | Can a contact be linked to multiple customers? | Yes — one contact can be linked to many customers. |
| RD-05 | Whose data is retained after a merge? | The user manually selects which contact becomes the primary (surviving) record; that contact's data is retained. |
| RD-06 | Can more than 2 contacts be merged at once? | Yes — multiple contacts can be merged in a single merge operation. |
| RD-07 | Is email address mandatory? | Yes — email is required when creating or editing a contact. |
| RD-08 | Can a contact belong to multiple groups? | Yes — a contact can be a member of many groups simultaneously. |
| RD-09 | What happens to a group when all contacts are removed? | The group still exists; empty groups are allowed. |
| RD-10 | What happens to contacts when a group is deleted? | Contacts are not affected — only the group is deleted. |

---

## 8. Out of Scope

- Importing contacts in bulk via CSV or external integrations.
- Sending emails or communications directly from the contact record.
- Contact activity timeline or interaction history (may be addressed in the CRM module).
- Restoring / un-merging soft-deleted contacts.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*
