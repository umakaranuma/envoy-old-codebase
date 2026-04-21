from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error

# Helper function to check if the user has permission
def check_permission(request, action_code):
    action = ActionService.getAction("RequestPolicy", action_code)
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    return None


# Helper function to handle query conditions, pagination, sorting
def apply_query_params(query, request, allowed_filters, search_columns, sort_columns):
    filter_json = request.query_params.get("filter", {})
    search_string = request.query_params.get("search", "")
    page = int(request.query_params.get("page", 1))
    limit = int(request.query_params.get("limit", 10))
    sort_by = request.query_params.get("sort_by", "name")
    sort_dir = request.query_params.get("sort_dir", "desc")

    return query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)


# Request Policy Insurers
@csrf_exempt
@api_view(["GET"])
def request_policy_insurers(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("core_service_providers")

    allowed_filters = ["name", "type_id"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# Request Policy Risk Types
@csrf_exempt
@api_view(["GET"])
def request_policy_risk_types(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crm_opportunity_types").select("id", "title AS name")

    allowed_filters = ["id", "title"]
    search_columns = ["title"]
    sort_columns = ["title", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# Request Policy Request Types
@csrf_exempt
@api_view(["GET"])
def request_policy_coverage_types(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crmp_coverage_types").select("id", "name")

    allowed_filters = ["id", "name"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# Request Policy Statuses
@csrf_exempt
@api_view(["GET"])
def request_policy_statuses(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("core_status").select("id", "name")

    allowed_filters = ["id", "name"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@csrf_exempt
@api_view(["GET"])
def request_types(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crmp_request_types")

    allowed_filters = ["name", "type_id"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# Payment Plans
@csrf_exempt
@api_view(["GET"])
def payment_plans(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crmp_payment_plans")

    allowed_filters = ["name", "type_id"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)



@csrf_exempt
@api_view(["GET"])
def request_endorsement_types(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crmp_endorsement_types") \
        .select("id", "name")

    allowed_filters = ["id", "name"]
    search_columns  = ["name"]
    sort_columns    = ["name", "id"]
    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def request_reason_codes_by_type(request, type_id):
    if error := check_permission(request, "VIEW"):
        return error

    query = (
        QueryBuilderService("crmp_endorsement_reasons_codes")
        .select("id", "code", "description AS name")
        .where("endorsement_type_id", type_id)
    )

    allowed_filters = ["id", "code", "description"]
    search_columns  = ["code", "description"]
    sort_columns    = ["code", "id"]
    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
