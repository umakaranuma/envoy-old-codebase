# Issue: Add Native Product to Sales Team

## Description
In the sales team creation popup, a new dropdown field for "Native Product" should be added. This field is optional.

## Requirements
- **Database**: Add a `native_product` foreign key to the `core_sales_teams` table, referencing `core_native_products`.
- **API**:
  - Update the Sales Team create/update endpoints to handle the optional `native_product_id`.
  - Ensure the list and detail endpoints return the linked native product information.
- **UI**:
  - Add a "Native Product" dropdown to the Sales Team creation and update popups.
  - The dropdown labels should be fetched from the Native Products list endpoint.
  - The field is not required.

## Status
| Task | Status |
| :--- | :--- |
| Add Native Product association to Sales Team | Completed |
