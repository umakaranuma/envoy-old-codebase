from datetime import datetime
import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from envoy_bu_crm_api.quotation.services.send_mail_service import SendMail
from envoy_bu_crm_api.quotation.services.document_cdn_service import DocumentCDNService
from messages import Message, Error
from django.views.decorators.csrf import csrf_exempt


from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices.QueryBuilderService import QueryBuilderService
from mServices.ResponseService import ResponseService


@csrf_exempt
@api_view(["GET"])
def quotation_approval(request):
    all_columns = [
        "crmq_quotations.id as id",
        "crmq_quotations.code as code",
        "crmq_quotations.requested_data as request_date",
        "crmq_quotations.customer_id as customer_id",
        "crmq_quotations.status as status",
        "crmq_quotations.notes as notes",
        "crmq_quotations.request_type as request_type",
        "crmq_quotations.opportunity_type_id as opportunity_type_id",
        "crm_opportunity_types.title as opportunity_type_title",
        "crmq_quotations.entity_id as entity_id",
        "crmq_quotations.opportunity_id as opportunity_id",
        "crm_opportunities.title as opportunity_title",
        "core_customers.name as display_name",
        "core_entity_approvals.id as approval_id",
        "core_entity_approvals.level as approval_level",
        "core_entity_approvals.status as approval_status",
        "core_entity_approvals.remarks as approval_remarks",
        "core_users.display_name as created_by_name",
    ]

    policy_columns = [
        "crmp_request_policies.id as id",
        "crmp_request_policies.policy_request_id as code",
        "crmp_request_policies.policy_request_date as request_date",
        "crmp_policy_base.customer_id as customer_id",
        "core_status.name as status",
        "core_entity_notes.notes as notes",
        "crmp_request_types.name as request_type",
        "crm_opportunity_types.id as opportunity_type_id",
        "crm_opportunity_types.title as opportunity_type_title",
        "crmp_request_policies.entity_id as entity_id",
        "crm_opportunities.id as opportunity_id",
        "crm_opportunities.title as opportunity_title",
        "core_entity_approvals.id as approval_id",
        "core_entity_approvals.level as approval_level",
        "core_entity_approvals.status as approval_status",
        "core_entity_approvals.remarks as approval_remarks",
        "core_users.display_name as created_by_name",
    ]

    user = request.user if request.user.is_authenticated else None
    logged_in_user_id = user.id if user else 3
    logged_in_role_id = user.role_id if user else 1

    print(f"DEBUG: User ID: {logged_in_user_id}, Role ID: {logged_in_role_id}")

    approvals_query = (
        QueryBuilderService("core_entity_approvals")
        .select("entity_id", "id")
        .whereNotIn("status", "open")
    )

    # TEMPORARY: Remove user/role filtering to test if that's the issue
    # Comment out the user/role filtering to see if that's causing the problem
    """
    if logged_in_user_id and logged_in_role_id:
        approvals_query = approvals_query.where_group(lambda group_conditions: [
            group_conditions.append((f"user = %s", [logged_in_user_id])),
            group_conditions.append((f"OR role = %s", [logged_in_role_id]))
        ])
    elif logged_in_user_id:
        approvals_query = approvals_query.where("user", logged_in_user_id)
    elif logged_in_role_id:
        approvals_query = approvals_query.where("role", logged_in_role_id)
    """

    approvals = approvals_query.get()

    unique_entity_approvals = {}
    for row in approvals:
        eid = row["entity_id"]
        if eid and eid not in unique_entity_approvals:
            unique_entity_approvals[eid] = row["id"]

    if not unique_entity_approvals:
        return ResponseService.response("SUCCESS", [], Message.NO_PENDING_APPROVALS)

    entity_ids = list(unique_entity_approvals.keys())
    approval_ids = list(unique_entity_approvals.values())

    entity_info_query = (
        QueryBuilderService("core_entities")
        .select("id", "type")
        .whereIn("id", entity_ids)
    )
    entities = entity_info_query.get()

    quotation_entity_ids = []
    policy_entity_ids = []

    for ent in entities:
        if ent["type"] == "Quotation Approval":
            quotation_entity_ids.append(ent["id"])
        elif ent["type"] == "policy":
            policy_entity_ids.append(ent["id"])

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    allowed_filters = [
        "crmq_quotations.id",
        "",
        "crmq_quotations.customer_id",
        "crmq_quotations.status",
    ]
    search_columns = allowed_filters
    allowed_sorting_columns = allowed_filters

    results = {}
    quotation_results = None
    policy_results = None

    if quotation_entity_ids:
        quotation_approval_ids = [
            unique_entity_approvals[eid]
            for eid in quotation_entity_ids
            if eid in unique_entity_approvals
        ]

        quotation_query = (
            QueryBuilderService("crmq_quotations")
            .select(*all_columns)
            .leftJoin(
                "crm_opportunity_types",
                "crm_opportunity_types.id",
                "crmq_quotations.opportunity_type_id",
            )
            .leftJoin(
                "core_customers", "core_customers.id", "crmq_quotations.customer_id"
            )
            .leftJoin(
                "core_entity_approvals",
                "core_entity_approvals.entity_id",
                "crmq_quotations.entity_id",
            )
            .leftJoin("core_entities", "core_entities.id", "crmq_quotations.entity_id")
            .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
            .leftJoin(
                "crm_opportunities",
                "crm_opportunities.id",
                "crmq_quotations.opportunity_id",
            )
            .whereIn("crmq_quotations.entity_id", quotation_entity_ids)
            .whereIn("core_entity_approvals.id", quotation_approval_ids)
            .whereNull("core_entity_approvals.deleted_at")
            # .apply_conditions(filter_json, allowed_filters, search_string, search_columns)  # TEMPORARILY DISABLED
            .get()
        )
        quotation_results = quotation_query

    if policy_entity_ids:
        policy_approval_ids = [
            unique_entity_approvals[eid]
            for eid in policy_entity_ids
            if eid in unique_entity_approvals
        ]

        policy_query = (
            QueryBuilderService("crmp_request_policies")
            .select(*policy_columns)
            .leftJoin(
                "core_entity_approvals",
                "core_entity_approvals.entity_id",
                "crmp_request_policies.entity_id",
            )
            .leftJoin(
                "core_entities", "core_entities.id", "crmp_request_policies.entity_id"
            )
            .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
            .leftJoin(
                "crmp_policy_base", "crmp_policy_base.id", "crmp_request_policies.id"
            )
            .leftJoin(
                "core_status", "core_status.id", "crmp_request_policies.status_id"
            )
            .leftJoin(
                "core_entity_notes",
                "core_entity_notes.entity_id",
                "crmp_request_policies.entity_id",
            )
            .leftJoin(
                "crmp_request_types",
                "crmp_request_types.id",
                "crmp_policy_base.request_type_id",
            )
            .leftJoin(
                "crm_opportunity_types",
                "crm_opportunity_types.id",
                "crmp_policy_base.risk_type_id",
            )
            .leftJoin(
                "crm_opportunities", "crm_opportunities.id", "crmp_policy_base.lead_id"
            )
            .whereIn("crmp_request_policies.entity_id", policy_entity_ids)
            .whereIn("core_entity_approvals.id", policy_approval_ids)
            .whereNull("core_entity_approvals.deleted_at")
            # .apply_conditions(filter_json, [], search_string, [])  # TEMPORARILY DISABLED
            .get()
        )
        policy_results = policy_query

    merged_rows = []
    if isinstance(quotation_results, list):
        for row in quotation_results:
            row_copy = dict(row)
            row_copy["entity_type"] = "quotation"
            merged_rows.append(row_copy)
    if isinstance(policy_results, list):
        for row in policy_results:
            row_copy = dict(row)
            row_copy["entity_type"] = "policy"
            merged_rows.append(row_copy)

    def sort_key(item):
        if sort_by and sort_by in item:
            return item.get(sort_by)
        return item.get("approval_id", 0)

    reverse = str(sort_dir).lower() == "desc"
    try:
        merged_rows.sort(key=sort_key, reverse=reverse)
    except Exception:
        # Fallback sort by approval_id when types are incomparable
        merged_rows.sort(key=lambda x: x.get("approval_id", 0), reverse=True)

    total = len(merged_rows)
    start = max((page - 1), 0) * limit
    end = start + limit
    paged_rows = merged_rows[start:end]
    pages = (total + limit - 1) // limit if limit else 1

    results = {
        "total_records": total,
        "per_page": limit,
        "current_page": page,
        "last_page": pages,
        "data": paged_rows,
    }

    return ResponseService.response("SUCCESS", results, Message.DATA_FETCHED)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def handle_quotation_approval(request, id):
    if request.method == "GET":
        return single_quotation_approval(request, id)

    if request.method == "PUT":
        return quotation_approval_changes(request, id)

    if request.method == "DELETE":
        return delete_quotation_approval(id)


def single_quotation_approval(request, id):
    all_columns = [
        "crmq_quotations.id as quotation_id",
        "crmq_quotations.code",
        "crmq_quotations.requested_data",
        "crmq_quotations.customer_id",
        "crmq_quotations.status",
        "crmq_quotations.notes",
        "crmq_quotations.request_type",
        "crmq_quotations.opportunity_type_id",
        "core_customers.name as display_name",
        "core_entity_approvals.id as approval_id",
        "crmq_quotations.entity_id",
        "crmq_quotations.email_data",
        "core_entity_approvals.level",
        "core_entity_approvals.status as approval_status",
        "core_entity_approvals.remarks",
        "crmq_quotations.opportunity_id",
        "core_users.display_name as created_by_name",
        "core_entity_approvals.date as approval_date",
        "core_users.display_name as approved_by_name",
    ]

    service_provider_columns = [
        "core_service_providers.id as service_provider_id",
        "core_service_providers.name as service_provider_name",
        "core_service_providers.status_id as service_provider_status",
    ]

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmq_quotations.code")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = [
        "crmq_quotations.id",
        "crmq_quotations.code",
        "crmq_quotations.customer_id",
        "crmq_quotations.status",
    ]
    search_columns = allowed_filters
    allowed_sorting_columns = allowed_filters

    # Fetch quotation details
    quotation_data = (
        QueryBuilderService("crmq_quotations")
        .select(*all_columns)
        .leftJoin("core_customers", "core_customers.id", "crmq_quotations.customer_id")
        .leftJoin(
            "core_entity_approvals",
            "core_entity_approvals.entity_id",
            "crmq_quotations.entity_id",
        )
        .leftJoin("core_entities", "core_entities.id", "crmq_quotations.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
        .leftJoin("core_users as cu", "cu.id", "core_entity_approvals.approved_by")
        .where("core_entity_approvals.id", id)
        .whereNull("core_entity_approvals.deleted_at")
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .first()
    )

    if not quotation_data:
        return ResponseService.response(
            "VALIDATION_ERROR", "Quotation not found.", Error.VALIDATION_ERROR
        )

    # Parse the JSON field if it exists
    raw_email_data = quotation_data.get("email_data")
    parsed_email_data = {}

    if raw_email_data:
        try:
            parsed_email_data = json.loads(raw_email_data)
        except json.JSONDecodeError:
            parsed_email_data = {"email_data": {}, "documents": []}

    # Separate into email_data and document_data
    quotation_data["email_data"] = parsed_email_data.get("email_data", {})
    quotation_data["document_data"] = parsed_email_data.get("documents", [])

    # Fetch service provider details
    service_providers = (
        QueryBuilderService("crmq_quotation_service_providers")
        .select(*service_provider_columns)
        .leftJoin(
            "core_service_providers",
            "core_service_providers.id",
            "crmq_quotation_service_providers.service_provider_id",
        )
        .where(
            "crmq_quotation_service_providers.quotation_id",
            quotation_data["quotation_id"],
        )
        .get()
    )

    quotation_data["service_providers"] = service_providers

    return ResponseService.response("SUCCESS", quotation_data, Message.DATA_FETCHED)


def quotation_approval_changes(request, id):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR", "Invalid JSON format.", Error.VALIDATION_ERROR
        )

    rules = {
        "status": "required",
        "remarks": "required",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    approval_record = (
        QueryBuilderService("core_entity_approvals").where("id", id).first()
    )
    if not approval_record:
        return ResponseService.response(
            "VALIDATION_ERROR", "Approval record not found.", Error.VALIDATION_ERROR
        )

    entity_id = approval_record["entity_id"]
    current_level = approval_record["level"] if approval_record["level"] else 0

    user = request.user if request.user.is_authenticated else None
    date = datetime.now()

    QueryBuilderService("core_entity_approvals").where("id", id).update(
        {
            "status": data["status"],
            "remarks": data["remarks"],
            "approved_by": user.id if user else 3,
            "date": date,
        }
    )

    if data["status"].lower() == "rejected":
        ruleCheck = (
            QueryBuilderService("core_entity_approval_rules")
            .where("entity_type", "common_approval")
            .where("action", "approval")
            .first()
        )

        if not ruleCheck or not ruleCheck.get("rule"):
            QueryBuilderService("core_entities").where("id", entity_id).update(
                {"approvel_status": False}
            )
            return ResponseService.response(
                "SUCCESS",
                "Approval reset after rejection (no rules).",
                Message.DATA_UPDATED,
            )

        try:
            parsed_rule = json.loads(ruleCheck["rule"])
        except (json.JSONDecodeError, TypeError):
            return ResponseService.response(
                "VALIDATION_ERROR", "Invalid rule JSON format.", Error.VALIDATION_ERROR
            )

        rules = parsed_rule.get("rules", [])
        if not rules:
            QueryBuilderService("core_entities").where("id", entity_id).update(
                {"approvel_status": False}
            )
            return ResponseService.response(
                "SUCCESS", "Approval reset (empty rules).", Message.DATA_UPDATED
            )

        QueryBuilderService("core_entities").where("id", entity_id).update(
            {"approvel_status": False}
        )
        min_level = min([r.get("level", 0) for r in rules])
        default_status = ruleCheck.get("default_status", "draft")

        for rule in rules:
            QueryBuilderService("core_entity_approvals").insert(
                {
                    "entity_id": entity_id,
                    "user": rule.get("user"),
                    "role": rule.get("role"),
                    "level": rule.get("level"),
                    "status": (
                        "pending" if rule.get("level") == min_level else default_status
                    ),
                    "remarks": None,
                }
            )

        return ResponseService.response(
            "SUCCESS",
            "Approval reset and re-routed after rejection.",
            Message.DATA_UPDATED,
        )

    if data["status"].lower() != "approved":
        return ResponseService.response(
            "SUCCESS", "Status updated.", Message.DATA_UPDATED
        )

    rule_data = (
        QueryBuilderService("core_entity_approval_rules")
        .where("entity_type", "common_approval")
        .where("action", "approval")
        .first()
    )

    if not rule_data or not rule_data.get("rule"):
        QueryBuilderService("core_entities").where("id", entity_id).update(
            {"approvel_status": True}
        )
        return ResponseService.response(
            "SUCCESS", "Final approval completed.", Message.DATA_UPDATED
        )

    try:
        rule_json = json.loads(rule_data["rule"])
    except:
        return ResponseService.response(
            "VALIDATION_ERROR", "Invalid rule format.", Error.VALIDATION_ERROR
        )

    rules = rule_json.get("rules", [])
    next_level = current_level + 1
    next_rule = next((r for r in rules if r.get("level") == next_level), None)

    if next_rule:
        updated = (
            QueryBuilderService("core_entity_approvals")
            .where("entity_id", entity_id)
            .where("level", next_level)
            .update({"status": "pending"})
        )
        if updated:
            return ResponseService.response(
                "SUCCESS", "Next level activated.", Message.DATA_UPDATED
            )

    QueryBuilderService("core_entities").where("id", entity_id).update(
        {"approvel_status": True}
    )

    # Fetch and trigger email after final approval
    quotation = (
        QueryBuilderService("crmq_quotations").where("entity_id", entity_id).first()
    )
    if quotation and quotation.get("email_data"):
        try:
            payload = json.loads(quotation["email_data"])
            request._full_data = {
                "service_provider_ids": quotation.get("service_provider_id", []),
                "subject": payload.get("email_data", {}).get("subject"),
                "body": payload.get("email_data", {}).get("body"),
                "links": [
                    doc.get("doc_link")
                    for doc in payload.get("documents", [])
                    if doc.get("doc_link")
                ],
                "documents": payload.get("documents", []),
            }
            quotation_approval_send_email(request)
        except Exception as e:
            print("Failed to send email after approval:", str(e))

    return ResponseService.response(
        "SUCCESS", "Final approval completed.", Message.DATA_UPDATED
    )


def delete_quotation_approval(id):
    # Fetch the record to ensure it exists
    data = (
        QueryBuilderService("core_entity_approvals")
        .where("core_entity_approvals.id", id)
        .first()
    )

    if not data:
        return ResponseService.response(
            "VALIDATION_ERROR", "data_not_found", Error.VALIDATION_ERROR
        )

    # Update the deleted_at field with the current date (no time)
    today = datetime.now().date()
    QueryBuilderService("core_entity_approvals").where(
        "core_entity_approvals.id", id
    ).update({"deleted_at": today})

    return ResponseService.response("SUCCESS", [], Message.DATA_DELETED)


@csrf_exempt
@api_view(["POST"])
def quotation_approval_send_email(request):
    data = request.data

    # Step 1: Validate required fields
    rules = {
        "service_provider_ids": "required|array",
        "subject": "required",
        "body": "required",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    subject = data["subject"]
    body = data["body"]

    # Step 2: Normalize service_provider_ids
    service_provider_ids = data["service_provider_ids"]
    if isinstance(service_provider_ids, str):
        service_provider_ids = [int(x.strip()) for x in service_provider_ids.split(",")]
    elif isinstance(service_provider_ids, list):
        service_provider_ids = [int(x) for x in service_provider_ids]
    else:
        return ResponseService.response(
            "VALIDATION_ERROR",
            "Invalid service_provider_ids format",
            Error.VALIDATION_ERROR,
        )

    # Step 3: Fetch provider emails
    provider_records = (
        QueryBuilderService("core_service_providers")
        .select("email")
        .whereIn("id", service_provider_ids)
        .get()
    )

    if not provider_records:
        return ResponseService.response(
            "VALIDATION_ERROR",
            "No matching service providers found.",
            Error.VALIDATION_ERROR,
        )

    recipient_emails = [
        row["email"] if row.get("email") else "kowreesan06@gmail.com"
        for row in provider_records
    ]

    # Step 4: Process documents array to get CDN URLs from doc field
    links = data.get("links", [])
    documents = data.get("documents", [])
    
    # Process documents array to get CDN URLs from doc field
    document_cdn_links = []
    if isinstance(documents, list):
        document_cdn_links = DocumentCDNService.process_documents_for_email(documents)
        
        # Also handle legacy document_link field for backward compatibility
        for doc in documents:
            if isinstance(doc, dict) and doc.get("document_link"):
                links.append(doc["document_link"])
    
    # Combine all links
    all_links = links + document_cdn_links

    # Step 5: Build email payload
    email_payload = [
        {
            "recipient_email": email,
            "subject": subject,
            "body": body,
            "priority": "high",
            "links": all_links,  # Use combined links including CDN URLs
        }
        for email in recipient_emails
    ]

    # Step 6: Send the email
    send_mail = SendMail()
    result = send_mail.send_email(email_payload)

    return ResponseService.response("SUCCESS", result, Message.EMAIL_SENT)


@csrf_exempt
@api_view(["PUT"])
def quotation_changes(request, id):
    data = request.data

    rules = {
        "remove_sp_ids": "required|array",
        "entity_id": "required",
        "email_data": "optional",
        "documents": "optional",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    remove_provider_ids = data.get("remove_sp_ids", [])
    entity_id = data.get("entity_id")
    email_data = data.get("email_data", {})
    documents = data.get("documents", [])

    # Ensure default email structure if missing
    if not email_data:
        email_data = {"subject": "No Subject", "body": "No content available."}

    email_storage_data = {
        "email_data": email_data,
        "documents": documents if documents else [],
    }

    # Save email data into quotation table
    QueryBuilderService("crmq_quotations").where("entity_id", entity_id).update(
        {"email_data": json.dumps(email_storage_data)}
    )

    # Step 1: Get the quotation_id using approval ID
    quotation_record = (
        QueryBuilderService("core_entity_approvals")
        .select("crmq_quotations.id as quotation_id")
        .leftJoin(
            "crmq_quotations",
            "crmq_quotations.entity_id",
            "core_entity_approvals.entity_id",
        )
        .where("core_entity_approvals.id", id)
        .first()
    )

    if not quotation_record or not quotation_record.get("quotation_id"):
        return ResponseService.response(
            "VALIDATION_ERROR",
            "Quotation not found for the given approval ID.",
            Error.VALIDATION_ERROR,
        )

    quotation_id = quotation_record["quotation_id"]

    removed_ids = []

    for sp_id in remove_provider_ids:
        deleted = (
            QueryBuilderService("crmq_quotation_service_providers")
            .where("quotation_id", quotation_id)
            .where("service_provider_id", sp_id)
            .delete()
        )
        if deleted:
            removed_ids.append(sp_id)

    quotation_info = (
        QueryBuilderService("crmq_quotations").where("id", quotation_id).first()
    )

    email_data_from_db = {}
    if quotation_info and quotation_info.get("email_data"):
        try:
            email_data_from_db = json.loads(quotation_info["email_data"])
        except json.JSONDecodeError:
            pass

    return ResponseService.response(
        "SUCCESS",
        {
            "quotation_id": quotation_id,
            "removed": removed_ids,
            "email_data": email_data_from_db.get("email_data", {}),
            "documents": email_data_from_db.get("documents", []),
        },
        Message.DATA_UPDATED,
    )


@csrf_exempt
@api_view(["GET"])
def entity_check(request, id):

    data = QueryBuilderService("core_entity_approvals").where("entity_id", id).first()

    if not data:
        return ResponseService.response("SUCCESS", False, Message.DATA_NOT_FOUND)

    return ResponseService.response("SUCCESS", True, Message.DATA_NOT_FOUND)
