# UI Tasks: Customer Management Module — Requirements

## 3.1 Create Customer
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

## 3.2 Read / List Customers
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

## 3.3 View Customer Detail
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

## 3.4 Edit Customer
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

## 3.5 Delete Customer
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

## 3.6 Parent Customer Relationship
- [ ] Implement UI for 3.6 Parent Customer Relationship.

## 3.7 Primary Contact Relationship
- [ ] Implement UI for 3.7 Primary Contact Relationship.

- [ ] Ensure UI supports: Should Account Name uniqueness be enforced globally or only within the same Customer Type?
- [ ] Ensure UI supports: Should there be a way to view all customers linked to a specific contact from the contact's detail page?
- [ ] Ensure UI supports: When a customer's type is locked after creation, should there be an admin override process to change it?
- [ ] Ensure UI supports: Should child customers be listed on the parent customer's detail page?
- [ ] Ensure UI supports: Should the BR Number have a specific format validation, or is it free text?

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Agent | Implemented Customer UI forms, lists, and relationships. Fixed TypeScript error in TR component (added noHover prop support). |
| Testing | Pending |  | |
