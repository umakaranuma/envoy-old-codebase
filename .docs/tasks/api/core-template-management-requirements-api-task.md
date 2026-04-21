# API Tasks: Template Management — Requirements Document

## 3.1 Create Template
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

- [ ] Ensure API supports: Users can create a new template by providing a title, description, and selecting a type (`single_step_form` or `multi_step_form`).
- [ ] Ensure API supports: Title is a required field.
- [ ] Ensure API supports: Description is an optional field.
- [ ] Ensure API supports: Type (`single_step_form` or `multi_step_form`) is required and must be selected at creation time.
- [ ] Ensure API supports: The form type cannot be changed after the template is created.
- [ ] Ensure API supports: Once the template metadata is saved, the user is taken into the form builder to design the form structure.
## 3.2 Form Builder — Structure
- [ ] Implement API logic for 3.2 Form Builder — Structure.

- [ ] Ensure API supports: For `single_step_form`, the builder presents a single page canvas.
- [ ] Ensure API supports: For `multi_step_form`, the builder presents multiple step tabs — each step is an independent page canvas.
- [ ] Ensure API supports: Users can add, rename, reorder, and remove steps in a `multi_step_form`.
- [ ] Ensure API supports: All form elements must be placed inside a **panel**. Elements cannot be placed directly on the page canvas outside of a panel.
- [ ] Ensure API supports: Users can add one or more panels to a page or step.
- [ ] Ensure API supports: Panels can be reordered within the page by drag-and-drop.
- [ ] Ensure API supports: Each panel has a **row layout setting** — the user can configure how many elements appear per row within that panel.
- [ ] Ensure API supports: Panels can be named/labelled.
## 3.3 Form Builder — Element Palette
- [ ] Implement API logic for 3.3 Form Builder — Element Palette.

- [ ] Ensure API supports: The form builder displays a grouped element palette from which users can drag elements into panels.
- [ ] Ensure API supports: Elements are organized into the following groups in the palette: Frequently Used, Text, Choices, Date & Time, Contact Info, Numbers, Rating & Ranking, Miscellaneous, Navigation & Layout, Display Text, and Media.
- [ ] Ensure API supports: Each element in the palette belongs to a category: `input_individual`, `input_group`, or `display`.
- [ ] Ensure API supports: `input_group` elements (Date Range, Location Coordinate) expand into their sub-elements when placed in a panel.
## 3.4 Form Builder — Element Configuration
- [ ] Implement API logic for 3.4 Form Builder — Element Configuration.

- [ ] Ensure API supports: Users can set the **label / name** for any element.
- [ ] Ensure API supports: Users can mark any `input_individual` or `input_group` element as **required** or **not required**.
- [ ] Ensure API supports: Users can set a **placeholder text** for applicable input elements.
- [ ] Ensure API supports: Users can set a **default value** for applicable input elements.
- [ ] Ensure API supports: For choice-type elements (Dropdown, Radio Box, Check Box, Multiple Choice, Multiple Select, Picture Choice, Option Scale), users can define the **list of options** available for selection.
- [ ] Ensure API supports: Options for choice-type elements can be added, edited, reordered, and removed.
- [ ] Ensure API supports: `display` category elements (Heading, Paragraph, Banner, Divider, HTML, Image, Video, PDF Viewer, Line Break, Section Collapse) do not support required, placeholder, or default value settings.
- [ ] Ensure API supports: Elements within a panel can be reordered by drag-and-drop.
- [ ] Ensure API supports: Elements can be removed from a panel individually.
## 3.5 Available Elements Reference
- [ ] Implement API logic for 3.5 Available Elements Reference.

## 3.6 View Templates
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

- [ ] Ensure API supports: Users can view a list of all active templates showing title, description, and type.
- [ ] Ensure API supports: The template list supports search by title.
- [ ] Ensure API supports: Users can filter the template list by type (`single_step_form` / `multi_step_form`).
- [ ] Ensure API supports: Users can open a template to view its full form structure in read-only mode.
- [ ] Ensure API supports: Soft-deleted templates are hidden from the default list view.
## 3.7 Edit Template
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

- [ ] Ensure API supports: Users can edit the title and description of a saved template.
- [ ] Ensure API supports: The template type cannot be changed after creation.
- [ ] Ensure API supports: Users can edit the form structure — add/remove/reorder panels, add/remove/reorder/configure elements, and add/remove/reorder steps (for `multi_step_form`).
- [ ] Ensure API supports: All edits are saved explicitly by the user (not auto-saved).
## 3.8 Duplicate Template
- [ ] Implement API logic for 3.8 Duplicate Template.

- [ ] Ensure API supports: Users can duplicate an existing template to create an independent copy.
- [ ] Ensure API supports: The duplicated template copies all metadata (title with a copy suffix, description, type) and the full form structure.
- [ ] Ensure API supports: The duplicate is an independent record — changes to it do not affect the original.
## 3.9 Delete Template
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Ensure API supports: Users can soft-delete a template.
- [ ] Ensure API supports: Soft-deleted templates are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure API supports: Hard deletion is not supported.
- [ ] Register permission: `template.create` (Create new templates and build their form structure)
- [ ] Register permission: `template.view` (View the template list and individual template details)
- [ ] Register permission: `template.edit` (Edit template metadata and form structure)
- [ ] Register permission: `template.duplicate` (Duplicate an existing template)
- [ ] Register permission: `template.delete` (Soft-delete a template)
- [ ] Ensure API supports: All create, edit, duplicate, and delete actions must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure API supports: The form builder must support drag-and-drop interactions with smooth reordering of panels and elements.
- [ ] Ensure API supports: Template form structures must be stored in a way that preserves element order, panel layout, and all element configuration properties.
- [ ] Ensure API supports: Soft-deleted templates must be retained indefinitely for audit purposes.
- [ ] Ensure API supports: The element palette must load all available elements and groups from the backend elements API.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
