from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
import json
from decimal import Decimal
from datetime import datetime

@csrf_exempt
@api_view(["GET"])
def debtor_aging_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("DebtorAging", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_debtor_aging(request)

def get_debtor_aging(request):
    # Base query to get invoices and their payments
    query = (
        QueryBuilderService("crmf_invoices")
        .select(
            "crmf_invoices.due_date",
            "crmf_invoices.outstanding_amount",
            "core_service_providers.name as insurer_name",
            "core_service_providers.id as insurer_id",
            "core_service_providers.logo as insurer_logo"
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id"
        )
        .leftJoin(
            "crmp_policy_base",
            "crmp_policy_base.id",
            "crmp_issued_policies.policy_base_id"
        )
        .leftJoin(
            "core_service_providers",
            "core_service_providers.id",
            "crmp_policy_base.insurer_id"
        )
        .where("crmf_invoices.outstanding_amount", "0", ">")
    )

    # Get filter parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "insurer_name")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["insurer_id", "due_date"]
    search_columns = ["core_service_providers.name"]
    sort_columns = ["insurer_name", "total_outstanding"]

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

    # Process the data to calculate aging
    rows = data.get("data", [])
    aging_data = {}

    today = datetime.now().date()

    for invoice in rows:
        insurer_id = invoice["insurer_id"]
        if insurer_id not in aging_data:
            aging_data[insurer_id] = {
                "insurer_id": insurer_id,
                "insurer_name": invoice["insurer_name"],
                "insurer_logo": invoice["insurer_logo"],
                "current": Decimal('0.00'),
                "days_1_30": Decimal('0.00'),
                "days_31_60": Decimal('0.00'),
                "days_61_90": Decimal('0.00'),
                "over_90_days": Decimal('0.00'),
                "total_outstanding": Decimal('0.00')
            }

        # due_date is already a date object, no need to parse
        due_date = invoice["due_date"]
        days_overdue = (today - due_date).days
        balance = Decimal(str(invoice["outstanding_amount"]))

        # Categorize by age
        if days_overdue <= 0:
            aging_data[insurer_id]["current"] += balance
        elif days_overdue <= 30:
            aging_data[insurer_id]["days_1_30"] += balance
        elif days_overdue <= 60:
            aging_data[insurer_id]["days_31_60"] += balance
        elif days_overdue <= 90:
            aging_data[insurer_id]["days_61_90"] += balance
        else:
            aging_data[insurer_id]["over_90_days"] += balance

        aging_data[insurer_id]["total_outstanding"] += balance

    # Convert the dictionary to a list and sort by insurer name
    processed_data = list(aging_data.values())
    processed_data.sort(key=lambda x: x["insurer_name"])

    # Convert Decimal to string for JSON serialization
    for item in processed_data:
        item["current"] = str(item["current"])
        item["days_1_30"] = str(item["days_1_30"])
        item["days_31_60"] = str(item["days_31_60"])
        item["days_61_90"] = str(item["days_61_90"])
        item["over_90_days"] = str(item["over_90_days"])
        item["total_outstanding"] = str(item["total_outstanding"])

    # Update the response data
    data["data"] = processed_data
    data["total"] = len(processed_data)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) 