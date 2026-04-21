# Product Category (Risk Type) Management — Requirements Document

**Module:** Core
**Feature:** Product Category Management
**Version:** 1.0
**Status:** Draft

---

## 1. Overview

The Product Category Management feature allows authorized users to create and manage risk types within the system. A risk type (product category) represents a category of insurable assets or services — for example, Auto Insurance, Home Insurance, or Life Insurance. Each product category can have templates assigned to it for specific purposes such as onboarding, claim, and claim evaluation.

Template assignment types are **seeded** by the system. For each assignment type, only **one template** can be assigned per product category at a time.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform product category management actions.

---

## 2. Key Rules

- A product category record holds: **title** and **description**.
- Title is **mandatory** and must be **unique** across all product categories.
- Description is **optional**.
- Product categories are **soft-deleted** — deactivated but not permanently removed.
- Templates are assigned to a product category **separately after creation**, not during the creation flow.
- Template assignment types are **seeded** by the system. The current seeded types are: `onboarding`, `claim`, and `claim_evaluation`.
- For each assignment type, a product category can have **only one template assigned** at a time.
- Any active template from the Template Management section can be assigned to a product category.
- Assigning a new template to an assignment type that already has one **replaces** the existing assignment.

---

## 3. Functional Requirements

### 3.1 Create Product Category

| # | Requirement | Permission |
|---|---|---|
| 3.1.1 | Users can create a new product category by providing a title and an optional description. | `risk_type.create` |
| 3.1.2 | Title is a required field; the form cannot be submitted without it. | `risk_type.create` |
| 3.1.3 | Title must be unique; a duplicate title is a hard block and cannot be saved. | `risk_type.create` |
| 3.1.4 | Description is an optional field. | `risk_type.create` |

---

### 3.2 View Product Categories

| # | Requirement | Permission |
|---|---|---|
| 3.2.1 | Users can view a list of all active product categories showing title and description. | `risk_type.view` |
| 3.2.2 | The product category list supports search by title. | `risk_type.view` |
| 3.2.3 | Users can view the full detail of a single product category including its assigned templates per assignment type. | `risk_type.view` |
| 3.2.4 | Soft-deleted product categories are hidden from the default list view. | `risk_type.view` |

---

### 3.3 Edit Product Category

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | Users can edit the title and description of an existing product category. | `risk_type.edit` |
| 3.3.2 | Title remains mandatory and unique during edit; it cannot be cleared or set to a duplicate value. | `risk_type.edit` |
| 3.3.3 | Soft-deleted product categories cannot be edited. | — |

---

### 3.4 Delete Product Category

| # | Requirement | Permission |
|---|---|---|
| 3.4.1 | Users can soft-delete a product category. | `risk_type.delete` |
| 3.4.2 | Soft-deleted product categories are deactivated and hidden from the default list but retained in the system. | — |
| 3.4.3 | Hard deletion is not supported. | — |

---

### 3.5 Template Assignment

| # | Requirement | Permission |
|---|---|---|
| 3.5.1 | After a product category is created, users can assign templates to it for each seeded assignment type. | `risk_type.assign_template` |
| 3.5.2 | The seeded assignment types are: `onboarding`, `claim`, and `claim_evaluation`. These types are system-managed and cannot be added, edited, or removed by users. | — |
| 3.5.3 | For each assignment type, only **one template** can be assigned to a product category at a time. | `risk_type.assign_template` |
| 3.5.4 | Any active template from the Template Management section can be selected for assignment. | `risk_type.assign_template` |
| 3.5.5 | If an assignment type already has a template assigned, assigning a new template replaces the existing one. | `risk_type.assign_template` |
| 3.5.6 | Users can remove a template assignment from an assignment type, leaving that type unassigned. | `risk_type.assign_template` |
| 3.5.7 | The product category detail view displays all three assignment types and their currently assigned template (or unassigned if none). | `risk_type.view` |
| 3.5.8 | Template assignment and removal actions are recorded in the audit log. | — |

---

## 4. Template Assignment Type Reference

| Assignment Type Code | Description | Seeded |
|---|---|---|
| `onboarding` | Template used during customer or policy onboarding for this risk type | Yes |
| `claim` | Template used when a claim is submitted for this risk type | Yes |
| `claim_evaluation` | Template used during the evaluation of a claim for this risk type | Yes |

---

## 5. Permission Reference Table

| Permission Key | Description |
|---|---|
| `risk_type.create` | Create new product categories |
| `risk_type.view` | View product category list and details including template assignments |
| `risk_type.edit` | Edit an existing product category's title and description |
| `risk_type.delete` | Soft-delete a product category |
| `risk_type.assign_template` | Assign or remove templates on a product category |

---

## 6. Non-Functional Requirements

| # | Requirement |
|---|---|
| 6.1 | All create, edit, delete, and template assignment actions must be recorded in the audit log with the acting user and timestamp. |
| 6.2 | Title uniqueness must be enforced at the database level. |
| 6.3 | Seeded assignment types must be pre-loaded at system initialisation and protected from modification or deletion. |
| 6.4 | Soft-deleted product categories must be retained indefinitely for audit purposes. |
| 6.5 | Only active (non-soft-deleted) templates must appear in the template selection dropdown during assignment. |

---

## 7. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create a product category with a title and description | I can define the types of insurable risks managed in the system |
| US-02 | Authorized user | Assign a template to a product category for onboarding | The correct form is used when onboarding a customer for that risk type |
| US-03 | Authorized user | Assign a template to a product category for claim | The correct form is used when a claim is submitted for that risk type |
| US-04 | Authorized user | Assign a template to a product category for claim evaluation | The correct form is used during claim evaluation for that risk type |
| US-05 | Authorized user | Replace an existing template assignment with a new one | I can update the form used for a specific assignment type without losing the category |
| US-06 | Authorized user | Remove a template assignment from an assignment type | I can unset a template for an assignment type when it is no longer applicable |
| US-07 | Authorized user | Edit a product category's title or description | I can keep category definitions accurate as requirements evolve |
| US-08 | Authorized user | Soft-delete a product category | I can retire risk types no longer in use without losing the audit trail |

---

## 8. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | What fields does a product category have? | Title (required, unique) and description (optional). |
| RD-02 | Is title unique? | Yes — duplicate titles are a hard block. |
| RD-03 | When is template assignment done? | Separately after the product category is created, not during the creation flow. |
| RD-04 | Which templates can be assigned? | Any active template from the Template Management section. |
| RD-05 | How many templates per assignment type per category? | Only one — assigning a new template replaces the existing one. |
| RD-06 | What are the assignment types? | Three seeded types: `onboarding`, `claim`, `claim_evaluation`. System-managed, not editable by users. |
| RD-07 | What happens when a product category is deleted? | Soft delete only — deactivated but not permanently removed. |

---

## 9. Out of Scope

- Creating or managing template assignment types (these are system-seeded and fixed).
- Linking product categories to policies or risks — handled by the Policy module.
- Versioning or history of template assignments per category.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*

---

## 10. Implementation Status

| Feature | Status | Notes |
|---|---|---|
| Product Category (Risk Type) CRUD | ✅ Completed | Implemented with `CoreRiskType` model and `risk-types` API. |
| Template Assignment | ✅ Completed | Managed via `RiskTypeController` and `assign-template` endpoint. |
| Reason Type (Endorsement Type) Restore | ✅ Completed | Restored `CoreEndorsementType` and legacy `endorsement-types` API for Reasons. |
| Redundant Field Cleanup | ✅ Completed | Removed `created_at`/`updated_at` from `CoreRiskType` as they are in `CoreEntity`. |
