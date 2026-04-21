import json
from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from envoy.models import UserInvitation
from mServices.ResponseService import ResponseService
import mServices.QueryBuilderService as QueryBuilderService
from mServices.ValidatorService import ValidatorService
from rest_framework.decorators import api_view
from envoy.models.role import Role
from envoy.utils import send_invitation_email
from django.shortcuts import get_object_or_404

@api_view(["GET"])
def get_user_invitations(request):
    try:
        # Pagination & sorting defaults
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("per_page", 10))
        sort_by = request.GET.get("sort_by", "core_user_invitations.name")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "core_user_invitations.name" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        search_string = request.GET.get("search", "")
        filter_json = json.loads(request.GET.get("filter", "{}"))

        # Query config
        all_columns = [
            "core_user_invitations.uid",
            "core_user_invitations.name",
            "core_user_invitations.email",
            "core_user_invitations.role_id",
            "core_roles.name as role_name"
        ]
        allowed_filters = ["core_user_invitations.name"]
        search_columns = ["core_user_invitations.name", "core_user_invitations.email"]
        allowed_sorting_columns = ["core_user_invitations.name", "core_user_invitations.email"]

        # Build query
        query = (
            QueryBuilderService("core_user_invitations")
            .leftJoin("core_roles", "core_roles.id", "core_user_invitations.role_id")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response(
            "SUCCESS",
            message="User invitations fetched successfully.",
            result=query,
        )

    except Exception as e:
        return ResponseService.response(
            "ERROR", message="Error fetching user invitations.", result=str(e)
        )



@api_view(["POST"])
def resend_user_invitation(request, uid):
    try:
        print(f"Resending invitation for UID: {uid}")
       
        invitation = UserInvitation.objects.get(uid=uid)
    
    except UserInvitation.DoesNotExist:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", message="Invitation not found.", result="Invitation not found."
        )
    
    success, error_message = send_invitation_email(
        invitation,invitation.role, "invitation_resend_email_template.html", "You're Invited Again!"
    )

    if not success:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", message=error_message, result=error_message
        )

    return ResponseService.response(
        "SUCCESS",
        message="invitation_resent_successfully",
        result="Invitation resent successfully.",
    )


@api_view(["POST"])
def cancel_invitation(request, uid):
    if request.path.endswith("/cancel"):
        print(f"Looking for UID: {uid}")
        try:
            invitation = None
            body = request.data if hasattr(request, "data") else {}
            email = (body.get("email") or body.get("contact_email") or "").strip()

            # If email is provided, only check and delete by email (ignore UID)
            if email:
                print(f"Email provided. Deleting by email only: {email}")
                deleted_count, _ = UserInvitation.objects.filter(email=email).delete()
                if deleted_count > 0:
                    return ResponseService.response(
                        "SUCCESS",
                        message="invitation_canceled_and_deleted",
                        result={"deleted_by": "email", "email": email, "deleted_count": deleted_count},
                    )
                return ResponseService.response(
                    "NOT_FOUND",
                    message="Invitation not found.",
                    result=f"No invitation found for email: {email}. Please check if it exists or has already been processed.",
                )
            
            # First, try to find with the provided UID as-is
            try:
                invitation = UserInvitation.objects.get(uid=uid)
                print(f"Found invitation with original UID: {invitation.name}")
            except UserInvitation.DoesNotExist:
                print(f"Original UID {uid} not found")
            
            # If not found and it's a non-hyphenated UUID, try converting to hyphenated format
            if not invitation and len(uid) == 32 and '-' not in uid:
                formatted_uid = f"{uid[:8]}-{uid[8:12]}-{uid[12:16]}-{uid[16:20]}-{uid[20:]}"
                print(f"Trying formatted UID: {formatted_uid}")
                try:
                    invitation = UserInvitation.objects.get(uid=formatted_uid)
                    print(f"Found invitation with formatted UID: {invitation.name}")
                except UserInvitation.DoesNotExist:
                    print(f"Formatted UID {formatted_uid} not found")
            
            # If still not found, return error
            if not invitation:
                print(f"No invitation found for UID: {uid}")
                return ResponseService.response(
                    "NOT_FOUND",
                    message="Invitation not found.",
                    result=f"No invitation found with UID: {uid}. Please check if the invitation exists or has already been processed.",
                )
            
            invitation.delete()  # Perform deletion
            print(f"Deleted invitation: {invitation.email}")

            return ResponseService.response(
                "SUCCESS", message="invitation_canceled_and_deleted", result=None
            )
        except Exception as e:
            print(f"Error: {str(e)}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", message="Error canceling invitation.", result=str(e)
            )

    return ResponseService.response("INTERNAL_SERVER_ERROR", message="Invalid request.", result=None)


@api_view(["PUT"])
def cancel_invitation_by_email(request):
    try:
        data = request.data
        uuid = request.data.get("uuid")
        email = request.data.get("email")

        rules = {
            "uuid": "required",
            "email": "required",
        }
        custom_messages = {
            "uuid.required": "UUID is required.",
            "email.required": "Email is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        try:
            invitation = UserInvitation.objects.get(email=email, uid=uuid)
            invitation.delete()
        except UserInvitation.DoesNotExist:
            return ResponseService.response("NOT_FOUND", message="Invitation not found.", result=None)

        return ResponseService.response("SUCCESS", message="invitation_canceled_and_deleted", result=None)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", message="Error canceling invitation.", result=str(e))


