from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_policy_api.service import (
    handle_entity,
    handle_entity_notes,
    handle_entity_docs,
)
from decimal import Decimal
from .invoice_utils import update_invoice_payment_details, update_invoice_status_after_payment
from types import SimpleNamespace
from datetime import datetime


@csrf_exempt
@api_view(["GET", "POST"])
def payment_list(request, policy_id=None):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("Payment", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_payments(request, policy_id)

    return create_payment(request)


def get_all_payments(request, policy_id=None):
    columns = [
        "crmp_payments.*",
        "remarks.notes as remarks",
        "docs.name as doc_name",
        "docs.doc as doc",
        "docs.type as doc_type",
        "core_entities.created_at as created_at",
        "core_users.display_name as created_by ",
        "core_users.picture as created_logo ",
        "crmp_invoices.invoice_number as invoice_code",
        "crmp_invoices.total_amount as total_amount",
    ]

    query = (
        QueryBuilderService("crmp_payments")
        .select(*columns)
        .leftJoin("crmp_invoices", "crmp_invoices.id", "crmp_payments.invoice_id")
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
            "crmp_endorsement_requests.issued_policy_id",
        )
        .leftJoin("core_entities", "core_entities.id", "crmp_payments.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
        .leftJoin(
            "core_entity_notes as remarks",
            "remarks.entity_id",
            "crmp_payments.entity_id",
        )
        .leftJoin(
            "core_entity_docs as docs",
            "docs.entity_id",
            "crmp_payments.entity_id",
        )
        .where_group(
            lambda group: group.extend(
                [
                    ("crmp_invoices.issued_policy_id = %s", [policy_id]),
                    ("crmp_issued_policies.id = %s", [policy_id]),
                ]
            )
        )
    )
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmp_payments.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["crmp_invoices.invoice_number", "core_entities.name"]
    search_columns = ["crmp_invoices.invoice_number"]
    sort_columns = ["crmp_payments.id"]

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def create_payment(request):
    data = json.loads(request.body or "{}")
    user = request.user if request.user.is_authenticated else None

    # Validation rules for required fields
    rules = {
        "invoice_id": "required|integer|exists:crmp_invoices,id",
        "paid_amount": "required|numeric",
        "created_by": "required|integer|exists:core_users,id",
        "created_at": "required",
        "payment_receipt_name": "required|string",
        "payment_receipt_url": "required|string",
        "payment_receipt_type": "nullable",
    }

    # Validate input data
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    # Fetch invoice with type information
    invoice = (
        QueryBuilderService("crmp_invoices")
        .select(
            "crmp_invoices.*",
            "crmp_endorsement_types.name as endorsement_type",
            "crmp_endorsement_requests.issued_policy_id"
        )
        .leftJoin(
            "crmp_endorsements_details",
            "crmp_endorsements_details.id",
            "crmp_invoices.endorsement_id"
        )
        .leftJoin(
            "crmp_endorsement_requests",
            "crmp_endorsement_requests.id",
            "crmp_endorsements_details.endorsement_request_id"
        )
        .leftJoin(
            "crmp_endorsement_types",
            "crmp_endorsement_types.id",
            "crmp_endorsement_requests.endorsement_type_id"
        )
        .where("crmp_invoices.id", data["invoice_id"])
        .first()
    )

    if not invoice:
        return ResponseService.response(
            "NOT_FOUND", 
            None, 
            "Invoice not found"
        )

    # Convert amounts to Decimal for accurate calculations
    paid_amount = Decimal(str(data["paid_amount"])).quantize(Decimal('.01'))
    outstanding_amount = Decimal(str(invoice.get("outstanding_amount", "0.00")))

    # Validate payment amount
    if paid_amount > outstanding_amount:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"paid_amount": ["Paid amount cannot exceed outstanding amount"]},
            Error.VALIDATION_ERROR
        )

    # Calculate new outstanding amount
    new_outstanding = (outstanding_amount - paid_amount).quantize(Decimal('.01'))
    data["outstanding_amount"] = str(new_outstanding)

    # Prepare base entity info
    entity_data = {
        "type": "payment",
        "approvel_status": False,
        "description": "Payment creation",
    }
    user_obj = SimpleNamespace(id=data["created_by"])

    # Create entity
    entity_id = handle_entity(
        entity_data,
        entity_id=data.get("entity_id"),
        user=user_obj,
        created_at=data["created_at"],
    )
    data["entity_id"] = entity_id

    # Insert payment
    created = QueryBuilderService("crmp_payments").insert(data)

    # Update invoice totals
    update_invoice_payment_details(data["invoice_id"], data["paid_amount"])
    
    # Update invoice status based on payment amounts
    update_invoice_status_after_payment(data["invoice_id"])

    # Update policy paid_amount if this is a policy-related invoice
    if invoice.get("issued_policy_id"):
        current_policy = (
            QueryBuilderService("crmp_issued_policies")
            .select("paid_amount")
            .where("id", invoice.get("issued_policy_id"))
            .first()
        )
        current_paid = Decimal(str(current_policy.get("paid_amount", "0.00")))
        new_paid = (current_paid + paid_amount).quantize(Decimal('.01'))

        # Update policy paid amount
        QueryBuilderService("crmp_issued_policies")\
            .where("id", invoice.get("issued_policy_id"))\
            .update({"paid_amount": str(new_paid)})

    # Handle optional notes
    if "remarks" in data:
        handle_entity_notes(entity_id, [{
            "note": data["remarks"],
            "created_by_id": request.user.id if request.user.is_authenticated else None,
            "created_at": datetime.now()
        }], is_update=False)

    # Handle attached receipt document
    receipt = None
    if "upload_receipt" in data:
        receipt = data["upload_receipt"]
    elif "payment_receipt_url" in data:
        receipt = {
            "doc": data["payment_receipt_url"],
            "name": data.get("payment_receipt_name", ""),
            "type": data.get("payment_receipt_type", "")
        }

    if receipt and receipt.get("doc"):
        handle_entity_docs(entity_id=entity_id, docs=[receipt])

    return ResponseService.response("SUCCESS", created, "default_create_success_msg")
