# Reporting System Documentation

This module provides a comprehensive reporting system for the Envoy BU Report API, built with Django and following a controller-based architecture.

## Overview

The reporting system consists of five main components:
1. **Report Types** - Categories for organizing reports
2. **Reports** - Main report entities with SQL queries and JSON configurations
3. **Report Charts** - Visual representations of report data
4. **Report Dashboards** - Collections of reports and charts
5. **Dashboard Tiles** - Individual components within dashboards

## Models

### ReportType
- `entity_id` - Unique identifier
- `name` - Type name
- `module` - Module classification
- `description` - Optional description
- Standard audit fields (created_by_id, updated_by_id, deleted_by_id, timestamps)

### Report
- `title` - Report title
- `type_id` - Foreign key to ReportType
- `entity_id` - Unique identifier
- `views` - View configuration
- `description` - Optional description
- `query` - SQL query string
- `json` - JSON configuration for dynamic query generation
- Standard audit fields

### ReportChart
- `report_id` - Foreign key to Report
- `title` - Chart title
- `type` - Chart type (bar, line, pie, etc.)
- `json` - Chart configuration
- `description` - Optional description
- Timestamps

### ReportDashboard
- `title` - Dashboard title
- `description` - Optional description
- `entity_id` - Unique identifier
- `module` - Module classification
- Standard audit fields

### ReportDashboardTile
- `entity_id` - Unique identifier
- `dashboard_id` - Foreign key to ReportDashboard
- `chart_id` - Optional foreign key to ReportChart
- `report_id` - Foreign key to Report
- `type` - Tile type
- Standard audit fields

## Services

### ResponseService
Standardized API response handling with proper HTTP status codes.

### SQLGeneratorService
Generates SQL queries from JSON configuration:
- Parses field definitions
- Builds SELECT clauses with aliases
- Handles WHERE conditions
- Supports table aliases

### SqlHelperService
SQL manipulation utilities:
- `remove_skipped_columns_from_sql()` - Removes specified columns from SELECT
- `apply_sort()` - Adds ORDER BY clauses
- `build_chart_where_clause()` - Builds WHERE clauses for charts
- `sanitize_json_data()` - Cleans JSON data

## Controllers

### ReportController
Main report management with methods:
- `get_all()` - List reports with filtering/pagination
- `get_one()` - Get single report
- `store_or_update()` - Create/update reports
- `delete()` - Soft delete reports
- `get_query_data()` - Execute dynamic queries
- `query_generate()` - Generate SQL from JSON

### ReportTypeController
Report type management with CRUD operations.

### ReportChartController
Chart management with additional methods:
- `get_by_report()` - Get charts for specific report
- `get_chart_data()` - Execute chart queries

### ReportDashboardController
Dashboard management with CRUD operations.

### DashboardTileController
Tile management with additional methods:
- `get_by_dashboard()` - Get tiles for specific dashboard

## API Endpoints

### Report Types
- `GET /report-types` - List report types
- `GET /report-types/{id}` - Get report type
- `POST /report-types` - Create report type
- `PUT /report-types/{id}` - Update report type
- `DELETE /report-types/{id}` - Delete report type

### Reports
- `GET /reports` - List reports
- `GET /reports/{id}` - Get report
- `POST /reports` - Create report
- `PUT /reports/{id}` - Update report
- `DELETE /reports/{id}` - Delete report
- `POST /generate-query` - Generate SQL from JSON
- `GET /report-data/{id}` - Get report data

### Report Charts
- `GET /report-charts` - List charts
- `GET /report-charts/{id}` - Get chart
- `POST /report-charts` - Create chart
- `PUT /report-charts/{id}` - Update chart
- `DELETE /report-charts/{id}` - Delete chart
- `GET /report-charts/report/{report_id}` - Get charts by report
- `GET /report-chart-data/{id}` - Get chart data

### Dashboards
- `GET /dashboards` - List dashboards
- `GET /dashboards/{id}` - Get dashboard
- `POST /dashboards` - Create dashboard
- `PUT /dashboards/{id}` - Update dashboard
- `DELETE /dashboards/{id}` - Delete dashboard

### Dashboard Tiles
- `GET /dashboard-tiles` - List tiles
- `GET /dashboard-tiles/{id}` - Get tile
- `POST /dashboard-tiles` - Create tile
- `PUT /dashboard-tiles/{id}` - Update tile
- `DELETE /dashboard-tiles/{id}` - Delete tile
- `GET /dashboard-tiles/dashboard/{dashboard_id}` - Get tiles by dashboard

## Features

### Dynamic SQL Generation
The system can generate SQL queries from JSON configurations:
```json
{
  "fields": [
    {"code": "u.name", "label": "User Name"},
    {"code": "u.email", "label": "Email"}
  ],
  "filters": [
    {"code": "u.status", "default": "active"}
  ]
}
```

### Advanced Filtering
- Search functionality across multiple fields
- Date range filtering
- Custom filter operators (LIKE, =, etc.)
- Pagination support

### Chart Integration
- Support for various chart types
- Dynamic data fetching for charts
- Chart-specific filtering

### Dashboard Management
- Tile-based dashboard layouts
- Chart and report integration
- Flexible tile positioning

## Usage Examples

### Creating a Report
```python
# Create report type
report_type = ReportType.objects.create(
    entity_id=1,
    name="User Reports",
    module="users",
    created_by_id=1
)

# Create report
report = Report.objects.create(
    title="Active Users Report",
    type_id=report_type,
    entity_id=1,
    json={
        "fields": [
            {"code": "u.name", "label": "Name"},
            {"code": "u.email", "label": "Email"}
        ]
    },
    created_by_id=1
)
```

### Generating SQL
```python
# Generate SQL from JSON
sql = SQLGeneratorService.generate_from_input(report.json)
# Returns: SELECT u.name AS "Name", u.email AS "Email" FROM u WHERE u.status = 'active';
```

### Getting Report Data
```python
# Execute dynamic query with filtering
data = ReportController.get_query_data(request, report_id)
```

## Database Tables

The system creates the following tables:
- `rep_report_types` - Report types
- `rep_reports` - Reports
- `rep_report_charts` - Report charts
- `rep_report_dashboards` - Dashboards
- `rep_report_dashboard_tiles` - Dashboard tiles

## Security Features

- Soft deletes for data preservation
- Input validation and sanitization
- SQL injection prevention through parameterized queries
- Standardized error handling and logging

## Dependencies

- Django 3.2+
- PostgreSQL (for JSONField support)
- psycopg2 (PostgreSQL adapter)

## Migration

Run migrations to create the database tables:
```bash
python manage.py makemigrations reports
python manage.py migrate
``` 