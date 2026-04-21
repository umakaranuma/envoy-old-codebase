# UI Tasks: Template Management — Requirements Document

## 3.1 Create Template
- [ ] Build form component for creating record.
- [ ] Implement form validation rules.
- [ ] Integrate POST API and handle success/error states.

- [ ] Ensure UI supports: Users can create a new template by providing a title, description, and selecting a type (`single_step_form` or `multi_step_form`).
- [ ] Ensure UI supports: Title is a required field.
- [ ] Ensure UI supports: Description is an optional field.
- [ ] Ensure UI supports: Type (`single_step_form` or `multi_step_form`) is required and must be selected at creation time.
- [ ] Ensure UI supports: The form type cannot be changed after the template is created.
- [ ] Ensure UI supports: Once the template metadata is saved, the user is taken into the form builder to design the form structure.
## 3.2 Form Builder — Structure
- [ ] Implement UI for 3.2 Form Builder — Structure.

- [ ] Ensure UI supports: For `single_step_form`, the builder presents a single page canvas.
- [ ] Ensure UI supports: For `multi_step_form`, the builder presents multiple step tabs — each step is an independent page canvas.
- [ ] Ensure UI supports: Users can add, rename, reorder, and remove steps in a `multi_step_form`.
- [ ] Ensure UI supports: All form elements must be placed inside a **panel**. Elements cannot be placed directly on the page canvas outside of a panel.
- [ ] Ensure UI supports: Users can add one or more panels to a page or step.
- [ ] Ensure UI supports: Panels can be reordered within the page by drag-and-drop.
- [ ] Ensure UI supports: Each panel has a **row layout setting** — the user can configure how many elements appear per row within that panel.
- [ ] Ensure UI supports: Panels can be named/labelled.
## 3.3 Form Builder — Element Palette
- [ ] Implement UI for 3.3 Form Builder — Element Palette.

- [ ] Ensure UI supports: The form builder displays a grouped element palette from which users can drag elements into panels.
- [ ] Ensure UI supports: Elements are organized into the following groups in the palette: Frequently Used, Text, Choices, Date & Time, Contact Info, Numbers, Rating & Ranking, Miscellaneous, Navigation & Layout, Display Text, and Media.
- [ ] Ensure UI supports: Each element in the palette belongs to a category: `input_individual`, `input_group`, or `display`.
- [ ] Ensure UI supports: `input_group` elements (Date Range, Location Coordinate) expand into their sub-elements when placed in a panel.
## 3.4 Form Builder — Element Configuration
- [ ] Implement UI for 3.4 Form Builder — Element Configuration.

- [ ] Ensure UI supports: Users can set the **label / name** for any element.
- [ ] Ensure UI supports: Users can mark any `input_individual` or `input_group` element as **required** or **not required**.
- [ ] Ensure UI supports: Users can set a **placeholder text** for applicable input elements.
- [ ] Ensure UI supports: Users can set a **default value** for applicable input elements.
- [ ] Ensure UI supports: For choice-type elements (Dropdown, Radio Box, Check Box, Multiple Choice, Multiple Select, Picture Choice, Option Scale), users can define the **list of options** available for selection.
- [ ] Ensure UI supports: Options for choice-type elements can be added, edited, reordered, and removed.
- [ ] Ensure UI supports: `display` category elements (Heading, Paragraph, Banner, Divider, HTML, Image, Video, PDF Viewer, Line Break, Section Collapse) do not support required, placeholder, or default value settings.
- [ ] Ensure UI supports: Elements within a panel can be reordered by drag-and-drop.
- [ ] Ensure UI supports: Elements can be removed from a panel individually.
## 3.5 Available Elements Reference
- [ ] Implement UI for 3.5 Available Elements Reference.

## 3.6 View Templates
- [ ] Build data table/list view component.
- [ ] Implement search/filtering/pagination UI.
- [ ] fetch data from GET API.

- [ ] Ensure UI supports: Users can view a list of all active templates showing title, description, and type.
- [ ] Ensure UI supports: The template list supports search by title.
- [ ] Ensure UI supports: Users can filter the template list by type (`single_step_form` / `multi_step_form`).
- [ ] Ensure UI supports: Users can open a template to view its full form structure in read-only mode.
- [ ] Ensure UI supports: Soft-deleted templates are hidden from the default list view.
## 3.7 Edit Template
- [ ] Build edit form component.
- [ ] Integrate PUT/PATCH API and handle success/error states.

- [ ] Ensure UI supports: Users can edit the title and description of a saved template.
- [ ] Ensure UI supports: The template type cannot be changed after creation.
- [ ] Ensure UI supports: Users can edit the form structure — add/remove/reorder panels, add/remove/reorder/configure elements, and add/remove/reorder steps (for `multi_step_form`).
- [ ] Ensure UI supports: All edits are saved explicitly by the user (not auto-saved).
## 3.8 Duplicate Template
- [ ] Implement UI for 3.8 Duplicate Template.

- [ ] Ensure UI supports: Users can duplicate an existing template to create an independent copy.
- [ ] Ensure UI supports: The duplicated template copies all metadata (title with a copy suffix, description, type) and the full form structure.
- [ ] Ensure UI supports: The duplicate is an independent record — changes to it do not affect the original.
## 3.9 Delete Template
- [ ] Build deletion confirmation modal.
- [ ] Integrate DELETE API and handle success/error states.

- [ ] Ensure UI supports: Users can soft-delete a template.
- [ ] Ensure UI supports: Soft-deleted templates are deactivated and hidden from the default list but retained in the system.
- [ ] Ensure UI supports: Hard deletion is not supported.
- [ ] Ensure UI supports: All create, edit, duplicate, and delete actions must be recorded in the audit log with the acting user and timestamp.
- [ ] Ensure UI supports: The form builder must support drag-and-drop interactions with smooth reordering of panels and elements.
- [ ] Ensure UI supports: Template form structures must be stored in a way that preserves element order, panel layout, and all element configuration properties.
- [ ] Ensure UI supports: Soft-deleted templates must be retained indefinitely for audit purposes.
- [ ] Ensure UI supports: The element palette must load all available elements and groups from the backend elements API.

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Completed | Antigravity | Implemented Template Management and Form Builder. |
| Testing | Completed | Antigravity | Manual verification of builder functionality. |
