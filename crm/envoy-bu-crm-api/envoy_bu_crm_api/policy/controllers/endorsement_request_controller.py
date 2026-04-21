# views.py
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from django.db.models import Max
from envoy_bu_crm_api.policy.models.crmp_endorsement_request import EndorsementRequest
from envoy_bu_crm_api.service import handle_entity, handle_entity_notes
from envoy_bu_crm_api.service import (
    send_approval_email_helper,
    get_recipient_email_by_customer_id,
)
from datetime import datetime


@csrf_exempt
@api_view(["GET", "POST"])
def endorsement_request_list(request):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("EndorsementRequest", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_endorsement_requests(request)

    return create_endorsement_request(request)


@csrf_exempt
@api_view(["GET", "POST"])
def endorsement_request_list_by_policy(request, policy_id):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("EndorsementRequest", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_endorsement_requests(request, policy_id=policy_id)

    return create_endorsement_request(request)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def endorsement_request_detail(request, request_id):
    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("EndorsementRequest", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_endorsement_requests(request, request_id)
    elif request.method == "PUT":
        return update_endorsement_request(request, request_id)
    elif request.method == "DELETE":
        return delete_endorsement_request(request_id)


def get_all_endorsement_requests(
    request, request_id=None, policy_id=None, _created=False
):
    columns = [
        "crmp_endorsement_requests.*",
        "crmp_endorsement_types.name AS endorsement_type_name",
        "crmp_endorsement_reasons_codes.code AS reason_code",
        "crmp_endorsement_reasons_codes.description AS reason_code_description",
        "notes.notes As remarks",
        "users.display_name as created_by",
        "users.picture as created_by_logo",
        "entities.created_at as created_at",
        "insurer_sp.name as insurer_name",
        "insurer_sp.logo as insurer_logo",
        "insurer_sp.id as insurer_id",
        "insurer_sp.email as insurer_email",
        "crmp_issued_policies.policy_effective_date as effective_date",
        "crmp_issued_policies.brokerage_policy_id as policy_id",
        "customers.name as policy_holder_name",
        "customers.logo as policy_holder_logo",
        "request_customer_contact.email AS policy_holder_email",
        "request_customer_contact.address AS policy_holder_address",
        "request_customer_contact.primary_contact AS policy_holder_primary_contact",
    ]

    query = (
        QueryBuilderService("crmp_endorsement_requests")
        .select(*columns)
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
        .leftJoin("core_users as users", "users.id", "entities.created_by_id")
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmp_endorsement_requests.issued_policy_id",
        )
        .leftJoin(
            "crmp_policy_base as policy_base",
            "policy_base.id",
            "crmp_issued_policies.policy_base_id",
        )
        .leftJoin(
            "core_service_providers as insurer_sp",
            "insurer_sp.id",
            "policy_base.insurer_id",
        )
        .leftJoin(
            "core_customers as customers", "customers.id", "policy_base.customer_id"
        )
        .leftJoin(
            "core_contacts as request_customer_contact",
            "request_customer_contact.id",
            "customers.primary_contact_id",
        )
    )

    if request_id:
        data = query.where("crmp_endorsement_requests.id", request_id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        if _created:
            return data
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get(
        "sort_by", "crmp_endorsement_requests.endorsement_type_id"
    )
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = [
        "crmp_endorsement_types.name",
        "crmp_endorsement_reasons_codes.code",
    ]
    search_columns = [
        "crmp_endorsement_requests.remarks",
        "crmp_endorsement_requests.notes_or_details",
    ]
    sort_columns = [
        "crmp_endorsement_types.name",
    ]
    if policy_id:
        query = query.where("crmp_endorsement_requests.issued_policy_id", policy_id)

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def create_endorsement_request(request):
    data = json.loads(request.body or "{}")
    data["endorsement_request"] = generate_endorse_request_id()

    # Default cover_value to 0 if not provided or invalid
    if "cover_value" not in data or str(data["cover_value"]).strip() == "":
        data["cover_value"] = 0

    errors = ValidatorService.validate(data, get_endorsement_request_rules())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    entity_data = {
        "type": "policy",
        "approvel_status": False,
    }
    user = request.user if request.user.is_authenticated else None
    entity_id = handle_entity(entity_data, entity_id=data.get("entity_id"), user=user)
    data["entity_id"] = entity_id
    data["mail_status"] = 0

    created = QueryBuilderService("crmp_endorsement_requests").insert(data)

    if "remarks" in data and data["remarks"]:
        handle_entity_notes(entity_id, [{
            "note": data["remarks"],
            "created_by_id": request.user.id if request.user.is_authenticated else None,
            "created_at": datetime.now()
        }], is_update=False)

    return ResponseService.response(
        "SUCCESS",
        get_all_endorsement_requests(
            request, request_id=created.get("id"), _created=True
        ),
        "default_create_success_msg",
    )

def update_endorsement_request(request, request_id):
    data = json.loads(request.body or "{}")
    errors = ValidatorService.validate(data, get_endorsement_request_rules())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    updated = (
        QueryBuilderService("endorsement_request").where("id", request_id).update(data)
    )
    if updated:
        return ResponseService.response(
            "SUCCESS", updated, "default_update_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_endorsement_request(request_id):
    deleted = (
        QueryBuilderService("endorsement_request").where("id", request_id).delete()
    )
    if deleted:
        return ResponseService.response(
            "SUCCESS", deleted, "default_delete_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


# validators.py
def get_endorsement_request_rules():
    return {
        "remarks": "string",
        "endorsement_type_id": "required|integer|exists:crmp_endorsement_types,id",
        "reason_code_id": "required|integer|exists:crmp_endorsement_reasons_codes,id",
        # "cover_value": "required|numeric",
        "issued_policy_id": "required|integer|exists:crmp_issued_policies,id",
    }


def generate_endorse_request_id():
    last = EndorsementRequest.objects.aggregate(Max("id"))["id__max"] or 0
    return f"EREQ-{last + 1}"


@api_view(["POST"])
def send_endorsement_email(request):
    data = json.loads(request.body or {})

    rules = {
        "subject": "required",
        "body": "required",
        "endorsement_request_id": "integer|required",
        "links": "array|nullable",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "VALIDATION_ERROR")

    action = ActionService.getAction("SendApprovalEmail", "CREATE")
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    endorsement_request_id = data.get("endorsement_request_id")
    subject = data.get("subject")
    body = data.get("body")
    links = data.get("links")

    policy_data = (
        QueryBuilderService("crmp_endorsement_requests")
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmp_endorsement_requests.issued_policy_id",
        )
        .leftJoin(
            "crmp_policy_base as policy_base",
            "policy_base.id",
            "crmp_issued_policies.policy_base_id",
        )
        .leftJoin(
            "core_service_providers as insurer_sp",
            "insurer_sp.id",
            "policy_base.insurer_id",
        )
        .where("crmp_endorsement_requests.id", endorsement_request_id)
        # .leftJoin("core_customers", "core_customers.id", "policy_base.customer_id")
        # .select("core_customers.id AS customer_id", "crmp_request_policies.entity_id")
        .first()
    )

    print("policy_data", policy_data)

    # if not policy_data or "customer_id" not in policy_data:
    #     return ResponseService.response(
    #         "NOT_FOUND", policy_data, "Policy or customer not found."
    #     )

    recipient_email = policy_data["email"]
    if not recipient_email:
        return ResponseService.response(
            "VALIDATION_ERROR", 'no email found', "VALIDATION_ERROR"
        )

    result = send_approval_email_helper(recipient_email, subject, body, links=links)
    if not result["success"]:
        return ResponseService.response(
            "VALIDATION_ERROR", result["error"], result["message"]
        )

    QueryBuilderService("crmp_endorsement_requests").where(
        "id", endorsement_request_id
    ).update({"mail_status": "1"})

    return ResponseService.response("SUCCESS", result["data"], result["message"])
