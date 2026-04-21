from rest_framework.decorators import api_view
from envoy.models import CoreOrganizationLevel  
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json


@api_view(["GET", "POST"])
def organization_level_view(request):
    if request.method == "GET":
        return list_organization_level(request)
    elif request.method == "POST":
        return create_organization_level(request)


def list_organization_level(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["level_order", "created_by_id", "updated_by_id", "created_at"]
        search_columns = ["title", "description"]
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        # Include node_count in sortable columns
        allowed_sorting_columns = [
            "id", "title", "description", "level_order",
            "created_by_id", "updated_by_id", "created_at", "updated_at"
        ]

        # All columns including alias for node_count
        all_columns = [
            "lvl.id as id",
            "lvl.title as title",
            "lvl.description as description",
            "lvl.level_order as level_order",
            "lvl.created_by_id as created_by_id",
            "lvl.updated_by_id as updated_by_id",
            "lvl.created_at as created_at",
            "lvl.updated_at as updated_at",
            "(SELECT COUNT(*) FROM core_organizational_nodes WHERE level_id = lvl.id) as node_count"
        ]

        query = (
            QueryBuilderService("core_organization_levels as lvl")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def create_organization_level(request):
    try:
        data = json.loads(request.body)

        rules = {
            "title": "required|unique:core_organization_levels,title|max:200",
            "description": "nullable|max:250",
            "level_order": "required|numeric|min:1"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.unique": "Title must be unique.",
            "title.max": "Title cannot exceed 200 characters.",
            "description.max": "Type cannot exceed 250 characters.",
            "level_order.numeric": "Standard fee must be a number.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        CoreOrganizationLevel.objects.create(
            title=data["title"],
            description=data.get("description", ""),
            level_order=data["level_order"],
            created_by_id=request.user.id if request.user.is_authenticated else None,   
        )

        return ResponseService.response("SUCCESS", None, "default_create_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "PUT", "DELETE"])
def organization_level_detail(request, id):
    if request.method == "GET":
        return get_organization_level(request, id)
    elif request.method == "PUT":
        return update_organization_level(request, id)
    elif request.method == "DELETE":
        return delete_organization_level(request, id)


def get_organization_level(request, id):
    try:
        organizationLevel = CoreOrganizationLevel.objects.get(id=id)
         # Get all nodes for this level
        nodes = organizationLevel.organization_nodes.all()
        node_names = [node.name for node in nodes]
        node_count = nodes.count()

        data = {
            "id": organizationLevel.id,
            "title": organizationLevel.title,
            "description": organizationLevel.description,
            "level_order":organizationLevel.level_order,
            "created_by_id": organizationLevel.created_by.id if organizationLevel.created_by else None,
            "created_by_display_name": organizationLevel.created_by.display_name if organizationLevel.created_by else None,
            "updated_by_id": organizationLevel.updated_by.id if organizationLevel.updated_by else None,
            "updated_by_display_name": organizationLevel.updated_by.display_name if organizationLevel.updated_by else None,
            "created_at":organizationLevel.created_at,
            "updated_at":organizationLevel.updated_at,
            "node_count": node_count,
            "node_names": node_names,
        }
        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")
    except CoreOrganizationLevel.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")


def update_organization_level(request, id):
    try:
        organizationLevel = CoreOrganizationLevel.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "title": f"required|unique:core_organization_levels,title,{id}|max:200",
            "description": "nullable|max:250",
            "level_order": "required|numeric|min:1"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.unique": "Title must be unique.",
            "title.max": "Title cannot exceed 200 characters.",
            "description.max": "Type cannot exceed 250 characters.",
            "level_order.numeric": "Standard fee must be a number.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        organizationLevel.title = data["title"]
        organizationLevel.description = data.get("description", "")
        organizationLevel.level_order = data["level_order"]
        organizationLevel.updated_by_id = request.user.id if request.user.is_authenticated else None
        organizationLevel.save()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
    except CoreOrganizationLevel.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_organization_level(request, id):
    try:
        organizationLevel = CoreOrganizationLevel.objects.get(id=id)
        organizationLevel.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except CoreOrganizationLevel.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
