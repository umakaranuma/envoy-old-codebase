from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import connection
from django.utils import timezone
import json
import logging

from mServices import QueryBuilderService
from mServices.ValidatorService import ValidatorService

from services.EntityService import EntityService
from ..services.response_service import ResponseService
from ..services.sql_generator_service import SQLGeneratorService
from ..services.sql_helper_service import SqlHelperService
from ..services.data_expoter import SQLToExcelExporter

logger = logging.getLogger(__name__)


class ReportController:

    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET", "PUT", "DELETE"])
    def report_one(request, report_id):
        """Handle GET, PUT, DELETE requests for a single report"""
        if request.method == "GET":
            return ReportController.get_one(request, report_id)
        
        if request.method == "PUT":
            return ReportController.store_or_update(request, report_id)
        
        if request.method == "DELETE":
            return ReportController.delete(request, report_id)

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST", "PUT", "GET"])
    def report_access(request, report_id=None):
        """Handle GET, POST, PUT requests for reports"""
        if request.method == "GET":
            return ReportController.get_all(request)
        
        if request.method == "POST":
            return ReportController.store_or_update(request, report_id=None)
        
        if request.method == "PUT":
            return ReportController.store_or_update(request, report_id)

    @staticmethod
    def get_all(request):
        """Get all reports with filtering, searching, and pagination"""
        try:
            # Get query parameters
            filters = json.loads(request.GET.get('filters', '{}'))
            search = request.GET.get('search', '')
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            sort_by = request.GET.get('sort_by', 'report.id')
            sort_dir = request.GET.get('sort_dir', 'desc')
            
            # Set default sort order to descending
            sort_by = "report.id" if sort_by in [None, ""] else sort_by
            sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
            
            allowed_filters = ["report.id", "report.title", "report.type_id_id"]
            search_columns = ["report.title"]
            sort_columns = ["report.created_at", "report.id", "report.title"]
            
            # Build query using QueryBuilderService
            query = (
                QueryBuilderService("rep_reports as report")
                .leftJoin("rep_report_types as type", "type.id", "report.type_id_id")
                .select(
                    "report.*",
                    "type.name as type_name",
                    "type.module as module"
                )
                .whereNull("report.deleted_at")
            )
            
            # Apply filters
            if filters.get('title'):
                query = query.where("report.title", filters['title'], "LIKE")
            if filters.get('type_id'):
                query = query.where("report.type_id_id", filters['type_id'])
            
            # Apply search
            if search:
                query = query.where("report.title", search, "LIKE")
            
            # Apply sorting and pagination
            data = query.paginate(page, limit, ['report.id', 'report.title'], sort_by, sort_dir)
            
            return ResponseService.response('SUCCESS', data, "Reports retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_all: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def get_one(request, report_id):
        """Get a single report by ID"""
        try:
            report = (
                QueryBuilderService("rep_reports as report")
                .leftJoin("rep_report_types as type", "type.id", "report.type_id_id")
                .select(
                    "report.*",
                    "type.name as type_name",
                    "type.module as module"
                )
                .where("report.id", report_id)
                .whereNull("report.deleted_at")
                .first()
            )
            
            if not report:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            return ResponseService.response('SUCCESS', report, "Report retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_one: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def store_or_update(request, report_id=None):
        """Create or update a report"""
        try:
            data = json.loads(request.body)
            # Accept `sql` as alias for `query` (keep both keys if provided)
            if isinstance(data, dict) and 'query' not in data and 'sql' in data:
                data['query'] = data.get('sql')
            if report_id:
                rules = {
                "title": f"required|string|unique:rep_reports,title,{report_id}",
                "type_id": "required|integer",
                "json": "required|dict",
                "sql": "required|string",
                "description": "optional|string"
            }
            else:
                
            # Validation
                rules = {
                "title": "required|string|unique:rep_reports,title",
                "type_id": "required|integer",
                "json": "required|dict",
                "sql": "required|string",
                "description": "optional|string"
            }
            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
            
            # Manual unique check for title (excluding current report when updating)
            existing_report = (
                QueryBuilderService("rep_reports")
                .where("title", data['title'])
                .whereNull("deleted_at")
            )
            
            if report_id:
                # When updating, exclude current report from unique check
                existing_report = existing_report.where("id", report_id)
            
            existing_report = existing_report.first()
            
            # if existing_report and (not report_id or existing_report['id'] != report_id):
            #     return ResponseService.response("VALIDATION_ERROR", {"title": ["Title must be unique"]}, "Title already exists")
            
            # Sanitize JSON
            data['json'] = SqlHelperService.sanitize_json_data(data['json'])
            # Ensure JSON is serialized for DB layer that doesn't accept dict parameters
            if isinstance(data['json'], (dict, list)):
                data['json'] = json.dumps(data['json'])
            
            if report_id:
                # Update existing report
                report = QueryBuilderService("rep_reports").where("id", report_id).first()
                if not report:
                    return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
                
                # Map type_id if provided during update
                if 'type_id' in data:
                    data['type_id_id'] = data['type_id']
                QueryBuilderService("rep_reports").where("id", report_id).update(data)
                message = "default_update_success_msg"
            else:
                entity_id = EntityService.store_entity("report_creation", request)
                data['entity_id'] = entity_id['id']
                data['created_by_id'] = request.user.id
                data['type_id_id'] = data['type_id']
                # Create new report
                report = QueryBuilderService("rep_reports").insert(data)
                message = "default_create_success_msg"
            
            return ResponseService.response('SUCCESS', None, message)
            
        except Exception as e:
            logger.error(f"Error in store_or_update: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def delete(request, report_id):
        """Soft delete a report"""
        try:
            report = QueryBuilderService("rep_reports").where("id", report_id).whereNull("deleted_at").first()
            
            if not report:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            # Soft delete
            QueryBuilderService("rep_reports").where("id", report_id).update({
                "deleted_at": timezone.now()
            })
            
            return ResponseService.response('SUCCESS', None, "default_delete_success_msg")
            
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET"])
    def get_query_data(request, report_id):
        """Get query data for a report with filtering and pagination"""
        try:
            report = QueryBuilderService("rep_reports").where("id", report_id).first()
            print(report, "report..........")
            
            if not report:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            # Debug: Check report structure
            logger.info(f"Report {report_id} data: {report}")
            logger.info(f"Report query: {report.get('query', 'NO_QUERY')}")
            
            # Check if report has any charts
            charts = QueryBuilderService("rep_report_charts").where("report_id_id", report_id).get()
            print(charts, "charts..........")
            has_charts = len(charts) > 0
            
            # Get parameters
            load_fields = request.GET.get('load_fields', 'false').lower() == 'true'
            search = request.GET.get('search', '').strip()
            filters = request.GET.get('filters', '{}')
            sort_by = request.GET.get('sort_by')
            sort_dir = request.GET.get('sort_dir', 'desc')
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            
            # Set default sort order to descending
            sort_by = "cus_payments.id" if sort_by in [None, ""] else sort_by
            sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
                
            # Parse filters
            if isinstance(filters, str):
                filters = json.loads(filters)
            
            # Parse JSON config first (needed for both query and no-query cases)
            json_config = report.get('json') or {}
            if isinstance(json_config, str):
                try:
                    json_config = json.loads(json_config)
                except Exception:
                    json_config = {}
            
            # Clean up corrupted field data
            fields = json_config.get('fields', [])
            if fields:
                cleaned_fields = []
                for field in fields:
                    if isinstance(field, dict) and 'label' in field:
                        # Clean up corrupted labels that contain SQL fragments
                        label = field['label']
                        if ' AS ' in label and '"' in label:
                            # Extract the actual label from SQL fragments like "column AS \"Label\""
                            try:
                                # Find the part after "AS" and extract the quoted label
                                as_part = label.split(' AS ')[-1]
                                if as_part.startswith('"') and as_part.endswith('"'):
                                    clean_label = as_part[1:-1]  # Remove quotes
                                elif as_part.startswith('\\"') and as_part.endswith('\\"'):
                                    clean_label = as_part[2:-2]  # Remove escaped quotes
                                else:
                                    clean_label = label
                            except:
                                clean_label = label
                        elif ' AS ' in label:
                            # Handle cases without quotes but with AS
                            try:
                                as_part = label.split(' AS ')[-1]
                                clean_label = as_part
                            except:
                                clean_label = label
                        elif '\\"' in label:
                            # Handle escaped quotes in labels
                            try:
                                # Extract text between escaped quotes
                                start = label.find('\\"') + 2
                                end = label.rfind('\\"')
                                if start > 1 and end > start:
                                    clean_label = label[start:end]
                                else:
                                    clean_label = label
                            except:
                                clean_label = label
                        else:
                            clean_label = label
                        
                        # Additional cleaning for very corrupted cases
                        if clean_label and len(clean_label) > 100:  # Very long labels are likely corrupted
                            # Try to extract meaningful parts
                            if '\\"' in clean_label:
                                # Look for text between escaped quotes
                                parts = clean_label.split('\\"')
                                if len(parts) >= 3:
                                    clean_label = parts[1]  # Take the first quoted part
                                else:
                                    clean_label = clean_label[:50] + "..."  # Truncate very long labels
                        
                        cleaned_field = field.copy()
                        cleaned_field['label'] = clean_label
                        cleaned_fields.append(cleaned_field)
                    else:
                        cleaned_fields.append(field)
                fields = cleaned_fields
                
                # Update the json_config with cleaned fields for response
                json_config['fields'] = cleaned_fields
            
            skip_columns = json_config.get('skip_columns', [])
            
            if load_fields:
                # Return field names only
                skip_codes = [col['code'] for col in skip_columns]
                columns = [field['label'] for field in fields if field['code'] not in skip_codes]
                return ResponseService.response('SUCCESS', {"data": columns}, "fields_loaded_successfully")
            
            # Check if report has a query
            if not report.get('query'):
                logger.warning(f"Report {report_id} has no query")
                return ResponseService.response('SUCCESS', {
                    'data': {
                        'report_id': report_id,
                        'report_title': report['title'],
                        'json': json_config,  # Use the actual json config from report
                        'data': [],
                        'fields': fields  # Keep original format
                    },
                    'total': 0
                }, 'report_data_collected_successfully')
            
            # Build SQL
            sql = report['query'].rstrip("; \n\r\t")
            logger.info(f"Executing SQL for report {report_id}: {sql[:200]}...")
            
            # Remove skipped columns
            if skip_columns:
                sql = SqlHelperService.remove_skipped_columns_from_sql(sql, skip_columns)
            
            # Apply filters and search
            if search:
                # Add search condition
                searchable_fields = [f"{field['code']}" for field in fields if field.get('dataType') == 'text']
                if searchable_fields:
                    search_conditions = [f"{field} LIKE '%{search}%'" for field in searchable_fields]
                    search_condition = ' OR '.join(search_conditions)
                    sql = SqlHelperService.add_where_condition(sql, search_condition)
            
            # Apply sorting
            allowed_sorting_columns = [field['label'] for field in fields if field['code'] not in [col['code'] for col in skip_columns]]
            if sort_by and sort_by in allowed_sorting_columns:
                sql = SqlHelperService.apply_sort(sql, sort_by, sort_dir, allowed_sorting_columns)
            
            # Debug: Log final SQL
            logger.info(f"Final SQL for report {report_id}: {sql}")
            
            # Execute query
            try:
                with connection.cursor() as cursor:
                    # Get total count
                    count_sql = f"SELECT COUNT(*) as total FROM ({sql}) AS sub"
                    logger.info(f"Executing count SQL: {count_sql[:200]}...")
                    cursor.execute(count_sql)
                    total = cursor.fetchone()[0]
                    logger.info(f"Total records found: {total}")
                    
                    # If no data found, return empty structure
                    if total == 0:
                        return ResponseService.response('SUCCESS', {
                            'data': {
                                'report_id': report_id,
                                'report_title': report['title'],
                                'json': json_config,  # Use the actual json config from report
                                'data': [],
                                'fields': fields  # Keep original format
                            },
                            'total': 0
                        }, 'report_data_collected_successfully')
                    
                    # Get paginated data
                    offset = (page - 1) * limit
                    paginated_sql = f"{sql} LIMIT {limit} OFFSET {offset}"
                    logger.info(f"Executing paginated SQL: {paginated_sql[:200]}...")
                    cursor.execute(paginated_sql)
                    
                    columns = [col[0] for col in cursor.description]
                    data = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    logger.info(f"Retrieved {len(data)} records")
            except Exception as query_error:
                logger.error(f"Error executing query for report {report_id}: {str(query_error)}")
                return ResponseService.response('INTERNAL_SERVER_ERROR', f"Query execution failed: {str(query_error)}")
            
            return ResponseService.response('SUCCESS', {
                'data': {
                    'report_id': report_id,
                    'report_title': report['title'],
                    'json': json_config,  # Use the actual json config from report
                    'data': data,
                    'fields': fields  # Keep original format
                },
                'total': total
            }, 'report_data_collected_successfully')
            
        except Exception as e:
            logger.error(f"Error in get_query_data: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def query_generate(request):
        """Generate SQL query from JSON configuration"""
        try:
            data = json.loads(request.body)
            
            # Validation
            rules = {
                "report_id": "required|integer",
                "query_data": "required|dict"
            }
            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
            
            report_id = data['report_id']
            query_data = data['query_data']
            
            # Generate SQL
            sql = SQLGeneratorService.generate_from_input(json.dumps(query_data))
            
            # Update report
            report = QueryBuilderService("rep_reports").where("id", report_id).first()
            print(report, "report")
            if not report:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            QueryBuilderService("rep_reports").where("id", report_id).update({
                "query": sql,
                    "json": json.dumps(query_data)
            })
            
            return ResponseService.response('SUCCESS', {"report_id": report_id}, "query_generated_successfully")
            
        except Exception as e:
            logger.error(f"Error in query_generate: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST"])
    def export_report_to_excel(request):
        """Export report data to Excel directly from SQL query"""
        try:
            data = json.loads(request.body)
            
            # Validation
            rules = {
                "report_id": "required|integer",
                "search": "optional|string",
                "filters": "optional|dict",
                "sort_by": "optional|string",
                "sort_dir": "optional|string",
                "styles": "optional|dict"
            }
            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
            
            report_id = data['report_id']
            search = data.get('search', '').strip()
            filters = data.get('filters', {})
            sort_by = data.get('sort_by')
            sort_dir = data.get('sort_dir', 'desc')
            styles = data.get('styles', {})
            
            # Get report
            report = QueryBuilderService("rep_reports").where("id", report_id).first()
            if not report:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            # Parse JSON config
            json_config = report.get('json') or {}
            if isinstance(json_config, str):
                try:
                    json_config = json.loads(json_config)
                except Exception:
                    json_config = {}
            
            # Clean up corrupted field data (same logic as get_query_data)
            fields = json_config.get('fields', [])
            if fields:
                cleaned_fields = []
                for field in fields:
                    if isinstance(field, dict) and 'label' in field:
                        label = field['label']
                        if ' AS ' in label and '"' in label:
                            try:
                                as_part = label.split(' AS ')[-1]
                                if as_part.startswith('"') and as_part.endswith('"'):
                                    clean_label = as_part[1:-1]
                                elif as_part.startswith('\\"') and as_part.endswith('\\"'):
                                    clean_label = as_part[2:-2]
                                else:
                                    clean_label = label
                            except:
                                clean_label = label
                        elif ' AS ' in label:
                            try:
                                as_part = label.split(' AS ')[-1]
                                clean_label = as_part
                            except:
                                clean_label = label
                        elif '\\"' in label:
                            try:
                                start = label.find('\\"') + 2
                                end = label.rfind('\\"')
                                if start > 1 and end > start:
                                    clean_label = label[start:end]
                                else:
                                    clean_label = label
                            except:
                                clean_label = label
                        else:
                            clean_label = label
                        
                        if clean_label and len(clean_label) > 100:
                            if '\\"' in clean_label:
                                parts = clean_label.split('\\"')
                                if len(parts) >= 3:
                                    clean_label = parts[1]
                                else:
                                    clean_label = clean_label[:50] + "..."
                        
                        cleaned_field = field.copy()
                        cleaned_field['label'] = clean_label
                        cleaned_fields.append(cleaned_field)
                    else:
                        cleaned_fields.append(field)
                fields = cleaned_fields
            
            skip_columns = json_config.get('skip_columns', [])
            
            # Check if report has a query
            if not report.get('query'):
                logger.warning(f"Report {report_id} has no query")
                return ResponseService.response('NO_DATA_FOUND', None, "Report has no SQL query")
            
            # Build SQL (same logic as get_query_data but without pagination)
            sql = report['query'].rstrip("; \n\r\t")
            logger.info(f"Building SQL for report {report_id} export: {sql[:200]}...")
            
            # Remove skipped columns
            if skip_columns:
                sql = SqlHelperService.remove_skipped_columns_from_sql(sql, skip_columns)
            
            # Apply search if provided
            if search:
                searchable_fields = [f"{field['code']}" for field in fields if field.get('dataType') == 'text']
                if searchable_fields:
                    search_conditions = [f"{field} LIKE '%{search}%'" for field in searchable_fields]
                    search_condition = ' OR '.join(search_conditions)
                    sql = SqlHelperService.add_where_condition(sql, search_condition)
            
            # Apply sorting if provided
            allowed_sorting_columns = [field['label'] for field in fields if field['code'] not in [col['code'] for col in skip_columns]]
            if sort_by and sort_by in allowed_sorting_columns:
                sql = SqlHelperService.apply_sort(sql, sort_by, sort_dir, allowed_sorting_columns)
            
            # Prepare sheet title (Excel sheet names are limited to 31 characters)
            sheet_title = (report['title'] or f"Report_{report_id}")[:31]
            
            # Prepare queries array for SQLToExcelExporter
            queries = [{
                "query": sql,
                "title": sheet_title
            }]
            
            # Prepare payload
            payload = {
                "queries": queries
            }
            
            # Add styles if provided
            if styles:
                payload["styles"] = styles
            
            logger.info(f"Exporting report {report_id} to Excel with SQL: {sql[:200]}...")
            
            # Export to Excel
            exporter = SQLToExcelExporter()
            export_response = exporter.export(payload)
            
            if export_response["status"] == "SUCCESS":
                return ResponseService.response("SUCCESS", export_response["data"], export_response.get("message", "Excel generated successfully"))
            else:
                return ResponseService.response("INTERNAL_SERVER_ERROR", None, export_response.get("message", "Excel export failed"))
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in request body: {str(e)}")
            return ResponseService.response("VALIDATION_ERROR", {"body": ["Invalid JSON format"]}, "Invalid JSON in request body")
        except Exception as e:
            logger.error(f"Error in export_report_to_excel: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))
