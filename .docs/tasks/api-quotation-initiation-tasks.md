# API Tasks: Quotation Request Initiation

## Overview
Based on the `quotation-management-spec.md`, these are the backend API and database tasks to support the Quotation Request Initiation flow.

## Tasks

- [ ] **Task 1: Database Models & Migrations**
  - [ ] Verify or create `crmq_quotation_requests` model with all required columns.
  - [ ] Verify or create the junction model `crmq_quotation_request_insurers`.
  - [ ] Verify or create the `crmq_quotation_communications` model.
  - [ ] Generate and run database migrations.

- [ ] **Task 2: Support Endpoints (Data Fetching for UI)**
  - [ ] Implement/Verify `GET /quotation-requests/init-data` (or similar logic) to resolve Risk Types and pre-filter Native Products for a given Lead (`?opportunity_id=<id>`).
  - [ ] Implement/Verify `GET /quotation-requests/insurers-by-product` to return a list of service providers matching the given Product ID.

- [ ] **Task 3: Quotation Request Creation Endpoint Payload Processing**
  - [ ] Implement `POST /quotation-requests` (or `/quotation-requests/<id>/send` composite endpoint) to receive payload: `opportunity_id`, `product_id`, `insurer_ids`, `subject`, `body`.
  - [ ] **Data Derivation**: Extract and derive `risk_type_id`, `customer_id`, and `account_manager_id` securely from the associated Lead context (`opportunity_id`).
  - [ ] **Stage & Approval Resolution**: Determine the appropriate `stage_id` (`SENT` vs `PENDING`) using settings from `core_settings` configuration for approval rules. Set `request_type` based on Lead info.

- [ ] **Task 4: Request Data Persistence**
  - [ ] Create the main `crmq_quotation_requests` record. Auto-generate the unique `code` (e.g., `QR-000001`).
  - [ ] Create multiple junction rows in `crmq_quotation_request_insurers` using the received `insurer_ids`.
  - [ ] Create initial outbound record in `crmq_quotation_communications` marking `has_attachment = true`.

- [ ] **Task 5: Excel Generation & Outbound Dispatch**
  - [ ] Implement server-side generation of an Excel attachment detailing the Risk Details extracted from the associated Lead.
  - [ ] Check validation: If `approval_required = false`, send the outbound email to the selected service providers via email client with Excel attached. Log the event.
  - [ ] If `approval_required = true`, route a notification to the system's Account Manager and bypass direct email dispatch.

---
**Status:** In Progress
