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
def commission_earned_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("CommissionEarned", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_all_commissions_earned(request)

def get_all_commissions_earned(request):
    # Define columns to select
    columns = [
        "crmf_agent_commission.id",
        "crmf_agent_commission.revenue_recognized as commission_amount",
        "crmp_issued_policies.brokerage_policy_id as policy_number",
        "core_users.first_name",
        "core_users.last_name",
        "core_entities.created_at as date"
    ]

    # Build base query
    query = (
        QueryBuilderService("crmf_agent_commission")
        .select(*columns)
        .leftJoin(
            "crmf_brokerage_commission",
            "crmf_brokerage_commission.id",
            "crmf_agent_commission.brokerage_commission_id"
        )
        .leftJoin(
            "crmf_invoices",
            "crmf_invoices.id",
            "crmf_brokerage_commission.invoice_id"
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id"
        )
        .leftJoin(
            "core_users",
            "core_users.id",
            "crmf_agent_commission.agent_id"
        )
        .leftJoin(
            "core_entities",
            "core_entities.id",
            "crmf_agent_commission.entity_id"
        )
    )

    # Get filter parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmf_agent_commissions.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    # Define allowed filters, search columns, and sort columns
    allowed_filters = [
        "brokerage_policy_id",
        "commission_amount",
        "core_entities.created_at"
    ]
    search_columns = [
        "crmp_issued_policies.brokerage_policy_id",
        "core_users.first_name",
        "core_users.last_name"
    ]
    sort_columns = [
        "brokerage_policy_id",
        "commission_amount",
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
        # Format commission amount as string
        if "commission_amount" in row:
            row["commission_amount"] = str(row["commission_amount"])
        
        # Combine first and last name into recipient_name
        if "first_name" in row and "last_name" in row:
            row["recipient_name"] = f"{row['first_name']} {row['last_name']}"
            del row["first_name"]
            del row["last_name"]

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) 