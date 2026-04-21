# Flag Management - Backend Tasks

## Models & Database
- [ ] Create `Flag` model in `envoy_core_api`.
  - Ensure table name is `core_flags` per the namespace rule.
  - Fields: `name` (CharField), `description` (TextField, optional), `color_code` (CharField), `deleted_at` (DateTimeField for soft delete), timestamps.
  - Soft-delete logic.

## Permissions
- [ ] Add following permissions to the system:
  - `flag.create`
  - `flag.view`
  - `flag.edit`
  - `flag.delete`

## Controllers / Views & Serializers
- [ ] Create `FlagSerializer`. Validate color code format. Handle "duplicate names" warning if needed natively.
- [ ] Implement CRUD ViewSet or individual controllers for Flags in `envoy_core_api`:
  - `GET /flags` - search, exclude deleted.
  - `POST /flags`
  - `PUT /flags/<id>`
  - `DELETE /flags/<id>` (soft delete)

## Architecture
- Ensure it conforms to the skill guidelines for Django/Core APIs in this project.
