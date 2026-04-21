import json
from rest_framework.decorators import api_view
from django.core.exceptions import ValidationError
from django.conf import settings
import requests
from datetime import datetime, date
from decimal import Decimal

from envoy.models.channel import Channel
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService

from envoy.utils import get_message

PAYMENT_CREATE_API_URL = getattr(settings, "PAYMENT_CREATE_API_URL", None)


def _to_json_safe(value):
    """
    Convert values (including Decimal and datetime) into JSON-serializable types.
    """
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _to_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_json_safe(v) for v in value]
    return value

# --------------------------------------------------------
#crm, policies, opportunities, interactions, notes, interested products all tables used in here in the core
#---------------------------------------------------------

@api_view(['GET'])
def customer_account_overview(request, customer_id):
    try:
        # 1. Customer & entity
        customer = QueryBuilderService("core_customers as c") \
            .select("c.*",) \
            .where("c.id", customer_id).first()
        if not customer:
            return ResponseService.response("NOT_FOUND", None, "Customer not found")
        entity_id = customer.get("entity_id")

        # 2. Opportunities (as Leads)
        opportunities = QueryBuilderService("crm_opportunities as o") \
            .select("o.*",) \
            .where("o.customer_id", customer_id).get()

       # 3. Interactions
        interactions = QueryBuilderService("core_intractions as i") \
            .leftJoin("core_contacts as c", "c.id", "i.contact_id") \
            .leftJoin("core_channels as ch", "ch.id", "i.channel_id") \
            .leftJoin("core_users as u", "u.id", "i.contact_by_id") \
            .select(
                "i.*",
                "c.name as contact_name",
                "c.email as contact_email",
                "ch.name as channel_name",
                "ch.description as channel_description",
                "u.first_name as contact_by_first_name",
                "u.last_name as contact_by_last_name",
                "u.display_name as contact_by_display_name"
            ) \
            .where("i.customer_id", customer_id) \
            .get()



        # 4. Notes (entity-scoped)
        notes = []
        if entity_id:
            notes = QueryBuilderService("core_entity_notes as n") \
                .leftJoin("core_users", "core_users.id", "n.added_by_id") \
                .select("n.*", "core_users.picture as added_by_picture", "core_users.display_name as added_by_name") \
                .where("n.entity_id", entity_id).get()

        # 5. Policies via policy base
        policies = QueryBuilderService("crmp_policy_base as pb") \
            .leftJoin("core_products as p", "p.id", "pb.product_id") \
            .select(
                "pb.*",
                "p.name as product_name",
            ) \
            .where("pb.customer_id", customer_id).get()

        # 6. Interested Products (Opportunities → InterestedProducts)
        interested_products = QueryBuilderService("crm_oppor_interested_products as ip") \
            .leftJoin("core_products as p", "p.id", "ip.product_id") \
            .select("ip.*","p.*") \
            .leftJoin("crm_opportunities as o", "o.id", "ip.opportunity_id") \
            .where("o.customer_id", customer_id).get()

        result = {
            "customer": customer,
            "leads": opportunities,
            "interactions": interactions,
            "notes": notes,
            "policies": policies,
            "interested_products": interested_products
        }

        return ResponseService.response("SUCCESS", result, "Customer overview fetched successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred")
    



@api_view(['GET'])
def get_customer_leads(request, customer_id):
    try:
        if not QueryBuilderService("core_customers").where("id", customer_id).first():
            return ResponseService.response("NOT_FOUND", None, "Customer not found.")

        all_columns = ["*"]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["title", "code", "type"]
        search_columns = ["title", "code"]
        allowed_sorting_columns = ["id", "title", "code", "created_at"]

        query = (
            QueryBuilderService("crm_opportunities")
            .select(*all_columns)
            .where("customer_id", customer_id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, get_message("RETRIEVED", entity="Leads"))
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, get_message("SERVER_ERROR", entity="Leads"))


@api_view(['GET'])
def get_customer_interactions(request, customer_id):
    try:
        all_columns = [
            "i.*",
            "c.name as contact_name",
            "c.email as contact_email",
            "ch.name as channel_name",
            "ch.description as channel_description",
            "u.display_name as contact_by_name"
        ]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "i.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "i.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["notes"]
        search_columns = ["i.notes"]
        allowed_sorting_columns = ["i.id", "i.date", "i.created_at"]

        query = (
            QueryBuilderService("core_intractions as i")
            .leftJoin("core_contacts as c", "c.id", "i.contact_id")
            .leftJoin("core_channels as ch", "ch.id", "i.channel_id")
            .leftJoin("core_users as u", "u.id", "i.contact_by_id")
            .select(*all_columns)
            .where("i.customer_id", customer_id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, get_message("RETRIEVED", entity="Interactions"))
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, get_message("SERVER_ERROR", entity="Interactions"))


@api_view(['GET'])
def get_customer_notes(request, customer_id):
    try:
        customer = QueryBuilderService("core_customers").select("entity_id").where("id", customer_id).first()
        if not customer:
            return ResponseService.response("NOT_FOUND", None, "Customer not found.")
        
        entity_id = customer.get("entity_id")
        if not entity_id:
            return ResponseService.response("NOT_FOUND", None, "Entity not found.")

        all_columns = [
            "n.*",
            "u.display_name as added_by_name",
            "u.picture as added_by_picture"
        ]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "n.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "n.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["is_high_priority"]
        search_columns = ["n.notes"]
        allowed_sorting_columns = ["n.id", "n.added_at", "n.created_at"]

        # Get all entity IDs for this customer (customer + opportunities + policies)
        entity_ids = [entity_id]  # Start with customer entity_id
        
        # Get opportunity entity_ids for this customer
        opportunities = QueryBuilderService("crm_opportunities as o") \
            .select("o.entity_id") \
            .where("o.customer_id", customer_id) \
            .whereNotNull("o.entity_id") \
            .get()
        
        # Add opportunity entity_ids to the list
        opportunity_entity_ids = [opp["entity_id"] for opp in opportunities if opp.get("entity_id")]
        entity_ids.extend(opportunity_entity_ids)
        
        # Get policy entity_ids for this customer
        policies = QueryBuilderService("crmp_policy_base as pb") \
            .select("pb.id as policy_base_id") \
            .where("pb.customer_id", customer_id) \
            .get()

        # Extract policy_base_ids from the policies list
        policy_base_ids = [policy["policy_base_id"] for policy in policies if policy.get("policy_base_id")]

        issued_policies = []
        if policy_base_ids:
            issued_policies = QueryBuilderService("crmp_issued_policies as ip") \
                .select("ip.entity_id") \
                .whereIn("ip.policy_base_id", policy_base_ids) \
                .get()
        
        # Add policy entity_ids to the list
        policy_entity_ids = [policy["entity_id"] for policy in issued_policies if policy.get("entity_id")]
        entity_ids.extend(policy_entity_ids)

        # Get notes for all entity IDs
        query = (
            QueryBuilderService("core_entity_notes as n")
            .leftJoin("core_users as u", "u.id", "n.added_by_id")
            .select(*all_columns)
            .whereIn("n.entity_id", entity_ids)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        # Add type information to each note
        # Debug: Print the query structure
        print(f"DEBUG: Query type: {type(query)}")
        print(f"DEBUG: Query keys: {query.keys() if isinstance(query, dict) else 'Not a dict'}")
        
        if isinstance(query, dict) and "data" in query:
            # For paginated results
            print(f"DEBUG: Found data array with {len(query['data'])} items")
            for note in query["data"]:
                if note.get("entity_id") == entity_id:
                    note["type"] = "customer"
                elif note.get("entity_id") in policy_entity_ids:
                    note["type"] = "policy"
                else:
                    note["type"] = "lead"
        elif hasattr(query, 'data') and isinstance(query.data, list):
            # For QueryBuilderService results
            print(f"DEBUG: Found query.data with {len(query.data)} items")
            for note in query.data:
                if note.get("entity_id") == entity_id:
                    note["type"] = "customer"
                elif note.get("entity_id") in policy_entity_ids:
                    note["type"] = "policy"
                else:
                    note["type"] = "lead"
        else:
            print(f"DEBUG: Unexpected query structure: {query}")

        return ResponseService.response("SUCCESS", query, get_message("RETRIEVED", entity="Notes"))
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, get_message("SERVER_ERROR", entity="Notes"))


@api_view(['GET'])
def get_customer_policies(request, customer_id):
    try:
        all_columns = [
            "pb.*",
            "ip.*",
            "p.name as product_name"
        ]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "pb.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "pb.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["status"]
        search_columns = ["p.name"]
        allowed_sorting_columns = ["pb.id", "pb.policy_start_date", "pb.created_at"]

        query = (
            QueryBuilderService("crmp_issued_policies as ip")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .leftJoin("core_products as p", "p.id", "pb.product_id")
            .select(*all_columns)
            .where("pb.customer_id", customer_id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, get_message("RETRIEVED", entity="Policies"))
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, get_message("SERVER_ERROR", entity="Policies"))




@api_view(['GET'])
def get_customer_interested_products(request, customer_id):
    try:
        all_columns = ["ip.*", "p.name as product_name"]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "ip.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_filters = []
        search_columns = ["p.name"]
        allowed_sorting_columns = ["p.name", "ip.id"]

        query = (
            QueryBuilderService("crm_oppor_interested_products as ip")
            .leftJoin("core_products as p", "p.id", "ip.product_id")
            .leftJoin("crm_opportunities as o", "o.id", "ip.opportunity_id")
            .select(*all_columns)
            .where("o.customer_id", customer_id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, get_message("RETRIEVED", entity="Interested Products"))
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, get_message("SERVER_ERROR", entity="Interested Products"))


@api_view(["GET"])
def get_customer_payments(request):
    """
    Retrieve all customer payments from cus_payments (no restrictions), paginated.
    """
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "cus_payments.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = [
            "cus_payments.id",
            "cus_payments.invoice_id",
            "cus_payments.paid_amount",
            "cus_payments.outstanding_amount",
            "cus_payments.status",
            "cus_payments.created_at",
            "cus_payments.updated_at",
        ]
        all_columns = [
            "cus_payments.*",
            "ci.invoice_number",
            "ci.invoice_type",
            "ci.invoice_amount as total_amount",
            "st.name as status_name",
            "st.type as status_type",
            "st.color as status_color",
        ]
        query = (
            QueryBuilderService("cus_payments")
            .leftJoin("crmf_invoices as ci", "cus_payments.invoice_id", "ci.id")
            .leftJoin("core_status as st", "st.id", "cus_payments.status_id")
            .select(*all_columns)
        )
        data = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        if not data or (isinstance(data, dict) and not data.get("data")):
            return ResponseService.response("NOT_FOUND", {}, "settlements_not_found")
        return ResponseService.response("SUCCESS", data, "settlements_retrieved")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "error")


def get_next_customer_payment_id():
    """Return the next customer_payment_id (max + 1) from cus_payments."""
    last = (
        QueryBuilderService("cus_payments")
        .select("customer_payment_id")
        .orderBy("customer_payment_id", "desc")
        .first()
    )
    if last and last.get("customer_payment_id") is not None:
        return (last["customer_payment_id"] or 0) + 1
    return 1


@api_view(["POST"])
def confirm_customer_payment(request):
    """
    Confirm a customer payment by creating a policy payment via PAYMENT_CREATE_API_URL
    and updating the cus_payments status to payment_confirmed.
    Expects JSON body with:
      - customer_payment_id (or id): required, cus_payments.id
      - remarks (optional)
    """
    try:
        if not PAYMENT_CREATE_API_URL:
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {
                    "payment": [
                        {
                            "error_type": "configuration_missing",
                            "tokens": {"_attribute": "PAYMENT_CREATE_API_URL"},
                        }
                    ]
                },
                "Payment service URL is not configured.",
            )

        try:
            body = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            body = {}

        # Normalize and validate input
        customer_payment_id = body.get("customer_payment_id") or body.get("id")
        validation_data = {"customer_payment_id": customer_payment_id}
        rules = {"customer_payment_id": "required|integer|exists:cus_payments,id"}

        errors = ValidatorService.validate(validation_data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "validation_error")

        # Fetch payment with invoice details
        payment = (
            QueryBuilderService("cus_payments as cp")
            .leftJoin("crmf_invoices as ci", "cp.invoice_id", "ci.id")
            .select(
                "cp.*",
                "ci.invoice_amount as total_amount",
            )
            .where("cp.id", customer_payment_id)
            .first()
        )

        if not payment:
            return ResponseService.response("NOT_FOUND", None, "payment_not_found")

        # Build payload for create_payment service
        user = getattr(request, "user", None)
        created_by = getattr(user, "id", None) if user else None
        created_by_name = getattr(user, "display_name", "") if user else ""

        # Fallbacks for numbers
        paid_amount = payment.get("paid_amount") or 0
        invoice_id = payment.get("invoice_id")
        invoice_amount = payment.get("total_amount") or ""
        outstanding_amount = payment.get("outstanding_amount") or 0

        # Simple new outstanding amount calculation (service will recompute accurately)
        try:
            new_outstanding_amount = float(outstanding_amount) - float(paid_amount)
        except Exception:
            new_outstanding_amount = outstanding_amount

        receipt_name = payment.get("confirm_receipt_name") or payment.get("receipt_name") or ""
        receipt_url = payment.get("confirm_receipt") or payment.get("receipt") or ""
        receipt_type = payment.get("confirm_receipt_type") or payment.get("receipt_type") or ""

        # Normalize created_at to a JSON-serializable string (YYYY-MM-DD or ISO)
        raw_created_at = body.get("created_at") or payment.get("created_at") or ""
        if isinstance(raw_created_at, (datetime, date)):
            created_at_val = raw_created_at.strftime("%Y-%m-%d")
        else:
            created_at_val = str(raw_created_at) if raw_created_at is not None else ""

        payload = {
            "created_at": created_at_val,
            "created_by": body.get("created_by") or created_by,
            "paid_amount": paid_amount,
            "invoice_id": invoice_id,
            "invoice_amount": str(invoice_amount) if invoice_amount is not None else "",
            "outstanding_amount": outstanding_amount,
            "upload_receipt": body.get("upload_receipt", ""),
            "remarks": body.get("remarks", ""),
            "created_by_name": body.get("created_by_name") or created_by_name,
            "total_amount": body.get("total_amount", ""),
            "new_outstanding_amount": new_outstanding_amount,
            "reference_id": payment.get("reference_id"),
            "payment_receipt_name": body.get("payment_receipt_name") or receipt_name,
            "payment_receipt_url": body.get("payment_receipt_url") or receipt_url,
            "payment_receipt_type": body.get("payment_receipt_type") or receipt_type,
            # Allow passing explicit confirmation receipt fields if needed
            "confirmation_payment_receipt_name": body.get("confirmation_payment_receipt_name"),
            "confirmation_payment_receipt_url": body.get("confirmation_payment_receipt_url"),
            "confirmation_payment_receipt_type": body.get("confirmation_payment_receipt_type"),
            # Forward existing customer_payment_id so finance service can link records
            "customer_payment_id": payment.get("id"),
        }

        # Ensure payload is fully JSON-serializable (no Decimal/datetime objects)
        payload = _to_json_safe(payload)

        headers = {
            "Content-Type": "application/json",
            "Expect": "",
        }
        # Forward caller's Authorization header to the payment service so it
        # can authenticate using the same JWT.
        auth_header = request.headers.get("Authorization")
        if auth_header:
            headers["Authorization"] = auth_header

        try:
            resp = requests.post(
                PAYMENT_CREATE_API_URL,
                json=payload,
                headers=headers,
                timeout=30,
            )
        except Exception as e:
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": f"Payment service call failed: {str(e)}"},
                "payment_service_unavailable",
            )

        try:
            resp_data = resp.json() if resp.content else {}
        except ValueError:
            resp_data = {}

        # Normalize duplicate reference validation to field-level error format if needed
        if (
            not resp_data.get("is_success", False)
            and resp_data.get("message") == "duplicate_reference_id"
        ):
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "reference_id": [
                        {
                            "error_type": "duplicate",
                            "tokens": {"_attribute": "reference_id"},
                        }
                    ]
                },
                "validation_error",
            )

        if not resp.ok or not resp_data.get("is_success", False):
            # Bubble up remote validation errors when available
            result_errors = resp_data.get("result") or {}
            message = resp_data.get("message") or "payment_creation_failed"

            if message.upper() == "VALIDATION_ERROR" or message.lower() == "validation_error":
                return ResponseService.response("VALIDATION_ERROR", result_errors, "validation_error")

            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": result_errors or message},
                message,
            )

        # On success, update local cus_payments status to payment_confirmed
        status_row = (
            QueryBuilderService("core_status")
            .select("id", "name")
            .where("module", "payment")
            .where("type", "payment_confirmed")
            .first()
        )

        if status_row and status_row.get("id"):
            QueryBuilderService("cus_payments").where("id", customer_payment_id).update(
                {
                    "status_id": status_row["id"],
                    "status": status_row.get("name"),
                }
            )

        return ResponseService.response("SUCCESS", resp_data.get("result"), "payment_confirmed")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "payment_confirmation_error",
        )

