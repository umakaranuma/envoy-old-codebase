# Customer Management Module — Requirements

## 1. Overview

The Customer Management module allows authorised users to create and manage customer records within the application. Customers can be of two types — **Corporate** or **Private** — and share the same set of fields regardless of type. Each customer can optionally be linked to a parent customer of the same type (one level deep only), and must have one primary contact either selected from the existing contacts list or created inline during customer creation. The contact is stored with a reference to the customer it was linked from, and a single contact can be linked to multiple customers.

---

## 2. Key Rules

- Customers are one of two types: **Corporate** or **Private**. All fields apply to both types.
- A customer can optionally have **one parent customer**, but the parent must be of the **same type** (Corporate → Corporate, Private → Private).
- Parent-child relationship is **one level deep only** — a child customer cannot itself be a parent.
- Each customer has **exactly one primary contact**.
- The primary contact can be **selected from the existing contacts list** or **created as a new contact inline**.
- A contact can be **linked to multiple customers**.
- The contact's ID is stored against the customer record to maintain the relationship.
- All actions are **permission-based**, governed by the role assigned to the acting user.

---

## 3. Functional Requirements

### 3.1 Create Customer

**Description:** Any user whose role includes the `customer.create` permission can create a new customer record.

**Permission Required:** `customer.create`

**Input Fields:**

| Field                   | Type          | Required | Constraints                                                                 |
|-------------------------|---------------|----------|-----------------------------------------------------------------------------|
| Customer Type           | Single-select | Yes      | Options: Corporate, Private                                                 |
| Account Name            | Text          | Yes      | Unique, max 200 characters                                                  |
| Email                   | Email         | Yes      | Valid email format                                                          |
| Address                 | Textarea      | No       | Max 500 characters                                                          |
| Website                 | URL           | No       | Valid URL format (e.g., https://example.com)                                |
| Primary Contact Number  | Text          | Yes      | Valid phone number with country code                                        |
| Secondary Contact Number| Text          | No       | Valid phone number with country code                                        |
| BR Number               | Text          | No       | Max 100 characters                                                          |
| Remarks                 | Textarea      | No       | Max 1000 characters                                                         |
| Parent Customer         | Single-select | No       | Must be same type as the customer being created; one level deep only        |
| Primary Contact         | Search-select or Inline Create | Yes | Select from existing contacts or create a new contact inline  |

**Behaviour:**
- The **Create Customer** option is only visible to users with the `customer.create` permission.
- **Customer Type** must be selected first — it determines which customers are available in the Parent Customer dropdown.
- **Account Name** must be unique across all customers in the system.
- **Parent Customer** dropdown only lists customers of the same type as the selected Customer Type.
- A customer that is already a child (has a parent) cannot appear in the Parent Customer dropdown — only level one customers (root customers) are selectable as parents.
- **Primary Contact** field allows two paths:
  - **Search & Select** — search the existing contacts list and select one.
  - **Create New Contact** — opens an inline form to create a new contact (see Section 3.1.1).
- The selected or newly created contact's ID is stored against the customer record.
- On successful creation, the customer appears in the customer list.

---

#### 3.1.1 Inline Contact Creation

**Description:** When creating a customer, if the required contact does not exist in the system, the user can create a new contact directly from within the customer form without navigating away.

**Inline Contact Form Fields:**

| Field        | Type          | Required | Constraints                              |
|--------------|---------------|----------|------------------------------------------|
| Salutation   | Single-select | No       | Options: Mr., Mrs., Ms., Miss., Dr., Prof., Other |
| First Name   | Text          | Yes      | Max 100 characters                       |
| Last Name    | Text          | Yes      | Max 100 characters                       |
| Email        | Email         | Yes      | Valid email format                       |
| Phone Number | Text          | Yes      | Valid phone number with country code     |
| Job Title    | Text          | No       | Max 150 characters                       |

**Behaviour:**
- The inline contact form opens as a modal or an expandable panel within the customer creation form.
- On saving the inline contact form, the new contact is created in the contacts list and its ID is immediately populated in the Primary Contact field of the customer form.
- If the inline contact creation is cancelled, the Primary Contact field returns to its empty state.
- The newly created contact is available in the contacts list for future use with other customers.
- A contact created inline can be linked to multiple customers — it is not exclusive to the customer it was created from.

---

### 3.2 Read / List Customers

**Description:** Displays all customer records in a paginated, searchable list.

**Permission Required:** `customer.view`

**Displayed Columns:**

| Column                 | Description                                      |
|------------------------|--------------------------------------------------|
| Account Name           | Name of the customer                             |
| Customer Type          | Corporate / Private                              |
| Email                  | Customer email address                           |
| Primary Contact Number | Main contact number                              |
| Primary Contact        | Name of the linked primary contact               |
| Parent Customer        | Name of the parent customer (if applicable)      |
| Created At             | Date the customer record was created             |
| Actions                | View / Edit / Delete                             |

**Behaviour:**
- The customer list is only visible to users with the `customer.view` permission.
- Search and filter by account name, customer type, email, or parent customer.
- Pagination supported.
- Action buttons (Edit, Delete) are shown only if the user holds the respective permissions.
- Clicking a customer name opens the customer detail view.

---

### 3.3 View Customer Detail

**Description:** Displays the full details of a specific customer record.

**Permission Required:** `customer.view`

**Displayed Information:**

| Field                    | Description                                              |
|--------------------------|----------------------------------------------------------|
| Customer Type            | Corporate / Private                                      |
| Account Name             | Customer account name                                    |
| Email                    | Customer email                                           |
| Address                  | Customer address                                         |
| Website                  | Customer website URL                                     |
| Primary Contact Number   | Main phone number                                        |
| Secondary Contact Number | Secondary phone number (if provided)                     |
| BR Number                | Business registration number (if provided)               |
| Remarks                  | Additional notes                                         |
| Parent Customer          | Linked parent customer name (if applicable)              |
| Primary Contact          | Contact name, email, phone, and job title                |
| Child Customers          | List of customers that have this customer as their parent |
| Created At / Updated At  | Record timestamps                                        |

---

### 3.4 Edit Customer

**Description:** Allows a user with the appropriate permission to update a customer record.

**Permission Required:** `customer.edit`

**Editable Fields:** All fields from Section 3.1, pre-populated with existing data.

**Behaviour:**
- The **Edit** action is only visible to users with the `customer.edit` permission.
- Account Name must remain unique (excluding the current customer).
- Customer Type **cannot be changed** after creation — changing the type would invalidate the parent-child relationship and contact links.
- If the Parent Customer is changed, the new selection must still be of the same type and must be a root-level customer.
- The Primary Contact can be replaced by selecting a different existing contact or creating a new one inline.
- Changing the Primary Contact updates the stored contact ID on the customer record.
- Changes take effect immediately upon saving.
- An audit log entry is created recording what changed, who made the change, and when.

---

### 3.5 Delete Customer

**Description:** Allows permanent removal of a customer record.

**Permission Required:** `customer.delete`

**Behaviour:**
- The **Delete** action is only visible to users with the `customer.delete` permission.
- **Deletion is blocked if the customer has child customers linked to it.** An error message is shown:
  > *"This customer cannot be deleted because it has [n] child customer(s) linked to it. Please reassign or remove all child customers before deleting."*
- A confirmation dialog is shown before deletion:
  > *"Are you sure you want to delete [Account Name]? This action cannot be undone."*
- On successful deletion, the customer record is permanently removed.
- The primary contact record is **not deleted** — it remains in the contacts list and may still be linked to other customers.

---

### 3.6 Parent Customer Relationship

**Description:** An optional one-level parent-child relationship between customers of the same type.

**Rules:**

| Rule                                              | Detail                                                        |
|---------------------------------------------------|---------------------------------------------------------------|
| Same type only                                    | Corporate customers can only have Corporate parents; Private customers can only have Private parents |
| One level deep only                               | A child customer cannot be selected as a parent              |
| One parent only                                   | A customer can have at most one parent                        |
| Multiple children allowed                         | A parent customer can have multiple child customers           |
| Deletion blocked                                  | A parent customer cannot be deleted while it has children     |

**Behaviour:**
- The Parent Customer dropdown is filtered dynamically based on the selected Customer Type.
- Only root-level customers (those with no parent themselves) are shown in the Parent Customer dropdown.
- The parent-child relationship is displayed in both the parent's and child's detail views.

---

### 3.7 Primary Contact Relationship

**Description:** Each customer must have exactly one primary contact stored by contact ID.

**Rules:**

| Rule                                              | Detail                                                        |
|---------------------------------------------------|---------------------------------------------------------------|
| One primary contact per customer                  | Each customer record holds exactly one contact ID             |
| Contact reusability                               | The same contact can be the primary contact for multiple customers |
| Contact not deleted with customer                 | Deleting a customer does not delete the linked contact        |
| Contact created inline                            | New contacts can be created directly within the customer form |

**Behaviour:**
- The Primary Contact field stores the contact's unique ID against the customer record.
- When a contact is selected or created, the system displays the contact's name, email, phone, and job title as a preview within the customer form.
- If a contact linked to a customer is later deleted from the contacts module, the customer record should flag the primary contact as missing and prompt the user to reassign.

---

## 4. Permission Reference

All Customer Management actions are governed by the following permissions, assigned via the Role Management module.

| Permission Key     | Action Controlled                                            |
|--------------------|--------------------------------------------------------------|
| `customer.view`    | View the customer list and customer details                  |
| `customer.create`  | Create a new customer record                                 |
| `customer.edit`    | Edit an existing customer record                             |
| `customer.delete`  | Permanently delete a customer record                         |

> Users without a permission will not see the associated UI controls or be able to call the associated API endpoints.

---

## 5. Non-Functional Requirements

| Requirement             | Detail                                                                                           |
|-------------------------|--------------------------------------------------------------------------------------------------|
| Permission Enforcement  | All actions enforced on both frontend (UI visibility) and backend (API level)                   |
| Uniqueness              | Account Name must be unique system-wide; validated on both client and server                    |
| Type Lock               | Customer Type cannot be modified after creation                                                 |
| Parent Validation       | Parent customer type match and depth limit enforced at both UI and API level                    |
| Contact Integrity       | Contact ID stored as a foreign key reference; orphaned contact links flagged to the user        |
| Audit Logging           | All create, edit, and delete actions logged with acting user identity and timestamp              |
| Validation              | All inputs validated on both client and server side                                             |
| Responsiveness          | UI must be responsive across desktop and tablet screen sizes                                    |

---

## 6. User Stories

| ID    | User Story                                                                                                                                      |
|-------|-------------------------------------------------------------------------------------------------------------------------------------------------|
| CM-01 | As a user with `customer.create` permission, I want to create a Corporate or Private customer with all relevant details.                        |
| CM-02 | As a user, I want to select a parent customer of the same type so I can define customer relationships.                                          |
| CM-03 | As a user, I want to select an existing contact as the primary contact so I can link an already known person to the customer.                   |
| CM-04 | As a user, I want to create a new contact inline while creating a customer so I don't have to navigate away from the form.                      |
| CM-05 | As a user with `customer.view` permission, I want to view a list of all customers with key details so I can manage them effectively.            |
| CM-06 | As a user with `customer.view` permission, I want to view the full details of a customer including their primary contact and parent customer.   |
| CM-07 | As a user with `customer.edit` permission, I want to update a customer's details and reassign the primary contact when needed.                  |
| CM-08 | As a user with `customer.delete` permission, I want to delete a customer record that has no child customers linked to it.                       |
| CM-09 | As a user, I want to be prevented from deleting a customer that has child customers so that relationships are not accidentally broken.           |
| CM-10 | As a user, I want to be prevented from selecting a child customer as a parent so the one-level depth rule is always maintained.                 |
| CM-11 | As a user, I want to be notified if a customer's primary contact has been deleted so I can reassign a valid contact.                            |

---

## 7. Out of Scope

- Contact management CRUD (handled in the Contacts module).
- Customer merge or duplicate detection.
- Customer portal or self-service access.
- Customer credit limits or financial data.
- Multi-type parent relationships (e.g., Corporate parent for a Private customer).

---

## 8. Open Questions

| #  | Question                                                                                                       | Owner     |
|----|----------------------------------------------------------------------------------------------------------------|-----------|
| 1  | Should Account Name uniqueness be enforced globally or only within the same Customer Type?                     | Product   |
| 2  | Should there be a way to view all customers linked to a specific contact from the contact's detail page?       | Product   |
| 3  | When a customer's type is locked after creation, should there be an admin override process to change it?       | Product   |
| 4  | Should child customers be listed on the parent customer's detail page?                                         | Product   |
| 5  | Should the BR Number have a specific format validation, or is it free text?                                    | Tech Lead |
