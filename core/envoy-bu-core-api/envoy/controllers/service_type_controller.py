from rest_framework.decorators import api_view
from envoy.models import CoreServiceType  
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json


@api_view(["GET", "POST"])
def service_type_view(request):
    if request.method == "GET":
        return list_service_type(request)
    elif request.method == "POST":
        return create_service_type(request)


def list_service_type(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["standardfee","created_by_id", "updated_by_id","created_at"]
        search_columns = ["title", "description"]
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        allowed_sorting_columns = ["id", "title", "description","standardfee","created_by_id","updated_by_id","created_at","updated_at"]

        all_columns = ["id", "title", "description","standardfee","created_by_id","updated_by_id","created_at","updated_at"]

        query = (
            QueryBuilderService("core_service_types")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def create_service_type(request):
    try:
        data = json.loads(request.body)

        rules = {
            "title": "required|unique:core_service_types,title|max:200",
            "description": "nullable|max:250",
            "standardfee": "required|numeric|min:0"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "standardfee.required": "Standard fee is required.",
            "title.unique": "Title must be unique.",
            "title.max": "Title cannot exceed 200 characters.",
            "description.max": "Type cannot exceed 250 characters.",
            "standardfee.numeric": "Standard fee must be a number.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        CoreServiceType.objects.create(
            title=data["title"],
            description=data.get("description", ""),
            standardfee=data.get("standardfee", 0.00),
            created_by_id=request.user.id if request.user.is_authenticated else None,   
        )

        return ResponseService.response("SUCCESS", None, "default_create_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "PUT", "DELETE"])
def service_type_detail(request, id):
    if request.method == "GET":
        return get_service_type(request, id)
    elif request.method == "PUT":
        return update_service_type(request, id)
    elif request.method == "DELETE":
        return delete_service_type(request, id)


def get_service_type(request, id):
    try:
        serviceType = CoreServiceType.objects.get(id=id)
        data = {
            "id": serviceType.id,
            "title": serviceType.title,
            "description": serviceType.description,
            "standardfee":serviceType.standardfee,
            "created_by_id": serviceType.created_by.id if serviceType.created_by else None,
            "created_by_display_name": serviceType.created_by.display_name if serviceType.created_by else None,
            "updated_by_id": serviceType.updated_by.id if serviceType.updated_by else None,
            "updated_by_display_name": serviceType.updated_by.display_name if serviceType.updated_by else None,
            "created_at":serviceType.created_at,
            "updated_at":serviceType.updated_at
        }
        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")
    except CoreServiceType.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")


def update_service_type(request, id):
    try:
        serviceType = CoreServiceType.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "title": f"required|unique:core_service_types,title,{id}|max:200",
            "description": "nullable|max:250",
            "standardfee": "required|numeric|min:0"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.unique": "Title must be unique.",
            "title.max": "Title cannot exceed 200 characters.",
            "description.max": "Type cannot exceed 250 characters.",
            "standardfee.numeric": "Standard fee must be a number.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        serviceType.title = data["title"]
        serviceType.description = data.get("description", "")
        serviceType.standardfee=data.get("standardfee",0.00)
        serviceType.updated_by_id = request.user.id if request.user.is_authenticated else None
        serviceType.save()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
    except CoreServiceType.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_service_type(request, id):
    try:
        serviceType = CoreServiceType.objects.get(id=id)
        serviceType.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except CoreServiceType.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
