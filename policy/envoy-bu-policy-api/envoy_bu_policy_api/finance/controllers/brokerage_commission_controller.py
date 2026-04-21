from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser
from envoy_bu_policy_api.finance.controllers.utils.commission_status_utils import (
    calculate_brokerage_commission_status,
    update_brokerage_commission_status,
    format_commission_status_with_metadata
)

def get_columns():
    return [
        "crmf_brokerage_commission.*",
        "core_entities.created_at as created_at",
        "cr.display_name as created_by",
        "cr.picture as created_by_logo",
        "crmf_invoices.invoice_number",
        "crmf_invoices.invoice_amount",
        "crmf_invoices.paid_amount",
        "crmf_invoices.transaction_type_id",
        # "crmf_invoices.outstanding_amount",
        "crmf_invoices.last_paid_date",
        "crmp_issued_policies.brokerage_policy_id",
        "crmp_issued_policies.premium_amount",
        "crmp_issued_policies.policy_effective_date",
        "crmp_issued_policies.end_date",
        "crmp_issued_policies.credit_period_days",
        # Commission Setup Information
        "crmf_commission_setups.*",
        # "core_users.display_name as user_name",
        # "core_teams.name as team_name",
        "core_service_providers.name as insurer_name",
        "core_service_providers.id as insurer_id",
        "core_vendor_products.name as product_name",
        # Calculated Fields
        "crmf_brokerage_commission.brokerage_revenue_percent",
        "crmf_brokerage_commission.brokerage_revenue_type",
        "crmf_brokerage_commission.revenue_recognized as brokerage_revenue_recognized",
        "crmf_brokerage_commission.commission_deductible",
        "crmf_brokerage_commission.revenue_realized as brokerage_revenue_realized",
        "crmf_brokerage_commission.overriding_commission_amount",
        "crmf_brokerage_commission.agent_commission as total_agent_commission",
        "(crmf_brokerage_commission.revenue_recognized - COALESCE(crmf_brokerage_commission.revenue_realized, 0) - COALESCE(crmf_brokerage_commission.commission_deductible, 0)) as outstanding",
        # Explicitly select ID from brokerage commission at the end to ensure it overwrites any other id
        "crmf_brokerage_commission.id",
        # Agent commission fields will be fetched separately to avoid duplicates
    ]

def build_base_query():
    return (
        QueryBuilderService("crmf_brokerage_commission")
        .select(*get_columns())
        .leftJoin("core_entities", "core_entities.id", "crmf_brokerage_commission.entity_id")
        .leftJoin("core_users as cr", "cr.id", "core_entities.created_by_id")
        .leftJoin("crmf_invoices", "crmf_invoices.id", "crmf_brokerage_commission.invoice_id")
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id"
        )
        # Commission Setup Join
        .leftJoin(
            "crmf_commission_setups",
            "crmf_commission_setups.id",
            "crmf_brokerage_commission.commission_setup_id"
        )
        .leftJoin(
            "core_service_providers",
            "crmf_invoices.insurer_id",
            "core_service_providers.id"
        )
        .leftJoin(
            "core_vendor_products",
            "crmf_commission_setups.product_id",
            "core_vendor_products.id"
        )
        # Note: Agent commission is fetched separately in the loop to avoid duplicates
        # Exclude refund (4) and cancellation (5) invoices - these are deductions, not commission calculations
        .whereNotIn("crmf_invoices.transaction_type_id", [4, 5])
        # Exclude Addition (2) invoices that don't have a commission setup (commission_setup_id IS NULL)
        # This ensures we only show Addition invoices that have commission calculations
        # Logic: Show all invoices EXCEPT Addition invoices without commission_setup_id
        # Using where_group: (transaction_type_id != 2) OR (commission_setup_id IS NOT NULL)
        .where_group(
            lambda group: group.extend([
                ("crmf_invoices.transaction_type_id != %s", [2]),
                ("crmf_brokerage_commission.commission_setup_id IS NOT NULL", []),
            ])
        )
    )

def get_filter_params(request):
    filter_json = json.loads(request.GET.get("filter", "{}"))
    
    # Add date filters to filter_json if provided
    start_date = request.GET.get("start_date", None)
    end_date = request.GET.get("end_date", None)
    
    if start_date and end_date:
        # Add time to make it cover the full day
        start_date = f"{start_date} 00:00:00"
        end_date = f"{end_date} 23:59:59"
        # Use two separate conditions for date range
        filter_json["core_entities.created_at_start"] = {
            "o": ">=",
            "v": start_date
        }
        filter_json["core_entities.created_at_end"] = {
            "o": "<=",
            "v": end_date
        }
    elif start_date:
        start_date = f"{start_date} 00:00:00"
        filter_json["core_entities.created_at"] = {
            "o": ">=",
            "v": start_date
        }
    elif end_date:
        end_date = f"{end_date} 23:59:59"
        filter_json["core_entities.created_at"] = {
            "o": "<=",
            "v": end_date
        }

    # Add insurer filter if provided
    insurer_id = request.GET.get("insurer_id", None)
    if insurer_id:
        filter_json["core_service_providers.id"] = {
            "o": "=",
            "v": insurer_id
        }
    sort_by = request.GET.get('sort_by')
    sort_dir = request.GET.get('sort_dir')

    sort_by = "core_entities.id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    return {
        'filter_json': json.dumps(filter_json),
        'search_string': request.GET.get("search", ""),
        'page': int(request.GET.get("page", 1)),
        'limit': int(request.GET.get("limit", 10)),
        'sort_by': sort_by,
        'sort_dir': sort_dir
    }

def get_allowed_filters():
    return [
        "crmf_invoices.invoice_number",
        "crmf_invoices.transaction_type_id",
        "crmp_issued_policies.brokerage_policy_id",
        "crmf_brokerage_commission.status",
        "core_vendor_products.name",
        "core_service_providers.name",
        "core_service_providers.id",
        "crmp_issued_policies.transaction_type",
        "core_teams.name",
        "crmf_commission_setups.commission_type",
        "core_entities.created_at",
        "core_entities.created_at_start",
        "core_entities.created_at_end"
    ]

def get_search_columns():
    return [
        "crmf_invoices.invoice_number",
        "crmp_issued_policies.brokerage_policy_id",
        "core_vendor_products.name",
        "core_service_providers.name",
        "core_teams.name"
    ]

def get_sort_columns():
    return ["crmf_brokerage_commission.id", "core_entities.created_at"]


def apply_commission_type_filter(query, commission_type):
    if commission_type:
        query = query.where("crmf_commission_setups.commission_type", commission_type)
    return query

# Helper to get teams for a commission setup

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

def format_percentage_value(value):
    """Format percentage value to remove trailing zeros but keep significant decimals"""
    if value is None:
        return None
    try:
        # Convert to float to remove trailing zeros, then back to string
        float_val = float(str(value))
        # If it's a whole number, return as integer string, otherwise return with significant decimals
        if float_val == int(float_val):
            return str(int(float_val))
        else:
            # Remove trailing zeros
            return str(float_val).rstrip('0').rstrip('.')
    except (ValueError, TypeError):
        return value

def format_fixed_value(value):
    """Format fixed value to always have 2 decimal places"""
    if value is None:
        return None
    try:
        float_val = float(str(value))
        # Format to 2 decimal places
        return f"{float_val:.2f}"
    except (ValueError, TypeError):
        return value

def format_brokerage_commission_percentages(row):
    """Format brokerage commission values based on their type: percentage removes trailing zeros, fixed keeps 2 decimals"""
    if isinstance(row, dict):
        # Format brokerage_revenue_percent based on brokerage_revenue_type
        brokerage_revenue_type = row.get('brokerage_revenue_type') or ''
        if brokerage_revenue_type:
            brokerage_revenue_type = str(brokerage_revenue_type).lower()
        if 'brokerage_revenue_percent' in row:
            if brokerage_revenue_type == 'percentage':
                row['brokerage_revenue_percent'] = format_percentage_value(row['brokerage_revenue_percent'])
            elif brokerage_revenue_type in ['fixed', 'flat']:
                row['brokerage_revenue_percent'] = format_fixed_value(row['brokerage_revenue_percent'])
        
        # Format agent_commission_percent based on agent_commission_type
        agent_commission_type = row.get('agent_commission_type') or ''
        if agent_commission_type:
            agent_commission_type = str(agent_commission_type).lower()
        if 'agent_commission_percent' in row and agent_commission_type:
            if agent_commission_type == 'percentage':
                row['agent_commission_percent'] = format_percentage_value(row['agent_commission_percent'])
            elif agent_commission_type in ['fixed', 'flat']:
                row['agent_commission_percent'] = format_fixed_value(row['agent_commission_percent'])
    return row

@csrf_exempt
@api_view(["GET"])
def brokerage_commission_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("BrokerageCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_all_brokerage_commissions(request)

def get_all_brokerage_commissions(request):
    params = get_filter_params(request)
    query = build_base_query()

    # Apply date range filters manually if they exist
    filter_json = json.loads(params['filter_json'])
    if "core_entities.created_at_start" in filter_json and "core_entities.created_at_end" in filter_json:
        start_date = filter_json["core_entities.created_at_start"]["v"]
        end_date = filter_json["core_entities.created_at_end"]["v"]
        query = query.where("core_entities.created_at", start_date, ">=")
        query = query.where("core_entities.created_at", end_date, "<=")
        # Remove these from filter_json as we've handled them manually
        del filter_json["core_entities.created_at_start"]
        del filter_json["core_entities.created_at_end"]
        params['filter_json'] = json.dumps(filter_json)

    data = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    ).paginate(
        params['page'],
        params['limit'],
        get_sort_columns(),
        params['sort_by'],
        params['sort_dir']
    )

    # Add teams array to each commission record and format percentages
    if data and 'data' in data:
        for row in data['data']:
            # Ensure id comes from crmf_brokerage_commission table
            # The id is explicitly selected from crmf_brokerage_commission at the end of columns list
            # This ensures it overwrites any id from crmf_commission_setups.*
            brokerage_commission_id = row.get('id')
            
            setup_id = row.get('commission_setup_id') or brokerage_commission_id
            if setup_id:
                row['teams'] = get_teams_for_setup(setup_id)
            else:
                row['teams'] = []
            
            # Get agent commission type and percent from first agent commission if not already in row
            # This avoids duplicates from joins and ensures we get the data
            if 'agent_commission_type' not in row or not row.get('agent_commission_type'):
                brokerage_commission_id = row.get('id')
                if brokerage_commission_id:
                    first_agent_commission = QueryBuilderService("crmf_agent_commission")\
                        .select("agent_commission_type", "agent_commission_percent")\
                        .where("brokerage_commission_id", brokerage_commission_id)\
                        .first()
                    if first_agent_commission:
                        row['agent_commission_type'] = first_agent_commission.get('agent_commission_type')
                        row['agent_commission_percent'] = first_agent_commission.get('agent_commission_percent')
            
            # Get status from database first (before calculating/formatting)
            # The status field from crmf_brokerage_commission.* will contain the raw database status
            db_status = str(row.get('status', '')).lower().strip() if row.get('status') else ''
            
            # Calculate and update status
            # Use invoice paid_amount as customer_settlements (customer payment)
            # revenue_realized is the insurer payment (editable)
            customer_settlements = row.get('paid_amount', 0) or 0  # From invoice
            
            # Only calculate status if it's not "completed" in the database
            if db_status == 'completed':
                # Status is already "completed", use it as is
                status = 'completed'
            else:
                status = calculate_brokerage_commission_status(
                    customer_settlements,
                    row.get('revenue_realized', 0) or 0,
                    row.get('revenue_recognized', 0) or 0
                )
            
            # Add status fields directly to response (status, status_type, status_id, status_color)
            # For "completed" status, format it appropriately
            if status == 'completed':
                row['status'] = 'COMPLETED'  # Use uppercase for consistency
                row['status_type'] = None
                row['status_id'] = None
                row['status_color'] = '#067647'  # Green color for completed
            else:
                status_metadata = format_commission_status_with_metadata(status, commission_type="brokerage")
                row['status'] = status_metadata.get('status')  # Use name from database
                row['status_type'] = status_metadata.get('status_type')
                row['status_id'] = status_metadata.get('status_id')
                row['status_color'] = status_metadata.get('status_color')
            
            # If status is "completed", set outstanding to 0.00
            if db_status == 'completed' or status == 'completed':
                row['outstanding'] = "0.00"
            
            # Format percentage values (only when type is "percentage")
            row = format_brokerage_commission_percentages(row)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def brokerage_commission_totals(request):
    action_type = "VIEW"
    action = ActionService.getAction("BrokerageCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    params = get_filter_params(request)
    query = build_base_query()

    # Apply date range filters manually if they exist
    filter_json = json.loads(params['filter_json'])
    if "core_entities.created_at_start" in filter_json and "core_entities.created_at_end" in filter_json:
        start_date = filter_json["core_entities.created_at_start"]["v"]
        end_date = filter_json["core_entities.created_at_end"]["v"]
        query = query.where("core_entities.created_at", start_date, ">=")
        query = query.where("core_entities.created_at", end_date, "<=")
        # Remove these from filter_json as we've handled them manually
        del filter_json["core_entities.created_at_start"]
        del filter_json["core_entities.created_at_end"]
        params['filter_json'] = json.dumps(filter_json)

    # Apply other conditions
    query = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    )
    
    # Calculate totals using the same filtered query
    totals = query.select(
        "SUM(crmf_brokerage_commission.brokerage_revenue_percent * crmf_brokerage_commission.revenue_realized / 100) as total_commission",
        "SUM(crmf_brokerage_commission.revenue_realized) as total_revenue_realized",
        "SUM(crmf_brokerage_commission.overriding_commission_amount) as total_overriding_commission",
        "SUM(crmf_brokerage_commission.agent_commission) as total_agent_commission",
        "SUM(COALESCE(crmf_brokerage_commission.commission_deductible, 0)) as total_commission_deductible",
        "SUM(crmf_brokerage_commission.revenue_recognized - COALESCE(crmf_brokerage_commission.revenue_realized, 0) - COALESCE(crmf_brokerage_commission.commission_deductible, 0)) as total_outstanding"
    ).first()

    return ResponseService.response("SUCCESS", totals, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def brokerage_commission_detail(request, commission_id):
    action_type = "VIEW"
    action = ActionService.getAction("BrokerageCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    commission = build_base_query().where("crmf_brokerage_commission.id", commission_id).first()

    if not commission:
        return ResponseService.response("NOT_FOUND", None, Error.DATA_NOT_FOUND)

    # Calculate and update status
    # Use invoice paid_amount as customer_settlements (customer payment)
    # revenue_realized is the insurer payment (editable)
    customer_settlements = commission.get('paid_amount', 0) or 0  # From invoice
    status = calculate_brokerage_commission_status(
        customer_settlements,
        commission.get('revenue_realized', 0) or 0,
        commission.get('revenue_recognized', 0) or 0
    )
    
    # Add status fields directly to response (status, status_type, status_id, status_color)
    status_metadata = format_commission_status_with_metadata(status, commission_type="brokerage")
    commission['status'] = status_metadata.get('status')  # Use name from database
    commission['status_type'] = status_metadata.get('status_type')
    commission['status_id'] = status_metadata.get('status_id')
    commission['status_color'] = status_metadata.get('status_color')

    # Format percentage values (only when type is "percentage")
    commission = format_brokerage_commission_percentages(commission)

    return ResponseService.response("SUCCESS", commission, Message.DATA_FETCHED) 

@csrf_exempt
@api_view(["POST"])
@parser_classes([JSONParser])
def multi_brokerage_commission_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("BrokerageCommission", action_type)
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    insurer_ids = request.data.get("insurer_ids", None)
    # Optional single commission filter from query params
    commission_id = request.GET.get("commission_id", None)
    # Check if we should filter for negative outstanding values only
    filter_negative_outstanding = request.data.get("negative_outstanding", False)
    # Also check query parameters for backward compatibility
    if not filter_negative_outstanding:
        filter_negative_outstanding = request.GET.get("negative_outstanding", "false").lower() == "true"
    
    params = get_filter_params(request)
    query = build_base_query()

    # Apply date range filters manually if they exist
    filter_json = json.loads(params['filter_json'])
    if "core_entities.created_at_start" in filter_json and "core_entities.created_at_end" in filter_json:
        start_date = filter_json["core_entities.created_at_start"]["v"]
        end_date = filter_json["core_entities.created_at_end"]["v"]
        query = query.where("core_entities.created_at", start_date, ">=")
        query = query.where("core_entities.created_at", end_date, "<=")
        del filter_json["core_entities.created_at_start"]
        del filter_json["core_entities.created_at_end"]
        params['filter_json'] = json.dumps(filter_json)

    # Apply other filters
    query = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    )

    # Now apply the insurer filter directly if insurer_ids is provided and non-empty
    if insurer_ids is not None and len(insurer_ids) > 0:
        query = query.whereIn("crmf_invoices.insurer_id", insurer_ids)
    # else: do not add any filter for core_service_providers.id, so all insurers are included

    # Apply commission_id filter if provided via query params
    if commission_id:
        query = query.where("crmf_brokerage_commission.id", commission_id)

    # Filter for negative outstanding values only if parameter is set
    # Outstanding = revenue_recognized - revenue_realized - commission_deductible
    # We want records where outstanding < 0 AND not yet settled (exclude RECEIVED IN FULL)
    # So: outstanding < 0 AND revenue_realized < revenue_recognized (insurer has not paid in full)
    # Also exclude status = 'completed' so list only returns commissions valid for api/brokerage-commission-settlements
    if filter_negative_outstanding:
        outstanding_expression = "(crmf_brokerage_commission.revenue_recognized - COALESCE(crmf_brokerage_commission.revenue_realized, 0) - COALESCE(crmf_brokerage_commission.commission_deductible, 0))"
        query = query.where(outstanding_expression, 0, "<")
        # Exclude already settled (RECEIVED IN FULL): only show where insurer has not paid in full
        query.conditions.append((
            "COALESCE(crmf_brokerage_commission.revenue_realized, 0) < crmf_brokerage_commission.revenue_recognized",
            []
        ))
        # Exclude commissions already settled (status = 'completed') - same check as brokerage-commission-settlements endpoint
        query = query.where("COALESCE(crmf_brokerage_commission.status, '')", "completed", "!=")

    # Multi brokerage commission list: always order in descending order (newest/latest first)
    params['sort_dir'] = 'desc'

    data = query.paginate(
        params['page'],
        params['limit'],
        get_sort_columns(),
        params['sort_by'],
        params['sort_dir']
    )

    # Format percentage values and add status metadata
    if data and 'data' in data and isinstance(data['data'], list):
        for row in data['data']:
            # Calculate and update status
            # Use invoice paid_amount as customer_settlements (customer payment)
            # revenue_realized is the insurer payment (editable)
            customer_settlements = row.get('paid_amount', 0) or 0  # From invoice
            status = calculate_brokerage_commission_status(
                customer_settlements,
                row.get('revenue_realized', 0) or 0,
                row.get('revenue_recognized', 0) or 0
            )
            
            # Add status fields directly to response (status, status_type, status_id, status_color)
            status_metadata = format_commission_status_with_metadata(status, commission_type="brokerage")
            row['status'] = status_metadata.get('status')  # Use name from database
            row['status_type'] = status_metadata.get('status_type')
            row['status_id'] = status_metadata.get('status_id')
            row['status_color'] = status_metadata.get('status_color')
            
            # Format percentages
            row = format_brokerage_commission_percentages(row)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["POST"])
@parser_classes([JSONParser])
def multi_brokerage_commission_totals(request):
    action_type = "VIEW"
    action = ActionService.getAction("BrokerageCommission", action_type)
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    insurer_ids = request.data.get("insurer_ids", None)
    commission_ids = request.data.get("commission_ids", None)
    params = get_filter_params(request)
    query = build_base_query()

    # Apply date range filters manually if they exist
    filter_json = json.loads(params['filter_json'])
    if "core_entities.created_at_start" in filter_json and "core_entities.created_at_end" in filter_json:
        start_date = filter_json["core_entities.created_at_start"]["v"]
        end_date = filter_json["core_entities.created_at_end"]["v"]
        query = query.where("core_entities.created_at", start_date, ">=")
        query = query.where("core_entities.created_at", end_date, "<=")
        del filter_json["core_entities.created_at_start"]
        del filter_json["core_entities.created_at_end"]
        params['filter_json'] = json.dumps(filter_json)

    # Apply other filters
    query = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    )

    # Now apply the insurer filter directly if insurer_ids is provided and non-empty
    if insurer_ids is not None and len(insurer_ids) > 0:
        query = query.whereIn("crmf_invoices.insurer_id", insurer_ids)
    # else: do not add any filter for core_service_providers.id, so all insurers are included

    # Apply the commission filter directly if commission_ids is provided and non-empty
    if commission_ids is not None and len(commission_ids) > 0:
        query = query.whereIn("crmf_brokerage_commission.id", commission_ids)

    # Calculate totals using the same filtered query
    totals = query.select(
        "SUM(crmf_brokerage_commission.brokerage_revenue_percent * crmf_brokerage_commission.revenue_realized / 100) as total_commission",
        "SUM(crmf_brokerage_commission.revenue_realized) as total_revenue_realized",
        "SUM(crmf_brokerage_commission.overriding_commission_amount) as total_overriding_commission",
        "SUM(crmf_brokerage_commission.agent_commission) as total_agent_commission",
        "SUM(COALESCE(crmf_brokerage_commission.commission_deductible, 0)) as total_commission_deductible",
        "SUM(crmf_brokerage_commission.revenue_recognized - COALESCE(crmf_brokerage_commission.revenue_realized, 0) - COALESCE(crmf_brokerage_commission.commission_deductible, 0)) as total_outstanding",
        "SUM(crmf_brokerage_commission.revenue_recognized) as gross_revenue"
    ).first()

    # Calculate net revenue = gross revenue - total deductibles
    gross_revenue = float(totals.get('gross_revenue', 0) or 0)
    total_deductibles = float(totals.get('total_commission_deductible', 0) or 0)
    net_revenue = gross_revenue - total_deductibles
    
    # Add net revenue to totals
    totals['net_revenue'] = net_revenue

    return ResponseService.response("SUCCESS", totals, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["PUT", "PATCH"])
@parser_classes([JSONParser])
def brokerage_commission_update(request, commission_id):
    """
    Update brokerage commission, specifically revenue_realized (insurer payment).
    This allows manual editing of revenue_realized when insurer pays.
    Status is automatically recalculated and updated.
    """
    from decimal import Decimal
    
    action_type = "EDIT"
    action = ActionService.getAction("BrokerageCommission", action_type)
    
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    
    try:
        data = json.loads(request.body or "{}")
        
        # Validate commission exists
        commission = QueryBuilderService("crmf_brokerage_commission").where("id", commission_id).first()
        if not commission:
            return ResponseService.response("NOT_FOUND", None, Error.DATA_NOT_FOUND)
        
        # Prepare update data
        update_data = {}
        
        # Allow updating revenue_realized (insurer payment)
        if "revenue_realized" in data:
            revenue_realized = Decimal(str(data["revenue_realized"]))
            # Get customer settlements from invoice paid_amount
            invoice = QueryBuilderService("crmf_invoices").where("id", commission.get("invoice_id")).first()
            customer_settlements = Decimal(str(invoice.get("paid_amount", 0) if invoice else 0))
            revenue_recognized = Decimal(str(commission.get("revenue_recognized", 0)))
            
            # Calculate and set status
            status = calculate_brokerage_commission_status(
                customer_settlements,
                revenue_realized,
                revenue_recognized
            )
            update_data["revenue_realized"] = str(revenue_realized)
            update_data["status"] = status
        
        # Update the commission
        if update_data:
            result = QueryBuilderService("crmf_brokerage_commission").where("id", commission_id).update(update_data)
            
            if result:
                # Return updated commission with status fields
                updated_commission = build_base_query().where("crmf_brokerage_commission.id", commission_id).first()
                if updated_commission:
                    # Calculate status
                    customer_settlements = updated_commission.get('paid_amount', 0) or 0
                    calculated_status = calculate_brokerage_commission_status(
                        customer_settlements,
                        updated_commission.get('revenue_realized', 0) or 0,
                        updated_commission.get('revenue_recognized', 0) or 0
                    )
                    
                    # Add status fields directly to response (status, status_type, status_id, status_color)
                    status_metadata = format_commission_status_with_metadata(calculated_status, commission_type="brokerage")
                    updated_commission['status'] = status_metadata.get('status')  # Use name from database
                    updated_commission['status_type'] = status_metadata.get('status_type')
                    updated_commission['status_id'] = status_metadata.get('status_id')
                    updated_commission['status_color'] = status_metadata.get('status_color')
                    updated_commission = format_brokerage_commission_percentages(updated_commission)
                return ResponseService.response("SUCCESS", updated_commission, Message.DATA_UPDATED)
            else:
                return ResponseService.response("ERROR", None, "Update failed")
        else:
            return ResponseService.response("VALIDATION_ERROR", {"error": "No valid fields to update"}, "validation_error")
            
    except Exception as e:
        return ResponseService.response("ERROR", {"error": str(e)}, "default_error")
