# User Invitation & Registration Flow — Full Task Specification

**Module:** Core — User Management  
**Feature:** User Invitation & Registration  
**Version:** 1.0  
**Status:** Completed  
**Source:** `envoy/urls.py`, `envoy/controllers/user_controller.py`, `envoy/middleware.py`, `envoy/utils.py`

---

## Table of Contents

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [Database Tables & Columns](#3-database-tables--columns)
4. [Environment Variables](#4-environment-variables)
5. [API Endpoints](#5-api-endpoints)
6. [Backend Tasks — Flow A: Create Invitation](#6-backend-tasks--flow-a-create-invitation)
7. [Backend Tasks — Flow B: Accept Invitation](#7-backend-tasks--flow-b-accept-invitation)
8. [Backend Tasks — Invitation Management](#8-backend-tasks--invitation-management)
9. [Backend Tasks — JWT Configuration](#9-backend-tasks--jwt-configuration)
10. [UI Tasks — Admin: Invite User](#10-ui-tasks--admin-invite-user)
11. [UI Tasks — Admin: Pending Invitations List](#11-ui-tasks--admin-pending-invitations-list)
12. [UI Tasks — Invitation Landing Page](#12-ui-tasks--invitation-landing-page)
13. [Error States & Messages](#13-error-states--messages)
14. [Security Notes](#14-security-notes)
15. [Resolved Decisions](#15-resolved-decisions)

---

## 1. Overview

The user invitation and registration system implements a **strict invite-only** model — there is no self-registration. Every user must be invited by an authorized admin. The system relies on an **external Identity Provider (IdP)** for authentication credentials; this API stores user records and issues its own JWTs after verifying the IdP token.

The full flow splits into two phases:

| Phase | Actor | Action |
|-------|-------|--------|
| **Flow A** | Admin | Creates an invitation → system sends email with a unique link |
| **Flow B** | Invited user | Clicks link → authenticates with IdP → API verifies and creates the account → JWT issued |

---

## 2. System Architecture

### Actors and responsibilities

| Layer | Responsibility |
|-------|----------------|
| **Core API** | Stores pending invites in `core_user_invitations`, sends invitation email, verifies IdP token, creates or reuses `core_users` rows, issues JWTs |
| **External IdP** | Handles user sign-up or sign-in; the client obtains an `idp_access_token` from the IdP |
| **Frontend** | Parses invitation link → drives IdP auth flow → calls `POST /api/verify-invitation` with IdP token + invitation UUID |
| **Email service** | Delivers the invitation HTML email; called via `EMAIL_SENDING_API_URL` |

### Flow summary

```
Admin → POST /api/users/invite
      → INSERT core_user_invitations (uid, name, email, role_id)
      → send_invitation_email() → user inbox

User → opens link → IdP sign-in/sign-up → gets idp_access_token
     → POST /api/verify-invitation (idp_access_token, invitation UUID)
     → API: GET EXTERNAL_API_URL → id, name, email from IdP
     → if idp_user_id exists in core_users → delete invite → issue JWT
     → if new user → INSERT core_users → delete invite → issue JWT
     → Frontend stores access_token → user is logged in
```

---

## 3. Database Tables & Columns

### 3.1 `core_user_invitations`

Stores pending invitations. Rows are **hard-deleted** when accepted or cancelled — this is not a soft-delete table.

| Column    | Type         | Nullable | Description |
|-----------|--------------|----------|-------------|
| `uid`     | UUID (PK)    | No       | Primary key. Auto-generated UUID. Used in the invitation link. Normalized (hyphens stripped) for DB lookup. |
| `name`    | VARCHAR(50)  | No       | Invitee's display name. Provided by admin at invite time. Max 50 characters. |
| `email`   | VARCHAR(255) | No       | Invitee's email address. Must be unique in this table (one pending invite per email). Must not exist in `core_users`. |
| `role_id` | INT (FK)     | No       | FK → `core_roles.id`. Role that will be assigned to the new user on acceptance. |

**Indexes:**
- `PRIMARY KEY (uid)`
- `UNIQUE INDEX idx_invitation_email (email)` — enforces one pending invite per email
- `INDEX idx_invitation_role (role_id)`

---

### 3.2 `core_users`

Application user records. Created on first successful `verify-invitation`, or reused if `idp_user_id` already exists.

| Column          | Type         | Nullable | Description |
|-----------------|--------------|----------|-------------|
| `id`            | INT (PK)     | No       | Primary key, auto-increment |
| `idp_user_id`   | VARCHAR(255) | No       | Unique ID from the external IdP (`result.id` from IdP user-info response). Used to look up existing users on subsequent accepts. |
| `email`         | VARCHAR(255) | No       | User's email from IdP |
| `first_name`    | VARCHAR(255) | Yes      | From IdP `result.name` |
| `display_name`  | VARCHAR(255) | Yes      | From IdP `result.name`; user can update later |
| `role_id`       | INT (FK)     | No       | FK → `core_roles.id`. Set from invitation `role_id` on creation. Not updated on existing-user accept path. |
| `entity_id`     | INT (FK)     | No       | FK → `core_entity.id`. Always set to `1` (default entity) via `get_or_create` on new user creation. |
| `code`          | VARCHAR(255) | No       | Unique application-level user code. Generated by `generate_unique_user_code()` at creation time. |

**Indexes:**
- `PRIMARY KEY (id)`
- `UNIQUE INDEX idx_users_idp_id (idp_user_id)`
- `UNIQUE INDEX idx_users_email (email)`
- `INDEX idx_users_role (role_id)`
- `INDEX idx_users_entity (entity_id)`

---

### 3.3 `core_roles`

Referenced by both `core_user_invitations` and `core_users`.

| Column | Type | Description |
|--------|------|-------------|
| `id`   | INT (PK) | Primary key |
| `name` | VARCHAR(255) | Role name (e.g. "Admin", "Agent") |

> Must be pre-seeded before any invitations can be created. The invite form's role dropdown is populated from this table.

---

### 3.4 `core_entity`

Default entity used for all new users.

| Column | Type | Description |
|--------|------|-------------|
| `id`   | INT (PK) | Primary key |
| `type` | VARCHAR(255) | Entity type label |

> A row with `id = 1` and `type = "Default Entity"` must always exist. It is created via `get_or_create(id=1, defaults={"type": "Default Entity"})` during the `verify-invitation` flow.

---

## 4. Environment Variables

| Variable | Role | Required |
|----------|------|----------|
| `JWT_SECRET` | Django `SECRET_KEY` and JWT signing key (`SIMPLE_JWT.SIGNING_KEY`) | Yes |
| `EXTERNAL_API_URL` | IdP user-info endpoint — `GET` this with the IdP Bearer token to retrieve `id`, `name`, `email` | Yes |
| `BROKERAGE_FRONTEND_BASE_URL` | Base URL used to build the invitation link embedded in the email | Yes |
| `EMAIL_SENDING_API_URL` | External service that delivers the invitation HTML email | Yes |
| DB vars | MySQL connection for all `core_*` tables | Yes |

---

## 5. API Endpoints

### 5.1 Invitation endpoints

| Method | Path | Handler | Auth | Description |
|--------|------|---------|------|-------------|
| `POST` | `/api/users/invite` | `create_invitations` | Protected (middleware) | Create invitation + send email |
| `POST` | `/api/verify-invitation` | `accept_invitations` | **Public** — no API JWT | Accept invite via IdP token |
| `GET`  | `/api/invitations` | — | Protected | List all pending invitations |
| `POST` | `/api/invitations/<uid>/resend` | — | Protected | Resend invitation email by UID |
| `POST` | `/api/invitations/<uid>/cancel` | — | Protected | Cancel invitation by UID |
| `POST` | `/api/invitations/cancel` | — | Protected | Cancel invitation by email (+ optional UUID) |

### 5.2 `POST /api/users/invite` — Request body

```json
{
  "name": "Sarah Johnson",
  "email": "sarah@acme.com",
  "role_id": 2
}
```

### 5.3 `POST /api/verify-invitation` — Request body

```json
{
  "idp_access_token": "<token-from-idp>",
  "invitation": "550e8400-e29b-41d4-a716-446655440000"
}
```

> UUID may be passed with or without hyphens. The backend normalizes it by stripping hyphens before the DB lookup.

### 5.4 `POST /api/verify-invitation` — Success response

```json
{
  "access_token": "<jwt-string>",
  "refresh_token": "<jwt-string>",
  "user": {
    "id": 42,
    "first_name": "Sarah",
    "display_name": "Sarah Johnson",
    "email": "sarah@acme.com",
    "idp_user_id": "<idp-id>",
    "role": { "id": 2, "name": "Agent" },
    "entity": { "id": 1, "type": "Default Entity" }
  }
}
```

### 5.5 Invitation email link shape

```
{BROKERAGE_FRONTEND_BASE_URL}/user-invitation
  ?invitation={uid}
  &name={name}
  &email={email}
  &role_id={role_id}
  &role_name={role_name}
```

---

## 6. Backend Tasks — Flow A: Create Invitation

### Task B-A1 — Request validation

| # | Task | Details |
|---|------|---------|
| B-A1.1 | Validate `name` | Required. Max 50 characters. Return 400 if missing or exceeds limit. |
| B-A1.2 | Validate `email` | Required. Must be a valid email format. Return 400 if missing or malformed. |
| B-A1.3 | Validate `role_id` | Required. Must exist as a row in `core_roles`. Return 400 if missing. Return 404 if role not found. |

### Task B-A2 — Duplicate checks

| # | Task | Details |
|---|------|---------|
| B-A2.1 | Check `core_users` for existing email | If a row with the same `email` already exists in `core_users`, return a duplicate-user error. Message: `"A user with this email address already exists."` HTTP 409. |
| B-A2.2 | Check `core_user_invitations` for existing email | If a row with the same `email` already exists in `core_user_invitations`, return a duplicate-invitation error. Message: `"A pending invitation already exists for this email address."` HTTP 409. |

### Task B-A3 — Create invitation row

| # | Task | Details |
|---|------|---------|
| B-A3.1 | Load the `Role` object | Query `core_roles` by `role_id`. |
| B-A3.2 | Insert `UserInvitation` | Create a new `core_user_invitations` row with `name`, `email`, `role_id`. The `uid` UUID is auto-generated by the model. |

### Task B-A4 — Send invitation email

| # | Task | Details |
|---|------|---------|
| B-A4.1 | Build invitation URL | Construct the frontend URL using `BROKERAGE_FRONTEND_BASE_URL` + path `/user-invitation` + query params: `invitation={uid}`, `name={name}`, `email={email}`, `role_id={role_id}`, `role_name={role.name}`. |
| B-A4.2 | Call `send_invitation_email()` | Located in `envoy/utils.py`. Builds the HTML email content and POSTs it to `EMAIL_SENDING_API_URL`. |
| B-A4.3 | Handle email send failure | If the email service returns an error, log the failure but still return success to the admin (the invitation row exists and can be resent). Do not roll back the DB insert. |

### Task B-A5 — Response

| # | Task | Details |
|---|------|---------|
| B-A5.1 | Return success | Use `ResponseService` success wrapper. Message: `"invitation_sent_successfully"`. HTTP 201. |

---

## 7. Backend Tasks — Flow B: Accept Invitation

### Task B-B1 — Request validation and UUID parsing

| # | Task | Details |
|---|------|---------|
| B-B1.1 | Validate `idp_access_token` | Required field. Return 400 if missing. |
| B-B1.2 | Validate `invitation` | Required field. Parse as UUID string. Return 400 if missing or cannot be parsed as a valid UUID. |
| B-B1.3 | Normalize UUID | Strip all hyphens from the `invitation` string before the DB lookup (e.g. `"550e8400-e29b-41d4..."` → `"550e8400e29b41d4..."`). |
| B-B1.4 | Confirm invitation exists | Query `core_user_invitations` where `uid = normalized_uuid`. Return 404 with message `"Invitation not found."` if no row exists. |

### Task B-B2 — Fetch IdP user profile

| # | Task | Details |
|---|------|---------|
| B-B2.1 | Call IdP user-info endpoint | `GET {EXTERNAL_API_URL}` with header `Authorization: Bearer {idp_access_token}`. |
| B-B2.2 | Parse IdP response | Expect JSON with `is_success: true` and `result` containing at minimum: `id` (used as `idp_user_id`), `name`, `email`. |
| B-B2.3 | Handle IdP failure | If `is_success` is `false` or the HTTP call fails, return 401 with message `"Identity provider authentication failed."` Do not create or modify any user records. |
| B-B2.4 | Extract fields | Map: `result.id` → `idp_user_id`, `result.name` → `first_name` / `display_name`, `result.email` → `email`. |

### Task B-B3 — Branch: Existing user path

Triggered when a row exists in `core_users` where `idp_user_id` matches the IdP `result.id`.

| # | Task | Details |
|---|------|---------|
| B-B3.1 | Look up existing user | Query `core_users` by `idp_user_id`. |
| B-B3.2 | Delete the invitation row | If a `core_user_invitations` row exists for this email, delete it (hard delete). |
| B-B3.3 | Do NOT update the user's role | The invitation's `role_id` is ignored on this path. The existing user's role stays unchanged. |
| B-B3.4 | Issue JWT | Call `RefreshToken.for_user(existing_user)` from `rest_framework_simplejwt.tokens`. |
| B-B3.5 | Return response | Return `access_token`, `refresh_token`, and user snapshot. Message: `"Invitation accepted successfully!"` HTTP 200. |

### Task B-B4 — Branch: New user path

Triggered when no `core_users` row has the matching `idp_user_id`.

| # | Task | Details |
|---|------|---------|
| B-B4.1 | Load invitation row | Fetch the `core_user_invitations` row to get `role_id`, `name`, `email`. |
| B-B4.2 | Load `Role` | Query `core_roles` by `role_id` from the invitation. |
| B-B4.3 | Resolve default entity | Call `Entity.objects.get_or_create(id=1, defaults={"type": "Default Entity"})`. Always uses entity `id=1`. |
| B-B4.4 | Generate unique user code | Call `generate_unique_user_code()` to produce a unique `code` value for the new user. |
| B-B4.5 | Create `core_users` row | Call `User.objects.create` with: `idp_user_id`, `email`, `first_name` (from IdP `name`), `display_name` (from IdP `name`), `role` (from invitation), `entity` (id=1), `code`. |
| B-B4.6 | Delete invitation row | Hard-delete the `core_user_invitations` row. |
| B-B4.7 | Issue JWT | Call `RefreshToken.for_user(user)`. |
| B-B4.8 | Return response | Return `access_token`, `refresh_token`, and full user snapshot. Message: `"invitation_accepted_successfully"`. HTTP 201. |

---

## 8. Backend Tasks — Invitation Management

### Task B-C1 — List pending invitations (`GET /api/invitations`)

| # | Task | Details |
|---|------|---------|
| B-C1.1 | Query all rows | Return all rows from `core_user_invitations`. |
| B-C1.2 | Serialize response | Include per row: `uid`, `name`, `email`, `role_id`, `role_name` (joined from `core_roles`), `created_at` (if tracked), derived `status` (Invited / Expired). |
| B-C1.3 | Compute status | If an invitation expiry window is configured, derive `status = "Expired"` if `created_at + expiry_hours < now`. Otherwise `status = "Invited"`. |

### Task B-C2 — Resend invitation (`POST /api/invitations/<uid>/cancel`)

| # | Task | Details |
|---|------|---------|
| B-C2.1 | Look up invitation by `uid` | Return 404 if not found. |
| B-C2.2 | Regenerate invitation link | Build a fresh frontend URL using the same fields. Optionally reset a `resent_at` timestamp on the row. |
| B-C2.3 | Resend email | Call `send_invitation_email()` with the refreshed link. |
| B-C2.4 | Return success | Message: `"Invitation resent successfully."` HTTP 200. |

### Task B-C3 — Cancel invitation by UID (`POST /api/invitations/<uid>/cancel`)

| # | Task | Details |
|---|------|---------|
| B-C3.1 | Look up invitation by `uid` | Return 404 if not found. |
| B-C3.2 | Hard-delete the row | `UserInvitation.objects.filter(uid=uid).delete()`. |
| B-C3.3 | Return success | Message: `"Invitation cancelled."` HTTP 200. |

### Task B-C4 — Cancel invitation by email (`POST /api/invitations/cancel`)

| # | Task | Details |
|---|------|---------|
| B-C4.1 | Accept `email` and optional `uid` in body | Both fields optional but at least one required. |
| B-C4.2 | Build query | Filter by `email` if provided; additionally filter by `uid` if provided. |
| B-C4.3 | Hard-delete matching rows | Delete all matching `core_user_invitations` rows. |
| B-C4.4 | Return success | Message: `"Invitation cancelled."` HTTP 200. Return 404 if no matching row found. |

---

## 9. Backend Tasks — JWT Configuration

The JWT setup uses **django-rest-framework-simplejwt**. The following settings are applied in `envoy/settings/base.py` under the `SIMPLE_JWT` dict.

| # | Task | Setting | Value |
|---|------|---------|-------|
| B-D1 | Token lifetime | `ACCESS_TOKEN_LIFETIME` | `timedelta(days=365 * 10)` — 10 years |
| B-D2 | Refresh lifetime | `REFRESH_TOKEN_LIFETIME` | `timedelta(days=365 * 10)` — 10 years |
| B-D3 | Token rotation | `ROTATE_REFRESH_TOKENS` | `True` — a new refresh token is issued on every refresh |
| B-D4 | Blacklist on rotation | `BLACKLIST_AFTER_ROTATION` | `True` — old refresh tokens are invalidated after rotation |
| B-D5 | Algorithm | `ALGORITHM` | `HS256` |
| B-D6 | Signing key | `SIGNING_KEY` | Read from env var `JWT_SECRET` (= Django `SECRET_KEY`) |
| B-D7 | Auth header | `AUTH_HEADER_TYPES` | `("Bearer",)` |
| B-D8 | User ID field | `USER_ID_FIELD` | `"id"` — references `core_users.id` |
| B-D9 | User ID claim | `USER_ID_CLAIM` | `"user_id"` — the claim name inside the JWT payload |
| B-D10 | Authentication class | `REST_FRAMEWORK.DEFAULT_AUTHENTICATION_CLASSES` | `CustomJWTAuthentication` from `envoy/custom_auth_check.py` |
| B-D11 | Public endpoint | `EndpointPermissionMiddleware` | `api/verify-invitation` is marked public — no API JWT required on this route |

**Token issuance pattern (in `accept_invitations`):**

```python
refresh = RefreshToken.for_user(user)  # or existing_user
response_data = {
    "access_token": str(refresh.access_token),
    "refresh_token": str(refresh),
}
```

**Subsequent API calls:** All protected endpoints require `Authorization: Bearer <access_token>` header. Handled by `CustomJWTAuthentication`.

---

## 10. UI Tasks — Admin: Invite User

### Screen: Invite User modal

Accessible from the Users list page. Visible only to users with the appropriate invite permission.

| Task ID | Component | Description |
|---------|-----------|-------------|
| UI-A1 | "Invite User" button | Displayed in the Users list page header. Hidden if the acting user lacks the invite permission. Opens the invite modal on click. |
| UI-A2 | Modal: Name field | Text input. Label: "Name". Required. Max 50 characters. Live character counter optional. |
| UI-A3 | Modal: Email field | Email input. Label: "Email Address". Required. Client-side format validation. Show inline error on blur if invalid. |
| UI-A4 | Modal: Role dropdown | Single-select. Label: "Role". Required. Populated from `GET /api/roles`. Show role name in options. |
| UI-A5 | Form validation on submit | Block submit if: name is empty, email is empty or invalid format, role is not selected. Focus and highlight the first failing field. |
| UI-A6 | Submit — loading state | Disable the submit button and show a spinner while `POST /api/users/invite` is in flight. |
| UI-A7 | Success response handling | Close the modal. Show success toast: `"Invitation sent to {email}"`. Refresh the pending invitations list. |
| UI-A8 | Error: duplicate user | Inline message below the email field: `"This email already has an active account."` Do not close the modal. |
| UI-A9 | Error: duplicate invitation | Inline message below the email field: `"A pending invitation already exists for this email."` Do not close the modal. |
| UI-A10 | Error: invalid role | Show generic form error: `"Selected role is invalid."` |
| UI-A11 | Cancel button | Closes the modal without submitting. Clears the form. |

---

## 11. UI Tasks — Admin: Pending Invitations List

### Screen: Invited Users section

A dedicated section or tab within User Management showing all rows from `core_user_invitations`.

| Task ID | Component | Description |
|---------|-----------|-------------|
| UI-B1 | Invitations table | Columns: Name, Email Address, Role, Invited On, Link Expires At (if expiry is tracked), Status, Actions. |
| UI-B2 | Status badge: Invited | Green badge. Shown when the invitation is active and within the expiry window. |
| UI-B3 | Status badge: Expired | Amber badge. Shown when the invitation is past its expiry window but not yet cancelled. |
| UI-B4 | Search / filter bar | Filter by name, email, or status (Invited / Expired). Debounced client-side or server-side search. |
| UI-B5 | Resend action | Button per row. Calls `POST /api/invitations/<uid>/resend`. On success: show toast `"Invitation resent to {email}"`. Update the "Invited On" timestamp in the row if the server returns updated data. Available for both Invited and Expired status rows. |
| UI-B6 | Cancel action | Button per row. Opens a confirmation dialog: `"Are you sure you want to cancel the invitation for {name} ({email})? This will invalidate their invitation link."` On confirm: calls `POST /api/invitations/<uid>/cancel`. Remove the row from the list on success. Show toast: `"Invitation cancelled."` |
| UI-B7 | Empty state | If no pending invitations exist, show: `"No pending invitations."` with a call-to-action to invite a user. |
| UI-B8 | Pagination | Server-side pagination if the invitation list is long. |

---

## 12. UI Tasks — Invitation Landing Page

### Screen: `/user-invitation` (public route, no auth required)

The page the invited user lands on after clicking the email link. This is a **frontend-only public route** — no API JWT is attached to any call here until after successful registration.

| Task ID | Component | Description |
|---------|-----------|-------------|
| UI-C1 | Parse query parameters | On page load, extract from URL: `invitation` (UUID), `name`, `email`, `role_id`, `role_name`. Store in component state. |
| UI-C2 | Validate invitation param | If `invitation` is missing or not a valid UUID format, immediately show the Invalid Link error screen (see UI-C10). Do not proceed. |
| UI-C3 | Welcome screen | Display a welcome message using the `name` and `role_name` from the URL params. Example: `"Hi Sarah, you've been invited to join as Agent."` Show the `email` address the invite was sent to. |
| UI-C4 | "Create your account" button | Primary action button. On click: initiate the IdP authentication flow (redirect to IdP sign-in/sign-up page, or open a popup depending on IdP integration). |
| UI-C5 | IdP callback handling | After the user completes IdP authentication, the frontend receives the `idp_access_token`. This step depends on the IdP integration (OAuth callback, postMessage, etc.). Extract the token. |
| UI-C6 | Call `POST /api/verify-invitation` | Immediately after receiving `idp_access_token`, call `POST /api/verify-invitation` with body `{ idp_access_token, invitation }`. **Do not attach any Authorization header to this request.** |
| UI-C7 | Show loading state | Show a loading indicator between the IdP callback and the `verify-invitation` response. Disable the action button. Message: `"Setting up your account…"` |
| UI-C8 | Success: store JWT and redirect | On success response: extract `access_token` from response body. Store securely (httpOnly cookie or in-memory — never in `localStorage`). Redirect the user to the application dashboard or home screen. |
| UI-C9 | Success: existing user path | The `verify-invitation` response for an existing user returns the same `access_token` + user payload. Handle identically to the new user path — store token and redirect. Do not show any message about role changes. |
| UI-C10 | Error: invalid link | If the `invitation` UUID is malformed or missing from the URL, show a full-screen error: `"This invitation link is invalid."` with no further actions. |
| UI-C11 | Error: invitation not found | If `verify-invitation` returns 404, show: `"This invitation has been cancelled or does not exist. Please contact your administrator to request a new invitation."` |
| UI-C12 | Error: invitation expired | If `verify-invitation` returns an expired-invitation error, show: `"This invitation link has expired. Please contact your administrator to resend the invitation."` |
| UI-C13 | Error: IdP authentication failed | If the IdP flow fails or `verify-invitation` returns 401, show: `"Authentication failed. Please try again."` with a retry button that re-initiates the IdP flow. Do not show technical error details. |
| UI-C14 | Error: network / server error | If `verify-invitation` returns 500 or the network call fails, show: `"Something went wrong. Please try again."` with a retry button. |
| UI-C15 | No back-navigation after success | After successful registration and redirect, the `/user-invitation` route should not be accessible again with the same `invitation` UUID (the row is deleted server-side). If the user navigates back, the API returns 404 which maps to UI-C11. |

---

## 13. Error States & Messages

### Backend error responses

| Trigger | HTTP Status | Message key / string |
|---------|-------------|----------------------|
| `name` missing | 400 | `"Name is required."` |
| `name` exceeds 50 chars | 400 | `"Name must not exceed 50 characters."` |
| `email` missing or invalid | 400 | `"A valid email address is required."` |
| `role_id` missing | 400 | `"Role is required."` |
| `role_id` not found in `core_roles` | 404 | `"Role not found."` |
| Email already in `core_users` | 409 | `"A user with this email address already exists."` |
| Email already in `core_user_invitations` | 409 | `"A pending invitation already exists for this email address."` |
| `invitation` UUID missing | 400 | `"Invitation token is required."` |
| `invitation` UUID invalid format | 400 | `"Invalid invitation token."` |
| `invitation` not found in DB | 404 | `"Invitation not found."` |
| IdP call fails / `is_success` false | 401 | `"Identity provider authentication failed."` |
| Generic server error | 500 | `"An unexpected error occurred."` |

### Frontend error display rules

| Error type | Display location | Dismissible |
|------------|-----------------|-------------|
| Field validation (create invite modal) | Inline below the field | Yes, on re-type |
| Duplicate email (create invite modal) | Inline below the email field | Yes, on change |
| Invitation not found (landing page) | Full screen message | No |
| Invitation expired (landing page) | Full screen message | No |
| IdP auth failure (landing page) | Inline with retry button | Yes, via retry |
| Network error (landing page) | Inline with retry button | Yes, via retry |

---

## 14. Security Notes

| # | Note |
|---|------|
| S-01 | `POST /api/verify-invitation` must not require an API JWT — it is listed as public in `EndpointPermissionMiddleware`. The client authenticates only via the IdP token in the request body. |
| S-02 | The `invitation` UUID is the only secret in the email link. It must be a cryptographically random UUID (standard UUID v4 is sufficient). |
| S-03 | On the existing-user accept path, the invitation `role_id` is **silently ignored**. The user's existing role in `core_users` is not modified. This prevents role escalation via a re-issued invitation. |
| S-04 | The `access_token` returned by `verify-invitation` must be stored in an httpOnly cookie or in-memory — never in `localStorage` or `sessionStorage` (XSS risk). |
| S-05 | Invitation rows are hard-deleted immediately on acceptance. A UUID cannot be reused once accepted. |
| S-06 | Cancelled invitation UUIDs that a user might still have in their email produce a 404 from `verify-invitation` — the same response as "not found". Do not distinguish between "cancelled" and "never existed" in the API response. |
| S-07 | The `BROKERAGE_FRONTEND_BASE_URL` and `EMAIL_SENDING_API_URL` must be set from environment variables — never hardcoded. |
| S-08 | JWT tokens have a 10-year lifetime (as configured). This is intentional per the current settings. Rotation is enabled (`ROTATE_REFRESH_TOKENS = True`) with blacklisting (`BLACKLIST_AFTER_ROTATION = True`). |

---

## 15. Resolved Decisions

| # | Question | Decision |
|---|----------|----------|
| RD-01 | Can a user register without an invitation? | No — invite-only. No self-registration path exists. |
| RD-02 | What happens if an already-registered user accepts an invitation? | They are logged in (JWT issued). The invitation's role is **not** applied to them. Their existing user record and role are unchanged. |
| RD-03 | Is the invitation row deleted on acceptance? | Yes — hard delete immediately on acceptance. Not a soft delete. |
| RD-04 | Can an email have multiple pending invitations at once? | No — enforced by the duplicate check in `create_invitations` and the `UNIQUE` index on `core_user_invitations.email`. |
| RD-05 | How is the invitation UUID formatted in the DB? | Hyphens are stripped before storage and lookup. The email link may include a hyphenated UUID; the backend normalizes it. |
| RD-06 | What entity is assigned to new users? | Always `core_entity.id = 1` ("Default Entity"), created via `get_or_create`. |
| RD-07 | How long are JWT tokens valid? | 10 years (`ACCESS_TOKEN_LIFETIME = timedelta(days=365 * 10)`). This is a deliberate product decision. |
| RD-08 | Does the landing page require authentication? | No. The `/user-invitation` route is fully public. No API token is attached to the `verify-invitation` call. |
| RD-09 | Who can create invitations? | Only users whose role/middleware allows access to `POST /api/users/invite`. The endpoint is protected (not in the public list). |
| RD-10 | What IdP fields are used to create the user? | `result.id` → `idp_user_id`, `result.name` → `first_name` / `display_name`, `result.email` → `email`. |

---

## Implementation Summary

| Task | Status | Date |
|------|--------|------|
| User Invitation Flow Update | Completed | 2026-03-25 |
| Backend Link Generation | Completed | 2026-03-25 |
| Frontend Registration Logic | Completed | 2026-03-25 |
| Fix Server Component Errors | Completed | 2026-03-25 |
| UI API Error Handling | Completed | 2026-03-25 |
| UI Consent Payload Update | Completed | 2026-03-25 |

---

*Document prepared from `USER_INVITATION_FLOW.md` API reference and codebase analysis. Version 1.0. Subject to revision as further implementation details are clarified.*
