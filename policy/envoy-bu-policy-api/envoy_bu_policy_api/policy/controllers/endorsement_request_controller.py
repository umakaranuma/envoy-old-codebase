# views.py
import re
import os
from urllib.parse import urlsplit
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response
import json
import requests
import math
import logging
from mServices import ResponseService, QueryBuilderService, ValidatorService
from core_models.core_models import EmailMessage
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from django.db.models import Max
from envoy_bu_policy_api.policy.models.crmp_endorsement_request import EndorsementRequest
from envoy_bu_policy_api.service import handle_entity, handle_entity_notes
from envoy_bu_policy_api.service import (
    send_approval_email_helper,
    get_recipient_email_by_customer_id,
)
from datetime import datetime, date
from decimal import Decimal


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
        "crmp_endorsement_reason_codes.code AS reason_code",
        "crmp_endorsement_reason_codes.description AS reason_code_description",
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
        # Indicate if this request has been processed (has corresponding endorsement detail)
        "CASE WHEN crmp_endorsements_details.id IS NOT NULL THEN 1 ELSE 0 END AS is_processed",
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
            "crmp_endorsement_reason_codes",
            "crmp_endorsement_reason_codes.id",
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
        .leftJoin(
            "crmp_endorsements_details",
            "crmp_endorsements_details.endorsement_request_id",
            "crmp_endorsement_requests.id",
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
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "entities.created_at" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    allowed_filters = [
        "crmp_endorsement_types.name",
        "crmp_endorsement_reason_codes.code",
    ]
    search_columns = [
        "crmp_endorsement_requests.remarks",
        "crmp_endorsement_requests.notes_or_details",
    ]
    sort_columns = [
        "entities.created_at",
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

    errors = ValidatorService.validate(data, get_endorsement_request_rules(data))
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)


    try:
        et = int(data.get("endorsement_type_id"))
    except (TypeError, ValueError):
        et = None
    if et not in (1, 2) and (str(data.get("cover_value", "")).strip() == ""):
        data["cover_value"] = 0

    entity_data = {"type": "policy", "approvel_status": False}
    user = request.user if request.user.is_authenticated else None
    entity_id = handle_entity(entity_data, entity_id=data.get("entity_id"), user=user)
    data["entity_id"] = entity_id
    data["mail_status"] = 0

    created = QueryBuilderService("crmp_endorsement_requests").insert(data)

    if data.get("remarks"):
        handle_entity_notes(entity_id, [{
            "note": data["remarks"],
            "created_by_id": request.user.id if request.user.is_authenticated else None,
            "created_at": datetime.now()
        }], is_update=False)

    # Update invoice status based on endorsement type
    try:
        update_invoice_status_based_on_endorsement(created.get("id"))
    except Exception as e:
        print(f"Error updating invoice status for endorsement request: {str(e)}")

    return ResponseService.response(
        "SUCCESS",
        get_all_endorsement_requests(request, request_id=created.get("id"), _created=True),
        "default_create_success_msg",
    )


def update_endorsement_request(request, request_id):
    data = json.loads(request.body or "{}")

    # ✅ Pass the payload so rules are conditional
    errors = ValidatorService.validate(data, get_endorsement_request_rules(data))
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # ✅ AFTER validation, default only when not type 1/2 and missing/blank
    try:
        et = int(data.get("endorsement_type_id"))
    except (TypeError, ValueError):
        et = None
    if et not in (1, 2) and (str(data.get("cover_value", "")).strip() == ""):
        data["cover_value"] = 0

    updated = QueryBuilderService("endorsement_request").where("id", request_id).update(data)
    if updated:
        return ResponseService.response("SUCCESS", updated, "default_update_success_msg")
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
def get_endorsement_request_rules(payload=None):
    rules = {
        "remarks": "string",
        "endorsement_type_id": "required|integer|exists:crmp_endorsement_types,id",
        "reason_code_id": "required|integer|exists:crmp_endorsement_reason_codes,id",
        "issued_policy_id": "required|integer|exists:crmp_issued_policies,id",
    }

    # default: optional numeric
    rules["cover_value"] = "numeric|min:0"

    # conditional: for type 1 or 2, make it required + numeric
    if payload:
        try:
            et = int(payload.get("endorsement_type_id"))
        except (TypeError, ValueError):
            et = None
        if et in (1, 2):
            rules["cover_value"] = "required|numeric|min:0"

    return rules



def generate_endorse_request_id():
    last = EndorsementRequest.objects.aggregate(Max("id"))["id__max"] or 0
    return f"EREQ-{last + 1}"


# --- small helpers (keep once in a utils module if you prefer) ---
def redact_token(token: str, keep: int = 6) -> str:
    if not token:
        return ""
    token = str(token)
    if len(token) <= keep:
        return "*" * len(token)
    return token[:keep] + "…" + "*" * max(0, len(token) - keep - 1)

def get_bearer_token(request):
    auth = request.META.get("HTTP_AUTHORIZATION", "")
    parts = auth.split(" ", 1)
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def send_endorsement_email(request):
    """
    Send endorsement email to insurer.
    
    Request Body:
        {
            "subject": "...",                   # required
            "body": "...",                      # required
            "endorsement_request_id": <int>,    # required
            "links": [ ... ],                   # optional
            "documents": [ ... ]                # optional
        }
    
    Returns:
        Success response with email send result or error response
    """
    
    # Validate request data
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return ResponseService.response("VALIDATION_ERROR", None, "Invalid JSON format")

    rules = {
        "subject": "required",
        "body": "required",
        "endorsement_request_id": "required|integer",
        "links": "array|nullable",
        "documents": "array|nullable",
    }
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "VALIDATION_ERROR")

    # Check authorization
    action = ActionService.getAction("SendApprovalEmail", "CREATE")
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    # Extract and prepare data
    endorsement_request_id = int(data["endorsement_request_id"])
    subject = (data["subject"] or "").strip()
    body = data["body"]
    links = data.get("links") or []
    documents = data.get("documents") or []

    # Append links to body if provided
    if isinstance(links, list) and links:
        link_lines = []
        for i, link in enumerate(links, 1):
            if isinstance(link, dict):
                title = str(link.get("title") or f"Link {i}")
                url = str(link.get("url") or "")
                link_lines.append(f"{i}. {title}: {url}")
            else:
                link_lines.append(f"{i}. {link}")
        body = f"{body}\n\nLinks:\n" + "\n".join(link_lines)

    # Get policy and insurer information
    policy = (
        QueryBuilderService("crmp_endorsement_requests as er")
        .leftJoin("crmp_issued_policies as ip", "ip.id", "er.issued_policy_id")
        .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
        .leftJoin("core_service_providers as sp", "sp.id", "pb.insurer_id")
        .select(
            "er.id as endorsement_request_id",
            "pb.id as policy_base_id",
            "pb.insurer_id as insurer_id",
            "sp.email as insurer_email",
        )
        .where("er.id", endorsement_request_id)
        .first()
    )
    
    if not policy:
        return ResponseService.response("NOT_FOUND", None, "Endorsement/policy not found.")

    to_email = (policy.get("insurer_email") or "").strip()
    insurer_id = policy.get("insurer_id")
    
    if not to_email:
        return ResponseService.response("VALIDATION_ERROR", None, "Insurer email not found for this endorsement.")

    # Get sender email from credentials
    from_email = _get_sender_email()
    if not from_email:
        return ResponseService.response(
            "SUCCESS",
            {"skipped": True},
            "Email send skipped: default Gmail credential not configured.",
        )

    print(f"[DEBUG] From email: {from_email}")
    print(f"[DEBUG] To email: {to_email}")
    print(f"[DEBUG] Subject: {subject}")
    print(f"[DEBUG] Body: {body}")
    print(f"[DEBUG] Documents: {documents}")
    print(f"[DEBUG] Endorsement request id: {endorsement_request_id}")
    print(f"[DEBUG] Insurer id: {insurer_id}")

    # Prepare attachments for email sending
    attachments = []
    if documents:
        for doc in documents:
            if isinstance(doc, dict) and doc.get("doc"):
                # Use the S3 URL directly instead of base64 data
                doc_key = doc.get("doc", "")
                cdn_base_url = os.getenv("CDN_BASE_URL")
                doc_url = f"{cdn_base_url}/{doc_key}"
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
                
                attachment = {
                    "filename": doc_name,
                    "content_type": content_type,
                    "file_url": doc_url  # Use S3 URL instead of base64 data
                }
                attachments.append(attachment)
                print(f"[EMAIL DEBUG][Endorsement] Added attachment: {attachment['filename']} with URL: {doc_url}")

    # Prepare email payload
    payload = {
        "subject": subject,
        "body": body,
        "to_email": to_email,
        # "from_email": from_email,
        "conversation_id": "",  # empty => let chatmail/send reuse/create
        "conversation_type": "ENDORSEMENT",
        "type_based_id": f"ER-{endorsement_request_id}",
        "insurer_id": insurer_id,
        "attachments": attachments,  # Add attachments to payload
    }

    # Send email via internal API
    response = _send_email_via_chatmail(request, payload)
    if not response.get("success"):
        return response.get("response")

    # Update endorsement mail status on success
    _update_endorsement_mail_status(endorsement_request_id)

    return ResponseService.response(
        "SUCCESS",
        response.get("data"),
        "Endorsement email sent and conversation handled.",
    )


def _get_sender_email():
    """Get default sender email from Gmail credentials."""
    try:
        cred = (
            QueryBuilderService("core_gmailcredential")
            .select("system_email")
            .first()
        )
        if cred:
            return (cred.get("system_email") or "").strip()
    except Exception:
        pass
    return None


def _send_email_via_chatmail(request, payload):
    """Send email via internal chatmail API."""
    # Build core API URL using the robust resolver
    core_base = _resolve_core_base(request)
    send_message_url = f"{core_base}/api/chatmail/send"

    headers = {
        "Content-Type": "application/json",
        "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
    }

    try:
        resp = requests.post(send_message_url, json=payload, headers=headers, timeout=30)
    except Exception as e:
        return {
            "success": False,
            "response": ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": str(e)},
                "Failed to call /api/chatmail/send",
            )
        }

    if resp.status_code != 200:
        return {
            "success": False,
            "response": ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"status": resp.status_code, "body": resp.text},
                "chatmail/send failed",
            )
        }

    try:
        result_json = resp.json()
    except Exception:
        result_json = {"raw": resp.text}

    return {
        "success": True,
        "data": result_json
    }


def _update_endorsement_mail_status(endorsement_request_id):
    """Update endorsement request mail status to sent."""
    try:
        QueryBuilderService("crmp_endorsement_requests").where(
            "id", endorsement_request_id
        ).update({"mail_status": "1"})
    except Exception:
        pass  # not fatal


logger = logging.getLogger(__name__)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def policy_sync_conversations(request, policy_id):
    """
    Sync conversations for a specific policy.
    
    First checks if the policy_id exists in crmp_endorsement_requests.issued_policy_id.
    If found, uses the endorsement request ID for type_based_id='ER-{endorsement_request_id}'.
    Otherwise, uses the original policy_id for type_based_id='ER-{policy_id}'.
    Then finds conversations in core_chat_conversations and POSTs to CORE /api/chatmail/sync-thread for each conversation.
    
    Args:
        request: HTTP request object
        policy_id: ID of the policy to sync conversations for
    
    Returns:
        Response with sync results and statistics
    """
    
    # Get all endorsement requests for the policy_id
    endorsement_requests = (
        QueryBuilderService("crmp_endorsement_requests")
        .select("id")
        .where("issued_policy_id", policy_id)
        .get()
    )
    
    # Return error if no endorsement requests found
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
        conversations = _get_policy_conversations(type_based_id)
        all_conversations.extend(conversations)
    
    conversations = all_conversations
    
    if not conversations:
        return ResponseService.response(
            "NOT_FOUND",
            None,
            f"No conversations found for policy {policy_id}"
        )

    # Sync each conversation
    sync_results = _sync_conversations(request, conversations)
    
    # Prepare response data
    response_data = _prepare_sync_response(policy_id, type_based_id, conversations, sync_results)
    
    # Return appropriate response based on sync results
    return _build_sync_response(response_data, policy_id)


def _get_policy_conversations(type_based_id):
    """Get conversations for a specific type_based_id."""
    return (
        QueryBuilderService("core_chat_conversations")
        .select("id as conversation_id", "code as conversation_code", "type", "created_at", "insurer_id")
        .where("type_based_id", type_based_id)
        .get()
    ) or []


def _sync_conversations(request, conversations):
    """Sync all conversations via the core API."""
    core_base = _resolve_core_base(request)
    sync_url = f"{core_base}/api/chatmail/sync-thread"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": request.META.get("HTTP_AUTHORIZATION", ""),
    }
    
    sync_results = []
    seen_ids = set()
    
    for conversation in conversations:
        conversation_id = conversation.get("conversation_id")
        insurer_id = conversation.get("insurer_id")
        
        if not conversation_id or conversation_id in seen_ids:
            continue
        seen_ids.add(conversation_id)
        
        sync_result = _sync_single_conversation(sync_url, headers, conversation)
        sync_results.append(sync_result)
    
    return sync_results


def _sync_single_conversation(sync_url, headers, conversation):
    """Sync a single conversation and return the result."""
    conversation_id = conversation.get("conversation_id")
    insurer_id = conversation.get("insurer_id")
    
    try:
        resp = requests.post(
            sync_url, 
            json={"conversation_id": conversation_id}, 
            headers=headers, 
            timeout=60
        )
        
        if resp.status_code == 200:
            try:
                sync_data = resp.json()
            except Exception:
                sync_data = {"raw": resp.text}
            
            return {
                "conversation_id": conversation_id,
                "insurer_id": insurer_id,
                "status": "success",
                "response": sync_data,
                "conversation_code": conversation.get("conversation_code"),
                "type": conversation.get("type"),
            }
        else:
            return {
                "conversation_id": conversation_id,
                "insurer_id": insurer_id,
                "status": "failed",
                "error": f"HTTP {resp.status_code}: {resp.text}",
                "conversation_code": conversation.get("conversation_code"),
                "type": conversation.get("type"),
            }
            
    except requests.exceptions.RequestException as e:
        return {
            "conversation_id": conversation_id,
            "insurer_id": insurer_id,
            "status": "failed",
            "error": f"Request error: {str(e)}",
            "conversation_code": conversation.get("conversation_code"),
            "type": conversation.get("type"),
        }
        
    except Exception as e:
        return {
            "conversation_id": conversation_id,
            "insurer_id": insurer_id,
            "status": "failed",
            "error": f"Unexpected error: {str(e)}",
            "conversation_code": conversation.get("conversation_code"),
            "type": conversation.get("type"),
        }


def _resolve_core_base(request) -> str:
    """
    Resolve the core API base URL.
    
    Priority order:
    1. settings.CORE_API_BASE_URL or env CORE_API_BASE_URL
    2. Use X-Forwarded-Host/Proto if present, else request host/proto
    3. Swap *-policy-api/*-crm-api -> *-core-api
    4. Fallback to https://dev-core-api.envoy.apptimus.lk
    """
    import os
    import re
    import ipaddress
    from urllib.parse import urlsplit
    from django.conf import settings
    
    # Check for explicit configuration
    explicit = (getattr(settings, "CORE_API_BASE_URL", "") or 
               os.environ.get("CORE_API_BASE_URL", "")).strip().rstrip("/")
    if explicit:
        return explicit

    # Get host and scheme from request
    fwd_host = (request.META.get("HTTP_X_FORWARDED_HOST") or "").split(",")[0].strip()
    host = fwd_host or request.get_host()
    host = host.split(":")[0]
    scheme = (request.META.get("HTTP_X_FORWARDED_PROTO") or 
              ("https" if request.is_secure() else "http")).split(",")[0].strip() or "https"

    # Handle IP addresses and localhost
    try:
        ipaddress.ip_address(host)
        return "https://dev-core-api.envoy.apptimus.lk"
    except ValueError:
        pass
    
    if host in {"localhost"}:
        return "https://dev-core-api.envoy.apptimus.lk"

    # Already core API?
    if "-core-api." in host:
        return f"{scheme}://{host}"

    # Swap service segment to core
    core_host = re.sub(r"^([a-z0-9]+)-[a-z0-9]+-api\.", r"\1-core-api.", host, flags=re.I)
    if core_host == host:
        core_host = host.replace("-policy-api.", "-core-api.").replace("-crm-api.", "-core-api.")

    # Fallback if still unchanged
    if core_host == host:
        return "https://dev-core-api.envoy.apptimus.lk"

    return f"{scheme}://{core_host}"


def _prepare_sync_response(policy_id, type_based_id, conversations, sync_results):
    """Prepare the response data structure."""
    successful_syncs = sum(1 for result in sync_results if result["status"] == "success")
    failed_syncs = sum(1 for result in sync_results if result["status"] == "failed")
    
    return {
        "policy_id": policy_id,
        "type_based_id": type_based_id,
        "total_conversations": len(conversations),
        "successful_syncs": successful_syncs,
        "failed_syncs": failed_syncs,
        "sync_results": sync_results,
    }


def _build_sync_response(response_data, policy_id):
    """Build the appropriate response based on sync results."""
    successful_syncs = response_data["successful_syncs"]
    failed_syncs = response_data["failed_syncs"]
    
    if failed_syncs == 0:
        return ResponseService.response(
            "SUCCESS", 
            response_data, 
            f"Successfully synced all {successful_syncs} conversations for policy {policy_id}"
        )
    
    if successful_syncs == 0:
        return ResponseService.response(
            "CONFLICT", 
            response_data, 
            f"Failed to sync any of the {failed_syncs} conversations for policy {policy_id}"
        )
    
    return ResponseService.response(
        "SUCCESS", 
        response_data, 
        f"Partially synced: {successful_syncs} successful, {failed_syncs} failed"
    )


# @api_view(["GET"])
# @permission_classes([IsAuthenticated])
# def endorsement_chat_messages(request, endorsement_id, insurer_id):
#     """
#     GET /api/endorsement/<endorsement_id>/chat/<insurer_id>?search=&page=1&limit=50&sort_by=&sort_dir=
    
#     Response (via ResponseService):
#     {
#         "is_success": true,
#         "message": "Chat messages fetched successfully.",
#         "result": {
#             "conversation_id": "<id>",
#             "total_records": <int>,
#             "per_page": <int>,
#             "current_page": <int>,
#             "last_page": <int>,
#             "data": [ ...messages... ]
#         },
#         "system_code": ""
#     }
#     """
#     try:
#         # ---- Resolve conversation from our DB ----
#         type_based_id = f"ER-{endorsement_id}"
#         email_message = EmailMessage.objects.filter(
#             type_based_id=type_based_id,
#             insurer_id=insurer_id
#         ).first()

#         if not email_message:
#             return ResponseService.response(
#                 "NOT_FOUND",
#                 result=None,
#                 message=f"No email message found for endorsement {endorsement_id} and insurer {insurer_id}"
#             )

#         conversation_id = email_message.conversation_id
#         if not conversation_id:
#             return ResponseService.response(
#                 "NOT_FOUND",
#                 result=None,
#                 message=f"No conversation_id found for endorsement {endorsement_id} and insurer {insurer_id}"
#             )

#         # ---- Bearer token from caller ----
#         idp_access_token = get_bearer_token(request)
#         if not idp_access_token:
#             return ResponseService.response(
#                 "VALIDATION_ERROR",
#                 result={"field": "Authorization"},
#                 message="Bearer token is required"
#             )

#         # ---- Query params ----
#         def _to_int(v, d):
#             try:
#                 return int(v)
#             except Exception:
#                 return d

#         page = max(1, _to_int(request.query_params.get("page", 1), 1))
#         limit = _to_int(request.query_params.get("limit", 50), 50)
#         if limit <= 0:
#             limit = 1
#         if limit > 200:
#             limit = 200  # safety cap

#         search = (request.query_params.get("search") or "").strip()
#         sort_by = (request.query_params.get("sort_by") or "").strip()
#         sort_dir = (request.query_params.get("sort_dir") or "").strip()

#         # ---- External API call (first attempt) ----
#         chat_api_url = f"https://dev-chat-app.apptimus.lk/api/conversations/{conversation_id}/messages"
#         headers = {
#             "Authorization": f"Bearer {idp_access_token}",
#             "Content-Type": "application/json",
#         }
#         params = {"page": page, "per_page": limit, "limit": limit}
#         if search:
#             params["search"] = search
#         if sort_by:
#             params["sort_by"] = sort_by
#         if sort_dir:
#             params["sort_dir"] = sort_dir

#         try:
#             resp = requests.get(chat_api_url, headers=headers, params=params, timeout=30)
#             resp.raise_for_status()
#             provider = resp.json() or {}
#         except requests.exceptions.RequestException as e:
#             logger.error(f"[endorsement_chat_messages] External API error conv={conversation_id}: {e}")
#             return ResponseService.response(
#                 "EXTERNAL_API_ERROR",
#                 result=None,
#                 message=f"Failed to fetch chat messages from external API: {str(e)}"
#             )

#         data_block = (provider or {}).get("data", {}) or {}
#         items_page = data_block.get("data", []) or []

#         # Prefer provider 'total'; else fallback to len(items we have)
#         try:
#             total = int(data_block.get("total", len(items_page)) or 0)
#         except Exception:
#             total = len(items_page)

#         provider_current_page = _to_int(data_block.get("current_page", None), None)
#         provider_per_page = _to_int(data_block.get("per_page", None), None)

#         # Decide whether provider respected pagination
#         provider_respected = (
#             provider_current_page == page and
#             (provider_per_page == limit or provider_per_page is None or provider_per_page == 0)
#         )

#         if provider_respected and items_page:
#             # Provider served the correct page; cap if overshot
#             page_items = items_page[:limit] if len(items_page) > limit else items_page
#             current_page = page
#             per_page_val = limit
#             last_page = math.ceil(total / per_page_val) if per_page_val else 1
#         else:
#             # Fallback: fetch page 1 with enough size, then virtual paginate
#             fallback_fetch_count = page * limit
#             fallback_per_page = min(max(fallback_fetch_count, 50), 500)

#             fallback_params = {"page": 1, "per_page": fallback_per_page, "limit": fallback_per_page}
#             if search:
#                 fallback_params["search"] = search
#             if sort_by:
#                 fallback_params["sort_by"] = sort_by
#             if sort_dir:
#                 fallback_params["sort_dir"] = sort_dir

#             try:
#                 fb_resp = requests.get(chat_api_url, headers=headers, params=fallback_params, timeout=30)
#                 fb_resp.raise_for_status()
#                 fb_provider = fb_resp.json() or {}
#                 fb_block = (fb_provider or {}).get("data", {}) or {}
#                 items_all = fb_block.get("data", []) or []
#                 try:
#                     total = int(fb_block.get("total", len(items_all)) or 0)
#                 except Exception:
#                     total = len(items_all)
#             except requests.exceptions.RequestException as e:
#                 logger.error(f"[endorsement_chat_messages] Fallback fetch failed conv={conversation_id}: {e}")
#                 items_all = items_page  # fall back to whatever we have

#             start = (page - 1) * limit
#             end = start + limit
#             page_items = items_all[start:end] if start < len(items_all) else []

#             current_page = page
#             per_page_val = limit
#             last_page = math.ceil(total / per_page_val) if per_page_val else 1
#             if last_page == 0:
#                 last_page = 1

#         # ---- Build ResponseService payload (now includes conversation_id) ----
#         result = {
#             "conversation_id": conversation_id,
#             "total_records": total,
#             "per_page": per_page_val,
#             "current_page": current_page,
#             "last_page": last_page,
#             "data": page_items,
#         }

#         return ResponseService.response(
#             "SUCCESS",
#             result=result,
#             message="Chat messages fetched successfully."
#         )

    # except Exception as e:
    #     logger.error(f"[endorsement_chat_messages] Unexpected error e={endorsement_id}, i={insurer_id}: {e}", exc_info=True)
    #     return ResponseService.response(
    #         "INTERNAL_SERVER_ERROR",
    #         result=None,
    #         message=str(e)
    #     )


def update_invoice_status_based_on_endorsement(endorsement_request_id):
    """
    Update invoice status based on endorsement type.
    This function handles:
    - Cancelled: When endorsement type is "Cancellations" (ID: 3)
    - Refunded: When endorsement type is "Refund" (ID: 2)
    
    Args:
        endorsement_request_id (int): The ID of the endorsement request
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get endorsement request details
        endorsement_request = (
            QueryBuilderService("crmp_endorsement_requests")
            .select(
                "id",
                "endorsement_type_id",
                "issued_policy_id",
                "cover_value"
            )
            .where("id", endorsement_request_id)
            .first()
        )
        
        if not endorsement_request:
            print(f"Endorsement request {endorsement_request_id} not found")
            return False
        
        issued_policy_id = endorsement_request.get("issued_policy_id")
        endorsement_type_id = endorsement_request.get("endorsement_type_id")
        
        if not issued_policy_id:
            print(f"No issued policy found for endorsement request {endorsement_request_id}")
            return False
        
        # Get all invoices for this policy (both finance and policy invoices)
        finance_invoices = (
            QueryBuilderService("crmf_invoices")
            .select("id", "invoice_number", "status_id", "paid_amount", "outstanding_amount", "due_date", "last_paid_date")
            .where("issued_policy_id", issued_policy_id)
            .get()
        )
        
        policy_invoices = (
            QueryBuilderService("crmp_invoices")
            .select("id", "invoice_number", "status_id", "paid_amount", "outstanding_amount", "due_date")
            .where("issued_policy_id", issued_policy_id)
            .get()
        )
        
        all_invoices = finance_invoices + policy_invoices
        
        if not all_invoices:
            print(f"No invoices found for policy {issued_policy_id}")
            return False
        
        # Import status update functions
        from envoy_bu_policy_api.finance.controllers.utils.invoice_utils import update_invoice_status_after_payment
        from envoy_bu_policy_api.policy.controllers.invoice_utils import update_invoice_status_after_payment as update_policy_invoice_status
        
        # Handle status updates based on endorsement type
        if endorsement_type_id == 3:  # Cancellations
            print(f"Processing cancellation for endorsement request {endorsement_request_id}")
            for invoice in all_invoices:
                if "crmf_invoices" in str(invoice):  # Finance invoice
                    update_invoice_status_after_payment(invoice["id"])
                    # Force status to Cancelled
                    QueryBuilderService("crmf_invoices").where("id", invoice["id"]).update({
                        "status_id": get_cancelled_status_id("finance_invoice")
                    })
                    print(f"Updated finance invoice {invoice['id']} to Cancelled")
                else:  # Policy invoice
                    update_policy_invoice_status(invoice["id"])
                    # Force status to Cancelled
                    QueryBuilderService("crmp_invoices").where("id", invoice["id"]).update({
                        "status_id": get_cancelled_status_id("policy_invoice")
                    })
                    print(f"Updated policy invoice {invoice['id']} to Cancelled")
                    
        elif endorsement_type_id == 2:  # Refund
            print(f"Processing refund for endorsement request {endorsement_request_id}")
            for invoice in all_invoices:
                if "crmf_invoices" in str(invoice):  # Finance invoice
                    update_invoice_status_after_payment(invoice["id"])
                    # Force status to Refunded
                    QueryBuilderService("crmf_invoices").where("id", invoice["id"]).update({
                        "status_id": get_refunded_status_id("finance_invoice")
                    })
                    print(f"Updated finance invoice {invoice['id']} to Refunded")
                else:  # Policy invoice
                    update_policy_invoice_status(invoice["id"])
                    # Force status to Refunded
                    QueryBuilderService("crmp_invoices").where("id", invoice["id"]).update({
                        "status_id": get_refunded_status_id("policy_invoice")
                    })
                    print(f"Updated policy invoice {invoice['id']} to Refunded")
        
        # Note: Overdue invoice management is handled via SQL queries on the live server
        # See get_overdue_invoices_sql_queries() function below for the queries
        
        return True
        
    except Exception as e:
        print(f"Error updating invoice status for endorsement request {endorsement_request_id}: {str(e)}")
        return False


def get_cancelled_status_id(module_type):
    """
    Get the Cancelled status ID for the specified module.
    
    Args:
        module_type (str): Either "finance_invoice" or "policy_invoice"
        
    Returns:
        int: Status ID or None if not found
    """
    try:
        if module_type == "finance_invoice":
            from envoy_bu_policy_api.finance.controllers.utils.invoice_utils import get_finance_invoice_status_id
            return get_finance_invoice_status_id("Cancelled")
        else:
            from envoy_bu_policy_api.policy.controllers.invoice_utils import get_invoice_status_id
            return get_invoice_status_id("Cancelled")
    except Exception as e:
        print(f"Error getting cancelled status ID for {module_type}: {str(e)}")
        return None


def get_refunded_status_id(module_type):
    """
    Get the Refunded status ID for the specified module.
    
    Args:
        module_type (str): Either "finance_invoice" or "policy_invoice"
        
    Returns:
        int: Status ID or None if not found
    """
    try:
        if module_type == "finance_invoice":
            from envoy_bu_policy_api.finance.controllers.utils.invoice_utils import get_finance_invoice_status_id
            return get_finance_invoice_status_id("Refunded")
        else:
            from envoy_bu_policy_api.policy.controllers.invoice_utils import get_invoice_status_id
            return get_invoice_status_id("Refunded")
    except Exception as e:
        print(f"Error getting refunded status ID for {module_type}: {str(e)}")
        return None


def get_endorsement_sql_queries():
    """
    Returns SQL queries for checking endorsement-related data.
    These can be run directly on the live server by DevOps.
    
    Returns:
        dict: Dictionary containing SQL queries
    """
    queries = {
        "check_endorsement_cancellations": """
            -- Check invoices that should be cancelled based on endorsement requests
            SELECT 
                er.id as endorsement_request_id,
                er.endorsement_type_id,
                et.name as endorsement_type_name,
                er.issued_policy_id,
                er.cover_value,
                er.created_at as endorsement_date
            FROM crmp_endorsement_requests er
            JOIN crmp_endorsement_types et ON er.endorsement_type_id = et.id
            WHERE er.endorsement_type_id IN (2, 3)  -- Refund (2) or Cancellations (3)
            ORDER BY er.created_at DESC;
        """,
        
        "check_invoice_status_summary": """
            -- Get summary of invoice statuses
            SELECT 
                'Finance Invoices' as invoice_type,
                cs.name as status_name,
                COUNT(*) as count
            FROM crmf_invoices fi
            JOIN core_status cs ON fi.status_id = cs.id
            GROUP BY cs.name, cs.id
            UNION ALL
            SELECT 
                'Policy Invoices' as invoice_type,
                cs.name as status_name,
                COUNT(*) as count
            FROM crmp_invoices pi
            JOIN core_status cs ON pi.status_id = cs.id
            GROUP BY cs.name, cs.id
            ORDER BY invoice_type, count DESC;
        """
    }
    
    return queries
