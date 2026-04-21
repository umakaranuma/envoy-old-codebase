# Issue: Standardize API Pagination, Search, Sorting & Per-Page Controls

**Status:** Closed (Resolved)  
**Priority:** High  
**Scope:** System-wide (envoy_core)  
**Raised:** 2026-03-31

---

## Problem Statement

Across the system, list API calls are inconsistent:

- Some use **hardcoded large limits** (`limit=1000`, `limit=50`) to simulate "get all" — this is dangerous for performance at scale.
- Many tables **do not support per-page row control** from the UI — the user cannot choose how many rows to display.
- Search is sometimes done **client-side** on a full fetched list instead of being passed to the server on every keystroke.
- Some endpoints **lack sort_by / sort_dir** support entirely.
- The `filters={}` parameter is missing from most client calls.

---

## Target API Format

Every list endpoint must support the following standardised query string:

```
/api/{resource}?search=h&page=1&limit=10&sort_by=name&sort_dir=asc&filters=%7B%7D
```

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Free-text search across indexed columns. Debounced on frontend (300ms). |
| `page` | int | Current page number (1-indexed). |
| `limit` | int | Rows per page. Must come from user-selected control in UI. |
| `sort_by` | string | Column name to sort by. Optional. |
| `sort_dir` | `asc` \| `desc` | Sort direction. Optional. |
| `filters` | JSON (URL-encoded) | Key-value filter object for column-specific filtering. |

---

## Affected Modules & Tables (envoy_core_ui)

### 1. Contacts — `/api/contacts`
**Backend file:** `contact_controller.py → contacts_view`  
**Client file:** `contacts/_route/api-services/contact.client.ts → getContacts`

**Current state:**
- ✅ Supports `search`, `page`, `limit`, `show_inactive`
- ❌ Missing `sort_by`, `sort_dir`, `filters`
- ❌ UI does `getContacts("", 1, 1000)` to load all contacts for the merge dropdown — needs lazy SearchableDropdown instead
- ❌ No per-page selector in the UI table

**Required changes:**
- Backend: add `sort_by`, `sort_dir` support (allowed: `id`, `name`, `email`)
- Frontend: add per-page selector (`[10, 25, 50]`) in table toolbar — pass as `limit`
- Frontend: search input debounced 300ms → triggers API call on change
- Frontend: remove `getContacts("", 1, 1000)` call; replace merge modal with SearchableDropdown fetcher

---

### 2. Contact Groups — `/api/contact-groups`
**Backend file:** `contact_controller.py → contact_groups_view` (to verify)  
**Client file:** `contacts/_route/api-services/contact.client.ts → getContactGroups`

**Current state:**
- ❌ No pagination — returns all groups
- ❌ No `search`, `sort_by`, `sort_dir`, `filters` support
- ❌ Search is done client-side only (`.filter()`)
- ❌ No per-page selector in the UI table

**Required changes:**
- Backend: update `contact_groups_view` to support all standard params
- Frontend: replace client-side filter with server-side search + pagination
- Frontend: add per-page selector and pagination component

---

### 3. Accounts — `/api/accounts`
**Backend file:** `customer_controller.py → getAll`  
**Client file:** `accounts/_route/api-services/account.client.ts → getAccounts`

**Current state:**
- ✅ Fully compliant — supports `search`, `page`, `limit`, `sort_by`, `sort_dir`, `filters`
- ❌ UI calls `getAccounts(search, undefined, 1, 50)` from dropdowns — fine for small datasets, verify limit is appropriate
- ❌ Per-page selector not confirmed in table toolbar

**Required changes:**
- Frontend: verify per-page selector exists; add if missing

---

### 4. Users / Staff — `/api/users`
**Backend file:** `user_controller.py`  
**Client file:** `users/_route/api-services/user.client.ts → getUsers`

**Current state (to be verified):**
- Status unknown — need to confirm `sort_by`, `sort_dir`, `filters` support
- ❌ Per-page selector existence to be confirmed

**Required changes:**
- Backend: add full standard param support if missing
- Frontend: add per-page selector if missing

---

### 5. Roles — `/api/roles`
**Backend file:** `role_controller.py`  
**Client file:** `roles/_route/api-services/role.client.ts`

**Current state:** Unknown — needs investigation.

**Required changes:**
- Backend: add full standard param support
- Frontend: add per-page selector if table exists

---

### 6. Teams — `/api/teams` or `/api/sales-teams`
**Backend file:** `sales_team_controller.py`  
**Client file:** (to locate)

**Current state:** Unknown — needs investigation.

**Required changes:**
- Backend: add full standard param support
- Frontend: add per-page selector if table exists

---

## UI Pattern — Per-Page Selector

Every table that supports pagination must include a per-page row selector. The control should be placed in the table toolbar, right-aligned.

### Options offered to user:
`[10, 25, 50, 100]` rows per page. Default: `10`.

### UI Component:
```tsx
<select
  value={limit}
  onChange={(e) => { setLimit(Number(e.target.value)); setPage(1); }}
  className="bg-[var(--surface-2)] border border-[var(--border)] rounded-[var(--radius-md)] h-[38px] px-3 text-[13px] outline-none focus:border-[var(--teal)] transition-all"
>
  {[10, 25, 50, 100].map(n => (
    <option key={n} value={n}>{n} / page</option>
  ))}
</select>
```

This value gets passed directly to the API as the `limit` parameter.

---

## Search Debouncing Pattern (Frontend)

Search must NOT fire an API call on every single keypress — it must be debounced:

```ts
// In page component
const [search, setSearch] = useState("");
const [debouncedSearch, setDebouncedSearch] = useState("");

useEffect(() => {
  const timer = setTimeout(() => setDebouncedSearch(search), 300);
  return () => clearTimeout(timer);
}, [search]);

useEffect(() => {
  fetchData(); // uses debouncedSearch
  setPage(1);
}, [debouncedSearch]);
```

The **raw `search` state** binds to the input (instant feedback), while **`debouncedSearch`** triggers the API call.

---

## Backend Pattern (Standard)

All list controllers must follow this pattern:

```python
search_term  = (request.GET.get("search") or "").strip()
page_number  = int(request.GET.get("page") or 1)
page_size    = int(request.GET.get("limit") or 10)
sort_column  = request.GET.get("sort_by") or "id"
sort_direction = (request.GET.get("sort_dir") or "desc").lower()

# Cap page_size to prevent abuse
page_size = min(page_size, 200)

result = QueryBuilderService("table_name") \
    .select(...) \
    .apply_conditions("{}", allowed_filters, search_term, search_columns) \
    .paginate(page_number, page_size, allowed_sorting_columns, sort_column, sort_direction)

return ResponseService.response("SUCCESS", result, "Fetched successfully")
```

---

## Implementation Order

| Priority | Module | Backend | Frontend | Status |
|----------|--------|---------|---------|--------|
| 1 | Contacts | Update sort support | Add per-page, debounced search, fix 1000-limit calls | ✅ Completed |
| 2 | Contact Groups | Add full pagination | Replace client-side filter | ✅ Completed |
| 3 | Users | Verify & update | Add per-page if missing | ✅ Completed |
| 4 | Teams | Verify & update | Add per-page if missing | ✅ Completed |
| 5 | Roles | Verify & update | Add per-page if missing | ✅ Completed |
| 6 | Accounts | Already done ✅ | Verify per-page in toolbar | ✅ Completed |

---

## Notes

- **Dropdowns** (SearchableDropdown fetchers like in AccountHierarchyModal) are exempt from per-page controls — they use a fixed `limit=50` which is acceptable for typeahead use cases.
- **"Get all" calls** (e.g., `getContacts("", 1, 1000)` for merge selectors) must be replaced with either lazy SearchableDropdown patterns or paginated modal lists.
- All new endpoints must be backwards-compatible — existing URL params must still work.
