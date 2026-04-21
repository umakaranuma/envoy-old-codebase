---
name: django-code-writing
description: Guides writing Django/DRF backend code following the envoy-bu-core-api project structure and conventions. Use when creating views/controllers, models, migrations, URLs, or when the user asks about Django project structure in this codebase.
---

# Django Code Writing

## Django project folder and file structure

Follow this layout for backend (Django) code as used in envoy-bu-core-api.

### App and module layout

- **Main app:** `envoy` — holds controllers, models, migrations, services, middleware.
- **Auth app:** `accounts` — login, JWT, and auth-related views (e.g. `accounts/views.py`).
- **Controllers (views):** `envoy/controllers/` — one module per resource (e.g. `roles_controller.py`, `contact_controller.py`, `reason_controller.py`). Use function-based views with `@api_view(["GET", "POST"])` or class-based views where appropriate.
- **Models:** `envoy/models/` — one file per model or logical group; expose via `envoy/models/__init__.py` if needed.
- **URLs:** `envoy/urls.py` — central URL config; include auth with `path("api/login", include("accounts.urls"))`. Add new routes here and import the controller function.
- **Migrations:** `envoy/migrations/` — Django migrations; no subfolders. One migration per change set; avoid mixing unrelated schema changes.
- **Settings:** `envoy/settings/` — `base.py` for shared config, `development.py` (or other env files) for overrides. `ROOT_URLCONF = "envoy.urls"`.

### Optional grouping by domain

- **Services:** `envoy/services/` for business logic (e.g. `entity_service.py`, `email_service.py`). Controllers in `envoy/controllers/services/` only if they are view-facing services (e.g. `NotificationService.py`).
- **Shared services:** If the project uses a shared package (e.g. `mServices`), use `ResponseService`, `QueryBuilderService`, `ValidatorService` from there; do not duplicate them inside `envoy`.

## Environment variables

- When adding or documenting a new variable used by the app, add the same key (with a placeholder or empty value, no secrets) to **`.env.example`** so other developers and deployments know which variables are required.
- JWT and external API settings (e.g. `JWT_SECRET`, `EXTERNAL_API_URL`, `DB_DATABASE`) should be documented in `.env.example`.

## Rate limiting

- **API endpoints** should be protected with rate limiting where appropriate (e.g. Django throttle classes, or a custom middleware). Prefer a sensible default (e.g. 60 requests per minute per user/IP) for API route groups; use stricter limits for auth-related or sensitive endpoints (e.g. login, password reset) if needed.

## API response format

- **All API responses** must use the standardized JSON format via **`ResponseService`** (from `mServices.ResponseService` or the project’s response module). Controllers must return `ResponseService.response(status_key, result=None, message=None, system_code=None)` instead of raw `JsonResponse()` or `Response()`.
- **Status keys:** `SUCCESS` (200), `NOT_FOUND` (404), `FORBIDDEN` (403), `INTERNAL_SERVER_ERROR` (500), `VALIDATION_ERROR` (417), `UNAUTHORIZED` (401), `CONFLICT` (409). Response body should include `is_success`, `message`, `result`, and `system_code`.
- Ensure the project’s `ResponseService` is used consistently; do not introduce ad-hoc JSON response shapes.

## List / get-all endpoint logic (QueryBuilderService)

- **List/get-all API endpoints** should use **`QueryBuilderService`** (from `mServices.QueryBuilderService` or the project’s query service) for filters, search, sorting, and pagination.
- **Pattern:** Build the query with `QueryBuilderService("table_name")` (or `"table_name as alias"`), then chain:
  - `.select(*columns)` for fields (use table-prefixed names when joining, e.g. `core_roles.id`, `core_roles.name`).
  - `.leftJoin("other_table as alias", "alias.id", "main_table.foreign_key")` when needed.
  - `.apply_conditions(filter_json, allowed_filters, search_string, search_columns)` for filters and search.
  - `.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)` for list responses, or `.get()` / `.first()` for single result.
- **Request parameters:** `filters` (JSON/object with column conditions), `search`, `page`, `limit`, `sort_by`, `sort_dir`. Use safe defaults (e.g. `page=1`, `limit=10`, `sort_by="id"`, `sort_dir="desc"`).
- **Controller responsibilities:** Define `allowed_filters`, `search_columns`, `allowed_sorting_columns`, and column lists; pass them into `QueryBuilderService`. Return the result via `ResponseService.response('SUCCESS', data, message)`.

**Example controller pattern (list with QueryBuilderService):**

```python
from rest_framework.decorators import api_view
from mServices.ResponseService import ResponseService
from mServices.QueryBuilderService import QueryBuilderService

@api_view(["GET", "POST"])
def reasons_view(request):
    if request.method == "GET":
        return list_reasons(request)
    elif request.method == "POST":
        return create_reason(request)

def list_reasons(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filters", "{}")

        allowed_filters = ["reason", "type_id"]
        search_columns = ["reason", "description"]
        sort_by = request.GET.get("sort_by") or "core_reasons.id"
        sort_dir = request.GET.get("sort_dir") or "desc"
        allowed_sorting_columns = ["core_reasons.id", "reason", "type_id"]

        all_columns = ["core_reasons.id", "reason", "type_id", "description"]

        query = (
            QueryBuilderService("core_reasons")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )
        return ResponseService.response("SUCCESS", query, "Reasons retrieved successfully!")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
```

## Validation (ValidatorService)

- Use **`ValidatorService.validate(data, rules, custom_messages)`** (from `mServices.ValidatorService`) for request body validation. Return `ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")` when validation fails.
- Define `rules` (e.g. `"field": "required|max:255|exists:table,column"`) and `custom_messages` for user-facing error text.

## User authentication (JWT)

- **API user authentication** must use **JWT**. The project uses **djangorestframework-simplejwt** (e.g. `RefreshToken.for_user(user)`, `rest_framework_simplejwt.authentication.JWTAuthentication`).
- **Protected routes:** Authentication is enforced by **`EndpointPermissionMiddleware`** in `envoy/middleware.py`. Public endpoints (e.g. login, verify-invitation, webhooks) are listed in `ENDPOINT_PERMISSIONS` with value `"public"`; all other API paths require a valid Bearer token.
- **Login:** Validate external IDP or credentials, then issue JWT and return via `ResponseService.response('SUCCESS', {'access_token': ..., 'user': ...})`. Do not return raw token-only responses; use the standard response format.
- **New public endpoints:** If an endpoint must be unauthenticated (e.g. webhook, callback), add its route to `ENDPOINT_PERMISSIONS` in `envoy/middleware.py` with permission `"public"`.

## Database transactions

- Use **database transactions** for any operation that modifies **multiple tables** or must succeed or fail as a whole. Use `from django.db import transaction` and wrap logic in `with transaction.atomic():` or `@transaction.atomic`. On exception, return an appropriate error via `ResponseService.response(...)` (e.g. `INTERNAL_SERVER_ERROR` or `CONFLICT`) and ensure no partial writes are committed.

## SQL safety (no raw user input)

- **Never** use raw SQL that concatenates user input (request data, query params, headers) into the query string. This leads to SQL injection.
- **Always** use **parameterized queries** (e.g. `cursor.execute(sql, [params])`), **Django ORM** (e.g. `Model.objects.filter(...)`), or the project’s **QueryBuilderService** (which should use parameter binding). Do not build SQL strings from user input.

## URL and controller conventions

- **URL prefix:** API routes are under `api/` (e.g. `path("api/roles", get_roles)`).
- **Controller naming:** One file per resource/domain, e.g. `roles_controller.py`, `contact_controller.py`. Export view functions and register them in `envoy/urls.py` with explicit imports to avoid circular imports.
- **HTTP methods:** Use `@api_view(["GET", "POST"])` and branch on `request.method` for combined list/create endpoints; use separate view functions for detail (get/update/delete) and register them on distinct paths (e.g. `api/roles/<int:role_id>`).

## Migrations

- **Table creation:** Define the table and columns in a migration. Do **not** add foreign key constraints in the same migration as large schema changes if the project uses a separate pattern for FKs; follow existing project convention (e.g. one migration per logical change).
- **Naming:** Use Django’s default migration naming (`XXXX_description.py`). Keep migrations reversible where possible (`RunPython`/`RunReversePython` or reversible operations).
