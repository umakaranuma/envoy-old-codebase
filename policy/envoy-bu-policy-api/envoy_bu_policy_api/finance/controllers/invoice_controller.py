from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from .utils.invoice_utils import update_invoice_payment_details

@csrf_exempt
@api_view(["GET"])
def invoice_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("Invoice", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_all_invoices(request)

def get_all_invoices(request):
    columns = [
        "crmf_invoices.*",
        "core_entities.created_at as created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_logo",
        "crmf_transaction_types.name as transaction_type_name",
        "crmf_transaction_types.code as transaction_type_code",
        "crmp_endorsements_details.endorsement_id as endorsement_code",
        "crmp_issued_policies.brokerage_policy_id as policy_number",
        "crmp_issued_policies.start_date as policy_start_date",
        "crmp_issued_policies.end_date as policy_end_date",
        "crmp_issued_policies.sum_insured as insured_amount",
        "crmp_issued_policies.premium_amount as premium_amount",
        "crmp_issued_policies.remarks AS insurer_notes",
        "crmp_issued_policies.insurer_policy_id as insurer_policy_id",
        "crmp_issued_policies.insurer_invoice_id as insurer_invoice_number",
        "crmp_issued_policies.brokerage_policy_id as brokerage_policy_id",
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
        "status.name AS invoice_status_name",
        "status.color AS invoice_status_color",
        "product_groups.name AS product_group",
        "product_groups.id AS product_group_id",

    ]

    query = (
        QueryBuilderService("crmf_invoices")
        .select(*columns)
        .leftJoin(
            "crmf_transaction_types",
            "crmf_transaction_types.id",
            "crmf_invoices.transaction_type_id"
        )
        .leftJoin(
            "core_status as status",
            "status.id",
            "crmf_invoices.status_id",
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
        .leftJoin("core_entities", "core_entities.id", "crmf_invoices.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
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

        .whereNotIn("crmf_invoices.invoice_type", ["service_render"])
    )

    # Get filters and search parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "crmf_invoices.id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    # Handle type parameter (invoice status filter)
    type_filter = request.GET.get("type")
    if type_filter:
        # Add status name filter to filter_json
        filter_json["status.name"] = {
            "o": "=",
            "v": type_filter
        }

    allowed_filters = [
        "crmf_invoices.invoice_number",
        "crmf_invoices.transaction_type_id",
        "crmf_invoices.invoice_date",
        "crmp_issued_policies.brokerage_policy_id",
        "status.name"  # Add status name to allowed filters
    ]
    search_columns = [
        "crmf_invoices.invoice_number",
        "crmp_issued_policies.brokerage_policy_id",
        "crmp_endorsements_details.endorsement_id"
    ]
    sort_columns = ["core_entities.created_at", "crmf_invoices.id", "crmf_invoices.invoice_date", "crmf_invoices.invoice_number"]

    # Convert filter_json back to JSON string for apply_conditions
    filter_json_str = json.dumps(filter_json)

    # Apply filters and search
    data = query.apply_conditions(
        filter_json_str, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

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
def invoice_detail(request, invoice_id):
    action_type = "VIEW"
    action = ActionService.getAction("Invoice", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    columns = [
        "crmf_invoices.*",
        "core_entities.created_at as created_at",
        "core_users.display_name as created_by",
        "core_users.picture as created_logo",
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
        "status.name AS invoice_status_name",
        "status.color AS invoice_status_color",
        "product_groups.name AS product_group",
        "product_groups.id AS product_group_id",

    ]

    invoice = (
        QueryBuilderService("crmf_invoices")
        .select(*columns)
        .leftJoin(
            "crmf_transaction_types",
            "crmf_transaction_types.id",
            "crmf_invoices.transaction_type_id"
        )
        .leftJoin(
            "core_status as status",
            "status.id",
            "crmf_invoices.status_id",
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
        .leftJoin("core_entities", "core_entities.id", "crmf_invoices.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
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

        .where("crmf_invoices.id", invoice_id)
        .first()
    )

    if not invoice:
        return ResponseService.response("ERROR", None, Error.DATA_NOT_FOUND)

    # Get product group products separately if product_group_id exists
    product_group_id = invoice.get("product_group_id")
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
        invoice["product_group_products"] = product_group_products_query
    else:
        invoice["product_group_products"] = []
    # Remove the raw JSON string
    invoice.pop("product_group_products_json", None)

    return ResponseService.response("SUCCESS", invoice, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["POST"])
def update_payment(request, invoice_id):
    action_type = "UPDATE"
    action = ActionService.getAction("Invoice", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    try:
        data = json.loads(request.body)
        paid_amount = data.get("paid_amount")
        
        if not paid_amount:
            return ResponseService.response("ERROR", None, "Paid amount is required")

        updated = update_invoice_payment_details(invoice_id, paid_amount)
        if updated:
            # Update invoice status based on payment amounts
            from .utils.invoice_utils import update_invoice_status_after_payment
            update_invoice_status_after_payment(invoice_id)
            return ResponseService.response("SUCCESS", None, "Payment updated successfully")
        return ResponseService.response("ERROR", None, "Failed to update payment")
    except Exception as e:
        return ResponseService.response("ERROR", None, str(e)) 