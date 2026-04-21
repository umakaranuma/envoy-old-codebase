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

