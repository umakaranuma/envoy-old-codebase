# User Management — API & UI Tasks

**Module:** Core
**Feature:** User Management
**Version:** 1.1
**Status:** Draft
**Stack:** Django · Django REST Framework · SimpleJWT · QueryBuilderService · ResponseService · ValidatorService
**Based on:** `user_management_requirements.md` + existing codebase patterns

---

## Table of Contents

1. [Database Tables](#1-database-tables)
2. [Data Relationship Diagram](#2-data-relationship-diagram)
3. [URL Route Reference](#3-url-route-reference)
4. [Flow 1 — Create User + Auto-Send Invitation](#4-flow-1--create-user--auto-send-invitation)
5. [Flow 2 — List Invited Users](#5-flow-2--list-invited-users)
6. [Flow 3 — Resend Invitation](#6-flow-3--resend-invitation)
7. [Flow 4 — Cancel Invitation](#7-flow-4--cancel-invitation)
8. [Flow 5 — Accept Invitation (External / IDP Registration)](#8-flow-5--accept-invitation-external--idp-registration)
9. [Flow 6 — List Users](#9-flow-6--list-users)
10. [Flow 7 — Get / Update Single User](#10-flow-7--get--update-single-user)
11. [Flow 8 — Deactivate / Reactivate User](#11-flow-8--deactivate--reactivate-user)
12. [Flow 9 — Delete User](#12-flow-9--delete-user)
13. [Flow 10 — Edit Own Profile (Self-Service)](#13-flow-10--edit-own-profile-self-service)
14. [UI Tasks — Users Screen](#14-ui-tasks--users-screen)
15. [UI Tasks — Invited Users Screen](#15-ui-tasks--invited-users-screen)
16. [UI Tasks — Registration Page (External)](#16-ui-tasks--registration-page-external)
17. [Permission Reference](#17-permission-reference)
18. [Audit Log Events](#18-audit-log-events)
19. [Non-Functional Requirements](#19-non-functional-requirements)

---

## 1. Database Tables

### 1.1 Table: `core_entity`

**Existing table.** Stores entity records. A `core_users` row holds an `entity_id` FK pointing here. On user registration via IDP, the default entity (`id=1`) is used via `get_or_create`.

```python
class CoreEntity(models.Model):
    type       = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='created_entities')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   related_name='updated_entities')
    class Meta:
        db_table = 'core_entity'
```

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `id` | `BIGINT` | No | auto | PK |
| `type` | `VARCHAR(100)` | No | — | e.g. `"Default Entity"`, `"Branch"` |
| `created_at` | `TIMESTAMP` | No | `NOW()` | Auto-set |
| `updated_at` | `TIMESTAMP` | No | `NOW()` | Auto-updated |
| `created_by_id` | `BIGINT` | Yes | NULL | FK → `core_users.id` |
| `updated_by_id` | `BIGINT` | Yes | NULL | FK → `core_users.id` |

**Seed requirement — ensure this row exists before any registration:**
```sql
INSERT INTO core_entity (id, type) VALUES (1, 'Default Entity')
ON CONFLICT (id) DO NOTHING;
```

---

### 1.2 Table: `core_users`

Primary user table. Stores all registered users. `role_id`, `first_name`, `last_name`, `display_name`, `email`, `entity_id`, `contact_no`, `picture`, and `code` are all stored here.

**How data arrives in this table:**
- `first_name`, `display_name`, `email`, `idp_user_id` — populated from the IDP response at registration time
- `role_id` — copied from `core_user_invitations.role_id` at registration
- `entity_id` — set to the default entity (`id=1`) via `get_or_create` at registration
- `code` — auto-generated via `generate_unique_user_code()` at registration
- `contact_no`, `picture`, `cover_pic`, address fields — populated later by the user via `PUT /api/users/me/profile` or by an admin via `PUT /api/users/{id}`

| Column | Type | Nullable | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `BIGINT` | No | auto | PK | — |
| `uid` | `UUID` | No | `uuid4()` | UNIQUE, NOT NULL | Public-safe identifier |
| `code` | `VARCHAR(20)` | Yes | NULL | UNIQUE | Auto-generated e.g. `U-AB1234`. Set at registration. |
| `title` | `VARCHAR(100)` | Yes | NULL | — | Salutation: Mr., Mrs., Ms., Miss., Dr., Prof., Other |
| `first_name` | `VARCHAR(80)` | No | — | NOT NULL | Set from IDP `name` on registration |
| `last_name` | `VARCHAR(80)` | Yes | NULL | — | Editable via profile update |
| `display_name` | `VARCHAR(80)` | No | — | NOT NULL | Shown to other users system-wide. Set from IDP `name` on registration. |
| `email` | `VARCHAR(254)` | No | — | UNIQUE, NOT NULL | Confirmed from IDP response at registration |
| `contact_no` | `VARCHAR(80)` | Yes | NULL | — | Includes country code e.g. `+94771234567`. Editable via profile. |
| `picture` | `VARCHAR(300)` | Yes | NULL | — | Profile image URL. Editable via profile or admin edit. |
| `cover_pic` | `VARCHAR(300)` | Yes | NULL | — | Cover image URL |
| `street_address` | `VARCHAR(255)` | Yes | NULL | — | — |
| `city` | `VARCHAR(100)` | Yes | NULL | — | — |
| `state` | `VARCHAR(100)` | Yes | NULL | — | — |
| `county` | `VARCHAR(100)` | Yes | NULL | — | — |
| `postal_code` | `VARCHAR(20)` | Yes | NULL | — | — |
| `idp_user_id` | `VARCHAR(255)` | Yes | NULL | UNIQUE | External Identity Provider user ID. Set at registration. |
| `role_id` | `BIGINT` | Yes | NULL | FK → `core_roles.id` | Copied from invitation at registration. Editable by admin. |
| `entity_id` | `BIGINT` | Yes | NULL | FK → `core_entity.id` | Set to default entity (`id=1`) at registration. References `core_entity`. |
| `status_id` | `BIGINT` | Yes | NULL | FK → `core_status.id` | Active / Inactive / Soft Deleted |
| `invited_by_id` | `BIGINT` | Yes | NULL | FK → `core_users.id` (self) | The admin who originally sent the invitation |
| `invited_at` | `TIMESTAMP` | Yes | NULL | — | Copied from `core_user_invitations.created_at` at registration |
| `registered_at` | `TIMESTAMP` | Yes | NULL | — | Set at registration. NULL means user has not yet accepted. |
| `deactivated_at` | `TIMESTAMP` | Yes | NULL | — | Set when status changes to Inactive |
| `soft_deleted_at` | `TIMESTAMP` | Yes | NULL | — | Set by auto soft-delete background job |
| `created_at` | `TIMESTAMP` | No | `NOW()` | NOT NULL | — |
| `updated_at` | `TIMESTAMP` | No | `NOW()` | NOT NULL, auto-update | — |

**Indexes:**

| Index Name | Columns | Purpose |
|---|---|---|
| `core_users_email_unique` | `email` | Enforce unique email |
| `core_users_uid_unique` | `uid` | Unique public identifier |
| `core_users_idp_user_id_unique` | `idp_user_id` | Prevent duplicate IDP registrations |
| `core_users_code_unique` | `code` | Unique user code |
| `core_users_status_id_idx` | `status_id` | Filter by status |
| `core_users_role_id_idx` | `role_id` | Join to core_roles |
| `core_users_entity_id_idx` | `entity_id` | Join to core_entity |
| `core_users_invited_by_idx` | `invited_by_id` | Lookup who invited a user |

**Django model — fields to verify or add to the existing model:**

```python
class User(AbstractBaseUser):
    uid             = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    code            = models.CharField(max_length=20, unique=True, null=True, blank=True)
    title           = models.CharField(max_length=100, null=True, blank=True)
    first_name      = models.CharField(max_length=80)
    last_name       = models.CharField(max_length=80, null=True, blank=True)
    display_name    = models.CharField(max_length=80)
    email           = models.EmailField(max_length=254, unique=True)
    contact_no      = models.CharField(max_length=80, null=True, blank=True)
    picture         = models.CharField(max_length=300, null=True, blank=True)
    cover_pic       = models.CharField(max_length=300, null=True, blank=True)
    street_address  = models.CharField(max_length=255, null=True, blank=True)
    city            = models.CharField(max_length=100, null=True, blank=True)
    state           = models.CharField(max_length=100, null=True, blank=True)
    county          = models.CharField(max_length=100, null=True, blank=True)
    postal_code     = models.CharField(max_length=20, null=True, blank=True)
    idp_user_id     = models.CharField(max_length=255, unique=True, null=True, blank=True)

    # FK relationships
    role    = models.ForeignKey('Role',       on_delete=models.SET_NULL, null=True, blank=True)
    entity  = models.ForeignKey('CoreEntity', on_delete=models.SET_NULL, null=True, blank=True)
    status  = models.ForeignKey('Status',     on_delete=models.SET_NULL, null=True, blank=True)
    invited_by = models.ForeignKey('self', on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='invited_users')

    # Lifecycle timestamps
    invited_at      = models.DateTimeField(null=True, blank=True)
    registered_at   = models.DateTimeField(null=True, blank=True)
    deactivated_at  = models.DateTimeField(null=True, blank=True)
    soft_deleted_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_users'
```

---

### 1.3 Table: `core_user_invitations`

Stores all invitations. A pending invitation lives here until accepted (deleted), cancelled (retained with `status='cancelled'`), or expired (status updated to `'expired'`).

```python
class UserInvitation(models.Model):
    uid          = models.CharField(max_length=32, unique=True)  # UUID hex32, no hyphens
    name         = models.CharField(max_length=150)
    email        = models.EmailField(max_length=254)
    role         = models.ForeignKey('Role', on_delete=models.SET_NULL, null=True)
    invited_by   = models.ForeignKey('User', on_delete=models.SET_NULL, null=True,
                                     related_name='sent_invitations')
    status       = models.CharField(max_length=20, default='pending')
    expires_at   = models.DateTimeField()
    resent_at    = models.DateTimeField(null=True, blank=True)
    resent_count = models.IntegerField(default=0)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey('User', on_delete=models.SET_NULL,
                                     null=True, blank=True,
                                     related_name='cancelled_invitations')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'core_user_invitations'
```

| Column | Type | Nullable | Default | Constraints | Notes |
|---|---|---|---|---|---|
| `id` | `BIGINT` | No | auto | PK | — |
| `uid` | `VARCHAR(32)` | No | — | UNIQUE, NOT NULL | UUID hex32. Regenerated on resend. |
| `name` | `VARCHAR(150)` | No | — | NOT NULL | Invitee name entered by admin |
| `email` | `VARCHAR(254)` | No | — | NOT NULL | Invitee email |
| `role_id` | `BIGINT` | Yes | NULL | FK → `core_roles.id` | Copied to `core_users.role_id` on registration |
| `invited_by_id` | `BIGINT` | Yes | NULL | FK → `core_users.id` | Admin who created the invitation |
| `status` | `VARCHAR(20)` | No | `'pending'` | NOT NULL | `pending` · `expired` · `cancelled` |
| `expires_at` | `TIMESTAMP` | No | — | NOT NULL | `created_at + 72 hrs` by default |
| `resent_at` | `TIMESTAMP` | Yes | NULL | — | Timestamp of most recent resend |
| `resent_count` | `INT` | No | `0` | NOT NULL | Total resend count |
| `cancelled_at` | `TIMESTAMP` | Yes | NULL | — | Set when admin cancels |
| `cancelled_by_id` | `BIGINT` | Yes | NULL | FK → `core_users.id` | Who cancelled |
| `created_at` | `TIMESTAMP` | No | `NOW()` | NOT NULL | — |
| `updated_at` | `TIMESTAMP` | No | `NOW()` | NOT NULL, auto-update | — |

**Indexes:**

| Index Name | Columns | Purpose |
|---|---|---|
| `cui_uid_unique` | `uid` | Lookup from invitation link |
| `cui_email_idx` | `email` | Duplicate pending check |
| `cui_status_idx` | `status` | Filter list |
| `cui_expires_at_idx` | `expires_at` | Background expiry job |

**Lifecycle rules:**

| Event | What happens to this row |
|---|---|
| User accepts | Row **hard deleted**. Data written to `core_users`. |
| Admin cancels | Row **retained**. `status='cancelled'`, `cancelled_at`, `cancelled_by_id` set. |
| Admin resends | Row **updated**: new `uid`, new `expires_at`, `status='pending'`, `resent_at=NOW()`, `resent_count+=1`. |
| Link expires | `status='expired'` (lazy update on list load or background job). |
| Re-invite attempt on registered user | Blocked at API. Check `core_users.registered_at IS NOT NULL` for matching email. |

---

### 1.4 Table: `core_status`

Existing table. Required status seed records for user management:

| `name` | `type_code` | `color` | Used for |
|---|---|---|---|
| `Active` | `user_active` | `#067647` | Registered users who can log in |
| `Inactive` | `user_inactive` | `#344054` | Deactivated users |
| `Soft Deleted` | `user_soft_deleted` | `#6c757d` | Auto-soft-deleted after 90 days inactive |

---

### 1.5 Table: `core_audit_logs`

Central audit table. Create if not yet present.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `id` | `BIGINT` | No | auto | PK |
| `actor_id` | `BIGINT` | Yes | NULL | FK → `core_users.id`. NULL for system actions. |
| `actor_name` | `VARCHAR(150)` | Yes | NULL | Snapshot of `display_name` at time of action |
| `action` | `VARCHAR(100)` | No | — | Event key e.g. `invitation.created`, `user.deactivated` |
| `entity_type` | `VARCHAR(100)` | No | — | e.g. `user`, `invitation` |
| `entity_id` | `BIGINT` | Yes | NULL | PK of affected record |
| `payload` | `JSONB` | Yes | NULL | Before/after snapshot or event context |
| `ip_address` | `VARCHAR(45)` | Yes | NULL | Actor IP |
| `created_at` | `TIMESTAMP` | No | `NOW()` | — |

---

### 1.6 Table: `core_in_app_notifications`

In-app notifications. Notifies the inviting admin when their invitee registers.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `id` | `BIGINT` | No | auto | PK |
| `recipient_id` | `BIGINT` | No | — | FK → `core_users.id` |
| `type` | `VARCHAR(100)` | No | — | e.g. `invitation.accepted` |
| `title` | `VARCHAR(255)` | No | — | Short heading |
| `body` | `TEXT` | Yes | NULL | Detail text |
| `payload` | `JSONB` | Yes | NULL | e.g. `{"registered_user_id": 42}` |
| `read_at` | `TIMESTAMP` | Yes | NULL | NULL = unread |
| `created_at` | `TIMESTAMP` | No | `NOW()` | — |

---

## 2. Data Relationship Diagram

```
core_entity (db_table = 'core_entity')
  id ◄──────────────────────────── core_users.entity_id
  created_by_id ────────────────── core_users.id (FK)
  updated_by_id ────────────────── core_users.id (FK)

core_roles
  id ◄──────────────────────────── core_users.role_id
  id ◄──────────────────────────── core_user_invitations.role_id

core_status
  id ◄──────────────────────────── core_users.status_id

core_users
  id ◄──────────────────────────── core_users.invited_by_id       (self FK)
  id ◄──────────────────────────── core_user_invitations.invited_by_id
  id ◄──────────────────────────── core_user_invitations.cancelled_by_id
  id ◄──────────────────────────── core_in_app_notifications.recipient_id
  id ◄──────────────────────────── core_audit_logs.actor_id
```

**What gets written to each table during the IDP registration flow:**

```
Step 1 — Admin sends invite
  → INSERT core_user_invitations
      uid, name, email, role_id, invited_by_id, status='pending', expires_at

Step 2 — User accepts via IDP
  → GET/CREATE core_entity WHERE id=1
  → GET core_roles WHERE id = invitation.role_id
  → GET core_status WHERE type_code = 'user_active'
  → INSERT core_users
      first_name    = IDP response name
      display_name  = IDP response name
      email         = IDP response email
      idp_user_id   = IDP response id
      role_id       = invitation.role_id         ← from core_user_invitations
      entity_id     = 1                          ← from core_entity
      status_id     = active_status.id           ← from core_status
      code          = generate_unique_user_code()
      invited_by_id = invitation.invited_by_id
      invited_at    = invitation.created_at
      registered_at = NOW()
  → DELETE core_user_invitations (row removed)
  → INSERT core_in_app_notifications (to invited_by user)
  → INSERT core_audit_logs
```

---

## 3. URL Route Reference

Register in `urls.py` in this exact order. The `me` route must come before `<int:user_id>`.

```python
from django.urls import path
from .views.user_views import (
    create_user_and_invite,
    get_user_invitations,
    resend_user_invitation,
    cancel_user_invitation,
    accept_invitation,
    get_users,
    user_detail,
    deactivate_user,
    reactivate_user,
    delete_user,
    update_own_profile,
)

urlpatterns = [
    # ── Invitations ──────────────────────────────────────────────────────────
    path("api/users/invite",
         create_user_and_invite,       name="create_user_and_invite"),
    path("api/invitations",
         get_user_invitations,          name="get_user_invitations"),
    path("api/invitations/<str:uid>/resend",
         resend_user_invitation,        name="resend_user_invitation"),
    path("api/invitations/<str:uid>/cancel",
         cancel_user_invitation,        name="cancel_user_invitation"),

    # ── Registration (Public — no auth required) ──────────────────────────────
    path("api/verify-invitation",
         accept_invitation,             name="accept_invitation"),

    # ── Self-Service Profile (MUST be before <int:user_id>) ──────────────────
    path("api/users/me/profile",
         update_own_profile,            name="update_own_profile"),

    # ── Users ────────────────────────────────────────────────────────────────
    path("api/users",
         get_users,                     name="get_users"),
    path("api/users/<int:user_id>",
         user_detail,                   name="user_detail"),
    path("api/users/<int:user_id>/deactivate",
         deactivate_user,               name="deactivate_user"),
    path("api/users/<int:user_id>/reactivate",
         reactivate_user,               name="reactivate_user"),
    path("api/users/<int:user_id>/delete",
         delete_user,                   name="delete_user"),
]
```

---

## 4. Flow 1 — Create User + Auto-Send Invitation

### Overview

Admin provides `name`, `email`, `role_id`. System inserts into `core_user_invitations` and sends the email. No `core_users` row is created yet — the user row is written only when the invitee completes IDP registration.

---

### API: `POST /api/users/invite`

**Permission required:** `users.create`
**View function:** `create_user_and_invite`

**Request body:**
```json
{
  "name": "Jane Smith",
  "email": "jane.smith@example.com",
  "role_id": 3
}
```

**Validation rules:**
```python
rules = {
    "name":    "required|max:150",
    "email":   "required|email|max:254",
    "role_id": "required|exists:core_roles,id",
}
custom_messages = {
    "name.required":    "Name cannot be empty.",
    "name.max":         "Name cannot exceed 150 characters.",
    "email.required":   "Email cannot be empty.",
    "email.email":      "Please enter a valid email address.",
    "email.max":        "Email cannot exceed 254 characters.",
    "role_id.required": "Role is required.",
    "role_id.exists":   "The selected role does not exist.",
}
```

**Backend logic — step by step:**

| Step | Action | Table |
|---|---|---|
| 1 | Verify actor has `users.create` permission | `core_users`, `core_roles` |
| 2 | Run `ValidatorService.validate(data, rules, custom_messages)` | — |
| 3 | `User.objects.filter(email=data["email"]).exists()` → if True → `VALIDATION_ERROR`: `email_already_registered` | `core_users` |
| 4 | `UserInvitation.objects.filter(email=data["email"], status='pending').exists()` → if True → `VALIDATION_ERROR`: `email_already_has_invitation` | `core_user_invitations` |
| 5 | `role = Role.objects.get(id=data["role_id"])` | `core_roles` |
| 6 | `uid = uuid.uuid4().hex` (32-char hex, no hyphens) | — |
| 7 | `expiry_hours` = read from settings (default 72). `expires_at = timezone.now() + timedelta(hours=expiry_hours)` | `settings` |
| 8 | `invitation = UserInvitation.objects.create(uid=uid, name=name, email=email, role=role, invited_by=request.user, status='pending', expires_at=expires_at)` | `core_user_invitations` |
| 9 | `send_invitation_email(invitation, role, "invitation_email_template.html", "You're Invited!")` | Email service |
| 10 | Write `core_audit_logs`: `action='invitation.created'`, `entity_type='invitation'`, `entity_id=invitation.id`, `payload={name, email, role_id}` | `core_audit_logs` |

**Invitation link (built inside `send_invitation_email`):**
```
{BROKERAGE_FRONTEND_BASE_URL}/user-invitation?invitation={uid}&name={name}&email={email}&role_id={role.id}&role_name={role.name}
```

**Success response — `200 OK`:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "invitation_sent_successfully",
  "result": {
    "uid": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
    "name": "Jane Smith",
    "email": "jane.smith@example.com",
    "role": { "id": 3, "name": "Sales Agent" },
    "status": "pending",
    "expires_at": "2026-03-23T10:00:00Z",
    "created_at": "2026-03-20T10:00:00Z"
  }
}
```

**Error responses:**

| Scenario | Code | Message key |
|---|---|---|
| Any field fails | `VALIDATION_ERROR` | Field-level errors |
| Email in `core_users` | `VALIDATION_ERROR` | `email_already_registered` |
| Pending invitation for email | `VALIDATION_ERROR` | `email_already_has_invitation` |
| Role not found | `VALIDATION_ERROR` | `role_id.exists` |
| Actor lacks `users.create` | `FORBIDDEN` | `forbidden` |

---

## 5. Flow 2 — List Invited Users

### API: `GET /api/invitations`

**Permission required:** `users.invite.manage`
**View function:** `get_user_invitations`

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `search` | string | — | Matches `name` or `email` |
| `status` | string | — | `pending` or `expired` |
| `page` | int | 1 | — |
| `per_page` | int | 10 | — |
| `sort_by` | string | `created_at` | — |
| `sort_dir` | string | `desc` | — |

**Backend logic:**

| Step | Action | Table |
|---|---|---|
| 1 | Check `users.invite.manage` | — |
| 2 | Lazy expiry: `UserInvitation.objects.filter(status='pending', expires_at__lt=timezone.now()).update(status='expired')` | `core_user_invitations` |
| 3 | Query `core_user_invitations` WHERE `status IN ('pending', 'expired')` via `QueryBuilderService` | `core_user_invitations` |
| 4 | LEFT JOIN `core_roles` on `role_id` | `core_roles` |
| 5 | LEFT JOIN `core_users as inv_by` on `invited_by_id` | `core_users` |
| 6 | Apply search, status filter, pagination | — |

**SELECT columns:**
```python
all_columns = [
    "core_user_invitations.id",
    "core_user_invitations.uid",
    "core_user_invitations.name",
    "core_user_invitations.email",
    "core_user_invitations.status",
    "core_user_invitations.expires_at",
    "core_user_invitations.resent_at",
    "core_user_invitations.resent_count",
    "core_user_invitations.created_at",
    "core_roles.id as role_id",
    "core_roles.name as role_name",
    "inv_by.id as invited_by_id",
    "inv_by.display_name as invited_by_name",
]
```

**JOINs:**
```python
.leftJoin("core_roles", "core_roles.id", "core_user_invitations.role_id")
.leftJoin("core_users as inv_by", "inv_by.id", "core_user_invitations.invited_by_id")
```

**Success response — `200 OK`:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "Invitations fetched successfully.",
  "result": {
    "current_page": 1,
    "last_page": 2,
    "total_records": 14,
    "count": 10,
    "data": [
      {
        "id": 5,
        "uid": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4",
        "name": "Jane Smith",
        "email": "jane.smith@example.com",
        "status": "pending",
        "role_id": 3,
        "role_name": "Sales Agent",
        "invited_by_id": 1,
        "invited_by_name": "Admin User",
        "expires_at": "2026-03-23T10:00:00Z",
        "resent_count": 0,
        "created_at": "2026-03-20T10:00:00Z"
      }
    ]
  }
}
```

---

## 6. Flow 3 — Resend Invitation

### API: `POST /api/invitations/<str:uid>/resend`

**Permission required:** `users.invite.manage`
**View function:** `resend_user_invitation`

**Backend logic:**

| Step | Action | Table |
|---|---|---|
| 1 | Check `users.invite.manage` | — |
| 2 | `uid = uid_param.replace("-", "")` | — |
| 3 | `invitation = UserInvitation.objects.get(uid=uid)` — `NOT_FOUND` if missing | `core_user_invitations` |
| 4 | If `invitation.status == 'cancelled'` → `VALIDATION_ERROR`: `invitation_already_cancelled` | — |
| 5 | `User.objects.filter(email=invitation.email, registered_at__isnull=False).exists()` → `VALIDATION_ERROR`: `user_already_registered` | `core_users` |
| 6 | `new_uid = uuid.uuid4().hex` | — |
| 7 | `new_expires_at = timezone.now() + timedelta(hours=expiry_hours)` | `settings` |
| 8 | Update: `invitation.uid=new_uid`, `invitation.expires_at=new_expires_at`, `invitation.status='pending'`, `invitation.resent_at=timezone.now()`, `invitation.resent_count+=1`; `.save()` | `core_user_invitations` |
| 9 | `send_invitation_email(invitation, invitation.role, "invitation_email_template.html", "Your Invitation Has Been Resent")` | Email service |
| 10 | Write `core_audit_logs`: `action='invitation.resent'`, payload=`{new_uid, new_expires_at, resent_count, resent_by_id}` | `core_audit_logs` |

**Success response — `200 OK`:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "invitation_resent_successfully",
  "result": {
    "uid": "new32hexuid",
    "expires_at": "2026-03-23T11:30:00Z",
    "resent_count": 1
  }
}
```

**Error responses:**

| Scenario | Code | Message key |
|---|---|---|
| UID not found | `NOT_FOUND` | `invitation_not_found` |
| Invitation cancelled | `VALIDATION_ERROR` | `invitation_already_cancelled` |
| User already registered | `VALIDATION_ERROR` | `user_already_registered` |
| Actor lacks permission | `FORBIDDEN` | `forbidden` |

---

## 7. Flow 4 — Cancel Invitation

### API: `POST /api/invitations/<str:uid>/cancel`

**Permission required:** `users.invite.manage`
**View function:** `cancel_user_invitation`

**Backend logic:**

| Step | Action | Table |
|---|---|---|
| 1 | Check `users.invite.manage` | — |
| 2 | `uid = uid_param.replace("-", "")` | — |
| 3 | `invitation = UserInvitation.objects.get(uid=uid)` — `NOT_FOUND` if missing | `core_user_invitations` |
| 4 | If `status == 'cancelled'` → `VALIDATION_ERROR`: `invitation_already_cancelled` | — |
| 5 | `User.objects.filter(email=invitation.email, registered_at__isnull=False).exists()` → `VALIDATION_ERROR`: `user_already_registered` | `core_users` |
| 6 | Update: `invitation.status='cancelled'`, `invitation.cancelled_at=timezone.now()`, `invitation.cancelled_by=request.user`; `.save()` | `core_user_invitations` |
| 7 | Write `core_audit_logs`: `action='invitation.cancelled'`, payload=`{cancelled_by_id, email, name}` | `core_audit_logs` |

**Success response — `200 OK`:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "invitation_cancelled_successfully",
  "result": {
    "uid": "a1b2c3d4...",
    "status": "cancelled",
    "cancelled_at": "2026-03-20T12:00:00Z"
  }
}
```

---

## 8. Flow 5 — Accept Invitation (External / IDP Registration)

### Overview

Public endpoint. Invitee authenticates with IDP, then POSTs their `idp_access_token` + `invitation` UID. Server validates the invitation, calls the IDP, then writes the full user record to `core_users` using data from both the IDP response and the invitation row.

**This is the only place `role_id`, `entity_id`, `first_name`, `display_name`, `email`, `code`, and `idp_user_id` are written to `core_users`.**

---

### API: `POST /api/verify-invitation`

**Authentication:** None (public)
**View function:** `accept_invitation`

**Request body:**
```json
{
  "idp_access_token": "eyJ...",
  "invitation": "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4"
}
```

**Validation rules:**
```python
rules = {
    "idp_access_token": "required",
    "invitation":       "required",
}
```

**Backend logic — step by step:**

| Step | Action | Table |
|---|---|---|
| 1 | Validate `idp_access_token` and `invitation` present | — |
| 2 | `uid = invitation_uid.replace("-", "")` | — |
| 3 | Validate UUID format with `uuid.UUID(invitation_uid)` — `VALIDATION_ERROR`: `invalid_invitation_uuid_format` on failure | — |
| 4 | `UserInvitation.objects.filter(uid=uid).exists()` — `VALIDATION_ERROR`: `invitation_does_not_exist` if False | `core_user_invitations` |
| 5 | `invitation = UserInvitation.objects.get(uid=uid)` | `core_user_invitations` |
| 6 | If `invitation.status == 'cancelled'` → `VALIDATION_ERROR`: `invitation_cancelled` | — |
| 7 | If `invitation.expires_at < timezone.now()` → update `status='expired'`, `.save()` → `VALIDATION_ERROR`: `invitation_expired` | `core_user_invitations` |
| 8 | `response = requests.get(EXTERNAL_API_URL, headers={"Authorization": f"Bearer {idp_access_token}"})` | External IDP |
| 9 | Parse: `idp_user_id`, `name`, `email` from `response["result"]` | — |
| 10 | Validate `idp_user_id` present — `VALIDATION_ERROR`: `invalid_idp_response` if missing | — |
| **— Returning user path (`User.objects.filter(idp_user_id=idp_user_id).exists()` = True):** | | |
| 11a | Delete invitation: `invitation.delete()` | `core_user_invitations` |
| 11b | JWT: `refresh = RefreshToken.for_user(existing_user)` | SimpleJWT |
| 11c | Return token + user object | — |
| **— New user path:** | | |
| 12a | `role = Role.objects.get(id=invitation.role_id)` | `core_roles` |
| 12b | `entity, _ = CoreEntity.objects.get_or_create(id=1, defaults={"type": "Default Entity"})` | `core_entity` |
| 12c | `active_status = Status.objects.get(type_code='user_active')` | `core_status` |
| 12d | `code = generate_unique_user_code()` | `core_users` |
| 12e | `user = User.objects.create(first_name=name, display_name=name, email=email, idp_user_id=idp_user_id, role=role, entity=entity, status=active_status, code=code, registered_at=timezone.now(), invited_by_id=invitation.invited_by_id, invited_at=invitation.created_at)` | `core_users` |
| 12f | `invitation.delete()` | `core_user_invitations` |
| 12g | Create notification for `invitation.invited_by_id`: type=`invitation.accepted`, title=`"Invitation Accepted"`, body=`"{name} has registered and is now active."`, payload=`{"registered_user_id": user.id}` | `core_in_app_notifications` |
| 12h | Write `core_audit_logs`: `action='user.registered'`, `entity_id=user.id`, payload=`{email, role_id, entity_id, code, registered_at}` | `core_audit_logs` |
| 12i | JWT: `refresh = RefreshToken.for_user(user)` | SimpleJWT |
| 12j | Return token + user object | — |

**Success response — `200 OK` (both paths):**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "invitation_accepted_successfully",
  "result": {
    "access_token": "eyJ...",
    "user": {
      "id": 42,
      "first_name": "Jane",
      "display_name": "Jane Smith",
      "email": "jane.smith@example.com",
      "idp_user_id": "idp_abc123",
      "code": "U-AB1234",
      "role":   { "id": 3, "name": "Sales Agent" },
      "entity": { "id": 1, "type": "Default Entity" }
    }
  }
}
```

**Error responses:**

| Scenario | Code | Message key |
|---|---|---|
| Missing fields | `VALIDATION_ERROR` | field-level |
| Malformed UUID | `VALIDATION_ERROR` | `invalid_invitation_uuid_format` |
| Invitation not found | `VALIDATION_ERROR` | `invitation_does_not_exist` |
| Invitation cancelled | `VALIDATION_ERROR` | `invitation_cancelled` |
| Invitation expired | `VALIDATION_ERROR` | `invitation_expired` |
| IDP call fails | `INTERNAL_SERVER_ERROR` | `idp_authentication_failed` |
| `idp_user_id` missing | `VALIDATION_ERROR` | `invalid_idp_response` |

---

## 9. Flow 6 — List Users

### API: `GET /api/users`

**Permission required:** `users.view`
**View function:** `get_users`

**Query parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `search` | string | — | `first_name`, `last_name`, `display_name`, `email`, `code`, `role_name` |
| `filters` | JSON string | `{}` | Key-value map (see alias map below) |
| `page` | int | 1 | — |
| `per_page` | int | 10 | — |
| `sort_by` | string | `id` | — |
| `sort_dir` | string | `desc` | — |

**Filter alias map:**
```python
filter_aliases = {
    "first_name":   "core_users.first_name",
    "last_name":    "core_users.last_name",
    "display_name": "core_users.display_name",
    "email":        "core_users.email",
    "contact_no":   "core_users.contact_no",
    "role_id":      "core_users.role_id",
    "role_name":    "core_roles.name",
    "status_id":    "core_users.status_id",
    "team_id":      "core_teams.name",
}
```

**SELECT columns:**
```python
all_columns = [
    "core_users.id",
    "core_users.uid",
    "core_users.code",
    "core_users.title",
    "core_users.first_name",
    "core_users.last_name",
    "core_users.display_name",
    "core_users.email",
    "core_users.contact_no",
    "core_users.picture",
    "core_users.idp_user_id",
    "core_users.role_id",
    "core_users.entity_id",
    "core_users.status_id",
    "core_users.invited_at",
    "core_users.registered_at",
    "core_users.deactivated_at",
    "core_roles.name as role_name",
    "core_entity.type as entity_type",     # NOTE: table is core_entity, not core_entity
    "core_status.name as status_name",
    "core_status.color as status_color",
    "core_teams.name as team_name",
    "inv_by.id as invited_by_id",
    "inv_by.display_name as invited_by_name",
]
```

**JOINs:**
```python
.leftJoin("core_roles",      "core_roles.id",          "core_users.role_id")
.leftJoin("core_entity",     "core_entity.id",          "core_users.entity_id")  # core_entity
.leftJoin("core_status",     "core_status.id",          "core_users.status_id")
.leftJoin("core_team_users", "core_team_users.user_id", "core_users.id")
.leftJoin("core_teams",      "core_teams.id",           "core_team_users.team_id")
.leftJoin("core_users as inv_by", "inv_by.id",          "core_users.invited_by_id")
.groupBy("core_users.id")
```

**Always-on WHERE clause — exclude unregistered and soft-deleted:**
```python
.whereNotNull("core_users.registered_at")
.whereIn("core_users.status_id", [active_status_id, inactive_status_id])
```

**Success response — `200 OK`:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "Users fetched successfully.",
  "result": {
    "current_page": 1,
    "last_page": 5,
    "total_records": 85,
    "count": 10,
    "data": [
      {
        "id": 42,
        "uid": "a1b2c3d4...",
        "code": "U-AB1234",
        "title": "Ms.",
        "first_name": "Jane",
        "last_name": "Smith",
        "display_name": "Jane S.",
        "email": "jane.smith@example.com",
        "contact_no": "+94771234567",
        "picture": null,
        "role_id": 3,
        "role_name": "Sales Agent",
        "entity_id": 1,
        "entity_type": "Default Entity",
        "status_id": 1,
        "status_name": "Active",
        "status_color": "#067647",
        "team_name": "South Region",
        "invited_by_id": 1,
        "invited_by_name": "Admin User",
        "registered_at": "2026-03-21T08:00:00Z"
      }
    ]
  }
}
```

---

## 10. Flow 7 — Get / Update Single User

### 10.1 GET `/api/users/<int:user_id>`

**Permission required:** `users.view`
**View function:** `user_detail` (GET branch)

Uses same SELECT columns and JOINs as Flow 6, plus:
```python
"core_users.cover_pic",
"core_users.street_address",
"core_users.city",
"core_users.state",
"core_users.county",
"core_users.postal_code",
"core_users.soft_deleted_at",
```

Return `NOT_FOUND` if `User.objects.filter(id=user_id).exists()` is False.

---

### 10.2 PUT `/api/users/<int:user_id>`

**Permission required:** `users.edit`
**View function:** `user_detail` (PUT branch)

**Request body:**
```json
{
  "title": "Ms.",
  "first_name": "Jane",
  "last_name": "Smith",
  "display_name": "Jane S.",
  "email": "jane.updated@example.com",
  "contact_no": "+94771234567",
  "picture": "https://cdn.example.com/pic.jpg",
  "cover_pic": "https://cdn.example.com/cover.jpg",
  "street_address": "123 Main St",
  "city": "Colombo",
  "state": "Western",
  "county": "Sri Lanka",
  "postal_code": "00100",
  "role_id": 4,
  "status_id": 1,
  "code": "U-XY9876"
}
```

**Validation rules:**
```python
rules = {
    "title":          "required|max:100",
    "first_name":     "required|max:80",
    "last_name":      "nullable|max:80",
    "display_name":   "required|max:80",
    "email":          f"required|email|max:254|unique:core_users,email,{user.id}",
    "contact_no":     "nullable|max:80",
    "picture":        "nullable|max:300",
    "cover_pic":      "nullable|max:300",
    "street_address": "nullable|max:255",
    "city":           "nullable|max:100",
    "state":          "nullable|max:100",
    "county":         "nullable|max:100",
    "postal_code":    "nullable|max:20",
    "role_id":        "required|exists:core_roles,id",
    "status_id":      "nullable|exists:core_status,id",
    "code":           f"nullable|unique:core_users,code,{user.id}",
}
```

**Additional logic to add to existing PUT handler:**

| Step | Action | Table |
|---|---|---|
| — | Snapshot `{title, first_name, last_name, email, role_id, status_id, code, contact_no}` before changes | — |
| — | If `status_id` → `user_inactive` id: set `user.deactivated_at = timezone.now()` | `core_users` |
| — | If `status_id` → `user_active` id: clear `user.deactivated_at = None` | `core_users` |
| — | After `.save()`: write `core_audit_logs` with `action='user.updated'`, payload=`{before, after}` | `core_audit_logs` |

**Note:** `entity_id` is **not** editable through this endpoint. It is set once at registration.

**Success response — `200 OK`:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "user_updated_successfully",
  "result": {
    "id": 42,
    "title": "Ms.",
    "first_name": "Jane",
    "last_name": "Smith",
    "display_name": "Jane S.",
    "email": "jane.updated@example.com",
    "contact_no": "+94771234567",
    "picture": null,
    "cover_pic": null,
    "code": "U-AB1234",
    "role":   { "id": 4, "name": "Team Lead" },
    "entity": { "id": 1, "type": "Default Entity" }
  }
}
```

---

## 11. Flow 8 — Deactivate / Reactivate User

### 11.1 POST `/api/users/<int:user_id>/deactivate`

**Permission required:** `users.deactivate`
**View function:** `deactivate_user`

| Step | Action | Table |
|---|---|---|
| 1 | Check `users.deactivate` permission | — |
| 2 | `user = User.objects.get(id=user_id)` — `NOT_FOUND` if missing | `core_users` |
| 3 | Guard: actor cannot deactivate themselves | — |
| 4 | Check `user.status.type_code == 'user_active'` — if not → `VALIDATION_ERROR`: `user_not_active` | `core_status` |
| 5 | `inactive_status = Status.objects.get(type_code='user_inactive')` | `core_status` |
| 6 | `user.status = inactive_status`; `user.deactivated_at = timezone.now()`; `.save()` | `core_users` |
| 7 | Invalidate active JWT sessions for this user if using token blacklist | Auth |
| 8 | Write `core_audit_logs`: `action='user.deactivated'` | `core_audit_logs` |

**Success response:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "user_deactivated_successfully",
  "result": { "id": 42, "status_name": "Inactive", "deactivated_at": "2026-03-21T11:00:00Z" }
}
```

---

### 11.2 POST `/api/users/<int:user_id>/reactivate`

**Permission required:** `users.deactivate`
**View function:** `reactivate_user`

| Step | Action | Table |
|---|---|---|
| 1 | Check `users.deactivate` | — |
| 2 | `user = User.objects.get(id=user_id)` — `NOT_FOUND` if missing | `core_users` |
| 3 | Check `user.status.type_code == 'user_inactive'` — if not → `VALIDATION_ERROR`: `user_not_inactive` | — |
| 4 | `active_status = Status.objects.get(type_code='user_active')` | `core_status` |
| 5 | `user.status = active_status`; `user.deactivated_at = None`; `.save()` | `core_users` |
| 6 | Write `core_audit_logs`: `action='user.reactivated'` | `core_audit_logs` |

**Success response:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "user_reactivated_successfully",
  "result": { "id": 42, "status_name": "Active" }
}
```

---

## 12. Flow 9 — Delete User

### DELETE `/api/users/<int:user_id>/delete`

**Permission required:** `users.delete`
**View function:** `delete_user`
**Request body:** `{ "confirm": true }`

| Step | Action | Table |
|---|---|---|
| 1 | Check `users.delete` | — |
| 2 | `user = User.objects.get(id=user_id)` — `NOT_FOUND` if missing | `core_users` |
| 3 | `request.data.get("confirm") != True` → `VALIDATION_ERROR`: `confirmation_required` | — |
| 4 | Snapshot: `{first_name, display_name, email, role_id, entity_id, status_id, code}` | — |
| 5 | Write `core_audit_logs` **before deletion**: `action='user.deleted'`, payload=`{snapshot}` | `core_audit_logs` |
| 6 | `user.delete()` | `core_users` |

**Success response:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "user_deleted_successfully",
  "result": null
}
```

---

## 13. Flow 10 — Edit Own Profile (Self-Service)

### PUT `/api/users/me/profile`

**Authentication:** Any active user — no permission key required
**View function:** `update_own_profile`

**Editable fields:** `title`, `first_name`, `last_name`, `display_name`, `contact_no`, `picture`, `cover_pic`, `street_address`, `city`, `state`, `county`, `postal_code`

**Fields this endpoint must NEVER update (guard explicitly):**
`email`, `role_id`, `entity_id`, `status_id`, `code`, `idp_user_id`

**Request body:**
```json
{
  "title": "Ms.",
  "first_name": "Jane",
  "last_name": "Smith",
  "display_name": "Jane S.",
  "contact_no": "+94771234567",
  "picture": "https://cdn.example.com/pic.jpg",
  "cover_pic": "https://cdn.example.com/cover.jpg",
  "street_address": "123 Main St",
  "city": "Colombo",
  "state": "Western",
  "county": "Sri Lanka",
  "postal_code": "00100"
}
```

**Validation rules:**
```python
rules = {
    "title":          "nullable|max:100",
    "first_name":     "required|max:80",
    "last_name":      "nullable|max:80",
    "display_name":   "required|max:80",
    "contact_no":     "nullable|max:80",
    "picture":        "nullable|max:300",
    "cover_pic":      "nullable|max:300",
    "street_address": "nullable|max:255",
    "city":           "nullable|max:100",
    "state":          "nullable|max:100",
    "county":         "nullable|max:100",
    "postal_code":    "nullable|max:20",
}
```

**Backend logic:**

| Step | Action | Table |
|---|---|---|
| 1 | `user = request.user` — confirm `user.status.type_code == 'user_active'` | `core_users` |
| 2 | Validate | — |
| 3 | If `display_name` not supplied → `display_name = (first_name + " " + (last_name or "")).strip()` | — |
| 4 | Apply fields to `user`; `.save()` | `core_users` |
| 5 | Write `core_audit_logs`: `action='user.profile_updated'`, payload=`{changed_fields: [...]}` | `core_audit_logs` |

**Success response:**
```json
{
  "is_success": true,
  "status_code": 200,
  "message": "profile_updated_successfully",
  "result": {
    "id": 42,
    "title": "Ms.",
    "first_name": "Jane",
    "last_name": "Smith",
    "display_name": "Jane S.",
    "contact_no": "+94771234567",
    "picture": "https://cdn.example.com/pic.jpg"
  }
}
```

---

## 14. UI Tasks — Users Screen

### 14.1 Page Layout (`/users`)

- Page heading: **"Users"**
- Two tabs at top of page:
  - **Tab 1 — "Users"** — registered users (active + inactive)
  - **Tab 2 — "Invited Users"** — pending/expired invitations (only rendered if actor has `users.invite.manage`)
- **"Invite User" button** — top right — only rendered if actor has `users.create`

---

### 14.2 Users Table (Tab 1)

Data from `GET /api/users`

| Column | Source | Notes |
|---|---|---|
| Code | `code` | e.g. `U-AB1234` |
| Name | `display_name` | Clickable → user detail |
| Email | `email` | — |
| Contact No. | `contact_no` | — |
| Role | `role_name` | — |
| Entity | `entity_type` | From `core_entity.type` via `entity_id` |
| Team | `team_name` | — |
| Status | `status_name` | Colour badge using `status_color` |
| Invited By | `invited_by_name` | — |
| Registered On | `registered_at` | Formatted date |
| Actions | — | Conditional |

**Action button rules:**

| Button | Condition |
|---|---|
| Edit | Actor has `users.edit` |
| Deactivate | Actor has `users.deactivate` AND `status_name = 'Active'` |
| Reactivate | Actor has `users.deactivate` AND `status_name = 'Inactive'` |
| Delete | Actor has `users.delete` |

---

### 14.3 Invite User Modal

| Field | Type | Required | Notes |
|---|---|---|---|
| Name | Text | Yes | Max 150 chars |
| Email | Email | Yes | Blur check for duplicates |
| Role | Single-select | Yes | From `GET /api/roles` |

| Behaviour | Detail |
|---|---|
| `email_already_registered` | Field error: "A user with this email is already registered." |
| `email_already_has_invitation` | Field error: "A pending invitation exists for this email. Go to Invited Users to resend." |
| On success | Close modal · switch to Invited Users tab · toast: "Invitation sent to [email]" |

---

### 14.4 Edit User Modal

Pre-populated from `GET /api/users/{id}`.

**Editable:** `title`, `first_name`, `last_name`, `display_name`, `email`, `contact_no`, `picture`, `cover_pic`, address fields, `role_id`, `code`

**Read-only (display only):** `entity_type` — set once at registration, not changed through this form

| Behaviour | Detail |
|---|---|
| Entity field | Show as read-only label: "Entity: Default Entity" |
| `code` field | Editable; show inline error if uniqueness fails |
| Status change | Via dedicated Deactivate / Reactivate buttons, not the edit form |

---

### 14.5 Deactivate Dialog

Text: `"Are you sure you want to deactivate [display_name]? They will immediately lose access."`
On confirm → `POST /api/users/{id}/deactivate` → update badge → toast

---

### 14.6 Reactivate Dialog

Text: `"Are you sure you want to reactivate [display_name]? They will regain access."`
On confirm → `POST /api/users/{id}/reactivate` → update badge → toast

---

### 14.7 Delete Dialog

Text: `"Are you sure you want to permanently delete [display_name]? This action cannot be undone."`
On confirm → `DELETE /api/users/{id}/delete` with `{ "confirm": true }` → remove row → toast

---

## 15. UI Tasks — Invited Users Screen

### 15.1 Invited Users Table (Tab 2)

Data from `GET /api/invitations`

| Column | Source | Notes |
|---|---|---|
| Name | `name` | — |
| Email | `email` | — |
| Role | `role_name` | — |
| Invited By | `invited_by_name` | — |
| Invited On | `created_at` | Formatted date/time |
| Link Expires At | `expires_at` | Amber warning if past |
| Times Resent | `resent_count` | Show `—` if 0 |
| Status | `status` | Blue = Pending · Amber = Expired |
| Actions | — | Resend · Cancel |

---

### 15.2 Resend

- Call `POST /api/invitations/{uid}/resend`
- On `user_already_registered` → error toast: "This user has already registered."
- On `invitation_already_cancelled` → error toast: "This invitation was cancelled. Create a new one."
- On success → toast: "Invitation resent. Expires in 72 hours." Update `expires_at` and `resent_count` in row in-place.

---

### 15.3 Cancel

- Confirm: `"Are you sure you want to cancel the invitation for [name] ([email])? Their link will be invalidated."`
- Call `POST /api/invitations/{uid}/cancel`
- On success → remove row · toast: "Invitation cancelled."
- On `user_already_registered` → error toast: "This user has already registered."

---

## 16. UI Tasks — Registration Page (External)

**Route:** `/user-invitation` (public, no auth)

**Query params from link:** `invitation`, `name`, `email`, `role_id`, `role_name`

| Step | Action |
|---|---|
| 1 | Show: `"Hello [name], you have been invited to join [App Name] as [role_name]."` |
| 2 | Show `email` as read-only confirmation |
| 3 | Show `"Continue with [IDP Provider]"` button |
| 4 | On IDP callback → receive `idp_access_token` |
| 5 | `POST /api/verify-invitation` with `{ invitation, idp_access_token }` |
| 6 | `invitation_cancelled` → "This invitation has been cancelled. Contact your administrator." |
| 7 | `invitation_expired` → "This invitation link has expired. Ask your administrator to resend." |
| 8 | `invitation_does_not_exist` → "This link is invalid or has already been used." |
| 9 | On success → store `access_token` in auth state · redirect to dashboard |

---

## 17. Permission Reference

| Permission key | Endpoints | Description |
|---|---|---|
| `users.create` | `POST /api/users/invite` | Create invitation |
| `users.view` | `GET /api/users` · `GET /api/users/{id}` | View users |
| `users.edit` | `PUT /api/users/{id}` | Update user |
| `users.deactivate` | `POST /api/users/{id}/deactivate` | Deactivate |
| `users.deactivate` | `POST /api/users/{id}/reactivate` | Reactivate |
| `users.delete` | `DELETE /api/users/{id}/delete` | Hard delete |
| `users.invite.manage` | `GET /api/invitations` | View invitations |
| `users.invite.manage` | `POST /api/invitations/{uid}/resend` | Resend |
| `users.invite.manage` | `POST /api/invitations/{uid}/cancel` | Cancel |
| *(any active user — self)* | `PUT /api/users/me/profile` | Own profile |
| *(public — no auth)* | `POST /api/verify-invitation` | IDP registration |

---

## 18. Audit Log Events

All rows written to `core_audit_logs`.

| `action` | Trigger | `entity_type` | Key `payload` fields |
|---|---|---|---|
| `invitation.created` | Admin invites | `invitation` | `{name, email, role_id, invited_by_id}` |
| `invitation.resent` | Admin resends | `invitation` | `{new_uid, new_expires_at, resent_count, resent_by_id}` |
| `invitation.cancelled` | Admin cancels | `invitation` | `{cancelled_by_id, name, email}` |
| `user.registered` | IDP accept | `user` | `{email, role_id, entity_id, code, registered_at}` |
| `user.updated` | Admin edits | `user` | `{before: {...}, after: {...}}` |
| `user.profile_updated` | Self-service | `user` | `{changed_fields: [...]}` |
| `user.deactivated` | Admin deactivates | `user` | `{deactivated_by_id, deactivated_at}` |
| `user.reactivated` | Admin reactivates | `user` | `{reactivated_by_id}` |
| `user.deleted` | Admin deletes | `user` | `{snapshot: {name, email, role_id, entity_id, code}}` |
| `user.auto_soft_deleted` | Background job | `user` | `{deactivated_at, threshold_days}` — `actor_id = NULL` |

---

## 19. Non-Functional Requirements

| # | Category | Requirement |
|---|---|---|
| 19.1 | Security | Invitation UIDs are UUID v4 hex32 (128-bit). Never use sequential IDs in links. |
| 19.2 | Security | `POST /api/verify-invitation` is public. Apply rate limiting: max 10 requests / IP / 15 minutes. |
| 19.3 | Security | IDP token validated server-side only by calling `EXTERNAL_API_URL`. Never trust client-supplied identity. |
| 19.4 | Security | All permission checks enforced at the Django view level — not only in the UI. |
| 19.5 | Entity | `core_entity` db_table name is `core_entity` (not `core_entity`). All JOIN calls must use `core_entity.id`. |
| 19.6 | Entity | On registration, use `CoreEntity.objects.get_or_create(id=1, defaults={"type": "Default Entity"})`. The `entity_id` on `core_users` must always reference a valid `core_entity` row. |
| 19.7 | Registration | `first_name`, `display_name`, `email`, `role_id`, `entity_id`, `code`, `idp_user_id`, `registered_at`, `status_id` are all written to `core_users` atomically during the accept-invitation flow. |
| 19.8 | Fields | `contact_no`, `picture`, `cover_pic`, and address fields are set to NULL at registration and filled in later via profile update or admin edit. |
| 19.9 | Code | `generate_unique_user_code()` loops until a unique `U-XXXXXX` is found. Must never return a code already in `core_users.code`. |
| 19.10 | Invitation rules | A user with `registered_at IS NOT NULL` in `core_users` can never be re-invited or have their invitation cancelled. Both endpoints check this. |
| 19.11 | Invitation rules | A `cancelled` invitation cannot be resent. A new invitation must be created via `POST /api/users/invite`. |
| 19.12 | Expiry | 72-hour expiry is read from `settings` — not hardcoded. Use key `invitation_link_expiry_hours`. |
| 19.13 | Email | Invitation dispatched within 2 minutes. Use async queue if latency is a concern. |
| 19.14 | UI | "Invited Users" tab only rendered for `users.invite.manage`. Both tabs on the same `/users` page. |
| 19.15 | UI | "Invite User" button only rendered for `users.create`. All action buttons conditionally rendered. |
| 19.16 | URL order | `api/users/me/profile` must be registered before `api/users/<int:user_id>` in `urls.py`. |
| 19.17 | Audit | Every create, update, deactivate, delete, and invitation action writes to `core_audit_logs`. |
| 19.18 | Self-service | `PUT /api/users/me/profile` must explicitly block `email`, `role_id`, `entity_id`, `status_id`, `code`, `idp_user_id` from being changed. |
