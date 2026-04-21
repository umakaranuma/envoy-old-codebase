# API Tasks: Contact Management — Requirements Document

## 3.1 Create Contact
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

- [ ] Ensure API supports: Users can create a new contact by providing full name, address, email address, and remarks.
- [ ] Ensure API supports: Email address is a required field; the form cannot be submitted without it.
- [ ] Ensure API supports: Full name is stored as a single text field.
- [ ] Ensure API supports: Address and remarks are optional fields.
- [ ] Ensure API supports: The system must validate that the email address is in a valid format.
- [ ] Ensure API supports: Duplicate email addresses should be flagged with a warning, but creation may still proceed (not a hard block).
## 3.2 View Contacts
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

- [ ] Ensure API supports: Users can view a list of all active contacts.
- [ ] Ensure API supports: The contact list supports search by name and email address.
- [ ] Ensure API supports: Users can view the full detail of a single contact, including all customers the contact is linked to.
- [ ] Ensure API supports: Soft-deleted (merged) contacts are hidden from the default list view.
- [ ] Ensure API supports: Users with appropriate permission can view merged/deactivated contacts via a filter or separate view.
## 3.3 Edit Contact
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit the full name, address, email address, and remarks of an existing contact.
- [ ] Ensure API supports: Email address remains mandatory during edit; it cannot be cleared.
- [ ] Ensure API supports: Soft-deleted contacts cannot be edited.
## 3.4 Delete Contact
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete a contact that is not linked to any customer.
- [ ] Ensure API supports: If a contact is linked to one or more customers, the system must warn the user before allowing deletion.
- [ ] Ensure API supports: Hard deletion is not supported; all deletions are soft deletes.
## 3.5 Link Contact to Customer
- [ ] Implement API logic for 3.5 Link Contact to Customer.

- [ ] Ensure API supports: A contact can be linked to multiple customers.
- [ ] Ensure API supports: When linking a contact to a customer, the user can designate the contact as the **primary contact** or **secondary contact** for that customer.
- [ ] Ensure API supports: Each customer can have at most one primary contact and one secondary contact at any time.
- [ ] Ensure API supports: Assigning a new primary contact to a customer automatically removes the primary designation from the previously assigned primary contact (demotes it, does not unlink).
- [ ] Ensure API supports: A contact can hold primary or secondary designations across different customers simultaneously.
## 3.6 Merge Contacts
- [ ] Implement API logic for 3.6 Merge Contacts.

- [ ] Ensure API supports: Users can select two or more contacts to merge into a single record.
- [ ] Ensure API supports: During the merge process, the user must designate one contact as the **primary (surviving) contact**.
- [ ] Ensure API supports: The data of the selected primary contact is retained on the surviving record.
- [ ] Ensure API supports: Non-primary contacts involved in the merge are **soft-deleted** (deactivated) after the merge is complete.
- [ ] Ensure API supports: All customer linkages from the non-primary (merged) contacts are transferred to the surviving primary contact.
- [ ] Ensure API supports: If a merged (non-primary) contact was designated as a primary or secondary contact for a customer, that designation is transferred to the surviving contact automatically.
- [ ] Ensure API supports: The system must display a clear confirmation summary before executing the merge, listing which contact will survive and which will be deactivated.
- [ ] Ensure API supports: A merge action is recorded in the audit log, referencing all involved contact IDs.
- [ ] Ensure API supports: Soft-deleted contacts created by a merge retain a reference to the surviving contact for traceability.
## 3.7 Contact Groups
- [ ] Implement API logic for 3.7 Contact Groups.

- [ ] Ensure API supports: Users can create a contact group by providing a group name and an optional description.
- [ ] Ensure API supports: Group name is a required field; a group cannot be created without one.
- [ ] Ensure API supports: Description is an optional field.
- [ ] Ensure API supports: During group creation or editing, users can search for and select one or more contacts to add to the group.
- [ ] Ensure API supports: A contact can be a member of multiple groups simultaneously.
- [ ] Ensure API supports: A group can exist with zero contacts; empty groups are permitted.
- [ ] Ensure API supports: Users can view a list of all contact groups, showing group name, description, and member count.
- [ ] Ensure API supports: Users can view the detail of a single group, including the full list of contacts within it.
- [ ] Ensure API supports: Users can edit a group's name, description, and member contacts.
- [ ] Ensure API supports: Users can remove one or more contacts from a group without deleting the group or the contacts.
- [ ] Ensure API supports: Users can delete a contact group. Deleting a group does not affect the contacts within it.
- [ ] Ensure API supports: Group name should be unique; duplicate group names should be flagged with a warning.
- [ ] Ensure API supports: All group create, edit, and delete actions must be recorded in the audit log.
- [ ] Register permission: `contact.create` (Create new contact records)
- [ ] Register permission: `contact.view` (View active contacts and their details)
- [ ] Register permission: `contact.view_inactive` (View soft-deleted / merged contacts)
- [ ] Register permission: `contact.edit` (Edit existing contact records)
- [ ] Register permission: `contact.delete` (Soft-delete a contact)
- [ ] Register permission: `contact.link` (Link a contact to a customer and set primary/secondary designation)
- [ ] Register permission: `contact.merge` (Merge two or more contacts into one)
- [ ] Register permission: `contact_group.create` (Create new contact groups)
- [ ] Register permission: `contact_group.view` (View contact groups and their members)
- [ ] Register permission: `contact_group.edit` (Edit group details and manage member contacts)
- [ ] Register permission: `contact_group.delete` (Delete a contact group)
- [ ] Ensure API supports: All create, edit, merge, and delete actions must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure API supports: Contact search results should return within 2 seconds for datasets up to 10,000 records.
- [ ] Ensure API supports: Soft-deleted contacts must be retained indefinitely for audit and traceability purposes.
- [ ] Ensure API supports: Merge operations must be atomic — either all changes succeed or none are applied.
- [ ] Ensure API supports: Contact group names should be indexed to support fast search and duplicate detection.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
