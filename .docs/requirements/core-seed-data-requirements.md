# Core System Seed Data — Requirements Document

**Module:** Core
**Feature:** Seed Data Initialization
**Version:** 1.1
**Status:** Draft

---

## 1. Overview

The Core Seed Data Initialization feature provides the out-of-the-box configuration data essential for the Envoy platform (including Core, CRM, Policy, and Customer modules) to execute its core operational logic. This information is written to database tables via a seed query or management command.

This ensures that system-wide lists, statuses, configurations, global settings, actions, and foundational rules are correctly laid down prior to system operation.

---

## 2. Entities and Seed Data Specifications

The seed procedure must reliably insert or update the following core entities:

### 2.1 Task Statuses
Defines the lifecycle phases for any given task in the system.

| Name | Description | Type Code | Color | Sort Index |
|---|---|---|---|---|
| TODO | Todo | `task_todo` | #0E7090 | 1 |
| IN PROGRESS | In Progress | `task_inprogress` | #175CD3 | 2 |
| DONE | Done | `task_done` | #067647 | 3 |

### 2.2 Currencies
Base supported currencies.

| Code | Name | Symbol | Decimal Digits | Rounding |
|---|---|---|---|---|
| USD | US Dollar | $ | 2 | 0 |
| LKR | Sri Lankan Rupee | Rs. | 2 | 0 |

### 2.3 Flex Fields
Dynamically extending core structures without altering schemas directly.

| Entity Type | Field Code | Field Label | Data Type | Mandatory | Enabled | Fixed |
|---|---|---|---|---|---|---|
| CUSTOMER | `number_of_employees` | Number of Employees | TEXT | No | Yes | Yes |
| CUSTOMER | `br_no` | BR NUMBER | TEXT | No | Yes | Yes |

### 2.4 Setting Keys & Global Settings
A registry of system-wide environment variables and behavioral toggles.

| Setting Name | Attribute Name | Default JSON / Value | Description |
|---|---|---|---|
| SALES_AGENT_ROLES | `sales_agent_roles` | `"2"` | - |
| OPPORTUNITY_CUSTOMER_REQUIRED_STAGE | `opportunity_customer_required_stage` | `"3"` | - |
| BASE_CURRENCY | `base_currency` | `"2"` | - |
| BASE_COUNTRY | `base_country` | `"178"` | - |
| COMMISSION_CONFIG | - | `{"agent_commission_config": "totalPremium", "payment_frequency": "monthly"}` | - |
| POLICY_LIFECYCLE_NOTIFICATIONS | `policy_lifecycle_notifications` | - | Covers everything related to your insurance policies... |
| PAYMENTS_AND_REMINDERS | `payments_and_reminders` | - | Payment due reminders... |
| ACCOUNT_AND_SECURITY | `account_and_security` | - | Important alerts about your login... |
| PROMOTIONS_AND_UPDATES | `promotions_and_updates` | - | News, offers, and promotions... |
| APPROVAL_PERMISSIONS | `approval_permissions` | `{"policy_request_approval": "true", "quotation_request_approval": "true"}` | Approval settings for policy and quotation requests |
| CUSTOMER_CONFIG | `customer_config` | `{"Policy management controller":"[Allow auto renewal, pdf]"}` | Customer configuration settings |

### 2.5 System Modules & Actions
Registers the major application subdivisions and the access control actions attached to them.

**Modules:** CRM, POLICY, CORE

**Actions:**
All of the following can be assigned as permissions (`can_be_permission` = True):

| Module | Entity | Action |
|---|---|---|
| CRM | TASK | VIEW_ALL, VIEW, UPDATE, ADD, DELETE |
| CORE | USER | VIEW_ALL, VIEW, UPDATE, ADD, DELETE |
| CORE | ROLE | VIEW_ALL, VIEW, UPDATE, ADD, DELETE |

### 2.6 Lifecycle Statuses
Standardized status mappings ensuring unified behavior across states.

#### Quotation Module
| Name | Description | Type Code | Color | Sort Index |
|---|---|---|---|---|
| REQUESTED | Quotation is being prepared | `quotation_draft` | #6c757d | 1 |
| SENT | Quotation has been sent | `quotation_sent` | #0E7090 | 2 |
| INPROGRESS | Client accepted the quotation | `quotation_inprogress` | #175CD3 | 3 |
| REJECTED | Client rejected the quotation | `quotation_rejected` | #B42318 | 4 |
| PENDING | Pending quotation | `quotation_pending` | #B54708 | 5 |
| CONFIRMED | Confirmed quotation | `quotation_confirmed` | #067647 | 6 |
| EXPIRED | Expired quotation | `quotation_expired` | #344054 | 7 |

#### Customer Module
| Name | Description | Type Code | Color | Sort Index |
|---|---|---|---|---|
| REQUESTED | customer request status | `customer_requested` | #6c757d | 1 |
| APPROVED | customer request status | `customer_approved` | #067647 | 2 |
| REJECTED | customer request status | `customer_rejected` | #B42318 | 3 |

#### Policy Module
| Name | Description | Type Code | Color | Sort Index |
|---|---|---|---|---|
| REQUESTED | policyStatus | `policy_requested` | #6c757d | 1 |
| PENDING ISSUANCE | policyStatus | `pol_pending_iss` | #B54708 | 2 |
| ACTIVE | policyStatus | `policy_active` | #067647 | 3 |
| DUE FOR RENEWAL | policyStatus | `pol_due_renewal` | #175CD3 | 4 |
| EXPIRED | policyStatus | `policy_expired` | #344054 | 5 |
| RENEWAL IN PROGRESS| policyStatus | `pol_renewal_progress` | #0E7090 | 6 |
| CANCELLED | policyStatus | `policy_cancelled` | #B42318 | 6 |
| RENEWED | policyStatus | `policy_renewed` | #175CD3 | 8 |

#### Endorsement Statuses (Policy Module)
| Name | Description | Type Code | Color | Sort Index |
|---|---|---|---|---|
| SETTLED | EndorsementStatus | `endorsement_settled` | #067647 | 1 |
| PENDING | EndorsementStatus | `endorsement_pending` | #B54708 | 2 |

#### Payment Module
| Name | Description | Type Code | Color | Sort Index |
|---|---|---|---|---|
| PENDING | Payment is awaiting confirmation | `payment_pending` | #B54708 | 1 |
| PARTIALLY PAID | Payment is partially settled | `pay_partially_paid`| #0E7090 | 2 |
| PAID | Payment is completed | `payment_paid` | #067647 | 3 |
| FAILED | Payment has failed | `payment_failed` | #dc3545 | 4 |
| REFUNDED | Payment was refunded | `payment_refunded` | #6c757d | 5 |

#### Invoice Module
| Name | Description | Type Code | Color | Sort Index |
|---|---|---|---|---|
| PENDING | Invoice is in draft | `invoice_pending` | #175CD3 | 1 |
| PARTIALLY PAID | Invoice has been sent | `inv_partially_paid` | #0E7090 | 2 |
| PAID | Invoice has been viewed | `invoice_paid` | #067647 | 3 |
| OVERDUE | Invoice payment is overdue | `invoice_overdue` | #B54708 | 4 |
| CANCELLED | Invoice was cancelled | `invoice_cancelled` | #B42318 | 5 |
| REFUNDED | Invoice was refunded | `invoice_refunded` | #363F72 | 6 |

#### Claim Module
| Name | Description | Type Code | Color | Sort Index |
|---|---|---|---|---|
| DRAFT | Claim is being drafted by the user | `claim_draft` | #344054 | 1 |
| EVALUATED | Claim has been submitted for review | `claim_submitted` | #0E7090 | 2 |
| NOTIFIED | Claim is being notified to the user | `claim_notified` | #363F72 | 3 |
| APPROVED | Claim has been approved after evaluation | `claim_approved` | #228b22 | 3 |
| SETTLED | Claim has been settled and closed | `claim_settled` | #067647 | 4 |
| REJECTED | Claim has been rejected | `claim_rejected` | #B42318 | 5 |

### 2.7 Notification Types
Categorization mapping to govern front-end styling and organizational clustering.

| Code | Name | Description | Color |
|---|---|---|---|
| `policy_issued` | Policy Issued | Notification when a policy is issued | #4CAF50 |
| `policy_expiry` | Policy Expiry | Notification when a policy is about to expire | #FF9800 |
| `policy_renewal` | Policy Renewal | Reminder for policy renewal | #2196F3 |
| `quotation_created` | Quotation Created | Quotation was created | #9C27B0 |
| `quotation_approved`| Quotation Approved | Quotation approved | #00BCD4 |
| `quotation_rejected`| Quotation Rejected | Quotation rejected | #F44336 |
| `claim_submitted` | Claim Submitted | New claim submitted | #FFC107 |
| `claim_approved` | Claim Approved | Claim approved | #8BC34A |
| `claim_rejected` | Claim Rejected | Claim rejected | #E91E63 |
| `payment_due` | Payment Due | Upcoming payment | #FF5722 |
| `payment_reminder` | Payment Reminder | Upcoming payment reminder | #607D8B |
| `account_update` | Account Update | Account updated | #3F51B5 |
| `maintenance` | Maintenance Alert | Maintenance alert | #795548 |
| `general` | General | General notification | #9E9E9E |

### 2.8 Services
Baseline values for broker / investigation services.

| Title | Fee | Description | Type | Module |
|---|---|---|---|---|
| Claim Investigation | 2500.00 | Investigation services | service render | core |
| Claim Documentation | 1800.50 | Documentation services | service render | core |
| Legal Advice | 3500.00 | Legal consultation | service render | core |
| Fraud Investigation | 4200.75 | Fraud detection services | service render | core |
| Outsourced Resource Person | 2800.25 | Resource personnel | service render | core |

### 2.9 Entity Approval Rules
Setup rules defining threshold levels or procedural routing for key operations.

| Action Focus | Entity Type | Default Status | Rule Structure JSON |
|---|---|---|---|
| `approval` | `common_approval` | `open` | `{"other": [], "rules": [{"role": null, "user": 1, "level": null}]}` |

---

## 3. Non-Functional Requirements

| # | Requirement |
|---|---|
| 3.1 | **Idempotency:** The seed command must execute safely multiple times (`update_or_create` logic) without generating duplicate database records. |
| 3.2 | **Maintainability:** The script must use descriptive variable names and be easily updatable by any backend engineer. |
| 3.3 | **Logging:** Standard output terminal notifications should highlight process start and successful completions. |
| 3.4 | **Failsafe Executions:** A missing internal dependency (such as a SettingKey reference) should yield a terminal Warning and log failure rather than crashing the overall seed workflow. |

---

*Document prepared based on internal backend seed query inputs.*
