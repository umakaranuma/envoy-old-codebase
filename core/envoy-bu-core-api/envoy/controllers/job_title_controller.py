from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from envoy.models import CoreJobTitle  
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json


@api_view(["GET", "POST"])
def job_title_view(request):
    if request.method == "GET":
        return list_job_title(request)
    elif request.method == "POST":
        return create_job_title(request)


def list_job_title(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["created_by_id", "updated_by_id","created_at"]
        search_columns = ["title", "description"]
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["id", "title", "description","created_by_id","updated_by_id","created_at","updated_at"]

        all_columns = ["id", "title", "description","created_by_id","updated_by_id","created_at","updated_at"]

        query = (
            QueryBuilderService("core_job_titles")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def create_job_title(request):
    try:
        data = json.loads(request.body)

        rules = {
            "title": "required|unique:core_job_titles,title|max:200",
            "description": "nullable|max:250"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.unique": "Title must be unique.",
            "title.max": "Title cannot exceed 200 characters.",
            "description.max": "Type cannot exceed 250 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        CoreJobTitle.objects.create(
            title=data["title"],
            description=data.get("description", ""),
            created_by_id=request.user.id if request.user.is_authenticated else None,   
        )

        return ResponseService.response("SUCCESS", None, "default_create_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "PUT", "DELETE"])
def job_title_detail(request, id):
    if request.method == "GET":
        return get_job_title(request, id)
    elif request.method == "PUT":
        return update_job_title(request, id)
    elif request.method == "DELETE":
        return delete_job_title(request, id)


def get_job_title(request, id):
    try:
        jobTitle = CoreJobTitle.objects.get(id=id)
        data = {
            "id": jobTitle.id,
            "title": jobTitle.title,
            "description": jobTitle.description,
        }
        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")
    except CoreJobTitle.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")


def update_job_title(request, id):
    try:
        jobTitle = CoreJobTitle.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "title": "required|unique:core_job_titles,title|max:200",
            "description": "nullable|max:250"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.max": "Title cannot exceed 200 characters.",
            "description.max": "Title cannot exceed 250 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        jobTitle.title = data["title"]
        jobTitle.description = data.get("description", "")
        jobTitle.updated_by_id = request.user.id if request.user.is_authenticated else None
        jobTitle.save()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
    except CoreJobTitle.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_job_title(request, id):
    try:
        jobTitle = CoreJobTitle.objects.get(id=id)
        jobTitle.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except CoreJobTitle.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
