import json
from django.shortcuts import get_object_or_404
from django.utils import timezone
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from envoy_bu_crm_api.quotation.models.crmq_quotation_form_submissions import QuotationFormSubmission
from envoy_bu_crm_api.quotation.models.crmq_quotation_service_providers import QuotationServiceProvider
from envoy_bu_crm_api.sales.models.OpportunityType import OpportunityType
from envoy_bu_crm_api.sales.models.core_models import Channel, Contact, Currency, Customer, Intraction, Task, User
from envoy_bu_crm_api.sales.models.opportunities import Opportunity
from envoy_bu_crm_api.sales.models.opportunity_form_submission import OpportunityFormSubmission
from envoy_bu_crm_api.sales.models.opportunity_health import OpportunityHealth
from envoy_bu_crm_api.sales.models.opportunity_oppor_type import OpportunityOpporType
from envoy_bu_crm_api.sales.models.opportunity_status import OpportunityStatus
from envoy_bu_crm_api.sales.models.opprtunity_task import OpportunityTask
from envoy_bu_crm_api.sales.models.risk import Risk
from envoy_bu_crm_api.sales.models.submission_risk import RiskSubmission
from envoy_bu_crm_api.service import _format_date_fields
from services.ActionService import ActionService
from services.ActivityService import ActivityService
from services.AuthService import AuthService
from services.NullableService import RequestPreprocessor
from services.SettingService import SettingService
from services.CodeService import CodeService
from services.EntityService import EntityService
from services.TaskService import TaskService
from messages import Message,Error
from setting_keys import SettingKeys
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from datetime import date, datetime
from django.db import DataError, transaction, IntegrityError

@csrf_exempt
@api_view(['GET', 'POST'])
def opportunity(request):
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return getAll(request)
    
    elif request.method == 'POST':
        action = ActionService.getAction("Opportunity","Create")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return create_opportunity(request)



from collections import defaultdict

def getAll(request):
    all_columns = [
        "oppo.*",
        "core_entities.created_at AS created_at",
        "core_entities.updated_at AS updated_at",
        "core_users.display_name AS sales_agent_name",
        "core_users.picture AS sales_agent_picture",
        "stage.name AS stage_name",
        "stage.type AS stage_type",
        "stage.color AS stage_color",
        "curr.name AS currency_name",
        "curr.symbol AS currency_symbol",
        "ch.name AS channel_name",
        "account_manager.display_name AS account_manager_name",
        "product.name AS product_name",
        "product_group.name AS product_group_name",
        "GROUP_CONCAT(DISTINCT oot.opportunity_type_id) AS opportunity_type_ids",
        "GROUP_CONCAT(DISTINCT ot.title) AS opportunity_type_names"
    ]

    fields = request.GET.get('fields', None)
    if fields == 'additional':
        all_columns.extend([
            # "oppo.contact_id",
            "contact.name AS contact_name",
            "contact.email AS contact_email",
            "contact.primary_contact AS primary_contact",
            "customer.name AS customer_name",
            "customer.logo AS customer_logo",
            "customer_contact.email AS customer_primary_contact_email",
            "customer_contact.address AS customer_primary_contact_address",
            "customer_contact.primary_contact AS customer_primary_contact_number"
        ])

    # Parse filters (supports URL-encoded JSON string under 'filters')
    raw_filter_json = request.GET.get("filters", '{}')
    print(f"Raw filter JSON: {raw_filter_json}")
    
    try:
        filter_dict = json.loads(raw_filter_json) if isinstance(raw_filter_json, str) else (raw_filter_json or {})
        print(f"Parsed filter dict: {filter_dict}")
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        filter_dict = {}
    
    # Extract type values for manual handling
    type_values = []
    if "type" in filter_dict and isinstance(filter_dict["type"], dict):
        type_filter = filter_dict["type"]
        print(f"Type filter found: {type_filter}")
        if isinstance(type_filter.get("v"), list):
            type_values = type_filter["v"]
        elif isinstance(type_filter.get("v"), str):
            type_values = [type_filter["v"]]
        print(f"Extracted type values: {type_values}")
    
    # Optional: support legacy 'type' param directly
    type_param = request.GET.get("type")
    if type_param and isinstance(type_param, str) and type_param.strip() and type_param.lower() not in ['','undefined','null']:
        if not type_values:  # Only add if no structured type filter
            type_values = [type_param.strip()]
    
    # Remove type from filter_dict since we'll handle it manually
    if "type" in filter_dict:
        del filter_dict["type"]

    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by')
    sort_dir = request.GET.get('sort_dir')
    # Normalize sort_by to include table alias if client passes raw column like 'sort_index'
    if sort_by in [None, ""]:
        sort_by = "oppo.id"
    elif sort_by == "sort_index":
        sort_by = "oppo.sort_index"
    
    # Check if any filters are applied
    filter_stage_id = request.GET.get('stage_id', None)
    filter_sales_agent_id = request.GET.get('sales_agent_id', None)
    filter_stage_type = request.GET.get('stage_type', None)
    filter_customer_id = request.GET.get('customer_id', None)
    
    # Set default sort direction based on sort field
    if sort_dir in [None, ""]:
        # For sort_index, default to ascending (natural board order)
        if sort_by == "oppo.sort_index":
            sort_dir = "asc"
        else:
            sort_dir = "desc"
    ids = request.GET.get('ids', None)
    quotation_filter = request.GET.get('quotation', None)
    allowed_filters = ['oppo.title', 'oppo.type', 'oppo.stage_id', 'oppo.sales_agent_id', 'oppo.contact_id', 'oppo.customer_id', 'stage.type']
    search_columns = ["oppo.title", "oppo.type", "oppo.code", "contact.name", "contact.primary_contact", "stage.name", "curr.name"]
    allowed_sorting_columns = ["oppo.title", "oppo.id", "oppo.sort_index"]

    # Map simple keys to fully-qualified columns expected by QueryBuilderService
    filter_aliases = {
        "title": "oppo.title",
        "type": "oppo.type",
        "stage_id": "oppo.stage_id",
        "sales_agent_id": "oppo.sales_agent_id",
        "contact_id": "oppo.contact_id",
        "customer_id": "oppo.customer_id",
    }
    mapped_filter_dict = { filter_aliases.get(k, k): v for k, v in filter_dict.items() }
    mapped_filter_json = json.dumps(mapped_filter_dict)

    data = (
        QueryBuilderService("crm_opportunities as oppo")
        .select(*all_columns)
        .leftJoin("core_entities", "core_entities.id", "oppo.entity_id")
        .leftJoin("core_users", "core_users.id", "oppo.sales_agent_id")
        .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")
        .leftJoin("core_currencies as curr", "curr.id", "oppo.currency_id")
        .leftJoin("core_channels as ch", "ch.id", "oppo.channel_id")
        .leftJoin("core_contacts as contact", "contact.id", "oppo.contact_id")
        .leftJoin("core_users as account_manager", "account_manager.id", "oppo.account_manager_id")
        .leftJoin("core_products as product", "product.id", "oppo.product_id")
        .leftJoin("core_product_groups as product_group", "product_group.id", "oppo.product_group_id")
        .leftJoin("crm_oppor_opportunity_types as oot", "oot.opportunity_id", "oppo.id")
        .leftJoin("crm_opportunity_types as ot", "oot.opportunity_type_id", "ot.id")
        .groupBy("oppo.id, oppo.title, oppo.type, oppo.contact_number, oppo.email, oppo.contact_id, oppo.customer_id, oppo.code, oppo.channel_id, oppo.last_contacted_date, oppo.campaign_id, oppo.stage_id, oppo.remarks, oppo.current_health_id, oppo.sales_agent_id, oppo.created_by_id, oppo.account_manager_id, oppo.currency_id, oppo.sort_index, oppo.lead_value, oppo.sale_value, oppo.country_id, oppo.transaction_type, oppo.issued_policy_id, oppo.entity_id, oppo.product_id, oppo.product_group_id, core_entities.created_at, core_entities.updated_at, core_users.display_name, core_users.picture, stage.name, stage.type, stage.color, curr.name, curr.symbol, ch.name, account_manager.display_name, product.name, product_group.name")
    )
    
    # Apply type filter manually using whereIn
    if type_values:
        print(f"Applying type filter with values: {type_values}")
        data = data.whereIn("oppo.type", type_values)
    else:
        print("No type values to filter")
    
    # Apply other filters and search using apply_conditions
    print(f"Applying conditions with mapped_filter_json: {mapped_filter_json}")
    data = data.apply_conditions(mapped_filter_json, allowed_filters, search_string, search_columns)

    if fields == 'additional':
        data = data.leftJoin("core_customers as customer", "customer.id", "oppo.customer_id")
        data = data.leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")
        data = data.groupBy("oppo.id, oppo.title, oppo.type, oppo.contact_number, oppo.email, oppo.contact_id, oppo.customer_id, oppo.code, oppo.channel_id, oppo.last_contacted_date, oppo.campaign_id, oppo.stage_id, oppo.remarks, oppo.current_health_id, oppo.sales_agent_id, oppo.created_by_id, oppo.account_manager_id, oppo.currency_id, oppo.sort_index, oppo.lead_value, oppo.sale_value, oppo.country_id, oppo.transaction_type, oppo.issued_policy_id, oppo.entity_id, oppo.product_id, oppo.product_group_id, core_entities.created_at, core_entities.updated_at, core_users.display_name, core_users.picture, stage.name, stage.type, stage.color, curr.name, curr.symbol, ch.name, account_manager.display_name, product.name, product_group.name, contact.name, contact.email, contact.primary_contact, customer.name, customer.logo, customer_contact.email, customer_contact.address, customer_contact.primary_contact")

    if filter_stage_id:
        data = data.where("oppo.stage_id", filter_stage_id)
    if filter_sales_agent_id:
        data = data.where("oppo.sales_agent_id", filter_sales_agent_id)
    if filter_stage_type:
        data = data.where("stage.type", filter_stage_type)
    if filter_customer_id:
        data = data.where("oppo.customer_id", filter_customer_id)

    # Filter for quotation parameter - return opportunities that don't have quotations
    if quotation_filter and quotation_filter.lower() == 'true':
        # Get all opportunity IDs that have quotations
        quoted_opportunity_ids = QueryBuilderService("crmq_quotations").select("opportunity_id").get()
        quoted_ids = [str(q["opportunity_id"]) for q in quoted_opportunity_ids if q.get("opportunity_id")]
        
        # Filter out opportunities that have quotations
        if quoted_ids:
            data = data.whereNotIn("oppo.id", quoted_ids)
    if ids:
        id_list = ids.split(',')
        data = data.whereIn("oppo.id", id_list).get()
    else:
        data = data.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)



    if isinstance(data, dict) and 'data' in data:
        items = data['data']
    else:
        items = data

    # Fetch latest health records for all opportunities
    opportunity_ids = [row.get('id') for row in items if row.get('id')]
    health_map = {}
    
    if opportunity_ids:
        # Get all health records for these opportunities
        all_health_records = (
            QueryBuilderService("crm_opportunity_health")
            .select("id", "opportunity_id", "health", "date")
            .whereIn("opportunity_id", opportunity_ids)
            .get()
        )
        
        # Group by opportunity_id and keep only the latest (highest id) for each
        for health_record in all_health_records:
            opp_id = health_record.get("opportunity_id")
            health_id = health_record.get("id")
            
            if opp_id not in health_map or health_id > health_map[opp_id].get("id"):
                health_map[opp_id] = {
                    "id": health_id,
                    "value": health_record.get("health"),
                    "date": health_record.get("date")
                }

    # Process opportunity types from GROUP_CONCAT results and add health data
    for row in items:
        opportunity_type_ids_str = row.get("opportunity_type_ids")
        opportunity_type_names_str = row.get("opportunity_type_names")
        
        if opportunity_type_ids_str and opportunity_type_names_str:
            # Split the concatenated strings
            type_ids = [int(id.strip()) for id in opportunity_type_ids_str.split(',') if id.strip()]
            type_names = [name.strip() for name in opportunity_type_names_str.split(',') if name.strip()]
            
            # Create opportunity types array
            row["opportunity_types"] = []
            for i, type_id in enumerate(type_ids):
                if i < len(type_names):
                    row["opportunity_types"].append({
                        "id": type_id,
                        "name": type_names[i]
                    })
        else:
            row["opportunity_types"] = []

        # Add latest health data from the health_map
        opp_id = row.get("id")
        if opp_id in health_map:
            health_data = health_map[opp_id]
            row["health_id"] = health_data["id"]
            row["health_value"] = health_data["value"]
            row["health_date"] = health_data["date"]
            row["health"] = health_data
        else:
            row["health_id"] = None
            row["health_value"] = None
            row["health_date"] = None
            row["health"] = None
        
        # Remove the individual health fields from response
        # row.pop("health_id", None)
        # row.pop("health_value", None)
        # row.pop("health_date", None)



    # Additional info mapping (tasks, contacts, customers)
    if fields == 'additional' and isinstance(data, dict) and 'data' in data:
        for item in items:
            if isinstance(item, dict):
                contact_id = item.get('contact_id')
                item['contact'] = {
                    'name': item.pop('contact_name', None),
                    'primary_contact': item.pop('primary_contact', None)
                } if contact_id else None

                customer_id = item.get('customer_id')
                item['customer'] = {
                    'name': item.pop('customer_name', None),
                    'logo': item.pop('customer_logo', None),
                    'email': item.pop('customer_primary_contact_email', None),
                    'address': item.pop('customer_primary_contact_address', None),
                    'primary_contact': item.pop('customer_primary_contact_number', None)
                } if customer_id else None

                opportunity_id = item.get('id')
                task_ids = OpportunityTask.objects.filter(opportunity_id=opportunity_id).values_list('task_id', flat=True)
                tasks = (
                    Task.objects
                    .filter(id__in=task_ids)
                    .select_related('task_status')
                    .order_by('sort_index')
                )
                selected_task = next((task for task in tasks if task.task_status and task.task_status.type.lower() == "task_todo"), None)
                item['next_task'] = {
                    'task': selected_task.task,
                    'start_date': selected_task.start_date,
                    'assigned_user_name': selected_task.assigned_to.display_name if selected_task.assigned_to else None,
                    'assigned_user_picture': selected_task.assigned_to.picture if selected_task.assigned_to else None
                } if selected_task else None

                

    return ResponseService.response('SUCCESS', data, Message.DATA_FETCHED)


def create_opportunity(request): 
    """ Create Opportunity with Required Fields & Auto-Create Tasks and Health"""

    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON format"}, Error.VALIDATION_ERROR)

    # Automatically assign the authenticated user as created_by_id
    user = request.user if request.user.is_authenticated else None

    if "created_by_id" not in data or not data["created_by_id"]:
        if user:
            data["created_by_id"] = user.id  # Assign the logged-in user's ID
        else:
            return ResponseService.response(
                "VALIDATION_ERROR", {"created_by_id": "User is required"}, Error.VALIDATION_ERROR
            )
        
    data["transaction_type"] = "new" if "transaction_type" not in data else data["transaction_type"].lower()

    # Convert empty strings to None for nullable fields
    nullable_fields = [
        "campaign_id", "contact_number", "email", "code", "remarks", "channel_id", 
        "sort_index", "entity_id", "current_health_id", "account_manager_id", 
        "sales_agent_id", "last_contacted_date", "health", "opportunity_type_id",
        "lead_value", "sale_value", "country_id", "issued_policy_id", "product_id", "product_group_id",
    ]
    for field in nullable_fields:
        if field in data and data[field] == "":
            data[field] = None

    # Auto-find account_manager_id if not provided and sales_agent_id is available
    if (not data.get("account_manager_id") or data.get("account_manager_id") == "") and data.get("sales_agent_id"):
        try:
            # Find the team_id for the sales_agent_id from core_team_users table
            team_user = QueryBuilderService("core_team_users")\
                .where("user_id", data["sales_agent_id"])\
                .select("team_id")\
                .first()
            
            if team_user and team_user.get("team_id"):
                # Find the manager_id from core_teams table
                team = QueryBuilderService("core_teams")\
                    .where("id", team_user["team_id"])\
                    .select("manager_id")\
                    .first()
                
                if team and team.get("manager_id"):
                    data["account_manager_id"] = team["manager_id"]
                    print(f"DEBUG: Auto-assigned account_manager_id: {data['account_manager_id']}")
                
        except Exception as e:
            # Log the error but don't fail the opportunity creation
            print(f"Warning: Could not auto-assign account manager: {e}")
            pass

    # Step 1: Validation Rules
    initial_rules = {
        "type": "required|in:Corporate,Personal",
        "contact_info_type": "required|in:manual,contact,customer",
        "stage_id": "required|exists:crm_opportunity_statuses,id",
        "currency_id": "required|exists:core_currencies,id",
        "opportunity_type_id": "array",
        "opportunity_type_id.*": "exists:crm_opportunity_types,id",
        "sales_agent_id": "exists:core_users,id",
        "channel_id": "exists:core_channels,id",
        "created_by_id": "required|exists:core_users,id",
        "account_manager_id": "exists:core_users,id",
        "health": "integer",
        "country_id": "exists:core_countries,id",
        "transaction_type": "in:new,renewal",
        "product_id": "exists:core_vendor_products,id",
        "product_group_id": "exists:core_product_groups,id",
    }

    custom_messages = {
        "opportunity_type_id.array": "Opportunity Type must be a list.",
        "opportunity_type_id.*.exists": "One or more provided opportunity types do not exist.",
        # "transaction_type.required": "Transaction type is required.",
        "transaction_type.in": "Transaction type must be one of: new, renewal."
    }

    # Remove nullable fields from validation if they are None, but preserve conditional validation rules
    for field in nullable_fields:
        if data.get(field) is None:
            # Check if this field has conditional validation rules (like required_if)
            if field in initial_rules:
                field_rules = initial_rules[field]
                # Only remove if it doesn't have conditional validation
                if not any(rule.startswith(('required_if:', 'required_unless:', 'required_with:', 'required_without:')) for rule in field_rules.split('|')):
                    initial_rules.pop(field, None)

    errors = ValidatorService.validate(data, initial_rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Step 2: Additional validation for contact_info_type
    rules = initial_rules.copy()

    # If renewal, only issued_policy_id must be present
    if (data.get("transaction_type") or "").lower() == "renewal":
        rules["issued_policy_id"] = "required|exists:crmp_issued_policies,id"
        custom_messages["issued_policy_id.required"] = "Issued Policy ID is required when transaction type is renewal."
        custom_messages["issued_policy_id.exists"] = "Invalid issued policy ID. Issued policy does not exist."
    else:
        rules["issued_policy_id"] = "nullable|exists:crmp_issued_policies,id"

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    setting_value = SettingService.getSettingKeyValue(SettingKeys.OPPORTUNITY_CUSTOMER_REQUIRED_STAGE)
    required_stage = int(setting_value) if setting_value is not None else None

    if data.get("stage_id") == required_stage:
        rules["customer_id"] = "required|exists:core_customers,id"
    else:
        contact_info_type = data.get("contact_info_type", "").lower()
        if contact_info_type == "manual":
            rules["contact_number"] = "required"
            rules["email"] = "email"
        elif contact_info_type == "customer":
            rules["customer_id"] = "required|exists:core_customers,id"
        elif contact_info_type == "contact":
            rules["contact_id"] = "required|exists:core_contacts,id"
        else:
            return ResponseService.response("VALIDATION_ERROR", {"contact_info_type": "Invalid contact_info_type"}, Error.VALIDATION_ERROR)

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Step 3: Validate Foreign Keys Safely
    try:
        foreign_keys = {
            "stage_id": OpportunityStatus,
            "currency_id": Currency,
            "customer_id": Customer,
            "contact_id": Contact,
            "sales_agent_id": User,
            "channel_id": Channel,
            "created_by_id": User,
            "account_manager_id": User,
        }
        for field, model in foreign_keys.items():
            if field in data and data[field] is not None:
                if not model.objects.filter(id=data[field]).exists():
                    return ResponseService.response("VALIDATION_ERROR", {field: "Invalid ID"}, Error.VALIDATION_ERROR)
    except Exception as e:
        return ResponseService.response("VALIDATION_ERROR", str(e), Error.VALIDATION_ERROR)

    # Step 4: Fetch the lowest sort_index for the given stage_id to place new opportunities at the top
    lowest_sort_index = (
        QueryBuilderService("crm_opportunities")
        .where("stage_id", data["stage_id"])
        .orderBy("sort_index", "asc")
        .select("sort_index")
        .first()
    )

    # New opportunities should have the smallest sort_index to appear first
    if lowest_sort_index and lowest_sort_index["sort_index"] is not None:
        # Place new opportunity before the current first one
        data["sort_index"] = lowest_sort_index["sort_index"] / 2
    else:
        # First opportunity in this stage
        data["sort_index"] = 1

    # Step 5: Handle title field
    if not data.get("title") or data["title"].strip() == "":
        last_stored_opportunity = QueryBuilderService("crm_opportunities").orderBy("id", "desc").select("id").first()
        last_id = last_stored_opportunity["id"] if last_stored_opportunity else 0
        data["title"] = f"Lead {last_id + 1}"

    # Step 6: Create Opportunity
    data["type"] = data.get("type", "").title()
    entity = EntityService.store("Opportunity", request)

    if not entity or "id" not in entity:
        return ResponseService.response("ERROR", None, "Failed to create entity")

    data["entity_id"] = entity["id"]
    data["code"] = CodeService.createOpporunityCode()

    # new_opportunity = QueryBuilderService("crm_opportunities").insert(data)

    health_value = data.pop("current_health_id", None)

    # Handle product information based on product_type
    product_type = data.get("product_type")
    product_id = data.get("product_id")
    
    if product_type and product_id:
        if product_type == "product":
            data["product_id"] = product_id
            data["product_group_id"] = None
        elif product_type == "group":
            data["product_id"] = None
            data["product_group_id"] = product_id
    
    # Remove the temporary product_type field from data before insertion
    data.pop("product_type", None)

    # Create Opportunity
    print(f"DEBUG: About to create opportunity with data: {data}")
    print(f"DEBUG: account_manager_id in data: {data.get('account_manager_id')}")
    # Ensure created_at is set since inserts use QueryBuilderService (not Django ORM)
    if "created_at" not in data or not data["created_at"]:
        data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_opportunity = QueryBuilderService("crm_opportunities").insert(data)
    print(f"DEBUG: Created opportunity: {new_opportunity}")

    # Create health record if value provided
    if health_value is not None:
        health_record = OpportunityHealth.objects.create(
            opportunity_id=new_opportunity["id"],
            date=date.today(),
            health=health_value   # store the actual health value
        )

        # Update opportunity with the generated health record ID
        QueryBuilderService("crm_opportunities")\
            .where("id", new_opportunity["id"])\
            .update({"current_health_id": health_record.id})

    # Step 9: Store opportunity_type_id
    opportunity_type_ids = data.get("opportunity_type_id", [])
    existing_type_ids = set(OpportunityType.objects.filter(id__in=opportunity_type_ids).values_list("id", flat=True))

    # Identify invalid IDs
    invalid_type_ids = set(opportunity_type_ids) - existing_type_ids

    if invalid_type_ids:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {
                "opportunity_type_id": [
                    {
                        "error_type": "exists",
                        "tokens": {
                            "_attribute": "opportunity_type_id"
                        }
                    }
                ]
            },
            Error.VALIDATION_ERROR
        )

    # Insert only valid IDs
    OpportunityOpporType.objects.bulk_create(
        [OpportunityOpporType(opportunity_id=new_opportunity["id"], opportunity_type_id=op_type_id) for op_type_id in existing_type_ids]
    )

    

    # Fetch the created opportunity with LEFT JOINs
    created_opportunity = (
        QueryBuilderService("crm_opportunities as oppo")
        .leftJoin("core_users", "core_users.id", "oppo.sales_agent_id")
        .leftJoin("core_users as account_manager", "account_manager.id", "oppo.account_manager_id")
        .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")
        .leftJoin("core_currencies as curr", "curr.id", "oppo.currency_id")
        .leftJoin("core_channels as ch", "ch.id", "oppo.channel_id")
        .leftJoin("crm_oppor_opportunity_types as oot", "oot.opportunity_id", "oppo.id")
        .leftJoin("crm_opportunity_types as ot", "oot.opportunity_type_id", "ot.id")
        .select(
            "oppo.*",
            "stage.name AS stage_name",
            "stage.type AS stage_type",
            "stage.color AS stage_color",
            "curr.name AS currency_name",
            "curr.symbol AS currency_symbol",
            "ch.name AS channel_name",
            "core_users.display_name AS sales_agent_name",
            "core_users.picture AS sales_agent_picture",
            "account_manager.display_name AS account_manager_name",
            "account_manager.picture AS account_manager_picture",
            "oot.opportunity_type_id"
        )
        .where("oppo.id", new_opportunity["id"])
        .get()
    )

    # Extract unique opportunity_type_ids
    opportunity_type_ids = list(set([row["opportunity_type_id"] for row in created_opportunity if row["opportunity_type_id"]]))

    # Update response to return opportunity_type_ids as an array
    if created_opportunity:
        created_opportunity[0]["opportunity_type_id"] = opportunity_type_ids

    # Log the activity using ActivityService
    ActivityService.store_activity(request=request, entity_id=entity["id"], activity="Lead Created")

    # Safely handle sales_agent_id
    sales_agent_id = new_opportunity.get("sales_agent_id", None)
    TaskService.saveOppourinityTask(new_opportunity["id"], data.get("stage_id"), sales_agent_id)

    # Log activity if sales_agent_id is not null
    if sales_agent_id:
        sales_agent = User.objects.get(id=sales_agent_id)
        ActivityService.store_activity(
            request=request,
            entity_id=new_opportunity["entity_id"],
            activity=f"Sales Agent {sales_agent.display_name}  is assigned to this opportunity"
        )

    # Handle renewal transaction type - duplicate risk details from existing policy
    if data.get("transaction_type") == "renewal" and data.get("issued_policy_id"):
        try:
            # Step 1: Get policy_base_id from crmp_issued_policies
            issued_policy = QueryBuilderService("crmp_issued_policies")\
                .where("id", data["issued_policy_id"])\
                .select("policy_base_id")\
                .first()
            
            if issued_policy and issued_policy.get("policy_base_id"):
                policy_base_id = issued_policy["policy_base_id"]
                
                # Step 2: Get risk_submission_ids from crmp_policy_risk_config
                policy_risk_configs = QueryBuilderService("crmp_policy_risk_config")\
                    .where("policy_base_id", policy_base_id)\
                    .select("risk_submission_id")\
                    .get()
                
                if policy_risk_configs:
                    risk_submission_ids = [prc["risk_submission_id"] for prc in policy_risk_configs if prc.get("risk_submission_id")]
                    
                    # Step 3: Get risk submission records from crm_risk_submissions
                    existing_risk_submissions = QueryBuilderService("crm_risk_submissions")\
                        .whereIn("id", risk_submission_ids)\
                        .get()
                    
                    # Step 4: Create new submissions and duplicate risk submission records with new lead_id
                    if existing_risk_submissions:
                        duplicated_count = 0
                        
                        for risk_submission in existing_risk_submissions:
                            # Get the original submission to get form_id
                            original_submission = QueryBuilderService("core_form_submissionss")\
                                .where("id", risk_submission["submission_id"])\
                                .select("form_id")\
                                .first()
                            
                            if original_submission:
                                # Create new submission in core_form_submissionss
                                new_submission = QueryBuilderService("core_form_submissionss").insert({
                                    "form_id": original_submission["form_id"],
                                    "user_id": request.user.id if request.user.is_authenticated else None,
                                    "customer_id": None
                                })
                                
                                # Copy form submission values from original submission to new submission
                                original_submission_values = QueryBuilderService("core_form_submission_valuess")\
                                    .where("form_submission_id", risk_submission["submission_id"])\
                                    .get()
                                
                                # Insert copied values for the new submission
                                for value_record in original_submission_values:
                                    QueryBuilderService("core_form_submission_valuess").insert({
                                        "form_submission_id": new_submission["id"],
                                        "custom_form_element_id": value_record["custom_form_element_id"],
                                        "form_element_id": value_record["form_element_id"],
                                        "value": value_record["value"]
                                    })
                                
                                # Create new submission risk entry with new submission_id and lead_id
                                # Increment version count by 1
                                new_version = risk_submission.get("version", 1) + 1
                                new_submission_risk_data = {
                                    "risk_id": risk_submission["risk_id"],
                                    "submission_id": new_submission["id"],
                                    "lead_id": new_opportunity["id"],
                                    "version": new_version,
                                    "created_at": date.today(),
                                    "updated_at": date.today()
                                }
                                
                                # Insert the new submission risk
                                QueryBuilderService("crm_risk_submissions").insert(new_submission_risk_data)
                                duplicated_count += 1
                        
                        # Log activity for risk duplication
                        ActivityService.store_activity(
                            request=request,
                            entity_id=new_opportunity["entity_id"],
                            activity=f"Created {duplicated_count} new risk submissions from issued policy {data['issued_policy_id']} for renewal opportunity"
                        )
        except Exception as e:
            # Log error but don't fail the opportunity creation
            print(f"Error duplicating risk details for renewal: {str(e)}")
            print(f"Error details: {type(e).__name__}: {str(e)}")
            ActivityService.store_activity(
                request=request,
                entity_id=new_opportunity["entity_id"],
                activity=f"Warning: Failed to duplicate risk details from issued policy {data.get('issued_policy_id', 'N/A')} - {str(e)}"
            )

    return ResponseService.response("SUCCESS", created_opportunity[0],Message.DATA_CREATED)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def single_opportunity_types(request, id):   
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return getSingle(request, id)
    
    elif request.method == 'PUT':
        action = ActionService.getAction("Opportunity","UPDATE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return update_single_opportunity(request, id)
    
    elif request.method == 'DELETE':
        action = ActionService.getAction("Opportunity","DELETE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return delete(request, id)

def getSingle(request, id):
    data = QueryBuilderService("crm_opportunities")\
            .where("id",id) \
            .first()
            
    if data:
        return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)
    else:
        return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)

def update_single_opportunity(request, id):
    """ Update a single opportunity """

    if not request.body or request.body == b'':
        return ResponseService.response("VALIDATION_ERROR", {"error": "Request body is empty"}, Error.VALIDATION_ERROR)

    data = json.loads(request.body)

    # Convert empty strings to None for nullable fields
    nullable_fields = [
        "campaign_id", "contact_number", "email", "remarks", "channel_id",
        "sort_index", "entity_id", "current_health_id", "account_manager_id",
        "sales_agent_id", "last_contacted_date", "health", "opportunity_type_id"
    ]
    for field in nullable_fields:
        if field in data and data[field] == "":
            data[field] = None

    # Validation rules
    rules = {
        "title": f"unique:crm_opportunities,title,{id}",  # Title is optional but must be unique if provided
        "stage_id": "exists:crm_opportunity_statuses,id",
        "currency_id": "exists:core_currencies,id",
        "sales_agent_id": "exists:core_users,id",
        "channel_id": "exists:core_channels,id",
        "account_manager_id": "exists:core_users,id",
        "health": "integer",
    }

    custom_messages = {
        "title.unique": "An opportunity with this title already exists.",
        "stage_id.exists": "Invalid stage ID.",
        "currency_id.exists": "Invalid currency ID.",
        "sales_agent_id.exists": "Invalid sales agent ID.",
        "channel_id.exists": "Invalid channel ID.",
        "account_manager_id.exists": "Invalid account manager ID.",
    }

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Fetch the existing opportunity
    existing_opportunity = QueryBuilderService("crm_opportunities").where("id", id).first()
    if not existing_opportunity:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Handle health updates
    new_health = data.get("health")
    if new_health is not None:
        current_health_id = existing_opportunity.get("current_health_id")
        if current_health_id:
            # Fetch the current health record
            current_health_record = OpportunityHealth.objects.filter(id=current_health_id).first()
            if current_health_record and current_health_record.health != new_health:
                # Create a new health record
                new_health_record = OpportunityHealth.objects.create(
                    opportunity_id=id,
                    date=date.today(),
                    health=new_health
                )
                # Update the `current_health_id` in the data
                data["current_health_id"] = new_health_record.id
        else:
            # Create a new health record if no current health exists
            new_health_record = OpportunityHealth.objects.create(
                opportunity_id=id,
                date=date.today(),
                health=new_health
            )
            data["current_health_id"] = new_health_record.id

    # Update the opportunity
    editable_fields = [
        "title", "type", "stage_id", "channel_id", "health", "currency_id",
        "account_manager_id", "sales_agent_id", "last_contacted_date", "remarks", "current_health_id"
    ]
    sanitized_data = {k: v for k, v in data.items() if k in editable_fields}

    updated = QueryBuilderService("crm_opportunities").where("id", id).update(sanitized_data)
    if not updated:
        return ResponseService.response("ERROR", None, "Failed to update opportunity")

    # Log activity for sales agent changes
    old_sales_agent_id = existing_opportunity.get("sales_agent_id")
    new_sales_agent_id = data.get("sales_agent_id")

    if new_sales_agent_id and new_sales_agent_id != old_sales_agent_id:
        # Import the history model
        from envoy_bu_crm_api.sales.models.sales_agent_history import SalesAgentHistory
        
        # Create history record
        history_record = SalesAgentHistory.objects.create(
            from_agent_id=old_sales_agent_id,
            to_agent_id=new_sales_agent_id,
            changed_by=request.user if request.user.is_authenticated else None,
            type=SalesAgentHistory.LEAD,
            lead_id=id,
            updated_at=timezone.now()
        )
        
        # Also maintain the existing activity logging
        if old_sales_agent_id:
            old_sales_agent = User.objects.get(id=old_sales_agent_id)
            new_sales_agent = User.objects.get(id=new_sales_agent_id)
            activity_message = (
                f"Sales Agent reassigned from {old_sales_agent.display_name} "
                f"to {new_sales_agent.display_name} for this opportunity"
            )
        else:
            new_sales_agent = User.objects.get(id=new_sales_agent_id)
            activity_message = (
                f"Sales Agent {new_sales_agent.display_name} "
                f"is assigned to this opportunity"
            )

        

    # Fetch the updated opportunity
    updated_opportunity = QueryBuilderService("crm_opportunities").where("id", id).first()

    ActivityService.store_activity(
            request=request,
            entity_id=updated_opportunity["entity_id"],
            activity=activity_message
        )

    return ResponseService.response("SUCCESS", updated_opportunity, Message.DATA_UPDATED)

def delete(request, id):
    deleted_data = QueryBuilderService("crm_opportunities")\
                    .where("id",id) \
                    .delete()           
    if deleted_data:
        return ResponseService.response('SUCCESS',deleted_data,Message.DATA_DELETED)
    else:
        return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)


@csrf_exempt
@api_view(["GET","PUT","DELETE"])
def single_opportunity(request, id):
    if request.method =='GET':
        action = ActionService.getAction("Opportunity", "VIEW")
        has_authority = AuthService.hasAuthority(request , action)

        if not has_authority:
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

        return get_single_opportunity(request, id)
    
    elif request.method == 'PUT':

        return update_opportunity(request,id)
    
    elif request.method == 'DELETE':

        return delete_opportunity(request,id)



def get_single_opportunity(request, id):
    """ Fetch a Single Opportunity with Related Data, Entity, Notes, and Documents """

    # Fetch Opportunity Data with Joins
    data = (
        QueryBuilderService("crm_opportunities as oppo")
        .leftJoin("core_entities", "core_entities.id", "oppo.entity_id")
        .leftJoin("core_users", "core_users.id","oppo.sales_agent_id")
        .leftJoin("core_users as account_manager", "account_manager.id", "oppo.account_manager_id")
        .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")  # Join Opportunity Status
        .leftJoin("core_currencies as curr", "curr.id", "oppo.currency_id")  # Join Currency
        .leftJoin("core_channels as ch", "ch.id", "oppo.channel_id")  # Join Channel
        .leftJoin("crmq_quotations as quotation", "quotation.opportunity_id", "oppo.id") # Join Quotation
        .leftJoin("core_status as quotation_status", "quotation_status.id", "quotation.status_id")  # Join Quotation Status
        .leftJoin("core_countries as country", "country.id", "oppo.country_id")  # Join Country
        .leftJoin("core_customers as customer", "customer.id", "oppo.customer_id")  # Join Account/Customer
        .leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")  # Join Customer Contact
        .leftJoin("core_products as product", "product.id", "oppo.product_id")  # Join Product
        .leftJoin("core_product_groups as product_group", "product_group.id", "oppo.product_group_id")  # Join Product Group
        .select(
            "oppo.*",
            "core_entities.created_at AS created_at",
            "core_entities.updated_at AS updated_at",
            "stage.name AS stage_name", "stage.type AS stage_type", "stage.color AS stage_color",
            "core_users.display_name AS sales_agent_name", "core_users.picture AS sales_agent_picture",
            "curr.name AS currency_name", "curr.symbol AS currency_symbol",
            "account_manager.display_name AS account_manager_name",  # ADDED
            "account_manager.picture AS account_manager_picture",  # ADDED
            "ch.name AS channel_name",
            "quotation.id AS quotation_id",
            "quotation_status.name AS quotation_status_name",
            "quotation_status.type AS quotation_status_type",
            "quotation_status.color AS quotation_status_color",
            "country.name AS country_name", "country.code AS country_code",
            "customer.id AS customer_id", "customer.name AS customer_name", "customer.logo AS customer_logo", "customer.type AS customer_type",
            "customer_contact.name AS customer_contact_name", "customer_contact.email AS customer_contact_email", 
            "customer_contact.primary_contact AS customer_contact_phone", "customer_contact.address AS customer_contact_address",
            "product.name AS product_name", "product.code AS product_code",
            "product_group.name AS product_group_name"
        )
        .where("oppo.id", id)
        .first()
    )

    if not data:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Fetch the latest health record separately
    latest_health = (
        QueryBuilderService("crm_opportunity_health")
        .select("id", "health", "date")
        .where("opportunity_id", id)
        .orderBy("id", "desc")
        .first()
    )

    # Create health object with latest health data
    health = {}
    if latest_health:
        health["id"] = latest_health.get("id")
        health["value"] = latest_health.get("health")
        health["date"] = latest_health.get("date")
    else:
        health["id"] = None
        health["value"] = None
        health["date"] = None
    
    data["health_id"] = health["id"]
    data["health_value"] = health["value"]
    data["health_date"] = health["date"]
    data["health"] = health

    # Fetch Entity Data Using Service
    entity_data = EntityService.get_entity_with_notes_and_docs(data["entity_id"])

    # Attach entity data to response
    data["entity"] = entity_data if entity_data else {}

    # Fetch risk_types (opportunity_types) for this opportunity
    risk_types = (
        QueryBuilderService("crm_oppor_opportunity_types as oot")
        .leftJoin("crm_opportunity_types as ot", "oot.opportunity_type_id", "ot.id")
        .where("oot.opportunity_id", id)
        .select("ot.id", "ot.title", "ot.description")
        .get()
    )
    
    # Attach risk_types to response
    data["risk_types"] = risk_types if risk_types else []

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def update_opportunity(request, id): 
    action = ActionService.getAction("Opportunity", "UPDATE")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)

    if not request.body or request.body == b'':
        return ResponseService.response("VALIDATION_ERROR", {"error": "Request body is empty"}, Error.VALIDATION_ERROR)

    data = json.loads(request.body)

    # Convert empty strings to None for nullable fields
    nullable_fields = [
        "channel_id", "health", "account_manager_id", "sales_agent_id",  
        "remarks", "current_health_id", "last_contacted_date", "country_id","sale_value", "lead_value","product_id",
        "product_group_id","issued_policy_id",
    ]
    for field in nullable_fields:
        if field in data and data[field] == "":
            data[field] = None

    rules = {
        "stage_id": "required|exists:crm_opportunity_statuses,id",
        "currency_id": "required|exists:core_currencies,id",
        "sales_agent_id": "exists:core_users,id",
        "channel_id": "exists:core_channels,id",
        "account_manager_id": "exists:core_users,id",
        "country_id": "exists:core_countries,id",
    }

    custom_messages = {
        "stage_id.exists": "Invalid stage ID.",
        "currency_id.exists": "Invalid currency ID.",
        "sales_agent_id.exists": "Invalid sales agent ID.",
        "channel_id.exists": "Invalid channel ID.",
        "account_manager_id.exists": "Invalid account manager ID.",
    }

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)

    existing_opportunity = QueryBuilderService("crm_opportunities").where("id", id).first()
    if not existing_opportunity:
        return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)

    # Validate opportunity_type_id if provided
    opportunity_type_ids = data.get("opportunity_type_id", [])
    existing_type_ids = set()  # Initialize to empty set
    
    if opportunity_type_ids:
        # Check if opportunity_type_id is a list
        if not isinstance(opportunity_type_ids, list):
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"opportunity_type_id": "opportunity_type_id must be an array"},
                Error.VALIDATION_ERROR
            )
        
        # Get the opportunity type (Personal or Corporate)
        opportunity_type = existing_opportunity.get("type") or data.get("type")
        
        # If opportunity type is Personal, validate that only one risk type is allowed
        if opportunity_type and opportunity_type.lower() == "personal":
            if len(opportunity_type_ids) > 1:
                return ResponseService.response(
                    "CONFLICT",
                    {"error": "Personal opportunities can only have one risk type assigned."},
                    Error.CONFLICT,
                    "VALIDATION_ERROR"
                )
        
        # Validate that all opportunity_type_ids exist
        existing_type_ids = set(OpportunityType.objects.filter(id__in=opportunity_type_ids).values_list("id", flat=True))
        invalid_type_ids = set(opportunity_type_ids) - existing_type_ids
        
        if invalid_type_ids:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "opportunity_type_id": [
                        {
                            "error_type": "exists",
                            "tokens": {
                                "_attribute": "opportunity_type_id"
                            }
                        }
                    ]
                },
                Error.VALIDATION_ERROR
            )

    # Handle product information based on product_type
    product_type = data.get("product_type")
    product_id = data.get("product_id")
    
    if product_type and product_id:
        if product_type == "product":
            data["product_id"] = product_id
            data["product_group_id"] = None
        elif product_type == "group":
            data["product_id"] = None
            data["product_group_id"] = product_id
    
    # Remove the temporary product_type field from data before update
    data.pop("product_type", None)

    # Fallback to existing title if empty
    if not data.get("title") or str(data["title"]).strip() == "":
        data["title"] = existing_opportunity["title"]

    try:
        with transaction.atomic():
            # Handle Opportunity Health creation
            new_health = data.get("health")
            if new_health is not None:
                current_health_id = existing_opportunity.get("current_health_id")
                should_update_health = True

                if current_health_id:
                    current_health_record = OpportunityHealth.objects.filter(id=current_health_id).first()
                    if current_health_record and current_health_record.health == new_health:
                        should_update_health = False

                if should_update_health:
                    new_health_record = OpportunityHealth.objects.create(
                        opportunity_id=id,
                        date=date.today(),
                        health=new_health
                    )
                    data["current_health_id"] = new_health_record.id
                else:
                    data["current_health_id"] = current_health_id

            # Filter allowed fields only
            editable_fields = [
                "title", "type", "stage_id", "channel_id", "health", "currency_id",
                "account_manager_id", "sales_agent_id", "last_contacted_date", "remarks", "current_health_id","country_id", "sale_value", "lead_value", "product_id", "product_group_id",
            ]
            sanitized_data = {k: v for k, v in data.items() if k in editable_fields}

            updated = QueryBuilderService("crm_opportunities").where("id", id).update(sanitized_data)
            if not updated:
                raise Exception("Opportunity update failed")
            
            # Handle opportunity_type_id update if provided
            if opportunity_type_ids:
                # Delete existing opportunity types for this opportunity
                QueryBuilderService("crm_oppor_opportunity_types")\
                    .where("opportunity_id", id)\
                    .delete()
                
                # Insert new opportunity types
                if existing_type_ids:
                    OpportunityOpporType.objects.bulk_create(
                        [OpportunityOpporType(opportunity_id=id, opportunity_type_id=op_type_id) for op_type_id in existing_type_ids]
                    )
            
    except DataError as e:
        # MySQL out-of-range check
        if "Out of range value for column" in str(e):
            return ResponseService.response(
                "VALIDATION_ERROR",
                "One or more values exceed the allowed range (e.g., sale_value or lead_value)",
                Error.VALIDATION_ERROR
            )
        return ResponseService.response("VALIDATION_ERROR", {"error": str(e)}, Error.VALIDATION_ERROR)


    except Exception as e:
        return ResponseService.response("VALIDATION_ERROR", {"error": str(e)}, Error.VALIDATION_ERROR)

    # Log Sales Agent change (outside atomic)
    old_sales_agent_id = existing_opportunity.get("sales_agent_id")
    new_sales_agent_id = data.get("sales_agent_id")

    if new_sales_agent_id and new_sales_agent_id != old_sales_agent_id:
        # Import the history model
        from envoy_bu_crm_api.sales.models.sales_agent_history import SalesAgentHistory
        
        # Create history record
        history_record = SalesAgentHistory.objects.create(
            from_agent_id=old_sales_agent_id,
            to_agent_id=new_sales_agent_id,
            changed_by=request.user if request.user.is_authenticated else None,
            type=SalesAgentHistory.LEAD,
            lead_id=id,
            updated_at=timezone.now()
        )
        
        # Also maintain the existing activity logging
        if old_sales_agent_id:
            old_sales_agent = User.objects.get(id=old_sales_agent_id)
            new_sales_agent = User.objects.get(id=new_sales_agent_id)
            activity_message = (
                f"Sales Agent reassigned from {old_sales_agent.display_name} "
                f"to {new_sales_agent.display_name} for this opportunity"
            )
        else:
            new_sales_agent = User.objects.get(id=new_sales_agent_id)
            activity_message = (
                f"Sales Agent {new_sales_agent.display_name} "
                f"is assigned to this opportunity"
            )

        ActivityService.store_activity(
            request=request,
            entity_id=existing_opportunity["entity_id"],
            activity=activity_message
        )

    return ResponseService.response("SUCCESS", updated, Message.DATA_UPDATED)


@api_view(["GET"])
def get_sales_agent_history(request, id):
    """Get sales agent change history for an opportunity"""
    try:
        # Get pagination parameters
        filter_json = request.GET.get('filters', '{}')
        # Handle "undefined" string case
        if filter_json == 'undefined' or filter_json == 'null':
            filter_json = '{}'
        
        search_string = request.GET.get('search', '')
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "crm_sales_agent_histories.updated_at")
        sort_dir = request.GET.get("sort_dir", "desc")
        
        # Define columns to select
        all_columns = [
            "crm_sales_agent_histories.id",
            "crm_sales_agent_histories.from_agent_id",
            "crm_sales_agent_histories.to_agent_id", 
            "crm_sales_agent_histories.changed_by_id",
            "crm_sales_agent_histories.updated_at",
            "crm_sales_agent_histories.type",
            "crm_sales_agent_histories.lead_id",
            # From agent details
            "from_agent.id AS from_agent_id",
            "from_agent.display_name AS from_agent_name",
            # To agent details  
            "to_agent.id AS to_agent_id",
            "to_agent.display_name AS to_agent_name",
            # Changed by details
            "changed_by.id AS changed_by_id",
            "changed_by.display_name AS changed_by_name",
            # Lead details
            "crm_opportunities.title AS lead_title",
            "crm_opportunities.stage_id AS lead_stage_id",
            "crm_opportunity_statuses.name AS lead_stage_name",
            "crm_opportunity_statuses.type AS lead_stage_type",
            "crm_opportunity_statuses.color AS lead_stage_color"
        ]
        
        # Define allowed filters and search columns
        allowed_filters = ['from_agent_id', 'to_agent_id', 'changed_by_id', 'type', 'lead_title', 'lead_stage_name']
        search_columns = ['from_agent.display_name', 'to_agent.display_name', 'changed_by.display_name', 'crm_opportunities.title', 'crm_opportunity_statuses.name']
        allowed_sorting_columns = ['crm_sales_agent_histories.updated_at', 'crm_sales_agent_histories.id', 'crm_opportunities.title']
        
        # Build query with joins
        query = (
            QueryBuilderService("crm_sales_agent_histories")
            .leftJoin("core_users AS from_agent", "from_agent.id", "crm_sales_agent_histories.from_agent_id")
            .leftJoin("core_users AS to_agent", "to_agent.id", "crm_sales_agent_histories.to_agent_id")
            .leftJoin("core_users AS changed_by", "changed_by.id", "crm_sales_agent_histories.changed_by_id")
            .leftJoin("crm_opportunities", "crm_opportunities.id", "crm_sales_agent_histories.lead_id")
            .leftJoin("crm_opportunity_statuses", "crm_opportunity_statuses.id", "crm_opportunities.stage_id")
            .select(*all_columns)
            .where("crm_sales_agent_histories.lead_id", id)
        )
        
        # Apply conditions if any filters or search are provided
        if filter_json != '{}' or search_string:
            query = query.apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        
        # Apply ordering and pagination
        data = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
        
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_opportunity(request, id):
    try:
        # Pre-check: block delete if referenced by quotations or policies
        blocking_sources = []
        try:
            quotation_ref = QueryBuilderService("crmq_quotations").where("opportunity_id", id).first()
            if quotation_ref:
                blocking_sources.append("quotations")
        except Exception:
            pass
        try:
            policy_ref = QueryBuilderService("crmp_policy_base").where("lead_id", id).first()
            if policy_ref:
                blocking_sources.append("policies")
        except Exception:
            pass

        if blocking_sources:
            return ResponseService.response(
                "VALIDATION_ERROR",
                blocking_sources,
                Message.DEFAULT_CONFLICT_MSG
            )

        with transaction.atomic():
            # Retrieve the opportunity instance
            opportunity = Opportunity.objects.get(id=id)

            # Delete related OpportunityFormSubmission instances
            OpportunityFormSubmission.objects.filter(opportunity=opportunity).delete()

            # Now, delete the opportunity
            opportunity.delete()

        return ResponseService.response("SUCCESS", None, Message.DATA_DELETED)

    except Opportunity.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None,Error.NOT_FOUND)

    except IntegrityError as e:
        # Handle FK constraint errors with a friendly message
        message = str(e)
        if "foreign key constraint fails" in message.lower() or "FOREIGN KEY" in message:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "error": "Cannot delete this opportunity because related records exist (e.g., policies, forms, or activities). Remove or unlink related records first."
                },
                "foreign_key_constraint"
            )
        return ResponseService.response("VALIDATION_ERROR", {"error": message}, "delete_failed")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)
@csrf_exempt
@api_view(['PATCH'])
def update_opportunity_status(request, id):
    """ Update Opportunity Status with Sorting"""


    try:
        data = json.loads(request.body.decode('utf-8'))  #  Decode request body safely
    except json.JSONDecodeError:
        return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON format"}, Error.VALIDATION_ERROR)

    #  Validation rules (NO validation for prev_opportunity_id & next_opportunity_id)
    rules = {
        'source_status_id': 'required|exists:crm_opportunity_statuses,id',
        'destination_status_id': 'required|exists:crm_opportunity_statuses,id',
        'update_opportunity_id': 'required|exists:crm_opportunities,id',
    }

    errors = ValidatorService.validate(data, rules, {})
    if errors:
        return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)

    action = ActionService.getAction("Opportunity", "UPDATE")
    has_authority = AuthService.hasAuthority(request , action)

    if not has_authority:
        return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)

    #  **Extra Database Validation for Foreign Keys**
    try:
        foreign_keys = {
            "source_status_id": OpportunityStatus,
            "destination_status_id": OpportunityStatus,
            "update_opportunity_id": Opportunity,
        }
        for field, model in foreign_keys.items():
            if field in data and not model.objects.filter(id=data[field]).exists():
                return ResponseService.response('VALIDATION_ERROR', {field: "Invalid ID"}, Error.VALIDATION_ERROR)

    except Exception as e:
        return ResponseService.response('VALIDATION_ERROR', str(e), Error.VALIDATION_ERROR)

    #  Update opportunity stage_id
    updated = QueryBuilderService("crm_opportunities")\
        .where("id", id)\
        .update({"stage_id": data["destination_status_id"]})

    if not updated:
        return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)

    #  Fetch related opportunities before sorting (handle None values)
    prev_opportunity = None
    next_opportunity = None

    if data.get("prev_opportunity_id"):
        prev_opportunity = QueryBuilderService("crm_opportunities").where("id", data["prev_opportunity_id"]).first()

    if data.get("next_opportunity_id"):
        next_opportunity = QueryBuilderService("crm_opportunities").where("id", data["next_opportunity_id"]).first()

    update_opportunity = QueryBuilderService("crm_opportunities").where("id", data["update_opportunity_id"]).first()

    #  Convert sort_index to float before calculation (handle None values)
    prev_sort_index = float(prev_opportunity["sort_index"]) if prev_opportunity and prev_opportunity["sort_index"] is not None else 0.0
    next_sort_index = float(next_opportunity["sort_index"]) if next_opportunity and next_opportunity["sort_index"] is not None else prev_sort_index + 1.0

    #  Calculate new sort index safely
    if update_opportunity:
        if prev_opportunity and next_opportunity:
            new_sort_index = (prev_sort_index + next_sort_index) / 2
        elif next_opportunity:
            new_sort_index = next_sort_index / 2
        elif prev_opportunity:
            new_sort_index = prev_sort_index + 1
        else:
            new_sort_index = 1  

        QueryBuilderService("crm_opportunities")\
            .where("id", update_opportunity["id"])\
            .update({"sort_index": new_sort_index})
        

        opportunity = QueryBuilderService("crm_opportunities")\
                        .where("id", id)\
                        .first()
        
        TaskService.saveOppourinityTask(id, data["destination_status_id"], opportunity["sales_agent_id"])


        # Extend JOINs to include contact and customer data
    updated_opportunity = (
        QueryBuilderService("crm_opportunities as oppo")
        .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")
        .leftJoin("core_users", "core_users.id", "oppo.sales_agent_id")
        .leftJoin("core_contacts as contact", "contact.id", "oppo.contact_id")
        .leftJoin("core_customers as customer", "customer.id", "oppo.customer_id")
        .leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")
        .select(
            "oppo.*",
            "stage.name AS stage_name",
            "stage.type AS stage_type",
            "stage.color AS stage_color",
            "core_users.display_name AS sales_agent_name",
            "core_users.email AS sales_agent_email",
            "core_users.contact_no AS sales_agent_contact",
            "contact.name AS contact_name",
            "contact.primary_contact AS primary_contact",
            "customer.name AS customer_name",
            "customer.logo AS customer_logo",
            "customer_contact.email AS customer_primary_contact_email"
        )
        .where("oppo.id", update_opportunity["id"])
        .first()
    )
    
    # Fetch the latest health record separately
    if updated_opportunity:
        latest_health = (
            QueryBuilderService("crm_opportunity_health")
            .select("id", "health", "date")
            .where("opportunity_id", updated_opportunity["id"])
            .orderBy("id", "desc")
            .first()
        )
        
        if latest_health:
            updated_opportunity["health_id"] = latest_health.get("id")
            updated_opportunity["health_value"] = latest_health.get("health")
            updated_opportunity["health_date"] = latest_health.get("date")
            updated_opportunity["current_health"] = latest_health.get("health")
            updated_opportunity["health"] = {
                "id": latest_health.get("id"),
                "value": latest_health.get("health"),
                "date": latest_health.get("date")
            }
        else:
            updated_opportunity["health_id"] = None
            updated_opportunity["health_value"] = None
            updated_opportunity["health_date"] = None
            updated_opportunity["current_health"] = None
            updated_opportunity["health"] = None

    # Add nested `contact` and `customer` objects
    if updated_opportunity:
        contact_id = updated_opportunity.get("contact_id")
        updated_opportunity["contact"] = {
            "name": updated_opportunity.pop("contact_name", None),
            "primary_contact": updated_opportunity.pop("primary_contact", None)
        } if contact_id else None

        customer_id = updated_opportunity.get("customer_id")
        updated_opportunity["customer"] = {
            "name": updated_opportunity.pop("customer_name", None),
            "logo": updated_opportunity.pop("customer_logo", None),
            "email": updated_opportunity.pop("customer_primary_contact_email", None)
        } if customer_id else None

        # Add `next_task` object
        opportunity_id = updated_opportunity.get("id")
        task_ids = OpportunityTask.objects.filter(opportunity_id=opportunity_id).values_list('task_id', flat=True)
        tasks = (
            Task.objects
            .filter(id__in=task_ids)
            .select_related('task_status', 'assigned_to')
            .order_by('sort_index')
        )

        selected_task = next((task for task in tasks if task.task_status and task.task_status.type.lower() == "task_todo"), None)

        updated_opportunity["next_task"] = {
            "task": selected_task.task,
            "start_date": selected_task.start_date,
            "assigned_user_name": selected_task.assigned_to.display_name if selected_task.assigned_to else None,
            "assigned_user_picture": selected_task.assigned_to.picture if selected_task.assigned_to else None
        } if selected_task else None


    # Fetch status names
    source_status = OpportunityStatus.objects.get(id=data["source_status_id"]).name
    destination_status = OpportunityStatus.objects.get(id=data["destination_status_id"]).name

     # Log the activity using ActivityService
    ActivityService.store_activity(
        request=request,
        entity_id=updated_opportunity["entity_id"],
        activity=f"Opportunity Status updated from {source_status} to {destination_status}"
    )

    return ResponseService.response('SUCCESS', updated_opportunity, Message.DATA_UPDATED)


@csrf_exempt
@api_view(['GET', 'POST', 'DELETE'])
def opportunity_types(request, id):  
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Type", "VIEW")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)
        return get_opportunity_types(request, id)

    elif request.method == 'POST':
        action = ActionService.getAction("Opportunity_Type", "CREATE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)
        return store_opportunity_type(request, id)

    # elif request.method == 'DELETE':
    #     action = ActionService.getAction("Opportunity_Type", "DELETE")
    #     if not AuthService.hasAuthority(request , action):
    #         return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
    #     return delete_opportunity_type(request, id)

def get_opportunity_types(request, id):
    data = (
        QueryBuilderService("crm_oppor_opportunity_types as oot")
        .leftJoin("crm_opportunity_types as ot", "oot.opportunity_type_id", "ot.id")
        .where("oot.opportunity_id", id)
        .select("ot.*")  
        .get()
    )
    
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) if data else ResponseService.response("SUCCESS", [], Message.DATA_FETCHED)


def store_opportunity_type(request, id):
    if not request.body or request.body == b'':
        return ResponseService.response("VALIDATION_ERROR", {"error": "Request body is empty"}, Error.VALIDATION_ERROR)
    
    data = json.loads(request.body)

    
    rules = {
        'type_id': 'required|exists:crm_opportunity_types,id'  
    }
    errors = ValidatorService.validate(data, rules, {})

    if errors:
        return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)

    
    existing_entry = (
        QueryBuilderService("crm_oppor_opportunity_types")
        .where("opportunity_id", id)
        .where("opportunity_type_id", data["type_id"])
        .first()
    )
    if existing_entry:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {
                "type_id": [
                    {
                        "error_type": "exist",
                        "tokens": {
                            "_attribute": "product_type_id"
                        }
                    }
                ]
            },
            Error.VALIDATION_ERROR
        )

    # Get the opportunity's type (Personal or Corporate)
    opportunity = QueryBuilderService("crm_opportunities")\
        .where("id", id)\
        .select("type")\
        .first()
    
    if not opportunity:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"error": "Opportunity not found"},
            Error.NOT_FOUND,
            "VALIDATION_ERROR"
        )
    
    opportunity_type = opportunity.get("type")
    
    # If opportunity type is Personal, check if there's already a risk type assigned
    if opportunity_type and opportunity_type.lower() == "personal":
        existing_risk_types = QueryBuilderService("crm_oppor_opportunity_types")\
            .where("opportunity_id", id)\
            .get()
        
        if existing_risk_types and len(existing_risk_types) >= 1:
            return ResponseService.response(
                "CONFLICT",
                {"error": "Personal opportunities can only have one risk type assigned."},
                Error.CONFLICT,
                "VALIDATION_ERROR"
            )

    
    new_data = QueryBuilderService("crm_oppor_opportunity_types").insert({
        "opportunity_id": id,
        "opportunity_type_id": data["type_id"]
    })
    
    return ResponseService.response("SUCCESS", new_data, Message.DATA_CREATED)

@csrf_exempt
@api_view(['DELETE'])
def delete_opportunity_type(request, id, type_id):
    """ Delete a specific opportunity type from an opportunity"""

    # Check if the record exists
    # exists = (
    #     QueryBuilderService("crm_oppor_opportunity_types")
    #     .where("opportunity_id", id)
    #     .where("opportunity_type_id", type_id)
    #     .exists()
    # )

    # if not exists:
    #     return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Delete the record
    QueryBuilderService("crm_oppor_opportunity_types")\
        .where("opportunity_id", id)\
        .where("opportunity_type_id", type_id)\
        .delete()

    return ResponseService.response("SUCCESS", None, Message.DATA_DELETED)


@csrf_exempt
@api_view(['GET'])
def get_opportunity_form_config(request, type_id):
    """Fetch opportunity form configurations."""
    action = ActionService.getAction("Opportunity_Form_Config", "VIEW")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)

    data_gethering_type = request.GET.get('data_gethering_type', None)
    query = QueryBuilderService("crm_opportunity_form_config") \
        .leftJoin("core_templates", "core_templates.id", "crm_opportunity_form_config.form_id") \
        .select("crm_opportunity_form_config.*", "crm_opportunity_form_config.id as config_id", ) \
        .where("crm_opportunity_form_config.opportunity_type_id", type_id)

    if data_gethering_type:
        query = query.where("data_gethering_type", data_gethering_type)

    data = query.first()

    # for forms in data:
    #     forms["attributes"] = QueryBuilderService("core_form_attributes").where('form_id', forms['id']).get()

    return ResponseService.response("SUCCESS", data or {}, Message.DATA_FETCHED)


# @csrf_exempt
# @api_view(['GET', 'POST'])
# def opportunity_info(request, id, type_id):  
#     if request.method == 'GET':
#         action = ActionService.getAction("Opportunity_Info", "VIEW")
#         if not AuthService.hasAuthority(request , action):
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
#         return get_opportunity_info(request, id, type_id)

#     elif request.method == 'POST':
#         action = ActionService.getAction("Opportunity_Info", "CREATE")
#         if not AuthService.hasAuthority(request , action):
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
#         return store_opportunity_info(request, id, type_id)


# def get_opportunity_info(request, id, type_id):
#     data = QueryBuilderService("crm_oppor_form_submissions")\
#             .where("opportunity_id", id)\
#             .where("oppor_form_config_id", type_id)\
#             .get()

#     return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) if data else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


# def store_opportunity_info(request, id, type_id):
#     if not request.body or request.body == b'':
#         return ResponseService.response("VALIDATION_ERROR", {"error": "Request body is empty"}, Error.VALIDATION_ERROR)
    
#     data = json.loads(request.body)
    
   
#     rules = {'data': 'required|array'}
#     errors = ValidatorService.validate(data, rules, {})

#     if errors:
#         return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)

    
#     form_config = QueryBuilderService("crm_opportunity_form_config")\
#                     .where("opportunity_type_id", type_id)\
#                     .where("data_gethering_type", "onboarding")\
#                     .first()
    
#     if not form_config:
#         return ResponseService.response("CONFLICT", {"error": "No valid form config found for this type"}, Error.CONFLICT)

    
#     for entry in data['data']:
#         entry['opportunity_id'] = id
#         entry['oppor_form_config_id'] = form_config["id"]
#         QueryBuilderService("crm_oppor_form_submissions").insert(entry)

#     return ResponseService.response("SUCCESS", data, "default_create_success_msg")




@csrf_exempt
@api_view(['GET'])
def opportunity_other_info(request):
    ids = request.GET.get('ids', None)

    data = []
    if ids:
        data = QueryBuilderService("crm_opportunities as oppo")\
                .leftJoin('crm_opportunity_statuses as stage','stage.id','oppo.stage_id') \
                .select('oppo.id','stage.name','stage.type','stage.color') \
                .whereIn("oppo.id", ids.split(',')) \
                .get()

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# @csrf_exempt
# @api_view(['GET'])
# def get_opportunity_type_form_config(request, type_id):
#     action = ActionService.getAction("Opportunity_Form_Config", "VIEW")
#     if not AuthService.hasAuthority(request , action):
#         return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)

#     data_gethering_type = request.GET.get('data_gethering_type', None)

#     query = QueryBuilderService("crm_opportunity_form_config") \
#         .leftJoin("form", "form.id", "crm_opportunity_form_config.form_id") \
#         .select("crm_opportunity_form_config.id as config_id", "form.*") \
#         .where("crm_opportunity_form_config.opportunity_type_id", type_id)

#     if data_gethering_type:
#         query = query.where("data_gethering_type", data_gethering_type)

#     data = query.get()

#     if not data:
#         return ResponseService.response("CONFLICT", {"error": "No form config found"}, "CONFLICT")

#     # Fetch form attributes
#     for form in data:
#         form["attributes"] = QueryBuilderService("formattribute").where("form_id", form["id"]).get()

#     return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# @csrf_exempt
# @api_view(['GET', 'POST', 'PUT', 'DELETE'])
# def opportunity_form_config_info(request, id, config_id, info_id=None):
#     """Handle opportunity form information based on HTTP method."""

#     if request.method == 'GET':
#         action = ActionService.getAction("Opportunity_Info", "VIEW")
#         if not AuthService.hasAuthority(request , action):
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
#         return get_opportunity_info(request, id, config_id, info_id)

#     elif request.method == 'POST' and not info_id:
#         action = ActionService.getAction("Opportunity_Info", "CREATE")
#         if not AuthService.hasAuthority(request , action):
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
#         return store_opportunity_info(request, id, config_id)

#     elif request.method == 'PUT' and info_id:
#         action = ActionService.getAction("Opportunity_Info", "UPDATE")
#         if not AuthService.hasAuthority(request , action):
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
#         return update_opportunity_info(request, id, config_id, info_id)

#     elif request.method == 'DELETE' and info_id:
#         action = ActionService.getAction("Opportunity_Info", "DELETE")
#         if not AuthService.hasAuthority(request , action):
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
#         return delete_opportunity_info(request, id, config_id, info_id)


# def get_opportunity_info(request, id, config_id, info_id=None):
#     """Fetch opportunity form info with pagination."""
    
#     filter_json = request.GET.get("filter", {})
#     search_string = request.GET.get("search", "")
#     page = int(request.GET.get("page", 1))
#     limit = int(request.GET.get("limit", 10))
#     sort_by = request.GET.get("sort_by", "id")
#     sort_dir = request.GET.get("sort_dir", "desc")
    
#     query = QueryBuilderService("crm_oppor_form_submissions") \
#         .where("opportunity_id", id) \
#         .where("oppor_form_config_id", config_id) \
#         .apply_conditions(filter_json, [], search_string, [])
    
#     if info_id:
#         query = query.where("id", info_id)
#         data = query.first()
#     else:
#         data = query.paginate(page, limit, ["id"], sort_by, sort_dir)

#     return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) if data else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


# def store_opportunity_info(request, id, config_id):
#     """Store new opportunity form info with customer assignment."""

#     if not request.body or request.body == b'':
#         return ResponseService.response("VALIDATION_ERROR", {"error": "Request body is empty"}, Error.VALIDATION_ERROR)

#     data = json.loads(request.body)

#     rules = {'data': 'required|array'}
#     errors = ValidatorService.validate(data, rules, {})

#     if errors:
#         return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)

#     # Fetch customer_id once if needed
#     opportunity = QueryBuilderService("crm_opportunities").select("id", "customer_id").where("id", id).first()
#     customer_id_from_opportunity = opportunity["customer_id"] if opportunity else None

#     for entry in data['data']:
#         entry['opportunity_id'] = id
#         entry['oppor_form_config_id'] = config_id

#         # If customer_id not given directly in entry, fallback to opportunity's customer_id
#         if 'customer_id' not in entry or not entry['customer_id']:
#             entry['customer_id'] = customer_id_from_opportunity

#         QueryBuilderService("crm_oppor_form_submissions").insert(entry)

#     return ResponseService.response("SUCCESS", data, "default_create_success_msg")



# def update_opportunity_info(request, id, config_id, info_id):
#     """Update existing opportunity form info."""
#     if not request.body or request.body == b'':
#         return ResponseService.response("VALIDATION_ERROR", {"error": "Request body is empty"}, Error.VALIDATION_ERROR)

#     data = json.loads(request.body)

#     existing_data = QueryBuilderService("crm_oppor_form_submissions") \
#         .where("opportunity_id", id) \
#         .where("oppor_form_config_id", config_id) \
#         .where("id", info_id) \
#         .first()

#     if not existing_data:
#         return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

#     QueryBuilderService("crm_oppor_form_submissions") \
#         .where("id", info_id) \
#         .update(data)

#     return ResponseService.response("SUCCESS", data, "default_update_success_msg")


# def delete_opportunity_info(request, id, config_id, info_id):
#     """Delete opportunity form info."""
#     existing_data = QueryBuilderService("crm_oppor_form_submissions") \
#         .where("opportunity_id", id) \
#         .where("oppor_form_config_id", config_id) \
#         .where("id", info_id) \
#         .first()

#     if not existing_data:
#         return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

#     QueryBuilderService("crm_oppor_form_submissions") \
#         .where("id", info_id) \
#         .delete()

#     return ResponseService.response("SUCCESS", None, "default_delete_success_msg")


# @csrf_exempt
# @api_view(["PUT"])
# def update_opportunity(request, id):
#     """Update opportunity details."""
#     if not request.body or request.body == b'':
#         return ResponseService.response("VALIDATION_ERROR", {"error": "Request body is empty"}, Error.VALIDATION_ERROR)

#     data = json.loads(request.body)

#     existing_opportunity = QueryBuilderService("crm_opportunities").where("id", id).first()

#     if not existing_opportunity:
#         return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

#     QueryBuilderService("crm_opportunities").where("id", id).update(data)

#     return ResponseService.response("SUCCESS", data, "Opportunity updated successfully.")



@csrf_exempt
@api_view(["GET", "POST"])
def interactions(request, id):
    """Handles listing and creating interactions for an opportunity."""

    if request.method == "GET":
        return get_interactions(request, id)
    elif request.method == "POST":
        return create_interaction(request, id)


def get_interactions(request, id):
    """Fetch all interactions related to an opportunity with pagination."""

    all_columns = [
        "core_intractions.*",
        "core_channels.name AS channel_name",
        "core_contacts.name AS contact_name",
        "core_customers.name AS customer_name",
        "core_users.first_name AS contact_by_first_name",
        "core_users.last_name AS contact_by_last_name",
        "core_users.display_name AS contact_by_display_name",
        
        "core_tasks.task AS task_title",
        "crm_opportunity_statuses.name AS opportunity_status_name"
    ]

    # Pagination & Filtering Setup
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "desc")
    # Normalize empty values to defaults
    sort_by = "core_intractions.id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    allowed_sorting_columns = ["core_intractions.id", "core_intractions.notes", "core_intractions.created_at"]
    ids = request.GET.get("ids", None)
    
    allowed_filters = []
    search_columns = ["core_intractions.notes"]

    data = (
        QueryBuilderService("core_intractions")
        .leftJoin("core_channels", "core_channels.id", "core_intractions.channel_id")
        .leftJoin("core_contacts", "core_contacts.id", "core_intractions.contact_id")
        .leftJoin("core_customers", "core_customers.id", "core_intractions.customer_id")
        .leftJoin("core_users", "core_users.id", "core_intractions.contact_by_id")
        .leftJoin("core_tasks", "core_tasks.id", "core_intractions.task_id")
        .leftJoin("crm_opportunity_statuses", "crm_opportunity_statuses.id", "core_intractions.opportunity_status_id")
        .select(*all_columns)
        .where("core_intractions.opportunity_id", id)
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
    )

    if ids:
        data = data.whereIn("core_intractions.id", ids.split(",")) \
                .orderBy(sort_by, sort_dir) \
                .get()
    else:
        data = data.orderBy(sort_by, sort_dir) \
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def create_interaction(request, id):
    """Create a new interaction for an opportunity."""

    data = json.loads(request.body) if request.body else {}
    data = RequestPreprocessor.clean_nullable_fields(data, [
        "contact_id", "customer_id", "task_id", "opportunity_status_id"
    ])

    rules = {
        "channel_id": "required|exists:core_channels,id",
        "opportunity_status_id": "exists:crm_opportunity_statuses,id",
        "contact_id": "exists:core_contacts,id",
        "customer_id": "exists:core_customers,id",
        "task_id": "exists:core_tasks,id",
        "notes": "max:500",
        "date": "required|date_format:%Y-%m-%d"
    }

    errors = ValidatorService.validate(data, rules, {})
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    if "contact_by_id" not in data or not data["contact_by_id"]:
        data["contact_by_id"] = request.user.id if request.user.is_authenticated else 1  # Default user ID

    # If customer_id is missing, retrieve it from the opportunity
    if not data.get("customer_id"):
        opportunity = QueryBuilderService("crm_opportunities").select("customer_id").where("id", id).first()
        if opportunity and opportunity.get("customer_id"):
            data["customer_id"] = opportunity["customer_id"]

    entity = EntityService.store("Interaction", request)
    if not entity or "id" not in entity:
        return ResponseService.response("ERROR", None, "Failed to create entity")

    new_data = QueryBuilderService("core_intractions").insert({
        **data,
        "opportunity_id": id,
        "entity_id": entity["id"]
    })

    return ResponseService.response("SUCCESS", new_data, Message.DATA_CREATED)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def single_interaction(request, id, int_id):
    """Handles single interaction actions: GET, UPDATE, DELETE."""

    if request.method == "GET":
        return get_single_interaction(request, id, int_id)
    elif request.method == "PUT":
        return update_interaction(request, id, int_id)
    elif request.method == "DELETE":
        return delete_interaction(request, id, int_id)


def get_single_interaction(request, id, int_id):
    """Fetch a single interaction with correct table names."""
    data = (
        QueryBuilderService("core_intractions")
        .leftJoin("core_channels", "core_channels.id", "core_intractions.channel_id")
        .leftJoin("core_contacts", "core_contacts.id", "core_intractions.contact_id")
        .leftJoin("core_customers", "core_customers.id", "core_intractions.customer_id")
        .leftJoin("core_users", "core_users.id", "core_intractions.contact_by_id")
        .leftJoin("core_tasks", "core_tasks.id", "core_intractions.task_id")
        .leftJoin("crm_opportunity_statuses", "crm_opportunity_statuses.id", "core_intractions.opportunity_status_id")
        .select(
            "core_intractions.*",
            "core_channels.name AS channel_name",
            "core_contacts.name AS contact_name",
            "core_customers.name AS customer_name",
            "core_users.first_name AS contact_by_first_name",
            "core_users.last_name AS contact_by_last_name",
            "core_users.display_name AS contact_by_display_name",
            "core_tasks.task AS task_title",
            "crm_opportunity_statuses.name AS opportunity_status_name"
        )
        .where("core_intractions.opportunity_id", id)
        .where("core_intractions.id", int_id)
        .first()
    )
    if not data:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Fetch Entity Data Using Service
    entity_data = EntityService.get_entity_with_notes_and_docs(data["entity_id"])

    # Attach entity data to response
    data["entity"] = entity_data if entity_data else {}

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) if data else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def update_interaction(request, id, int_id):
    """Update an existing interaction."""
    data = json.loads(request.body) if request.body else {}

    
    rules = {
        "channel_id": "exists:core_channels,id",
        "contact_by_id": "required|exists:core_users,id",
        "opportunity_status_id": "exists:crm_opportunity_statuses,id",
        "contact_id": "exists:core_contacts,id",
        "customer_id": "exists:core_customers,id",
        "task_id": "exists:core_tasks,id",
        "notes": "max:500"
    }

    errors = ValidatorService.validate(data, rules, {})
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    updated_data = QueryBuilderService("core_intractions").where("id", int_id).update(data)

    return ResponseService.response("SUCCESS", updated_data, Message.DATA_UPDATED) if updated_data else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_interaction(request, id, int_id):
    """Delete an interaction."""
    deleted_data = QueryBuilderService("core_intractions").where("id", int_id).delete()

    return ResponseService.response("SUCCESS", deleted_data, Message.DATA_DELETED) if deleted_data else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)




@csrf_exempt
@api_view(['PATCH'])
def update_opportunity_customer(request, id):
    """Update the Customer ID of an Opportunity"""

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON format"}, Error.VALIDATION_ERROR)

    # Validation rules
    rules = {
        "customer_id": "required|exists:core_customers,id"
    }

    errors = ValidatorService.validate(data, rules, {})
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Authorization check
    action = ActionService.getAction("Opportunity", "UPDATE")
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    # Check customer exists (safety)
    customer_id = data["customer_id"]
    customer = Customer.objects.filter(id=customer_id).first()
    if not customer:
        return ResponseService.response("NOT_FOUND", {"customer_id": "Invalid customer"}, Error.NOT_FOUND)

    # Get the current opportunity to check its type
    opportunity = QueryBuilderService("crm_opportunities").where("id", id).first()
    if not opportunity:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Check if customer type and opportunity type match
    customer_type = customer.type
    opportunity_type = opportunity.get("type")
    
    if customer_type != opportunity_type:
        return ResponseService.response("CONFLICT", {
            "error": f"Customer type ({customer_type}) does not match opportunity type ({opportunity_type})"
        },Error.CONFLICT,"CONFLICT")

    # Update the opportunity
    updated = QueryBuilderService("crm_opportunities")\
        .where("id", id)\
        .update({"customer_id": customer_id})

    if not updated:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Update customer_id in crm_risks for all risks that have submissions linked to this opportunity
    try:
        # Get all risk IDs that have submissions linked to this opportunity
        risk_submissions = RiskSubmission.objects.filter(lead_id=id).values_list('risk_id', flat=True)
        
        if risk_submissions:
            # Update customer_id for all related risks
            Risk.objects.filter(id__in=risk_submissions).update(customer_id=customer_id)
            
    except Exception as e:
        # Log the error but don't fail the main operation
        print(f"Warning: Failed to update customer_id for related risks: {str(e)}")

    # Fetch updated opportunity
    opportunity = QueryBuilderService("crm_opportunities").where("id", id).first()

    # Get extra info like in previous method
    updated_opportunity = (
        QueryBuilderService("crm_opportunities as oppo")
        .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")
        .leftJoin("crm_opportunity_health as health", "health.id", "oppo.current_health_id")
        .leftJoin("core_users", "core_users.id", "oppo.sales_agent_id")
        .leftJoin("core_contacts as contact", "contact.id", "oppo.contact_id")
        .leftJoin("core_customers as customer", "customer.id", "oppo.customer_id")
        .leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")
        .select(
            "oppo.*",
            "stage.name AS stage_name",
            "stage.type AS stage_type",
            "stage.color AS stage_color",
            "core_users.display_name AS sales_agent_name",
            "core_users.email AS sales_agent_email",
            "core_users.contact_no AS sales_agent_contact",
            "health.health AS current_health",
            "contact.name AS contact_name",
            "contact.primary_contact AS primary_contact",
            "customer.name AS customer_name",
            "customer.logo AS customer_logo",
            "customer_contact.email AS customer_primary_contact_email"
        )
        .where("oppo.id", id)
        .first()
    )

    # Add contact and customer nesting
    if updated_opportunity:
        contact_id = updated_opportunity.get("contact_id")
        updated_opportunity["contact"] = {
            "name": updated_opportunity.pop("contact_name", None),
            "primary_contact": updated_opportunity.pop("primary_contact", None)
        } if contact_id else None

        customer_id = updated_opportunity.get("customer_id")
        updated_opportunity["customer"] = {
            "name": updated_opportunity.pop("customer_name", None),
            "logo": updated_opportunity.pop("customer_logo", None),
            "email": updated_opportunity.pop("customer_primary_contact_email", None)
        } if customer_id else None

        # Fetch next task
        task_ids = OpportunityTask.objects.filter(opportunity_id=id).values_list('task_id', flat=True)
        tasks = (
            Task.objects
            .filter(id__in=task_ids)
            .select_related('task_status', 'assigned_to')
            .order_by('sort_index')
        )

        selected_task = next((task for task in tasks if task.task_status and task.task_status.type.lower() == "task_todo"), None)

        updated_opportunity["next_task"] = {
            "task": selected_task.task,
            "start_date": selected_task.start_date,
            "assigned_user_name": selected_task.assigned_to.display_name if selected_task.assigned_to else None,
            "assigned_user_picture": selected_task.assigned_to.picture if selected_task.assigned_to else None
        } if selected_task else None

    # Log activity
    ActivityService.store_activity(
        request=request,
        entity_id=updated_opportunity["entity_id"],
        activity=f"Customer updated to {updated_opportunity['customer']['name'] if updated_opportunity['customer'] else 'N/A'}"
    )

    return ResponseService.response("SUCCESS", updated_opportunity, Message.DATA_UPDATED)



@api_view(['GET'])
def get_opportunity_policies(request, opportunity_id):
    """Retrieve all policies related to a specific opportunity (lead)."""
    try:
        # Validate opportunity
        opportunity = QueryBuilderService("crm_opportunities").where("id", opportunity_id).first()
        if not opportunity:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

        # Request params
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "pb.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_filters = ["pb.policy_start_date", "pb.policy_expiry_date", "p.name"]
        search_columns = ["p.name", "pb.quotation_notes"]
        allowed_sorting_columns = ["pb.policy_start_date", "pb.policy_expiry_date", "p.name"]

        # Main query
        policies = (
            QueryBuilderService("crmp_policy_base as pb")
            .leftJoin("core_products as p", "p.id", "pb.product_id")
            .select("pb.*", "p.name as product_name", "p.code as product_code")
            .where("pb.lead_id", opportunity_id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", policies, Message.DATA_FETCHED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred")




@api_view(["GET"])
def get_issued_policies_by_lead(request, lead_id):
    columns = [
        "crmp_issued_policies.*",
        "crmp_issued_policies.remarks AS insurer_notes",
        "policy_base.quotation_document as quotation_document",
        "policy_base.quotation_document_name as quotation_document_name",
        "insurer_sp.name AS insurer_name",
        "insurer_sp.logo AS insurer_logo",
        # Product details
        "products.id AS product_id",
        "products.name AS product_name",
        "products.code AS product_code",
        "product_groups.id AS product_group_id",
        "product_groups.name AS product_group_name",
        # Risk type details - removed since it's many-to-many relationship
        # "risk_type.id AS risk_type_id",
        # "risk_type.title AS risk_type_name",
        # Sum insured and status
        "policy_base.sum_insured AS sum_insured_amount",
        "policy_base.status_id AS status_id",
        "status.name AS status_name",
        "status.color AS status_color"
    ]

    query = (
        QueryBuilderService("crmp_issued_policies")
        .select(*columns)
        .leftJoin("crmp_policy_base as policy_base", "policy_base.id", "crmp_issued_policies.policy_base_id")
        .leftJoin("core_service_providers as insurer_sp", "insurer_sp.id", "policy_base.insurer_id")
        .leftJoin("core_vendor_products as products", "products.id", "policy_base.product_id")
        .leftJoin("core_product_groups as product_groups", "product_groups.id", "policy_base.product_group_id")
        # Removed risk_type join since it's many-to-many relationship
        # .leftJoin("crm_opportunity_types as risk_type", "risk_type.id", "policy_base.risk_type_id")
        .leftJoin("core_status as status", "status.id", "policy_base.status_id")
        .where("policy_base.lead_id", lead_id)
    )

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmp_issued_policies.start_date",)
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["insurer_sp.name", "products.name", "product_groups.name"]
    search_columns = [
        "crmp_issued_policies.brokerage_policy_id",
        "policy_base.quotation_document_name",
        "insurer_sp.name",
        "products.name",
        "product_groups.name"
    ]
    sort_columns = [
        "crmp_issued_policies.end_date",
        "crmp_issued_policies.start_date",
        "insurer_sp.name",
        "products.name",
        "product_groups.name",
        "policy_base.sum_insured"
    ]

    result = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    rows = result.get("data", [])

    result = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    rows = result.get("data", [])
    
    # Fetch risk types for each policy base
    if rows:
        policy_base_ids = [policy.get("policy_base_id") for policy in rows if policy.get("policy_base_id")]
        
        if policy_base_ids:
            # Query to get risk types for all policy bases
            risk_types_query = (
                QueryBuilderService("crmp_policy_base_risk_types")
                .select(
                    "crmp_policy_base_risk_types.policy_base_id",
                    "crm_opportunity_types.id AS risk_type_id",
                    "crm_opportunity_types.title AS risk_type_name"
                )
                .leftJoin(
                    "crm_opportunity_types",
                    "crm_opportunity_types.id",
                    "crmp_policy_base_risk_types.risk_type_id"
                )
                .whereIn("crmp_policy_base_risk_types.policy_base_id", policy_base_ids)
            )
            
            risk_types_data = risk_types_query.get()
            
            # Group risk types by policy_base_id
            risk_types_by_policy = {}
            for risk_type in risk_types_data:
                policy_base_id = risk_type["policy_base_id"]
                if policy_base_id not in risk_types_by_policy:
                    risk_types_by_policy[policy_base_id] = []
                risk_types_by_policy[policy_base_id].append({
                    "id": risk_type["risk_type_id"],
                    "name": risk_type["risk_type_name"]
                })
            
            # Add risk types to each policy
            for policy in rows:
                policy_base_id = policy.get("policy_base_id")
                policy["risk_types"] = risk_types_by_policy.get(policy_base_id, [])
    
    for policy in rows:
        _format_date_fields(policy)

    result["data"] = rows

    return ResponseService.response("SUCCESS", result,Message.DATA_FETCHED)
