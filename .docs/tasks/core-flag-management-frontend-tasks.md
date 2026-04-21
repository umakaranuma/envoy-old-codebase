# Flag Management - Frontend Tasks

## Pages & Navigation
- [ ] Add `Flags` link to sidebar if applicable.
- [ ] Create `Flags` overview page under `envoy_core_ui/app/a/flags/page.tsx` (or similar).

## State & API Services
- [ ] Create `flag.service.ts` or equivalent to interface with backend CRUD.
  - `getFlags` (with search)
  - `createFlag`
  - `updateFlag`
  - `deleteFlag`

## UI Components
- [ ] List View:
  - Data table with search functionality.
  - Columns: Name, Description, Color (rendered swatch), Actions.
  - Loading State using `<TLoader />`.
  - Empty state using `EmptyState`.
- [ ] Form / Modal (Create & Edit):
  - Fields: Label (Name - string), Description (text), Color selector (color picker).
  - Validation using Zod.
- [ ] Delete logic:
  - `PopConfirm` wrapped delete action button.
