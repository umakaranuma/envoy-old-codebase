from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_policy_api.service import _format_date_fields
import json

@csrf_exempt
@api_view(["GET"])
def journal_entry_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("JournalEntry", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_all_entries(request)

def get_all_entries(request):
    columns = [
        "crmf_journal_entries.*",
        "core_entities.created_at as created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_by_logo",
        "core_entities.updated_at as updated_at",
        "up_users.display_name as updated_by",
        "up_users.picture as updated_by_logo",
        "crmf_chart_of_account.account_name",
        "crmf_chart_of_account.account_number"
    ]

    query = (
        QueryBuilderService("crmf_journal_entries")
        .select(*columns)
        .leftJoin("core_entities", "core_entities.id", "crmf_journal_entries.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
        .leftJoin("core_users as up_users", "up_users.id", "core_entities.updated_by_id")
        .leftJoin("crmf_chart_of_account", "crmf_chart_of_account.id", "crmf_journal_entries.account_id")
    )

    # Get filter parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmf_journal_entries.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = [
        "entry_number",
        "date",
        "account_id",
        "core_entities.created_at"
    ]
    search_columns = [
        "entry_number",
        "description",
        "crmf_chart_of_account.account_name",
        "crmf_chart_of_account.account_number"
    ]
    sort_columns = [
        "entry_number",
        "date",
        "debit_amount",
        "credit_amount",
        "created_at"
    ]

    # Apply filters and search
    data = query.apply_conditions(
        filter_json,
        allowed_filters,
        search_string,
        search_columns
    ).paginate(
        page,
        limit,
        sort_columns,
        sort_by,
        sort_dir
    )

    # Format date fields for each record
    rows = data.get("data", [])
    for item in rows:
        _format_date_fields(item)
    data["data"] = rows

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) 