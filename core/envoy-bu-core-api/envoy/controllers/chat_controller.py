import math
from rest_framework.decorators import api_view
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
from django.contrib.auth.models import User
from envoy.models.mail_model import GmailCredential, EmailMessage
from envoy.controllers.approval_controller import get_bearer_token
from django.utils import timezone
import json
import requests
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])  # remove this if you want it public
def user_mail_config(request):
    """
    Return the list of Gmail addresses (system_email) linked to a user.
    - If ?user_id= is provided, use that.
    - Otherwise, use the authenticated request.user.id
    """
    try:
        # Prefer explicit param; fall back to current user
        user_id = request.GET.get("user_id")
        if not user_id and request.user and request.user.is_authenticated:
            user_id = request.user.id

        # Validate
        rules = {"user_id": "required|integer|min:1"}
        custom_messages = {
            "user_id.required": "User ID is required.",
            "user_id.integer": "User ID must be a number.",
            "user_id.min": "User ID must be greater than 0.",
        }
        errors = ValidatorService.validate({"user_id": user_id}, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Query only what we need (emails), no secrets
        rows = (
            QueryBuilderService("core_gmailcredential")
            .select("id", "system_email")         # keep id if you need to reference a credential later
            .where("user_id", int(user_id))
            .orderBy("id", "asc")
            .get()
        )

        emails = [{"credential_id": r["id"], "email": r["system_email"]} for r in rows] if rows else []

        data = {
            "user_id": int(user_id),
            "total": len(emails),
            "emails": emails,                      # e.g., [{"credential_id": 3, "email": "x@gmail.com"}]
        }
        return ResponseService.response("SUCCESS", data, "Gmail addresses retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@csrf_exempt
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_user_specific_mail_config(request, user_id, config_id):
    """
    Delete a specific Gmail credential for a specific user.
    RESTful endpoint: DELETE /api/user/{user_id}/mail-config/{config_id}
    """
    try:
        # Validate parameters
        validation_data = {
            "user_id": user_id,
            "config_id": config_id
        }
        
        rules = {
            "user_id": "required|exists:core_users,id",
            "config_id": "required|exists:core_gmailcredential,id"
        }
        
        custom_messages = {
            "user_id.required": "User ID is required.",
            "user_id.integer": "User ID must be a number.",
            "user_id.min": "User ID must be greater than 0.",
            "user_id.exists": "User with this ID does not exist.",
            "config_id.required": "Config ID is required.",
            "config_id.integer": "Config ID must be a number.",
            "config_id.min": "Config ID must be greater than 0.",
            "config_id.exists": "Gmail credential with this ID does not exist."
        }
        
        # Validate
        errors = ValidatorService.validate(validation_data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Check if the credential belongs to the specified user
        credential_check = (
            QueryBuilderService("core_gmailcredential")
            .select("id", "user_id", "system_email")
            .where("id", int(config_id))
            .where("user_id", int(user_id))
            .get()
        )
        
        if not credential_check:
            return ResponseService.response("NOT_FOUND", {}, "Gmail credential not found for this user.")
        
        # Check if user has permission to delete
        # Users can only delete their own credentials unless they are superusers
        if request.user.id != int(user_id) and not request.user.is_superuser:
            return ResponseService.response("FORBIDDEN", {}, "You don't have permission to delete this credential.")

        # Perform deletion
        deleted_count = (
            QueryBuilderService("core_gmailcredential")
            .where("id", int(config_id))
            .where("user_id", int(user_id))
            .delete()
        )
        
        if deleted_count > 0:
            data = {
                "user_id": int(user_id),
                "deleted_config_id": int(config_id),
                "deleted_email": credential_check[0]["system_email"],
                "deleted_count": deleted_count
            }
            return ResponseService.response("SUCCESS", data, f"Gmail credential '{credential_check[0]['system_email']}' deleted successfully.")
        else:
            return ResponseService.response("NOT_FOUND", {}, "Gmail credential not found or already deleted.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@csrf_exempt
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quotation_insurer_chat_messages(request, quotation_id, insurer_id):
    """
    GET /api/<quotation_id>/chat/<insurer_id>?search=&page=1&limit=50&sort_by=&sort_dir=
    
    Response (via ResponseService):
    {
        "is_success": true,
        "message": "Chat messages fetched successfully.",
        "result": {
            "conversation_id": "<id>",
            "total_records": <int>,
            "per_page": <int>,
            "current_page": <int>,
            "last_page": <int>,
            "data": [ ...messages... ]
        },
        "system_code": ""
    }
    """
    try:
        # ---- Resolve conversation from our DB ----
        type_based_id = f"QR-{quotation_id}"
        email_message = EmailMessage.objects.filter(
            type_based_id=type_based_id,
            insurer_id=insurer_id
        ).first()

        if not email_message:
            return ResponseService.response(
                "NOT_FOUND",
                result=None,
                message=f"No email message found for quotation {quotation_id} and insurer {insurer_id}"
            )

        conversation_id = email_message.conversation_id
        if not conversation_id:
            return ResponseService.response(
                "NOT_FOUND",
                result=None,
                message=f"No conversation_id found for quotation {quotation_id} and insurer {insurer_id}"
            )

        # ---- Bearer token from caller ----
        idp_access_token = get_bearer_token(request)
        if not idp_access_token:
            return ResponseService.response(
                "VALIDATION_ERROR",
                result={"field": "Authorization"},
                message="Bearer token is required"
            )

        # ---- Query params ----
        def _to_int(v, d):
            try:
                return int(v)
            except Exception:
                return d

        page = max(1, _to_int(request.query_params.get("page", 1), 1))
        limit = _to_int(request.query_params.get("limit", 50), 50)
        if limit <= 0:
            limit = 1
        if limit > 200:
            limit = 200  # safety cap

        search = (request.query_params.get("search") or "").strip()
        sort_by = (request.query_params.get("sort_by") or "").strip()
        sort_dir = (request.query_params.get("sort_dir") or "").strip()

        # ---- External API call (first attempt) ----
        chat_api_url = f"https://dev-chat-app.apptimus.lk/api/conversations/{conversation_id}/messages"
        headers = {
            "Authorization": f"Bearer {idp_access_token}",
            "Content-Type": "application/json",
        }
        params = {"page": page, "per_page": limit, "limit": limit}
        if search:
            params["search"] = search
        if sort_by:
            params["sort_by"] = sort_by
        if sort_dir:
            params["sort_dir"] = sort_dir

        try:
            resp = requests.get(chat_api_url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            provider = resp.json() or {}
        except requests.exceptions.RequestException as e:
            logger.error(f"[quotation_insurer_chat_messages] External API error conv={conversation_id}: {e}")
            return ResponseService.response(
                "EXTERNAL_API_ERROR",
                result=None,
                message=f"Failed to fetch chat messages from external API: {str(e)}"
            )

        data_block = (provider or {}).get("data", {}) or {}
        items_page = data_block.get("data", []) or []

        # Prefer provider 'total'; else fallback to len(items we have)
        try:
            total = int(data_block.get("total", len(items_page)) or 0)
        except Exception:
            total = len(items_page)

        provider_current_page = _to_int(data_block.get("current_page", None), None)
        provider_per_page = _to_int(data_block.get("per_page", None), None)

        # Decide whether provider respected pagination
        provider_respected = (
            provider_current_page == page and
            (provider_per_page == limit or provider_per_page is None or provider_per_page == 0)
        )

        if provider_respected and items_page:
            # Provider served the correct page; cap if overshot
            page_items = items_page[:limit] if len(items_page) > limit else items_page
            current_page = page
            per_page_val = limit
            last_page = math.ceil(total / per_page_val) if per_page_val else 1
        else:
            # Fallback: fetch page 1 with enough size, then virtual paginate
            fallback_fetch_count = page * limit
            fallback_per_page = min(max(fallback_fetch_count, 50), 500)

            fallback_params = {"page": 1, "per_page": fallback_per_page, "limit": fallback_per_page}
            if search:
                fallback_params["search"] = search
            if sort_by:
                fallback_params["sort_by"] = sort_by
            if sort_dir:
                fallback_params["sort_dir"] = sort_dir

            try:
                fb_resp = requests.get(chat_api_url, headers=headers, params=fallback_params, timeout=30)
                fb_resp.raise_for_status()
                fb_provider = fb_resp.json() or {}
                fb_block = (fb_provider or {}).get("data", {}) or {}
                items_all = fb_block.get("data", []) or []
                try:
                    total = int(fb_block.get("total", len(items_all)) or 0)
                except Exception:
                    total = len(items_all)
            except requests.exceptions.RequestException as e:
                logger.error(f"[quotation_insurer_chat_messages] Fallback fetch failed conv={conversation_id}: {e}")
                items_all = items_page  # fall back to whatever we have

            start = (page - 1) * limit
            end = start + limit
            page_items = items_all[start:end] if start < len(items_all) else []

            current_page = page
            per_page_val = limit
            last_page = math.ceil(total / per_page_val) if per_page_val else 1
            if last_page == 0:
                last_page = 1

        # ---- Process sent_at fields in chat messages ----
        for message in page_items:
            if "sent_at" in message and message["sent_at"]:
                # Convert sent_at to timezone.now().isoformat() format
                message["sent_at"] = timezone.now().isoformat()

        # ---- Build ResponseService payload (now includes conversation_id) ----
        result = {
            "conversation_id": conversation_id,
            "total_records": total,
            "per_page": per_page_val,
            "current_page": current_page,
            "last_page": last_page,
            "data": page_items,
            "timestamp": timezone.now().isoformat(),
        }

        return ResponseService.response(
            "SUCCESS",
            result=result,
            message="Chat messages fetched successfully."
        )

    except Exception as e:
        logger.error(f"[quotation_insurer_chat_messages] Unexpected error q={quotation_id}, i={insurer_id}: {e}", exc_info=True)
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            result=None,
            message=str(e)
        )