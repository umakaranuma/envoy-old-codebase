from django.http import JsonResponse
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
import json
from rest_framework.decorators import api_view
from envoy.models.entity import Entity
from envoy.models.role import Role
from envoy.models.user import User
from envoy.models.user_invitation import UserInvitation
from envoy.models.action import Action
from envoy.models.role_authority import RoleAuthority
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
from mServices.ValidatorService import ValidatorService
from django.db import transaction

from envoy.services.entity_validator_service import EntityService
# from services.ActionService import ActionService
# from services.AuthService import AuthService


# --------------------------------------------------------
# GET /roles & POST /roles - List all roles or create a new role
@api_view(["GET", "POST"])
def get_roles(request):
    if request.method == "GET":
        # action = ActionService.getAction("Role","VIEW")
        # authority = AuthService.hasAuthority(action)

        # if authority:
            return list_roles(request)
        
        # return ResponseService.response('FORBIDDEN',None,"Unauth")

    elif request.method == "POST":
        return create_role(request)

def list_roles(request):
    try:

        # page = int(request.GET.get("page", 1))
        # per_page = int(request.GET.get("per_page", 10))

        # roles_queryset = Role.objects.all().order_by("id")  
        # paginator = Paginator(roles_queryset, per_page)
        # paginated_roles = paginator.get_page(page)

        # data = [
        #     {
        #         "id": role.id,
        #         "name": role.name,
        #         "description": role.description,
        #         "system_role": role.system_role,
        #         "permissions": list(role.get_permissions().values("id", "action")),
        #     }
        #     for role in paginated_roles
        # ]

        # response_data = {
        #     "current_page": page,
        #     "last_page": paginator.num_pages,
        #     "total_records": paginator.count,
        #     "count": len(paginated_roles),
        #     "data": data,
        # }

        # return ResponseService.response(
        #     "SUCCESS", response_data, "Roles retrieved successfully!"
        # )
    
    
# ---------------------QueryBuilderService--------------------------------
        all_columns = ['core_roles.id','core_roles.name','core_roles.description','core_roles.system_role',]
        filter_json = request.GET.get('filters', '{}') 
        search_string = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        role_detail = Role.objects.all().order_by("id")
        paginator = Paginator(role_detail, limit)
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["name", "description"]
        search_columns = ["name", "description"]
        allowed_sorting_columns = ["name", "description"]

        query = QueryBuilderService("core_roles")\
                .select(*all_columns) \
                .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \
                
        if not query:
            query = []

        return ResponseService.response('SUCCESS',query,"Roles retrieved successfully!")

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

    except ValueError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"pagination": ["Invalid pagination parameters"]},
            "Invalid Request",
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )

def create_role(request):
    data = json.loads(request.body)

    rules = {
        "name": "required|max:255|unique:core_roles,name",
        "description": "max:320",
        "permission_ids": "array",
        "permission_ids.*": "exists:core_actions,id",

    }

    custom_messages = {
        "name.required": "Name cannot be empty.",
        "name.max": "Name cannot exceed 255 characters.",
        "name.unique": "This name is already exists.",
        "permission_ids.array": "Permissions must be a list.",
        "permission_ids.exists": "One or more provided permissions do not exist.",
    }

    try:
        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # entity = Entity.objects.filter(type="ROLE").first()
        # if not entity:
        entity_action = {"entity": "ROLE"}
        entity = EntityService.store(entity_action, None, user=request.user)

        role = Role.objects.create(
            name=data.get("name", None), 
            description=data.get("description", None),
            entity_id=entity.id
        )

        permission_ids = data.get("permission_ids", [])
        valid_actions = Action.objects.filter(id__in=permission_ids)

        RoleAuthority.objects.bulk_create(
            [RoleAuthority(role_id=role.id, action_id=action.id) for action in valid_actions]
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "id": role.id,
                "name": role.name,  
                "description": role.description,  
                "entity_id": entity.id,  
                "permissions": list(valid_actions.values("id", "action")),
            },
            "default_create_success_msg",
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

# --------------------------------------------------------
# GET /roles/{id}, PUT /roles/{id}, DELETE /roles/{id} - Retrieve, Update or Delete a role
@api_view(["GET", "PUT", "DELETE"])
def role_detail(request, role_id):
    if request.method == "GET":
        return get_role(request, role_id)
    elif request.method == "PUT":
        return update_role(request, role_id)
    elif request.method == "DELETE":
        return delete_role(request, role_id)


def get_role(request, role_id):
    try:
        role = Role.objects.get(id=role_id)

        all_columns = ['core_roles.id', 'core_roles.name', 'core_roles.description', 'core_roles.system_role']

        # Fetch the role via QueryBuilderService
        response_data = (
            QueryBuilderService("core_roles")
            .select(*all_columns)
            .where("core_roles.id", role_id)
            .first()
        )

        if not response_data:
            return ResponseService.response("NOT_FOUND", None, "Role not found")

        # Get linked permissions
        permissions = list(
            role.get_permissions().values("id", "entity", "action", "remarks", "can_be_permission")
        )
        response_data["permissions"] = permissions

        return ResponseService.response("SUCCESS", response_data, "Role retrieved successfully!")

    except Role.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Role not found")


def update_role(request, role_id):
    try:
        role = Role.objects.get(id=role_id)
        data = json.loads(request.body)
        rules = {
            "name": f"required|max:255|unique:core_roles,name,{role_id}",
            "description": "max:320",
            "permission_ids": "array",
            "permission_ids.*":"exists:core_actions,id"
        }

        custom_messages = {
            "name.required": "Name cannot be empty.",
            "name.max": "Name cannot exceed 255 characters.",
            "permission_ids.array": "Permissions must be a list.",
            "permission_ids.exists": "One or more provided permissions do not exist.",
        }

        
        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

       
        role.name = data["name"]
        role.description = data.get("description", role.description)
        role.system_role = data.get("system_role", role.system_role)
          
        if "entity_id" in data:
            return ResponseService.response("VALIDATION_ERROR", None, "Entity ID cannot be updated.")

        role.save()

        permission_ids = set(data.get("permission_ids", []))
        existing_permission_ids = set(
            RoleAuthority.objects.filter(role_id=role).values_list("action_id", flat=True)
        )

       
        valid_actions = Action.objects.filter(id__in=permission_ids)
        valid_action_ids = set(valid_actions.values_list("id", flat=True))
        
        # invalid_permissions = permission_ids - valid_action_ids
        # if invalid_permissions:
        #     return ResponseService.response(
        #         "VALIDATION_ERROR",
        #         {"permissions": [f"Invalid permission IDs: {', '.join(map(str, invalid_permissions))}"]},
        #         "Validation Error"
        #     )

       
        permissions_to_add = valid_action_ids - existing_permission_ids
        permissions_to_remove = existing_permission_ids - permission_ids


        RoleAuthority.objects.filter(role_id=role, action_id__in=permissions_to_remove).delete()
        actions_to_add = Action.objects.filter(id__in=permissions_to_add)
        RoleAuthority.objects.bulk_create(
            [RoleAuthority(role_id=role.id, action_id=action.id) for action in actions_to_add]
        )

       
        updated_permissions = list(role.get_permissions().values("id", "action"))

        return ResponseService.response(
            "SUCCESS",
            {
                "id": role.id,
                "name": role.name,
                "description": role.description,
                "system_role": role.system_role,
                "permissions": updated_permissions,
            },
            "default_update_success_msg"
        )

    except Role.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Role not found")

    except ValidationError as e:
        return ResponseService.response("VALIDATION_ERROR", e.message_dict, "Validation Error")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_role(request, role_id):
    
    try:
       
        rules = {
            "role_id": "required|exists:core_roles,id"
        }

        custom_messages = {
            "role_id.required": "Role ID is required.",
            "role_id.exists": "Role with the given ID does not exist.",
        }

        role = Role.objects.get(id=role_id)

        if role is None:
         return ResponseService.response("VALIDATION_ERROR", [], "data_not_found")
        
        userRole = User.objects.filter(role_id=role_id).first()
        if userRole:
            return ResponseService.response("CONFLICT", [], "role_delete_error_msg")
        
        invitationRole = UserInvitation.objects.filter(role_id=role_id).first()
        if invitationRole:
            return ResponseService.response("CONFLICT", [], "role_delete_error_msg")
        
        errors = ValidatorService.validate({"role_id": role_id}, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

       
        role = Role.objects.get(id=role_id)
        
        role.delete()

        return ResponseService.response("SUCCESS", "Deleted", "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



# --------------------------------------------------------
# GET /roles/privileges/count - Count actions for roles
@api_view(["GET"])
def count_role_privileges(request):
    """
    Count the total actions associated with given role IDs.
    """
    role_ids = request.GET.get("ids", "")

    if not role_ids:
        return JsonResponse({"error": "No role IDs provided"}, status=400)

    try:
        role_ids = [int(i) for i in role_ids.split(",")]
    except ValueError:
        return JsonResponse({"error": "Invalid role IDs format"}, status=400)

    total_actions = (
        Role.objects.filter(id__in=role_ids).aggregate(
            total_actions=Count("roleauthority__action_id")
        )["total_actions"]
        or 0
    )

    return JsonResponse(
        {
            "data": {
                "role_ids": role_ids,
                "total_actions": total_actions,
            }
        },
        status=200,
    )


# --------------------------------------------------------
# GET /roles/users/count - Count users for roles
@api_view(["GET"])
def count_role_users(request):
    """
    Count the total users associated with given role IDs.
    """
    role_ids = request.GET.get("ids", "")

    if not role_ids:
        return JsonResponse({"error": "No role IDs provided"}, status=400)

    try:
        role_ids = [int(i) for i in role_ids.split(",")]
    except ValueError:
        return JsonResponse({"error": "Invalid role IDs format"}, status=400)

    total_users = (
        Role.objects.filter(id__in=role_ids).aggregate(total_users=Count("user"))[
            "total_users"
        ]
        or 0
    )

    return JsonResponse(
        {
            "data": {
                "role_ids": role_ids,
                "total_users": total_users,
            }
        },
        status=200,
    )


@api_view(["GET", "POST"])
def get_actions(request):
    if request.method == "GET":
        return list_actions(request)
    elif request.method == "POST":
        return create_action(request)


def list_actions(request):
    """
    Retrieve a list of actions grouped by module using QueryBuilderService.
    """
    try:
        # Extract query params
        module_key = request.GET.get("module_key", None)  # e.g., "CRM,Core"
        if not module_key:
            return ResponseService.response(
                "SUCCESS", [], "No module key provided, no actions returned."
            )

        # Split module_key into a list
        module_keys = module_key.split(",")

        # Fetch module IDs based on the provided module keys
        modules = (
            QueryBuilderService("core_modules")
            .select("id", "name", "`key`")  # Escape the `key` column
            .whereIn("`key`", module_keys)  # Escape the `key` column in the condition
            .get()
        )
        if not modules:
            return ResponseService.response(
                "SUCCESS", [], "No matching modules found for the provided keys."
            )

        # Map module IDs to their names
        module_map = {module["id"]: module["name"] for module in modules}
        module_ids = list(module_map.keys())

        # Fetch actions for the retrieved module IDs
        actions = (
            QueryBuilderService("core_actions")
            .select("id", "module_id", "entity", "action", "remarks")
            .whereIn("module_id", module_ids)
            .where("can_be_permission", True)
            .get()
        )

        # Group actions by module
        grouped_actions = {}
        for action in actions:
            module_name = module_map.get(action["module_id"], "Unknown")
            if module_name not in grouped_actions:
                grouped_actions[module_name] = []
            grouped_actions[module_name].append(
                {
                    "id": action["id"],
                    "entity": action["entity"],
                    "action": action["action"],
                    "remarks": action["remarks"],
                }
            )

        # Format the result
        result = [
            {"module": module, "permissions": permissions}
            for module, permissions in grouped_actions.items()
        ]

        return ResponseService.response(
            "SUCCESS", result, "Actions retrieved successfully!"
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )



def create_action(request):
    """
    Create a new action.
    """
    try:
        data = json.loads(request.body)

        rules = {
            "entity": "required",
            "action": "required",
            "can_be_permission": "boolean",
        }

        custom_messages = {
            "entity.required": "Entity name is required.",
            "action.required": "Action name is required.",
            "can_be_permission.boolean": "can_be_permission must be a boolean value.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        action = Action.objects.create(
            entity=data["entity"],
            action=data["action"],
            remarks=data.get("remarks", ""),
            can_be_permission=data.get("can_be_permission", False),
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "id": action.id,
                "entity": action.entity,
                "action": action.action,
                "remarks": action.remarks,
                "can_be_permission": action.can_be_permission,
            },
            "default_create_success_msg",
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )
@api_view(["GET", "POST"])
def role_permissions(request, role_id):
    """
    Retrieve or update the permissions for a specific role.
    """
    try:
        # Fetch the role to ensure it exists
        role = Role.objects.filter(id=role_id).first()
        if not role:
            return ResponseService.response(
                "NOT_FOUND", None, f"Role with ID {role_id} does not exist"
            )

        if request.method == "GET":
            # Fetch permissions associated with the role
            permissions = list(
                RoleAuthority.objects.filter(role_id=role_id)
                .values_list("action_id", flat=True)
            )

            return ResponseService.response(
                "SUCCESS",
                {"permissions": permissions},
                "default_fetch_success_msg"
            )

        elif request.method == "POST":
            # Parse the request body
            data = json.loads(request.body)

            # Validation rules
            rules = {
                "permissions": "required|array",
                "permissions.*": "exists:core_actions,id",
            }

            custom_messages = {
                "permissions.required": "Permissions list is required.",
                "permissions.array": "Permissions must be a list.",
                "permissions.*.exists": "One or more provided permissions do not exist.",
            }

            # Validate the input
            errors = ValidatorService.validate(data, rules, custom_messages)
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )

            # Extract the new permissions
            new_permission_ids = set(data.get("permissions", []))

            # Fetch existing permissions for the role
            existing_permission_ids = set(
                RoleAuthority.objects.filter(role_id=role_id)
                .values_list("action_id", flat=True)
            )

            # Determine permissions to add and remove
            permissions_to_add = new_permission_ids - existing_permission_ids
            permissions_to_remove = existing_permission_ids - new_permission_ids

            # Remove old permissions
            RoleAuthority.objects.filter(
                role_id=role_id, action_id__in=permissions_to_remove
            ).delete()

            # Add new permissions
            RoleAuthority.objects.bulk_create(
                [
                    RoleAuthority(role_id=role_id, action_id=action_id)
                    for action_id in permissions_to_add
                ]
            )

            # Fetch updated permissions
            updated_permissions = list(
                RoleAuthority.objects.filter(role_id=role_id)
                .values_list("action_id", flat=True)
            )

            return ResponseService.response(
                "SUCCESS",
                {"permissions": updated_permissions},
                "update_success_msg"
            )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )