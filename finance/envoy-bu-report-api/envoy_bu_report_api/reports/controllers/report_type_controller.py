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


class ReportTypeController:
    # @staticmethod
    # @csrf_exempt
    # @require_http_methods(["GET"])
  
    @staticmethod
    @csrf_exempt
    @require_http_methods(["GET","PUT","DELETE"])
    def report_type_one(request, id):

        if request.method == "GET":
            return ReportTypeController.get_one(request, id)
        
        if request.method == "PUT":
            return ReportTypeController.store_and_update(request, id)
        
        if request.method == "DELETE":
            return ReportTypeController.delete(request, id)
        
    def get_one(request, id):
        """Get a single report type by ID"""
        try:
            report_type = (
                QueryBuilderService("rep_report_types")
                .select("*")
                .where("id", id)
                .whereNull("deleted_at")
                .first()
            )
            
            if not report_type:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            return ResponseService.response('SUCCESS', report_type, "Report type retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_one: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))


  

    @staticmethod
    @csrf_exempt
    @require_http_methods(["POST", "PUT", "GET"])
    def report_type_access(request, id=None):

        if request.method == "GET":
            return ReportTypeController.get_all(request)
        
        if request.method == "POST":
            return ReportTypeController.store_and_update(request,id = None)
        
        if request.method == "PUT":
            return ReportTypeController.store_and_update(request,id)
    
    @staticmethod
    def store_and_update(request,id=None):
        """Create or update a report type"""
        try:
            data = json.loads(request.body)
            
            # Validation
            rules = {
                "name": "required|string",
                "module": "required|string",
            }
            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
            
            if id:
                # Update existing report type
                report_type = QueryBuilderService("rep_report_types").where("id", id).first()
                if not report_type:
                    return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
                
                QueryBuilderService("rep_report_types").where("id", id).update(data)
                # Get updated data
                updated_report_type = QueryBuilderService("rep_report_types").where("id", id).first()
                message = "default_update_success_msg"
                return ResponseService.response('SUCCESS', updated_report_type, message)
            else:

                entity_data = EntityService.store_entity("report_type", request)
                if entity_data is None:
                    return ResponseService.response('UNAUTHORIZED', None, "User not authenticated")
                
                data["entity_id"] = entity_data["id"]
                data["created_by_id"] = request.user.id
                print(data["entity_id"])
                # Create new report type
                report_type = QueryBuilderService("rep_report_types").insert(data)
                message = "default_create_success_msg"
                return ResponseService.response('SUCCESS', report_type, message)
            
        except Exception as e:
            logger.error(f"Error in store_or_update: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))
        
    @staticmethod
    def get_all(request):
        """Get all report types with filtering and pagination"""
        try:
            # Get query parameters
            filters = json.loads(request.GET.get('filters', '{}'))
            search = request.GET.get('search', '')
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            sort_by = request.GET.get('sort_by', 'type.id')
            sort_dir = request.GET.get('sort_dir', 'desc')
            
            # Set default sort order to descending
            sort_by = "type.id" if sort_by in [None, ""] else sort_by
            sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
            
            allowed_filters = ["type.id", "type.name", "type.module"]
            search_columns = ["type.name"]
            sort_columns = ["type.created_at", "type.id", "type.name"]
            
            # Build query using QueryBuilderService
            query = (
                QueryBuilderService("rep_report_types as type")
                .select("*")
                .whereNull("deleted_at")
            )
            
            # Apply filters
            if filters.get('name'):
                query = query.where("type.name", filters['name'], "LIKE")
            if filters.get('module'):
                query = query.where("type.module", filters['module'], "LIKE")
            
            # Apply search
            if search:
                query = query.where("type.name", search, "LIKE")
            
            # Apply sorting and pagination
            data = query.paginate(page, limit, ['type.id', 'type.name'], sort_by, sort_dir)
            
            return ResponseService.response('SUCCESS', data, "Report types retrieved successfully")
            
        except Exception as e:
            logger.error(f"Error in get_all: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e))


    @staticmethod
    @csrf_exempt
    @require_http_methods(["DELETE"])
    def delete(request, id):
        """Soft delete a report type"""
        try:
            report_type = QueryBuilderService("rep_report_types").where("id", id).whereNull("deleted_at").first()
            
            if not report_type:
                return ResponseService.response('NO_DATA_FOUND', None, "data_not_found")
            
            # Soft delete
            QueryBuilderService("rep_report_types").where("id", id).update({
                "deleted_at": timezone.now()
            })
            
            return ResponseService.response('SUCCESS', None, "default_delete_success_msg")
            
        except Exception as e:
            logger.error(f"Error in delete: {str(e)}")
            return ResponseService.response('INTERNAL_SERVER_ERROR', str(e)) 