from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_policy_api.service import (
    handle_entity,
    handle_entity_notes,
    handle_entity_docs,
)
from decimal import Decimal
from .utils.invoice_utils import update_invoice_payment_details, update_invoice_status_after_payment
from types import SimpleNamespace
from datetime import datetime, date
import time
from ..models.crmf_incentives import Incentive
from envoy_bu_policy_api.finance.controllers.utils.commission.commission_pay_utils import update_revenue_realized, update_agent_commission_revenue_realized_for_brokerage_payment
from envoy_bu_policy_api.finance.controllers.utils.commission.base_calculator import get_commission_calculation_mode

# Configuration constants for receipt number generation
RECEIPT_NUMBER_CONFIG = {
    "PREFIX": "RCPT",
    "MAX_ATTEMPTS": 10,
    "RANDOM_MIN": 1000,
    "RANDOM_MAX": 9999,
    "RETRY_DELAY": 0.001,  # seconds
    "FORMAT": "RCPT-YYYYMMDD-XXXX"
}

def validate_receipt_number_format(receipt_number):
    """Validate that receipt number follows expected format"""
    if not receipt_number:
        return False, "Receipt number is empty"
    
    if not isinstance(receipt_number, str):
        return False, "Receipt number must be a string"
    
    expected_prefix = f"{RECEIPT_NUMBER_CONFIG['PREFIX']}-"
    if not receipt_number.startswith(expected_prefix):
        return False, f"Receipt number must start with '{expected_prefix}'"
    
    # Check if it's a fallback receipt (contains FALLBACK or EMERGENCY)
    if "FALLBACK" in receipt_number or "EMERGENCY" in receipt_number:
        return True, "Fallback receipt number (acceptable for emergency cases)"
    
    # Check if it's a timestamp-suffixed receipt (contains HHMMSS)
    if len(receipt_number.split("-")) == 4 and receipt_number.split("-")[3].isdigit() and len(receipt_number.split("-")[3]) == 6:
        return True, "Timestamp-suffixed receipt number (acceptable for database errors)"
    
    # Check standard format: RCPT-YYYYMMDD-XXXX
    parts = receipt_number.split("-")
    if len(parts) != 3:
        return False, f"Receipt number must have 3 parts separated by '-', got {len(parts)}"
    
    if not parts[1].isdigit() or len(parts[1]) != 8:
        return False, "Date part must be 8 digits (YYYYMMDD)"
    
    if not parts[2].isdigit() or len(parts[2]) != 4:
        return False, "Random part must be 4 digits"
    
    return True, "Valid receipt number format"

@csrf_exempt
@api_view(["GET", "POST"])
def payment_list(request, policy_id=None, invoice_id=None):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("Payment", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_payments(request, policy_id, invoice_id)

    return create_payment(request)


def get_all_payments(request, policy_id=None, invoice_id=None):
    columns = [
        "crmf_payments.*",
        "remarks.notes as remarks",
        "docs.name as doc_name",
        "docs.doc as doc",
        "docs.type as doc_type",
        "core_entities.created_at as payment_created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_logo",
        "crmf_invoices.invoice_number as invoice_code",
        "crmf_invoices.invoice_amount as total_amount",
        "crmf_invoices.paid_amount as total_paid_amount",
        "crmf_invoices.outstanding_amount as current_outstanding",
        "crmf_invoices.last_paid_date as last_payment_date",
        "crmf_invoices.invoice_date",
        "crmf_invoices.due_date",
        "crmf_invoices.invoice_type",
        "crmf_transaction_types.name as transaction_type_name",
        "crmf_transaction_types.code as transaction_type_code",
        "crmp_endorsements_details.endorsement_id as endorsement_code",
        "crmp_issued_policies.brokerage_policy_id as policy_number",
        "crmp_issued_policies.start_date as policy_start_date",
        "crmp_issued_policies.end_date as policy_end_date",
        "crmp_issued_policies.sum_insured as insured_amount",
        "crmp_issued_policies.premium_amount as premium_amount",
        "crmp_issued_policies.remarks AS insurer_notes",
        "products.id AS product_id",
        "risk_type.title AS risk_type_name",
        "risk_type.id AS risk_type_id",
        "insurer_sp.name AS insurer_info_full_name",
        "insurer_sp.id AS insurer_id",
        "insurer_sp.logo AS insurer_info_logo",
        "customers.name as customer_name",
        "customers.logo as customer_logo",
        "customers.id as customer_id",
        "products.name as product",
        "request_policy.policy_request_id as policy_request_code",
        "request_policy.id as policy_request_id",
        "request_status.name AS policy_request_status",
        "request_status.color AS policy_request_status_color",
        "policy_base.quotation_document as quotation_document",
        "policy_base.quotation_document_name as quotation_document_name",
        "request_by.display_name AS requested_by",
        "request_by.picture AS requested_by_logo",
        "request_type.name AS request_type",
        "request_type.id AS request_type_id",
        "request_customer_contact.email AS customer_email",
        "request_customer_contact.address AS customer_address",
        "request_customer_contact.primary_contact AS customer_primary_contact",
        "coverage_type.name AS coverage_type",
        "coverage_type.id AS coverage_type_id",
        "payment_plan.name AS payment_plan",
        "payment_plan.id AS payment_plan_id",
        "updated_by.display_name AS updated_by",
        "updated_by.picture AS updated_by_logo",
        "core_entities.updated_at AS updated_at",
        "product_groups.id AS product_group_id",
        "product_groups.name AS product_group",


    ]

    query = (
        QueryBuilderService("crmf_payments")
        .select(*columns)
        .leftJoin("crmf_invoices", "crmf_invoices.id", "crmf_payments.invoice_id")
        .leftJoin(
            "crmf_transaction_types",
            "crmf_transaction_types.id",
            "crmf_invoices.transaction_type_id"
        )
        .leftJoin(
            "crmp_endorsements_details",
            "crmp_endorsements_details.id",
            "crmf_invoices.endorsement_id"
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id"
        )
        .leftJoin("core_entities", "core_entities.id", "crmf_payments.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
        .leftJoin(
            "core_entity_notes as remarks",
            "remarks.entity_id",
            "crmf_payments.entity_id"
        )
        .leftJoin(
            "core_entity_docs as docs",
            "docs.entity_id",
            "crmf_payments.entity_id"
        )
        .leftJoin(
            "crmp_policy_base as policy_base",
            "policy_base.id",
            "crmp_issued_policies.policy_base_id",
        )
        .leftJoin(
            "crm_opportunity_types as risk_type",
            "risk_type.id",
            "policy_base.risk_type_id",
        )
        .leftJoin(
            "core_service_providers as insurer_sp",
            "insurer_sp.id",
            "policy_base.insurer_id",
        )
        .leftJoin(
            "core_customers as customers", "customers.id", "policy_base.customer_id"
        )
        .leftJoin("core_vendor_products as products", "products.id", "policy_base.product_id")
        .leftJoin("core_product_groups as product_groups", "product_groups.id", "policy_base.product_group_id")

        .leftJoin(
            "core_users as request_by", "request_by.id", "policy_base.request_by_id"
        )
        .leftJoin(
            "crmp_request_policies as request_policy",
            "request_policy.id",
            "crmp_issued_policies.policy_request_id",
        )
        .leftJoin(
            "core_status as request_status",
            "request_status.id",
            "request_policy.status_id",
        )
        .leftJoin(
            "crmp_request_types as request_type",
            "request_type.id",
            "policy_base.request_type_id",
        )
        .leftJoin(
            "core_contacts as request_customer_contact",
            "request_customer_contact.id",
            "customers.primary_contact_id",
        )
        .leftJoin(
            "crmp_coverage_types as coverage_type",
            "coverage_type.id",
            "policy_base.coverage_type_id",
        )
        .leftJoin(
            "crmp_payment_plans as payment_plan",
            "payment_plan.id",
            "policy_base.payment_mode_id",
        )
        .leftJoin("core_users as updated_by", "updated_by.id", "core_entities.updated_by_id")

    )

    # Add conditions based on provided IDs
    if invoice_id:
        # For invoice-specific payments, order by payment date to show history
        query = (
            query.where("crmf_payments.invoice_id", invoice_id)
            .orderBy("core_entities.created_at", "desc")
        )
    elif policy_id:
        query = query.where_group(
            lambda group: group.extend(
                [
                    ("crmf_invoices.issued_policy_id = %s", [policy_id]),
                    ("crmp_issued_policies.id = %s", [policy_id]),
                ]
            )
        )

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by" )
    sort_dir = request.GET.get("sort_dir")
    sort_by = "core_entities.created_at" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    allowed_filters = ["crmf_invoices.invoice_number", "core_entities.name", "crmf_payments.receipt_number"]
    search_columns = ["crmf_invoices.invoice_number", "crmf_payments.receipt_number"]
    sort_columns = ["crmf_payments.id", "core_entities.created_at"]

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    # Add payment summary for invoice-specific queries
    if invoice_id:
        payment_summary = {
            "total_payments": len(data.get("data", [])),
            "total_paid": sum(Decimal(str(payment.get("paid_amount", "0.00"))) for payment in data.get("data", [])),
            "current_outstanding": data.get("data", [{}])[0].get("current_outstanding", "0.00") if data.get("data") else "0.00",
            "last_payment_date": data.get("data", [{}])[0].get("last_payment_date") if data.get("data") else None
        }
        data["payment_summary"] = payment_summary

    # Get product group products separately for items that have product_group_id
    for item in data.get("data", []):
        product_group_id = item.get("product_group_id")
        if product_group_id:
            # Fetch product group products separately
            product_group_products_query = (
                QueryBuilderService("core_product_group_products")
                .select(
                    "core_product_group_products.id",
                    "core_product_group_products.product_id",
                    "core_product_vendor_products.vendor_product_id",
                    "core_vendor_products.name as vendor_product_name"
                )
                .leftJoin("core_product_vendor_products", "core_product_vendor_products.product_id", "core_product_group_products.product_id")
                .leftJoin("core_vendor_products", "core_vendor_products.id", "core_product_vendor_products.vendor_product_id")
                .where("core_product_group_products.product_group_id", product_group_id)
                .get()
            )
            item["product_group_products"] = product_group_products_query
        else:
            item["product_group_products"] = []
        # Remove the raw JSON string
        item.pop("product_group_products_json", None)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def customer_payment_id(request,invoice_id):

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "cus_payments.id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    allowed_filters = ["cus_payments.id",]
    search_columns = ["cus_payments.id"]
    sort_columns = ["cus_payments.created_at", "cus_payments.id",]


    invoice = (
        QueryBuilderService('crmf_invoices')
        .where('id',invoice_id)
        .first()
    )

    if not invoice:
        return ResponseService.response("NOT_FOUND",None,"invoice_data_not_found")
    
    print(invoice)
    data = (
        QueryBuilderService('cus_payments')
        .select('id','invoice_id','customer_payment_id')
        .where('invoice_id',invoice_id)
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns )
        .paginate(page, limit, sort_columns, sort_by, sort_dir)
        
    )
    print(data)

    if not data:
        return ResponseService.response("NOT_FOUND",None,"data_not_found")
    print(data)
    return ResponseService.response("SUCCESS",data,"data_get_successfully")


def create_payment(request):
    data = json.loads(request.body or "{}")
    user = request.user if request.user.is_authenticated else None
    
    print(f"DEBUG: Full request data received: {data}")

    # Validation rules for required fields
    rules = {
        "invoice_id": "required|integer|exists:crmf_invoices,id",
        "paid_amount": "required|numeric|gt:0",
        "created_by": "required|integer|exists:core_users,id",
        "created_at": "required",
        "payment_receipt_name": "required|string",
        "payment_receipt_url": "required|string",
        "payment_receipt_type": "nullable",
        "confirmation_payment_receipt_name":"nullable",
        "confirmation_payment_receipt_url":"nullable",
        "confirmation_payment_receipt_type":"nullable",
        "customer_payment_id":"nullable|unique|integer|exist:cus_payments,customer_payment_id",
        "reference_id": "required|string",
    }

    # Validate input data
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    # Fetch invoice with type information
    invoice = (
        QueryBuilderService("crmf_invoices")
        .select(
            "crmf_invoices.*",
            "crmf_invoices.issued_policy_id as issued_policyId",
            "crmp_endorsement_types.name as endorsement_type",
            "crmp_endorsement_requests.issued_policy_id",
            "crmp_policy_base.customer_id"
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id",
        )
        .leftJoin(
            "crmp_policy_base",
            "crmp_policy_base.id",
            "crmp_issued_policies.policy_base_id",
        )
        .leftJoin(
            "crmp_endorsements_details",
            "crmp_endorsements_details.id",
            "crmf_invoices.endorsement_id"
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
        .where("crmf_invoices.id", data["invoice_id"])
        .first()
    )

    if not invoice:
        return ResponseService.response(
            "NOT_FOUND", 
            None, 
            "Invoice not found"
        )

    print("invoice :",invoice)
    # Convert amounts to Decimal for accurate calculations
    paid_amount = Decimal(str(data["paid_amount"])).quantize(Decimal('.01'))
    outstanding_amount = Decimal(str(invoice.get("outstanding_amount", "0.00")))

    # Check brokerage commission outstanding amount
    # If outstanding amount is 0 or negative, prevent new payments
    brokerage_commission = (
        QueryBuilderService("crmf_brokerage_commission")
        .select(
            "crmf_brokerage_commission.revenue_recognized",
            "crmf_brokerage_commission.revenue_realized",
            "crmf_brokerage_commission.commission_deductible"
        )
        .where("crmf_brokerage_commission.invoice_id", data["invoice_id"])
        .first()
    )

    if brokerage_commission:
        # Calculate brokerage commission outstanding amount
        revenue_recognized = Decimal(str(brokerage_commission.get("revenue_recognized", "0.00")))
        revenue_realized = Decimal(str(brokerage_commission.get("revenue_realized", "0.00")))
        commission_deductible = Decimal(str(brokerage_commission.get("commission_deductible", "0.00")))
        
        brokerage_outstanding = revenue_recognized - revenue_realized - commission_deductible
        
        # If brokerage commission outstanding is 0 or negative, prevent payment
        if brokerage_outstanding <= 0:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "paid_amount": [{
                        "error_type": "no_payment_allowed_zero_or_negative_outstanding",
                        "tokens": {"_attribute": "paid_amount"}
                    }]
                },
                "Cannot create payment. Brokerage commission outstanding amount is 0 or negative."
            )

    # Validate payment amount
    if paid_amount > outstanding_amount:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {
                "paid_amount": [{
                    "error_type": "paid_amount_cannot_exceed_outstanding_amount",
                    "tokens": {"_attribute": "paid_amount"}
                }]
            },
            Error.VALIDATION_ERROR
        )

    # Validate paid_amount against premium amount calculation
    # paid_amount should be <= (current premium amount - refund invoices - cancellation invoices - paid amounts)
    issued_policy_id = invoice.get("issued_policyId") or invoice.get("issued_policy_id")
    if issued_policy_id:
        # Get current premium amount from issued policy
        issued_policy = (
            QueryBuilderService("crmp_issued_policies")
            .select("premium_amount")
            .where("id", issued_policy_id)
            .first()
        )
        
        if issued_policy:
            current_premium = Decimal(str(issued_policy.get("premium_amount", "0.00")))
            
            # Get sum of refund invoices (transaction_type_id = 4) for this policy
            refund_invoices = (
                QueryBuilderService("crmf_invoices")
                .select("invoice_amount")
                .where("issued_policy_id", issued_policy_id)
                .where("transaction_type_id", 4)  # Refund
                .get()
            )
            refund_total = sum(Decimal(str(inv.get("invoice_amount", "0.00"))) for inv in refund_invoices)
            
            # Get sum of cancellation invoices (transaction_type_id = 5) for this policy
            cancellation_invoices = (
                QueryBuilderService("crmf_invoices")
                .select("invoice_amount")
                .where("issued_policy_id", issued_policy_id)
                .where("transaction_type_id", 5)  # Cancellation
                .get()
            )
            cancellation_total = sum(Decimal(str(inv.get("invoice_amount", "0.00"))) for inv in cancellation_invoices)
            
            # Get sum of all paid amounts from payments for all invoices of this policy
            all_policy_invoices = (
                QueryBuilderService("crmf_invoices")
                .select("id")
                .where("issued_policy_id", issued_policy_id)
                .get()
            )
            invoice_ids = [inv.get("id") for inv in all_policy_invoices if inv.get("id")]
            
            paid_total = Decimal("0.00")
            if invoice_ids:
                all_payments = (
                    QueryBuilderService("crmf_payments")
                    .select("paid_amount")
                    .whereIn("invoice_id", invoice_ids)
                    .get()
                )
                paid_total = sum(Decimal(str(payment.get("paid_amount", "0.00"))) for payment in all_payments)
            
            # Calculate maximum allowed paid amount
            # Formula: current_premium - refund_total - cancellation_total - paid_total
            max_allowed_paid_raw = current_premium -refund_total - cancellation_total - paid_total
            max_allowed_paid = max(Decimal("0.00"), max_allowed_paid_raw)
            
            # Validate that paid_amount doesn't exceed the calculated maximum
            if paid_amount > max_allowed_paid:
                validation_errors = {}
                if "paid_amount" not in validation_errors:
                    validation_errors["paid_amount"] = []
                ValidatorService._add_error(
                    validation_errors, 
                    "paid_amount", 
                    "lte_numeric", 
                    {
                        "_attribute": "paid_amount",
                        "value": str(max_allowed_paid)
                    }
                )
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    validation_errors,
                    Error.VALIDATION_ERROR
                )
    # Calculate new outstanding amount
    new_outstanding = (outstanding_amount - paid_amount).quantize(Decimal('.01'))
    data["outstanding_amount"] = str(new_outstanding)

    # Auto-generate receipt number with safe handling
    # Format: RCPT-YYYYMMDD-XXXX (e.g., RCPT-20241214-1234)
    def generate_receipt_number(max_attempts=None):
        """Generate a unique receipt number with format: RCPT-YYYYMMDD-XXXX"""
        import random
        import time
        
        # Use configuration constants
        max_attempts = max_attempts or RECEIPT_NUMBER_CONFIG["MAX_ATTEMPTS"]
        prefix = RECEIPT_NUMBER_CONFIG["PREFIX"]
        random_min = RECEIPT_NUMBER_CONFIG["RANDOM_MIN"]
        random_max = RECEIPT_NUMBER_CONFIG["RANDOM_MAX"]
        retry_delay = RECEIPT_NUMBER_CONFIG["RETRY_DELAY"]
        
        attempt_count = 0
        
        while attempt_count < max_attempts:
            try:
                # Get current date
                current_date = datetime.now().strftime("%Y%m%d")
                
                # Generate a random 4-digit number
                random_suffix = str(random.randint(random_min, random_max))
                
                # Create receipt number
                receipt_number = f"{prefix}-{current_date}-{random_suffix}"
                
                # Check if this receipt number already exists
                try:
                    existing_payment = QueryBuilderService("crmf_payments").where("receipt_number", receipt_number).first()
                    
                    # If exists, try again with different random number
                    if existing_payment:
                        attempt_count += 1
                        time.sleep(retry_delay)  # Small delay to ensure different random seed
                        continue
                    
                    # If we reach here, the receipt number is unique
                    return receipt_number
                    
                except Exception as db_error:
                    print(f"Warning: Database error checking receipt number uniqueness: {db_error}")
                    # If we can't verify uniqueness, use the generated number
                    # but add a timestamp suffix to minimize collision risk
                    timestamp_suffix = datetime.now().strftime("%H%M%S")
                    safe_receipt_number = f"{receipt_number}-{timestamp_suffix}"
                    print(f"Using safe receipt number with timestamp: {safe_receipt_number}")
                    return safe_receipt_number
                    
            except Exception as e:
                print(f"Error in receipt number generation attempt {attempt_count + 1}: {e}")
                attempt_count += 1
                time.sleep(retry_delay)  # Small delay before retry
        
        # If we've exhausted all attempts, use a timestamp-based fallback
        print(f"Warning: Exhausted {max_attempts} attempts to generate unique receipt number")
        fallback_receipt = f"{prefix}-{datetime.now().strftime('%Y%m%d%H%M%S')}-FALLBACK"
        print(f"Using fallback receipt number: {fallback_receipt}")
        return fallback_receipt
    
    # Generate and assign receipt number with comprehensive error handling
    try:
        data["receipt_number"] = generate_receipt_number()
        print(f"Successfully generated receipt number: {data['receipt_number']}")
        
        # Validate the generated receipt number format
        if not data["receipt_number"].startswith("RCPT-"):
            raise ValueError("Generated receipt number doesn't have expected format")
            
    except Exception as e:
        print(f"Critical error in receipt number generation: {e}")
        print("Stack trace:", e.__traceback__)
        
        # Emergency fallback: use timestamp-based receipt number
        try:
            emergency_receipt = f"{RECEIPT_NUMBER_CONFIG['PREFIX']}-{datetime.now().strftime('%Y%m%d%H%M%S')}-EMERGENCY"
            data["receipt_number"] = emergency_receipt
            print(f"Using emergency fallback receipt number: {emergency_receipt}")
        except Exception as fallback_error:
            print(f"Even fallback receipt number generation failed: {fallback_error}")
            # Last resort: use a simple timestamp
            try:
                data["receipt_number"] = f"{RECEIPT_NUMBER_CONFIG['PREFIX']}-{int(time.time())}"
                print(f"Using last resort receipt number: {data['receipt_number']}")
            except Exception as last_resort_error:
                print(f"CRITICAL: All receipt number generation methods failed: {last_resort_error}")
                # Absolute last resort: use a hardcoded fallback
                data["receipt_number"] = f"{RECEIPT_NUMBER_CONFIG['PREFIX']}-FALLBACK-{int(time.time())}"
                print(f"Using absolute last resort receipt number: {data['receipt_number']}")

    # If reference_id is passed, resolve customer_payment_id and reject if already linked (before creating entity)
    if data.get("reference_id") is not None and data.get("reference_id") != "":
        cus_payment = (
            QueryBuilderService("cus_payments")
            .select("id")
            .where("reference_id", data["reference_id"])
            .first()
        )
        if cus_payment:
            cus_payment_id = cus_payment.get("id")
            # customer_payment_id is unique on crmf_payments; prevent duplicate link
            existing = (
                QueryBuilderService("crmf_payments")
                .where("customer_payment_id", cus_payment_id)
                .first()
            )
            if existing:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {
                        "reference_id": [{
                            "error_type": "duplicate",
                            "tokens": {"_attribute": "reference_id"}
                        }]
                    },
                    Error.VALIDATION_ERROR,
                )
            data["customer_payment_id"] = cus_payment_id

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

    # Insert payment with additional safety checks
    print(f"Inserting payment with receipt number: {data['receipt_number']}")
    
    # Final validation before insertion
    if not data.get("receipt_number"):
        print("ERROR: Receipt number is missing, cannot proceed with payment creation")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            {"error": "Receipt number generation failed"}, 
            "receipt_number_generation_failed"
        )
    
            # Validate receipt number format
        is_valid, validation_message = validate_receipt_number_format(data["receipt_number"])
        if not is_valid:
            print(f"WARNING: Receipt number validation failed: {validation_message}")
            print(f"Receipt number: {data['receipt_number']}")
            print(f"Expected format: {RECEIPT_NUMBER_CONFIG['FORMAT']}")
        else:
            print(f"Receipt number validation: {validation_message}")
    
    try:
        created = QueryBuilderService("crmf_payments").insert(data)
        print(f"Payment inserted successfully with ID: {created.get('id', 'Unknown')}")
    except Exception as insert_error:
        print(f"ERROR: Failed to insert payment: {insert_error}")
        print(f"Payment data: {data}")
        
        # Try to clean up the entity if payment insertion fails
        try:
            if data.get("entity_id"):
                print(f"Cleaning up entity {data['entity_id']} due to payment insertion failure")
                # You might want to add entity cleanup logic here
        except Exception as cleanup_error:
            print(f"ERROR: Failed to cleanup entity: {cleanup_error}")
        
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            {"error": f"Payment insertion failed: {str(insert_error)}"}, 
            "payment_insertion_failed"
        )

    issued_policy_id = None
    issued_policy_id = invoice.get("issued_policyId")

    try:
        confirmation_name = data.get("confirmation_payment_receipt_name", "")
        customer_payment_id = data.get("customer_payment_id", "")

        risk_type_id = (
            QueryBuilderService("crmf_invoices")
            .select("crmp_policy_base.risk_type_id", "crmp_issued_policies.id")
            .leftJoin("crmp_issued_policies", "crmp_issued_policies.id", "crmf_invoices.issued_policy_id")
            .leftJoin("crmp_policy_base", "crmp_policy_base.id", "crmp_issued_policies.policy_base_id")
            .where("crmf_invoices.id", data["invoice_id"])
            .first()
        )

        if not risk_type_id or not risk_type_id.get("risk_type_id"):
            risk_type_id = (
                QueryBuilderService("crmp_policy_risk_config")
                .leftJoin("crm_risk_submissions", "crm_risk_submissions.id", "crmp_policy_risk_config.risk_submission_id")
                .select("crm_risk_submissions.risk_type_id")
                .first()
            )

        # Resolve risk type title safely using the found risk_type_id
        risk_type_title = ""
        if risk_type_id and risk_type_id.get("risk_type_id"):
            risk_type_row = (
                QueryBuilderService("crm_opportunity_types")
                .select("crm_opportunity_types.title")
                .where("crm_opportunity_types.id", risk_type_id.get("risk_type_id"))
                .first()
            )
            risk_type_title = risk_type_row.get("title", "") if risk_type_row else ""

        if not confirmation_name and not customer_payment_id:
            # Send "Policy Payment Created"
            NotificationService.generate_notification(
                type_code="policy",
                title="Policy Payment Created",
                meta_data={ "policy_payment": "created" , "id" : issued_policy_id},
                message=f"{risk_type_title} policy payment created with ID {issued_policy_id}. Paid amount : {data['paid_amount']}",
                customer_id=invoice.get("customer_id",""),
                user_id=request.user.id if request.user.is_authenticated else None
            )
        else:
            # Send "Policy Payment Confirmed"
            NotificationService.generate_notification(
                type_code="policy",
                title="Policy Payment Confirmed",
                meta_data={ "policy_payment": "created" , "id" : issued_policy_id},
                message=f"Your {risk_type_title} policy payment confirmed for {issued_policy_id}. Paid amount: {data['paid_amount']}. Invoice no: {invoice['invoice_number']}",
                customer_id=invoice.get("customer_id",""),
                user_id=request.user.id if request.user.is_authenticated else None
            )
    except Exception as notify_exc:
        print(f"NotificationService error: {notify_exc}")

    # Update invoice totals
    update_invoice_payment_details(data["invoice_id"], data["paid_amount"])
    
    # Update invoice status based on payment amounts
    update_invoice_status_after_payment(data["invoice_id"])

    # Always recalculate commissions on every payment
    # Get updated invoice with total paid_amount after payment update
    updated_invoice = QueryBuilderService("crmf_invoices").where("id", data["invoice_id"]).first()
    if not updated_invoice:
        print(f"WARNING: Could not fetch updated invoice {data['invoice_id']} for commission calculation")
    else:
        total_paid_amount = Decimal(str(updated_invoice.get("paid_amount", "0.00")))
        invoice_amount = Decimal(str(updated_invoice.get("invoice_amount", "0.00")))
        transaction_type_id = updated_invoice.get("transaction_type_id")
        
        print(f"DEBUG: Recalculating commissions for payment:")
        print(f"  - Invoice ID: {data['invoice_id']}")
        print(f"  - Invoice Amount: {invoice_amount}")
        print(f"  - Total Paid Amount: {total_paid_amount}")
        print(f"  - Transaction Type ID: {transaction_type_id}")
        print(f"  - Payment Proportion: {(total_paid_amount / invoice_amount * 100) if invoice_amount > 0 else 0:.2f}%")
        
        # IMPORTANT: Commission calculations for refund and cancellation types (transaction_type_id 4, 5)
        # are handled ONLY in create_endorsement, NOT in create_payment
        # All commission calculations including deductible storage must happen when endorsement is created
        # When refund/cancellation invoices are paid, NO commission calculations should occur here
        if transaction_type_id in [4, 5]:  # Refund (4) or Cancellation (5)
            print(f"DEBUG: Skipping commission calculation for refund/cancellation invoice (transaction_type_id: {transaction_type_id})")
            print(f"DEBUG: All commission calculations for refund/cancellation must happen in create_endorsement only, not in create_payment")
        else:
            # For regular invoices, update brokerage commission revenue_realized if exists
            brokerage_commission = QueryBuilderService("crmf_brokerage_commission").where("invoice_id", data["invoice_id"]).first()
            if brokerage_commission and "id" in brokerage_commission:
                print(f"Updating brokerage commission revenue_realized: commission_id={brokerage_commission['id']}, invoice_id={data['invoice_id']}, total_paid={total_paid_amount}")
                update_revenue_realized('crmf_brokerage_commission', brokerage_commission["id"], invoice_id=data["invoice_id"], paid_amount=total_paid_amount)
                
                # Update brokerage commission status (only brokerage, not agent commission)
                from envoy_bu_policy_api.finance.controllers.utils.commission_status_utils import update_brokerage_commission_status
                update_brokerage_commission_status(brokerage_commission["id"])
                
                # IMPORTANT: Update agent commission revenue_realized ONLY (NOT status)
                # Agent commission status should ONLY be updated at api/agent-commission-payments endpoint
                # This ensures status reflects actual payments made to agents, not just customer payments
                calculation_mode = get_commission_calculation_mode()
                print(f"Updating agent commission revenue_realized: brokerage_commission_id={brokerage_commission['id']}, invoice_id={data['invoice_id']}, total_paid={total_paid_amount}, calculation_mode={calculation_mode}")
                print(f"IMPORTANT: Agent commission status will NOT be updated here - status only updates at api/agent-commission-payments endpoint")
                
                # ========== DEBUG: Get current agent commission statuses BEFORE update ==========
                print(f"\n{'='*80}")
                print(f"DEBUG PAYMENT API: Getting agent commission statuses BEFORE update")
                print(f"{'='*80}")
                agent_commissions_before = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", brokerage_commission["id"]).get()
                statuses_before = {}
                for ac in agent_commissions_before:
                    if "id" in ac:
                        ac_id = ac["id"]
                        status_before = ac.get("status")
                        revenue_recognized = ac.get("revenue_recognized", 0)
                        revenue_realized_before = ac.get("revenue_realized", 0)
                        statuses_before[ac_id] = status_before
                        print(f"DEBUG: Agent Commission ID {ac_id}:")
                        print(f"  - Status BEFORE: '{status_before}'")
                        print(f"  - Revenue Recognized: {revenue_recognized}")
                        print(f"  - Revenue Realized BEFORE: {revenue_realized_before}")
                print(f"{'='*80}\n")
                
                # Update revenue_realized (this function explicitly does NOT update status)
                print(f"DEBUG PAYMENT API: Calling update_agent_commission_revenue_realized_for_brokerage_payment")
                print(f"  - Brokerage Commission ID: {brokerage_commission['id']}")
                print(f"  - Invoice ID: {data['invoice_id']}")
                print(f"  - Total Paid: {total_paid_amount}")
                update_agent_commission_revenue_realized_for_brokerage_payment(brokerage_commission["id"], data["invoice_id"], total_paid_amount, calculation_mode)
                
                # ========== DEBUG: Verify that agent commission status was NOT changed ==========
                print(f"\n{'='*80}")
                print(f"DEBUG PAYMENT API: Verifying agent commission statuses AFTER update")
                print(f"{'='*80}")
                agent_commissions_after = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", brokerage_commission["id"]).get()
                for ac_after in agent_commissions_after:
                    ac_id = ac_after.get("id")
                    status_before = statuses_before.get(ac_id)
                    status_after = ac_after.get("status")
                    revenue_realized_after = ac_after.get("revenue_realized", 0)
                    
                    print(f"DEBUG: Agent Commission ID {ac_id}:")
                    print(f"  - Status BEFORE update: '{status_before}'")
                    print(f"  - Status AFTER update: '{status_after}'")
                    print(f"  - Revenue Realized AFTER: {revenue_realized_after}")
                    
                    if status_before and status_after and status_before != status_after:
                        print(f"  - ❌ ERROR: Status CHANGED from '{status_before}' to '{status_after}' - RESTORING!")
                        # Restore original status
                        restore_result = QueryBuilderService("crmf_agent_commission").where("id", ac_id).update({"status": status_before})
                        print(f"  - Restore result: {restore_result}")
                        
                        # Verify restoration
                        ac_restored = QueryBuilderService("crmf_agent_commission").where("id", ac_id).first()
                        status_restored = ac_restored.get("status") if ac_restored else None
                        print(f"  - Status after restore: '{status_restored}'")
                        if status_restored == status_before:
                            print(f"  - ✅ Status successfully restored to '{status_before}'")
                        else:
                            print(f"  - ❌ FAILED to restore status! Still '{status_restored}'")
                    elif status_before:
                        print(f"  - ✅ Status unchanged: '{status_before}'")
                    else:
                        print(f"  - ⚠️  Could not verify status (status_before was None)")
                print(f"{'='*80}\n")
            else:
                print(f"WARNING: No brokerage commission found for invoice_id={data['invoice_id']}. Commissions may not have been created during invoice generation.")

    # Update policy paid_amount if this is a policy-related invoice
    if invoice.get("id"):
        current_policy = (
            QueryBuilderService("crmf_invoices")
            .select("paid_amount")
            .where("id", invoice.get("id"))
            .first()
        )
        current_paid = Decimal(str(current_policy.get("paid_amount", "0.00")))
        new_paid = (current_paid + paid_amount).quantize(Decimal('.01'))

        # Update policy paid amount
        QueryBuilderService("crmf_invoices")\
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
    print(f"DEBUG: Checking document data in payment creation")
    print(f"DEBUG: upload_receipt in data: {'upload_receipt' in data}")
    print(f"DEBUG: payment_receipt_url in data: {'payment_receipt_url' in data}")
    print(f"DEBUG: payment_receipt_name in data: {'payment_receipt_name' in data}")
    print(f"DEBUG: payment_receipt_type in data: {'payment_receipt_type' in data}")
    
    # Check for document data in multiple possible formats
    if "upload_receipt" in data and data["upload_receipt"]:
        receipt = data["upload_receipt"]
        print(f"DEBUG: Using upload_receipt: {receipt}")
    elif "payment_receipt_url" in data and data["payment_receipt_url"]:
        receipt = {
            "doc": data["payment_receipt_url"],
            "name": data.get("payment_receipt_name", ""),
            "type": data.get("payment_receipt_type", "")
        }
        print(f"DEBUG: Using payment_receipt_url: {receipt}")
    elif data.get("payment_receipt_name") or data.get("payment_receipt_url"):
        # Even if payment_receipt_url is empty, if we have a name, create the document record
        receipt = {
            "doc": data.get("payment_receipt_url", ""),
            "name": data.get("payment_receipt_name", ""),
            "type": data.get("payment_receipt_type", "")
        }
        print(f"DEBUG: Using payment receipt data (even with empty URL): {receipt}")
    else:
        print(f"DEBUG: No receipt document found in data")

    if receipt and (receipt.get("doc") or receipt.get("name")):
        print(f"DEBUG: Calling handle_entity_docs with entity_id={entity_id}, receipt={receipt}")
        result = handle_entity_docs(entity_id=entity_id, docs=[receipt])
        print(f"DEBUG: handle_entity_docs result: {result}")
    else:
        print(f"DEBUG: No receipt document to store - receipt={receipt}")

    return ResponseService.response("SUCCESS", created, "default_create_success_msg")


@csrf_exempt
@api_view(["GET","PUT"])
def payment_detail(request, payment_id):

    if request.method == "GET" :
        return get_payment_detail(request, payment_id)
    if request.method == "PUT" :
        return update_payment_details(request, payment_id)


def update_payment_details(request, payment_id):
    data = json.loads(request.body or "{}")

    # Fetch payment to verify existence
    payment = (
        QueryBuilderService('crmf_payments')
        .where('id', payment_id)
        .first()
    )

    if not payment:
        return ResponseService.response("NOT_FOUND", None, "DATA_NOT_FOUND")

    # Validation rules
    rules = {
        "confirmation_payment_receipt_name": "required",
        "confirmation_payment_receipt_url": "nullable",
        "confirmation_payment_receipt_type": "nullable",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    # Perform update
    update_result = (
        QueryBuilderService('crmf_payments')
        .where('id', payment_id)
        .update(data)
    )

    if update_result == 0:
        return ResponseService.response("UPDATE_FAILED", None, "FAILED_TO_UPDATE")

    # Optionally fetch the updated record again
    updated_payment = (
        QueryBuilderService('crmf_payments')
        .where('id', payment_id)
        .first()
    )
    
    # Update invoice status if needed (this function only updates receipt details, not amounts)
    # but we call it to ensure status is current
    if updated_payment and updated_payment.get("invoice_id"):
        update_invoice_status_after_payment(updated_payment["invoice_id"])
        
        # Send payment confirmation notification when insurer confirms payment
        try:
            from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
            
            # Get payment and policy details for notification
            payment_details = (
                QueryBuilderService("crmf_payments as p")
                .leftJoin("crmf_invoices as inv", "inv.id", "p.invoice_id")
                .leftJoin("crmp_issued_policies as ip", "ip.id", "inv.issued_policy_id")
                .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
                .leftJoin("core_customers as c", "c.id", "pb.customer_id")
                .leftJoin("core_vendor_products as vp", "vp.id", "pb.product_id")
                .select(
                    "p.paid_amount",
                    "p.confirmation_payment_receipt_url",
                    "p.confirmation_payment_receipt_name",
                    "ip.brokerage_policy_id",
                    "c.id as customer_id",
                    "c.name as customer_name",
                    "vp.name as product_name"
                )
                .where("p.id", payment_id)
                .first()
            )
            
            if payment_details and payment_details.get("customer_id"):
                # Format confirmation receipt URL
                confirmation_receipt_url = payment_details.get("confirmation_payment_receipt_url")
                confirmation_receipt_name = payment_details.get("confirmation_payment_receipt_name")
                
                # Format detailed message
                detailed_message = NotificationService.format_payment_confirmation_message(
                    policy_number=payment_details.get("brokerage_policy_id", "N/A"),
                    product_name=payment_details.get("product_name", "Unknown Product"),
                    payment_amount=str(payment_details.get("paid_amount", "0.00")),
                    confirmation_receipt_url=confirmation_receipt_url
                )
                
                # Prepare payment data for metadata
                payment_data = {
                    "payment_id": payment_id,
                    "brokerage_policy_id": payment_details.get("brokerage_policy_id"),
                    "payment_amount": str(payment_details.get("paid_amount", "0.00")),
                    "product_name": payment_details.get("product_name"),
                    "confirmation_receipt_url": confirmation_receipt_url,
                    "confirmation_receipt_name": confirmation_receipt_name
                }
                
                # Prepare links for metadata
                links = []
                if confirmation_receipt_url:
                    links.append({"title": "Confirmation Receipt", "url": confirmation_receipt_url})
                
                # Generate detailed notification
                NotificationService.generate_detailed_notification(
                    type_code="payment_confirmation",
                    title="Payment Confirmed by Insurer",
                    detailed_message=detailed_message,
                    customer_id=payment_details.get("customer_id"),
                    user_id=request.user.id if request.user.is_authenticated else None,
                    payment_data=payment_data,
                    links=links
                )
                
                print(f"✅ Payment confirmation notification sent to customer {payment_details.get('customer_id')}")
            else:
                print(f"⚠️ Could not send payment confirmation notification - missing payment details or customer_id")
                
        except Exception as notify_e:
            print(f"⚠️ Error sending payment confirmation notification: {str(notify_e)}")
            # Don't fail the entire operation for notification errors

    return ResponseService.response("SUCCESS", updated_payment, "default_update_success_msg")



    
    

def get_payment_detail(request, payment_id):
    action_type = "VIEW"
    action = ActionService.getAction("Payment", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    columns = [
        "crmf_payments.*",
        "remarks.notes as remarks",
        "docs.name as doc_name",
        "docs.doc as doc",
        "docs.type as doc_type",
        "core_entities.created_at as payment_created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_logo",
        "crmf_invoices.invoice_number as invoice_code",
        "crmf_invoices.invoice_amount as total_amount",
        "crmf_invoices.paid_amount as total_paid_amount",
        "crmf_invoices.outstanding_amount as current_outstanding",
        "crmf_invoices.last_paid_date as last_payment_date",
        "crmf_invoices.invoice_date",
        "crmf_invoices.due_date",
        "crmf_invoices.invoice_type",
        "crmf_transaction_types.name as transaction_type_name",
        "crmf_transaction_types.code as transaction_type_code",
        "crmp_endorsements_details.endorsement_id as endorsement_code",
        "crmp_issued_policies.brokerage_policy_id as policy_number",
        "crmp_issued_policies.start_date as policy_start_date",
        "crmp_issued_policies.end_date as policy_end_date",
        "crmp_issued_policies.sum_insured as insured_amount",
        "crmp_issued_policies.premium_amount as premium_amount",
        "crmp_issued_policies.remarks AS insurer_notes",
        "products.id AS product_id",
        "risk_type.title AS risk_type_name",
        "risk_type.id AS risk_type_id",
        "insurer_sp.name AS insurer_info_full_name",
        "insurer_sp.id AS insurer_id",
        "insurer_sp.logo AS insurer_info_logo",
        "customers.name as customer_name",
        "customers.logo as customer_logo",
        "customers.id as customer_id",
        "products.name as product",
        "request_policy.policy_request_id as policy_request_code",
        "request_policy.id as policy_request_id",
        "request_status.name AS policy_request_status",
        "request_status.color AS policy_request_status_color",
        "policy_base.quotation_document as quotation_document",
        "policy_base.quotation_document_name as quotation_document_name",
        "request_by.display_name AS requested_by",
        "request_by.picture AS requested_by_logo",
        "request_type.name AS request_type",
        "request_type.id AS request_type_id",
        "request_customer_contact.email AS customer_email",
        "request_customer_contact.address AS customer_address",
        "request_customer_contact.primary_contact AS customer_primary_contact",
        "coverage_type.name AS coverage_type",
        "coverage_type.id AS coverage_type_id",
        "payment_plan.name AS payment_plan",
        "payment_plan.id AS payment_plan_id",
        "updated_by.display_name AS updated_by",
        "updated_by.picture AS updated_by_logo",
        "product_groups.name AS product_group",
        "product_groups.id AS product_group_id"
    ]

    payment = (
        QueryBuilderService("crmf_payments")
        .select(*columns)
        .leftJoin("crmf_invoices", "crmf_invoices.id", "crmf_payments.invoice_id")
        .leftJoin(
            "crmf_transaction_types",
            "crmf_transaction_types.id",
            "crmf_invoices.transaction_type_id"
        )
        .leftJoin(
            "crmp_endorsements_details",
            "crmp_endorsements_details.id",
            "crmf_invoices.endorsement_id"
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id"
        )
        .leftJoin("core_entities", "core_entities.id", "crmf_payments.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
        .leftJoin(
            "core_entity_notes as remarks",
            "remarks.entity_id",
            "crmf_payments.entity_id"
        )
        .leftJoin(
            "core_entity_docs as docs",
            "docs.entity_id",
            "crmf_payments.entity_id"
        )
        .leftJoin(
            "crmp_policy_base as policy_base",
            "policy_base.id",
            "crmp_issued_policies.policy_base_id",
        )
        .leftJoin(
            "crm_opportunity_types as risk_type",
            "risk_type.id",
            "policy_base.risk_type_id",
        )
        .leftJoin(
            "core_service_providers as insurer_sp",
            "insurer_sp.id",
            "policy_base.insurer_id",
        )
        .leftJoin(
            "core_customers as customers", "customers.id", "policy_base.customer_id"
        )
        .leftJoin("core_vendor_products as products", "products.id", "policy_base.product_id")
        .leftJoin("core_product_groups as product_groups", "product_groups.id", "policy_base.product_group_id")

        .leftJoin(
            "core_users as request_by", "request_by.id", "policy_base.request_by_id"
        )
        .leftJoin(
            "crmp_request_policies as request_policy",
            "request_policy.id",
            "crmp_issued_policies.policy_request_id",
        )
        .leftJoin(
            "core_status as request_status",
            "request_status.id",
            "request_policy.status_id",
        )
        .leftJoin(
            "crmp_request_types as request_type",
            "request_type.id",
            "policy_base.request_type_id",
        )
        .leftJoin(
            "core_contacts as request_customer_contact",
            "request_customer_contact.id",
            "customers.primary_contact_id",
        )
        .leftJoin(
            "crmp_coverage_types as coverage_type",
            "coverage_type.id",
            "policy_base.coverage_type_id",
        )
        .leftJoin(
            "crmp_payment_plans as payment_plan",
            "payment_plan.id",
            "policy_base.payment_mode_id",
        )
        .leftJoin("core_users as updated_by", "updated_by.id", "core_entities.updated_by_id")

        .where("crmf_payments.id", payment_id)
        .first()
    )

    if not payment:
        return ResponseService.response("ERROR", None, Error.DATA_NOT_FOUND)

    # Get product group products separately if product_group_id exists
    product_group_id = payment.get("product_group_id")
    if product_group_id:
        # Fetch product group products separately
        product_group_products_query = (
            QueryBuilderService("core_product_group_products")
            .select(
                "core_product_group_products.id",
                "core_product_group_products.product_id",
                "core_product_vendor_products.vendor_product_id",
                "core_vendor_products.name as vendor_product_name"
            )
            .leftJoin("core_product_vendor_products", "core_product_vendor_products.product_id", "core_product_group_products.product_id")
            .leftJoin("core_vendor_products", "core_vendor_products.id", "core_product_vendor_products.vendor_product_id")
            .where("core_product_group_products.product_group_id", product_group_id)
            .get()
        )
        payment["product_group_products"] = product_group_products_query
    else:
        payment["product_group_products"] = []
    # Remove the raw JSON string
    payment.pop("product_group_products_json", None)

    return ResponseService.response("SUCCESS", payment, Message.DATA_FETCHED)


def get_columns():
    return [
        "crmf_agent_commission_payments.id",
        "crmf_agent_commission_payments.payment_amount",
        # "crmf_agent_commission_payments.payment_type",
        "crmf_agent_commission_payments.payment_date",
        # "crmf_agent_commission_payments.payment_notes",
        "agent.display_name as agent_name",
        "agent.email as agent_email",
        "agent.picture as agent_picture",
        "core_entities.created_at",
        "created_by.display_name as created_by",
        "created_by.picture as created_by_logo"
    ]


def build_base_query():
    return (
        QueryBuilderService("crmf_agent_commission_payments")
        .select(*get_columns())
        .leftJoin("crmf_agent_commission as commission","commission.id","crmf_agent_commission_payments.agent_commission_id")
        .leftJoin("core_users as agent", "agent.id", "commission.agent_id")
        .leftJoin("core_entities", "core_entities.id", "crmf_agent_commission_payments.entity_id")
        .leftJoin("core_users as created_by", "created_by.id", "core_entities.created_by_id")
    )


def get_allowed_filters():
    return [
        "crmf_agent_commission_payments.payment_type",
        "crmf_agent_commission_payments.payment_date",
        "agent.display_name",
        "agent.email"
    ]


def get_sort_columns():
    return [
        "crmf_agent_commission_payments.payment_date",
        "crmf_agent_commission_payments.payment_amount",
        "agent.display_name",
        "core_entities.created_at"
    ]


def get_search_columns():
    return [
        "agent.display_name",
        "agent.email",
    ]


@csrf_exempt
@api_view(['GET'])
def get_payments(request):
    """Get all payments with filtering and pagination"""
    if not AuthService.hasAuthority(request, ActionService.getAction("finance", "view_payments")):
        return ResponseService.response("ERROR", None, Error.UNAUTHORIZED)

    # Get pagination parameters manually
    filter_json = request.GET.get("filter", "{}")
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmf_agent_commission_payments.payment_date")
    sort_dir = request.GET.get("sort_dir", "desc")
    
    query = build_base_query()
    
    data = query.apply_conditions(
        filter_json,
        get_allowed_filters(),
        search_string,
        get_search_columns()
    ).paginate(
        page,
        limit,
        get_sort_columns(),
        sort_by,
        sort_dir
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@csrf_exempt
@api_view(['GET'])
def get_agent_payments(request, agent_id):
    """Get payments for a specific agent"""
    if not AuthService.hasAuthority(request, ActionService.getAction("finance", "view_payments")):
        return ResponseService.response("ERROR", None, Error.UNAUTHORIZED)

    # Get pagination parameters manually
    filter_json = request.GET.get("filter", "{}")
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmf_agent_commission_payments.payment_date")
    sort_dir = request.GET.get("sort_dir", "desc")
    
    query = build_base_query().where("agent.id", agent_id)
    
    data = query.apply_conditions(
        filter_json,
        get_allowed_filters(),
        search_string,
        get_search_columns()
    ).paginate(
        page,
        limit,
        get_sort_columns(),
        sort_by,
        sort_dir
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@csrf_exempt
@api_view(['GET', 'POST'])
def get_multiple_agent_payments(request):
    """GET: Fetch payments for multiple agents. POST: Process eligible payments for multiple agents and update statuses."""
    if not AuthService.hasAuthority(request, ActionService.getAction("finance", "view_payments")):
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, Error.UNAUTHORIZED)

    try:
        if request.method == "POST":
            data = json.loads(request.body)
            agent_ids = data.get('agent_ids', [])
        else:
            agent_ids = request.GET.getlist('agent_ids')
            agent_ids = [int(aid) for aid in agent_ids if str(aid).isdigit()]

        if not agent_ids:
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Agent IDs are required")

        # GET: Just fetch payments
        if request.method == "GET":
            filter_json = request.GET.get("filter", "{}")
            search_string = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            sort_by = request.GET.get("sort_by", "crmf_agent_commission_payments.payment_date")
            sort_dir = request.GET.get("sort_dir", "desc")
            query = build_base_query().whereIn("agent.id", agent_ids)
            data = query.apply_conditions(
                filter_json,
                get_allowed_filters(),
                search_string,
                get_search_columns()
            ).paginate(
                page,
                limit,
                get_sort_columns(),
                sort_by,
                sort_dir
            )
            return ResponseService.response("SUCCESS", {"payments": data}, Message.DATA_FETCHED)

        # POST: Process eligible payments for each agent
        payment_summaries = {}
        for agent_id in agent_ids:
            payment_summaries[agent_id] = pay_all_eligible_for_agent(agent_id, request)
        return ResponseService.response("SUCCESS", {"payment_summaries": payment_summaries}, Message.DATA_FETCHED)

    except json.JSONDecodeError:
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Invalid JSON format")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, str(e))


def pay_all_eligible_for_agent(agent_id, request):
    from django.db import transaction
    results = {"commissions_paid": [], "incentives_paid": []}

    # 1. Find eligible commissions (status == 'issued' or 'overdue')
    eligible_commissions = QueryBuilderService("crmf_agent_commission") \
        .select("id", "revenue_recognized", "revenue_realized", "commission_deductible") \
        .where("agent_id", agent_id) \
        .whereIn("status", ["issued", "overdue"]) \
        .get()

    # 2. Find eligible incentives (status == 'pending' or 'approved')
    eligible_incentives = QueryBuilderService("crmf_incentives") \
        .select("id", "incentive_amount") \
        .where("agent_id", agent_id) \
        .whereIn("status", ["pending", "approved"]) \
        .get()

    # 3. Pay commissions
    for commission in eligible_commissions:
        # Outstanding = recognized - realized - deductible (if negative, set to 0)
        commission_deductible = float(commission.get("commission_deductible", 0) or 0)
        outstanding = max(0, float(commission["revenue_recognized"]) - float(commission["revenue_realized"]) - commission_deductible)
        if outstanding > 0:
            with transaction.atomic():
                entity_id = handle_entity({
                    "type": "commission_payment",
                    "approvel_status": True,
                    "description": f"Auto payment for commission {commission['id']}"
                }, user=request.user if hasattr(request, 'user') else None)
                payment_data = {
                    "agent_commission_id": commission["id"],
                    "incentive_id": None,
                    "payment_amount": outstanding,
                    "payment_type": "commission",
                    "entity_id": entity_id,
                    "payment_date": date.today(),
                }
                QueryBuilderService("crmf_agent_commission_payments").insert(payment_data)
                
                # Update the paid_amount field in the agent commission record
                current_commission = QueryBuilderService("crmf_agent_commission").where("id", commission["id"]).first()
                if current_commission:
                    current_paid = Decimal(str(current_commission.get("paid_amount", "0.00")))
                    new_paid = current_paid + Decimal(str(outstanding))
                    QueryBuilderService("crmf_agent_commission").where("id", commission["id"]).update({
                        "paid_amount": str(new_paid),
                        "status": "paid"
                    })
                    print(f"Updated agent commission {commission['id']} paid_amount from {current_paid} to {new_paid}")
                else:
                    # Fallback: just update status
                    QueryBuilderService("crmf_agent_commission").where("id", commission["id"]).update({"status": "paid"})
                results["commissions_paid"].append(commission["id"])

    # 4. Pay incentives
    for incentive in eligible_incentives:
        with transaction.atomic():
            entity_id = handle_entity({
                "type": "incentive_payment",
                "approvel_status": True,
                "description": f"Auto payment for incentive {incentive['id']}"
            }, user=request.user if hasattr(request, 'user') else None)
            payment_data = {
                "agent_commission_id": None,
                "incentive_id": incentive["id"],
                "payment_amount": incentive["incentive_amount"],
                "payment_type": "incentive",
                "entity_id": entity_id,
                "payment_date": date.today(),
            }
            QueryBuilderService("crmf_agent_commission_payments").insert(payment_data)
            Incentive.objects.filter(id=incentive["id"]).update(status="paid")
            results["incentives_paid"].append(incentive["id"])

    return results


