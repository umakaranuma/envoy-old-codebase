from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mServices import QueryBuilderService
from envoy_bu_policy_api.finance.models.crmf_incentive_setups import IncentiveSetup
from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import get_periods_for_setup, find_agents_for_period, aggregate_performance_data, calculate_incentive_reward, save_incentive_record, incentive_record_exists, generate_incentive_setup_code, incentive_record_exists_for_agent_period
import json
from django.db import transaction
import datetime
from mServices import ResponseService, ValidatorService
from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_DEFINITIONS
from django.http import JsonResponse
from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import  query_policies

# --- Utility and CRUD functions (must be defined before API views) ---
def get_incentive_setups(request):
    try:
        all_columns = [
            "crmf_incentive_setups.*",
            "CASE crmf_incentive_setups.reward_type_id WHEN 1 THEN 'Fixed' WHEN 2 THEN 'Percentage' WHEN 3 THEN 'Tiered' ELSE 'Unknown' END as reward_type",
            "crmf_reward_types.name as reward_type_name",
        ]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "crmf_incentive_setups.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["crmf_incentive_setups.id", "crmf_incentive_setups.name", "crmf_incentive_setups.incentive_code"]
        search_columns = ["crmf_incentive_setups.name", "crmf_incentive_setups.description", "crmf_incentive_setups.incentive_code"]
        allowed_sorting_columns = ["crmf_incentive_setups.id", "crmf_incentive_setups.name", "crmf_incentive_setups.created_at", "crmf_incentive_setups.incentive_code"]
        query = (
            QueryBuilderService("crmf_incentive_setups")
            .select(*all_columns)
            .leftJoin(
                "crmf_reward_types",
                "crmf_incentive_setups.reward_type_id",
                "crmf_reward_types.id"
            )
            .whereNull("crmf_incentive_setups.deleted_at")
        )
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
        return JsonResponse({
            "is_success": True,
            "message": "incentive_setups_retrieved",
            "result": data,
            "system_code": ""
        })
    except Exception as e:
        return JsonResponse({
            "is_success": False,
            "message": "default_not_found",
            "result": {"error": str(e)},
            "system_code": ""
        }, status=500)

def validate_logic_tree(tree):
    """
    Recursively validate the logic tree for AND/OR conditions and leaf conditions.
    """
    if not isinstance(tree, dict):
        return False, "Each condition must be a dict."
    if "logic" in tree:
        if tree["logic"] not in ("AND", "OR"):
            return False, f"Invalid logic operator: {tree['logic']}"
        if not isinstance(tree.get("conditions"), list) or not tree["conditions"]:
            return False, "Logic node must have a non-empty 'conditions' list."
        for cond in tree["conditions"]:
            valid, msg = validate_logic_tree(cond)
            if not valid:
                return False, msg
        return True, None
    # Leaf node
    if "field" not in tree or "operator" not in tree or "value" not in tree:
        return False, "Leaf condition must have 'field', 'operator', and 'value'."
    field = tree["field"]
    operator = tree["operator"]
    value = tree["value"]
    if field not in PERFORMANCE_FIELD_DEFINITIONS:
        return False, f"Invalid field: {field}"
    allowed_operators = set(PERFORMANCE_FIELD_DEFINITIONS[field]["operators"])
    if operator not in allowed_operators:
        return False, f"Invalid operator '{operator}' for field {field}"
    if value is None:
        return False, f"Value required for operator '{operator}' on field {field}"
    return True, None

def store_incentive_setup(request):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response(
                "VALIDATION_ERROR", {"error": "Invalid JSON data"}, "invalid_json"
            )
        # Validation rules
        rules = {
            "name": "required|string",
            "incentive_base_field": "required|string",
            "description": "string",
            "performance_fields": "required|list",  # Now a list of field-condition dicts
            "reward_type_id": "integer",
            "reward_type": "string",
            "reward_type_value": "numeric",  # Allow empty string, will be validated below
            "repeation_type": "required|string|in:One-Time,Monthly,Quarterly,Annually",
            "start_date": "required|date",
            "end_date": "required|date"
        }
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "validation_error")
        
        # Validate reward_type_value (handle empty string)
        reward_type_value = data.get("reward_type_value")
        if reward_type_value == "" or reward_type_value is None:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"reward_type_value": "reward_type_value is required and cannot be empty"},
                "validation_error"
            )
        try:
            reward_type_value = float(reward_type_value)
        except (ValueError, TypeError):
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"reward_type_value": f"reward_type_value must be a valid number, got: {data.get('reward_type_value')}"},
                "validation_error"
            )
        
        # Determine reward_type_id from reward_type string if reward_type_id is not provided
        reward_type_id = data.get("reward_type_id")
        reward_type = data.get("reward_type", "").lower().strip() if data.get("reward_type") else ""
        
        if not reward_type_id and reward_type:
            # Map reward_type string to reward_type_id
            # 1 = Fixed, 2 = Percentage, 3 = Tiered
            if reward_type in ["fixed", "flat"]:
                reward_type_id = 1
            elif reward_type in ["percentage", "percent", "%"]:
                reward_type_id = 2
            elif reward_type in ["tiered", "tier"]:
                reward_type_id = 3
            else:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"reward_type": f"Invalid reward_type '{data.get('reward_type')}'. Must be 'fixed', 'percentage', or 'tiered'"},
                    "validation_error"
                )
        elif not reward_type_id:
            # If neither reward_type_id nor reward_type is provided, default to Fixed
            reward_type_id = 1
            print(f"Warning: Neither reward_type_id nor reward_type provided, defaulting to Fixed (1)")
        
        # Validate that reward_type_id and reward_type match if both are provided
        if reward_type_id and reward_type:
            expected_id = None
            if reward_type in ["fixed", "flat"]:
                expected_id = 1
            elif reward_type in ["percentage", "percent", "%"]:
                expected_id = 2
            elif reward_type in ["tiered", "tier"]:
                expected_id = 3
            
            if expected_id and reward_type_id != expected_id:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"reward_type": f"reward_type '{data.get('reward_type')}' does not match reward_type_id {reward_type_id}"},
                    "validation_error"
                )
        # Validate date range
        start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        if start_date >= end_date:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"date_range": "End date must be after start date"},
                "validation_error"
            )
        # Validate performance_fields structure and values
        performance_fields = data.get("performance_fields", None)
        if not performance_fields:
            return ResponseService.response("VALIDATION_ERROR", {"performance_fields": "Must be provided"}, "validation_error")
        valid, msg = validate_logic_tree(performance_fields)
        if not valid:
            return ResponseService.response("VALIDATION_ERROR", {"performance_fields": msg}, "validation_error")
        with transaction.atomic():
            now = datetime.datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Generate unique incentive setup code
            setup_code = generate_incentive_setup_code()
            print(f"Generated incentive setup code: {setup_code}")
            
            # Store reward_type in performance_fields if provided
            if reward_type:
                if isinstance(performance_fields, dict):
                    performance_fields["reward_type"] = reward_type
                else:
                    performance_fields = {"reward_type": reward_type, "conditions": performance_fields}
            
            incentive_setup_data = {
                "name": data["name"],
                "incentive_code": setup_code,
                "incentive_base_field": data["incentive_base_field"],
                "description": data.get("description"),
                "performance_fields": json.dumps(performance_fields),
                "reward_type_id": int(reward_type_id),
                "reward_type_value": float(reward_type_value),
                "repeation_type": data["repeation_type"],
                "start_date": data["start_date"],
                "end_date": data["end_date"],
                "created_at": formatted_now,
                "updated_at": formatted_now
            }
            new_incentive_setup = QueryBuilderService("crmf_incentive_setups").insert(incentive_setup_data)
            if not new_incentive_setup or "id" not in new_incentive_setup:
                raise Exception("Failed to create incentive setup")
            return ResponseService.response(
                "SUCCESS",
                {"id": new_incentive_setup["id"]},
                "incentive_setup_created_successfully"
            )
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "database_error")

def get_incentive_setup_by_id(request, id):
    try:
        all_columns = [
            "crmf_incentive_setups.*",
            "CASE crmf_incentive_setups.reward_type_id WHEN 1 THEN 'Fixed' WHEN 2 THEN 'Percentage' END as reward_type",
            "crmf_reward_types.name as reward_type_name",
        ]
        incentive_setup = (
            QueryBuilderService("crmf_incentive_setups")
            .select(*all_columns)
            .leftJoin(
                "crmf_reward_types",
                "crmf_incentive_setups.reward_type_id",
                "crmf_reward_types.id"
            )
            .where("crmf_incentive_setups.id", id)
            .whereNull("crmf_incentive_setups.deleted_at")
            .first()
        )
        if not incentive_setup:
            return ResponseService.response(
                "NOT_FOUND",
                {},
                "incentive_setup_not_found"
            )
        return ResponseService.response("SUCCESS", incentive_setup, "incentive_setup_retrieved")
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "default_not_found")

def update_incentive_setup(request, id):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response(
                "VALIDATION_ERROR", {"error": "Invalid JSON data"}, "invalid_json"
            )
        # Validation rules
        rules = {
            "name": "required|string",
            "incentive_base_field": "required|string",
            "description": "string",
            "performance_fields": "required|list",
            "reward_type_id": "integer",
            "reward_type": "string",
            "reward_type_value": "numeric",  # Allow empty string, will be validated below
            "repeation_type": "required|string|in:One-Time,Monthly,Quarterly",
            "start_date": "required|date",
            "end_date": "required|date",
        }
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "validation_error")
        
        # Validate reward_type_value (handle empty string)
        reward_type_value = data.get("reward_type_value")
        if reward_type_value == "" or reward_type_value is None:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"reward_type_value": "reward_type_value is required and cannot be empty"},
                "validation_error"
            )
        try:
            reward_type_value = float(reward_type_value)
        except (ValueError, TypeError):
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"reward_type_value": f"reward_type_value must be a valid number, got: {data.get('reward_type_value')}"},
                "validation_error"
            )
        
        # Determine reward_type_id from reward_type string if reward_type_id is not provided
        reward_type_id = data.get("reward_type_id")
        reward_type = data.get("reward_type", "").lower().strip() if data.get("reward_type") else ""
        
        if not reward_type_id and reward_type:
            # Map reward_type string to reward_type_id
            # 1 = Fixed, 2 = Percentage, 3 = Tiered
            if reward_type in ["fixed", "flat"]:
                reward_type_id = 1
            elif reward_type in ["percentage", "percent", "%"]:
                reward_type_id = 2
            elif reward_type in ["tiered", "tier"]:
                reward_type_id = 3
            else:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"reward_type": f"Invalid reward_type '{data.get('reward_type')}'. Must be 'fixed', 'percentage', or 'tiered'"},
                    "validation_error"
                )
        elif not reward_type_id:
            # If neither reward_type_id nor reward_type is provided, use existing value from database
            existing_setup = QueryBuilderService("crmf_incentive_setups").where("id", id).first()
            if existing_setup:
                reward_type_id = existing_setup.get("reward_type_id", 1)
            else:
                reward_type_id = 1
            print(f"Warning: Neither reward_type_id nor reward_type provided, using existing value: {reward_type_id}")
        
        # Validate that reward_type_id and reward_type match if both are provided
        if reward_type_id and reward_type:
            expected_id = None
            if reward_type in ["fixed", "flat"]:
                expected_id = 1
            elif reward_type in ["percentage", "percent", "%"]:
                expected_id = 2
            elif reward_type in ["tiered", "tier"]:
                expected_id = 3
            
            if expected_id and reward_type_id != expected_id:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"reward_type": f"reward_type '{data.get('reward_type')}' does not match reward_type_id {reward_type_id}"},
                    "validation_error"
                )
        # Validate date range
        start_date = datetime.datetime.strptime(data["start_date"], "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(data["end_date"], "%Y-%m-%d").date()
        if start_date >= end_date:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"date_range": "End date must be after start date"},
                "validation_error"
            )
        # Validate performance_fields structure and values
        performance_fields = data.get("performance_fields", None)
        if not performance_fields:
            return ResponseService.response("VALIDATION_ERROR", {"performance_fields": "Must be provided"}, "validation_error")
        valid, msg = validate_logic_tree(performance_fields)
        if not valid:
            return ResponseService.response("VALIDATION_ERROR", {"performance_fields": msg}, "validation_error")
        with transaction.atomic():
            now = datetime.datetime.now()
            formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
            
            # Store reward_type in performance_fields if provided
            if reward_type:
                if isinstance(performance_fields, dict):
                    performance_fields["reward_type"] = reward_type
                else:
                    performance_fields = {"reward_type": reward_type, "conditions": performance_fields}
            
            update_data = {
                "name": data["name"],
                "incentive_base_field": data["incentive_base_field"],
                "description": data.get("description"),
                "performance_fields": json.dumps(performance_fields),
                "reward_type_id": int(reward_type_id),
                "reward_type_value": float(reward_type_value),
                "repeation_type": data["repeation_type"],
                "start_date": data["start_date"],
                "end_date": data["end_date"],
                "updated_at": formatted_now
            }
            
            # Only update incentive_code if provided in the request
            if "incentive_code" in data and data.get("incentive_code"):
                update_data["incentive_code"] = data["incentive_code"]
            updated = (
                QueryBuilderService("crmf_incentive_setups")
                .where("id", id)
                .whereNull("deleted_at")
                .update(update_data)
            )
            if not updated:
                return ResponseService.response(
                    "NOT_FOUND",
                    {},
                    "incentive_setup_not_found"
                )
            return ResponseService.response(
                "SUCCESS",
                {"id": id},
                "incentive_setup_updated_successfully"
            )
    except Exception as e:
        return ResponseService.response("DATABASE_ERROR", {"error": str(e)}, "database_error")

def delete_incentive_setup(request, id):
    try:
        now = datetime.datetime.now()
        formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
        deleted = (
            QueryBuilderService("crmf_incentive_setups")
            .where("id", id)
            .whereNull("deleted_at")
            .update({"deleted_at": formatted_now})
        )
        if not deleted:
            return ResponseService.response(
                "NOT_FOUND",
                {},
                "incentive_setup_not_found"
            )
        return ResponseService.response(
            "SUCCESS",
            {},
            "incentive_setup_deleted_successfully"
        )
    except Exception as e:
        return ResponseService.response("DATABASE_ERROR", {"error": str(e)}, "database_error")

# 1. GET all performance fields
@csrf_exempt
@api_view(["GET"])
def list_performance_field_definitions(request):
    """
    List all available performance field definitions (UI/validation metadata for all fields).
    For dropdown fields, populate values from database tables.
    """
    try:
        # Mapping of field names to their database tables and columns
        dropdown_field_mappings = {
            "risk_type": {
                "table": "crm_opportunity_types",
                "id_column": "id",
                "label_column": "title"
            },
            "product": {
                "table": "core_vendor_products",
                "id_column": "id",
                "label_column": "name"
            },
            "insurer": {
                "table": "core_service_providers",
                "id_column": "id",
                "label_column": "name"
            },
            "role": {
                "table": "core_roles",
                "id_column": "id",
                "label_column": "name"
            },
            "team_role": {
                "static_values": True,  # Special handling - use static values instead of database query
                "values": [
                    {"id": "team lead", "label": "Team Lead"},
                    {"id": "team member", "label": "Team Member"}
                ]
            },
            "native_product": {
                "table": "core_products",
                "id_column": "id",
                "label_column": "name"
            },
            "sales_agent": {
                "table": "core_users",
                "id_column": "id",
                "label_column": "display_name"
            }
        }
        
        field_defs = []
        for field_name, field_def in PERFORMANCE_FIELD_DEFINITIONS.items():
            field_data = {"field": field_name, **field_def}
            
            # If widget is dropdown and field has a mapping, populate values
            if field_def.get("widget") == "dropdown" and field_name in dropdown_field_mappings:
                mapping = dropdown_field_mappings[field_name]
                try:
                    # Check if this field uses static values (like team_role)
                    if mapping.get("static_values"):
                        field_data["values"] = mapping.get("values", [])
                    else:
                        # Fetch data from database
                        records = QueryBuilderService(mapping["table"])\
                            .select(mapping["id_column"], mapping["label_column"])\
                            .get()
                        
                        # Format as dropdown values: [{id: id, label: name}]
                        field_data["values"] = [
                            {
                                "id": record[mapping["id_column"]],
                                "label": record[mapping["label_column"]] or f"ID {record[mapping['id_column']]}"
                            }
                            for record in records
                        ]
                except Exception as e:
                    # If there's an error fetching data, set empty array
                    field_data["values"] = []
            
            field_defs.append(field_data)
        
        return ResponseService.response("SUCCESS", field_defs, "performance_field_definitions_listed")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "database_error")

# 2. GET all setups, POST to create setup
@csrf_exempt
@api_view(["GET", "POST"])
def incentive_setup(request):
    if request.method == "GET":
        return get_incentive_setups(request)
    elif request.method == "POST":
        return store_incentive_setup(request)

# 3. GET one, PUT to edit, DELETE to remove
@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def incentive_setup_single(request, id):
    try:
        if request.method == "GET":
            return get_incentive_setup_by_id(request, id)
        elif request.method == "PUT":
            return update_incentive_setup(request, id)
        elif request.method == "DELETE":
            return delete_incentive_setup(request, id)
    except Exception as e:
        return JsonResponse({
            "is_success": False,
            "message": "default_not_found",
            "result": {
                "error": str(e)
            },
            "system_code": ""
        }, status=500)

# 4. (Optional) APIs for related data for setup creation
@csrf_exempt
@api_view(["GET"])
def get_all_reward_types(request):
    try:
        reward_types = QueryBuilderService("crmf_reward_types").select("id", "name").get()
        return ResponseService.response("SUCCESS", reward_types, "reward_types_retrieved")
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "default_not_found")

@csrf_exempt
@api_view(["GET"])
def get_all_reward_configs(request):
    try:
        reward_configs = QueryBuilderService("crmf_reward_configs").select("id", "name").get()
        return ResponseService.response("SUCCESS", reward_configs, "reward_configs_retrieved")
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "default_not_found")

@csrf_exempt
@api_view(["GET"])
def get_repetition_types(request):
    """
    Get all available repetition types for incentive setups with pagination.
    """
    try:
        # Get pagination parameters
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "").lower()
        
        repetition_types = [
            {"id": 1, "name": "One-Time", "description": "Single occurrence incentive"},
            {"id": 2, "name": "Monthly", "description": "Monthly recurring incentive"},
            {"id": 3, "name": "Quarterly", "description": "Quarterly recurring incentive"},
            {"id": 4, "name": "Annually", "description": "Annual recurring incentive"}
        ]
        
        # Apply search filter
        if search_string:
            repetition_types = [
                rt for rt in repetition_types
                if search_string in rt.get("name", "").lower() or search_string in rt.get("description", "").lower()
            ]
        
        # Calculate pagination
        total = len(repetition_types)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = repetition_types[start:end]
        
        # Calculate last page
        last_page = (total // limit) + (1 if total % limit > 0 else 0) if limit > 0 else 0
        
        # Build pagination response matching QueryBuilderService.paginate() structure
        data = {
            "total_records": total,
            "per_page": limit,
            "current_page": page,
            "last_page": last_page,
            "data": paginated_data
        }
        
        return ResponseService.response("SUCCESS", data, "repetition_types_retrieved")
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "default_not_found")

@csrf_exempt
@api_view(["GET"])
def list_incentive_base_fields(request):
    """
    List all possible fields that can be used as incentive_base_field (numeric fields) with pagination.
    """
    try:
        # Get pagination parameters
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "").lower()
        
        # Get base fields (just field names like before)
        base_fields = [
            field for field, definition in PERFORMANCE_FIELD_DEFINITIONS.items()
            if definition.get("type") in ("Decimal", "Integer")
        ]
        
        # Apply search filter
        if search_string:
            base_fields = [
                field for field in base_fields
                if search_string in field.lower() or 
                (field in PERFORMANCE_FIELD_DEFINITIONS and 
                 search_string in PERFORMANCE_FIELD_DEFINITIONS[field].get("description", "").lower())
            ]
        
        # Calculate pagination
        total = len(base_fields)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = base_fields[start:end]

        # Helper: make a user-friendly label from the field key
        def _humanize(field_key):
            return field_key.replace("_", " ").title()

        # Build definitions (user-friendly + exact meaning) for the paginated fields
        definitions = {}
        for field in paginated_data:
            field_def = PERFORMANCE_FIELD_DEFINITIONS.get(field, {})
            full_desc = field_def.get("description", "")
            # Short, user-friendly description (first sentence if available)
            short_desc = full_desc.split(". ")[0].strip() if full_desc else ""

            definitions[field] = {
                "key": field,
                "label": _humanize(field),
                "type": field_def.get("type", ""),
                "short_description": short_desc,
                "full_description": full_desc,
            }
        
        # Calculate last page
        last_page = (total // limit) + (1 if total % limit > 0 else 0) if limit > 0 else 0
        
        # Build pagination response
        data = {
            "total_records": total,
            "per_page": limit,
            "current_page": page,
            "last_page": last_page,
            "data": paginated_data,
            "definitions": definitions,
        }

        # Wrap in standard JsonResponse structure
        return JsonResponse({
            "is_success": True,
            "message": "incentive_base_fields_listed",
            "result": data,
            "system_code": ""
        })
    except Exception as e:
        return JsonResponse({
            "is_success": False,
            "message": "database_error",
            "result": {"error": str(e)},
            "system_code": ""
        }, status=500)

def initiate_incentive_award(request, setup_id):
    try:
        setup_obj = IncentiveSetup.objects.filter(id=setup_id).first()
        if not setup_obj:
            return JsonResponse({"success": False, "message": "Incentive setup not found"}, status=404)
        # Import the Decimal conversion utility
        from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import convert_decimal_to_float
        
        setup = {
            "start_date": str(setup_obj.start_date),
            "end_date": str(setup_obj.end_date),
            "repeation_type": setup_obj.repeation_type,
            "performance_fields": setup_obj.performance_fields,
            "reward_type": setup_obj.reward_type,
            "reward_type_id": setup_obj.reward_type.id if setup_obj.reward_type else None,
            "reward_type_string": setup_obj.reward_type.reward_type if setup_obj.reward_type else None,
            "reward_type_value": convert_decimal_to_float(setup_obj.reward_type_value),
            "incentive_base_field": setup_obj.incentive_base_field,
            "id":setup_id
        }
        
        # Convert all Decimal values in setup to float
        setup = convert_decimal_to_float(setup)
        # Duplicate check logic
        total_awarded = 0
        total_skipped = 0
        periods = get_periods_for_setup(setup)
        for period_start, period_end in periods:
            period = {"start_date": period_start.strftime("%Y-%m-%d"), "end_date": period_end.strftime("%Y-%m-%d")}
            agent_ids = find_agents_for_period(setup, (period_start, period_end))
            print(agent_ids,'agent_ids')
            for agent_id in agent_ids:
                # Use period-based duplicate check instead of commission_date
                if incentive_record_exists_for_agent_period(setup["id"], agent_id, period_start, period_end):
                    print(f"Incentive record already exists for setup {setup['id']}, agent {agent_id}, period {period_start} to {period_end}")
                    total_skipped += 1
                    continue
                performance_data = aggregate_performance_data(agent_id, setup, period)
                print(performance_data,'performance_data')
                
                # Convert all Decimal values in performance_data to float
                performance_data = convert_decimal_to_float(performance_data)
                print(f"Converted performance data: {performance_data}")
                
                result = calculate_incentive_reward(setup, performance_data, agent_id)
                
                # Convert all Decimal values in result to float
                result = convert_decimal_to_float(result)
                print(f"Converted result: {result}")
                
                if result["eligible"]:
                    save_incentive_record(setup, agent_id, period, performance_data, result)
                    total_awarded += 1
        return JsonResponse({"success": True, "message": "Incentive calculation initiated.", "awarded": total_awarded, "skipped": total_skipped})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)

# Example endpoint to get detailed policy list for a given field/condition
@csrf_exempt
@api_view(["POST"])
def get_policies_by_field(request):
    """
    POST body: {"agent_id": int, "field_key": str, "operator": str, "value": any, "period": {"start_date": str, "end_date": str}}
    field_key must be present in PERFORMANCE_FIELD_DEFINITIONS and mapped in the registry.
    For select (list) operations, use the plural entity name (e.g., 'policies').
    """
    try:
        data = json.loads(request.body)
        agent_id = data["agent_id"]
        field_key = data["field_key"]
        operator = data["operator"]
        value = data["value"]
        period = data.get("period")
        result = query_policies(agent_id, field_key, operator, value, period)
        return ResponseService.response("SUCCESS", result, "policies_queried")
    except Exception as e:
        return ResponseService.response("ERROR", {"error": str(e)}, "query_error")

@api_view(['POST'])
def create_incentive_table(request):
    """
    Manually create the crmf_incentives table for testing purposes.
    """
    try:
        from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import create_incentive_table_simple
        
        print("=== Manual table creation requested ===")
        success = create_incentive_table_simple()
        
        if success:
            return JsonResponse({
                "success": True,
                "message": "crmf_incentives table created successfully"
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "Failed to create crmf_incentives table"
            }, status=500)
            
    except Exception as e:
        print(f"Error in create_incentive_table: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "success": False,
            "message": f"Error creating table: {str(e)}"
        }, status=500)

def run_all_incentive_awards(request):
    """
    Run incentive award process for all setups and periods, skipping if already awarded for that setup/agent/period.
    If any setup/period/agent fails, skip and continue with others. Collect errors for reporting.
    Performance optimized with timeout and limits.
    
    Query Parameters:
        - timeout: Maximum execution time in seconds (default: 300, was 60)
        - batch_size: Number of setups to process per batch (default: None, process all)
    """
    import time
    start_time = time.time()
    # Increased timeout from 60 to 300 seconds (5 minutes) to handle larger workloads
    # Can be overridden via query parameter: ?timeout=600
    max_execution_time = int(request.GET.get('timeout', 300))
    batch_size = request.GET.get('batch_size')  # Optional batch processing
    
    try:
        # Check table structure first
        from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import check_incentive_table_structure, test_database_connection, incentive_record_exists_for_period
        print("=== Running database connection test ===")
        db_test_result = test_database_connection()
        if not db_test_result:
            print(" Database connection test failed, but continuing with incentive calculation...")
        
        table_ok = check_incentive_table_structure()
        if not table_ok:
            print(" Table structure check failed, but continuing with incentive calculation...")
            print("This might result in errors when trying to save incentives, but we'll attempt the process anyway.")
            # Don't return error, continue with the process
            # The save_incentive_record function will handle any table issues
        
        setups = QueryBuilderService("crmf_incentive_setups").whereNull("deleted_at").get()
        print(f"Found {len(setups)} incentive setups to process")
        
        # Log all setup IDs being processed
        setup_ids = [s["id"] for s in setups]
        print(f"Setup IDs to process: {setup_ids}")
        
        total_awarded = 0
        total_skipped = 0
        errors = []
        processed_setup_ids = []
        last_processed_setup_id = None
        
        print(f"Processing {len(setups)} incentive setups...")
        print(f"Timeout set to {max_execution_time} seconds (can be overridden via ?timeout=N query parameter)")
        
        for idx, setup in enumerate(setups):
            print(f"\n{'='*80}")
            print(f"Processing Setup ID: {setup['id']} ({idx + 1}/{len(setups)})")
            print(f"{'='*80}")
            # Check timeout
            elapsed_time = time.time() - start_time
            if elapsed_time > max_execution_time:
                remaining_setups = len(setups) - idx
                print(f"⚠️  TIMEOUT: Reached {max_execution_time} seconds limit after processing {idx} setups")
                print(f"  Last processed setup: {last_processed_setup_id}")
                print(f"  Remaining setups: {remaining_setups}")
                print(f"  Recommendation: Increase timeout via ?timeout=600 or process in batches")
                errors.append({
                    "type": "timeout",
                    "message": f"Processing timeout after {max_execution_time} seconds",
                    "processed_setups": idx,
                    "total_setups": len(setups),
                    "last_processed_setup_id": last_processed_setup_id,
                    "remaining_setups": remaining_setups,
                    "elapsed_time": round(elapsed_time, 2)
                })
                break
                
            try:
                setup_obj = IncentiveSetup.objects.filter(id=setup["id"]).first()
                if not setup_obj:
                    continue
                # Import the Decimal conversion utility
                from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import convert_decimal_to_float
                
                setup_dict = {
                    "start_date": str(setup_obj.start_date),
                    "end_date": str(setup_obj.end_date),
                    "repeation_type": setup_obj.repeation_type,
                    "performance_fields": setup_obj.performance_fields,
                    "reward_type": setup_obj.reward_type,
                    "reward_type_id": setup_obj.reward_type.id if setup_obj.reward_type else None,
                    "reward_type_string": setup_obj.reward_type.reward_type if setup_obj.reward_type else None,
                    "reward_type_value": convert_decimal_to_float(setup_obj.reward_type_value),
                    "incentive_base_field": setup_obj.incentive_base_field,
                    "id": setup_obj.id
                }
                
                # Convert all Decimal values in setup_dict to float
                setup_dict = convert_decimal_to_float(setup_dict)
                print(f"Setup {setup_obj.id}: {setup_dict}")
                print(f"Performance fields: {setup_obj.performance_fields}")
                print(f"Performance fields type: {type(setup_obj.performance_fields)}")
                print(f"Reward type: {setup_obj.reward_type}")
                print(f"Reward type value: {setup_obj.reward_type_value}")
                print(f"Incentive base field: {setup_obj.incentive_base_field}")
                
                # Validate and normalize performance_fields structure
                try:
                    if isinstance(setup_obj.performance_fields, str):
                        performance_fields = json.loads(setup_obj.performance_fields)
                    else:
                        performance_fields = setup_obj.performance_fields
                    
                    print(f"Parsed performance fields: {performance_fields}")
                    print(f"Parsed performance fields type: {type(performance_fields)}")
                    
                    # Update the setup_dict with normalized performance_fields
                    setup_dict["performance_fields"] = performance_fields
                    
                except Exception as e:
                    print(f"Error parsing performance_fields for setup {setup_obj.id}: {e}")
                    errors.append({
                        "setup_id": setup_obj.id,
                        "error": f"Error parsing performance_fields: {str(e)}"
                    })
                    continue
                
                from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import get_periods_for_setup
                periods = get_periods_for_setup(setup_dict)
                print(f"Periods for setup {setup_obj.id}: {periods}")
                
                if not periods:
                    print(f"Warning: No periods found for setup {setup_obj.id}")
                    continue
                
                # Performance optimization: Skip very old setups
                current_year = datetime.datetime.now().year
                setup_start_year = None
                try:
                    if isinstance(setup_dict.get("start_date"), str):
                        setup_start_year = int(setup_dict.get("start_date")[:4])
                    elif hasattr(setup_dict.get("start_date"), 'year'):
                        setup_start_year = setup_dict.get("start_date").year
                except:
                    pass
                
                if setup_start_year and setup_start_year < (current_year - 15):  # Skip setups older than 15 years
                    print(f"Skipping setup {setup_dict['id']} - too old (start year: {setup_start_year})")
                    total_skipped += 1
                    continue
                
                # Check if this setup already has any incentives for any of its periods
                setup_has_incentives = False
                skipped_periods = []
                for period_start, period_end in periods:
                    if incentive_record_exists_for_period(setup_dict["id"], (period_start, period_end)):
                        skipped_periods.append(f"{period_start} to {period_end}")
                        print(f"*** Setup {setup_dict['id']} already has incentives for period {period_start} to {period_end}, skipping entire setup ***")
                        setup_has_incentives = True
                        total_skipped += 1
                        break
                
                if setup_has_incentives:
                    print(f"*** SKIPPING Setup {setup_dict['id']} - Records already exist for periods: {', '.join(skipped_periods)} ***")
                    last_processed_setup_id = setup_dict['id']
                    processed_setup_ids.append(setup_dict['id'])
                    continue
                
                # Performance optimization: Skip very old setups
                current_year = datetime.datetime.now().year
                setup_start_year = None
                try:
                    if isinstance(setup_dict.get("start_date"), str):
                        setup_start_year = int(setup_dict.get("start_date")[:4])
                    elif hasattr(setup_dict.get("start_date"), 'year'):
                        setup_start_year = setup_dict.get("start_date").year
                except:
                    pass
                
                if setup_start_year and setup_start_year < (current_year - 15):  # Skip setups older than 15 years
                    print(f"Skipping setup {setup_dict['id']} - too old (start year: {setup_start_year})")
                    total_skipped += 1
                    continue
                
                for period_start, period_end in periods:
                    period = {"start_date": period_start.strftime("%Y-%m-%d"), "end_date": period_end.strftime("%Y-%m-%d")}
                    print(f"Processing period: {period}")
                    
                    # Check if incentives already exist for this setup and period
                    if incentive_record_exists_for_period(setup_dict["id"], (period_start, period_end)):
                        print(f"Incentives already exist for setup {setup_dict['id']} and period {period}, skipping...")
                        total_skipped += 1
                        continue
                    
                    agent_ids = find_agents_for_period(setup_dict, (period_start, period_end))
                    print(f"*** Setup {setup_dict['id']} - Found {len(agent_ids)} agent IDs for period {period}: {agent_ids} ***")
                    
                    if not agent_ids:
                        print(f"*** WARNING: Setup {setup_dict['id']} - No agents found for period {period}, trying fallback approach... ***")
                        # Try to find agents without date filtering
                        try:
                            from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import get_registry_for_field
                            if isinstance(setup_obj.performance_fields, str):
                                pf = json.loads(setup_obj.performance_fields)
                            else:
                                pf = setup_obj.performance_fields
                            
                            if isinstance(pf, dict) and "conditions" in pf and pf["conditions"]:
                                # Filter fields that don't have registry entries
                                filter_fields = {"role", "role_id", "agent_id", "product", "insurer", "risk_type", "native_product", "product_id"}
                                
                                # Find the first field that has a registry entry (skip filter fields)
                                registry = None
                                for condition in pf["conditions"]:
                                    field = condition.get("field")
                                    if field and field not in filter_fields:
                                        registry = get_registry_for_field(field)
                                        if registry:
                                            break
                                
                                if registry:
                                    base_table = registry["base_table"]
                                    agent_field = registry.get("agent_field")
                                    joins = registry.get("joins", [])
                                    if agent_field:
                                        print(f"Trying fallback agent lookup from {base_table}")
                                        try:
                                            # Extract column name from agent_field (handle table.column format)
                                            if "." in agent_field:
                                                agent_column = agent_field.split(".")[-1]
                                                agent_table = agent_field.split(".")[0]
                                            else:
                                                agent_column = agent_field
                                                agent_table = base_table
                                            
                                            # Build query with joins if needed
                                            from django.db import connection
                                            sql = f"SELECT DISTINCT {agent_field} as agent_id FROM {base_table}"
                                            
                                            # Add joins
                                            for join in joins:
                                                sql += f" JOIN {join['table']} ON {join['on']}"
                                            
                                            # Execute query
                                            with connection.cursor() as cursor:
                                                cursor.execute(sql)
                                                results = cursor.fetchall()
                                                fallback_agent_ids = [row[0] for row in results if row[0] is not None]
                                                print(f"Fallback agent IDs from {base_table}: {fallback_agent_ids}")
                                                if fallback_agent_ids:
                                                    agent_ids = fallback_agent_ids
                                                    print(f"Using fallback agent IDs: {agent_ids}")
                                        except Exception as fallback_error:
                                            print(f"Fallback agent lookup failed: {fallback_error}")
                        except Exception as e:
                            print(f"Fallback agent lookup failed: {e}")
                    
                    if not agent_ids:
                        print(f"No agents found for period {period}, skipping...")
                        continue
                    
                    # Performance optimization: Limit agents per setup to prevent excessive processing
                    max_agents_per_setup = 10
                    if len(agent_ids) > max_agents_per_setup:
                        print(f"Limiting agents for setup {setup_dict['id']} from {len(agent_ids)} to {max_agents_per_setup} for performance")
                        agent_ids = agent_ids[:max_agents_per_setup]
                    
                    # Check if this is a team-based incentive
                    from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import is_team_based_incentive, check_all_team_members_achieved_target, calculate_collective_commission_for_team
                    is_team_incentive = is_team_based_incentive(setup_dict)
                    print(f"Incentive setup {setup_dict['id']} is team-based: {is_team_incentive}")
                    
                    # For team-based incentives, we need TEAM-LEVEL evaluation
                    # NOT individual agent evaluation using representative agent
                    if is_team_incentive:
                        # Extract product filter from conditions if present
                        product_id = None
                        performance_fields = setup_dict.get("performance_fields", {})
                        if isinstance(performance_fields, str):
                            import json
                            performance_fields = json.loads(performance_fields)
                        
                        product_id_from_condition = None
                        product_condition_field = None  # "product" = vendor, "native_product" = native
                        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                            for condition in performance_fields.get("conditions", []):
                                if isinstance(condition, dict):
                                    cond_field = condition.get("field")
                                    cond_value = condition.get("value")
                                    if cond_field in ["product", "product_id", "native_product"]:
                                        product_id_from_condition = int(cond_value) if cond_value else None
                                        product_condition_field = cond_field
                                        break
                        product_id = product_id_from_condition
                        
                        # Find all team managers (team leads) 
                        # Check if there's a team_role = "team lead" condition
                        has_team_lead_condition = False
                        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                            for condition in performance_fields.get("conditions", []):
                                if isinstance(condition, dict):
                                    cond_field = condition.get("field")
                                    cond_value = condition.get("value")
                                    if cond_field == "team_role":
                                        value_lower = str(cond_value).lower().strip()
                                        if value_lower in ["team lead", "team_lead", "manager", "lead"]:
                                            has_team_lead_condition = True
                                            break
                        
                        # CRITICAL FIX: Process EACH TEAM separately, not all teams under a manager together
                        # If a manager manages multiple teams, each team should be validated independently
                        from django.db import connection
                        teams_to_process = []
                        
                        with connection.cursor() as cursor:
                            if has_team_lead_condition:
                                # Get all teams managed by managers in agent_ids
                                placeholders = ",".join(["%s"] * len(agent_ids))
                                cursor.execute(f"""
                                    SELECT DISTINCT id, manager_id
                                    FROM core_teams
                                    WHERE manager_id IN ({placeholders})
                                    AND deleted_at IS NULL
                                """, agent_ids)
                                team_results = cursor.fetchall()
                                teams_to_process = [{"team_id": row[0], "manager_id": row[1]} for row in team_results if row[0] is not None]
                            else:
                                # If no team_role condition, get teams from agent_ids (assuming they're team IDs)
                                placeholders = ",".join(["%s"] * len(agent_ids))
                                cursor.execute(f"""
                                    SELECT id, manager_id
                                    FROM core_teams
                                    WHERE id IN ({placeholders})
                                    AND deleted_at IS NULL
                                """, agent_ids)
                                team_results = cursor.fetchall()
                                teams_to_process = [{"team_id": row[0], "manager_id": row[1]} for row in team_results if row[0] is not None]
                        
                        # When setup has a product (e.g. MBSL product 31), only process teams that are
                        # linked to that product in core_product_teams. So only that product's team lead gets the offer.
                        # core_product_teams.product_id is the NATIVE product id (core_products); incentive "product"
                        # dropdown uses vendor product id (core_vendor_products). Resolve vendor -> native when needed.
                        if product_id and teams_to_process:
                            product_team_ids = set()
                            ids_for_product_teams = [product_id]  # default: use as-is (native)
                            if product_condition_field in ["product", "product_id"]:
                                # Condition value is vendor product id; resolve to native product id(s)
                                try:
                                    native_rows = QueryBuilderService("core_product_vendor_products").where(
                                        "vendor_product_id", product_id
                                    ).select("product_id").get()
                                    if native_rows:
                                        ids_for_product_teams = [r["product_id"] for r in native_rows if r.get("product_id") is not None]
                                    else:
                                        ids_for_product_teams = []
                                except Exception as e:
                                    ids_for_product_teams = []
                                    print(f"Product-team resolve vendor->native failed: {e}")
                            if not ids_for_product_teams:
                                teams_to_process = []
                                print(f"Product filter: no native product linked to (vendor) product {product_id}, skipping team incentives")
                            else:
                                try:
                                    with connection.cursor() as c2:
                                        placeholders = ",".join(["%s"] * len(ids_for_product_teams))
                                        try:
                                            c2.execute(f"""
                                                SELECT team_id FROM core_product_teams
                                                WHERE product_id IN ({placeholders}) AND deleted_at IS NULL
                                            """, ids_for_product_teams)
                                        except Exception:
                                            c2.execute(f"""
                                                SELECT team_id FROM core_product_teams
                                                WHERE product_id IN ({placeholders})
                                            """, ids_for_product_teams)
                                        product_team_rows = c2.fetchall()
                                    product_team_ids = {row[0] for row in product_team_rows if row[0] is not None}
                                    if product_team_ids:
                                        teams_to_process = [t for t in teams_to_process if t["team_id"] in product_team_ids]
                                        print(f"Product filter: only teams linked to product {product_id} (native ids {ids_for_product_teams}): {sorted(product_team_ids)} -> {len(teams_to_process)} teams to process")
                                    else:
                                        teams_to_process = []
                                        print(f"Product filter: no teams linked to product {product_id} in core_product_teams, skipping team incentives for this product")
                                except Exception as e:
                                    teams_to_process = []
                                    print(f"Product-team filter failed (core_product_teams). No incentives for this product. Error: {e}")
                        
                        print(f"=== TEAM-LEVEL PROCESSING (Per-Team Validation) ===")
                        print(f"Found {len(teams_to_process)} teams to process")
                        print(f"Product filter: {product_id}")
                        
                        # Process EACH TEAM separately
                        for team_info in teams_to_process:
                            team_id = team_info["team_id"]
                            team_manager_id = team_info["manager_id"]
                            try:
                                print(f"\n{'='*80}")
                                print(f"Processing Team ID: {team_id}, Manager: {team_manager_id}")
                                print(f"{'='*80}")
                                
                                # Check if incentive already exists for this manager in this period
                                # If it exists, we'll UPDATE it by adding this team's commission (combine rewards)
                                existing_incentive = None
                                if incentive_record_exists_for_agent_period(setup_dict["id"], team_manager_id, period_start, period_end):
                                    # Get existing incentive record to update it
                                    from envoy_bu_policy_api.finance.models.crmf_incentives import Incentive
                                    existing_incentive = Incentive.objects.filter(
                                        incentive_setup_id=setup_dict["id"],
                                        agent_id=team_manager_id,
                                        period_start=period_start,
                                        period_end=period_end,
                                        deleted_at__isnull=True
                                    ).first()
                                    
                                    if existing_incentive:
                                        print(f"⚠️  Incentive record already exists for manager {team_manager_id} in period {period_start} to {period_end}")
                                        print(f"  This manager manages multiple teams. Will COMBINE rewards by adding this team's commission.")
                                        print(f"  Existing incentive amount: {existing_incentive.incentive_amount}")
                                        print(f"  Existing performance value: {existing_incentive.actual_performance_value}")
                                
                                # TEAM-LEVEL VALIDATION: Check if ALL members of THIS TEAM achieved their targets
                                # This validates ONE team at a time (not all teams under manager)
                                # When setup has a product condition (e.g. product 31), achievement is checked
                                # for THAT product only (premium from product 31 vs target). Reward base is also
                                # filtered by the same product. When no product in setup, achievement = overall.
                                team_validation_result = check_all_team_members_achieved_target(team_id, period, product_id)
                                
                                if not team_validation_result.get("all_achieved", False):
                                    print(f"❌ Team {team_id} (Manager {team_manager_id}) NOT eligible: {team_validation_result.get('message', 'Unknown reason')}")
                                    print(f"  Members achieved: {team_validation_result.get('members_achieved', 0)}/{team_validation_result.get('total_members', 0)}")
                                    for member_result in team_validation_result.get("member_results", []):
                                        status = "✅" if member_result.get("achieved_target") else "❌"
                                        print(f"  {status} Member {member_result.get('member_id')}: {member_result.get('achieved')} vs {member_result.get('target')} - {member_result.get('message')}")
                                    total_skipped += 1
                                    continue
                                
                                print(f"✅ Team {team_id} (Manager {team_manager_id}) ELIGIBLE: All {team_validation_result.get('total_members', 0)} members achieved target")
                                
                                # All members passed - now check other conditions (team_role, product, etc.)
                                # These are filter conditions, not achievement conditions
                                other_conditions_met = True
                                
                                # Check team_role condition if present
                                if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                                    from envoy_bu_policy_api.finance.controllers.utils.evaluate_incentive_logic import evaluate_filter_field
                                    for condition in performance_fields.get("conditions", []):
                                        if isinstance(condition, dict):
                                            cond_field = condition.get("field")
                                            cond_operator = condition.get("operator")
                                            cond_value = condition.get("value")
                                            
                                            # Check filter conditions (team_role, product, etc.)
                                            if cond_field == "team_role":
                                                team_role_met = evaluate_filter_field(cond_field, cond_operator, cond_value, team_manager_id)
                                                if not team_role_met:
                                                    print(f"❌ Team role condition not met for manager {team_manager_id}")
                                                    other_conditions_met = False
                                                    break
                                            # Product filter is already applied in team validation
                                            elif cond_field in ["product", "product_id", "native_product"]:
                                                # Already handled in team validation
                                                pass
                                            # Skip achievement conditions - already validated by team check
                                            elif cond_field in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
                                                # Already validated by team check
                                                pass
                                
                                if not other_conditions_met:
                                    print(f"❌ Other conditions not met for team manager {team_manager_id}")
                                    total_skipped += 1
                                    continue
                                
                                # All conditions met - calculate reward for TEAM MANAGER
                                reward_type_value = setup_dict.get("reward_type_value", 0)
                                reward_type_id = setup_dict.get("reward_type_id", 1)
                                is_percentage = (reward_type_id == 2)
                                
                                # REWARD BASE FIX: Use ONLY achieved members' collective commission
                                # Business rule: "10% of agent commission" = 10% of commission from members
                                # who actually achieved their targets in this team for the given period.
                                achieved_member_ids = [
                                    r["member_id"]
                                    for r in team_validation_result.get("member_results", [])
                                    if r.get("achieved_target")
                                ]

                                if not achieved_member_ids:
                                    print(f"❌ No team members with achieved targets for team {team_id}, manager {team_manager_id}")
                                    total_skipped += 1
                                    continue

                                collective_commission = calculate_collective_commission_for_team(
                                    achieved_member_ids,
                                    setup_dict,
                                    period,
                                    product_id
                                )
                                
                                if is_percentage:
                                    # Calculate percentage from team collective commission
                                    team_reward_amount = (collective_commission * float(reward_type_value)) / 100.0
                                    team_reward_amount = round(team_reward_amount, 2)
                                    print(f"Team {team_id} reward amount ({reward_type_value}% of team collective commission {collective_commission}): {team_reward_amount}")
                                else:
                                    # For fixed rewards, use the fixed amount directly
                                    team_reward_amount = float(reward_type_value)
                                    team_reward_amount = round(team_reward_amount, 2)
                                    print(f"Team {team_id} reward amount (fixed): {team_reward_amount}")
                                
                                # MULTI-TEAM HANDLING: If manager manages multiple teams, combine rewards
                                if existing_incentive:
                                    # MULTI-TEAM SCENARIO: Manager manages multiple teams
                                    # Combine this team's commission with existing incentive
                                    print(f"⚠️  MULTI-TEAM DETECTED: Manager {team_manager_id} already has incentive for this period")
                                    print(f"  Existing incentive ID: {existing_incentive.id}")
                                    print(f"  Existing incentive amount: {existing_incentive.incentive_amount}")
                                    print(f"  Existing performance value: {existing_incentive.actual_performance_value}")
                                    print(f"  Adding Team {team_id} commission: {collective_commission}")
                                    print(f"  Adding Team {team_id} reward: {team_reward_amount}")
                                    
                                    # Combine commissions and rewards
                                    combined_commission = float(existing_incentive.actual_performance_value or 0) + collective_commission
                                    combined_reward = float(existing_incentive.incentive_amount or 0) + team_reward_amount
                                    
                                    # Update existing record with combined values
                                    import datetime as dt
                                    from django.db import connection
                                    
                                    update_data = {
                                        "actual_performance_value": round(combined_commission, 2),
                                        "incentive_amount": round(combined_reward, 2),
                                        "performance_metric_value": round(combined_reward, 2),
                                        "updated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    }
                                    
                                    # Update the record
                                    with connection.cursor() as cursor:
                                        set_clauses = []
                                        params = []
                                        for key, value in update_data.items():
                                            if key == "updated_at":
                                                set_clauses.append(f"{key} = %s")
                                            else:
                                                set_clauses.append(f"{key} = %s")
                                            params.append(value)
                                        params.append(existing_incentive.id)
                                        
                                        sql = f"UPDATE crmf_incentives SET {', '.join(set_clauses)} WHERE id = %s"
                                        cursor.execute(sql, params)
                                    
                                    print(f"✅ Updated incentive record {existing_incentive.id} with combined values:")
                                    print(f"  Combined commission: {combined_commission}")
                                    print(f"  Combined reward: {combined_reward}")
                                    total_awarded += 1
                                else:
                                    # First team for this manager - create new incentive record
                                    team_performance_data = {
                                        setup_dict.get("incentive_base_field", "sum_of_agent_commission_recognized"): collective_commission
                                    }
                                    team_performance_data = convert_decimal_to_float(team_performance_data)
                                    
                                    # Create result dict for saving
                                    result = {
                                        "eligible": True,
                                        "reward_amount": team_reward_amount,
                                        "message": f"All team {team_id} members achieved target",
                                        "team_validation": team_validation_result
                                    }
                                    
                                    # Save incentive record for TEAM MANAGER (not members)
                                    print(f"Saving incentive record for TEAM MANAGER {team_manager_id} (Team {team_id})")
                                    print(f"Manager ID being saved: {team_manager_id}")
                                    print(f"Incentive amount being saved: {team_reward_amount}")
                                    print(f"Reward base: Team collective commission = {collective_commission}")
                                    
                                    save_success = save_incentive_record(setup_dict, team_manager_id, period, team_performance_data, result)
                                    if save_success:
                                        total_awarded += 1
                                        print(f"✅ Successfully saved incentive record for team manager {team_manager_id} (Team {team_id})")
                                    else:
                                        print(f"❌ Failed to save incentive record for team manager {team_manager_id}")
                                        errors.append({
                                            "setup_id": setup_dict["id"],
                                            "agent_id": team_manager_id,
                                            "team_id": team_id,
                                            "period": period,
                                            "error": "Failed to save incentive record"
                                        })
                                
                            except Exception as team_exc:
                                print(f"Error processing team {team_id} (manager {team_manager_id}): {team_exc}")
                                import traceback
                                traceback.print_exc()
                                errors.append({
                                    "setup_id": setup_dict["id"],
                                    "agent_id": team_manager_id,
                                    "team_id": team_id,
                                    "period": period,
                                    "error": str(team_exc)
                                })
                                continue
                        
                        # Skip individual agent processing for team-based incentives
                        print(f"Team-based incentive processing completed. Skipping individual agent processing.")
                        continue
                    
                    # Regular individual incentive (not team-based)
                    if not is_team_incentive:
                        # Regular individual incentive (not team-based)
                        # Use bulk aggregation for better performance
                        from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import aggregate_performance_data_bulk, incentive_record_exists_for_agent_period
                        
                        # Filter out agents that already have incentives for this period
                        eligible_agent_ids = []
                        for agent_id in agent_ids:
                            if incentive_record_exists_for_agent_period(setup_dict["id"], agent_id, period_start, period_end):
                                print(f"Incentive record already exists for setup {setup_dict['id']}, agent {agent_id}, period {period_start} to {period_end}")
                                total_skipped += 1
                            else:
                                eligible_agent_ids.append(agent_id)
                        
                        if not eligible_agent_ids:
                            print(f"All agents already have incentives for this period, skipping...")
                            continue
                        
                        # Bulk aggregate performance data for all eligible agents
                        print(f"Bulk aggregating performance data for {len(eligible_agent_ids)} agents")
                        bulk_performance_data = aggregate_performance_data_bulk(eligible_agent_ids, setup_dict, period)
                        print(f"Bulk aggregation completed, processing {len(bulk_performance_data)} agents")
                        
                        # Process each agent with their pre-aggregated data
                        for agent_id in eligible_agent_ids:
                            try:
                                print(f"Processing agent {agent_id} for period {period}")
                                
                                # Get pre-aggregated performance data
                                performance_data = bulk_performance_data.get(agent_id, {})
                                print(f"Performance data for agent {agent_id}: {performance_data}")
                                
                                # Convert all Decimal values in performance_data to float
                                performance_data = convert_decimal_to_float(performance_data)
                                print(f"Converted performance data for agent {agent_id}: {performance_data}")
                                
                                print(f"Calculating incentive reward for agent {agent_id}")
                                print(f"Performance data for agent {agent_id}: {performance_data}")
                                result = calculate_incentive_reward(setup_dict, performance_data, agent_id)
                                print(f"Incentive calculation result for agent {agent_id}: {result}")
                                
                                # Convert all Decimal values in result to float
                                result = convert_decimal_to_float(result)
                                print(f"Converted result for agent {agent_id}: {result}")
                                print(f"Reward amount: {result.get('reward_amount')}, Eligible: {result.get('eligible')}")
                                
                                if result["eligible"]:
                                    # Check if agent has any sales/commission - skip if incentive amount is 0
                                    reward_amount = result.get('reward_amount', 0)
                                    incentive_base_field = setup_dict.get("incentive_base_field")
                                    
                                    # Get performance_fields to check if it's target-based
                                    performance_fields = setup_dict.get("performance_fields", {})
                                    if isinstance(performance_fields, str):
                                        import json
                                        performance_fields = json.loads(performance_fields)
                                    
                                    # For target-based incentives, check if agent has achieved target
                                    # Don't skip if they achieved target even if base field is 0 (they might still get fixed reward)
                                    is_target_based = False
                                    if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                                        for condition in performance_fields.get("conditions", []):
                                            if isinstance(condition, dict):
                                                field = condition.get("field")
                                                if field in ["sum_of_agent_achieved", "sum_of_agent_sales_target"]:
                                                    is_target_based = True
                                                    break
                                    
                                    # Check if agent has actual sales/commission
                                    has_sales = False
                                    base_value = None

                                    if incentive_base_field:
                                        # Try to resolve the base field value similarly to calculate_incentive_reward
                                        # 1. Direct key lookup
                                        if incentive_base_field in performance_data:
                                            base_value = performance_data.get(incentive_base_field, 0)
                                        else:
                                            # 2. Look up via PERFORMANCE_FIELD_REGISTRY (parameter/field mapping)
                                            try:
                                                from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
                                                for reg in PERFORMANCE_FIELD_REGISTRY:
                                                    if reg.get("parameter") == incentive_base_field or incentive_base_field in reg.get("field", []):
                                                        # Try parameter key first
                                                        param_key = reg.get("parameter")
                                                        if param_key and param_key in performance_data:
                                                            base_value = performance_data.get(param_key, 0)
                                                        else:
                                                            # Then try all mapped field names
                                                            for field_name in reg.get("field", []):
                                                                if field_name in performance_data:
                                                                    base_value = performance_data.get(field_name, 0)
                                                                    break
                                                        if base_value is not None:
                                                            break
                                            except Exception as resolve_exc:
                                                print(f"Error resolving incentive_base_field '{incentive_base_field}' in has_sales check: {resolve_exc}")

                                        if base_value and float(base_value) > 0:
                                            has_sales = True
                                    else:
                                        # If no base field is configured, check common commission/volume fields
                                        commission_fields = [
                                            "sum_of_agent_commission_realized",
                                            "sum_of_agent_commission_recognized",
                                            "sum_of_brokerage_revenue_realized",
                                            "sum_of_brokerage_revenue_recognized",
                                            "sum_of_premium_amount"
                                        ]
                                        for field in commission_fields:
                                            if field in performance_data and performance_data.get(field, 0) > 0:
                                                has_sales = True
                                                break

                                    # Safety net: if reward_amount is already positive, treat as having sales
                                    try:
                                        if not has_sales and reward_amount and float(reward_amount) > 0:
                                            print(
                                                "has_sales inferred from positive reward_amount "
                                                f"(base field '{incentive_base_field}' not directly found)"
                                            )
                                            has_sales = True
                                    except (ValueError, TypeError):
                                        pass
                                    
                                    # For target-based incentives with percentage rewards, base field (commission) is required
                                    # For fixed rewards or if target is achieved, we should still create the record
                                    reward_type_id = setup_dict.get("reward_type_id", 1)
                                    is_percentage = (reward_type_id == 2)
                                    
                                    # Check if this is a penalty (negative reward_type_value indicates penalty)
                                    reward_type_value = setup_dict.get("reward_type_value", 0)
                                    is_penalty = False
                                    try:
                                        if reward_type_value and float(reward_type_value) < 0:
                                            is_penalty = True
                                    except (ValueError, TypeError):
                                        pass
                                    
                                    # Skip agents only if:
                                    # 1. It's a percentage reward AND base field is 0 AND it's NOT a penalty (penalties should be tracked even if 0)
                                    # 2. OR reward amount is exactly 0 AND it's not a target-based incentive AND it's NOT a penalty
                                    # 3. For penalties: Always create record if condition is met, even if amount is 0 (to track penalty was applied)
                                    should_skip = False
                                    if is_percentage and not has_sales and not is_penalty:
                                        # Percentage reward but no base value - skip (unless it's a penalty)
                                        print(f"Skipping agent {agent_id} - percentage reward but no base field value (incentive amount would be 0)")
                                        print(f"  Base field: {incentive_base_field}, Performance data keys: {list(performance_data.keys())}")
                                        should_skip = True
                                    elif reward_amount == 0 and not is_target_based and not is_penalty:
                                        # Non-target-based incentive with 0 amount - skip (unless it's a penalty)
                                        print(f"Skipping agent {agent_id} - incentive amount is 0 (not target-based)")
                                        should_skip = True
                                    elif reward_amount == 0 and is_target_based and is_percentage and not has_sales and not is_penalty:
                                        # Target-based percentage reward but no commission to calculate from - skip (unless it's a penalty)
                                        print(f"Skipping agent {agent_id} - target achieved but no commission to calculate percentage from")
                                        print(f"  Base field: {incentive_base_field}, Performance data: {performance_data}")
                                        should_skip = True
                                    
                                    # For penalties: Always create record if eligible, even if amount is 0 (to track that penalty was applied)
                                    # This must be checked AFTER all skip conditions to override them
                                    if is_penalty:
                                        print(f"Penalty detected for agent {agent_id} - will create record even if amount is 0 (to track penalty was applied)")
                                        should_skip = False
                                    
                                    if should_skip:
                                        total_skipped += 1
                                        continue
                                    
                                    # Log detailed information before saving
                                    print(f"=== SAVING INCENTIVE FOR AGENT {agent_id} ===")
                                    print(f"Agent ID: {agent_id}")
                                    print(f"Setup ID: {setup_dict.get('id')}")
                                    print(f"Reward Amount: {reward_amount}")
                                    print(f"Base Field: {incentive_base_field}")
                                    print(f"Base Field Value: {base_value if 'base_value' in locals() else 'N/A'}")
                                    print(f"Has Sales: {has_sales}")
                                    print(f"Is Target-Based: {is_target_based}")
                                    print(f"Is Penalty: {is_penalty if 'is_penalty' in locals() else 'N/A'}")
                                    print(f"Performance Data: {performance_data}")
                                    # Log target achievement if applicable
                                    if is_target_based:
                                        achieved = performance_data.get("sum_of_agent_achieved", 0)
                                        target = performance_data.get("sum_of_agent_sales_target", 0)
                                        if target and float(target) > 0:
                                            achievement_pct = (float(achieved) / float(target)) * 100.0
                                            print(f"Target Achievement: {achieved} / {target} = {achievement_pct:.2f}%")
                                        else:
                                            print(f"Target Achievement: {achieved} / {target} (target is 0 or missing)")
                                    print(f"Result: {result}")
                                    
                                    # CRITICAL: Check if incentive already exists for this agent + setup + period combination
                                    # This prevents duplicate generation when run-all is called multiple times for the same date/period
                                    if incentive_record_exists_for_agent_period(setup_dict["id"], agent_id, period_start, period_end):
                                        print(f"⏭️  SKIPPED: Incentive record already exists for agent {agent_id}, setup {setup_dict['id']}, period {period_start} to {period_end}")
                                        total_skipped += 1
                                        continue
                                    
                                    print(f"Saving incentive record for agent {agent_id}")
                                    print(f"Agent ID being saved: {agent_id}")
                                    print(f"Incentive amount being saved: {result.get('reward_amount')}")
                                    save_success = save_incentive_record(setup_dict, agent_id, period, performance_data, result)
                                    if save_success:
                                        total_awarded += 1
                                        print(f"Successfully saved incentive record for agent {agent_id}")
                                    else:
                                        print(f"Failed to save incentive record for agent {agent_id}")
                                        errors.append({
                                            "setup_id": setup_dict["id"],
                                            "agent_id": agent_id,
                                            "period": period,
                                            "error": "Failed to save incentive record"
                                        })
                                else:
                                    print(f"Agent {agent_id} not eligible for incentive: {result.get('message', 'Unknown reason')}")
                                    print(f"  Performance data: {performance_data}")
                                    print(f"  Result: {result}")
                            except Exception as agent_exc:
                                print(f"Error processing agent {agent_id}: {agent_exc}")
                                import traceback
                                traceback.print_exc()
                                # Convert any Decimal objects to float for JSON serialization
                                error_msg = str(agent_exc)
                                if "Object of type Decimal is not JSON serializable" in error_msg:
                                    error_msg = "Decimal serialization error - converting to float"
                                
                                errors.append({
                                    "setup_id": setup_dict["id"],
                                    "agent_id": agent_id,
                                    "period": period,
                                    "error": error_msg
                                })
                                continue
                # Mark setup as processed successfully
                last_processed_setup_id = setup_dict.get("id")
                processed_setup_ids.append(setup_dict.get("id"))
            except Exception as setup_exc:
                # Convert any Decimal objects to float for JSON serialization
                error_msg = str(setup_exc)
                if "Object of type Decimal is not JSON serializable" in error_msg:
                    error_msg = "Decimal serialization error - converting to float"
                
                errors.append({
                    "setup_id": setup.get("id"),
                    "error": error_msg
                })
                # Still mark as processed (even if with error) for timeout tracking
                last_processed_setup_id = setup.get("id")
                processed_setup_ids.append(setup.get("id"))
                continue
        elapsed_time = time.time() - start_time
        return JsonResponse({
            "is_success": True,
            "message": "incentive_setup_retrieved",
            "result": {
                "awarded": total_awarded,
                "skipped": total_skipped,
                "errors": errors,
                "total_setups": len(setups),
                "processed_setups": len(processed_setup_ids),
                "processed_setup_ids": processed_setup_ids,
                "last_processed_setup_id": last_processed_setup_id,
                "elapsed_time_seconds": round(elapsed_time, 2),
                "timeout_seconds": max_execution_time
            },
            "system_code": ""
        })
    except Exception as e:
        # Convert any Decimal objects to float for JSON serialization
        error_msg = str(e)
        if "Object of type Decimal is not JSON serializable" in error_msg:
            error_msg = "Decimal serialization error - converting to float"
        
        return JsonResponse({"success": False, "message": error_msg}, status=500)

@csrf_exempt
@api_view(["GET", "POST"])
def advanced_user_search(request):
    try:
        # Support both GET (with search query parameter) and POST (with keywords in JSON body)
        search_string = request.GET.get("search", "")
        
        # For POST requests, get keywords from JSON body
        if request.method == "POST":
            try:
                data = json.loads(request.body)
                keywords = data.get("keywords", [])
                # If keywords provided in POST, convert to search string
                if keywords:
                    search_string = " ".join(keywords) if isinstance(keywords, list) else str(keywords)
            except:
                keywords = []
        else:
            # For GET requests, use search query parameter
            keywords = [search_string] if search_string else []
        
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "display_name")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["id", "display_name", "email"]
        
        # Define search columns for apply_conditions (like in policy controllers)
        search_columns = [
            "core_users.display_name",
            # "core_users.email"
        ]

        # If no search string, return all users paginated
        if not search_string:
            users_paginated = QueryBuilderService("core_users") \
                .select("id", "display_name", "email", "role_id") \
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
            users = users_paginated.get("data", [])
            # Attach team(s) and role name
            team_map = {}
            if users:
                user_ids_page = [u["id"] for u in users]
                team_user_rows = QueryBuilderService("core_team_users").select("user_id", "team_id").whereIn("user_id", user_ids_page).get()
                team_ids_page = list(set([row["team_id"] for row in team_user_rows]))
                teams = QueryBuilderService("core_teams").select("id", "name").whereIn("id", team_ids_page).get()
                team_map = {t["id"]: t["name"] for t in teams}
                user_team_map = {}
                for row in team_user_rows:
                    user_team_map.setdefault(row["user_id"], []).append(team_map.get(row["team_id"]))
                for u in users:
                    u["teams"] = user_team_map.get(u["id"], [])
            # Attach role name
            if users:
                role_ids_page = list(set([u["role_id"] for u in users if u.get("role_id")]))
                roles = QueryBuilderService("core_roles").select("id", "name").whereIn("id", role_ids_page).get()
                role_map = {r["id"]: r["name"] for r in roles}
                for u in users:
                    u["role"] = role_map.get(u["role_id"]) if u.get("role_id") else None
            return ResponseService.response("SUCCESS", users_paginated, "users_found")

        user_ids = set()
        primary_user_ids = set()  # Initialize outside the if block
        
        # Primary search: Use apply_conditions like in policy controllers for user name/email
        # This provides partial matching with LIKE queries
        if search_string:
            user_query = QueryBuilderService("core_users") \
                .select("id", "display_name", "email", "role_id")
            
            # Apply search conditions (like in policy controllers)
            filter_json = json.loads(request.GET.get("filter", "{}"))
            allowed_filters = []
            user_query = user_query.apply_conditions(
                filter_json, allowed_filters, search_string, search_columns
            )
            
            # Get users matching the search string in display_name or email
            primary_user_rows = user_query.get()
            primary_user_ids = set([row["id"] for row in primary_user_rows])
            user_ids.update(primary_user_ids)
        
        # Secondary search: Only if no primary matches found, search in related entities
        if not primary_user_ids and search_string:
            # 1. Team name - use LIKE for partial matching
            team_rows = QueryBuilderService("core_teams").select("id").whereLike(["name"], search_string).get()
            team_ids = [row["id"] for row in team_rows]
            if team_ids:
                team_user_rows = QueryBuilderService("core_team_users").select("user_id").whereIn("team_id", team_ids).get()
                user_ids.update([row["user_id"] for row in team_user_rows])

            # 2. Role name - use LIKE for partial matching
            role_rows = QueryBuilderService("core_roles").select("id").whereLike(["name"], search_string).get()
            role_ids = [row["id"] for row in role_rows]
            if role_ids:
                role_user_rows = QueryBuilderService("core_users").select("id").whereIn("role_id", role_ids).get()
                user_ids.update([row["id"] for row in role_user_rows])

            # 3. Product name - use LIKE for partial matching
            product_rows = QueryBuilderService("core_vendor_products").select("id").whereLike(["name"], search_string).get()
            product_ids = [row["id"] for row in product_rows]
            if product_ids:
                # Find users linked to these products via issued policies through policy_base relationship
                issued_policy_rows = (
                    QueryBuilderService("crmp_issued_policies")
                    .select("crmp_policy_base.sales_agent_id")
                    .leftJoin("crmp_policy_base", "crmp_policy_base.id", "crmp_issued_policies.policy_base_id")
                    .whereIn("crmp_policy_base.product_id", product_ids)
                    .get()
                )
                user_ids.update([row["sales_agent_id"] for row in issued_policy_rows if row["sales_agent_id"]])

            # 4. Policy number (issued) - use LIKE for partial matching
            issued_policy_rows = (
                QueryBuilderService("crmp_issued_policies")
                .select("crmp_policy_base.sales_agent_id")
                .leftJoin("crmp_policy_base", "crmp_policy_base.id", "crmp_issued_policies.policy_base_id")
                .whereLike(["brokerage_policy_id"], search_string)
                .get()
            )
            user_ids.update([row["sales_agent_id"] for row in issued_policy_rows if row["sales_agent_id"]])

            # 5. Policy number (base/request) - use LIKE for partial matching
            request_policy_rows = QueryBuilderService("crmp_request_policies").select("policy_base_id").whereLike(["policy_request_id"], search_string).get()
            policy_base_ids = [row["policy_base_id"] for row in request_policy_rows if row.get("policy_base_id")]
            if policy_base_ids:
                base_policy_rows = QueryBuilderService("crmp_policy_base").select("request_by_id").whereIn("id", policy_base_ids).get()
                user_ids.update([row["request_by_id"] for row in base_policy_rows if row["request_by_id"]])

        # Remove None/empty
        user_ids = [uid for uid in user_ids if uid]
        if not user_ids:
            return ResponseService.response("SUCCESS", {"data": [], "total": 0, "page": page, "limit": limit}, "no_users_found")

        # If we have primary matches (user name/email), only return those
        # Don't include secondary matches (teams/roles/products/policies) when primary matches exist
        if search_string and primary_user_ids:
            user_ids = list(primary_user_ids)

        # Paginate
        users_paginated = QueryBuilderService("core_users") \
            .select("id", "display_name", "email", "role_id") \
            .whereIn("id", user_ids) \
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        users = users_paginated.get("data", [])

        # Attach team(s) and role name
        team_map = {}
        if users:
            user_ids_page = [u["id"] for u in users]
            team_user_rows = QueryBuilderService("core_team_users").select("user_id", "team_id").whereIn("user_id", user_ids_page).get()
            team_ids_page = list(set([row["team_id"] for row in team_user_rows]))
            teams = QueryBuilderService("core_teams").select("id", "name").whereIn("id", team_ids_page).get()
            team_map = {t["id"]: t["name"] for t in teams}
            user_team_map = {}
            for row in team_user_rows:
                user_team_map.setdefault(row["user_id"], []).append(team_map.get(row["team_id"]))
            for u in users:
                u["teams"] = user_team_map.get(u["id"], [])
        # Attach role name
        if users:
            role_ids_page = list(set([u["role_id"] for u in users if u.get("role_id")]))
            roles = QueryBuilderService("core_roles").select("id", "name").whereIn("id", role_ids_page).get()
            role_map = {r["id"]: r["name"] for r in roles}
            for u in users:
                u["role"] = role_map.get(u["role_id"]) if u.get("role_id") else None
        return ResponseService.response("SUCCESS", users_paginated, "users_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "search_error") 

@csrf_exempt
@api_view(["GET"])
def get_all_incentives(request):
    """
    List all incentives with filters, joins, and pagination.
    Filters: agent_id, commission_date, status
    Returns agent_name, incentive_setup_name, reward_type_name, and all main fields.
    """
    try:
        columns = [
            "crmf_incentives.*",
            "crmf_incentives.performance_metric_value as incentive_amount",
            "crmf_incentives.incentive_amount as incentive_amount_value",
            "core_users.display_name as agent_name",
            "crmf_incentive_setups.name as incentive_setup_name",
            "crmf_reward_types.id as rewar_type_id",
            "crmf_reward_types.name as reward_type_name"
        ]
        query = (
            QueryBuilderService("crmf_incentives")
            .select(*columns)
            .leftJoin("core_users", "core_users.id", "crmf_incentives.agent_id")
            .leftJoin("crmf_incentive_setups", "crmf_incentive_setups.id", "crmf_incentives.incentive_setup_id")
            .leftJoin("crmf_reward_types", "crmf_reward_types.id", "crmf_incentive_setups.reward_type_id")
            .whereNull("crmf_incentives.deleted_at")
        )
        # Filters
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "crmf_incentives.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = [
            "crmf_incentives.agent_id",
            "crmf_incentives.commission_date",
            "crmf_incentives.status",
            "crmf_incentives.incentive_setup_id",
            "crmf_incentives.reward_type_id"
        ]
        search_columns = [
            "core_users.display_name",
            "crmf_incentive_setups.name",
            "crmf_reward_types.name"
        ]
        sort_columns = [
            "crmf_incentives.id",
            "crmf_incentives.commission_date",
            "crmf_incentives.agent_id"
        ]
        # Apply filters and search
        data = query.apply_conditions(
            filter_json,
            allowed_filters,
            search_string,
            search_columns
        ).paginate(
            page,
            limit,
            sort_columns,
            sort_by,
            sort_dir
        )
        # Optionally format/rename fields if needed
        return ResponseService.response("SUCCESS", data, "incentives_fetched")
    except Exception as e:
        return ResponseService.response("ERROR", {"error": str(e)}, "error_fetching_incentives") 

@api_view(['POST'])
def cleanup_duplicates(request):
    """
    Clean up duplicate incentive records that may have been created.
    """
    try:
        from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import cleanup_duplicate_incentives
        print("=== Manual duplicate cleanup requested ===")
        cleaned_count = cleanup_duplicate_incentives()
        return JsonResponse({
            "is_success": True,
            "message": "duplicates_cleaned",
            "result": {
                "cleaned_count": cleaned_count,
                "message": f"Successfully cleaned {cleaned_count} duplicate records"
            },
            "system_code": ""
        })
    except Exception as e:
        print(f"Error in cleanup_duplicates: {e}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            "is_success": False,
            "message": "default_not_found",
            "result": {"error": f"Error cleaning duplicates: {str(e)}"},
            "system_code": ""
        }, status=500) 