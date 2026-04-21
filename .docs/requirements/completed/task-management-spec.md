# Task Management — Full Specification

**Module:** CRM  
**Feature:** Task Management (Tasks, Task Types, Task Configs)  
**Version:** 1.0  
**Status:** Ready for Development  
**Last Updated:** 2026-03-26

---

## Table of Contents

1. [Overview & Module Structure](#1-overview--module-structure)
2. [Database Tables & Columns](#2-database-tables--columns)
3. [Task Status — Source from `core_statuses`](#3-task-status--source-from-core_statuses)
4. [API Endpoints](#4-api-endpoints)
5. [Screen 1 — Task Management (Kanban + List View)](#5-screen-1--task-management-kanban--list-view)
6. [Screen 2 — Task Single View](#6-screen-2--task-single-view)
7. [Screen 3 — Task Types (Settings)](#7-screen-3--task-types-settings)
8. [Screen 4 — Task Configs (Settings)](#8-screen-4--task-configs-settings)
9. [Business Logic & Key Rules](#9-business-logic--key-rules)
10. [Permission Reference](#10-permission-reference)
11. [Non-Functional Requirements](#11-non-functional-requirements)

---

## 1. Overview & Module Structure

The Task Management module is a CRM sub-feature that manages tasks linked to **opportunities (leads)**. It has three separate UI areas:

| UI Area | Sidebar Location | What It Does |
|---------|-----------------|--------------|
| **Tasks** | CRM → Tasks | Main task board — Kanban view and List view. Left panel shows users. Main area shows tasks per status column. |
| **Task Types** | CRM → Task Types | CRUD for task type definitions (e.g. "Call", "Meeting", "Email"). |
| **Task Configs** | CRM → (Settings / Task Configs) | CRUD for task configuration templates — predefined tasks linked to a stage and a type, with expected completion days. Sortable per stage. |

### Relationships

```
core_statuses (type = 'task')
    ↓ used as
core_tasks.task_status_id

core_tasks  ←→  crm_opportunity_tasks  ←→  crm_opportunities
(one task     (junction table)           (one opportunity
 per row)                                 per row)

crm_task_types → used by → crm_task_configs
crm_task_configs → template for → crm_opportunity_tasks (via task creation)
```

---

## 2. Database Tables & Columns

### 2.1 `core_tasks`

The main task record. Each task is linked to at least one opportunity via `crm_opportunity_tasks`.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | INT (PK) | No | auto | Primary key |
| `code` | VARCHAR(20) | No | — | Unique 6-digit code (auto-generated if not provided). Format: `000007`. |
| `task` | VARCHAR(250) | No | — | Task title / name. Required. |
| `description` | TEXT | Yes | NULL | Task description. Optional. |
| `assigned_to_id` | INT (FK) | Yes | NULL | FK → `core_users.id`. SET NULL on user delete. |
| `assigned_date` | DATE | Yes | NULL | Date the task was assigned. |
| `start_date` | DATE | Yes | NULL | Planned start date. |
| `due_date` | DATE | Yes | NULL | Deadline. Must be on or after `start_date`. |
| `task_status_id` | INT (FK) | No | — | FK → `core_statuses.id` WHERE `type = 'task'`. Required. |
| `sort_index` | FLOAT | Yes | NULL | Float ordering value within a status column (for Kanban drag-and-drop). Uses midpoint formula. |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX idx_task_status (task_status_id)`
- `INDEX idx_task_assigned (assigned_to_id)`
- `INDEX idx_task_sort (task_status_id, sort_index)`

**Delete guard:** A task with `status_type IN ('task_inprogress', 'task_done')` **cannot be deleted**. The API returns `FORBIDDEN`. Only tasks with `task_todo` status can be deleted.

---

### 2.2 `crm_opportunity_tasks`

Junction table linking tasks to opportunities.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `opportunity_id` | INT (FK) | No | FK → `crm_opportunities.id`. CASCADE. |
| `task_id` | INT (FK) | No | FK → `core_tasks.id`. CASCADE. |

**Indexes:**
- `PRIMARY KEY (id)`
- `INDEX idx_opp_task_opp (opportunity_id)`
- `INDEX idx_opp_task_task (task_id)`

> A task must always be linked to at least one opportunity. `opportunity_id` is required during task creation and stored in this junction table (not on `core_tasks` itself).

---

### 2.3 `core_statuses` (shared — filter by `type = 'task'`)

This is the shared status table used across modules. Task statuses are seeded with `type = 'task'`.

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT (PK) | Primary key |
| `name` | VARCHAR(255) | Display name (e.g. "TODO", "INPROGRESS", "DONE") |
| `description` | VARCHAR(255) | Optional description |
| `type_code` | VARCHAR(100) | Unique code (e.g. `task_todo`, `task_inprogress`, `task_done`) |
| `type` | VARCHAR(100) | Entity type. Filter by `type = 'task'` to get task statuses. |
| `color` | VARCHAR(20) | Hex color string (e.g. `#344054`) |
| `sort_index` | INT | Display order |

**Seeded task statuses:**

| Name | Type Code | Color | Sort |
|------|-----------|-------|------|
| TODO | `task_todo` | `#344054` | 1 |
| INPROGRESS | `task_inprogress` | `#175CD3` | 2 |
| DONE | `task_done` | `#0E7090` | 3 |

> **Important:** The API at `GET /tasks-statuses` fetches from `core_task_status` (this appears to be a view or alias over `core_statuses WHERE type = 'task'`). When querying for task statuses to populate Kanban columns, use `type = 'task'` as the filter.

---

### 2.4 `core_task_status_histories`

Audit log for task status changes.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `task_id` | INT (FK) | No | FK → `core_tasks.id` |
| `task_status_id` | INT (FK) | No | FK → `core_statuses.id` — the new status after change |
| `changed_by_id` | INT (FK) | Yes | FK → `core_users.id` |
| `remark` | TEXT | Yes | Auto-generated: "Task status changed from {old} to {new}" |
| `created_at` | DATETIME | No | Timestamp of the change |

---

### 2.5 `core_task_assignee_histories`

Audit log for task assignee changes.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `task_id` | INT (FK) | No | FK → `core_tasks.id` |
| `from_assigned_id` | INT (FK) | Yes | FK → `core_users.id` — previous assignee |
| `to_assigned_id` | INT (FK) | Yes | FK → `core_users.id` — new assignee |
| `changed_by_id` | INT (FK) | Yes | FK → `core_users.id` — who made the change |
| `remark` | TEXT | Yes | Auto-generated: "Task reassigned from {old} to {new}" |
| `created_at` | DATETIME | No | Timestamp of the reassignment |

---

### 2.6 `crm_task_types`

Simple lookup table for task type categories.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `name` | VARCHAR(250) | No | Unique. Required. (e.g. "Call", "Meeting", "Follow-up") |
| `description` | VARCHAR(250) | Yes | Optional |

**Delete guard:** A task type cannot be deleted if it is referenced by any row in `crm_task_configs`.

---

### 2.7 `crm_task_configs`

Predefined task templates linked to an opportunity stage and a task type.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `task` | VARCHAR(250) | No | Task name/description. Required. |
| `code` | VARCHAR(80) | No | Unique 6-digit auto-generated code. |
| `task_type_id` | INT (FK) | No | FK → `crm_task_types.id`. RESTRICT on delete. |
| `opportunity_status_id` | INT (FK) | No | FK → `core_statuses.id` (WHERE `type = 'opportunity'`). RESTRICT on delete. |
| `expected_days` | INT | Yes | 1 | Default days to completion. Defaults to 1 if not provided. |
| `reminder_expected_days` | INT | Yes | NULL | Days before due date to send a reminder. |
| `sort_index` | FLOAT | Yes | NULL | Ordering within a stage group. Float midpoint for drag-and-drop reorder. |

---

### 2.8 `core_intractions` (Task Interactions)

Logs interactions (calls, emails, meetings) made in relation to a task.

| Column | Type | Nullable | Description |
|--------|------|----------|-------------|
| `id` | INT (PK) | No | Primary key |
| `task_id` | INT (FK) | No | FK → `core_tasks.id` |
| `channel_id` | INT (FK) | No | FK → `core_channels.id`. Required. |
| `date` | DATE | No | Date of the interaction. Required. Format: `YYYY-MM-DD`. |
| `opportunity_status_id` | INT (FK) | Yes | FK → `core_statuses.id` |
| `customer_id` | INT (FK) | Yes | FK → customer table |
| `contact_id` | INT (FK) | Yes | FK → `core_contacts.id` |
| `opportunity_id` | INT (FK) | Yes | FK → `crm_opportunities.id` |
| `contact_by_id` | INT (FK) | Yes | FK → `core_users.id` — who made the interaction |
| `notes` | VARCHAR(500) | Yes | Interaction notes. Max 500 chars. |
| `entity_id` | INT (FK) | No | FK → `core_entity.id` — created via `EntityService.store`. |

---

## 3. Task Status — Source from `core_statuses`

Task statuses are fetched from `core_statuses` filtered by `type = 'task'`. The Kanban board uses these statuses as column definitions.

### Query to get task statuses

```sql
SELECT id, name, type_code, color, sort_index
FROM core_statuses
WHERE type = 'task'
ORDER BY sort_index ASC;
```

### Status behavior rules

| Status | `type_code` | Can be deleted? | Kanban column color |
|--------|-------------|-----------------|---------------------|
| TODO | `task_todo` | Yes | `#344054` (dark slate) |
| INPROGRESS | `task_inprogress` | No — API returns 403 | `#175CD3` (blue) |
| DONE | `task_done` | No — API returns 403 | `#0E7090` (teal) |

> Deletion check is done server-side by comparing `status_type` to `['task_inprogress', 'task_done']`. The UI should also visually suppress the Delete button for tasks in these statuses.

---

## 4. API Endpoints

### 4.1 Tasks

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/tasks` | `Task.VIEW` | List tasks. Supports `?filters=`, `?search=`, `?page=`, `?limit=`, `?sort_by=`, `?sort_dir=`, `?task_status_id=`, `?assigned_to=`, `?opportunity_id=`, `?fields=additional` |
| `POST` | `/tasks` | `Task.CREATE` | Create new task. Requires `opportunity_id` in body (stored in junction table, not on core_tasks). |
| `GET` | `/tasks/<id>` | `Task.VIEW` | Get single task with full joined data including opportunity, stage, assignee. |
| `PUT` | `/tasks/<id>` | `Task.UPDATE` | Update task. Tracks assignee and status changes in history tables. |
| `DELETE` | `/tasks/<id>` | `Task.DELETE` | Soft-validation delete. **Blocked for `task_inprogress` and `task_done` statuses.** Cascades: deletes `core_task_assignee_histories`, `core_task_status_histories`, `crm_opportunity_tasks`, then `core_tasks`. |
| `PATCH` | `/tasks/<id>/status` | `Task.UPDATE` | Update task status with Kanban drag-and-drop. Recalculates `sort_index` using float midpoint. Logs to `core_task_status_histories`. |
| `PUT` | `/tasks/<id>/status` | `Task.UPDATE` | Simple status update (no sort_index recalculation). Logs to `core_task_status_histories`. |
| `PATCH` | `/tasks/<id>/assignee` | `Task.UPDATE` | Update task assignee. Logs to `core_task_assignee_histories`. |
| `GET` | `/tasks/<id>/status-histories` | `Task.VIEW` | Paginated status change history for a task. |
| `GET` | `/tasks/<id>/assignee-histories` | `Task.VIEW` | Paginated assignee change history for a task. |
| `GET` | `/tasks/<id>/interactions` | `Task.VIEW` | List interactions for a task. |
| `POST` | `/tasks/<id>/interactions` | `Task_Interaction.CREATE` | Create interaction for a task. Auto-resolves `opportunity_id` and `customer_id` from task linkage. |
| `GET` | `/tasks/<id>/interactions/<int_id>` | `Task.VIEW` | Get single interaction. Returns entity data via `EntityService`. |
| `PUT` | `/tasks/<id>/interactions/<int_id>` | `Task.UPDATE` | Update an interaction. |
| `DELETE` | `/tasks/<id>/interactions/<int_id>` | `Task.DELETE` | Delete an interaction. |
| `GET` | `/tasks-statuses` | `Task.VIEW` | List all task statuses (from `core_statuses WHERE type = 'task'`). Includes `total_task_count`. Optional `?assigned_to=` to count per assignee. |
| `GET` | `/tasks-statuses/<task_status_id>/` | `Task.VIEW` | Single task status with total task count. |
| `GET` | `/tasks-assignees` | `Task.VIEW` | List unique users assigned to opportunity-linked tasks. Paginated, searchable. |
| `GET` | `/tasks/opportunities/many` | — | Get opportunity details for multiple task IDs. Query: `?ids=1,2,3` |
| `GET` | `/tasks/assignee/calendar` | — | Calendar view of tasks by date range. Query: `?start_date=`, `?end_date=`, `?assignee_id=` |

#### `POST /tasks` — Request Body

```json
{
  "task": "Follow up with client",
  "description": "Call to confirm policy terms",
  "task_status_id": 1,
  "assigned_to_id": 5,
  "assigned_date": "2025-07-25",
  "start_date": "2025-07-25",
  "due_date": "2025-07-30",
  "opportunity_id": 14
}
```

> `opportunity_id` is extracted and stored in `crm_opportunity_tasks`. It is NOT stored on `core_tasks`.

#### `PATCH /tasks/<id>/status` — Kanban drag-and-drop body

```json
{
  "source_status_id": 1,
  "destination_status_id": 2,
  "update_task_id": 7,
  "prev_task_id": 3,
  "next_task_id": 9
}
```

> New `sort_index` is calculated as: midpoint of `prev_task.sort_index` and `next_task.sort_index`. If no prev: `next / 2`. If no next: `prev + 1`. If neither: `1`.

#### `GET /tasks` query parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Searches `task`, `description`, `task_status_name`, `display_name`, `status_color`, `code` |
| `filters` | JSON string | Allowed: `task_status_id`, `assigned_to_id`, `start_date`, `due_date` |
| `task_status_id` | int | Filter by specific status |
| `assigned_to` | int | Filter by assigned user |
| `opportunity_id` | int | Filter by linked opportunity |
| `fields` | string | Pass `additional` to include opportunity data (stage info) per task |
| `page` | int | Page number (default 1) |
| `limit` | int | Page size (default 10) |
| `sort_by` | string | Allowed: `core_tasks.task`, `core_tasks.assigned_to_id`, `core_tasks.start_date` |
| `sort_dir` | string | `asc` or `desc` |

---

### 4.2 Task Types

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/task-types` | `TaskType.VIEW` | List all task types. Supports `?search=`, `?page=`, `?limit=` |
| `POST` | `/task-types` | `TaskType.CREATE` | Create a task type. `name` required, unique. |
| `GET` | `/task-types/<id>` | `TaskType.VIEW` | Get single task type. |
| `PUT` | `/task-types/<id>` | `TaskType.UPDATE` | Update task type. Name uniqueness excludes self. |
| `DELETE` | `/task-types/<id>` | `TaskType.DELETE` | Delete task type. **Blocked if any `crm_task_configs` row references it** — returns `CONFLICT`. |

#### `POST /task-types` — Request Body

```json
{
  "name": "Call",
  "description": "Phone call interaction"
}
```

---

### 4.3 Task Configs

| Method | Endpoint | Permission | Description |
|--------|----------|------------|-------------|
| `GET` | `/task-configs` | `TaskConfig.VIEW` | List task configs. Supports `?filters={"task_type_id":1, "opportunity_status_id":2}`, `?search=` (on `task`, `code`), `?page=`, `?limit=`, `?sort_by=crm_task_configs.sort_index` |
| `POST` | `/task-configs` | `TaskConfig.CREATE` | Create task config. Auto-generates `code` if not provided. Defaults `expected_days` to 1. |
| `GET` | `/task-configs/<id>` | `TaskConfig.VIEW` | Get single task config. |
| `PUT` | `/task-configs/<id>` | `TaskConfig.UPDATE` | Update task config. Converts empty `expected_days` to 1. |
| `DELETE` | `/task-configs/<id>` | `TaskConfig.DELETE` | Delete task config. Also deletes related `crm_opportunity_tasks` rows. |
| `POST` | `/task-configs/order` | `TaskConfig.UPDATE` | Reorder task configs within a stage. Body: `{ assigned_stage_id, order: [id1, id2, id3] }`. Sets `sort_index` = array index. |

#### `POST /task-configs` — Request Body

```json
{
  "task": "Initial discovery call",
  "task_type_id": 1,
  "opportunity_status_id": 3,
  "expected_days": 2,
  "reminder_expected_days": 1
}
```

---

## 5. Screen 1 — Task Management (Kanban + List View)

**Route:** `/crm/tasks`  
**Sidebar:** CRM → Tasks

### 5.1 Page Layout

The Task Management screen has a **two-panel layout**:

```
┌────────────────────────────────────────────────────────────┐
│  Page Header: "Task Management"          [Kanban View ↓]   │
├──────────────┬─────────────────────────────────────────────┤
│              │                                             │
│  LEFT PANEL  │   MAIN BOARD (Kanban or List)               │
│  (Users)     │                                             │
│              │   [TODO 762] [IN PROGRESS 3] [DONE 22]      │
│  User cards  │   Columns of task cards per status          │
│  Paginated   │                                             │
└──────────────┴─────────────────────────────────────────────┘
```

### 5.2 Left Panel — Users

| Task ID | Component | Description |
|---------|-----------|-------------|
| TM-01 | Users list | Calls `GET /tasks-assignees`. Shows paginated user cards: avatar, display name, email. |
| TM-02 | User card selection | Clicking a user card sets `?assigned_to=<id>` filter on the task board. Selected card has a highlighted border (teal). |
| TM-03 | Pagination | "1–3 of 3" with Previous / Next below the user list. Page size: 3 per page. |
| TM-04 | Default state | On first load, no user is selected — all tasks visible across all users. |

### 5.3 Top Bar

| Task ID | Component | Description |
|---------|-----------|-------------|
| TM-05 | View toggle | "Kanban View" button with a dropdown arrow. Toggles between Kanban and List view. Default: Kanban. |
| TM-06 | Page title | "Task Management" as the H1. |

### 5.4 Kanban View

| Task ID | Component | Description |
|---------|-----------|-------------|
| TM-07 | Status columns | Calls `GET /tasks-statuses`. One column per status ordered by `sort_index`. Column header shows status name + count badge. |
| TM-08 | Column count badge | Badge shows total tasks in that status column. Color matches the status color from `core_statuses.color`. |
| TM-09 | Task cards | Each card shows: Task code (top-left, amber pill), Stage badge (top-right, colored dot), Task title, Assignee avatar + name, Assigned Date + Due Date labels and values, 3-dot actions menu. |
| TM-10 | Stage badge on card | The stage badge shows the **opportunity's** stage (from `crm_opportunity_statuses`), not the task status. Color comes from `stage_color`. |
| TM-11 | Task card — 3-dot menu | Options: View, Edit, Delete. Delete is hidden for tasks with `task_inprogress` or `task_done` status. |
| TM-12 | Kanban drag-and-drop | Cards can be dragged between status columns. On drop: call `PATCH /tasks/<id>/status` with `source_status_id`, `destination_status_id`, `update_task_id`, `prev_task_id` (card above drop point), `next_task_id` (card below drop point). |
| TM-13 | Column scroll | Each column scrolls independently. Column height fills the viewport. |
| TM-14 | Load tasks per column | Call `GET /tasks?task_status_id=<id>&assigned_to=<id>&fields=additional` for each column (or a single call filtered by the selected user). |
| TM-15 | Empty column state | Show "No tasks" placeholder when a column has 0 tasks. |

### 5.5 List View

| Task ID | Component | Description |
|---------|-----------|-------------|
| TM-16 | Table columns | Task Code, Task Title, Status badge, Stage badge (opportunity stage), Assignee, Assigned Date, Due Date, Actions |
| TM-17 | Search bar | Debounced search hitting `GET /tasks?search=`. Searches task title, code, status name, assignee name. |
| TM-18 | Filter by status | Dropdown filter for status. Appends `?task_status_id=` to query. |
| TM-19 | Pagination | Server-side. Shows "Showing X–Y of Z". Default page size: 10. |
| TM-20 | Add task button | "Add Task" button opens a create task modal/drawer. |

### 5.6 Create Task Modal

| Task ID | Component | Description |
|---------|-----------|-------------|
| TM-21 | Task name | Text input. Required. Maps to `task`. |
| TM-22 | Description | Textarea. Optional. Maps to `description`. |
| TM-23 | Status | Single-select from `GET /tasks-statuses`. Required. Maps to `task_status_id`. Default: first status (TODO). |
| TM-24 | Assigned To | Searchable user dropdown from `GET /tasks-assignees`. Optional. Maps to `assigned_to_id`. |
| TM-25 | Assigned Date | Date picker. Optional. Maps to `assigned_date`. |
| TM-26 | Start Date | Date picker. Optional. Maps to `start_date`. |
| TM-27 | Due Date | Date picker. Optional. Must be ≥ start_date. Maps to `due_date`. |
| TM-28 | Opportunity | Required. Searchable dropdown from `GET /crm/opportunities`. Maps to `opportunity_id` (stored in junction table). |
| TM-29 | Submit | Calls `POST /tasks`. On success: close modal, refresh board, show toast "Task created." |

---

## 6. Screen 2 — Task Single View

**Route:** `/crm/tasks/<id>/view`  
**API:** `GET /tasks/<id>`

### 6.1 Header Section

| Task ID | Component | Description |
|---------|-----------|-------------|
| SV-01 | Back button | Teal circle with left arrow. Navigates back to Task Management list. |
| SV-02 | Page title | "Task Management" |
| SV-03 | Edit button | Teal "Edit" button top-right. Opens edit form/drawer. Calls `PUT /tasks/<id>`. |

### 6.2 Detail Info Grid

A 3-column grid of labeled fields (label above, value below):

| Field | Data Source | Notes |
|-------|-------------|-------|
| Lead Code | `opportunity_code` | Shown as a teal link (e.g. `ORD-000014`). Links to the opportunity view. |
| Lead Name | `opportunity_title` | Plain text. |
| Lead Stage | `opportunity_stage_name` | Shown as a pill badge. Color from `opportunity_stage_color`. |
| Task | `task` | Task title. |
| Description | `description` | Plain text. Shows `—` if null. |
| Assigned Date | `assigned_date` | Formatted date. Shows `—` if null. |
| Start Date | `start_date` | Formatted date. Shows `—` if null. |
| Due Date | `due_date` | Formatted date. Shows `—` if null. |
| Current Status | `task_status_name` | Pill badge. Color from `task_status_color`. |

### 6.3 Tabs Section

Three tabs below the detail grid:

#### Tab 1 — Interaction

| Task ID | Component | Description |
|---------|-----------|-------------|
| SV-04 | Interactions list | Calls `GET /tasks/<id>/interactions`. Table showing: Channel, Contact, Date, Notes, Status. |
| SV-05 | Add Interaction button | Opens a modal. Required fields: `channel_id`, `date`. Optional: `notes`, `contact_id`, `opportunity_status_id`. Calls `POST /tasks/<id>/interactions`. |
| SV-06 | Edit / Delete interaction | Row actions. Edit calls `PUT /tasks/<id>/interactions/<int_id>`. Delete calls `DELETE /tasks/<id>/interactions/<int_id>`. |

#### Tab 2 — Status Change

| Task ID | Component | Description |
|---------|-----------|-------------|
| SV-07 | Status history table | Calls `GET /tasks/<id>/status-histories`. Columns: Status (badge), Changed Date, Changed By, Remarks. |
| SV-08 | Status badge | Color from `task_status_color`. Shows status name in pill. |
| SV-09 | Pagination | Rows per page selector (10/25/50). Shows "X–Y of Z". Previous/Next. |

#### Tab 3 — Reassignment

| Task ID | Component | Description |
|---------|-----------|-------------|
| SV-10 | Reassignment history table | Calls `GET /tasks/<id>/assignee-histories`. Columns: Changed By (avatar + name), From Assignee (avatar + name), To Assignee (avatar + name), Date, Remark. |
| SV-11 | Pagination | Standard paginated table. |

---

## 7. Screen 3 — Task Types (Settings)

**Route:** `/crm/task-types`  
**Sidebar:** CRM → Task Types

### 7.1 List View

| Task ID | Component | Description |
|---------|-----------|-------------|
| TT-01 | Page header | "Task Types" + "Add Task Type" button. |
| TT-02 | Table | Columns: Name, Description, Actions (Edit, Delete). |
| TT-03 | Search | Debounced search on `name` and `description`. |
| TT-04 | Add Task Type | Opens a modal with Name (required) and Description (optional). Calls `POST /task-types`. |
| TT-05 | Edit Task Type | Opens pre-filled modal. Calls `PUT /task-types/<id>`. |
| TT-06 | Delete Task Type | Confirmation dialog. Calls `DELETE /task-types/<id>`. If the type is used in any Task Config, show error: "This task type cannot be deleted because it is used in one or more task configurations." |
| TT-07 | Pagination | Server-side. |

---

## 8. Screen 4 — Task Configs (General Settings)

**Route:** `/settings` → Tab: **Task Config**  
**Location:** Settings → General Settings → Task Config tab  
**Not** in the CRM sidebar — this is a system-wide settings screen accessible via the Settings navigation.

### 8.0 General Settings — Tab Structure

The Task Config screen lives inside the **General Settings** page, which has four tabs:

| Tab | Description |
|-----|-------------|
| Customer Portal | Customer portal configuration |
| Commission Config | Commission calculation rules |
| **Task Config** | Task configuration templates (this screen) |
| Permissions | Role-permission assignment matrix |

The page header shows "General Settings" with a back button (teal circle with left arrow chevron).

---

### 8.1 Task Config Tab — Layout

```
┌──────────────────────────────────────────────────────────────┐
│  [Customer Portal] [Commission Config] [Task Config] [Perms]│
│                                    [+ Add New Task Config]   │
│  ┌─ Search…  ──────────┐          [≡] [⊞] [⛶]              │
│  └─────────────────────┘                                     │
│  Task ↓ | Assigned Stage ↓ | Task Type ↓ | Expected Days ↓ | Reminder Days ↓ | Action │
│  ─────────────────────────────────────────────────────────── │
│  Test Task Config  ● LEAD   Test Task Type     1               0               ...     │
│  saas              ● LEAD   Test Task Type     1               0               ...     │
│  as                ● PROSPECT Test Task Type   1               0               ...     │
│  Nihil sed ipsum   ● LEAD   check_sorting      2               0               ...     │
│  Veritatis cum     ● LEAD   check_sorting      19              0               ...     │
│                          Rows per page: 10 ▾     1–5 of 5  ← Previous  Next →         │
└──────────────────────────────────────────────────────────────┘
```

---

### 8.2 Table Columns

| Column | Source | Notes |
|--------|--------|-------|
| Task | `crm_task_configs.task` | Config task name. Sortable. |
| Assigned Stage | `crm_task_configs.opportunity_status_id` → joined `core_statuses.name` | Displayed as colored badge with dot. Sortable. |
| Task Type | `crm_task_configs.task_type_id` → joined `crm_task_types.name` | Plain text. Sortable. |
| Expected Time Period To Complete (Days) | `crm_task_configs.expected_days` | Integer. Right-aligned. Sortable. Default 1. |
| Expected Time To Send Reminder (Days) | `crm_task_configs.reminder_expected_days` | Integer. Right-aligned. Sortable. Null stored as 0 displayed. |
| Action | — | 3-dot menu → Edit, Delete. |

---

### 8.3 UI Tasks

| Task ID | Component | Description |
|---------|-----------|-------------|
| TC-01 | Tab location | Task Config is the 3rd tab on the General Settings page. Clicking makes it active with teal underline + light teal background. |
| TC-02 | Add button | "Add New Task Config" button (teal, top-right of tab content). Opens the Add modal. |
| TC-03 | Search | Debounced search input. Filters on `task` name, stage name, task type name client-side. Server: `?search=` on `crm_task_configs.task` and `crm_task_configs.code`. |
| TC-04 | Toolbar icons | Three icon buttons: Filter (≡), Column visibility (⊞), Fullscreen (⛶). |
| TC-05 | Table sorting | All columns are sortable. Clicking column header toggles `sort_dir`. Sends `?sort_by=<col>&sort_dir=asc|desc` to `GET /task-configs`. |
| TC-06 | Stage badge | Colored pill badge: dot + stage name. Color comes from `core_statuses.color` for that stage. Background is a lighter tint of the same color. |
| TC-07 | 3-dot action menu | Context menu with: **Edit** (opens pre-filled modal), **Delete** (confirmation → `DELETE /task-configs/<id>`). |
| TC-08 | Pagination | Footer: "Rows per page" selector (10/25/50), page range ("1–5 of 5"), Previous / Next buttons. Default page size: 10. |
| TC-09 | Add Task Config modal | Title: "Add New Task Details". Fields: Task (required textarea), Task Type (required dropdown), Assigned Stage (required dropdown), Expected Days (number, default 1), Reminder Days (number, default 0). Buttons: **Create** (primary teal), **Cancel** (secondary). |
| TC-10 | Edit Task Config modal | Same as Add modal. Title: "Edit Task Details". Submit button: **Update**. Pre-populated with existing record values. Calls `PUT /task-configs/<id>`. |
| TC-11 | Delete confirmation | Browser confirm dialog or inline confirmation toast. Calls `DELETE /task-configs/<id>`. Server also cascades to delete related `crm_opportunity_tasks` rows. |

---

### 8.4 "Assigned Stage" Dropdown — Data Source

The Assigned Stage dropdown in the Add / Edit modal must be populated from:

```
GET core_statuses WHERE type = 'opportunity'
ORDER BY sort_index ASC
```

**Seeded opportunity stages available in dropdown:**

| Display Name | Type Code | Color | Sort |
|--------------|-----------|-------|------|
| LEAD | `opp_lead` | `#344054` | 1 |
| PROSPECT | `opp_prospect` | `#175CD3` | 2 |
| QUALIFIED | `opp_qualified` | `#0E7090` | 3 |
| WON | `opp_won` | `#067647` | 4 |
| LOSS | `opp_loss` | `#B42318` | 5 |

> **Critical:** Filter by `type = 'opportunity'` — NOT `type = 'task'`. Task configs are linked to opportunity stages (what stage an opportunity is in when the task should be triggered), not to task statuses.

The dropdown shows the stage **name** only (e.g. "LEAD", "PROSPECT"). The `id` is stored as `opportunity_status_id` on `crm_task_configs`.

---

### 8.5 "Task Type" Dropdown — Data Source

The Task Type dropdown in the Add / Edit modal must be populated from:

```
GET /task-types
```

Returns all rows from `crm_task_types`. Each option shows `name`. Stores `id` as `task_type_id` on `crm_task_configs`.

> Only active task types appear. If a task type was deleted, it must not appear in the dropdown (server enforces this via the FK constraint).

---

### 8.6 Add / Edit Modal — Field Reference

| Field | Required | Type | Default | Maps to | Validation |
|-------|----------|------|---------|---------|------------|
| Task | Yes | Textarea | — | `crm_task_configs.task` | Non-empty string |
| Task Type | Yes | Dropdown (`GET /task-types`) | — | `crm_task_configs.task_type_id` | Must select a valid type |
| Assigned Stage | Yes | Dropdown (`core_statuses WHERE type='opportunity'`) | — | `crm_task_configs.opportunity_status_id` | Must select a valid stage |
| Expected Time Period To Complete (Days) | No | Number | `1` | `crm_task_configs.expected_days` | Integer ≥ 1. Server defaults to 1 if empty. |
| Expected Time To Send Reminder (Days) | No | Number | `0` | `crm_task_configs.reminder_expected_days` | Integer ≥ 0. Server stores NULL if empty. |

**POST /task-configs request body:**
```json
{
  "task": "Initial discovery call",
  "task_type_id": 1,
  "opportunity_status_id": 1,
  "expected_days": 2,
  "reminder_expected_days": 1
}
```

**Server behavior on create:**
- If `code` not provided → server auto-generates a unique 6-digit numeric code
- If `expected_days` is empty/null → defaults to `1`
- If `reminder_expected_days` is empty → stored as `NULL` in DB

---

## 9. Business Logic & Key Rules

### 9.1 Task Creation

1. `opportunity_id` is **required** at creation. It is NOT stored on `core_tasks` — it goes into `crm_opportunity_tasks`.
2. If `code` is not provided, the server generates a unique 6-digit random numeric code.
3. `sort_index` is auto-set to `max(sort_index) + 1` within the target `task_status_id`. This ensures new tasks appear at the bottom of the Kanban column.
4. `changed_by_id` is automatically set from `request.user.id`.

### 9.2 Kanban Drag-and-Drop Sort Index

All sort_index calculations use the float midpoint formula:

| Case | Formula |
|------|---------|
| Between task A and task B | `(A.sort_index + B.sort_index) / 2` |
| Before the first task | `first_task.sort_index / 2` |
| After the last task | `last_task.sort_index + 1` |
| No neighbors | `1` |

This allows reordering without updating any other records.

### 9.3 Task Deletion Guard

Deletion is **blocked at the API level** for tasks where `task_status.type_code IN ('task_inprogress', 'task_done')`. The UI should:
1. Hide the Delete action button for these tasks.
2. If the API returns `FORBIDDEN`, display: "This task cannot be deleted because it is in progress or already done."

Deletion cascade order:
1. `core_task_assignee_histories` WHERE `task_id = id`
2. `core_task_status_histories` WHERE `task_id = id`
3. `crm_opportunity_tasks` WHERE `task_id = id`
4. `core_tasks` WHERE `id = id`

All steps run inside a database transaction.

### 9.4 Status Change Logging

Every status change — whether via Kanban drag-and-drop (`PATCH /tasks/<id>/status`) or direct update (`PUT /tasks/<id>/status`) — writes a row to `core_task_status_histories` with:
- `task_id`
- `task_status_id` (new status)
- `changed_by_id`
- `remark`: "Task status changed from {old_status_name} to {new_status_name}"
- `created_at`

### 9.5 Assignee Change Logging

When the assignee is changed (via `PUT /tasks/<id>` or `PATCH /tasks/<id>/assignee`), if `old_assigned_to != new_assigned_to`, a row is written to `core_task_assignee_histories`:
- `task_id`
- `from_assigned_id`, `to_assigned_id`
- `changed_by_id`
- `remark`: "Task reassigned from {old_name} to {new_name}"

### 9.6 Interaction Auto-Population

When creating a task interaction (`POST /tasks/<id>/interactions`), the server auto-resolves:
- `opportunity_id`: from `crm_opportunity_tasks WHERE task_id = id` if not provided
- `customer_id`: from `crm_opportunities WHERE id = opportunity_id` if not provided
- `contact_by_id`: from `request.user.id`
- `entity_id`: created via `EntityService.store("Interaction", request)`

### 9.7 Task Config `expected_days` Default

If `expected_days` is empty string or null, the server sets it to `1` (not `0` or `NULL`). The UI number input should default to `1` and not allow submission of an empty value.

---

## 10. Permission Reference

| Permission Key | Endpoint Actions Gated |
|----------------|------------------------|
| `Task.VIEW` | `GET /tasks`, `GET /tasks/<id>`, `GET /tasks/<id>/status-histories`, `GET /tasks/<id>/assignee-histories`, `GET /tasks/<id>/interactions`, `GET /tasks-statuses`, `GET /tasks-assignees` |
| `Task.CREATE` | `POST /tasks` |
| `Task.UPDATE` | `PUT /tasks/<id>`, `PATCH /tasks/<id>/status`, `PUT /tasks/<id>/status`, `PATCH /tasks/<id>/assignee` |
| `Task.DELETE` | `DELETE /tasks/<id>` |
| `Task_Interaction.CREATE` | `POST /tasks/<id>/interactions` |
| `Task.UPDATE` (reused) | `PUT /tasks/<id>/interactions/<int_id>`, `DELETE /tasks/<id>/interactions/<int_id>` |
| `TaskType.VIEW` | `GET /task-types`, `GET /task-types/<id>` |
| `TaskType.CREATE` | `POST /task-types` |
| `TaskType.UPDATE` | `PUT /task-types/<id>` |
| `TaskType.DELETE` | `DELETE /task-types/<id>` |
| `TaskConfig.VIEW` | `GET /task-configs`, `GET /task-configs/<id>` |
| `TaskConfig.CREATE` | `POST /task-configs` |
| `TaskConfig.UPDATE` | `PUT /task-configs/<id>`, `POST /task-configs/order` |
| `TaskConfig.DELETE` | `DELETE /task-configs/<id>` |

---

## 11. Non-Functional Requirements

| # | Requirement |
|---|-------------|
| NFR-01 | The Kanban board must support drag-and-drop between status columns. Drop must call `PATCH /tasks/<id>/status` and update `sort_index` via the float midpoint formula without re-indexing other tasks. |
| NFR-02 | The `GET /tasks` endpoint must support filtering by `task_status_id`, `assigned_to`, and `opportunity_id` simultaneously. |
| NFR-03 | The task status `type_code` values (`task_todo`, `task_inprogress`, `task_done`) must be used for business logic checks — not the display `name` — because names can be renamed. |
| NFR-04 | All status and assignee changes must be logged atomically with the task update (not as a separate background job). |
| NFR-05 | Task deletion must run all cascade deletes inside a single database transaction. If any step fails, all steps are rolled back. |
| NFR-06 | The `opportunity_id` field is required for task creation but is not stored on `core_tasks`. It must be stored in `crm_opportunity_tasks` immediately after the task is created. |
| NFR-07 | The Task Config order endpoint (`POST /task-configs/order`) must accept `assigned_stage_id` and an `order` array of config IDs, and update each config's `sort_index` to its position in the array (0-indexed). |
| NFR-08 | The Kanban view column counts (e.g. "TODO 762") must come from `GET /tasks-statuses` which includes `total_task_count` per status. When a user filter is applied, re-fetch with `?assigned_to=<id>` to get filtered counts. |
| NFR-09 | Task type deletion must check for references in `crm_task_configs` before deleting. The API returns `CONFLICT`; the UI shows an explanatory error message. |
| NFR-10 | The calendar view endpoint (`GET /tasks/assignee/calendar`) returns tasks formatted as `{ id, title, start, end }` where both `start` and `end` are derived from `start_date`. |

---

*Document prepared from codebase analysis of `task_controller.py`, `task_config_controller.py`, URL configuration, and model definitions. Version 1.0.*

## Task Status Summary

| Task | Status | Date |
|------|--------|------|
| Backend API Implementation | Completed | 2026-03-26 |
| Core Settings UI Integration | Completed | 2026-03-26 |
| CRM Task Management UI (Vanguard X) | Completed | 2026-03-27 |
| CRM Task Type CRUD | Completed | 2026-03-27 |
| Database Migrations | Completed | 2026-03-26 |
