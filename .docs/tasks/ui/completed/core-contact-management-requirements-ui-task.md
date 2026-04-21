# UI Tasks: Contact Management — Requirements Document

## 3.1 Create Contact
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can create a new contact by providing full name, address, email address, and remarks.
- [ ] Ensure UI supports: Email address is a required field; the form cannot be submitted without it.
- [ ] Ensure UI supports: Full name is stored as a single text field.
- [ ] Ensure UI supports: Address and remarks are optional fields.
- [ ] Ensure UI supports: The system must validate that the email address is in a valid format.
- [ ] Ensure UI supports: Duplicate email addresses should be flagged with a warning, but creation may still proceed (not a hard block).
## 3.2 View Contacts
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active contacts.
- [ ] Ensure UI supports: The contact list supports search by name and email address.
- [ ] Ensure UI supports: Users can view the full detail of a single contact, including all customers the contact is linked to.
- [ ] Ensure UI supports: Soft-deleted (merged) contacts are hidden from the default list view.
- [ ] Ensure UI supports: Users with appropriate permission can view merged/deactivated contacts via a filter or separate view.
## 3.3 Edit Contact
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit the full name, address, email address, and remarks of an existing contact.
- [ ] Ensure UI supports: Email address remains mandatory during edit; it cannot be cleared.
- [ ] Ensure UI supports: Soft-deleted contacts cannot be edited.
## 3.4 Delete Contact
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete a contact that is not linked to any customer.
- [ ] Ensure UI supports: If a contact is linked to one or more customers, the system must warn the user before allowing deletion.
- [ ] Ensure UI supports: Hard deletion is not supported; all deletions are soft deletes.
## 3.5 Link Contact to Customer
- [ ] Implement UI for 3.5 Link Contact to Customer.

- [ ] Ensure UI supports: A contact can be linked to multiple customers.
- [ ] Ensure UI supports: When linking a contact to a customer, the user can designate the contact as the **primary contact** or **secondary contact** for that customer.
- [ ] Ensure UI supports: Each customer can have at most one primary contact and one secondary contact at any time.
- [ ] Ensure UI supports: Assigning a new primary contact to a customer automatically removes the primary designation from the previously assigned primary contact (demotes it, does not unlink).
- [ ] Ensure UI supports: A contact can hold primary or secondary designations across different customers simultaneously.
## 3.6 Merge Contacts
- [ ] Implement UI for 3.6 Merge Contacts.

- [ ] Ensure UI supports: Users can select two or more contacts to merge into a single record.
- [ ] Ensure UI supports: During the merge process, the user must designate one contact as the **primary (surviving) contact**.
- [ ] Ensure UI supports: The data of the selected primary contact is retained on the surviving record.
- [ ] Ensure UI supports: Non-primary contacts involved in the merge are **soft-deleted** (deactivated) after the merge is complete.
- [ ] Ensure UI supports: All customer linkages from the non-primary (merged) contacts are transferred to the surviving primary contact.
- [ ] Ensure UI supports: If a merged (non-primary) contact was designated as a primary or secondary contact for a customer, that designation is transferred to the surviving contact automatically.
- [ ] Ensure UI supports: The system must display a clear confirmation summary before executing the merge, listing which contact will survive and which will be deactivated.
- [ ] Ensure UI supports: A merge action is recorded in the audit log, referencing all involved contact IDs.
- [ ] Ensure UI supports: Soft-deleted contacts created by a merge retain a reference to the surviving contact for traceability.
## 3.7 Contact Groups
- [ ] Implement UI for 3.7 Contact Groups.

- [ ] Ensure UI supports: Users can create a contact group by providing a group name and an optional description.
- [ ] Ensure UI supports: Group name is a required field; a group cannot be created without one.
- [ ] Ensure UI supports: Description is an optional field.
- [ ] Ensure UI supports: During group creation or editing, users can search for and select one or more contacts to add to the group.
- [ ] Ensure UI supports: A contact can be a member of multiple groups simultaneously.
- [ ] Ensure UI supports: A group can exist with zero contacts; empty groups are permitted.
- [ ] Ensure UI supports: Users can view a list of all contact groups, showing group name, description, and member count.
- [ ] Ensure UI supports: Users can view the detail of a single group, including the full list of contacts within it.
- [ ] Ensure UI supports: Users can edit a group's name, description, and member contacts.
- [ ] Ensure UI supports: Users can remove one or more contacts from a group without deleting the group or the contacts.
- [ ] Ensure UI supports: Users can delete a contact group. Deleting a group does not affect the contacts within it.
- [ ] Ensure UI supports: Group name should be unique; duplicate group names should be flagged with a warning.
- [ ] Ensure UI supports: All group create, edit, and delete actions must be recorded in the audit log.
- [ ] Ensure UI supports: All create, edit, merge, and delete actions must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure UI supports: Contact search results should return within 2 seconds for datasets up to 10,000 records.
- [ ] Ensure UI supports: Soft-deleted contacts must be retained indefinitely for audit and traceability purposes.
- [ ] Ensure UI supports: Merge operations must be atomic — either all changes succeed or none are applied.
- [ ] Ensure UI supports: Contact group names should be indexed to support fast search and duplicate detection.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Agent | Implemented forms, merge states, and lists. |
| Testing | Pending |  | |
