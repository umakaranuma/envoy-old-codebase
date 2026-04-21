# Hierarchy Management Module — Requirements

## 1. Overview

The Hierarchy Management module allows authorised users to define and manage parent-child relationships between users and between teams within the application. The module maintains two completely independent hierarchies — a **User Hierarchy** and a **Team Hierarchy** — each with its own tree structure. Hierarchies are structural only and do not affect permissions, data visibility, or access control in any way. Each user or team can have only one parent, and the hierarchy supports unlimited depth levels.

---

## 2. Key Rules

- **Two independent hierarchies** exist — User Hierarchy and Team Hierarchy. They have no relation to each other.
- Each user or team can have **only one parent** at any level.
- A user or team can have **multiple children**.
- Hierarchy depth is **unlimited** — there is no cap on how many levels deep a tree can go.
- The hierarchy is **structural only** — it does not affect permissions, roles, or data visibility.
- A parent user or team **cannot be deleted** if it has children assigned. Children must be reassigned or removed first.
- All actions are **permission-based**, governed by the role assigned to the acting user.

---

## 3. Hierarchy Concepts

```
Root Node (no parent)
 ├── Child Node
 │    ├── Grandchild Node
 │    │    └── Great-grandchild Node (unlimited depth...)
 │    └── Grandchild Node
 └── Child Node
```

- **Root Node** — A user or team with no parent. Multiple root nodes can exist.
- **Parent Node** — Any user or team that has at least one child assigned beneath it.
- **Child Node** — Any user or team that has been assigned a parent.
- **Leaf Node** — A user or team at the bottom of the tree with no children.

---

## 4. Functional Requirements

### 4.1 User Hierarchy

#### 4.1.1 View User Hierarchy

**Description:** Displays the full user hierarchy as an interactive tree view.

**Permission Required:** `hierarchy.user.view`

**Displayed Information:**
- Tree structure showing all users and their parent-child relationships.
- Each node displays the user's display name and role.
- Expandable and collapsible tree nodes.
- Root-level users (no parent) are shown at the top level.
- Search/filter to locate a specific user within the tree.

**Behaviour:**
- The hierarchy view is only visible to users with the `hierarchy.user.view` permission.
- Users with no parent are shown as root nodes.
- Clicking a node opens the user detail or allows hierarchy editing based on permissions.

---

#### 4.1.2 Assign Parent to a User

**Description:** Allows an authorised user to set or change the parent of a user in the hierarchy.

**Permission Required:** `hierarchy.user.edit`

**Input Fields:**

| Field        | Type          | Required | Constraints                                             |
|--------------|---------------|----------|---------------------------------------------------------|
| User         | Single-select | Yes      | The user whose parent is being set                      |
| Parent User  | Single-select | No       | Any active user except the user itself or its own descendants |

**Behaviour:**
- The **Assign Parent** action is only visible to users with the `hierarchy.user.edit` permission.
- A user cannot be assigned as their own parent.
- A user cannot be assigned a parent that is one of their own descendants — this would create a circular reference and must be blocked with a validation error.
- If a user already has a parent, the new selection replaces the existing parent.
- Setting the Parent User field to empty removes the user from the hierarchy and makes them a root node.
- Changes take effect immediately.

---

#### 4.1.3 Remove Parent from a User

**Description:** Detaches a user from their parent, making them a root-level node.

**Permission Required:** `hierarchy.user.edit`

**Behaviour:**
- Removing a parent from a user does not affect the user's children — they remain attached to the user.
- The user becomes a root node with no parent.
- A confirmation prompt is shown before removing the parent relationship.

---

#### 4.1.4 Delete a Node from User Hierarchy

**Description:** A user cannot be removed from the hierarchy independently — deleting a user is handled by the User Management module. However, before a user can be deleted, the system checks for children in the hierarchy.

**Behaviour:**
- If the user being deleted has children in the User Hierarchy, **deletion is blocked**.
- An error message is shown:
  > *"This user cannot be deleted because they have [n] child user(s) in the hierarchy. Please reassign or remove all child users before deleting."*
- Once all children are reassigned or removed, the user can be deleted via the User Management module.

---

### 4.2 Team Hierarchy

#### 4.2.1 View Team Hierarchy

**Description:** Displays the full team hierarchy as an interactive tree view.

**Permission Required:** `hierarchy.team.view`

**Displayed Information:**
- Tree structure showing all teams and their parent-child relationships.
- Each node displays the team name and account manager name.
- Expandable and collapsible tree nodes.
- Root-level teams (no parent) are shown at the top level.
- Search/filter to locate a specific team within the tree.

**Behaviour:**
- The hierarchy view is only visible to users with the `hierarchy.team.view` permission.
- Teams with no parent are shown as root nodes.
- Clicking a node opens the team detail or allows hierarchy editing based on permissions.

---

#### 4.2.2 Assign Parent to a Team

**Description:** Allows an authorised user to set or change the parent of a team in the hierarchy.

**Permission Required:** `hierarchy.team.edit`

**Input Fields:**

| Field        | Type          | Required | Constraints                                               |
|--------------|---------------|----------|-----------------------------------------------------------|
| Team         | Single-select | Yes      | The team whose parent is being set                        |
| Parent Team  | Single-select | No       | Any existing team except the team itself or its own descendants |

**Behaviour:**
- The **Assign Parent** action is only visible to users with the `hierarchy.team.edit` permission.
- A team cannot be assigned as its own parent.
- A team cannot be assigned a parent that is one of its own descendants — circular references are blocked with a validation error.
- If a team already has a parent, the new selection replaces the existing parent.
- Setting the Parent Team field to empty removes the team from the hierarchy and makes it a root node.
- Changes take effect immediately.

---

#### 4.2.3 Remove Parent from a Team

**Description:** Detaches a team from their parent, making them a root-level node.

**Permission Required:** `hierarchy.team.edit`

**Behaviour:**
- Removing a parent from a team does not affect the team's children — they remain attached to the team.
- The team becomes a root node with no parent.
- A confirmation prompt is shown before removing the parent relationship.

---

#### 4.2.4 Delete a Node from Team Hierarchy

**Description:** A team cannot be removed from the hierarchy independently — deletion is handled by the Sales Team module. However, before a team can be deleted, the system checks for children in the hierarchy.

**Behaviour:**
- If the team being deleted has children in the Team Hierarchy, **deletion is blocked**.
- An error message is shown:
  > *"This team cannot be deleted because it has [n] child team(s) in the hierarchy. Please reassign or remove all child teams before deleting."*
- Once all children are reassigned or removed, the team can be deleted via the Sales Team module.

---

## 5. Circular Reference Protection

Circular references must be prevented at all times. A circular reference occurs when assigning a parent would create a loop in the tree.

**Examples of blocked assignments:**

| Scenario                                         | Result   |
|--------------------------------------------------|----------|
| Assigning a user/team as its own parent          | Blocked  |
| Assigning a direct child as a parent             | Blocked  |
| Assigning a deeper descendant as a parent        | Blocked  |

**Behaviour:**
- The system validates the entire ancestor chain before saving any parent assignment.
- If a circular reference is detected, an error is shown:
  > *"This assignment would create a circular reference in the hierarchy and cannot be saved."*
- This validation is enforced on both the frontend and the backend API.

---

## 6. Permission Reference

All Hierarchy Management actions are governed by the following permissions, assigned via the Role Management module.

| Permission Key          | Action Controlled                                            |
|-------------------------|--------------------------------------------------------------|
| `hierarchy.user.view`   | View the user hierarchy tree                                 |
| `hierarchy.user.edit`   | Assign, change, or remove a parent for a user               |
| `hierarchy.team.view`   | View the team hierarchy tree                                 |
| `hierarchy.team.edit`   | Assign, change, or remove a parent for a team               |

> Users without a permission will not see the associated UI controls or be able to call the associated API endpoints. The hierarchy being structural-only means these permissions have no bearing on data access or role authority.

---

## 7. Non-Functional Requirements

| Requirement              | Detail                                                                                          |
|--------------------------|-------------------------------------------------------------------------------------------------|
| Permission Enforcement   | All actions enforced on both frontend (UI visibility) and backend (API level)                  |
| Circular Reference Check | Must be validated on both client and server before any parent assignment is saved               |
| Performance              | Hierarchy tree must render within 3 seconds for trees up to 1,000 nodes                        |
| Scalability              | Data model must support unlimited depth without performance degradation (e.g., using closure table or nested set pattern) |
| Structural Only          | Hierarchy changes must never affect user permissions, role assignments, or data visibility      |
| Audit Logging            | All parent assignments, changes, and removals logged with acting user identity and timestamp    |
| Validation               | All inputs validated on both client and server side                                             |
| Responsiveness           | UI must be responsive across desktop and tablet screen sizes                                    |

---

## 8. User Stories

| ID    | User Story                                                                                                                                    |
|-------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| HM-01 | As a user with `hierarchy.user.view` permission, I want to view the full user hierarchy as a tree so I can understand reporting structures.   |
| HM-02 | As a user with `hierarchy.user.edit` permission, I want to assign a parent to a user so I can define their position in the hierarchy.         |
| HM-03 | As a user with `hierarchy.user.edit` permission, I want to change a user's parent so I can restructure the hierarchy when needed.             |
| HM-04 | As a user with `hierarchy.user.edit` permission, I want to remove a user's parent so they become a root-level node.                           |
| HM-05 | As a user, I want to be prevented from creating circular references in the hierarchy so the tree structure stays valid.                        |
| HM-06 | As a user with `hierarchy.team.view` permission, I want to view the full team hierarchy as a tree so I can understand team structures.        |
| HM-07 | As a user with `hierarchy.team.edit` permission, I want to assign a parent to a team so I can define its position in the team hierarchy.      |
| HM-08 | As a user with `hierarchy.team.edit` permission, I want to change a team's parent so I can restructure the team hierarchy when needed.        |
| HM-09 | As a user with `hierarchy.team.edit` permission, I want to remove a team's parent so it becomes a root-level node.                            |
| HM-10 | As a user, I want deletion of a parent user or team to be blocked if they have children, so I don't accidentally break the hierarchy.         |
| HM-11 | As a user, I want to search within the hierarchy tree so I can quickly locate a specific user or team without scrolling through the entire tree. |

---

## 9. Out of Scope

- Hierarchy-based permission inheritance (hierarchy is structural only).
- Hierarchy-based data visibility or reporting roll-ups.
- Cross-hierarchy relationships (linking user hierarchy nodes to team hierarchy nodes).
- Bulk reassignment of children when a parent is removed.
- Visualisation exports (e.g., exporting the tree as an image or PDF).

---

## 10. Open Questions

| #  | Question                                                                                                          | Owner     |
|----|-------------------------------------------------------------------------------------------------------------------|-----------|
| 1  | Should there be a maximum number of children allowed per node, or is it truly unlimited?                          | Product   |
| 2  | When a user is deactivated, should they remain in the hierarchy or be automatically detached?                     | Product   |
| 3  | Should the tree view support drag-and-drop for reassigning parents, or only form-based assignment?                | Product   |
| 4  | Should users be able to view only their own branch of the hierarchy, or always the full tree?                     | Product   |
| 5  | Is there a need for a bulk import/export of hierarchy relationships (e.g., via CSV)?                              | Tech Lead |
