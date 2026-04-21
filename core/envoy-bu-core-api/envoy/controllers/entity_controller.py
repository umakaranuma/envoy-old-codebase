from mServices.QueryBuilderService import QueryBuilderService
from envoy.models.entity import Entity
from envoy.models.entity_note import EntityNote
from envoy.models.entity_document import EntityDocument
from envoy.models.entity_flag import EntityFlag
from envoy.models.entity_activity import EntityActivity
from envoy.models.flag import Flag
from envoy.models.flex_value import FlexValue
from rest_framework.decorators import api_view
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
import json


@api_view(['GET'])
def get_entities(request):
    ids = request.GET.get('ids', None)

    data = []
    if ids:
        data = (
            QueryBuilderService("core_entities")
            .leftJoin("core_users as creator", "creator.id", "core_entities.created_by_id")
            .leftJoin("core_users as updater", "updater.id", "core_entities.updated_by_id")
            .select(
                "core_entities.*",
                "creator.display_name as created_by_name",
                "creator.picture as created_by_picture",
                "updater.display_name as updated_by_name",
                "updater.picture as updated_by_picture"
            )
            .whereIn("core_entities.id", ids.split(','))
            .get()
        )

    return ResponseService.response('SUCCESS', data, "Entities fetched successfully")


@api_view(["GET"])
def get_entity_with_details(request, id):
    try:
        attri = request.GET.get("attri", "")
        include_fields = [a.strip() for a in attri.split(",") if a.strip()]

        # Use QueryBuilderService to fetch entity with user info
        entity = (
            QueryBuilderService("core_entities as e")
            .leftJoin("core_users as created_by", "created_by.id", "e.created_by_id")
            .leftJoin("core_users as updated_by", "updated_by.id", "e.updated_by_id")
            .select(
                "e.id",
                "e.type",
                "e.created_by_id",
                "e.updated_by_id",
                "e.created_at",
                "created_by.display_name as created_by_name",
                "created_by.picture as created_by_profile",
                "updated_by.display_name as updated_by_name",
                "updated_by.picture as updated_by_profile"
            )
            .where("e.id", id)
            .first()
        )

        if not entity:
            return ResponseService.response("NOT_FOUND", None, "Entity not found")

        data = dict(entity)

        # Conditional: Notes
        if "notes" in include_fields:
            data["notes"] = list(
                EntityNote.objects.filter(entity_id=id).values()
            )

        # Conditional: Documents
        if "documents" in include_fields:
            data["documents"] = list(
                EntityDocument.objects.filter(entity_id=id).values()
            )

        # Conditional: Flags
        if "flags" in include_fields:
            flags = (
                QueryBuilderService("core_entity_flags as ef")
                .leftJoin("core_flags as f", "f.id", "ef.flag_id")
                .select(
                    "ef.flag_id as id",
                    "f.name",
                    "f.description",
                    "f.color"
                )
                .where("ef.entity_id", id)
                .get()
            )
            data["flags"] = list(flags)

        # Conditional: Activities
        if "activities" in include_fields:
            data["activities"] = list(
                EntityActivity.objects.filter(entity_id=id).values()
            )

        # Conditional: Flex Field Values
        if "flex_field_values" in include_fields:
            flex_value = FlexValue.objects.filter(entity_id=id).first()
            data["flex_field_values"] = flex_value.flex_values if flex_value else {}

        return ResponseService.response(
            "SUCCESS", message="Entity details fetched successfully", result=data
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Something went wrong"
        )


#----------------------------------

# -------------------- Entity Activities --------------------

@api_view(["GET", "POST"])
def entity_activities(request, id):
    if request.method == "GET":
        return get_entity_activities(request, id)
    elif request.method == "POST":
        return post_entity_activities(request, id)


def get_entity_activities(request, id):
    """Retrieve all activities for a specific entity with pagination, sorting, and optional date filtering"""
    try:
        all_columns = ["ea.*", "core_users.display_name as added_by_name", "core_users.picture as added_by_picture"]
        filter_json = request.GET.get("filter", "{}")
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_filters = ["activity"]
        search_columns = ["activity"]
        allowed_sorting_columns = ["activity", "added_at"]

        from_date = request.GET.get("from_date")
        to_date = request.GET.get("to_date")

        # Build the query
        query = (
            QueryBuilderService("core_entity_activities as ea")
            .select(*all_columns)
            .where("ea.entity_id", id)
            .leftJoin("core_users", "core_users.id","ea.added_by_id")
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        )

        # Date filtering
        if from_date and to_date:
            query = query.whereBetween("ea.added_at", from_date, to_date)
        elif from_date:
            query = query.where("ea.added_at", from_date, ">=")
        elif to_date:
            query = query.where("ea.added_at", to_date, "<=")

        # Pagination
        query = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

        return ResponseService.response(
            "SUCCESS",
            query,
            "Activities Fetched Successfully"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error"
        )


def post_entity_activities(request, id):
    try:
        entity = Entity.objects.filter(id=id).first()
        if not entity:
            return ResponseService.response("NOT_FOUND", None, "Entity not found")

        data = json.loads(request.body)
        rules = {"activity": "required"}
        messages = {"activity.required": "Activity is required."}

        errors = ValidatorService.validate(data, rules, messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        activity = EntityActivity.objects.create(entity=entity, activity=data["activity"])

        return ResponseService.response("SUCCESS", {"id": activity.id}, "default_create_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(["PUT", "DELETE"])
def entity_activity_detail(request, id, activity_id):
    try:
        activity = EntityActivity.objects.filter(id=activity_id, entity_id=id).first()
        if not activity:
            return ResponseService.response("NOT_FOUND", None, "Activity not found")

        if request.method == "PUT":
            data = json.loads(request.body)
            rules = {"activity": "required"}
            messages = {"activity.required": "Activity is required."}

            errors = ValidatorService.validate(data, rules, messages)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

            activity.activity = data["activity"]
            activity.save()

            return ResponseService.response("SUCCESS", None, "default_update_success_msg")

        elif request.method == "DELETE":
            activity.delete()
            return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


# -------------------- Entity Flags --------------------

@api_view(["POST"])
def entity_flags(request, id):
    try:
        entity = Entity.objects.filter(id=id).first()
        if not entity:
            return ResponseService.response("NOT_FOUND", None, "Entity not found")

        data = json.loads(request.body)
        rules = {"flag_id": "required|exists:core_flags,id"}
        messages = {"flag_id.required": "Flag is required."}

        errors = ValidatorService.validate(data, rules, messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Check if the flag is already added to the entity
        existing_entity_flag = EntityFlag.objects.filter(entity=entity, flag_id=data["flag_id"]).first()
        if existing_entity_flag:
            return ResponseService.response("CONFLICT", None, "flag_conflict_msg", "FLAG_ALREADY_ADDED")

        flag = Flag.objects.filter(id=data["flag_id"]).first()
        if not flag:
            return ResponseService.response("NOT_FOUND", None, "Flag not found")

        entity_flag = EntityFlag.objects.create(entity=entity, flag=flag)

        return ResponseService.response("SUCCESS", {"id": entity_flag.id}, "default_create_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
@api_view(["PUT", "DELETE"])
def entity_flag_detail(request, id, flag_id):
    try:
        entity_flag = EntityFlag.objects.filter(flag_id=flag_id, entity_id=id).first()
        if not entity_flag:
            return ResponseService.response("NOT_FOUND", None, "Flag not found")

        if request.method == "PUT":
            data = json.loads(request.body)
            rules = {"flag_id": "required|exists:core_flags,id"}
            messages = {"flag_id.required": "Flag is required."}

            errors = ValidatorService.validate(data, rules, messages)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

            new_flag = Flag.objects.filter(id=data["flag_id"]).first()
            if not new_flag:
                return ResponseService.response("NOT_FOUND", None, "New flag not found")

            entity_flag.flag = new_flag
            entity_flag.save()

            return ResponseService.response("SUCCESS", None, "default_update_success_msg")

        elif request.method == "DELETE":
            entity_flag.delete()
            return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
