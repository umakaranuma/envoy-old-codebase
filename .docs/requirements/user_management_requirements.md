# User Management Module — Requirements

## 1. Overview

The User Management module allows any user with the appropriate permissions to invite, manage, and maintain users within the application. Access to each action (create, edit, deactivate, delete, manage invitations) is governed entirely by the permissions assigned to the user's role — not by a fixed "admin" designation. User creation follows an email-based invitation flow — an authorised user creates a user record, the system sends an invitation email, and the invited user completes their own account registration via a secure link. Once registered, the user becomes active and can manage their own profile details.

---

## 2. User Lifecycle

```
Authorised User Creates User → System Sends Invitation Email → User Status: "Invited"
       │                                                               │
       │                               ┌───────────────────────────────┤
       │                               ▼                               ▼
       │                  Authorised User Resends Invite    Authorised User Cancels Invite
       │                               │                               │
       │                               ▼                               ▼
       │                     New Link Sent                    Status: "Cancelled"
       │
       └──── Invited User Clicks Link & Registers ────→ Status: "Active" → User Can Log In
```

---

## 3. Functional Requirements

### 3.1 Create User

**Description:** Any user whose role includes the `users.create` permission can create a new user by providing basic details. The system then sends an invitation email to the new user.

**Permission Required:** `users.create`

**Input Fields:**

| Field          | Type         | Required | Constraints                                   |
|----------------|--------------|----------|-----------------------------------------------|
| Name           | Text         | Yes      | Max 150 characters                            |
| Email Address  | Email        | Yes      | Unique, valid email format                    |
| Role           | Single-select| Yes      | Must select one role from the existing roles list |

**Behaviour:**
- The **Create User** option is only visible and accessible to users who have the `users.create` permission.
- Email address must be unique across the system.
- The role dropdown is populated from the Role Management module.
- On successful creation, the user record is saved with status **"Invited"**.
- The system automatically sends an invitation email to the provided email address.
- The creator does **not** set a password — the invited user sets it themselves during registration.
- The created user appears in the **Invited Users** section with an **"Invited"** status badge.

---

### 3.2 Invitation Email

**Description:** Upon user creation, the system sends an automated invitation email to the new user.

**Email Content:**
- Welcome message with the application name.
- A secure invitation link to complete registration.
- Expiry notice for the invitation link.

**Invitation Link Behaviour:**

| Property        | Detail                                                                                 |
|-----------------|----------------------------------------------------------------------------------------|
| Link Expiry     | Configurable by authorised users (default: 72 hours); settable in application settings |
| Link Usage      | Single-use — invalidated after registration                                            |
| Expired Link    | User is shown an error with option to request a new link                               |

---

### 3.3 Invited Users Management

**Description:** Users who have been invited but have not yet accepted the invitation are grouped and managed under an **"Invited Users"** section. Users with the appropriate permissions can resend or cancel invitations for these users.

**Permission Required:** `users.invite.manage` (covers resend and cancel actions)

**Invited Users List View:**

| Column          | Description                                           |
|-----------------|-------------------------------------------------------|
| Name            | Name provided by the creator at invitation            |
| Email Address   | Invited email address                                 |
| Role            | Assigned role                                         |
| Invited By      | Name of the user who sent the invitation              |
| Invited On      | Date and time the invitation was sent                 |
| Link Expires At | Date and time the invitation link expires             |
| Status          | Invited / Expired                                     |
| Actions         | Resend Invitation / Cancel Invitation                 |

**Behaviour:**
- The **Invited Users** section is only visible to users with the `users.invite.manage` permission.
- Only users with **"Invited"** or **"Expired"** status appear in this section.
- Once a user completes registration, they are removed from the Invited Users section and appear in the main Users list as **"Active"**.
- A visual indicator (e.g., warning badge) is shown for invitations whose links have **expired** (past 72 hours) but the user has still not registered.
- Search and filter by name, email, or status (Invited / Expired) is supported.

---

#### 3.3.1 Resend Invitation

**Description:** Allows a user with the appropriate permission to resend the invitation email to a user who has not yet accepted their invite.

**Permission Required:** `users.invite.manage`

**Behaviour:**
- The **Resend Invitation** action is only visible to users with the `users.invite.manage` permission.
- Available for users with **"Invited"** or **"Expired"** status only.
- Resending generates a **new secure token** and invalidates the previous invitation link.
- The invitation expiry timer resets to 72 hours from the time of resend.
- The **"Invited On"** and **"Link Expires At"** timestamps are updated in the Invited Users list.
- A confirmation toast/notification is shown to the user who performed the resend after the email is sent successfully.
- The invited user receives a new invitation email with the updated link.

---

#### 3.3.2 Cancel Invitation

**Description:** Allows a user with the appropriate permission to cancel a pending invitation, preventing the invited user from registering via the existing or any future link.

**Permission Required:** `users.invite.manage`

**Behaviour:**
- The **Cancel Invitation** action is only visible to users with the `users.invite.manage` permission.
- Available for users with **"Invited"** or **"Expired"** status only.
- A confirmation dialog is shown before cancellation:
  > *"Are you sure you want to cancel the invitation for [name / email]? This action will invalidate their invitation link."*
- On confirmation:
  - The invitation token is immediately invalidated.
  - The user's status changes to **"Cancelled"**.
  - The user record is removed from the **Invited Users** section.
  - If the cancelled user attempts to use their old invitation link, they are shown an error message indicating the invitation has been cancelled.
- A cancelled invitation **cannot be reactivated**. A new invitation must be created for the same email address if needed.
- The email address is freed up and can be used for a new invitation.
- Cancelled invitation records are **retained in the audit log** with the cancellation timestamp and the identity of the user who performed the cancellation. They are not permanently deleted.

---

### 3.4 User Registration (User Self-Service)

**Description:** The invited user completes their account setup by clicking the invitation link.

**Registration Flow:**
1. User clicks the invitation link in the email.
2. System validates the link (checks token validity and expiry).
3. User is directed to the registration page, pre-filled with their email address (read-only).
4. User sets their password and confirms it.
5. On successful submission, the account is activated.
6. User is redirected to the login page (or logged in automatically).

**Registration Form Fields:**

| Field             | Type      | Required | Constraints                                    |
|-------------------|-----------|----------|------------------------------------------------|
| Email Address     | Email     | Yes      | Pre-filled, read-only                          |
| Password          | Password  | Yes      | Min 8 characters, must include uppercase, lowercase, and a number |
| Confirm Password  | Password  | Yes      | Must match Password                            |

**Behaviour:**
- If the link is expired or already used, an error message is shown with an option to request a new invitation.
- On successful registration, user status changes from **"Invited"** to **"Active"**.
- Upon successful registration, the system sends an **in-app notification** to the user who originally sent the invitation, informing them that the invited user has completed their registration and is now active. If that user is not currently logged in, the notification is shown the next time they log in.

---

### 3.5 Read / List Users

**Description:** Displays all active and inactive users in a paginated, searchable list.

**Permission Required:** `users.view`

**Displayed Columns:**

| Column        | Description                              |
|---------------|------------------------------------------|
| Name          | Full name of the user                    |
| Email Address | User's email                             |
| Role          | Assigned role                            |
| Status        | Active / Inactive                        |
| Created At    | Date the user was created                |
| Actions       | View / Edit / Deactivate                 |

**Behaviour:**
- This list shows only **Active** and **Inactive** users.
- **Invited / Expired / Cancelled** users are managed separately under the Invited Users section (3.3).
- Search and filter by name, email, role, or status.
- Pagination supported.
- Clicking a user opens their detail/edit view.

---

### 3.6 Edit User

**Description:** Allows a user with the appropriate permission to edit another user's basic details and role assignment.

**Permission Required:** `users.edit`

**Editable Fields:**

| Field         | Type          | Required | Constraints                                   |
|---------------|---------------|----------|-----------------------------------------------|
| Name          | Text          | Yes      | Max 150 characters                            |
| Email Address | Email         | Yes      | Unique, valid email format                    |
| Role          | Single-select | Yes      | Must select one role from existing roles list |

**Behaviour:**
- The **Edit** action is only visible to users with the `users.edit` permission.
- Email address must remain unique (excluding current user).
- If the email address is changed, a **re-verification email is sent to the new email address**. The user's email is updated in the system only after they verify the new address by clicking the verification link. Until verified, the old email address remains active.
- Role changes take effect immediately.

---

### 3.7 Edit Profile (User Self-Service)

**Description:** An active user can update their own profile details from within the application.

**Editable Fields:**

| Field          | Type          | Required | Constraints                                                                         |
|----------------|---------------|----------|-------------------------------------------------------------------------------------|
| Salutation     | Single-select | No       | Options: Mr., Mrs., Ms., Miss., Dr., Prof., Other                                   |
| First Name     | Text          | Yes      | Max 100 characters                                                                  |
| Last Name      | Text          | Yes      | Max 100 characters                                                                  |
| Display Name   | Text          | Yes      | Auto-generated as "First Name + Last Name", user can override; max 100 characters  |
| Country Code   | Single-select | No       | Dropdown of international dial codes (e.g., +94, +1, +44)                          |
| Contact Number | Text          | No       | Numeric only, validated against selected country code format                        |

**Behaviour:**
- Display Name is auto-populated from First Name + Last Name but can be customised.
- Display Name is **visible to other users** across the application (e.g., in comments, activity logs, mentions).
- The Country Code selector and Contact Number field are paired — selecting a country code is required when a contact number is entered.
- Users can only edit their own profile; they cannot edit other users' profiles.
- Changes are saved immediately on submission with a success notification.

---

### 3.8 Deactivate / Reactivate User

**Description:** Users with the appropriate permission can deactivate an active user or reactivate an inactive user.

**Permission Required:** `users.deactivate`

**Behaviour:**
- The **Deactivate** and **Reactivate** actions are only visible to users with the `users.deactivate` permission.
- A confirmation dialog is shown before deactivation.
- A deactivated user cannot log in to the application.
- Deactivated users remain visible in the user list with **"Inactive"** status.
- An inactive user can be reactivated by any user with the `users.deactivate` permission at any time.
- The user's data and role assignments are preserved during deactivation.
- If a user remains in **"Inactive"** status beyond a configurable inactivity threshold (default: 90 days), the system **soft-deletes** the user record. Soft-deleted users are hidden from all user lists but their data is retained in the system and can be restored by a user with the appropriate permission if required.

---

### 3.9 Delete User

**Description:** Allows permanent removal of a user from the system.

**Permission Required:** `users.delete`

**Behaviour:**
- The **Delete** action is only visible to users with the `users.delete` permission.
- A confirmation dialog is shown before deletion.
- Hard deletion removes the user record permanently.
- The user performing the deletion should be warned if the target user owns any data within the system before proceeding.

---

## 4. User Status Lifecycle

| Status       | Description                                                                    | Transitions                                                                                   |
|--------------|--------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| Invited      | User created and invitation email sent, not yet registered                     | → Active (user registers) · → Expired (link expires) · → Cancelled (authorised user cancels) |
| Expired      | Invitation link has passed the configurable expiry window without registration | → Invited (authorised user resends) · → Cancelled (authorised user cancels)                  |
| Cancelled    | Invitation cancelled; link is invalidated; record retained in audit log        | No further transitions — a new invitation must be created                                     |
| Active       | User has completed registration and can log in                                 | → Inactive (user with `users.deactivate` permission deactivates)                             |
| Inactive     | User has been deactivated                                                      | → Active (reactivated) · → Soft-Deleted (after configurable inactivity threshold)            |
| Soft-Deleted | User hidden from all lists; data retained and restorable                       | → Inactive (restored by authorised user)                                                     |

---

## 5. Permission Reference

All User Management actions are governed by the following permissions. These are assigned via the Role Management module.

| Permission Key          | Action Controlled                                              |
|-------------------------|----------------------------------------------------------------|
| `users.view`            | View the user list and user details                            |
| `users.create`          | Create a new user and send an invitation                       |
| `users.edit`            | Edit an existing user's name, email, and role                  |
| `users.deactivate`      | Deactivate or reactivate a user                                |
| `users.delete`          | Permanently delete a user                                      |
| `users.invite.manage`   | View invited users, resend invitations, cancel invitations     |

> Any user whose assigned role includes one or more of the above permissions will have access to the corresponding actions. Users without a permission will not see the associated UI controls or be able to call the associated API endpoints.

---

## 6. Non-Functional Requirements

| Requirement         | Detail                                                                                          |
|---------------------|-------------------------------------------------------------------------------------------------|
| Permission Enforcement | All actions must be enforced on both the frontend (UI visibility) and backend (API level)   |
| Self-Service        | Any active user can edit their own profile regardless of role permissions                       |
| Invitation Security | Invitation tokens must be cryptographically secure and single-use                               |
| Audit Logging       | All user management actions (create, edit, deactivate, delete, resend invite, cancel invite) must be logged with the acting user's identity and timestamp |
| Email Delivery      | Invitation emails must be delivered within 2 minutes of user creation                          |
| Validation          | All inputs validated on both client and server side                                             |
| Responsiveness      | UI must be responsive across desktop and tablet screen sizes                                    |

---

## 7. User Stories

| ID    | User Story                                                                                                                          |
|-------|-------------------------------------------------------------------------------------------------------------------------------------|
| UM-01 | As a user with `users.create` permission, I want to create a new user with a name, email, and role so they can be invited to the application. |
| UM-02 | As a new user, I want to receive an invitation email so I can complete my account registration.                                     |
| UM-03 | As a new user, I want to click the invitation link and set my password so I can activate my account.                               |
| UM-04 | As a user with `users.invite.manage` permission, I want to view all invited users in a dedicated section so I can track who has and hasn't accepted their invite. |
| UM-05 | As a user with `users.invite.manage` permission, I want to see which invitations have expired so I can take action on them.         |
| UM-06 | As a user with `users.invite.manage` permission, I want to resend an invitation so users whose link expired can still register.     |
| UM-07 | As a user with `users.invite.manage` permission, I want to cancel an invitation so I can prevent an unintended user from registering. |
| UM-08 | As an invited user, I want to be shown a clear error if my invitation link has expired or been cancelled so I understand what to do next. |
| UM-09 | As a user with `users.view` permission, I want to view a list of active and inactive users with their status so I can manage them effectively. |
| UM-10 | As a user with `users.edit` permission, I want to edit a user's name, email, and role so I can keep user records up to date.        |
| UM-11 | As an active user, I want to update my salutation, first name, last name, display name, and contact number in my profile.           |
| UM-12 | As a user with `users.deactivate` permission, I want to deactivate a user so they can no longer access the application.            |
| UM-13 | As a user with `users.deactivate` permission, I want to reactivate a deactivated user so they can regain access when needed.        |

---

## 8. Out of Scope

- Single Sign-On (SSO) / OAuth integration.
- Multi-role assignment per user (currently one role per user).
- Password reset flow (separate module).
- User profile photo / avatar management.
- Two-factor authentication (2FA).

---

## 9. Resolved Decisions

All previously open questions have been answered and incorporated into the requirements above.

| #  | Question                                                                                   | Decision                                                                                                           | Reflected In     |
|----|--------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|------------------|
| 1  | If a user's email address is changed, should a re-verification email be triggered?        | **Yes** — a verification email is sent to the new address; the old email stays active until verified              | Section 3.6      |
| 2  | Should invitation link expiry be configurable?                                             | **Yes** — expiry is configurable with a default of 72 hours                                                        | Section 3.2      |
| 3  | Should deactivated users be soft-deleted after a period of inactivity?                    | **Yes** — soft-deletion occurs after a configurable inactivity threshold (default: 90 days); data is retained     | Sections 3.8, 4  |
| 4  | Should the display name be visible to other users (e.g., in comments)?                    | **Yes** — display name is shown to other users across the application                                              | Section 3.7      |
| 5  | Is a country code selector needed alongside the contact number field?                     | **Yes** — a country code dropdown is paired with the contact number field                                          | Section 3.7      |
| 6  | Should cancelled invitations be permanently removed or retained in an audit log?          | **Retain** — cancelled invitation records are kept in the audit log with cancellation timestamp and actor identity | Section 3.3.2    |
| 7  | Should the inviting user receive a notification when the invited user registers?          | **Yes** — the user who originally sent the invitation receives an in-app notification upon successful registration | Section 3.4      |
