from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
import json
from envoy_bu_crm_api.service import send_approval_email_helper,get_recipient_email_by_customer_id


@api_view(["GET"])
def get_all_policy_approvals(request, policy_id=None):

    columns = [
        "core_entity_approvals.*",
        "crmp_request_policies.policy_request_id as policy_request_code",
        "crmp_request_policies.id AS policy_request_id",
        "core_users.display_name AS requested_by",
        "core_users.picture AS requested_by_logo",
        "core_entities.type AS request_type",
        "core_entities.created_at AS requested_on",
        "core_customers.name AS customer_name",
        "core_customers.logo AS customer_logo",
        "products.name AS product_name",
        "core_contacts.email AS customer_email",
        "risk_type.title AS risk_type",
        "crmp_request_policies.product_expiration_date AS expiration_date",
        "crmp_request_policies.product_effective_date AS effective_date",
        "crmp_request_policies.premium_payment_plan AS premium_payment_plan",
    ]
    # Check if user has the required action permission
    action = ActionService.getAction("RequestPolicyApproval", "VIEW")
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    query = (
        QueryBuilderService("core_entity_approvals")
        .select(*columns)
        .leftJoin(
            "core_entities", "core_entities.id", "core_entity_approvals.entity_id"
        )
        .leftJoin(
            "crmp_request_policies",
            "crmp_request_policies.entity_id",
            "core_entities.id",
        )
        .leftJoin("core_users", "core_users.id", "core_entity_approvals.user")
        .leftJoin(
            "crm_opportunities", "crm_opportunities.id", "crmp_request_policies.lead_id"
        )
        .leftJoin(
            "crm_opportunity_types as risk_type",
            "risk_type.id",
            "crm_opportunities.type",
        )
        .leftJoin(
            "core_customers", "core_customers.id", "crm_opportunities.customer_id"
        )
        .leftJoin(
            "core_contacts", "core_contacts.id", "core_customers.primary_contact_id"
        )
        .leftJoin(
            "crm_oppor_interested_products as interested_products",
            "interested_products.opportunity_id",
            "crmp_request_policies.lead_id",
        )
        .leftJoin(
            "core_products as products", "products.id", "interested_products.product_id"
        )
        .where("core_entities.type", "policy")
    )

    # Single approval retrieval by policy_id
    if policy_id:
        data = query.where("crmp_request_policies.id", policy_id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    # Apply filters, pagination, and sorting
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_entity_approvals.status")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = [
        "core_users.display_name",
        "core_entity_approvals.status",
        "core_entities.type",
        "crmp_request_policies.policy_request_id",
    ]
    search_columns = [
        "core_entity_approvals.policy_request_id",
        "core_users.display_name",
        "core_entities.type",
        "crmp_request_policies.policy_request_id",
    ]
    sort_columns = [
        "core_entity_approvals.approval_date",
        "core_users.display_name",
        "core_entities.type",
    ]

    # Apply the filter, search, and pagination logic
    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@api_view(["POST"])
def send_approval_email(request):
    data = json.loads(request.body or {})

    rules = {
        "subject": "required",
        "body": "required",
        "policy_request_id": "integer|required",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "VALIDATION_ERROR")

    action = ActionService.getAction("SendApprovalEmail", "CREATE")
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    policy_id = data.get("policy_request_id")
    subject = data.get("subject")
    body = data.get("body")

    policy_data = (
        QueryBuilderService("crmp_request_policies")
        .leftJoin("core_customers", "core_customers.id", "crmp_request_policies.customer_id")
        .where("crmp_request_policies.id", policy_id)
        .select("core_customers.id AS customer_id", "crmp_request_policies.entity_id")
        .first()
    )

    if not policy_data or not policy_data.get("customer_id"):
        return ResponseService.response("NOT_FOUND", None, "Policy or customer not found.")

    recipient_email, error_msg = get_recipient_email_by_customer_id(policy_data["customer_id"])
    if not recipient_email:
        return ResponseService.response("VALIDATION_ERROR", error_msg, "VALIDATION_ERROR")

    result = send_approval_email_helper(recipient_email, subject, body)
    if not result["success"]:
        return ResponseService.response("VALIDATION_ERROR", result["error"], result["message"])

    QueryBuilderService("core_entity_approvals").where("entity_id", policy_data["entity_id"]).update({"status": "confirmed"})
    return ResponseService.response("SUCCESS", result["data"], result["message"])



