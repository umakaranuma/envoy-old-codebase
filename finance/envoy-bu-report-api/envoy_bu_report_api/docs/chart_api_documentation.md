# Chart API Documentation

## Overview
The Chart API provides endpoints to retrieve chart data in various formats suitable for different chart types and visualization libraries. The API now includes chart data directly in the main endpoints for convenience.

## Endpoints

### 1. Get Chart by ID (with optional chart data)
**Endpoint:** `GET /report-charts/{id}`

**Description:** Retrieves a single report chart with optional chart data.

**Parameters:**
- `id` (path): Chart ID
- `data_only` (query, optional): Set to `true` to return only chart data without metadata
- `from_date` (query, optional): Start date for filtering
- `to_date` (query, optional): End date for filtering
- `date_column` (query, optional): Column name for date filtering
- `filter_values` (query, optional): JSON string of additional filters

**Response Options:**
- **With metadata (default):** Chart information + `chart_data` field
- **Data only:** Set `data_only=true` to get only the formatted chart data

### 2. Get All Charts for a Report (with optional chart data)
**Endpoint:** `GET /report-charts/report/{report_id}`

**Description:** Retrieves all charts for a specific report with optional chart data.

**Parameters:**
- `report_id` (path): Report ID
- `data_only` (query, optional): Set to `true` to return only chart data without metadata
- `from_date` (query, optional): Start date for filtering
- `to_date` (query, optional): End date for filtering
- `date_column` (query, optional): Column name for date filtering
- `filter_values` (query, optional): JSON string of additional filters

**Response Options:**
- **With metadata (default):** Array of charts with `chart_data` field for each
- **Data only:** Set `data_only=true` to get only the formatted chart data for all charts

### 3. Get Chart Data by ID (Legacy)
**Endpoint:** `GET /report-chart-data/{id}`

**Description:** Legacy endpoint that retrieves only chart data for visualization.

**Parameters:**
- `id` (path): Chart ID
- `from_date` (query, optional): Start date for filtering
- `to_date` (query, optional): End date for filtering
- `date_column` (query, optional): Column name for date filtering
- `filter_values` (query, optional): JSON string of additional filters

**Response:** Formatted data based on chart type

### 4. Get Chart Data by Report ID (Legacy)
**Endpoint:** `GET /report-chart-data/report/{report_id}`

**Description:** Legacy endpoint that retrieves chart data for all charts in a specific report.

**Parameters:**
- `report_id` (path): Report ID
- `from_date` (query, optional): Start date for filtering
- `to_date` (query, optional): End date for filtering
- `date_column` (query, optional): Column name for date filtering
- `filter_values` (query, optional): JSON string of additional filters

**Response:** Object containing all charts with their formatted data

## Chart Types and Response Formats

### Single Bar / Line Single / Area Single
**Chart Types:** `single_bar`, `line_single`, `area_single`, `bar_single`

**Response Format:**
```json
[
    {
        "label": "NPR001",
        "value": "native product 1"
    },
    {
        "label": "NPR002",
        "value": "test native"
    }
]
```

**Alternative Format (fallback):**
```json
{
    "invoice_no": ["INV-001", "INV-002"],
    "total_amount": ["100.00", "200.00"]
}
```

### Stacked Bar / Line Multiple / Area Multi
**Chart Types:** `stacked_bar`, `line_multiple`, `area_multi`, `bar_stacked`, `line_multi`, `area_multiple`

**Response Format:**
```json
{
    "labels": ["2025-04-30", "2025-06-02"],
    "datasets": [
        {
            "label": "INV-001",
            "data": [100, 0]
        },
        {
            "label": "INV-002",
            "data": [0, 200]
        }
    ]
}
```

### Group Bar
**Chart Types:** `group_bar`, `bar_group`, `grouped_bar`

**Response Format:**
```json
{
    "labels": ["INV-001", "INV-002"],
    "datasets": [
        {
            "label": "Group 1",
            "data": [1, 0]
        },
        {
            "label": 13,
            "data": [0, 1]
        }
    ]
}
```

### Donut / Pie
**Chart Types:** `donut`, `pie`, `donut_pie`, `pie_chart`

**Response Format:**
```json
[
    {
        "label": "INV-001",
        "value": "100.00"
    },
    {
        "label": "INV-002",
        "value": "200.00"
    }
]
```

### Scatter Plot
**Chart Types:** `scatter`, `scatter_plot`, `scatterplot`

**Response Format:**
```json
{
    "labels": {
        "x": "date",
        "y": "total_amount"
    },
    "data": [
        {
            "date": "2025-04-30",
            "total_amount": "100.00"
        }
    ]
}
```

### Area Chart - Single
**Chart Types:** `area_single`, `area_chart_single`

**Response Format:**
```json
{
    "date": ["2025-04-30", "2025-06-02"],
    "total_amount": ["100.00", "200.00"]
}
```

### Area Chart - Multi
**Chart Types:** `area_multi`, `area_chart_multi`, `area_multiple`

**Response Format:**
```json
{
    "labels": ["2025-04-30", "2025-06-02"],
    "datasets": [
        {
            "label": "100.00",
            "data": [1, 0]
        },
        {
            "label": "200.00",
            "data": [0, 1]
        }
    ]
}
```

## Usage Examples

### Example 1: Get Chart with Metadata and Data
```bash
GET /report-charts/123
```
**Response includes:** Chart information + `chart_data` field with formatted data

### Example 2: Get Chart Data Only
```bash
GET /report-charts/123?data_only=true
```
**Response:** Only the formatted chart data (no metadata)

### Example 3: Get All Charts for Report with Data
```bash
GET /report-charts/report/456
```
**Response includes:** Array of charts, each with `chart_data` field

### Example 4: Get All Chart Data for Report Only
```bash
GET /report-charts/report/456?data_only=true
```
**Response:** Object with chart data only (no metadata)

### Example 5: Apply Date Filtering
```bash
GET /report-charts/123?from_date=2025-01-01&to_date=2025-12-31&date_column=created_at
```

### Example 6: Apply Additional Filters
```bash
GET /report-charts/123?filter_values={"status":"active","category":"sales"}
```

## Data Column Detection

The API automatically detects common column names:
- **Invoice/ID columns:** `invoice_no`, `id`, `invoice_id`, `code`
- **Amount columns:** `total_amount`, `amount`, `value`, `total`, `name`
- **Date columns:** `date`, `created_at`, `created_date`

## Response Structure

### With Metadata (default)
```json
{
    "is_success": true,
    "message": "Report chart retrieved successfully",
    "result": {
        "id": 123,
        "title": "Chart Title",
        "type": "single-bar",
        "chart_data": {
            "invoice_no": ["INV-001", "INV-002"],
            "total_amount": ["100.00", "200.00"]
        }
    }
}
```

### Data Only (data_only=true)
```json
{
    "is_success": true,
    "message": "default_get_success_msg",
    "result": {
        "invoice_no": ["INV-001", "INV-002"],
        "total_amount": ["100.00", "200.00"]
    }
}
```

## Error Handling

- **404 Not Found:** Chart or report not found
- **400 Bad Request:** Invalid parameters
- **500 Internal Server Error:** Server-side error

## Notes

- Chart types are case-insensitive and support various naming conventions
- Date filtering requires both `from_date` and `to_date` parameters
- The `filter_values` parameter should be a valid JSON string
- All amounts are returned as strings to preserve decimal precision
- Use `data_only=true` to get the same response format as the legacy chart data endpoints
- The main endpoints now provide both metadata and chart data in a single request
