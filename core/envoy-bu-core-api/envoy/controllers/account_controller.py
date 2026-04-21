from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
import json
import random
import requests

from envoy.controllers.services.NotificationService import NotificationService
from envoy.models import Customer, Contact
from envoy.models import CustomerInvitation
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService

from django.shortcuts import get_object_or_404
import mServices.QueryBuilderService as QueryBuilderService

from envoy.models.customer_additional_contact import CustomerAdditionalContact
from django.http import Http404

from envoy.services.entity_validator_service import EntityService
from django.conf import settings
from envoy.models.mail_model import GmailCredential
from envoy.services import email_service as svc
from envoy.services.email_service import ensure_fresh_token
from django.template.loader import render_to_string
import logging

logger = logging.getLogger(__name__)


def getAll(request, account_id=None):
    selected_columns = [
        "core_customers.*",
        "ct.name as primary_contact_name",
        "ct.email as primary_contact_email",
        "ct.primary_contact as primary_contact_number",
        "ct.address as primary_contact_address",
        "ct.secondary_contact as primary_contact_secondary_number",
        "ct.website_url as primary_contact_website_url",
    ]

    # Parse filters (supports URL-encoded JSON string under 'filters')
    raw_filter_json = request.GET.get("filters", '{}')
    try:
        filter_dict = json.loads(raw_filter_json) if isinstance(raw_filter_json, str) else (raw_filter_json or {})
    except json.JSONDecodeError:
        filter_dict = {}
    
    # Extract type values for manual handling
    type_values = []
    if "type" in filter_dict and isinstance(filter_dict["type"], dict):
        type_filter = filter_dict["type"]
        if isinstance(type_filter.get("v"), list):
            type_values = type_filter["v"]
        elif isinstance(type_filter.get("v"), str):
            type_values = [type_filter["v"]]
    
    # Optional: support legacy 'type' param directly
    type_param = request.GET.get("type")
    if type_param and isinstance(type_param, str) and type_param.strip() and type_param.lower() not in ['','undefined','null']:
        if not type_values:  # Only add if no structured type filter
            type_values = [type_param.strip()]
    
    # Remove type from filter_dict since we'll handle it manually
    if "type" in filter_dict:
        del filter_dict["type"]

    search_term = (request.GET.get("search") or "").strip()
    page_number = int(request.GET.get("page") or 1)
    page_size = int(request.GET.get("limit") or 10)

    sort_column = request.GET.get("sort_by")
    sort_direction = request.GET.get("sort_dir")
    sort_column = "core_customers.id" if sort_column in [None, ""] else sort_column
    sort_direction = ("desc" if sort_direction in [None, ""] else sort_direction).lower()
    sort_direction = "asc" if sort_direction == "asc" else "desc"

    ids_param = request.GET.get("ids")
    ignore_id_value = request.GET.get("ignore")

    # Use fully-qualified columns everywhere to avoid ambiguity
    allowed_filters = ["core_customers.name", "core_customers.type"]
    search_columns = ["core_customers.name", "ct.name", "ct.email"]
    allowed_sorting_columns = [
        "core_customers.id",
        "core_customers.name",
        "core_customers.type",
        "ct.name",
    ]

    # Map simple keys to fully-qualified columns expected by QueryBuilderService
    filter_aliases = {
        "name": "core_customers.name",
    }
    mapped_filter_dict = { filter_aliases.get(k, k): v for k, v in filter_dict.items() }
    mapped_filter_json = json.dumps(mapped_filter_dict)

    try:
        customers_query = (
            QueryBuilderService("core_customers")
            .leftJoin("core_contacts as ct", "ct.id", "core_customers.primary_contact_id")
            .select(*selected_columns)
        )
        # Apply type filter manually using whereIn
        if type_values:
            customers_query = customers_query.whereIn("core_customers.type", type_values)
        
        # Apply other filters and search using apply_conditions
        customers_query = customers_query.apply_conditions(mapped_filter_json, allowed_filters, search_term, search_columns)

        if account_id:
            customers_query = customers_query.where("core_customers.id", account_id)

        if ignore_id_value:
            customers_query = customers_query.whereNotIn("core_customers.id", [ignore_id_value])

        if ids_param:
            id_list = [i.strip() for i in ids_param.split(",") if i.strip()]
            result = customers_query.whereIn("core_customers.id", id_list).get()
        else:
            result = customers_query.paginate(
                page_number,
                page_size,
                allowed_sorting_columns,
                sort_column,
                sort_direction,
            )
    except Exception as e:
        print(f"ERROR in query building: {e}")
        print(f"allowed_filters: {allowed_filters}")
        print(f"search_term: {search_term}")
        raise e

    return ResponseService.response(
        "SUCCESS",
        message="Accounts fetched successfully.",
        result=result,
    )


def generate_unique_portal_id():
    """
    Generate a unique 8-digit portal ID for customers
    """
    while True:
        # Generate a random 8-digit number
        portal_id = str(random.randint(10000000, 99999999))
        
        # Check if it exists in the database
        exists = QueryBuilderService("core_customers") \
            .where("portal_id", portal_id) \
            .first()
            
        if not exists:
            return portal_id

@api_view(["GET", "POST"])
def get_accounts(request):
    if request.method == "GET":
        try:
            return getAll(request)      

            # # ------------------------QueryBuilderService--------------------------------

            # # all_columns = ["customer.id", "customer.code", "customer.type", "customer.name", "customer.logo", "customer.remarks", "customer.parent_id", "customer.primary_contact_id"]
            # all_columns = ["customer.id", "customer.code", "customer.type", "customer.name", "customer.logo", "customer.remarks",]
            # filter_json = request.GET.get('filter', {})
            # search_string = request.GET.get('search', '')
            # page = int(request.GET.get('page', 1))
            # limit = int(request.GET.get('limit', 10))
            # account_detail = Customer.objects.all().order_by("id")
            # paginator = Paginator(account_detail, limit)
            # sort_by = request.GET.get('sort_by', 'id')
            # sort_dir = request.GET.get('sort_dir', 'desc')
            # allowed_filters = ["name",]
            # search_columns = ["name"]
            # allowed_sorting_columns = ["name"]

            # query = QueryBuilderService("customer")\
            #         .select(*all_columns) \
            #         .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
            #         .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \

            # response_data = {
            #     "current_page": page,
            #     "last_page": paginator.num_pages,
            #     "total_records": paginator.count,
            #     "count": limit,
            #     "data": query
            # }

        except ValidationError as e:
            return ResponseService.response(
                "VALIDATION_ERROR", e.message_dict, "Validation Error"
            )

        except Exception as e:
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
            )

    elif request.method == "POST":
        try:
            data = request.data

            nullable_fields = ["website_url", "email"]
            for field in nullable_fields:
                if field in data and (data[field] == "" or data[field] is None):
                    del data[field]  



            #  Validation Rules
            rules = {
                "type": "required|in:Corporate,Personal",
                "name": "required|max:200",
                "primary_contact": "required_without:primary_contact_id|max:20",
                # "primary_contact_id": "nullable|exists:core_contacts,id",
                "parent_id": "nullable|exists:core_customers,id",
                "logo": "nullable",
                "remarks": "nullable",
                "primary_contact": "required|max:20",
                "email": "required|email|max:255|unique:core_contacts,email",
                "address": "max:255",
                "secondary_contact": "max:20",
                "website_url": "nullable|url",
                "is_configure": "nullable|boolean",
                # "number_of_employees": "nullable|max:255",  # Flex field
                # "br_no": "nullable|max:255",                # Flex field
            }

            custom_messages = {
                "type.required": "Type is required.",
                "type.in": "Type must be 'Corporate' or 'Personal'.",
                "name.required": "Name is required.",
                "primary_contact.required_without": "Primary contact is required if primary_contact_id is not provided.",
                "primary_contact.max": "Primary contact cannot exceed 20 characters.",
                # "primary_contact_id.exists": "The provided primary contact ID does not exist.",
                "parent_id.exists": "The provided parent ID does not exist.",
                "email.email": "Invalid email format.",
                "email.max": "Email cannot exceed 255 characters.",
                "address.max": "Address cannot exceed 255 characters.",
                "secondary_contact.max": "Secondary contact cannot exceed 20 characters.",
                # "website_url.url": "Invalid URL format.",
            }

            #  Validate Data
            errors = ValidatorService.validate(data, rules, custom_messages)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

            validated_data = data

            #  Handle Primary Contact
            # primary_contact = None
            # if validated_data.get("primary_contact_id"):
            #     primary_contact = Contact.objects.filter(id=validated_data["primary_contact_id"]).first()
            #     if not primary_contact:
            #         return ResponseService.response(
            #             "VALIDATION_ERROR",
            #             {"primary_contact_id": ["The specified primary contact does not exist."]},
            #             "Validation Error",
            #         )
            # else:
            primary_contact = Contact.objects.create(
                    name=validated_data["name"],
                    primary_contact=validated_data["primary_contact"],
                    show_in_list=False,
                    email=validated_data.get("email", ""),
                    address=validated_data.get("address", ""),
                    secondary_contact=validated_data.get("secondary_contact", ""),
                    website_url=validated_data.get("website_url", ""),
                )

            parent_account = Customer.objects.filter(id=validated_data.get("parent_id")).first()

            # # Extract flex field data
            # flex_fields_data = {
            #     "number_of_employees": validated_data.get("number_of_employees"),
            #     "br_no": validated_data.get("br_no"),
            # }

            # Create Entity and FlexValues
            entity_action = {"entity": "customer"}
            # entity = EntityService.store(entity_action, flex_fields_data, user=request.user)
            entity = EntityService.store(entity_action, validated_data.get("flex_fields", {}), user=request.user)

            portal_id = None

            # Create Customer and link entity
            portal_id = generate_unique_portal_id()
            customer = Customer.objects.create(
                type=validated_data["type"],
                name=validated_data["name"],
                logo=validated_data.get("logo", ""),
                remarks=validated_data.get("remarks", ""),
                parent=parent_account,
                primary_contact=primary_contact,
                entity=entity,
                portal_id=int(portal_id)  # Convert to int since we store it as IntegerField
            )

            # Check if account configuration is requested
            # Normalize is_configure to boolean (handle both 1/0 and true/false)
            is_configure = validated_data.get("is_configure", False)
            if isinstance(is_configure, (int, str)):
                is_configure = bool(int(is_configure)) if str(is_configure).isdigit() else bool(is_configure)
            
            if is_configure:
                # Validate email is present for configuration
                email = validated_data.get("email", "")
                if not email or email.strip() == "":
                    print("Account configuration skipped: Email is required for configuration")
                else:
                    try:
                        # Call account configuration logic directly without HTTP overhead
                        config_result = perform_account_configuration_direct(
                            name=validated_data["name"],
                            email=email,
                            customer_id=customer.id,
                            contact_no=validated_data.get("primary_contact", "")
                        )
                        
                        # If configuration failed, log the error but don't fail customer creation
                        if not config_result.get("success", False):
                            print(f"Account configuration failed: {config_result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        # Log the error but don't fail the customer creation
                        print(f"Account configuration failed: {str(e)}")
                        import traceback
                        traceback.print_exc()
                        # Continue with normal response

            return ResponseService.response(
                "SUCCESS",
                {
                    "id": customer.id,
                    "code": customer.code,
                    "type": customer.type,
                    "name": customer.name,
                    "logo": customer.logo,
                    "remarks": customer.remarks,
                    "parent_id": customer.parent.id if customer.parent else None,
                    "primary_contact_id": customer.primary_contact.id,
                    "portal_id": customer.portal_id,  # Include portal_id in response
                },
                "default_create_success_msg",
            )

        except ValidationError as e:
            return ResponseService.response("VALIDATION_ERROR", e.message_dict, "Validation Error")

        except Exception as e:
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
            )

@api_view(["GET"])
def account_email_detail(request, id):

    customer = QueryBuilderService("core_customers").where("id", id).first()

    if not customer:
        return ResponseService.response("NOT_FOUND", {}, "not_found")

    email = QueryBuilderService("core_customers").leftJoin("core_contacts as ct", "ct.id", "core_customers.primary_contact_id") \
        .select("ct.email") \
        .where("core_customers.id", id) \
        .first()

    if email is None or email.get("email") is None:
        return ResponseService.response("SUCCESS", {}, "customer_primary_contact_email_not_found")

    return ResponseService.response("SUCCESS", email, "Account configuration fetched successfully.")



def _send_invitation_email_via_gmail(invitation, template_name, subject):
    """
    Send customer invitation email using Gmail API (same method as send_chatmail_message).
    This is more reliable than the external email API.
    """
    try:
        # Get frontend URL for invitation link
        frontend_url = settings.CUSTOMER_FRONTEND_BASE_URL
        if not frontend_url:
            return False, "CUSTOMER_FRONTEND_BASE_URL is not configured in settings"
        
        # Build invitation link
        invitation_link = f"{frontend_url}/invitation?portal_id={invitation.portal_id}&email={invitation.email}&idp_customer_id={invitation.idp_customer_id}&token={invitation.token}&is_enrolled={invitation.is_enrolled}&invitation={invitation.uid}"
        
        # Render email template
        try:
            email_content = render_to_string(
                template_name, {"invitation_link": invitation_link}
            )
        except Exception as e:
            logger.error(f"Error rendering email template: {e}")
            return False, f"Failed to render email template: {str(e)}"
        
        # Get default system email from Gmail credentials
        try:
            gmail_credential_row = (
                QueryBuilderService("core_gmailcredential")
                .select("system_email", "id")
                .orderBy("id", "asc")
                .first()
            )
            if not gmail_credential_row or not gmail_credential_row.get("system_email"):
                return False, "No Gmail credentials found. Please connect a Gmail account first."
            
            from_email = gmail_credential_row["system_email"]
            
            # Get Gmail credential object
            cred = GmailCredential.objects.get(system_email=from_email)
            # Ensure token is fresh before using it
            cred = ensure_fresh_token(cred)
            
        except GmailCredential.DoesNotExist:
            return False, f"Gmail account {from_email} is not connected. Please connect your Gmail account first."
        except Exception as e:
            logger.error(f"Error getting Gmail credential: {e}")
            return False, f"Failed to get Gmail credential: {str(e)}"
        
        # Validate email addresses
        to_email = invitation.email
        if not from_email or not to_email:
            return False, f"Invalid email addresses: from_email='{from_email}', to_email='{to_email}'"
        
        # Send email via Gmail API (same method as send_chatmail_message)
        try:
            logger.info(f"[send_invitation_email_via_gmail] Sending invitation email from {from_email} to {to_email}")
            gmail_response = svc.send_email(
                credential=cred,
                to_email=to_email,
                subject=subject,
                body=email_content,
                thread_id=None,  # New conversation, no thread
                reply_to_message_id=None,  # Not a reply
                attachments=None  # No attachments for invitations
            )
            
            logger.info(f"[send_invitation_email_via_gmail] Email sent successfully. Message ID: {gmail_response.get('id')}")
            return True, None
            
        except Exception as e:
            logger.error(f"[send_invitation_email_via_gmail] Email sending failed: {str(e)}")
            return False, f"Failed to send email via Gmail API: {str(e)}"
            
    except Exception as e:
        logger.error(f"[send_invitation_email_via_gmail] Unexpected error: {str(e)}")
        return False, f"Unexpected error: {str(e)}"

def _safe_convert_contact_no(contact_no):
    """
    Safely convert contact_no to integer or None.
    Handles strings, integers, and values that exceed integer limits.
    """
    if contact_no is None:
        return None
    
    # Convert to string first to handle both string and int inputs
    contact_str = str(contact_no).strip()
    
    # Return None if empty
    if not contact_str or contact_str == "":
        return None
    
    # Try to convert to integer
    try:
        # Check if it's within integer range (MySQL INT max: 2,147,483,647)
        contact_int = int(contact_str)
        # MySQL INTEGER max value
        max_int = 2147483647
        if contact_int > max_int:
            print(f"Warning: contact_no {contact_str} exceeds integer limit, setting to None")
            return None
        return contact_int
    except (ValueError, OverflowError):
        print(f"Warning: Could not convert contact_no '{contact_str}' to integer, setting to None")
        return None

def perform_account_configuration_direct(name, email, customer_id, contact_no=None):
    """
    Direct function to perform account configuration logic without HTTP request overhead.
    Returns a dictionary with success status and any error messages.
    """
    try:
        # Validate email is provided
        if not email or not email.strip():
            return {
                "success": False,
                "error": "Email is required for account configuration"
            }
        
        # Safely convert contact_no
        contact_no = _safe_convert_contact_no(contact_no)
        
        # Check if invitation already exists for this email and customer
        existing_invitation = CustomerInvitation.objects.filter(
            email=email, 
            customer_id=customer_id
        ).first()
        
        if existing_invitation:
            print(f"Invitation already exists for email {email} and customer {customer_id}")
            return {
                "success": True,
                "uid": str(existing_invitation.uid),
                "message": "Invitation already exists"
            }
        
        # Customer registration
        registration_response = customer_registerion(name, email)
        print("............registration_response.......", registration_response)
        if not registration_response or not registration_response.get("is_success", False):
            return {
                "success": False,
                "error": registration_response.get("message", "Registration failed.")
            }

        # Update idp_customer_id in core_customers
        try:
            user_id = None
            if (
                registration_response.get("result")
                and registration_response["result"].get("users")
                and len(registration_response["result"]["users"]) > 0
            ):
                user_id = registration_response["result"]["users"][0].get("id")
            if user_id:
                Customer.objects.filter(id=customer_id).update(idp_customer_id=user_id)
        except Exception as e:
            print("Failed to update idp_customer_id:", e)
            return {
                "success": False,
                "error": f"Failed to update idp_customer_id: {str(e)}"
            }

        # Generate auth key and restore credentials
        # Try to get token from credentials restore, but fallback to registration token if it fails
        token = None
        auth_key_response = generate_auth_key()
        print("............generate_auth_key.......", auth_key_response)

        credentials_restore_response = credentials_restore(auth_key_response, email)
        print("............credentials_restore.......", credentials_restore_response)
        
        # Extract token from credentials restore response if successful
        if credentials_restore_response.get("is_success"):
            token = credentials_restore_response.get("token")
        
        # Fallback: Use token from registration response if credentials restore failed
        if not token and registration_response.get("result") and registration_response["result"].get("users"):
            user_data = registration_response["result"]["users"][0]
            if user_data.get("token") and isinstance(user_data.get("token"), dict):
                token = user_data["token"].get("token")
            elif isinstance(user_data.get("token"), str):
                token = user_data.get("token")
        
        print("............final_token.......", token)

        # Create invitation
        try:
            # contact_no is already converted at the beginning of the function
            invitation = CustomerInvitation.objects.create(
                name=name,
                email=email,
                contact_no=contact_no,  # Already converted to int or None
                customer_id=customer_id,
            )
        except Exception as e:
            print("Invitation creation error:", e)
            # Check if it's a unique constraint error for email
            if "unique" in str(e).lower() and "email" in str(e).lower():
                # Try to find existing invitation
                existing_invitation = CustomerInvitation.objects.filter(
                    email=email, 
                    customer_id=customer_id
                ).first()
                if existing_invitation:
                    print(f"Using existing invitation for email {email}")
                    invitation = existing_invitation
                else:
                    return {
                        "success": False,
                        "error": f"Email {email} is already registered for another customer"
                    }
            else:
                return {
                    "success": False,
                    "error": str(e)
                }

        if invitation is None:
            return {
                "success": False,
                "error": "Failed to create invitation"
            }

        # Get portal details
        portal_id = (
            QueryBuilderService("core_customers").select("portal_id", "idp_customer_id", "is_enrolled").where("id", customer_id).first()
        )
        if not portal_id:
            return {
                "success": False,
                "error": "customer_not_found"
            }

        invitation.portal_id = portal_id.get("portal_id", None)
        invitation.idp_customer_id = portal_id.get("idp_customer_id", None)
        invitation.is_enrolled = portal_id.get("is_enrolled", False)
        
        # Token is already extracted above (with fallback to registration token)
        invitation.token = token
        print("token,enrolled", token, invitation.is_enrolled)
        
        # Save the invitation with updated fields
        invitation.save()
        
        # Send invitation email using Gmail API (same method as send_chatmail_message)
        try:
            send_success, send_error = _send_invitation_email_via_gmail(
                invitation, "invitation_email_template.html", "You're Invited!"
            )
            if not send_success:
                logger.error(f"Email sending failed: {send_error}")
                return {
                    "success": False,
                    "error": send_error or "Failed to send invitation email"
                }
            logger.info(f"Invitation email sent successfully to {invitation.email}")
        except Exception as e:
            logger.error(f"Email sending error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
        
        print("Returning success response with invitation uid:", invitation.uid)
        return {
            "success": True,
            "uid": str(invitation.uid)
        }
        
    except Exception as e:
        print("Account configuration error:", e)
        return {
            "success": False,
            "error": str(e)
        }

@api_view(["POST"])
def account_configuration(request):
    data = json.loads(request.body)

    rules = {
        "name": "required|max:50",
        "email": "required|email|unique:core_customer_invitations,email",
        # "contact_no": "nullable",
        "customer_id": "required|exists:core_customers,id",
    }

    custom_messages = {
        "name.required": "Name cannot be empty.",
        "email.required": "Email cannot be empty.",
        "email.unique": "This email is already registered.",
        "customer_id.required": "Customer ID is required.",
    }
    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    email = data.get("email", "")
    name  = data.get("name", "")
    registration_response = customer_registerion(name, email,)
    print("............registration_response.......",registration_response)
    if not registration_response or not registration_response.get("is_success", False):
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": registration_response.get("message", "Registration failed.")},
            "Customer Registration Error"
        )

    # Update idp_customer_id in core_customers
    try:
        user_id = None
        if (
            registration_response.get("result")
            and registration_response["result"].get("users")
            and len(registration_response["result"]["users"]) > 0
        ):
            user_id = registration_response["result"]["users"][0].get("id")
        if user_id:
            Customer.objects.filter(id=data["customer_id"]).update(idp_customer_id=user_id)
    except Exception as e:
        print("Failed to update idp_customer_id:", e)
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": f"Failed to update idp_customer_id: {str(e)}"},
            "Customer Update Error"
        )


    # reset_password_response = customer_reset_password(data["email"])
    # print("............reset_password_response.......",reset_password_response)
    # if not reset_password_response or not reset_password_response.get("is_success", False):
    #     return ResponseService.response(
    #         "INTERNAL_SERVER_ERROR",
    #         {"error": reset_password_response.get("message", "Reset password failed.")},
    #         "Customer Reset Password Error"
    #     )

    auth_key_response = generate_auth_key()
    print("............generate_auth_key.......", auth_key_response)

    credentials_restore_response = credentials_restore(auth_key_response, email)
    print("............credentials_restore.......", credentials_restore_response)


    try:
        # Safely convert contact_no to integer or None
        safe_contact_no = _safe_convert_contact_no(data.get("contact_no", None))
        invitation = CustomerInvitation.objects.create(
            name=data["name"],
            email=data["email"],
            contact_no=safe_contact_no,
            customer_id=data.get("customer_id", None),
        )
    except Exception as e:
        print("Invitation creation error:", e)
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Invitation Creation Error")

    if invitation is None:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": "Failed to create invitation"}, "Invitation Creation Error")

    portal_id =  (
        QueryBuilderService("core_customers").select("portal_id","idp_customer_id","is_enrolled").where("id", data["customer_id"]).first()
    )
    if not portal_id:
        return ResponseService.response("NOT_FOUND", {}, "customer_not_found")

    invitation.portal_id = portal_id.get("portal_id", None)
    invitation.idp_customer_id = portal_id.get("idp_customer_id", None)
    invitation.is_enrolled = portal_id.get("is_enrolled", False)
    
    # Extract token from credentials restore response
    token = None
    
    if credentials_restore_response.get("is_success"):
        token = credentials_restore_response.get("token")
   
    invitation.token = token  
    print("token,enrolled", token, invitation.is_enrolled)
    
    try:
        # Use Gmail API for sending (same method as send_chatmail_message)
        send_success, send_error = _send_invitation_email_via_gmail(
            invitation, "invitation_email_template.html", "You're Invited!"
        )
        if not send_success:
            logger.error(f"Email sending failed: {send_error}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", {"error": send_error or "Failed to send invitation email"}, "Email Sending Error"
            )
    except Exception as e:
        logger.error(f"Email sending error: {str(e)}")
        import traceback
        traceback.print_exc()
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Email Sending Error"
        )
    
    try:
        print("Returning success response with invitation uid:", invitation.uid)
        
        return ResponseService.response("SUCCESS", {"uid": str(invitation.uid)}, "invitation_sent_successfully")
    except Exception as e:
        print("Final response error:", e)
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Final Response Error")

CUSTOMER_REGISTRATION_API_URL = settings.CUSTOMER_REGISTRATION_API_URL

def customer_registerion(name, email):
    """
    Sends a registration POST request to the external CUSTOMER_REGISTRATION_API_URL
    with the provided name and email from the request body, wrapped in a 'users' object.
    """
    try:
        # Validate that CUSTOMER_REGISTRATION_API_URL is configured
        if not CUSTOMER_REGISTRATION_API_URL:
            return {
                "is_success": False,
                "message": "CUSTOMER_REGISTRATION_API_URL is not configured in settings"
            }
        
        payload = {
            "users": {
                "name": name,
                "email": email
            }
        }
        headers = {
            "Content-Type": "application/json",
            "Expect": ""
        }
        print(headers, payload)
        print("CUSTOMER_REGISTRATION_API_URL:", CUSTOMER_REGISTRATION_API_URL)
        response = requests.post(
            CUSTOMER_REGISTRATION_API_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
        print("registration response:", response.json())
        try:
            return response.json() if response.content else {"is_success": False, "message": "No content"}
        except ValueError:
            return {"is_success": False, "message": "Invalid JSON response from registration API"}
    except Exception as e:
        return {"is_success": False, "message": str(e)}
    
CUSTOMER_RESET_PASSWAORD_API_URL = settings.CUSTOMER_RESET_PASSWAORD_API_URL
CUSTOMER_FRONTEND_BASE_URL = settings.CUSTOMER_FRONTEND_BASE_URL

GENERATE_AUTH_KEY_API_URL = settings.GENERATE_AUTH_KEY_API_URL
CREDENTIALS_RESTORE_API_URL = settings.CREDENTIALS_RESTORE_API_URL

def generate_auth_key():
    try:
        # Validate that GENERATE_AUTH_KEY_API_URL is configured
        if not GENERATE_AUTH_KEY_API_URL:
            return {
                "is_success": False,
                "message": "GENERATE_AUTH_KEY_API_URL is not configured in settings"
            }
        
        idp_backend_app_secret_key = settings.IDP_BACKEND_APP_SECRET_KEY
        sp_code = settings.CUSTOMER_SP_CODE
        
        headers = {
            "x-app-key": idp_backend_app_secret_key,
            "x-sp-code": sp_code,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            GENERATE_AUTH_KEY_API_URL,
            headers=headers,
            timeout=10,
        )
        
        if response.status_code == 200:
            response_data = response.json()
            # Extract token from response (valid for 2 minutes)
            token = response_data.get("token") or response_data.get("result", {}).get("token")
            return {
                "is_success": True, 
                "token": token,
                "message": "Auth key generated successfully"
            }
        else:
            return {
                "is_success": False, 
                "message": f"Failed to generate auth key. Status: {response.status_code}"
            }
            
    except Exception as e:
        return {"is_success": False, "message": str(e)}

def credentials_restore(auth_key_response, email):
    try:
        # Validate that CREDENTIALS_RESTORE_API_URL is configured
        if not CREDENTIALS_RESTORE_API_URL:
            return {
                "is_success": False,
                "message": "CREDENTIALS_RESTORE_API_URL is not configured in settings"
            }
        
        sp_code = settings.CUSTOMER_SP_CODE
        
        # Extract token from auth key response
        if not auth_key_response.get("is_success") or not auth_key_response.get("token"):
            return {
                "is_success": False, 
                "message": "Invalid auth key response or missing token"
            }
        
        secret_token = auth_key_response.get("token")
        
        headers = {
            "x-secret-token": secret_token,
            "x-sp-code": sp_code,
            "Content-Type": "application/json"
        }
        
        payload = {
            "email": email
        }
        
        response = requests.post(
            CREDENTIALS_RESTORE_API_URL,
            json=payload,
            headers=headers,
            timeout=10,
        )
        
        if response.status_code == 200:
            response_data = response.json()
            # Extract token from credentials restore response
            token = response_data.get("token") or response_data.get("result", {}).get("token")
            return {
                "is_success": True,
                "token": token,
                "message": "Credentials restored successfully"
            }
        else:
            return {
                "is_success": False,
                "message": f"Failed to restore credentials. Status: {response.status_code}"
            }
            
    except Exception as e:
        return {"is_success": False, "message": str(e)}


# def customer_reset_password(email):
#     try:
#         # Check if CUSTOMER_FRONTEND_BASE_URL is configured
#         if not CUSTOMER_FRONTEND_BASE_URL:
#             return {"is_success": False, "message": "CUSTOMER_FRONTEND_BASE_URL is not configured in settings"}
#         print("CUSTOMER_FRONTEND_BASE_URL", CUSTOMER_FRONTEND_BASE_URL)
#         payload = {
#             "email": email,
#             "sp": "en_customer",
#             "redirect": "https://dev-customer.envoy.apptimus.lk"
#             # "redirect": CUSTOMER_FRONTEND_BASE_URL
#         }
#         headers = {
#             "Content-Type": "application/json",
#             "Expect": ""
#         }
#         print("headers, payload",headers, payload)
#         print("CUSTOMER_RESET_PASSWAORD_API_URL", CUSTOMER_RESET_PASSWAORD_API_URL)
#         response = requests.post(
#             CUSTOMER_RESET_PASSWAORD_API_URL,
#             json=payload,
#             headers=headers,
#             timeout=10,
#         )
#         response.raise_for_status()
#         print("registration response:", response.json())
#         try:
#             return response.json() if response.content else {"is_success": False, "message": "No content"}
#         except ValueError:
#             return {"is_success": False, "message": "Invalid JSON response from API"}
#     except Exception as e:
#         return {"is_success": False, "message": str(e)}

@api_view(["GET", "PUT", "DELETE"])
def account_detail(request, id):
    if request.method == "GET":
        return get_account(request, id)
    elif request.method == "PUT":
        return update_account(request, id)
    elif request.method == "DELETE":
        return delete_account(request, id)

def get_account(request, id):
    try:
        account = (
            QueryBuilderService("core_customers as c")
            .select(
                "c.id",
                "c.entity_id",
                "c.code",
                "c.type",
                "c.name",
                "c.logo",
                "c.remarks",
                "c.parent_id",
                "c.primary_contact_id",
                "ct.name as primary_contact_name",
                "ct.address as address",
                "ct.primary_contact as primary_contact_number",
                "ct.secondary_contact",
                "ct.email as email",
                "ct.picture as picture",
                "ct.duplicated_contact_id as duplicated_contact_id",
                "ct.website_url as website_url",
            )
            .leftJoin("core_contacts as ct", "ct.id", "c.primary_contact_id")
            .where("c.id", id)
            .first()
        )

        if not account:
            return ResponseService.response(
                "NOT_FOUND", {"error": f"Account with id {id} does not exist"}, "Not Found"
            )

        # Restructure response
        result = {
            "id": account["id"],
            "code": account["code"],
            "entity_id": account["entity_id"],
            "type": account["type"],
            "name": account["name"],
            "logo": account["logo"],
            "remarks": account["remarks"],
            "parent_id": account["parent_id"],
            "primary_contact_id": account["primary_contact_id"],
            "primary_contact": {
                "name": account["primary_contact_name"],
                "primary_contact": account["primary_contact_number"],
                "secondary_contact": account["secondary_contact"],
                "email": account["email"],
                "address": account["address"],
                "picture": account["picture"],
                "duplicated_contact_id": account["duplicated_contact_id"],
                "website_url": account["website_url"],
            }
        }

        return ResponseService.response(
            "SUCCESS", result, "Account fetched successfully"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred"
        )


def update_account(request, id):
    try:
        account = Customer.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "name": "required|max:200",
            "primary_contact": "required|max:20",
            # "primary_contact": "required_without:primary_contact_id|max:20",
            "primary_contact_id": "nullable|exists:core_contacts,id",
            "parent_id": "nullable|exists:core_customers,id",
            "logo": "nullable",
            "remarks": "nullable",
            "email": "nullable|email|max:255",
            "address": "nullable|max:255",
            "secondary_contact": "nullable|max:20",
            # "website_url": "nullable|url",
        }

        custom_messages = {
            "name.required": "Name is required.",
            "primary_contact.required": "Primary contact is required",
            "primary_contact.max": "Primary contact cannot exceed 20 characters.",
            "primary_contact_id.exists": "The provided primary contact ID does not exist.",
            "parent_id.exists": "The provided parent ID does not exist.",
            "email.email": "Invalid email format.",
            "address.max": "Address cannot exceed 255 characters.",
            "secondary_contact.max": "Secondary contact cannot exceed 20 characters.",
            # "website_url.url": "Invalid URL format.",
        }

        validation_errors = ValidatorService.validate(data, rules, custom_messages)
        if validation_errors:
            return ResponseService.response(
                "VALIDATION_ERROR", validation_errors, "Validation Error"
            )

        validated_data = data

        # Update or create primary contact
        if validated_data.get("primary_contact_id"):
            primary_contact = Contact.objects.filter(id=validated_data["primary_contact_id"]).first()
            if not primary_contact:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"primary_contact_id": ["The specified primary contact does not exist."]},
                    "Validation Error",
                )
        else:
            # Create or update contact inline (if account already had one)
            if account.primary_contact:
                primary_contact = account.primary_contact
                primary_contact.name = validated_data["name"]
                primary_contact.primary_contact = validated_data["primary_contact"]
                primary_contact.email = validated_data.get("email", "")
                primary_contact.address = validated_data.get("address", "")
                primary_contact.secondary_contact = validated_data.get("secondary_contact", "")
                primary_contact.website_url = validated_data.get("website_url", "")
                primary_contact.save()
            else:
                primary_contact = Contact.objects.create(
                    name=validated_data["name"],
                    primary_contact=validated_data["primary_contact"],
                    show_in_list=False,
                    email=validated_data.get("email", ""),
                    address=validated_data.get("address", ""),
                    secondary_contact=validated_data.get("secondary_contact", ""),
                    website_url=validated_data.get("website_url", ""),
                )

        parent_account = Customer.objects.filter(id=validated_data.get("parent_id")).first()

        # Update the account
        account.name = validated_data["name"]
        account.logo = validated_data.get("logo", account.logo)
        account.remarks = validated_data.get("remarks", account.remarks)
        account.parent = parent_account
        account.primary_contact = primary_contact
        account.save()

        # 🔁Update flex field values
        flex_fields_data = validated_data.get("flex_fields", {})
        if flex_fields_data and account.entity:
            EntityService.update(
    action={"entity": "customer"},
    entity_id=account.entity.id,
    data=flex_fields_data,
    user=request.user
)



        updated_data = {
            "id": account.id,
            "code": account.code,
            "type": account.type,
            "name": account.name,
            "logo": account.logo,
            "remarks": account.remarks,
            "parent_id": account.parent.id if account.parent else None,
            "primary_contact_id": account.primary_contact.id if account.primary_contact else None,
        }
        user = request.user
        print("user",user.id)
        
        # Enhanced NotificationService call with policy details
        try:
            # Get policy information for this customer
            policy_details = QueryBuilderService("crmp_issued_policies as ip") \
                .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id") \
                .leftJoin("core_products as p", "p.id", "pb.product_id") \
                .select(
                    "ip.id as policy_id",
                    "ip.brokerage_policy_id",
                    "p.name as product_name",
                    "pb.premium_amount",
                    "pb.sum_insured",
                    "pb.policy_start_date",
                    "pb.policy_expiry_date"
                ) \
                .where("pb.customer_id", id) \
                .get()
            
            # Prepare notification message with policy details
            notification_message = f"Customer data has been updated for {account.name}"
            
            # Add policy details to message if policies exist
            if policy_details and len(policy_details) > 0:
                policy_info = []
                for policy in policy_details:
                    policy_info.append(
                        f"Policy: {policy.get('brokerage_policy_id', 'N/A')} | "
                        f"Product: {policy.get('product_name', 'N/A')} | "
                        f"Start: {policy.get('policy_start_date', 'N/A')} | "
                        f"Expiry: {policy.get('policy_expiry_date', 'N/A')} | "
                        f"Premium: {policy.get('premium_amount', 'N/A')} | "
                        f"Sum Insured: {policy.get('sum_insured', 'N/A')}"
                    )
                notification_message += f". Related policies: {'; '.join(policy_info)}"
            else:
                notification_message += ". No related policies found."
            
            # Prepare metadata with customer and policy details
            notification_metadata = {
                "customer_id": id,
                "customer_name": account.name,
                "updated_fields": list(validated_data.keys()),
                "policies": policy_details if policy_details else []
            }
            
            NotificationService.generate_notification(
                type_code="customer_update",
                title="Customer Data Updated",
                meta_data=notification_metadata,
                message=notification_message,
                customer_id=id,
                user_id=(user.id if getattr(user, 'id', None) else None)
            )
        except Exception as notify_exc:
            print(f"NotificationService error: {notify_exc}")

        return ResponseService.response(
            "SUCCESS", message="default_update_success_msg", result=updated_data
        )

    except Customer.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", {"error": f"Account with id {id} does not exist"}, "Not Found"
        )
    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred"
        )


def delete_account(request, id):
    try:
        account = Customer.objects.get(id=id)
        account.delete()
        return ResponseService.response(
            "SUCCESS", message="default_delete_success_msg"
        )
    except Customer.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", {"error": f"Account with id {id} does not exist"}, "Not Found"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred"
        )



@api_view(["GET", "POST"])
def get_customer_contact(request, id):
    if request.method == "GET":
        return get_customer_contacts(request, id)
    elif request.method == "POST":
        return store_customer_contact(request, id)


# --------------------------------------------------------
# GET /customers/{id}/contacts - Get All Contacts for a Customer
def get_customer_contacts(request, id):
    try:
        customer = Customer.objects.get(id=id)

        # ---------------------Query Parameters--------------------------------
        filter_json = request.GET.get("filter", {})  # Filtering conditions
        search_string = request.GET.get("search", "")  # Search query
        page = int(request.GET.get("page", 1))  # Pagination: Page number
        limit = int(request.GET.get("limit", 10))  # Pagination: Records per page
        
        # Handle empty string values for sorting
        sort_by = request.GET.get("sort_by", "core_customer_contacts.id")
        sort_by = "core_customer_contacts.id" if sort_by in [None, ""] else sort_by
        sort_dir = request.GET.get("sort_dir", "desc")
        # Always default to descending order if not explicitly set to 'asc'
        sort_dir = "desc" if sort_dir not in ["asc"] else sort_dir

        # ---------------------Allowed Filters & Sorting--------------------------------
        all_columns = [
            "core_contacts.id",
            "core_customer_contacts.title",
            "core_contacts.name",
            "core_contacts.email",
            "core_contacts.primary_contact",
            "core_contacts.secondary_contact",
            "core_contacts.remarks",
            "core_customer_contacts.is_primary"
        ]
        allowed_filters = ["core_contacts.name", "core_contacts.email"]
        search_columns = ["core_contacts.name", "core_contacts.email"]
        allowed_sorting_columns = ["core_customer_contacts.id", "core_contacts.id", "core_contacts.name", "core_contacts.email"]

        # ---------------------Query Execution--------------------------------
        query = (
            QueryBuilderService("core_customer_contacts")
            .leftJoin("core_contacts", "core_contacts.id", "core_customer_contacts.contact_id") 
            .select(*all_columns)
            .where("core_customer_contacts.customer_id", customer.id)
            .apply_conditions(
                filter_json, allowed_filters, search_string, search_columns
            )
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

       
        # ---------------------Response Data--------------------------------
        # response_data = {
        #     # "current_page": page,
        #     # "total_records": len(query),
        #     # "count": limit,
        #     "data": query,
        # }

        return ResponseService.response(
            "SUCCESS",
            message="Contacts fetched successfully.",
            result=query,
        )

    except Customer.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", f"Customer with ID {id} does not exist", "Not Found"
        )
    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


# --------------------------------------------------------
# POST /customers/{id}/contacts - Assign a Contact to a Customer
def store_customer_contact(request, id):
    try:
        customer = Customer.objects.get(id=id)
        data = json.loads(request.body)

        rules = {"contact_id": "required|exists:core_contacts,id"}

        custom_messages = {
            "contact_id.required": "Contact ID is required.",
            "contact_id.exists": "The provided contact ID does not exist.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        contact = Contact.objects.get(id=data["contact_id"])

        # Check if the contact is already assigned to the same customer
        if CustomerAdditionalContact.objects.filter(customer=customer, contact=contact).exists():
            return ResponseService.response(
                "CONFLICT",
                None,
                "customer_contact_conflict_error_msg",
                "CUSTOMER_CONTACT_ALREADY_ADDED"
            )
        
        # Set is_primary to False if not provided
        is_primary = data.get("is_primary", False)

        # If is_primary is True, update any existing primary contact for this customer to False
        if is_primary:
            CustomerAdditionalContact.objects.filter(customer=customer, is_primary=True).update(is_primary=False)

        # Create a new CustomerAdditionalContact entry
        CustomerAdditionalContact.objects.create(
            customer=customer, contact=contact, title="Additional Contact",is_primary = is_primary
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "customer_id": customer.id,
                "contact": {
                    "id": contact.id,
                    "name": contact.name,
                    "email": contact.email,
                    "primary_contact": contact.primary_contact,
                },
            },
            "contact_assigned_to_customer_successfully",
        )

    except Customer.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", None, f"Customer with ID {id} does not exist"
        )
    except Contact.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND",
            None,
            f"Contact with ID {data.get('contact_id')} does not exist",
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )


@api_view(["DELETE"])
def delete_customer_contact(request, id, contact_id):
    try:
        data = {"customer_id": id, "contact_id": contact_id}

        rules = {
            "customer_id": "required|exists:core_customers,id",
            "contact_id": "required|exists:core_contacts,id",
        }

        custom_messages = {
            "customer_id.required": "Customer ID is required.",
            "customer_id.exists": "The provided customer ID does not exist.",
            "contact_id.required": "Contact ID is required.",
            "contact_id.exists": "The provided contact ID does not exist.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        customer = Customer.objects.get(id=id)
        contact = Contact.objects.get(id=contact_id)

        # Remove from CustomerAdditionalContact table
        deleted_count, _ = CustomerAdditionalContact.objects.filter(
            customer=customer, contact=contact
        ).delete()

        if deleted_count == 0:
            return ResponseService.response(
                "NOT_FOUND", None, "Contact not associated with this customer"
            )

        return ResponseService.response(
            "SUCCESS",
            None,
            "default_delete_success_msg",
        )

    except Customer.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", None, f"Customer with ID {id} does not exist"
        )
    except Contact.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", None, f"Contact with ID {contact_id} does not exist"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )



@api_view(["POST", "DELETE"])
def account_hierarchy(request, id):
    if request.method == "POST":
        return store_account_hierarchy(request, id)
    elif request.method == "DELETE":
        return delete_account_hierarchy(request, id)


# --------------------------------------------------------
# POST /accounts/{id}/hierarchies - Assign Parent Account
def store_account_hierarchy(request, id):
    try:
        
        parent_account = get_object_or_404(Customer, id=id)
        data = json.loads(request.body)

    
        rules = {
            "parent_id": "required|exists:core_customers,id",
            "child_id": "required|exists:core_customers,id",
        }

        custom_messages = {
            "parent_id.required": "Parent ID is required.",
            "parent_id.exists": "The provided parent account ID does not exist.",
            "child_id.required": "Child ID is required.",
            "child_id.exists": "The provided child account ID does not exist.",
        }

    
        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        
        child_account = get_object_or_404(Customer, id=data["child_id"])
        child_account.parent = parent_account
        child_account.save(update_fields=["parent"])

        return ResponseService.response(
            "SUCCESS",
            {
                "child_id": child_account.id,
                "child_name": child_account.name,
                "new_parent_id": parent_account.id,
                "new_parent_name": parent_account.name,
            },
            "default_create_success_msg",
        )

    except ValidationError as e:
        return ResponseService.response("VALIDATION_ERROR", e.message_dict, "Validation Error")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "An unexpected error occurred."
        )




# --------------------------------------------------------
# DELETE /accounts/{id}/hierarchies - Remove Parent Account
def delete_account_hierarchy(request, id):
    try:
        
        account = get_object_or_404(Customer, id=id)

        
        if account.parent is None:
            return ResponseService.response(
                "SUCCESS", {"account_id": account.id}, "No parent hierarchy to remove."
            )

       
        account.parent = None
        account.save(update_fields=["parent_id"])

        return ResponseService.response(
            "SUCCESS", {"account_id": account.id}, "default_delete_success_msg"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "An unexpected error occurred."
        )

def build_hierarchy(node, visited=None, depth=0, max_depth=10):
    if visited is None:
        visited = set()

    if node.id in visited or depth > max_depth:
        return None

    visited.add(node.id)

    return {
        "id": node.id,
        "code": node.code,
        "name": node.name,
        "type": node.type,
        "parent_id": node.parent.id if node.parent else None,
        "children": [build_hierarchy(child, visited, depth + 1, max_depth) for child in node.children.all() if child.id not in visited],
    }

@api_view(["GET"])
def get_account_hierarchies(request):
    try:
        node_id = request.GET.get("node_id")

        if not node_id:
            # Get top-level accounts if no ID is provided
            root_accounts = Customer.objects.filter(parent_id=None).prefetch_related("children")
            hierarchies = [build_hierarchy(account) for account in root_accounts]
            return ResponseService.response(
                "SUCCESS", message="Account hierarchy fetched successfully.", result=hierarchies
            )

        # Get the target node
        customer = get_object_or_404(Customer, id=node_id)

        # Go up the chain to the root parent
        root = customer
        while root.parent is not None:
            root = root.parent

        # Build hierarchy from the top-most parent (root)
        hierarchy = build_hierarchy(root)

        return ResponseService.response(
            "SUCCESS", message="Account hierarchy fetched successfully.", result=[hierarchy]
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


@api_view(["PATCH"])
def update_primary_contact(request, id, contact_id):
    """
    Set a contact as the primary contact for a customer.
    Example: PATCH /customers/{id}/contacts/{contact_id}/primary
    """
    try:
        # Step 1: Validate `customer_id` exists in `core_customer_contacts`
        rules = {"id": "required|exists:core_customer_contacts,customer_id"}
        errors = ValidatorService.validate({"id": id}, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Step 2: Validate `contact_id` belongs to `customer_id`
        contact_exists = QueryBuilderService("core_customer_contacts") \
            .select("contact_id") \
            .where("customer_id", id) \
            .where("contact_id", contact_id) \
            .first()

        if not contact_exists:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"contact_id": [{"error_type": "exists", "tokens": {"_attribute": "contact_id"}}]},
                "Validation Error"
            )

        # Step 3: Get all contacts linked to this `customer_id`
        customer_contacts = QueryBuilderService("core_customer_contacts") \
            .select("contact_id") \
            .where("customer_id", id) \
            .get()

        if not customer_contacts:
            return ResponseService.response("NOT_FOUND", None, f"No contacts found for Customer ID {id}.")

        # Step 4: Set `is_primary = False` for all customer contacts
        contact_ids = [contact["contact_id"] for contact in customer_contacts]
        QueryBuilderService("core_customer_contacts") \
            .whereIn("contact_id", contact_ids) \
            .update({"is_primary": False})

        # Step 5: Set `is_primary = True` only for the selected `contact_id`
        QueryBuilderService("core_customer_contacts") \
            .where("customer_id", id) \
            .where("contact_id", contact_id) \
            .update({"is_primary": True})

        # Step 6: Return success response
        return ResponseService.response(
            "SUCCESS",
            message="Primary contact updated successfully.",
            result={"customer_id": id, "primary_contact_id": contact_id}
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )
    



@api_view(["GET"])
def get_primary_contacts_by_customer_ids(request):
    try:
        ids_param = request.GET.get("ids")
        if not ids_param:
            return ResponseService.response(
                "VALIDATION_ERROR", {"ids": "Customer IDs are required."}, "Validation Error"
            )

        id_list = [int(cid.strip()) for cid in ids_param.split(",") if cid.strip().isdigit()]

        # Fetch primary contacts from CustomerAdditionalContact table using QueryBuilderService
        primary_contacts = (
            QueryBuilderService("core_customer_contacts")
            .select(
                "core_customer_contacts.customer_id",
                "core_customer_contacts.contact_id",
                "core_customer_contacts.title",
                "core_contacts.name",
                "core_contacts.email",
                "core_contacts.primary_contact",
                "core_contacts.secondary_contact",
                "core_contacts.address",
                "core_contacts.website_url",
                "core_contacts.remarks",
                "core_contacts.picture"
            )
            .leftJoin("core_contacts", "core_contacts.id", "core_customer_contacts.contact_id")
            .whereIn("core_customer_contacts.customer_id", id_list)
            .where("core_customer_contacts.is_primary", True)
            .get()
        )

        # Prepare result structure
        result = {}
        for pc in primary_contacts:
            contact_details = {
                "id": pc["contact_id"],
                "name": pc["name"],
                "email": pc["email"],
                "primary_contact": pc["primary_contact"],
                "secondary_contact": pc["secondary_contact"],
                "address": pc["address"],
                "website_url": pc["website_url"],
                "remarks": pc["remarks"],
                "picture": pc["picture"],
                "title": pc["title"],
            }
            if pc["customer_id"] in result:
                result[pc["customer_id"]].append(contact_details)
            else:
                result[pc["customer_id"]] = [contact_details]

        return ResponseService.response(
            "SUCCESS",
            result=result,
            message="Primary contacts fetched successfully."
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )
    

@api_view(["GET"])
def get_customers_by_contact_id(request, id):
    try:
        # Fetch customers from core_customer_contacts table using QueryBuilderService
        customers = (
            QueryBuilderService("core_customer_contacts")
            .select(
                "core_customer_contacts.*",
                "core_customers.id as customer_id",
                "core_customers.name",
                "core_customers.type",
                "core_customers.code",
                "core_customers.logo",
                "core_customers.remarks",
                "core_customers.parent_id",
                "core_customers.primary_contact_id"
            )
            .leftJoin("core_customers", "core_customers.id", "core_customer_contacts.customer_id")
            .where("core_customer_contacts.contact_id", id)
            .get()
        )

        # Prepare result structure
        result = []
        for customer in customers:
            customer_details = {
                "core_customer_contacts": {
                    "id": customer["id"],
                    "customer_id": customer["customer_id"],
                    "contact_id": customer["contact_id"],
                    "title": customer["title"],
                    "is_primary": customer["is_primary"],
                },
                "core_customers": {
                    "id": customer["customer_id"],
                    "name": customer["name"],
                    "type": customer["type"],
                    "code": customer["code"],
                    "logo": customer["logo"],
                    "remarks": customer["remarks"],
                    "parent_id": customer["parent_id"],
                    "primary_contact_id": customer["primary_contact_id"]
                }
            }
            result.append(customer_details)

        return ResponseService.response(
            "SUCCESS",
            result=result,
            message="Customers fetched successfully."
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )



