# Sales Team Module — Requirements

## 1. Overview

The Sales Team module allows authorised users to create and manage sales teams within the application. Each team consists of a team name, a single account manager, and one or more team members. Access to all management actions is governed by the permissions assigned to a user's role. A user can belong to multiple teams simultaneously, and the account manager and team members are treated as distinct, non-overlapping roles within a team.

---

## 2. Key Rules

- A user can be a **member of multiple teams** at the same time.
- Each team has **exactly one account manager**.
- The **account manager cannot also be a team member** within the same team — they are separate positions.
- **Any active user** in the system can be selected as a team member or account manager.
- A team **cannot be deleted** while it has members assigned. Members must be removed first.
- All actions are **permission-based** — governed by the role assigned to the acting user.

---

## 3. Functional Requirements

### 3.1 Create Sales Team

**Description:** Any user whose role includes the `sales_team.create` permission can create a new sales team.

**Permission Required:** `sales_team.create`

**Input Fields:**

| Field           | Type          | Required | Constraints                                                       |
|-----------------|---------------|----------|-------------------------------------------------------------------|
| Team Name       | Text          | Yes      | Unique, max 150 characters                                        |
| Account Manager | Single-select | Yes      | Select one active user; cannot be the same person as any team member |
| Team Members    | Multi-select  | No       | Select one or more active users; cannot include the account manager |

**Behaviour:**
- The **Create Sales Team** option is only visible to users with the `sales_team.create` permission.
- Team name must be unique across all sales teams in the system.
- The Account Manager dropdown lists all active users in the system.
- The Team Members multi-select lists all active users excluding the currently selected account manager.
- If the account manager selection changes, the team members list updates dynamically to exclude the newly selected account manager.
- A team can be created without any members — the team name and account manager are the minimum required.
- On successful creation, the team appears in the Sales Team list.

---

### 3.2 Read / List Sales Teams

**Description:** Displays all sales teams in a paginated, searchable list.

**Permission Required:** `sales_team.view`

**Displayed Columns:**

| Column          | Description                                    |
|-----------------|------------------------------------------------|
| Team Name       | Name of the sales team                         |
| Account Manager | Name of the assigned account manager           |
| Members Count   | Total number of team members                   |
| Created At      | Date the team was created                      |
| Actions         | View / Edit / Delete                           |

**Behaviour:**
- The Sales Team list is only visible to users with the `sales_team.view` permission.
- Search and filter by team name or account manager name.
- Pagination supported.
- Clicking a team name opens the team detail view.
- Action buttons (Edit, Delete) are shown only if the user holds the respective permissions.

---

### 3.3 View Sales Team Detail

**Description:** Displays the full details of a specific sales team.

**Permission Required:** `sales_team.view`

**Displayed Information:**

| Field           | Description                                        |
|-----------------|----------------------------------------------------|
| Team Name       | Name of the sales team                             |
| Account Manager | Name and profile of the account manager            |
| Team Members    | List of all members with their name and role       |
| Created At      | Date the team was created                          |
| Updated At      | Date the team was last modified                    |

---

### 3.4 Edit Sales Team

**Description:** Allows a user with the appropriate permission to update a team's name, account manager, or members.

**Permission Required:** `sales_team.edit`

**Editable Fields:**

| Field           | Type          | Required | Constraints                                                          |
|-----------------|---------------|----------|----------------------------------------------------------------------|
| Team Name       | Text          | Yes      | Unique, max 150 characters                                           |
| Account Manager | Single-select | Yes      | Select one active user; cannot be the same person as any team member |
| Team Members    | Multi-select  | No       | Select one or more active users; cannot include the account manager  |

**Behaviour:**
- The form is pre-populated with the team's existing data.
- Team name must remain unique (excluding the current team).
- If the account manager is changed to someone who is currently a team member, the system must show a validation error — the user must be removed from the members list before being assigned as account manager, or vice versa.
- Members can be added or removed freely.
- If a member is removed from a team, they are simply unassigned from that team; their user account remains active.
- Changes take effect immediately upon saving.
- An audit log entry is created recording what changed, who made the change, and when.

---

### 3.5 Delete Sales Team

**Description:** Allows a user with the appropriate permission to permanently delete a sales team.

**Permission Required:** `sales_team.delete`

**Behaviour:**
- The **Delete** action is only visible to users with the `sales_team.delete` permission.
- **Deletion is blocked if the team currently has one or more members assigned.** An error message is shown:
  > *"This team cannot be deleted because it has [n] member(s) assigned. Please remove all members before deleting the team."*
- A team with only an account manager and no members **can** be deleted.
- A confirmation dialog is shown before deletion:
  > *"Are you sure you want to delete [Team Name]? This action cannot be undone."*
- On successful deletion, the team is permanently removed from the system.
- The account manager and any members (if fully removed prior) are not affected — their user accounts remain intact.

---

### 3.6 Manage Team Members

**Description:** Within the edit view, authorised users can add or remove members from a team.

**Permission Required:** `sales_team.edit`

**Behaviour:**
- Any active user in the system can be added as a team member.
- The account manager of the team is excluded from the member selection list.
- A user can be a member of multiple teams simultaneously — there is no restriction on how many teams a user belongs to.
- Removing a member from a team does not affect their user account or membership in other teams.
- There is no minimum number of members required — a team can have zero members (account manager only).

---

## 4. Permission Reference

All Sales Team actions are governed by the following permissions, assigned via the Role Management module.

| Permission Key       | Action Controlled                                           |
|----------------------|-------------------------------------------------------------|
| `sales_team.view`    | View the sales team list and team details                   |
| `sales_team.create`  | Create a new sales team                                     |
| `sales_team.edit`    | Edit an existing team's name, account manager, and members  |
| `sales_team.delete`  | Permanently delete a sales team                             |

> Any user whose assigned role includes one or more of the above permissions will have access to the corresponding actions. Users without a permission will not see the associated UI controls or be able to call the associated API endpoints.

---

## 5. Non-Functional Requirements

| Requirement            | Detail                                                                                         |
|------------------------|------------------------------------------------------------------------------------------------|
| Permission Enforcement | All actions enforced on both frontend (UI visibility) and backend (API level)                 |
| Uniqueness             | Team name must be unique system-wide; validated on both client and server                     |
| Conflict Validation    | Account manager and team member conflict must be caught at both UI and API level               |
| Audit Logging          | All create, edit, and delete actions logged with the acting user's identity and timestamp      |
| Validation             | All inputs validated on both client and server side                                            |
| Responsiveness         | UI must be responsive across desktop and tablet screen sizes                                   |

---

## 6. User Stories

| ID    | User Story                                                                                                                              |
|-------|-----------------------------------------------------------------------------------------------------------------------------------------|
| ST-01 | As a user with `sales_team.create` permission, I want to create a sales team with a name, account manager, and members.                |
| ST-02 | As a user with `sales_team.view` permission, I want to view a list of all sales teams so I can see how they are structured.            |
| ST-03 | As a user with `sales_team.view` permission, I want to view the full details of a team including all its members and account manager.  |
| ST-04 | As a user with `sales_team.edit` permission, I want to update a team's name, account manager, and members to keep it accurate.         |
| ST-05 | As a user with `sales_team.edit` permission, I want to add or remove members from a team without affecting their user accounts.        |
| ST-06 | As a user with `sales_team.delete` permission, I want to delete a team that has no members so I can remove unused teams.               |
| ST-07 | As a user, I want to be prevented from deleting a team that still has members so that no data is accidentally lost.                    |
| ST-08 | As a user, I want to be prevented from assigning the same person as both account manager and team member within the same team.         |
| ST-09 | As a user, I want to be able to assign a user to multiple teams so that shared resources can be managed flexibly.                      |

---

## 7. Out of Scope

- Hierarchical or nested team structures (parent/child teams).
- Team performance metrics or reporting (separate module).
- Assigning targets or quotas to teams.
- Team-level notifications or messaging.

---

## 8. Open Questions

| #  | Question                                                                                              | Owner     |
|----|-------------------------------------------------------------------------------------------------------|-----------|
| 1  | Should there be a maximum limit on the number of members per team?                                    | Product   |
| 2  | When the account manager of a team is deactivated, should the team be flagged or automatically unassigned? | Product   |
| 3  | Should a user be able to view only the teams they belong to, or all teams in the system?              | Product   |
| 4  | Should team membership history be tracked (e.g., who was added/removed and when)?                    | Tech Lead |
