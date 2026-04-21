# Service Provider Management — Frontend Tasks

**Module:** Core
**Feature:** Service Provider Management
**Stack:** Next.js / React
**Version:** 1.0

---

## Summary

| Area | Task Count |
|---|---|
| Pages / Screens | 4 |
| Components | 12 |
| API Integration | 9 |
| State & Logic | 6 |
| Validation | 5 |

---

## SECTION 1 — Pages / Screens

---

### TASK FE-01 — Service Provider List Page

**Route:** `/service-providers`
**Permission Gate:** `service_provider.view`

**What to build:**
- Page layout with title "Service Providers" and a top-right "Add New Partner" button (shown only if user has `service_provider.create` permission)
- Paginated data table with the following columns:
  - Logo (avatar/thumbnail)
  - Partner Name
  - Email
  - Contact Number
  - Primary Contact Name
  - Actions column: View, Edit, Duplicate, Delete (each button shown only if user has the respective permission)
- Search bar above the table — searches by partner name and email (debounced, fires after 300ms)
- Empty state UI when no results are found
- Loading skeleton while data is fetching
- Soft-deleted records must never appear in this list

**Action behaviours:**
- **View** → navigates to `/service-providers/{id}`
- **Edit** → navigates to `/service-providers/{id}/edit`
- **Duplicate** → triggers confirmation modal → calls duplicate API → on success, navigates to the new record's edit page or shows a success toast
- **Delete** → triggers confirmation modal ("Are you sure you want to delete {Partner Name}? This action cannot be undone.") → calls soft-delete API → removes row from list on success

---

### TASK FE-02 — Create Service Provider Page

**Route:** `/service-providers/create`
**Permission Gate:** `service_provider.create`

**What to build:**
- Multi-section form page with three clearly labelled sections (tabs or stacked card layout):
  1. General Information
  2. Contact Persons
  3. Bank Account Info
- "Save" and "Cancel" buttons in the page footer
- On successful save → redirect to the detail view of the newly created service provider
- On cancel → navigate back to the list page with a confirmation prompt if the form has unsaved changes

**Section 1 — General Information fields:**

| Field | Type | Required |
|---|---|---|
| Logo | Image upload (JPG/PNG, max 5MB) | No |
| Partner Name | Text input | Yes |
| Email | Email input | Yes |
| Contact Number | Country code dropdown + number input | Yes |
| Fax Number | Text input | No |
| Address | Textarea | Yes |
| Website | URL input | No |

**Section 2 — Contact Persons fields:**
- Renders a dynamic list of contact blocks
- "Add Contact" button appends a new empty contact block to the list
- Each contact block contains:

| Field | Type | Required |
|---|---|---|
| Contact Type | Single-select: Primary / Secondary | Yes |
| Salutation | Single-select: Mr., Mrs., Ms., Miss., Dr., Prof. | Yes |
| Contact Person Name | Text input | Yes |
| Role | Text input | No |
| Email | Email input | No |
| Contact Number | Country code dropdown + number input | Yes |
| Remarks | Textarea | No |

- Each contact block has a "Remove" button (icon button, top-right of the block)
- **Primary demotion warning:** If user selects "Primary" as contact type and a Primary contact already exists in the list, show an inline warning: *"Setting this contact as Primary will demote the existing Primary contact to Secondary."*

**Section 3 — Bank Account Info fields:**

| Field | Type | Required |
|---|---|---|
| Account Holder Name | Text input | No |
| Bank Name | Text input | No |
| Account Number | Text input | No |
| Bank Branch | Text input | No |
| IBAN / Swift Code | Text input | No |
| Payment Gateway URL | URL input | No |

---

### TASK FE-03 — Service Provider Detail Page

**Route:** `/service-providers/{id}`
**Permission Gate:** `service_provider.view`

**What to build:**
- Read-only display of all three sections (General Info, Contact Persons, Bank Account Info)
- Top-right action buttons: Edit, Duplicate, Delete (permission-gated)
- Logo displayed as an image (using the presigned URL returned by the API)
- **Contacts section:**
  - Lists all contacts for this service provider
  - Primary contact has a distinct "Primary" badge (e.g. coloured chip)
  - Secondary contacts listed below with "Secondary" badge
  - "Add Contact" button visible if user has `service_provider.edit` permission — opens the Add Contact modal (see TASK FE-07)
  - Edit and Remove action per contact row (permission-gated to `service_provider.edit`)
- **Insurer Products section** (at the bottom of the page):
  - Section heading: "Insurer Products"
  - Search input to filter by product name (fires against the insurer products sub-resource API)
  - Table columns: Product Name (link to insurer product detail), Risk Type, Coverage Level, Currency, Last Update Date
  - Empty state: "No insurer products linked to this service provider."
  - Paginated
  - Only shows active (non-soft-deleted) insurer products

---

### TASK FE-04 — Edit Service Provider Page

**Route:** `/service-providers/{id}/edit`
**Permission Gate:** `service_provider.edit`

**What to build:**
- Same layout and field structure as the Create page (FE-02)
- All fields pre-populated with existing data fetched from the API
- Existing contacts displayed in the contacts list, each with Edit and Remove buttons
- Logo preview shown if a logo was previously uploaded; user can replace it by uploading a new file
- "Save Changes" and "Cancel" buttons in the footer
- On successful save → redirect to the detail view
- Soft-deleted service providers must redirect to a 404/not-found page if accessed directly by URL

---

## SECTION 2 — Components

---

### TASK FE-05 — LogoUpload Component

**Reusable component for logo upload**

- Displays a dashed upload area with icon and "Upload Logo" label
- Accepts drag-and-drop or click-to-browse
- Client-side validation before upload:
  - Only JPG and PNG accepted (reject other types with an inline error)
  - Max file size: 5MB (reject with inline error)
- Shows a preview thumbnail after file selection
- "Remove" button to clear the selected file
- On form submit, the parent form reads the File object from this component and sends it as multipart

---

### TASK FE-06 — CountryCodePhoneInput Component

**Reusable phone number input with country code selector**

- Two-part input: left side is a searchable dropdown of country dial codes with flag icons; right side is a plain number input
- Country code dropdown shows: flag emoji + dial code (e.g. 🇱🇰 +94)
- Searchable by country name or dial code
- Value model: `{ country_code: "+94", number: "771234567" }`
- Validation: both parts required together when the field is marked as required
- Used in: General Information (provider contact number), each Contact Person block

---

### TASK FE-07 — Add / Edit Contact Modal

**Modal for adding a new contact or editing an existing contact on the detail page**

- Opens as a modal dialog (not full page navigation)
- Contains all contact person fields (Contact Type, Salutation, Name, Role, Email, Contact Number, Remarks)
- On save:
  - If adding → calls `POST /api/service-providers/{id}/contacts/`
  - If editing → calls `PUT /api/service-providers/{id}/contacts/{contact_id}/`
- Shows primary demotion warning inline if Contact Type is set to "Primary" and a Primary already exists
- Validates all required fields before allowing submit
- On success → closes modal and refreshes the contacts list without a full page reload

---

### TASK FE-08 — ContactPersonBlock Component

**Inline contact block used inside the Create and Edit forms**

- Renders all contact fields inside a card/panel
- "Remove" icon button in the top-right corner of the block
- Receives index and value from parent form state
- Emits onChange (field-level updates) and onRemove events to parent
- Displays inline field-level validation errors

---

### TASK FE-09 — ServiceProviderFormSections Component

**Wrapper that manages the three-section form layout**

- Handles the tab or accordion layout for General Info / Contact Persons / Bank Account Info
- Shows section-level error indicators (e.g. red dot on tab) if any field in that section has a validation error
- Manages scroll-to-error behaviour on submit

---

### TASK FE-10 — DeleteConfirmationModal Component

**Reusable soft-delete confirmation modal**

- Props: `entityName`, `onConfirm`, `onCancel`, `isLoading`
- Displays: "Are you sure you want to delete {entityName}? This action cannot be undone."
- Confirm button shows a spinner while `isLoading` is true
- Used for both service provider delete and contact remove actions

---

### TASK FE-11 — DuplicateConfirmationModal Component

**Confirmation modal before duplicating a service provider**

- Displays: "This will create an independent copy of {Partner Name}. Continue?"
- On confirm → calls duplicate API → on success, navigates to the new record
- Shows loading state on the confirm button during the API call

---

### TASK FE-12 — InsurerProductsMiniList Component

**Read-only insurer products list shown inside the service provider detail page**

- Accepts `serviceProviderId` as prop
- Fetches from `/api/service-providers/{id}/insurer-products/` on mount
- Search input — fires a new fetch with `?search=` query param
- Paginated table: Product Name (link), Risk Type, Coverage Level, Currency, Last Update Date
- Loading skeleton and empty state included

---

### TASK FE-13 — PrimaryContactBadge Component

**Small visual badge to indicate contact type**

- `Primary` → green/blue filled chip
- `Secondary` → grey outlined chip
- Used in the contacts list inside the detail and edit pages

---

## SECTION 3 — API Integration (Service Layer)

---

### TASK FE-14 — List Service Providers

```typescript
GET /api/service-providers/?search={query}&page={n}&page_size=20
```
- Called on page load and on search input change (debounced)
- Returns paginated list: `{ results, count, next, previous }`

---

### TASK FE-15 — Create Service Provider

```typescript
POST /api/service-providers/
Content-Type: multipart/form-data
```
- Sends all three sections as `multipart/form-data`
- Logo file (if selected) sent as a `File` object under the `logo` key
- Nested objects (`contacts[]`, `bank_account`) serialized appropriately for multipart
- On `201` → redirect to detail page

---

### TASK FE-16 — Get Service Provider Detail

```typescript
GET /api/service-providers/{id}/
```
- Called on detail and edit page mount
- Returns full record including `logo_url` (presigned S3 URL), contacts array, bank account object

---

### TASK FE-17 — Update Service Provider

```typescript
PUT /api/service-providers/{id}/
Content-Type: multipart/form-data
```
- Same payload shape as create
- If no new logo file is selected, do not send the `logo` field (backend keeps existing key)
- On `200` → redirect to detail page

---

### TASK FE-18 — Soft-Delete Service Provider

```typescript
DELETE /api/service-providers/{id}/
```
- Called from delete confirmation modal
- On `204` → remove item from list state / redirect to list if on detail page

---

### TASK FE-19 — Duplicate Service Provider

```typescript
POST /api/service-providers/{id}/duplicate/
```
- No request body
- On `201` → navigate to the new record returned in the response

---

### TASK FE-20 — Contact Sub-resource (Add / Edit / Delete)

```typescript
POST   /api/service-providers/{id}/contacts/
PUT    /api/service-providers/{id}/contacts/{contact_id}/
DELETE /api/service-providers/{id}/contacts/{contact_id}/
```
- All three called from the Add/Edit Contact Modal and the contact remove button on the detail page
- On success → refetch contacts list for this service provider

---

### TASK FE-21 — Get Insurer Products for Service Provider

```typescript
GET /api/service-providers/{id}/insurer-products/?search={query}&page={n}&page_size=10
```
- Called from the InsurerProductsMiniList component
- Refreshes on search input change

---

## SECTION 4 — State & Form Management

---

### TASK FE-22 — Create / Edit Form State

- Use `react-hook-form` (or equivalent) for form state management
- `contacts` field is a dynamic array managed via `useFieldArray`
- Form default values populated from API on edit mode
- On submit, build a `FormData` object:
  - Append scalar fields directly
  - Append logo as a `File` if a new one was selected
  - Serialize `contacts` array and `bank_account` object (flatten into indexed keys for multipart, e.g. `contacts[0][name]`)
- Track `isDirty` state to prompt confirmation on unsaved navigation

---

### TASK FE-23 — Primary Contact Demotion State

- In the `contacts` field array, maintain a check: when a contact's `contact_type` is changed to "Primary", find any existing contact in the array already set to "Primary" and change it to "Secondary"
- Show inline warning before auto-demoting
- This mirrors the backend behaviour client-side for immediate visual feedback

---

### TASK FE-24 — Permission-Gated UI

- Wrap action buttons (Add, Edit, Duplicate, Delete) with a `PermissionGuard` component or hook
- Permission keys to check: `service_provider.create`, `service_provider.view`, `service_provider.edit`, `service_provider.duplicate`, `service_provider.delete`
- Buttons not permitted are hidden (not just disabled)

---

### TASK FE-25 — Logo Preview & Upload State

- Maintain local state: `{ file: File | null, previewUrl: string | null, existingUrl: string | null }`
- `existingUrl` populated from `logo_url` returned by API on edit mode
- `previewUrl` generated via `URL.createObjectURL(file)` when a new file is selected
- On form submit, only include `logo` in the payload if `file` is not null

---

### TASK FE-26 — Search Debounce

- Debounce the search input on the list page by 300ms before firing the API call
- Debounce the insurer products search inside the detail page by 300ms as well
- Reset pagination to page 1 on every new search query

---

### TASK FE-27 — Toast / Notification Feedback

- Success toasts for: Create, Update, Duplicate, Delete, Add Contact, Edit Contact, Remove Contact
- Error toasts for: any API failure (use the error message from the API response if available, fallback to generic message)

---

## SECTION 5 — Validation Rules (Client-Side)

---

### TASK FE-28 — General Information Validation

| Field | Rule |
|---|---|
| Partner Name | Required |
| Email | Required, valid email format |
| Contact Number | Required, country code must be selected, number must not be empty |
| Address | Required |
| Website | Optional, but if provided must be a valid URL format |
| Logo | Optional, but if provided must be JPG/PNG and under 5MB |

---

### TASK FE-29 — Contact Person Validation

| Field | Rule |
|---|---|
| Contact Type | Required |
| Salutation | Required |
| Contact Person Name | Required |
| Contact Number | Required, country code must be selected |
| Email | Optional, but if provided must be valid email format |

---

### TASK FE-30 — Bank Account Validation

| Field | Rule |
|---|---|
| Payment Gateway URL | Optional, but if provided must be a valid URL format |
| All other fields | Optional, free text |

---

### TASK FE-31 — Form-Level Submit Validation

- Block submit if any required field across any section is empty
- Scroll to the first error field automatically
- Highlight the section tab/header in red if it contains errors

---

### TASK FE-32 — Duplicate Name Awareness

- Not a hard block on the frontend — the backend returns a `400` with a field error if the name is already taken
- Display the backend error message inline under the Partner Name field on conflict

---

## SECTION 6 — Routing Summary

| Route | Page | Guard |
|---|---|---|
| `/service-providers` | List | `service_provider.view` |
| `/service-providers/create` | Create | `service_provider.create` |
| `/service-providers/{id}` | Detail | `service_provider.view` |
| `/service-providers/{id}/edit` | Edit | `service_provider.edit` |

---

## Notes

- Always use the `logo_url` field (presigned S3 URL) for displaying logos — never store or cache the URL locally as it expires.
- Do not attempt to upload the logo directly to S3 from the frontend. Send the file to the backend API endpoint; the backend handles the S3 upload.
- Contacts are managed as a sub-resource — on the create form they are bundled in the main payload; on the detail/edit page after creation they are managed via the contacts sub-resource endpoints independently.

---

## Implementation Status

| Task | Status | Date |
|---|---|---|
| FE-01 Service Provider List Page | ✅ Done | 2026-03-23 |
| FE-02 Create Service Provider Page | ✅ Done | 2026-03-23 |
| FE-04 Edit Service Provider Page | ✅ Done | 2026-03-23 |
| FE-14 List Service Providers API | ✅ Done | 2026-03-23 |
| FE-15 Create Service Provider API | ✅ Done | 2026-03-23 |
| FE-16 Get Service Provider Detail API | ✅ Done | 2026-03-23 |
| FE-17 Update Service Provider API | ✅ Done | 2026-03-23 |
| FE-18 Soft-Delete Service Provider API | ✅ Done | 2026-03-23 |
| FE-22 Create / Edit Form State | ✅ Done | 2026-03-23 |
| FE-26 Search Debounce | ✅ Done | 2026-03-23 |
| FE-28 General Info Validation | ✅ Done | 2026-03-23 |
| FE-29 Contact Person Validation | ✅ Done | 2026-03-23 |
| FE-30 Bank Account Validation | ✅ Done | 2026-03-23 |
| FE-05 Logo Upload Component | ✅ Done | 2026-03-23 |
| Navigation (Sidebar) | ✅ Done | 2026-03-23 |
| Other tasks (Detail page, Modals, Permissions, etc.) | ⏳ Pending | — |
