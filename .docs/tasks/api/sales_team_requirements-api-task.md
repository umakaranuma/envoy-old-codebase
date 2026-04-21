# API Tasks: Sales Team Module — Requirements

## 3.1 Create Sales Team
- [ ] Define database model/schema.
- [ ] Create POST endpoint with validation.
- [ ] Implement permission checks.

## 3.2 Read / List Sales Teams
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

## 3.3 View Sales Team Detail
- [ ] Create GET endpoint (list) with filters.
- [ ] Implement permission checks for viewing.

## 3.4 Edit Sales Team
- [ ] Create PUT/PATCH endpoint with validation.
- [ ] Implement permission checks for editing.

## 3.5 Delete Sales Team
- [ ] Create DELETE endpoint.
- [ ] Implement permission checks for deletion.

## 3.6 Manage Team Members
- [ ] Implement API logic for 3.6 Manage Team Members.

- [ ] Register permission: `sales_team.view` (View the sales team list and team details)
- [ ] Register permission: `sales_team.create` (Create a new sales team)
- [ ] Register permission: `sales_team.edit` (Edit an existing team's name, account manager, and members)
- [ ] Register permission: `sales_team.delete` (Permanently delete a sales team)
- [ ] Ensure API supports: Should there be a maximum limit on the number of members per team?
- [ ] Ensure API supports: When the account manager of a team is deactivated, should the team be flagged or automatically unassigned?
- [ ] Ensure API supports: Should a user be able to view only the teams they belong to, or all teams in the system?
- [ ] Ensure API supports: Should team membership history be tracked (e.g., who was added/removed and when)?

---
## Task Status
| Task Type | Status | Assignee | Notes |
|---|---|---|---|
| Development | Pending |  | |
| Testing | Pending |  | |
