# Product Item Management — Requirements Document

**Module:** Core
**Feature:** Product Item Management
**Version:** 1.1
**Status:** Draft

---

## 1. Overview

The Product Item Management feature allows authorized users to create and manage product items within the system. Product items are reusable entries defined by a title, category, and description that can be assigned to insurer products to represent specific coverage details such as benefits, limitations, exclusions, and other conditions.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform product item management actions.

---

## 2. Key Rules

- A product item record holds: **title**, **category**, and **description**.
- Title is **mandatory** when creating a product item.
- Category is **mandatory** — selected from seeded values: `Benefits`, `Limitations`, `Exclusions`, `Other Conditions`.
- Description is **optional**.
- Product item titles should be unique within the same category; duplicate titles within the same category are flagged with a warning.
- Product items are **soft-deleted** — deactivated but not permanently removed.

---

## 3. Functional Requirements

### 3.1 Create Product Item

| # | Requirement | Permission |
|---|---|---|
| 3.1.1 | Users can create a new product item by providing a title, selecting a category, and optionally providing a description. | `product_item.create` |
| 3.1.2 | **Title** is a required field; the form cannot be submitted without it. | `product_item.create` |
| 3.1.3 | **Category** is a required field — selected from seeded values: `Benefits`, `Limitations`, `Exclusions`, `Other Conditions`. | `product_item.create` |
| 3.1.4 | **Description** is an optional field. | `product_item.create` |
| 3.1.5 | Duplicate titles within the same category should be flagged with a warning, but creation may still proceed (not a hard block). | `product_item.create` |

---

### 3.2 View Product Items

| # | Requirement | Permission |
|---|---|---|
| 3.2.1 | Users can view a list of all active product items showing title, category, and description. | `product_item.view` |
| 3.2.2 | The product item list supports search by title. | `product_item.view` |
| 3.2.3 | The product item list can be filtered by category. | `product_item.view` |
| 3.2.4 | Soft-deleted product items are hidden from the default list view. | `product_item.view` |

---

### 3.3 Edit Product Item

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | Users can edit the title, category, and description of an existing product item. | `product_item.edit` |
| 3.3.2 | Title remains mandatory during edit; it cannot be cleared. | `product_item.edit` |
| 3.3.3 | Category remains mandatory during edit; it cannot be cleared. | `product_item.edit` |
| 3.3.4 | Soft-deleted product items cannot be edited. | — |

---

### 3.4 Delete Product Item

| # | Requirement | Permission |
|---|---|---|
| 3.4.1 | Users can soft-delete a product item. | `product_item.delete` |
| 3.4.2 | Soft-deleted product items are deactivated and hidden from the default list but retained in the system. | — |
| 3.4.3 | Hard deletion is not supported. | — |

---

## 4. Permission Reference Table

| Permission Key | Description |
|---|---|
| `product_item.create` | Create new product items |
| `product_item.view` | View product item list and details |
| `product_item.edit` | Edit an existing product item's title, category, and description |
| `product_item.delete` | Soft-delete a product item |

---

## 5. Non-Functional Requirements

| # | Requirement |
|---|---|
| 5.1 | All create, edit, and delete actions must be recorded in the audit log with the acting user and timestamp. |
| 5.2 | Soft-deleted product items must be retained indefinitely for audit purposes. |
| 5.3 | Category seeded values (`Benefits`, `Limitations`, `Exclusions`, `Other Conditions`) must be pre-loaded at system initialisation and protected from modification. |

---

## 6. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create a product item with a title, category, and description | I can define reusable coverage detail entries for use in insurer products |
| US-02 | Authorized user | Edit a product item's title, category, or description | I can keep product item definitions accurate and up to date |
| US-03 | Authorized user | Filter product items by category | I can quickly find items belonging to a specific coverage type |
| US-04 | Authorized user | Search for a product item by title | I can quickly find the item I need |
| US-05 | Authorized user | Soft-delete a product item | I can retire items no longer in use without losing the audit trail |

---

## 7. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | What fields does a product item have? | Title (required), category (required — seeded), and description (optional). |
| RD-02 | What happens when a product item is deleted? | Soft delete only — deactivated but not permanently removed. |

---

## 8. Out of Scope

- Assigning product items to insurer products directly from this screen — that is handled within the Insurer Product management flow.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*

---

## Implementation Status

| Task | Status | Date |
|---|---|---|
| CoreProductItem Model | ✅ Done | 2026-03-23 |
| Product Item CRUD API | ✅ Done | 2026-03-23 |
| Product Item List Page | ✅ Done | 2026-03-23 |
| Product Item Form Modal | ✅ Done | 2026-03-23 |
| Sidebar Navigation Link | ✅ Done | 2026-03-23 |
