from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging

from mServices import QueryBuilderService
from mServices.ValidatorService import ValidatorService

from services.EntityService import EntityService
from ..services.response_service import ResponseService

logger = logging.getLogger(__name__)


class ReportDashboardController:
    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET", "PUT", "DELETE"])
    def report_dashboard_one(request, id):
        """Handle GET, PUT, DELETE requests for a single dashboard"""
        if request.method == "GET":
            return ReportDashboardController.get_one(request, id)
        
        if request.method == "PUT":
            return ReportDashboardController.store_or_update(request, id)
        
        if request.method == "DELETE":
            return ReportDashboardController.delete(request, id)

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST", "PUT", "GET"])
    def report_dashboard_access(request, id=None):
        """Handle GET, POST, PUT requests for dashboards"""
        if request.method == "GET":
            return ReportDashboardController.get_all(request)
        
        if request.method == "POST":
            return ReportDashboardController.store_or_update(request, id=None)
        
        if request.method == "PUT":
            return ReportDashboardController.store_or_update(request, id)

    @staticmethod
    def get_all(request):
        """Get all dashboards with filtering and pagination"""
        try:
            # Get query parameters
            filters = json.loads(request.GET.get('filters', '{}'))
            search = request.GET.get('search', '')
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            sort_by = request.GET.get('sort_by', 'dashboard.id')
            sort_dir = request.GET.get('sort_dir', 'asc')
            
            # Build query using QueryBuilderService
            query = (
                QueryBuilderService("rep_report_dashboards as dashboard")
                .select("*")
                .whereNull("dashboard.deleted_at")
            )
            
            # Apply filters
            if filters.get('title'):
                query = query.where("dashboard.title", filters['title'], "LIKE")
            if filters.get('module'):
                query = query.where("dashboard.module", filters['module'], "LIKE")
            
            # Apply search
            if search:
                query = query.where("dashboard.title", search, "LIKE")
            
            # Apply sorting and pagination
            data = query.paginate(page, limit, ['dashboard.id', 'dashboard.title'], sort_by, sort_dir)
            
            return ResponseService.response('SUCCESS', data, "Dashboards retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_all: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def get_one(request, id):
        """Get a single dashboard by ID"""
        try:
            dashboard = (
                QueryBuilderService("rep_report_dashboards")
                .select("*")
                .where("id", id)
                .whereNull("deleted_at")
                .first()
            )
            
            if not dashboard:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            return ResponseService.response('SUCCESS', dashboard, "Dashboard retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_one: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def store_or_update(request, id=None):
        """Create or update a dashboard"""
        try:
            data = json.loads(request.body)
            
            if id:
                rules = {
                    "title": f"required|string|unique:rep_report_dashboards,title,{id}",
                    "module": "required|string",
                    "description": "optional|string"
                }
            else:
            # Validation
             rules = {
                "title": "required|string|unique:rep_report_dashboards,title",
                "module": "required|string",
                "description": "optional|string"
               
            }
            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
            
            if id:
                # Update existing dashboard
                dashboard = QueryBuilderService("rep_report_dashboards").where("id", id).first()
                if not dashboard:
                    return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
                
                QueryBuilderService("rep_report_dashboards").where("id", id).update(data)
                message = "default_update_success_msg"
            else:
                entity = EntityService.store_entity("rep_report_dashboards", request)
                data['entity_id'] = entity['id']
                data['created_by_id'] = request.user.id
                # Create new dashboard
                dashboard = QueryBuilderService("rep_report_dashboards").insert(data)
                message = "default_create_success_msg"
            
            return ResponseService.response('SUCCESS', None, message)
            
        except Exception as e:
            logger.error(f"Error in store_or_update: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))

    @staticmethod
    def delete(request, id):
        """Soft delete a dashboard"""
        try:
            dashboard = QueryBuilderService("rep_report_dashboards").where("id", id).whereNull("deleted_at").first()
            
            if not dashboard:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            # Soft delete
            QueryBuilderService("rep_report_dashboards").where("id", id).update({
                "deleted_at": timezone.now(),
                "deleted_by_id": request.user.id
            })
            
            return ResponseService.response('SUCCESS', None, "default_delete_success_msg")
            
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e)) 