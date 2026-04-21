# Envoy Platform Deployment Guidelines

## Core Module Database Migrations
Run the following commands in the `envoy_core\envoy_core_api` directory:
```powershell
python manage.py migrate
```
> [!NOTE]
> The initial migrations (`0001_initial.py`) have been consolidated to resolve circular dependencies between the core models and the custom user model.

## CRM Deployment Guidelines

## Database Migrations
Run the following commands in the `envoy_crm\envoy_crm_api` directory:
```powershell
python manage.py makemigrations 
python manage.py migrate --fake sales
python manage.py migrate --fake task
```
> [!IMPORTANT]
> If you encounter `InconsistentMigrationHistory`, manually verify the `django_migrations` table for any mismatched record names (e.g., `0001_initial_opportunity_cre` instead of `0001_initial`).

## Dependency Management
- Ensure `mServices` is installed in the Python environment.
- Verify that `messages.py` and `setting_keys.py` exist in the root of the `envoy_crm_api` project directory. These provide essential service constants for the controllers.

## Data Seeding
Ensure that the `core_status` table in the Core database contains entries with `module='task'`. These statuses define the Kanban columns in the CRM Task Management view. 

## Environment Variables
No new environment variables are required, provided that the `CRM_API_URL` is correctly configured in the Core UI and the `CORE_API_URL` is correctly configured in the CRM UI.

## Authentication
The CRM API validates bearer tokens against the `JWT_SECRET` shared with the Core module. Ensure these secrets match in both modules' production environments.
