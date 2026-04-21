# User invitation flow — API reference

This document describes how **staff/admin invites** a user, how the **invitee accepts** via the frontend, how the **core user record** is created, and how **JWT tokens** are issued. It maps to `envoy/urls.py` routes and `envoy/controllers/user_controller.py`.

---

## Overview

| Layer | Responsibility |
|--------|----------------|
| **This API** | Stores pending invites (`core_user_invitations`), sends email, verifies IdP token, creates/links `core_users`, issues JWTs. |
| **External IdP** | User signs up or logs in; client obtains `idp_access_token`. User profile is read via `EXTERNAL_API_URL`. |
| **Frontend** | Link in email → user completes IdP flow → calls `POST /api/verify-invitation` with token + invitation UUID. |

---

## Endpoints

| Method | Path | Handler | Auth |
|--------|------|---------|------|
| `POST` | `/api/users/invite` | `create_invitations` | Protected (middleware; not in public list) |
| `POST` | `/api/verify-invitation` | `accept_invitations` | **Public** (no API JWT; IdP token in body) |

Related (invitation management):

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/invitations` | List pending invitations |
| `POST` | `/api/invitations/<uid>/resend` | Resend email |
| `POST` | `/api/invitations/<uid>/cancel` | Cancel by UID |
| `POST` | `/api/invitations/cancel` | Cancel by email (and optional UUID) |

---

## Database tables

| Table | Model | Role in this flow |
|-------|--------|-------------------|
| `core_user_invitations` | `UserInvitation` | Pending invite: `uid` (PK, UUID), `name`, `email`, `role_id` (FK → `core_roles`). Row deleted when accepted or cleaned up. |
| `core_users` | `User` | Application user: `idp_user_id`, `email`, `first_name`, `display_name`, `role_id`, `entity_id`, `code`, etc. Created on first successful verify, or reused if `idp_user_id` already exists. |
| `core_roles` | `Role` | Role assigned at invite time; applied to new `User` on accept. |
| `core_entities` | `Entity` | Default entity: code uses `get_or_create(id=1, defaults={"type": "Default Entity"})` for new users. |

---

## Flow A — Create invitation (`POST /api/users/invite`)

### Request body (JSON)

| Field | Rules |
|-------|--------|
| `name` | Required, max 50 characters |
| `email` | Required, valid email, **must not exist** in `core_users` |
| `role_id` | Required, must exist in `core_roles` |

### Server steps

1. Validate with `ValidatorService`.
2. If any row in `core_user_invitations` has the same **email**, return duplicate-invitation error (one pending invite per email).
3. Load `Role` and create `UserInvitation` (UUID `uid` generated automatically).
4. Call `send_invitation_email()` (`envoy/utils.py`): builds a frontend URL using `BROKERAGE_FRONTEND_BASE_URL`, posts HTML to `EMAIL_SENDING_API_URL`.

### Email link shape

The invite link targets the brokerage frontend, roughly:

`{BROKERAGE_FRONTEND_BASE_URL}/user-invitation?invitation={uid},name=...,email=...,role_id=...,role_name=...`

(Exact query formatting is defined in `send_invitation_email`.)

### Success response

Standard `ResponseService` success with message such as `invitation_sent_successfully`.

---

## Flow B — Accept invitation (`POST /api/verify-invitation`)

### Request body (JSON)

| Field | Purpose |
|-------|---------|
| `idp_access_token` | Bearer token from the **IdP** (not this API’s JWT). |
| `invitation` | Invitation UUID string (with or without hyphens). |

### Server steps

1. Validate required fields; parse `invitation` as UUID; normalize by **removing hyphens** for DB lookup on `core_user_invitations.uid`.
2. Confirm invitation exists (`exists:core_user_invitations,uid`).
3. **IdP user-info:** `GET` to `EXTERNAL_API_URL` with header `Authorization: Bearer {idp_access_token}`.
4. Expect JSON with `is_success` and `result` containing at least `id`, `name`, `email` (used as `idp_user_id`, display name, email).
5. **Branch:**
   - **Existing `core_users` row** where `idp_user_id` matches IdP `id`: delete matching `UserInvitation` if present; issue JWT; return user snapshot (**invitation role is not merged** into the existing user in this path).
   - **No such user:** load invitation → role; ensure default `Entity` (id `1`); **`User.objects.create`** with IdP name/email, `idp_user_id`, invitation role, entity, generated `code` (`generate_unique_user_code`); delete invitation; issue JWT; return new user.

### Success response payload (conceptual)

- `access_token` — JWT access token (string).
- `user` — subset of user fields: `id`, `first_name`, `display_name`, `email`, `idp_user_id`, `role`, `entity`.

Message examples: `invitation_accepted_successfully`, `Invitation accepted successfully!` (existing user path).

---

## Middleware: why `verify-invitation` needs no API JWT

`EndpointPermissionMiddleware` (`envoy/middleware.py`) marks **`api/verify-invitation`** as **public**. The client authenticates to the **IdP** first; this endpoint only receives the IdP access token in the JSON body.

---

## JWT token generation

### Library

- **django-rest-framework-simplejwt** — `RefreshToken` from `rest_framework_simplejwt.tokens`.

### Where tokens are created

In `accept_invitations` (`user_controller.py`), after a successful IdP check and user resolution:

```python
refresh = RefreshToken.for_user(existing_user)  # or for_user(user) for new user
# Response includes:
str(refresh.access_token)
```

So the **subject** of the JWT is the Django user instance passed to `for_user` (the row in `core_users`).

### Settings (`envoy/settings/base.py` — `SIMPLE_JWT`)

| Setting | Value (as in repo) |
|---------|---------------------|
| `ACCESS_TOKEN_LIFETIME` | 10 years (`timedelta(days=365 * 10)`) |
| `REFRESH_TOKEN_LIFETIME` | 10 years |
| `ROTATE_REFRESH_TOKENS` | `True` |
| `BLACKLIST_AFTER_ROTATION` | `True` |
| `ALGORITHM` | `HS256` |
| `SIGNING_KEY` | `SECRET_KEY` from env (`JWT_SECRET`) |
| `AUTH_HEADER_TYPES` | `Bearer` |
| `USER_ID_FIELD` | `id` |
| `USER_ID_CLAIM` | `user_id` |

### API authentication after invite

Clients send:

`Authorization: Bearer <access_token>`

via `CustomJWTAuthentication` (`envoy/custom_auth_check.py`) as configured under `REST_FRAMEWORK` `DEFAULT_AUTHENTICATION_CLASSES`.

---

## Environment variables (relevant)

| Variable | Role |
|----------|------|
| `JWT_SECRET` | Django `SECRET_KEY` / JWT signing key |
| `EXTERNAL_API_URL` | IdP user-info endpoint (e.g. `.../api/user-info`) |
| `BROKERAGE_FRONTEND_BASE_URL` | Base URL for invitation links in emails |
| `EMAIL_SENDING_API_URL` | Service that sends invitation HTML emails |
| DB vars | MySQL connection for `core_*` tables |

See `.env.example` for sample values.

---

## Sequence diagram

```mermaid
sequenceDiagram
    participant Admin as Admin client
    participant API as Core API
    participant DB as Database
    participant Mail as Email API
    participant FE as Frontend
    participant IdP as Identity provider
    participant User as Invited user

    Admin->>API: POST /api/users/invite
    API->>DB: INSERT core_user_invitations
    API->>Mail: POST invitation email
    Mail-->>User: Email with link
    User->>FE: Open link, sign in/up at IdP
    User->>API: POST /api/verify-invitation (idp_access_token, invitation)
    API->>IdP: GET EXTERNAL_API_URL (Bearer idp_access_token)
    IdP-->>API: user id, name, email
    API->>DB: INSERT or SELECT core_users; DELETE core_user_invitations
    API-->>User: access_token (JWT) + user
```

---

## Summary

1. **Invite** → row in `core_user_invitations` + email with `uid` in the link.  
2. **User** completes **IdP** authentication and obtains `idp_access_token`.  
3. **Verify** → IdP profile is fetched; **new** `core_users` row is created with invitation **role** and default **entity**, or an **existing** user is recognized by `idp_user_id`.  
4. **JWT** is issued with `RefreshToken.for_user(...)`; use **`Bearer`** + **`access_token`** for subsequent API calls.
