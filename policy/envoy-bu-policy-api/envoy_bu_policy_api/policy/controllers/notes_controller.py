# views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_policy_api.service import handle_entity, _format_date_fields


@csrf_exempt
@api_view(["GET"])
def policy_note_list(request, policy_id):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("Notes", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_notes(request, policy_id=policy_id, note_id=None)

    return create_note(request)


@csrf_exempt
@api_view(["POST"])
def policy_note_create(request):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("Notes", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return create_note(request)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def policy_note_detail(request, note_id):
    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("Notes", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_notes(request, note_id=note_id)
    elif request.method == "PUT":
        return update_note(request, note_id)
    elif request.method == "DELETE":
        return delete_note(note_id)


def get_notes_validation_rules():
    return {
        "title": "string|max:255",
        "content": "required|string",
        "health": "string|max:255",
        "remarks": "string",
        "issued_policy_id": "required|integer|exists:crmp_issued_policies,id",
    }


def get_all_notesx(request, policy_id=None, note_id=None):
    columns = [
        "crmp_notes.*",
        "core_entities.created_at as created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_by_logo",
    ]

    query = (
        QueryBuilderService("crmp_notes")
        .select(*columns)
        .leftJoin("core_entities", "core_entities.id", "crmp_notes.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
    )

    if policy_id:
        result = query.where("crmp_notes.issued_policy_id", policy_id)

    if note_id:
        data = result.where("id", note_id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    # Pagination, Search, Sorting, Filtering
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    search = request.GET.get("search", "")
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    filter_json = json.loads(request.GET.get("filter", "{}"))

    allowed_filters = ["title", "content", "health", "remarks"]
    search_columns = ["title", "content", "remarks"]
    sort_columns = ["id", "created_at"]

    query = result.apply_conditions(
        filter_json, allowed_filters, search, search_columns
    )
    data = result.paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def create_note(request):
    data = json.loads(request.body or "{}")
    errors = ValidatorService.validate(data, get_notes_validation_rules())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    user = request.user if request.user.is_authenticated else None
    entity_data = {
        "type": "notes",
        "approvel_status": False,
    }
    entity_id = handle_entity(entity_data, entity_id=data.get("entity_id"), user=user)
    data["entity_id"] = entity_id
    created = QueryBuilderService("crmp_notes").insert(data)
    return ResponseService.response("SUCCESS", created, "default_create_success_msg")


def update_note(request, note_id):
    data = json.loads(request.body or "{}")
    errors = ValidatorService.validate(data, get_notes_validation_rules())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    updated = QueryBuilderService("crmp_notes").where("id", note_id).update(data)
    if updated:
        notes_data = QueryBuilderService("crmp_notes").where("id", note_id).first()
        if notes_data.get("entity_id") is not None:
            user = request.user if request.user.is_authenticated else None
            entity_id = notes_data.get("entity_id")
            entity_data = {
                "approvel_status": False,
            }
            handle_entity(entity_data, entity_id=entity_id, user=user)
        return ResponseService.response(
            "SUCCESS", updated, "default_update_success_msg"
        )

    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_note(note_id):
    deleted = QueryBuilderService("crmp_notes").where("id", note_id).delete()
    if deleted:
        return ResponseService.response(
            "SUCCESS", deleted, "default_delete_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def get_all_notes(request, policy_id=None, note_id=None):
    # Select columns, including created_at + user details
    columns = [
        "crmp_notes.*",
        "core_entities.created_at as created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_by_logo",
        "core_entities.updated_at as updated_at",
        "up_users.display_name as updated_by",
        "up_users.picture as updated_by_logo",
    ]

    # Build base query
    qb = (
        QueryBuilderService("crmp_notes")
        .select(*columns)
        .leftJoin("core_entities", "core_entities.id", "crmp_notes.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
        .leftJoin(
            "core_users as up_users", "up_users.id", "core_entities.updated_by_id"
        )
    )

    # Apply optional policy filter first
    if policy_id:
        qb = qb.where("crmp_notes.issued_policy_id", policy_id)

    # Handle fetching a single note by ID (with policy filter if provided)
    if note_id:
        note_qb = qb.where("crmp_notes.id", note_id)
        data = note_qb.first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

        _format_date_fields(data)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    # Pagination, Search, Sorting, Filtering for list endpoint
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    search = request.GET.get("search", "")
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "core_entities.created_at" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    filter_json = json.loads(request.GET.get("filter", "{}"))

    allowed_filters = ["title", "content", "health", "remarks"]
    search_columns = ["title", "content", "remarks"]
    sort_columns = ["core_entities.created_at", "id", "created_at"]

    # Apply filters, search, and pagination
    qb = qb.apply_conditions(filter_json, allowed_filters, search, search_columns)
    paginated = qb.paginate(page, limit, sort_columns, sort_by, sort_dir)

    # Format any '_at' date fields on each record
    rows = paginated.get("data", [])
    for item in rows:
        _format_date_fields(item)
    paginated["data"] = rows

    return ResponseService.response("SUCCESS", paginated, Message.DATA_FETCHED)
