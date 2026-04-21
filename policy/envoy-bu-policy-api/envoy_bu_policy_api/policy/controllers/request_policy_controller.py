from sys import exception
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from mServices import ResponseService, QueryBuilderService, ValidatorService
from core_models.core_models import ProductDocumentType
from core_models.crm_models import Risk, RiskSubmission
from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
from envoy_bu_policy_api.policy.models.crmp_policy_documents import PolicyRequestDocument
from services.ActionService import ActionService
from services.AuthService import AuthService
from services.ActivityService import ActivityService
from messages import Message, Error
import json
from datetime import datetime, date
from django.db.models import Max
from envoy_bu_policy_api.policy.models.crmp_request_policies import RequestPolicy
from django.db import transaction
from envoy_bu_policy_api.service import handle_entity_notes,replace_empty_strings_with_none,handle_entity,_format_date_fields
from envoy_bu_policy_api.policy.controllers.policy_status_utils import get_request_policy_status_id
from django.conf import settings
# from services.Querybuilderservice import QueryBuilderService

@csrf_exempt
@api_view(["GET", "POST"])
def request_policy_list(request):
    """GET: List all request policies | POST: Create a new request policy"""
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("RequestPolicy", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_request_policies(request)

    return create_request_policy(request)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def request_policy_detail(request, policy_id):
    """GET: Retrieve | PUT: Update | DELETE: Delete request policy by ID"""
    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("RequestPolicy", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_request_policies(request, policy_id)  # Fetch single policy
    elif request.method == "PUT":
        return update_request_policy(request, policy_id)
    elif request.method == "DELETE":
        return delete_request_policy(policy_id)


import json

def _fetch_policy_risk_types(policy_base_id):
    """Fetch risk types associated with a policy from crmp_policy_base_risk_types"""
    return (
        QueryBuilderService("crmp_policy_base_risk_types as pbrt")
        .leftJoin(
            "crm_opportunity_types as ot", "ot.id", "pbrt.risk_type_id"
        )
        .select(
            "ot.id AS risk_type_id",
            "ot.title AS risk_type_name",
            "ot.description AS risk_type_description",
        )
        .where("pbrt.policy_base_id", policy_base_id)
        .groupBy("ot.id", "ot.title", "ot.description")
        .orderBy("ot.id", "asc")
        .get()
    )


def _fetch_confirmed_vendor_responses(quotation_id):
    """Fetch confirmed vendor responses for a quotation using QueryBuilderService"""
    if not quotation_id:
        return []
    
    return (
        QueryBuilderService("crmq_vendor_response as vr")
        .leftJoin("crmq_quotation_service_providers as qsp", "qsp.id", "vr.vendor_quotation_id")
        .leftJoin("core_service_providers as sp", "sp.id", "qsp.service_provider_id")
        .select(
            "vr.id",
            "vr.quotation_id",
            "vr.coverage_details as quotation_document",
            "vr.coverage_details_name as quotation_document_name",
            "vr.coverage_details_type as quotation_document_type",
            "vr.received_date as quotation_issued_date",
            "vr.expiry_date as quotation_issued_date",
            "sp.name as service_provider_name",
            "sp.logo as service_provider_logo"
            
        )
        .where("vr.quotation_id", quotation_id)
        .where("vr.status", "CONFIRMED")
        .orderBy("vr.id", "desc")
        .get()
    )


def get_all_request_policies(request, policy_id=None):
    columns = [
        "rp.*",
        "MAX(base.premium_amount) AS premium_amount",
        "MAX(base.sum_insured) AS sum_insured",
        "MAX(base.quotation_issued_date) AS quotation_issued_date",
        "MAX(base.quotation_expiry_date) AS quotation_expiry_date",
        "MAX(base.policy_start_date) AS policy_start_date",
        "MAX(base.policy_expiry_date) AS policy_expiry_date",
        "MAX(base.quotation_notes) AS quotation_notes",
        "MAX(base.quotation_document_name) AS quotation_document_name",
        "MAX(base.quotation_document) AS quotation_document",
        "MAX(quotations.id) AS quotation_id",
        "MAX(quotations.code) AS quotation_code",
        "MAX(sp.name) AS insurer_company_name",
        "MAX(sp.logo) AS insurer_company_logo",
        "MAX(risk_type.title) AS risk_type",
        "MAX(req_user.display_name) AS requested_by",
        "MAX(req_user.picture) AS requested_by_logo",
        "MAX(status.name) AS status",
        "MAX(status.color) AS status_color",
        "MAX(status.type) AS status_type",
        "MAX(base.status_id) AS policy_base_status_id",
        "MAX(request_type.name) AS request_type",
        "MAX(product.name) AS product_name",

        # ---- PRODUCTS from base.product_id (single product) ----
        """(
            SELECT JSON_ARRAYAGG(
                JSON_OBJECT(
                    'id', vp.id,
                    'name', vp.name,
                    'is_primary', 1
                )
            )
            FROM core_vendor_products vp
            WHERE vp.id = base.product_id
        ) AS products""",

        "MAX(customer.name) AS customer_name",
        "MAX(customer.id) AS customer_id",
        "MAX(customer_contact.email) AS customer_email",
        "MAX(customer_contact.primary_contact) AS customer_primary_contact",
        "MAX(customer_contact.address) AS customer_address",
        "MAX(entity_notes.notes) AS insurer_notes",
        "MAX(coverage_type.name) AS coverage_type",
        "MAX(payment_plan.name) AS payment_plan",
        "MAX(entity.created_at) AS created_at",
        "MAX(created_by.display_name) AS created_by",
        "MAX(created_by.picture) AS created_by_logo",
        # "base.id AS policy_base_id",
        "MAX(updated_by.display_name) AS updated_by",
        "MAX(updated_by.picture) AS updated_by_logo",
        # ---- Issued policy fields (full) ----
        "MAX(issued_policy.id)                           AS issued_policy_id",
        "MAX(issued_policy.brokerage_policy_id)          AS brokerage_policy_id",
        "MAX(issued_policy.start_date)                   AS issued_start_date",
        "MAX(issued_policy.end_date)                     AS issued_end_date",
        "MAX(issued_policy.paid_amount)                  AS issued_paid_amount",
        "MAX(issued_policy.credit_period_days)           AS credit_period_days",
        "MAX(issued_policy.credit_age_days)              AS credit_age_days",
        "MAX(issued_policy.insurer_policy_id)            AS insurer_policy_id",
        "MAX(issued_policy.insurer_invoice_id)           AS insurer_invoice_id",
        "MAX(issued_policy.sum_insured)                  AS issued_sum_insured",
        "MAX(issued_policy.premium_amount)               AS issued_premium_amount",
        "MAX(issued_policy.policy_effective_date)        AS policy_effective_date",
        "MAX(issued_policy.policy_document)              AS policy_document",
        "MAX(issued_policy.policy_document_name)         AS policy_document_name",
        "MAX(issued_policy.invoice_document)             AS invoice_document",
        "MAX(issued_policy.invoice_document_name)        AS invoice_document_name",
        "MAX(issued_policy.initial_premium_amount)       AS initial_premium_amount",
        "MAX(issued_policy.remarks)                      AS issued_remarks",
        "MAX(issued_policy.is_renewal)                   AS is_renewal",
        "MAX(issued_policy.policy_request_id)            AS issued_policy_request_id",
        "MAX(issued_policy.entity_id)                    AS issued_entity_id",
        "MAX(issued_policy.policy_base_id)               AS issued_policy_base_id",
        # Account manager for request policies (from policy_base.account_manager_id)
        "MAX(account_manager.display_name)      AS account_manager_name",
        "MAX(account_manager.id)                 AS account_manager_id",
        # Sales agent for issued policies
        "MAX(sales_agent.display_name)                  AS sales_agent_name",
        "MAX(sales_agent.id)                            AS sales_agent_id",
        # Customer contact details (from core_customer_contacts)
        "MAX(CASE WHEN customer_contacts.is_primary = 1 THEN customer_contacts.title ELSE NULL END) AS customer_title",

        # ---- DOCUMENT ARRAYS via correlated subqueries (no null entries) ----
        """COALESCE((
            SELECT JSON_ARRAYAGG(JSON_OBJECT('id', dt.id, 'value', d.value, 'document_name', dt.name))
            FROM crmp_policy_documents d
            JOIN core_product_document_types dt ON dt.id = d.document_type_id
            WHERE d.policy_base_id = base.id AND dt.type = 'policy'
        ), JSON_ARRAY()) AS policy_document_value""",

        """COALESCE((
            SELECT JSON_ARRAYAGG(JSON_OBJECT('id', dt.id, 'value', d.value, 'document_name', dt.name))
            FROM crmp_policy_documents d
            JOIN core_product_document_types dt ON dt.id = d.document_type_id
            WHERE d.policy_base_id = base.id AND dt.type = 'risk'
        ), JSON_ARRAY()) AS risk_document_value""",

    ]

    query = (
        QueryBuilderService("crmp_request_policies AS rp")
        .leftJoin("crmp_policy_base AS base", "base.id", "rp.policy_base_id")
        .leftJoin("core_service_providers AS sp", "sp.id", "base.insurer_id")
        .leftJoin("crm_opportunity_types AS risk_type", "risk_type.id", "base.risk_type_id")
        .leftJoin("core_users AS req_user", "req_user.id", "base.request_by_id")
        .leftJoin("core_status AS status", "status.id", "base.status_id")
        .leftJoin("crmp_request_types AS request_type", "request_type.id", "base.request_type_id")
        .leftJoin("core_vendor_products AS product", "product.id", "base.product_id")  # optional
        .leftJoin("core_customers AS customer", "customer.id", "base.customer_id")
        .leftJoin("core_contacts AS customer_contact", "customer_contact.id", "customer.primary_contact_id")
        .leftJoin("core_entity_notes AS entity_notes", "entity_notes.entity_id", "rp.entity_id")
        .leftJoin("crmp_coverage_types AS coverage_type", "coverage_type.id", "base.coverage_type_id")
        .leftJoin("crmp_payment_plans AS payment_plan", "payment_plan.id", "base.payment_mode_id")
        .leftJoin("core_entities AS entity", "entity.id", "rp.entity_id")
        .leftJoin("core_users AS created_by", "created_by.id", "entity.created_by_id")
        .leftJoin("core_users AS updated_by", "updated_by.id", "entity.updated_by_id")
        .leftJoin("core_entity_approvals", "core_entity_approvals.entity_id", "rp.entity_id")
        .leftJoin("crmp_issued_policies AS issued_policy", "issued_policy.policy_base_id", "base.id")
        .leftJoin("core_users AS account_manager", "account_manager.id", "base.account_manager_id")
        .leftJoin("core_users AS sales_agent", "sales_agent.id", "base.sales_agent_id")
        .leftJoin("core_customer_contacts AS customer_contacts", "customer_contacts.customer_id", "customer.id")
        .leftJoin("crmq_quotations AS quotations", "quotations.opportunity_id", "base.lead_id")

        .select(*columns)
        .groupBy("rp.id")
    )

    # Helper to parse JSON fields returned as strings by the MySQL driver
    def _parse_json_field(obj, key):
        val = obj.get(key)
        if isinstance(val, str):
            try:
                obj[key] = json.loads(val)
            except Exception:
                pass

    if policy_id:
        # When getting a single policy, don't apply the approval status filter
        row = query.where("rp.id", policy_id).first()
        if not row:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

        _parse_json_field(row, "products")
        _parse_json_field(row, "policy_document_value")
        _parse_json_field(row, "risk_document_value")

        # Fetch and add risk_types
        policy_base_id = row.get("policy_base_id")
        if policy_base_id:
            risk_type_data = _fetch_policy_risk_types(policy_base_id)
            row["risk_types"] = risk_type_data
        else:
            row["risk_types"] = []

        # Fetch and add confirmed vendor responses
        quotation_id = row.get("quotation_id")
        if quotation_id:
            vendor_responses = _fetch_confirmed_vendor_responses(quotation_id)
            row["confirmed_vendor_responses"] = vendor_responses
        else:
            row["confirmed_vendor_responses"] = []

        # Structure status object like in issued_policy_detail
        # Use policy_base_status_id if available, otherwise fall back to status_id from rp.*
        status_id = row.get("policy_base_status_id") or row.get("status_id")
        status_obj = {
            "id": status_id,
            "name": row.get("status"),
            "color": row.get("status_color"),
            "type": row.get("status_type")
        }
        row["status"] = status_obj

        return ResponseService.response("SUCCESS", row, Message.DATA_FETCHED)

    # List path - Apply approval status filter only when getting all policies
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by") or "rp.id"
    sort_dir = request.GET.get("sort_dir") or "desc"

    allowed_filters = [
        "request_type.name",
        "status.name",
        "sp.name",
    ]
    search_columns = [
        "rp.policy_request_id",
        "sp.name",
        "request_type.name",
        "rp.policy_request_date",
    ]
    sort_columns = [
        "rp.id",
        "rp.policy_request_date",
        "sp.name",
        "request_type.name",
    ]

    # Apply approval status filter only for list view (not for single policy)
    data = query.where("core_entity_approvals.status", "approved").apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    rows = data.get("data") or data.get("rows") or []
    for item in rows:
        _parse_json_field(item, "products")
        _parse_json_field(item, "policy_document_value")
        _parse_json_field(item, "risk_document_value")
        
        # Fetch and add risk_types for each policy
        policy_base_id = item.get("policy_base_id")
        if policy_base_id:
            risk_type_data = _fetch_policy_risk_types(policy_base_id)
            item["risk_types"] = risk_type_data
        else:
            item["risk_types"] = []

        # Fetch and add confirmed vendor responses for each policy
        quotation_id = item.get("quotation_id")
        if quotation_id:
            vendor_responses = _fetch_confirmed_vendor_responses(quotation_id)
            item["confirmed_vendor_responses"] = vendor_responses
        else:
            item["confirmed_vendor_responses"] = []

        # Structure status object like in issued_policy_detail
        # Use policy_base_status_id if available, otherwise fall back to status_id from rp.*
        status_id = item.get("policy_base_status_id") or item.get("status_id")
        status_obj = {
            "id": status_id,
            "name": item.get("status"),
            "color": item.get("status_color"),
            "type": item.get("status_type")
        }
        item["status"] = status_obj

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def generate_policy_request_id():
    with transaction.atomic():
        last = (
            RequestPolicy.objects.select_for_update().aggregate(Max("id"))["id__max"]
            or 0
        )
        return f"PR-{last + 1}"


def _is_policy_request_approval_required():
    """
    Check APPROVAL_PERMISSIONS setting: core_setting_keys (attribute_name or name = 'APPROVAL_PERMISSIONS')
    -> core_setting_global.value e.g. {'policy_request_approval': 'true', 'quotation_request_approval': 'true'}.
    Returns True if policy requests require approval (store in approval table); False to create directly (show in get_all_request_policies without approval).
    """
    try:
        setting_key = (
            QueryBuilderService("core_setting_keys")
            .where("attribute_name", "approval_permissions")
            .first()
        )
        if not setting_key:
            setting_key = (
                QueryBuilderService("core_setting_keys")
                .where("name", "APPROVAL_PERMISSIONS")
                .first()
            )
        if not setting_key:
            return True  # default: require approval
        row = (
            QueryBuilderService("core_setting_global")
            .where("setting_key_id", setting_key["id"])
            .first()
        )
        if not row or not row.get("value"):
            return True
        raw = row["value"]
        if isinstance(raw, dict):
            val = raw.get("policy_request_approval", "true")
        else:
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except (ValueError, TypeError):
                try:
                    import ast
                    parsed = ast.literal_eval(raw) if isinstance(raw, str) else raw
                except (ValueError, SyntaxError):
                    return True
            val = (parsed or {}).get("policy_request_approval", "true")
        return str(val).strip().lower() == "true"
    except Exception:
        return True


def _is_notification_success(result):
    """Treat notification as success if status is SUCCESS or response has notification data with id (handles different response shapes)."""
    if result is None:
        return False
    # Unwrap response-like objects (e.g. DRF Response, HttpResponse wrapper) that expose .data
    if not isinstance(result, dict) and hasattr(result, "data"):
        result = getattr(result, "data", None)
    # Parse HttpResponse.content if result has content (bytes or str JSON)
    if result is not None and not isinstance(result, dict) and hasattr(result, "content"):
        try:
            raw = getattr(result, "content", None)
            if raw is not None:
                result = json.loads(raw.decode() if isinstance(raw, bytes) else raw)
        except (TypeError, ValueError, AttributeError):
            result = None
    if not isinstance(result, dict):
        return False
    status = result.get("status") or result.get("Status") or ""
    if str(status).upper() == "SUCCESS":
        return True
    if str(status).upper() in ("INTERNAL_SERVER_ERROR", "VALIDATION_ERROR"):
        return False
    # Response may use different keys; if we have data with id (inserted notification), treat as success
    data = result.get("data") or result.get("Data") or result.get("result") or result.get("body")
    if isinstance(data, dict) and data.get("id") is not None:
        return True
    # Some wrappers return the notification dict at top level (e.g. {"id": 839, "title": ...})
    if result.get("id") is not None and isinstance(result.get("id"), (int, float)):
        return True
    return data is not None


def create_request_policy_by_lead(request):
    data = json.loads(request.body or "{}")
    errors = ValidatorService.validate(data, get_request_policy_rules_lead())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    if data.get("lead_id"):
        lead_data = get_confirmed_lead_by_id(data["lead_id"])
        if not lead_data:
            return ResponseService.response(
                "NOT_FOUND", "Lead not found.", Error.NOT_FOUND
            )

    now = datetime.now()
    user = request.user if request.user.is_authenticated else None
    entity = QueryBuilderService("core_entities").insert(
        {
            "type": "policy",
            "approvel_status": False,
            "created_at": now,
            "created_by_id": user.id if user else None,
            "updated_by_id": None,
        }
    )

    entity_id = entity["id"]

    # QueryBuilderService("core_entity_approvals").insert(
    #     {
    #         "entity_id": entity_id,
    #         "user": user.id if user else None,
    #         "role": None,
    #         "level": 1,
    #         "status": "pending",
    #         "remarks": "",
    #     }
    # )

    # Create the policy request
    data["policy_request_id"] = generate_policy_request_id()
    data["policy_request_date"] = now.date().isoformat()
    data["entity_id"] = entity_id
    # Use proper status ID instead of hardcoded value
    data["status_id"] = get_request_policy_status_id("PENDING_ISSUANCE")
    if not data["status_id"]:
        print("WARNING: Could not get PENDING_ISSUANCE status ID, using fallback")
        data["status_id"] = 1  # Fallback
    data["quotation_document_name"] = lead_data.get("quotation_document_name", None)
    data["quotation_document"] = lead_data.get("quotation_document", None)
    data["insurer_id"] = lead_data.get("insurer_id", None)
    data["lead_id"] = lead_data.get("lead_id", None)
    data["customer_id"] = lead_data.get("customer_id", None)
    data["risk_type_id"] = lead_data.get("risk_type_id", None)

    data["sum_insured"] = 10000000  # checking cmt need
    data["coverage_amount"] = 10000000  # checking cmt need

    created = QueryBuilderService("crmp_request_policies").insert(data)

    return ResponseService.response("SUCCESS", created, "default_create_success_msg")


def update_request_policy(request, policy_id):
    data = json.loads(request.body or "{}")
    errors = ValidatorService.validate(data, get_request_policy_rules_put())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    updated = (
        QueryBuilderService("crmp_request_policies").where("id", policy_id).update(data)
    )
    if updated:
        return ResponseService.response(
            "SUCCESS", updated, "default_update_success_msg"
        )

    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_request_policy(policy_id):
    deleted = (
        QueryBuilderService("crmp_request_policies").where("id", policy_id).delete()
    )
    if deleted:
        return ResponseService.response(
            "SUCCESS", deleted, "default_delete_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def get_request_policy_rules_put():
    return {
        "policy_document": "nullable",
        "policy_document_name": "string",
    }


def get_request_policy_rules_lead():
    return {
        "lead_id": "required|integer|exists:crm_opportunities,id",
    }


def get_confirmed_lead_by_id(lead_id):
    query = (
        QueryBuilderService("crmq_quotation_service_providers")
        .select(
            "crm_opportunities.title AS lead_title",
            "crm_opportunities.id AS lead_id",
            "core_customers.name AS customer_name",
            "core_customers.id AS customer_id",
            "crm_opportunity_types.title AS risk_type_name",
            "crm_opportunity_types.id AS risk_type_id",
            "core_service_providers.name AS insurer_name",
            "core_service_providers.id AS insurer_id",
            "send_quotation_docs.doc AS quotation_document_name",
            "send_quotation_docs.name AS quotation_document",
        )
        .leftJoin(
            "crmq_quotations",
            "crmq_quotations.id",
            "crmq_quotation_service_providers.quotation_id",
        )
        .leftJoin("core_customers", "core_customers.id", "crmq_quotations.customer_id")
        .leftJoin(
            "core_service_providers",
            "core_service_providers.id",
            "crmq_quotation_service_providers.service_provider_id",
        )
        .leftJoin(
            "crm_opportunities",
            "crm_opportunities.id",
            "crmq_quotations.opportunity_id",
        )
        .leftJoin(
            "crm_opportunity_types",
            "crm_opportunity_types.id",
            "crmq_quotations.opportunity_type_id",
        )
        .leftJoin(
            "crm_opportunity_statuses AS crm_opportunity_statuses_stage",
            "crm_opportunity_statuses_stage.id",
            "crm_opportunities.stage_id",
        )
        .leftJoin(
            "crm_opportunity_statuses",
            "crm_opportunity_statuses.id",
            "crmq_quotation_service_providers.status",
        )
        .leftJoin(
            "crmq_send_quotations",
            "crmq_send_quotations.opportunity_id",
            "crm_opportunities.id",
        )
        .leftJoin(
            "core_entity_docs AS send_quotation_docs",
            "send_quotation_docs.entity_id",
            "crmq_send_quotations.entity_id",
        )
        # .where("crmq_quotation_service_providers.status", 1)  # CONFIRMED
        # .where("crm_opportunity_statuses_stage.name", "QUALIFIED")  # QUALIFIED stage
        .where("crm_opportunities.id", lead_id)
    )

    data = query.first()
    if data:
        return query.first()
    else:
        return data




def create_request_policy(request):
    """
    Create a new request policy.
    
    This endpoint expects risk_ids to be provided as an object with risk_type_ids as keys
    and arrays of risk_ids as values. The risk_type_ids are automatically extracted from
    the risk_ids object keys.
    
    Required fields:
    - customer_id: ID of the customer
    - risk_ids: Object with structure {"risk_type_id": [risk_id1, risk_id2, ...]}
    - product_type: Either "product" or "group"
    - Either product_id (if product_type="product") OR product_group_id (if product_type="group")
    
    The function will:
    1. Extract risk_type_ids from the risk_ids object keys
    2. Validate that all risk_ids exist for the customer and specified risk types
    3. Use the provided risk_ids for policy configuration
    4. Validate all required documents for the specified product or product group
    5. For product groups, it will fetch documents from all products in the group
    6. Store product_id and product_group_id directly in policy_base table
    7. Maintain all product details in the main policy_base table (no separate table needed)
    """
    data = json.loads(request.body or "{}")
    
    # Store original data for validation before any preprocessing
    original_data = data.copy()
    print(f" DEBUG: Original data for validation: {original_data}")
    
    # Determine draft vs convert-draft-to-request:
    # - If client sends is_draft=true (or status DRAFT), treat as draft: skip validation, update or create draft.
    # - If client sends draft_policy_base_id but is_draft=false, treat as "convert draft to request policy" (run validation, then update existing policy_base).
    draft_policy_base_id = data.get("draft_policy_base_id")
    is_draft = data.get("is_draft", False) or str(data.get("status", "")).upper() == "DRAFT"
    if draft_policy_base_id and not is_draft:
        # Converting draft to request policy: run validation and create proper request policy from existing draft
        is_draft = False
        print(f" DEBUG: draft_policy_base_id provided ({draft_policy_base_id}) with is_draft=false - converting draft to request policy")
    elif draft_policy_base_id and is_draft:
        # Updating an existing draft: keep is_draft=true, skip required validation, find policy base and update
        print(f" DEBUG: draft_policy_base_id provided ({draft_policy_base_id}) with is_draft=true - updating existing draft (no required validation)")
    
    # Set request_type_id based on is_renewal
    is_renewal = data.get("is_renewal", 0)
    data["request_type_id"] = 2 if is_renewal == 1 else 1
    original_data["request_type_id"] = data["request_type_id"]

    # Skip validation if this is a draft
    if not is_draft:
        # Validate original data with ValidatorService (before any preprocessing)
        print(f" DEBUG: Running ValidatorService validation with original data")
        print(f" DEBUG: Original data for validation: {original_data}")
        rules = get_request_policy_rules()
        print(f" DEBUG: Validation rules: {rules}")
        
        try:
            errors = ValidatorService.validate(original_data, rules)
            print(f" DEBUG: ValidatorService.validate returned errors: {errors}")
            if errors:
                print(f" DEBUG: Validation failed, returning VALIDATION_ERROR")
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
                )
            else:
                print(f" DEBUG: Validation passed, proceeding with policy creation")
        except Exception as e:
            print(f" DEBUG: ValidatorService.validate threw an exception: {str(e)}")
            print(f" DEBUG: Exception type: {type(e)}")
            import traceback
            print(f" DEBUG: Full traceback: {traceback.format_exc()}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", 
                {"error": f"ValidatorService validation failed: {str(e)}"}, 
                Error.INTERNAL_SERVER_ERROR
            )
    else:
        print(f" DEBUG: Draft mode - skipping validation")

    # Convert empty strings to None for specific fields
    # For drafts, also include date fields to avoid database errors
    keys_to_check = ['premium_amount', 'sum_insured', 'payment_mode_id', 'coverage_type_id', 'product_id', 
        'product_group_id', 'insurer_id', 'request_type_id', 'risk_type_id', 'sales_agent_id', 'account_manager_id',
        'quotation_id']
    
    # For drafts, also convert empty date fields to None
    if is_draft:
        keys_to_check.extend(['quotation_expiry_date', 'quotation_issued_date', 'policy_start_date', 'policy_expiry_date'])
    else:
        keys_to_check.extend(['quotation_expiry_date', 'quotation_issued_date'])
    
    print(f" DEBUG: Before replace_empty_strings_with_none - data: {data}")
    print(f" DEBUG: Keys to check for empty strings: {keys_to_check}")
    data = replace_empty_strings_with_none(data, keys_to_check)
    print(f" DEBUG: After replace_empty_strings_with_none - data: {data}")
    
    # Validate and format date fields if provided (for both drafts and non-drafts)
    date_fields = ['policy_start_date', 'policy_expiry_date', 'quotation_issued_date', 'quotation_expiry_date']
    for date_field in date_fields:
        if date_field in data and data[date_field] is not None and data[date_field] != '':
            try:
                # If it's already a string, try to parse and validate format
                if isinstance(data[date_field], str):
                    # Try to parse the date string to validate format (YYYY-MM-DD)
                    parsed_date = datetime.strptime(data[date_field], '%Y-%m-%d')
                    # Keep as string in YYYY-MM-DD format
                    data[date_field] = parsed_date.strftime('%Y-%m-%d')
                    print(f" DEBUG: Validated and formatted {date_field}: {data[date_field]}")
                elif isinstance(data[date_field], date):
                    # If it's already a date object, convert to string
                    data[date_field] = data[date_field].strftime('%Y-%m-%d')
                    print(f" DEBUG: Converted {date_field} from date object to string: {data[date_field]}")
            except (ValueError, TypeError) as e:
                print(f" DEBUG: Invalid date format for {date_field}: {data[date_field]}, error: {str(e)}")
                # For drafts, invalid dates are set to None, for non-drafts this would have been caught in validation
                if is_draft:
                    data[date_field] = None
                    print(f" DEBUG: Draft mode - setting invalid {date_field} to None")
                else:
                    return ResponseService.response(
                        "VALIDATION_ERROR",
                        {date_field: [f"Invalid date format. Expected YYYY-MM-DD format."]},
                        Error.VALIDATION_ERROR
                    )

    # Handle product_id and product_group_id validation
    product_id = data.get("product_id")
    product_group_id = data.get("product_group_id")
    product_type = data.get("product_type")  # Extract product_type early so it's available for drafts

    if "lead_id" in data and data["lead_id"] == "":
        data["lead_id"] = None

    # Custom validation: Check if lead_id already exists in crmp_policy_base
    lead_id = data.get("lead_id")
    if lead_id:
        existing_policy = QueryBuilderService("crmp_policy_base").where("lead_id", lead_id).first()
        if existing_policy:
            return ResponseService.response(
                "VALIDATION_ERROR", 
                f"Policy request already exists for lead ID {lead_id}", 
                "policy_already_exists",
                ""
            )

    # Extract risk_type_ids and validate risk_ids structure (skip validation for drafts)
    customer_id = data.get("customer_id")
    provided_risk_ids = data.get("risk_ids", {})
    
    if not customer_id:
        return ResponseService.response("VALIDATION_ERROR", {"customer_id": ["Customer ID is required."]}, Error.VALIDATION_ERROR)
    
    # Extract risk_type_ids from the risk_ids object keys
    if provided_risk_ids and isinstance(provided_risk_ids, dict):
        # Extract risk_type_ids from the keys of risk_ids object
        risk_type_ids = [int(risk_type_id_str) for risk_type_id_str in provided_risk_ids.keys()]
        data["risk_type_ids"] = risk_type_ids
        
        # Use first risk_type_id for backward compatibility
        if risk_type_ids:
            data["risk_type_id"] = risk_type_ids[0]
        
        # Validate risk_ids structure: {"risk_type_id": [risk_id1, risk_id2, ...]}
        # Skip validation for drafts
        if not is_draft:
            validation_errors = validate_risk_ids_structure(provided_risk_ids, customer_id, risk_type_ids)
            if validation_errors:
                return ResponseService.response("VALIDATION_ERROR", validation_errors, "risk_selection_error", "NO_RISK_VALIDATION")
        else:
            print(f" DEBUG: Draft mode - skipping risk_ids validation")
        
        # Set the provided risk_ids for further processing
        data["risk_ids"] = provided_risk_ids
        
        # Log the provided risk_ids for debugging
        print(f"Provided risk_ids: {provided_risk_ids} for customer_id: {customer_id}, extracted risk_type_ids: {risk_type_ids}")
    else:
        # Skip risk_ids requirement check for drafts
        if not is_draft:
            return ResponseService.response("VALIDATION_ERROR", {"risk_ids": ["risk_ids object is required and must contain risk_type_id to risk_ids mapping"]}, Error.VALIDATION_ERROR)
        else:
            print(f" DEBUG: Draft mode - skipping risk_ids requirement check")
            # For drafts, set empty risk_ids if not provided
            data["risk_ids"] = {}
            data["risk_type_ids"] = []

    # --- Document Validation (happens before policy creation) ---
    # Handle document validation based on product_type
    values = data.get("values", {}) if isinstance(data.get("values"), dict) else {}
    product_type = data.get("product_type")
    
    if product_type == "product" and product_id:
        # Direct product document validation
        all_required_docs = ProductDocumentType.objects.filter(
            vendor_product_id=product_id, 
            is_mandatory=True
        )
    elif product_type == "group" and product_group_id:
        # Group-based document validation (similar to product_documents_enhanced)
        # Step 1: Get product_ids from core_product_group_products where product_group_id = product_group_id
        group_products = QueryBuilderService("core_product_group_products")\
            .select("product_id")\
            .where("product_group_id", product_group_id)\
            .get()
        
        if not group_products:
            return ResponseService.response("NOT_FOUND", [], "No products found in this group.")
        
        # Extract product IDs
        product_ids = [gp["product_id"] for gp in group_products]
        
        # Step 2: Get vendor_product_ids from core_product_vendor_products where product_id in product_ids
        vendor_product_mappings = QueryBuilderService("core_product_vendor_products")\
            .select("vendor_product_id")\
            .whereIn("product_id", product_ids)\
            .get()
        
        if not vendor_product_mappings:
            return ResponseService.response("NOT_FOUND", [], "No vendor products found for these products.")
        
        # Extract vendor product IDs
        vendor_product_ids = [vpm["vendor_product_id"] for vpm in vendor_product_mappings]
        
        # Step 3: Get all required documents from core_product_document_types where vendor_product_id in vendor_product_ids
        all_required_docs = ProductDocumentType.objects.filter(
            vendor_product_id__in=vendor_product_ids,
            is_mandatory=True
        )
    else:
        all_required_docs = []

    # Validate mandatory docs (skip validation for drafts)
    if not is_draft:
        missing_docs = []
        for doc in all_required_docs:
            if str(doc.id) not in values:
                missing_docs.append({
                    "id": doc.id, 
                    "name": doc.name, 
                    "product_id": doc.vendor_product_id
                })

        if missing_docs:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"missing_documents": missing_docs},
                f"Missing required documents: {[d['name'] for d in missing_docs]}"
            )
    else:
        print(f"Draft mode - Skipping document validation")

    now = datetime.now()
    user = request.user if request.user.is_authenticated else None

    is_policy = data.get("is_policy", False)
    lead_id = data.get("lead_id")

    if is_policy and lead_id:
        # Update existing records
        policy_base = QueryBuilderService("crmp_policy_base").where("lead_id", lead_id).first()
        if policy_base:
            policy_base_id = policy_base["id"]
            # Update policy_base
            base_fields = [
                "risk_details_form_id", "risk_type_id", "insurer_id", "customer_id",
                "lead_id", "request_by_id", "premium_amount", "quotation_document_size",
                "quotation_document", "quotation_document_name", "request_type_id",
                "product_id", "payment_mode_id", "coverage_type_id", "sum_insured",
                "quotation_issued_date", "quotation_expiry_date", "policy_start_date",
                "policy_expiry_date", "quotation_notes", "quotation_id", "quotation_code"
            ]
            policy_base_data = {field: data.get(field) for field in base_fields if field in data}
            QueryBuilderService("crmp_policy_base").where("id", policy_base_id).update(policy_base_data)

            # Risk types are now managed through the PolicyRiskConfig table
            # No need to maintain separate policy_base_risk_types table

            # Product and product_group are updated directly in policy_base table
            # Update request policy
            request_policy = QueryBuilderService("crmp_request_policies").where("policy_base_id", policy_base_id).first()
            if request_policy:
                request_policy_id = request_policy["id"]  #  Ensure we assign it
                entity_id = request_policy["entity_id"]
                QueryBuilderService("crmp_request_policies").where("policy_base_id", policy_base_id).update({
                    "policy_request_date": now.date().isoformat()
                })
            else:
                # Create new request policy if not exists
                approval_required = _is_policy_request_approval_required()
                entity = QueryBuilderService("core_entities").insert({
                    "type": "policy",
                    "approvel_status": not approval_required,  # False = needs approval, True = direct (no approval)
                    "created_at": now,
                    "created_by_id": user.id if user else None,
                    "updated_by_id": None,
                })
                entity_id = entity["id"]
                approval_status = "pending" if approval_required else "approved"
                QueryBuilderService("core_entity_approvals").insert({
                    "entity_id": entity_id,
                    "user": user.id if user else None,
                    "role": None,
                    "level": 1,
                    "status": approval_status,
                    "remarks": "",
                })
                # Use proper status ID instead of hardcoded value
                status_id = get_request_policy_status_id("PENDING_ISSUANCE")
                if not status_id:
                    print("WARNING: Could not get PENDING_ISSUANCE status ID, using fallback")
                    status_id = 1  # Fallback
                    
                request_policy_data = QueryBuilderService("crmp_request_policies").insert({
                    "policy_request_id": generate_policy_request_id(),
                    "policy_request_date": now.date().isoformat(),
                    "entity_id": entity_id,
                    "status_id": status_id,
                    "policy_base_id": policy_base_id
                })
                request_policy_id = request_policy_data["id"]  #  Assigned here too

                    #  Validate existing mandatory docs for update
            current_product_id = product_id or policy_base.get("product_id")
            current_product_group_id = product_group_id or policy_base.get("product_group_id")
            values = data.get("values", {}) if isinstance(data.get("values"), dict) else {}
            
            # Initialize stored_documents to prevent UnboundLocalError
            stored_documents = {}

            if product_type == "product" and current_product_id:
                # Get all required documents for the product
                all_required_docs = ProductDocumentType.objects.filter(
                    vendor_product_id=current_product_id, 
                    is_mandatory=True
                )

                missing_docs = []
                for doc in all_required_docs:
                    # Check if doc already exists in DB or is passed in request
                    exists_in_db = PolicyRequestDocument.objects.filter(
                        policy_base_id=policy_base_id,
                        document_type_id=doc.id
                    ).exists()
                    exists_in_request = str(doc.id) in values

                    if not (exists_in_db or exists_in_request):
                        missing_docs.append({"id": doc.id, "name": doc.name, "product_id": doc.vendor_product_id})

                if missing_docs:
                    return ResponseService.response(
                        "VALIDATION_ERROR",
                        {"missing_documents": missing_docs},
                        f"Missing required documents: {[d['name'] for d in missing_docs]}"
                    )
            elif product_type == "group" and current_product_group_id:
                # Group-based document validation for update
                # Step 1: Get product_ids from core_product_group_products where product_group_id = current_product_group_id
                group_products = QueryBuilderService("core_product_group_products")\
                    .select("product_id")\
                    .where("product_group_id", current_product_group_id)\
                    .get()
                
                if not group_products:
                    return ResponseService.response("NOT_FOUND", [], "No products found in this group.")
                
                # Extract product IDs
                product_ids = [gp["product_id"] for gp in group_products]
                
                # Step 2: Get vendor_product_ids from core_product_vendor_products where product_id in product_ids
                vendor_product_mappings = QueryBuilderService("core_product_vendor_products")\
                    .select("vendor_product_id")\
                    .whereIn("product_id", product_ids)\
                    .get()
                
                if not vendor_product_mappings:
                    return ResponseService.response("NOT_FOUND", [], "No vendor products found for these products.")
                
                # Extract vendor product IDs
                vendor_product_ids = [vpm["vendor_product_id"] for vpm in vendor_product_mappings]
                
                # Step 3: Get all required documents from core_product_document_types where vendor_product_id in vendor_product_ids
                all_required_docs = ProductDocumentType.objects.filter(
                    vendor_product_id__in=vendor_product_ids,
                    is_mandatory=True
                )

                missing_docs = []
                for doc in all_required_docs:
                    # Check if doc already exists in DB or is passed in request
                    exists_in_db = PolicyRequestDocument.objects.filter(
                        policy_base_id=policy_base_id,
                        document_type_id=doc.id
                    ).exists()
                    exists_in_request = str(doc.id) in values

                    if not (exists_in_db or exists_in_request):
                        missing_docs.append({"id": doc.id, "name": doc.name, "product_id": doc.vendor_product_id})

                if missing_docs:
                    return ResponseService.response(
                        "VALIDATION_ERROR",
                        {"missing_documents": missing_docs},
                        f"Missing required documents: {[d['name'] for d in missing_docs]}"
                    )

                # Save docs from request values (both mandatory & optional)
                for doc_type_id_str, doc_info in values.items():
                    try:
                        doc_type_id = int(doc_type_id_str)
                        if not ProductDocumentType.objects.filter(id=doc_type_id, vendor_product_id=current_product_id).exists():
                            continue
                        doc_obj, created = PolicyRequestDocument.objects.update_or_create(
                            policy_base_id=policy_base_id,
                            document_type_id=doc_type_id,
                            defaults={"value": doc_info}
                        )
                        # Store the document value in our response object
                        stored_documents[doc_type_id_str] = doc_obj.value
                    except ValueError:
                        continue

     

            # Update crmp_policy_risk_config with structured risk_ids
            QueryBuilderService("crmp_policy_risk_config").where("policy_base_id", policy_base_id).delete()

            # Handle structured risk_ids: {"risk_type_id": [risk_id1, risk_id2, ...]}
            if "risk_ids" in data and isinstance(data["risk_ids"], dict):
                for risk_type_id_str, risk_id_list in data["risk_ids"].items():
                    for risk_id in risk_id_list:
                        # Get risk_submission from crm_risk_submissions table
                        risk_submission = QueryBuilderService("crm_risk_submissions").where("risk_id", risk_id).first()
                        if risk_submission:
                            # Insert using the risk_submission foreign key (not submission_id)
                            QueryBuilderService("crmp_policy_risk_config").insert({
                                "policy_base_id": policy_base_id,
                                "risk_submission_id": risk_submission["id"]  # Use the risk_submission record ID
                            })
                        
                        # Update risk submissions with lead_id if provided
                        if data.get("lead_id"):
                            QueryBuilderService("crm_risk_submissions").where("risk_id", risk_id).update({
                                "lead_id": data["lead_id"]
                            })

            if "insurer_notes" in data and data["insurer_notes"]:
                handle_entity_notes(entity_id, [{
                    "note": data["insurer_notes"],
                    "created_by_id": user.id if user else None,
                    "created_at": now
                }], is_update=False)

            update_customer_contact_info(data)

            # Notification to Account Manager for Policy Update/Approval
            try:
                # Fetch detailed policy information for notification
                policy_details = (
                    QueryBuilderService("crmp_request_policies as rp")
                    .leftJoin("crmp_policy_base as pb", "pb.id", "rp.policy_base_id")
                    .leftJoin("core_customers as customer", "customer.id", "pb.customer_id")
                    .leftJoin("crm_opportunities as opp", "opp.id", "pb.lead_id")
                    .leftJoin("core_users as account_mgr", "account_mgr.id", "opp.account_manager_id")
                    .leftJoin("core_vendor_products as product", "product.id", "pb.product_id")
                    .leftJoin("core_product_groups as product_group", "product_group.id", "pb.product_group_id")
                    .leftJoin("crmp_request_types as req_type", "req_type.id", "pb.request_type_id")
                    .select(
                        "rp.id as request_policy_id",
                        "rp.policy_request_id",
                        "pb.id as policy_base_id",
                        "pb.premium_amount",
                        "customer.name as customer_name",
                        "customer.id as customer_id",
                        "opp.id as lead_id",
                        "opp.title as lead_title",
                        "account_mgr.id as account_manager_id",
                        "account_mgr.display_name as account_manager_name",
                        "product.name as product_name",
                        "product_group.name as product_group_name",
                        "req_type.name as request_type_name"
                    )
                    .where("rp.policy_base_id", policy_base_id)
                    .first()
                )

                if policy_details and policy_details.get("account_manager_id"):
                    # Ensure customer_id is valid
                    notification_customer_id = policy_details.get("customer_id") or data.get("customer_id")
                    
                    if notification_customer_id:
                        request_id = policy_details.get("policy_request_id", "")
                        customer_name = policy_details.get("customer_name", "Unknown Customer")
                        product_display = policy_details.get("product_group_name") or policy_details.get("product_name", "N/A")
                        request_type = policy_details.get("request_type_name", "Policy")
                        premium_amount = policy_details.get("premium_amount", 0)
                        formatted_premium = f"${premium_amount:,.2f}" if premium_amount else "N/A"
                        
                        approval_link = f"{settings.FRONTEND_URL}/approvals/policy/{policy_base_id}" if hasattr(settings, 'FRONTEND_URL') else f"/approvals/policy/{policy_base_id}"
                        
                        notification_message = (
                            f"Updated {request_type} Request for Approval\n\n"
                            f"Request ID: {request_id}\n"
                            f"Customer: {customer_name}\n"
                            f"Product: {product_display}\n"
                            f"Premium: {formatted_premium}\n"
                            f"\nThis policy request has been updated. Please review."
                        )
                        
                        print(f"📧 Sending update notification to Account Manager ID: {policy_details.get('account_manager_id')}, Customer ID: {notification_customer_id}")
                        result = NotificationService.generate_notification(
                            type_code="policy_approval",
                            title="Policy Request Updated - Review Required",
                            meta_data={
                                "policy_base_id": policy_base_id,
                                "request_policy_id": policy_details.get("request_policy_id"),
                                "request_id": request_id,
                                "request_type": request_type,
                                "approval_link": approval_link,
                                "customer_name": customer_name,
                                "product_name": product_display,
                                "action_required": "review_update"
                            },
                            message=notification_message,
                            customer_id=notification_customer_id,
                            user_id=policy_details.get("account_manager_id")
                        )
                        print(f"✓ Notification result: {result}")
                        print(f"✓ Update notification sent to Account Manager (ID: {policy_details.get('account_manager_id')})")
                    else:
                        print(f"⚠ Cannot send update notification: No customer_id found")
            except Exception as update_notify_exc:
                print(f"⚠ Error sending update notification: {update_notify_exc}")

            # Prepare response data with stored documents
            created_record = QueryBuilderService("crmp_request_policies").where("policy_base_id", policy_base_id).first()
            response_data = created_record if created_record else {}
            if stored_documents:
                response_data["stored_documents"] = stored_documents
                
            return ResponseService.response("SUCCESS", response_data, "default_update_success_msg")
        else:
            return ResponseService.response("NOT_FOUND", "Policy base not found for the given lead_id.", Error.NOT_FOUND)
    else:
        # Create new records
        approval_required = _is_policy_request_approval_required()
        entity = QueryBuilderService("core_entities").insert({
            "type": "policy",
            "approvel_status": not approval_required,  # False = needs approval, True = direct (no approval)
            "created_at": now,
            "created_by_id": user.id if user else None,
            "updated_by_id": None,
        })
        entity_id = entity["id"]

        approval_status = "pending" if approval_required else "approved"
        QueryBuilderService("core_entity_approvals").insert({
            "entity_id": entity_id,
            "user": user.id if user else None,
            "role": None,
            "level": 1,
            "status": approval_status,
            "remarks": "",
        })

        # Determine sales_agent_id and account_manager_id from lead data or request data
        sales_agent_id = None
        account_manager_id = None
        
        # First, try to get from lead data if lead_id is provided
        if data.get("lead_id"):
            lead_details = QueryBuilderService("crm_opportunities")\
                .select("sales_agent_id", "account_manager_id")\
                .where("id", data.get("lead_id"))\
                .first()
            
            if lead_details:
                sales_agent_id = lead_details.get("sales_agent_id")
                account_manager_id = lead_details.get("account_manager_id")
        
        # If sales_agent_id is provided directly in the request, use it
        if data.get("sales_agent_id"):
            sales_agent_id = data.get("sales_agent_id")
        
        # If account_manager_id is provided directly in the request, use it
        if data.get("account_manager_id"):
            account_manager_id = data.get("account_manager_id")
        
        # Set sales_agent_id in data if found
        if sales_agent_id:
            data["sales_agent_id"] = sales_agent_id
        
        # If we have sales_agent_id but no account_manager_id, try to find account manager
        if sales_agent_id and not account_manager_id:
            try:
                # Try to get account manager from the sales agent's team
                team_member = QueryBuilderService("core_team_users")\
                    .leftJoin("core_teams", "core_teams.id", "core_team_users.team_id")\
                    .select("core_teams.manager_id")\
                    .where("core_team_users.user_id", sales_agent_id)\
                    .first()
                
                if team_member and team_member.get("manager_id"):
                    account_manager_id = team_member["manager_id"]
                    print(f"DEBUG: Found account_manager_id {account_manager_id} for sales_agent_id {sales_agent_id}")
                else:
                    print(f"DEBUG: No team manager found for sales_agent_id {sales_agent_id}")
            except Exception as e:
                print(f"DEBUG: Error finding account manager for sales_agent_id {sales_agent_id}: {str(e)}")
        
        # Set account_manager_id in data if found
        if account_manager_id:
            data["account_manager_id"] = account_manager_id

        base_fields = [
            "risk_details_form_id", "risk_type_id", "insurer_id", "customer_id",
            "lead_id", "request_by_id", "premium_amount", "quotation_document_size",
            "quotation_document", "quotation_document_name", "request_type_id",
            "product_id", "product_group_id", "payment_mode_id", "coverage_type_id", "sum_insured",
            "quotation_issued_date", "quotation_expiry_date", "policy_start_date",
            "policy_expiry_date", "quotation_notes", "sales_agent_id", "account_manager_id",
            "quotation_id", "quotation_code"
        ]
        
        # Check if draft_policy_base_id is provided - if so, update existing policy_base
        # draft_policy_base_id can be either crmp_request_policies.id (request policy id) or crmp_policy_base.id; resolve to policy_base_id.
        provided_draft_id = data.get("draft_policy_base_id")
        provided_policy_base_id = None
        is_draft_update = provided_draft_id is not None and str(provided_draft_id).strip() != ""
        
        if is_draft_update:
            # Resolve draft_policy_base_id: try crmp_request_policies.id first, then crmp_policy_base.id
            request_policy_by_id = QueryBuilderService("crmp_request_policies").where("id", provided_draft_id).first()
            if request_policy_by_id:
                provided_policy_base_id = request_policy_by_id.get("policy_base_id")
                print(f" DEBUG: draft_policy_base_id ({provided_draft_id}) resolved as request_policy id -> policy_base_id: {provided_policy_base_id}")
            if provided_policy_base_id is None:
                # Treat as policy_base id
                existing_pb = QueryBuilderService("crmp_policy_base").where("id", provided_draft_id).first()
                if existing_pb:
                    provided_policy_base_id = provided_draft_id
                    print(f" DEBUG: draft_policy_base_id ({provided_draft_id}) treated as policy_base id")
            if provided_policy_base_id is None:
                return ResponseService.response("NOT_FOUND", None, f"Draft not found: no request policy or policy base with ID {provided_draft_id}.")
            
            # Update existing draft policy_base
            print(f" DEBUG: Draft update mode - updating existing policy_base_id: {provided_policy_base_id}")
            
            # Verify the policy_base exists
            existing_policy_base = QueryBuilderService("crmp_policy_base").where("id", provided_policy_base_id).first()
            if not existing_policy_base:
                return ResponseService.response("NOT_FOUND", None, f"Policy base with ID {provided_policy_base_id} not found.")
            
            # Prepare update data - only include fields that are not None and not empty strings
            policy_base_data = {field: data.get(field) for field in base_fields 
                              if field in data and data.get(field) is not None and data.get(field) != ''}
            
            # For draft update (is_draft=true): ensure FK fields reference existing rows to avoid IntegrityError.
            # If a referenced row doesn't exist, skip updating that field (keep existing value).
            if is_draft:
                # customer_id -> core_customers
                if "customer_id" in policy_base_data:
                    try:
                        cid = int(policy_base_data["customer_id"])
                        if not QueryBuilderService("core_customers").where("id", cid).first():
                            policy_base_data.pop("customer_id", None)
                            print(f" DEBUG: Draft update - customer_id {cid} not found in core_customers, keeping existing value")
                        else:
                            policy_base_data["customer_id"] = cid
                    except (TypeError, ValueError):
                        policy_base_data.pop("customer_id", None)
                # insurer_id -> core_service_providers
                if "insurer_id" in policy_base_data:
                    try:
                        iid = int(policy_base_data["insurer_id"])
                        if not QueryBuilderService("core_service_providers").where("id", iid).first():
                            policy_base_data.pop("insurer_id", None)
                            print(f" DEBUG: Draft update - insurer_id {iid} not found in core_service_providers, keeping existing value")
                        else:
                            policy_base_data["insurer_id"] = iid
                    except (TypeError, ValueError):
                        policy_base_data.pop("insurer_id", None)
                # product_id: may reference core_products or vendor product table - skip strict check or check core_product_vendor_products
                if "product_id" in policy_base_data:
                    try:
                        policy_base_data["product_id"] = int(policy_base_data["product_id"])
                    except (TypeError, ValueError):
                        policy_base_data.pop("product_id", None)
                # request_by_id, sales_agent_id, account_manager_id -> user table (optional check)
                for fk_field in ("request_by_id", "sales_agent_id", "account_manager_id"):
                    if fk_field in policy_base_data:
                        try:
                            policy_base_data[fk_field] = int(policy_base_data[fk_field])
                        except (TypeError, ValueError):
                            policy_base_data.pop(fk_field, None)
            
            # Don't update required date fields if they're not provided (keep existing values)
            # Only set defaults if the field is completely missing from the update
            required_date_fields = {
                'policy_start_date': date.today().strftime('%Y-%m-%d'),
                'policy_expiry_date': (date.today().replace(year=date.today().year + 1)).strftime('%Y-%m-%d')
            }
            
            for req_field, default_value in required_date_fields.items():
                # Only set default if field is not in data at all (not provided in request)
                if req_field not in data:
                    if req_field not in existing_policy_base or not existing_policy_base.get(req_field):
                        policy_base_data[req_field] = default_value
                        print(f" DEBUG: Draft update - set default {req_field} to {default_value}")
            
            print(f" DEBUG: Draft update mode - policy_base_data keys to update: {list(policy_base_data.keys())}")
            
            # Update the existing policy_base
            if policy_base_data:
                QueryBuilderService("crmp_policy_base").where("id", provided_policy_base_id).update(policy_base_data)
                print(f" DEBUG: Successfully updated policy_base_id: {provided_policy_base_id}")
            
            policy_base_id = provided_policy_base_id
            print(f" DEBUG: Updating existing policy_base {policy_base_id} - treating as non-draft (is_draft=false) to create proper request policy")
        else:
            # Create new policy_base (original logic)
            # For drafts, only include fields that are not None and not empty strings
            # For non-drafts, include all fields that exist in data (validation ensures required fields)
            if is_draft:
                policy_base_data = {field: data.get(field) for field in base_fields 
                                  if field in data and data.get(field) is not None and data.get(field) != ''}
                
                # For drafts, handle required date fields that might be missing
                # If policy_start_date or policy_expiry_date are missing, provide placeholder dates
                # This prevents database errors for required fields without defaults
                required_date_fields = {
                    'policy_start_date': date.today().strftime('%Y-%m-%d'),  # Default to today
                    'policy_expiry_date': (date.today().replace(year=date.today().year + 1)).strftime('%Y-%m-%d')  # Default to 1 year from today
                }
                
                for req_field, default_value in required_date_fields.items():
                    if req_field not in policy_base_data or policy_base_data[req_field] is None or policy_base_data[req_field] == '':
                        policy_base_data[req_field] = default_value
                        print(f" DEBUG: Draft mode - set default {req_field} to {default_value}")
                
                print(f" DEBUG: Draft mode - policy_base_data keys: {list(policy_base_data.keys())}")
            else:
                policy_base_data = {field: data.get(field) for field in base_fields if field in data}
            
            policy_base = QueryBuilderService("crmp_policy_base").insert(policy_base_data)
            policy_base_id = policy_base["id"]
       
        # Set policy base status based on request type or draft status
        try:
            from envoy_bu_policy_api.policy.controllers.policy_status_utils import set_policy_base_status_by_scenario
            
            if is_draft:
                # Set to DRAFT status for draft requests
                result = set_policy_base_status_by_scenario(policy_base_id, "draft")
                if result.get("success"):
                    print(f"Successfully set policy base {policy_base_id} status to DRAFT (draft mode)")
                else:
                    print(f"Warning: Failed to set policy base status to DRAFT: {result.get('message')}")
            else:
                request_type = QueryBuilderService("crmp_request_types")\
                    .where("id", data.get("request_type_id"))\
                    .select("name")\
                    .first()
                
                if request_type and request_type.get("name"):
                    request_type_name = request_type["name"]
                    
                    if request_type_name == "New Request":
                        result = set_policy_base_status_by_scenario(policy_base_id, "pending_issuance")
                    elif request_type_name == "Renewal":
                        result = set_policy_base_status_by_scenario(policy_base_id, "renewal_in_progress")
                    elif request_type_name == "Cancellation":
                        result = set_policy_base_status_by_scenario(policy_base_id, "cancelled")
                    else:
                        result = set_policy_base_status_by_scenario(policy_base_id, "pending_issuance")
                    
                    if result.get("success"):
                        print(f"Successfully set policy base {policy_base_id} status based on request type: {request_type_name}")
                    else:
                        print(f"Warning: Failed to set policy base status: {result.get('message')}")
                else:
                    result = set_policy_base_status_by_scenario(policy_base_id, "pending_issuance")
                    print(f"Request type not found, set policy base status to pending_issuance")
                
        except Exception as e:
            print(f"Error setting policy base status: {e}")
       
        # Determine the correct status for request policy based on request type or draft status
        status_id = None  # Initialize status_id
        
        # If this is a draft, set status to DRAFT
        if is_draft:
            status_id = get_request_policy_status_id("DRAFT")
            print(f"Draft mode - Set request policy status to DRAFT")
        else:
            try:
                request_type = QueryBuilderService("crmp_request_types")\
                    .where("id", data.get("request_type_id"))\
                    .select("name")\
                    .first()
                
                if request_type and request_type.get("name"):
                    request_type_name = request_type["name"]
                    
                    if request_type_name == "New Request":
                        status_id = get_request_policy_status_id("PENDING_ISSUANCE")
                        print(f"Set request policy status to PENDING_ISSUANCE")
                    elif request_type_name == "Renewal":
                        status_id = get_request_policy_status_id("RENEWAL_IN_PROGRESS")
                        print(f"Set request policy status to RENEWAL_IN_PROGRESS")
                    elif request_type_name == "Cancellation":
                        status_id = get_request_policy_status_id("CANCELLED")
                        print(f"Set request policy status to CANCELLED")
                    else:
                        # Default to PENDING_ISSUANCE for unknown request types
                        status_id = get_request_policy_status_id("PENDING_ISSUANCE")
                        print(f"Unknown request type '{request_type_name}', defaulting to PENDING_ISSUANCE")
                else:
                    # Fallback if request type not found
                    status_id = get_request_policy_status_id("PENDING_ISSUANCE")
                    print(f"Request type not found, defaulting to PENDING_ISSUANCE")
                    
            except Exception as e:
                print(f"Error determining request policy status: {e}")
                # Fallback to PENDING_ISSUANCE
                status_id = get_request_policy_status_id("PENDING_ISSUANCE")

        # Risk types are now managed through the PolicyRiskConfig table
        # No need to maintain separate policy_base_risk_types table

        # Product and product_group are already stored in policy_base table

        # CRITICAL: Ensure status_id is never null (NOT NULL constraint)
        if not status_id:
            print("WARNING: status_id is null, forcing to PENDING_ISSUANCE")
            status_id = get_request_policy_status_id("PENDING_ISSUANCE")
            # If still null, use a hardcoded fallback (should never happen if core_status table is properly seeded)
            if not status_id:
                print("CRITICAL ERROR: Could not get PENDING_ISSUANCE status ID, using fallback")
                status_id = 1  # This should be the PENDING_ISSUANCE status ID

        # Check if request_policy already exists - always check when draft_policy_base_id is provided
        # This prevents creating duplicate request_policies
        existing_request_policy = None
        if is_draft_update or provided_policy_base_id:
            existing_request_policy = QueryBuilderService("crmp_request_policies").where("policy_base_id", policy_base_id).first()
            if existing_request_policy:
                print(f" DEBUG: Found existing request_policy with ID: {existing_request_policy.get('id')} for policy_base_id: {policy_base_id}")
        
        if existing_request_policy:
            # Update existing request_policy (e.g. draft save second time)
            request_policy_data = {
                "policy_request_date": now.date().isoformat(),
                "status_id": status_id
            }
            QueryBuilderService("crmp_request_policies").where("id", existing_request_policy.get("id")).update(request_policy_data)
            request_policy_id = existing_request_policy.get("id")
            created = None  # Not a new insert; skip "if created" logic later (e.g. update_customer_contact_info, inheritance entity_id from created)
            print(f" DEBUG: Updated existing request_policy with ID: {request_policy_id} (prevented duplicate creation)")
        else:
            # Create new request_policy
            request_policy_data = {
                "policy_request_id": generate_policy_request_id(),
                "policy_request_date": now.date().isoformat(),
                "entity_id": entity_id,
                "status_id": status_id,
                "policy_base_id": policy_base_id
            }
            created = QueryBuilderService("crmp_request_policies").insert(request_policy_data)
            request_policy_id = created.get("id") if isinstance(created, dict) else created

        # --- Risk Duplication Logic for request_type_id = 2 ---
        if data.get("request_type_id") == 2 and data.get("risk_ids") and isinstance(data.get("risk_ids"), dict):
            try:
                # Get the lead_id from the data
                lead_id = data.get("lead_id")
                
                if lead_id and lead_id.strip() and lead_id.lower() not in ['null', 'undefined', '']:
                    # If lead_id is provided, directly assign existing risk_ids without duplication
                    print(f"DEBUG: Lead_id provided ({lead_id}), skipping risk duplication and directly assigning existing risks")
                    
                    for risk_type_id_str, risk_id_list in data["risk_ids"].items():
                        for risk_id in risk_id_list:
                            # Get the latest risk submission for this risk_id (highest version or latest created)
                            latest_risk_submission = QueryBuilderService("crm_risk_submissions")\
                                .where("risk_id", risk_id)\
                                .orderBy("version", "desc")\
                                .orderBy("created_at", "desc")\
                                .first()
                            
                            if latest_risk_submission:
                                # Directly assign the latest risk_submission to the new policy_base_id
                                QueryBuilderService("crmp_policy_risk_config").insert({
                                    "policy_base_id": policy_base_id,
                                    "risk_submission_id": latest_risk_submission["id"]
                                })
                    
                    # Log activity for direct risk assignment
                    total_risks = sum(len(risk_list) for risk_list in data["risk_ids"].values())
                    ActivityService.store_activity(
                        request=request,
                        entity_id=data.get("entity_id"),
                        activity=f"Direct assignment: Assigned {total_risks} existing risk submissions to new policy_base_id {policy_base_id} (lead_id: {lead_id})"
                    )
                    
                else:
                    # If no lead_id provided, perform the full risk duplication process
                    print(f"DEBUG: No lead_id provided, performing full risk duplication")
                    
                    # Process each risk_type_id and its associated risk_ids
                    for risk_type_id_str, risk_id_list in data["risk_ids"].items():
                        for risk_id in risk_id_list:
                            # Get the latest risk submission for this risk_id (highest version or latest created)
                            existing_risk_submission = QueryBuilderService("crm_risk_submissions")\
                                .where("risk_id", risk_id)\
                                .orderBy("version", "desc")\
                                .orderBy("created_at", "desc")\
                                .first()
                            
                            if existing_risk_submission:
                                # Get the original submission to get form_id
                                original_submission = QueryBuilderService("core_form_submissionss")\
                                    .where("id", existing_risk_submission["submission_id"])\
                                    .select("form_id")\
                                    .first()
                                
                                if original_submission:
                                    # Create new submission in core_form_submissionss
                                    new_submission = QueryBuilderService("core_form_submissionss").insert({
                                        "form_id": original_submission["form_id"],
                                        "user_id": request.user.id if request.user.is_authenticated else None,
                                        "customer_id": None
                                    })
                                    
                                    # Copy form submission values from original submission to new submission
                                    original_submission_values = QueryBuilderService("core_form_submission_valuess")\
                                        .where("form_submission_id", existing_risk_submission["submission_id"])\
                                        .get()
                                    
                                    # Insert copied values for the new submission
                                    for value_record in original_submission_values:
                                        QueryBuilderService("core_form_submission_valuess").insert({
                                            "form_submission_id": new_submission["id"],
                                            "custom_form_element_id": value_record["custom_form_element_id"],
                                            "form_element_id": value_record["form_element_id"],
                                            "value": value_record["value"]
                                        })
                                    
                                    # Create new submission risk entry with new submission_id and lead_id
                                    # Increment version count by 1
                                    current_version = existing_risk_submission.get("version", 1)
                                    new_version = current_version + 1
                                    print(f"DEBUG: Risk {risk_id} - Current version: {current_version}, New version: {new_version}")
                                    
                                    new_submission_risk_data = {
                                        "risk_id": existing_risk_submission["risk_id"],
                                        "submission_id": new_submission["id"],
                                        "lead_id": lead_id,
                                        "version": new_version,
                                        "created_at": date.today(),
                                        "updated_at": date.today()
                                    }
                                    
                                    # Insert the new submission risk
                                    new_risk_submission = QueryBuilderService("crm_risk_submissions").insert(new_submission_risk_data)
                                    
                                    # Update crmp_policy_risk_config table with new risk_submission_id
                                    QueryBuilderService("crmp_policy_risk_config").insert({
                                        "policy_base_id": policy_base_id,
                                        "risk_submission_id": new_risk_submission["id"]
                                    })
                    
                    # Log activity for risk duplication
                    total_risks = sum(len(risk_list) for risk_list in data["risk_ids"].values())
                    ActivityService.store_activity(
                        request=request,
                        entity_id=data.get("entity_id"),
                        activity=f"Created {total_risks} new risk submissions with form values for request_type_id = 2 request policy"
                    )
                
            except Exception as e:
                # Log error but don't fail the policy creation
                print(f"Error processing risk details for request_type_id = 2: {str(e)}")
                print(f"Error details: {type(e).__name__}: {str(e)}")
                ActivityService.store_activity(
                    request=request,
                    entity_id=data.get("entity_id"),
                    activity=f"Warning: Failed to process risk details for request_type_id = 2 - {str(e)}"
                )

        # Insert into crmp_policy_risk_config with structured risk_ids
        # Handle structured risk_ids: {"risk_type_id": [risk_id1, risk_id2, ...]}
        # Skip storing original risk_ids if request_type_id = 2 (will be handled in duplication logic)
        if "risk_ids" in data and isinstance(data["risk_ids"], dict) and data.get("request_type_id") != 2:
            # For draft updates, delete existing risk configurations first to avoid duplicates
            if is_draft_update:
                QueryBuilderService("crmp_policy_risk_config").where("policy_base_id", policy_base_id).delete()
                print(f" DEBUG: Draft update - deleted existing risk configurations for policy_base_id: {policy_base_id}")
            
            for risk_type_id_str, risk_id_list in data["risk_ids"].items():
                for risk_id in risk_id_list:
                    # Get risk_submission from crm_risk_submissions table
                    risk_submission = QueryBuilderService("crm_risk_submissions").where("risk_id", risk_id).first()
                    if risk_submission:
                        # Check if this risk_submission_id already exists for this policy_base_id (for non-draft updates)
                        if not is_draft_update:
                            existing_config = QueryBuilderService("crmp_policy_risk_config")\
                                .where("policy_base_id", policy_base_id)\
                                .where("risk_submission_id", risk_submission["id"])\
                                .first()
                            if existing_config:
                                print(f" DEBUG: Risk submission {risk_submission['id']} already exists for policy_base_id {policy_base_id}, skipping insert")
                                continue
                        
                        # Insert using the risk_submission foreign key (not submission_id)
                        QueryBuilderService("crmp_policy_risk_config").insert({
                            "policy_base_id": policy_base_id,
                            "risk_submission_id": risk_submission["id"]  # Use the risk_submission record ID
                        })
                    
                    # Update risk submissions with lead_id if provided
                    if data.get("lead_id"):
                        QueryBuilderService("crm_risk_submissions").where("risk_id", risk_id).update({
                            "lead_id": data["lead_id"]
                        })

        # Store risk_type_ids in crmp_policy_base_risk_types table
        if "risk_type_ids" in data and isinstance(data["risk_type_ids"], list) and data["risk_type_ids"]:
            # For draft updates, delete existing risk_type_ids first to avoid duplicates
            if is_draft_update:
                QueryBuilderService("crmp_policy_base_risk_types").where("policy_base_id", policy_base_id).delete()
                print(f" DEBUG: Draft update - deleted existing risk_type_ids for policy_base_id: {policy_base_id}")
            
            for risk_type_id in data["risk_type_ids"]:
                # Check if this risk_type_id already exists for this policy_base_id (for non-draft updates)
                if not is_draft_update:
                    existing_risk_type = QueryBuilderService("crmp_policy_base_risk_types")\
                        .where("policy_base_id", policy_base_id)\
                        .where("risk_type_id", risk_type_id)\
                        .first()
                    if existing_risk_type:
                        print(f" DEBUG: Risk type {risk_type_id} already exists for policy_base_id {policy_base_id}, skipping insert")
                        continue
                
                # Insert risk_type_id (only if not exists for non-draft, or always for draft updates after deletion)
                QueryBuilderService("crmp_policy_base_risk_types").insert({
                    "policy_base_id": policy_base_id,
                    "risk_type_id": risk_type_id
                })

        # --- Document Storage (validation already done above) ---
        values = data.get("values", {}) if isinstance(data.get("values"), dict) else {}
        stored_documents = {}
        
        if (product_type == "product" and product_id and values) or (product_type == "group" and product_group_id and values):
            if product_type == "product":
                # Get all documents for the product
                all_docs = ProductDocumentType.objects.filter(vendor_product_id=product_id)
            else:  # product_type == "group"
                # Group-based document retrieval for storage
                # Step 1: Get product_ids from core_product_group_products where product_group_id = product_group_id
                group_products = QueryBuilderService("core_product_group_products")\
                    .select("product_id")\
                    .where("product_group_id", product_group_id)\
                    .get()
                
                if not group_products:
                    return ResponseService.response("NOT_FOUND", [], "No products found in this group.")
                
                # Extract product IDs
                product_ids = [gp["product_id"] for gp in group_products]
                
                # Step 2: Get vendor_product_ids from core_product_vendor_products where product_id in product_ids
                vendor_product_mappings = QueryBuilderService("core_product_vendor_products")\
                    .select("vendor_product_id")\
                    .whereIn("product_id", product_ids)\
                    .get()
                
                if not vendor_product_mappings:
                    return ResponseService.response("NOT_FOUND", [], "No vendor products found for these products.")
                
                # Extract vendor product IDs
                vendor_product_ids = [vpm["vendor_product_id"] for vpm in vendor_product_mappings]
                
                # Step 3: Get all documents from core_product_document_types where vendor_product_id in vendor_product_ids
                all_docs = ProductDocumentType.objects.filter(vendor_product_id__in=vendor_product_ids)

            # Store passed docs
            for doc_type_id_str, doc_info in values.items():
                try:
                    doc_type_id = int(doc_type_id_str)
                    if not all_docs.filter(id=doc_type_id).exists():
                        continue
                    
                    doc_obj, created = PolicyRequestDocument.objects.update_or_create(
                        policy_base_id=policy_base_id,
                        document_type_id=doc_type_id,
                        defaults={"value": doc_info}
                    )
                    
                    # Store the document value in our response object
                    stored_documents[doc_type_id_str] = doc_obj.value
                except ValueError:
                    continue


        # Fetch comprehensive policy information for both notifications
        print(f"\n{'='*80}")
        print(f"NOTIFICATION PROCESS STARTED")
        print(f"Request Policy ID: {request_policy_id}")
        print(f"Policy Base ID: {policy_base_id}")
        print(f"{'='*80}")
        
        try:
            # Fetch detailed policy information including risk type and insurer
            print(f"DEBUG: Fetching policy details for request_policy_id={request_policy_id}")
            policy_details = (
                QueryBuilderService("crmp_request_policies as rp")
                .leftJoin("crmp_policy_base as pb", "pb.id", "rp.policy_base_id")
                .leftJoin("core_customers as customer", "customer.id", "pb.customer_id")
                .leftJoin("crm_opportunities as opp", "opp.id", "pb.lead_id")
                .leftJoin("core_users as account_mgr", "account_mgr.id", "opp.account_manager_id")
                .leftJoin("core_vendor_products as product", "product.id", "pb.product_id")
                .leftJoin("core_product_groups as product_group", "product_group.id", "pb.product_group_id")
                .leftJoin("crmp_request_types as req_type", "req_type.id", "pb.request_type_id")
                .leftJoin("crm_opportunity_types as risk_type", "risk_type.id", "pb.risk_type_id")
                .leftJoin("core_service_providers as insurer", "insurer.id", "pb.insurer_id")
                .select(
                    "rp.id as request_policy_id",
                    "rp.policy_request_id",
                    "pb.id as policy_base_id",
                    "pb.premium_amount",
                    "pb.sum_insured",
                    "customer.name as customer_name",
                    "customer.id as customer_id",
                    "opp.id as lead_id",
                    "opp.title as lead_title",
                    "account_mgr.id as account_manager_id",
                    "account_mgr.display_name as account_manager_name",
                    "account_mgr.email as account_manager_email",
                    "product.name as product_name",
                    "product_group.name as product_group_name",
                    "req_type.name as request_type_name",
                    "risk_type.title as risk_type_name",
                    "insurer.name as insurer_name"
                )
                .where("rp.id", request_policy_id)
                .first()
            )
            
            print(f"DEBUG: Policy details fetched: {policy_details is not None}")
            if policy_details:
                print(f"DEBUG: Policy details keys: {list(policy_details.keys()) if policy_details else 'None'}")

            if policy_details:
                # Extract all details for notification
                request_id = policy_details.get("policy_request_id", f"PR-{request_policy_id}")
                customer_name = policy_details.get("customer_name", "Unknown Customer")
                lead_title = policy_details.get("lead_title", "")
                product_display = policy_details.get("product_group_name") or policy_details.get("product_name", "N/A")
                request_type = policy_details.get("request_type_name", "Policy")
                risk_type_name = policy_details.get("risk_type_name", "")
                insurer_name = policy_details.get("insurer_name", "")
                premium_amount = policy_details.get("premium_amount", 0)
                notification_customer_id = policy_details.get("customer_id") or data.get("customer_id")
                
                print(f"DEBUG: Extracted notification data:")
                print(f"  Request ID: {request_id}")
                print(f"  Customer Name: {customer_name}")
                print(f"  Request Type: {request_type}")
                print(f"  Product: {product_display}")
                print(f"  Risk Type: {risk_type_name}")
                print(f"  Insurer: {insurer_name}")
                print(f"  Customer ID for notification: {notification_customer_id}")
                
                # Format premium amount with currency
                formatted_premium = f"${premium_amount:,.2f}" if premium_amount else "N/A"
                
                # Create approval link (adjust URL based on your frontend routing)
                approval_link = f"{settings.FRONTEND_URL}/approvals/policy/{policy_base_id}" if hasattr(settings, 'FRONTEND_URL') else f"/approvals/policy/{policy_base_id}"
                
                # Build comprehensive notification message in the format: 
                # "Quotation: New quotation approval request QR-00168 for Umakaran Uma - Products: home insurance - Insurance: apptimus"
                message_parts = [f"{request_type}: New {request_type.lower()} approval request {request_id} for {customer_name}"]
                
                # Add product information
                if product_display and product_display != "N/A":
                    message_parts.append(f"Product: {product_display}")
                
                # Add risk type if available
                if risk_type_name:
                    message_parts.append(f"Risk Type: {risk_type_name}")
                
                # Add insurer if available
                if insurer_name:
                    message_parts.append(f"Insurance: {insurer_name}")
                
                # Add premium
                message_parts.append(f"Premium: {formatted_premium}")
                
                # Join all parts with " - "
                notification_message = " - ".join(message_parts)
                
                # Create detailed message for account manager (multi-line format)
                detailed_message = (
                    f"{request_type}: New {request_type.lower()} approval request\n\n"
                    f"Request ID: {request_id}\n"
                    f"Customer: {customer_name}\n"
                )
                
                if lead_title:
                    detailed_message += f"Opportunity: {lead_title}\n"
                
                if product_display and product_display != "N/A":
                    detailed_message += f"Product: {product_display}\n"
                
                if risk_type_name:
                    detailed_message += f"Risk Type: {risk_type_name}\n"
                
                if insurer_name:
                    detailed_message += f"Insurance Provider: {insurer_name}\n"
                
                detailed_message += (
                    f"Premium: {formatted_premium}\n"
                    f"\nPlease review and approve this {request_type.lower()} request."
                )
                
                # Send notification to requester (the person who created the request)
                print(f"\nDEBUG: Checking notification_customer_id: {notification_customer_id}")
                if notification_customer_id:
                    print(f"DEBUG: notification_customer_id is valid, proceeding with requester notification")
                    try:
                        print(f"\n{'='*80}")
                        print(f"Sending notification to Requester (User ID: {user.id if user else 'N/A'})")
                        result = NotificationService.generate_notification(
                            type_code="policy",
                            title=f"{request_type} Approval Request - {request_id}",
                            meta_data={
                                "policy_base_id": policy_base_id,
                                "request_policy_id": request_policy_id,
                                "request_id": request_id,
                                "request_type": request_type,
                                "customer_name": customer_name,
                                "product_name": product_display,
                                "risk_type": risk_type_name,
                                "insurer_name": insurer_name,
                                "premium_amount": str(premium_amount),
                                "approval_link": approval_link
                            },
                            message=notification_message,
                            customer_id=notification_customer_id,
                user_id=user.id if user else None
            )
                        
                        # Check if notification was successful
                        notification_data = (result or {}).get("data") or (result or {}).get("Data") or {}
                        if _is_notification_success(result):
                            print(f" NOTIFICATION SUCCESS - Requester Notification Created")
                            print(f"{'='*80}")
                            print(f"Notification Details Stored in Database:")
                            print(f"   Notification ID: {notification_data.get('id', 'N/A')}")
                            print(f"   Title: {request_type} Approval Request - {request_id}")
                            print(f"   Message: {notification_message[:100]}{'...' if len(notification_message) > 100 else ''}")
                            print(f"   Customer ID: {notification_customer_id}")
                            print(f"   User ID: {user.id if user else None}")
                            print(f"   Type Code: policy")
                            print(f"   Metadata Keys: {list(result.get('data', {}).get('metadata', {}).keys()) if 'metadata' in str(result.get('data', {})) else 'stored'}")
                            print(f"{'='*80}\n")
                        else:
                            print(f" NOTIFICATION FAILED - Requester Notification")
                            print(f"   Error: {(result or {}).get('message') or (result or {}).get('Message') or 'Unknown error'}")
                            print(f"{'='*80}\n")
                    except Exception as notify_exc:
                        print(f"NOTIFICATION EXCEPTION - Requester Notification Failed")
                        print(f"   Error: {notify_exc}")
                        print(f"{'='*80}\n")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"DEBUG: Cannot send requester notification - notification_customer_id is None")
                    print(f"  - policy_details customer_id: {policy_details.get('customer_id')}")
                    print(f"  - data customer_id: {data.get('customer_id')}")
                
                    # Get account manager ID (either from lead or fallback to request_by)
                    account_manager_id = policy_details.get("account_manager_id")
                    
                    # If no account manager in lead, try to get from sales agent's team
                    if not account_manager_id and data.get("lead_id"):
                        # Try to get account manager from the sales agent's team
                        lead_details = QueryBuilderService("crm_opportunities")\
                            .select("sales_agent_id")\
                            .where("id", data.get("lead_id"))\
                            .first()
                        
                        if lead_details and lead_details.get("sales_agent_id"):
                            # Try to get team manager for the sales agent (if table exists)
                            try:
                                team_member = QueryBuilderService("core_team_users")\
                                    .leftJoin("core_teams", "core_teams.id", "core_team_users.team_id")\
                                    .select("core_teams.manager_id")\
                                    .where("core_team_users.user_id", lead_details["sales_agent_id"])\
                                    .first()
                                
                                if team_member and team_member.get("manager_id"):
                                    account_manager_id = team_member["manager_id"]
                                    # Fetch account manager details
                                    account_mgr = QueryBuilderService("core_users")\
                                        .select("id", "display_name", "email")\
                                        .where("id", account_manager_id)\
                                        .first()
                                    
                                    if account_mgr:
                                        policy_details["account_manager_id"] = account_mgr["id"]
                                        policy_details["account_manager_name"] = account_mgr["display_name"]
                                        policy_details["account_manager_email"] = account_mgr["email"]
                            except Exception as e:
                                print(f"DEBUG: core_team_users table not available: {str(e)}")
                                # Skip team-based account manager lookup
                                pass
                
                # Send notification to account manager if exists
                if account_manager_id and notification_customer_id:
                    try:
                        print(f"\n{'='*80}")
                        print(f"📧 Sending notification to Account Manager (ID: {account_manager_id})")
                        result = NotificationService.generate_notification(
                            type_code="policy_approval",
                            title=f"{request_type} Approval Request - {request_id}",
                            meta_data={
                                "policy_base_id": policy_base_id,
                                "request_policy_id": request_policy_id,
                                "request_id": request_id,
                                "request_type": request_type,
                                "approval_link": approval_link,
                                "customer_name": customer_name,
                                "product_name": product_display,
                                "risk_type": risk_type_name,
                                "insurer_name": insurer_name,
                                "premium_amount": str(premium_amount),
                                "lead_id": policy_details.get("lead_id"),
                                "action_required": "approval"
                            },
                            message=detailed_message,
                            customer_id=notification_customer_id,
                            user_id=account_manager_id
                        )
                        
                        # Check if notification was successful
                        notification_data = (result or {}).get("data") or (result or {}).get("Data") or {}
                        if _is_notification_success(result):
                            print(f"✅ NOTIFICATION SUCCESS - Account Manager Notification Created")
                            print(f"{'='*80}")
                            print(f"📋 Notification Details Stored in Database:")
                            print(f"   Notification ID: {notification_data.get('id', 'N/A')}")
                            print(f"   Title: {request_type} Approval Request - {request_id}")
                            print(f"   Message: {detailed_message[:100]}{'...' if len(detailed_message) > 100 else ''}")
                            print(f"   Customer ID: {notification_customer_id}")
                            print(f"   User ID (Account Manager): {account_manager_id}")
                            print(f"   Type Code: policy_approval")
                            print(f"   Action Required: approval")
                            print(f"   Approval Link: {approval_link}")
                            print(f"   Metadata Keys: {list(result.get('data', {}).get('metadata', {}).keys()) if 'metadata' in str(result.get('data', {})) else 'stored'}")
                            print(f"{'='*80}\n")
                        else:
                            print(f"❌ NOTIFICATION FAILED - Account Manager Notification")
                            print(f"   Error: {(result or {}).get('message') or (result or {}).get('Message') or 'Unknown error'}")
                            print(f"{'='*80}\n")
                    except Exception as am_notify_exc:
                        print(f"❌ NOTIFICATION EXCEPTION - Account Manager Notification Failed")
                        print(f"   Error: {am_notify_exc}")
                        print(f"{'='*80}\n")
                        import traceback
                        traceback.print_exc()
                elif not notification_customer_id:
                    print(f"⚠ Cannot send notification: No customer_id found for policy request {request_id}")
                else:
                    print(f"⚠ No Account Manager found for policy request {request_id}. Notification not sent.")
            else:
                print(f"\n{'='*80}")
                print(f"ERROR: Could not fetch policy details for notification")
                print(f"Request Policy ID: {request_policy_id}")
                print(f"Policy Base ID: {policy_base_id}")
                print(f"{'='*80}\n")
                
        except Exception as approval_notify_exc:
            print(f"\n{'='*80}")
            print(f"EXCEPTION in notification process: {approval_notify_exc}")
            print(f"{'='*80}\n")
            import traceback
            traceback.print_exc()

        if created:
            update_customer_contact_info(data)

        if "insurer_notes" in data and data["insurer_notes"]:
            handle_entity_notes(entity_id, [{
                "note": data["insurer_notes"],
                "created_by_id": user.id if user else None,
                "created_at": now
            }], is_update=False)

        # --- Policy Inheritance Logic ---
        # Store inheritance data if it's a renewal (is_renewal = 1) OR if creating from request with valid lead_id
        should_create_inheritance = is_renewal
        
        # Initialize request_policy variable
        request_policy = None
        request_entity_id = None
        
        # Check if we should create inheritance for request-based policies
        if not should_create_inheritance:
            # Check if the policy_base has a lead_id that corresponds to an issued_policy_id in opportunities
            policy_base_id_param = data.get("policy_base_id")
            if policy_base_id_param:
                print(f"DEBUG: Checking if policy_base {policy_base_id_param} has valid lead_id for inheritance")
                
                # Get lead_id from policy_base
                policy_base = QueryBuilderService("crmp_policy_base")\
                    .select("lead_id")\
                    .where("id", policy_base_id_param)\
                    .first()
                
                if policy_base and policy_base.get("lead_id"):
                    lead_id_from_policy_base = policy_base.get("lead_id")
                    print(f"DEBUG: Found lead_id from policy_base: {lead_id_from_policy_base}")
                    
                    # Check if this lead_id has an issued_policy_id in opportunities
                    opportunity = QueryBuilderService("crm_opportunities")\
                        .select("issued_policy_id")\
                        .where("id", lead_id_from_policy_base)\
                        .first()
                    
                    if opportunity and opportunity.get("issued_policy_id"):
                        should_create_inheritance = True
                        print(f"DEBUG: Valid lead_id found with issued_policy_id: {opportunity.get('issued_policy_id')} - will create inheritance")
                    else:
                        print(f"DEBUG: No issued_policy_id found for lead_id {lead_id_from_policy_base} - skipping inheritance")
                else:
                    print(f"DEBUG: No lead_id found in policy_base {policy_base_id_param} - skipping inheritance")
        
        if should_create_inheritance:
            try:
                print(f"DEBUG: Processing inheritance for request policy {request_policy_id} (is_renewal: {is_renewal})")
                
                # Find the original issued_policy_id to inherit from
                original_issued_policy_id = None
                
                # Method 1: Check if lead_id is provided (this is the opportunity_id in request policy context)
                lead_id = data.get("lead_id")
                if lead_id:
                    print(f"DEBUG: Looking for original policy via lead_id: {lead_id}")
                    opportunity = QueryBuilderService("crm_opportunities")\
                        .select("issued_policy_id")\
                        .where("id", lead_id)\
                        .first()
                    
                    if opportunity and opportunity.get("issued_policy_id"):
                        original_issued_policy_id = opportunity.get("issued_policy_id")
                        print(f"DEBUG: Found original policy via lead_id: {original_issued_policy_id}")
                
                # Method 2: Check if opportunity_id is provided (alternative field name)
                if not original_issued_policy_id:
                    opportunity_id = data.get("opportunity_id")
                    if opportunity_id:
                        print(f"DEBUG: Looking for original policy via opportunity_id: {opportunity_id}")
                        opportunity = QueryBuilderService("crm_opportunities")\
                            .select("issued_policy_id")\
                            .where("id", opportunity_id)\
                            .first()
                        
                        if opportunity and opportunity.get("issued_policy_id"):
                            original_issued_policy_id = opportunity.get("issued_policy_id")
                            print(f"DEBUG: Found original policy via opportunity_id: {original_issued_policy_id}")
                
                # Method 3: Check if lea_id is provided (alternative field name for opportunity_id)
                if not original_issued_policy_id:
                    lea_id = data.get("lea_id")
                    if lea_id:
                        print(f"DEBUG: Looking for original policy via lea_id: {lea_id}")
                        opportunity = QueryBuilderService("crm_opportunities")\
                            .select("issued_policy_id")\
                            .where("id", lea_id)\
                            .first()
                        
                        if opportunity and opportunity.get("issued_policy_id"):
                            original_issued_policy_id = opportunity.get("issued_policy_id")
                            print(f"DEBUG: Found original policy via lea_id: {original_issued_policy_id}")
                
                # Method 4: Check if policy_base_id is provided (fallback)
                if not original_issued_policy_id:
                    policy_base_id_param = data.get("policy_base_id")
                    if policy_base_id_param:
                        print(f"DEBUG: Looking for original policy via policy_base_id: {policy_base_id_param}")
                        original_policy = QueryBuilderService("crmp_issued_policies")\
                            .select("id")\
                            .where("policy_base_id", policy_base_id_param)\
                            .first()
                        
                        if original_policy:
                            original_issued_policy_id = original_policy.get("id")
                            print(f"DEBUG: Found original policy via policy_base_id: {original_issued_policy_id}")
                        else:
                            print(f"DEBUG: No issued policy found for policy_base_id: {policy_base_id_param}")
                
                # Create inheritance record if we found the original policy
                if original_issued_policy_id:
                    print(f"DEBUG: Creating inheritance record - ORIGINAL policy: {original_issued_policy_id}, NEW request policy: {request_policy_id}")
                    
                    # Get the correct entity_id for inheritance - use the entity_id from the newly created request policy (or entity_id when updating existing)
                    inheritance_entity_id = (created.get("entity_id") if (created and isinstance(created, dict)) else entity_id)
                    print(f"DEBUG: Using entity_id from newly created request policy: {inheritance_entity_id}")
                    
                    # Prepare inheritance data - CORRECT: issued_policy_id should be the ORIGINAL policy
                    inheritance_data = {
                        "issued_policy_id": original_issued_policy_id,  # This is the OLD/ORIGINAL policy we're inheriting from
                        "entity_id": inheritance_entity_id,  # This is the entity_id from the NEW request policy
                    }
                    
                    # Add optional inheritance fields if provided
                    if "start_date" in data:
                        inheritance_data["start_date"] = data["start_date"]
                    elif "policy_start_date" in data:
                        inheritance_data["start_date"] = data["policy_start_date"]
                    else:
                        # Provide default start_date if not provided
                        inheritance_data["start_date"] = datetime.now()
                    
                    if "policy_effective_date" in data and data["policy_effective_date"] and data["policy_effective_date"].strip():
                        inheritance_data["policy_effective_date"] = data["policy_effective_date"]
                    
                    # Insert inheritance record
                    inheritance_created = QueryBuilderService("crmp_issued_policies_inheritance").insert(inheritance_data)
                    if inheritance_created:
                        print(f"DEBUG: Successfully created policy inheritance record")
                        print(f"DEBUG: Inheritance record links ORIGINAL policy {original_issued_policy_id} to NEW request policy {request_policy_id}")
                        print(f"DEBUG: This means policy {original_issued_policy_id} is being renewed/replaced by request policy {request_policy_id}")
                    else:
                        print(f"DEBUG: Failed to create policy inheritance record")
                else:
                    print(f"WARNING: No original policy found for renewal inheritance. lead_id: {lead_id}, opportunity_id: {data.get('opportunity_id')}, lea_id: {data.get('lea_id')}, policy_base_id: {data.get('policy_base_id')}")
                
            except Exception as e:
                print(f"ERROR: Failed to create policy inheritance record: {str(e)}")
                # Don't fail the entire operation for inheritance errors

        # Prepare response data with stored documents
        print(f"DEBUG: Preparing response data...")
        print(f"DEBUG: request_policy_id: {request_policy_id}")
        print(f"DEBUG: stored_documents: {stored_documents}")
        
        # Fetch the created record for response
        created_record = QueryBuilderService("crmp_request_policies").where("id", request_policy_id).first()
        print(f"DEBUG: created_record fetched: {created_record is not None}")
        
        response_data = created_record if created_record else {}
        if stored_documents:
            response_data["stored_documents"] = stored_documents
            
        print(f"DEBUG: Final response_data: {response_data}")
        print(f"DEBUG: About to return SUCCESS response")
            
        return ResponseService.response("SUCCESS", response_data, "default_create_success_msg")


def validate_risk_ids_structure(risk_ids, customer_id, risk_type_ids):
    """
    Validate the risk_ids structure: {"risk_type_id": [risk_id1, risk_id2, ...]}
    
    Args:
        risk_ids: Dictionary with risk_type_ids as keys and arrays of risk_ids as values
        customer_id: Customer ID to validate against
        risk_type_ids: Array of risk_type_ids extracted from the risk_ids object keys
    
    Returns:
        dict: Validation errors if any, empty dict if valid
    """
    errors = {}
    
    # 1. Validate that risk_ids is not null/empty
    if not risk_ids:
        errors["risk_ids"] = ["Please select at least one risk for the policy request"]
        return errors
    
    # 2. Validate that risk_ids is a dictionary
    if not isinstance(risk_ids, dict):
        errors["risk_ids"] = ["Risk selection format is invalid. Please select risks properly."]
        return errors
    
    # 3. Validate each risk_type_id and its associated risk_ids
    for risk_type_id_str, risk_id_list in risk_ids.items():
        try:
            risk_type_id = int(risk_type_id_str)
        except (ValueError, TypeError):
            if "risk_ids" not in errors:
                errors["risk_ids"] = []
            errors["risk_ids"].append(f"Invalid risk type selection: {risk_type_id_str}")
            continue
        
        # Validate that risk_type_id exists in the database and get its name
        risk_type_info = QueryBuilderService("crm_opportunity_types").where("id", risk_type_id).first()
        if not risk_type_info:
            if "risk_ids" not in errors:
                errors["risk_ids"] = []
            errors["risk_ids"].append(f"Selected risk type (ID: {risk_type_id}) does not exist")
            continue
        
        risk_type_name = risk_type_info.get("title", f"Risk Type {risk_type_id}")
        
        # Validate risk_id_list is not null/empty
        if not risk_id_list:
            if "risk_ids" not in errors:
                errors["risk_ids"] = []
            errors["risk_ids"].append(f"Please select at least one risk for '{risk_type_name}'")
            continue
        
        # Validate that risk_id_list is an array
        if not isinstance(risk_id_list, list):
            if "risk_ids" not in errors:
                errors["risk_ids"] = []
            errors["risk_ids"].append(f"Invalid risk selection format for '{risk_type_name}'")
            continue
        
        # Validate each risk_id in the list
        for risk_id in risk_id_list:
            try:
                risk_id_int = int(risk_id)
            except (ValueError, TypeError):
                if "risk_ids" not in errors:
                    errors["risk_ids"] = []
                errors["risk_ids"].append(f"Invalid risk ID '{risk_id}' selected for '{risk_type_name}'")
                continue
            
            # Validate that the risk exists and belongs to the correct customer and risk_type
            risk_exists = QueryBuilderService("crm_risks") \
                .where("id", risk_id_int) \
                .where("customer_id", customer_id) \
                .where("risk_type_id", risk_type_id) \
                .first()
            
            if not risk_exists:
                if "risk_ids" not in errors:
                    errors["risk_ids"] = []
                errors["risk_ids"].append(f"Selected risk (ID: {risk_id_int}) for '{risk_type_name}' is not available for this customer")
    
    return errors


def get_request_policy_rules():
    return {
        "lead_id": "nullable|exists:crm_opportunities,id",
        "quotation_document_name": "string",
        "quotation_document": "nullable",
        "insurer_id": "integer|required|exists:core_service_providers,id",
        "insurer_notes": "string",
        # "quotation_expiry_date": "date",
        "quotation_issued_date": "date|before_or_equal:policy_start_date",
        "request_by_id": "integer|exists:core_users,id",
        "premium_amount": "decimal",
        "customer_id": "integer|required|exists:core_customers,id",
        # "customer_primary_contact": "string|required",
        # "customer_email": "string|required|email",
        # "customer_address": "string|required",
        "policy_start_date": "date|required",
        "policy_expiry_date": "date|required|after:policy_start_date",
        "payment_mode_id": "nullable|exists:crmp_payment_plans,id",
        "sum_insured": "decimal|required",
        # "request_type_id": "integer|required|exists:crmp_request_types,id",
        "risk_type_ids": "required|array|min:1",
        "risk_type_ids.*": "integer|exists:crm_opportunity_types,id",
        "product_id": "nullable|required_without:product_group_id|exists:core_vendor_products,id",
        "product_group_id": "nullable|required_without:product_id|exists:core_product_groups,id",
        "product_type": "required|string|in:product,group",
        "coverage_type_id": "nullable|exists:crmp_coverage_types,id",
        "quotation_notes": "string",
        "is_policy": "boolean",
        "risk_ids": "required|object",  
        "sales_agent_id": "required|exists:core_users,id",
        "account_manager_id": "nullable|integer|exists:core_users,id",

    }

def update_customer_contact_info(data):
    customer = (
        QueryBuilderService("core_customers")
        .select("primary_contact_id")
        .where("id", data["customer_id"])
        .first()
    )
    customer_update = None
    if customer:
        customer_update = (
            QueryBuilderService("core_contacts")
            .where("id", customer["primary_contact_id"])
            # .update(
            #     # {
            #     #     "primary_contact": data["customer_primary_contact"],
            #     #     "email": data["customer_email"],
            #     #     "address": data["customer_address"],
            #     # }
            # )
        )
    return {"customer_update": customer_update}

@csrf_exempt
@api_view(['POST'])
def policy_trigger(request):
    data = request.data
    rules_def = {
        "entity_data": "required",
        "entity_type": "required",
        "action": "required",
        "email_data": "optional",
        "documents": "optional",
    }
    errors = ValidatorService.validate(data, rules_def)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    entity_id = data.get("entity_data", {}).get("id")
    if not entity_id:
        return ResponseService.response("VALIDATION_ERROR", "Missing entity_id inside entity_data.", Error.VALIDATION_ERROR)

    entity_row = QueryBuilderService("core_entities").select("id", "type").where("id", entity_id).first()
    if not entity_row or (entity_row.get("type") or "").strip().lower() != "policy":
        return ResponseService.response("VALIDATION_ERROR", "Entity type mismatch or not found.", Error.VALIDATION_ERROR)

    entity_type = (data.get("entity_type") or "").strip()
    action = (data.get("action") or "").strip()
    
    # Extract optional email and documents
    email_data = data.get("email_data", {})
    
    # Extract documents from email_data (only documents, not defaultDocuments)
    documents = email_data.get("documents", [])

    print("Email:", email_data)
    print("Documents:", documents)

    # Fetch approval rules
    ruleCheck = QueryBuilderService('core_entity_approval_rules')\
        .where('entity_type', entity_type)\
        .where('action', action)\
        .first()

    if not ruleCheck or not ruleCheck.get("rule"):
        QueryBuilderService('core_entities')\
            .where('id', entity_id)\
            .update({'approvel_status': True})
        return ResponseService.response("SUCCESS", "No rule found. Marked approved.", Message.DATA_CREATED)

    try:
        parsed_rule = json.loads(ruleCheck["rule"])
        rules = parsed_rule.get("rules", [])
    except Exception:
        return ResponseService.response("VALIDATION_ERROR", "Invalid rule format.", Error.VALIDATION_ERROR)

    if not rules:
        QueryBuilderService('core_entities')\
            .where('id', entity_id)\
            .update({'approvel_status': True})
        return ResponseService.response("SUCCESS", "No approval rules defined.", Message.DATA_CREATED)

    # Respect APPROVAL_PERMISSIONS: if policy_request_approval is false, mark approved and skip approval flow
    approval_required = _is_policy_request_approval_required()
    if not approval_required:
        QueryBuilderService('core_entities')\
            .where('id', entity_id)\
            .update({'approvel_status': True})
        QueryBuilderService("core_entity_approvals").insert({
            "entity_id": entity_id,
            "user": sorted(rules, key=lambda r: r.get("level", 0))[0].get("user") if rules else None,
            "role": None,
            "level": 1,
            "status": "approved",
            "remarks": None
        })
        # Fall through to save email_data/documents below, then return before approval notifications
        sorted_rules = []
    else:
        # Update approvel_status (needs approval)
        QueryBuilderService('core_entities')\
            .where('id', entity_id)\
            .update({'approvel_status': False})

        # Insert approvals from rules
        sorted_rules = sorted(rules, key=lambda r: r.get("level", 0))
        min_level = sorted_rules[0]["level"]
        default_status = ruleCheck.get("default_status", "draft")

        for rule in sorted_rules:
            status = "pending" if rule.get("level") == min_level else default_status
            QueryBuilderService("core_entity_approvals").insert({
                "entity_id": entity_id,
                "user": rule.get("user"),
                "role": rule.get("role"),
                "level": rule.get("level"),
                "status": status,
                "remarks": None
            })

    # Set dummy email_data if not provided
    if not email_data:
        email_data = {
            "subject": "No Subject",
            "body": "No content available."
        }

    # Create cleaned email_data (remove documents and defaultDocuments)
    cleaned_email_data = {
        "subject": email_data.get("subject", "No Subject"),
        "body": email_data.get("body", "No content available.")
    }

    # Create the storage format as requested
    storage_data = {
        "documents": documents,
        "email_data": cleaned_email_data
    }

    # Save the data in the request policies table
    try:
        QueryBuilderService("crmp_request_policies").where("entity_id", entity_id).update({"email_data": json.dumps(storage_data)})
    except Exception:
        note = QueryBuilderService("core_entity_notes").select("id").where("entity_id", entity_id).first()
        if note:
            QueryBuilderService("core_entity_notes").where("id", note["id"]).update({"notes": json.dumps(storage_data)})
        else:
            QueryBuilderService("core_entity_notes").insert({"entity_id": entity_id, "notes": json.dumps(storage_data)})

    # Optionally store or send email and document metadata (example print only)
    if email_data:
        print("Storing Email Subject:", email_data.get("subject"))
        print("Storing Email Body:", email_data.get("body"))

    if documents:
        for doc in documents:
            print(f"Doc Name: {doc.get('name')} | Type: {doc.get('type')} | Path: {doc.get('doc')}")

    # Send notification to account managers (approvers)
    try:
        from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
        
        # Get policy request details for notification
        policy_request = QueryBuilderService("crmp_request_policies as rp")\
            .leftJoin("crmp_policy_base as pb", "pb.id", "rp.policy_base_id")\
            .leftJoin("core_customers as customer", "customer.id", "pb.customer_id")\
            .leftJoin("crm_opportunities as opp", "opp.id", "pb.lead_id")\
            .leftJoin("core_vendor_products as product", "product.id", "pb.product_id")\
            .leftJoin("core_product_groups as product_group", "product_group.id", "pb.product_group_id")\
            .leftJoin("crmp_request_types as req_type", "req_type.id", "pb.request_type_id")\
            .select(
                "rp.policy_request_id",
                "rp.id as request_policy_id",
                "pb.id as policy_base_id",
                "pb.premium_amount",
                "customer.name as customer_name",
                "customer.id as customer_id",
                "product.name as product_name",
                "product_group.name as product_group_name",
                "req_type.name as request_type"
            )\
            .where("rp.entity_id", entity_id)\
            .first()
        
        if policy_request:
            # Get all approvers from the approval rules
            approvers = []
            for rule in sorted_rules:
                if rule.get("user"):
                    approvers.append(rule.get("user"))
            
            # Send notification to each approver
            for approver_user_id in approvers:
                try:
                    product_display = policy_request.get("product_name") or policy_request.get("product_group_name") or "N/A"
                    
                    notification_message = (
                        f"Policy approval request for {policy_request.get('customer_name', 'Unknown Customer')}\n"
                        f"Request ID: {policy_request.get('policy_request_id')}\n"
                        f"Product: {product_display}\n"
                        f"Premium: {policy_request.get('premium_amount', 'N/A')}\n"
                        f"\nPlease review and approve this policy request."
                    )
                    
                    result = NotificationService.generate_notification(
                        type_code="policy_approval",
                        title=f"{policy_request.get('request_type', 'Policy')} Approval Request",
                        meta_data={
                            "policy_base_id": policy_request.get("policy_base_id"),
                            "request_policy_id": policy_request.get("request_policy_id"),
                            "request_id": policy_request.get("policy_request_id"),
                            "action_required": "approval",
                            "entity_id": entity_id
                        },
                        message=notification_message,
                        customer_id=policy_request.get("customer_id"),
                        user_id=approver_user_id
                    )
                    
                    if _is_notification_success(result):
                        print(f"Approval notification sent to approver (User ID: {approver_user_id})")
                    else:
                        print(f"Failed to send notification to approver (User ID: {approver_user_id})")
                        
                except Exception as approver_notify_exc:
                    print(f"Error sending notification to approver {approver_user_id}: {approver_notify_exc}")
        else:
            print(f"Could not find policy request for entity_id {entity_id}")
            
    except Exception as notify_exc:
        print(f"Error in approval notification process: {notify_exc}")
        import traceback
        traceback.print_exc()

    return ResponseService.response("SUCCESS", "Policy approval routing initiated with email and document data.", Message.DATA_CREATED)



@api_view(["GET"])
def endorsement_chat_messages(request, endorsement_id: int):
    """
    GET /api/endorsement/<endorsement_id>/chat-messages

    Find the conversation for the given endorsement_id,
    then fetch all messages directly from the database using QueryBuilderService.

    The conversation is found in core_chat_conversations table where:
    - type_based_id = 'ER-{endorsement_id}'
    """
    try:
        # Get current user
        user = request.user if request.user.is_authenticated else None
        if not user:
            return ResponseService.response(
                "UNAUTHORIZED",
                None,
                "User not authenticated"
            )

        # Get user's email for comparison (kept same as policy version)
        user_email = getattr(user, 'email', '').strip().lower()

        # Try alternative email fields if the main email field is empty
        if not user_email:
            alternative_fields = ['username', 'system_email', 'gmail_email']
            for field in alternative_fields:
                alt_email = getattr(user, field, '').strip().lower()
                if alt_email and '@' in alt_email:
                    user_email = alt_email
                    break

        # Construct the type_based_id format: ER-{endorsement_id}
        type_based_id = f"ER-{endorsement_id}"

        # Get query parameters for pagination and filtering
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "").strip()
        sort_by = request.GET.get("sort_by", "sent_at")
        sort_dir = request.GET.get("sort_dir", "desc")
        filter_json = request.GET.get("filter", {})

        # Validate pagination parameters
        if page < 1:
            page = 1
        if limit < 1:
            limit = 10
        if limit > 100:
            limit = 100  # Safety cap

        # Find the conversation in core_chat_conversations table
        conversation = (
            QueryBuilderService("core_chat_conversations")
            .select(
                "id as conversation_id",
                "code as conversation_code",
                "type",
                "created_at",
                "gmail_thread_id",
                "insurer_id",
            )
            .where("type_based_id", type_based_id)
            .first()
        )

        if not conversation:
            return ResponseService.response(
                "SUCCESS",
                None,
                f"No conversation found for endorsement {endorsement_id}"
            )

        conversation_id = conversation["conversation_id"]

        # Define columns and configuration (same as policy)
        all_columns = [
            "id",
            "conversation_id",
            "gmail_message_id",
            "gmail_thread_id",
            "first_message_id",
            "from_email",
            "to_email",
            "subject",
            "body",
            "sent_at",
        ]

        allowed_filters = ["subject", "from_email", "to_email"]
        search_columns = ["subject", "body", "from_email", "to_email"]
        allowed_sorting_columns = ["sent_at", "id", "subject", "from_email"]

        # Build query using QueryBuilderService pattern
        query = (
            QueryBuilderService("core_email_messages")
            .select(*all_columns)
            .where("conversation_id", conversation_id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        # Get attachments for all messages
        messages = query.get("data", [])
        message_ids = [msg["id"] for msg in messages]
        attachments = []

        if message_ids:
            attachments_query = (
                QueryBuilderService("core_email_attachments")
                .select(
                    "id",
                    "email_message_id",
                    "file_name",
                    "file_url",
                    "content_type",
                    "size_bytes",
                    "gmail_attachment_id",
                    "is_image",
                    "created_at",
                )
                .whereIn("email_message_id", message_ids)
                .get()
            )
            attachments = attachments_query

        # Group attachments by message_id
        attachments_by_message = {}
        for attachment in attachments:
            mid = attachment["email_message_id"]
            attachments_by_message.setdefault(mid, []).append({
                "id": attachment["id"],
                "file_name": attachment["file_name"],
                "content_type": attachment["content_type"],
                "size_bytes": attachment["size_bytes"],
                "is_image": attachment["is_image"],
                "file_url": attachment["file_url"],
                "gmail_attachment_id": attachment["gmail_attachment_id"],
                "download_url": attachment["file_url"],
            })

        # Get insurer's email from the conversation
        insurer_email = None
        if conversation.get("insurer_id"):
            insurer_record = (
                QueryBuilderService("core_service_providers")
                .select("email")
                .where("id", conversation["insurer_id"])
                .first()
            )
            if insurer_record and insurer_record.get("email"):
                insurer_email = insurer_record["email"].strip().lower()
                print(f"[DEBUG] Found insurer email: {insurer_email}")
            else:
                print(f"[DEBUG] No insurer record found for insurer_id: {conversation['insurer_id']}")
        else:
            print(f"[DEBUG] No insurer_id in conversation: {conversation}")

        # Process messages to add type and sender_name
        for message in messages:
            # Add attachments
            message["attachments"] = attachments_by_message.get(message["id"], [])

            # Normalize email format
            def normalize_email(email_string):
                """Normalize email format to handle any remaining inconsistencies"""
                if not email_string:
                    return ""
                email_string = email_string.strip()
                # Handle "Name <email@domain.com>"
                if "<" in email_string and ">" in email_string:
                    start = email_string.find("<") + 1
                    end = email_string.find(">")
                    if start < end:
                        return email_string[start:end].strip().lower()
                return email_string.lower()

            # Get normalized emails
            from_email_raw = message.get("from_email", "")
            to_email_raw = message.get("to_email", "")

            from_email_normalized = normalize_email(from_email_raw)
            to_email_normalized = normalize_email(to_email_raw)

            # Determine message type based on insurer's email
            if insurer_email:
                if from_email_normalized == insurer_email:
                    # Insurer sent this message to us (insurer is sender)
                    message["type"] = "received"
                    print(f"[DEBUG] Message {message['id']}: received (insurer is sender)")
                elif to_email_normalized == insurer_email:
                    # We sent this message to the insurer (insurer is receiver)
                    message["type"] = "sent"
                    print(f"[DEBUG] Message {message['id']}: sent (insurer is receiver)")
                else:
                    # Default to received if no match
                    message["type"] = "received"
                    print(f"[DEBUG] Message {message['id']}: received (default) - from: {from_email_normalized}, to: {to_email_normalized}, insurer: {insurer_email}")
            else:
                # If no insurer email found, default to received
                message["type"] = "received"
                print(f"[DEBUG] Message {message['id']}: received (no insurer email)")

            # Sender name resolution
            sender_name = "Unknown"

            # Try extract from "Name <email>" format
            if "<" in from_email_raw and ">" in from_email_raw:
                name_part = from_email_raw.split("<")[0].strip()
                if name_part and name_part != from_email_normalized:
                    sender_name = name_part

            # DB lookups if still unknown
            if sender_name == "Unknown":
                user_record = (
                    QueryBuilderService("core_users")
                    .select("display_name", "email")
                    .where("email", from_email_normalized)
                    .first()
                )
                if user_record and user_record.get("display_name"):
                    sender_name = user_record.get("display_name")
                else:
                    service_provider_record = (
                        QueryBuilderService("core_service_providers")
                        .select("name", "email")
                        .where("email", from_email_normalized)
                        .first()
                    )
                    if service_provider_record and service_provider_record.get("name"):
                        sender_name = service_provider_record.get("name")
                    else:
                        sender_name = from_email_normalized.split("@")[0] if "@" in from_email_normalized else from_email_normalized

            message["sender_name"] = sender_name

        # Add conversation metadata to the response
        query["conversation_metadata"] = {
            "conversation_id": conversation_id,
            "conversation_code": conversation["conversation_code"],
            "type": conversation["type"],
            "created_at": conversation["created_at"],
            "gmail_thread_id": conversation["gmail_thread_id"],
            "endorsement_id": endorsement_id,
            "type_based_id": type_based_id,
        }

        return ResponseService.response(
            "SUCCESS",
            query,
            f"Chat messages retrieved successfully for endorsement {endorsement_id}"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )


@csrf_exempt
@api_view(["PUT"])
def request_policy_download_docs(request, request_policy_id):
    try:
        data = request.data

        rules = {
          "type": "required|in:insurer_policy,insurer_invoice,others",
          "document_url": "required",
          "document_name": "required",
          "document_type": "required",
        }

        rules = ValidatorService.validate(data, rules)
        if rules:
            return ResponseService.response("VALIDATION_ERROR", rules, Error.VALIDATION_ERROR)
        
        data["request_policy_id"] = request_policy_id
        request_policy_doc = QueryBuilderService("crmp_request_policy_docs").insert(data)
        if request_policy_doc:


            if data.get("type") in ["insurer_policy", "insurer_invoice"]:
                data_analyzer = analyze_insurer_policy(request_policy_doc)
                print(f"Data analyzer: {data_analyzer}")
                
                if data_analyzer and isinstance(data_analyzer, list) and len(data_analyzer) > 0:
                    # Store the entire analysis result as JSON
                    try:
                        QueryBuilderService("crmp_request_policy_docs").where("id", request_policy_doc["id"]).update({
                            "data_analysis": json.dumps(data_analyzer)
                        })
                        print("Data analysis stored successfully")
                    except Exception as update_error:
                        print(f"Error storing data analysis: {str(update_error)}")
                else:
                    print("No valid data analysis result to store")


            return ResponseService.response("SUCCESS", request_policy_doc, "download_successfull")

            
        else:
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Request policy download docs")


    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, f"Internal server error: {str(e)}")



DATA_ANALYZER = settings.DATA_ANALYZER
ENVOYS3URL = settings.ENVOYS3URL

def analyze_insurer_policy(request):
    try:
        document_url = request.get("document_url")
        if not document_url:
            print("No document_url provided")
            return None
            
        full_document_url = ENVOYS3URL + document_url
        document_type = "policy"

        payload = {
            "document_urls": [full_document_url], 
            "document_type": document_type
        }

        print("payload:", payload)

        response = requests.post(DATA_ANALYZER, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"API response received: {len(result) if isinstance(result, list) else 'not a list'}")
            return result
        else:
            print(f"API request failed with status {response.status_code}: {response.text}")
            return None
    except requests.exceptions.Timeout:
        print("API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {str(e)}")
        return None
    except Exception as e:
        print(f"Error analyzing insurer policy: {str(e)}")
        return None
    


@csrf_exempt
@api_view(["GET"])
def request_policy_data_analysis(request, request_policy_id):
    try:
        # Get data analysis from the database
        docs = QueryBuilderService("crmp_request_policy_docs")\
            .where("request_policy_id", request_policy_id)\
            .whereIn("type", ["insurer_policy", "insurer_invoice"])\
            .select("crmp_request_policy_docs.*")\
            .get()

        if not docs:
            return ResponseService.response("NOT_FOUND", None, "No data analysis found for this policy")

        # Initialize combined object
        combined_data = {
            "policy_details": {},
            "invoice_details": {}
        }
        
        for doc in docs:
            data_analysis = doc.get("data_analysis")
            doc_type = doc.get("type")
            
            if data_analysis:
                try:
                    # Parse JSON if it's a string
                    if isinstance(data_analysis, str):
                        analysis_data = json.loads(data_analysis)
                    else:
                        analysis_data = data_analysis
                    
                    # Extract specific details from the analysis
                    if isinstance(analysis_data, list) and len(analysis_data) > 0:
                        details = analysis_data[0].get("details", {})
                        policy_fields = details.get("policy_fields", {})
                        endorsement_fields = details.get("endorsement_fields", {})
                        
                        if doc_type == "insurer_policy":
                            # Policy details from insurer_policy documents
                            # Get document_info for fallback document_id
                            document_info = details.get("document_info", {})
                            document_number = document_info.get("document_number", "")
                            
                            # Use insurer_policy_id if available, otherwise use document_number
                            policy_id = policy_fields.get("insurer_policy_id", "")
                            if not policy_id and document_number:
                                policy_id = document_number
                            
                            combined_data["policy_details"] = {
                                "document_name": doc.get("document_name"),
                                "insurer_policy_id": policy_id,
                                "policy_issue_date": policy_fields.get("policy_issue_date", ""),
                                "start_date": policy_fields.get("start_date", ""),
                                "end_date": policy_fields.get("end_date", ""),
                                "credit_period_days": policy_fields.get("credit_period_days", ""),
                                "credit_age_days": policy_fields.get("credit_age_days", ""),
                                "sum_insured": policy_fields.get("sum_insured", ""),
                                "risk_type": policy_fields.get("risk_type", ""),
                                "payment_mode": policy_fields.get("payment_mode", ""),
                                "requested_by": policy_fields.get("requested_by", ""),
                                "sales_agent": policy_fields.get("sales_agent", ""),
                                "policy_document_url": doc.get("document_url"),
                                "policy_document_name": doc.get("document_name"),
                                "policy_document_type": doc.get("document_type"),
                            }
                        elif doc_type == "insurer_invoice":
                            # Invoice details from insurer_invoice documents
                            combined_data["invoice_details"] = {
                                "document_name": doc.get("document_name"),
                                "insurer_invoice_id": endorsement_fields.get("insurer_invoice_id", ""),
                                "insurer_invoice_number": endorsement_fields.get("insurer_invoice_number", ""),
                                "amount_or_cover_value": endorsement_fields.get("amount_or_cover_value", ""),
                                "invoice_document_url": doc.get("document_url"),
                                "invoice_document_name": doc.get("document_name"),
                                "invoice_document_type": doc.get("document_type"),
                            }
                        
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON for document {doc.get('id')}: {str(e)}")
                    continue
                except Exception as e:
                    print(f"Error extracting data for document {doc.get('id')}: {str(e)}")
                    continue

        # Check if we have any data
        if combined_data["policy_details"] or combined_data["invoice_details"]:
            return ResponseService.response("SUCCESS", combined_data, "Data analysis retrieved successfully")
        else:
            return ResponseService.response("NOT_FOUND", None, "No valid data analysis found")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, f"Internal server error: {str(e)}")


@csrf_exempt
@api_view(["GET"])
def draft_policies_list(request):
    """GET: List all draft policies from policy_base table"""
    action_type = "VIEW"
    action = ActionService.getAction("RequestPolicy", action_type)
    
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    
    try:
        # Get DRAFT status ID
        draft_status = QueryBuilderService("core_status")\
            .where("type", "policy_draft")\
            .where("module", "policy")\
            .select("id")\
            .first()
        
        if not draft_status:
            return ResponseService.response("NOT_FOUND", [], "DRAFT status not found in core_status table")
        
        draft_status_id = draft_status["id"]
        
        # Build query to get all draft policies from policy_base
        columns = [
            "pb.id as policy_base_id",
            "pb.customer_id",
            "pb.insurer_id",
            "pb.product_id",
            "pb.product_group_id",
            "pb.risk_type_id",
            "pb.request_type_id",
            "pb.request_by_id",
            "pb.lead_id",
            "pb.premium_amount",
            "pb.sum_insured",
            "pb.payment_mode_id",
            "pb.coverage_type_id",
            "pb.sales_agent_id",
            "pb.account_manager_id",
            "pb.policy_start_date",
            "pb.policy_expiry_date",
            "pb.quotation_issued_date",
            "pb.quotation_expiry_date",
            "pb.quotation_notes",
            "pb.quotation_document",
            "pb.quotation_document_name",
            "pb.quotation_id",
            "pb.quotation_code",
            "pb.status_id",
            # Get entity_id from request_policies or issued_policies if available
            "COALESCE(rp.entity_id, ip.entity_id) as entity_id",
            # Customer details
            "customer.name as customer_name",
            "customer.type as customer_type",
            "customer.logo as customer_logo",
            "customer_contact.email as customer_email",
            "customer_contact.primary_contact as customer_primary_contact",
            # Insurer details
            "insurer.name as insurer_name",
            # Product details
            "product.name as product_name",
            # Request type
            "req_type.name as request_type_name",
            # Risk type
            "risk_type.title as risk_type_name",
            # Sales agent
            "sales_agent.display_name as sales_agent_name",
            # Account manager
            "account_mgr.display_name as account_manager_name",
            # Status
            "status.name as status_name",
            "status.color as status_color",
            # Check if exists in request_policies
            "CASE WHEN rp.id IS NOT NULL THEN 'policy_request' WHEN ip.id IS NOT NULL THEN 'policy' ELSE NULL END as type",
            "rp.id as request_policy_id",
            "rp.policy_request_id as request_policy_code",
            "ip.id as issued_policy_id",
            "ip.brokerage_policy_id as issued_policy_code",
            # Created by information
            "created_by.display_name as created_by_name",
            "created_by.id as created_by_id",
            # Entity timestamps (created_at and updated_at from entity table)
            "COALESCE(rp_entity.created_at, ip_entity.created_at) as created_at",
            "COALESCE(rp_entity.updated_at, ip_entity.updated_at) as updated_at"
        ]
        
        query = QueryBuilderService("crmp_policy_base as pb")\
            .leftJoin("core_customers as customer", "customer.id", "pb.customer_id")\
            .leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")\
            .leftJoin("core_service_providers as insurer", "insurer.id", "pb.insurer_id")\
            .leftJoin("core_vendor_products as product", "product.id", "pb.product_id")\
            .leftJoin("crmp_request_types as req_type", "req_type.id", "pb.request_type_id")\
            .leftJoin("crm_opportunity_types as risk_type", "risk_type.id", "pb.risk_type_id")\
            .leftJoin("core_users as sales_agent", "sales_agent.id", "pb.sales_agent_id")\
            .leftJoin("core_users as account_mgr", "account_mgr.id", "pb.account_manager_id")\
            .leftJoin("core_status as status", "status.id", "pb.status_id")\
            .leftJoin("crmp_request_policies as rp", "rp.policy_base_id", "pb.id")\
            .leftJoin("crmp_issued_policies as ip", "ip.policy_base_id", "pb.id")\
            .leftJoin("core_entities as rp_entity", "rp_entity.id", "rp.entity_id")\
            .leftJoin("core_entities as ip_entity", "ip_entity.id", "ip.entity_id")\
            .leftJoin("core_users as created_by", "created_by.id", "COALESCE(rp_entity.created_by_id, ip_entity.created_by_id)")\
            .select(*columns)\
            .where("pb.status_id", draft_status_id)
        
        # Apply filters and pagination
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by") or "pb.id"
        sort_dir = request.GET.get("sort_dir") or "desc"
        
        allowed_filters = [
            "pb.customer_id",
            "pb.insurer_id",
            "pb.product_id",
            "customer.name",
            "insurer.name",
            "status.name"
        ]
        
        search_columns = [
            "customer.name",
            "insurer.name",
            "product.name",
            "rp.policy_request_id",
            "ip.brokerage_policy_id"
        ]
        
        query = query.apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        
        allowed_sorting_columns = ["pb.id", "pb.created_at", "customer.name", "insurer.name", "status.name"]
        data = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        
        # Format date fields
        if isinstance(data, dict) and "data" in data:
            for item in data["data"]:
                _format_date_fields(item)
        elif isinstance(data, list):
            for item in data:
                _format_date_fields(item)
        
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
        
    except Exception as e:
        import traceback
        print(f"ERROR in draft_policies_list: {str(e)}")
        print(traceback.format_exc())
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, f"Internal server error: {str(e)}")


@csrf_exempt
@api_view(["GET"])
def draft_policy_detail(request, policy_base_id):
    """GET: Get single draft policy by policy_base_id - Returns all details like request_policy_detail and issued_policy_detail"""
    action_type = "VIEW"
    action = ActionService.getAction("RequestPolicy", action_type)
    
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    
    try:
        # Get DRAFT status ID
        draft_status = QueryBuilderService("core_status")\
            .where("type", "policy_draft")\
            .where("module", "policy")\
            .select("id")\
            .first()
        
        if not draft_status:
            return ResponseService.response("NOT_FOUND", None, "DRAFT status not found in core_status table")
        
        draft_status_id = draft_status["id"]
        
        # Build comprehensive query similar to request_policy_detail and issued_policy_detail
        columns = [
            # Policy Base fields
            "pb.*",
            "pb.id as policy_base_id",
            "pb.premium_amount",
            "pb.sum_insured",
            "pb.quotation_issued_date",
            "pb.quotation_expiry_date",
            "pb.policy_start_date",
            "pb.policy_expiry_date",
            "pb.quotation_notes",
            "pb.quotation_document_name",
            "pb.quotation_document",
            "pb.quotation_document_size",
            
            # Get entity_id from request_policies or issued_policies if available
            "COALESCE(rp.entity_id, ip.entity_id) as entity_id",
            
            # Insurer/Service Provider details
            "insurer.name as insurer_company_name",
            "insurer.logo as insurer_company_logo",
            "insurer.email as insurer_email",
            "insurer.id as insurer_id",
            
            # Risk type
            "risk_type.title as risk_type",
            "risk_type.id as risk_type_id",
            "risk_type.description as risk_type_description",
            
            # Requested by
            "req_user.display_name as requested_by",
            "req_user.picture as requested_by_logo",
            "req_user.id as requested_by_id",
            
            # Status
            "status.name as status",
            "status.color as status_color",
            "status.type as status_type",
            "status.id as status_id",
            
            # Request type
            "request_type.name as request_type",
            "request_type.id as request_type_id",
            
            # Product
            "product.name as product_name",
            "product.id as product_id",
            
            # Product Group
            "product_group.name as product_group_name",
            "product_group.id as product_group_id",
            
            # Customer details
            "customer.name as customer_name",
            "customer.id as customer_id",
            "customer.logo as customer_logo",
            "customer.type as customer_type",
            "customer_contact.email as customer_email",
            "customer_contact.primary_contact as customer_primary_contact",
            "customer_contact.address as customer_address",
            
            # Coverage type
            "coverage_type.name as coverage_type",
            "coverage_type.id as coverage_type_id",
            
            # Payment plan
            "payment_plan.name as payment_plan",
            "payment_plan.id as payment_plan_id",
            
            # Sales agent
            "sales_agent.display_name as sales_agent_name",
            "sales_agent.id as sales_agent_id",
            "sales_agent.email as sales_agent_email",
            "sales_agent.picture as sales_agent_logo",
            
            # Account manager
            "account_mgr.display_name as account_manager_name",
            "account_mgr.id as account_manager_id",
            "account_mgr.email as account_manager_email",
            "account_mgr.picture as account_manager_logo",
            
            # Entity (created/updated by)
            "COALESCE(rp_entity.created_at, ip_entity.created_at) as created_at",
            "COALESCE(rp_entity.updated_at, ip_entity.updated_at) as updated_at",
            "created_by.display_name as created_by",
            "created_by.picture as created_by_logo",
            "created_by.id as created_by_id",
            "updated_by.display_name as updated_by",
            "updated_by.picture as updated_by_logo",
            "updated_by.id as updated_by_id",
            
            # Quotation (prefer stored values from policy_base, fallback to JOIN)
            "COALESCE(pb.quotation_id, quotations.id) as quotation_id",
            "COALESCE(pb.quotation_code, quotations.code) as quotation_code",
            
            # Entity notes (insurer notes)
            "entity_notes.notes as insurer_notes",
            
            # Check if exists in request_policies or issued_policies and determine type
            "CASE WHEN rp.id IS NOT NULL THEN 'policy_request' WHEN ip.id IS NOT NULL THEN 'policy' ELSE NULL END as type",
            
            # Request policy details (if exists)
            "rp.id as request_policy_id",
            "rp.policy_request_id as request_policy_code",
            "rp.policy_request_date",
            "rp.email_data as request_email_data",
            
            # Issued policy details (if exists)
            "ip.id as issued_policy_id",
            "ip.brokerage_policy_id as issued_policy_code",
            "ip.start_date as issued_start_date",
            "ip.end_date as issued_end_date",
            "ip.paid_amount as issued_paid_amount",
            "ip.premium_amount as issued_premium_amount",
            "ip.credit_period_days",
            "ip.credit_age_days",
            "ip.insurer_invoice_id",
            "ip.insurer_policy_id",
            "ip.policy_effective_date",
            "ip.policy_document",
            "ip.policy_document_name",
            "ip.invoice_document",
            "ip.invoice_document_name",
            "ip.initial_premium_amount",
            "ip.remarks as issued_remarks",
            "ip.is_renewal",
            
            # Products will be fetched separately as single object based on product_id or product_group_id
            """(
                SELECT JSON_ARRAYAGG(
                    JSON_OBJECT(
                        'id', vp.id,
                        'name', vp.name,
                        'is_primary', 1
                    )
                )
                FROM core_vendor_products vp
                WHERE vp.id = pb.product_id
            ) AS products""",
            
            # Policy documents as JSON array
            """COALESCE((
                SELECT JSON_ARRAYAGG(JSON_OBJECT('id', dt.id, 'value', d.value, 'document_name', dt.name))
                FROM crmp_policy_documents d
                JOIN core_product_document_types dt ON dt.id = d.document_type_id
                WHERE d.policy_base_id = pb.id AND dt.type = 'policy'
            ), JSON_ARRAY()) AS policy_document_value""",
            
            # Risk documents as JSON array
            """COALESCE((
                SELECT JSON_ARRAYAGG(JSON_OBJECT('id', dt.id, 'value', d.value, 'document_name', dt.name))
                FROM crmp_policy_documents d
                JOIN core_product_document_types dt ON dt.id = d.document_type_id
                WHERE d.policy_base_id = pb.id AND dt.type = 'risk'
            ), JSON_ARRAY()) AS risk_document_value""",
            
            # Product documents as JSON array (if type = 'product' exists)
            """COALESCE((
                SELECT JSON_ARRAYAGG(JSON_OBJECT('id', dt.id, 'value', d.value, 'document_name', dt.name))
                FROM crmp_policy_documents d
                JOIN core_product_document_types dt ON dt.id = d.document_type_id
                WHERE d.policy_base_id = pb.id AND dt.type = 'product'
            ), JSON_ARRAY()) AS product_document_value""",
        ]
        
        query = QueryBuilderService("crmp_policy_base as pb")\
            .leftJoin("core_customers as customer", "customer.id", "pb.customer_id")\
            .leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")\
            .leftJoin("core_service_providers as insurer", "insurer.id", "pb.insurer_id")\
            .leftJoin("crm_opportunity_types as risk_type", "risk_type.id", "pb.risk_type_id")\
            .leftJoin("core_users as req_user", "req_user.id", "pb.request_by_id")\
            .leftJoin("core_status as status", "status.id", "pb.status_id")\
            .leftJoin("crmp_request_types as request_type", "request_type.id", "pb.request_type_id")\
            .leftJoin("core_vendor_products as product", "product.id", "pb.product_id")\
            .leftJoin("core_product_groups as product_group", "product_group.id", "pb.product_group_id")\
            .leftJoin("crmp_coverage_types as coverage_type", "coverage_type.id", "pb.coverage_type_id")\
            .leftJoin("crmp_payment_plans as payment_plan", "payment_plan.id", "pb.payment_mode_id")\
            .leftJoin("core_users as sales_agent", "sales_agent.id", "pb.sales_agent_id")\
            .leftJoin("core_users as account_mgr", "account_mgr.id", "pb.account_manager_id")\
            .leftJoin("crmp_request_policies as rp", "rp.policy_base_id", "pb.id")\
            .leftJoin("crmp_issued_policies as ip", "ip.policy_base_id", "pb.id")\
            .leftJoin("core_entities as rp_entity", "rp_entity.id", "rp.entity_id")\
            .leftJoin("core_entities as ip_entity", "ip_entity.id", "ip.entity_id")\
            .leftJoin("core_users as created_by", "created_by.id", "COALESCE(rp_entity.created_by_id, ip_entity.created_by_id)")\
            .leftJoin("core_users as updated_by", "updated_by.id", "COALESCE(rp_entity.updated_by_id, ip_entity.updated_by_id)")\
            .leftJoin("crmq_quotations as quotations", "quotations.opportunity_id", "pb.lead_id")\
            .leftJoin("core_entity_notes as entity_notes", "entity_notes.entity_id", "COALESCE(rp.entity_id, ip.entity_id)")\
            .select(*columns)\
            .where("pb.id", policy_base_id)\
            # .where("pb.status_id", draft_status_id)
        
        data = query.first()
        
        if not data:
            return ResponseService.response("NOT_FOUND", None, "Draft policy not found or is not a draft")
        
        # Helper to parse JSON fields returned as strings by the MySQL driver
        def _parse_json_field(obj, key):
            val = obj.get(key)
            if isinstance(val, str):
                try:
                    obj[key] = json.loads(val)
                except Exception:
                    pass
        
        # Parse JSON fields
        _parse_json_field(data, "policy_document_value")
        _parse_json_field(data, "risk_document_value")
        _parse_json_field(data, "product_document_value")
        
        # Remove products array if it exists (from SQL subquery)
        if "products" in data:
            del data["products"]
        
        # Fetch product and product_group independently (both can exist)
        product_id = data.get("product_id")
        product_group_id = data.get("product_group_id")
        
        # Fetch product if product_id exists
        if product_id:
            product = QueryBuilderService("core_vendor_products")\
                .select("id", "name")\
                .where("id", product_id)\
                .first()
            
            if product:
                data["product"] = {"id": product["id"], "name": product["name"]}
            else:
                data["product"] = None
        else:
            data["product"] = None
        
        # Fetch product_group if product_group_id exists
        if product_group_id:
            product_group = QueryBuilderService("core_product_groups")\
                .select("id", "name")\
                .where("id", product_group_id)\
                .first()
            
            if product_group:
                data["product_group"] = {"id": product_group["id"], "name": product_group["name"]}
            else:
                data["product_group"] = None
        else:
            data["product_group"] = None
        
        # Format date fields
        _format_date_fields(data)
        
        # Fetch and add risk_types (using the helper function like in request_policy_detail)
        risk_type_data = _fetch_policy_risk_types(policy_base_id)
        data["risk_types"] = risk_type_data if risk_type_data else []
        
        # Fetch and add confirmed vendor responses (if quotation_id exists)
        quotation_id = data.get("quotation_id")
        if quotation_id:
            vendor_responses = _fetch_confirmed_vendor_responses(quotation_id)
            data["quotation_info"] = vendor_responses if vendor_responses else []
        else:
            data["quotation_info"] = []
        
        # Fetch risk configurations if available
        risk_configs = QueryBuilderService("crmp_policy_risk_config as prc")\
            .leftJoin("crm_risk_submissions as rs", "rs.id", "prc.risk_submission_id")\
            .leftJoin("crm_risks as r", "r.id", "rs.risk_id")\
            .select("rs.risk_id as risk_id", "r.risk_type_id as risk_type_id")\
            .where("prc.policy_base_id", policy_base_id)\
            .get()
        
        # Transform risk_configs into grouped object: { "risk_type_id": [risk_id1, risk_id2, ...] }
        risk_configs_grouped = {}
        if risk_configs:
            for config in risk_configs:
                risk_type_id = config.get("risk_type_id")
                risk_id = config.get("risk_id")
                if risk_type_id and risk_id:
                    risk_type_id_str = str(risk_type_id)
                    if risk_type_id_str not in risk_configs_grouped:
                        risk_configs_grouped[risk_type_id_str] = []
                    if risk_id not in risk_configs_grouped[risk_type_id_str]:
                        risk_configs_grouped[risk_type_id_str].append(risk_id)
        
        data["risk_configs"] = risk_configs_grouped
        
        # Structure status object like in issued_policy_detail
        status_obj = {
            "id": data.get("status_id"),
            "name": data.get("status"),
            "color": data.get("status_color"),
            "type": data.get("status_type")
        }
        data["status"] = status_obj
        
        # Add request_policy details if exists (like in issued_policy_detail)
        if data.get("request_policy_id"):
            request_policy_data = QueryBuilderService("crmp_request_policies")\
                .where("id", data.get("request_policy_id"))\
                .first()
            data["policy_request"] = request_policy_data if request_policy_data else None
        
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
        
    except Exception as e:
        import traceback
        print(f"ERROR in draft_policy_detail: {str(e)}")
        print(traceback.format_exc())
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, f"Internal server error: {str(e)}")


@csrf_exempt
@api_view(["DELETE"])
def delete_draft_policy(request, policy_base_id):
    """DELETE: Delete draft policy by policy_base_id"""
    action_type = "DELETE"
    action = ActionService.getAction("RequestPolicy", action_type)
    
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    
    try:
        # Get DRAFT status ID
        draft_status = QueryBuilderService("core_status")\
            .where("type", "policy_draft")\
            .where("module", "policy")\
            .select("id")\
            .first()
        
        if not draft_status:
            return ResponseService.response("NOT_FOUND", None, "DRAFT status not found in core_status table")
        
        draft_status_id = draft_status["id"]
        
        # Verify that the policy exists and is a draft
        policy_base = QueryBuilderService("crmp_policy_base")\
            .select("id", "status_id")\
            .where("id", policy_base_id)\
            .first()
        
        if not policy_base:
            return ResponseService.response("NOT_FOUND", None, "Draft policy not found or is not a draft")
        
        # Check if there are related request_policies or issued_policies
        request_policy = QueryBuilderService("crmp_request_policies")\
            .select("id", "entity_id")\
            .where("policy_base_id", policy_base_id)\
            .first()
        
        issued_policy = QueryBuilderService("crmp_issued_policies")\
            .select("id", "entity_id")\
            .where("policy_base_id", policy_base_id)\
            .first()
        
        # Delete related data first (cascading deletes)
        # Delete policy risk configs
        QueryBuilderService("crmp_policy_risk_config")\
            .where("policy_base_id", policy_base_id)\
            .delete()
        
        # Delete policy base risk types
        QueryBuilderService("crmp_policy_base_risk_types")\
            .where("policy_base_id", policy_base_id)\
            .delete()
        
        # Delete policy documents
        QueryBuilderService("crmp_policy_documents")\
            .where("policy_base_id", policy_base_id)\
            .delete()
        
        # Delete request policy if exists
        if request_policy:
            entity_id = request_policy.get("entity_id")
            
            # Delete entity notes
            QueryBuilderService("core_entity_notes")\
                .where("entity_id", entity_id)\
                .delete()
            
            # Delete entity approvals
            QueryBuilderService("core_entity_approvals")\
                .where("entity_id", entity_id)\
                .delete()
            
            # Delete request policy
            QueryBuilderService("crmp_request_policies")\
                .where("id", request_policy["id"])\
                .delete()
            
            # Delete entity
            QueryBuilderService("core_entities")\
                .where("id", entity_id)\
                .delete()
        
        # Delete issued policy if exists
        if issued_policy:
            entity_id = issued_policy.get("entity_id")
            
            # Delete entity notes
            QueryBuilderService("core_entity_notes")\
                .where("entity_id", entity_id)\
                .delete()
            
            # Delete entity approvals
            QueryBuilderService("core_entity_approvals")\
                .where("entity_id", entity_id)\
                .delete()
            
            # Delete issued policy
            QueryBuilderService("crmp_issued_policies")\
                .where("id", issued_policy["id"])\
                .delete()
            
            # Delete entity
            QueryBuilderService("core_entities")\
                .where("id", entity_id)\
                .delete()
        
        # Finally, delete the policy base
        deleted = QueryBuilderService("crmp_policy_base")\
            .where("id", policy_base_id)\
            .delete()
        
        if deleted:
            return ResponseService.response("SUCCESS", {"id": policy_base_id}, "Draft policy deleted successfully")
        else:
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Failed to delete draft policy")
        
    except Exception as e:
        import traceback
        print(f"ERROR in delete_draft_policy: {str(e)}")
        print(traceback.format_exc())
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, f"Internal server error: {str(e)}")

