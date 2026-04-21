# Quotation Management — Full Specification

**Module:** CRM  
**Feature:** Quotation Management  
**Version:** 1.0  
**Status:** Ready for Development  
**Last Updated:** 2026-03-30

---

## Terminology

> **Quotation Request** refers to the top-level record that tracks the entire quotation lifecycle for a lead.  
> **Received Quotation** refers to an individual insurer's quotation response captured within a quotation request.  
> **Shortlisted Quotation** refers to a received quotation selected by the agent for customer presentation.  
> **Insurer**, **Partner**, and **Service Provider** refer to the same entity throughout this document.  
> **Risk Type** and **Product Category** refer to the same entity.  
> **Lead** and **Opportunity** are interchangeable — see Sales Management spec for full definition.

---

## Table of Contents

1. [Overview & Architecture](#1-overview--architecture)
2. [Status System — Source from `core_status`](#2-status-system--source-from-core_status)
3. [Database Tables & Columns](#3-database-tables--columns)
4. [API Endpoints](#4-api-endpoints)
5. [Screen 1 — Quotation Request List View](#5-screen-1--quotation-request-list-view)
6. [Screen 2 — Quotation Request Initiation (from Lead)](#6-screen-2--quotation-request-initiation-from-lead)
7. [Screen 3 — Quotation Request Initiation (from Quotation Module)](#7-screen-3--quotation-request-initiation-from-quotation-module)
8. [Screen 4 — Email Composition & Dispatch](#8-screen-4--email-composition--dispatch)
9. [Screen 5 — Quotation Single View](#9-screen-5--quotation-single-view)
10. [Screen 6 — Received Quotations Management](#10-screen-6--received-quotations-management)
11. [Screen 7 — Quotation Comparison & Shortlisting](#11-screen-7--quotation-comparison--shortlisting)
12. [Screen 8 — Sharing Quotations with Customer](#12-screen-8--sharing-quotations-with-customer)
13. [Screen 9 — Recommendation Document](#13-screen-9--recommendation-document)
14. [Screen 10 — Customer Confirmation](#14-screen-10--customer-confirmation)
15. [Screen 11 — Policy Request Initiation](#15-screen-11--policy-request-initiation)
16. [Business Logic & Key Rules](#16-business-logic--key-rules)
17. [Permission Reference](#17-permission-reference)
18. [Non-Functional Requirements](#18-non-functional-requirements)

---

## 1. Overview & Architecture

The Quotation Module manages the full lifecycle of a quotation — from requesting quotes from insurers, through capturing and comparing responses, to customer confirmation and policy request initiation. A quotation request may be initiated from a Lead Profile or directly from the Quotation Module.

**No separate quotation status table is used.** All statuses come from the shared `core_status` table filtered by `module = 'quotation'`.

### Module Dependencies

```
crm_opportunities (Lead)
    ↓
crmq_quotation_requests
    ├── core_status (module='quotation')          ← drives request stage
    ├── core_risk_types (Risk Type)               ← auto-filled from lead
    ├── core_native_products (Native Product)     ← filtered by risk type
    ├── core_service_providers (Insurers)         ← auto-selected by product
    ├── core_customers (Customer Account)         ← carried from lead
    └── core_users (requested_by, account_manager)

crmq_received_quotations
    ├── crmq_quotation_requests
    └── core_service_providers (Insurer)

crmq_shortlisted_quotations
    ├── crmq_quotation_requests
    └── crmq_received_quotations

crmq_recommendation_documents
    ├── crmq_quotation_requests
    └── crmq_shortlisted_quotations (many-to-many)

crmq_quotation_communications (Chat)
    └── crmq_quotation_requests
```

### Quotation Request Lifecycle Flow

```
INITIATION (Lead / Quotation Module)
    ↓
INSURER SELECTION → EMAIL COMPOSITION → APPROVAL CHECK
    ↓                                       ↓
[Skip Approval]                    [Approval Required]
    ↓                                       ↓
SENT TO INSURERS ←─────────────── Account Manager Approves
    ↓
QUOTATIONS RECEIVED → COMPARISON → SHORTLISTING
    ↓
SHARE WITH CUSTOMER (direct quotation OR recommendation document)
    ↓
CUSTOMER CONFIRMATION (portal OR agent)
    ↓
POLICY REQUEST INITIATED
```

---

## 2. Status System — Source from `core_status`

### Query to Get Quotation Stages

```sql
SELECT id, name, type, color, sort_index
FROM core_status
WHERE module = 'quotation'
ORDER BY sort_index ASC;
```

### Seeded Quotation Stages

| Name | Type Code | Color | Hex | Sort |
|------|-----------|-------|-----|------|
| REQUESTED | `quotation_draft` | Grey | `#6c757d` | 1 |
| SENT | `quotation_sent` | Teal | `#0E7090` | 2 |
| INPROGRESS | `quotation_inprogress` | Blue | `#175CD3` | 3 |
| REJECTED | `quotation_rejected` | Red | `#B42318` | 4 |
| PENDING | `quotation_pending` | Amber | `#B54708` | 5 |
| CONFIRMED | `quotation_confirmed` | Green | `#067647` | 6 |
| EXPIRED | `quotation_expired` | Dark | `#344054` | 7 |

> **Critical:** Filter by `module = 'quotation'`. The `type` column stores the unique code (e.g. `quotation_draft`).

---

## 3. Database Tables & Columns

### 3.1 `crmq_quotation_requests`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `code` | VARCHAR(50) | No | Unique auto-generated ID. Format: `QR-000001`. |
| `requested_date` | DATE | No | Date the request was created. Defaults to today. |
| `request_type` | VARCHAR(20) | No | `new` or `renewal`. |
| `stage_id` | INT (FK) | No | FK → `core_status.id` WHERE `module='quotation'`. |
| `requested_by_id` | INT (FK) | No | FK → `core_users.id`. Auto-set from `request.user`. |
| `account_manager_id` | INT (FK) | Yes | FK → `core_users.id`. Resolved from lead team if not provided. |
| `opportunity_id` | INT (FK) | No | FK → `crm_opportunities.id`. CASCADE delete. |
| `customer_id` | INT (FK) | No | FK → `core_customers.id`. Carried from lead. |
| `risk_type_id` | INT (FK) | Yes | FK → `core_risk_types.id`. Auto-filled from lead risk data. |
| `product_id` | INT (FK) | Yes | FK → `core_native_products.id`. Native product selected by user. |
| `approval_required` | BOOLEAN | No | Whether approval routing is active. Derived from `core_settings`. |
| `created_at` | DATETIME | No | Auto-set on creation. |
| `updated_at` | DATETIME | No | Auto-updated on save. |

**Indexes:** PK on `id`, index on `opportunity_id`, `stage_id`, `customer_id`.

---

### 3.2 `crmq_quotation_request_insurers` (junction)

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `quotation_request_id` | INT (FK) | FK → `crmq_quotation_requests.id`. CASCADE delete. |
| `insurer_id` | INT (FK) | FK → `core_service_providers.id`. RESTRICT delete. |

> Populated automatically based on product-insurer mapping. User can modify selection before sending.

---

### 3.3 `crmq_quotation_communications`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `quotation_request_id` | INT (FK) | No | FK → `crmq_quotation_requests.id`. CASCADE delete. |
| `insurer_id` | INT (FK) | Yes | FK → `core_service_providers.id`. NULL for internal messages. |
| `direction` | VARCHAR(10) | No | `outbound` (to insurer) or `inbound` (from insurer). |
| `subject` | VARCHAR(255) | Yes | Email subject. |
| `body` | TEXT | No | Email body / message content. |
| `sent_by_id` | INT (FK) | Yes | FK → `core_users.id`. NULL for inbound. |
| `sent_at` | DATETIME | No | Timestamp of send / receipt. |
| `has_attachment` | BOOLEAN | No | Whether risk detail Excel was attached (outbound). |

---

### 3.4 `crmq_received_quotations`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `quotation_request_id` | INT (FK) | No | FK → `crmq_quotation_requests.id`. CASCADE delete. |
| `insurer_id` | INT (FK) | No | FK → `core_service_providers.id`. RESTRICT delete. |
| `quotation_version` | VARCHAR(20) | Yes | Version label (e.g. `v1`, `v2`). |
| `quotation_ref` | VARCHAR(100) | Yes | Insurer's own quotation ID / reference. |
| `quotation_value` | DECIMAL(20,2) | Yes | Premium or quoted value. |
| `received_date` | DATE | No | Date quotation was received. |
| `expiry_date` | DATE | Yes | Quotation expiry date. |
| `status_id` | INT (FK) | No | FK → `core_status.id`. `quotation_confirmed` or `quotation_rejected`. |
| `document` | VARCHAR(500) | Yes | File path to uploaded quotation document. |
| `is_auto_extracted` | BOOLEAN | No | Whether data was pre-filled by system scan. Defaults to `false`. |
| `added_manually` | BOOLEAN | No | Whether this entry was created via "Add New". Defaults to `false`. |
| `created_by_id` | INT (FK) | Yes | FK → `core_users.id`. |
| `created_at` | DATETIME | No | Auto-set on creation. |

**Computed field:** `remaining_days` = `expiry_date - today` (returned in API response; not stored).

---

### 3.5 `crmq_shortlisted_quotations`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `quotation_request_id` | INT (FK) | No | FK → `crmq_quotation_requests.id`. CASCADE delete. |
| `received_quotation_id` | INT (FK) | No | FK → `crmq_received_quotations.id`. CASCADE delete. |
| `shortlisted_by_id` | INT (FK) | No | FK → `core_users.id`. |
| `shortlisted_at` | DATETIME | No | Timestamp of shortlisting. |

---

### 3.6 `crmq_recommendation_documents`

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `quotation_request_id` | INT (FK) | No | FK → `crmq_quotation_requests.id`. CASCADE delete. |
| `document` | VARCHAR(500) | No | File path to generated recommendation document. |
| `status` | VARCHAR(10) | No | `draft` or `sent`. |
| `created_by_id` | INT (FK) | No | FK → `core_users.id`. |
| `sent_at` | DATETIME | Yes | NULL if still draft. |
| `created_at` | DATETIME | No | Auto-set on creation. |

---

### 3.7 `crmq_recommendation_document_quotations` (junction)

| Column | Type | Description |
|--------|------|-------------|
| `recommendation_document_id` | INT (FK) | FK → `crmq_recommendation_documents.id`. CASCADE delete. |
| `shortlisted_quotation_id` | INT (FK) | FK → `crmq_shortlisted_quotations.id`. RESTRICT delete. |

---

## 4. API Endpoints

### 4.1 Quotation Requests

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/quotation-requests` | `quotation.view` | List all quotation requests. Supports filters: `stage`, `customer_id`, `opportunity_id`, `requested_by`, `date_from`, `date_to`. |
| `POST` | `/quotation-requests` | `quotation.create` | Create a new quotation request. |
| `GET` | `/quotation-requests/<id>` | `quotation.view` | Single quotation request with full joined data. |
| `PUT` | `/quotation-requests/<id>` | `quotation.update` | Update quotation request details. |
| `DELETE` | `/quotation-requests/<id>` | `quotation.delete` | Soft-delete a quotation request. |
| `PATCH` | `/quotation-requests/<id>/stage` | `quotation.update` | Update quotation request stage. |
| `GET` | `/quotation-requests/<id>/insurers` | `quotation.view` | List insurers selected for this request. |
| `PUT` | `/quotation-requests/<id>/insurers` | `quotation.update` | Replace insurer selection list. |

---

### 4.2 Quotation Initiation Support

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/quotation-requests/init-data` | `quotation.create` | Returns risk type (from lead), filtered native products, and auto-selected insurer list. Query param: `?opportunity_id=<id>`. |
| `GET` | `/quotation-requests/insurers-by-product` | `quotation.create` | Returns insurers supporting a given product. Query param: `?product_id=<id>`. |
| `GET` | `/quotation-requests/approval-config` | — | Returns whether approval routing is active for quotation dispatch. |

---

### 4.3 Email Dispatch

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `POST` | `/quotation-requests/<id>/send` | `quotation.send` | Send quotation request email to insurers (or to account manager if approval required). Attaches risk detail Excel. |
| `POST` | `/quotation-requests/<id>/approve` | `quotation.approve` | Account manager approves and forwards request to insurers. |

---

### 4.4 Communications (Chat)

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/quotation-requests/<id>/communications` | `quotation.view` | List all communication threads for the quotation request. |
| `POST` | `/quotation-requests/<id>/communications` | `quotation.update` | Add a new message / log an inbound reply. |

---

### 4.5 Received Quotations

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/quotation-requests/<id>/received-quotations` | `quotation.view` | List all received quotations for a request. |
| `POST` | `/quotation-requests/<id>/received-quotations` | `quotation.update` | Manually add a received quotation. |
| `PUT` | `/quotation-requests/<id>/received-quotations/<rq_id>` | `quotation.update` | Update a received quotation record. |
| `DELETE` | `/quotation-requests/<id>/received-quotations/<rq_id>` | `quotation.update` | Remove a received quotation. |
| `POST` | `/quotation-requests/<id>/received-quotations/<rq_id>/attach` | `quotation.update` | Attach a document from communication chat to a quotation record. Triggers auto-extraction attempt. |

---

### 4.6 Shortlisting & Comparison

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/quotation-requests/<id>/shortlisted` | `quotation.view` | List shortlisted quotations. |
| `POST` | `/quotation-requests/<id>/shortlisted` | `quotation.update` | Shortlist one or more received quotations. Body: `{ received_quotation_ids: [1, 2] }`. |
| `DELETE` | `/quotation-requests/<id>/shortlisted/<sq_id>` | `quotation.update` | Remove a quotation from shortlist. |
| `GET` | `/quotation-requests/<id>/compare` | `quotation.view` | Return side-by-side comparison data for selected received quotations. Query: `?ids=1,2,3`. |

---

### 4.7 Recommendation Documents

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/quotation-requests/<id>/recommendation-documents` | `quotation.view` | List all recommendation documents (sent and draft). |
| `POST` | `/quotation-requests/<id>/recommendation-documents` | `quotation.update` | Generate a new recommendation document from shortlisted quotations. |
| `PUT` | `/quotation-requests/<id>/recommendation-documents/<doc_id>` | `quotation.update` | Update a draft recommendation document. |
| `POST` | `/quotation-requests/<id>/recommendation-documents/<doc_id>/send` | `quotation.send` | Send recommendation document to customer. Updates status to `sent`. |

---

### 4.8 Customer Confirmation

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `PATCH` | `/quotation-requests/<id>/received-quotations/<rq_id>/confirm` | `quotation.update` | Agent manually marks a quotation as confirmed. Remaining quotations are marked rejected. |
| `POST` | `/quotation-requests/<id>/confirm-via-portal` | — | Internal endpoint called by Customer Portal on selection. Auto-confirms selected, rejects others. |

---

### 4.9 Policy Request Initiation

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `POST` | `/quotation-requests/<id>/initiate-policy` | `policy.create` | Creates a policy request pre-filled with customer, risk data, insurer, and pricing from the confirmed quotation. |

---

## 5. Screen 1 — Quotation Request List View

### 5.1 Layout

A paginated, filterable table of all quotation requests accessible to the logged-in user.

### 5.2 Displayed Columns

| Column | Source |
|--------|--------|
| Quotation Request ID | `crmq_quotation_requests.code` |
| Requested Date | `crmq_quotation_requests.requested_date` |
| Request Type | `crmq_quotation_requests.request_type` (`new` / `renewal`) |
| Stage | `core_status.name` (badge with status color) |
| Requested By | `core_users.full_name` |
| Customer Account | `core_customers.name` |
| Actions | View / Delete |

### 5.3 Filters

- Stage (multi-select from `core_status WHERE module='quotation'`)
- Date range (requested date from / to)
- Request type (`new` / `renewal`)
- Customer account (search)
- Requested by (user search)

### 5.4 Behaviour

- Clicking a row opens the Quotation Single View.
- A **"New Quotation Request"** button opens the initiation flow (Screen 3).
- Pagination is supported (default 20 per page).

---

## 6. Screen 2 — Quotation Request Initiation (from Lead)

### 6.1 Pre-conditions

The following must be true before "Request Quotation" is available on a Lead Profile:

| # | Condition |
|---|-----------|
| PC-01 | Lead must be in the **QUALIFIED** stage. |
| PC-02 | A **customer account** must be mapped to the lead. |
| PC-03 | **Risk details** must have been recorded on the lead. |

If any condition is unmet, the "Request Quotation" button is disabled and shows an inline tooltip explaining the missing requirement.

### 6.2 Modal Fields

When the user clicks "Request Quotation" on a qualified lead, a modal opens:

| Field | Type | Behaviour |
|-------|------|-----------|
| Risk Type | Read-only | Auto-populated from lead risk data. |
| Product (Native Product) | Select | Filtered to products mapped to the selected risk type. Required. |
| Insurers | Multi-select (checkbox list) | Auto-selected based on product-insurer mapping. User can modify. At least one required. |

### 6.3 Behaviour

- Selecting a different product re-queries insurer list and resets selection.
- User can deselect or add insurers manually.
- On **Proceed**, the system navigates to the Email Composition screen (Screen 4).

---

## 7. Screen 3 — Quotation Request Initiation (from Quotation Module)

### 7.1 Modal Fields

| Field | Type | Behaviour |
|-------|------|-----------|
| Lead | Search / Select | Required. User searches and selects from qualified leads. |
| Risk Type | Read-only | Auto-filled from the selected lead's risk data. |
| Product (Native Product) | Select | Auto-filled if a product was already selected on the lead. Otherwise user selects. |
| Insurers | Multi-select | Auto-selected based on product. User can modify. |

### 7.2 Behaviour

- Once a lead is selected, risk type and product populate automatically where available.
- Remaining flow (email composition, approval) is identical to Screen 2.

---

## 8. Screen 4 — Email Composition & Dispatch

### 8.1 Layout

Full-page or large modal email composer shown after insurer selection.

### 8.2 Fields

| Field | Type | Behaviour |
|-------|------|-----------|
| To | Read-only chip list | Insurer contact emails from `core_service_providers`. Not editable here. |
| Subject | Text input | Editable. No default. Required. |
| Body | Rich text / textarea | Pre-populated with configurable email template. Editable. |
| Attachment | Read-only badge | Risk detail auto-attached as Excel file. Cannot be removed. |

### 8.3 Approval Routing

| Condition | Behaviour |
|-----------|-----------|
| `approval_required = false` | Email is sent directly to all selected insurers on click of **Send**. |
| `approval_required = true` | Email is routed to the Account Manager for review. Status set to `PENDING`. A notification is sent to the Account Manager. |

> Approval configuration is read from `core_settings` (entity type: `common_approval`).

### 8.4 Post-Send Behaviour

- A `crmq_quotation_requests` record is created with stage `SENT` (or `PENDING` if approval required).
- A `crmq_quotation_communications` outbound record is logged.
- The user is redirected to the Quotation Single View.

---

## 9. Screen 5 — Quotation Single View

The Quotation Single View is the primary workspace for the full quotation lifecycle after initiation.

### 9.1 Sections

#### 9.1.1 Basic Details

| Field | Source |
|-------|--------|
| Request ID | `crmq_quotation_requests.code` |
| Stage | `core_status.name` (colored badge) |
| Requested By | `core_users.full_name` |
| Request Date | `crmq_quotation_requests.requested_date` |
| Request Type | `crmq_quotation_requests.request_type` |
| Customer Account | `core_customers.name` |
| Product | `core_native_products.name` |
| Risk Type | `core_risk_types.title` |

#### 9.1.2 Risk Details

- Dynamic table rendered based on the risk type associated with the lead.
- Read-only display of all risk submission fields and values.
- Content sourced from the lead's risk data record.

#### 9.1.3 Communication (Chat)

- Displays all inbound and outbound messages in a chat-style threaded interface.
- Each message shows: direction, insurer name (if applicable), sender, timestamp, body.
- Documents received via chat can be **downloaded** or **attached to a received quotation** directly from the chat item.
- Users can compose and send new outbound messages from this section.

#### 9.1.4 Received Quotations

Described in Screen 6.

#### 9.1.5 Shortlisted Quotations

Described in Screen 7.

#### 9.1.6 Documents

Two sub-tabs:
- **Sent Documents** — all recommendation documents with `status = 'sent'`.
- **Draft Documents** — recommendation documents with `status = 'draft'`.

---

## 10. Screen 6 — Received Quotations Management

### 10.1 Table Columns

| Column | Source |
|--------|--------|
| Insurer Name | `core_service_providers.name` |
| Quotation Version | `crmq_received_quotations.quotation_version` |
| Quotation ID | `crmq_received_quotations.quotation_ref` |
| Quotation Value | `crmq_received_quotations.quotation_value` |
| Received Date | `crmq_received_quotations.received_date` |
| Expiry Date | `crmq_received_quotations.expiry_date` |
| Remaining Days | Computed: `expiry_date - today` |
| Status | `core_status.name` (`CONFIRMED` / `REJECTED`) |
| Document | Download link if uploaded |
| Actions | Edit / Delete / Shortlist / Confirm |

### 10.2 Adding Quotations from Chat

| # | Behaviour |
|---|-----------|
| QR-01 | User clicks a document attachment in the Communication (Chat) section. |
| QR-02 | A download option and an "Attach to Quotation" option are presented. |
| QR-03 | On "Attach to Quotation", a modal opens to confirm or edit auto-extracted field values. |
| QR-04 | System attempts OCR/data extraction to pre-fill quotation fields. |
| QR-05 | User confirms and the received quotation record is saved with `is_auto_extracted = true`. |

### 10.3 Adding Quotations Manually ("Add New")

| Field | Type | Required |
|-------|------|----------|
| Insurer | Select (from request's insurer list) | Yes |
| Quotation Version | Text | No |
| Quotation ID / Ref | Text | No |
| Quotation Value | Decimal | Yes |
| Received Date | Date picker | Yes |
| Expiry Date | Date picker | Yes |
| Document | File upload | No |

Saved with `added_manually = true`.

### 10.4 Selection for Comparison

- Each row has a checkbox for multi-selection.
- The **"Compare Selected"** button activates when ≥ 2 quotations are checked.
- The **"Shortlist Selected"** button activates when ≥ 1 quotation is checked.

---

## 11. Screen 7 — Quotation Comparison & Shortlisting

### 11.1 Comparison View

- Selected received quotations are displayed in a side-by-side columnar layout.
- Each column represents one insurer's quotation.
- Comparison rows include:

| Row | Description |
|-----|-------------|
| Insurer | Insurer name |
| Premium / Value | `quotation_value` |
| Coverage Details | From insurer product items (Benefits) |
| Sum Insured | From risk details |
| Expiry Date | `expiry_date` |
| Remaining Days | Computed |
| Document | Download link |

### 11.2 Shortlisting Behaviour

| # | Behaviour |
|---|-----------|
| SL-01 | User selects quotations (from comparison view or table) and clicks **"Shortlist"**. |
| SL-02 | Selected quotations are saved to `crmq_shortlisted_quotations`. |
| SL-03 | Shortlisted quotations appear in the **Shortlisted Quotations** section of the Single View. |
| SL-04 | A quotation can be removed from the shortlist without deleting the received quotation record. |
| SL-05 | At least one shortlisted quotation is required before sharing with the customer. |

---

## 12. Screen 8 — Sharing Quotations with Customer

### 12.1 Options

| Scenario | Action |
|----------|--------|
| Single shortlisted quotation | User can send the quotation directly to the customer without generating a recommendation document. |
| Multiple shortlisted quotations | User can generate a recommendation document that includes all shortlisted quotations for comparison. |

### 12.2 Direct Send (Single Quotation)

- User selects "Send to Customer" on a shortlisted quotation.
- An email/notification is composed and sent to the customer.
- The quotation document (if uploaded) is attached.

### 12.3 Recommendation Document (Multiple Quotations)

- User selects "Generate Recommendation" from the Shortlisted Quotations section.
- Navigates to Recommendation Document flow (Screen 9).

---

## 13. Screen 9 — Recommendation Document

### 13.1 Document Generation

| # | Behaviour |
|---|-----------|
| RD-01 | System compiles shortlisted quotations into a formatted recommendation document. |
| RD-02 | Document includes: broker details, comparison table, selected quotations, and recommendation summary. |
| RD-03 | User can preview the document before sending. |
| RD-04 | User may choose to **Send** immediately or **Save as Draft**. |

### 13.2 Save as Draft

- Document saved with `status = 'draft'`.
- Appears in the **Draft Documents** tab of the Single View.
- Can be re-opened, updated, and sent at any later point.

### 13.3 Send to Customer

- Document sent to customer via email (customer contact from `core_customers`).
- Status updated to `sent`. `sent_at` timestamp recorded.
- Appears in **Sent Documents** tab.

### 13.4 Document Tracking

| Tab | Filter |
|-----|--------|
| Sent Documents | `crmq_recommendation_documents WHERE status = 'sent'` |
| Draft Documents | `crmq_recommendation_documents WHERE status = 'draft'` |

---

## 14. Screen 10 — Customer Confirmation

### 14.1 Via Customer Portal

| # | Behaviour |
|---|-----------|
| CP-01 | Customer logs into portal and views the shared quotations or recommendation document. |
| CP-02 | Customer selects their preferred quotation. |
| CP-03 | System calls `POST /quotation-requests/<id>/confirm-via-portal`. |
| CP-04 | Selected quotation: status updated to `CONFIRMED` (`quotation_confirmed`). |
| CP-05 | All other received quotations on the same request: status updated to `REJECTED` (`quotation_rejected`). |
| CP-06 | Quotation request stage updated to `CONFIRMED`. |
| CP-07 | Agent is notified of customer confirmation. |

### 14.2 Via Agent (Manual)

| # | Behaviour |
|---|-----------|
| AG-01 | Agent opens the received quotations list in the Single View. |
| AG-02 | Agent clicks **"Confirm"** on the selected quotation. |
| AG-03 | System calls `PATCH /quotation-requests/<id>/received-quotations/<rq_id>/confirm`. |
| AG-04 | Selected quotation: `status` → `quotation_confirmed`. |
| AG-05 | All other received quotations on the same request: `status` → `quotation_rejected`. |
| AG-06 | Quotation request stage updated to `CONFIRMED`. |

> **Only one quotation per request can hold `quotation_confirmed` status at any time.** Confirming a new quotation automatically rejects all others.

---

## 15. Screen 11 — Policy Request Initiation

### 15.1 Trigger

- The **"Initiate Policy Request"** button becomes available on the Quotation Single View once the request stage is `CONFIRMED`.

### 15.2 Data Carried Forward

The following data is pre-filled in the new policy request:

| Data | Source |
|------|--------|
| Customer Details | `core_customers` via `crmq_quotation_requests.customer_id` |
| Risk Data | Lead's risk submission record |
| Selected Insurer | Confirmed received quotation's `insurer_id` |
| Quotation Value / Premium | `crmq_received_quotations.quotation_value` |
| Product | `crmq_quotation_requests.product_id` |
| Quotation Reference | `crmq_received_quotations.quotation_ref` |

### 15.3 Behaviour

- Calls `POST /quotation-requests/<id>/initiate-policy`.
- Creates a new policy request record in the Policy Module.
- User is redirected to the new Policy Request Single View.
- The quotation request remains accessible and is not modified by this action.

---

## 16. Business Logic & Key Rules

### 16.1 Pre-conditions for Initiation from Lead

The "Request Quotation" action on a lead is blocked unless:
1. Lead is in the **QUALIFIED** stage.
2. A **customer account** is mapped (`opportunity.customer_id IS NOT NULL`).
3. **Risk details** exist for the lead.

### 16.2 Insurer Auto-Selection

When a native product is selected, the system queries all service providers that support that product (via the insurer product mapping) and pre-selects them all. The user retains full control to deselect or add insurers.

### 16.3 Approval Routing

- Approval configuration is stored in `core_settings` (entity type: `common_approval`).
- If approval is enabled, sending a request sets the stage to `PENDING` and routes to the Account Manager.
- The Account Manager can approve (forwards to insurers, stage → `SENT`) or reject the request.
- If approval is disabled, the email is sent directly to insurers and the stage is set to `SENT` immediately.

### 16.4 Risk Detail Excel Attachment

- On request send, the system generates an Excel file from the lead's risk submission data.
- The file is automatically attached to the outbound email.
- This attachment cannot be removed by the user at the composition step.

### 16.5 Auto-Extraction on Document Attach

- When attaching a document received in chat to a quotation record, the system performs an automated scan to extract field values.
- If extraction succeeds, fields are pre-populated but remain editable by the user before saving.
- If extraction fails, the user fills in all fields manually.
- `is_auto_extracted` flag records whether extraction was attempted and successful.

### 16.6 Remaining Days Computation

`remaining_days` is a computed field returned by the API:

```python
remaining_days = (expiry_date - date.today()).days
```

Negative values indicate an expired quotation. This triggers the `quotation_expired` status display in the UI.

### 16.7 Single Confirmation Rule

When any received quotation is confirmed (via agent or portal), **all other received quotations belonging to the same `quotation_request_id` are automatically set to `quotation_rejected`**. This is enforced at the server level in the confirmation endpoint, not by the client.

### 16.8 Policy Initiation Guard

`POST /quotation-requests/<id>/initiate-policy` returns `VALIDATION_ERROR` if:
- The quotation request stage is not `CONFIRMED`.
- No received quotation has `status = quotation_confirmed`.

### 16.9 Communication Trail Immutability

- Sent communication records (`crmq_quotation_communications`) are read-only after creation.
- They cannot be edited or deleted to preserve the complete audit trail.

### 16.10 Recommendation Document Versioning

- Multiple recommendation documents can exist per quotation request (drafts and sent versions).
- Each generation creates a new record; previous documents are not overwritten.

---

## 17. Permission Reference

| Permission Code | Description |
|-----------------|-------------|
| `quotation.view` | View quotation requests, received quotations, communications, documents. |
| `quotation.create` | Initiate a new quotation request. |
| `quotation.update` | Edit request details, manage insurers, add/edit received quotations, shortlist, generate documents. |
| `quotation.send` | Send emails to insurers and recommendation documents to customers. |
| `quotation.approve` | Approve a pending quotation request (Account Manager). |
| `quotation.delete` | Soft-delete a quotation request. |
| `policy.create` | Required to initiate a policy request from a confirmed quotation. |

---

## 18. Non-Functional Requirements

| # | Requirement |
|---|-------------|
| 18.1 | **Auto-generation:** Quotation request codes must be auto-generated in the format `QR-000001` and guaranteed unique. |
| 18.2 | **Soft Delete:** Quotation requests are soft-deleted only; hard deletion is not supported. |
| 18.3 | **Immutable Communications:** Communication thread records must never be editable or deletable post-creation. |
| 18.4 | **Atomic Confirmation:** Confirming a received quotation and rejecting all others must be performed in a single database transaction. |
| 18.5 | **File Validation:** Uploaded quotation documents must be validated for allowed file types (PDF, DOCX, XLSX) and maximum file size. |
| 18.6 | **Excel Generation:** The risk detail Excel attachment must be generated server-side and must reflect the latest risk submission data at the time of send. |
| 18.7 | **Notifications:** Stage changes (SENT, PENDING, CONFIRMED) must trigger in-app notifications to relevant users (agent, account manager, customer). |
| 18.8 | **Performance:** The list view must load within 2 seconds for up to 500 records using database-level pagination. |
| 18.9 | **Audit Trail:** All stage transitions and status changes must be logged with user ID and timestamp. |
| 18.10 | **Portal Security:** The `confirm-via-portal` endpoint must authenticate the customer session before processing confirmation. |

---

*Document prepared based on the Quotation Module functional flow specification. Subject to revision as further requirements are clarified.*
