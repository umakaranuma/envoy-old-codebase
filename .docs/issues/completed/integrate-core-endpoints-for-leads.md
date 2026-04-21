# Issue: Integrate Core Endpoints for Lead Creation

## Description
The "Create New Lead" (Opportunity) popup in the CRM UI currently uses mock data for several dropdowns. It needs to be integrated with the Core API to fetch real-time data and provide a dynamic contact information selection logic.

## Requirements
- **API Integration**:
  - Implement service methods in `sales.client.ts` to fetch the following from the Core API:
    - Risk Types (Product Categories)
    - Channels
    - Currencies
    - Accounts
    - Contacts
    - Sales Agents (Users)
- **UI Enhancements**:
  - **Dropdowns**: Populate "Risk Type", "Channel", "Currency", and "Sales Agent" dropdowns using data from the Core API.
  - **Contact Info Logic**:
    - Add a toggle/selection for "Contact Info Type" with three options: `Manual`, `Accounts`, `Contacts`.
    - **Manual**: Display input fields for Email and Contact Number.
    - **Accounts**: Fetch all accounts from Core and display them in a searchable dropdown.
    - **Contacts**: Fetch all contacts from Core and display them in a searchable dropdown.
- **Form Submission**:
  - Consolidate all form data and send it to the existing `POST /opportunities` endpoint.
  - Ensure the payload adheres to the backend requirements:
    - `contact_info_type` set to `manual`, `customer`, or `contact`.
    - Relevant IDs (`customer_id`, `contact_id`) or manual values (`email`, `contact_number`) passed correctly.
    - `opportunity_type_id` passed as an array of selected Risk Type IDs.

## Status
| Task | Status |
| :--- | :--- |
| Implement API fetchers in `sales.client.ts` | Completed |
| Add state and data fetching logic to `SalesManagementPage` | Completed |
| Update "Create New Lead" Modal UI with dynamic dropdowns | Completed |
| Implement conditional Contact Info logic | Completed |
| Verify form submission with proper payload mapping | Completed |
