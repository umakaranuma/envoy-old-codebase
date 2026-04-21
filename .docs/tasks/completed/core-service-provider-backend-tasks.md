# Service Provider Management — Backend / API Tasks

**Module:** Core
**Feature:** Service Provider Management
**Stack:** Django + Django REST Framework
**Version:** 1.0

---

## Summary

| Area | Task Count |
|---|---|
| Models & Migrations | 4 |
| Serializers | 5 |
| Views & Endpoints | 9 |
| Business Logic / Services | 4 |
| Permissions | 2 |
| Audit Logging | 1 |
| URL Configuration | 1 |
| Tests | 5 |

---

## SECTION 1 — Models & Migrations

---

### TASK BE-01 — ServiceProvider Model

**File:** `models.py`

Create the `ServiceProvider` model with the following fields:

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | — | Auto |
| `partner_name` | CharField(255) | Yes | — |
| `email` | EmailField | Yes | — |
| `contact_country_code` | CharField(10) | Yes | e.g. "+94" |
| `contact_number` | CharField(20) | Yes | — |
| `fax_number` | CharField(20) | No | null, blank |
| `address` | TextField | Yes | — |
| `website` | URLField | No | null, blank |
| `logo_key` | CharField(500) | No | S3 object key — NOT the presigned URL |
| `is_active` | BooleanField | — | Default: True |
| `created_by` | FK → User | No | SET_NULL, null=True, related_name="+" |
| `created_at` | DateTimeField | — | auto_now_add=True |
| `updated_at` | DateTimeField | — | auto_now=True |

```
db_table = "service_providers"
```

**Important:** Store `logo_key` (the S3 object key), never the presigned URL. Presigned URLs expire — generate them fresh on every read.

---

### TASK BE-02 — ServiceProviderContact Model

**File:** `models.py`

Create the `ServiceProviderContact` model:

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | — | Auto |
| `service_provider` | FK → ServiceProvider | Yes | CASCADE, related_name="contacts" |
| `contact_type` | CharField(10) | Yes | Choices: `Primary`, `Secondary` |
| `salutation` | CharField(10) | Yes | Choices: Mr., Mrs., Ms., Miss., Dr., Prof. |
| `name` | CharField(255) | Yes | — |
| `role` | CharField(255) | No | null, blank |
| `email` | EmailField | No | null, blank |
| `contact_country_code` | CharField(10) | Yes | — |
| `contact_number` | CharField(20) | Yes | — |
| `remarks` | TextField | No | null, blank |
| `created_at` | DateTimeField | — | auto_now_add=True |

```
db_table = "service_provider_contacts"
```

---

### TASK BE-03 — ServiceProviderBankAccount Model

**File:** `models.py`

Create the `ServiceProviderBankAccount` model:

| Field | Type | Required | Notes |
|---|---|---|---|
| `id` | AutoField (PK) | — | Auto |
| `service_provider` | OneToOneField → ServiceProvider | Yes | CASCADE, related_name="bank_account" |
| `account_holder_name` | CharField(255) | No | null, blank |
| `bank_name` | CharField(255) | No | null, blank |
| `account_number` | CharField(100) | No | null, blank |
| `bank_branch` | CharField(255) | No | null, blank |
| `iban_swift_code` | CharField(100) | No | null, blank |
| `payment_gateway_url` | URLField | No | null, blank |

```
db_table = "service_provider_bank_accounts"
```

---

### TASK BE-04 — Database Migrations

- Generate and apply migrations for all three models above
- Ensure `logo_key` column is nullable and blank-safe
- Verify foreign key constraints and cascade rules are correct before applying to staging/production

---

## SECTION 2 — Serializers

---

### TASK BE-05 — ServiceProviderContactSerializer

**File:** `serializers.py`

- Fields: `id`, `contact_type`, `salutation`, `name`, `role`, `email`, `contact_country_code`, `contact_number`, `remarks`
- Validate `contact_type` is one of `Primary`, `Secondary`
- Validate `salutation` is one of the allowed choices
- `contact_number` and `contact_country_code` both required together

---

### TASK BE-06 — ServiceProviderBankAccountSerializer

**File:** `serializers.py`

- Fields: `account_holder_name`, `bank_name`, `account_number`, `bank_branch`, `iban_swift_code`, `payment_gateway_url`
- All fields optional
- Validate `payment_gateway_url` format if provided

---

### TASK BE-07 — ServiceProviderSerializer (Main)

**File:** `serializers.py`

- **Write field:** `logo` — `ImageField`, write_only, optional. Validates file type (JPG/PNG) and size (max 5MB)
- **Read field:** `logo_url` — `SerializerMethodField`, read_only. Calls `S3PresignedService.generate_presigned_download_url(obj.logo_key)` if `logo_key` is set; returns `None` otherwise
- **Nested:** `contacts` — `ServiceProviderContactSerializer(many=True, required=False)`
- **Nested:** `bank_account` — `ServiceProviderBankAccountSerializer(required=False, allow_null=True)`
- `is_active`, `created_at`, `updated_at` — read_only

**create() method:**
1. Pop `logo`, `contacts`, `bank_account` from validated_data
2. If `logo` file present → call `S3PresignedService.upload_file_to_s3(file_content, file_name, folder="service-providers/logos")` → store returned `file_key` on the instance
3. Create `ServiceProvider` instance
4. For each contact in `contacts` → call `_handle_contact_create(service_provider, contact_data)` (applies primary demotion logic)
5. Create `ServiceProviderBankAccount` (even if all fields are null — always create the row)

**update() method:**
1. Pop `logo`, `contacts`, `bank_account` from validated_data
2. If new `logo` file → upload to S3, update `logo_key`
3. Update scalar fields via `setattr`
4. `update_or_create` on the bank account
5. Do NOT handle contacts in the update — contacts are managed via the sub-resource endpoints

---

### TASK BE-08 — ServiceProviderListSerializer (Lightweight)

**File:** `serializers.py`

A lightweight serializer for the list endpoint — avoids N+1 from nesting full contacts:

- Fields: `id`, `partner_name`, `email`, `contact_country_code`, `contact_number`, `logo_url`, `is_active`, `created_at`
- Also expose `primary_contact_name` via `SerializerMethodField` — fetches the name of the contact where `contact_type="Primary"` for this provider (use `prefetch_related` on the queryset to avoid N+1)

---

### TASK BE-09 — ServiceProviderDuplicateSerializer

**File:** `serializers.py`

- Read-only serializer returning the newly created duplicate's `id`, `partner_name`, and detail URL
- Used as the response body for the duplicate endpoint

---

## SECTION 3 — Views & Endpoints

---

### TASK BE-10 — List & Create Endpoint

**Class:** `ServiceProviderListCreateView(ListCreateAPIView)`
**URL:** `GET/POST /api/service-providers/`

**GET behaviour:**
- Returns paginated list of active service providers (`is_active=True`)
- Supports `?search=` query param — filters on `partner_name__icontains` OR `email__icontains`
- Uses `ServiceProviderListSerializer`
- `select_related("bank_account")` + `prefetch_related("contacts")` to avoid N+1
- Permission: `service_provider.view`

**POST behaviour:**
- Accepts `multipart/form-data` (include `MultiPartParser` and `FormParser` in `parser_classes`)
- Uses `ServiceProviderSerializer`
- Calls `serializer.save(created_by=request.user)`
- On success → returns `201` with the full serialized record
- Writes audit log entry on success
- Permission: `service_provider.create`

---

### TASK BE-11 — Retrieve, Update & Soft-Delete Endpoint

**Class:** `ServiceProviderDetailView(RetrieveUpdateDestroyAPIView)`
**URL:** `GET / PUT / PATCH / DELETE /api/service-providers/{id}/`

**GET behaviour:**
- Returns full record including nested contacts and bank account, and `logo_url`
- Only returns records where `is_active=True` — return `404` if soft-deleted
- Permission: `service_provider.view`

**PUT / PATCH behaviour:**
- Accepts `multipart/form-data`
- Only soft-deleted providers return `404`
- Writes audit log entry on success
- Permission: `service_provider.edit`

**DELETE behaviour:**
- Does NOT delete the record — sets `is_active=False`, records `deleted_at` timestamp and acting user
- Returns `204 No Content`
- Writes audit log entry
- Permission: `service_provider.delete`

---

### TASK BE-12 — Duplicate Endpoint

**Class:** `ServiceProviderDuplicateView(APIView)`
**URL:** `POST /api/service-providers/{id}/duplicate/`

**Behaviour:**
1. Fetch original service provider by `pk` where `is_active=True` — return `404` if not found
2. Create a new `ServiceProvider` copying all fields, with `partner_name` suffixed as `"{original_name} - Copy"`
3. Deep-copy all `ServiceProviderContact` records linked to the original
4. Deep-copy the `ServiceProviderBankAccount` record
5. `logo_key` is shared (same S3 object) — no need to copy the file
6. Set `created_by=request.user` on the new record
7. Write audit log entry referencing both original and new record IDs
8. Return `201` with the new record's `id` and `partner_name`
- Permission: `service_provider.duplicate`

---

### TASK BE-13 — Contact List & Add Endpoint

**Class:** `ServiceProviderContactListCreateView(APIView)`
**URL:** `GET / POST /api/service-providers/{id}/contacts/`

**GET behaviour:**
- Returns all contacts for the given service provider
- Ordered: Primary first, then Secondary contacts by `created_at`
- Permission: `service_provider.view`

**POST behaviour:**
- Validates the incoming contact data using `ServiceProviderContactSerializer`
- Applies **primary demotion logic** before saving:
  - If `contact_type == "Primary"` → update all existing contacts for this provider with `contact_type="Primary"` to `contact_type="Secondary"` first
- Creates the new contact
- Writes audit log entry
- Returns `201` with the new contact data
- Permission: `service_provider.edit`

---

### TASK BE-14 — Contact Edit & Remove Endpoint

**Class:** `ServiceProviderContactDetailView(APIView)`
**URL:** `PUT / DELETE /api/service-providers/{id}/contacts/{contact_id}/`

**PUT behaviour:**
- Validates the updated data
- Applies **primary demotion logic** (excluding the current contact from the demotion filter)
- Saves changes
- Writes audit log entry
- Permission: `service_provider.edit`

**DELETE behaviour:**
- Deletes the contact record permanently (hard delete — contacts themselves are not soft-deleted, only the service provider is)
- Writes audit log entry
- Returns `204 No Content`
- Permission: `service_provider.edit`

---

### TASK BE-15 — Insurer Products Sub-Resource Endpoint

**Class:** `ServiceProviderInsurerProductsView(ListAPIView)`
**URL:** `GET /api/service-providers/{id}/insurer-products/`

**Behaviour:**
- Returns a paginated list of active insurer products where `service_provider_id = {id}`
- Filters out soft-deleted insurer products
- Supports `?search=` query param filtering on product name
- Response fields per item: `id`, `product_name`, `risk_type`, `coverage_level`, `currency`, `last_update_date`
- If service provider does not exist (or is soft-deleted) → return `404`
- Permission: `service_provider.view`

---

### TASK BE-16 — Logo Upload Endpoint (Optional — if needed separately)

**Class:** `ServiceProviderLogoUploadView(APIView)`
**URL:** `POST /api/service-providers/upload-logo/`

> Note: Logo upload is handled as part of the create/edit multipart payload. This endpoint is only needed if the frontend needs to upload the logo independently (e.g. before form submission).

**Behaviour:**
- Accepts a single `logo` file in `multipart/form-data`
- Validates file type (JPG/PNG) and size (max 5MB)
- Uploads to S3 via `S3PresignedService.upload_file_to_s3()`
- Returns `{ "file_key": "...", "file_url": "..." }` (presigned URL for immediate preview)
- Permission: `service_provider.create` or `service_provider.edit`

---

### TASK BE-17 — GET Endpoints Parser Classes

Ensure all views that accept file uploads include:

```python
parser_classes = [MultiPartParser, FormParser, JSONParser]
```

Views that only serve data (GET-only) do not need `MultiPartParser`.

---

### TASK BE-18 — URL Configuration

**File:** `urls.py`

Register all endpoints:

```python
urlpatterns = [
    path("service-providers/",
         ServiceProviderListCreateView.as_view()),

    path("service-providers/upload-logo/",
         ServiceProviderLogoUploadView.as_view()),

    path("service-providers/<int:pk>/",
         ServiceProviderDetailView.as_view()),

    path("service-providers/<int:pk>/duplicate/",
         ServiceProviderDuplicateView.as_view()),

    path("service-providers/<int:pk>/contacts/",
         ServiceProviderContactListCreateView.as_view()),

    path("service-providers/<int:pk>/contacts/<int:contact_id>/",
         ServiceProviderContactDetailView.as_view()),

    path("service-providers/<int:pk>/insurer-products/",
         ServiceProviderInsurerProductsView.as_view()),
]
```

Include this urlconf under the `/api/` prefix in the root URL config.

---

## SECTION 4 — Business Logic / Services

---

### TASK BE-19 — S3 Logo Upload Integration

**File:** `services/s3_service.py` (already exists — see provided S3PresignedService)

Integrate with the existing `S3PresignedService`:

- On logo upload: call `S3PresignedService.upload_file_to_s3(file_content, file_name, folder="service-providers/logos")`
- Store the returned `file_key` in the `logo_key` column
- On any GET that includes a logo: call `S3PresignedService.generate_presigned_download_url(logo_key)` to generate a fresh temporary URL
- **Never** store the presigned URL in the database — it expires

---

### TASK BE-20 — Primary Contact Demotion Logic

**File:** `services/contact_service.py` or inline in the view/serializer

Extract as a reusable utility function:

```python
def set_contact_as_primary(service_provider_id: int, exclude_contact_id: int = None):
    """
    Demotes any existing Primary contact for the given service provider to Secondary.
    Pass exclude_contact_id to skip the contact currently being updated.
    """
    qs = ServiceProviderContact.objects.filter(
        service_provider_id=service_provider_id,
        contact_type="Primary"
    )
    if exclude_contact_id:
        qs = qs.exclude(pk=exclude_contact_id)
    qs.update(contact_type="Secondary")
```

Call this function before saving any contact with `contact_type="Primary"`.
This must be enforced at the service/view layer — not just the frontend — so direct API calls also respect the rule.

---

### TASK BE-21 — Soft-Delete Logic

**File:** Add a custom `delete()` override or a manager method

Soft delete sets:
- `is_active = False`
- (Optional) `deleted_at = now()` — add this field to the model if you want to track when deletion happened
- `deleted_by = request.user` — add this FK to the model if needed for auditing

Queryset default manager must filter `is_active=True` unless explicitly overridden.

```python
class ServiceProviderManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)

class ServiceProviderAllManager(models.Manager):
    """Use this when you need to include soft-deleted records (e.g. audit views)."""
    pass
```

---

### TASK BE-22 — Duplicate Logic

**File:** `services/duplicate_service.py` or inline in the view

Steps to implement:
1. Fetch original `ServiceProvider` record
2. Create new `ServiceProvider` with all fields copied, `partner_name` suffixed with `" - Copy"`, `created_by` set to acting user
3. Copy all related `ServiceProviderContact` records — iterate and create new instances with `service_provider` pointing to the duplicate
4. Copy `ServiceProviderBankAccount` — create a new instance with `service_provider` pointing to the duplicate
5. `logo_key` is shared — no S3 copy needed
6. Return the new `ServiceProvider` instance

---

## SECTION 5 — Permissions

---

### TASK BE-23 — Permission Keys Registration

Ensure the following permission keys are registered in the system's permission/role management module and seeded in the database:

| Permission Key | Description |
|---|---|
| `service_provider.create` | Create new service providers |
| `service_provider.view` | View service provider list and details |
| `service_provider.edit` | Edit an existing service provider and manage its contacts |
| `service_provider.duplicate` | Duplicate an existing service provider |
| `service_provider.delete` | Soft-delete a service provider |

---

### TASK BE-24 — Permission Enforcement on All Endpoints

Apply permission checks on every endpoint using the project's existing permission backend:

- All endpoints return `401 Unauthorized` if the user is not authenticated
- All endpoints return `403 Forbidden` if the user's role does not include the required permission
- Permission checks must be enforced at the API level — not just the UI — so that direct API calls are also protected

---

## SECTION 6 — Audit Logging

---

### TASK BE-25 — Audit Log Entries

Write an audit log entry for every mutating action. Each entry must record:

| Field | Value |
|---|---|
| `entity_type` | `"service_provider"` or `"service_provider_contact"` |
| `entity_id` | ID of the affected record |
| `action` | `"create"`, `"update"`, `"delete"`, `"duplicate"`, `"contact_add"`, `"contact_update"`, `"contact_remove"` |
| `actor` | FK to the acting user (request.user) |
| `timestamp` | `now()` |
| `changes` | JSON snapshot of changed fields (for update actions) — optional but recommended |

Actions that require audit entries:
- Create service provider
- Update service provider (general info or bank account)
- Soft-delete service provider
- Duplicate service provider (reference both original and new IDs)
- Add contact to service provider
- Edit contact
- Remove contact

---

## SECTION 7 — Tests

---

### TASK BE-26 — Model Tests

- Test `ServiceProvider` creation with all required fields
- Test soft-delete sets `is_active=False` and hides the record from the default queryset
- Test `ServiceProviderBankAccount` OneToOne relationship
- Test `ServiceProviderContact` FK relationship and cascade

---

### TASK BE-27 — Serializer Tests

- Test `ServiceProviderSerializer.create()` with logo file → assert `logo_key` is saved, not the URL
- Test `ServiceProviderSerializer.get_logo_url()` → assert presigned URL is generated from `logo_key`
- Test logo validation rejects non-JPG/PNG files
- Test logo validation rejects files over 5MB

---

### TASK BE-28 — Contact Demotion Tests

- Test: adding a second Primary contact demotes the existing Primary to Secondary
- Test: editing a contact's type to Primary demotes the current Primary (excluding itself)
- Test: multiple Secondary contacts can exist simultaneously
- Test: removing the Primary contact does not auto-promote any Secondary

---

### TASK BE-29 — Endpoint Tests

- `GET /api/service-providers/` — returns only active records; search filters correctly
- `POST /api/service-providers/` — creates provider with contacts and bank account in one request
- `DELETE /api/service-providers/{id}/` — soft-deletes; subsequent GET returns 404
- `POST /api/service-providers/{id}/duplicate/` — creates independent copy with suffixed name; original unchanged
- `GET /api/service-providers/{id}/insurer-products/` — returns only active insurer products for that provider

---

### TASK BE-30 — Permission Tests

- Unauthenticated requests → `401`
- Authenticated user without `service_provider.create` → `403` on POST
- Authenticated user without `service_provider.delete` → `403` on DELETE
- Authenticated user without `service_provider.edit` → `403` on contact add/edit/remove endpoints

---

## SECTION 8 — Endpoint Reference Summary

| Method | Endpoint | Permission | Description |
|---|---|---|---|
| `GET` | `/api/service-providers/` | `service_provider.view` | List active service providers |
| `POST` | `/api/service-providers/` | `service_provider.create` | Create new service provider |
| `GET` | `/api/service-providers/{id}/` | `service_provider.view` | Get full detail |
| `PUT/PATCH` | `/api/service-providers/{id}/` | `service_provider.edit` | Update service provider |
| `DELETE` | `/api/service-providers/{id}/` | `service_provider.delete` | Soft-delete |
| `POST` | `/api/service-providers/{id}/duplicate/` | `service_provider.duplicate` | Duplicate |
| `GET` | `/api/service-providers/{id}/contacts/` | `service_provider.view` | List contacts |
| `POST` | `/api/service-providers/{id}/contacts/` | `service_provider.edit` | Add contact |
| `PUT` | `/api/service-providers/{id}/contacts/{cid}/` | `service_provider.edit` | Edit contact |
| `DELETE` | `/api/service-providers/{id}/contacts/{cid}/` | `service_provider.edit` | Remove contact |
| `GET` | `/api/service-providers/{id}/insurer-products/` | `service_provider.view` | List linked insurer products |
| `POST` | `/api/service-providers/upload-logo/` | `service_provider.create/edit` | Upload logo independently |

---

## Notes

- Always store the S3 `file_key`, never the presigned URL.
- The primary demotion logic must live in the backend — do not rely solely on frontend enforcement.
- Soft-deleted records must be excluded from all list and detail endpoints by default. The default model manager should enforce this.
- The duplicate endpoint shares the same `logo_key` as the original — no S3 object copy is needed; both records point to the same file.
- Contact records are hard-deleted when removed (not soft-deleted) — only the `ServiceProvider` itself is soft-deleted.

---

## Implementation Status

| Task | Status | Date |
|---|---|---|
| BE-01 ServiceProvider Model | ✅ Done | 2026-03-23 |
| BE-02 ServiceProviderContact Model | ✅ Done | 2026-03-23 |
| BE-03 ServiceProviderBankAccount Model | ✅ Done | 2026-03-23 |
| BE-04 Database Migrations | ✅ Done | 2026-03-23 |
| BE-10 List & Create Endpoint | ✅ Done | 2026-03-23 |
| BE-11 Retrieve, Update & Soft-Delete Endpoint | ✅ Done | 2026-03-23 |
| BE-18 URL Configuration | ✅ Done | 2026-03-23 |
| BE-20 Primary Contact Demotion Logic | ✅ Done | 2026-03-23 |
| BE-21 Soft-Delete Logic | ✅ Done | 2026-03-23 |
| BE-19 S3 Logo Upload Integration | ✅ Done | 2026-03-23 |
| Other tasks (Duplicate, Permissions, Tests) | ⏳ Pending | — |
