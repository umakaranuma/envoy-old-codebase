# API Tasks: Customer Management Module — Requirements

## 3.1 Create Customer
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

## 3.2 Read / List Customers
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

## 3.3 View Customer Detail
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

## 3.4 Edit Customer
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

## 3.5 Delete Customer
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

## 3.6 Parent Customer Relationship
- [ ] Implement API logic for 3.6 Parent Customer Relationship.

## 3.7 Primary Contact Relationship
- [ ] Implement API logic for 3.7 Primary Contact Relationship.

- [ ] Register permission: `customer.view` (View the customer list and customer details)
- [ ] Register permission: `customer.create` (Create a new customer record)
- [ ] Register permission: `customer.edit` (Edit an existing customer record)
- [ ] Register permission: `customer.delete` (Permanently delete a customer record)
- [ ] Ensure API supports: Should Account Name uniqueness be enforced globally or only within the same Customer Type?
- [ ] Ensure API supports: Should there be a way to view all customers linked to a specific contact from the contact's detail page?
- [ ] Ensure API supports: When a customer's type is locked after creation, should there be an admin override process to change it?
- [ ] Ensure API supports: Should child customers be listed on the parent customer's detail page?
- [ ] Ensure API supports: Should the BR Number have a specific format validation, or is it free text?

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
