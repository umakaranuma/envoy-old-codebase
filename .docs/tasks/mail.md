 path("api/auth-google-start/<mail_address>", ctl.auth_google_start, name="auth-google-start"),
    path("api/auth-google-callback", ctl.auth_google_callback, name="auth-google-callback"),
    path("api/gmail/status", ctl.gmail_status, name="gmail-status"),
    path("api/gmail/messages", ctl.gmail_messages, name="gmail-messages"),
    path("api/gmail/send", ctl.send_email, name="send-email"),
    path("api/gmail/history", ctl.email_history, name="email-history"),
    path("api/gmail/thread-replies", ctl.email_thread_replies, name="email-thread-replies"),
    path("api/oauth/debug", ctl.test_oauth_debug, name="oauth-debug"),
    path("api/send-message", ctl.send_message, name="send-message"),

    #chat related apis
    path("api/user-mail-config", user_mail_config, name="user_mail_config"),
    path("api/user/<int:user_id>/mail-config/<int:config_id>", delete_user_specific_mail_config, name="delete_user_specific_mail_config"),
    path("api/<int:quotation_id>/chat/<str:insurer_id>", quotation_insurer_chat_messages, name="quotation_insurer_chat_messages"),
    path("api/quotation-thread-messages/<int:quotation_id>", ctl.quotation_thread_messages, name="quotation_insurer_chat_messages"),

    # Chatmail endpoints
    path("api/chatmail/send", send_chatmail_message, name="send_chatmail_message"),
    path("api/chatmail/messages", get_chatmail_messages, name="get_chatmail_messages"),
    path("api/chatmail/conversations", get_chatmail_conversations, name="get_chatmail_conversations"),
    path("api/chatmail/sync-thread", sync_gmail_thread, name="sync_gmail_thread"),
    path("api/chatmail/mark-conversation-seen", mark_conversation_seen, name="mark_conversation_seen"),
    path("api/chatmail/download-attachment", download_attachment, name="download_attachment"),
    path("api/chatmail/attachment-info", get_attachment_info, name="get_attachment_info"),
    path("api/chatmail/gmail-webhook", gmail_webhook, name="gmail_webhook"),
    path("api/gmail/push-webhook", gmail_push_webhook, name="gmail_push_webhook"),
    
    # Quotation chat messages endpoint
    path("api/<int:quotation_id>/chat-messages/<str:insurer_id>", quotation_chat_messages, name="quotation_chat_messages"),
    # Quotation sync conversations endpoint
    path("api/quotation/<int:quotation_id>/sync-conversations", quotation_sync_conversations, name="quotation_sync_conversations"),
    
    # Policy chat messages endpoint
    path("api/policy/<int:policy_id>/chat-messages", policy_chat_messages, name="policy_chat_messages"),
    # Policy sync conversations endpoint
    path("api/policy/<int:policy_id>/sync-conversations", policy_sync_conversations, name="policy_sync_conversations"),
    # Policy sync conversations endpoint (new with endorsement request logic)
    path("api/policy/<int:policy_id>/sync-endorsement-requests", policy_sync_conversations_new, name="policy_sync_conversations_new"),



    from datetime import datetime
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from mServices.ResponseService import ResponseService
from mServices.QueryBuilderService import QueryBuilderService
from mServices.ValidatorService import ValidatorService
from envoy.constants import Error
import requests
from django.conf import settings
import os
from envoy.models.form_submissions import CoreFormSubmission
from envoy.controllers.services.NotificationService import NotificationService




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
        "crmp_request_policies.policy_base_id as policy_base_id",
        "crmp_policy_base.customer_id as customer_id",
        "core_status.name as status",
        "core_entity_notes.notes as notes",
        "crmp_request_types.name as request_type",
        "crm_opportunity_types.id as opportunity_type_id",
        "crm_opportunity_types.title as opportunity_type_title",
        "crmp_request_policies.entity_id as entity_id",
        "crm_opportunities.id as opportunity_id",
        "crm_opportunities.title as opportunity_title",
        "core_customers.name as display_name",
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

    # Get status filter from request parameters
    status_filter = request.GET.get("status", "").strip().lower()

    approvals_query = (
        QueryBuilderService("core_entity_approvals")
        .select("entity_id", "id")
    )
    
    # Apply status filter if provided
    if status_filter:
        if status_filter == "open":
            approvals_query = approvals_query.where("status", "open")
        elif status_filter == "pending":
            approvals_query = approvals_query.where("status", "pending")
        elif status_filter == "approved":
            approvals_query = approvals_query.where("status", "approved")
        elif status_filter == "rejected":
            approvals_query = approvals_query.where("status", "rejected")
        else:
            # If invalid status provided, return empty result
            return ResponseService.response("SUCCESS", [], f"No approvals found with status: {status_filter}")
    else:
        # Default behavior: exclude "open" status (existing logic)
        approvals_query = approvals_query.whereNotIn("status", "open")

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
        if status_filter:
            return ResponseService.response("SUCCESS", [], f"No approvals found with status: {status_filter}")
        else:
            return ResponseService.response("SUCCESS", [], "No pending approvals found")

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
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    # Separate search columns for quotations and policies
    quotation_search_columns = [
        "crmq_quotations.code",
        "core_customers.name",
        "crm_opportunities.title",
    ]
    
    policy_search_columns = [
        "crmp_request_policies.policy_request_id",
        "core_customers.name",
        "crm_opportunities.title",
    ]
    
    allowed_filters = [
        "crmq_quotations.id",
        "crmq_quotations.code",
        "crmq_quotations.customer_id",
        "crmq_quotations.status",
        "crmp_request_policies.policy_request_id",
        "core_customers.name",
    ]
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
            .apply_conditions(filter_json, allowed_filters, search_string, quotation_search_columns)
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
                "crmp_policy_base", "crmp_policy_base.id", "crmp_request_policies.policy_base_id"
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
            .leftJoin(
                "core_customers", "core_customers.id", "crmp_policy_base.customer_id"
            )
            .whereIn("crmp_request_policies.entity_id", policy_entity_ids)
            .whereIn("core_entity_approvals.id", policy_approval_ids)
            .whereNull("core_entity_approvals.deleted_at")
            .apply_conditions(filter_json, allowed_filters, search_string, policy_search_columns)
            .get()
        )
        policy_results = policy_query

    merged_rows = []
    if isinstance(quotation_results, list):
        for row in quotation_results:
            row_copy = dict(row)
            row_copy["entity_type"] = "quotation"
            
            # Set quotation_request_id and nullify policy fields
            row_copy["quotation_request_id"] = row_copy.get("id")
            row_copy["policy_request_id"] = None
            row_copy["policy_base_id"] = None
            
            # Format request_type field for quotations
            request_type = row_copy.get("request_type", "").lower()
            if request_type == "new":
                row_copy["request_type"] = "New Request"
            elif request_type == "renew":
                row_copy["request_type"] = "Renewal Request"
            
            merged_rows.append(row_copy)
    if isinstance(policy_results, list):
        for row in policy_results:
            row_copy = dict(row)
            row_copy["entity_type"] = "policy"

            # Set policy fields and nullify quotation_request_id
            row_copy["policy_request_id"] = row_copy.get("code")
            row_copy["policy_base_id"] = row_copy.get("policy_base_id")
            row_copy["quotation_request_id"] = None

             # Format request_type field for policies
            request_type = row_copy.get("request_type", "").lower()
            if request_type == "new":
                row_copy["request_type"] = "New Request"
            elif request_type == "renewal":
                row_copy["request_type"] = "Renewal Request"
            
            # Format opportunity_type_id as array for policies
            opportunity_type_id = row_copy.get("opportunity_type_id")
            if opportunity_type_id:
                # If it's a single ID, convert to array format
                if isinstance(opportunity_type_id, int):
                    row_copy["opportunity_type_id"] = f"[{opportunity_type_id}]"
                elif isinstance(opportunity_type_id, str):
                    # If it's already a string, ensure it's in array format
                    if not opportunity_type_id.startswith("["):
                        row_copy["opportunity_type_id"] = f"[{opportunity_type_id}]"
            else:
                # If no opportunity_type_id, set as empty array
                row_copy["opportunity_type_id"] = "[]"
            
            merged_rows.append(row_copy)

    # Always sort by core_entity_approvals.id in descending order
    def sort_key(item):
        return item.get("approval_id", 0)
    
    try:
        merged_rows.sort(key=sort_key, reverse=True)  # Always descending order
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

    message = "Data fetched successfully"
    if status_filter:
        message = f"Data fetched successfully (filtered by status: {status_filter})"
    
    return ResponseService.response("SUCCESS", results, message)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def handle_quotation_approval(request, id):
    if request.method == "GET":
        return single_quotation_approval(request, id)

    if request.method == "PUT":
        return quotation_changes(request, id)

    if request.method == "DELETE":
        return delete_quotation_approval(id)


import json

def single_quotation_approval(request, id):
    """Return a UNIFORM payload for a single approval (quotation/policy) with normalized opportunity_types."""

    # ---- approval → entity ----
    meta = (
        QueryBuilderService("core_entity_approvals")
        .select(
            "core_entity_approvals.id as approval_id",
            "core_entity_approvals.entity_id as entity_id",
            "core_entities.type as entity_type",
        )
        .leftJoin("core_entities", "core_entities.id", "core_entity_approvals.entity_id")
        .where("core_entity_approvals.id", id)
        .whereNull("core_entity_approvals.deleted_at")
        .first()
    )
    if not meta:
        return ResponseService.response("VALIDATION_ERROR", "Approval not found.", "Validation error")

    entity_id = meta.get("entity_id")
    etype = (meta.get("entity_type") or "").strip().lower()

    # ---- helpers ----
    def _parse_email(raw):
        if not raw:
            return {}, []
        try:
            p = json.loads(raw)
            return p.get("email_data") or {}, p.get("documents") or []
        except json.JSONDecodeError:
            return {}, []

    def _parse_id_list(v):
        """Turn '[1, 2]' or '1,2' or 1 → [1,2] (ints)."""
        if v is None:
            return []
        if isinstance(v, int):
            return [v]
        s = str(v).strip()
        try:
            j = json.loads(s)
            if isinstance(j, list):
                out = []
                for x in j:
                    try:
                        out.append(int(x))
                    except:
                        pass
                return out
        except Exception:
            pass
        s = s.strip("[]")
        out = []
        for part in s.split(","):
            part = part.strip()
            if part.isdigit():
                out.append(int(part))
        return out

    # -------------------- QUOTATION --------------------
    if etype == "quotation approval":
        cols = [
            "crmq_quotations.code as code",
            "crmq_quotations.requested_data as request_date",
            "crmq_quotations.customer_id as customer_id",
            "crmq_quotations.status as status",
            "crmq_quotations.notes as notes",
            "crmq_quotations.request_type as request_type",
            "crmq_quotations.opportunity_type_id as opportunity_type_id",  # may be '[1,2]' string
            "crmq_quotations.opportunity_id as opportunity_id",
            "crmq_quotations.entity_id as entity_id",
            "crmq_quotations.email_data as raw_email_data",
            "core_customers.name as customer_name",
            "crm_opportunities.title as opportunity_title",
            "crm_opportunities.code as opportunity_code",
            "core_entity_approvals.id as approval_id",
            "core_entity_approvals.level as approval_level",
            "core_entity_approvals.status as approval_status",
            "core_entity_approvals.remarks as approval_remarks",
            "core_entity_approvals.date as approval_date",
            "core_users.display_name as created_by_name",
            "cu.display_name as approved_by_name",
        ]
        data = (
            QueryBuilderService("crmq_quotations")
            .select(*cols)
            .leftJoin("core_customers", "core_customers.id", "crmq_quotations.customer_id")
            .leftJoin("crm_opportunities", "crm_opportunities.id", "crmq_quotations.opportunity_id")
            .leftJoin("core_entity_approvals", "core_entity_approvals.entity_id", "crmq_quotations.entity_id")
            .leftJoin("core_entities", "core_entities.id", "crmq_quotations.entity_id")
            .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
            .leftJoin("core_users as cu", "cu.id", "core_entity_approvals.approved_by")
            .where("crmq_quotations.entity_id", entity_id)
            .whereNull("core_entity_approvals.deleted_at")
            .first()
        )
        if not data:
            return ResponseService.response("VALIDATION_ERROR", "Quotation not found.", "Validation error")

        # Normalize opportunity_types for quotation
        ids = _parse_id_list(data.get("opportunity_type_id"))
        opp_list = []
        if ids:
            titles = QueryBuilderService("crm_opportunity_types").select("id", "title").whereIn("id", ids).get() or []
            title_map = {t["id"]: t["title"] for t in titles}
            opp_list = [{"id": i, "title": title_map.get(i)} for i in ids]

        # keep single fields for quotation (back-compat)
        data["opportunity_type_id"] = opp_list[0]["id"] if opp_list else None
        data["opportunity_type_title"] = opp_list[0]["title"] if opp_list else None

        # Format request_type field
        request_type = data.get("request_type", "").lower()
        if request_type == "new":
            data["request_type"] = "New Request"
        elif request_type == "renew":
            data["request_type"] = "Renewal Request"

        email_data, document_data = _parse_email(data.pop("raw_email_data", None))

        sp_cols = [
            "core_service_providers.id as service_provider_id",
            "core_service_providers.name as service_provider_name",
            "core_service_providers.status_id as service_provider_status",
        ]
        sps = (
            QueryBuilderService("crmq_quotation_service_providers")
            .select(*sp_cols)
            .leftJoin("core_service_providers", "core_service_providers.id", "crmq_quotation_service_providers.service_provider_id")
            .leftJoin("crmq_quotations", "crmq_quotations.id", "crmq_quotation_service_providers.quotation_id")
            .where("crmq_quotations.entity_id", entity_id)
            .get()
        ) or []

        payload = {
            "entity_type": "quotation",
            **data,
            "opportunity_types": opp_list,
            "email_data": email_data,
            "document_data": document_data,
            "service_providers": sps,
        }
        return ResponseService.response("SUCCESS", payload, "Data fetched successfully")

    # -------------------- POLICY --------------------
    if etype == "policy":
        # base policy record (without single opp fields; we'll provide array only)
        cols = [
            "crmp_request_policies.policy_request_id as code",
            "crmp_request_policies.policy_request_date as request_date",
            "crmp_policy_base.customer_id as customer_id",
            "core_status.name as status",
            "core_entity_notes.notes as notes",
            "crmp_request_types.name as request_type",
            "crmp_request_policies.entity_id as entity_id",
            "crmp_request_policies.email_data as policy_email_data",
            "crmp_policy_base.risk_type_id as opportunity_type_id",
            "crm_opportunities.id as opportunity_id",
            "crm_opportunities.title as opportunity_title",
            "crm_opportunities.code as opportunity_code",
            "core_entity_approvals.id as approval_id",
            "core_entity_approvals.level as approval_level",
            "core_entity_approvals.status as approval_status",
            "core_entity_approvals.remarks as approval_remarks",
            "core_entity_approvals.date as approval_date",
            "core_users.display_name as created_by_name",
            "cu.display_name as approved_by_name",
            "core_customers.name as customer_name",
        ]
        data = (
            QueryBuilderService("crmp_request_policies")
            .select(*cols)
            .leftJoin("core_entity_approvals", "core_entity_approvals.entity_id", "crmp_request_policies.entity_id")
            .leftJoin("core_entities", "core_entities.id", "crmp_request_policies.entity_id")
            .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
            .leftJoin("core_users as cu", "cu.id", "core_entity_approvals.approved_by")
            .leftJoin("crmp_policy_base", "crmp_policy_base.id", "crmp_request_policies.policy_base_id")
            .leftJoin("core_status", "core_status.id", "crmp_request_policies.status_id")
            .leftJoin("core_entity_notes", "core_entity_notes.entity_id", "crmp_request_policies.entity_id")
            .leftJoin("crmp_request_types", "crmp_request_types.id", "crmp_policy_base.request_type_id")
            .leftJoin("crm_opportunities", "crm_opportunities.id", "crmp_policy_base.lead_id")
            .leftJoin("core_customers", "core_customers.id", "crmp_policy_base.customer_id")
            .where("crmp_request_policies.entity_id", entity_id)
            .whereNull("core_entity_approvals.deleted_at")
            .first()
        )
        if not data:
            return ResponseService.response("VALIDATION_ERROR", "Policy request not found.", "Validation error")

        # Resolve policy_base_id first (more reliable for multi risk types & insurer)
        base = (
            QueryBuilderService("crmp_request_policies")
            .select("crmp_policy_base.id as policy_base_id")
            .leftJoin("crmp_policy_base", "crmp_policy_base.id", "crmp_request_policies.policy_base_id")
            .where("crmp_request_policies.entity_id", entity_id)
            .first()
        )
        policy_base_id = base.get("policy_base_id") if base else None

        # Build opportunity_types from mapping table
        opp_list = []
        if policy_base_id:
            opp_list = (
                QueryBuilderService("crmp_policy_base_risk_types")
                .select(
                    "crm_opportunity_types.id as id",
                    "crm_opportunity_types.title as title",
                )
                .leftJoin("crm_opportunity_types", "crm_opportunity_types.id", "crmp_policy_base_risk_types.risk_type_id")
                .where("crmp_policy_base_risk_types.policy_base_id", policy_base_id)
                .get()
            ) or []

        # Policy service_providers from insurer_id (make it a list)
        sps = []
        if policy_base_id:
            sp = (
                QueryBuilderService("crmp_policy_base")
                .select(
                    "core_service_providers.id as service_provider_id",
                    "core_service_providers.name as service_provider_name",
                    "core_service_providers.status_id as service_provider_status",
                )
                .leftJoin("core_service_providers", "core_service_providers.id", "crmp_policy_base.insurer_id")
                .where("crmp_policy_base.id", policy_base_id)
                .first()
            )
            if sp:
                sps = [sp]

        email_data, document_data = _parse_email(data.pop("policy_email_data", None))

        # Format request_type field for policies
        request_type = data.get("request_type", "").lower()
        if request_type == "new":
            data["request_type"] = "New Request"
        elif request_type == "renewal":
            data["request_type"] = "Renewal Request"

        # Assemble payload (include opportunity_type_id for policy)
        payload = {
            "entity_type": "policy",
            **data,
            "opportunity_types": opp_list,   # always an array
            "email_data": email_data,
            "document_data": document_data,
            "service_providers": sps,
        }

        return ResponseService.response("SUCCESS", payload, "Data fetched successfully")

    return ResponseService.response("VALIDATION_ERROR", f"Unsupported entity type: {meta.get('entity_type')}", "Validation error")



# make sure you have: import json

def quotation_changes(request, id):
    data = request.data

    rules = {
        "service_provider_ids": "required|array",
        "entity_id": "required",   # kept for back-compat; we resolve actual entity from approval
        "email_data": "optional",
        "documents": "optional",
    }
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation error")

    # Normalize inputs
    raw_sp_ids = data.get("service_provider_ids") or []
    try:
        sp_ids = sorted({int(x) for x in raw_sp_ids})
    except Exception:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"service_provider_ids": ["Must be an array of integers"]},
            "Validation error",
        )

    email_data = data.get("email_data") or {}
    documents = data.get("documents") or []

    # Extract documents from email_data if they exist there
    email_documents = []
    if isinstance(email_data, dict) and "documents" in email_data:
        email_documents = email_data.get("documents", [])
        # Remove documents from email_data to keep only subject and body
        email_data = {k: v for k, v in email_data.items() if k != "documents"}

    # Combine documents from both sources (top-level and email_data)
    all_documents = documents + email_documents

    # Filter email_data to only include essential fields (subject and body)
    # Remove unnecessary fields like files, recipientNames, defaultTemplate
    if isinstance(email_data, dict):
        filtered_email_data = {}
        for key in ["subject", "body"]:
            if key in email_data:
                filtered_email_data[key] = email_data[key]
        email_data = filtered_email_data

    # Ensure default email structure if missing
    if not isinstance(email_data, dict) or "subject" not in email_data or "body" not in email_data:
        email_data = {
            "subject": (email_data.get("subject") if isinstance(email_data, dict) else None) or "No Subject",
            "body": (email_data.get("body") if isinstance(email_data, dict) else None) or "No content available.",
        }

    email_storage_data = {
        "email_data": email_data,  # Now contains only subject and body
        "documents": all_documents if isinstance(all_documents, list) else [],
    }

    # Resolve entity type + entity_id from approval id (authoritative)
    meta = (
        QueryBuilderService("core_entity_approvals")
        .select(
            "core_entity_approvals.entity_id as entity_id",
            "core_entities.type as entity_type",
        )
        .leftJoin("core_entities", "core_entities.id", "core_entity_approvals.entity_id")
        .where("core_entity_approvals.id", id)
        .first()
    )
    if not meta:
        return ResponseService.response(
            "VALIDATION_ERROR",
            "Approval not found for given id.",
            "Validation error",
        )

    entity_id = meta.get("entity_id")
    entity_type = (meta.get("entity_type") or "").strip().lower()

    # ---------- QUOTATION (editable providers) ----------
    if entity_type in ("quotation approval", "quotation"):
        # Save email data
        QueryBuilderService("crmq_quotations").where("entity_id", entity_id).update(
            {"email_data": json.dumps(email_storage_data)}
        )

        # Get quotation_id
        quotation_record = (
            QueryBuilderService("crmq_quotations")
            .select("id as quotation_id")
            .where("entity_id", entity_id)
            .first()
        )
        if not quotation_record or not quotation_record.get("quotation_id"):
            return ResponseService.response(
                "VALIDATION_ERROR",
                "Quotation not found for the resolved entity.",
                "Validation error",
            )
        quotation_id = quotation_record["quotation_id"]

        # Sync mapping table to EXACTLY match sp_ids (no arrays returned in payload)
        current_rows = (
            QueryBuilderService("crmq_quotation_service_providers")
            .select("service_provider_id")
            .where("quotation_id", quotation_id)
            .get()
        ) or []
        current_ids = sorted({int(r["service_provider_id"]) for r in current_rows if r.get("service_provider_id") is not None})

        to_add = [sp for sp in sp_ids if sp not in current_ids]
        to_remove = [sp for sp in current_ids if sp not in sp_ids]

        for sp_id in to_add:
            QueryBuilderService("crmq_quotation_service_providers").insert(
                {"quotation_id": quotation_id, "service_provider_id": sp_id}
            )
        if to_remove:
            QueryBuilderService("crmq_quotation_service_providers") \
                .where("quotation_id", quotation_id) \
                .whereIn("service_provider_id", to_remove) \
                .delete()

        # Final provider details
        final_rows = (
            QueryBuilderService("crmq_quotation_service_providers")
            .select("service_provider_id")
            .where("quotation_id", quotation_id)
            .get()
        ) or []
        final_ids = sorted({int(r["service_provider_id"]) for r in final_rows if r.get("service_provider_id") is not None})

        service_providers = []
        if final_ids:
            service_providers = (
                QueryBuilderService("core_service_providers")
                .select("id", "name", "email", "status_id")
                .whereIn("id", final_ids)
                .get()
            ) or []

        # Read back email_data for response
        quotation_info = QueryBuilderService("crmq_quotations").where("id", quotation_id).first()
        email_data_from_db = {}
        if quotation_info and quotation_info.get("email_data"):
            try:
                email_data_from_db = json.loads(quotation_info["email_data"])
            except json.JSONDecodeError:
                email_data_from_db = {"email_data": {}, "documents": []}

        return ResponseService.response(
            "SUCCESS",
            {
                "mode": "quotation",
                "entity_id": entity_id,
                "quotation_id": quotation_id,
                "service_providers": service_providers,
                "email_data": email_data_from_db.get("email_data", {}),
                "documents": email_data_from_db.get("documents", []),
            },
            "Quotation updated successfully",
        )

    # ---------- POLICY (providers NOT editable, same response shape) ----------
    elif entity_type == "policy":
        # Save email data only; DO NOT change providers/insurer
        QueryBuilderService("crmp_request_policies").where("entity_id", entity_id).update(
            {"email_data": json.dumps(email_storage_data)}
        )

        # Resolve policy + current insurer (read-only)
        policy_row = (
            QueryBuilderService("crmp_request_policies as pr")
            .select("pr.id as policy_id", "pr.policy_base_id as policy_base_id")
            .where("pr.entity_id", entity_id)
            .first()
        )
        if not policy_row or not policy_row.get("policy_id"):
            return ResponseService.response(
                "VALIDATION_ERROR",
                "Policy request not found for the resolved entity.",
                "Validation error",
            )

        policy_id = policy_row["policy_id"]
        policy_base_id = policy_row.get("policy_base_id")

        service_providers = []
        if policy_base_id:
            pb = (
                QueryBuilderService("crmp_policy_base")
                .select("insurer_id")
                .where("id", policy_base_id)
                .first()
            ) or {}
            insurer_id = pb.get("insurer_id")
            if insurer_id:
                provider = (
                    QueryBuilderService("core_service_providers")
                    .select("id", "name", "email", "status_id")
                    .where("id", insurer_id)
                    .first()
                )
                if provider:
                    service_providers = [provider]

        # Read-back email_data for response
        pr_info = QueryBuilderService("crmp_request_policies").where("id", policy_id).first()
        email_data_from_db = {}
        if pr_info and pr_info.get("email_data"):
            try:
                email_data_from_db = json.loads(pr_info["email_data"])
            except json.JSONDecodeError:
                email_data_from_db = {"email_data": {}, "documents": []}

        return ResponseService.response(
            "SUCCESS",
            {
                "mode": "policy",
                "entity_id": entity_id,
                "policy_id": policy_id,
                "policy_base_id": policy_base_id,
                "service_providers": service_providers,  # read-only
                "email_data": email_data_from_db.get("email_data", {}),
                "documents": email_data_from_db.get("documents", []),
            },
            "default_update_success_msg",
        )

    # ---------- Unsupported ----------
    else:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"entity_type": entity_type},
            "validation_error",
        )



# --- auth helpers ---
def get_bearer_token(request):
    """
    Return the raw Bearer/JWT token from the Authorization header, or None.
    Accepts schemes: Bearer / JWT / Token (case-insensitive).
    """
    auth_header = request.headers.get("Authorization") or request.META.get("HTTP_AUTHORIZATION", "")
    scheme, _, token = auth_header.partition(" ")
    if token and scheme.lower() in ("bearer", "jwt", "token"):
        return token.strip()
    return None

def redact_token(token: str, left: int = 12, right: int = 8) -> str:
    if not token:
        return ""
    return token if len(token) <= (left + right) else f"{token[:left]}...{token[-right:]}"


@csrf_exempt
@api_view(["PUT"])
def quotation_approval_changes(request, id):
    try:
        data = json.loads(request.body)
        # --- DEBUG: print Bearer/JWT token (using helper) ---
        token = get_bearer_token(request)
        if token:
            print(f"[DEBUG] Authorization scheme=Bearer, token={redact_token(token)}")
        else:
            print("[DEBUG] No Bearer/JWT token found in Authorization header")

    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR", "Invalid JSON format.", "Validation error"
        )

    rules = {"status": "required", "remarks": "required"}
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation error")

    approval_record = (
        QueryBuilderService("core_entity_approvals").where("id", id).first()
    )
    if not approval_record:
        return ResponseService.response(
            "VALIDATION_ERROR", "Approval record not found.", "Validation error"
        )

    # Check if status is already approved
    current_status = approval_record.get("status", "").lower()
    if current_status == "approved":
        return ResponseService.response(
            "VALIDATION_ERROR",
            "Approval status is already approved. No changes needed.",
            "validation_error",
        )

    entity_id = approval_record["entity_id"]
    current_level = approval_record["level"] if approval_record["level"] else 0

    user = request.user if request.user.is_authenticated else None
    date = datetime.now()

    # Update this approval row
    QueryBuilderService("core_entity_approvals").where("id", id).update(
        {
            "status": data["status"],
            "remarks": data["remarks"],
            "approved_by": user.id if user else 3,
            "date": date,
        }
    )

    # ========== NOTIFICATION SERVICE ==========
    # Send notification to sales agent (creator) about approval/rejection
    try:
        # Get entity details to find the creator (sales agent)
        entity_row = QueryBuilderService("core_entities").where("id", entity_id).first()
        if entity_row:
            sales_agent_id = entity_row.get("created_by_id")  # Fixed: column name is created_by_id
            entity_type_str = (entity_row.get("type") or "").strip().lower()
            
            print(f"[NOTIFICATION DEBUG] sales_agent_id: {sales_agent_id}, entity_type: {entity_type_str}")
            
            # Skip notification if no sales agent found
            if not sales_agent_id:
                print(f"[NOTIFICATION] Skipping notification - no sales_agent_id found for entity_id: {entity_id}")
                raise Exception("No sales agent found")
            
            # Get approver name
            approver_name = "Unknown"
            if user:
                approver_name = user.display_name if hasattr(user, 'display_name') else f"User {user.id}"
            else:
                approver_record = QueryBuilderService("core_users").where("id", user.id if user else 3).first()
                if approver_record:
                    approver_name = approver_record.get("display_name", "Unknown")
            
            # Determine notification type and gather data based on entity type
            if entity_type_str == "quotation approval":
                # Get quotation details
                quotation = QueryBuilderService("crmq_quotations").where("entity_id", entity_id).first()
                if quotation:
                    # Get customer name
                    customer_name = "Unknown Customer"
                    if quotation.get("customer_id"):
                        customer = QueryBuilderService("core_customers").select("name").where("id", quotation["customer_id"]).first()
                        if customer:
                            customer_name = customer.get("name", "Unknown Customer")
                    
                    # Get opportunity type
                    opportunity_type_name = "N/A"
                    if quotation.get("opportunity_type_id"):
                        try:
                            # opportunity_type_id is stored as JSON, could be single ID or array
                            opportunity_type_id = quotation["opportunity_type_id"]
                            if isinstance(opportunity_type_id, str):
                                opportunity_type_id = json.loads(opportunity_type_id)
                            
                            # Handle if it's a single ID or array
                            if isinstance(opportunity_type_id, list) and len(opportunity_type_id) > 0:
                                opportunity_type_id = opportunity_type_id[0]
                            
                            if opportunity_type_id:
                                opportunity_type = QueryBuilderService("crm_opportunity_types")\
                                    .select("title")\
                                    .where("id", opportunity_type_id)\
                                    .first()
                                if opportunity_type and opportunity_type.get("title"):
                                    opportunity_type_name = opportunity_type["title"]
                        except Exception as e:
                            print(f"[NOTIFICATION] Error parsing opportunity_type_id: {e}")
                    
                    # Get insurer names from crmq_quotation_service_providers
                    insurer_names = []
                    if quotation.get("id"):
                        service_providers = QueryBuilderService("crmq_quotation_service_providers")\
                            .select("service_provider_id")\
                            .where("quotation_id", quotation["id"])\
                            .get()
                        
                        if service_providers:
                            sp_ids = [sp.get("service_provider_id") for sp in service_providers if sp.get("service_provider_id")]
                            if sp_ids:
                                insurers = QueryBuilderService("core_service_providers")\
                                    .select("name")\
                                    .whereIn("id", sp_ids)\
                                    .get()
                                insurer_names = [ins.get("name") for ins in insurers if ins.get("name")]
                    
                    # Build notification message
                    insurers_str = ", ".join(insurer_names) if insurer_names else "N/A"
                    
                    if data["status"].lower() == "approved":
                        title = "Quotation Approved"
                        message = (f"Your quotation request has been approved by {approver_name}. "
                                 f"Customer: {customer_name}, Request ID: {quotation.get('code', 'N/A')}, "
                                 f"Opportunity Type: {opportunity_type_name}, Insurers: {insurers_str}")
                    else:
                        title = "Quotation Rejected"
                        message = (f"Your quotation request has been rejected by {approver_name}. "
                                 f"Customer: {customer_name}, Request ID: {quotation.get('code', 'N/A')}, "
                                 f"Opportunity Type: {opportunity_type_name}, Insurers: {insurers_str}")
                    
                    # Send notification to sales agent (not customer)
                    NotificationService.generate_notification(
                        type_code="quotation_approval",
                        title=title,
                        meta_data={
                            "quotation_id": quotation.get("id"),
                            "quotation_code": quotation.get("code"),
                            "customer_id": quotation.get("customer_id"),  # For reference only
                            "customer_name": customer_name,
                            "approver_name": approver_name,
                            "opportunity_type": opportunity_type_name,
                            "status": data["status"]
                        },
                        message=message,
                        customer_id=None,  # Not for customer
                        user_id=sales_agent_id  # Notification goes to sales agent
                    )
            
            elif entity_type_str == "policy":
                # Get policy details
                policy = QueryBuilderService("crmp_request_policies").where("entity_id", entity_id).first()
                if policy:
                    # Get customer name from policy base
                    customer_name = "Unknown Customer"
                    insurer_name = "Unknown Insurer"
                    product_names = []
                    
                    risk_type_name = "N/A"
                    
                    if policy.get("policy_base_id"):
                        policy_base = QueryBuilderService("crmp_policy_base")\
                            .select("customer_id", "insurer_id", "product_id", "product_group_id", "risk_type_id")\
                            .where("id", policy["policy_base_id"])\
                            .first()
                        
                        if policy_base:
                            if policy_base.get("customer_id"):
                                customer = QueryBuilderService("core_customers").select("name").where("id", policy_base["customer_id"]).first()
                                if customer:
                                    customer_name = customer.get("name", "Unknown Customer")
                            
                            if policy_base.get("insurer_id"):
                                insurer = QueryBuilderService("core_service_providers").select("name").where("id", policy_base["insurer_id"]).first()
                                if insurer:
                                    insurer_name = insurer.get("name", "Unknown Insurer")
                            
                            # Get product name - check both product_id and product_group_id
                            if policy_base.get("product_id"):
                                vendor_product = QueryBuilderService("core_vendor_products")\
                                    .select("name")\
                                    .where("id", policy_base["product_id"])\
                                    .whereNull("deleted_at")\
                                    .first()
                                if vendor_product and vendor_product.get("name"):
                                    product_names.append(f"{vendor_product['name']} (Product)")
                            
                            if policy_base.get("product_group_id"):
                                product_group = QueryBuilderService("core_product_groups")\
                                    .select("name")\
                                    .where("id", policy_base["product_group_id"])\
                                    .whereNull("deleted_at")\
                                    .first()
                                if product_group and product_group.get("name"):
                                    product_names.append(f"{product_group['name']} (Product Group)")
                            
                            # Get risk type name
                            if policy_base.get("risk_type_id"):
                                risk_type = QueryBuilderService("crm_opportunity_types")\
                                    .select("title")\
                                    .where("id", policy_base["risk_type_id"])\
                                    .first()
                                if risk_type and risk_type.get("title"):
                                    risk_type_name = risk_type["title"]
                    
                    products_str = ", ".join(product_names) if product_names else "N/A"
                    
                    # Build notification message
                    if data["status"].lower() == "approved":
                        title = "Policy Approved"
                        message = (f"Your policy request has been approved by {approver_name}. "
                                 f"Customer: {customer_name}, Request ID: {policy.get('policy_request_id', 'N/A')}, "
                                 f"Product: {products_str}, Risk Type: {risk_type_name}, "
                                 f"Insurer: {insurer_name}")
                    else:
                        title = "Policy Rejected"
                        message = (f"Your policy request has been rejected by {approver_name}. "
                                 f"Customer: {customer_name}, Request ID: {policy.get('policy_request_id', 'N/A')}, "
                                 f"Product: {products_str}, Risk Type: {risk_type_name}, "
                                 f"Insurer: {insurer_name}")
                    
                    # Send notification to sales agent (not customer)
                    NotificationService.generate_notification(
                        type_code="policy_approval",
                        title=title,
                        meta_data={
                            "policy_id": policy.get("id"),
                            "policy_request_id": policy.get("policy_request_id"),
                            "customer_id": policy_base.get("customer_id") if policy.get("policy_base_id") and policy_base else None,  # For reference only
                            "customer_name": customer_name,
                            "product": products_str,
                            "risk_type": risk_type_name,
                            "insurer_name": insurer_name,
                            "approver_name": approver_name,
                            "status": data["status"]
                        },
                        message=message,
                        customer_id=None,  # Not for customer
                        user_id=sales_agent_id  # Notification goes to sales agent
                    )
    except Exception as notify_exc:
        print(f"[NOTIFICATION] Error sending notification: {notify_exc}")
        # Don't fail the approval process if notification fails
    # ========== END NOTIFICATION SERVICE ==========

    # Update quotation status when approval is approved or rejected
    # This needs to be done BEFORE any return statements
    entity_row = QueryBuilderService("core_entities").where("id", entity_id).first()
    entity_type = (entity_row or {}).get("type", "") if entity_row else ""
    
    if str(entity_type).strip().lower() == "quotation approval" and data["status"].lower() in ["approved", "rejected"]:
        # Determine the status type based on approval status
        status_type = "quotation_inprogress" if data["status"].lower() == "approved" else "quotation_rejected"
        
        status_data = QueryBuilderService("core_status as status")\
            .select("status.id AS status_id","status.name AS status_name")\
            .where("status.type", status_type)\
            .first()
        
        if status_data:
            # Update quotation status and status_id
            update_data = {
                "status": status_data['status_name']
            }
            
            # Try to update status_id if the field exists in the table
            try:
                # First try to update with both status and status_id
                update_data_with_id = {
                    "status": status_data['status_name'],
                    "status_id": status_data['status_id']
                }
                QueryBuilderService("crmq_quotations").where("entity_id", entity_id).update(update_data_with_id)
            except Exception as e:
                # If status_id field doesn't exist, just update status
                print(f"[DEBUG] status_id field not found in crmq_quotations table: {e}")
                QueryBuilderService("crmq_quotations").where("entity_id", entity_id).update(update_data)

    # Rejection branch
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
                "Data updated successfully",
            )

        try:
            parsed_rule = json.loads(ruleCheck["rule"])
        except (json.JSONDecodeError, TypeError):
            return ResponseService.response(
                "VALIDATION_ERROR", "Invalid rule JSON format.", "Validation error"
            )

        rules = parsed_rule.get("rules", [])
        if not rules:
            QueryBuilderService("core_entities").where("id", entity_id).update(
                {"approvel_status": False}
            )
            return ResponseService.response(
                "SUCCESS", "Approval reset (empty rules).", "Data updated successfully"
            )

        QueryBuilderService("core_entities").where("id", entity_id).update(
            {"approvel_status": False}
        )
        min_level = min([r.get("level", 0) for r in rules])
        default_status = ruleCheck.get("default_status", "draft")

        for rule in rules:
            rule_level = rule.get("level")
            QueryBuilderService("core_entity_approvals").where("entity_id", entity_id).where("level", rule_level).update(
                {
                    "user": rule.get("user"),
                    "role": rule.get("role"),
                    "level": rule.get("level"),
                    "status": (
                        "pending" if rule_level == min_level else default_status
                    ),
                    "remarks": None,
                }
            )

        return ResponseService.response(
            "SUCCESS",
            "Approval reset and re-routed after rejection.",
            "default_update_success_msg",
        )

    # Non-approved simple update
    if data["status"].lower() != "approved":
        return ResponseService.response(
            "SUCCESS", "Status updated.", "default_update_success_msg"
        )

    # Pull the common_approval rule set
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
        # Continue to email branching after marking final approved
    else:
        try:
            rule_json = json.loads(rule_data["rule"])
        except Exception:
            return ResponseService.response(
                "VALIDATION_ERROR", "Invalid rule format.", "validation_error"
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
                    "SUCCESS", "Next level activated.", "default_update_success_msg"
                )

        # No more levels -> mark final approval
        QueryBuilderService("core_entities").where("id", entity_id).update(
            {"approvel_status": True}
        )

    # -------------------------------
    # Branch email by core_entities.type
    # -------------------------------
    entity_row = QueryBuilderService("core_entities").where("id", entity_id).first()
    entity_type = (entity_row or {}).get("type", "") if entity_row else ""

    # Authentication is handled by Django's authentication system
    # The chatmail endpoint uses @permission_classes([IsAuthenticated])

    # Resolve default FROM address (shared)
    from_email = None
    try:
        gmail_credential = (
            QueryBuilderService("core_gmailcredential")
            .select("system_email")
            # .where("user_id", user.id)  # shared mailbox per your note
            .first()
        )
        if gmail_credential:
            from_email = gmail_credential["system_email"]
    except Exception:
        pass

    if not from_email:
        print("[EMAIL] Skipping email: no default Gmail credential found")
        return ResponseService.response(
            "SUCCESS",
            "Final approval completed. Email sending skipped due to missing default Gmail credential.",
            "default_update_success_msg",
        )

    base_url = request.build_absolute_uri("/").rstrip("/")
    send_message_url = f"{base_url}/api/chatmail/send"
    headers = {
        "Content-Type": "application/json",
        "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
    }
    red_headers = dict(headers)
    if red_headers.get("Authorization"):
        parts = red_headers["Authorization"].split(" ", 1)
        if len(parts) == 2:
            red_headers["Authorization"] = parts[0] + " " + redact_token(parts[1])

    # --------- CASE 1: Quotation approval (existing flow) ---------
    if str(entity_type).strip().lower() == "quotation approval":
        quotation = (
            QueryBuilderService("crmq_quotations").where("entity_id", entity_id).first()
        )
        if quotation and quotation.get("email_data"):
            try:
                payload = json.loads(quotation["email_data"])

                # Extract documents from payload and print details
                documents = payload.get("documents", [])
                print(f"[EMAIL DEBUG][Quotation] Found {len(documents)} documents in email_data:")
                for i, doc in enumerate(documents):
                    if isinstance(doc, dict):
                        doc_key = doc.get("doc", "")
                        cdn_base_url = os.getenv("CDN_BASE_URL")
                        
                        # Ensure proper URL construction
                        if doc_key:
                            doc_key = doc_key.lstrip('/')
                            doc_url = f"{cdn_base_url.rstrip('/')}/{doc_key}"
                        else:
                            doc_url = "No document key found"
                        
                        doc_name = doc.get("name", "Unknown")
                        print(f"  Document {i+1}: {doc_name} - {doc_url}")

                # Get service provider IDs for this quotation
                sp_rows = (
                    QueryBuilderService("crmq_quotation_service_providers")
                    .select("service_provider_id")
                    .where("quotation_id", quotation["id"])
                    .get()
                )
                service_provider_ids = [r["service_provider_id"] for r in sp_rows]

                # Resolve provider records (id + email)
                provider_records = (
                    QueryBuilderService("core_service_providers")
                    .select("id", "email")
                    .whereIn("id", service_provider_ids)
                    .get()
                )
                providers = []
                for row in provider_records:
                    sp_id = row.get("id")
                    email = (row.get("email") or "kowreesan06@gmail.com").strip()
                    if sp_id:
                        providers.append({"id": sp_id, "email": email})

                results = []
                for sp in providers:
                    to_email = sp["email"]
                    insurer_id = sp["id"]

                    # Map entity type to conversation type
                    conversation_type = "QUOTATION" if entity_type.lower() == "quotation approval" else entity_type.upper()
                    
                    # Ensure required fields have fallback values
                    email_subject = payload.get("email_data", {}).get("subject", "")
                    email_body = payload.get("email_data", {}).get("body", "")
                    
                    if not email_subject:
                        email_subject = "Quotation Approval Notification"
                    if not email_body:
                        email_body = "Your quotation has been approved."
                    
                    # Prepare attachments for email sending
                    attachments = []
                    if documents:
                        for doc in documents:
                            if isinstance(doc, dict) and doc.get("doc"):
                                # Use the S3 URL directly instead of base64 data
                                doc_key = doc.get("doc", "")
                                cdn_base_url = os.getenv("CDN_BASE_URL", "https://your-cdn-domain.com")  # Add fallback
                                
                                # Ensure proper URL construction
                                if doc_key:
                                    # Remove leading slash if present to avoid double slashes
                                    doc_key = doc_key.lstrip('/')
                                    doc_url = f"{cdn_base_url.rstrip('/')}/{doc_key}"
                                else:
                                    doc_url = ""
                                
                                doc_name = doc.get("name", "document.pdf")
                                
                                # Determine content type based on file extension
                                if doc_name.lower().endswith('.xlsx'):
                                    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                elif doc_name.lower().endswith('.pdf'):
                                    content_type = "application/pdf"
                                elif doc_name.lower().endswith('.docx'):
                                    content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                else:
                                    content_type = "application/octet-stream"
                                
                                # Only add attachment if we have a valid URL
                                if doc_url and doc_url != "No document key found":
                                    attachment = {
                                        "filename": doc_name,
                                        "content_type": content_type,
                                        "file_url": doc_url  # Use S3 URL instead of base64 data
                                    }
                                    attachments.append(attachment)
                                    print(f"[EMAIL DEBUG][Quotation] Added attachment: {attachment['filename']} with URL: {doc_url}")
                                else:
                                    print(f"[EMAIL DEBUG][Quotation] Skipped attachment: {doc_name} - Invalid or missing document URL")
                    
                    send_message_payload = {
                        "body": email_body,
                        "subject": email_subject,
                        "to_email": to_email,
                        "from_email": from_email,
                        "conversation_id": "",
                        "conversation_type": conversation_type,
                        "type_based_id": f"QR-{quotation['id']}" if quotation.get("id") else "QR-001",
                        "insurer_id": insurer_id,
                        "attachments": attachments,  # Add attachments to payload
                    }

                    # DEBUG
                    try:
                        import json as _json

                        print("[EMAIL DEBUG][Quotation] Sending message:")
                        print(f"  from_email    : {from_email}")
                        print(f"  to_email      : {to_email}")
                        print(f"  subject       : {send_message_payload['subject']}")
                        print(f"  insurer_id    : {insurer_id}")
                        print(f"  type_based_id : {send_message_payload['type_based_id']}")
                        print(f"  POST {send_message_url}")
                        print(f"  headers       : {red_headers}")
                        print(f"  payload       : {_json.dumps(send_message_payload, ensure_ascii=False)}")
                    except Exception:
                        pass

                    try:
                        response = requests.post(
                            send_message_url,
                            json=send_message_payload,
                            headers=headers,
                            timeout=30,
                        )
                        if response.status_code == 200:
                            results.append(
                                {
                                    "email": to_email,
                                    "status": "sent",
                                    "response": response.json(),
                                }
                            )
                        else:
                            results.append(
                                {
                                    "email": to_email,
                                    "status": "failed",
                                    "error": response.text,
                                }
                            )
                    except Exception as e:
                        results.append(
                            {"email": to_email, "status": "failed", "error": str(e)}
                        )

                print(f"[EMAIL DEBUG][Quotation] Results: {results}")

            except Exception as e:
                print(f"[EMAIL][Quotation] Failed to send emails after approval: {e}")

    # --------- CASE 2: Policy ---------
    elif str(entity_type).strip().lower() == "policy":
        # 1) Find the policy row by entity_id
        policy = (
            QueryBuilderService("crmp_request_policies")
            .where("entity_id", entity_id)
            .first()
        )
        if not policy or not policy.get("email_data"):
            print("[EMAIL][Policy] No policy row or email_data found; skipping.")
        else:
            # 2) Parse the email payload stored in crmp_request_policies.email_data
            try:
                payload = json.loads(policy["email_data"])
            except Exception:
                payload = {}

            # Extract documents from payload and print details
            documents = payload.get("documents", [])
            print(f"[EMAIL DEBUG][Policy] Found {len(documents)} documents in email_data:")
            for i, doc in enumerate(documents):
                if isinstance(doc, dict):
                    doc_key = doc.get("doc", "")
                    cdn_base_url = os.getenv("CDN_BASE_URL", "https://your-cdn-domain.com")
                    
                    # Ensure proper URL construction
                    if doc_key:
                        doc_key = doc_key.lstrip('/')
                        doc_url = f"{cdn_base_url.rstrip('/')}/{doc_key}"
                    else:
                        doc_url = "No document key found"
                    
                    doc_name = doc.get("name", "Unknown")
                    print(f"  Document {i+1}: {doc_name} - {doc_url}")

            # 3) Resolve from_email (default/shared mailbox)
            from_email = None
            try:
                gmail_credential = (
                    QueryBuilderService("core_gmailcredential")
                    .select("system_email")
                    # .where("user_id", user.id)  # shared mailbox per your note
                    .first()
                )
                if gmail_credential:
                    from_email = gmail_credential["system_email"]
            except Exception as e:
                print(f"[EMAIL][Policy] Failed to resolve from_email: {e}")

            if not from_email:
                print("[EMAIL][Policy] No from_email found; skipping send.")
            else:
                # 4) Resolve insurer email:
                #    crmp_request_policies.policy_base_id -> crmp_policy_base.insurer_id
                #    -> core_service_providers.email
                to_email = None
                insurer_id = None
                try:
                    policy_base_id = policy.get("policy_base_id")
                    if policy_base_id:
                        policy_base = (
                            QueryBuilderService("crmp_policy_base")
                            .select("id", "insurer_id")
                            .where("id", policy_base_id)
                            .first()
                        )
                        if policy_base and policy_base.get("insurer_id"):
                            insurer_id = policy_base["insurer_id"]
                            provider = (
                                QueryBuilderService("core_service_providers")
                                .select("id", "email")
                                .where("id", insurer_id)
                                .first()
                            )
                            if provider and provider.get("email"):
                                to_email = (provider["email"] or "").strip()
                except Exception as e:
                    print(f"[EMAIL][Policy] Error resolving insurer email: {e}")

                if not to_email:
                    print("[EMAIL][Policy] Could not resolve insurer email; skipping send.")
                else:
                    # 5) Build payload and call internal /api/chatmail/send
                    # Map entity type to conversation type
                    conversation_type = "POLICY" if entity_type.lower() == "policy" else entity_type.upper()
                    
                    # Ensure required fields have fallback values
                    email_subject = payload.get("email_data", {}).get("subject", "")
                    email_body = payload.get("email_data", {}).get("body", "")
                    
                    if not email_subject:
                        email_subject = "Policy Approval Notification"
                    if not email_body:
                        email_body = "Your policy has been approved."
                    
                    # Prepare attachments for email sending
                    attachments = []
                    if documents:
                        for doc in documents:
                            if isinstance(doc, dict) and doc.get("doc"):
                                # Use the S3 URL directly instead of base64 data
                                doc_key = doc.get("doc", "")
                                cdn_base_url = os.getenv("CDN_BASE_URL", "https://your-cdn-domain.com")
                                
                                # Ensure proper URL construction
                                if doc_key:
                                    # Remove leading slash if present to avoid double slashes
                                    doc_key = doc_key.lstrip('/')
                                    doc_url = f"{cdn_base_url.rstrip('/')}/{doc_key}"
                                else:
                                    doc_url = ""
                                
                                doc_name = doc.get("name", "document.pdf")
                                
                                # Determine content type based on file extension
                                if doc_name.lower().endswith('.xlsx'):
                                    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                elif doc_name.lower().endswith('.pdf'):
                                    content_type = "application/pdf"
                                elif doc_name.lower().endswith('.docx'):
                                    content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                                else:
                                    content_type = "application/octet-stream"
                                
                                # Only add attachment if we have a valid URL
                                if doc_url and doc_url != "No document key found":
                                    attachment = {
                                        "filename": doc_name,
                                        "content_type": content_type,
                                        "file_url": doc_url  # Use S3 URL instead of base64 data
                                    }
                                    attachments.append(attachment)
                                    print(f"[EMAIL DEBUG][Policy] Added attachment: {attachment['filename']} with URL: {doc_url}")
                                else:
                                    print(f"[EMAIL DEBUG][Policy] Skipped attachment: {doc_name} - Invalid or missing document URL")
                    
                    send_message_payload = {
                        "body": email_body,
                        "subject": email_subject,
                        "to_email": to_email,
                        "from_email": from_email,
                        "conversation_id": "",                  # new conversation
                        "conversation_type": conversation_type,
                        "type_based_id": f"PR-{policy['id']}" if policy.get("id") else "PR-001",
                        "insurer_id": insurer_id,               # pass insurer_id as requested
                        "attachments": attachments,  # Add attachments to payload
                    }

                    base_url = request.build_absolute_uri('/').rstrip('/')
                    send_message_url = f"{base_url}/api/chatmail/send"
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
                    }

                    # ---- Optional debug ----
                    try:
                        red_headers = dict(headers)
                        if red_headers.get("Authorization"):
                            parts = red_headers["Authorization"].split(" ", 1)
                            if len(parts) == 2:
                                red_headers["Authorization"] = parts[0] + " " + redact_token(parts[1])
                        import json as _json
                        print("[EMAIL][Policy] POST /api/chatmail/send")
                        print(f"  from_email    : {from_email}")
                        print(f"  to_email      : {to_email}")
                        print(f"  subject       : {send_message_payload['subject']}")
                        print(f"  insurer_id    : {insurer_id}")
                        print(f"  type_based_id : {send_message_payload['type_based_id']}")
                        print(f"  headers       : {red_headers}")
                        print(f"  payload       : {_json.dumps(send_message_payload, ensure_ascii=False)}")
                    except Exception:
                        pass

                    try:
                        response = requests.post(
                            send_message_url,
                            json=send_message_payload,
                            headers=headers,
                            timeout=30
                        )
                        if response.status_code == 200:
                            print("[EMAIL][Policy] Send OK:", response.json())
                        else:
                            print("[EMAIL][Policy] Send FAILED:", response.status_code, response.text)
                    except Exception as e:
                        print(f"[EMAIL][Policy] Error calling /api/chatmail/send: {e}")


    else:
        # Neither quotation nor policy; nothing to email in this flow
        print(f"[EMAIL] Entity type '{entity_type}' has no email branch; skipping.")

    return ResponseService.response(
        "SUCCESS", "Final approval completed.", "default_update_success_msg"
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
            "VALIDATION_ERROR", "data_not_found", "Validation error"
        )

    # Update the deleted_at field with the current date (no time)
    today = datetime.now().date()
    QueryBuilderService("core_entity_approvals").where(
        "core_entity_approvals.id", id
    ).update({"deleted_at": today})

    return ResponseService.response("SUCCESS", [], "Data deleted successfully")


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
            "VALIDATION_ERROR", errors, "Validation error"
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
            "Validation error",
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
            "Validation error",
        )

    recipient_emails = [
        row["email"] if row.get("email") else "kowreesan06@gmail.com"
        for row in provider_records
    ]

    # Step 4: Get user's Gmail credentials for from_email
    user = request.user if request.user.is_authenticated else None
    if not user:
        return ResponseService.response(
            "VALIDATION_ERROR",
            "User not authenticated",
            "Validation error",
        )

    # Get user's Gmail credential
    gmail_credential = (
        QueryBuilderService("core_gmailcredential")
        .select("system_email")
        .where("user_id", user.id)
        .first()
    )

    if not gmail_credential:
        return ResponseService.response(
            "VALIDATION_ERROR",
            "User does not have Gmail credentials configured",
            "Validation error",
        )

    from_email = gmail_credential["system_email"]

    # Step 5: Authentication is handled by Django's authentication system
    # The chatmail endpoint uses @permission_classes([IsAuthenticated])

    # Step 6: Send emails using the send-message API for each recipient
    results = []
    for to_email in recipient_emails:
        try:
            # Prepare payload for chatmail API
            send_message_payload = {
                "body": body,
                "subject": subject,
                "to_email": to_email,
                "from_email": from_email,
                "conversation_id": "", # Empty for new conversations
                "conversation_type": "QUOTATION",  # Map to available conversation type
                "type_based_id": "QR-001"
            }

            # Make internal call to chatmail API
            # Since this is an internal call, we'll use the Django test client or make a direct function call
            # For now, we'll use requests to call our own API
            base_url = request.build_absolute_uri('/').rstrip('/')
            send_message_url = f"{base_url}/api/chatmail/send"
            
            # Use the same headers as the original request for authentication
            headers = {
                'Content-Type': 'application/json',
                'Authorization': request.META.get('HTTP_AUTHORIZATION', '')
            }
            
            response = requests.post(
                send_message_url,
                json=send_message_payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                results.append({
                    "email": to_email,
                    "status": "sent",
                    "response": response.json()
                })
            else:
                results.append({
                    "email": to_email,
                    "status": "failed",
                    "error": response.text
                })
                
        except Exception as e:
            results.append({
                "email": to_email,
                "status": "failed",
                "error": str(e)
            })

    return ResponseService.response("SUCCESS", {
        "total_recipients": len(recipient_emails),
        "results": results
    }, "Email sending completed")





@csrf_exempt
@api_view(["GET"])
def entity_check(request, id):

    data = QueryBuilderService("core_entity_approvals").where("entity_id", id).first()

    if not data:
        return ResponseService.response("SUCCESS", False, "Data not found")

    return ResponseService.response("SUCCESS", True, "Data not found")

import json
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from mServices.ResponseService import ResponseService


logger = logging.getLogger(__name__)


# -----------------------
# Helpers
# -----------------------
def _parse_id_list(v):
    """Accept 7 / '7' / '7,8' / '[7,8]' → [ints]."""
    if v is None or v == "":
        return []
    if isinstance(v, int):
        return [v]
    s = str(v).strip()
    try:
        j = json.loads(s)
        if isinstance(j, list):
            out = []
            for x in j:
                try:
                    out.append(int(x))
                except:
                    pass
            return out
    except Exception:
        pass
    s = s.strip("[]")
    out = []
    for part in s.split(","):
        part = part.strip()
        if part.isdigit():
            out.append(int(part))
    return out


def fetch_elements_data(template_id, submission_id=None):
    """
    Returns (steps, panels, elements) with element 'value' populated from submission values
    and 'element_code' joined from core_form_elements.
    """
    steps = (
        QueryBuilderService("core_form_custom_form_steps")
        .select("*")
        .where("form_id", template_id)
        .orderBy("step_number")
        .get()
        or []
    )

    panels = (
        QueryBuilderService("core_form_custom_form_panels")
        .select("*")
        .where("form_id", template_id)
        .orderBy("order_number")
        .get()
        or []
    )

    panel_ids = [p["id"] for p in panels] or [0]

    elements_query = (
        QueryBuilderService("core_form_custom_form_elements as ele")
        .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id")
        .select("ele.*", "fe.code as element_code")
        .whereIn("ele.panel_id", panel_ids)
        .orderBy("ele.order_number")
        .get()
        or []
    )

    values_dict = {}
    if submission_id:
        values_query = (
            QueryBuilderService("core_form_submission_valuess")
            .select("custom_form_element_id", "value")
            .where("form_submission_id", submission_id)
            .get()
            or []
        )
        values_dict = {str(v["custom_form_element_id"]): v["value"] for v in values_query}

    elements = []
    for element in elements_query:
        options = (
            QueryBuilderService("core_form_custom_form_element_options")
            .select("*")
            .where("element_id", element["id"])
            .get()
            or []
        )
        element["options"] = options
        element["value"] = values_dict.get(str(element["id"])) if submission_id else None
        elements.append(element)

    return steps, panels, elements


def _inline_submission_struct_on_risk(risk):
    """
    If risk has submission_id, add:
      risk["template"], risk["steps"], risk["panels"], risk["elements"]
    """
    try:
        sub_id = risk.get("submission_id")
        if not sub_id:
            return risk

        submission = (
            CoreFormSubmission.objects.select_related("form")
            .filter(id=sub_id)
            .first()
        )
        if not submission or not submission.form_id:
            return risk

        form = submission.form
        template = {
            "id": form.id,
            "name": getattr(form, "name", None),
            "description": getattr(form, "description", None),
            "type": getattr(form, "type", None),
        }
        steps, panels, elements = fetch_elements_data(template_id=form.id, submission_id=submission.id)

        # Inline onto the risk object (exact shape you asked for)
        risk["template"] = template
        risk["steps"] = steps
        risk["panels"] = panels
        risk["elements"] = elements
        return risk
    except Exception as ex:
        logger.warning(f"_inline_submission_struct_on_risk failed for risk {risk.get('id')}: {ex}")
        return risk


def _inline_submission_struct_on_risks(risks):
    return [_inline_submission_struct_on_risk(r) for r in (risks or [])]


# -----------------------
# Endpoint
# -----------------------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def approval_risk_details(request, approval_id: int):
    """
    GET /api/approvals/<approval_id>/risk-details?risk_type_id=1,2

    - If entity is a QUOTATION:
        crmq_quotations(entity_id) -> crm_opportunities.lead_id
        crm_risk_details where lead_id = <lead_id> [and risk_type_id IN (?)]
    - If entity is a POLICY:
        crmp_request_policies(entity_id) -> policy_id
        crmp_policy_risk_config(policy_id) -> risk_id[]
        crm_risk_details where id IN (risk_id[]) [and risk_type_id IN (?)]
    """
    try:
        # 1) Resolve entity/type from approval
        meta = (
            QueryBuilderService("core_entity_approvals")
            .select(
                "core_entity_approvals.id as approval_id",
                "core_entity_approvals.entity_id as entity_id",
                "core_entities.type as entity_type",
            )
            .leftJoin("core_entities", "core_entities.id", "core_entity_approvals.entity_id")
            .where("core_entity_approvals.id", approval_id)
            .whereNull("core_entity_approvals.deleted_at")
            .first()
        )
        if not meta:
            return ResponseService.response("NOT_FOUND", None, f"Approval {approval_id} not found.")

        entity_id = meta.get("entity_id")
        entity_type = (meta.get("entity_type") or "").strip().lower()

        # Optional filter
        risk_type_ids = _parse_id_list(request.query_params.get("risk_type_id"))

        # 2) Branch by entity_type
        risks = []
        source = {}

        if entity_type in ("quotation approval", "quotation"):
            qrow = (
                QueryBuilderService("crmq_quotations as q")
                .select(
                    "q.id as quotation_id",
                    "q.opportunity_id as opportunity_id",
                    "crm_opportunities.id as lead_id",
                )
                .leftJoin("crm_opportunities", "crm_opportunities.id", "q.opportunity_id")
                .where("q.entity_id", entity_id)
                .first()
            )
            if not qrow or not qrow.get("lead_id"):
                return ResponseService.response(
                    "NOT_FOUND",
                    {"entity_id": entity_id, "entity_type": entity_type},
                    "Lead not found for this quotation."
                )

            lead_id = qrow["lead_id"]
            source = {"mode": "quotation", "lead_id": lead_id, "opportunity_id": qrow.get("opportunity_id")}

            qry = QueryBuilderService("crm_risk_submissions as rd").select("rd.*").where("rd.lead_id", lead_id).leftJoin("crm_risks as r", "r.id", "rd.risk_id")
            if risk_type_ids:
                qry = qry.whereIn("r.risk_type_id", risk_type_ids)
            risks = qry.get() or []

        elif entity_type == "policy":
            # 1. Get policy_base_id from crmp_request_policies
            prow = (
                QueryBuilderService("crmp_request_policies")
                .select("id as policy_id", "policy_base_id")
                .where("entity_id", entity_id)
                .first()
            )
            if not prow or not prow.get("policy_id"):
                return ResponseService.response(
                    "NOT_FOUND",
                    {"entity_id": entity_id, "entity_type": entity_type},
                    "Policy request not found for this approval."
                )
            
            policy_id = prow["policy_id"]
            policy_base_id = prow.get("policy_base_id")
            
            if not policy_base_id:
                return ResponseService.response(
                    "NOT_FOUND",
                    {"entity_id": entity_id, "entity_type": entity_type, "policy_id": policy_id},
                    "Policy base not found for this policy request."
                )
            
            # 2. Get customer_id from crmp_policy_base
            policy_base = (
                QueryBuilderService("crmp_policy_base")
                .select("customer_id")
                .where("id", policy_base_id)
                .first()
            )
            if not policy_base or not policy_base.get("customer_id"):
                return ResponseService.response(
                    "NOT_FOUND",
                    {"entity_id": entity_id, "entity_type": entity_type, "policy_id": policy_id, "policy_base_id": policy_base_id},
                    "Customer not found for this policy base."
                )
            
            customer_id = policy_base["customer_id"]
            source = {"mode": "policy", "policy_id": policy_id, "policy_base_id": policy_base_id, "customer_id": customer_id}

            # 3. Get risk types from crmp_policy_base_risk_types for this policy_base_id
            risk_type_rows = (
                QueryBuilderService("crmp_policy_base_risk_types")
                .select("risk_type_id")
                .where("policy_base_id", policy_base_id)
                .get()
            ) or []
            
            policy_risk_type_ids = [r["risk_type_id"] for r in risk_type_rows if r.get("risk_type_id")]
            if not policy_risk_type_ids:
                return ResponseService.response(
                    "SUCCESS",
                    {
                        "approval_id": approval_id,
                        "entity_id": entity_id,
                        "entity_type": entity_type,
                        "filters": {"risk_type_ids": risk_type_ids},
                        "source": source,
                        "risks": [],
                        "count": 0,
                    },
                    "No risk types found for this policy base."
                )

            # 4. Find risk details in crm_risk_details that match both customer_id and risk_type_id
            qry = (
                QueryBuilderService("crm_risks as r")
                .select("r.*", "rs.submission_id")
                .leftJoin("crm_risk_submissions as rs", "rs.risk_id", "r.id")
                .where("r.customer_id", customer_id)
                .whereIn("r.risk_type_id", policy_risk_type_ids)
            )
            
            # Apply additional risk_type_id filter if provided in query params
            if risk_type_ids:
                # Intersect the policy risk types with the requested risk types
                filtered_risk_type_ids = list(set(policy_risk_type_ids) & set(risk_type_ids))
                if not filtered_risk_type_ids:
                    return ResponseService.response(
                        "SUCCESS",
                        {
                            "approval_id": approval_id,
                            "entity_id": entity_id,
                            "entity_type": entity_type,
                            "filters": {"risk_type_ids": risk_type_ids},
                            "source": source,
                            "risks": [],
                            "count": 0,
                        },
                        "No matching risk types found for the requested filter."
                    )
                qry = qry.whereIn("rd.risk_type_id", filtered_risk_type_ids)
            
            risks = qry.get() or []

        else:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"entity_type": entity_type},
                f"Unsupported entity type for approval {approval_id}"
            )

        # 3) Inline submission structure onto each risk
        risks = _inline_submission_struct_on_risks(risks)

        return ResponseService.response(
            "SUCCESS",
            {
                "approval_id": approval_id,
                "entity_id": entity_id,
                "entity_type": entity_type,
                "filters": {"risk_type_ids": risk_type_ids},
                "source": source,
                "risks": risks,
                "count": len(risks),
            },
            "Risk details fetched successfully."
        )

    except Exception as e:
        logger.exception(f"[approval_risk_details] error for approval_id={approval_id}: {e}")
        return Response(
            {"error": "Internal server error", "message": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def get_service_providers(request):
    all_columns = [
        "core_service_providers.id",
        "core_service_providers.name",
        "core_service_providers.description",
        "core_service_providers.status_id",
    ]   

    filter_json = request.GET.get("filter", {}) 
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_service_providers.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["core_service_providers.id", "core_service_providers.name"]
    search_columns = ["core_service_providers.id", "core_service_providers.name"]
    allowed_sorting_columns = ["core_service_providers.id", "core_service_providers.name"]

    query = QueryBuilderService("core_service_providers")\
            .select(*all_columns)\
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    
    return ResponseService.response('SUCCESS',query, "default_success_message")


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quotation_chat_messages(request, quotation_id, insurer_id):
    """
    GET /api/<quotation_id>/chat-messages/<insurer_id>
    
    Find the conversation_id for the given quotation_id and insurer_id,
    then fetch all messages directly from the database using QueryBuilderService.
    
    The conversation is found in core_chat_conversations table where:
    - type_based_id = 'QR-{quotation_id}'
    - insurer_id = {insurer_id}
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
        
        # Get user's email for comparison
        user_email = getattr(user, 'email', '').strip().lower()
        
        # Try alternative email fields if the main email field is empty
        if not user_email:
            # Try other common email fields
            alternative_fields = ['username', 'system_email', 'gmail_email']
            for field in alternative_fields:
                alt_email = getattr(user, field, '').strip().lower()
                if alt_email and '@' in alt_email:
                    user_email = alt_email
                    break
        
        # Construct the type_based_id format: QR-{quotation_id}
        type_based_id = f"QR-{quotation_id}"
        
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
                "insurer_id"
            )
            .where("type_based_id", type_based_id)
            .where("insurer_id", insurer_id)
            .first()
        )
        
        if not conversation:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                f"No conversation found for quotation {quotation_id} and insurer {insurer_id}"
            )
        
        conversation_id = conversation["conversation_id"]
        
        # Define columns and configuration
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
            "sent_at"
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
                    "created_at"
                )
                .whereIn("email_message_id", message_ids)
                .get()
            )
            attachments = attachments_query
        
        # Group attachments by message_id
        attachments_by_message = {}
        for attachment in attachments:
            message_id = attachment["email_message_id"]
            if message_id not in attachments_by_message:
                attachments_by_message[message_id] = []
            attachments_by_message[message_id].append({
                "id": attachment["id"],
                "file_name": attachment["file_name"],
                "content_type": attachment["content_type"],
                "size_bytes": attachment["size_bytes"],
                "is_image": attachment["is_image"],
                "file_url": attachment["file_url"],
                "gmail_attachment_id": attachment["gmail_attachment_id"],
                "download_url": attachment["file_url"]
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
                
                # Handle "Name <email@domain.com>" format (in case any still exist)
                if "<" in email_string and ">" in email_string:
                    start = email_string.find("<") + 1
                    end = email_string.find(">")
                    if start < end:
                        return email_string[start:end].strip().lower()
                
                # Handle raw email format
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
                    # If insurer email doesn't match either from or to, default to received
                    message["type"] = "received"
                    print(f"[DEBUG] Message {message['id']}: received (default) - from: {from_email_normalized}, to: {to_email_normalized}, insurer: {insurer_email}")
            else:
                # If no insurer email found, default to received
                message["type"] = "received"
                print(f"[DEBUG] Message {message['id']}: received (no insurer email)")
            
            # Get sender name with improved logic
            sender_name = "Unknown"
            
            # Try to extract name from the original from_email string first
            if "<" in from_email_raw and ">" in from_email_raw:
                name_part = from_email_raw.split("<")[0].strip()
                if name_part and name_part != from_email_normalized:
                    sender_name = name_part
            
            # If no name extracted, try database lookup
            if sender_name == "Unknown":
                # Try users table first
                user_record = (
                    QueryBuilderService("core_users")
                    .select("display_name", "email")
                    .where("email", from_email_normalized)
                    .first()
                )
                
                if user_record and user_record.get("display_name"):
                    sender_name = user_record.get("display_name")
                else:
                    # Try service_providers table
                    service_provider_record = (
                        QueryBuilderService("core_service_providers")
                        .select("name", "email")
                        .where("email", from_email_normalized)
                        .first()
                    )
                    
                    if service_provider_record and service_provider_record.get("name"):
                        sender_name = service_provider_record.get("name")
                    else:
                        # Final fallback: use email username
                        if "@" in from_email_normalized:
                            sender_name = from_email_normalized.split("@")[0]
                        else:
                            sender_name = from_email_normalized
            
            message["sender_name"] = sender_name
        
        # Add conversation metadata to the response
        query["conversation_metadata"] = {
            "conversation_id": conversation_id,
            "conversation_code": conversation["conversation_code"],
            "type": conversation["type"],
            "created_at": conversation["created_at"],
            "gmail_thread_id": conversation["gmail_thread_id"],
            "quotation_id": quotation_id,
            "insurer_id": insurer_id,
            "type_based_id": type_based_id
        }
        
        return ResponseService.response(
            "SUCCESS",
            query,
            f"Chat messages retrieved successfully for quotation {quotation_id} and insurer {insurer_id}"
        )
            
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quotation_sync_conversations(request, quotation_id):
    """
    GET/POST /api/<quotation_id>/sync-conversations
    
    Find all conversation_ids for the given quotation_id in core_chat_conversations table,
    then sync each conversation using the chatmail sync-thread endpoint.
    
    The conversations are found in core_chat_conversations table where:
    - type_based_id = 'QR-{quotation_id}'
    """
    try:
        # Construct the type_based_id format: QR-{quotation_id}
        type_based_id = f"QR-{quotation_id}"
        
        # Find all conversations for this quotation in core_chat_conversations table
        conversations = (
            QueryBuilderService("core_chat_conversations")
            .select("id as conversation_id", "code as conversation_code", "type", "created_at", "insurer_id")
            .where("type_based_id", type_based_id)
            .get()
        )
        
        if not conversations:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                f"No conversations found for quotation {quotation_id}"
            )
        
        # Results tracking
        sync_results = []
        successful_syncs = 0
        failed_syncs = 0
        total_new_messages = 0
        total_new_attachments = 0
        total_updated_bodies = 0
        
        # Base URL for internal API calls
        base_url = request.build_absolute_uri("/").rstrip("/")
        
        # Headers for internal requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
        }
        
        print(f"[SYNC] Found {len(conversations)} conversations for quotation {quotation_id}")
        
        # Sync each conversation
        for conversation in conversations:
            conversation_id = conversation["conversation_id"]
            insurer_id = conversation["insurer_id"]
            
            try:
                # Call the sync-thread endpoint for this conversation
                sync_url = f"{base_url}/api/chatmail/sync-thread"
                
                print(f"[SYNC] Syncing conversation {conversation_id} (insurer: {insurer_id})")
                
                # The sync-thread endpoint expects conversation_id in the request body
                sync_payload = {"conversation_id": conversation_id}
                
                response = requests.post(sync_url, json=sync_payload, headers=headers, timeout=60)  # Longer timeout for sync operations
                
                if response.status_code == 200:
                    sync_data = response.json()
                    successful_syncs += 1
                    
                    # Extract attachment and message statistics from sync response
                    sync_response_data = sync_data.get('data', {})
                    new_messages = sync_response_data.get('new_messages_count', 0)
                    new_attachments = sync_response_data.get('new_attachments_count', 0)
                    updated_bodies = sync_response_data.get('updated_bodies_count', 0)
                    
                    total_new_messages += new_messages
                    total_new_attachments += new_attachments
                    total_updated_bodies += updated_bodies
                    
                    sync_results.append({
                        "conversation_id": conversation_id,
                        "insurer_id": insurer_id,
                        "status": "success",
                        "response": sync_data,
                        "conversation_code": conversation["conversation_code"],
                        "type": conversation["type"],
                        "new_messages": new_messages,
                        "new_attachments": new_attachments,
                        "updated_bodies": updated_bodies
                    })
                    
                    
                else:
                    failed_syncs += 1
                    
                    sync_results.append({
                        "conversation_id": conversation_id,
                        "insurer_id": insurer_id,
                        "status": "failed",
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "conversation_code": conversation["conversation_code"],
                        "type": conversation["type"]
                    })
                    
                    
            except requests.exceptions.RequestException as e:
                failed_syncs += 1
                
                sync_results.append({
                    "conversation_id": conversation_id,
                    "insurer_id": insurer_id,
                    "status": "failed",
                    "error": f"Request error: {str(e)}",
                    "conversation_code": conversation["conversation_code"],
                    "type": conversation["type"]
                })
                
                
            except Exception as e:
                failed_syncs += 1
                
                sync_results.append({
                    "conversation_id": conversation_id,
                    "insurer_id": insurer_id,
                    "status": "failed",
                    "error": f"Unexpected error: {str(e)}",
                    "conversation_code": conversation["conversation_code"],
                    "type": conversation["type"]
                })
                
        
        # Prepare response
        response_data = {
            "quotation_id": quotation_id,
            "type_based_id": type_based_id,
            "total_conversations": len(conversations),
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "total_new_messages": total_new_messages,
            "total_new_attachments": total_new_attachments,
            "total_updated_bodies": total_updated_bodies,
            "sync_results": sync_results
        }
        
        # Determine overall status
        if failed_syncs == 0:
            message = f"Successfully synced all {successful_syncs} conversations for quotation {quotation_id} - {total_new_messages} messages, {total_new_attachments} attachments, {total_updated_bodies} bodies updated"
            status_code = "SUCCESS"
        elif successful_syncs == 0:
            message = f"Failed to sync any of the {failed_syncs} conversations for quotation {quotation_id}"
            status_code = "PARTIAL_FAILURE"
        else:
            message = f"Partially synced conversations for quotation {quotation_id}: {successful_syncs} successful, {failed_syncs} failed - {total_new_messages} messages, {total_new_attachments} attachments, {total_updated_bodies} bodies updated"
            status_code = "PARTIAL_SUCCESS"
        
        print(f"[SYNC] Summary: {successful_syncs} successful, {failed_syncs} failed - {total_new_messages} messages, {total_new_attachments} attachments, {total_updated_bodies} bodies updated")
        
        return ResponseService.response(status_code, response_data, message)
        
    except Exception as e:
        print(f"[SYNC] Internal error for quotation {quotation_id}: {e}")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def policy_chat_messages(request, policy_id):
    """
    GET /api/<policy_id>/chat-messages
    
    Find the conversation_id for the given policy_id,
    then fetch all messages directly from the database using QueryBuilderService.
    
    The conversation is found in core_chat_conversations table where:
    - type_based_id = 'PR-{policy_id}'
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
        
        # Get user's email for comparison
        user_email = getattr(user, 'email', '').strip().lower()
        
        # Try alternative email fields if the main email field is empty
        if not user_email:
            # Try other common email fields
            alternative_fields = ['username', 'system_email', 'gmail_email']
            for field in alternative_fields:
                alt_email = getattr(user, field, '').strip().lower()
                if alt_email and '@' in alt_email:
                    user_email = alt_email
                    break
        
        # Construct the type_based_id format: PR-{policy_id}
        type_based_id = f"PR-{policy_id}"
        
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
                "insurer_id"
            )
            .where("type_based_id", type_based_id)
            .first()
        )
        
        if not conversation:
            return ResponseService.response(
                "SUCCESS",
                [],
                f"No conversation found for policy {policy_id}"
            )
        
        conversation_id = conversation["conversation_id"]
        
        # Define columns and configuration
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
            "sent_at"
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
                    "created_at"
                )
                .whereIn("email_message_id", message_ids)
                .get()
            )
            attachments = attachments_query
        
        # Group attachments by message_id
        attachments_by_message = {}
        for attachment in attachments:
            message_id = attachment["email_message_id"]
            if message_id not in attachments_by_message:
                attachments_by_message[message_id] = []
            attachments_by_message[message_id].append({
                "id": attachment["id"],
                "file_name": attachment["file_name"],
                "content_type": attachment["content_type"],
                "size_bytes": attachment["size_bytes"],
                "is_image": attachment["is_image"],
                "file_url": attachment["file_url"],
                "gmail_attachment_id": attachment["gmail_attachment_id"],
                "download_url": attachment["file_url"]
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
                
                # Handle "Name <email@domain.com>" format (in case any still exist)
                if "<" in email_string and ">" in email_string:
                    start = email_string.find("<") + 1
                    end = email_string.find(">")
                    if start < end:
                        return email_string[start:end].strip().lower()
                
                # Handle raw email format
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
                    # If insurer email doesn't match either from or to, default to received
                    message["type"] = "received"
                    print(f"[DEBUG] Message {message['id']}: received (default) - from: {from_email_normalized}, to: {to_email_normalized}, insurer: {insurer_email}")
            else:
                # If no insurer email found, default to received
                message["type"] = "received"
                print(f"[DEBUG] Message {message['id']}: received (no insurer email)")
            
            # Get sender name with improved logic
            sender_name = "Unknown"
            
            # Try to extract name from the original from_email string first
            if "<" in from_email_raw and ">" in from_email_raw:
                name_part = from_email_raw.split("<")[0].strip()
                if name_part and name_part != from_email_normalized:
                    sender_name = name_part
            
            # If no name extracted, try database lookup
            if sender_name == "Unknown":
                # Try users table first
                user_record = (
                    QueryBuilderService("core_users")
                    .select("display_name", "email")
                    .where("email", from_email_normalized)
                    .first()
                )
                
                if user_record and user_record.get("display_name"):
                    sender_name = user_record.get("display_name")
                else:
                    # Try service_providers table
                    service_provider_record = (
                        QueryBuilderService("core_service_providers")
                        .select("name", "email")
                        .where("email", from_email_normalized)
                        .first()
                    )
                    
                    if service_provider_record and service_provider_record.get("name"):
                        sender_name = service_provider_record.get("name")
                    else:
                        # Final fallback: use email username
                        if "@" in from_email_normalized:
                            sender_name = from_email_normalized.split("@")[0]
                        else:
                            sender_name = from_email_normalized
            
            message["sender_name"] = sender_name
        
        # Add conversation metadata to the response
        query["conversation_metadata"] = {
            "conversation_id": conversation_id,
            "conversation_code": conversation["conversation_code"],
            "type": conversation["type"],
            "created_at": conversation["created_at"],
            "gmail_thread_id": conversation["gmail_thread_id"],
            "policy_id": policy_id,
            "type_based_id": type_based_id
        }
        
        return ResponseService.response(
            "SUCCESS",
            query,
            f"Chat messages retrieved successfully for policy {policy_id}"
        )
            
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def policy_sync_conversations(request, policy_id):
    """
    GET/POST /api/<policy_id>/sync-conversations
    
    Find all conversation_ids for the given policy_id in core_chat_conversations table,
    then sync each conversation using the chatmail sync-thread endpoint.
    
    The conversations are found in core_chat_conversations table where:
    - type_based_id = 'PR-{policy_id}'
    
    Enhanced with better error handling and debugging for document fetching and CDN key functionality.
    """
    try:
        # Construct the type_based_id format: PR-{policy_id}
        type_based_id = f"PR-{policy_id}"
        
        print(f"[POLICY_SYNC] Starting sync for policy {policy_id} with type_based_id: {type_based_id}")
        
        # Find all conversations for this policy in core_chat_conversations table
        conversations = (
            QueryBuilderService("core_chat_conversations")
            .select("id as conversation_id", "code as conversation_code", "type", "created_at", "insurer_id")
            .where("type_based_id", type_based_id)
            .get()
        )
        
        if not conversations:
            print(f"[POLICY_SYNC] No conversations found for policy {policy_id}")
            return ResponseService.response(
                "NOT_FOUND",
                None,
                f"No conversations found for policy {policy_id}"
            )
        
        # Results tracking
        sync_results = []
        successful_syncs = 0
        failed_syncs = 0
        total_new_messages = 0
        total_new_attachments = 0
        total_updated_bodies = 0
        
        # Base URL for internal API calls
        base_url = request.build_absolute_uri("/").rstrip("/")
        
        # Headers for internal requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
        }
        
        print(f"[POLICY_SYNC] Found {len(conversations)} conversations for policy {policy_id}")
        print(f"[POLICY_SYNC] Using base_url: {base_url}")
        print(f"[POLICY_SYNC] Authorization header present: {'Yes' if headers.get('Authorization') else 'No'}")
        
        # Debug: Print conversation details
        for i, conv in enumerate(conversations):
            print(f"[POLICY_SYNC] Conversation {i+1}: ID={conv['conversation_id']}, Code={conv['conversation_code']}, Type={conv['type']}, Insurer={conv['insurer_id']}")
        
        # Check CDN configuration
        import os
        cdn_base_url = os.getenv("CDN_BASE_URL")
        print(f"[POLICY_SYNC] CDN_BASE_URL configured: {'Yes' if cdn_base_url else 'No'}")
        if cdn_base_url:
            print(f"[POLICY_SYNC] CDN_BASE_URL: {cdn_base_url}")
        
        # Check S3 configuration
        s3_bucket = os.getenv("S3_BUCKET_NAME")
        s3_region = os.getenv("S3_REGION")
        print(f"[POLICY_SYNC] S3_BUCKET_NAME configured: {'Yes' if s3_bucket else 'No'}")
        print(f"[POLICY_SYNC] S3_REGION configured: {'Yes' if s3_region else 'No'}")
        
        # Check if S3PresignedService is available
        try:
            from envoy.services.s3_presigned_service import S3PresignedService
            print(f"[POLICY_SYNC] S3PresignedService import: SUCCESS")
        except ImportError as e:
            print(f"[POLICY_SYNC] S3PresignedService import: FAILED - {e}")
        
        # Sync each conversation
        for conversation in conversations:
            conversation_id = conversation["conversation_id"]
            insurer_id = conversation["insurer_id"]
            
            print(f"[POLICY_SYNC] Processing conversation {conversation_id} (insurer: {insurer_id})")
            
            try:
                # Call the sync-thread endpoint for this conversation
                sync_url = f"{base_url}/api/chatmail/sync-thread"
                
                print(f"[POLICY_SYNC] Syncing conversation {conversation_id} (insurer: {insurer_id})")
                print(f"[POLICY_SYNC] Sync URL: {sync_url}")
                
                # The sync-thread endpoint expects conversation_id in the request body
                sync_payload = {"conversation_id": conversation_id}
                
                print(f"[POLICY_SYNC] Sync payload: {sync_payload}")
                
                response = requests.post(sync_url, json=sync_payload, headers=headers, timeout=60)  # Longer timeout for sync operations
                
                print(f"[POLICY_SYNC] Response status: {response.status_code}")
                
                if response.status_code == 200:
                    sync_data = response.json()
                    successful_syncs += 1
                    
                    # Debug: Print full sync response
                    print(f"[POLICY_SYNC] Full sync response: {sync_data}")
                    
                    # Extract attachment and message statistics from sync response
                    sync_response_data = sync_data.get('data', {})
                    new_messages = sync_response_data.get('new_messages_count', 0)
                    new_attachments = sync_response_data.get('new_attachments_count', 0)
                    updated_bodies = sync_response_data.get('updated_bodies_count', 0)
                    
                    # Debug: Print extracted statistics
                    print(f"[POLICY_SYNC] Extracted stats - Messages: {new_messages}, Attachments: {new_attachments}, Bodies: {updated_bodies}")
                    
                    total_new_messages += new_messages
                    total_new_attachments += new_attachments
                    total_updated_bodies += updated_bodies
                    
                    sync_results.append({
                        "conversation_id": conversation_id,
                        "insurer_id": insurer_id,
                        "status": "success",
                        "response": sync_data,
                        "conversation_code": conversation["conversation_code"],
                        "type": conversation["type"],
                        "new_messages": new_messages,
                        "new_attachments": new_attachments,
                        "updated_bodies": updated_bodies
                    })
                    
                    print(f"[POLICY_SYNC] ✅ Successfully synced conversation {conversation_id} - {new_messages} messages, {new_attachments} attachments, {updated_bodies} bodies updated")
                    
                    # Log detailed sync response for debugging
                    if new_attachments > 0:
                        print(f"[POLICY_SYNC] 📎 Document fetching successful for conversation {conversation_id}: {new_attachments} new attachments")
                        print(f"[POLICY_SYNC] 📎 CDN key functionality working: CDN_BASE_URL={'configured' if cdn_base_url else 'not configured'}")
                    
                else:
                    failed_syncs += 1
                    error_text = response.text
                    
                    # Debug: Print detailed error information
                    print(f"[POLICY_SYNC] ❌ Failed to sync conversation {conversation_id}: {response.status_code}")
                    print(f"[POLICY_SYNC] ❌ Error response text: {error_text}")
                    print(f"[POLICY_SYNC] ❌ Error response headers: {dict(response.headers)}")
                    
                    sync_results.append({
                        "conversation_id": conversation_id,
                        "insurer_id": insurer_id,
                        "status": "failed",
                        "error": f"HTTP {response.status_code}: {error_text}",
                        "conversation_code": conversation["conversation_code"],
                        "type": conversation["type"]
                    })
                    print(f"[POLICY_SYNC] ❌ Error response: {error_text}")
                    
            except requests.exceptions.RequestException as e:
                failed_syncs += 1
                
                sync_results.append({
                    "conversation_id": conversation_id,
                    "insurer_id": insurer_id,
                    "status": "failed",
                    "error": f"Request error: {str(e)}",
                    "conversation_code": conversation["conversation_code"],
                    "type": conversation["type"]
                })
                
                print(f"[POLICY_SYNC] ❌ Request error for conversation {conversation_id}: {e}")
                
            except Exception as e:
                failed_syncs += 1
                
                sync_results.append({
                    "conversation_id": conversation_id,
                    "insurer_id": insurer_id,
                    "status": "failed",
                    "error": f"Unexpected error: {str(e)}",
                    "conversation_code": conversation["conversation_code"],
                    "type": conversation["type"]
                })
                
                print(f"[POLICY_SYNC] ❌ Unexpected error for conversation {conversation_id}: {e}")
        
        # Prepare response
        response_data = {
            "policy_id": policy_id,
            "type_based_id": type_based_id,
            "total_conversations": len(conversations),
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "total_new_messages": total_new_messages,
            "total_new_attachments": total_new_attachments,
            "total_updated_bodies": total_updated_bodies,
            "sync_results": sync_results,
            "configuration_status": {
                "cdn_configured": bool(cdn_base_url),
                "s3_bucket_configured": bool(s3_bucket),
                "s3_region_configured": bool(s3_region)
            }
        }
        
        # Determine overall status
        if failed_syncs == 0:
            message = f"Successfully synced all {successful_syncs} conversations for policy {policy_id} - {total_new_messages} messages, {total_new_attachments} attachments, {total_updated_bodies} bodies updated"
            status_code = "SUCCESS"
        elif successful_syncs == 0:
            message = f"Failed to sync any of the {failed_syncs} conversations for policy {policy_id}"
            status_code = "PARTIAL_FAILURE"
        else:
            message = f"Partially synced conversations for policy {policy_id}: {successful_syncs} successful, {failed_syncs} failed - {total_new_messages} messages, {total_new_attachments} attachments, {total_updated_bodies} bodies updated"
            status_code = "PARTIAL_SUCCESS"
        
        print(f"[POLICY_SYNC] Summary: {successful_syncs} successful, {failed_syncs} failed - {total_new_messages} messages, {total_new_attachments} attachments, {total_updated_bodies} bodies updated")
        
        # Debug: Print detailed summary for troubleshooting
        print(f"[POLICY_SYNC] 🔍 DEBUGGING SUMMARY:")
        print(f"[POLICY_SYNC] 🔍 - Total conversations found: {len(conversations)}")
        print(f"[POLICY_SYNC] 🔍 - Successful syncs: {successful_syncs}")
        print(f"[POLICY_SYNC] 🔍 - Failed syncs: {failed_syncs}")
        print(f"[POLICY_SYNC] 🔍 - New messages: {total_new_messages}")
        print(f"[POLICY_SYNC] 🔍 - New attachments: {total_new_attachments}")
        print(f"[POLICY_SYNC] 🔍 - Updated bodies: {total_updated_bodies}")
        print(f"[POLICY_SYNC] 🔍 - CDN_BASE_URL configured: {'Yes' if cdn_base_url else 'No'}")
        print(f"[POLICY_SYNC] 🔍 - S3_BUCKET_NAME configured: {'Yes' if s3_bucket else 'No'}")
        
        if total_new_attachments == 0 and successful_syncs > 0:
            print(f"[POLICY_SYNC] ⚠️  WARNING: No new attachments found despite successful syncs!")
            print(f"[POLICY_SYNC] ⚠️  This could mean:")
            print(f"[POLICY_SYNC] ⚠️  1. Conversations have no attachments")
            print(f"[POLICY_SYNC] ⚠️  2. All attachments already exist (duplicates)")
            print(f"[POLICY_SYNC] ⚠️  3. S3 upload is failing silently")
            print(f"[POLICY_SYNC] ⚠️  4. CDN_BASE_URL not configured properly")
        
        return ResponseService.response(status_code, response_data, message)
        
    except Exception as e:
        print(f"[POLICY_SYNC] Internal error for policy {policy_id}: {e}")
        import traceback
        print(f"[POLICY_SYNC] Traceback: {traceback.format_exc()}")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def policy_sync_conversations_new(request, policy_id):
    """
    GET/POST /api/<policy_id>/sync-conversations-new
    
    Find all endorsement requests for the given policy_id in crmp_endorsement_requests table,
    then find conversations for each endorsement request using type_based_id='ER-{endorsement_id}',
    then sync each conversation using the chatmail sync-thread endpoint.
    """
    try:
        # Get all endorsement requests for the policy_id
        endorsement_requests = (
            QueryBuilderService("crmp_endorsement_requests")
            .select("id")
            .where("issued_policy_id", policy_id)
            .get()
        )
        
        if not endorsement_requests:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                f"No endorsement requests found for policy {policy_id}"
            )
        
        # Get conversations for all endorsement requests
        all_conversations = []
        for endorsement_request in endorsement_requests:
            endorsement_id = endorsement_request.get("id")
            type_based_id = f"ER-{endorsement_id}"
            
            conversations = (
                QueryBuilderService("core_chat_conversations")
                .select("id as conversation_id", "code as conversation_code", "type", "created_at", "insurer_id")
                .where("type_based_id", type_based_id)
                .get()
            )
            all_conversations.extend(conversations)
        
        conversations = all_conversations
        
        if not conversations:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                f"No conversations found for policy {policy_id}"
            )
        
        # Results tracking
        sync_results = []
        successful_syncs = 0
        failed_syncs = 0
        total_new_messages = 0
        total_new_attachments = 0
        total_updated_bodies = 0
        
        # Base URL for internal API calls
        base_url = request.build_absolute_uri("/").rstrip("/")
        
        # Headers for internal requests
        headers = {
            "Content-Type": "application/json",
            "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
        }
        
        # Check CDN configuration
        import os
        cdn_base_url = os.getenv("CDN_BASE_URL")
        
        # Check S3 configuration
        s3_bucket = os.getenv("S3_BUCKET_NAME")
        s3_region = os.getenv("S3_REGION")
        
        # Sync each conversation
        for conversation in conversations:
            conversation_id = conversation["conversation_id"]
            insurer_id = conversation["insurer_id"]
            
            try:
                # Call the sync-thread endpoint for this conversation
                sync_url = f"{base_url}/api/chatmail/sync-thread"
                
                # The sync-thread endpoint expects conversation_id in the request body
                sync_payload = {"conversation_id": conversation_id}
                
                response = requests.post(sync_url, json=sync_payload, headers=headers, timeout=60)
                
                if response.status_code == 200:
                    sync_data = response.json()
                    successful_syncs += 1
                    
                    # Extract attachment and message statistics from sync response
                    sync_response_data = sync_data.get('data', {})
                    new_messages = sync_response_data.get('new_messages_count', 0)
                    new_attachments = sync_response_data.get('new_attachments_count', 0)
                    updated_bodies = sync_response_data.get('updated_bodies_count', 0)
                    
                    total_new_messages += new_messages
                    total_new_attachments += new_attachments
                    total_updated_bodies += updated_bodies
                    
                    sync_results.append({
                        "conversation_id": conversation_id,
                        "insurer_id": insurer_id,
                        "status": "success",
                        "response": sync_data,
                        "conversation_code": conversation["conversation_code"],
                        "type": conversation["type"],
                        "new_messages": new_messages,
                        "new_attachments": new_attachments,
                        "updated_bodies": updated_bodies
                    })
                    
                    
                else:
                    failed_syncs += 1
                    
                    sync_results.append({
                        "conversation_id": conversation_id,
                        "insurer_id": insurer_id,
                        "status": "failed",
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "conversation_code": conversation["conversation_code"],
                        "type": conversation["type"]
                    })
                    
                    
            except requests.exceptions.RequestException as e:
                failed_syncs += 1
                
                sync_results.append({
                    "conversation_id": conversation_id,
                    "insurer_id": insurer_id,
                    "status": "failed",
                    "error": f"Request error: {str(e)}",
                    "conversation_code": conversation["conversation_code"],
                    "type": conversation["type"]
                })
                
                
            except Exception as e:
                failed_syncs += 1
                
                sync_results.append({
                    "conversation_id": conversation_id,
                    "insurer_id": insurer_id,
                    "status": "failed",
                    "error": f"Unexpected error: {str(e)}",
                    "conversation_code": conversation["conversation_code"],
                    "type": conversation["type"]
                })
                
        
        # Prepare response
        response_data = {
            "policy_id": policy_id,
            "total_conversations": len(conversations),
            "successful_syncs": successful_syncs,
            "failed_syncs": failed_syncs,
            "total_new_messages": total_new_messages,
            "total_new_attachments": total_new_attachments,
            "total_updated_bodies": total_updated_bodies,
            "sync_results": sync_results
        }
        
        # Determine overall status
        if failed_syncs == 0:
            message = f"Successfully synced all {successful_syncs} conversations for policy {policy_id} - {total_new_messages} messages, {total_new_attachments} attachments, {total_updated_bodies} bodies updated"
            status_code = "SUCCESS"
        elif successful_syncs == 0:
            message = f"Failed to sync any of the {failed_syncs} conversations for policy {policy_id}"
            status_code = "PARTIAL_FAILURE"
        else:
            message = f"Partially synced conversations for policy {policy_id}: {successful_syncs} successful, {failed_syncs} failed - {total_new_messages} messages, {total_new_attachments} attachments, {total_updated_bodies} bodies updated"
            status_code = "PARTIAL_SUCCESS"
        
        
        return ResponseService.response(status_code, response_data, message)
        
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_endorsement_documents(request, endorsement_id):
    """
    GET /api/endorsement/{endorsement_id}/documents
    
    Get all documents/attachments from conversations related to a specific endorsement.
    
    Flow:
    1. Find conversation for the endorsement using type_based_id='ER-{endorsement_id}'
    2. Get all email attachments from core_email_attachments table for that conversation
    3. Return document details including file URLs, names, sizes, etc.
    """
    try:
        # Step 1: Find conversation for the endorsement
        type_based_id = f"ER-{endorsement_id}"
        
        # Use a simpler approach first
        conversation = QueryBuilderService("core_chat_conversations").where("type_based_id", type_based_id).get()
        
        if not conversation:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                f"No conversation found for endorsement {endorsement_id}"
            )
        
        # Get the first (and should be only) conversation
        conversation_data = conversation[0]
        conversation_id = conversation_data["id"]
        
        # Step 2: Get all email attachments for this conversation
        try:
            # Get attachments by joining through email_messages table
            attachments = (
                QueryBuilderService("core_email_attachments as ea")
                .leftJoin("core_email_messages as em", "em.id", "ea.email_message_id")
                .where("em.conversation_id", conversation_id)
                .get()
            )
        except Exception as e:
            # Fallback: get all messages for this conversation first, then get attachments
            try:
                messages = QueryBuilderService("core_email_messages").where("conversation_id", conversation_id).get()
                
                if messages:
                    message_ids = [msg["id"] for msg in messages]
                    
                    # Get attachments for these messages
                    attachments = []
                    for msg_id in message_ids:
                        msg_attachments = QueryBuilderService("core_email_attachments").where("email_message_id", msg_id).get()
                        if msg_attachments:
                            attachments.extend(msg_attachments)
                else:
                    attachments = []
            except Exception as e2:
                attachments = []
        
        # Step 3: Format response data
        documents = []
        
        for attachment in attachments:
            file_size_bytes = attachment.get("size_bytes") or 0
            
            documents.append({
                "attachment_id": attachment.get("id"),
                "filename": attachment.get("file_name"),
                "file_url": attachment.get("file_url"),
                "file_size": file_size_bytes,
                "content_type": attachment.get("content_type"),
                "created_at": attachment.get("created_at").isoformat() if attachment.get("created_at") else None
            })
        
        # Prepare simplified response - just the documents array
        if not documents:
            message = f"No documents found for endorsement {endorsement_id}"
        else:
            message = f"Found {len(documents)} documents for endorsement {endorsement_id}"
        
        return ResponseService.response("SUCCESS", documents, message)
        
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )


@api_view(["GET"])
def get_risks_by_type_and_customer(request, risk_type_id):
    try:
        # Get query parameters
        customer_id = request.query_params.get("customer_id")
        approval_id = request.query_params.get("approval_id")
        lead_id = request.query_params.get("lead_id")
        policy_base_id = request.query_params.get("policy_base_id")
        sort_by = request.query_params.get("sort_by", "")
        sort_dir = request.query_params.get("sort_dir", "desc")
        
        # Validate required parameters
        if not customer_id:
            return ResponseService.response("BAD_REQUEST", None, "Customer ID is required.", system_code=400)

        # Fields for risk data
        risk_columns = [
            "rd.id",
            "rd.code AS risk_code",
            "rt.title AS risk_type_title",
            "cust.id AS customer_id",
            "cust.name AS customer_name",
            "cust.logo AS customer_logo"
        ]

        # Initialize base query
        base_query = QueryBuilderService("crm_risks as rd") \
            .leftJoin("crm_opportunity_types AS rt", "rt.id", "rd.risk_type_id") \
            .leftJoin("core_customers AS cust", "cust.id", "rd.customer_id") \
            .select(*risk_columns, "rs.submission_id", "rs.id as risk_submissions_id") \
            .leftJoin("crm_risk_submissions as rs", "rs.risk_id", "rd.id") \
            .where("rd.risk_type_id", risk_type_id) \
            .where("rd.customer_id", customer_id)\
            .where("rd.is_deleted", False)

        # Handle direct filtering parameters first (lead_id or policy_base_id)
        if lead_id and lead_id.strip() and lead_id.lower() not in ['null', 'undefined', '']:
            # Direct lead_id filtering - filter risks by lead_id from crm_risk_submissions
            base_query = base_query.where("rs.lead_id", lead_id)
            
        elif policy_base_id and policy_base_id.strip() and policy_base_id.lower() not in ['null', 'undefined', '']:
            # Direct policy_base_id filtering - get risk_submissions_id from crmp_policy_risk_config
            try:
                risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                    .select("risk_submission_id") \
                    .where("policy_base_id", policy_base_id) \
                    .get()
            except:
                try:
                    risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                        .select("risk_submissions_id") \
                        .where("policy_base_id", policy_base_id) \
                        .get()
                except:
                    try:
                        risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                            .select("submission_id") \
                            .where("policy_base_id", policy_base_id) \
                            .get()
                    except:
                        try:
                            risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                                .select("risk_id") \
                                .where("policy_base_id", policy_base_id) \
                                .get()
                        except:
                            return ResponseService.response("SUCCESS", [], "Unable to access crmp_policy_risk_config table.")
            
            if risk_configs:
                # Extract the submission IDs (try different possible column names)
                submission_ids = []
                for rc in risk_configs:
                    if rc.get("risk_submission_id"):
                        submission_ids.append(rc["risk_submission_id"])
                    elif rc.get("risk_submissions_id"):
                        submission_ids.append(rc["risk_submissions_id"])
                    elif rc.get("submission_id"):
                        submission_ids.append(rc["submission_id"])
                    elif rc.get("risk_id"):
                        submission_ids.append(rc["risk_id"])
                
                if submission_ids:
                    # Filter risks by submission IDs
                    base_query = base_query.whereIn("rs.id", submission_ids)
                else:
                    return ResponseService.response("SUCCESS", [], "No risk submissions found for this policy_base_id.")
            else:
                return ResponseService.response("SUCCESS", [], "No risk configurations found for this policy_base_id.")
                
        # Handle approval_id logic for different approval types (only if no direct filtering)
        # Only process if approval_id has a meaningful value (not null, empty, or undefined)
        elif approval_id and approval_id.strip() and approval_id.lower() not in ['null', 'undefined', '']:
            # Get approval details to determine entity type
            approval = QueryBuilderService("core_entity_approvals as ea") \
                .select("ea.entity_id", "ce.type as entity_type") \
                .leftJoin("core_entities as ce", "ce.id", "ea.entity_id") \
                .where("ea.id", approval_id) \
                .first()
            
            if not approval:
                return ResponseService.response("NOT_FOUND", None, "Approval not found.", system_code=404)
            
            entity_id = approval["entity_id"]
            entity_type = approval["entity_type"]
            
            if entity_type and entity_type.lower() in ("quotation approval", "quotation"):
                # For quotation: find opportunity_id, then find risks in crm_risk_submissions by lead_id
                qrow = (
                    QueryBuilderService("crmq_quotations as q")
                    .select(
                        "q.id as quotation_id",
                        "q.opportunity_id as opportunity_id",
                        "crm_opportunities.id as lead_id",
                    )
                    .leftJoin("crm_opportunities", "crm_opportunities.id", "q.opportunity_id")
                    .where("q.entity_id", entity_id)
                    .first()
                )
                
                if not qrow or not qrow.get("lead_id"):
                    return ResponseService.response(
                        "NOT_FOUND",
                        {"entity_id": entity_id, "entity_type": entity_type},
                        "Lead not found for this quotation."
                    )
                
                lead_id = qrow["lead_id"]
                # Filter risks by lead_id from crm_risk_submissions
                base_query = base_query.where("rs.lead_id", lead_id)
                
            elif entity_type and entity_type.lower() == "policy":
                # For policy: find policy_base_id from crmp_request_policies, then find risk_submissions_id from crmp_policy_risk_config
                prow = (
                    QueryBuilderService("crmp_request_policies")
                    .select("id as policy_id", "policy_base_id")
                    .where("entity_id", entity_id)
                    .first()
                )
                
                if not prow or not prow.get("policy_id"):
                    return ResponseService.response(
                        "NOT_FOUND",
                        {"entity_id": entity_id, "entity_type": entity_type},
                        "Policy request not found for this approval."
                    )
                
                policy_base_id = prow.get("policy_base_id")
                if not policy_base_id:
                    return ResponseService.response(
                        "NOT_FOUND",
                        {"entity_id": entity_id, "entity_type": entity_type, "policy_id": prow["policy_id"]},
                        "Policy base not found for this policy request."
                    )
                
                # Get risk_submissions_id from crmp_policy_risk_config table
                # Try different possible column names
                try:
                    risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                        .select("risk_submission_id") \
                        .where("policy_base_id", policy_base_id) \
                        .get()
                except:
                    try:
                        risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                            .select("risk_submissions_id") \
                            .where("policy_base_id", policy_base_id) \
                            .get()
                    except:
                        try:
                            risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                                .select("submission_id") \
                                .where("policy_base_id", policy_base_id) \
                                .get()
                        except:
                            try:
                                risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                                    .select("risk_id") \
                                    .where("policy_base_id", policy_base_id) \
                                    .get()
                            except:
                                return ResponseService.response("SUCCESS", [], "Unable to access crmp_policy_risk_config table.")
                
                if risk_configs:
                    # Extract the submission IDs (try different possible column names)
                    submission_ids = []
                    for rc in risk_configs:
                        if rc.get("risk_submission_id"):
                            submission_ids.append(rc["risk_submission_id"])
                        elif rc.get("risk_submissions_id"):
                            submission_ids.append(rc["risk_submissions_id"])
                        elif rc.get("submission_id"):
                            submission_ids.append(rc["submission_id"])
                        elif rc.get("risk_id"):
                            submission_ids.append(rc["risk_id"])
                    
                    if submission_ids:
                        # Filter risks by submission IDs
                        base_query = base_query.whereIn("rs.id", submission_ids)
                    else:
                        return ResponseService.response("SUCCESS", [], "No risk submissions found for this policy.")
                else:
                    return ResponseService.response("SUCCESS", [], "No risk configurations found for this policy.")

        # Define allowed sorting columns
        allowed_sorting_columns = ["id", "code", "risk_code", "risk_type_title", "customer_name"]
        
        # Apply sorting if specified
        if sort_by and sort_by in allowed_sorting_columns:
            if sort_dir.lower() == "desc":
                base_query = base_query.orderBy(f"{sort_by}", "DESC")
            else:
                base_query = base_query.orderBy(f"{sort_by}", "ASC")
        
        # Get all results without pagination
        all_risks = base_query.get()
        
        if not all_risks:
            return ResponseService.response("SUCCESS", [], "No risk details found for this type and customer.")

        # Process risk data and group by risk_id to get only the latest submission
        risk_submissions = {}  # Dictionary to store latest submission for each risk_id
        
        for risk in all_risks:
            submission_id = risk.get("submission_id")
            risk_id = risk["id"]
            
            if not submission_id:
                continue

            # Keep only the latest submission for each risk_id
            if risk_id not in risk_submissions or submission_id > risk_submissions[risk_id]["submission_id"]:
                risk_submissions[risk_id] = risk

        # Process the latest submissions
        results = []
        for risk_id, risk in risk_submissions.items():
            submission_id = risk.get("submission_id")
            
            submission = CoreFormSubmission.objects.select_related("form").filter(id=submission_id).first()
            if submission and submission.form:
                _, _, elements = fetch_elements_data(submission.form.id, submission_id=submission.id)
                result_item = {str(ele["id"]): ele.get("value") for ele in elements}
                result_item["form_submission_id"] = submission.id
                result_item["submission_id"] = risk.get("risk_submissions_id")
                result_item["template_id"] = submission.form.id
                result_item["risk_id"] = risk["id"]
                result_item["risk_code"] = risk["risk_code"]
                result_item["risk_type_title"] = risk["risk_type_title"]
                result_item["customer_id"] = risk["customer_id"]
                result_item["customer_name"] = risk["customer_name"]
                result_item["customer_logo"] = risk["customer_logo"]
                results.append(result_item)

        return ResponseService.response("SUCCESS", results,
         "Risk details retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def fetch_elements_data(template_id, submission_id=None):
    steps = QueryBuilderService("core_form_custom_form_steps") \
        .select("*") \
        .where("form_id", template_id) \
        .get()

    panels = QueryBuilderService("core_form_custom_form_panels") \
        .select("*") \
        .where("form_id", template_id) \
        .orderBy("order_number") \
        .get()

    panel_ids = [panel["id"] for panel in panels]

    elements_query = QueryBuilderService("core_form_custom_form_elements as ele") \
        .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id") \
        .select("ele.*") \
        .whereIn("ele.panel_id", panel_ids if panel_ids else [0]) \
        .orderBy("ele.order_number") \
        .get()

    element_ids = [e["id"] for e in elements_query]

    values_dict = {}
    if submission_id:
        values_query = QueryBuilderService("core_form_submission_valuess") \
            .select("custom_form_element_id", "value") \
            .where("form_submission_id", submission_id) \
            .get()
        values_dict = {str(v["custom_form_element_id"]): v["value"] for v in values_query}

    elements = []
    for element in elements_query:
        options = QueryBuilderService("core_form_custom_form_element_options") \
            .select("*") \
            .where("element_id", element["id"]) \
            .get()
        element["options"] = options
        element["value"] = values_dict.get(str(element["id"])) if submission_id else None
        elements.append(element)

    return steps, panels, elements





import logging
import os
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from envoy.models.chat_conversation import ChatConversation
from envoy.models.email_message import EmailChatMessage
from envoy.models.email_attachment import EmailAttachment
from envoy.models.mail_model import GmailCredential
from envoy.services import email_service as svc
from envoy.services.email_service import ensure_fresh_token
from mServices.QueryBuilderService import QueryBuilderService
from mServices.ResponseService import ResponseService

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def send_chatmail_message(request):
    """
    Send a chatmail message and store it in our database tables.
    If conversation_id is provided, it will be sent as a reply in the same conversation.
    """
    try:
        # Extract data from request
        to_email = request.data.get('to_email')
        from_email = request.data.get('from_email')
        subject = request.data.get('subject')
        body = request.data.get('body')
        conversation_id = request.data.get('conversation_id')
        attachments = request.data.get('attachments', [])
        documents = request.data.get('documents', [])
        
        # Process documents if provided (for backward compatibility)
        if documents and not attachments:
            import os
            for doc in documents:
                if isinstance(doc, dict) and doc.get("doc"):
                    # Use the S3 URL directly instead of base64 data
                    doc_key = doc.get("doc", "")
                    cdn_base_url = os.getenv("CDN_BASE_URL")
                    doc_url = f"{cdn_base_url}/{doc_key}"
                    doc_name = doc.get("name", "document.pdf")
                    
                    # Use provided type from payload, fallback to file extension detection
                    provided_type = doc.get("type", "")
                    if provided_type:
                        content_type = provided_type
                    else:
                        # Determine content type based on file extension
                        if doc_name.lower().endswith('.xlsx'):
                            content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        elif doc_name.lower().endswith('.pdf'):
                            content_type = "application/pdf"
                        elif doc_name.lower().endswith('.docx'):
                            content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        else:
                            content_type = "application/octet-stream"
                    
                    # Use provided size from payload, fallback to 0
                    provided_size = doc.get("size", "")
                    try:
                        size_bytes = int(provided_size) if provided_size else 0
                    except (ValueError, TypeError):
                        size_bytes = 0
                    
                    attachment = {
                        "filename": doc_name,
                        "content_type": content_type,
                        "file_url": doc_url,  # Use S3 URL instead of base64 data
                        "size_bytes": size_bytes
                    }
                    attachments.append(attachment)
                    logger.info(f"[send_chatmail_message] Added attachment: {attachment['filename']} with URL: {doc_url}, size: {size_bytes} bytes, type: {content_type}")
        
        # Get user from request
        user = request.user
        
        # Normalize email formats to ensure consistency
        def normalize_email_format(email_string):
            """Normalize email format to extract just the email address"""
            if not email_string:
                return ""
            
            email_string = email_string.strip()
            
            # Handle "Name <email@domain.com>" format
            if "<" in email_string and ">" in email_string:
                start = email_string.find("<") + 1
                end = email_string.find(">")
                if start < end:
                    return email_string[start:end].strip().lower()
            
            # Handle raw email format
            return email_string.lower()
        
        # If conversation_id is provided, try to derive addresses when missing
        if conversation_id:
            try:
                logger.info(f"[DEBUG] Looking for conversation_id: {conversation_id}")
                
                # Get the conversation
                conversation = ChatConversation.objects.get(id=conversation_id)
                
                # Derive to_email from conversation's insurer_id if not provided
                if not to_email and conversation.insurer_id:
                    try:
                        insurer_record = (
                            QueryBuilderService("core_service_providers")
                            .select("email")
                            .where("id", conversation.insurer_id)
                            .first()
                        )
                        if insurer_record and insurer_record.get("email"):
                            to_email = insurer_record["email"].strip()
                            logger.info(f"[send_chatmail_message] Derived to_email '{to_email}' from conversation insurer_id {conversation.insurer_id}")
                        else:
                            logger.warning(f"[send_chatmail_message] No email found for insurer_id {conversation.insurer_id}")
                    except Exception as e:
                        logger.error(f"[send_chatmail_message] Error deriving to_email from conversation insurer_id {conversation.insurer_id}: {e}")
                
                # If still no to_email, try to derive from latest email in conversation (fallback)
                if not to_email:
                    latest_email = (
                        EmailChatMessage.objects
                        .filter(conversation_id=conversation_id)
                        .order_by("-sent_at", "-id")
                        .first()
                    )
                    if latest_email:
                        logger.info(f"[DEBUG] Found latest email: from='{latest_email.from_email}', to='{latest_email.to_email}'")
                        to_email = latest_email.to_email
                        logger.info(f"[send_chatmail_message] Derived to_email '{to_email}' from latest email in conversation_id {conversation_id}")
                    else:
                        logger.warning(f"[send_chatmail_message] No EmailChatMessage found for conversation_id {conversation_id}")
                
                # For from_email, we ALWAYS prefer the default system email from Gmail credentials
                # Only use latest email's from_email if no system email is available
                if not from_email:
                    # Try to get default system email from Gmail credentials first
                    try:
                        gmail_credential_row = (
                            QueryBuilderService("core_gmailcredential")
                            .select("system_email")
                            .orderBy("id", "asc")
                            .first()
                        )
                        if gmail_credential_row and gmail_credential_row.get("system_email"):
                            from_email = gmail_credential_row["system_email"]
                            logger.info(f"[send_chatmail_message] Using default from_email from Gmail credentials: {from_email}")
                        else:
                            # Fallback to latest email's from_email only if no system email found
                            latest_email = (
                                EmailChatMessage.objects
                                .filter(conversation_id=conversation_id)
                                .order_by("-sent_at", "-id")
                                .first()
                            )
                            if latest_email:
                                from_email = latest_email.from_email
                                logger.info(f"[send_chatmail_message] Fallback: Derived from_email '{from_email}' from latest email in conversation_id {conversation_id}")
                            else:
                                logger.warning(f"[send_chatmail_message] No system email found and no EmailChatMessage for conversation_id {conversation_id}")
                    except Exception as e:
                        logger.error(f"[send_chatmail_message] Error getting default system email: {e}")
                        
            except ChatConversation.DoesNotExist:
                logger.error(f"[send_chatmail_message] Conversation with ID {conversation_id} not found")
            except Exception as e:
                logger.error(f"[send_chatmail_message] Error deriving emails for conversation_id={conversation_id}: {e}")
        
        # If no conversation_id provided, try to derive from_email from Gmail credentials
        if not conversation_id and not from_email:
            try:
                gmail_credential_row = (
                    QueryBuilderService("core_gmailcredential")
                    .select("system_email")
                    .orderBy("id", "asc")
                    .first()
                )
                if gmail_credential_row and gmail_credential_row.get("system_email"):
                    from_email = gmail_credential_row["system_email"]
                    logger.info(f"[send_chatmail_message] Using default from_email from Gmail credentials: {from_email}")
                else:
                    logger.warning(f"[send_chatmail_message] No default system_email found in core_gmailcredential")
            except Exception as e:
                logger.warning(f"[send_chatmail_message] Could not load default system_email: {e}")
        
        # If creating new conversation and to_email is missing, try to derive from insurer_id
        if not conversation_id and not to_email:
            insurer_id = request.data.get('insurer_id')
            if insurer_id:
                try:
                    insurer_record = (
                        QueryBuilderService("core_service_providers")
                        .select("email")
                        .where("id", insurer_id)
                        .first()
                    )
                    if insurer_record and insurer_record.get("email"):
                        to_email = insurer_record["email"].strip()
                        logger.info(f"[send_chatmail_message] Derived to_email '{to_email}' from insurer_id {insurer_id}")
                    else:
                        logger.warning(f"[send_chatmail_message] No email found for insurer_id {insurer_id}")
                except Exception as e:
                    logger.error(f"[send_chatmail_message] Error deriving to_email from insurer_id {insurer_id}: {e}")
        
        # Normalize email formats
        to_email = normalize_email_format(to_email)
        from_email = normalize_email_format(from_email)
        
        # Debug logging after normalization
        logger.info(f"[DEBUG] After normalization:")
        logger.info(f"[DEBUG] to_email: '{to_email}'")
        logger.info(f"[DEBUG] from_email: '{from_email}'")
        
        # Validate required fields based on whether conversation_id is provided
        if conversation_id:
            # For existing conversations, only body is required
            if not body:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"body": ["body is required when replying to existing conversation"]},
                    "Validation error"
                )
            
            # Subject is optional for replies (can use "Re: " + original subject)
            if not subject:
                # Try to get subject from the latest message in the conversation
                try:
                    latest_message = (
                        EmailChatMessage.objects
                        .filter(conversation_id=conversation_id)
                        .order_by("-sent_at", "-id")
                        .first()
                    )
                    if latest_message and latest_message.subject:
                        # Remove existing "Re: " prefix if present to avoid "Re: Re: ..."
                        original_subject = latest_message.subject
                        if original_subject.lower().startswith('re: '):
                            original_subject = original_subject[4:].strip()
                        subject = f"Re: {original_subject}"
                        logger.info(f"[send_chatmail_message] Auto-generated subject: {subject}")
                    else:
                        subject = "Re: Message"
                        logger.info(f"[send_chatmail_message] Using default subject: {subject}")
                except Exception as e:
                    subject = "Re: Message"
                    logger.warning(f"[send_chatmail_message] Error getting subject from conversation: {e}")
            else:
                # Ensure subject starts with "Re: " for proper threading
                if not subject.lower().startswith('re: '):
                    subject = f"Re: {subject}"
                    logger.info(f"[send_chatmail_message] Added 'Re: ' prefix to subject: {subject}")
        else:
            # For new conversations, all fields are required
            if not to_email:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"to_email": ["to_email is required for new conversations"]},
                    "Validation error"
                )
            
            if not subject:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"subject": ["subject is required for new conversations"]},
                    "Validation error"
                )
            
            if not body:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"body": ["body is required for new conversations"]},
                    "Validation error"
                )
            
            if not from_email:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"from_email": ["from_email is required for new conversations"]},
                    "Validation error"
                )
        
        # Check if Gmail is connected for the sender email
        try:
            cred = GmailCredential.objects.get(system_email=from_email)
            # Ensure token is fresh before using it
            cred = ensure_fresh_token(cred)
        except GmailCredential.DoesNotExist:
            return ResponseService.response(
                "UNAUTHORIZED",
                {
                    "connected": False,
                    "action": "connect_first",
                    "email": from_email
                },
                f"Gmail account {from_email} is not connected. Please connect your Gmail account first."
            )
        
        # Handle conversation (existing or new)
        if conversation_id:
            # Reply to existing conversation
            try:
                conversation = ChatConversation.objects.get(id=conversation_id)
                logger.info(f"Replying to existing conversation: {conversation.code}")
            except ChatConversation.DoesNotExist:
                return ResponseService.response(
                    "NOT_FOUND",
                    None,
                    f"Conversation with ID {conversation_id} not found"
                )
        else:
            # Create new conversation
            conversation_type = request.data.get('conversation_type', 'QUOTATION')
            type_based_id = request.data.get('type_based_id')
            insurer_id = request.data.get('insurer_id')
            
            conversation = ChatConversation.objects.create(
                type=conversation_type,
                type_based_id=type_based_id,
                insurer_id=insurer_id,
                user=user,
                gmail_thread_id=None  # Will be set after first email is sent
            )
            logger.info(f"Created new conversation: {conversation.code}")

        # Create email message record (outgoing message is seen by the sender)
        email_message = EmailChatMessage.objects.create(
            conversation=conversation,
            gmail_message_id=None,  # Will be set after Gmail API call
            gmail_thread_id=conversation.gmail_thread_id,
            from_email=from_email,
            to_email=to_email,
            subject=subject,
            body=body,
            sent_at=None,  # Will be set after successful send
            is_seen=True,
        )

        # Handle attachments - convert base64 data back to bytes for email service
        email_attachments = []
        for attachment_data in attachments:
            # Create database record
            EmailAttachment.objects.create(
                email_message=email_message,
                file_name=attachment_data.get('filename') or attachment_data.get('file_name'),
                file_url=attachment_data.get('file_url'),
                content_type=attachment_data.get('content_type'),
                size_bytes=attachment_data.get('size_bytes', 0),
                gmail_attachment_id=attachment_data.get('gmail_attachment_id'),
                is_image=attachment_data.get('is_image', False)
            )
            
            # Prepare attachment for email service
            if attachment_data.get('data'):
                import base64
                try:
                    # Convert base64 string back to bytes
                    if isinstance(attachment_data['data'], str):
                        attachment_bytes = base64.b64decode(attachment_data['data'])
                    else:
                        attachment_bytes = attachment_data['data']
                    
                    email_attachment = {
                        'filename': attachment_data.get('filename') or attachment_data.get('file_name', 'attachment'),
                        'content_type': attachment_data.get('content_type', 'application/octet-stream'),
                        'data': attachment_bytes
                    }
                    email_attachments.append(email_attachment)
                    logger.info(f"[send_chatmail_message] Prepared attachment: {email_attachment['filename']}")
                except Exception as e:
                    logger.error(f"[send_chatmail_message] Error processing attachment: {e}")
                    continue
            elif attachment_data.get('file_url'):
                # Handle S3 URL attachments - download the file and attach it
                try:
                    import requests
                    file_url = attachment_data.get('file_url')
                    filename = attachment_data.get('filename') or attachment_data.get('file_name', 'attachment')
                    content_type = attachment_data.get('content_type', 'application/octet-stream')
                    
                    # Download the file from S3 URL
                    response = requests.get(file_url, timeout=30)
                    response.raise_for_status()
                    
                    email_attachment = {
                        'filename': filename,
                        'content_type': content_type,
                        'data': response.content
                    }
                    email_attachments.append(email_attachment)
                    logger.info(f"[send_chatmail_message] Downloaded and prepared S3 attachment: {filename} from {file_url}")
                except Exception as e:
                    logger.error(f"[send_chatmail_message] Error downloading S3 attachment from {attachment_data.get('file_url')}: {e}")
                    continue

        # Send email via Gmail API
        try:
            logger.info(f"[DEBUG] Final email details:")
            logger.info(f"[DEBUG] from_email: '{from_email}'")
            logger.info(f"[DEBUG] to_email: '{to_email}'")
            logger.info(f"[DEBUG] subject: '{subject}'")
            logger.info(f"[DEBUG] body length: {len(body) if body else 0}")
            logger.info(f"[DEBUG] thread_id: '{conversation.gmail_thread_id}'")
            
            # Validate email addresses before sending
            if not from_email or not to_email:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {
                        "from_email": from_email,
                        "to_email": to_email
                    },
                    f"Invalid email addresses: from_email='{from_email}', to_email='{to_email}'"
                )
            
            # Get the latest message ID for proper threading
            reply_to_message_id = None
            if conversation_id and conversation.gmail_thread_id:
                try:
                    latest_message = (
                        EmailChatMessage.objects
                        .filter(conversation_id=conversation_id)
                        .exclude(gmail_message_id__isnull=True)
                        .exclude(gmail_message_id='')
                        .order_by("-sent_at", "-id")
                        .first()
                    )
                    if latest_message and latest_message.gmail_message_id:
                        reply_to_message_id = latest_message.gmail_message_id
                        logger.info(f"[send_chatmail_message] Using reply_to_message_id: {reply_to_message_id}")
                except Exception as e:
                    logger.warning(f"[send_chatmail_message] Could not get latest message ID for threading: {e}")
            
            logger.info(f"Sending email from {from_email} to {to_email}")
            logger.info(f"[send_chatmail_message] Sending with {len(email_attachments)} attachments")
            gmail_response = svc.send_email(
                credential=cred,
                to_email=to_email,
                subject=subject,
                body=body,
                thread_id=conversation.gmail_thread_id,
                reply_to_message_id=reply_to_message_id,
                attachments=email_attachments
            )
            
            # Update message with Gmail details
            email_message.gmail_message_id = gmail_response.get('id')
            email_message.sent_at = timezone.now()
            email_message.save()

            # Update conversation with Gmail thread ID if it's the first message
            if not conversation.gmail_thread_id:
                conversation.gmail_thread_id = gmail_response.get('threadId')
                conversation.save()

            logger.info(f"Email sent successfully: {email_message.id}")
            
            return ResponseService.response(
                "SUCCESS",
                {
                    'message_id': email_message.id,
                    'conversation_id': conversation.id,
                    'conversation_code': conversation.code,
                    'gmail_thread_id': conversation.gmail_thread_id,
                    'gmail_message_id': email_message.gmail_message_id
                },
                "Email sent successfully"
            )
            
        except Exception as e:
            logger.error(f"Email sending failed: {str(e)}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                None,
                f"Failed to send email: {str(e)}"
            )

    except Exception as e:
        logger.error(f"Error in send_chatmail_message: {str(e)}")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            None,
            f"Internal server error: {str(e)}"
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chatmail_messages(request):
    """Get chatmail messages with optional Gmail sync"""
    try:
        conversation_id = request.GET.get('conversation_id')
        user_id = request.GET.get('user_id')
        sync_thread = request.GET.get('sync_thread', 'false').lower() == 'true'
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        if not conversation_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "conversation_id is required",
                    "error_code": "MISSING_CONVERSATION_ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sync with Gmail if requested
        sync_info = None
        if sync_thread:
            sync_result = sync_gmail_thread_messages(conversation_id)
            if not sync_result['success']:
                return Response(
                    {
                        "error": "Thread sync failed",
                        "message": sync_result['message'],
                        "error_code": "THREAD_SYNC_FAILED"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            sync_info = sync_result['data']
        
        messages = EmailChatMessage.objects.all()
        messages = messages.filter(conversation_id=conversation_id)
        
        if user_id:
            messages = messages.filter(conversation__user_id=user_id)
        
        # Optimize queries with proper select_related and prefetch_related
        messages = messages.select_related('conversation').prefetch_related('attachments')
        messages = messages.order_by('-sent_at', '-id')
        
        # Get total count efficiently
        total_count = messages.count()
        
        # Paginate results
        start = (page - 1) * page_size
        end = start + page_size
        paginated_messages = messages[start:end]
        
        # Build response data efficiently
        message_data = []
        for message in paginated_messages:
            # Use prefetched attachments to avoid N+1 queries
            attachments_data = []
            for att in message.attachments.all():
                attachment_data = {
                    'id': att.id,
                    'file_name': att.file_name,
                    'content_type': att.content_type,
                    'size_bytes': att.size_bytes,
                    'is_image': att.is_image
                }
                
                # Keep the original gmail:// format for file_url
                attachment_data['file_url'] = att.file_url
                
                # Add clickable URLs for direct access
                if att.file and att.file.name:
                    # File is stored locally - use direct media URL
                    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
                    direct_url = f"{base_url}{att.file.url}"
                    attachment_data['download_url'] = direct_url
                    attachment_data['view_url'] = direct_url if att.is_image else None
                else:
                    # Fallback to download endpoint if file not stored locally
                    base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
                    download_url = f"{base_url}/api/chatmail/download-attachment?attachment_id={att.id}"
                    attachment_data['download_url'] = download_url
                    attachment_data['view_url'] = download_url if att.is_image else None
                
                attachments_data.append(attachment_data)
            
            message_data.append({
                'id': message.id,
                'conversation_id': message.conversation_id,
                'conversation_code': message.conversation.code,
                'from_email': message.from_email,
                'to_email': message.to_email,
                'subject': message.subject,
                'body': message.body,
                'sent_at': message.sent_at,
                'gmail_message_id': message.gmail_message_id,
                'is_seen': getattr(message, 'is_seen', False),
                'attachments': attachments_data
            })
        
        response_data = {
            'messages': message_data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': (total_count + page_size - 1) // page_size
            }
        }
        
        # Add sync info if Gmail sync was performed
        if sync_info:
            response_data['sync_info'] = sync_info
            message = "Messages retrieved successfully with Gmail sync"
        else:
            message = "Messages retrieved successfully from database"
        
        return Response(
            {
                "success": True,
                "message": message,
                "data": response_data
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in get_chatmail_messages: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def sync_gmail_thread(request):
    """
    Sync Gmail thread messages for a specific conversation.
    This endpoint fetches all messages from the Gmail thread and stores them in our database.
    """
    try:
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "conversation_id is required",
                    "error_code": "MISSING_CONVERSATION_ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Sync the thread
        sync_result = sync_gmail_thread_messages(conversation_id)
        
        if sync_result['success']:
            return Response(
                {
                    "success": True,
                    "message": "Gmail thread synced successfully",
                    "data": sync_result['data']
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "error": "Thread sync failed",
                    "message": sync_result['message'],
                    "error_code": "THREAD_SYNC_FAILED"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    except Exception as e:
        logger.error(f"Error in sync_gmail_thread: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )





def sync_gmail_thread_messages(conversation_id):
    """
    Optimized helper function to sync Gmail thread messages for a conversation.
    Returns a dict with success status and data/error message.
    """
    try:
        # Get the conversation
        try:
            conversation = ChatConversation.objects.get(id=conversation_id)
        except ChatConversation.DoesNotExist:
            return {
                'success': False,
                'message': f"Conversation with ID {conversation_id} not found"
            }
        
        # Check if conversation has a Gmail thread ID
        if not conversation.gmail_thread_id:
            return {
                'success': False,
                'message': f"Conversation {conversation_id} does not have a Gmail thread ID"
            }
        
        # Get any Gmail credential (we'll use the first one for now)
        try:
            cred = GmailCredential.objects.first()
            if not cred:
                return {
                    'success': False,
                    'message': "No Gmail credentials found. Please connect a Gmail account first."
                }
            # Ensure token is fresh before using it
            cred = ensure_fresh_token(cred)
        except GmailCredential.DoesNotExist:
            return {
                'success': False,
                'message': "No Gmail credentials found. Please connect a Gmail account first."
            }
        
        # Get all existing message IDs for this conversation to avoid processing duplicates
        existing_message_ids = set(
            EmailChatMessage.objects.filter(
                conversation=conversation
            ).values_list('gmail_message_id', flat=True)
        )
        
        # Also get messages with empty bodies that need to be updated
        messages_with_empty_bodies = EmailChatMessage.objects.filter(
            conversation=conversation,
            body__isnull=True
        ) | EmailChatMessage.objects.filter(
            conversation=conversation,
            body=''
        )
        
        # Create a set of message IDs that need body updates
        messages_needing_body_update = set(
            messages_with_empty_bodies.values_list('gmail_message_id', flat=True)
        )
        
        # Get all existing attachment IDs for this conversation to avoid processing duplicates
        existing_attachment_ids = set(
            EmailAttachment.objects.filter(
                email_message__conversation=conversation
            ).values_list('gmail_attachment_id', flat=True)
        )
        
        # Also get existing attachments based on file content (filename + content_type + size)
        # This prevents storing the same file multiple times when Gmail creates new attachment IDs for replies
        existing_attachment_content = set()
        existing_attachments = EmailAttachment.objects.filter(
            email_message__conversation=conversation
        ).values('file_name', 'content_type', 'size_bytes')
        
        for att in existing_attachments:
            if att['file_name'] and att['content_type'] and att['size_bytes']:
                content_key = f"{att['file_name']}_{att['content_type']}_{att['size_bytes']}"
                existing_attachment_content.add(content_key)
        
        # Fetch thread messages from Gmail API (this is fast - just gets message IDs)
        try:
            thread_data = svc.get_thread_messages(cred, conversation.gmail_thread_id)
            thread_messages = thread_data.get('messages', [])
        except Exception as e:
            logger.error(f"Error fetching Gmail thread messages: {str(e)}")
            return {
                'success': False,
                'message': f"Failed to fetch Gmail thread messages: {str(e)}"
            }
        
        # Quick check: if all messages already exist, we might still need to update bodies
        thread_message_ids = {msg.get('id') for msg in thread_messages}
        all_messages_exist = thread_message_ids.issubset(existing_message_ids)
        
        # If all messages exist but some have empty bodies, we should still process for body updates
        if all_messages_exist and not messages_needing_body_update:
            return {
                'success': True,
                'message': 'All messages already synced',
                'data': {
                    'conversation_id': conversation_id,
                    'thread_id': conversation.gmail_thread_id,
                    'new_messages_count': 0,
                    'skipped_messages_count': len(thread_messages),
                    'new_attachments_count': 0,
                    'updated_bodies_count': 0,
                    'total_messages_in_thread': len(thread_messages)
                }
            }
        
        # Process only new messages (much faster!)
        new_messages_count = 0
        new_attachments_count = 0
        skipped_messages_count = 0
        
        for gmail_message in thread_messages:
            gmail_message_id = gmail_message.get('id')
            
            # Skip if message already exists
            if gmail_message_id in existing_message_ids:
                skipped_messages_count += 1
                continue
            
            # This is a new message - process it
            try:
                message_details = svc.get_message_details(cred, gmail_message_id)
                
                # Extract headers
                headers = message_details.get('payload', {}).get('headers', [])
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), '')
                from_email = next((h['value'] for h in headers if h['name'].lower() == 'from'), '')
                to_email = next((h['value'] for h in headers if h['name'].lower() == 'to'), '')
                date_header = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                
                # Clean emoji and special characters from text fields
                import re
                subject = re.sub(r'[^\x00-\x7F]+', '', subject)
                from_email = re.sub(r'[^\x00-\x7F]+', '', from_email)
                to_email = re.sub(r'[^\x00-\x7F]+', '', to_email)
                
                # Parse sent date
                sent_at = None
                if date_header:
                    try:
                        from email.utils import parsedate_to_datetime
                        sent_at = parsedate_to_datetime(date_header)
                    except:
                        pass
                
                # Extract body - comprehensive extraction for all Gmail message structures
                body = ''
                payload = message_details.get('payload', {})
                
                def extract_body_from_payload(payload_obj):
                    """Recursively extract body content from Gmail message payload"""
                    nonlocal body
                    
                    # If we already found a body, don't overwrite it
                    if body:
                        return
                    
                    # Check if this payload has a body with data
                    if payload_obj.get('body', {}).get('data'):
                        try:
                            import base64
                            content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('utf-8')
                            content = re.sub(r'[^\x00-\x7F]+', '', content)
                            if content.strip():
                                body = content
                                return
                        except (UnicodeDecodeError, Exception):
                            try:
                                content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('ascii', errors='ignore')
                                content = re.sub(r'[^\x00-\x7F]+', '', content)
                                if content.strip():
                                    body = content
                                    return
                            except Exception:
                                pass
                    
                    # Check if this payload has parts
                    if payload_obj.get('parts'):
                        for part in payload_obj['parts']:
                            # Prefer text/plain over text/html
                            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                                try:
                                    content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                    content = re.sub(r'[^\x00-\x7F]+', '', content)
                                    if content.strip():
                                        body = content
                                        return
                                except (UnicodeDecodeError, Exception):
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('ascii', errors='ignore')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except Exception:
                                        pass
                            
                            # If no text/plain found, try text/html
                            elif part.get('mimeType') == 'text/html' and part.get('body', {}).get('data') and not body:
                                try:
                                    content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                    content = re.sub(r'[^\x00-\x7F]+', '', content)
                                    if content.strip():
                                        body = content
                                        return
                                except (UnicodeDecodeError, Exception):
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('ascii', errors='ignore')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except Exception:
                                        pass
                            
                            # Recursively check nested parts
                            elif part.get('parts'):
                                extract_body_from_payload(part)
                
                # Extract body from the main payload
                extract_body_from_payload(payload)
                
                # If still no body found, try alternative extraction methods
                if not body:
                    # Try to get body from the message snippet if available
                    snippet = message_details.get('snippet', '')
                    if snippet:
                        body = re.sub(r'[^\x00-\x7F]+', '', snippet)
                    
                    # If still no body, try to extract from any text part
                    def find_any_text_content(payload_obj):
                        nonlocal body
                        if body:
                            return
                        
                        if payload_obj.get('body', {}).get('data'):
                            try:
                                content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('utf-8', errors='ignore')
                                content = re.sub(r'[^\x00-\x7F]+', '', content)
                                if content.strip():
                                    body = content
                                    return
                            except Exception:
                                pass
                        
                        if payload_obj.get('parts'):
                            for part in payload_obj['parts']:
                                if part.get('mimeType', '').startswith('text/') and part.get('body', {}).get('data'):
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except Exception:
                                        pass
                                elif part.get('parts'):
                                    find_any_text_content(part)
                    
                    find_any_text_content(payload)
                
                # Clean up the body content - remove quoted replies and email metadata
                if body:
                    def clean_email_body(content):
                        """Clean email body by removing quoted replies and metadata"""
                        if not content:
                            return content
                        
                        # Remove HTML entities first
                        content = re.sub(r'&[a-zA-Z]+;', '', content)
                        
                        # Handle single-line content by splitting on common reply patterns
                        if '\n' not in content or content.count('\n') < 2:
                            # For single-line content, try to extract just the first part before reply indicators
                            patterns_to_remove = [
                                r' On .+ at \d+:\d+, .+ wrote:.*',
                                r' On .+, .+ wrote:.*',
                                r' From: .+ <.+@.+>.*',
                                r' To: .+ <.+@.+>.*',
                                r' Subject: .+.*',
                                r' Date: .+.*',
                                r' Sent: .+.*',
                                r' Cc: .+.*',
                                r' Bcc: .+.*',
                                r' >.*',
                                r' [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*'
                            ]
                            
                            cleaned_content = content
                            for pattern in patterns_to_remove:
                                cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
                            
                            # Remove extra whitespace
                            cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                            return cleaned_content.strip()
                        
                        # For multi-line content, process line by line
                        lines = content.split('\n')
                        cleaned_lines = []
                        in_quoted_section = False
                        
                        for line in lines:
                            line_stripped = line.strip()
                            
                            # Skip empty lines
                            if not line_stripped:
                                continue
                            
                            # Check if this line starts a quoted section
                            if (line_stripped.startswith('On ') and 'wrote:' in line_stripped or
                                line_stripped.startswith('>') or
                                line_stripped.startswith('From:') or
                                line_stripped.startswith('To:') or
                                line_stripped.startswith('Subject:') or
                                line_stripped.startswith('Date:') or
                                line_stripped.startswith('Sent:') or
                                line_stripped.startswith('Cc:') or
                                line_stripped.startswith('Bcc:') or
                                re.match(r'^On .+ at \d+:\d+, .+ wrote:$', line_stripped) or
                                re.match(r'^On .+, .+ wrote:$', line_stripped) or
                                re.match(r'^From: .+ <.+@.+>$', line_stripped) or
                                re.match(r'^To: .+ <.+@.+>$', line_stripped) or
                                re.match(r'^Subject: .+$', line_stripped) or
                                re.match(r'^Date: .+$', line_stripped) or
                                re.match(r'^Sent: .+$', line_stripped)):
                                in_quoted_section = True
                                continue
                            
                            # If we're in a quoted section, skip lines that look like email addresses
                            if in_quoted_section:
                                if (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', line_stripped) or
                                    line_stripped in ['&lt;', '&gt;', '&amp;', '&quot;', '&apos;']):
                                    continue
                            
                            # Add the line if it's not in a quoted section or if it's meaningful content
                            if not in_quoted_section:
                                cleaned_lines.append(line)
                        
                        # Join the cleaned lines
                        cleaned_content = '\n'.join(cleaned_lines).strip()
                        
                        # Remove extra whitespace
                        cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                        
                        return cleaned_content.strip()
                    
                    # Clean the extracted body
                    body = clean_email_body(body)
                
                # Extract attachments (only new ones)
                attachments = []
                def extract_attachments_from_parts(parts):
                    for part in parts:
                        if part.get('filename') and part.get('body', {}).get('attachmentId'):
                            attachment_id = part.get('body', {}).get('attachmentId')
                            filename = part.get('filename', '')
                            mime_type = part.get('mimeType', '')
                            size = part.get('body', {}).get('size', 0)
                            
                            # Check both attachment ID and content duplicates
                            content_key = f"{filename}_{mime_type}_{size}"
                            is_duplicate = (
                                attachment_id in existing_attachment_ids or 
                                content_key in existing_attachment_content
                            )
                            
                            if not is_duplicate:
                                attachment_info = {
                                    'filename': filename,
                                    'mimeType': mime_type,
                                    'size': size,
                                    'attachmentId': attachment_id,
                                    'is_image': mime_type.startswith('image/')
                                }
                                attachments.append(attachment_info)
                        elif part.get('parts'):
                            extract_attachments_from_parts(part['parts'])
                
                if payload.get('parts'):
                    extract_attachments_from_parts(payload['parts'])
                elif payload.get('filename') and payload.get('body', {}).get('attachmentId'):
                    attachment_id = payload.get('body', {}).get('attachmentId')
                    filename = payload.get('filename', '')
                    mime_type = payload.get('mimeType', '')
                    size = payload.get('body', {}).get('size', 0)
                    
                    # Check both attachment ID and content duplicates
                    content_key = f"{filename}_{mime_type}_{size}"
                    is_duplicate = (
                        attachment_id in existing_attachment_ids or 
                        content_key in existing_attachment_content
                    )
                    
                    if not is_duplicate:
                        attachment_info = {
                            'filename': filename,
                            'mimeType': mime_type,
                            'size': size,
                            'attachmentId': attachment_id,
                            'is_image': mime_type.startswith('image/')
                        }
                        attachments.append(attachment_info)
                
                # Basic validation to ensure data is safe for database
                try:
                    subject = str(subject)[:1000] if subject else ''
                    from_email = str(from_email)[:500] if from_email else ''
                    to_email = str(to_email)[:500] if to_email else ''
                    body = str(body)[:10000] if body else ''
                    
                    # Normalize email formats to ensure consistency
                    def normalize_email_format(email_string):
                        """Normalize email format to extract just the email address"""
                        if not email_string:
                            return ""
                        
                        email_string = email_string.strip()
                        
                        # Handle "Name <email@domain.com>" format
                        if "<" in email_string and ">" in email_string:
                            start = email_string.find("<") + 1
                            end = email_string.find(">")
                            if start < end:
                                return email_string[start:end].strip().lower()
                        
                        # Handle raw email format
                        return email_string.lower()
                    
                    # Normalize email formats
                    from_email = normalize_email_format(from_email)
                    to_email = normalize_email_format(to_email)
                    
                    # Clean attachment data
                    for attachment_info in attachments:
                        attachment_info['filename'] = str(attachment_info['filename'])[:255] if attachment_info['filename'] else ''
                        attachment_info['mimeType'] = str(attachment_info['mimeType'])[:100] if attachment_info['mimeType'] else ''
                        attachment_info['attachmentId'] = str(attachment_info['attachmentId'])[:500] if attachment_info['attachmentId'] else ''
                    
                except Exception as e:
                    logger.error(f"Error cleaning message data for {gmail_message_id}: {str(e)}")
                    continue
                
                # Create new message record (incoming messages are unseen until user opens conversation)
                email_message = EmailChatMessage.objects.create(
                    conversation=conversation,
                    gmail_message_id=gmail_message_id,
                    gmail_thread_id=conversation.gmail_thread_id,
                    from_email=from_email,
                    to_email=to_email,
                    subject=subject,
                    body=body,
                    sent_at=sent_at,
                    first_message_id=thread_messages[0].get('id') if thread_messages else None,
                    is_seen=False,
                )
                new_messages_count += 1
                
                # Handle attachments for new message
                for attachment_info in attachments:
                    attachment, created = EmailAttachment.objects.get_or_create(
                        email_message=email_message,
                        gmail_attachment_id=attachment_info['attachmentId'],
                        defaults={
                            'file_name': attachment_info['filename'],
                            'file_url': f"gmail://{gmail_message_id}/{attachment_info['attachmentId']}",  # Set proper gmail:// format
                            'content_type': attachment_info['mimeType'],
                            'size_bytes': attachment_info['size'],
                            'is_image': attachment_info['is_image']
                        }
                    )
                    
                    # Download and upload to S3 if it's a new attachment OR if existing attachment still has Gmail URL
                    should_upload_to_s3 = (
                        (created and attachment_info['attachmentId']) or  # New attachment
                        (not created and attachment.file_url and attachment.file_url.startswith('gmail://') and attachment_info['attachmentId'])  # Existing attachment with Gmail URL
                    )
                    
                    if should_upload_to_s3:
                        if created:
                            logger.info(f"[DOCUMENT_SYNC] Processing NEW attachment: {attachment_info['filename']}")
                        else:
                            logger.info(f"[DOCUMENT_SYNC] Processing EXISTING attachment with Gmail URL: {attachment_info['filename']} (current URL: {attachment.file_url})")
                        
                        try:
                            # Fetch attachment data from Gmail
                            attachment_data = svc.get_attachment(cred, gmail_message_id, attachment_info['attachmentId'])
                            
                            if attachment_data and attachment_data.get('data'):
                                import base64
                                
                                # Check if S3PresignedService is available
                                try:
                                    from envoy.services.s3_presigned_service import S3PresignedService
                                    logger.info(f"[DOCUMENT_SYNC] S3PresignedService imported successfully")
                                except ImportError as e:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Failed to import S3PresignedService: {e}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Import error details: {type(e).__name__}: {str(e)}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                except Exception as e:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Unexpected error importing S3PresignedService: {e}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Error type: {type(e).__name__}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                
                                # Decode the attachment data
                                file_data = base64.urlsafe_b64decode(attachment_data['data'])
                                
                                # Generate folder path for organization
                                folder_path = f"attachments/{conversation.id}/{email_message.id}"
                                
                                # Debug: Log environment configuration
                                import os
                                logger.info(f"[DOCUMENT_SYNC] Environment check for {attachment_info['filename']}:")
                                logger.info(f"[DOCUMENT_SYNC] - S3_ACCESS_KEY_ID: {'Set' if os.getenv('S3_ACCESS_KEY_ID') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - S3_SECRET_ACCESS_KEY: {'Set' if os.getenv('S3_SECRET_ACCESS_KEY') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - S3_BUCKET_NAME: {'Set' if os.getenv('S3_BUCKET_NAME') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - S3_REGION: {'Set' if os.getenv('S3_REGION') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - CDN_BASE_URL: {'Set' if os.getenv('CDN_BASE_URL') else 'Not set'}")
                                logger.info(f"[DOCUMENT_SYNC] - File size: {len(file_data)} bytes")
                                logger.info(f"[DOCUMENT_SYNC] - Folder path: {folder_path}")
                                
                                # Check if all required S3 environment variables are set
                                required_s3_vars = ['S3_ACCESS_KEY_ID', 'S3_SECRET_ACCESS_KEY', 'S3_BUCKET_NAME', 'S3_REGION']
                                missing_vars = [var for var in required_s3_vars if not os.getenv(var)]
                                if missing_vars:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Missing required S3 environment variables: {missing_vars}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Cannot upload to S3, attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                
                                # Test S3PresignedService instantiation
                                try:
                                    # Try to get the S3 client to test credentials
                                    s3_client = S3PresignedService._get_client()
                                    logger.info(f"[DOCUMENT_SYNC] ✅ S3PresignedService client created successfully")
                                except Exception as client_error:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Failed to create S3PresignedService client: {client_error}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Client error type: {type(client_error).__name__}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                
                                # Upload to S3 using presigned service
                                try:
                                    upload_result = S3PresignedService.upload_file_to_s3(
                                        file_content=file_data,
                                        file_name=attachment_info['filename'],
                                        folder=folder_path
                                    )
                                    
                                    # Debug: Log upload result details
                                    logger.info(f"[DOCUMENT_SYNC] Upload result for {attachment_info['filename']}: {upload_result}")
                                    
                                except Exception as upload_error:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ S3 upload failed for {attachment_info['filename']}: {upload_error}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Upload error type: {type(upload_error).__name__}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Upload error details: {str(upload_error)}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    continue
                                
                                if upload_result and upload_result.get('file_key'):
                                    # Get S3 key from upload result
                                    s3_key = upload_result["file_key"]
                                    
                                    # Construct CDN URL using CDN_BASE_URL
                                    import os
                                    cdn_base_url = os.getenv("CDN_BASE_URL")
                                    
                                    logger.info(f"[DOCUMENT_SYNC] Processing attachment {attachment_info['filename']} for conversation {conversation_id}")
                                    logger.info(f"[DOCUMENT_SYNC] S3 key: {s3_key}")
                                    logger.info(f"[DOCUMENT_SYNC] CDN_BASE_URL configured: {'Yes' if cdn_base_url else 'No'}")
                                    
                                    if cdn_base_url:
                                        cdn_url = f"{cdn_base_url.rstrip('/')}/{s3_key}"
                                        # Update attachment with CDN URL
                                        attachment.file_url = cdn_url
                                        attachment.save()
                                        
                                        logger.info(f"[DOCUMENT_SYNC] ✅ Uploaded attachment {attachment_info['filename']} to S3: {s3_key}")
                                        logger.info(f"[DOCUMENT_SYNC] ✅ CDN URL constructed: {cdn_url}")
                                        logger.info(f"[DOCUMENT_SYNC] ✅ CDN key functionality working properly")
                                        logger.info(f"[DOCUMENT_SYNC] ✅ Attachment URL updated from Gmail to CDN: {attachment.file_url}")
                                    else:
                                        # Fallback to presigned URL if CDN_BASE_URL not configured
                                        attachment.file_url = upload_result['file_url']
                                        attachment.save()
                                        
                                        logger.info(f"[DOCUMENT_SYNC] ⚠️ Uploaded attachment {attachment_info['filename']} to S3: {s3_key}")
                                        logger.warning(f"[DOCUMENT_SYNC] ⚠️ CDN_BASE_URL not configured, using presigned URL: {upload_result['file_url']}")
                                        logger.info(f"[DOCUMENT_SYNC] ⚠️ Attachment URL updated from Gmail to S3 presigned: {attachment.file_url}")
                                else:
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Failed to upload attachment {attachment_info['filename']} to S3")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Upload result: {upload_result}")
                                    logger.error(f"[DOCUMENT_SYNC] ❌ Attachment will remain with Gmail URL: {attachment.file_url}")
                                    
                            else:
                                logger.warning(f"Could not fetch attachment data for {attachment_info['filename']}")
                                
                        except Exception as e:
                            logger.error(f"Error uploading attachment {attachment_info['filename']} to S3: {str(e)}")
                            logger.error(f"Exception type: {type(e).__name__}")
                            logger.error(f"Exception details: {e}")
                            import traceback
                            logger.error(f"Traceback: {traceback.format_exc()}")
                            logger.error(f"Attachment will remain with Gmail URL: {attachment.file_url}")
                            # Continue with other attachments even if one fails
                    
                    if created:
                        new_attachments_count += 1
                        logger.info(f"Added new attachment {attachment_info['filename']} to message {gmail_message_id}")
                    else:
                        if attachment.file_url and not attachment.file_url.startswith('gmail://'):
                            logger.info(f"Attachment {attachment_info['filename']} already exists with CDN URL: {attachment.file_url}")
                        else:
                            logger.info(f"Attachment {attachment_info['filename']} already exists with Gmail URL: {attachment.file_url}")
                
                # Log if any attachments were skipped due to content duplicates
                if len(attachments) == 0 and message_details.get('payload', {}).get('parts'):
                    # Check if there were attachments but they were all duplicates
                    total_attachments_in_message = 0
                    def count_attachments_in_parts(parts):
                        nonlocal total_attachments_in_message
                        for part in parts:
                            if part.get('filename') and part.get('body', {}).get('attachmentId'):
                                total_attachments_in_message += 1
                            elif part.get('parts'):
                                count_attachments_in_parts(part['parts'])
                    
                    count_attachments_in_parts(message_details.get('payload', {}).get('parts', []))
                    if total_attachments_in_message > 0:
                        logger.info(f"Skipped {total_attachments_in_message} duplicate attachments in message {gmail_message_id} (same files already exist in conversation)")
                
            except Exception as e:
                logger.error(f"Error processing new message {gmail_message_id}: {str(e)}")
                continue
        
        # Update existing messages that have empty bodies
        updated_bodies_count = 0
        if messages_needing_body_update:
            logger.info(f"Found {len(messages_needing_body_update)} messages with empty bodies, attempting to update them")
            
            for gmail_message_id in messages_needing_body_update:
                try:
                    # Get the existing message
                    existing_message = EmailChatMessage.objects.get(
                        conversation=conversation,
                        gmail_message_id=gmail_message_id
                    )
                    
                    # Skip if body is already populated
                    if existing_message.body and existing_message.body.strip():
                        continue
                    
                    # Fetch fresh message details from Gmail
                    message_details = svc.get_message_details(cred, gmail_message_id)
                    
                    # Extract body using the same comprehensive logic
                    body = ''
                    payload = message_details.get('payload', {})
                    
                    # Import re module for text cleaning
                    import re
                    
                    def extract_body_from_payload_for_update(payload_obj):
                        """Recursively extract body content from Gmail message payload for updates"""
                        nonlocal body
                        
                        if body:
                            return
                        
                        # Check if this payload has a body with data
                        if payload_obj.get('body', {}).get('data'):
                            try:
                                import base64
                                content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('utf-8')
                                content = re.sub(r'[^\x00-\x7F]+', '', content)
                                if content.strip():
                                    body = content
                                    return
                            except (UnicodeDecodeError, Exception):
                                try:
                                    content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('ascii', errors='ignore')
                                    content = re.sub(r'[^\x00-\x7F]+', '', content)
                                    if content.strip():
                                        body = content
                                        return
                                except Exception:
                                    pass
                        
                        # Check if this payload has parts
                        if payload_obj.get('parts'):
                            for part in payload_obj['parts']:
                                # Prefer text/plain over text/html
                                if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except (UnicodeDecodeError, Exception):
                                        try:
                                            content = base64.urlsafe_b64decode(part['body']['data']).decode('ascii', errors='ignore')
                                            content = re.sub(r'[^\x00-\x7F]+', '', content)
                                            if content.strip():
                                                body = content
                                                return
                                        except Exception:
                                            pass
                                
                                # If no text/plain found, try text/html
                                elif part.get('mimeType') == 'text/html' and part.get('body', {}).get('data') and not body:
                                    try:
                                        content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                                        content = re.sub(r'[^\x00-\x7F]+', '', content)
                                        if content.strip():
                                            body = content
                                            return
                                    except (UnicodeDecodeError, Exception):
                                        try:
                                            content = base64.urlsafe_b64decode(part['body']['data']).decode('ascii', errors='ignore')
                                            content = re.sub(r'[^\x00-\x7F]+', '', content)
                                            if content.strip():
                                                body = content
                                                return
                                        except Exception:
                                            pass
                                
                                # Recursively check nested parts
                                elif part.get('parts'):
                                    extract_body_from_payload_for_update(part)
                    
                    # Extract body from the main payload
                    extract_body_from_payload_for_update(payload)
                    
                    # If still no body found, try alternative extraction methods
                    if not body:
                        # Try to get body from the message snippet if available
                        snippet = message_details.get('snippet', '')
                        if snippet:
                            body = re.sub(r'[^\x00-\x7F]+', '', snippet)
                        
                        # If still no body, try to extract from any text part
                        def find_any_text_content_for_update(payload_obj):
                            nonlocal body
                            if body:
                                return
                            
                            if payload_obj.get('body', {}).get('data'):
                                try:
                                    content = base64.urlsafe_b64decode(payload_obj['body']['data']).decode('utf-8', errors='ignore')
                                    content = re.sub(r'[^\x00-\x7F]+', '', content)
                                    if content.strip():
                                        body = content
                                        return
                                except Exception:
                                    pass
                            
                            if payload_obj.get('parts'):
                                for part in payload_obj['parts']:
                                    if part.get('mimeType', '').startswith('text/') and part.get('body', {}).get('data'):
                                        try:
                                            content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                            content = re.sub(r'[^\x00-\x7F]+', '', content)
                                            if content.strip():
                                                body = content
                                                return
                                        except Exception:
                                            pass
                                    elif part.get('parts'):
                                        find_any_text_content_for_update(part)
                        
                        find_any_text_content_for_update(payload)
                    
                    # Clean up the body content - remove quoted replies and email metadata
                    if body:
                        def clean_email_body_for_update(content):
                            """Clean email body by removing quoted replies and metadata"""
                            if not content:
                                return content
                            
                            # Remove HTML entities first
                            content = re.sub(r'&[a-zA-Z]+;', '', content)
                            
                            # Handle single-line content by splitting on common reply patterns
                            if '\n' not in content or content.count('\n') < 2:
                                # For single-line content, try to extract just the first part before reply indicators
                                patterns_to_remove = [
                                    r' On .+ at \d+:\d+, .+ wrote:.*',
                                    r' On .+, .+ wrote:.*',
                                    r' From: .+ <.+@.+>.*',
                                    r' To: .+ <.+@.+>.*',
                                    r' Subject: .+.*',
                                    r' Date: .+.*',
                                    r' Sent: .+.*',
                                    r' Cc: .+.*',
                                    r' Bcc: .+.*',
                                    r' >.*',
                                    r' [a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}.*'
                                ]
                                
                                cleaned_content = content
                                for pattern in patterns_to_remove:
                                    cleaned_content = re.sub(pattern, '', cleaned_content, flags=re.IGNORECASE)
                                
                                # Remove extra whitespace
                                cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                                return cleaned_content.strip()
                            
                            # For multi-line content, process line by line
                            lines = content.split('\n')
                            cleaned_lines = []
                            in_quoted_section = False
                            
                            for line in lines:
                                line_stripped = line.strip()
                                
                                # Skip empty lines
                                if not line_stripped:
                                    continue
                                
                                # Check if this line starts a quoted section
                                if (line_stripped.startswith('On ') and 'wrote:' in line_stripped or
                                    line_stripped.startswith('>') or
                                    line_stripped.startswith('From:') or
                                    line_stripped.startswith('To:') or
                                    line_stripped.startswith('Subject:') or
                                    line_stripped.startswith('Date:') or
                                    line_stripped.startswith('Sent:') or
                                    line_stripped.startswith('Cc:') or
                                    line_stripped.startswith('Bcc:') or
                                    re.match(r'^On .+ at \d+:\d+, .+ wrote:$', line_stripped) or
                                    re.match(r'^On .+, .+ wrote:$', line_stripped) or
                                    re.match(r'^From: .+ <.+@.+>$', line_stripped) or
                                    re.match(r'^To: .+ <.+@.+>$', line_stripped) or
                                    re.match(r'^Subject: .+$', line_stripped) or
                                    re.match(r'^Date: .+$', line_stripped) or
                                    re.match(r'^Sent: .+$', line_stripped)):
                                    in_quoted_section = True
                                    continue
                                
                                # If we're in a quoted section, skip lines that look like email addresses
                                if in_quoted_section:
                                    if (re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', line_stripped) or
                                        line_stripped in ['&lt;', '&gt;', '&amp;', '&quot;', '&apos;']):
                                        continue
                                
                                # Add the line if it's not in a quoted section or if it's meaningful content
                                if not in_quoted_section:
                                    cleaned_lines.append(line)
                            
                            # Join the cleaned lines
                            cleaned_content = '\n'.join(cleaned_lines).strip()
                            
                            # Remove extra whitespace
                            cleaned_content = re.sub(r'\s+', ' ', cleaned_content)
                            
                            return cleaned_content.strip()
                        
                        # Clean the extracted body
                        body = clean_email_body_for_update(body)
                    
                    # Update the message body if we found content
                    if body and body.strip():
                        existing_message.body = body[:10000]  # Limit to 10k characters
                        existing_message.save()
                        updated_bodies_count += 1
                        logger.info(f"Updated body for message {gmail_message_id}")
                    
                except Exception as e:
                    logger.error(f"Error updating body for message {gmail_message_id}: {str(e)}")
                    continue
        
        logger.info(f"Synced Gmail thread for conversation {conversation_id}: {new_messages_count} new messages, {skipped_messages_count} skipped (already stored), {new_attachments_count} new attachments, {updated_bodies_count} bodies updated")
        
        return {
            'success': True,
            'message': f"Successfully synced {new_messages_count} new messages, skipped {skipped_messages_count} existing messages, added {new_attachments_count} new attachments, and updated {updated_bodies_count} message bodies",
            'data': {
                'conversation_id': conversation_id,
                'thread_id': conversation.gmail_thread_id,
                'new_messages_count': new_messages_count,
                'skipped_messages_count': skipped_messages_count,
                'new_attachments_count': new_attachments_count,
                'updated_bodies_count': updated_bodies_count,
                'total_messages_in_thread': len(thread_messages)
            }
        }
        
    except Exception as e:
        logger.error(f"Error in sync_gmail_thread_messages: {str(e)}")
        return {
            'success': False,
            'message': f"Internal error during thread sync: {str(e)}"
        }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_chatmail_conversations(request):
    """Get all chatmail conversations with unread (unseen) message count per conversation."""
    try:
        from django.db.models import Count, Q

        user_id = request.GET.get('user_id')
        conversation_type = request.GET.get('conversation_type')
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        
        conversations = ChatConversation.objects.all()
        
        if user_id:
            conversations = conversations.filter(user_id=user_id)
        
        if conversation_type:
            conversations = conversations.filter(type=conversation_type)
        
        # Annotate unread count: messages where is_seen=False (new messages received)
        conversations = conversations.select_related('user', 'insurer').annotate(
            unread_count=Count('messages', filter=Q(messages__is_seen=False), distinct=True)
        ).order_by('-created_at')
        
        # Paginate results
        total_count = conversations.count()
        start = (page - 1) * page_size
        end = start + page_size
        paginated_conversations = conversations[start:end]
        
        conversation_data = []
        for conversation in paginated_conversations:
            unread = getattr(conversation, 'unread_count', 0) or 0
            conversation_data.append({
                'id': conversation.id,
                'code': conversation.code,
                'type': conversation.type,
                'type_based_id': conversation.type_based_id,
                'insurer_id': conversation.insurer_id,
                'insurer_name': conversation.insurer.name if conversation.insurer else None,
                'user_id': conversation.user_id,
                'user_name': conversation.user.display_name if conversation.user else None,
                'gmail_thread_id': conversation.gmail_thread_id,
                'created_at': conversation.created_at,
                'message_count': conversation.messages.count(),
                'unread_count': unread,
                'has_new_messages': unread > 0,
            })
        
        return Response(
            {
                "success": True,
                "message": "Conversations retrieved successfully",
                "data": {
                    'conversations': conversation_data,
                    'pagination': {
                        'page': page,
                        'page_size': page_size,
                        'total_count': total_count,
                        'total_pages': (total_count + page_size - 1) // page_size
                    }
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in get_chatmail_conversations: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_conversation_seen(request):
    """
    Mark all messages in a conversation as seen (read).
    Call this when the user opens a conversation so unread_count goes to zero.
    """
    try:
        conversation_id = request.data.get('conversation_id')
        if not conversation_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "conversation_id is required",
                    "error_code": "MISSING_CONVERSATION_ID",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            conversation = ChatConversation.objects.get(id=conversation_id)
        except ChatConversation.DoesNotExist:
            return Response(
                {
                    "error": "Not found",
                    "message": f"Conversation with id {conversation_id} not found",
                    "error_code": "CONVERSATION_NOT_FOUND",
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        updated = EmailChatMessage.objects.filter(conversation=conversation, is_seen=False).update(is_seen=True)
        return Response(
            {
                "success": True,
                "message": "Conversation marked as seen",
                "data": {
                    "conversation_id": conversation_id,
                    "messages_marked_seen": updated,
                },
            },
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Error in mark_conversation_seen: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": str(e),
                "error_code": "INTERNAL_SERVER_ERROR",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_attachment(request):
    """
    Download/access attachment file from S3 or local storage.
    This endpoint serves files from S3/CDN or falls back to local storage.
    """
    try:
        attachment_id = request.GET.get('attachment_id')
        
        if not attachment_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "attachment_id is required",
                    "error_code": "MISSING_ATTACHMENT_ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the attachment record
        try:
            attachment = EmailAttachment.objects.get(id=attachment_id)
        except EmailAttachment.DoesNotExist:
            return Response(
                {
                    "error": "Attachment not found",
                    "message": f"Attachment with ID {attachment_id} not found",
                    "error_code": "ATTACHMENT_NOT_FOUND"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if file is stored in S3 with CDN URL
        if attachment.file_url and attachment.file_url.startswith('https://'):
            # Redirect to CDN URL for direct access
            from django.http import HttpResponseRedirect
            return HttpResponseRedirect(attachment.file_url)
        
        # Fallback to local file storage
        if attachment.file and attachment.file.name:
            from django.http import FileResponse
            
            try:
                # Open and serve the local file
                file_handle = attachment.file.open('rb')
                response = FileResponse(file_handle, content_type=attachment.content_type)
                
                # Set appropriate headers
                if attachment.is_image:
                    # For images, display in browser
                    response['Content-Disposition'] = f'inline; filename="{attachment.file_name}"'
                else:
                    # For other files, download
                    response['Content-Disposition'] = f'attachment; filename="{attachment.file_name}"'
                
                response['Content-Length'] = attachment.size_bytes
                
                return response
                
            except Exception as e:
                logger.error(f"Error serving local attachment file: {str(e)}")
                return Response(
                    {
                        "error": "Failed to serve file",
                        "message": f"Failed to serve attachment file: {str(e)}",
                        "error_code": "FILE_SERVE_FAILED"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        
        # No file found in either S3 or local storage
        return Response(
            {
                "error": "File not found",
                "message": "Attachment file is not available",
                "error_code": "FILE_NOT_FOUND"
            },
            status=status.HTTP_404_NOT_FOUND
        )
            
    except Exception as e:
        logger.error(f"Error in download_attachment: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_attachment_info(request):
    """
    Get attachment information without downloading the file.
    This is useful for displaying attachment details in the UI.
    """
    try:
        attachment_id = request.GET.get('attachment_id')
        
        if not attachment_id:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "attachment_id is required",
                    "error_code": "MISSING_ATTACHMENT_ID"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the attachment record
        try:
            attachment = EmailAttachment.objects.select_related('email_message__conversation').get(id=attachment_id)
        except EmailAttachment.DoesNotExist:
            return Response(
                {
                    "error": "Attachment not found",
                    "message": f"Attachment with ID {attachment_id} not found",
                    "error_code": "ATTACHMENT_NOT_FOUND"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Determine file access URLs based on storage location
        if attachment.file_url and attachment.file_url.startswith('https://'):
            # File is stored in S3 with CDN URL - use CDN URL for direct access
            download_url = attachment.file_url
            view_url = attachment.file_url if attachment.is_image else None
            storage_type = "s3_cdn"
        elif attachment.file and attachment.file.name:
            # File is stored locally - use direct media URL
            base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
            direct_url = f"{base_url}{attachment.file.url}"
            download_url = direct_url
            view_url = direct_url if attachment.is_image else None
            storage_type = "local"
        else:
            # Fallback to download endpoint if file not stored anywhere
            base_url = request.build_absolute_uri('/')[:-1]  # Remove trailing slash
            download_url = f"{base_url}/api/chatmail/download-attachment?attachment_id={attachment.id}"
            view_url = download_url if attachment.is_image else None
            storage_type = "unknown"
        
        # Return attachment information
        attachment_info = {
            'id': attachment.id,
            'file_name': attachment.file_name,
            'content_type': attachment.content_type,
            'size_bytes': attachment.size_bytes,
            'is_image': attachment.is_image,
            'created_at': attachment.created_at,
            'file_url': attachment.file_url,  # CDN URL or gmail:// format
            'storage_type': storage_type,  # s3_cdn, local, or unknown
            'download_url': download_url,
            'view_url': view_url,
            'message_info': {
                'message_id': attachment.email_message.id,
                'subject': attachment.email_message.subject,
                'conversation_id': attachment.email_message.conversation.id,
                'conversation_code': attachment.email_message.conversation.code
            }
        }
        
        return Response(
            {
                "success": True,
                "message": "Attachment information retrieved successfully",
                "data": attachment_info
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in get_attachment_info: {str(e)}")
        return Response(
            {
                "error": "Internal server error",
                "message": f"Internal server error: {str(e)}",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@api_view(['POST'])
def gmail_push_webhook(request):
    """
    Gmail Push Notification Webhook Handler for Real-time Email Detection.
    
    This endpoint receives push notifications with type, id, and mail.
    It finds conversations for that specific quotation/policy/endorsement and checks for new messages.
    
    Expected payload:
    {
        "type": "quotation" | "policy" | "endorsement",
        "id": <quotation_id | policy_id | endorsement_id>,
        "mail": "envoy.cloud.services@gmail.com"
    }
    
    The endpoint will:
    1. Construct type_based_id (QR-{id}, PR-{id}, or ER-{id})
    2. Find conversations with that type_based_id
    3. Get their gmail_thread_ids
    4. Check those threads for new messages
    5. Send notifications if new insurer messages are found
    """
    try:
        import json
        
        logger.info(f"[GMAIL_WEBHOOK] Received push notification")
        
        # Parse notification data
        notification_data = {}
        if request.body:
            try:
                notification_data = json.loads(request.body.decode('utf-8'))
            except:
                if hasattr(request, 'data') and request.data:
                    notification_data = request.data
        
        logger.info(f"[GMAIL_WEBHOOK] Notification data: {notification_data}")
        
        # Extract required fields from payload
        type_param = notification_data.get('type', '').lower()
        id_param = notification_data.get('id')
        email_address = notification_data.get('mail') or notification_data.get('email')
        
        # Validate required fields
        if not type_param or not id_param:
            logger.warning(f"[GMAIL_WEBHOOK] Missing required fields: type={type_param}, id={id_param}")
            return Response({
                "status": "acknowledged",
                "error": "Missing required fields: type and id are required"
            }, status=status.HTTP_200_OK)
        
        # Validate type
        valid_types = ['quotation', 'policy', 'endorsement']
        if type_param not in valid_types:
            logger.warning(f"[GMAIL_WEBHOOK] Invalid type: {type_param}")
            return Response({
                "status": "acknowledged",
                "error": f"Invalid type. Must be one of: {', '.join(valid_types)}"
            }, status=status.HTTP_200_OK)
        
        # Construct type_based_id based on type
        type_prefix_map = {
            'quotation': 'QR',
            'policy': 'PR',
            'endorsement': 'ER'
        }
        type_prefix = type_prefix_map[type_param]
        type_based_id = f"{type_prefix}-{id_param}"
        
        logger.info(f"[GMAIL_WEBHOOK] Processing notification for type={type_param}, id={id_param}, type_based_id={type_based_id}")
        
        # Get email address (use provided mail or default to system email)
        SYSTEM_EMAIL = "envoy.cloud.services@gmail.com"
        if not email_address:
            email_address = SYSTEM_EMAIL
            logger.info(f"[GMAIL_WEBHOOK] Using default system email: {email_address}")
        
        # Get Gmail credential for the email
        try:
            cred = GmailCredential.objects.get(system_email=email_address)
        except GmailCredential.DoesNotExist:
            logger.warning(f"[GMAIL_WEBHOOK] No Gmail credential found for {email_address}")
            return Response({
                "status": "acknowledged",
                "error": f"No Gmail credential found for {email_address}"
            }, status=status.HTTP_200_OK)
        
        # Find conversations for this type_based_id
        try:
            conversations = ChatConversation.objects.filter(
                type_based_id=type_based_id
            ).exclude(
                gmail_thread_id__isnull=True
            ).exclude(
                gmail_thread_id=''
            ).select_related('user', 'insurer')
            
            if not conversations.exists():
                logger.info(f"[GMAIL_WEBHOOK] No conversations found for type_based_id: {type_based_id}")
                return Response({
                    "status": "acknowledged",
                    "type": type_param,
                    "id": id_param,
                    "type_based_id": type_based_id,
                    "conversations": [],
                    "message": f"No conversations found for {type_param} {id_param}"
                }, status=status.HTTP_200_OK)
            
            logger.info(f"[GMAIL_WEBHOOK] Found {conversations.count()} conversations for type_based_id: {type_based_id}")
            
            # Process each conversation - check if thread has new messages
            synced_conversations = set()
            conversations_details = []  # Track conversation details with new message counts
            notifications_sent = 0
            
            for conversation in conversations:
                try:
                    # Avoid syncing the same conversation multiple times
                    if conversation.id in synced_conversations:
                        continue
                    
                    if not conversation.gmail_thread_id:
                        logger.debug(f"[GMAIL_WEBHOOK] Conversation {conversation.id} has no gmail_thread_id, skipping")
                        continue
                    
                    logger.info(f"[GMAIL_WEBHOOK] Checking conversation {conversation.id} (thread: {conversation.gmail_thread_id})...")
                    
                    # Sync this conversation - the sync function will check for new messages
                    sync_result = sync_gmail_thread_messages(conversation.id)
                    
                    if sync_result.get('success'):
                        synced_conversations.add(conversation.id)
                        new_messages = sync_result.get('data', {}).get('new_messages_count', 0)
                        new_attachments = sync_result.get('data', {}).get('new_attachments_count', 0)
                        updated_bodies = sync_result.get('data', {}).get('updated_bodies_count', 0)
                        
                        logger.info(f"[GMAIL_WEBHOOK] Conversation {conversation.id} has {new_messages} new messages, {new_attachments} attachments, {updated_bodies} bodies updated")
                        
                        # Store conversation details (include all synced conversations, even with 0 new messages)
                        conversations_details.append({
                            "conversation_id": conversation.id,
                            "conversation_code": conversation.code,
                            "gmail_thread_id": conversation.gmail_thread_id,
                            "insurer_id": conversation.insurer.id if conversation.insurer else None,
                            "insurer_name": conversation.insurer.name if conversation.insurer else None,
                            "new_messages_count": new_messages,
                            "new_attachments_count": new_attachments,
                            "updated_bodies_count": updated_bodies
                        })
                        
                        # Check if any new messages are from insurers and send notifications
                        if new_messages > 0:
                            notifications_sent += _send_notifications_for_new_insurer_messages(conversation)
                    else:
                        logger.warning(f"[GMAIL_WEBHOOK] Failed to sync conversation {conversation.id}: {sync_result.get('message')}")
                        
                except Exception as conv_error:
                    logger.error(f"[GMAIL_WEBHOOK] Error processing conversation {conversation.id}: {str(conv_error)}")
                    continue
            
            logger.info(f"[GMAIL_WEBHOOK] Processed notification: synced {len(synced_conversations)} conversation(s), sent {notifications_sent} notification(s)")
            
        except Exception as sync_error:
            logger.error(f"[GMAIL_WEBHOOK] Error syncing conversations: {str(sync_error)}")
        
        # Always return 200 to acknowledge receipt (Gmail expects this)
        return Response({
            "status": "acknowledged",
            "type": type_param,
            "id": id_param,
            "type_based_id": type_based_id,
            "synced_conversations": len(synced_conversations),
            "notifications_sent": notifications_sent,
            "conversations": conversations_details
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"[GMAIL_WEBHOOK] Unexpected error: {str(e)}", exc_info=True)
        # Still return 200 to acknowledge (don't want Gmail to retry)
        return Response({"status": "acknowledged", "error": str(e)}, status=status.HTTP_200_OK)


def _send_notifications_for_new_insurer_messages(conversation):
    """
    Check for unread reply messages (from insurer) in a conversation and send a single notification
    with the count, e.g. "You received 2 reply message(s) for this conversation."
    Reply messages are stored in DB with is_seen=False (unread) until the user opens the conversation.
    Returns the number of notifications sent (0 or 1).
    """
    try:
        from envoy.controllers.services.NotificationService import NotificationService

        # Get insurer_id from conversation
        insurer_id = None
        if hasattr(conversation, 'insurer') and conversation.insurer:
            insurer_id = conversation.insurer.id
        elif hasattr(conversation, 'insurer_id'):
            insurer_id = conversation.insurer_id

        # Only process if conversation has insurer_id and type_based_id
        if not insurer_id or not conversation.type_based_id:
            return 0

        # Get insurer email for matching reply messages
        insurer_record = (
            QueryBuilderService("core_service_providers")
            .select("email", "name")
            .where("id", insurer_id)
            .first()
        )

        if not insurer_record or not insurer_record.get("email"):
            return 0

        insurer_email_raw = insurer_record.get("email").strip().lower()

        def normalize_email(email_string):
            if not email_string:
                return ""
            email_string = email_string.strip()
            if "<" in email_string and ">" in email_string:
                start = email_string.find("<") + 1
                end = email_string.find(">")
                if start < end:
                    return email_string[start:end].strip().lower()
            return email_string.lower()

        insurer_email = normalize_email(insurer_email_raw)

        # Count unread reply messages from insurer (stored as is_seen=False)
        unread_reply_count = (
            EmailChatMessage.objects
            .filter(
                conversation=conversation,
                is_seen=False,
            )
            .exclude(from_email__isnull=True)
            .exclude(from_email="")
        )
        # Filter in Python for normalized from_email match (DB may store "Name <email>" or raw email)
        unread_reply_ids = [
            m.id for m in unread_reply_count
            if normalize_email(m.from_email or "") == insurer_email
        ]
        unread_count = len(unread_reply_ids)

        if unread_count == 0:
            return 0

        # Get user_id from conversation
        user_id = None
        if hasattr(conversation, 'user') and conversation.user:
            user_id = conversation.user.id
        if not user_id:
            return 0

        # Extract quotation_request_id from type_based_id for metadata
        type_based_id = conversation.type_based_id
        quotation_request_id = None
        if type_based_id.startswith("QR-"):
            quotation_request_id = type_based_id.replace("QR-", "")
        elif type_based_id.startswith("PR-"):
            quotation_request_id = type_based_id.replace("PR-", "")

        insurer_name = insurer_record.get("name", "Insurer")
        reply_word = "reply" if unread_count == 1 else "replies"
        notification_title = f"New {reply_word.capitalize()} from {insurer_name}"
        notification_message = (
            f"You received {unread_count} reply message{'s' if unread_count != 1 else ''} for this conversation."
        )

        meta_data = {
            "conversation_id": str(conversation.id),
            "conversation_code": conversation.code,
            "insurer_id": str(insurer_id),
            "insurer_name": insurer_name,
            "unread_reply_count": unread_count,
            "message_ids": [str(i) for i in unread_reply_ids],
        }
        if quotation_request_id:
            meta_data["quotation_request_id"] = quotation_request_id

        try:
            NotificationService.generate_notification(
                type_code="email_reply",
                title=notification_title,
                meta_data=meta_data,
                message=notification_message,
                customer_id=None,
                user_id=user_id,
            )
            logger.info(
                f"[NOTIFICATION] Sent notification: {unread_count} unread reply message(s) for conversation {conversation.id} (user: {user_id})"
            )
            return 1
        except Exception as notify_error:
            logger.error(f"[NOTIFICATION] Failed to send notification: {str(notify_error)}")
            return 0

    except Exception as e:
        logger.error(f"[NOTIFICATION] Error checking for insurer notifications: {str(e)}")
        return 0


# ----- Gmail Pub/Sub push webhook (real-time notifications) -----

def _extract_from_and_body_from_gmail_message(message_details: dict) -> tuple:
    """Extract From and body from Gmail API message details. Returns (from_email, body)."""
    import base64
    import re
    headers = message_details.get("payload", {}).get("headers", [])
    from_email = next((h["value"] for h in headers if h.get("name", "").lower() == "from"), "")
    from_email = re.sub(r"[^\x00-\x7F]+", "", from_email)
    body = ""

    def extract_body(payload_obj):
        nonlocal body
        if payload_obj.get("body", {}).get("data"):
            try:
                content = base64.urlsafe_b64decode(payload_obj["body"]["data"]).decode("utf-8", errors="ignore")
                if content.strip():
                    body = content
                    return
            except Exception:
                pass
        if payload_obj.get("parts"):
            for part in payload_obj["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    try:
                        content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        if content.strip():
                            body = content
                            return
                    except Exception:
                        pass
                elif part.get("mimeType") == "text/html" and part.get("body", {}).get("data") and not body:
                    try:
                        content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        if content.strip():
                            body = content
                            return
                    except Exception:
                        pass
                elif part.get("parts"):
                    extract_body(part)

    extract_body(message_details.get("payload", {}))
    if not body:
        body = message_details.get("snippet", "") or ""
    return (from_email or "(unknown)", body.strip() or "(empty)")


def _extract_full_mail_details(message_details: dict) -> dict:
    """
    Extract full mail details from Gmail API message for logging/printing.
    Returns dict with: message_id, thread_id, from_email, to_email, subject, date, body, snippet.
    """
    import base64
    import re
    payload = message_details.get("payload", {})
    headers = payload.get("headers", [])
    def header(name):
        return next((h.get("value", "") for h in headers if h.get("name", "").lower() == name.lower()), "")

    from_email = re.sub(r"[^\x00-\x7F]+", "", header("From") or "")
    to_email = re.sub(r"[^\x00-\x7F]+", "", header("To") or "")
    subject = re.sub(r"[^\x00-\x7F]+", "", header("Subject") or "").replace("\r", "").replace("\n", " ").strip()
    date_str = header("Date") or ""

    body = ""

    def extract_body(payload_obj):
        nonlocal body
        if payload_obj.get("body", {}).get("data"):
            try:
                content = base64.urlsafe_b64decode(payload_obj["body"]["data"]).decode("utf-8", errors="ignore")
                if content.strip():
                    body = content
                    return
            except Exception:
                pass
        if payload_obj.get("parts"):
            for part in payload_obj["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    try:
                        content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        if content.strip():
                            body = content
                            return
                    except Exception:
                        pass
                elif part.get("mimeType") == "text/html" and part.get("body", {}).get("data") and not body:
                    try:
                        content = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="ignore")
                        if content.strip():
                            body = content
                            return
                    except Exception:
                        pass
                elif part.get("parts"):
                    extract_body(part)

    extract_body(payload)
    if not body:
        body = message_details.get("snippet", "") or ""

    return {
        "message_id": message_details.get("id", ""),
        "thread_id": message_details.get("threadId", ""),
        "from_email": from_email or "(unknown)",
        "to_email": to_email or "(unknown)",
        "subject": subject or "(no subject)",
        "date": date_str or "(no date)",
        "body": (body or "").strip() or "(empty)",
        "snippet": (message_details.get("snippet") or "").strip(),
    }


def _print_new_message_from_gmail(cred, message_id: str, inbox_email: str = "") -> None:
    """
    When a new mail is received (push triggered), fetch that message and print its exact details:
    message_id, thread_id, From, To, Subject, Date, Body. Also logs the same to application log.
    """
    import envoy.services.email_service as svc
    try:
        message_details = svc.get_message_details(cred, message_id)
        details = _extract_full_mail_details(message_details)
        to_inbox = inbox_email or (cred.system_email if cred else "")

        # Log so it appears in application logs
        logger.info(
            "[GMAIL_PUBSUB] New mail received | message_id=%s | thread_id=%s | from=%s | to=%s | subject=%s",
            details["message_id"],
            details["thread_id"],
            details["from_email"],
            details["to_email"],
            details["subject"],
        )

        # Print exact mail details to console (same as thread)
        print("\n" + "=" * 60)
        print("[GMAIL_PUBSUB] NEW MAIL RECEIVED (from this thread)")
        print("=" * 60)
        print(f"  Message ID : {details['message_id']}")
        print(f"  Thread ID : {details['thread_id']}")
        print(f"  To (inbox): {to_inbox}")
        print(f"  From      : {details['from_email']}")
        print(f"  To        : {details['to_email']}")
        print(f"  Subject   : {details['subject']}")
        print(f"  Date      : {details['date']}")
        print("  --- Body ---")
        print(details["body"])
        print("  ---")
        print("=" * 60 + "\n")
    except Exception as e:
        logger.warning(f"[GMAIL_PUBSUB] Could not fetch/print message {message_id}: {e}")
        print(f"[GMAIL_PUBSUB] Could not fetch/print message {message_id}: {e}")


def _handle_gmail_history(history_id: str, email_address: str) -> None:
    """
    Fetch Gmail history and sync affected threads to ChatConversation.
    Push sends the *current* historyId (after the change); we must request history *after* the
    previous id, so we use startHistoryId = (push historyId - 1) to get the new message(s).
    Prints From + full body for every new message, then runs sync for linked conversations.
    """
    import envoy.services.email_service as svc
    try:
        cred = GmailCredential.objects.filter(system_email=email_address).first()
        if not cred:
            logger.warning(f"[GMAIL_PUBSUB] No Gmail credential for {email_address}")
            return
        cred = ensure_fresh_token(cred)

        # Determine startHistoryId:
        # - Prefer last_history_id we have already processed (gap-safe)
        # - Fallback to (push historyId - 1) heuristic on first run
        stored_last = getattr(cred, "last_history_id", None)
        if stored_last:
            start_history_id = str(stored_last)
        else:
            try:
                start_history_id = str(max(1, int(history_id) - 1))
            except (TypeError, ValueError):
                start_history_id = history_id

        seen_thread_ids = set()
        page_token = None
        total_printed = 0
        while True:
            history_response = svc.get_history(cred, start_history_id, max_results=100, page_token=page_token)
            history_items = history_response.get("history", [])
            for item in history_items:
                messages_added = item.get("messagesAdded", [])
                for msg_added in messages_added:
                    msg = msg_added.get("message") if isinstance(msg_added.get("message"), dict) else {}
                    if not msg and isinstance(msg_added, dict) and "id" in msg_added:
                        msg = msg_added
                    message_id = msg.get("id") if isinstance(msg, dict) else None
                    thread_id = msg.get("threadId") if isinstance(msg, dict) else None
                    if message_id:
                        _print_new_message_from_gmail(cred, str(message_id), email_address)
                        total_printed += 1
                    if thread_id and thread_id not in seen_thread_ids:
                        seen_thread_ids.add(thread_id)
                        _process_new_message(thread_id)
            page_token = history_response.get("nextPageToken")
            if not page_token:
                break

        # Update last_history_id so the next push starts from here and avoids gaps
        try:
            cred.last_history_id = str(history_id)
            cred.save(update_fields=["last_history_id"])
        except Exception as save_err:
            logger.warning(
                "[GMAIL_PUBSUB] Could not persist last_history_id=%s for %s: %s",
                history_id,
                email_address,
                save_err,
            )
        if total_printed == 0:
            if not history_response.get("history"):
                logger.debug("[GMAIL_PUBSUB] No history records for startHistoryId=%s (push historyId=%s)", start_history_id, history_id)
            else:
                logger.debug("[GMAIL_PUBSUB] History had items but no messagesAdded with message id")
    except Exception as e:
        logger.error(f"[GMAIL_PUBSUB] Error in _handle_gmail_history: {str(e)}", exc_info=True)
        print(f"[GMAIL_PUBSUB] Error: {e}")


def _broadcast_new_mail_to_stream(conversation) -> None:
    """
    Notify the conversation owner via SSE so /api/notifications/stream receives a new_notification event.
    Called when new mail is synced for this conversation so the frontend can refetch notifications/chatmail.
    """
    try:
        user_id = getattr(conversation, "user_id", None) or (
            conversation.user.id if getattr(conversation, "user", None) else None
        )
        if user_id:
            from envoy.controllers.notification_live import broadcast_new_notification
            broadcast_new_notification(user_id)
            logger.debug("[GMAIL_PUBSUB] Broadcast new_notification to stream for user_id=%s (conversation %s)", user_id, conversation.id)
    except Exception as e:
        logger.warning("[GMAIL_PUBSUB] Failed to broadcast new mail to stream: %s", e)


def _process_new_message(thread_id: str) -> None:
    """
    Map thread_id to ChatConversation and run sync_gmail_thread_messages; notify if new messages.
    When new messages are synced, push to SSE stream so connected clients get real-time update.
    """
    try:
        conversation = ChatConversation.objects.filter(gmail_thread_id=thread_id).first()
        if not conversation:
            return
        result = sync_gmail_thread_messages(conversation.id)
        if not result.get("success"):
            return
        new_count = result.get("data", {}).get("new_messages_count", 0)
        if new_count > 0:
            _send_notifications_for_new_insurer_messages(conversation)
            # Push to notification stream so SSE clients get real-time update (even if no
            # email_reply notification was created, e.g. sender not insurer)
            _broadcast_new_mail_to_stream(conversation)
    except Exception as e:
        logger.error(f"[GMAIL_PUBSUB] Error in _process_new_message thread {thread_id}: {str(e)}", exc_info=True)


def _run_gmail_history_sync(history_id: str, email_address: str | None) -> None:
    """Run history sync in background; used by gmail_webhook to avoid proxy timeouts (502)."""
    try:
        mailbox = email_address
        if not mailbox:
            cred = GmailCredential.objects.first()
            mailbox = cred.system_email if cred else "(first credential)"
        print(f"[GMAIL_PUBSUB] Processing history sync for inbox: {mailbox} | historyId: {history_id}")
        if email_address:
            _handle_gmail_history(history_id, email_address)
        else:
            if cred:
                _handle_gmail_history(history_id, cred.system_email)
    except Exception as e:
        logger.error(f"[GMAIL_PUBSUB] Background sync error: {str(e)}", exc_info=True)
    finally:
        from django.db import connection
        connection.close()


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def gmail_webhook(request):
    """
    Pub/Sub push endpoint for Gmail push notifications.
    Expects POST body: { "message": { "data": "<base64-encoded JSON>" } }
    Decoded data: { "emailAddress": "...", "historyId": "..." }
    Returns 200 immediately and processes sync in a background thread to avoid 502 timeouts.
    """
    import base64
    import json
    import threading
    try:
        data = getattr(request, "data", None) or (json.loads(request.body.decode("utf-8")) if request.body else {})
        message = data.get("message")
        if not message:
            return Response({"status": "no message"}, status=status.HTTP_200_OK)
        raw_data = message.get("data")
        if not raw_data:
            return Response({"status": "no data"}, status=status.HTTP_200_OK)
        decoded = base64.b64decode(raw_data).decode("utf-8")
        payload = json.loads(decoded)
        email_address = payload.get("emailAddress")
        history_id = "".join(str(payload.get("historyId") or "").split())
        if not history_id:
            return Response({"status": "missing historyId"}, status=status.HTTP_200_OK)
        # If GMAIL_WATCH_ONLY_EMAIL is set, only process pushes for that mailbox (e.g. envoy.cloud.services@gmail.com)
        watch_only = os.getenv("GMAIL_WATCH_ONLY_EMAIL", "").strip()
        if watch_only and (not email_address or str(email_address or "").strip().lower() != watch_only.lower()):
            print(f"[GMAIL_PUBSUB] Skipped (only watching {watch_only}): inbox={email_address or '(none)'}")
            return Response({"status": "skipped", "reason": "only_this_inbox"}, status=status.HTTP_200_OK)
        inbox_display = "".join(str(email_address or "(from payload)").split()).replace("\n", " ").replace("\r", " ")
        print(f"[GMAIL_PUBSUB] Webhook triggered | Inbox (TO): {inbox_display} | historyId: {history_id}")
        # Process in background so we return 200 quickly and avoid proxy timeout (502)
        thread = threading.Thread(
            target=_run_gmail_history_sync,
            args=(history_id, email_address),
            daemon=True,
        )
        thread.start()
        return Response({"status": "received"}, status=status.HTTP_200_OK)
    except Exception as e:
        logger.error(f"[GMAIL_PUBSUB] Webhook error: {str(e)}", exc_info=True)
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_200_OK)

        # app/controllers/gmail_controller.py
import json
import os
from django.http import HttpResponse
from pydantic import ValidationError, validate_email
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.conf import settings
from envoy.controllers.approval_controller import get_bearer_token
from envoy.services import email_service as svc
from envoy.models.mail_model import GmailCredential, EmailMessage
import logging
import base64
from django.utils import timezone
from django.db import models
from django.core import signing
import time
from urllib.parse import urlencode
from django.utils.html import escape
import requests
from mServices.QueryBuilderService import QueryBuilderService


logger = logging.getLogger(__name__)

SCOPE_DESCRIPTIONS = {
    "openid": "Sign in with your Google account",
    "email": "View your email address",
    "https://www.googleapis.com/auth/userinfo.email": "See your primary Google account email",
    "https://www.googleapis.com/auth/gmail.readonly": "Read your Gmail messages and labels",
    "https://www.googleapis.com/auth/gmail.send": "Send email as you",
    "https://www.googleapis.com/auth/gmail.compose": "Create and manage drafts",
    "https://www.googleapis.com/auth/gmail.modify": "Read mail and modify labels",
}

# ---------- helpers ----------
def _mask(v: str) -> str:
    if not v:
        return ""
    if len(v) <= 8:
        return v[:2] + "…"
    return v[:4] + "…" + v[-4:]

def _get_conf(name: str, default=None):
    # Try Django settings, fallback to environment
    if hasattr(settings, name):
        val = getattr(settings, name)
        if val is not None:
            return val
    return os.environ.get(name, default)

def _parse_scopes(val):
    """
    Accepts:
      - list/tuple: returned as list
      - JSON array string: '["email","openid", ...]'
      - space/comma separated string (optionally quoted): 'email openid ...'
    Returns a list[str].
    """
    if isinstance(val, (list, tuple)):
        return list(val)
    if not isinstance(val, str):
        return []
    s = val.strip()
    # strip surrounding quotes if present
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        s = s[1:-1].strip()
    # JSON array?
    if s.startswith('[') and s.endswith(']'):
        try:
            arr = json.loads(s)
            return [str(x) for x in arr]
        except Exception:
            pass
    # split by whitespace or commas
    parts = []
    for chunk in s.replace(',', ' ').split():
        if chunk:
            parts.append(chunk)
    return parts

# ---------- START: auth_google_start ----------
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def auth_google_start(request, mail_address: str):
    """
    Start Google OAuth flow for *this* mail_address.
    Generates Google OAuth URL with full debug visibility.
    """
    try:
        print("\n================ GOOGLE OAUTH START ================\n")

        # ---- Load config ----
        client_id = _get_conf("GOOGLE_CLIENT_ID")
        client_secret = _get_conf("GOOGLE_CLIENT_SECRET")
        redirect_uri = _get_conf("GOOGLE_REDIRECT_URI")
        scopes_raw = _get_conf("GOOGLE_SCOPES")

        print("[CONFIG]")
        print("CLIENT_ID present:", bool(client_id))
        print("CLIENT_SECRET present:", bool(client_secret))
        print("REDIRECT_URI:", redirect_uri)
        print("RAW_SCOPES:", repr(scopes_raw))

        # ---- Parse & normalize scopes ----
        scopes = _parse_scopes(scopes_raw) if scopes_raw else []
        scopes = list(dict.fromkeys(s.strip() for s in scopes if s.strip()))  # dedupe + clean

        if not scopes:
            scopes = [
                "openid",
                "email",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/gmail.readonly",
                "https://www.googleapis.com/auth/gmail.send",
                "https://www.googleapis.com/auth/gmail.compose",
                "https://www.googleapis.com/auth/gmail.modify",
            ]

        print("\n[SCOPES]")
        print("COUNT:", len(scopes))
        for s in scopes:
            print(" -", s)

        # ---- Config validation ----
        missing = []
        if not client_id:
            missing.append("GOOGLE_CLIENT_ID")
        if not client_secret:
            missing.append("GOOGLE_CLIENT_SECRET")
        if not redirect_uri:
            missing.append("GOOGLE_REDIRECT_URI")

        if missing:
            print("\n[ERROR] Missing OAuth config:", missing)
            return Response(
                {
                    "error": "GOOGLE_OAUTH_CONFIG_MISSING",
                    "missing": missing,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ---- Validate email ----
        try:
            validate_email(mail_address)
        except ValidationError:
            print("\n[ERROR] Invalid email provided:", mail_address)
            return Response(
                {"error": "INVALID_EMAIL"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        print("\n[ACCOUNT TARGETING]")
        print("Login hint:", mail_address)
        print("Request user id:", request.user.id)

        # ---- Build signed state ----
        state_payload = {
            "uid": request.user.id,
            "email": mail_address,
            "ts": int(time.time()),
        }
        state = signing.dumps(state_payload, salt="google-oauth-state")

        print("\n[STATE]")
        print("State payload:", state_payload)
        print("Signed state length:", len(state))

        # ---- Build OAuth URL ----
        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "access_type": "offline",      # REQUIRED for refresh_token
            "prompt": "consent",           # REQUIRED to force refresh_token
            "include_granted_scopes": "true",
            "state": state,
            "login_hint": mail_address,
        }

        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"

        print("\n[OAUTH URL GENERATED]")
        print(auth_url)

        print("\n[IMPORTANT WARNINGS]")
        print("✔ Ensure callback stores token_data['access_token'], NOT id_token")
        print("✔ Ensure refresh_token is saved on FIRST consent")
        print("✔ Access tokens expire in ~1 hour")

        print("\n================ END GOOGLE OAUTH START ================\n")

        return Response(
            {
                "message": "Google OAuth authorization URL generated",
                "auth_url": auth_url,
                "state": state,
                "redirect_uri": redirect_uri,
                "scopes": scopes,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.exception("auth_google_start failed")
        return Response(
            {
                "error": "INTERNAL_SERVER_ERROR",
                "message": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# ---------- START: auth_google_callback ----------
@api_view(["GET"])
def auth_google_callback(request):
    """
    Handle Google OAuth callback (public endpoint).
    - Validates signed 'state' (uid + email)
    - Exchanges code for tokens
    - Enforces that the approved Google account matches the intended email
    - Saves/updates credentials
    - Returns a tiny success HTML that auto-closes
    """
    print("🔥 CALLBACK FUNCTION CALLED 🔥")
    print("🔥 CALLBACK FUNCTION CALLED 🔥")
    print("🔥 CALLBACK FUNCTION CALLED 🔥")
    try:
        print("=== OAUTH CALLBACK STARTED ===")
        print(f"Request URL: {request.get_full_path()}")
        print(f"Request params: {dict(request.query_params)}")
        print(f"Request method: {request.method}")
        print(f"Request headers: {dict(request.headers)}")
        
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        error = request.query_params.get("error")

        print(f"Code: {'PRESENT' if code else 'MISSING'}")
        print(f"State: {'PRESENT' if state else 'MISSING'}")
        print(f"Error: {error or 'NONE'}")
        
        if code:
            print(f"Code value: {code[:20]}...")
        if state:
            print(f"State value: {state[:50]}...")

        logger.info(
            "OAuth callback received - code: %s, state: %s, error: %s",
            "present" if code else "missing",
            "present" if state else "missing",
            error or "none",
        )

        if error:
            error_description = request.query_params.get("error_description", "Unknown error")
            logger.error("Google OAuth error: %s - %s", error, error_description)
            return Response(
                {
                    "error": "Google OAuth authorization failed",
                    "message": f"Authorization was denied: {error_description}",
                    "error_code": "GOOGLE_OAUTH_DENIED",
                    "google_error": error,
                    "google_error_description": error_description,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not code:
            print("=== MISSING AUTHORIZATION CODE ===")
            logger.error("Missing authorization code in callback")
            
            # Return debug HTML instead of JSON error
            debug_html = f"""<!doctype html>
<html>
<head><title>OAuth Debug</title></head>
<body>
    <h2>❌ OAuth Callback Debug</h2>
    <p><strong>Status:</strong> Missing authorization code</p>
    <p><strong>Request URL:</strong> {request.get_full_path()}</p>
    <p><strong>Request Params:</strong> {dict(request.query_params)}</p>
    <p><strong>Request Method:</strong> {request.method}</p>
    <p><strong>Headers:</strong> {dict(request.headers)}</p>
    <p>This means the OAuth flow did not complete properly or the redirect URI is incorrect.</p>
</body>
</html>"""
            return HttpResponse(debug_html, content_type="text/html")
        if not state:
            logger.error("Missing state parameter in callback")
            return Response(
                {
                    "error": "Missing state parameter",
                    "message": "State parameter is required for security",
                    "error_code": "MISSING_STATE_PARAMETER",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            print("=== VALIDATING STATE ===")
            print(f"State value: {state}")
            st = signing.loads(state, salt="google-oauth-state", max_age=600)  # 10 minutes
            print(f"State payload: {st}")
            user_id = st.get("uid")
            intended_email = st.get("email")
            print(f"User ID: {user_id}")
            print(f"Intended email: {intended_email}")
        except signing.BadSignature:
            print("=== STATE VALIDATION FAILED - Bad Signature ===")
            logger.error("Invalid or expired state signature")
            return Response(
                {
                    "error": "Invalid state parameter",
                    "message": "State parameter is invalid or expired",
                    "error_code": "INVALID_STATE_PARAMETER",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user_id = st.get("uid")
        intended_email = st.get("email")
        if not user_id or not intended_email:
            logger.error("State payload missing required fields: %s", st)
            return Response(
                {
                    "error": "Invalid state parameter",
                    "message": "State payload is missing required fields",
                    "error_code": "INVALID_STATE_PARAMETER",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resolve the user
        print("=== RESOLVING USER ===")
        print(f"Looking for user ID: {user_id}")
        from django.contrib.auth.models import User
        try:
            user = User.objects.get(id=user_id)
            print(f"User found: {user.username} (ID: {user.id})")
        except User.DoesNotExist:
            print(f"=== USER NOT FOUND ===")
            print(f"User with ID {user_id} does not exist")
            logger.error("User with ID %s does not exist", user_id)
            return Response(
                {
                    "error": "User not found",
                    "message": "User with the provided ID does not exist",
                    "error_code": "USER_NOT_FOUND",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --- Token exchange (ensure svc uses same redirect_uri) ---
        # svc should read GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI via settings or env,
        # just like start() does. If not, pass redirect explicitly.
        try:
            print("=== TOKEN EXCHANGE ===")
            print(f"Exchanging code: {code[:20]}...")
            logger.info("Starting token exchange")
            token_res = svc.exchange_code_for_tokens(code)  # pass redirect if your svc needs it
            print(f"Token response keys: {list(token_res.keys())}")
            print(f"Access token present: {'access_token' in token_res}")
            print(f"Refresh token present: {'refresh_token' in token_res}")
            logger.info("Token exchange successful")
        except Exception as e:
            print(f"=== TOKEN EXCHANGE FAILED ===")
            print(f"Error: {str(e)}")
            logger.error("Token exchange failed: %s", str(e))
            return Response(
                {
                    "error": "TOKEN_EXCHANGE_FAILED",
                    "message": "Failed to exchange authorization code for access token",
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        access_token = token_res.get("access_token")
        if not access_token:
            logger.error("Token response missing access_token: %s", token_res)
            return Response(
                {
                    "error": "INVALID_TOKEN_RESPONSE",
                    "message": "Google did not return a valid access token",
                    "token_response": token_res,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Fetch user info and enforce intended email
        try:
            print("=== FETCHING USER INFO ===")
            logger.info("Fetching user info from Google")
            userinfo = svc.fetch_userinfo(access_token)
            print(f"User info: {userinfo}")
            email = userinfo.get("email")
            print(f"Email from Google: {email}")
            print(f"Intended email: {intended_email}")
            if not email:
                print("=== EMAIL NOT FOUND IN USERINFO ===")
                logger.error("Userinfo missing email: %s", userinfo)
                return Response(
                    {
                        "error": "EMAIL_NOT_FOUND",
                        "message": "Could not retrieve email from Google user info",
                        "userinfo": userinfo,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if email.lower() != intended_email.lower():
                print("=== EMAIL MISMATCH ===")
                print(f"Intended: {intended_email}")
                print(f"Actual: {email}")
                logger.error("Email mismatch: intended=%s, actual=%s", intended_email, email)
                return Response(
                    {
                        "error": "EMAIL_MISMATCH",
                        "message": f"Please sign in as {intended_email}. You signed in as {email}.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            print("=== EMAIL VALIDATION PASSED ===")
            logger.info("User info retrieved and email enforced for: %s", email)

            # Save / update credentials
            try:
                print("=== SAVING CREDENTIALS ===")
                print(f"Email: {email}")
                print(f"User ID: {user.id}")
                print(f"Token response: {token_res}")
                cred = svc.upsert_credential(email, token_res, user)
                print(f"=== CREDENTIALS SAVED SUCCESSFULLY ===")
                print(f"Credential object: {cred}")
                print(f"Credential type: {type(cred)}")
                if cred:
                    print(f"Credential ID: {cred.id}")
                    print(f"System email: {cred.system_email}")
                    print(f"User: {cred.user}")
                else:
                    print("=== CREDENTIAL IS NONE ===")
                    print("The upsert_credential function returned None!")
                logger.info("Gmail credentials saved for email: %s, user_id: %s", email, user.id)
            except Exception as e:
                print(f"=== CREDENTIAL SAVE FAILED ===")
                print(f"Error: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                logger.error("Failed to save credentials: %s", str(e))
                
                # Return debug HTML instead of JSON error
                error_html = f"""<!doctype html>
<html>
<head><title>Credential Save Error</title></head>
<body>
    <h2>❌ Credential Save Error</h2>
    <p><strong>Error:</strong> {str(e)}</p>
    <p><strong>Error Type:</strong> {type(e)}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>User ID:</strong> {user.id}</p>
    <p><strong>Full Traceback:</strong></p>
    <pre style="background: #f3f4f6; padding: 10px; border-radius: 4px; overflow-x: auto;">{traceback.format_exc()}</pre>
    <p>Check the server console for more details.</p>
</body>
</html>"""
                return HttpResponse(error_html, content_type="text/html")

            # Success HTML
            print("=== GENERATING SUCCESS HTML ===")
            print(f"Credential object: {cred}")
            if cred:
                print(f"Credential ID: {cred.id}")
                print(f"Credential email: {cred.system_email}")
                email_safe = escape(cred.system_email or "")
            else:
                print("=== CREDENTIAL IS NONE - CANNOT GENERATE SUCCESS HTML ===")
                email_safe = escape(email or "")
            
            # Check database count
            from envoy.models.mail_model import GmailCredential
            try:
                total_creds = GmailCredential.objects.count()
                print(f"=== DATABASE CHECK ===")
                print(f"Total credentials in database: {total_creds}")
                print(f"Current credential ID: {cred.id}")
            except Exception as e:
                print(f"=== DATABASE CHECK FAILED ===")
                print(f"Error accessing database: {str(e)}")
                import traceback
                print(f"Database error traceback: {traceback.format_exc()}")
                total_creds = 0
            
            # Add a simple test to verify the credential exists
            try:
                test_cred = GmailCredential.objects.get(id=cred.id)
                print(f"=== CREDENTIAL VERIFICATION ===")
                print(f"Found credential: {test_cred.system_email}")
                print(f"User: {test_cred.user.username}")
            except Exception as e:
                print(f"=== CREDENTIAL VERIFICATION FAILED ===")
                print(f"Error: {str(e)}")
            
            # Retrieved credentials information
            if cred:
                retrieved_creds = f"""
                <div style="background: #e0f2fe; padding: 16px; margin: 16px 0; border-radius: 8px; border-left: 4px solid #0284c7;">
                    <h3 style="color: #0284c7; margin-top: 0;">🔑 Retrieved Credentials (Full Access - Unmasked):</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; font-family: monospace; font-size: 13px;">
                        <div>
                            <p><strong>Email:</strong> {cred.system_email}</p>
                            <p><strong>User:</strong> {cred.user.username} (ID: {cred.user.id})</p>
                            <p><strong>Credential ID:</strong> {cred.id}</p>
                            <p><strong>Token Expiry:</strong> {cred.token_expiry}</p>
                            <p><strong>Token URI:</strong> {cred.token_uri}</p>
                        </div>
                        <div>
                            <p><strong>Client ID:</strong></p>
                            <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto;">{cred.client_id}</pre>
                        </div>
                    </div>
                    <div style="margin-top: 16px;">
                        <p><strong>Access Token (Full):</strong></p>
                        <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.access_token}</pre>
                    </div>
                    <div style="margin-top: 16px;">
                        <p><strong>Refresh Token (Full):</strong></p>
                        <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.refresh_token or 'None'}</pre>
                    </div>
                    <div style="margin-top: 16px;">
                        <p><strong>Client Secret (Full):</strong></p>
                        <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #f8f9fa; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.client_secret}</pre>
                    </div>
                </div>
                """
            else:
                retrieved_creds = f"""
                <div style="background: #fef2f2; padding: 16px; margin: 16px 0; border-radius: 8px; border-left: 4px solid #ef4444;">
                    <h3 style="color: #ef4444; margin-top: 0;">❌ Credential Save Failed:</h3>
                    <p><strong>Error:</strong> The upsert_credential function returned None</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>User ID:</strong> {user.id}</p>
                    <p>Check the server console for more details.</p>
                </div>
                """
            
            # Add a simple test message
            if cred:
                test_message = f"""
                <div style="background: #fef3c7; padding: 16px; margin: 16px 0; border-radius: 8px; border-left: 4px solid #f59e0b;">
                    <h3 style="color: #f59e0b; margin-top: 0;">🧪 Test Information:</h3>
                    <p><strong>Callback Reached:</strong> ✅ YES</p>
                    <p><strong>Credential Created:</strong> ✅ YES</p>
                    <p><strong>Database Count:</strong> {total_creds}</p>
                    <p><strong>Credential ID:</strong> {cred.id}</p>
                    <p><strong>Email:</strong> {cred.system_email}</p>
                    <p><strong>User:</strong> {cred.user.username}</p>
                    <p><strong>Access Token (Full):</strong></p>
                    <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 11px;">{cred.access_token}</pre>
                    <p><strong>Refresh Token (Full):</strong></p>
                    <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 11px;">{cred.refresh_token or 'None'}</pre>
                </div>
                """
            else:
                test_message = f"""
                <div style="background: #fef2f2; padding: 16px; margin: 16px 0; border-radius: 8px; border-left: 4px solid #ef4444;">
                    <h3 style="color: #ef4444; margin-top: 0;">🧪 Test Information:</h3>
                    <p><strong>Callback Reached:</strong> ✅ YES</p>
                    <p><strong>Credential Created:</strong> ❌ NO (Returned None)</p>
                    <p><strong>Database Count:</strong> {total_creds}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>User ID:</strong> {user.id}</p>
                    <p><strong>Error:</strong> upsert_credential function returned None</p>
                </div>
                """
            
            # Debug information
            debug_info = f"""
            <div style="background: #f3f4f6; padding: 16px; margin: 16px 0; border-radius: 8px; font-family: monospace; font-size: 12px;">
                <h3>🔍 Debug Information (Full Credentials - Unmasked):</h3>
                <p><strong>Total Credentials in DB:</strong> {total_creds}</p>
                <p><strong>Credential ID:</strong> {cred.id}</p>
                <p><strong>System Email:</strong> {cred.system_email}</p>
                <p><strong>User ID:</strong> {cred.user.id}</p>
                <p><strong>User Name:</strong> {cred.user.username}</p>
                <p><strong>Token Expiry:</strong> {cred.token_expiry}</p>
                <p><strong>Token URI:</strong> {cred.token_uri}</p>
                <p><strong>Client ID (Full):</strong></p>
                <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 11px;">{cred.client_id}</pre>
                <p><strong>Client Secret (Full):</strong></p>
                <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 150px; overflow-y: auto; font-size: 11px;">{cred.client_secret}</pre>
                <p><strong>Access Token (Full):</strong></p>
                <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.access_token}</pre>
                <p><strong>Refresh Token (Full):</strong></p>
                <pre style="white-space: pre-wrap; word-break: break-all; overflow-x: auto; background: #fff; padding: 8px; border-radius: 4px; max-height: 200px; overflow-y: auto; font-size: 11px;">{cred.refresh_token or 'None'}</pre>
            </div>
            """
            
            html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Connected</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; margin: 40px; }}
    .card {{ max-width: 800px; margin: 0 auto; padding: 24px; border: 1px solid #e5e7eb; border-radius: 12px; }}
    h2 {{ margin: 0 0 8px; }}
    .muted {{ color: #6b7280; margin-top: 4px; }}
  </style>
</head>
<body>
  <div class="card">
    <h2>✅ Gmail connected</h2>
    <div class="muted">Account: {email_safe}</div>
    <p>You can close this window.</p>
    {test_message}
    {retrieved_creds}
    {debug_info}
  </div>
  <script>
    (function () {{
      try {{
        window.opener && window.opener.postMessage(
          {{
            type: "GOOGLE_OAUTH_SUCCESS",
            email: "{email_safe}",
            userId: {user.id}
          }},
          "*"
        );
      }} catch (e) {{}}
      window.close();
    }})();
  </script>
</body>
</html>"""
            return HttpResponse(html, content_type="text/html", status=200)

        except Exception as e:
            logger.error("Userinfo or credential save failed: %s", str(e))
            return Response(
                {
                    "error": "USERINFO_OR_SAVE_FAILED",
                    "message": "Failed to retrieve user info or save credentials",
                    "details": str(e),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

    except Exception as e:
        print(f"🔥 CALLBACK ERROR: {str(e)}")
        print(f"🔥 CALLBACK ERROR TYPE: {type(e)}")
        import traceback
        print(f"🔥 TRACEBACK: {traceback.format_exc()}")
        
        logger.error("Unexpected error in auth_google_callback: %s", str(e), exc_info=True)
        
        # Return debug HTML instead of JSON error
        error_html = f"""<!doctype html>
<html>
<head><title>OAuth Error</title></head>
<body>
    <h2>❌ OAuth Callback Error</h2>
    <p><strong>Error:</strong> {str(e)}</p>
    <p><strong>Error Type:</strong> {type(e)}</p>
    <p><strong>Request URL:</strong> {request.get_full_path()}</p>
    <p><strong>Request Params:</strong> {dict(request.query_params)}</p>
    <p><strong>Full Traceback:</strong></p>
    <pre style="background: #f3f4f6; padding: 10px; border-radius: 4px; overflow-x: auto;">{traceback.format_exc()}</pre>
    <p>Check the server console for more details.</p>
</body>
</html>"""
        return HttpResponse(error_html, content_type="text/html")

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def gmail_status(request):
    """
    Check Gmail integration status for a user.
    """
    try:
        email = request.query_params.get("email")
        user_id = request.user.id if hasattr(request.user, 'id') else None
        
        if not email:
            return Response(
                {
                    "error": "Email parameter required",
                    "message": "Email parameter is required to check Gmail status",
                    "error_code": "MISSING_EMAIL_PARAMETER"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Filter by both email and user for security
        if user_id:
            exists = GmailCredential.objects.filter(system_email=email, user_id=user_id).exists()
        else:
            exists = GmailCredential.objects.filter(system_email=email).exists()
        
        return Response(
            {
                "connected": exists,
                "email": email,
                "message": "Gmail status checked successfully"
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in gmail_status: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while checking Gmail status",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def gmail_messages(request):
    """
    Retrieve Gmail messages for a connected account.
    """
    try:
        email = request.query_params.get("email")
        if not email:
            return Response(
                {
                    "error": "Email parameter required",
                    "message": "Email parameter is required to retrieve Gmail messages",
                    "error_code": "MISSING_EMAIL_PARAMETER"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            cred = GmailCredential.objects.get(system_email=email)
        except GmailCredential.DoesNotExist:
            return Response(
                {
                    "error": "Gmail not connected",
                    "message": "Gmail account is not connected. Please connect your Gmail account first.",
                    "error_code": "GMAIL_NOT_CONNECTED",
                    "connected": False,
                    "action": "connect_first"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Get query parameters with defaults
        q = request.query_params.get("q", "")
        label = request.query_params.get("label", "INBOX")
        
        try:
            max_results = int(request.query_params.get("max", 10))
            if max_results <= 0 or max_results > 100:
                max_results = 10
        except ValueError:
            max_results = 10
        
        try:
            data = svc.list_messages(cred, q=q, label=label, max_results=max_results)
            logger.info(f"Gmail messages retrieved for {email}: {len(data.get('messages', []))} messages")
            
            return Response(
                {
                    "message": "Gmail messages retrieved successfully",
                    "email": email,
                    "connected": True,
                    "query": q,
                    "label": label,
                    "max_results": max_results,
                    "data": data
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error retrieving Gmail messages for {email}: {str(e)}")
            return Response(
                {
                    "error": "Failed to retrieve Gmail messages",
                    "message": "An error occurred while retrieving Gmail messages",
                    "error_code": "GMAIL_MESSAGES_RETRIEVAL_FAILED",
                    "details": str(e),
                    "email": email
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in gmail_messages: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving Gmail messages",
                "error_code": "INTERNAL_SERVER_ERROR"
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
def test_oauth_debug(request):
    """
    Debug endpoint to check OAuth status and credentials.
    """
    try:
        from envoy.models.mail_model import GmailCredential
        
        # Get all credentials
        credentials = GmailCredential.objects.all()
        cred_list = []
        
        for cred in credentials:
            cred_list.append({
                "email": cred.system_email,
                "has_access_token": bool(cred.access_token),
                "has_refresh_token": bool(cred.refresh_token),
                "token_expiry": cred.token_expiry.isoformat() if cred.token_expiry else None,
                "client_id": cred.client_id[:20] + "..." if cred.client_id else None
            })
        
        return Response(
            {
                "message": "OAuth Debug Information",
                "total_credentials": len(cred_list),
                "credentials": cred_list,
                "google_config": {
                    "client_id_set": bool(settings.GOOGLE_CLIENT_ID),
                    "client_secret_set": bool(settings.GOOGLE_CLIENT_SECRET),
                    "redirect_uri_set": bool(settings.GOOGLE_REDIRECT_URI),
                    "scopes_set": bool(settings.GOOGLE_SCOPES)
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in test_oauth_debug: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Debug endpoint error",
                "message": "Error retrieving debug information",
                "error_code": "DEBUG_ERROR",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_email(request):
    """
    Send email via Gmail API.
    
    Request body:
    {
        "to_email": "recipient@example.com",
        "subject": "Email Subject",
        "body": "Email body content",
        "thread_id": "optional_thread_id_for_replies",
        "conversation_id": "optional_conversation_id",
        "conversation_code": "optional_conversation_code",
        "first_message_id": "optional_first_message_id",
        "from_email": "sender@example.com"
    }
    """
    try:
        # Get request data
        to_email = request.data.get("to_email")
        subject = request.data.get("subject", "")
        body = request.data.get("body")
        thread_id = request.data.get("thread_id")
        conversation_id = request.data.get("conversation_id")
        conversation_code = request.data.get("conversation_code")
        first_message_id = request.data.get("first_message_id")
        from_email = request.data.get("from_email")
        
        # Validate required fields
        if not to_email:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "to_email is required",
                    "error_code": "MISSING_TO_EMAIL"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Note: body is still required for Gmail API but not stored in our model
        if not body:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "body is required",
                    "error_code": "MISSING_BODY"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not from_email:
            return Response(
                {
                    "error": "Missing required field",
                    "message": "from_email is required",
                    "error_code": "MISSING_FROM_EMAIL"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if Gmail is connected for the sender email
        try:
            cred = GmailCredential.objects.get(system_email=from_email)
        except GmailCredential.DoesNotExist:
            return Response(
                {
                    "error": "Gmail not connected",
                    "message": f"Gmail account {from_email} is not connected. Please connect your Gmail account first.",
                    "error_code": "GMAIL_NOT_CONNECTED",
                    "connected": False,
                    "action": "connect_first"
                },
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Create EmailMessage record
        
        
        email_message = EmailMessage.objects.create(
            to_email=to_email,
            thread_id=thread_id,
            conversation_id=conversation_id,
            conversation_code=conversation_code,
            first_message_id=first_message_id,
            user_id=request.user.id,
            from_email=from_email,
            status='pending',
            type_based_id= "direct_mail_test"
        )
        
        try:
            # Send email via Gmail API
            logger.info(f"Sending email from {from_email} to {to_email}")
            gmail_response = svc.send_email(
                credential=cred,
                to_email=to_email,
                subject=subject,
                body=body,
                thread_id=thread_id
            )
            
            # Update EmailMessage with success details
            email_message.status = 'sent'
            email_message.gmail_message_id = gmail_response.get('id')
            email_message.gmail_thread_id = gmail_response.get('threadId')
            email_message.sent_at = timezone.now()
            email_message.save()
            
            logger.info(f"Email sent successfully. Message ID: {email_message.gmail_message_id}")
            
            return Response(
                {
                    "message": "Email sent successfully",
                    "email_message_id": email_message.id,
                    "gmail_message_id": email_message.gmail_message_id,
                    "gmail_thread_id": email_message.gmail_thread_id,
                    "to_email": to_email,
                    "from_email": from_email,
                    "subject": subject,
                    "is_reply": bool(thread_id),
                    "first_message_id": email_message.first_message_id,
                    "sent_at": email_message.sent_at.isoformat() if email_message.sent_at else None
                },
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            # Update EmailMessage with error details
            email_message.status = 'failed'
            email_message.error_message = str(e)
            email_message.save()
            
            logger.error(f"Failed to send email: {str(e)}")
            return Response(
                {
                    "error": "Failed to send email",
                    "message": "An error occurred while sending the email",
                    "error_code": "EMAIL_SEND_FAILED",
                    "details": str(e),
                    "email_message_id": email_message.id
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Unexpected error in send_email: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while sending email",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def email_history(request):
    """
    Get email message history for the authenticated user.
    
    Query parameters:
    - email: Filter by sender email (optional)
    - status: Filter by status (pending, sent, failed, draft) (optional)
    - limit: Number of records to return (default: 20, max: 100)
    """
    try:
        from envoy.models.mail_model import EmailMessage
        
        # Get query parameters
        email = request.query_params.get("email")
        status = request.query_params.get("status")
        limit = request.query_params.get("limit", 20)
        
        # Validate limit
        try:
            limit = int(limit)
            if limit <= 0 or limit > 100:
                limit = 20
        except ValueError:
            limit = 20
        
        # Build query
        queryset = EmailMessage.objects.filter(user_id=request.user.id)
        
        if email:
            queryset = queryset.filter(from_email=email)
        
        if status:
            queryset = queryset.filter(status=status)
        
        # Get results
        email_messages = queryset.order_by('-created_at')[:limit]
        
        # Prepare response data
        messages = []
        for msg in email_messages:
            messages.append({
                "id": msg.id,
                "to_email": msg.to_email,
                "from_email": msg.from_email,
                "thread_id": msg.thread_id,
                "conversation_id": msg.conversation_id,
                "conversation_code": msg.conversation_code,
                "first_message_id": msg.first_message_id,
                "status": msg.status,
                "gmail_message_id": msg.gmail_message_id,
                "gmail_thread_id": msg.gmail_thread_id,
                "created_at": msg.created_at.isoformat(),
                "sent_at": msg.sent_at.isoformat() if msg.sent_at else None,
                "error_message": msg.error_message,
                "retry_count": msg.retry_count
            })
        
        return Response(
            {
                "message": "Email history retrieved successfully",
                "total_messages": len(messages),
                "user_id": request.user.id,
                "filters": {
                    "email": email,
                    "status": status,
                    "limit": limit
                },
                "messages": messages
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error in email_history: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving email history",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(e)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
import base64
import hashlib
import logging
import re
from datetime import datetime, timezone as dt_timezone
from typing import Optional ,Tuple
from envoy.services.email_service import (
    get_thread_messages,
    get_message_details,
    search_messages_by_conversation,
)

logger = logging.getLogger(__name__)


def _norm_addr(s: Optional[str]) -> str:
    if not s:
        return ""
    s = s.strip()
    if "<" in s and ">" in s:
        s = s[s.find("<") + 1 : s.find(">")]
    return s.strip().lower()


def _fingerprint(msg: dict) -> str:
    frm = _norm_addr(msg.get("from_email"))
    to = _norm_addr(msg.get("to_email"))
    subject = (msg.get("subject") or "").strip().lower()
    body_snip = (msg.get("body") or "")[:200].strip()
    basis = f"{frm}|{to}|{subject}|{body_snip}"
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()


def _ms_to_iso(ms_str: Optional[str]) -> Optional[str]:
    if not ms_str:
        return None
    try:
        ms = int(ms_str)
        return datetime.utcfromtimestamp(ms / 1000).replace(tzinfo=dt_timezone.utc).isoformat()
    except Exception:
        return str(ms_str)


def _parse_dt_for_sort(ts: Optional[str]) -> float:
    if not ts:
        return 0.0
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except Exception:
        pass
    try:
        return int(ts) / 1000.0
    except Exception:
        return 0.0


def _header_get(headers: list, name: str, default: str = "") -> str:
    return next((h["value"] for h in headers if h.get("name", "").lower() == name.lower()), default)


# --- new: clean latest reply and capture "On ... wrote:" time -------------
# More comprehensive regex to match various "On ... wrote:" formats
_REPLY_BREAK_RE = re.compile(r"(?mi)^\s*On .+?wrote:\s*$|^.*On .+?wrote:\s*$")
# captures like: "On Sat, Aug 9, 2025, 12:37 AM" and variations
_REPLY_TIME_CAPTURE_RE = re.compile(r"(?mi)^\s*(On\s+.+?),?\s+wrote:\s*$|^.*(On\s+.+?),?\s+wrote:\s*$")

from typing import Tuple, Optional

def _extract_reply_and_time(raw_text: str) -> Tuple[str, Optional[str]]:
    """
    Extract latest reply (before quoted 'On ... wrote:' block) and mess_time.
    - Handles inline "On ... wrote:" on same line
    - Drops lines starting with '>'
    - Normalizes weird Unicode spaces from Gmail (e.g., narrow no-break space)
    - Returns (clean_one_line_body, mess_time or None)
    """
    if not raw_text:
        return "", None

    # Normalize newlines + normalize Unicode spaces Gmail likes to use
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    text = (
        text
        .replace("\u00A0", " ")  # NO-BREAK SPACE
        .replace("\u202F", " ")  # NARROW NO-BREAK SPACE
        .replace("\u2009", " ")  # THIN SPACE (just in case)
    )

    # Remove fully quoted lines starting with '>'
    lines = [ln for ln in text.split("\n") if not ln.lstrip().startswith(">")]
    text = "\n".join(lines)

    # Find the first "On ... wrote:" anywhere (case-insensitive, dot matches newline)
    # We capture the middle part so we can compute a clean mess_time.
    m = re.search(r'(?is)\bOn\s+(?P<meta>.+?)\s*wrote:', text)
    mess_time: Optional[str] = None

    if m:
        # Body is everything BEFORE the quoted marker
        body_part = text[:m.start()]
        # Clean body: single spaces, trim; keep emojis as-is
        body = re.sub(r'[ \t]+', ' ', body_part.replace("\n", " ")).strip()

        # Build a cleaner mess_time from meta
        meta = m.group("meta")
        # Remove bracketed email if present
        meta = re.sub(r'<[^>]+>', '', meta).strip()
        # Collapse whitespace
        meta = re.sub(r'\s+', ' ', meta).strip()

        # Try to cut at the end of the time token, e.g., "12:59 PM"
        # Handle AM/PM with optional Unicode space
        ampm_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', meta, flags=re.I)
        if ampm_match:
            meta = meta[:ampm_match.end()].strip()
        else:
            # Fallback: a 24h time like "13:45"
            h24 = re.search(r'(\b\d{1,2}:\d{2}\b)', meta)
            if h24:
                meta = meta[:h24.end()].strip()
            # else: leave meta as-is (date-only)

        mess_time = f"On {meta}" if meta else None
        return body, mess_time

    # No quoted marker found → return cleaned original as body, no mess_time
    body = re.sub(r'[ \t]+', ' ', text.replace("\n", " ")).strip()
    return body, None

# -------------------------------------------------------------------------
from email.utils import getaddresses
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def email_thread_replies(request):
    """
    Get all email replies from a particular message thread using conversation_code.
    Fetches both local DB and Gmail API messages, de-dupes, and cleans bodies.
    Also syncs missing messages to external chat app when conversation_id is available.
    """

    # -------------------- helpers --------------------
    def _normalize_emails(value):
        """Return a set of lowercase bare emails from an address header/string."""
        if not value:
            return set()
        return {addr.lower() for _, addr in getaddresses([value]) if addr}

    def _classify_status(from_val, to_like_val, identity_emails):
        """
        sent:     if From ∈ identity
        received: if any(To/Cc/Delivered-To) ∈ identity and From ∉ identity
        unknown:  otherwise
        """
        from_set = _normalize_emails(from_val)
        to_set   = _normalize_emails(to_like_val)
        if from_set & identity_emails:
            return "sent"
        if to_set & identity_emails:
            return "received"
        return "unknown"

    def _extract_clean_body_and_time(md):
        """
        Given a Gmail message detail `md`, return (clean_body, mess_time).
        Uses your existing _extract_reply_and_time(body_text).
        """
        import base64, re, html

        payload = md.get("payload", {})
        body_text = ""

        def decode_body_data(data):
            try:
                return base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
            except UnicodeDecodeError:
                try:
                    return base64.urlsafe_b64decode(data).decode("latin-1", errors="replace")
                except Exception:
                    return str(base64.urlsafe_b64decode(data), errors="replace")

        # Prefer text/plain; fallback to text/html
        if payload.get("body", {}).get("data"):
            body_text = decode_body_data(payload["body"]["data"])
        elif "parts" in payload:
            for part in payload.get("parts", []):
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    body_text = decode_body_data(part["body"]["data"])
                    break
            if not body_text:
                for part in payload.get("parts", []):
                    if part.get("mimeType") == "text/html" and part.get("body", {}).get("data"):
                        html_text = decode_body_data(part["body"]["data"])
                        html_text = html.unescape(html_text)
                        body_text = re.sub(r"<[^>]+>", "", html_text)
                        body_text = re.sub(r"\s+", " ", body_text).strip()
                        break

        clean_body, mess_time = _extract_reply_and_time(body_text)
        return clean_body, mess_time

    # ---- Chat API config + auth helpers
    CHAT_API_BASE = getattr(settings, "CHAT_API_BASE", "https://dev-chat-app.apptimus.lk/api")

    def _redact_token(tok: str) -> str:
        if not tok:
            return ""
        if len(tok) <= 10:
            return tok[:2] + "…"
        return tok[:4] + "…" + tok[-4:]

    def _get_chat_token(req):
        # 1) query param
        qp = req.query_params.get("idp_access_token")
        if qp:
            return qp.strip()
        # 2) Authorization header from caller
        auth = req.META.get("HTTP_AUTHORIZATION") or req.headers.get("Authorization")
        if auth and auth.lower().startswith("bearer "):
            return auth.split(" ", 1)[1].strip()
        # 3) settings fallback
        return getattr(settings, "CHAT_API_TOKEN", None)

    def _chat_headers(token: str):
        h = {"Accept": "application/json", "Content-Type": "application/json"}
        if token:
            h["Authorization"] = f"Bearer {token}"
        return h

    try:
        conversation_code = request.query_params.get("conversation_code")
        limit = request.query_params.get("limit", 50)
        include_gmail_data = request.query_params.get("include_gmail_data", "false").lower() == "true"
        include_gmail_messages = request.query_params.get("include_gmail_messages", "true").lower() == "true"

        if not conversation_code:
            return Response(
                {
                    "error": "Missing required parameter",
                    "message": "conversation_code parameter is required",
                    "error_code": "MISSING_PARAMETER",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            limit = int(limit)
            if limit <= 0 or limit > 200:
                limit = 50
        except ValueError:
            limit = 50

        queryset = (
            EmailMessage.objects.filter(conversation_code=conversation_code, user_id=request.user.id)
            .order_by("created_at")
        )

        messages = []
        gmail_messages = []
        thread_ids = set()

        # conversation_id and thread-level first_message_id from DB
        conversation_id = (
            queryset.exclude(conversation_id__isnull=True)
            .values_list("conversation_id", flat=True)
            .first()
        )
        logger.info(f"[chat-sync] conversation_id for code {conversation_code}: {conversation_id}")

        thread_first_message_id = (
            queryset.exclude(first_message_id__isnull=True)
            .values_list("first_message_id", flat=True)
            .first()
        )

        # identity emails for local classification
        identity_local = set()
        user_email = getattr(request.user, "email", None)
        if user_email:
            identity_local.add(user_email.lower())

        # ---- Local messages
        failed_messages = []
        for msg in queryset:
            computed_status = _classify_status(
                getattr(msg, "from_email", None),
                getattr(msg, "to_email", None),
                identity_local,
            )
            final_status = computed_status if computed_status != "unknown" else (getattr(msg, "status", None) or "unknown")

            message_data = {
                "id": msg.id,
                "to_email": getattr(msg, "to_email", None),
                "from_email": getattr(msg, "from_email", None),
                "thread_id": getattr(msg, "thread_id", "") or "",
                "conversation_id": getattr(msg, "conversation_id", None),
                "conversation_code": msg.conversation_code,
                "first_message_id": getattr(msg, "first_message_id", None),
                "status": final_status,
                "created_at": (msg.created_at.isoformat() if getattr(msg, "created_at", None) else None),
                "sent_at": (msg.sent_at.isoformat() if getattr(msg, "sent_at", None) else None),
                "error_message": getattr(msg, "error_message", None),
                "retry_count": getattr(msg, "retry_count", 0),
                "source": "local_database",
                "body": getattr(msg, "body", None) or getattr(msg, "message", None) or "",
                "attachments": [],  # Add empty attachments array for local messages
                "attachment_images": [],  # Add empty attachment_images array for local messages
            }

            gmail_msg_id = getattr(msg, "gmail_message_id", None)
            gmail_thread_id = getattr(msg, "gmail_thread_id", None)
            if include_gmail_data:
                message_data.update(
                    {
                        "gmail_message_id": gmail_msg_id,
                        "gmail_thread_id": gmail_thread_id,
                    }
                )

            if message_data["status"] == 'failed':
                failed_messages.append(message_data)
            else:
                messages.append(message_data)

            if gmail_thread_id:
                thread_ids.add(gmail_thread_id)
                logger.info(f"Added thread_id: {gmail_thread_id} from local message {msg.id}")

        # ---- Gmail API messages
        if include_gmail_messages:
            try:
                gmail_credentials = GmailCredential.objects.all()
                logger.info(f"Found {gmail_credentials.count()} Gmail credentials")
                
                if gmail_credentials.exists():
                    credential = gmail_credentials.first()
                    logger.info(f"Using Gmail credential for: {credential.system_email}")
                    logger.info(f"Thread IDs to fetch: {thread_ids}")

                    identity_gmail = {str(credential.system_email).lower()} if getattr(credential, "system_email", None) else set()

                    # 1) From known thread IDs
                    for thread_id in thread_ids:
                        try:
                            logger.info(f"Fetching Gmail thread: {thread_id}")
                            thread_data = get_thread_messages(credential, thread_id)
                            logger.info(f"Found {len(thread_data.get('messages', []))} messages in thread {thread_id}")
                            for gm in thread_data.get("messages", []):
                                try:
                                    md = get_message_details(credential, gm["id"])
                                    headers = md.get("payload", {}).get("headers", [])
                                    subject = _header_get(headers, "Subject", "")
                                    from_header = _header_get(headers, "From", "")
                                    to_header = _header_get(headers, "To", "")
                                    cc_header = _header_get(headers, "Cc", "")
                                    delivered_to = _header_get(headers, "Delivered-To", "")
                                    internet_message_id = _header_get(headers, "Message-Id", "").strip() or None

                                    clean_body, mess_time = _extract_clean_body_and_time(md)
                                    to_like = ", ".join([h for h in [to_header, cc_header, delivered_to] if h])
                                    status_val = _classify_status(from_header, to_like, identity_gmail)
                                    iso_ts = _ms_to_iso(md.get("internalDate"))

                                    gmail_messages.append({
                                         "id": f"gmail_{gm['id']}",
                                         "to_email": to_header,
                                         "from_email": from_header,
                                         "subject": subject,
                                         "body": clean_body,
                                         "mess_time": mess_time,
                                         "thread_id": thread_id,
                                         "conversation_id": None,
                                         "conversation_code": conversation_code,
                                         "status": status_val,
                                         "created_at": iso_ts,
                                         "sent_at": iso_ts,
                                         "error_message": None,
                                         "retry_count": 0,
                                         "source": "gmail_api",
                                         "gmail_message_id": gm["id"],
                                         "gmail_thread_id": thread_id,
                                         "internet_message_id": internet_message_id,
                                         "first_message_id": thread_first_message_id,
                                         "attachments": [],  # Add empty attachments array for Gmail messages
                                         "attachment_images": [],  # Add empty attachment_images array for Gmail messages
                                     })
                                except Exception as e:
                                    logger.warning(f"Error parsing Gmail message {gm.get('id')}: {e}")
                                    continue
                        except Exception as e:
                            logger.warning(f"Error fetching Gmail thread {thread_id}: {e}")
                            continue

                    # 2) Search by conversation code
                    try:
                        logger.info(f"Searching Gmail for conversation code: {conversation_code}")
                        search_results = search_messages_by_conversation(credential, conversation_code, max_results=20)
                        logger.info(f"Found {len(search_results.get('messages', []))} messages by conversation search")
                        for gm in search_results.get("messages", []):
                            try:
                                md = get_message_details(credential, gm["id"])
                                headers = md.get("payload", {}).get("headers", [])
                                subject = _header_get(headers, "Subject", "")
                                from_header = _header_get(headers, "From", "")
                                to_header = _header_get(headers, "To", "")
                                cc_header = _header_get(headers, "Cc", "")
                                delivered_to = _header_get(headers, "Delivered-To", "")
                                internet_message_id = _header_get(headers, "Message-Id", "").strip() or None

                                clean_body, mess_time = _extract_clean_body_and_time(md)
                                to_like = ", ".join([h for h in [to_header, cc_header, delivered_to] if h])
                                status_val = _classify_status(from_header, to_like, identity_gmail)
                                iso_ts = _ms_to_iso(md.get("internalDate"))

                                gmail_messages.append({
                                    "id": f"gmail_{gm['id']}",
                                    "to_email": to_header,
                                    "from_email": from_header,
                                    "subject": subject,
                                    "body": clean_body,
                                    "mess_time": mess_time,
                                    "thread_id": gm.get("threadId"),
                                    "conversation_id": None,
                                    "conversation_code": conversation_code,
                                    "status": status_val,
                                    "created_at": iso_ts,
                                    "sent_at": iso_ts,
                                    "error_message": None,
                                    "retry_count": 0,
                                    "source": "gmail_api_search",
                                    "gmail_message_id": gm["id"],
                                    "gmail_thread_id": gm.get("threadId"),
                                    "internet_message_id": internet_message_id,
                                    "first_message_id": thread_first_message_id,
                                    "attachments": [],  # Add empty attachments array for Gmail search messages
                                    "attachment_images": [],  # Add empty attachment_images array for Gmail search messages
                                })
                            except Exception as e:
                                logger.warning(f"Error parsing searched Gmail message {gm.get('id')}: {e}")
                                continue
                    except Exception as e:
                        logger.warning(f"Error searching Gmail messages for conversation {conversation_code}: {e}")
                        
                    # 3) Fallback search by thread IDs
                    if not gmail_messages and thread_ids:
                        logger.info("No messages found by conversation code, trying thread ID search")
                        for thread_id in thread_ids:
                            try:
                                params = {"q": f"threadId:{thread_id}", "maxResults": 20}
                                r = requests.get(
                                    "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                                    headers={"Authorization": f"Bearer {credential.access_token}"},
                                    params=params,
                                    timeout=30
                                )
                                r.raise_for_status()
                                data = r.json()
                                messages_found = data.get('messages', [])
                                logger.info(f"Found {len(messages_found)} messages for thread ID {thread_id}")
                                
                                for gm in messages_found:
                                    try:
                                        md = get_message_details(credential, gm["id"])
                                        headers = md.get("payload", {}).get("headers", [])
                                        subject = _header_get(headers, "Subject", "")
                                        from_header = _header_get(headers, "From", "")
                                        to_header = _header_get(headers, "To", "")
                                        cc_header = _header_get(headers, "Cc", "")
                                        delivered_to = _header_get(headers, "Delivered-To", "")
                                        internet_message_id = _header_get(headers, "Message-Id", "").strip() or None

                                        clean_body, mess_time = _extract_clean_body_and_time(md)
                                        to_like = ", ".join([h for h in [to_header, cc_header, delivered_to] if h])
                                        status_val = _classify_status(from_header, to_like, identity_gmail)
                                        iso_ts = _ms_to_iso(md.get("internalDate"))

                                        gmail_messages.append({
                                            "id": f"gmail_{gm['id']}",
                                            "to_email": to_header,
                                            "from_email": from_header,
                                            "subject": subject,
                                            "body": clean_body,
                                            "mess_time": mess_time,
                                            "thread_id": thread_id,
                                            "conversation_id": None,
                                            "conversation_code": conversation_code,
                                            "status": status_val,
                                            "created_at": iso_ts,
                                            "sent_at": iso_ts,
                                            "error_message": None,
                                            "retry_count": 0,
                                            "source": "gmail_api_thread_search",
                                            "gmail_message_id": gm["id"],
                                            "gmail_thread_id": thread_id,
                                            "internet_message_id": internet_message_id,
                                            "first_message_id": thread_first_message_id,
                                            "attachments": [],  # Add empty attachments array for Gmail thread search messages
                                            "attachment_images": [],  # Add empty attachment_images array for Gmail thread search messages
                                        })
                                    except Exception as e:
                                        logger.warning(f"Error parsing Gmail message {gm.get('id')}: {e}")
                                        continue
                            except Exception as e:
                                logger.warning(f"Error searching Gmail for thread ID {thread_id}: {e}")
                                continue
            except Exception as e:
                logger.warning(f"Error fetching Gmail messages: {e}")

        # ---- Combine & De-duplicate
        logger.info(f"Local messages found: {len(messages)}")
        logger.info(f"Gmail API messages found: {len(gmail_messages)}")
        
        gmail_ids = {gm.get("gmail_message_id") for gm in gmail_messages if gm.get("gmail_message_id")}
        gmail_imids = {gm.get("internet_message_id") for gm in gmail_messages if gm.get("internet_message_id")}
        gmail_fps = {_fingerprint(gm) for gm in gmail_messages}

        unique_messages = []
        seen_keys = set()

        for m in gmail_messages:
            key = m.get("gmail_message_id") or m.get("internet_message_id") or _fingerprint(m)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_messages.append(m)

        for m in messages:
            key = m.get("gmail_message_id") or _fingerprint(m)
            if key not in seen_keys:
                seen_keys.add(key)
                unique_messages.append(m)

        logger.info(f"Total unique messages after deduplication: {len(unique_messages)}")

        if not unique_messages and failed_messages:
            logger.info("No successful messages found, including failed messages as fallback")
            unique_messages = failed_messages

        # -------------------- Chat sync (with token) --------------------
        chat_sync = {"attempted": 0, "posted": 0, "skipped_existing": 0, "errors": 0}
        existing_chat_texts = set()

        chat_token = _get_chat_token(request)
        if not chat_token:
            logger.warning("[chat-sync] Missing idp_access_token (query param/header/settings). Skipping chat fetch/post.")
        else:
            logger.info(f"[chat-sync] Using idp_access_token={_redact_token(chat_token)}")

            if conversation_id:
                # 1) Pull existing chat messages to de-dupe
                try:
                    url_get = f"{CHAT_API_BASE}/conversations/{conversation_id}/messages"
                    params = {"per_page": 200}
                    r = requests.get(url_get, headers=_chat_headers(chat_token), params=params, timeout=30)
                    r.raise_for_status()
                    resp_json = r.json() if r.content else {}
                    existing_list = ((resp_json or {}).get("data") or {}).get("data") or []
                    existing_chat_texts = {str(it.get("content", "")).strip() for it in existing_list if it.get("content")}
                    logger.info(f"[chat-sync] Existing chat messages fetched: {len(existing_chat_texts)}")
                except requests.HTTPError as e:
                    chat_sync["errors"] += 1
                    logger.warning(f"[chat-sync] Failed to fetch chat messages: {e}")
                except Exception as e:
                    chat_sync["errors"] += 1
                    logger.warning(f"[chat-sync] Exception fetching chat messages: {e}")

                # 2) Post any email messages not yet in chat
                url_post = f"{CHAT_API_BASE}/messages"
                for m in unique_messages:
                    text = (m.get("body") or "").strip()
                    if not text:
                        continue
                    chat_sync["attempted"] += 1

                    if text in existing_chat_texts:
                        chat_sync["skipped_existing"] += 1
                        continue

                    reply_msg_id = ""
                    if m.get("status") == "received":
                        reply_msg_id = m.get("first_message_id") or thread_first_message_id or ""

                    # Extract attachments from the message if available
                    attachments = ""
                    attachment_images = ""
                    
                    # Check if the message has attachment data
                    if isinstance(m, dict):
                        # Look for attachment fields in the message
                        msg_attachments = m.get("attachments", [])
                        msg_attachment_images = m.get("attachment_images", [])
                        
                        # For now, send empty strings to avoid format issues with external API
                        # TODO: Implement proper attachment handling if needed
                        if msg_attachments:
                            logger.info(f"[chat-sync] Message has {len(msg_attachments)} attachments, sending empty string to external API")
                        if msg_attachment_images:
                            logger.info(f"[chat-sync] Message has {len(msg_attachment_images)} attachment images, sending empty string to external API")
                    
                    payload = {
                        "msg": text,
                        "conversation_id": conversation_id,
                        "attachments": attachments,
                        "attachment_images": attachment_images,
                        "reply_msg_id": reply_msg_id,
                    }

                    try:
                        pr = requests.post(url_post, headers=_chat_headers(chat_token), json=payload, timeout=30)
                        if 200 <= pr.status_code < 300:
                            chat_sync["posted"] += 1
                            existing_chat_texts.add(text)
                        else:
                            chat_sync["errors"] += 1
                            logger.warning(f"[chat-sync] Failed to post message (status {pr.status_code}): {pr.text}")
                            if pr.status_code == 401:
                                break
                    except Exception as e:
                        chat_sync["errors"] += 1
                        logger.warning(f"[chat-sync] Exception while posting message: {e}")

        # ---- Sort & limit for API response
        unique_messages.sort(key=lambda x: _parse_dt_for_sort(x.get("created_at")))
        unique_messages = unique_messages[:limit]

        if not unique_messages:
            return Response(
                {
                    "error": "No messages found",
                    "message": f"No email messages found for conversation_code: {conversation_code}",
                    "error_code": "NO_MESSAGES_FOUND",
                    "conversation_code": conversation_code,
                    "conversation_id": conversation_id,
                    "chat_sync": chat_sync,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        # Count only non-failed messages for total
        total_messages = len([m for m in unique_messages if m.get("status") != "failed"])
        status_summary = {}
        for m in unique_messages:
            st = m.get("status", "unknown")
            status_summary[st] = status_summary.get(st, 0) + 1

        first_message = unique_messages[0]
        last_message = unique_messages[-1]

        return Response(
            {
                "message": "Email thread replies retrieved successfully",
                "conversation_code": conversation_code,
                "conversation_id": conversation_id,
                "conversation_summary": {
                    "total_messages": total_messages,
                    "status_summary": status_summary,
                    "first_message_date": first_message.get("created_at"),
                    "last_message_date": last_message.get("created_at"),
                    "conversation_duration_days": 0,
                },
                "filters": {
                    "conversation_code": conversation_code,
                    "limit": limit,
                    "include_gmail_data": include_gmail_data,
                    "include_gmail_messages": include_gmail_messages,
                },
                "sources": {
                    "local_database_count": len(messages),
                    "local_database_failed_count": len(failed_messages),
                    "gmail_api_count": len(gmail_messages),
                    "total_unique_count": len(unique_messages),
                },
                "chat_sync": chat_sync,
                "messages": unique_messages,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error in email_thread_replies: {str(e)}", exc_info=True)
        return Response(
            {
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving email thread replies",
                "error_code": "INTERNAL_SERVER_ERROR",
                "details": str(e),
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_message(request):
    """
    Send message via external chat API and then send email via Gmail.

    Body:
      body (req), subject (opt), to_mail (req unless derived), conversation_id (opt),
      from_email (opt -> will default from core_gmailcredential), idp_access_token (from header),
      type_based_id (opt), insurer_id (opt)
    """
    def _norm_str(val):
        if val is None:
            return None
        if isinstance(val, str):
            s = val.strip()
            return s or None
        return str(val)

    try:
        # prefer Authorization header over body
        idp_access_token = get_bearer_token(request)

        body = request.data.get("body")
        subject = _norm_str(request.data.get("subject", ""))
        to_mail = _norm_str(request.data.get("to_mail"))
        from_email = _norm_str(request.data.get("from_email"))
        type_based_id = request.data.get("type_based_id", None)
        conversation_id = _norm_str(request.data.get("conversation_id"))
        insurer_id = request.data.get("insurer_id", None)
        
        # Handle attachments
        attachments = request.data.get("attachments", [])
        attachment_images = request.data.get("attachment_images", [])
        
        # Validate and clean attachments format
        if not isinstance(attachments, list):
            attachments = []
        if not isinstance(attachment_images, list):
            attachment_images = []
            
        # For external API, we need to send empty strings if no valid attachments
        # The external API expects either files or empty strings, not attachment objects
        external_attachments = ""
        external_attachment_images = ""
        
        # Only set attachments if we have valid ones (the API will handle the validation)
        if attachments and len(attachments) > 0:
            # For now, send empty string to avoid format issues
            # TODO: Implement proper file upload handling if needed
            external_attachments = ""
            logger.info(f"Attachments provided but sending empty string to external API: {len(attachments)} items")
        
        if attachment_images and len(attachment_images) > 0:
            # For now, send empty string to avoid format issues
            # TODO: Implement proper file upload handling if needed
            external_attachment_images = ""
            logger.info(f"Attachment images provided but sending empty string to external API: {len(attachment_images)} items")
        
        # Use the processed values for external API calls
        attachments_for_external = external_attachments
        attachment_images_for_external = external_attachment_images

        # ----- NEW: fallback to default shared mailbox if from_email is missing -----
        if not from_email:
            try:
                gmail_credential_row = (
                    QueryBuilderService("core_gmailcredential")
                    .select("system_email")
                    .orderBy("id", "asc")
                    .first()
                )
                if gmail_credential_row and gmail_credential_row.get("system_email"):
                    from_email = gmail_credential_row["system_email"]
                    print(f"[send_message] Using default from_email: {from_email}")
                    logger.info(f"[send_message] Using default from_email from core_gmailcredential: {from_email}")
            except Exception as e:
                logger.warning(f"[send_message] Could not load default system_email: {e}")

        # validations
        if not body:
            return Response(
                {"error": "Missing required field", "message": "body is required", "error_code": "MISSING_BODY"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not idp_access_token:
            return Response(
                {"error": "Missing required field", "message": "idp_access_token is required for external API authentication", "error_code": "MISSING_IDP_ACCESS_TOKEN"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # If conversation_id is provided, try to derive addresses when missing
        if conversation_id:
            try:
                latest_email = (
                    EmailMessage.objects
                    .filter(conversation_id=conversation_id)
                    .order_by("-sent_at", "-created_at")
                    .first()
                )
                if latest_email:
                    # Derive to_mail if still missing
                    if not to_mail:
                        to_mail = latest_email.to_email
                        logger.info(f"[send_message] Derived to_mail '{to_mail}' from conversation_id {conversation_id}")
                    # Only derive from_email if STILL missing (we prefer the default shared mailbox)
                    if not from_email:
                        from_email = latest_email.from_email
                        logger.info(f"[send_message] Derived from_email '{from_email}' from conversation_id {conversation_id}")
                else:
                    logger.warning(f"[send_message] No EmailMessage found for conversation_id {conversation_id}")
            except Exception as e:
                logger.error(f"[send_message] Error deriving emails for conversation_id={conversation_id}: {e}")

        # Validate we at least have a recipient
        if not to_mail:
            return Response(
                {"error": "Missing required field", "message": "to_mail is required (not provided and could not be derived from conversation_id)", "error_code": "MISSING_TO_MAIL"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # At this point, from_email may still be None if there is no default credential configured.
        # We won't fail here; the GmailCredential lookup will give a clear 401 if not connected.

        current_user = request.user
        if not getattr(current_user, "idp_user_id", None):
            return Response(
                {"error": "User not configured", "message": "Current user does not have idp_user_id configured", "error_code": "USER_NOT_CONFIGURED"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        external_headers = {
            "Authorization": f"Bearer {idp_access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Envoy-BU-Core-API/1.0",
        }

        # ==============================
        # A) Existing conversation flow
        # ==============================
        if conversation_id:
            # 1) Send chat message to existing conversation (no group creation)
            conv_for_api = int(conversation_id) if conversation_id.isdigit() else conversation_id
            msg_payload = {
                "msg": body,
                "conversation_id": conv_for_api,
                "attachments": attachments_for_external,
                "attachment_images": attachment_images_for_external,
                "reply_msg_id": "",
            }
            
            logger.info(f"[send_message] Sending to external API - conversation_id: {conv_for_api}, attachments_count: {len(attachments)}, attachment_images_count: {len(attachment_images)}")
            try:
                r = requests.post(
                    "https://dev-chat-app.apptimus.lk/api/messages",
                    json=msg_payload,
                    headers=external_headers,
                    timeout=30,
                )
                r.raise_for_status()
                msg_data = r.json()
                if not msg_data.get("success"):
                    return Response(
                        {
                            "error": "Message sending failed",
                            "message": msg_data.get("msg", "Unknown error"),
                            "error_code": "MESSAGE_SENDING_FAILED",
                            "external_response": msg_data,
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
                first_message_id = (msg_data.get("data") or {}).get("id")
            except requests.exceptions.RequestException as e:
                logger.error(f"[send_message] Chat send failed: {e}")
                error_details = f"Failed to send message: {e}"
                
                # Add more details for specific error codes
                if hasattr(e, 'response') and e.response is not None:
                    try:
                        error_response = e.response.json()
                        error_details += f" - API Response: {error_response}"
                        logger.error(f"[send_message] External API error response: {error_response}")
                    except:
                        error_details += f" - Response text: {e.response.text}"
                        logger.error(f"[send_message] External API error response text: {e.response.text}")
                
                return Response(
                    {"error": "External API error", "message": error_details, "error_code": "EXTERNAL_API_ERROR"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # 2) Resolve Gmail thread_id from DB by conversation_id (prefer same from_email if available)
            try:
                q = (
                    EmailMessage.objects
                    .filter(conversation_id=conversation_id)
                    .exclude(gmail_thread_id__isnull=True)
                    .exclude(gmail_thread_id__exact="")
                )
                latest = (
                    q.filter(from_email=from_email).order_by("-sent_at", "-created_at").first()
                    if from_email else None
                ) or q.order_by("-sent_at", "-created_at").first()
                thread_id = latest.gmail_thread_id if latest else None
            except Exception as e:
                logger.error(f"[send_message] Thread lookup failed: {e}")
                thread_id = None

            if not thread_id:
                return Response(
                    {
                        "error": "THREAD_NOT_FOUND_FOR_CONVERSATION",
                        "message": "Could not resolve Gmail thread for this conversation_id. "
                                   "Ensure the conversation has a previously stored Gmail message.",
                        "error_code": "THREAD_NOT_FOUND_FOR_CONVERSATION",
                        "conversation_id": conversation_id,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # 3) Send email reply in the SAME Gmail thread (no DB insert on this path)
            try:
                if not from_email:
                    # still no sender? explicit 401 to guide setup
                    return Response(
                        {
                            "error": "Gmail not connected",
                            "message": "No default sender configured. Please add a row in core_gmailcredential.",
                            "error_code": "GMAIL_NOT_CONNECTED",
                            "connected": False,
                            "action": "connect_first",
                            "group_created": False,
                            "message_sent": True,
                            "conversation_id": conversation_id,
                            "first_message_id": first_message_id,
                        },
                        status=status.HTTP_401_UNAUTHORIZED,
                    )

                cred = GmailCredential.objects.get(system_email=from_email)
            except GmailCredential.DoesNotExist:
                return Response(
                    {
                        "error": "Gmail not connected",
                        "message": f"Gmail account {from_email or '(unset)'} is not connected. Please connect your Gmail account first.",
                        "error_code": "GMAIL_NOT_CONNECTED",
                        "connected": False,
                        "action": "connect_first",
                        "group_created": False,
                        "message_sent": True,
                        "conversation_id": conversation_id,
                        "first_message_id": first_message_id,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            try:
                gmail_res = svc.send_email(
                    credential=cred,
                    to_email=to_mail,
                    subject=subject or "",
                    body=body,
                    thread_id=thread_id,  # reply
                    attachments=attachments,  # Use original attachments for Gmail
                )
                return Response(
                    {
                        "success": True,
                        "message": "Message and reply email sent successfully (existing conversation).",
                        "data": {
                            "mode": "reply_existing",
                            "conversation_id": conversation_id,
                            "first_message_id": first_message_id,
                            "gmail_message_id": gmail_res.get("id"),
                            "gmail_thread_id": gmail_res.get("threadId"),
                            "sent_at": timezone.now().isoformat(),
                            "thread_id_used": thread_id,
                            "message_data": msg_data.get("data"),
                            "from_email": from_email,
                            "to_mail": to_mail,
                        },
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                logger.error(f"[send_message] Gmail reply failed: {e}")
                return Response(
                    {
                        "error": "EMAIL_SENDING_FAILED",
                        "message": f"Failed to send email via Gmail API: {e}",
                        "error_code": "EMAIL_SENDING_FAILED",
                        "group_created": False,
                        "message_sent": True,
                        "conversation_id": conversation_id,
                        "first_message_id": first_message_id,
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        # ==========================
        # B) New conversation flow
        # ==========================
        group_title = subject or "New Message Group"
        group_payload = {"title": group_title, "user_ids": []}

        try:
            g = requests.post(
                "https://dev-chat-app.apptimus.lk/api/group/stroe",
                json=group_payload,
                headers=external_headers,
                timeout=30,
            )
            g.raise_for_status()
            group_data = g.json()
            if group_data.get("title") == "Title cannot be empty":
                return Response({"error": "Group creation failed", "message": "Title cannot be empty", "error_code": "EMPTY_TITLE"}, status=status.HTTP_400_BAD_REQUEST)
            if group_data.get("user_ids") == "List of Users need to be provided":
                return Response({"error": "Group creation failed", "message": "List of Users need to be provided", "error_code": "EMPTY_USER_IDS"}, status=status.HTTP_400_BAD_REQUEST)
            if group_data.get("msg") != "Group has been added successfully":
                return Response({"error": "Group creation failed", "message": group_data.get("msg", "Unknown error"), "error_code": "GROUP_CREATION_FAILED", "external_response": group_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            conversation_id_created = (group_data.get("data") or {}).get("conversation_id")
            if not conversation_id_created:
                return Response({"error": "Group creation failed", "message": "No conversation_id received from group creation", "error_code": "NO_CONVERSATION_ID"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            conversation_code = (group_data.get("data") or {}).get("gsid", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"[send_message] Group create failed: {e}")
            return Response({"error": "External API error", "message": f"Failed to create group: {e}", "error_code": "EXTERNAL_API_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # send chat message
        try:
            msg_payload = {
                "msg": body, 
                "conversation_id": conversation_id_created, 
                "attachments": attachments_for_external, 
                "attachment_images": attachment_images_for_external, 
                "reply_msg_id": ""
            }
            
            logger.info(f"[send_message] Sending to external API (new conversation) - conversation_id: {conversation_id_created}, attachments_count: {len(attachments)}, attachment_images_count: {len(attachment_images)}")
            
            mr = requests.post(
                "https://dev-chat-app.apptimus.lk/api/messages",
                json=msg_payload,
                headers=external_headers,
                timeout=30,
            )
            mr.raise_for_status()
            message_data = mr.json()
            if not message_data.get("success"):
                return Response({"error": "Message sending failed", "message": message_data.get("msg", "Unknown error"), "error_code": "MESSAGE_SENDING_FAILED"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            first_message_id = (message_data.get("data") or {}).get("id")
            if not first_message_id:
                return Response({"error": "Message sending failed", "message": "No message ID received from message sending", "error_code": "NO_MESSAGE_ID"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.RequestException as e:
            logger.error(f"[send_message] Chat send failed: {e}")
            error_details = f"Failed to send message: {e}"
            
            # Add more details for specific error codes
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_response = e.response.json()
                    error_details += f" - API Response: {error_response}"
                    logger.error(f"[send_message] External API error response: {error_response}")
                except:
                    error_details += f" - Response text: {e.response.text}"
                    logger.error(f"[send_message] External API error response text: {e.response.text}")
            
            return Response({"error": "External API error", "message": error_details, "error_code": "EXTERNAL_API_ERROR"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # send email and store row
        try:
            if not from_email:
                return Response(
                    {
                        "error": "Gmail not connected",
                        "message": "No default sender configured. Please add a row in core_gmailcredential.",
                        "error_code": "GMAIL_NOT_CONNECTED",
                        "connected": False,
                        "action": "connect_first",
                        "group_created": True,
                        "message_sent": True,
                        "conversation_id": conversation_id_created,
                        "first_message_id": first_message_id,
                    },
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            cred = GmailCredential.objects.get(system_email=from_email)
        except GmailCredential.DoesNotExist:
            return Response(
                {
                    "error": "Gmail not connected",
                    "message": f"Gmail account {from_email} is not connected. Please connect your Gmail account first.",
                    "error_code": "GMAIL_NOT_CONNECTED",
                    "connected": False,
                    "action": "connect_first",
                    "group_created": True,
                    "message_sent": True,
                    "conversation_id": conversation_id_created,
                    "first_message_id": first_message_id,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            email_message = EmailMessage.objects.create(
                to_email=to_mail,
                thread_id=None,
                conversation_id=conversation_id_created,
                conversation_code=conversation_code or "",
                first_message_id=first_message_id,
                user_id=current_user.id,
                from_email=from_email,
                status="pending",
                type_based_id=type_based_id,
                insurer_id=insurer_id,
            )

            gmail_res = svc.send_email(
                credential=cred,
                to_email=to_mail,
                subject=subject or "",
                body=body,
                thread_id=None,  # new thread
                attachments=attachments,  # Use original attachments for Gmail
            )
            email_message.gmail_message_id = gmail_res.get("id")
            email_message.gmail_thread_id = gmail_res.get("threadId")
            email_message.sent_at = timezone.now()
            email_message.status = "sent"
            email_message.save()

            return Response(
                {
                    "success": True,
                    "message": "Message and email sent successfully (new conversation).",
                    "data": {
                        "mode": "new_conversation",
                        "conversation_id": conversation_id_created,
                        "first_message_id": first_message_id,
                        "conversation_code": conversation_code,
                        "gmail_message_id": email_message.gmail_message_id,
                        "gmail_thread_id": email_message.gmail_thread_id,
                        "sent_at": email_message.sent_at.isoformat() if email_message.sent_at else None,
                        "group_data": group_data.get("data"),
                        "message_data": message_data.get("data"),
                        "from_email": from_email,
                        "to_mail": to_mail,
                    },
                },
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            logger.error(f"[send_message] Gmail send failed: {e}")
            return Response(
                {
                    "error": "Email sending failed",
                    "message": f"Failed to send email via Gmail API: {e}",
                    "error_code": "EMAIL_SENDING_FAILED",
                    "group_created": True,
                    "message_sent": True,
                    "conversation_id": conversation_id_created,
                    "first_message_id": first_message_id,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    except Exception as e:
        logger.error(f"[send_message] Unexpected error: {e}", exc_info=True)
        return Response(
            {"error": "Internal server error", "message": f"An unexpected error occurred: {e}", "error_code": "INTERNAL_SERVER_ERROR"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quotation_thread_messages(request, quotation_id):
    """
    Get all thread messages for a specific quotation.
    Fetches all conversation_codes for the quotation and then gets thread replies for each.
    """
    try:
        # Construct the type_based_id format: QR-{quotation_id}
        type_based_id = f"QR-{quotation_id}"
        
        # Get all EmailMessage records for this quotation
        email_messages = EmailMessage.objects.filter(
            type_based_id=type_based_id
        ).values_list('conversation_code', flat=True).distinct()
        
        if not email_messages:
            return Response({
                "message": f"No email messages found for quotation {quotation_id}",
                "data": [],
                "quotation_id": quotation_id,
                "type_based_id": type_based_id
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get thread replies for each conversation_code by calling the function directly
        all_thread_replies = []
        
        for conversation_code in email_messages:
            if conversation_code:
                try:
                    logger.info(f"Processing thread-replies for conversation_code: {conversation_code}")
                    
                    # Create a mock request object for the email_thread_replies function
                    from django.test import RequestFactory
                    from django.contrib.auth.models import User
                    
                    # Create a mock request with the same user and query parameters
                    factory = RequestFactory()
                    mock_request = factory.get(f'/api/gmail/thread-replies?conversation_code={conversation_code}')
                    mock_request.user = request.user
                    mock_request.query_params = {'conversation_code': conversation_code}
                    
                    # Call the email_thread_replies function directly
                    from envoy.controllers.mail_controller import email_thread_replies
                    response = email_thread_replies(mock_request)
                    
                    if response.status_code == 200:
                        thread_data = response.data
                        
                        # Extract messages from the response
                        if isinstance(thread_data, dict) and 'messages' in thread_data:
                            messages = thread_data['messages']
                            # Add conversation_code to each message for reference
                            for message in messages:
                                message['conversation_code'] = conversation_code
                            all_thread_replies.extend(messages)
                        else:
                            logger.warning(f"Unexpected response format for conversation_code {conversation_code}: {thread_data}")
                    else:
                        logger.error(f"Thread-replies function returned status {response.status_code} for conversation_code {conversation_code}")
                        
                except Exception as e:
                    logger.error(f"Error processing thread-replies for conversation_code {conversation_code}: {str(e)}")
                    continue
        
        # Sort all messages by timestamp if available
        try:
            all_thread_replies.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        except:
            pass  # If sorting fails, keep original order
        
        return Response({
            "message": f"Successfully retrieved thread messages for quotation {quotation_id}",
            "data": all_thread_replies,
            "quotation_id": quotation_id,
            "type_based_id": type_based_id,
            "conversation_codes_found": list(email_messages),
            "total_messages": len(all_thread_replies)
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in quotation_thread_messages for quotation {quotation_id}: {str(e)}")
        return Response({
            "error": "Internal server error",
            "message": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
