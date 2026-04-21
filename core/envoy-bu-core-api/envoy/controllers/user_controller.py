from django.http import JsonResponse
from rest_framework.decorators import api_view
import json
from envoy.models import UserInvitation
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
from envoy.models import Role
from envoy.utils import send_invitation_email
from rest_framework.response import Response
import requests
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from envoy.models import User
from envoy.models import Entity
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
import uuid
import random
import string

@api_view(["POST"])
def create_invitations(request):
    data = json.loads(request.body)

    rules = {
        "name": "required|max:50",
        "email": "required|email|unique:core_users,email",
        "role_id": "required|exists:core_roles,id",
    }

    custom_messages = {
        "name.required": "Name cannot be empty.",
        "email.required": "Email cannot be empty.",
        "email.unique": "This email is already registered.",
        "role_id.required": "Role ID is required.",
        "role_id.exists": "Role with the given ID does not exist.",
    }

    try:
        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Check if an invitation already exists for this email
        if UserInvitation.objects.filter(email=data["email"]).exists():
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"email": [{"error_type": "duplicate_invitation", "tokens": {"_attribute": "email"}}]},
                "email_already_has_invitation",
            )

        role = Role.objects.get(id=data.get("role_id"))

        invitation = UserInvitation.objects.create(
            name=data["name"],
            email=data["email"],
            role_id=role.id,
        )
        print("invitation:", invitation)

        # invitation.role = (
        #     QueryBuilderService("core_roles").where("id", role.id).select("core_roles.name").first()
        # )

        print("invitation:", invitation,role)

        send_invitation_email(
            invitation,role, "invitation_email_template.html", "You're Invited!"
        )

        return ResponseService.response("SUCCESS", message="invitation_sent_successfully")

    except ValidationError as e:
        return ResponseService.response("VALIDATION_ERROR", "Validation Error")


EXTERNAL_API_URL = settings.EXTERNAL_API_URL

@api_view(["POST"])
def accept_invitations(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Step 1: Initial validation (only checks if required fields are present)
        rules = {
            "idp_access_token": "required",
            "invitation": "required",
        }

        custom_messages = {
            "idp_access_token.required": "Idp Access Token cannot be empty.",
            "invitation.required": "Invitation ID cannot be empty.",
        }

        try:
            errors = ValidatorService.validate(data, rules, custom_messages)
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )
        except ValidationError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Invitation Not Accepted!",
            )

        user_token = data.get("idp_access_token")
        invitation_uid = data.get("invitation")

        # Step 2: Normalize UUID by removing hyphens
        normalized_invitation_uid = invitation_uid.replace("-", "")

        try:
            # Validate UUID format
            invitation_uuid = uuid.UUID(invitation_uid)
        except ValueError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Invalid Invitation UUID format!"
            )

        # Step 3: Use ValidatorService to check if invitation exists
        rules = {
            "invitation": "exists:core_user_invitations,uid",
        }

        custom_messages = {
            "invitation.exists": "Invitation does not exist.",
        }

        try:
            errors = ValidatorService.validate(
                {"invitation": normalized_invitation_uid}, 
                rules, 
                custom_messages
            )
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )
        except ValidationError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Invitation does not exist!",
            )

        headers = {"Authorization": f"Bearer {user_token}"}

        response = requests.get(EXTERNAL_API_URL, headers=headers)
        try:
            response_data = response.json()
        except ValueError:
            return JsonResponse({"error": "Invalid JSON response from IDP"}, status=500)

        if not response_data.get("is_success") or "result" not in response_data:
            return Response(
                {"error": "Invalid Response from IDP"},
            )

        idp_user_id = response_data["result"]["id"]
        name = response_data["result"]["name"]
        email = response_data["result"]["email"]

        user_data = {
            "idp_user_id": idp_user_id,
            "name": name,
            "email": email,
        }
        user_rules = {
            "idp_user_id": "required",
        }

        user_custom_messages = {
            "idp_user_id.required": "Invalid Idp Id."
        }
        
        try:
            errors = ValidatorService.validate(
                user_data, user_rules, user_custom_messages
            )
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )

            existing_user = User.objects.filter(idp_user_id=idp_user_id).first()

            if existing_user:
                try:
                    valid_invitation = UserInvitation.objects.get(uid=normalized_invitation_uid)
                    valid_invitation.delete()
                except UserInvitation.DoesNotExist:
                    pass
                refresh = RefreshToken.for_user(existing_user)
                return ResponseService.response(
                    "SUCCESS",
                    result={"access_token": str(refresh.access_token),"user": {
            "id": existing_user.id,
            "first_name": existing_user.first_name,
            "display_name": existing_user.display_name,
            "email": existing_user.email,
            "idp_user_id": existing_user.idp_user_id,
            "role": {
                "id": existing_user.role.id if existing_user.role else None,
                "name": existing_user.role.name if existing_user.role else None,
            },
            "entity": {
                "id": existing_user.entity.id if existing_user.entity else None,
                "type": existing_user.entity.type if existing_user.entity else None,
            },
        },},
                    message="Invitation accepted successfully!",
                )

            # Fetch valid invitation (already checked existence above)
            valid_invitation = get_object_or_404(
                UserInvitation, 
                uid=normalized_invitation_uid  # Fetch using the normalized UUID
            )

            role_instance = (
                Role.objects.get(id=valid_invitation.role.id)
                if valid_invitation.role
                else None
            )
            entity_instance, created = Entity.objects.get_or_create(
                id=1, defaults={"type": "Default Entity"}
            )

            user = User.objects.create(
                first_name=name,
                display_name=name,
                email=email,
                idp_user_id=idp_user_id,
                role=role_instance,
                entity=entity_instance,
                code=generate_unique_user_code()
            )

            if user:
                valid_invitation.delete()
                refresh = RefreshToken.for_user(user)
                return ResponseService.response(
                    "SUCCESS",
                    result={"access_token": str(refresh.access_token),"user": {
                "id": user.id,
                "first_name": user.first_name,
                "display_name": user.display_name,
                "email": user.email,
                "idp_user_id": user.idp_user_id,
                "role": {
                    "id": user.role.id if user.role else None,
                    "name": user.role.name if user.role else None,
                },
                "entity": {
                    "id": user.entity.id if user.entity else None,
                    "type": user.entity.type if user.entity else None,
                },
            }},
                    message="invitation_accepted_successfully",
                )

        except ValidationError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Invitation Not Accepted!",
            )
        
@api_view(["GET"])
def get_users(request):
    try:
        #  Fetch query parameters
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        search_string = request.GET.get("search", "")
        raw_filter_json = request.GET.get("filters", '{}')

        #  Define alias map: frontend key => database column
        filter_aliases = {
            "first_name": "core_users.first_name",
            "last_name": "core_users.last_name",
            "display_name": "core_users.display_name",
            "email": "core_users.email",
            "contact_no": "core_users.contact_no",
            "role_id": "core_users.role_id",
            "role_name":"core_roles.name",
            "status_id":"core_users.status_id",
            "team_id":"core_teams.name"
        }

        # Apply alias mapping
        filter_dict = json.loads(raw_filter_json)
        mapped_filter_dict = {
            filter_aliases.get(k, k): v for k, v in filter_dict.items()
        }
        mapped_filter_json = json.dumps(mapped_filter_dict)

        # Allowed columns
        allowed_filters = list(filter_aliases.values())
        search_columns = ["core_users.first_name", "core_users.last_name", "core_users.display_name", "core_status.name", "core_users.email", "core_users.contact_no", "core_roles.name", "core_users.code"]
        allowed_sorting_columns = ["core_users.first_name","core_teams.name", "core_users.last_name","core_users.display_name","core_users.status_id","core_status.name","core_users.email", "core_users.contact_no","core_roles.name","core_users.code"]

        #  Define columns for selection
        all_columns = [
            "core_users.id",
            "core_users.title",
            "core_users.first_name",
            "core_users.last_name",
            "core_users.display_name",
            "core_users.email",
            "core_users.contact_no",
            "core_users.picture",
            "core_users.idp_user_id",
            "core_users.role_id",
            "core_users.entity_id",
            "core_roles.name as role_name",
            "core_entities.type as entity_type",
            "core_status.name as status_name",
            "core_users.status_id",
            "core_users.code",
            "core_teams.name as team_name",
            # "lu.display_name as leader_name"
        ]

        #  Querying the database efficiently using QueryBuilderService
        query = QueryBuilderService("core_users") \
        .select(*all_columns,aggregate_mode=True) \
        .leftJoin("core_roles", "core_roles.id", "core_users.role_id") \
        .leftJoin("core_entities", "core_entities.id", "core_users.entity_id") \
        .leftJoin("core_status", "core_status.id", "core_users.status_id") \
        .leftJoin("core_team_users", "core_team_users.user_id", "core_users.id") \
        .leftJoin("core_teams", "core_teams.id", "core_team_users.team_id") \
        .apply_conditions(mapped_filter_json, allowed_filters, search_string, search_columns) \
        .groupBy("core_users.id") \
        .paginate(page, per_page, allowed_sorting_columns, sort_by, sort_dir)

        # #  Response Handling
        # response_data = {
        #     "current_page": page,
        #     "last_page": query.get("total_pages", 1),
        #     "total_records": query.get("total_count", 0),
        #     "count": len(query.get("data", [])),
        #     "data": query.get("data", [])
        # }

        return ResponseService.response(
            "SUCCESS", query, "Users fetched successfully."
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

    except ValueError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"pagination": ["Invalid pagination parameters"]},
            "Invalid Request"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )

@api_view(["GET", "PUT"])
def user_detail(request, user_id):
    if request.method == "GET":
        try:
            # Check if user exists
            user = User.objects.filter(id=user_id).exists()
            if not user:
                return ResponseService.response("NOT_FOUND", None, "User not found.")

            # QueryBuilderService Columns & Filters
            all_columns = [
            "core_users.id", "core_teams.name as team_name", "core_users.title", 
            "core_users.first_name", "core_users.last_name", "core_users.display_name",
            "core_users.email", "core_users.contact_no", "core_users.picture", 
            "core_users.cover_pic", "core_users.street_address", "core_users.city",
            "core_users.state", "core_users.postal_code", "core_users.county",
            "core_users.idp_user_id", "core_users.role_id AS role_id", 
            "core_users.entity_id AS entity_id", "core_users.code",
            "core_roles.name AS role_name", "core_entities.type AS entity_type",
            "core_users.status_id", "core_status.name as status_name"
            ]

            filter_json = request.GET.get("filter", {})
            search_string = request.GET.get("search", "")
            allowed_filters = ["core_users.first_name", "core_users.last_name","core_users.display_name","core_users.status_id", "core_users.email", "core_users.contact_no"]
            search_columns = ["core_users.first_name", "core_users.last_name","core_users.display_name", "core_users.email", "core_users.contact_no"]
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            sort_by = request.GET.get("sort_by", "id")
            sort_dir = request.GET.get("sort_dir", "desc")
            allowed_sorting_columns = ["core_users.first_name","core_users.code","core_users.last_name","core_users.display_name", "core_users.email", "core_users.contact_no"]

            # Query the Database using QueryBuilderService
            response_data = (
                QueryBuilderService("core_users")
                .select(*all_columns)
                .leftJoin("core_roles", "core_roles.id", "core_users.role_id")
                .leftJoin("core_entities", "core_entities.id", "core_users.entity_id")
                .leftJoin("core_status","core_status.id","core_users.status_id")
                .leftJoin("core_team_users", "core_team_users.user_id", "core_users.id") \
                .leftJoin("core_teams", "core_teams.id", "core_team_users.team_id") \
                .where("core_users.id", user_id)
                .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
            )

            # Extract Data (if exists)
            response_data = response_data["data"][0] if response_data.get("data") else {}

            return ResponseService.response(
                "SUCCESS", response_data, "User fetched successfully."
            )

        except Exception as e:
            return ResponseService.response(
                "ERROR", message="Error fetching user.", result={"error": str(e)}
            )

    elif request.method == "PUT":
        try:
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)
            
            rules = {
                "title": "max:100|required",
                "first_name": "required|max:80",
                "last_name": "max:80",
                "display_name": "required|max:80",
                "email": f"required|email|max:254|unique:core_users,email,{user.id}",
                "contact_no": "max:80",
                "picture": "max:300",
                "cover_pic": "max:300",
                "street_address": "max:255",
                "city": "max:100",
                "state": "max:100",
                "county": "max:100",
                "postal_code": "max:20",
                "role_id": "required|exists:core_roles,id",
                "status_id":"nullable|exists:core_status,id",
                "code":f"nullable|unique:core_users,code,{user.id}",
            }

            custom_messages = {
                "title.max": "Title cannot exceed 100 characters.",
                "title.required": "Title cannot be empty.",
                "first_name.required": "First name cannot be empty.",
                "first_name.max": "First name cannot exceed 80 characters.",
                "last_name.max": "Last name cannot exceed 80 characters.",
                "display_name.required": "Display name cannot be empty.",
                "display_name.max": "Display name cannot exceed 80 characters.",
                "email.required": "Email cannot be empty.",
                "email.email": "Email must be a valid email address.",
                "email.max": "Email cannot exceed 254 characters.",
                "email.unique": "This email is already registered.",
                "contact_no.max": "Contact number cannot exceed 80 characters.",
                "picture.max": "Picture URL cannot exceed 300 characters.",
                "pic.max": "Pic URL cannot exceed 300 characters.",
                "cover_pic.max": "Cover pic URL cannot exceed 300 characters.",
                "street_address.max": "Street address cannot exceed 255 characters.",
                "city.max": "City cannot exceed 100 characters.",
                "state.max": "State cannot exceed 100 characters.",
                "county.max": "County cannot exceed 100 characters.",
                "postal_code.max": "Postal code cannot exceed 20 characters.",
                "role_id.required": "Role ID is required.",
                "role_id.exists": "Role with the given ID does not exist.",
                "status_id.exists":"Status with the given ID does not exit.",
                "code.unique": "This code is already registered.",
            }

            errors = ValidatorService.validate(data, rules, custom_messages)
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )

            user.title = data.get("title", user.title)
            user.first_name = data.get("first_name", user.first_name)
            user.last_name = data.get("last_name", user.last_name)
            user.display_name = data.get("display_name", user.display_name)
            user.email = data.get("email", user.email)
            user.contact_no = data.get("contact_no", user.contact_no)
            user.picture = data.get("picture", user.picture)
            user.cover_pic = data.get("cover_pic", user.cover_pic)
            user.street_address = data.get("street_address", user.street_address)
            user.city = data.get("city", user.city)
            user.state = data.get("state", user.state)
            user.county = data.get("county", user.county)
            user.postal_code = data.get("postal_code", user.postal_code)
            user.status_id = data.get("status_id", user.status_id)
            user.code = data.get("code", user.code)

            role_id = data.get("role_id", user.role.id)
            user.role = Role.objects.get(id=role_id)

            user.entity = user.entity

            user.save()

            return ResponseService.response(
                "SUCCESS",
                result={
                    "id": user.id,
                    "first_name": user.first_name,
                    "display_name": user.display_name,
                    "email": user.email,
                    "idp_user_id": user.idp_user_id,
                    "picture": user.picture,
                    "cover_pic": user.cover_pic,
                    "title": user.title,
                    "contact_no": user.contact_no,
                    "role": {
                        "id": user.role.id if user.role else None,
                        "name": user.role.name if user.role else None,
                    },
                    "entity": {
                        "id": user.entity.id if user.entity else None,
                        "type": user.entity.type if user.entity else None,
                    },
                },
                message="user_updated_successfully",
            )

        except User.DoesNotExist:
            return ResponseService.response(
                "NOT_FOUND", message="User not found.", result=None
            )

        except Role.DoesNotExist:
            return ResponseService.response(
                "VALIDATION_ERROR", message="Invalid Role ID.", result=None
            )

        except ValidationError as e:
            return ResponseService.response(
                "VALIDATION_ERROR", message=str(e), result=None
            )

        except Exception as e:
            return ResponseService.response(
                "ERROR", message="Error updating user.", result={"error": str(e)}
            )

def generate_unique_user_code():
    prefix = "U"
    while True:
        random_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        code = f"{prefix}-{random_code}"
        if not User.objects.filter(code=code).exists():
            return code
