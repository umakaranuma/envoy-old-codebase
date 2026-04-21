# Insurer Invoice Number
# Boroker Invoice Number
# Endorsement Id
# Transaction Type
# Invoice Date
# Total Amount
# Paid Amount
# Outstanding Amount
# Remarks

from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error


@csrf_exempt
@api_view(["GET"])
def invoice_list(request, policy_id=None):
    action_type = "VIEW"
    action = ActionService.getAction("Invoice", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_all_invoices(request, policy_id)


def get_all_invoices(request, policy_id=None):
    columns = [
        "crmp_invoices.*",
        "core_entities.created_at as created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_logo",
        "crmp_endorsements_details.endorsement_id as endorsement_code",
        # "crmp_endorsements_details.endorsement_type as endorsement_type",
        # "crmp_endorsement_requests.request_code as endorsement_request_code",
        # "crmp_issued_policies.policy_number as policy_number",
    ]

    query = (
        QueryBuilderService("crmp_invoices")
        .select(*columns)
        .leftJoin(
            "crmp_endorsements_details",
            "crmp_endorsements_details.id",
            "crmp_invoices.endorsement_id",
        )
        .leftJoin(
            "crmp_endorsement_requests",
            "crmp_endorsement_requests.id",
            "crmp_endorsements_details.endorsement_request_id",
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmp_invoices.issued_policy_id",
        )
        .leftJoin("core_entities", "core_entities.id", "crmp_invoices.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
    )
    
    # Filter by policy_id if provided
    if policy_id:
        query = query.where("crmp_invoices.issued_policy_id", policy_id)

    # Get filters and search parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmp_invoices.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["crmp_invoices.invoice_number", "crmp_issued_policies.policy_number"]
    search_columns = ["crmp_invoices.invoice_number", "crmp_issued_policies.policy_number"]
    sort_columns = ["crmp_invoices.id"]

    # Apply filters and search
    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
