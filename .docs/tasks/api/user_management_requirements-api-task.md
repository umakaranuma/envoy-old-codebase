# API Tasks: User Management Module — Requirements

## 3.1 Create User
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

## 3.2 Invitation Email
- [ ] Implement API logic for 3.2 Invitation Email.

## 3.3 Invited Users Management
- [ ] Implement API logic for 3.3 Invited Users Management.

## 3.4 User Registration (User Self-Service)
- [ ] Implement API logic for 3.4 User Registration (User Self-Service).

## 3.5 Read / List Users
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

## 3.6 Edit User
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

## 3.7 Edit Profile (User Self-Service)
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

## 3.8 Deactivate / Reactivate User
- [ ] Implement API logic for 3.8 Deactivate / Reactivate User.

## 3.9 Delete User
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

- [ ] Register permission: `users.view` (View the user list and user details)
- [ ] Register permission: `users.create` (Create a new user and send an invitation)
- [ ] Register permission: `users.edit` (Edit an existing user's name, email, and role)
- [ ] Register permission: `users.deactivate` (Deactivate or reactivate a user)
- [ ] Register permission: `users.delete` (Permanently delete a user)
- [ ] Register permission: `users.invite.manage` (View invited users, resend invitations, cancel invitations)
- [ ] Ensure API supports: If a user's email address is changed, should a re-verification email be triggered?
- [ ] Ensure API supports: Should invitation link expiry be configurable?
- [ ] Ensure API supports: Should deactivated users be soft-deleted after a period of inactivity?
- [ ] Ensure API supports: Should the display name be visible to other users (e.g., in comments)?
- [ ] Ensure API supports: Is a country code selector needed alongside the contact number field?
- [ ] Ensure API supports: Should cancelled invitations be permanently removed or retained in an audit log?
- [ ] Ensure API supports: Should the inviting user receive a notification when the invited user registers?

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
