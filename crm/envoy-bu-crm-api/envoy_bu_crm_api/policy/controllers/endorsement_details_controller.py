from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from datetime import date
from django.db.models import Max
from envoy_bu_crm_api.policy.models.crmp_endorsements_details import Endorsement
from .invoice_utils import generate_invoice_for_endorsement
from decimal import Decimal
import decimal


@csrf_exempt
@api_view(["GET", "POST"])
def endorsement_list(request, policy_id=None):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("Endorsement", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_endorsements(request, endorsement_id=None, policy_id=policy_id)

    return create_endorsement(request)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def endorsement_detail(request, endorsement_id):
    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("Endorsement", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_endorsements(request, endorsement_id=endorsement_id)
    elif request.method == "PUT":
        return update_endorsement(request, endorsement_id)
    elif request.method == "DELETE":
        return delete_endorsement(endorsement_id)


def get_all_endorsements(request, endorsement_id=None, policy_id=None):
    columns = [
        "crmp_endorsements_details.*",
        "crmp_endorsement_types.name AS endorsement_type_name",
        "crmp_endorsement_reasons_codes.code AS reason_code",
        "crmp_endorsement_reasons_codes.description AS reason_code_description",
        "notes.notes AS remarks",
        "users.display_name AS created_by",
        "users.picture AS created_by_logo",
        "entities.created_at AS created_at",
        "crmp_endorsement_requests.endorsement_request as endorsement_request_code",
        "invoices.invoice_number AS invoice_number ",
        "CASE WHEN invoices.outstanding_amount > 0 THEN 'Outstanding' ELSE 'Settled' END AS invoice_status",
    ]

    query = (
        QueryBuilderService("crmp_endorsements_details")
        .select(*columns)
        .leftJoin(
            "crmp_endorsement_requests",
            "crmp_endorsement_requests.id",
            "crmp_endorsements_details.endorsement_request_id",
        )
        .leftJoin(
            "crmp_endorsement_types",
            "crmp_endorsement_types.id",
            "crmp_endorsement_requests.endorsement_type_id",
        )
        .leftJoin(
            "crmp_endorsement_reasons_codes",
            "crmp_endorsement_reasons_codes.id",
            "crmp_endorsement_requests.reason_code_id",
        )
        .leftJoin(
            "core_entities as entities",
            "entities.id",
            "crmp_endorsement_requests.entity_id",
        )
        .leftJoin(
            "core_entity_notes as notes",
            "notes.entity_id",
            "crmp_endorsement_requests.entity_id",
        )
        .leftJoin(
            "core_users as users",
            "users.id",
            "entities.created_by_id",
        )
        .leftJoin(
            "crmp_invoices as invoices",
            "invoices.endorsement_id",
            "crmp_endorsements_details.id",
        )
    )

    if endorsement_id:
        data = query.where("crmp_endorsements_details.id", endorsement_id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmp_endorsements_details.endorsement_date")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["status", "endorsement_id"]
    search_columns = ["endorsement_id", "remarks"]
    sort_columns = ["endorsement_date", "amount", "status"]
    if policy_id:
        data = query.leftJoin(
            "crmp_endorsement_requests as er",
            "er.id",
            "crmp_endorsements_details.endorsement_request_id",
        ).where("er.issued_policy_id", policy_id)

        data = query.apply_conditions(
            filter_json, allowed_filters, search_string, search_columns
        ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def create_endorsement(request):
    data = json.loads(request.body or "{}")
    data["endorsement_id"] = generate_endorse_request_id()
    data["status"] = 2
    errors = ValidatorService.validate(data, get_endorsement_rules())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    # Set default endorsement_date if not provided
    if not data.get("endorsement_date"):
        data["endorsement_date"] = str(date.today())

    # Get endorsement type and policy info
    endorsement_info = (
        QueryBuilderService("crmp_endorsement_requests")
        .select(
            "crmp_endorsement_types.name as endorsement_type",
            "crmp_endorsement_requests.cover_value as amount",
            "crmp_endorsement_requests.issued_policy_id as issued_policy_id"
        )
        .leftJoin(
            "crmp_endorsement_types",
            "crmp_endorsement_types.id",
            "crmp_endorsement_requests.endorsement_type_id"
        )
        .where("crmp_endorsement_requests.id", data["endorsement_request_id"])
        .first()
    )

    # Get initial premium amount from issued policy
    if endorsement_info and endorsement_info.get("issued_policy_id"):
        policy_info = (
            QueryBuilderService("crmp_issued_policies")
            .select(
                "initial_premium_amount",
                "premium_amount",
                "paid_amount"
            )
            .where("id", endorsement_info.get("issued_policy_id"))
            .first()
        )
        
        # Set current premium amount from initial premium amount
        data["current_premium_amount"] = policy_info.get("initial_premium_amount", "0.00")
        data["paid_amount"] = "0.00"
        data["amount"] = endorsement_info["amount"]

    # Get endorsement type and amount for calculations
    endorsement_type = endorsement_info.get("endorsement_type") if endorsement_info else None
    try:
        amount = Decimal(str(endorsement_info.get("amount", "0.00") or "0.00")).quantize(Decimal('.01'))

    except (decimal.InvalidOperation, TypeError):
        amount = Decimal("0.00")
   
        
    invoice_data = {
        "paid_amount": "0.00",
        "outstanding_amount": "0.00",
        "total_amount": str(amount)
    }
    
    if endorsement_type == "Cancellations":
        # For cancellations, mark full amount as paid and deduct from premium
        invoice_data["paid_amount"] = str(amount)
        invoice_data["outstanding_amount"] = "0.00"

        
    elif endorsement_type == "Refund":
        # For refunds, deduct from both premium and paid amount
        invoice_data["paid_amount"] = "0.00"
        invoice_data["outstanding_amount"] = str(amount)

        
    else:
        # For Additions and Non-Financials, add to premium only
        invoice_data["paid_amount"] = "0.00"
        invoice_data["outstanding_amount"] = str(amount)


    user = request.user if request.user.is_authenticated else None
    created = QueryBuilderService("crmp_endorsements_details").insert(data)

    # Generate invoice with the calculated amounts
    generate_invoice_for_endorsement(created["id"], is_update=False, user=user, invoice_data=invoice_data)

    return ResponseService.response("SUCCESS", created, "default_create_success_msg")


def update_endorsement(request, endorsement_id):
    data = json.loads(request.body or "{}")
    rules = get_endorsement_rules_put()
    rules["endorsement_id"] = "string"  # not required for update
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    updated = (
        QueryBuilderService("crmp_endorsements_details")
        .where("id", endorsement_id)
        .update(data)
    )
    user = request.user if request.user.is_authenticated else None

    generate_invoice_for_endorsement(endorsement_id, is_update=True, user=user)
    if updated:
        return ResponseService.response(
            "SUCCESS", updated, "default_update_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_endorsement(endorsement_id):
    deleted = (
        QueryBuilderService("crmp_endorsements_details")
        .where("id", endorsement_id)
        .delete()
    )
    if deleted:
        return ResponseService.response(
            "SUCCESS", deleted, "default_delete_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def get_endorsement_rules():
    return {
        # "endorsement_request_id": "required|integer|unique:crmp_endorsements_details,endorsement_request_id",
        "remarks": "string",
    }
def get_endorsement_rules_put():
    return {
        "remarks": "string",
    }


# |exists:crmp_endorsement_requests,id


def generate_endorse_request_id():
    last = Endorsement.objects.aggregate(Max("id"))["id__max"] or 0
    return f"END-{last + 1}"
