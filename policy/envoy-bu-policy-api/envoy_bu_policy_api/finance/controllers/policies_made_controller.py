from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
import json
from decimal import Decimal

@csrf_exempt
@api_view(["GET"])
def policies_made_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("PoliciesMade", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_all_policies_made(request)

def get_all_policies_made(request):
    # Define columns to select
    columns = [
        "crmp_issued_policies.id",
        "crmp_issued_policies.brokerage_policy_id as policy_number",
        "crmp_issued_policies.premium_amount",
        "crmp_issued_policies.policy_effective_date",
        "core_customers.name as customer_name",
        "core_entities.created_at as date"
    ]

    # Build base query
    query = (
        QueryBuilderService("crmp_issued_policies")
        .select(*columns)
        .leftJoin(
            "crmp_policy_base",
            "crmp_policy_base.id",
            "crmp_issued_policies.policy_base_id"
        )
        .leftJoin(
            "core_customers",
            "core_customers.id",
            "crmp_policy_base.customer_id"
        )
        .leftJoin(
            "core_entities",
            "core_entities.id",
            "crmp_issued_policies.entity_id"
        )
    )

    # Get filter parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmp_issued_policies.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    # Define allowed filters, search columns, and sort columns
    allowed_filters = [
        "brokerage_policy_id",
        "customer_name",
        "premium_amount",
        "policy_effective_date",
        "core_entities.created_at"
    ]
    search_columns = [
        "crmp_issued_policies.brokerage_policy_id",
        "core_customers.name",
        "crmp_issued_policies.premium_amount"
    ]
    sort_columns = [
        "brokerage_policy_id",
        "customer_name",
        "premium_amount",
        "policy_effective_date",
        "date"
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

    # Process the data
    rows = data.get("data", [])
    for row in rows:
        # Format premium amount as string
        if "premium_amount" in row:
            row["premium_amount"] = str(row["premium_amount"])

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) 