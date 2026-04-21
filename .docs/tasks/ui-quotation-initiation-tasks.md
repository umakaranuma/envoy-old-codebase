# UI Tasks: Quotation Request Initiation

## Overview
Based on the `quotation-management-spec.md`, these are the frontend tasks to implement the Quotation Request Initiation flow.

## Tasks

- [ ] **Task 1: Quotation Request Initiation Modal (UI Component)**
  - [ ] Implement the base modal component.
  - [ ] Add Form state management (using React Hook Form and Zod).
  - [ ] Add fields: Lead (Search/Select), Risk Type (Read-only), Product (Select), and Insurers (Multi-select Checkboxes).
  - [ ] Implement conditional rendering: if initiated from a Lead Profile directly, hide the Lead selection field and pre-fill Risk Type.

- [ ] **Task 2: API Integration inside Modal (Frontend)**
  - [ ] Integrate endpoint to fetch Lead Data/Qualified Leads list.
  - [ ] Integrate GET request to fetch initialization data upon Lead selection to auto-fill Risk Type.
  - [ ] Integrate fetching of available Native Products constrained by the selected Risk Type.
  - [ ] Integrate GET request to fetch and auto-select Insurers based on the selected Product.
  - [ ] Handle component re-renders, auto-selections, and field resets when Product or Lead changes.

- [ ] **Task 3: Email Composition Component (Screen 4)**
  - [ ] Implement an email composer UI.
  - [ ] Display "To" field as a read-only chip list of the selected insurers' email addresses.
  - [ ] Add "Subject" input field with validation (Required).
  - [ ] Add "Body" rich text or textarea field, pre-populated with standard default template.
  - [ ] Add read-only "Attachment" badge indicating Risk Detail Excel will be attached.
  
- [ ] **Task 4: Submit & Dispatch Workflow**
  - [ ] Collect data payload: `opportunity_id`, `product_id`, `insurer_ids`, `subject`, `body`.
  - [ ] Form Submission: Create a `POST` request to the backend with the collected payload.
  - [ ] Handle response: Show success toast/notification.
  - [ ] Navigate user to the newly created Quotation Single View page if successful.

---
**Status:** In Progress
