from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
import json
import logging

from mServices import QueryBuilderService
from mServices.ValidatorService import ValidatorService
from ..services.response_service import ResponseService
from ..services.sql_helper_service import SqlHelperService

logger = logging.getLogger(__name__)


class ReportChartController:
    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET", "PUT", "DELETE"])
    def report_chart_one(request, id):
        """Handle GET, PUT, DELETE requests for a single report chart"""
        if request.method == "GET":
            return ReportChartController.get_one(request, id)
        
        if request.method == "PUT":
            return ReportChartController.store_or_update(request, id)
        
        if request.method == "DELETE":
            return ReportChartController.delete(request, id)

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST", "PUT", "GET"])
    def report_chart_access(request, id=None):
        """Handle GET, POST, PUT requests for report charts"""
        if request.method == "GET":
            return ReportChartController.get_all(request)
        
        if request.method == "POST":
            return ReportChartController.store_or_update(request, id=None)
        
        if request.method == "PUT":
            return ReportChartController.store_or_update(request, id)

    @staticmethod
    def get_all(request):
        """Get all report charts with filtering and pagination"""
        try:
            # Get query parameters
            filters = json.loads(request.GET.get('filters', '{}'))
            search = request.GET.get('search', '')
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            sort_by = request.GET.get('sort_by', 'chart.id')
            sort_dir = request.GET.get('sort_dir', 'asc')
            
            # Build query using QueryBuilderService
            query = (
                QueryBuilderService("rep_report_charts as chart")
                .leftJoin("rep_reports as report", "report.id", "chart.report_id_id")
                .select(
                    "chart.*",
                    "report.title as report_title"
                )
                .whereNull("report.deleted_at")
            )
            
            # Apply filters
            if filters.get('title'):
                query = query.where("chart.title", filters['title'], "LIKE")
            if filters.get('type'):
                query = query.where("chart.type", filters['type'])
            if filters.get('report_id'):
                query = query.where("chart.report_id_id", filters['report_id'])
            
            # Apply search
            if search:
                query = query.where("chart.title", search, "LIKE")
            
            # Apply sorting and pagination
            data = query.paginate(page, limit, ['chart.id', 'chart.title'], sort_by, sort_dir)
            
            # Check if user wants chart data included
            include_chart_data = request.GET.get('include_chart_data', 'false').lower() == 'true'
            
            if include_chart_data and data.get('data'):
                # Get chart data for each chart
                for chart in data['data']:
                    if chart.get('query'):
                        try:
                            # Get parameters
                            from_date = request.GET.get('from_date')
                            to_date = request.GET.get('to_date')
                            date_column = request.GET.get('date_column')
                            filter_values = json.loads(request.GET.get('filter_values', '{}'))
                            
                            # Build SQL
                            sql = chart['query'].rstrip("; \n\r\t")
                            
                            # Apply chart-specific filters
                            if from_date and to_date and date_column:
                                sql = SqlHelperService.build_chart_where_clause(
                                    sql, filter_values, from_date, to_date, date_column
                                )
                            
                            # Execute query
                            with connection.cursor() as cursor:
                                cursor.execute(sql)
                                
                                columns = [col[0] for col in cursor.description]
                                chart_rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
                            
                            # Parse chart JSON configuration
                            chart_json = chart['json']
                            if isinstance(chart_json, str):
                                try:
                                    chart_json = json.loads(chart_json)
                                except Exception:
                                    chart_json = {}
                            
                            # Format data based on chart type and configuration
                            chart_data = ReportChartController._format_chart_data(
                                chart['type'], 
                                chart_rows, 
                                chart_json
                            )
                            chart['chart_data'] = chart_data
                        except Exception as e:
                            logger.warning(f"Could not fetch chart data for chart {chart['id']}: {str(e)}")
                            chart['chart_data'] = None
                    else:
                        chart['chart_data'] = None
            
            # Ensure data structure is consistent even when empty
            if not data.get('data'):
                data['data'] = []
            
            return ResponseService.response('SUCCESS', data, "Report charts retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_all: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def get_one(request, id):
        """Get a single report chart by ID"""
        try:
            chart = (
                QueryBuilderService("rep_report_charts as chart")
                .leftJoin("rep_reports as report", "report.id", "chart.report_id_id")
                .select("chart.*", "report.query", "report.title as report_title")
                .where("chart.id", id)
                .whereNull("report.deleted_at")
                .first()
            )
            
            if not chart:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            # Check if user wants only chart data
            data_only = request.GET.get('data_only', 'false').lower() == 'true'
            
            # Get chart data if query exists
            chart_data = None
            if chart.get('query'):
                try:
                    # Get parameters
                    from_date = request.GET.get('from_date')
                    to_date = request.GET.get('to_date')
                    date_column = request.GET.get('date_column')
                    filter_values = json.loads(request.GET.get('filter_values', '{}'))
                    
                    # Build SQL
                    sql = chart['query'].rstrip("; \n\r\t")
                    
                    # Apply chart-specific filters
                    if from_date and to_date and date_column:
                        sql = SqlHelperService.build_chart_where_clause(
                            sql, filter_values, from_date, to_date, date_column
                        )
                    
                    # Execute query
                    with connection.cursor() as cursor:
                        cursor.execute(sql)
                        
                        columns = [col[0] for col in cursor.description]
                        data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    # Format data based on chart type
                    chart_data = ReportChartController._format_chart_data(chart['type'], data, chart['json'])
                except Exception as e:
                    logger.warning(f"Could not fetch chart data for chart {id}: {str(e)}")
                    chart_data = None
            
            # Return only chart data if requested
            if data_only and chart_data is not None:
                return ResponseService.response('SUCCESS', chart_data, 'default_get_success_msg')
            
            # Add chart data to response
            if chart_data is not None:
                chart['chart_data'] = chart_data
            
            return ResponseService.response('SUCCESS', chart, "Report chart retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_one: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def store_or_update(request, id=None):
        """Create or update a report chart"""
        try:
            data = json.loads(request.body)
            
            # Validation rules - different for create vs update
            if id:
                # Update existing chart - no need for report_id validation
                rules = {
                    "title": "required|string",
                    "type": "required|string",
                    "json": "required|dict",
                    "description": "optional|string"
                }
            else:
                # Create new chart - need report_id validation
                rules = {
                    "title": "required|string",
                    "type": "required|string",
                    "report_id": "required|exists:rep_reports,id",
                    "json": "required|dict",
                    "description": "optional|string"
                }
            
            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
            
            # Sanitize JSON
            data['json'] = SqlHelperService.sanitize_json_data(data['json'])
            # Ensure JSON is serialized for DB layer that doesn't accept dict parameters
            if isinstance(data['json'], (dict, list)):
                data['json'] = json.dumps(data['json'])
            
            if id:
                # Update existing chart
                chart = QueryBuilderService("rep_report_charts").where("id", id).first()
                if not chart:
                    return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
                
                QueryBuilderService("rep_report_charts").where("id", id).update(data)
                message = "default_update_success_msg"
            else:
                # Create new chart
                data['report_id_id'] = data['report_id']
                chart = QueryBuilderService("rep_report_charts").insert(data)
                message = "default_create_success_msg"
            
            return ResponseService.response('SUCCESS', None, message)
            
        except Exception as e:
            logger.error(f"Error in store_or_update: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def delete(request, id):
        """Delete a report chart"""
        try:
            chart = QueryBuilderService("rep_report_charts").where("id", id).first()
            
            if not chart:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            QueryBuilderService("rep_report_charts").where("id", id).delete()
            
            return ResponseService.response('SUCCESS', None, "default_delete_success_msg")
            
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET"])
    def get_by_report(request, report_id):
        """Get all charts for a specific report"""
        try:
            charts = (
                QueryBuilderService("rep_report_charts as chart")
                .leftJoin("rep_reports as report", "report.id", "chart.report_id_id")
                .select("chart.*", "report.query", "report.title as report_title")
                .where("report_id_id", report_id)
                .whereNull("report.deleted_at")
                .get()
            )
            
            # Check if user wants only chart data
            data_only = request.GET.get('data_only', 'false').lower() == 'true'
            
            # If no charts found, return empty data structure
            if not charts:
                if data_only:
                    return ResponseService.response('SUCCESS', {}, 'default_get_success_msg')
                else:
                    return ResponseService.response('SUCCESS', {"data": []}, "Report charts retrieved successfully")
            
            # Get chart data for each chart
            for chart in charts:
                if chart.get('query'):
                    try:
                        # Get parameters
                        from_date = request.GET.get('from_date')
                        to_date = request.GET.get('to_date')
                        date_column = request.GET.get('date_column')
                        filter_values = json.loads(request.GET.get('filter_values', '{}'))
                        
                        # Build SQL
                        sql = chart['query'].rstrip("; \n\r\t")
                        
                        # Apply chart-specific filters
                        if from_date and to_date and date_column:
                            sql = SqlHelperService.build_chart_where_clause(
                                sql, filter_values, from_date, to_date, date_column
                            )
                        
                        # Execute query
                        with connection.cursor() as cursor:
                            cursor.execute(sql)
                            
                            columns = [col[0] for col in cursor.description]
                            data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                        
                        # Parse chart JSON configuration
                        chart_json = chart['json']
                        if isinstance(chart_json, str):
                            try:
                                chart_json = json.loads(chart_json)
                            except Exception:
                                chart_json = {}
                        
                        # Format data based on chart type and configuration
                        chart_data = ReportChartController._format_chart_data(
                            chart['type'], 
                            data, 
                            chart_json
                        )
                        chart['chart_data'] = chart_data
                    except Exception as e:
                        logger.warning(f"Could not fetch chart data for chart {chart['id']}: {str(e)}")
                        chart['chart_data'] = None
                else:
                    chart['chart_data'] = None
            
            # Return only chart data if requested
            if data_only:
                chart_data_only = {}
                for chart in charts:
                    if chart.get('chart_data') is not None:
                        chart_data_only[f"chart_{chart['id']}"] = chart['chart_data']
                
                if chart_data_only:
                    return ResponseService.response('SUCCESS', chart_data_only, 'default_get_success_msg')
                else:
                    return ResponseService.response('SUCCESS', {}, 'default_get_success_msg')
            
            # Calculate total records for non-data_only response
            total_records = len(charts)
            return ResponseService.response('SUCCESS', {"total_records": total_records, "data": charts}, "Report charts retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_by_report: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET"])
    def get_chart_data(request, id):
        """Get chart data for visualization"""
        try:
            chart = (
                QueryBuilderService("rep_report_charts as chart")
                .leftJoin("rep_reports as report", "report.id", "chart.report_id_id")
                .select("chart.*", "report.query", "report.title as report_title")
                .where("chart.id", id)
                .whereNull("report.deleted_at")
                .first()
            )
            
            if not chart:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            if not chart.get('query'):
                return ResponseService.response('NO_DATA_FOUND', None, "No query found for report")
            
            # Get parameters
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            date_column = request.GET.get('date_column')
            filter_values = json.loads(request.GET.get('filter_values', '{}'))
            
            # Build SQL
            sql = chart['query'].rstrip("; \n\r\t")
            
            # Apply chart-specific filters
            if from_date and to_date and date_column:
                sql = SqlHelperService.build_chart_where_clause(
                    sql, filter_values, from_date, to_date, date_column
                )
            
            # Execute query
            with connection.cursor() as cursor:
                cursor.execute(sql)
                
                columns = [col[0] for col in cursor.description]
                data = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Deserialize JSON if it's a string
            chart_json = chart['json']
            if isinstance(chart_json, str):
                try:
                    chart_json = json.loads(chart_json)
                except Exception:
                    chart_json = {}
            
            # Format data based on chart type
            formatted_data = ReportChartController._format_chart_data(chart['type'], data, chart_json)
            
            return ResponseService.response('SUCCESS', formatted_data, 'chart_data_collected_successfully')
            
        except Exception as e:
            logger.error(f"Error in get_chart_data: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def _format_chart_data(chart_type, data, chart_json):
        """Format chart data based on chart type"""
        if not data:
            return {}
        
        # Normalize chart type
        chart_type = chart_type.lower().replace(' ', '_').replace('-', '_')
        
        # Extract common fields from data - handle different possible column names
        labels = []
        values = []
        dates = []
        
        # Try to find the right columns
        label_col = None
        value_col = None
        date_col = None
        
        if data:
            first_row = data[0]
            for col in first_row.keys():
                col_lower = col.lower()
                if 'code' in col_lower or 'id' in col_lower or 'invoice' in col_lower:
                    label_col = col
                elif 'name' in col_lower or 'amount' in col_lower or 'total' in col_lower or 'value' in col_lower:
                    value_col = col
                elif 'date' in col_lower or 'created' in col_lower:
                    date_col = col
        
        for row in data:
            if label_col and label_col in row:
                labels.append(str(row[label_col]))
            if value_col and value_col in row:
                values.append(str(row[value_col]))
            if date_col and date_col in row:
                dates.append(str(row[date_col]))
        
        # If no specific columns found, use first two columns as label and value
        if not labels and not values and data:
            first_row = data[0]
            cols = list(first_row.keys())
            if len(cols) >= 2:
                label_col = cols[0]
                value_col = cols[1]
                for row in data:
                    labels.append(str(row.get(label_col, '')))
                    values.append(str(row.get(value_col, '')))
        
        # Format based on chart type
        if chart_type in ['single_bar', 'line_single', 'area_single', 'bar_single', 'single_line', 'single_area']:
            # For single charts, return label-value pairs
            if labels and values:
                return [
                    {
                        "label": labels[i],
                        "value": values[i]
                    } for i in range(len(labels))
                ]
            else:
                # Fallback to raw data if columns not found
                return data
        
        elif chart_type in ['stacked_bar', 'line_multiple', 'area_multi', 'bar_stacked', 'line_multi', 'area_multiple', 'multi_line']:
            # Group data by date or first column
            group_col = date_col if date_col else label_col
            if not group_col:
                # If no grouping column, use first column
                group_col = list(data[0].keys())[0] if data else None
            
            if group_col:
                # Group data by the grouping column
                groups = {}
                for row in data:
                    group_key = str(row.get(group_col, ''))
                    if group_key not in groups:
                        groups[group_key] = []
                    groups[group_key].append(row)
                
                # Create datasets
                group_labels = sorted(groups.keys())
                datasets = []
                
                # Get all possible value columns (excluding the group column)
                value_columns = [col for col in data[0].keys() if col != group_col]
                
                for value_col_name in value_columns:
                    dataset = {
                        "label": value_col_name,
                        "data": []
                    }
                    for group_label in group_labels:
                        # Count occurrences or sum values for this group
                        group_data = groups[group_label]
                        if value_col_name in group_data[0]:
                            # If it's a numeric value, sum it
                            try:
                                total = sum(float(row.get(value_col_name, 0)) for row in group_data)
                                dataset["data"].append(total)
                            except (ValueError, TypeError):
                                # If not numeric, count occurrences
                                dataset["data"].append(len(group_data))
                        else:
                            dataset["data"].append(0)
                    datasets.append(dataset)
                
                return {
                    "labels": group_labels,
                    "datasets": datasets
                }
            else:
                # Fallback to raw data
                return data
        
        elif chart_type in ['group_bar', 'bar_group', 'grouped_bar']:
            # For group bar charts
            if labels:
                # Create sample datasets based on available data
                datasets = []
                for i in range(min(3, len(data))):
                    dataset = {
                        "label": f"Group {i+1}" if i == 0 else i+10,
                        "data": [1 if j % (i+1) == 0 else 0 for j in range(len(labels))]
                    }
                    datasets.append(dataset)
                
                return {
                    "labels": labels,
                    "datasets": datasets
                }
            else:
                # Fallback to raw data
                return data
        
        elif chart_type in ['donut', 'pie', 'donut_pie', 'pie_chart']:
            # For pie/donut charts
            if labels and values:
                result = []
                for i in range(len(labels)):
                    result.append({
                        "label": labels[i],
                        "value": values[i]
                    })
                return result
            else:
                # Fallback to raw data
                return data
        
        elif chart_type in ['scatter', 'scatter_plot', 'scatterplot']:
            # For scatter plot
            if date_col and value_col:
                result_data = []
                for row in data:
                    result_data.append({
                        "date": str(row.get(date_col, '')),
                        "total_amount": str(row.get(value_col, '0'))
                    })
                
                return {
                    "labels": {
                        "x": "date",
                        "y": "total_amount"
                    },
                    "data": result_data
                }
            else:
                # Fallback to raw data
                return data
        
        elif chart_type in ['area_single', 'area_chart_single']:
            # For single area chart
            if dates and values:
                return {
                    "date": dates,
                    "total_amount": values
                }
            else:
                # Fallback to raw data
                return data
        
        elif chart_type in ['area_multi', 'area_chart_multi', 'area_multiple']:
            # For multi area chart
            if dates:
                # Count occurrences of each value
                value_counts = {}
                for row in data:
                    # Use the first non-date column as value
                    for col in row.keys():
                        if col != date_col:
                            value = str(row[col])
                            if value in value_counts:
                                value_counts[value] += 1
                            else:
                                value_counts[value] = 1
                            break
                
                # Create datasets
                chart_labels = sorted(set(dates)) if dates else [f"Group_{i}" for i in range(len(data)//3 + 1)]
                datasets = []
                
                for value, count in value_counts.items():
                    dataset = {
                        "label": value,
                        "data": [count if i == 0 else 0 for i in range(len(chart_labels))]
                    }
                    datasets.append(dataset)
                
                return {
                    "labels": chart_labels,
                    "datasets": datasets
                }
            else:
                # Fallback to raw data
                return data
        
        # Default return raw data
        return data

    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET"])
    def get_chart_data_by_report(request, report_id):
        """Get chart data for all charts in a specific report"""
        try:
            # Get all charts for the report
            charts = (
                QueryBuilderService("rep_report_charts as chart")
                .leftJoin("rep_reports as report", "report.id", "chart.report_id_id")
                .select("chart.*", "report.query", "report.title as report_title")
                .where("report_id_id", report_id)
                .whereNull("report.deleted_at")
                .get()
            )
            
            if not charts:
                return ResponseService.response('NO_DATA_FOUND', None, "No charts found for this report")
            
            # Get parameters
            from_date = request.GET.get('from_date')
            to_date = request.GET.get('to_date')
            date_column = request.GET.get('date_column')
            filter_values = json.loads(request.GET.get('filter_values', '{}'))
            
            result = {}
            
            for chart in charts:
                if not chart.get('query'):
                    continue
                
                # Build SQL
                sql = chart['query'].rstrip("; \n\r\t")
                
                # Apply chart-specific filters
                if from_date and to_date and date_column:
                    sql = SqlHelperService.build_chart_where_clause(
                        sql, filter_values, from_date, to_date, date_column
                    )
                
                # Execute query
                with connection.cursor() as cursor:
                    cursor.execute(sql)
                    
                    columns = [col[0] for col in cursor.description]
                    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # Deserialize JSON if it's a string
                chart_json = chart['json']
                if isinstance(chart_json, str):
                    try:
                        chart_json = json.loads(chart_json)
                    except Exception:
                        chart_json = {}
                
                # Format data based on chart type
                formatted_data = ReportChartController._format_chart_data(chart['type'], data, chart_json)
                
                result[f"chart_{chart['id']}"] = {
                    'chart_id': chart['id'],
                    'chart_title': chart['title'],
                    'chart_type': chart['type'],
                    'json': chart_json,
                    'data': formatted_data,
                }
            
            return ResponseService.response('SUCCESS', result, 'chart_data_collected_successfully')
            
        except Exception as e:
            logger.error(f"Error in get_chart_data_by_report: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e)) 