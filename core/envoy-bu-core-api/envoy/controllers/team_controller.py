from rest_framework.decorators import api_view
from envoy.models import Team,TeamUser
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json
import re
from django.db import transaction
from envoy.models.product_team import ProductTeam
from messages import Message,Error

@api_view(["GET", "POST"])
def team_view(request):
    if request.method == "GET":
        return list_teams(request)
    elif request.method == "POST":
        return create_team(request)
    
def list_teams(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = json.loads(request.GET.get("filter", "{}"))

        allowed_filters = ["ct.status_id", "ct.created_at"]
        search_columns = ["ct.name", "ct.description"]
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = [
            "ct.id", "ct.name", "ct.description",
            "core_status.name as status_name", "ct.status_id",
            "ct.leader_id", "leader.display_name as leader_name",
            "ct.manager_id", "manager.display_name as manager_name",
            "ct.detector_id", "detector.display_name as detector_name",
            "ct.created_at", "ct.updated_at",
        ]

        all_columns =allowed_sorting_columns

        query = (
            QueryBuilderService("core_teams as ct")
            .leftJoin("core_status", "core_status.id", "ct.status_id")
            .leftJoin("core_users as leader", "leader.id", "ct.leader_id")
            .leftJoin("core_users as manager", "manager.id", "ct.manager_id")
            .leftJoin("core_users as detector", "detector.id", "ct.detector_id")
            .select(*all_columns)
            .whereNull("ct.deleted_at")
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, Message.DATA_FETCHED)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)

def create_team(request):
    try:
        data = json.loads(request.body)

        rules = {
            "name": "required|unique:core_teams,name|max:200",
            "description": "nullable|max:250",
            "status_id": "nullable|exists:core_status,id",
            "leader_id": "nullable|exists:core_users,id",
            "manager_id": "required|exists:core_users,id",
            "detector_id": "nullable|exists:core_users,id",
            "user_ids": "required|list|min:1",
            "user_ids.*": "exists:core_users,id",
            "product_ids": "nullable|list",
            "product_ids.*": "exists:core_products,id"
        }

        custom_messages = {
            "name.required": "Name is required.",
            "name.unique": "Name must be unique.",
            "name.max": "Name cannot exceed 200 characters.",
            "description.max": "Description cannot exceed 250 characters.",
            "leader_id.required": "Leader ID is required.",
            "manager_id.required": "Manager ID is required.",
            "detector_id.required": "Detector ID is required.",
            "leader_id.exists": "Leader must be a valid user.",
            "manager_id.exists": "Manager must be a valid user.",
            "detector_id.exists": "Detector must be a valid user.",
            "user_ids.required": "At least one user ID must be provided.",
            "user_ids.*.exists": "One or more user IDs are invalid.",
            "product_ids.*.exists": "One or more product IDs are invalid."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

        with transaction.atomic():
            team_data = {
                "name": data["name"],
                "description": data.get("description", ""),
                "leader_id": data["leader_id"],
                "manager_id": data["manager_id"],
                "detector_id": data["detector_id"],
            }

            if "status_id" in data:
                team_data["status_id"] = data["status_id"]

            team = Team.objects.create(**team_data)
                    # Create team user associations

            user_ids = data["user_ids"]
            created_users = []
            for uid in user_ids:
                if not TeamUser.objects.filter(team_id=team.id, user_id=uid).exists():
                    TeamUser.objects.create(team_id=team.id, user_id=uid)
                    created_users.append(uid)

            # Assign team to products if product_ids provided
            if "product_ids" in data and data["product_ids"]:
                product_ids = data["product_ids"]
                for product_id in product_ids:
                    if not ProductTeam.objects.filter(product_id=product_id, team_id=team.id).exists():
                        ProductTeam.objects.create(product_id=product_id, team_id=team.id)

        return ResponseService.response("SUCCESS", None, Message.DATA_CREATED)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)

@api_view(["GET", "PUT", "DELETE"])
def team_detail(request, id):
    if request.method == "GET":
        return get_team(request, id)
    elif request.method == "PUT":
        return update_team(request, id)
    elif request.method == "DELETE":
        return delete_team(request, id)



def get_team(request, id):
    try:
        # Select fields for the team
        team_columns = [
            "core_teams.id",
            "core_teams.name",
            "core_teams.description",
            "core_teams.status_id",
            "core_status.name as status_name",
            "core_teams.leader_id",
            "leader.display_name as leader_name",
            "core_teams.manager_id",
            "manager.display_name as manager_name",
            "core_teams.detector_id",
            "detector.display_name as detector_name",
            "core_teams.created_at",
        ]

        # Fetch team details
        team = QueryBuilderService("core_teams") \
            .select(*team_columns) \
            .leftJoin("core_status", "core_status.id", "core_teams.status_id") \
            .leftJoin("core_users AS leader", "leader.id", "core_teams.leader_id") \
            .leftJoin("core_users AS manager", "manager.id", "core_teams.manager_id") \
            .leftJoin("core_users AS detector", "detector.id", "core_teams.detector_id") \
            .where("core_teams.id", id) \
            .whereNull("core_teams.deleted_at") \
            .first()

        if not team:
            return ResponseService.response("NOT_FOUND", {}, Error.NOT_FOUND)

        # Fetch associated users
        user_columns = [
            "core_users.id",
            "core_users.display_name",
            "core_users.email",
            "core_users.picture",
            "core_users.code",
            "core_users.contact_no",
        ]
        users = QueryBuilderService("core_users") \
            .select(*user_columns) \
            .leftJoin("core_team_users", "core_team_users.user_id", "core_users.id") \
            .where("core_team_users.team_id", id) \
            .get()

        # Assign role names based on team relationship
        for user in users:
            if user["id"] == team["leader_id"]:
                user["role_name"] = "leader"
            elif user["id"] == team["manager_id"]:
                user["role_name"] = "manager"
            elif user["id"] == team["detector_id"]:
                user["role_name"] = "detector"
            else:
                user["role_name"] = "sales agent"

        team["sales_agents"] = users

        # Fetch associated products
        product_columns = [
            "core_products.id",
            "core_products.name",
            "core_products.code",
            "core_products.category_id",
            "core_products.created_at",
        ]
        products = QueryBuilderService("core_products") \
            .select(*product_columns) \
            .leftJoin("core_product_teams", "core_product_teams.product_id", "core_products.id") \
            .where("core_product_teams.team_id", id) \
            .get()

        team["products"] = products

        return ResponseService.response("SUCCESS", team, Message.DATA_FETCHED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)


def update_team(request, id):
    try:
        team = Team.objects.get(id=id, deleted_at__isnull=True)
        data = json.loads(request.body)

        rules = {
            "name": f"required|unique:core_teams,name,{id},id|max:200",
            "description": "nullable|max:250",
            "status_id": "nullable|exists:core_status,id",
            "leader_id": "nullable|integer",
            "manager_id": "required|integer",
            "detector_id": "nullable|integer",
            "user_ids": "nullable|list",
            "user_ids.*": "exists:core_users,id",
            "product_ids": "nullable|list",
            "product_ids.*": "exists:core_products,id"
        }

        custom_messages = {
            "name.required": "Name is required.",
            "name.max": "Name cannot exceed 200 characters.",
            "description.max": "Description cannot exceed 250 characters.",
            "user_ids.*.exists": "One or more user IDs are invalid.",
            "product_ids.*.exists": "One or more product IDs are invalid."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

        with transaction.atomic():
            team.name = data["name"]
            team.description = data.get("description", "")
            team.status_id = data["status_id"]
            team.leader_id = data["leader_id"]
            team.manager_id = data["manager_id"]
            team.detector_id = data["detector_id"]
            team.save()

            # Handle user assignments if user_ids provided
            if "user_ids" in data:
                # Remove existing user assignments
                TeamUser.objects.filter(team_id=id).delete()
                
                # Add new user assignments if user_ids is not empty
                if data["user_ids"]:
                    for user_id in data["user_ids"]:
                        TeamUser.objects.create(team_id=id, user_id=user_id)

            # Handle product assignments if product_ids provided
            if "product_ids" in data:
                # Remove existing product assignments
                ProductTeam.objects.filter(team_id=id).delete()
                
                # Add new product assignments if product_ids is not empty
                if data["product_ids"]:
                    for product_id in data["product_ids"]:
                        ProductTeam.objects.create(product_id=product_id, team_id=id)

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
    except Team.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)


def delete_team(request, id):
    try:
        team = Team.objects.get(id=id, deleted_at__isnull=True)
        from django.utils import timezone
        team.deleted_at = timezone.now()
        team.save()
        return ResponseService.response("SUCCESS", None, Message.DATA_DELETED)
    except Team.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_account_managers(request):
    """
    Get all account managers from core_teams table
    Returns unique account managers with their details
    """
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = json.loads(request.GET.get("filter", "{}"))
        agent_id = request.GET.get("agent_Id")  # Get the agent_Id parameter
        product_id = request.GET.get("product_id")  # Get the product_id parameter
        product_group_id = request.GET.get("product_group_id")  # Get the product_group_id parameter
        
        # Track if product_id/product_group_id were originally provided (before normalization)
        product_id_provided = bool(product_id)
        product_group_id_provided = bool(product_group_id)
        
        # Normalize agent_id: treat None, empty string, or invalid values as None
        # Also extract product_id/product_group_id if embedded in agent_id value (malformed URL)
        if agent_id:
            agent_id_str = str(agent_id).strip()
            
            # Try to extract product_id and product_group_id from malformed agent_id value
            # Example: agent_Id=?product_id=12?search= -> extract product_id=12
            if not product_id and ("product_id" in agent_id_str or "product_id=" in agent_id_str):
                match = re.search(r'product_id[=:](\d+)', agent_id_str)
                if match:
                    product_id = match.group(1)
                    product_id_provided = True
            
            if not product_group_id and ("product_group_id" in agent_id_str or "product_group_id=" in agent_id_str):
                match = re.search(r'product_group_id[=:](\d+)', agent_id_str)
                if match:
                    product_group_id = match.group(1)
                    product_group_id_provided = True
            
            # Now normalize agent_id itself
            agent_id = agent_id_str
            # Handle malformed URLs where "?" might be in the value (e.g., agent_Id=4?search=)
            # Extract only the part before "?" if present
            if "?" in agent_id:
                agent_id = agent_id.split("?")[0].strip()
            # Remove any leading "?" if still present
            if agent_id.startswith("?"):
                agent_id = agent_id[1:].strip()
            # If after processing it's empty or invalid, set to None
            if not agent_id or agent_id.lower() in ["null", "none", "undefined"]:
                agent_id = None
        else:
            agent_id = None
        
        # Normalize product_id: treat None, empty string, or invalid values as None
        if product_id:
            product_id = str(product_id).strip()
            # Handle malformed URLs where "?" might be in the value
            if "?" in product_id:
                product_id = product_id.split("?")[0].strip()
            if product_id.startswith("?"):
                product_id = product_id[1:].strip()
            if not product_id or product_id.lower() in ["null", "none", "undefined"]:
                product_id = None
        else:
            product_id = None
        
        # Normalize product_group_id: treat None, empty string, or invalid values as None
        if product_group_id:
            product_group_id = str(product_group_id).strip()
            # Handle malformed URLs where "?" might be in the value
            if "?" in product_group_id:
                product_group_id = product_group_id.split("?")[0].strip()
            if product_group_id.startswith("?"):
                product_group_id = product_group_id[1:].strip()
            if not product_group_id or product_group_id.lower() in ["null", "none", "undefined"]:
                product_group_id = None
        else:
            product_group_id = None

        allowed_filters = []
        search_columns = ["manager.display_name", "manager.email"]
        sort_by = request.GET.get("sort_by", "manager.display_name")
        sort_dir = request.GET.get("sort_dir", "asc")
        sort_by = "manager.display_name" if sort_by in [None, ""] else sort_by
        sort_dir = "asc" if sort_dir in [None, ""] else sort_dir
        
        allowed_sorting_columns = [
            "manager.id", "manager.display_name", "manager.email", 
            "manager.contact_no", "manager.code"
        ]

        # Select fields for account managers (only manager info, no team-specific columns)
        manager_columns = [
            "manager.id as manager_id",
            "manager.display_name as manager_name", 
            "manager.email as manager_email",
            "manager.picture as manager_picture",
            "manager.code as manager_code",
            "manager.contact_no as manager_contact"
        ]

        # Handle product_id and product_group_id filtering to get team_ids
        team_ids_from_filters = []
        
        # Get team_ids from product_id (treat product_id as core_vendor_products.id / insurer product id)
        if product_id:
            try:
                vendor_product_id_int = int(product_id)
                # Resolve insurer product id -> native product id(s) via core_product_vendor_products
                mappings = QueryBuilderService("core_product_vendor_products")\
                    .select("product_id")\
                    .where("vendor_product_id", vendor_product_id_int)\
                    .get()
                native_product_ids = [m["product_id"] for m in mappings if m.get("product_id")]
                if native_product_ids:
                    product_teams = QueryBuilderService("core_product_teams")\
                        .select("team_id")\
                        .whereIn("product_id", native_product_ids)\
                        .get()
                    if product_teams:
                        team_ids_from_product = [pt["team_id"] for pt in product_teams if pt.get("team_id")]
                        team_ids_from_filters.extend(team_ids_from_product)
            except (ValueError, TypeError):
                # If product_id is not a valid integer, ignore it
                pass
        
        # Get team_ids from product_group_id (core_product_group_teams table)
        if product_group_id:
            try:
                product_group_id_int = int(product_group_id)
                product_group_teams = QueryBuilderService("core_product_group_teams")\
                    .select("team_id")\
                    .where("product_group_id", product_group_id_int)\
                    .get()
                
                if product_group_teams:
                    team_ids_from_group = [pgt["team_id"] for pgt in product_group_teams if pgt.get("team_id")]
                    team_ids_from_filters.extend(team_ids_from_group)
            except (ValueError, TypeError):
                # If product_group_id is not a valid integer, ignore it
                pass
        
        # Remove duplicates from team_ids_from_filters
        team_ids_from_filters = list(set(team_ids_from_filters)) if team_ids_from_filters else None
        
        # If product_id or product_group_id was provided but no teams found, return empty result
        if (product_id_provided or product_group_id_provided) and not team_ids_from_filters:
            return ResponseService.response(
                "SUCCESS",
                {
                    "total_records": 0,
                    "per_page": limit,
                    "current_page": page,
                    "last_page": 0,
                    "data": []
                },
                Message.DATA_FETCHED
            )

        # Build the base query
        # Use leftJoin and filter out NULL managers to ensure we only get teams with managers
        query = (
            QueryBuilderService("core_teams as ct")
            .leftJoin("core_users as manager", "manager.id", "ct.manager_id")
            .select(*manager_columns)
            .whereNull("ct.deleted_at")
            .whereNotNull("ct.manager_id")
        )
        
        # Add product_id/product_group_id filtering if team_ids are available
        if team_ids_from_filters:
            query = query.whereIn("ct.id", team_ids_from_filters)
        
        # Add agent filtering ONLY if agent_Id is provided and valid
        if agent_id:
            try:
                # Convert to int to ensure it's a valid ID
                agent_id = int(agent_id)
                query = query.leftJoin("core_team_users as ctu", "ctu.team_id", "ct.id")
                query = query.where("ctu.user_id", agent_id)
            except (ValueError, TypeError):
                # If agent_id is not a valid integer, ignore it and return all managers
                agent_id = None
        
        query = (
            query
            .groupBy("manager.id")
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, Message.DATA_FETCHED)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def get_sales_agents(request):
    """
    Get all sales agents (users in teams) with optional filters
    Supports filtering by manager_id, product_id, and product_group_id
    """
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = json.loads(request.GET.get("filter", "{}"))
        manager_id = request.GET.get("manager_id")  # Get the manager_id parameter
        product_id = request.GET.get("product_id")  # Get the product_id parameter
        product_group_id = request.GET.get("product_group_id")  # Get the product_group_id parameter
        
        # Track if product_id/product_group_id were originally provided (before normalization)
        product_id_provided = bool(product_id)
        product_group_id_provided = bool(product_group_id)
        
        # Normalize manager_id: treat None, empty string, or invalid values as None
        # Also extract product_id/product_group_id if embedded in manager_id value (malformed URL)
        if manager_id:
            manager_id_str = str(manager_id).strip()
            
            # Try to extract product_id and product_group_id from malformed manager_id value
            # Example: manager_id=?product_id=12?search= -> extract product_id=12
            if not product_id and ("product_id" in manager_id_str or "product_id=" in manager_id_str):
                match = re.search(r'product_id[=:](\d+)', manager_id_str)
                if match:
                    product_id = match.group(1)
                    product_id_provided = True
            
            if not product_group_id and ("product_group_id" in manager_id_str or "product_group_id=" in manager_id_str):
                match = re.search(r'product_group_id[=:](\d+)', manager_id_str)
                if match:
                    product_group_id = match.group(1)
                    product_group_id_provided = True
            
            # Now normalize manager_id itself
            manager_id = manager_id_str
            # Handle malformed URLs where "?" might be in the value
            if "?" in manager_id:
                manager_id = manager_id.split("?")[0].strip()
            if manager_id.startswith("?"):
                manager_id = manager_id[1:].strip()
            if not manager_id or manager_id.lower() in ["null", "none", "undefined"]:
                manager_id = None
        else:
            manager_id = None
        
        # Normalize product_id: treat None, empty string, or invalid values as None
        if product_id:
            product_id = str(product_id).strip()
            if "?" in product_id:
                product_id = product_id.split("?")[0].strip()
            if product_id.startswith("?"):
                product_id = product_id[1:].strip()
            if not product_id or product_id.lower() in ["null", "none", "undefined"]:
                product_id = None
        else:
            product_id = None
        
        # Normalize product_group_id: treat None, empty string, or invalid values as None
        if product_group_id:
            product_group_id = str(product_group_id).strip()
            if "?" in product_group_id:
                product_group_id = product_group_id.split("?")[0].strip()
            if product_group_id.startswith("?"):
                product_group_id = product_group_id[1:].strip()
            if not product_group_id or product_group_id.lower() in ["null", "none", "undefined"]:
                product_group_id = None
        else:
            product_group_id = None

        allowed_filters = []
        search_columns = ["core_users.display_name", "core_users.email"]
        sort_by = request.GET.get("sort_by", "core_users.display_name")
        sort_dir = request.GET.get("sort_dir", "asc")
        sort_by = "core_users.display_name" if sort_by in [None, ""] else sort_by
        sort_dir = "asc" if sort_dir in [None, ""] else sort_dir
        
        allowed_sorting_columns = [
            "core_users.id", "core_users.display_name", "core_users.email", 
            "core_users.contact_no", "core_users.code"
        ]

        # Select fields for sales agents (users)
        user_columns = [
            "core_users.id as user_id",
            "core_users.display_name as user_name",
            "core_users.email as user_email",
            "core_users.picture as user_picture",
            "core_users.code as user_code",
            "core_users.contact_no as user_contact"
        ]

        # Handle product_id and product_group_id filtering to get team_ids
        team_ids_from_filters = []
        
        # Get team_ids from product_id (treat product_id as core_vendor_products.id / insurer product id)
        if product_id:
            try:
                vendor_product_id_int = int(product_id)
                # Resolve insurer product id -> native product id(s) via core_product_vendor_products
                mappings = QueryBuilderService("core_product_vendor_products")\
                    .select("product_id")\
                    .where("vendor_product_id", vendor_product_id_int)\
                    .get()
                native_product_ids = [m["product_id"] for m in mappings if m.get("product_id")]
                if native_product_ids:
                    product_teams = QueryBuilderService("core_product_teams")\
                        .select("team_id")\
                        .whereIn("product_id", native_product_ids)\
                        .get()
                    if product_teams:
                        team_ids_from_product = [pt["team_id"] for pt in product_teams if pt.get("team_id")]
                        team_ids_from_filters.extend(team_ids_from_product)
            except (ValueError, TypeError):
                pass
        
        # Get team_ids from product_group_id (core_product_group_teams table)
        if product_group_id:
            try:
                product_group_id_int = int(product_group_id)
                product_group_teams = QueryBuilderService("core_product_group_teams")\
                    .select("team_id")\
                    .where("product_group_id", product_group_id_int)\
                    .get()
                
                if product_group_teams:
                    team_ids_from_group = [pgt["team_id"] for pgt in product_group_teams if pgt.get("team_id")]
                    team_ids_from_filters.extend(team_ids_from_group)
            except (ValueError, TypeError):
                pass
        
        # Remove duplicates from team_ids_from_filters
        team_ids_from_filters = list(set(team_ids_from_filters)) if team_ids_from_filters else None
        
        # If product_id or product_group_id was provided but no teams found, return empty result
        if (product_id_provided or product_group_id_provided) and not team_ids_from_filters:
            return ResponseService.response(
                "SUCCESS",
                {
                    "total_records": 0,
                    "per_page": limit,
                    "current_page": page,
                    "last_page": 0,
                    "data": []
                },
                Message.DATA_FETCHED
            )

        # Build the base query - get users from teams via core_team_users
        query = (
            QueryBuilderService("core_team_users as ctu")
            .leftJoin("core_users", "core_users.id", "ctu.user_id")
            .leftJoin("core_teams as ct", "ct.id", "ctu.team_id")
            .select(*user_columns)
            .whereNull("ctu.deleted_at")
            .whereNull("ct.deleted_at")
        )
        
        # Add manager_id filtering if provided
        if manager_id:
            try:
                manager_id_int = int(manager_id)
                query = query.where("ct.manager_id", manager_id_int)
            except (ValueError, TypeError):
                manager_id = None
        
        # Add product_id/product_group_id filtering if team_ids are available
        if team_ids_from_filters:
            query = query.whereIn("ctu.team_id", team_ids_from_filters)
        
        query = (
            query
            .groupBy("core_users.id")
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, Message.DATA_FETCHED)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)