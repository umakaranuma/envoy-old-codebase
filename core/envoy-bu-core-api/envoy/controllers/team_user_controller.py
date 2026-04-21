from rest_framework.decorators import api_view
from envoy.models.team_user import TeamUser
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
import json
from django.db import transaction
from mServices.QueryBuilderService import QueryBuilderService

@api_view(["GET", "POST"])
def team_user_view(request, team_id):
    if request.method == "GET":
        return list_team_users_by_team_id(request, team_id)
    elif request.method == "POST":
        return create_team_user(request, team_id)

def list_team_users_by_team_id(request, team_id):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = json.loads(request.GET.get("filter", "{}"))

        allowed_filters = ["tu.team_id", "tu.user_id"]
        search_columns = []  # Add user fields if you want search by user info later
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["tu.id", "tu.team_id", "tu.user_id", "tu.created_at", "tu.updated_at"]

        all_columns = ["tu.id", "tu.team_id", "tu.user_id", "tu.created_at", "tu.updated_at", "tu.deleted_at"]

        query = (
            QueryBuilderService("core_team_users as tu")
            .select(*all_columns)
            .where("tu.team_id", team_id)  # filter by team_id explicitly
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "Team users retrieved successfully!")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
    
def create_team_user(request, team_id):
    try:
        data = json.loads(request.body)
        rules = {
            "user_ids": "required|list|min:1",
            "user_ids.*": "exists:core_users,id"
        }

        custom_messages = {
            "user_ids.required": "At least one user ID must be provided.",
            "user_ids.*.exists": "One or more user IDs are invalid."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        user_ids = data["user_ids"]

        with transaction.atomic():
            created_users = []
            for uid in user_ids:
                if not TeamUser.objects.filter(team_id=team_id, user_id=uid).exists():
                    TeamUser.objects.create(team_id=team_id, user_id=uid)
                    created_users.append(uid)

        return ResponseService.response(
            "SUCCESS",
            None,
            "Users added to team successfully."
        )
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def list_users_not_in_any_team(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        search_string = request.GET.get("search", "")
        filter_json = json.loads(request.GET.get("filter", "{}"))
        allowed_filters=[]
        allowed_sorting_columns = [
            "u.id", "u.first_name", "u.last_name", "u.display_name", "u.email"
        ]
        search_columns = ["u.first_name", "u.last_name", "u.display_name", "u.email"]

        all_columns = [
            "u.id", "u.first_name", "u.last_name", "u.display_name",
            "u.email", "u.contact_no", "u.city", "u.state", "u.role_id"
        ]

        query = (
            QueryBuilderService("core_users as u")
            .select(*all_columns)
            .leftJoin("core_team_users as tu", "u.id",  "tu.user_id")
            .whereNull("tu.user_id")
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "Users not in any team retrieved successfully!")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "PUT", "DELETE"])
def team_user_detail(request, id):
    if request.method == "GET":
        return get_team_user(request, id)
    elif request.method == "DELETE":
        return delete_team_user(request, id)

def get_team_user(request, id):
    try:
        tu = TeamUser.objects.get(id=id)
        data = {
            "id": tu.id,
            "team_id": tu.team_id,
            "user_id": tu.user_id,
            "created_at": tu.created_at,
            "updated_at": tu.updated_at,
            "deleted_at": tu.deleted_at,
        }
        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")
    except TeamUser.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")

def delete_team_user(request, id):
    try:
        tu = TeamUser.objects.get(id=id)
        tu.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except TeamUser.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")