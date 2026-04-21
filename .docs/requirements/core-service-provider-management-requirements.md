# Service Provider Management — Requirements Document

**Module:** Core
**Feature:** Service Provider Management
**Version:** 1.1
**Status:** Draft

---

## 1. Overview

The Service Provider Management feature allows authorized users to create and manage service providers (partners) within the system. A service provider record captures the provider's general information, primary and secondary contact persons, and bank account details. Service providers can be used across other modules (e.g. Policy, Finance) to associate external partners with brokerage operations.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform service provider management actions.

---

## 2. Key Rules

- A service provider record is composed of three sections: **General Information**, **Contact Persons**, and **Bank Account Info**.
- Partner name, email, and contact number are **mandatory** in the general information section.
- A service provider supports exactly **two contact persons** — one with contact type **Primary** and one with contact type **Secondary**.
- Each contact person requires a salutation, contact person name, and contact number as mandatory fields.
- Contact type is fixed to **Primary** or **Secondary** — it cannot be a custom value.
- All bank account fields are **optional**.
- Service providers are **soft-deleted** — deactivated but not permanently removed.
- A service provider can be **duplicated** to create an independent copy.

---

## 3. Functional Requirements

### 3.1 Create Service Provider

#### 3.1.1 General Information

| # | Requirement | Permission |
|---|---|---|
| 3.1.1 | Users can upload a **logo** image for the service provider. Logo is optional. | `service_provider.create` |
| 3.1.2 | **Partner name** is a required field. | `service_provider.create` |
| 3.1.3 | **Email** is a required field. The system must validate it is in a valid email format. | `service_provider.create` |
| 3.1.4 | **Contact number** is a required field. It includes a country code selector (flag + dial code) and the number. | `service_provider.create` |
| 3.1.5 | **Fax number** is an optional field. | `service_provider.create` |
| 3.1.6 | **Address** is a required field. | `service_provider.create` |
| 3.1.7 | **Website** is an optional field. | `service_provider.create` |

#### 3.1.2 Contact Persons

| # | Requirement | Permission |
|---|---|---|
| 3.1.8 | A service provider supports two contact persons — **Primary** and **Secondary**. | `service_provider.create` |
| 3.1.9 | **Contact type** is a required field and is fixed to either `Primary` or `Secondary`. | `service_provider.create` |
| 3.1.10 | **Salutation** is a required field for each contact person (e.g. Mr., Mrs., Ms., Dr.). | `service_provider.create` |
| 3.1.11 | **Contact person name** is a required field. | `service_provider.create` |
| 3.1.12 | **Contact number** is a required field for each contact person. It includes a country code selector and the number. | `service_provider.create` |
| 3.1.13 | **Role** is an optional field for each contact person. | `service_provider.create` |
| 3.1.14 | **Email** is an optional field for each contact person. | `service_provider.create` |
| 3.1.15 | **Remarks** is an optional field for each contact person. | `service_provider.create` |

#### 3.1.3 Bank Account Info

| # | Requirement | Permission |
|---|---|---|
| 3.1.16 | **Account holder name** is an optional field. | `service_provider.create` |
| 3.1.17 | **Bank name** is an optional field. | `service_provider.create` |
| 3.1.18 | **Account number** is an optional field. | `service_provider.create` |
| 3.1.19 | **Bank branch** is an optional field. | `service_provider.create` |
| 3.1.20 | **IBAN / Swift code** is an optional field (for international use). | `service_provider.create` |
| 3.1.21 | **Payment gateway URL** is an optional field. | `service_provider.create` |

---

### 3.2 View Service Providers

| # | Requirement | Permission |
|---|---|---|
| 3.2.1 | Users can view a list of all active service providers showing partner name, email, and contact number. | `service_provider.view` |
| 3.2.2 | The service provider list supports search by partner name and email. | `service_provider.view` |
| 3.2.3 | Users can view the full detail of a single service provider including all three sections. | `service_provider.view` |
| 3.2.4 | Soft-deleted service providers are hidden from the default list view. | `service_provider.view` |

---

### 3.3 Service Provider Detail — Insurer Products

The single view of a service provider displays all insurer products that have been assigned to that service provider.

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | The service provider detail view includes an **Insurer Products** section listing all active insurer products linked to that service provider. | `service_provider.view` |
| 3.3.2 | Each insurer product entry displays: product name, risk type, coverage level, currency, and last update date. | `service_provider.view` |
| 3.3.3 | If no insurer products are linked to the service provider, the section displays an empty state message. | `service_provider.view` |
| 3.3.4 | The insurer products list within the detail view supports search by product name. | `service_provider.view` |
| 3.3.5 | Soft-deleted insurer products are not shown in this list. | `service_provider.view` |
| 3.3.6 | Each insurer product entry in the list links to the full insurer product detail view. | `service_provider.view` |

---

### 3.4 Edit Service Provider

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | Users can edit all fields across the general information, contact persons, and bank account info sections. | `service_provider.edit` |
| 3.3.2 | All mandatory field rules from creation apply during edit. | `service_provider.edit` |
| 3.3.3 | Soft-deleted service providers cannot be edited. | — |

---

### 3.5 Duplicate Service Provider

| # | Requirement | Permission |
|---|---|---|
| 3.4.1 | Users can duplicate an existing service provider to create an independent copy. | `service_provider.duplicate` |
| 3.4.2 | The duplicate copies all fields across all three sections, with the partner name suffixed to indicate it is a copy. | `service_provider.duplicate` |
| 3.4.3 | The duplicate is a fully independent record — changes to it do not affect the original. | — |

---

### 3.6 Delete Service Provider

| # | Requirement | Permission |
|---|---|---|
| 3.5.1 | Users can soft-delete a service provider. | `service_provider.delete` |
| 3.5.2 | Soft-deleted service providers are deactivated and hidden from the default list but retained in the system. | — |
| 3.5.3 | Hard deletion is not supported. | — |

---

## 4. Field Reference Summary

### General Information

| Field | Required | Notes |
|---|---|---|
| Logo | No | Image upload |
| Partner Name | Yes | — |
| Email | Yes | Must be valid email format |
| Contact Number | Yes | Country code selector + number |
| Fax Number | No | — |
| Address | Yes | — |
| Website | No | — |

### Contact Person (Primary & Secondary)

| Field | Required | Notes |
|---|---|---|
| Contact Type | Yes | Fixed: `Primary` or `Secondary` |
| Salutation | Yes | e.g. Mr., Mrs., Ms., Dr. |
| Contact Person Name | Yes | — |
| Contact Number | Yes | Country code selector + number |
| Role | No | — |
| Email | No | — |
| Remarks | No | — |

### Bank Account Info

| Field | Required | Notes |
|---|---|---|
| Account Holder Name | No | — |
| Bank Name | No | — |
| Account Number | No | — |
| Bank Branch | No | — |
| IBAN / Swift Code | No | For international use |
| Payment Gateway URL | No | — |

---

## 5. Permission Reference Table

| Permission Key | Description |
|---|---|
| `service_provider.create` | Create new service providers |
| `service_provider.view` | View service provider list and details |
| `service_provider.edit` | Edit an existing service provider |
| `service_provider.duplicate` | Duplicate an existing service provider |
| `service_provider.delete` | Soft-delete a service provider |

---

## 6. Non-Functional Requirements

| # | Requirement |
|---|---|
| 6.1 | All create, edit, duplicate, and delete actions must be recorded in the audit log with the acting user and timestamp. |
| 6.2 | Uploaded logo images must be validated for file type (JPG, PNG) and size limits. |
| 6.3 | Soft-deleted service providers must be retained indefinitely for audit purposes. |
| 6.4 | Contact number fields must support international formats via country code selector. |

---

## 7. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create a service provider with general info, contact persons, and bank details | I can register external partners in the system |
| US-02 | Authorized user | Add a primary and secondary contact person to a service provider | I have clear points of contact for each partner |
| US-03 | Authorized user | Store bank account details for a service provider | Finance-related transactions can reference the correct account information |
| US-04 | Authorized user | Edit a service provider's details | I can keep partner information accurate and up to date |
| US-05 | Authorized user | Duplicate a service provider | I can use an existing partner as a starting point for a new one |
| US-06 | Authorized user | Soft-delete a service provider | I can retire partners no longer in use without losing the audit trail |
| US-07 | Authorized user | Search for a service provider by name or email | I can quickly locate the partner I need |
| US-08 | Authorized user | View all insurer products linked to a service provider on their detail page | I can see at a glance what products are offered by that partner |

---

## 8. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | How many contacts can a service provider have? | Exactly two — one Primary and one Secondary contact person. |
| RD-02 | What happens when a service provider is deleted? | Soft delete only — deactivated but not permanently removed. |
| RD-03 | Can a service provider be duplicated? | Yes — creates a fully independent copy of all fields across all sections. |
| RD-04 | Should insurer products be shown in the service provider detail view? | Yes — the single view of a service provider displays all active insurer products linked to that provider. |

---

## 9. Out of Scope

- Linking service providers to specific policies, claims, or finance records — handled by the respective modules.
- Service provider portal or external login access.
- Managing multiple bank accounts per service provider.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*
