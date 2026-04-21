# Template & Form Builder — Full Specification

**Module:** Core  
**Feature:** Template Management + Form Builder  
**Version:** 2.0  
**Status:** Ready for Development  
**Last Updated:** 2026-03-25

---

## Table of Contents

1. [Overview](#1-overview)
2. [Data Models & Tables](#2-data-models--tables)
3. [API Endpoints](#3-api-endpoints)
4. [Screen 1 — Template List](#4-screen-1--template-list)
5. [Screen 2 — Create Template Modal](#5-screen-2--create-template-modal)
6. [Screen 3 — Template Single View (Form Builder)](#6-screen-3--template-single-view-form-builder)
7. [Builder Zone — Left Panel: Element Palette](#7-builder-zone--left-panel-element-palette)
8. [Builder Zone — Center Canvas: Steps & Panels](#8-builder-zone--center-canvas-steps--panels)
9. [Builder Zone — Right Panel: Element Configuration](#9-builder-zone--right-panel-element-configuration)
10. [Row Layout & Column Size System](#10-row-layout--column-size-system)
11. [Drag-and-Drop Interaction Rules](#11-drag-and-drop-interaction-rules)
12. [Ordering System (Float Midpoint)](#12-ordering-system-float-midpoint)
13. [Element Reference — All 49 Seeded Elements](#13-element-reference--all-49-seeded-elements)
14. [Permission Reference](#14-permission-reference)
15. [Non-Functional Requirements](#15-non-functional-requirements)
16. [Resolved Decisions](#16-resolved-decisions)
17. [Out of Scope](#17-out-of-scope)

---

## 1. Overview

The Template Management feature provides a **drag-and-drop form builder** for creating reusable form templates. A template is a structured form definition composed of steps (for multi-step forms), panels (layout containers), and elements (individual form fields).

Templates are used across modules (CRM, Policy, Claims) as reusable form structures. They are never tied to a specific module at creation — they are generic and reusable.

### Core concepts

| Concept | Description |
|---------|-------------|
| **Template** | The root record. Has a `title`, `type` (`single_form` or `multi_step_form`), and optional `description`. |
| **Step** | A page within a `multi_step_form`. Has a `step_number` (Float) and `title`. Not used in `single_form`. |
| **Panel** | A layout container inside a step (or directly in the form for `single_form`). Has a `title`, `order_number` (Float), and `columns_per_row` setting. Elements live inside panels. |
| **Element** | A form field placed inside a panel. References a base element definition from `core_form_elements`. Has `label`, `is_required`, `order_number`, `column_size`, `category`, `code`. |
| **Option** | A selectable value for choice-type elements (Dropdown, Radio Box, etc.). Stored in `core_form_custom_form_element_options`. |
| **Display Value** | A default or display value for elements. Stored in `core_form_display_element_values`. Used for heading text, default input values, HTML content. |

### Two form types

```
single_form
  └── Panel (step_id = null)
        └── Element → Element → Element

multi_step_form
  ├── Step 1 (step_number = 1.0)
  │     └── Panel (step_id = Step 1)
  │           └── Element → Element
  └── Step 2 (step_number = 2.0)
        └── Panel (step_id = Step 2)
              └── Element → Element
```

**Key rule:** `type` cannot be changed after template creation. Changing it would invalidate all `step_id` references on existing panels.

---

## 2. Data Models & Tables

### 2.1 `core_templates`

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INT (PK) | No | auto | Primary key |
| `title` | VARCHAR(200) | No | — | Template name. Required. Must be unique system-wide. |
| `type` | VARCHAR(20) | No | — | `single_form` or `multi_step_form`. Required. Locked after creation. |
| `description` | VARCHAR(250) | Yes | NULL | Optional description |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE INDEX idx_template_title (title)`

---

### 2.2 `core_form_custom_form_steps`

Only used by `multi_step_form` templates. Not applicable to `single_form`.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INT (PK) | No | auto | Primary key |
| `form_id` | INT (FK) | No | — | FK → `core_templates.id`. CASCADE on template delete. |
| `title` | VARCHAR(200) | No | — | Step label shown in the step tab. Required. |
| `step_number` | FLOAT | No | — | Float ordering value. Drives tab order in the builder. |
| `description` | VARCHAR(250) | Yes | NULL | Optional step description |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX idx_step_form (form_id)`
- `INDEX idx_step_number (form_id, step_number)` — supports ordered step fetch

**Ordering:** `step_number` is a Float. New steps append at `max(step_number) + 1`. Reordering uses the midpoint formula (see Section 12).

---

### 2.3 `core_form_custom_form_panels`

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INT (PK) | No | auto | Primary key |
| `form_id` | INT (FK) | No | — | FK → `core_templates.id`. CASCADE on delete. |
| `step_id` | INT (FK) | Yes | NULL | FK → `core_form_custom_form_steps.id`. SET NULL on step delete. NULL for `single_form`. |
| `title` | VARCHAR(200) | Yes | NULL | Optional panel label/heading |
| `order_number` | FLOAT | No | 1.0 | Float ordering value within the form. Drives panel stacking order. |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX idx_panel_form (form_id)`
- `INDEX idx_panel_step (step_id)`
- `INDEX idx_panel_order (form_id, order_number)`

> **Note:** The `columns_per_row` setting for row layout is currently managed at the element level via `column_size`. There is no explicit `columns_per_row` column on the panel. Row layout is derived from the `column_size` values of the elements within the panel (see Section 10).

---

### 2.4 `core_form_custom_form_elements`

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INT (PK) | No | auto | Primary key |
| `label` | VARCHAR(200) | Yes | NULL | User-defined label/name for the element |
| `step_id` | INT (FK) | Yes | NULL | FK → `core_form_custom_form_steps.id`. Required for `multi_step_form`; null for `single_form`. |
| `panel_id` | INT (FK) | Yes | NULL | FK → `core_form_custom_form_panels.id`. SET NULL on panel delete. |
| `element_id` | INT (FK) | No | — | FK → `core_form_elements.id`. The base element definition. |
| `is_required` | BOOLEAN | No | FALSE | Whether this field is required on form submission |
| `parent_id` | INT (FK) | Yes | NULL | Self-FK → `core_form_custom_form_elements.id`. Used for `input_group` sub-elements (e.g. Date Range → From, To). |
| `order_number` | FLOAT | Yes | NULL | Float ordering within the panel. Drives element position. |
| `column_size` | INT | No | — | Number of columns this element occupies (1–max_columns). Drives row layout. |
| `category` | VARCHAR(200) | Yes | NULL | Copied from `core_form_elements.category`: `input_individual`, `input_group`, or `display` |
| `code` | VARCHAR(200) | Yes | NULL | Copied from `core_form_elements.code` (e.g. `SHORT_ANSWER`, `DROPDOWN`) |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX idx_elem_panel (panel_id)`
- `INDEX idx_elem_step (step_id)`
- `INDEX idx_elem_parent (parent_id)`
- `INDEX idx_elem_order (panel_id, order_number)`

---

### 2.5 `core_form_custom_form_element_options`

Stores selectable options for choice-type elements.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `element_id` | INT (FK) | No | FK → `core_form_custom_form_elements.id`. CASCADE on element delete. |
| `option_value` | VARCHAR(200) | No | The option text (e.g. "Yes", "No", "Option 1") |

**Applicable to:** `DROPDOWN`, `RADIO_BOX`, `MULTI_CHOICE`, `MULTI_SELECT`, `PICTURE_CHOICE`, `OPTION_SCALE`

---

### 2.6 `core_form_display_element_values`

Stores default/display text values for elements.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `element_id` | INT (FK) | No | FK → `core_form_custom_form_elements.id`. CASCADE on element delete. |
| `value` | TEXT | No | The stored value. Meaning depends on element type — e.g. heading text for `HEADING`, default value for inputs, HTML content for `HTML`. |

One row per element maximum.

---

### 2.7 `core_form_elements` (seed data — read-only)

Base element definitions. 49 rows seeded via `seed_core_form_elements` management command.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `title` | VARCHAR(200) | Human-readable name (e.g. "Short Answer") |
| `element_group` | VARCHAR(200) | Palette group (e.g. "Frequently Used", "Choices", "Date & Time") |
| `category` | VARCHAR(20) | `input_individual`, `input_group`, or `display` |
| `code` | VARCHAR(200) | Unique code (e.g. `SORT_ANSWER`, `DROPDOWN`, `HEADING`) |
| `description` | VARCHAR(250) | Optional description |
| `group_id` | INT (FK self) | For sub-elements of `input_group` — points to the parent group element |
| `group_element_order_number` | FLOAT | Sub-element order within the group (e.g. 1 = From, 2 = To in Date Range) |

**This table is seeded and read-only.** Users never create or modify rows here.

---

### 2.8 `core_form_submissionss` (submission target — read-only from builder)

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `form_id` | INT (FK) | FK → `core_templates.id` |
| `user_id` | INT (FK) | FK → `core_users.id`. Nullable. |
| `customer_id` | INT (FK) | FK → customer table. Nullable. |

> Note: table name has a double `s` — `core_form_submissionss`. This is the model's `db_table` value as defined in the codebase. Templates with submissions cannot be deleted.

---

## 3. API Endpoints

### 3.1 Template CRUD

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/api/templates` | `template.view` | List templates. Supports `?search=`, `?filter={"type":"..."}`, `?page=`, `?limit=`, `?sort_by=`, `?sort_dir=` |
| `POST` | `/api/templates` | `template.create` | Create template. Body: `{ title, type, description? }` |
| `GET` | `/api/templates/<id>` | `template.view` | Get full template detail: template + steps + panels + elements + options + values in one payload |
| `PUT` | `/api/templates/<id>` | `template.edit` | Update `title`, `type`, `description`. Type uniqueness check excludes self. |
| `DELETE` | `/api/templates/<id>` | `template.delete` | Hard-delete. **Blocked if any `core_form_submissionss` rows reference this template.** |

#### `GET /api/templates` query parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Searches `title` and `description` (ILIKE) |
| `filter` | JSON string | Allowed keys: `title`, `type` |
| `page` | int | Page number (default 1) |
| `limit` | int | Records per page (default 10) |
| `sort_by` | string | Allowed: `title`, `type`, `id` (default `id`) |
| `sort_dir` | string | `asc` or `desc` (default `desc`) |

#### `POST /api/templates` request body

```json
{
  "title": "Onboarding Form",
  "type": "single_form",
  "description": "Used during customer onboarding"
}
```

#### `GET /api/templates/<id>` response shape

```json
{
  "template": { "id": 1, "name": "...", "type": "...", "description": "..." },
  "steps": [ { "id": 1, "title": "Step 1", "step_number": 1.0, "description": null } ],
  "panels": [ { "id": 1, "title": "Contact Details", "step_id": 1, "order_number": 1.0 } ],
  "elements": [
    {
      "id": 1, "label": "Full Name", "element_id": 1, "step_id": 1,
      "panel_id": 1, "order_number": 1.0, "column_size": 6,
      "is_required": true, "category": "input_individual",
      "code": "SORT_ANSWER", "options": [], "value": null
    }
  ]
}
```

---

### 3.2 Step Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/api/forms/<id>/steps` | `template.view` | List all steps for a template, ordered by `step_number` |
| `POST` | `/api/forms/<id>/steps` | `template.edit` | Create step. Auto-sets `step_number` = `max(step_number) + 1`. Body: `{ title, description? }` |
| `GET` | `/api/forms/<id>/steps/<step_id>` | `template.view` | Get single step detail |
| `PATCH` | `/api/forms/<id>/steps/<step_id>` | `template.edit` | Update step. Reorders using `prev_step_id` / `next_step_id`. Body: `{ title, description?, prev_step_id?, next_step_id? }` |
| `DELETE` | `/api/forms/<id>/steps/<step_id>` | `template.edit` | Delete step. **Cascades:** deletes all panels in step → all elements in those panels → all submission values for those elements. |

#### `PATCH /api/forms/<id>/steps/<step_id>` — reorder logic

Send `prev_step_id` and/or `next_step_id` to calculate new `step_number`:

| Case | Formula |
|------|---------|
| Between two steps | `(prev.step_number + next.step_number) / 2` |
| Before first step | `next.step_number / 2` |
| After last step | `prev.step_number + 1` |
| No references | Falls back to `1.0` |

---

### 3.3 Panel Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `POST` | `/api/forms/<id>/panels` | `template.edit` | Create panel. For `multi_step_form`, `step_id` is required. Auto-increments `order_number`. Body: `{ title?, step_id? }` |
| `GET` | `/api/forms/<id>/steps/<step_id>/panels` | `template.view` | List panels for a specific step, ordered by `order_number` |
| `PATCH` | `/api/forms/<id>/panels/<panel_id>` | `template.edit` | Update panel title, step, and order. Uses `prev_panel_id` / `next_panel_id` for reorder. |
| `DELETE` | `/api/forms/<id>/panels/<panel_id>` | `template.edit` | Delete panel. **Cascades:** deletes all elements in panel → all submission values for those elements. |
| `POST` | `/api/forms/<id>/panels/<panel_id>/duplicate` | `template.edit` | Deep-copy panel. Creates new panel with midpoint `order_number`. Duplicates all elements, options, and display values. Returns full panel + elements structure. |

#### `POST /api/forms/<id>/panels` request body

```json
{
  "title": "Personal Information",
  "step_id": 1
}
```

> For `single_form`, omit `step_id` entirely — it will be stored as NULL.

#### `POST /api/forms/<id>/panels/<panel_id>/duplicate` response shape

```json
{
  "panel": { "id": 5, "title": "Personal Information (Copy)", "step_id": 1, "order_number": 1.5 },
  "elements": [ { "id": 10, "label": "...", "options": [], "value": null, ... } ]
}
```

---

### 3.4 Element Endpoints

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `POST` | `/api/forms/<id>/elements` | `template.edit` | Create element inside a panel. Handles options (bulk insert) and display value in one atomic transaction. |
| `GET` | `/api/forms/<id>/elements` | `template.view` | Get all `input_individual` elements for the form (excludes `display` and `input_group`). Includes options and values. |
| `GET` | `/api/forms/<id>/elements/<element_id>` | `template.view` | Get single element detail with options and value. |
| `PATCH` | `/api/forms/<id>/elements/<element_id>` | `template.edit` | Update element. Replaces all options (delete + bulk_create). Updates or creates display value. Reorders using `prev_element_id` / `next_element_id`. |
| `DELETE` | `/api/forms/<id>/elements/<element_id>` | `template.edit` | Delete element. FK cascade handles options and values. |
| `GET` | `/api/templates/form-elements` | `template.view` | Get all 49 seeded base elements grouped into palette groups. Returns `elements` (individual) and `group_elements` (sub-elements of input_group). Used to populate the left-side element palette. |

#### `POST /api/forms/<id>/elements` request body

```json
{
  "label": "Full Name",
  "panel_id": 1,
  "step_id": 1,
  "element_id": 1,
  "is_required": true,
  "column_size": 6,
  "category": "input_individual",
  "code": "SORT_ANSWER",
  "options": [],
  "value": null,
  "parent_id": null
}
```

> For `single_form`, omit `step_id`. For `input_group` sub-elements, set `parent_id` to the parent `input_group` element's ID.

#### `GET /api/templates/form-elements` response shape

```json
{
  "elements": [
    {
      "group": "Frequently Used",
      "elements": [
        { "id": 1, "title": "Short Answer", "code": "SORT_ANSWER", "category": "input_individual", "options": [] },
        { "id": 2, "title": "Multiple Choice", "code": "MULTI_CHOICE", "category": "input_individual", "options": [] }
      ]
    },
    {
      "group": "Choices",
      "elements": [ ... ]
    }
  ],
  "group_elements": [
    { "id": 17, "title": "From", "code": "DATE_RANGE_FROM_DATE", "group_id": 16, "group_element_order_number": 1 },
    { "id": 18, "title": "To",   "code": "DATE_RANGE_TO_DATE",   "group_id": 16, "group_element_order_number": 2 }
  ]
}
```

---

## 4. Screen 1 — Template List

**Route:** `/templates`  
**Permission:** `template.view`

### UI Tasks

| Task ID | Component | Description |
|---------|-----------|-------------|
| TL-01 | Page header | Title "Templates" + total count. "New Template" button (gated by `template.create`). |
| TL-02 | Search bar | Debounced search on `title`. Calls `GET /api/templates?search=`. |
| TL-03 | Type filter | Dropdown or toggle filter for `single_form` / `multi_step_form`. Appends `filter={"type":"..."}` to query. |
| TL-04 | Templates table | Columns: Title, Type badge, Description (truncated), Actions. |
| TL-05 | Type badge | `single_form` → neutral "Single Form" badge. `multi_step_form` → brand "Multi Step" badge. |
| TL-06 | Row: Open action | Clicking the row or a "Open Builder" button navigates to `/templates/<id>` (the form builder). |
| TL-07 | Row: Edit metadata | "Edit" action opens the edit modal (title + description only — type is locked). Calls `PUT /api/templates/<id>`. |
| TL-08 | Row: Duplicate | "Duplicate" action clones the full template. Calls `POST /api/templates` with title suffixed "(Copy)" and same type + description, then copies all steps/panels/elements programmatically. Shows toast on success. |
| TL-09 | Row: Delete | "Delete" action shows confirmation dialog. Calls `DELETE /api/templates/<id>`. If blocked (template has submissions), shows: "This template cannot be deleted because it has active submissions." |
| TL-10 | Pagination | Server-side. Default page_size = 10. Shows "Showing X–Y of Z". |
| TL-11 | Empty state | "No templates yet. Create your first template to get started." with a "New Template" CTA. |

---

## 5. Screen 2 — Create Template Modal

**Trigger:** "New Template" button on the list page  
**Permission:** `template.create`

### UI Tasks

| Task ID | Component | Description |
|---------|-----------|-------------|
| MC-01 | Modal trigger | "New Template" button. Opens a 480 px modal. |
| MC-02 | Title field | Text input. Label: "Template Title". Required. Max 200 characters. Duplicate title shows inline warning (hard block — the API enforces uniqueness). |
| MC-03 | Type selector | Two clearly distinct option cards or a segmented control: "Single Form" (one page) vs "Multi Step Form" (wizard with multiple pages). Required. Type cannot be changed later — show a hint: "This cannot be changed after creation." |
| MC-04 | Description field | Textarea. Label: "Description". Optional. Max 250 characters. Live counter. |
| MC-05 | Submit | Calls `POST /api/templates`. On success: close modal, navigate directly to `/templates/<new_id>` (the form builder). Do not return to the list — the user should land in the builder immediately. |
| MC-06 | Validation | Title required. Type required. On submit without required fields: shake modal, focus first invalid field. |
| MC-07 | Cancel | Closes modal without saving. |

---

## 6. Screen 3 — Template Single View (Form Builder)

**Route:** `/templates/<id>`  
**Permission:** `template.view` (read-only view) / `template.edit` (builder editing)

### Layout Structure

The form builder is a **three-panel layout**:

```
┌─────────────────────────────────────────────────────────────┐
│  Template header: title | type badge | Save | Back          │
├──────────────┬──────────────────────────────┬───────────────┤
│              │                              │               │
│  LEFT PANEL  │     CENTER CANVAS            │  RIGHT PANEL  │
│  (240px)     │     (flex, fills space)      │  (280px)      │
│              │                              │               │
│  Element     │  Step tabs (multi_step only) │  Element      │
│  Palette     │  + Panel list                │  Config       │
│              │  + Elements in panels        │  (shows when  │
│              │                              │  element      │
│              │                              │  is selected) │
└──────────────┴──────────────────────────────┴───────────────┘
```

### Header Tasks

| Task ID | Component | Description |
|---------|-----------|-------------|
| BH-01 | Template title | Displayed in the header. Clicking opens an inline edit field. Calls `PUT /api/templates/<id>` on blur/enter. |
| BH-02 | Type badge | Read-only badge (`single_form` or `multi_step_form`). Not clickable. |
| BH-03 | Save button | Saves pending changes to the builder state. Explicitly triggered by the user — no auto-save. Disabled when no unsaved changes. |
| BH-04 | Back button | Navigates to the template list. Warns if there are unsaved changes: "You have unsaved changes. Leave without saving?" |
| BH-05 | Builder mode indicator | If the user has `template.view` but not `template.edit`, all builder controls are hidden and a "View only" badge is shown. Drag-and-drop is disabled. |

---

## 7. Builder Zone — Left Panel: Element Palette

**Data source:** `GET /api/templates/form-elements`  
**Loaded once** when the builder opens. Cached for the session.

### UI Tasks

| Task ID | Component | Description |
|---------|-----------|-------------|
| LP-01 | Palette load | On builder open, call `GET /api/templates/form-elements`. Display a loading skeleton. Cache the result — do not re-fetch on every panel drop. |
| LP-02 | Group sections | Render each group as a collapsible accordion section: "Frequently Used", "Text", "Choices", "Date & Time", "Contact Info", "Numbers", "Rating & Ranking", "Miscellaneous", "Navigation & Layout", "Display Text", "Media". |
| LP-03 | "Frequently Used" open by default | The "Frequently Used" group is expanded by default. All others are collapsed. |
| LP-04 | Element cards | Each element shown as a small draggable card: icon (based on element type) + element title. |
| LP-05 | Category visual differentiation | `input_individual` elements — standard card style. `input_group` elements — show a subtle "group" indicator (e.g. a stacked-cards icon). `display` elements — slightly muted/italic style to distinguish them. |
| LP-06 | Search within palette | A search input at the top of the left panel. Filters elements across all groups in real time (client-side, no API call). Matching groups auto-expand; non-matching groups collapse. |
| LP-07 | Drag initiation | Clicking and dragging an element card from the palette initiates a drag event. The drag payload carries: `element_id`, `code`, `category`, `title`, `group_id` (for `input_group`). |
| LP-08 | `input_group` drag behavior | When a `DATE_RANGE` or `LOCATION` element is dragged and dropped, the system automatically creates **multiple elements**: the group parent + all its sub-elements. Sub-elements reference the parent via `parent_id`. The palette renders these as a single draggable card; the API call creates multiple element records. |
| LP-09 | Panel collapse state | The left panel can be collapsed to a narrow icon rail to give more space to the canvas. A toggle button in the panel header handles this. |

---

## 8. Builder Zone — Center Canvas: Steps & Panels

### 8.1 Step Management (multi_step_form only)

| Task ID | Component | Description |
|---------|-----------|-------------|
| ST-01 | Step tabs | Render one tab per step, ordered by `step_number`. Active step's canvas is shown; others are hidden. |
| ST-02 | Add step | "+" button at the end of the tab row. Calls `POST /api/forms/<id>/steps` with a default title "Step N". Activates the new step. |
| ST-03 | Rename step | Double-clicking a step tab makes the title inline-editable. On blur/enter, calls `PATCH /api/forms/<id>/steps/<step_id>` with the new title. |
| ST-04 | Reorder step tabs | Step tabs are draggable. On drop, call `PATCH /api/forms/<id>/steps/<step_id>` with `prev_step_id` and `next_step_id` of the neighbors after the drop. New `step_number` is calculated server-side as the midpoint. |
| ST-05 | Delete step | Each step tab has a "×" remove button (visible on hover). Clicking shows a confirmation: "Deleting this step will also delete all panels and elements within it." On confirm, calls `DELETE /api/forms/<id>/steps/<step_id>`. Switches to the previous or next step. |
| ST-06 | Single form — no step tabs | For `single_form`, the step tab row is hidden entirely. The canvas shows a single page. |

### 8.2 Panel Management

| Task ID | Component | Description |
|---------|-----------|-------------|
| PA-01 | Add panel | "Add Panel" button below the last panel on the current step/page. Calls `POST /api/forms/<id>/panels` with `step_id` (for `multi_step_form`) or without it (for `single_form`). New panel appears at the bottom with an empty drop zone. |
| PA-02 | Panel title | Each panel has an optional title displayed at its top. Clicking the title makes it inline-editable. On blur/enter, calls `PATCH /api/forms/<id>/panels/<panel_id>`. |
| PA-03 | Panel reorder | Panels have a drag handle (e.g. `⠿` icon) at their top-left. Dragging and dropping a panel reorders it. On drop, calls `PATCH /api/forms/<id>/panels/<panel_id>` with `prev_panel_id` and `next_panel_id`. |
| PA-04 | Panel duplicate | Each panel has a "Duplicate" action (via a "⋯" context menu). Calls `POST /api/forms/<id>/panels/<panel_id>/duplicate`. The duplicated panel appears immediately below the original. |
| PA-05 | Panel delete | "Delete Panel" in the panel context menu. Confirmation: "Deleting this panel will also remove all elements within it." On confirm, calls `DELETE /api/forms/<id>/panels/<panel_id>`. |
| PA-06 | Panel drop zone | Each panel has a visible drop zone area where elements can be dropped from the palette. Drop zone shows a dashed border and a "Drop elements here" hint when empty. |
| PA-07 | Columns-per-row selector | Each panel has a "Columns" control in its header (e.g. a 1/2/3/4 button group). This sets the default `column_size` for newly dropped elements and visually divides the panel into that many columns. The actual `column_size` is stored per element, not on the panel itself. |
| PA-08 | Empty panel state | A panel with no elements shows: dashed border drop zone + "Drag elements here" label. |

---

## 9. Builder Zone — Right Panel: Element Configuration

The right panel opens when an element is clicked/selected on the canvas. It shows the configuration form for that element.

### 9.1 Configuration Panel Behavior

| Task ID | Component | Description |
|---------|-----------|-------------|
| RC-01 | Open on click | Clicking any element on the canvas opens the right configuration panel. The selected element is highlighted with a border on the canvas. |
| RC-02 | Close | Clicking elsewhere on the canvas (not on an element) deselects and closes the right panel. |
| RC-03 | Save on change | Changes in the configuration panel are applied via `PATCH /api/forms/<id>/elements/<element_id>` when the user confirms (either auto-apply on field blur, or an explicit "Apply" button). |
| RC-04 | Category-aware fields | Fields shown depend on the element's `category`. See Section 9.2. |

### 9.2 Configuration Fields by Category

#### `input_individual` elements

| Field | UI Control | API Field | Applies To |
|-------|-----------|-----------|------------|
| Label / Name | Text input | `label` | All |
| Required | Toggle switch | `is_required` | All |
| Column size | Number stepper or slider (1 to max columns) | `column_size` | All |
| Options | Drag-reorderable list + "Add option" | `options[]` | `DROPDOWN`, `RADIO_BOX`, `MULTI_CHOICE`, `MULTI_SELECT`, `PICTURE_CHOICE`, `OPTION_SCALE` |
| Default value | Text input | `value` (stored in `core_form_display_element_values`) | Most input types |
| Placeholder text | Text input | Stored in `value` or as a label convention | Text inputs, email, phone |

#### `input_group` elements (Date Range, Location Coordinate)

| Field | UI Control | Description |
|-------|-----------|-------------|
| Group label | Text input | Label for the parent group |
| Sub-element labels | Separate label field per sub-element | Each sub-element (e.g. "From", "To") has its own label |
| Required | Toggle per sub-element | `is_required` per sub-element |

Sub-elements are rendered as a nested section in the right panel. Each sub-element's `PATCH` call references the sub-element's own `id`.

#### `display` elements

| Field | UI Control | Description |
|-------|-----------|-------------|
| Content / value | Textarea or rich text | The display content (e.g. heading text, paragraph content, HTML). Stored in `core_form_display_element_values`. |
| No `is_required`, no `options`, no `placeholder` | — | Display elements have no interaction config. |

### 9.3 Element Actions in Configuration Panel

| Action | Behavior | API Call |
|--------|----------|---------|
| Remove element | "Remove" button in the config panel header. Confirmation: "Remove this element from the panel?" | `DELETE /api/forms/<id>/elements/<element_id>` |
| Duplicate element | "Duplicate" button. Creates a copy of the element directly below it in the same panel with the same config. | `POST /api/forms/<id>/elements` with same payload, new `order_number` = midpoint |

---

## 10. Row Layout & Column Size System

### How it works

The canvas uses a **12-column grid system** (configurable per panel). Each element's `column_size` determines how many columns it occupies in that row.

```
Panel: columns_per_row = 3 (i.e. max_column_size = 4 per element in a 12-col grid)

Row 1:  [Element A: col_size=4] [Element B: col_size=4] [Element C: col_size=4]
Row 2:  [Element D: col_size=8]           [Element E: col_size=4]
Row 3:  [Element F: col_size=12]
```

### Column size rules

| Rule | Detail |
|------|--------|
| Total columns per row | Derived from the panel's column setting. Default: 12 columns total. |
| `column_size` value | Integer 1–12. Stored per element in `core_form_custom_form_elements.column_size`. |
| Full-width element | `column_size = 12`. Takes the entire row. |
| Two equal columns | Each element has `column_size = 6`. |
| Three equal columns | Each element has `column_size = 4`. |
| Four equal columns | Each element has `column_size = 3`. |
| Row overflow | If elements in a row sum to > 12, the overflow wraps to the next row automatically. |

### UI representation

The panel header shows a **columns-per-row quick-select** control (e.g. 1 / 2 / 3 / 4 buttons). Selecting "3" sets newly dropped elements to `column_size = 4` by default. Existing elements are not changed.

Individual element `column_size` can be adjusted in the right configuration panel — a stepper or slider from 1 to 12.

### API mapping

`column_size` is sent in the `POST /api/forms/<id>/elements` and `PATCH /api/forms/<id>/elements/<element_id>` request bodies as an integer.

---

## 11. Drag-and-Drop Interaction Rules

### From palette → panel (add element)

| Step | What happens |
|------|-------------|
| 1 | User drags an element card from the left palette |
| 2 | Hovering over a panel highlights the panel's drop zone |
| 3 | On drop: call `POST /api/forms/<id>/elements` with the element's `element_id`, `panel_id`, default `column_size` (from panel's columns setting), `category`, `code`, and `step_id` (for `multi_step_form`) |
| 4 | For `input_group` elements: also create sub-elements, each with `parent_id` pointing to the group element's `id`. Use `group_element_order_number` from the seed data to set sub-element `order_number`. |
| 5 | New element appears at the bottom of the panel (highest `order_number`) |
| 6 | Right configuration panel opens automatically for the newly dropped element |

### Reorder within panel (element drag)

| Step | What happens |
|------|-------------|
| 1 | User drags an element within its panel |
| 2 | Drop indicator appears between elements as the user hovers |
| 3 | On drop: call `PATCH /api/forms/<id>/elements/<element_id>` with `prev_element_id` and `next_element_id` of the neighbors at the drop position |
| 4 | New `order_number` = midpoint (computed server-side) |

### Move element to different panel

| Step | What happens |
|------|-------------|
| 1 | User drags element and drops it onto a different panel |
| 2 | Call `PATCH /api/forms/<id>/elements/<element_id>` with the new `panel_id`, new `step_id` (if different step), and `prev_element_id` / `next_element_id` within the target panel |

### Reorder panels

| Step | What happens |
|------|-------------|
| 1 | User drags panel by its drag handle |
| 2 | Drop indicator appears between panels |
| 3 | On drop: call `PATCH /api/forms/<id>/panels/<panel_id>` with `prev_panel_id` and `next_panel_id` |

### Constraints

| Rule | Detail |
|------|--------|
| Elements must stay in panels | You cannot drop an element directly on the page canvas outside a panel. Only valid drop targets are panel drop zones. |
| `display` elements | Can be placed in panels but have no `is_required` or options config. |
| `input_group` sub-elements | Cannot be dragged independently from the palette. They are always created automatically when the parent group element is dropped. They can be reordered within the panel like any other element, but their `parent_id` is preserved. |

---

## 12. Ordering System (Float Midpoint)

Steps, panels, and elements all use the same float ordering strategy. This allows reordering without touching any other records.

### Rules

| Operation | Formula |
|-----------|---------|
| Append to end | `new = max(order_number) + 1` |
| Move between A and B | `new = (A.order_number + B.order_number) / 2` |
| Move before first | `new = first.order_number / 2` |
| Move after last | `new = last.order_number + 1` |
| No neighbors | Falls back to `1.0` |

### API fields for reorder

| Entity | PATCH field | Meaning |
|--------|------------|---------|
| Step | `prev_step_id` | ID of the step that should be directly before the moved step |
| Step | `next_step_id` | ID of the step that should be directly after the moved step |
| Panel | `prev_panel_id` | ID of the panel directly before in the new position |
| Panel | `next_panel_id` | ID of the panel directly after in the new position |
| Element | `prev_element_id` | ID of the element directly before in the new position |
| Element | `next_element_id` | ID of the element directly after in the new position |

Pass only the relevant IDs. Omit both to fall back to default. Pass only one if moving to the start or end.

---

## 13. Element Reference — All 49 Seeded Elements

### `input_individual` category (42 elements)

| ID | Title | Code | Group |
|----|-------|------|-------|
| 1  | Short Answer | `SORT_ANSWER` | Frequently Used |
| 2  | Multiple Choice | `MULTI_CHOICE` | Frequently Used |
| 3  | Email Input | `EMAIL_INPUT` | Frequently Used |
| 7  | Dropdown | `DROPDOWN` | Choices |
| 8  | Picture Choice | `PICTURE_CHOICE` | Choices |
| 9  | Multiple Select | `MULTI_SELECT` | Choices |
| 10 | Switch | `SWITCH` | Choices |
| 11 | Check Box | `MULTI_CHOICE` | Choices |
| 12 | Radio Box | `RADIO_BOX` | Choices |
| 13 | Date Picker | `DATE_PICKER` | Date & Time |
| 14 | Time Picker | `TIME_PICKER` | Date & Time |
| 15 | Date & Time | `DATE_TIME` | Date & Time |
| 19 | Ranking | `RANKING` | Rating & Ranking |
| 20 | Star Rating | `STAR_RATING` | Rating & Ranking |
| 21 | Slider | `SLIDER` | Rating & Ranking |
| 22 | Option Scale | `OPTION_SCALE` | Rating & Ranking |
| 23 | Short Answer | `SORT_ANSWER` | Text |
| 24 | Long Answer | `LONG_ANSWER` | Text |
| 25 | Phone | `PHONE_INPUT` | Contact Info |
| 26 | Email | `EMAIL_INPUT` | Contact Info |
| 27 | Address | `ADDRESS` | Contact Info |
| 28 | Numbers | `NUMBERS` | Numbers |
| 29 | Currency | `CURRENCY` | Numbers |
| 30 | URL Input | `URL_INPUT` | Miscellaneous |
| 31 | Color Picker | `COLOR_PICKER` | Miscellaneous |
| 32 | Password | `PASSWORD` | Miscellaneous |
| 33 | File Upload | `FILE_UPLOAD` | Miscellaneous |
| 34 | Signature | `SIGNATURE` | Miscellaneous |
| 35 | Voice Recording | `VOICE_RECORDING` | Miscellaneous |
| 36 | Submission Picker | `SUBMISSION_PICKER` | Miscellaneous |
| 40 | Captcha | `CAPTCHA` | Miscellaneous |
| 41 | Subform | `SUBFORM` | Miscellaneous |

### `input_group` category (2 groups + 4 sub-elements)

| ID | Title | Code | Type | Sub-elements |
|----|-------|------|------|--------------|
| 16 | Date Range | `DATE_RANGE` | Group parent | IDs 17, 18 |
| 17 | From | `DATE_RANGE_FROM_DATE` | Sub-element | `group_id=16`, `order=1` |
| 18 | To | `DATE_RANGE_TO_DATE` | Sub-element | `group_id=16`, `order=2` |
| 37 | Location Coordinate | `LOCATION` | Group parent | IDs 38, 39 |
| 38 | Latitude | `LOCATION_LATITUDE` | Sub-element | `group_id=37`, `order=1` |
| 39 | Longitude | `LOCATION_LONGITUDE` | Sub-element | `group_id=37`, `order=2` |

### `display` category (11 elements)

| ID | Title | Code | Group |
|----|-------|------|-------|
| 4  | Heading | `HEADING` | Display Text |
| 5  | Paragraph | `PARAGRAPH` | Display Text |
| 6  | Banner | `BANNER` | Display Text |
| 49 | Line Break | `LINE_BREAK` | Display Text |
| 42 | Section Collapse | `SECTION_COLLAPSE` | Navigation & Layout |
| 43 | Divider | `DIVIDER` | Navigation & Layout |
| 44 | Panel | `PANEL` | Navigation & Layout |
| 45 | HTML | `HTML` | Navigation & Layout |
| 46 | Image | `IMAGE_VIEWER` | Media |
| 47 | Video | `VIDEO_VIEWER` | Media |
| 48 | PDF Viewer | `PDF_VIEWER` | Media |

### Choice-type elements (require `options`)

Elements that must have at least one option defined: `DROPDOWN`, `RADIO_BOX`, `MULTI_CHOICE` (Check Box), `MULTI_SELECT`, `PICTURE_CHOICE`, `OPTION_SCALE`

---

## 14. Permission Reference

| Permission Key | Description | UI Behavior If Absent |
|----------------|-------------|----------------------|
| `template.view` | View template list and open builder in read-only mode | Hide entire Templates section |
| `template.create` | Create new templates | Hide "New Template" button |
| `template.edit` | Edit template metadata and form structure in the builder | Builder is read-only; all add/drag/config controls hidden |
| `template.duplicate` | Duplicate an existing template | Hide "Duplicate" action |
| `template.delete` | Soft-delete a template | Hide "Delete" action |

---

## 15. Non-Functional Requirements

| # | Requirement |
|---|-------------|
| NFR-01 | All create, edit, duplicate, and delete actions must be recorded in the audit log with the acting user's ID and timestamp. |
| NFR-02 | The element palette must load all 49 base elements once on builder open. The response is cached client-side for the session — no re-fetching on every interaction. |
| NFR-03 | Drag-and-drop interactions must be smooth. Drop operations call the API asynchronously — the UI updates optimistically and reverts on error. |
| NFR-04 | The `GET /api/templates/<id>` detail endpoint returns the full nested structure (steps + panels + elements + options + values) in a single response to avoid waterfall requests on builder load. |
| NFR-05 | `order_number` values are Floats. They are stored and compared as floating-point numbers. UI should never display raw `order_number` values to users. |
| NFR-06 | Deleting a step cascades through panels → elements → submission values in the correct order to avoid FK constraint violations. |
| NFR-07 | Template deletion is blocked if `core_form_submissionss` rows reference the template. The API returns a `CONFLICT` response; the UI shows an explanatory message. |
| NFR-08 | The builder must handle both `single_form` and `multi_step_form` in the same component. The step tab row is conditionally rendered based on `template.type`. |
| NFR-09 | `input_group` element creation is atomic — the parent group element and all its sub-elements must be created in a single transaction. |
| NFR-10 | Element configuration changes (options, values, labels) are applied via explicit save, not auto-saved on keystroke. |

---

## 16. Resolved Decisions

| # | Question | Decision |
|---|----------|----------|
| RD-01 | Can template `type` be changed after creation? | No. Type is locked after creation. Changing it would break all `step_id` references. |
| RD-02 | Where is `columns_per_row` stored? | Not on the panel model — it is derived from element `column_size` values. The panel header shows a quick-select that sets the default `column_size` for new elements. |
| RD-03 | How is reordering done without renumbering all rows? | Float midpoint formula. Moving between positions only updates one record. |
| RD-04 | Can elements be placed directly on the canvas outside a panel? | No. Elements must always be inside a panel. |
| RD-05 | How do `input_group` elements (Date Range, Location) work? | They are dragged as a single palette card. On drop, the system creates the parent group element + all sub-elements with `parent_id` set. |
| RD-06 | Is there auto-save in the builder? | No. All changes are saved explicitly by the user. |
| RD-07 | What happens when a panel is deleted? | All elements in the panel are deleted, and all submission values for those elements are deleted (cascade). |
| RD-08 | What is the `value` field on elements used for? | For `display` elements: the visible content (heading text, HTML, etc.). For `input_individual` elements: the default/pre-filled value. Stored in `core_form_display_element_values`. |
| RD-09 | Can a `display` element be marked required? | No. `display` elements (`HEADING`, `DIVIDER`, `HTML`, etc.) do not support `is_required`, options, or placeholder. |
| RD-10 | What is `column_size`? | An integer (1–12) stored per element. Determines how many columns the element spans in the panel's grid row. Controls visual layout width. |

---

## 17. Out of Scope

- Form submissions and submission data storage. The builder only defines the structure; submissions are handled by the consuming module (CRM, Policy, Claims).
- Conditional logic or branching between elements or steps (e.g. "show element B only if element A = Yes").
- Theming or visual styling of form elements beyond layout (column size, order, label).
- Importing or exporting templates in external formats (e.g. JSON, CSV).
- Template versioning or rollback to a previous form structure.
- Real-time collaborative editing of a template by multiple users.
- Preview mode for how the form looks to end users (out of scope for the builder itself — handled by the consuming module).

---

*Document prepared from codebase analysis of `template_controller.py`, `form_controller.py`, `seed_core_form_elements.py`, and model definitions. Version 2.0. Subject to revision as further implementation details are clarified.*

## Task Status

| Component | Status | Description |
|-----------|--------|-------------|
| Backend Models | Completed | Implementation of 8 core models for template builder. |
| Seeding | Completed | Seeded 49 base elements via management command. |
| API Controllers | Completed | Comprehensive CRUD endpoints for templates, steps, panels, and elements. |
| Frontend UI | Completed | Premium Template List and Form Builder with drag-and-drop. |
