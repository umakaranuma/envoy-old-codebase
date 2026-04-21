# Product Management — Requirements Document

**Module:** Core
**Feature:** Product Management
**Version:** 1.0
**Status:** Draft

---

## 1. Overview

The Product Management feature allows authorized users to create and manage three types of products within the system: **Insurer Products**, **Native Products**, and **Product Groups**.

- An **Insurer Product** represents a product offered by an external service provider (insurer/partner) for a specific risk type, with coverage level, currency, and terms.
- A **Native Product** is an internally defined product that maps to one or more insurer products under a specific risk type.
- A **Product Group** bundles multiple native products together with a currency and assigned sales teams for use in the sales and policy workflow.

> **Terminology Notes:**
> - *Insurer*, *Partner*, and *Service Provider* refer to the same entity.
> - *Risk Type* and *Product Category* refer to the same entity.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform product management actions.

---

## 2. Key Rules

- Product names must be **unique** across all products of the same type (insurer product, native product, product group).
- All three product types are **soft-deleted** — deactivated but not permanently removed.
- **Coverage Level** is seeded with three fixed values: `Basic`, `Plus`, and `Premium`.
- For insurer products, **product items** are assigned separately after the product is created.
- For native products, one or more insurer products are selected at creation, filtered by the selected risk type.
- For product groups, native products, currency, and teams are all assigned **during creation**.

---

## 3. Functional Requirements

---

### 3.1 Insurer Product — Create

| # | Requirement | Permission |
|---|---|---|
| 3.1.1 | Users can create a new insurer product by providing the required fields listed below. | `insurer_product.create` |
| 3.1.2 | **Product name** is a required field and must be unique. | `insurer_product.create` |
| 3.1.3 | **Risk type (product category)** is a required field — selected from active product categories. | `insurer_product.create` |
| 3.1.4 | **Insurer info (service provider)** is a required field — selected from active service providers. | `insurer_product.create` |
| 3.1.5 | **Coverage level** is a required field — selected from seeded values: `Basic`, `Plus`, `Premium`. | `insurer_product.create` |
| 3.1.6 | **Description** is a required field. | `insurer_product.create` |
| 3.1.7 | **Remarks** is an optional field. | `insurer_product.create` |
| 3.1.8 | **Currency** is a required field — selected from available currencies. | `insurer_product.create` |
| 3.1.9 | **Last update date** is a required field — a date picker defaulting to today's date. | `insurer_product.create` |
| 3.1.10 | **Terms & Conditions** is an optional file upload field (PDF or document). | `insurer_product.create` |

---

### 3.2 Insurer Product — Product Items Assignment

Product items are assigned to an insurer product separately after the product is created.

| # | Requirement | Permission |
|---|---|---|
| 3.2.1 | After an insurer product is created, users can assign product items to it. | `insurer_product.assign_item` |
| 3.2.2 | Each product item has: **title** (required), **category** (required), and **description** (optional). | `insurer_product.assign_item` |
| 3.2.3 | The product item **category** is seeded with fixed values: `Benefits`, `Limitations`, `Exclusions`, `Other Conditions`. | — |
| 3.2.4 | Multiple product items can be assigned to a single insurer product. | `insurer_product.assign_item` |
| 3.2.5 | Product items can be added, edited, and removed from the insurer product at any time. | `insurer_product.assign_item` |
| 3.2.6 | The insurer product detail view displays all assigned product items grouped by category. | `insurer_product.view` |

---

### 3.3 Insurer Product — View

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | Users can view a list of all active insurer products showing product name, risk type, insurer, and coverage level. | `insurer_product.view` |
| 3.3.2 | The list supports search by product name. | `insurer_product.view` |
| 3.3.3 | The list can be filtered by risk type, insurer, and coverage level. | `insurer_product.view` |
| 3.3.4 | Users can view the full detail of a single insurer product including all fields and assigned product items. | `insurer_product.view` |
| 3.3.5 | Soft-deleted insurer products are hidden from the default list view. | `insurer_product.view` |

---

### 3.4 Insurer Product — Edit

| # | Requirement | Permission |
|---|---|---|
| 3.4.1 | Users can edit all fields of an existing insurer product. | `insurer_product.edit` |
| 3.4.2 | All mandatory field rules from creation apply during edit. | `insurer_product.edit` |
| 3.4.3 | Soft-deleted insurer products cannot be edited. | — |

---

### 3.5 Insurer Product — Delete

| # | Requirement | Permission |
|---|---|---|
| 3.5.1 | Users can soft-delete an insurer product. | `insurer_product.delete` |
| 3.5.2 | Soft-deleted insurer products are deactivated and hidden from the default list but retained in the system. | — |
| 3.5.3 | Hard deletion is not supported. | — |

---

### 3.6 Native Product — Create

| # | Requirement | Permission |
|---|---|---|
| 3.6.1 | Users can create a new native product by providing the required fields listed below. | `native_product.create` |
| 3.6.2 | **Product name** is a required field and must be unique. | `native_product.create` |
| 3.6.3 | **Risk type (product category)** is a required field — selected from active product categories. | `native_product.create` |
| 3.6.4 | Based on the selected risk type, the user must select one or more **insurer products** that are linked to that risk type. | `native_product.create` |
| 3.6.5 | The insurer product selection list is filtered to show only active insurer products matching the selected risk type. | `native_product.create` |
| 3.6.6 | The **service provider (insurer)** is automatically saved based on the selected insurer product(s). | — |
| 3.6.7 | At least one insurer product must be selected before the native product can be saved. | `native_product.create` |

---

### 3.7 Native Product — View

| # | Requirement | Permission |
|---|---|---|
| 3.7.1 | Users can view a list of all active native products showing product name and risk type. | `native_product.view` |
| 3.7.2 | The list supports search by product name. | `native_product.view` |
| 3.7.3 | The list can be filtered by risk type. | `native_product.view` |
| 3.7.4 | Users can view the full detail of a single native product including its linked insurer products and service providers. | `native_product.view` |
| 3.7.5 | Soft-deleted native products are hidden from the default list view. | `native_product.view` |

---

### 3.8 Native Product — Edit

| # | Requirement | Permission |
|---|---|---|
| 3.8.1 | Users can edit all fields of an existing native product including the linked insurer products. | `native_product.edit` |
| 3.8.2 | All mandatory field rules from creation apply during edit. | `native_product.edit` |
| 3.8.3 | If the risk type is changed, the insurer product selection must be reset and re-selected based on the new risk type. | `native_product.edit` |
| 3.8.4 | Soft-deleted native products cannot be edited. | — |

---

### 3.9 Native Product — Delete

| # | Requirement | Permission |
|---|---|---|
| 3.9.1 | Users can soft-delete a native product. | `native_product.delete` |
| 3.9.2 | Soft-deleted native products are deactivated and hidden from the default list but retained in the system. | — |
| 3.9.3 | Hard deletion is not supported. | — |

---

### 3.10 Product Group — Create

| # | Requirement | Permission |
|---|---|---|
| 3.10.1 | Users can create a new product group by providing the required fields listed below. | `product_group.create` |
| 3.10.2 | **Group name** is a required field and must be unique. | `product_group.create` |
| 3.10.3 | One or more **native products** must be selected and assigned to the group at creation time. | `product_group.create` |
| 3.10.4 | **Currency** is a required field — selected from available currencies. | `product_group.create` |
| 3.10.5 | One or more **sales teams** must be selected and assigned to the group at creation time. | `product_group.create` |
| 3.10.6 | A product group cannot be saved without at least one native product and one sales team selected. | `product_group.create` |

---

### 3.11 Product Group — View

| # | Requirement | Permission |
|---|---|---|
| 3.11.1 | Users can view a list of all active product groups showing group name, currency, and assigned team count. | `product_group.view` |
| 3.11.2 | The list supports search by group name. | `product_group.view` |
| 3.11.3 | Users can view the full detail of a single product group including all assigned native products and sales teams. | `product_group.view` |
| 3.11.4 | Soft-deleted product groups are hidden from the default list view. | `product_group.view` |

---

### 3.12 Product Group — Edit

| # | Requirement | Permission |
|---|---|---|
| 3.12.1 | Users can edit the group name, native products, currency, and sales teams of an existing product group. | `product_group.edit` |
| 3.12.2 | All mandatory field rules from creation apply during edit. | `product_group.edit` |
| 3.12.3 | Soft-deleted product groups cannot be edited. | — |

---

### 3.13 Product Group — Delete

| # | Requirement | Permission |
|---|---|---|
| 3.13.1 | Users can soft-delete a product group. | `product_group.delete` |
| 3.13.2 | Soft-deleted product groups are deactivated and hidden from the default list but retained in the system. | — |
| 3.13.3 | Hard deletion is not supported. | — |

---

## 4. Field Reference Summary

### Insurer Product

| Field | Required | Notes |
|---|---|---|
| Product Name | Yes | Must be unique |
| Risk Type | Yes | Selected from active product categories |
| Insurer Info | Yes | Selected from active service providers |
| Coverage Level | Yes | Seeded: `Basic`, `Plus`, `Premium` |
| Description | Yes | — |
| Remarks | No | — |
| Currency | Yes | Selected from available currencies |
| Last Update Date | Yes | Date picker, defaults to today |
| Terms & Conditions | No | File upload (PDF / document) |

### Insurer Product Item

| Field | Required | Notes |
|---|---|---|
| Title | Yes | — |
| Category | Yes | Seeded: `Benefits`, `Limitations`, `Exclusions`, `Other Conditions` |
| Description | No | — |

### Native Product

| Field | Required | Notes |
|---|---|---|
| Product Name | Yes | Must be unique |
| Risk Type | Yes | Selected from active product categories |
| Insurer Products | Yes | One or more; filtered by selected risk type |
| Service Provider | Auto | Derived from selected insurer products |

### Product Group

| Field | Required | Notes |
|---|---|---|
| Group Name | Yes | Must be unique |
| Native Products | Yes | One or more selected at creation |
| Currency | Yes | Selected from available currencies |
| Sales Teams | Yes | One or more selected at creation |

---

## 5. Seeded Reference Values

| Entity | Field | Seeded Values |
|---|---|---|
| Insurer Product | Coverage Level | `Basic`, `Plus`, `Premium` |
| Product Item | Category | `Benefits`, `Limitations`, `Exclusions`, `Other Conditions` |

---

## 6. Permission Reference Table

| Permission Key | Description |
|---|---|
| `insurer_product.create` | Create new insurer products |
| `insurer_product.view` | View insurer product list and details |
| `insurer_product.edit` | Edit an existing insurer product |
| `insurer_product.delete` | Soft-delete an insurer product |
| `insurer_product.assign_item` | Assign, edit, and remove product items on an insurer product |
| `native_product.create` | Create new native products |
| `native_product.view` | View native product list and details |
| `native_product.edit` | Edit an existing native product |
| `native_product.delete` | Soft-delete a native product |
| `product_group.create` | Create new product groups |
| `product_group.view` | View product group list and details |
| `product_group.edit` | Edit an existing product group |
| `product_group.delete` | Soft-delete a product group |

---

## 7. Non-Functional Requirements

| # | Requirement |
|---|---|
| 7.1 | All create, edit, and delete actions across all product types must be recorded in the audit log with the acting user and timestamp. |
| 7.2 | Product name uniqueness must be enforced at the database level per product type. |
| 7.3 | Soft-deleted records must be retained indefinitely for audit purposes. |
| 7.4 | Insurer product selection in native product creation must dynamically filter based on the selected risk type. |
| 7.5 | Seeded values (coverage level, product item category) must be pre-loaded at system initialisation and protected from modification. |
| 7.6 | Uploaded Terms & Conditions files must be validated for allowed file types and size limits. |

---

## 8. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create an insurer product with coverage details and terms | I can register an external insurer's product offering in the system |
| US-02 | Authorized user | Assign product items (benefits, limitations, exclusions) to an insurer product | I can define the detailed coverage breakdown for each product |
| US-03 | Authorized user | Create a native product linked to one or more insurer products | I can define internally managed products backed by insurer offerings |
| US-04 | Authorized user | Filter insurer products by risk type when creating a native product | I only see relevant insurer products for the selected category |
| US-05 | Authorized user | Create a product group with native products, currency, and teams | I can bundle related products for use by specific sales teams |
| US-06 | Authorized user | Edit any product type's details | I can keep product information accurate as requirements change |
| US-07 | Authorized user | Soft-delete any product type | I can retire products no longer in use without losing the audit trail |
| US-08 | Authorized user | Search and filter products by name, risk type, or coverage level | I can quickly find the product I need |

---

## 9. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | Are insurer, partner, and service provider the same? | Yes — all three terms refer to the same entity in the system. |
| RD-02 | Are risk type and product category the same? | Yes — both terms refer to the same entity. |
| RD-03 | Are all deletions soft deletes? | Yes — soft delete only across all three product types. |
| RD-04 | Are product names unique? | Yes — unique per product type (insurer product, native product, product group). |
| RD-05 | When are product items assigned to an insurer product? | Separately after the insurer product is created. |
| RD-06 | How many insurer products can a native product link to? | One or more — multiple insurer products can be selected, filtered by risk type. |
| RD-07 | What fields does a product group have? | Group name, one or more native products, currency, and one or more sales teams — all assigned at creation time. |

---

## 10. Out of Scope

- Pricing or premium calculation per product — handled by the Policy or Finance module.
- Linking products to policies or quotations directly — handled by the CRM and Policy modules.
- Product versioning or approval workflows.
- Bulk import of products.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*
