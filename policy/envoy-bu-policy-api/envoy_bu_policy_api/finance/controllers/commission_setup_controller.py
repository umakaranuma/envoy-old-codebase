from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.db import transaction
import datetime
from mServices import ResponseService, QueryBuilderService, ValidatorService
from envoy_bu_policy_api.finance.controllers.utils.service import get_commission_setup_service
from messages import Error, Message


@csrf_exempt
@api_view(["GET"])
def get_teams_details(request, id):
    try:
        all_columns = [
            "core_teams.id",
            "core_teams.name",
            "core_users.id as user_id",
            "core_users.display_name as user_name",
            "core_roles.name as role_name",
        ]

        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "core_teams.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["core_teams.name", "core_teams.id"]


        # Fetch team details by ID
        team = (
            QueryBuilderService("core_teams")
            .select(*all_columns)
            .leftJoin(
                "core_team_users",
                "core_teams.id",
                "core_team_users.team_id"
            )
            .leftJoin(
                "core_users",
                "core_team_users.user_id",
                "core_users.id"
            )
            .leftJoin(
                "core_roles",
                "core_users.role_id",
                "core_roles.id"
            )
            .where("core_teams.id", id)
            .whereNull("core_teams.deleted_at")
            .apply_conditions(
                filter_json=filter_json,
                allowed_filters=[],
                search_string=search_string,
                search_columns=["core_teams.name", "core_users.display_name"]
            )
            .paginate(
                page=page,
                limit=limit,
                allowed_sorting_columns=allowed_sorting_columns,
                sort_by=sort_by,
                sort_dir=sort_dir
            )
        )

        if not team:
            return ResponseService.response(
                "NOT_FOUND", {}, Error.NOT_FOUND
            )

        return ResponseService.response("SUCCESS", team, Message.DATA_FETCHED)

    except Exception as e:
        return ResponseService.response(
            "NOT_FOUND", {"error": str(e)}, Error.NOT_FOUND
        )

@csrf_exempt
@api_view(["GET", "POST"])
def tst(request):
    if request.method == "GET":

        data = get_commission_setup_service(11,8)

        return ResponseService.response("SUCCESS", {}, Message.DATA_FETCHED)

    elif request.method == "POST":

        data = json.loads(request.body)
        # Process the data as needed
        return ResponseService.response(
            "SUCCESS", data={"message": "POST request successful", "data": data}
        )


@csrf_exempt
@api_view(["GET", "POST"])
def commission_setup(request):
    if request.method == "GET":
        return get_commission_setup(request, None)
    elif request.method == "POST":
        return store_commission_setup(request, None)


@csrf_exempt
@api_view(["POST"])
def commission_setup_multi(request):
    """
    Create multiple commission setups at once with the same validation rules (all-or-nothing)
    Also checks for duplicates within the input array.
    """
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "is_success": False,
                    "message": "invalid_json",
                    "result": [{"error": "Invalid JSON data"}],
                    "system_code": ""
                },
                "invalid_json"
            )
        
        # Handle both single object and array formats
        if isinstance(data, dict):
            # Single object - convert to array
            data = [data]
        elif not isinstance(data, list) or not data:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "is_success": False,
                    "message": "invalid_data_format",
                    "result": [{"error": "Data must be a non-empty array of commission setups or a single commission setup object"}],
                    "system_code": ""
                },
                "invalid_data_format"
            )
        error_list = []
        # Check for duplicates within the input array
        seen_keys = {}
        for idx, setup_data in enumerate(data):
            # Create key based on product_id/product_group_id, transaction_type, and all team_ids
            team_ids = setup_data.get("sales_team_ids", [])
            team_ids_str = ",".join(sorted(map(str, team_ids)))
            
            # Determine the identifier for this setup (product_id or product_group_id)
            setup_identifier = None
            if "product_id" in setup_data and setup_data["product_id"] is not None:
                setup_identifier = f"product_{setup_data['product_id']}"
            elif "product_group_id" in setup_data and setup_data["product_group_id"] is not None:
                # For product group-based setups, include insurer_ids in the identifier
                # Handle both insurer_id (singular) and insurer_ids (plural) formats
                insurer_ids = setup_data.get("insurer_ids", [])
                if not insurer_ids and "insurer_id" in setup_data:
                    insurer_ids = [setup_data["insurer_id"]]
                insurer_ids_str = ",".join(sorted(map(str, insurer_ids)))
                setup_identifier = f"group_{setup_data['product_group_id']}_insurers_{insurer_ids_str}"
            
            if setup_identifier:
                key = (setup_identifier, team_ids_str, str(setup_data.get("transaction_type")))
                if key in seen_keys:
                    # Mark both this and the previous index as duplicate_in_request
                    prev_idx = seen_keys[key]
                    # Only add error for previous index if not already present
                    already = next((e for e in error_list if e["index"] == prev_idx and "duplicate_in_request" in e["errors"]), None)
                    if not already:
                        error_list.append({"index": prev_idx, "errors": {"duplicate_in_request": True}})
                    error_list.append({"index": idx, "errors": {"duplicate_in_request": True}})
                else:
                    seen_keys[key] = idx
        # Continue with validation and DB duplicate check only for non-duplicate-in-request
        for idx, setup_data in enumerate(data):
            # Skip if already marked as duplicate_in_request
            if any(e["index"] == idx and "duplicate_in_request" in e["errors"] for e in error_list):
                continue
            errors = _validate_commission_setup(setup_data)
            if errors:
                error_list.append({"index": idx, "errors": errors})
            elif _check_duplicate_commission_setup(setup_data):
                error_list.append({"index": idx, "errors": {"duplicate": [
                    {"error_type": "duplicate", "tokens": {"_attribute": "commission_setup"}}
                ]}})
        if error_list:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "is_success": False,
                    "message": "validation_error",
                    "result": error_list,
                    "system_code": ""
                },
                "validation_error"
            )
        with transaction.atomic():
            now = datetime.datetime.now()
            ids = []
            for setup_data in data:
                commission_id = _create_commission_setup(setup_data, now)
                ids.append(commission_id)
            return ResponseService.response(
                "SUCCESS",
                {
                    "is_success": True,
                    "message": "all_commission_setups_created",
                    "result": [{"id": cid} for cid in ids],
                    "system_code": ""
                },
                Message.DATA_CREATED
            )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {
                "is_success": False,
                "message": "database_error",
                "result": [{"error": str(e)}],
                "system_code": ""
            },
           Error.INTERNAL_SERVER_ERROR
        )

# Explicitly mark the view as synchronous for Django/DRF async compatibility
commission_setup_multi._is_coroutine = False


def get_commission_setup(request, id=None):
    try:
        all_columns = [
            "DISTINCT crmf_commission_setups.*",
            # Remove legacy team_name field
            # "core_teams.name as team_name",
            "core_service_providers.id as insurer_id",
            "core_service_providers.name as insurer_name",
            "core_service_providers.logo as insurer_logo",
            "core_service_providers.address as insurer_address",
            "core_service_providers.contact_no as insurer_contact_no",
            "core_service_providers.email as insurer_email",
            "core_service_providers.website as insurer_website",
            "core_service_providers.fax_no as insurer_fax_no",
            "core_service_providers.description as insurer_description",
            "core_service_providers.status_id as insurer_status_id",
            "core_vendor_products.name as product_name",
            "crmf_transaction_types.name as transaction_type_name",
            "core_product_groups.name as product_group_name",
            "CASE WHEN core_product_groups.name IS NULL THEN 'individual_product' WHEN core_vendor_products.name IS NULL THEN 'product_group' END as type",
        ]

        # Initialize base query
        query = (
            QueryBuilderService("crmf_commission_setups")
            .select(*all_columns)
            .leftJoin(
                "core_service_providers",
                "crmf_commission_setups.insurer_id",
                "core_service_providers.id"
            )
            .leftJoin(
                "core_vendor_products",
                "crmf_commission_setups.product_id",
                "core_vendor_products.id"
            )
            .leftJoin(
                "crmf_transaction_types",
                "crmf_commission_setups.transaction_type",
                "crmf_transaction_types.id"
            )
            .leftJoin(
                "core_product_groups",
                "crmf_commission_setups.product_group_id",
                "core_product_groups.id"
            )
            .whereNull("crmf_commission_setups.deleted_at")
        )

        def get_teams_for_setup(setup_id):
            team_rows = QueryBuilderService("crmf_commission_setup_teams") \
                .select("team_id") \
                .where("commission_setup_id", setup_id) \
                .get()
            team_ids = [row["team_id"] for row in team_rows]
            if not team_ids:
                return []
            teams = QueryBuilderService("core_teams") \
                .select("id", "name") \
                .whereIn("id", team_ids) \
                .get()
            
            return teams

        def create_insurer_object(row):
            """Create insurer object from row data"""
            if not row.get("insurer_id"):
                return None
            
            return {
                "id": row.get("insurer_id"),
                "name": row.get("insurer_name"),
                "logo": row.get("insurer_logo"),
                "address": row.get("insurer_address"),
                "contact_no": row.get("insurer_contact_no"),
                "email": row.get("insurer_email"),
                "website": row.get("insurer_website"),
                "fax_no": row.get("insurer_fax_no"),
                "description": row.get("insurer_description"),
                "status_id": row.get("insurer_status_id")
            }

        def get_insurers_for_setup(setup_id):
            """Get insurer information for product group type commission setups"""
            insurer_rows = QueryBuilderService("crmf_commission_setup_service_providers") \
                .select(
                    "crmf_commission_setup_service_providers.service_provider_id as insurer_id",
                    "core_service_providers.name as insurer_name",
                    "core_service_providers.logo as insurer_logo",
                    "core_service_providers.address as insurer_address",
                    "core_service_providers.contact_no as insurer_contact_no",
                    "core_service_providers.email as insurer_email",
                    "core_service_providers.website as insurer_website",
                    "core_service_providers.fax_no as insurer_fax_no",
                    "core_service_providers.description as insurer_description",
                    "core_service_providers.status_id as insurer_status_id"
                ) \
                .leftJoin(
                    "core_service_providers",
                    "crmf_commission_setup_service_providers.service_provider_id",
                    "core_service_providers.id"
                ) \
                .where("crmf_commission_setup_service_providers.commission_setup_id", setup_id) \
                .get()
            
            if not insurer_rows:
                return []
            
            # Convert to insurer objects
            insurers = []
            for row in insurer_rows:
                insurer_obj = {
                    "id": row.get("insurer_id"),
                    "name": row.get("insurer_name"),
                    "logo": row.get("insurer_logo"),
                    "address": row.get("insurer_address"),
                    "contact_no": row.get("insurer_contact_no"),
                    "email": row.get("insurer_email"),
                    "website": row.get("insurer_website"),
                    "fax_no": row.get("insurer_fax_no"),
                    "description": row.get("insurer_description"),
                    "status_id": row.get("insurer_status_id")
                }
                insurers.append(insurer_obj)
            
            return insurers

        if id:
            commission = query.where("crmf_commission_setups.id", id).first()
            if not commission:
                return ResponseService.response(
                    "NOT_FOUND",
                    {},
                    "commission_setup_not_found"
                )
            
            # Get all commission field values for this setup
            commission_values = (
                QueryBuilderService("crmf_commission_field_values")
                .select(
                    "crmf_commission_field_values.*",
                    "crmf_commission_fields.attribute_name as field_name",
                    "core_users.display_name as user_name",
                    "core_users.email as user_email",
                    "core_roles.name as role_name",
                )
                .leftJoin(
                    "crmf_commission_fields",
                    "crmf_commission_fields.id",
                    "crmf_commission_field_values.commission_field_id"
                )
                .leftJoin(
                    "core_users",
                    "crmf_commission_field_values.user_id",
                    "core_users.id"
                )
                .leftJoin(
                    "core_roles",
                    "core_users.role_id",
                    "core_roles.id"
                )
                .where("commission_setup_id", id)
                .get()
            )
            commission["commission_values"] = {}
            for value in commission_values:
                field_name = value.get("field_name")
                if not field_name in commission["commission_values"]:
                    commission["commission_values"][field_name] = []
                commission["commission_values"][field_name].append({
                    "value": value.get("value"),
                    "type": value.get("type"),
                    "user_name": value.get("user_name"),
                    "user_email": value.get("user_email"),
                    "user_id": value.get("user_id"),
                    "role_name": value.get("role_name"),
                })
            # Add agent_commission_percent_type and brokerage_revenue_percent_type
            agent_type = None
            brokerage_type = None
            agent_list = commission["commission_values"].get("agent_commission_percent", [])
            brokerage_list = commission["commission_values"].get("brokerage_revenue_percent", [])
            if agent_list and isinstance(agent_list, list):
                agent_type = agent_list[0].get("type")
            if brokerage_list and isinstance(brokerage_list, list):
                brokerage_type = brokerage_list[0].get("type")
            commission["agent_commission_percent_type"] = agent_type
            commission["brokerage_revenue_percent_type"] = brokerage_type
            # Add teams array at the end
            commission["teams"] = get_teams_for_setup(commission["id"])
            
            # Add insurer object
            if commission.get("type") == "individual_product":
                commission["insurer"] = create_insurer_object(commission)
            else:
                # For product group setups, get insurers from service providers table
                insurers = get_insurers_for_setup(commission["id"])
                if insurers:
                    # Use the first insurer's information
                    commission["insurer"] = insurers[0]
                else:
                    commission["insurer"] = None
            
            # Remove legacy team fields if present
            commission.pop("sales_team_id", None)
            commission.pop("team_name", None)
            
            # Remove individual insurer fields to avoid duplication
            commission.pop("insurer_id", None)
            commission.pop("insurer_name", None)
            commission.pop("insurer_logo", None)
            commission.pop("insurer_address", None)
            commission.pop("insurer_contact_no", None)
            commission.pop("insurer_email", None)
            commission.pop("insurer_website", None)
            commission.pop("insurer_fax_no", None)
            commission.pop("insurer_description", None)
            commission.pop("insurer_status_id", None)
            return ResponseService.response("SUCCESS", commission, "data_get")

        # List all commission setups with pagination
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by" )
        sort_dir = request.GET.get("sort_dir")
        sort_by = "crmf_commission_setups.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        # Handle product_type filter manually since it's a computed field
        product_type_filter = request.GET.get("type")
        if product_type_filter:
            if product_type_filter == "individual_product":
                query = query.whereNotNull("core_vendor_products.name").whereNull("core_product_groups.name")
            elif product_type_filter == "product_group":
                query = query.whereNull("core_vendor_products.name").whereNotNull("core_product_groups.name")

        allowed_filters = ["crmf_commission_setups.id"]
        search_columns = ["crmf_commission_setups.id", "core_vendor_products.name", "core_product_groups.name"]
        allowed_sorting_columns = ["crmf_commission_setups.id", "crmf_commission_setups.created_at", "type"]

        data = (query
            .apply_conditions(
                filter_json=filter_json,
                allowed_filters=allowed_filters,
                search_string=search_string,
                search_columns=search_columns
            )
            .paginate(
                page=page, 
                limit=limit,
                allowed_sorting_columns=allowed_sorting_columns,
                sort_by=sort_by,
                sort_dir=sort_dir
            )
        )
        # Add teams array and types to each commission setup
        for row in data.get('data', []):
            row["teams"] = get_teams_for_setup(row["id"])
            
            # Add insurer object
            if row.get("type") == "individual_product":
                row["insurer"] = create_insurer_object(row)
            else:
                # For product group setups, get insurers from service providers table
                insurers = get_insurers_for_setup(row["id"])
                if insurers:
                    # Use the first insurer's information
                    row["insurer"] = insurers[0]
                else:
                    row["insurer"] = None
            
            row.pop("sales_team_id", None)
            row.pop("team_name", None)
            
            # Remove individual insurer fields to avoid duplication
            row.pop("insurer_id", None)
            row.pop("insurer_name", None)
            row.pop("insurer_logo", None)
            row.pop("insurer_address", None)
            row.pop("insurer_contact_no", None)
            row.pop("insurer_email", None)
            row.pop("insurer_website", None)
            row.pop("insurer_fax_no", None)
            row.pop("insurer_description", None)
            row.pop("insurer_status_id", None)
            # Get commission field values for this setup
            commission_values = (
                QueryBuilderService("crmf_commission_field_values")
                .select(
                    "crmf_commission_field_values.*",
                    "crmf_commission_fields.attribute_name as field_name"
                )
                .leftJoin(
                    "crmf_commission_fields",
                    "crmf_commission_fields.id",
                    "crmf_commission_field_values.commission_field_id"
                )
                .where("commission_setup_id", row["id"])
                .get()
            )
            values_by_field = {}
            for value in commission_values:
                field_name = value.get("field_name")
                if not field_name in values_by_field:
                    values_by_field[field_name] = []
                values_by_field[field_name].append({
                    "value": value.get("value"),
                    "type": value.get("type")
                })
            agent_type = None
            brokerage_type = None
            agent_list = values_by_field.get("agent_commission_percent", [])
            brokerage_list = values_by_field.get("brokerage_revenue_percent", [])
            if agent_list and isinstance(agent_list, list):
                agent_type = agent_list[0].get("type")
            if brokerage_list and isinstance(brokerage_list, list):
                brokerage_type = brokerage_list[0].get("type")
            row["agent_commission_percent_type"] = agent_type
            row["brokerage_revenue_percent_type"] = brokerage_type
        return ResponseService.response("SUCCESS", data, "data_get")
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "default_not_found")


def store_commission_setup(request, id=None):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "is_success": False,
                    "message": "invalid_json",
                    "result": {"error": "Invalid JSON data"},
                    "system_code": ""
                },
                "invalid_json"
            )
        errors = _validate_commission_setup(data)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "is_success": False,
                    "message": "validation_error",
                    "result": errors,
                    "system_code": ""
                },
                "validation_error"
            )
        if not id and _check_duplicate_commission_setup(data):
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "is_success": False,
                    "message": "validation_error",
                    "result": {"duplicate": [
                        {"error_type": "duplicate", "tokens": {"_attribute": "commission_setup"}}
                    ]},
                    "system_code": ""
                },
                "validation_error"
            )
        with transaction.atomic():
            now = datetime.datetime.now()
            commission_id = _create_commission_setup(data, now)
            return ResponseService.response(
                "SUCCESS",
                {
                    "is_success": True,
                    "message": "default_create_success_msg",
                    "result": {"id": commission_id},
                    "system_code": ""
                },
                "default_create_success_msg"
            )
    except Exception as e:
        return ResponseService.response(
            "DATABASE_ERROR",
            {
                "is_success": False,
                "message": "database_error",
                "result": {"error": str(e)},
                "system_code": ""
            },
            "database_error"
        )


@csrf_exempt
@api_view(["GET"])
def get_teams(request):
    try:

        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["name", ""]

        team = (
            QueryBuilderService("core_teams")
            .select("core_teams.id", "core_teams.name")
            .whereNull("core_teams.deleted_at")
            .apply_conditions(filter_json, [], search_string, ["core_teams.name"])
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", team, "Teams retrieved successfully")
    except Exception as e:
        return ResponseService.response(
            "NOT_FOUND", {}, "Failed to retrieve teams: " + str(e)
        )


def check_commissions_calculated(commission_setup_id):
    """
    Check if commissions are calculated for a commission setup.
    
    Args:
        commission_setup_id (int): ID of the commission setup to check
        
    Returns:
        dict: {
            'has_commissions': bool,
            'brokerage_count': int,
            'agent_count': int
        }
    """
    try:
        # Check for brokerage commissions
        brokerage_commissions = QueryBuilderService("crmf_brokerage_commission")\
            .select("id")\
            .where("commission_setup_id", commission_setup_id)\
            .get()
        
        # Check for agent commissions
        agent_commissions = QueryBuilderService("crmf_agent_commission")\
            .select("id")\
            .where("commission_setup_id", commission_setup_id)\
            .get()
        
        brokerage_count = len(brokerage_commissions) if brokerage_commissions else 0
        agent_count = len(agent_commissions) if agent_commissions else 0
        has_commissions = brokerage_count > 0 or agent_count > 0
        
        return {
            'has_commissions': has_commissions,
            'brokerage_count': brokerage_count,
            'agent_count': agent_count
        }
    except Exception as e:
        print(f"Error checking commissions for commission setup {commission_setup_id}: {str(e)}")
        # If there's an error, assume commissions exist to be safe
        return {
            'has_commissions': True,
            'brokerage_count': 0,
            'agent_count': 0
        }


def soft_delete_commission_setup(commission_setup_id):
    """
    Soft delete commission setup by setting deleted_at timestamp.
    Also soft deletes related user commissions if they exist.
    Note: Commission calculations (brokerage/agent commissions) don't have deleted_at
    columns, so they are not soft deleted. They are used to prevent deletion when they exist.
    
    Args:
        commission_setup_id (int): ID of the commission setup to delete
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        now = datetime.datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Starting soft delete for commission setup ID: {commission_setup_id}")
        
        # Soft delete user commissions (has deleted_at column)
        try:
            QueryBuilderService("crmf_user_commissions")\
                .where("commission_setup_id", commission_setup_id)\
                .whereNull("deleted_at")\
                .update({"deleted_at": formatted_now})
        except Exception as e:
            print(f"Note: Could not soft delete user commissions: {str(e)}")
        
        # Soft delete the commission setup itself
        deleted = QueryBuilderService("crmf_commission_setups")\
            .where("id", commission_setup_id)\
            .whereNull("deleted_at")\
            .update({"deleted_at": formatted_now})
        
        if deleted:
            print(f"Successfully soft deleted commission setup ID: {commission_setup_id}")
            return True
        else:
            print(f"Commission setup {commission_setup_id} not found or already deleted")
            return False
        
    except Exception as e:
        print(f"Error during soft delete of commission setup {commission_setup_id}: {str(e)}")
        return False


def hard_delete_commission_setup(commission_setup_id):
    """
    Hard delete commission setup and all related data from connected tables.
    This function ensures no foreign key constraint issues occur.
    
    Args:
        commission_setup_id (int): ID of the commission setup to delete
        
    Returns:
        bool: True if successful, False if failed
    """
    try:
        print(f"Starting hard delete for commission setup ID: {commission_setup_id}")
        
        # Step 1: Delete commission field values
        field_values_deleted = QueryBuilderService("crmf_commission_field_values")\
            .where("commission_setup_id", commission_setup_id).delete()
        print(f"Deleted {field_values_deleted} commission field values")
        
        # Step 2: Delete commission setup teams (join table)
        teams_deleted = QueryBuilderService("crmf_commission_setup_teams")\
            .where("commission_setup_id", commission_setup_id).delete()
        print(f"Deleted {teams_deleted} commission setup teams")
        
        # Step 3: Delete user commissions
        user_commissions_deleted = QueryBuilderService("crmf_user_commissions")\
            .where("commission_setup_id", commission_setup_id).delete()
        print(f"Deleted {user_commissions_deleted} user commissions")
        
        # Step 4: Delete agent commission payments first (before deleting agent commissions)
        # First get all agent commission IDs before deleting them
        agent_commission_ids = QueryBuilderService("crmf_agent_commission")\
            .select("id").where("commission_setup_id", commission_setup_id).get()
        
        payments_deleted = 0
        if agent_commission_ids:
            agent_commission_id_list = [item['id'] for item in agent_commission_ids]
            for agent_comm_id in agent_commission_id_list:
                payment_result = QueryBuilderService("crmf_agent_commission_payments")\
                    .where("agent_commission_id", agent_comm_id).delete()
                if payment_result:
                    payments_deleted += 1
        print(f"Deleted {payments_deleted} agent commission payments")
        
        # Step 5: Delete agent commissions (these have PROTECT constraint)
        agent_commissions_deleted = QueryBuilderService("crmf_agent_commission")\
            .where("commission_setup_id", commission_setup_id).delete()
        print(f"Deleted {agent_commissions_deleted} agent commissions")
        
        # Step 6: Delete brokerage commissions (these have PROTECT constraint)
        brokerage_commissions_deleted = QueryBuilderService("crmf_brokerage_commission")\
            .where("commission_setup_id", commission_setup_id).delete()
        print(f"Deleted {brokerage_commissions_deleted} brokerage commissions")
        
        # Step 7: Delete commission setup service providers
        service_providers_deleted = QueryBuilderService("crmf_commission_setup_service_providers")\
            .where("commission_setup_id", commission_setup_id).delete()
        print(f"Deleted {service_providers_deleted} commission setup service providers")
        
        # Step 8: Delete update history records
        history_deleted = QueryBuilderService("crmf_update_histories")\
            .where("commission_setup_id", commission_setup_id).delete()
        print(f"Deleted {history_deleted} update history records")
        
        # Step 9: Delete flex field entities
        flex_fields_deleted = QueryBuilderService("crmf_flex_field_entities")\
            .where("commission_setup_id", commission_setup_id).delete()
        print(f"Deleted {flex_fields_deleted} flex field entities")
        
        # Step 10: Finally delete the commission setup itself
        setup_deleted = QueryBuilderService("crmf_commission_setups")\
            .where("id", commission_setup_id).delete()
        print(f"Deleted commission setup: {setup_deleted}")
        
        print(f"Successfully completed hard delete for commission setup ID: {commission_setup_id}")
        return True
        
    except Exception as e:
        print(f"Error during hard delete of commission setup {commission_setup_id}: {str(e)}")
        return False

def bulk_soft_delete_commission_setups(commission_setup_ids):
    """
    Bulk soft delete multiple commission setups.
    Skips setups that have calculated commissions.
    
    Args:
        commission_setup_ids (list): List of commission setup IDs to delete
        
    Returns:
        dict: Results of the bulk delete operation
    """
    results = {
        'successful': [],
        'failed': [],
        'skipped_with_commissions': [],
        'total_processed': len(commission_setup_ids),
        'total_successful': 0,
        'total_failed': 0,
        'total_skipped': 0
    }
    
    for setup_id in commission_setup_ids:
        try:
            # Check if commission setup exists
            commission_setup = (
                QueryBuilderService("crmf_commission_setups")
                .where("id", setup_id)
                .whereNull("deleted_at")
                .first()
            )
            
            if not commission_setup:
                results['failed'].append(setup_id)
                results['total_failed'] += 1
                continue
            
            # Check if commissions are calculated
            commission_check = check_commissions_calculated(setup_id)
            if commission_check['has_commissions']:
                results['skipped_with_commissions'].append({
                    'id': setup_id,
                    'brokerage_count': commission_check['brokerage_count'],
                    'agent_count': commission_check['agent_count']
                })
                results['total_skipped'] += 1
                continue
            
            # Perform soft delete
            success = soft_delete_commission_setup(setup_id)
            if success:
                results['successful'].append(setup_id)
                results['total_successful'] += 1
            else:
                results['failed'].append(setup_id)
                results['total_failed'] += 1
        except Exception as e:
            print(f"Exception during bulk delete of commission setup {setup_id}: {str(e)}")
            results['failed'].append(setup_id)
            results['total_failed'] += 1
    
    return results


def bulk_hard_delete_commission_setups(commission_setup_ids):
    """
    Bulk hard delete multiple commission setups and all their related data.
    This function is kept for backward compatibility but should not be used
    for normal deletion operations.
    
    Args:
        commission_setup_ids (list): List of commission setup IDs to delete
        
    Returns:
        dict: Results of the bulk delete operation
    """
    results = {
        'successful': [],
        'failed': [],
        'total_processed': len(commission_setup_ids),
        'total_successful': 0,
        'total_failed': 0
    }
    
    for setup_id in commission_setup_ids:
        try:
            success = hard_delete_commission_setup(setup_id)
            if success:
                results['successful'].append(setup_id)
                results['total_successful'] += 1
            else:
                results['failed'].append(setup_id)
                results['total_failed'] += 1
        except Exception as e:
            print(f"Exception during bulk delete of commission setup {setup_id}: {str(e)}")
            results['failed'].append(setup_id)
            results['total_failed'] += 1
    
    return results

@csrf_exempt
@api_view(["GET","PUT","DELETE"])
def commission_setup_single(request, id):
    try:
        if request.method == "GET":
            return get_commission_setup(request, id)
        elif request.method == "PUT":
            return edit_commission_setup(request, id)
        elif request.method == "DELETE":
            # Check if commission setup exists
            commission_setup = (
                QueryBuilderService("crmf_commission_setups")
                .where("id", id)
                .whereNull("deleted_at")
                .first()
            )   
            if not commission_setup:
                return ResponseService.response(
                    "NOT_FOUND", {}, "data_not_found"
                )
            
            # Check if commissions are calculated
            commission_check = check_commissions_calculated(id)
            if commission_check['has_commissions']:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {
                        "message": "Cannot delete commission setup with calculated commissions",
                        "brokerage_count": commission_check['brokerage_count'],
                        "agent_count": commission_check['agent_count']
                    },
                    "commission_setup_has_calculated_commissions"
                )
            
            # Perform soft delete of commission setup
            delete_success = soft_delete_commission_setup(id)
            
            if not delete_success:
                return ResponseService.response(
                    "ERROR", {}, "commission_setup_delete_failed"
                )
            
            return ResponseService.response("SUCCESS", {}, "default_delete_success_msg")
    except Exception as e:
        return ResponseService.response(
            "ERROR", {"error": str(e)}, "default_error"
        )



def edit_commission_setup(request, id):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON"}, "invalid_json")

        # Determine if this is product-based or product group-based setup
        has_product_id = "product_id" in data and data["product_id"] is not None and data["product_id"] != 0
        has_product_group_id = "product_group_id" in data and data["product_group_id"] is not None and data["product_group_id"] != 0
        
        # Handle single insurer_id format (convert to insurer_ids array) for product group setups
        if has_product_group_id and "insurer_id" in data and "insurer_ids" not in data:
            data["insurer_ids"] = [data["insurer_id"]]

        # Auto-populate sales_team_ids if not provided for product group-based setups
        if has_product_group_id and "insurer_ids" in data:
            if not data.get("sales_team_ids") or len(data.get("sales_team_ids", [])) == 0:
                data["sales_team_ids"] = _get_team_ids_for_insurer_product_group(
                    data["insurer_ids"], 
                    data["product_group_id"]
                )
        
        # Validation rules (multi-team) - make product_id and native_product_id conditional
        rules = {
            "transaction_type": "required|integer",
            "sales_team_ids": "required|array",  # Use sales_team_ids (array)
            "brokerage_revenue_percent": "required|array",
            "agent_commission_percent": "required|array",
            "commission_percent": "required|array",
            "revised_commission_percent": "array"
        }
        
        # Add conditional validation based on setup type
        if has_product_id:
            rules.update({
                "product_id": "required|integer",
                "native_product_id": "required|integer"
            })
        elif has_product_group_id:
            rules.update({
                "product_group_id": "required|integer",
                "insurer_ids": "required|array"
            })

        errors = ValidatorService.validate(data, rules)
        # Custom validation: ensure every revised_commission_percent entry has a team_id
        for idx, item in enumerate(data.get("revised_commission_percent", [])):
            if "team_id" not in item:
                if not errors:
                    errors = {}
                errors[f"revised_commission_percent_{idx}"] = "Each revised commission must have a team_id"
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "validation_error")

        with transaction.atomic():
            now = datetime.datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

            # Step 1: Use hard_delete_commission_setup to handle all foreign key constraints
            delete_success = hard_delete_commission_setup(id)
            if not delete_success:
                return ResponseService.response(
                    "ERROR", 
                    {"error": "Failed to delete existing commission setup and related data"}, 
                    "commission_setup_update_failed"
                )

            # Step 2: Recreate commission setup with same ID (no sales_team_id field)
            insert_data = {
                "id": id,
                "transaction_type": int(data["transaction_type"]),
                "brokerage_revenue_percent": str(round(float(data["brokerage_revenue_percent"][0]["value"]), 2)),
                "agent_commission_percent": str(round(float(data["agent_commission_percent"][0]["value"]), 2)),
                "created_at": formatted_now,
                "updated_at": formatted_now,
            }
            
            # Add fields based on setup type
            if has_product_id:
                insert_data.update({
                    "product_id": int(data["product_id"]),
                    "native_product_id": int(data["native_product_id"]),
                })
                # Add insurer_id if provided (for product-based setups)
                if "insurer_id" in data:
                    insert_data["insurer_id"] = int(data["insurer_id"])
            elif has_product_group_id:
                insert_data.update({
                    "product_group_id": int(data["product_group_id"]),
                    "product_id": 0,  # Set default value for product_id (required by database)
                    "native_product_id": 0,  # Set default value for native_product_id (required by database)
                })

            QueryBuilderService("crmf_commission_setups").insert(insert_data)

            # Step 3: Insert team associations (join table)
            team_ids = data.get("sales_team_ids", [])
            for team_id in team_ids:
                team_data = {
                    "commission_setup_id": id,
                    "team_id": int(team_id),
                    "created_at": formatted_now,
                }
                QueryBuilderService("crmf_commission_setup_teams").insert(team_data)

            # Step 3.5: Insert insurer associations for product group-based setups
            if has_product_group_id and "insurer_ids" in data:
                insurer_ids = data.get("insurer_ids", [])
                for insurer_id in insurer_ids:
                    insurer_data = {
                        "commission_setup_id": id,
                        "service_provider_id": int(insurer_id),
                    }
                    QueryBuilderService("crmf_commission_setup_service_providers").insert(insurer_data)

            # Step 4: Fetch commission fields
            commission_fields = QueryBuilderService("crmf_commission_fields").get()
            field_map = {field["attribute_name"]: field["id"] for field in commission_fields}

            array_fields = [
                "brokerage_revenue_percent",
                "agent_commission_percent",
            ]

            # Step 5: Insert array fields
            for field_name in array_fields:
                field_id = field_map.get(field_name)
                if not field_id:
                    raise Exception(f"Missing field config for: {field_name}")

                for item in data[field_name]:
                    QueryBuilderService("crmf_commission_field_values").insert({
                        "commission_field_id": field_id,
                        "commission_setup_id": id,
                        "value": str(round(float(item["value"]), 2)),
                        "type": str(item["type"]),
                        "created_at": formatted_now,
                        "updated_at": formatted_now
                    })

            # Step 6: Insert commission percent
            percent_field_id = field_map.get("commission_percent")
            for item in data["commission_percent"]:
                insert_data = {
                    "commission_field_id": percent_field_id,
                    "commission_setup_id": id,
                    "user_id": int(item["user_id"]),
                    "value": str(round(float(item["value"]), 2)),
                    "type": str(item["type"]),
                    "created_at": formatted_now,
                    "updated_at": formatted_now
                }
                # Add team_id if provided
                if "team_id" in item:
                    insert_data["team_id"] = int(item["team_id"])
                QueryBuilderService("crmf_commission_field_values").insert(insert_data)

            # Step 7: Insert revised commission percent (optional)
            revised_field_id = field_map.get("revised_commission_percent")
            if revised_field_id and "revised_commission_percent" in data:
                for item in data["revised_commission_percent"]:
                    insert_data = {
                        "commission_field_id": revised_field_id,
                        "commission_setup_id": id,
                        "user_id": int(item["user_id"]),
                        "value": str(round(float(item["value"]), 2)),
                        "type": str(item["type"]),
                        "created_at": formatted_now,
                        "updated_at": formatted_now
                    }
                    # Add team_id if provided
                    if "team_id" in item:
                        insert_data["team_id"] = int(item["team_id"])
                    QueryBuilderService("crmf_commission_field_values").insert(insert_data)

            return ResponseService.response("SUCCESS", {"id": id}, "default_update_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "database_error")


@csrf_exempt
@api_view(["GET"])
def product_vendor(request,id):

    all_column = {
        "core_service_providers.*"  
     }

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_service_providers.id")
    sort_dir = request.GET.get("sort_dir", "desc")
    allowed_sorting_columns = ["core_service_providers.name", "core_service_providers.id"]

    data = (
        QueryBuilderService("core_vendor_products")
        .select(*all_column)
        .leftJoin("core_product_vendor_products","core_product_vendor_products.product_id","core_vendor_products.id")
        .leftJoin("core_vendor_products","core_vendor_products.id","core_product_vendor_products.vendor_product_id")
        .leftJoin("core_service_providers","core_service_providers.id","core_vendor_products.vendor_id")
        .where("core_vendor_products.id",id)
         .apply_conditions(
                filter_json=filter_json,
                allowed_filters=[],
                search_string=search_string,
                search_columns=["core_vendor_products.name"]
            )
            .paginate(
                page=page,
                limit=limit,
                allowed_sorting_columns=allowed_sorting_columns,
                sort_by=sort_by,
                sort_dir=sort_dir
            )
        

    )

    return ResponseService.response("SUCCESS", data, "data_get")

@csrf_exempt
@api_view(["GET"])
def product_group_insurers(request, id):
    try:
        product_group = QueryBuilderService("core_product_groups").where("id", id).first()
        if not product_group:
            return ResponseService.response("NOT_FOUND", [], "Product group not found")
        product_group_id = product_group["id"]

        # Get product IDs for this product group
        product_ids_result = (
            QueryBuilderService("core_product_group_products")
            .select("product_id")
            .where("product_group_id", product_group_id)
            .get()
        )
        
        if not product_ids_result:
            return ResponseService.response("SUCCESS", [], "No products found for this product group")
        
        # Extract product IDs from the result
        product_ids = [item["product_id"] for item in product_ids_result]

        # Get vendor product IDs for these products
        vendor_product_ids_result = (
            QueryBuilderService("core_product_vendor_products")
            .select("vendor_product_id")
            .whereIn("product_id", product_ids)
            .get()
        )
        
        if not vendor_product_ids_result:
            return ResponseService.response("SUCCESS", [], "No vendor products found for these products")
        
        # Extract vendor product IDs from the result
        vendor_product_ids = [item["vendor_product_id"] for item in vendor_product_ids_result]

        # Get vendor IDs for these vendor products
        vendor_ids_result = (
            QueryBuilderService("core_vendor_products")
            .select("vendor_id")
            .whereIn("id", vendor_product_ids)
            .get()
        )
        
        if not vendor_ids_result:
            return ResponseService.response("SUCCESS", [], "No vendors found for these vendor products")
        
        # Extract vendor IDs from the result
        vendor_ids = [item["vendor_id"] for item in vendor_ids_result]

        all_columns = [
            "core_service_providers.id",
            "core_service_providers.name",
            "core_service_providers.logo",
        ]

        # Get pagination and filtering parameters
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "core_service_providers.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["core_service_providers.name", "core_service_providers.id"]

        # Get service providers (insurers) for these vendors
        data = QueryBuilderService("core_service_providers") \
            .select(*all_columns) \
            .whereIn("id", vendor_ids) \
            .apply_conditions(
                filter_json=filter_json,
                allowed_filters=[],
                search_string=search_string,
                search_columns=["core_service_providers.name"]
            ) \
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        
        return ResponseService.response("SUCCESS", data, "data_get")
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "default_not_found")


@csrf_exempt
@api_view(["GET"])
def insurence_teams(request, product_group_id, id):
    try:
        insurer = QueryBuilderService("core_service_providers").where("id", id).first()
        if not insurer:
            return ResponseService.response("NOT_FOUND", [], "Insurer not found")
        insurer_id = insurer["id"]

        product_group = QueryBuilderService("core_product_groups").where("id", product_group_id).first()
        if not product_group:
            return ResponseService.response("NOT_FOUND", [], "Product group not found")
        product_group_request_id = product_group["id"]


        # Get vendor product IDs for this insurer
        vendor_product_ids_result = QueryBuilderService("core_vendor_products").where("vendor_id", insurer_id).select("id").get()
        if not vendor_product_ids_result:
            return ResponseService.response("SUCCESS", [], "No vendor products found for this insurer")
        
        vendor_product_ids = [item["id"] for item in vendor_product_ids_result]

        #Get product IDs for these vendor products
        product_ids_result = QueryBuilderService("core_product_vendor_products").whereIn("vendor_product_id", vendor_product_ids).select("product_id").get()
        if not product_ids_result:
            return ResponseService.response("SUCCESS", [], "No products found for these vendor products")
              
        product_ids = [item["product_id"] for item in product_ids_result]

        product_group_id_result = QueryBuilderService("core_product_group_products").whereIn("product_id", product_ids).select("product_group_id","product_id").get()
        if not product_group_id_result:
            return ResponseService.response("SUCCESS", [], "No product group products found for these products")
        
        product_group_ids_for_products = [item["product_group_id"] for item in product_group_id_result]
        core_product_ids_for_group = [item["product_id"] for item in product_group_id_result]

        # Ensure requested product group is present among mappings
        if product_group_request_id not in product_group_ids_for_products:
            return ResponseService.response("SUCCESS", [], "Product group not found for these products")


        # Get team IDs mapped to this product group
        team_ids_result = QueryBuilderService("core_product_group_teams").where("product_group_id", product_group_request_id).select("team_id").get()
        if not team_ids_result:
            return ResponseService.response("SUCCESS", [], "No teams found for these products")
        
        team_ids = list({item["team_id"] for item in team_ids_result if item.get("team_id") is not None})

        all_columns = [
            "core_teams.id",
            "core_teams.name",
        ]

        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "core_teams.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["core_teams.name", "core_teams.id"]
        
        # Get unique teams first
        data = QueryBuilderService("core_teams") \
            .select(*all_columns) \
            .whereIn("core_teams.id", team_ids) \
            .apply_conditions(
                filter_json=filter_json,
                allowed_filters=[],
                search_string=search_string,
                search_columns=["core_teams.name"]
            ) \
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        
        # If you need users for each team, you can add a separate query here
        # or modify the frontend to make a separate call to get users for each team
        
        return ResponseService.response("SUCCESS", data, "data_get")
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "default_not_found")


@csrf_exempt
@api_view(["GET", "PUT"])
def commission_setup_team_users(request, commission_setup_id, team_id):
    try:
        if request.method == "GET":
            # Pagination params
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            sort_by = request.GET.get("sort_by", "id")
            sort_dir = request.GET.get("sort_dir", "desc")
            allowed_sorting_columns = ["id", "core_users.display_name", "core_users.email"]

            # Get team details to determine roles
            team_details = QueryBuilderService("core_teams").where("id", team_id).first()
            leader_id = team_details.get("leader_id") if team_details else None
            detector_id = team_details.get("detector_id") if team_details else None
            manager_id = team_details.get("manager_id") if team_details else None

            # Paginated user query, ensure id is always present as 'id'
            users_paginated = QueryBuilderService("core_team_users") \
                .select("core_users.id as id", "core_users.display_name", "core_users.email","core_users.picture","core_users.code") \
                .leftJoin("core_users", "core_team_users.user_id", "core_users.id") \
                .where("core_team_users.team_id", team_id) \
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
            users = users_paginated.get("data", [])
            if not users:
                return ResponseService.response("NOT_FOUND", users_paginated, "no_users_found")

            # Get agent commission percent from crmf_commission_field_values (global for the setup)
            field_agent = QueryBuilderService("crmf_commission_fields").where("attribute_name", "agent_commission_percent").first()
            agent_commission_percent = None
            if field_agent:
                field_id = field_agent["id"]
                agent_values = QueryBuilderService("crmf_commission_field_values") \
                    .select("value", "type") \
                    .where("commission_field_id", field_id) \
                    .where("commission_setup_id", commission_setup_id) \
                    .get()
                if agent_values and len(agent_values) > 0:
                    agent_commission_percent = {
                        "value": agent_values[0].get("value"),
                        "type": agent_values[0].get("type")
                    }

            # Get revised commission values for these users in this commission setup
            field_revised = QueryBuilderService("crmf_commission_fields").where("attribute_name", "revised_commission_percent").first()
            revised_map = {}
            if field_revised:
                field_id = field_revised["id"]
                revised_values = QueryBuilderService("crmf_commission_field_values") \
                    .select("user_id", "value", "type") \
                    .where("commission_field_id", field_id) \
                    .where("commission_setup_id", commission_setup_id) \
                    .where("team_id", team_id) \
                    .get()
                for val in revised_values:
                    revised_map[val["user_id"]] = {"value": val["value"], "type": val["type"]}

            # Attach commission info to each user using 'id'
            for user in users:
                user_id = user.get("id")
                
                # Determine role based on team structure
                if user_id == leader_id:
                    user["role_name"] = "leader"
                elif user_id == detector_id:
                    user["role_name"] = "detector"
                elif user_id == manager_id:
                    user["role_name"] = "manager"
                else:
                    user["role_name"] = "sales agent"
                
                user["revised_commission"] = revised_map.get(user_id, None)
                user["agent_commission_percent"] = agent_commission_percent
                user["commission_type"] = agent_commission_percent["type"] if agent_commission_percent else None

            users_paginated["data"] = users
            return ResponseService.response("SUCCESS", users_paginated, "team_users_with_commission_paginated")
        elif request.method == "PUT":
            # Remove all previous revised commission values for this team and setup
            field = QueryBuilderService("crmf_commission_fields").where("attribute_name", "revised_commission_percent").first()
            if not field:
                return ResponseService.response("VALIDATION_ERROR", {"error": "revised_commission_percent field not found"}, "field_not_found")
            field_id = field["id"]
            QueryBuilderService("crmf_commission_field_values") \
                .where("commission_field_id", field_id) \
                .where("commission_setup_id", commission_setup_id) \
                .where("team_id", team_id) \
                .delete()
            # Insert new revised commission values from request body
            try:
                data = json.loads(request.body)
            except Exception:
                return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON"}, "invalid_json")
            now = datetime.datetime.now()
            for user in data:
                user_id = user.get("id")
                revised = user.get("revised_commission")
                if not user_id or not revised:
                    continue
                
                QueryBuilderService("crmf_commission_field_values").insert({
                    "commission_field_id": field_id,
                    "commission_setup_id": commission_setup_id,
                    "user_id": user_id,
                    "team_id": team_id,
                    "value": revised.get("value"),
                    "type": revised.get("type"),
                    "created_at": now,
                    "updated_at": now
                })
                print(field_id,commission_setup_id,team_id,user_id,'field_idfield_id2')
                
            return ResponseService.response("SUCCESS", {"updated": True}, "team_users_revised_commission_updated")
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "default_not_found")

# -- DRY Helper Functions --
def _check_team_finance_records(commission_setup_id, team_id):
    """
    Check if team has active finance records that would be affected by deletion.
    
    Args:
        commission_setup_id (int): Commission setup ID
        team_id (int): Team ID to check
        
    Returns:
        dict: {
            "has_active_records": bool,
            "details": str,
            "counts": dict
        }
    """
    try:
        counts = {
            "brokerage_commissions": 0,
            "agent_commissions": 0,
            "commission_payments": 0
        }
        
        # Check 1: Brokerage commissions linked to this commission setup
        brokerage_commissions = (
            QueryBuilderService("crmf_brokerage_commission")
            .where("commission_setup_id", commission_setup_id)
            .get()
        )
        counts["brokerage_commissions"] = len(brokerage_commissions)
        
        # Check 2: Agent commissions linked via brokerage commissions
        if brokerage_commissions:
            brokerage_ids = [bc["id"] for bc in brokerage_commissions]
            agent_commissions = (
                QueryBuilderService("crmf_agent_commission")
                .whereIn("brokerage_commission_id", brokerage_ids)
                .get()
            )
            counts["agent_commissions"] = len(agent_commissions)
            
            # Check 3: Commission payments linked via agent commissions
            if agent_commissions:
                agent_commission_ids = [ac["id"] for ac in agent_commissions]
                commission_payments = (
                    QueryBuilderService("crmf_agent_commission_payments")
                    .whereIn("agent_commission_id", agent_commission_ids)
                    .get()
                )
                counts["commission_payments"] = len(commission_payments)
        
        # Check 4: User commissions directly linked to this team and commission setup
        user_commissions = (
            QueryBuilderService("crmf_user_commissions")
            .where("commission_setup_id", commission_setup_id)
            .where("team_id", team_id)
            .whereNull("deleted_at")
            .get()
        )
        counts["user_commissions"] = len(user_commissions)
        
        # Determine if there are active records
        has_active_records = (
            counts["brokerage_commissions"] > 0 or
            counts["agent_commissions"] > 0 or
            counts["commission_payments"] > 0 or
            counts["user_commissions"] > 0
        )
        
        # Generate details message
        if has_active_records:
            details_parts = []
            if counts["brokerage_commissions"] > 0:
                details_parts.append(f"{counts['brokerage_commissions']} brokerage commission(s)")
            if counts["agent_commissions"] > 0:
                details_parts.append(f"{counts['agent_commissions']} agent commission(s)")
            if counts["commission_payments"] > 0:
                details_parts.append(f"{counts['commission_payments']} commission payment(s)")
            if counts["user_commissions"] > 0:
                details_parts.append(f"{counts['user_commissions']} user commission(s)")
            
            details = f"Team has active finance records: {', '.join(details_parts)}"
        else:
            details = "No active finance records found for this team"
        
        return {
            "has_active_records": has_active_records,
            "details": details,
            "counts": counts
        }
        
    except Exception as e:
        print(f"Error checking team finance records: {str(e)}")
        # If there's an error, err on the side of caution and prevent deletion
        return {
            "has_active_records": True,
            "details": f"Error checking finance records: {str(e)}",
            "counts": {}
        }

def _get_team_ids_for_insurer_product_group(insurer_ids, product_group_id):
    """
    Get team IDs for given insurer IDs and product group ID.
    This replicates the logic from insurence_teams endpoint.
    """
    try:
        all_team_ids = set()
        
        for insurer_id in insurer_ids:
            # Get vendor product IDs for this insurer
            vendor_product_ids_result = QueryBuilderService("core_vendor_products").where("vendor_id", insurer_id).select("id").get()
            if not vendor_product_ids_result:
                continue
            
            vendor_product_ids = [item["id"] for item in vendor_product_ids_result]

            # Get product IDs for these vendor products
            product_ids_result = QueryBuilderService("core_product_vendor_products").whereIn("vendor_product_id", vendor_product_ids).select("product_id").get()
            if not product_ids_result:
                continue
                
            product_ids = [item["product_id"] for item in product_ids_result]

            # Check if any of these products belong to the requested product group
            product_group_id_result = QueryBuilderService("core_product_group_products").whereIn("product_id", product_ids).select("product_group_id","product_id").get()
            if not product_group_id_result:
                continue
            
            product_group_ids_for_products = [item["product_group_id"] for item in product_group_id_result]

            # Ensure requested product group is present among mappings
            if product_group_id not in product_group_ids_for_products:
                continue

            # Get team IDs mapped to this product group
            team_ids_result = QueryBuilderService("core_product_group_teams").where("product_group_id", product_group_id).select("team_id").get()
            if team_ids_result:
                team_ids = [item["team_id"] for item in team_ids_result if item.get("team_id") is not None]
                all_team_ids.update(team_ids)
        
        return list(all_team_ids)
    except Exception as e:
        print(f"Error getting team IDs for insurer {insurer_ids} and product group {product_group_id}: {str(e)}")
        return []

def _validate_commission_setup(data):
    # Determine if this is product-based or product group-based setup
    has_product_id = "product_id" in data and data["product_id"] is not None
    has_product_group_id = "product_group_id" in data and data["product_group_id"] is not None
    
    # Handle single insurer_id format (convert to insurer_ids array for validation)
    if "insurer_id" in data and "insurer_ids" not in data:
        data["insurer_ids"] = [data["insurer_id"]]
    
    # Validate that exactly one of product_id or product_group_id is provided
    if not has_product_id and not has_product_group_id:
        return {"setup_type": "Either product_id or product_group_id must be provided"}
    
    if has_product_id and has_product_group_id:
        return {"setup_type": "Cannot specify both product_id and product_group_id"}
    
    # Base rules that apply to both types
    base_rules = {
        "transaction_type": "required|integer",
        "sales_team_ids": "required|array",  # Allow empty array
        "brokerage_revenue_percent": "required|array",
        "agent_commission_percent": "required|array",
        "commission_percent": "array",  # Make optional
        "revised_commission_percent": "array"
    }
    
    # Add specific rules based on setup type
    if has_product_id:
        base_rules.update({
            "product_id": "required|integer",
            "native_product_id": "required|integer",
        })
        # For product-based setups, insurer_id is optional (single insurer)
        if "insurer_id" in data:
            base_rules["insurer_id"] = "integer"
    else:  # product group based
        base_rules.update({
            "product_group_id": "required|integer",
        })
        # For product group-based setups, insurer_ids is required (multiple insurers)
        base_rules["insurer_ids"] = "required|array|min:1"
    
    errors = ValidatorService.validate(data, base_rules)
    
    # Additional validation: sales_team_ids can be empty array (optional teams)
    # For product group-based setups, sales_team_ids will be auto-populated if empty
    sales_team_ids = data.get("sales_team_ids", [])
    # Note: Empty sales_team_ids array is allowed - it will be auto-populated for product group setups
    
    # Additional validation for product group-based setups: ensure insurer_ids is not empty
    if has_product_group_id:
        insurer_ids = data.get("insurer_ids", [])
        if not insurer_ids or len(insurer_ids) == 0:
            if not errors:
                errors = {}
            errors["insurer_ids"] = "At least one insurer must be selected for product group-based setups"
    
    # Custom validation: ensure every revised_commission_percent entry has a team_id
    for idx, item in enumerate(data.get("revised_commission_percent", [])):
        if "team_id" not in item:
            if not errors:
                errors = {}
            errors[f"revised_commission_percent_{idx}"] = "Each revised commission must have a team_id"
    return errors

def _check_duplicate_commission_setup(setup_data):
    # Check if any of the team IDs already have a commission setup for this product/product_group/transaction_type
    team_ids = setup_data.get("sales_team_ids", [])
    
    # Determine if this is product-based or product group-based setup
    has_product_id = "product_id" in setup_data and setup_data["product_id"] is not None
    has_product_group_id = "product_group_id" in setup_data and setup_data["product_group_id"] is not None
    
    # If no team IDs, check for duplicates without team constraint
    if not team_ids:
        query = (
            QueryBuilderService("crmf_commission_setups")
            .where("transaction_type", int(setup_data["transaction_type"]))
            .whereNull("crmf_commission_setups.deleted_at")
        )
        
        # Add appropriate where clause based on setup type
        if has_product_id:
            query = query.where("product_id", int(setup_data["product_id"]))
            if "insurer_id" in setup_data and setup_data["insurer_id"] is not None:
                query = query.where("insurer_id", int(setup_data["insurer_id"]))
        elif has_product_group_id:
            query = query.where("product_group_id", int(setup_data["product_group_id"]))
            if "insurer_ids" in setup_data and setup_data["insurer_ids"]:
                insurer_ids = [int(insurer_id) for insurer_id in setup_data["insurer_ids"]]
                query = query.leftJoin("crmf_commission_setup_service_providers", 
                                     "crmf_commission_setups.id", 
                                     "crmf_commission_setup_service_providers.commission_setup_id")
                query = query.whereIn("crmf_commission_setup_service_providers.service_provider_id", insurer_ids)
        
        existing_setup = query.first()
        if existing_setup:
            return True
        return False
    
    # Check for duplicates with team IDs
    for team_id in team_ids:
        query = (
            QueryBuilderService("crmf_commission_setups")
            .leftJoin("crmf_commission_setup_teams", "crmf_commission_setups.id", "crmf_commission_setup_teams.commission_setup_id")
            .where("crmf_commission_setup_teams.team_id", int(team_id))
            .where("transaction_type", int(setup_data["transaction_type"]))
            .whereNull("crmf_commission_setups.deleted_at")
        )
        
        # Add appropriate where clause based on setup type
        if has_product_id:
            query = query.where("product_id", int(setup_data["product_id"]))
            # For product-based setups, also check insurer_id if provided
            if "insurer_id" in setup_data and setup_data["insurer_id"] is not None:
                query = query.where("insurer_id", int(setup_data["insurer_id"]))
        elif has_product_group_id:
            query = query.where("product_group_id", int(setup_data["product_group_id"]))
            # For product group-based setups, check if any of the insurers already exist
            if "insurer_ids" in setup_data and setup_data["insurer_ids"]:
                insurer_ids = [int(insurer_id) for insurer_id in setup_data["insurer_ids"]]
                # Check if any of the requested insurers already have a setup for this product group
                query = query.leftJoin("crmf_commission_setup_service_providers", 
                                     "crmf_commission_setups.id", 
                                     "crmf_commission_setup_service_providers.commission_setup_id")
                query = query.whereIn("crmf_commission_setup_service_providers.service_provider_id", insurer_ids)
        
        existing_setup = query.first()
        if existing_setup:
            return True
    return False

def _create_commission_setup(setup_data, now):
    # Determine if this is product-based or product group-based setup
    has_product_id = "product_id" in setup_data and setup_data["product_id"] is not None
    has_product_group_id = "product_group_id" in setup_data and setup_data["product_group_id"] is not None
    
    # Handle single insurer_id format (convert to insurer_ids array)
    if "insurer_id" in setup_data and "insurer_ids" not in setup_data:
        setup_data["insurer_ids"] = [setup_data["insurer_id"]]
    
    # Auto-populate sales_team_ids if not provided for product group-based setups
    if has_product_group_id and "insurer_ids" in setup_data:
        if not setup_data.get("sales_team_ids") or len(setup_data.get("sales_team_ids", [])) == 0:
            setup_data["sales_team_ids"] = _get_team_ids_for_insurer_product_group(
                setup_data["insurer_ids"], 
                setup_data["product_group_id"]
            )
    
    setup_data_to_insert = {
        "transaction_type": int(setup_data["transaction_type"]),
        "brokerage_revenue_percent": str(round(float(setup_data["brokerage_revenue_percent"][0]["value"]), 2)),
        "agent_commission_percent": str(round(float(setup_data["agent_commission_percent"][0]["value"]), 2)),
        "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
        "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    # Add fields based on setup type
    if has_product_id:
        setup_data_to_insert.update({
            "product_id": int(setup_data["product_id"]),
            "native_product_id": int(setup_data["native_product_id"]),
        })
        # Add insurer_id if provided (for product-based setups)
        if "insurer_id" in setup_data:
            setup_data_to_insert["insurer_id"] = int(setup_data["insurer_id"])
    elif has_product_group_id:
        setup_data_to_insert.update({
            "product_group_id": int(setup_data["product_group_id"]),
            "product_id": 0,  # Set default value for product_id (required by database)
            "native_product_id": 0,  # Set default value for native_product_id (required by database)
        })
        # Note: For product group-based setups, insurers are handled via CommissionSetupServiceProvider
    new_setup = QueryBuilderService("crmf_commission_setups").insert(setup_data_to_insert)
    if not new_setup or "id" not in new_setup:
        raise Exception("Failed to create commission setup")
    commission_id = new_setup["id"]
    
    # Insert team associations (only if sales_team_ids is not empty)
    team_ids = setup_data.get("sales_team_ids", [])
    if team_ids:  # Only insert if there are team IDs
        for team_id in team_ids:
            team_data = {
                "commission_setup_id": commission_id,
                "team_id": int(team_id),
                "created_at": now.strftime("%Y-%m-%d %H:%M:%S"),
            }
            QueryBuilderService("crmf_commission_setup_teams").insert(team_data)
    
    # Insert insurer associations for product group-based setups
    if has_product_group_id and "insurer_ids" in setup_data:
        insurer_ids = setup_data.get("insurer_ids", [])
        for insurer_id in insurer_ids:
            insurer_data = {
                "commission_setup_id": commission_id,
                "service_provider_id": int(insurer_id),
            }
            QueryBuilderService("crmf_commission_setup_service_providers").insert(insurer_data)
    commission_fields = QueryBuilderService("crmf_commission_fields").get()
    if not commission_fields:
        raise Exception("No commission fields found")
    field_map = {field["attribute_name"]: field["id"] for field in commission_fields}
    commission_arrays = [
        "brokerage_revenue_percent",
        "agent_commission_percent",
        "target_achievement_commission_percent"
    ]
    for key in commission_arrays:
        if key not in setup_data or key not in field_map:
            continue
        field_id = field_map[key]
        for item in setup_data[key]:
            insert_data = {
                "commission_field_id": field_id,
                "commission_setup_id": commission_id,
                "value": str(item["value"]),
                "type": str(item["type"]),
                "created_at": now,
                "updated_at": now
            }
            if not QueryBuilderService("crmf_commission_field_values").insert(insert_data):
                raise Exception(f"Failed to insert value for {key}")
    if "commission_percent" in setup_data and "commission_percent" in field_map:
        field_id = field_map["commission_percent"]
        for item in setup_data["commission_percent"]:
            value_data = {
                "commission_field_id": field_id,
                "commission_setup_id": commission_id,
                "user_id": int(item["user_id"]),
                "value": str(item["value"]),
                "type": str(item["type"]),
                "created_at": now,
                "updated_at": now
            }
            # Add team_id if provided
            if "team_id" in item:
                value_data["team_id"] = int(item["team_id"])
            if not QueryBuilderService("crmf_commission_field_values").insert(value_data):
                raise Exception("Failed to insert commission_percent value")
    if "revised_commission_percent" in setup_data and "revised_commission_percent" in field_map:
        field_id = field_map["revised_commission_percent"]
        for item in setup_data["revised_commission_percent"]:
            value_data = {
                "commission_field_id": field_id,
                "commission_setup_id": commission_id,
                "user_id": int(item["user_id"]),
                "value": str(item["value"]),
                "type": str(item["type"]),
                "created_at": now,
                "updated_at": now
            }
            # Add team_id if provided
            if "team_id" in item:
                value_data["team_id"] = int(item["team_id"])
            if not QueryBuilderService("crmf_commission_field_values").insert(value_data):
                raise Exception("Failed to insert revised_commission_percent value")
    return commission_id

@csrf_exempt
@api_view(["POST"])
def bulk_delete_commission_setups(request):
    """
    Bulk delete multiple commission setups and all their related data.
    This endpoint accepts a list of commission setup IDs to delete.
    """
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON"}, "invalid_json")
        
        # Validation rules
        rules = {
            "commission_setup_ids": "required|array"
        }
        
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "validation_error")
        
        commission_setup_ids = data.get("commission_setup_ids", [])
        
        if not commission_setup_ids:
            return ResponseService.response("VALIDATION_ERROR", {"error": "No commission setup IDs provided"}, "no_ids_provided")
        
        # Validate that all IDs are integers
        try:
            commission_setup_ids = [int(id) for id in commission_setup_ids]
        except (ValueError, TypeError):
            return ResponseService.response("VALIDATION_ERROR", {"error": "All commission setup IDs must be valid integers"}, "invalid_id_format")
        
        # Perform bulk soft delete
        results = bulk_soft_delete_commission_setups(commission_setup_ids)
        
        # Build response message
        message_parts = []
        if results['total_successful'] > 0:
            message_parts.append(f"Successfully deleted {results['total_successful']} commission setup(s)")
        if results['total_skipped'] > 0:
            message_parts.append(f"Skipped {results['total_skipped']} setup(s) with calculated commissions")
        if results['total_failed'] > 0:
            message_parts.append(f"Failed to delete {results['total_failed']} setup(s)")
        
        message = ". ".join(message_parts) if message_parts else "No action taken"
        
        if results['total_failed'] == 0 and results['total_skipped'] == 0:
            return ResponseService.response("SUCCESS", {
                "message": message,
                "results": results
            }, "bulk_delete_success")
        elif results['total_successful'] > 0:
            return ResponseService.response("PARTIAL_SUCCESS", {
                "message": message,
                "results": results
            }, "bulk_delete_partial")
        else:
            return ResponseService.response("ERROR", {
                "message": message,
                "results": results
            }, "bulk_delete_failed")
            
    except Exception as e:
        return ResponseService.response("ERROR", {"error": str(e)}, "bulk_delete_exception")

@csrf_exempt
@api_view(["DELETE"])
def remove_team_from_commission_setup(request, id, team_id):
    """
    Remove a team from commission setup and clean up all related data.
    This includes removing team associations and cleaning up commission field values.
    """
    try:
        # Step 1: Validate that commission setup exists
        commission_setup = (
            QueryBuilderService("crmf_commission_setups")
            .where("id", id)
            .whereNull("deleted_at")
            .first()
        )
        
        if not commission_setup:
            return ResponseService.response(
                "NOT_FOUND", 
                {}, 
                "commission_setup_not_found"
            )
        
        # Step 2: Validate that team exists in this commission setup
        team_association = (
            QueryBuilderService("crmf_commission_setup_teams")
            .where("commission_setup_id", id)
            .where("team_id", team_id)
            .first()
        )
        
        if not team_association:
            return ResponseService.response(
                "NOT_FOUND", 
                {}, 
                "team_not_found_in_commission_setup"
            )
        
        # Step 3: Check for active finance records that would be affected
        finance_check_result = _check_team_finance_records(id, team_id)
        
        if finance_check_result["has_active_records"]:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "message": "Cannot delete team with active commission records",
                    "details": finance_check_result["details"],
                    "affected_records": finance_check_result["counts"]
                },
                "team_deletion_blocked_finance_records"
            )
        
        # Step 4: Check if this is the only team (optional validation)
        remaining_teams = (
            QueryBuilderService("crmf_commission_setup_teams")
            .where("commission_setup_id", id)
            .get()
        )
        
        if len(remaining_teams) == 1:
            # This is the last team - log warning but allow if no finance records
            print(f"Warning: Removing the last team from commission setup {id}")
        
        with transaction.atomic():
            # Step 5: Delete commission field values with this team_id
            field_values_deleted = (
                QueryBuilderService("crmf_commission_field_values")
                .where("commission_setup_id", id)
                .where("team_id", team_id)
                .delete()
            )
            print(f"Deleted {field_values_deleted} commission field values for team {team_id}")
            
            # Step 6: Delete user commissions for this team (if any)
            user_commissions_deleted = (
                QueryBuilderService("crmf_user_commissions")
                .where("commission_setup_id", id)
                .where("team_id", team_id)
                .delete()
            )
            print(f"Deleted {user_commissions_deleted} user commissions for team {team_id}")
            
            # Step 7: Delete the team association
            team_association_deleted = (
                QueryBuilderService("crmf_commission_setup_teams")
                .where("commission_setup_id", id)
                .where("team_id", team_id)
                .delete()
            )
            print(f"Deleted team association: {team_association_deleted}")
            
            return ResponseService.response(
                "SUCCESS", 
                {
                    "message": f"Successfully removed team {team_id} from commission setup {id}",
                    "deleted_records": {
                        "field_values": field_values_deleted,
                        "user_commissions": user_commissions_deleted,
                        "team_association": team_association_deleted
                    }
                }, 
                "default_delete_success_msg"
            )
            
    except Exception as e:
        return ResponseService.response(
            "ERROR", 
            {"error": str(e)}, 
            "remove_team_from_commission_setup_exception"
        )