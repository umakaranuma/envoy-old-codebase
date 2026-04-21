# Template Management — Requirements Document

**Module:** Core
**Feature:** Template Management
**Version:** 1.0
**Status:** Draft

---

## 1. Overview

The Template Management feature allows authorized users to create, manage, and reuse form templates within the system. A template is a reusable form structure built using a drag-and-drop form builder. Templates are typed as either a `single_step_form` or `multi_step_form`, and are composed of panels that contain draggable form elements.

Each element placed in a panel can be individually configured — including its label, required state, placeholder, default value, and options (where applicable). Panels also support layout configuration, such as how many elements appear per row.

This feature is entirely **permission-driven** — any user whose role includes the relevant permissions can perform template management actions.

---

## 2. Key Rules

- A template has three core fields: **title**, **description**, and **type** (`single_step_form` or `multi_step_form`).
- A `single_step_form` has one page; a `multi_step_form` has multiple steps — each step behaves like an independent single page.
- Both form types use **panels** as the structural container — elements must always be placed inside a panel.
- Each panel supports a **row layout setting** — the user can configure how many elements appear per row within the panel.
- Elements are dragged from a grouped element palette and dropped into panels.
- Each element placed in a panel can be configured with: **label/name**, **required or not**, **placeholder text**, **default value**, and **options** (for choice-type elements such as Dropdown, Radio Box, Multiple Choice, etc.).
- Elements are categorized as `input_individual`, `input_group`, or `display`. Display elements (e.g. Heading, Divider, Panel, HTML) do not have required/placeholder/default value settings.
- `input_group` elements (e.g. Date Range, Location Coordinate) contain sub-elements that are configured individually.
- A saved template can be **edited** at any time.
- A template can be **duplicated** to create an independent copy.
- Templates are **soft-deleted** — they are deactivated but not permanently removed.
- Templates have no publish/draft status — they are always live once saved.

---

## 3. Functional Requirements

### 3.1 Create Template

| # | Requirement | Permission |
|---|---|---|
| 3.1.1 | Users can create a new template by providing a title, description, and selecting a type (`single_step_form` or `multi_step_form`). | `template.create` |
| 3.1.2 | Title is a required field. | `template.create` |
| 3.1.3 | Description is an optional field. | `template.create` |
| 3.1.4 | Type (`single_step_form` or `multi_step_form`) is required and must be selected at creation time. | `template.create` |
| 3.1.5 | The form type cannot be changed after the template is created. | — |
| 3.1.6 | Once the template metadata is saved, the user is taken into the form builder to design the form structure. | `template.create` |

---

### 3.2 Form Builder — Structure

| # | Requirement | Permission |
|---|---|---|
| 3.2.1 | For `single_step_form`, the builder presents a single page canvas. | `template.create` / `template.edit` |
| 3.2.2 | For `multi_step_form`, the builder presents multiple step tabs — each step is an independent page canvas. | `template.create` / `template.edit` |
| 3.2.3 | Users can add, rename, reorder, and remove steps in a `multi_step_form`. | `template.create` / `template.edit` |
| 3.2.4 | All form elements must be placed inside a **panel**. Elements cannot be placed directly on the page canvas outside of a panel. | `template.create` / `template.edit` |
| 3.2.5 | Users can add one or more panels to a page or step. | `template.create` / `template.edit` |
| 3.2.6 | Panels can be reordered within the page by drag-and-drop. | `template.create` / `template.edit` |
| 3.2.7 | Each panel has a **row layout setting** — the user can configure how many elements appear per row within that panel. | `template.create` / `template.edit` |
| 3.2.8 | Panels can be named/labelled. | `template.create` / `template.edit` |

---

### 3.3 Form Builder — Element Palette

| # | Requirement | Permission |
|---|---|---|
| 3.3.1 | The form builder displays a grouped element palette from which users can drag elements into panels. | `template.create` / `template.edit` |
| 3.3.2 | Elements are organized into the following groups in the palette: Frequently Used, Text, Choices, Date & Time, Contact Info, Numbers, Rating & Ranking, Miscellaneous, Navigation & Layout, Display Text, and Media. | `template.create` / `template.edit` |
| 3.3.3 | Each element in the palette belongs to a category: `input_individual`, `input_group`, or `display`. | — |
| 3.3.4 | `input_group` elements (Date Range, Location Coordinate) expand into their sub-elements when placed in a panel. | `template.create` / `template.edit` |

---

### 3.4 Form Builder — Element Configuration

After an element is dropped into a panel, the user can configure it via an element settings panel.

| # | Requirement | Permission |
|---|---|---|
| 3.4.1 | Users can set the **label / name** for any element. | `template.create` / `template.edit` |
| 3.4.2 | Users can mark any `input_individual` or `input_group` element as **required** or **not required**. | `template.create` / `template.edit` |
| 3.4.3 | Users can set a **placeholder text** for applicable input elements. | `template.create` / `template.edit` |
| 3.4.4 | Users can set a **default value** for applicable input elements. | `template.create` / `template.edit` |
| 3.4.5 | For choice-type elements (Dropdown, Radio Box, Check Box, Multiple Choice, Multiple Select, Picture Choice, Option Scale), users can define the **list of options** available for selection. | `template.create` / `template.edit` |
| 3.4.6 | Options for choice-type elements can be added, edited, reordered, and removed. | `template.create` / `template.edit` |
| 3.4.7 | `display` category elements (Heading, Paragraph, Banner, Divider, HTML, Image, Video, PDF Viewer, Line Break, Section Collapse) do not support required, placeholder, or default value settings. | — |
| 3.4.8 | Elements within a panel can be reordered by drag-and-drop. | `template.create` / `template.edit` |
| 3.4.9 | Elements can be removed from a panel individually. | `template.create` / `template.edit` |

---

### 3.5 Available Elements Reference

#### Input — Individual (`input_individual`)

| Group | Element Title | Code |
|---|---|---|
| Frequently Used | Short Answer | `SORT_ANSWER` |
| Frequently Used | Email Input | `EMAIL_INPUT` |
| Frequently Used | Multiple Choice | `MULTI_CHOICE` |
| Text | Short Answer | `SORT_ANSWER` |
| Text | Long Answer | `LONG_ANSWER` |
| Choices | Dropdown | `DROPDOWN` |
| Choices | Multiple Select | `MULTI_SELECT` |
| Choices | Picture Choice | `PICTURE_CHOICE` |
| Choices | Check Box | `MULTI_CHOICE` |
| Choices | Radio Box | `RADIO_BOX` |
| Choices | Switch | `SWITCH` |
| Date & Time | Date Picker | `DATE_PICKER` |
| Date & Time | Time Picker | `TIME_PICKER` |
| Date & Time | Date & Time | `DATE_TIME` |
| Contact Info | Email | `EMAIL_INPUT` |
| Contact Info | Phone | `PHONE_INPUT` |
| Contact Info | Address | `ADDRESS` |
| Numbers | Numbers | `NUMBERS` |
| Numbers | Currency | `CURRENCY` |
| Rating & Ranking | Ranking | `RANKING` |
| Rating & Ranking | Star Rating | `STAR_RATING` |
| Rating & Ranking | Slider | `SLIDER` |
| Rating & Ranking | Option Scale | `OPTION_SCALE` |
| Miscellaneous | Password | `PASSWORD` |
| Miscellaneous | URL Input | `URL_INPUT` |
| Miscellaneous | Color Picker | `COLOR_PICKER` |
| Miscellaneous | File Upload | `FILE_UPLOAD` |
| Miscellaneous | Signature | `SIGNATURE` |
| Miscellaneous | Voice Recording | `VOICE_RECORDING` |
| Miscellaneous | Submission Picker | `SUBMISSION_PICKER` |
| Miscellaneous | Captcha | `CAPTCHA` |
| Miscellaneous | Subform | `SUBFORM` |

#### Input — Group (`input_group`)

| Group | Element Title | Code | Sub-elements |
|---|---|---|---|
| Date & Time | Date Range | `DATE_RANGE` | From (`DATE_RANGE_FROM_DATE`), To (`DATE_RANGE_TO_DATE`) |
| Miscellaneous | Location Coordinate | `LOCATION` | Latitude (`LOCATION_LATITUDE`), Longitude (`LOCATION_LONGITUDE`) |

#### Display (`display`)

| Group | Element Title | Code |
|---|---|---|
| Navigation & Layout | Divider | `DIVIDER` |
| Navigation & Layout | Section Collapse | `SECTION_COLLAPSE` |
| Navigation & Layout | Panel | `PANEL` |
| Navigation & Layout | HTML | `HTML` |
| Display Text | Line Break | `LINE_BREAK` |
| Display Text | Heading | `HEADING` |
| Display Text | Paragraph | `PARAGRAPH` |
| Display Text | Banner | `BANNER` |
| Media | Image | `IMAGE_VIEWER` |
| Media | Video | `VIDEO_VIEWER` |
| Media | PDF Viewer | `PDF_VIEWER` |

---

### 3.6 View Templates

| # | Requirement | Permission |
|---|---|---|
| 3.6.1 | Users can view a list of all active templates showing title, description, and type. | `template.view` |
| 3.6.2 | The template list supports search by title. | `template.view` |
| 3.6.3 | Users can filter the template list by type (`single_step_form` / `multi_step_form`). | `template.view` |
| 3.6.4 | Users can open a template to view its full form structure in read-only mode. | `template.view` |
| 3.6.5 | Soft-deleted templates are hidden from the default list view. | `template.view` |

---

### 3.7 Edit Template

| # | Requirement | Permission |
|---|---|---|
| 3.7.1 | Users can edit the title and description of a saved template. | `template.edit` |
| 3.7.2 | The template type cannot be changed after creation. | — |
| 3.7.3 | Users can edit the form structure — add/remove/reorder panels, add/remove/reorder/configure elements, and add/remove/reorder steps (for `multi_step_form`). | `template.edit` |
| 3.7.4 | All edits are saved explicitly by the user (not auto-saved). | `template.edit` |

---

### 3.8 Duplicate Template

| # | Requirement | Permission |
|---|---|---|
| 3.8.1 | Users can duplicate an existing template to create an independent copy. | `template.duplicate` |
| 3.8.2 | The duplicated template copies all metadata (title with a copy suffix, description, type) and the full form structure. | `template.duplicate` |
| 3.8.3 | The duplicate is an independent record — changes to it do not affect the original. | — |

---

### 3.9 Delete Template

| # | Requirement | Permission |
|---|---|---|
| 3.9.1 | Users can soft-delete a template. | `template.delete` |
| 3.9.2 | Soft-deleted templates are deactivated and hidden from the default list but retained in the system. | — |
| 3.9.3 | Hard deletion is not supported. | — |

---

## 4. Permission Reference Table

| Permission Key | Description |
|---|---|
| `template.create` | Create new templates and build their form structure |
| `template.view` | View the template list and individual template details |
| `template.edit` | Edit template metadata and form structure |
| `template.duplicate` | Duplicate an existing template |
| `template.delete` | Soft-delete a template |

---

## 5. Non-Functional Requirements

| # | Requirement |
|---|---|
| 5.1 | All create, edit, duplicate, and delete actions must be recorded in the audit log with the acting user and timestamp. |
| 5.2 | The form builder must support drag-and-drop interactions with smooth reordering of panels and elements. |
| 5.3 | Template form structures must be stored in a way that preserves element order, panel layout, and all element configuration properties. |
| 5.4 | Soft-deleted templates must be retained indefinitely for audit purposes. |
| 5.5 | The element palette must load all available elements and groups from the backend elements API. |

---

## 6. User Stories

| # | As a... | I want to... | So that... |
|---|---|---|---|
| US-01 | Authorized user | Create a template with a title, description, and type | I can define a reusable form structure for use in the system |
| US-02 | Authorized user | Build a form by dragging elements into panels | I can design the form layout visually without writing code |
| US-03 | Authorized user | Configure each element's label, required state, placeholder, default value, and options | I can control exactly how each field behaves in the form |
| US-04 | Authorized user | Set the number of elements per row on a panel | I can control the layout density of the form |
| US-05 | Authorized user | Add multiple steps to a multi-step form | I can break long forms into logical sections across pages |
| US-06 | Authorized user | Edit a saved template | I can update the form structure as requirements change |
| US-07 | Authorized user | Duplicate an existing template | I can reuse a form structure as a starting point without modifying the original |
| US-08 | Authorized user | Soft-delete a template | I can retire unused templates while keeping them for audit purposes |
| US-09 | Authorized user | Search and filter templates by type | I can quickly find the template I need |

---

## 7. Resolved Decisions

| # | Question | Decision |
|---|---|---|
| RD-01 | What fields does a template have? | Title (required), description (optional), and type (required — `single_step_form` or `multi_step_form`). |
| RD-02 | How does multi_step_form differ from single_step_form? | Each step in a multi_step_form behaves like a single-page canvas with panels, identical to a single_step_form page. |
| RD-03 | Can elements be placed directly on the canvas? | No — elements must always be placed inside a panel. |
| RD-04 | What properties can be configured per element? | Label/name, required, placeholder text, default value, and options (for choice-type elements). |
| RD-05 | Can panels control row layout? | Yes — each panel has a setting for how many elements appear per row. |
| RD-06 | Can a template be edited after saving? | Yes — title, description, and full form structure can be edited at any time. |
| RD-07 | Can a template be duplicated? | Yes — duplication creates a fully independent copy of the template and its form structure. |
| RD-08 | What happens when a template is deleted? | Soft delete only — the template is deactivated but not permanently removed. |
| RD-09 | Does a template have a draft/published status? | No — templates are always live once saved; there is no status concept. |

---

## 8. Out of Scope

- Form submissions and submission data storage (handled by the module that uses the template, e.g. CRM, Policy).
- Conditional logic or branching between elements or steps.
- Theming or visual styling of form elements beyond layout configuration.
- Importing or exporting templates in external formats (e.g. JSON export).
- Template versioning or rollback to a previous form structure.

---

*Document prepared based on stakeholder input. Subject to revision as further requirements are clarified.*

---

## Task Status Summary
| Task | Status | Implementation Details |
|---|---|---|
| Fix seeded form elements view and interactivity in UI | Completed | Replaced mock UI elements in FormCanvas with accurate functional controls based on FormPreview logic |
