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
        "crmf_invoices.*",
        "crmf_invoice_types.name as transaction_type_name",
        "crmf_invoice_types.code as transaction_type_code",
        "crmf_invoice_types.id as transaction_type_id",
        "core_entities.created_at as created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_logo",
        "crmp_endorsements_details.endorsement_id as endorsement_code",
        "status.name AS invoice_status_name",
        "status.color AS invoice_status_color",
        "status.type AS invoice_status_type",
        # "crmp_endorsements_details.endorsement_type as endorsement_type",
        # "crmp_endorsement_requests.request_code as endorsement_request_code",
        # "crmp_issued_policies.policy_number as policy_number",
    ]

    query = (
        QueryBuilderService("crmf_invoices as crmf_invoices")
        .select(*columns)
        .leftJoin(
            "crmp_endorsements_details",
            "crmp_endorsements_details.id",
            "crmf_invoices.endorsement_id",
        )
        .leftJoin(
            "core_status as status",
            "status.id",
            "crmf_invoices.status_id",
        )
        .leftJoin(
            "crmp_endorsement_requests",
            "crmp_endorsement_requests.id",
            "crmp_endorsements_details.endorsement_request_id",
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id",
        )
        .leftJoin(
            "crmf_invoice_types",
            "crmf_invoice_types.id",
            "crmf_invoices.transaction_type_id",
        )
        .leftJoin("core_entities", "core_entities.id", "crmf_invoices.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
    )
    
    # Filter by policy_id if provided
    if policy_id:
        query = query.where("crmf_invoices.issued_policy_id", policy_id)

    # Get filters and search parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "core_entities.created_at" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    allowed_filters = ["crmf_invoices.invoice_number", "crmp_issued_policies.policy_number"]
    search_columns = ["crmf_invoices.invoice_number", "crmp_issued_policies.policy_number"]
    sort_columns = ["core_entities.created_at", "crmf_invoices.id"]

    # Apply filters and search
    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    # Process each record to format transaction_type
    rows = data.get("data", []) or data.get("rows", [])
    for row in rows:
        if row:
            transaction_type = {}
            transaction_type["id"] = row.get("transaction_type_id")
            transaction_type_name = row.get("transaction_type_name")
            # Change "New Business" to "Premium"
            if transaction_type_name == "New Business":
                transaction_type_name = "Premium"
            transaction_type["name"] = transaction_type_name
            transaction_type["code"] = row.get("transaction_type_code")
            row["transaction_type"] = transaction_type
            # Also update the direct field in the row
            row["transaction_type_name"] = transaction_type_name
    
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
