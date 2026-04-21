from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
import json
from datetime import datetime
from django.db.models import Max
from envoy_bu_crm_api.policy.models.crmp_request_policies import RequestPolicy
from django.db import transaction
from envoy_bu_crm_api.service import handle_entity_notes,replace_empty_strings_with_none

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


def get_all_request_policies(request, policy_id=None):
    columns = [
        "rp.*",
        "base.premium_amount",
        "base.sum_insured",
        "base.quotation_issued_date",
        "base.quotation_expiry_date",
        "base.policy_start_date",
        "base.policy_expiry_date",
        "base.quotation_notes",
        "base.quotation_document_name as quotation_document_name",
        "base.quotation_document as quotation_document",
        "sp.name AS insurer_company_name",
        "sp.logo AS insurer_company_logo",
        "risk_type.title AS risk_type",
        "req_user.display_name AS requested_by",
        "req_user.picture AS requested_by_logo",
        "status.name AS status",
        "status.color AS status_color",
        "request_type.name AS request_type",
        "product.name AS product_name",
        "customer.name AS customer_name",
        "customer_contact.email AS customer_email",
        "customer_contact.primary_contact AS customer_primary_contact",
        "customer_contact.address AS customer_address",
        "entity_notes.notes AS insurer_notes",
        "coverage_type.name AS coverage_type",
        "payment_plan.name AS payment_plan",
        "entity.created_at AS created_at",
        "created_by.display_name AS created_by",
        "created_by.picture AS created_by_logo",
        "updated_by.display_name AS updated_by",
        "updated_by.picture AS updated_by_logo",
        "issued_policy.id AS issued_policy_id",
        "CASE WHEN customer_contacts.is_primary = 1 THEN customer_contacts.title ELSE NULL END AS customer_title",

    ]

    query = (
        QueryBuilderService("crmp_request_policies AS rp")
        .leftJoin("crmp_policy_base AS base", "base.id", "rp.policy_base_id")
        .leftJoin("core_service_providers AS sp", "sp.id", "base.insurer_id")
        .leftJoin("crm_opportunity_types AS risk_type", "risk_type.id", "base.risk_type_id")
        .leftJoin("core_users AS req_user", "req_user.id", "base.request_by_id")
        .leftJoin("core_status AS status", "status.id", "rp.status_id")
        .leftJoin("crmp_request_types AS request_type", "request_type.id", "base.request_type_id")
        .leftJoin("core_products AS product", "product.id", "base.product_id")
        .leftJoin("core_customers AS customer", "customer.id", "base.customer_id")
        .leftJoin("core_contacts AS customer_contact", "customer_contact.id", "customer.primary_contact_id")
        .leftJoin("core_entity_notes AS entity_notes", "entity_notes.entity_id", "rp.entity_id")
        .leftJoin("crmp_coverage_types AS coverage_type", "coverage_type.id", "base.coverage_type_id")
        .leftJoin("crmp_payment_plans AS payment_plan", "payment_plan.id", "base.payment_mode_id")
        .leftJoin("core_entities AS entity", "entity.id", "rp.entity_id")
        .leftJoin("core_users AS created_by", "created_by.id", "entity.created_by_id")
        .leftJoin("core_users AS updated_by", "updated_by.id", "entity.updated_by_id")
        .leftJoin("crmp_issued_policies AS issued_policy", "issued_policy.policy_base_id", "base.id").leftJoin("core_customer_contacts AS customer_contacts", "customer_contacts.customer_id", "customer.id")

        .select(*columns)
    )

    if policy_id:
        row = query.where("rp.id", policy_id).first()
        if not row:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        return ResponseService.response("SUCCESS", row, Message.DATA_FETCHED)

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "rp.policy_request_date")
    sort_dir = request.GET.get("sort_dir", "desc")

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
        "rp.policy_request_date",
        "sp.name",
        "request_type.name",
    ]

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def generate_policy_request_id():
    with transaction.atomic():
        last = (
            RequestPolicy.objects.select_for_update().aggregate(Max("id"))["id__max"]
            or 0
        )
        return f"PR-{last + 1}"


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

    approval_record = QueryBuilderService("core_entity_approvals").insert(
        {
            "entity_id": entity_id,
            "user": user.id if user else None,
            "role": None,
            "level": 1,
            "status": "pending",
            "remarks": "",
        }
    )

    # Create the policy request
    data["policy_request_id"] = generate_policy_request_id()
    data["policy_request_date"] = now.date().isoformat()
    data["entity_id"] = entity_id
    data["status_id"] = (
        4  # checking cmt need to check the status id for "requested" seeder
    )
    data["quotation_document_name"] = lead_data.get("quotation_document_name", None)
    data["quotation_document"] = lead_data.get("quotation_document", None)
    data["insurer_id"] = lead_data.get("insurer_id", None)
    data["lead_id"] = lead_data.get("lead_id", None)
    data["customer_id"] = lead_data.get("customer_id", None)
    data["risk_type_id"] = lead_data.get("risk_type_id", None)

    data["sum_insured"] = 10000000  # checking cmt need
    data["coverage_amount"] = 10000000  # checking cmt need

    created = QueryBuilderService("crmp_request_policies").insert(data)

    # Send approval notification
    try:
        from envoy_bu_crm_api.quotation.services.NotificationService import NotificationService
        
        # Get customer name
        customer_name = "N/A"
        if data.get("customer_id"):
            customer = QueryBuilderService("core_customers") \
                .select("name") \
                .where("id", data.get("customer_id")) \
                .first()
            if customer:
                customer_name = customer.get("name", "N/A")
        
        # Get product name from risk type
        product_name = "N/A"
        if data.get("risk_type_id"):
            risk_type = QueryBuilderService("crm_risk_types") \
                .select("title") \
                .where("id", data.get("risk_type_id")) \
                .first()
            if risk_type:
                product_name = risk_type.get("title", "N/A")
        
        # Get insurer/service provider name
        insurer_name = "N/A"
        if data.get("insurer_id"):
            insurer = QueryBuilderService("core_service_providers") \
                .select("name") \
                .where("id", data.get("insurer_id")) \
                .first()
            if insurer:
                insurer_name = insurer.get("name", "N/A")
        
        # Get lead/opportunity details
        opportunity_title = "N/A"
        if lead_data.get("lead_id"):
            opportunity = QueryBuilderService("crm_opportunities") \
                .select("title") \
                .where("id", lead_data.get("lead_id")) \
                .first()
            if opportunity:
                opportunity_title = opportunity.get("title", "N/A")
        
        # Prepare comprehensive message
        notification_message = f"New policy approval request {data.get('policy_request_id', 'N/A')} for {customer_name}"
        notification_message += f" - Product: {product_name}"
        if insurer_name != "N/A":
            notification_message += f" - Insurer: {insurer_name}"
        
        # Send notification to the approver
        approval_users = [approval_record.get("user")] if approval_record.get("user") else []
        approval_roles = [approval_record.get("role")] if approval_record.get("role") else []
        
        NotificationService.send_approval_notification(
            approval_users=approval_users,
            approval_roles=approval_roles,
            request_type="policy",
            request_id=created.get("id"),
            request_code=data.get("policy_request_id", "N/A"),
            customer_name=customer_name,
            product_name=product_name,
            entity_id=entity_id,
            approval_url="/policy-request-approvals",
            additional_metadata={
                "insurer_name": insurer_name,
                "insurer_id": data.get("insurer_id"),
                "lead_id": lead_data.get("lead_id"),
                "opportunity_title": opportunity_title,
                "risk_type_id": data.get("risk_type_id"),
                "custom_message": notification_message
            }
        )
        print(f"Approval notification sent for policy request {data.get('policy_request_id')} with all details")
    except Exception as notify_error:
        print(f"Failed to send approval notification: {str(notify_error)}")
        # Don't fail the main flow if notification fails

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


from datetime import datetime
import json

def create_request_policy(request):
    data = json.loads(request.body or "{}")
    
     # Set request_type_id based on is_policy
    is_policy = data.get("is_policy", False)
    data["request_type_id"] = 2 if is_policy else 1

    errors = ValidatorService.validate(data, get_request_policy_rules())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    keys_to_check = ['premium_amount', 'sum_insured', 'quotation_expiry_date',
        'quotation_issued_date']
    data = replace_empty_strings_with_none(data, keys_to_check)

    # Use first risk_type_id for backward compatibility
    if "risk_type_ids" in data and isinstance(data["risk_type_ids"], list) and data["risk_type_ids"]:
        data["risk_type_id"] = data["risk_type_ids"][0]

    if "lead_id" in data and data["lead_id"] == "":
        data["lead_id"] = None

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
                "policy_expiry_date", "quotation_notes"
            ]
            policy_base_data = {field: data.get(field) for field in base_fields if field in data}
            QueryBuilderService("crmp_policy_base").where("id", policy_base_id).update(policy_base_data)

            # Update risk types
            QueryBuilderService("crmp_policy_base_risk_types").where("policy_base_id", policy_base_id).delete()
            if "risk_type_ids" in data and isinstance(data["risk_type_ids"], list):
                for rt_id in data["risk_type_ids"]:
                    QueryBuilderService("crmp_policy_base_risk_types").insert({
                        "policy_base_id": policy_base_id,
                        "risk_type_id": rt_id
                    })

            # Update request policy
            request_policy = QueryBuilderService("crmp_request_policies").where("policy_base_id", policy_base_id).first()
            if request_policy:
                entity_id = request_policy["entity_id"]
                QueryBuilderService("crmp_request_policies").where("policy_base_id", policy_base_id).update({
                    "policy_request_date": now.date().isoformat(),
                    "status_id": 6
                })
            else:
                # Create new request policy if not exists
                entity = QueryBuilderService("core_entities").insert({
                    "type": "policy",
                    "approvel_status": False,
                    "created_at": now,
                    "created_by_id": user.id if user else None,
                    "updated_by_id": None,
                })
                entity_id = entity["id"]
                QueryBuilderService("core_entity_approvals").insert({
                    "entity_id": entity_id,
                    "user": user.id if user else None,
                    "role": None,
                    "level": 1,
                    "status": "pending",
                    "remarks": "",
                })
                request_policy_data = {
                    "policy_request_id": generate_policy_request_id(),
                    "policy_request_date": now.date().isoformat(),
                    "entity_id": entity_id,
                    "status_id": 6,
                    "policy_base_id": policy_base_id
                }
                QueryBuilderService("crmp_request_policies").insert(request_policy_data)

            if "insurer_notes" in data and data["insurer_notes"]:
                handle_entity_notes(entity_id, [{
                    "note": data["insurer_notes"],
                    "created_by_id": user.id if user else None,
                    "created_at": now
                }], is_update=False)

            update_customer_contact_info(data)

            return ResponseService.response("SUCCESS", {"policy_base_id": policy_base_id}, "default_update_success_msg")
        else:
            return ResponseService.response("NOT_FOUND", "Policy base not found for the given lead_id.", Error.NOT_FOUND)
    else:
        # Create new records
        entity = QueryBuilderService("core_entities").insert({
            "type": "policy",
            "approvel_status": False,
            "created_at": now,
            "created_by_id": user.id if user else None,
            "updated_by_id": None,
        })
        entity_id = entity["id"]

        approval_record = QueryBuilderService("core_entity_approvals").insert({
            "entity_id": entity_id,
            "user": user.id if user else None,
            "role": None,
            "level": 1,
            "status": "pending",
            "remarks": "",
        })

        base_fields = [
            "risk_details_form_id", "risk_type_id", "insurer_id", "customer_id",
            "lead_id", "request_by_id", "premium_amount", "quotation_document_size",
            "quotation_document", "quotation_document_name", "request_type_id",
            "product_id", "payment_mode_id", "coverage_type_id", "sum_insured",
            "quotation_issued_date", "quotation_expiry_date", "policy_start_date",
            "policy_expiry_date", "quotation_notes"
        ]
        policy_base_data = {field: data.get(field) for field in base_fields if field in data}
        policy_base = QueryBuilderService("crmp_policy_base").insert(policy_base_data)
        policy_base_id = policy_base["id"]

        if "risk_type_ids" in data and isinstance(data["risk_type_ids"], list):
            for rt_id in data["risk_type_ids"]:
                QueryBuilderService("crmp_policy_base_risk_types").insert({
                    "policy_base_id": policy_base_id,
                    "risk_type_id": rt_id
                })

        request_policy_data = {
            "policy_request_id": generate_policy_request_id(),
            "policy_request_date": now.date().isoformat(),
            "entity_id": entity_id,
            "status_id": 6,
            "policy_base_id": policy_base_id
        }
        created = QueryBuilderService("crmp_request_policies").insert(request_policy_data)

        if created:
            update_customer_contact_info(data)

        if "insurer_notes" in data and data["insurer_notes"]:
            handle_entity_notes(entity_id, [{
                "note": data["insurer_notes"],
                "created_by_id": user.id if user else None,
                "created_at": now
            }], is_update=False)

        # Send approval notification
        try:
            from envoy_bu_crm_api.quotation.services.NotificationService import NotificationService
            
            # Get customer name
            customer_name = "N/A"
            if data.get("customer_id"):
                customer = QueryBuilderService("core_customers") \
                    .select("name") \
                    .where("id", data.get("customer_id")) \
                    .first()
                if customer:
                    customer_name = customer.get("name", "N/A")
            
            # Get product name
            product_name = "N/A"
            if data.get("product_id"):
                product = QueryBuilderService("core_products") \
                    .select("name") \
                    .where("id", data.get("product_id")) \
                    .first()
                if product:
                    product_name = product.get("name", "N/A")
            elif data.get("risk_type_id"):
                risk_type = QueryBuilderService("crm_risk_types") \
                    .select("title") \
                    .where("id", data.get("risk_type_id")) \
                    .first()
                if risk_type:
                    product_name = risk_type.get("title", "N/A")
            
            # Get insurer/service provider name
            insurer_name = "N/A"
            if data.get("insurer_id"):
                insurer = QueryBuilderService("core_service_providers") \
                    .select("name") \
                    .where("id", data.get("insurer_id")) \
                    .first()
                if insurer:
                    insurer_name = insurer.get("name", "N/A")
            
            # Get lead/opportunity details
            opportunity_title = "N/A"
            if data.get("lead_id"):
                opportunity = QueryBuilderService("crm_opportunities") \
                    .select("title") \
                    .where("id", data.get("lead_id")) \
                    .first()
                if opportunity:
                    opportunity_title = opportunity.get("title", "N/A")
            
            # Prepare comprehensive message
            notification_message = f"New policy approval request {request_policy_data.get('policy_request_id', 'N/A')} for {customer_name}"
            notification_message += f" - Product: {product_name}"
            if insurer_name != "N/A":
                notification_message += f" - Insurer: {insurer_name}"
            
            # Send notification to the approver
            approval_users = [approval_record.get("user")] if approval_record.get("user") else []
            approval_roles = [approval_record.get("role")] if approval_record.get("role") else []
            
            NotificationService.send_approval_notification(
                approval_users=approval_users,
                approval_roles=approval_roles,
                request_type="policy",
                request_id=created.get("id"),
                request_code=request_policy_data.get("policy_request_id", "N/A"),
                customer_name=customer_name,
                product_name=product_name,
                entity_id=entity_id,
                approval_url="/policy-request-approvals",
                additional_metadata={
                    "insurer_name": insurer_name,
                    "insurer_id": data.get("insurer_id"),
                    "lead_id": data.get("lead_id"),
                    "opportunity_title": opportunity_title,
                    "risk_type_id": data.get("risk_type_id"),
                    "product_id": data.get("product_id"),
                    "custom_message": notification_message
                }
            )
            print(f"Approval notification sent for policy request {request_policy_data.get('policy_request_id')} with all details")
        except Exception as notify_error:
            print(f"Failed to send approval notification: {str(notify_error)}")
            # Don't fail the main flow if notification fails

        return ResponseService.response("SUCCESS", created, "default_create_success_msg")


def get_request_policy_rules():
    return {
        "lead_id": "nullable|exists:crm_opportunities,id",
        "quotation_document_name": "string",
        "quotation_document": "nullable",
        "insurer_id": "integer|required|exists:core_service_providers,id",
        "insurer_notes": "string",
        # "quotation_expiry_date": "date",
        # "quotation_issued_date": "date",
        "request_by_id": "integer|exists:core_users,id",
        "premium_amount": "decimal",
        "customer_id": "integer|required|exists:core_customers,id",
        "customer_primary_contact": "string|required",
        "customer_email": "string|required|email",
        "customer_address": "string|required",
        "policy_start_date": "date|required",
        "policy_expiry_date": "date|required",
        "payment_mode_id": "integer|required|exists:crmp_payment_plans,id",
        "sum_insured": "decimal|required",
        # "request_type_id": "integer|required|exists:crmp_request_types,id",
        "risk_type_ids": "required|array|min:1",
        "risk_type_ids.*": "integer|exists:crm_opportunity_types,id",
        "product_id": "integer|required|exists:core_products,id",
        "coverage_type_id": "integer|required|exists:crmp_coverage_types,id",
        "quotation_notes": "string",
        "is_policy": "boolean",
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
            .update(
                {
                    "primary_contact": data["customer_primary_contact"],
                    "email": data["customer_email"],
                    "address": data["customer_address"],
                }
            )
        )
    return {"customer_update": customer_update}

