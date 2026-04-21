from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, parser_classes
import json
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from rest_framework.parsers import JSONParser
from envoy_bu_policy_api.finance.controllers.utils.commission_status_utils import (
    calculate_agent_commission_status,
    format_commission_status_with_metadata
)
from services.pdf_download_service import PDFDownloadService
from services.s3_presigned_service import S3PresignedService
import os

def get_columns():
    return [
        # Explicitly list and alias all fields from crmf_agent_commission
        "crmf_agent_commission.id as id",
        "crmf_agent_commission.brokerage_commission_id",
        "crmf_agent_commission.agent_id",
        "crmf_agent_commission.agent_commission_percent",
        "crmf_agent_commission.agent_commission_type",
        "crmf_agent_commission.revised_amount_percent as revised_amount_percent",
        "crmf_agent_commission.revised_amount_type",
        "crmf_agent_commission.target_achievement_amount",
        "crmf_agent_commission.revised_amount",
        "crmf_agent_commission.revenue_recognized",
        "crmf_agent_commission.revenue_realized",
        "crmf_agent_commission.paid_amount",
        "crmf_agent_commission.status",
        "crmf_agent_commission.entity_id",
        "crmf_agent_commission.commission_setup_id",
        "crmf_agent_commission.commission_deductible",
        "core_entities.created_at as created_at",
        "cr.display_name as created_by",
        "cr.picture as created_by_logo",
        "crmf_brokerage_commission.brokerage_revenue_percent",
        "crmf_brokerage_commission.revenue_recognized as brokerage_revenue_recognized",
        "crmf_brokerage_commission.revenue_realized as brokerage_revenue_realized",
        "crmf_brokerage_commission.overriding_commission_amount",
        "crmf_brokerage_commission.agent_commission as total_agent_commission",
        "crmf_invoices.invoice_number",
        "crmf_invoices.invoice_amount",
        "crmf_invoices.paid_amount",
        # "crmf_invoices.outstanding_amount",
        "crmf_invoices.last_paid_date",
        "crmp_issued_policies.brokerage_policy_id",
        "crmp_issued_policies.premium_amount",
        "crmp_issued_policies.policy_effective_date",
        "crmp_issued_policies.end_date",
        # Explicitly list and alias all fields from crmf_commission_setups
        "crmf_commission_setups.id as commission_setup_id",
        "crmf_commission_setups.insurer_id",
        "crmf_commission_setups.product_id",
        # "crmf_commission_setups.commission_percent",
        # "crmf_commission_setups.status as commission_setup_status",
        "core_service_providers.name as insurer_name",
        "core_vendor_products.name as product_name",
        "agent.display_name as agent_name",
        "agent.email as agent_email",
        "agent.picture as agent_picture",
        "COALESCE(crmf_agent_commission.revenue_realized, 0) - COALESCE((SELECT SUM(payment_amount) FROM crmf_agent_commission_payments WHERE agent_commission_id = crmf_agent_commission.id), 0) - COALESCE(crmf_agent_commission.commission_deductible, 0) as outstanding",
        "COALESCE((SELECT SUM(payment_amount) FROM crmf_agent_commission_payments WHERE agent_commission_id = crmf_agent_commission.id), 0) as paid_amount"
        # "core_vendor_products.type as product_type",
        # Calculated Fields
        # "CASE WHEN crmp_issued_policies.status = 'active' THEN 1 ELSE 0 END as is_active",
        # "CASE WHEN crmp_issued_policies.status = 'pending' THEN 1 ELSE 0 END as is_pending",
        # "CASE WHEN crmp_issued_policies.status = 'cancelled' THEN 1 ELSE 0 END as is_cancelled"
    ]

def build_base_query():
    return (
        QueryBuilderService("crmf_agent_commission")
        .select(*get_columns())
        .leftJoin("core_entities", "core_entities.id", "crmf_agent_commission.entity_id")
        .leftJoin("core_users as cr", "cr.id", "core_entities.created_by_id")
        .leftJoin("core_users as agent", "agent.id", "crmf_agent_commission.agent_id")
        .leftJoin(
            "crmf_brokerage_commission",
            "crmf_brokerage_commission.id",
            "crmf_agent_commission.brokerage_commission_id"
        )
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
            "crmf_commission_setups.insurer_id",
            "core_service_providers.id"
        )
        .leftJoin(
            "core_vendor_products",
            "crmf_commission_setups.product_id",
            "core_vendor_products.id"
        )
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
        start_date = f"{start_date} 00:00:00"
        end_date = f"{end_date} 23:59:59"
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
    
    # Add agent filter if provided
    agent_id = request.GET.get("agent_id", None)
    if agent_id:
        filter_json["agent.id"] = {
            "o": "=",
            "v": agent_id
        }

    # Handle empty sort parameters - use defaults if empty strings are passed
    sort_by = request.GET.get("sort_by", "core_entities.created_at")
    sort_dir = request.GET.get("sort_dir", "desc")
    
    # If empty strings are passed, use default values
    if not sort_by or sort_by.strip() == "":
        sort_by = "core_entities.created_at"
    if not sort_dir or sort_dir.strip() == "":
        sort_dir = "desc"
    
    # Ensure latest records come first
    if sort_by == "core_entities.created_at" and sort_dir != "desc":
        sort_dir = "desc"
    
    return {
        'filter_json': json.dumps(filter_json),
        'search_string': request.GET.get("search", ""),
        'page': int(request.GET.get("page", 1)),
        'limit': int(request.GET.get("limit", 10)),
        'sort_by': sort_by,
        'sort_dir': sort_dir,
        'status': request.GET.get("status", None)
    }

def get_allowed_filters():
    return [
        "crmf_invoices.invoice_number",
        "crmp_issued_policies.brokerage_policy_id",
        "crmf_agent_commission.status",
        "agent.id",
        "core_vendor_products.name",
        "core_service_providers.name",
        "crmp_issued_policies.transaction_type",
        "core_entities.created_at",
        "core_entities.created_at_start",
        "core_entities.created_at_end"
    ]

def get_search_columns():
    return [
        "crmf_invoices.invoice_number",
        "crmp_issued_policies.brokerage_policy_id",
        "agent.display_name",
        "core_vendor_products.name",
        "core_service_providers.name",
        "core_entities.created_at"
    ]

def get_sort_columns():
    return ["crmf_agent_commission.id", "core_entities.created_at"]

def apply_date_filters(query, filter_json):
    if "core_entities.created_at_start" in filter_json and "core_entities.created_at_end" in filter_json:
        start_date = filter_json["core_entities.created_at_start"]["v"]
        end_date = filter_json["core_entities.created_at_end"]["v"]
        query = query.where("core_entities.created_at", start_date, ">=")
        query = query.where("core_entities.created_at", end_date, "<=")
        del filter_json["core_entities.created_at_start"]
        del filter_json["core_entities.created_at_end"]
    return query, filter_json

def get_commission_totals(query):
    return query.select(
        "SUM(crmf_agent_commission.revenue_recognized) as total_commission_earned",
        "SUM(crmf_agent_commission.revenue_realized) as total_commission_received",
        "SUM(crmf_agent_commission.revenue_recognized - crmf_agent_commission.revenue_realized) as total_commission_pending",
        "SUM(crmf_agent_commission.revenue_recognized - crmf_agent_commission.revenue_realized) as total_outstanding"
        # "COUNT(CASE WHEN crmp_issued_policies.status = 'active' THEN 1 END) as total_active_policies",
        # "COUNT(CASE WHEN crmp_issued_policies.status = 'pending' THEN 1 END) as total_pending_policies",
        # "COUNT(CASE WHEN crmp_issued_policies.status = 'cancelled' THEN 1 END) as total_cancelled_policies"
    ).first()

def get_policy_stats(query):
    return query.select(
        "COUNT(*) as total_policies",
        # "COUNT(CASE WHEN crmp_issued_policies.status = 'active' THEN 1 END) as active_policies",
        # "COUNT(CASE WHEN crmp_issued_policies.status = 'pending' THEN 1 END) as pending_policies",
        # "COUNT(CASE WHEN crmp_issued_policies.status = 'cancelled' THEN 1 END) as cancelled_policies",
        "SUM(crmf_agent_commission.revenue_recognized) as total_commission_earned",
        "SUM(crmf_agent_commission.revenue_realized) as total_commission_received",
        "SUM(crmf_agent_commission.revenue_recognized - crmf_agent_commission.revenue_realized) as total_commission_pending"
    ).first()

@csrf_exempt
@api_view(["GET"])
def agent_commission_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_all_agent_commissions(request)

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

def get_original_agent_commission_percent(commission_setup_id, agent_id):
    """Get the original agent commission percentage from commission setup"""
    if not commission_setup_id or not agent_id:
        return None
    
    try:
        # Get the original agent commission percentage from commission setup
        agent_commission_field = QueryBuilderService("crmf_commission_fields").where("attribute_name", "agent_commission_percent").first()
        if not agent_commission_field:
            print(f"DEBUG: agent_commission_percent field not found")
            return None
        
        field_id = agent_commission_field.get('id')
        if not field_id:
            print(f"DEBUG: field_id is None")
            return None
        
        # Get the value for this agent from commission setup
        commission_value = (
            QueryBuilderService("crmf_commission_field_values")
            .where("commission_setup_id", commission_setup_id)
            .where("commission_field_id", field_id)
            .where("user_id", agent_id)
            .first()
        )
        
        if commission_value and commission_value.get('value'):
            print(f"DEBUG: Found original agent_commission_percent for agent {agent_id}: {commission_value.get('value')}")
            return commission_value.get('value')
        
        # If no user-specific value, try to get a default value (where user_id IS NULL)
        default_value = (
            QueryBuilderService("crmf_commission_field_values")
            .where("commission_setup_id", commission_setup_id)
            .where("commission_field_id", field_id)
            .whereNull("user_id")
            .first()
        )
        
        if default_value and default_value.get('value'):
            print(f"DEBUG: Found default agent_commission_percent: {default_value.get('value')}")
            return default_value.get('value')
        
        print(f"DEBUG: No original agent_commission_percent found for commission_setup_id={commission_setup_id}, agent_id={agent_id}")
        return None
    except Exception as e:
        print(f"Error getting original agent commission percent: {e}")
        import traceback
        traceback.print_exc()
        return None

def format_commission_percentages(row):
    """Format commission values based on their type: percentage removes trailing zeros, fixed keeps 2 decimals"""
    if isinstance(row, dict):
        # Check if there's a revised commission - if so, get the original agent commission percentage
        revised_amount_percent = row.get('revised_amount_percent')
        revised_amount = row.get('revised_amount', 0) or 0
        commission_setup_id = row.get('commission_setup_id')
        agent_id = row.get('agent_id')
        current_agent_commission_percent = row.get('agent_commission_percent')
        
        # If revised commission exists, get the original agent commission percentage from commission setup
        # When a revised commission is created, agent_commission_percent is overwritten with the revised value
        # So we need to get the original value from the commission setup
        has_revised_commission = False
        try:
            if revised_amount_percent:
                revised_percent_val = float(str(revised_amount_percent))
                if revised_percent_val > 0:
                    has_revised_commission = True
            if not has_revised_commission and revised_amount:
                revised_amount_val = float(str(revised_amount))
                if revised_amount_val > 0:
                    has_revised_commission = True
        except (ValueError, TypeError):
            pass
        
        if has_revised_commission:
            print(f"DEBUG: Revised commission detected for agent_commission_id={row.get('id')}, getting original value...")
            print(f"DEBUG: Current agent_commission_percent={current_agent_commission_percent}, revised_amount_percent={revised_amount_percent}")
            original_agent_commission_percent = get_original_agent_commission_percent(commission_setup_id, agent_id)
            if original_agent_commission_percent is not None:
                print(f"DEBUG: Replacing agent_commission_percent from {current_agent_commission_percent} to {original_agent_commission_percent}")
                # Replace with original value from commission setup
                row['agent_commission_percent'] = original_agent_commission_percent
            else:
                print(f"DEBUG: Could not retrieve original agent_commission_percent, keeping current value: {current_agent_commission_percent}")
                # Also update the type if needed - get it from commission setup
                original_agent_commission_type = None
                try:
                    agent_commission_field = QueryBuilderService("crmf_commission_fields").where("attribute_name", "agent_commission_percent").first()
                    if agent_commission_field:
                        field_id = agent_commission_field.get('id')
                        commission_value = (
                            QueryBuilderService("crmf_commission_field_values")
                            .where("commission_setup_id", commission_setup_id)
                            .where("commission_field_id", field_id)
                            .where("user_id", agent_id)
                            .first()
                        )
                        if not commission_value:
                            commission_value = (
                                QueryBuilderService("crmf_commission_field_values")
                                .where("commission_setup_id", commission_setup_id)
                                .where("commission_field_id", field_id)
                                .whereNull("user_id")
                                .first()
                            )
                        if commission_value:
                            original_agent_commission_type = commission_value.get('type', 'percentage')
                except Exception:
                    pass
                
                if original_agent_commission_type:
                    row['agent_commission_type'] = original_agent_commission_type
        
        # Format agent_commission_percent based on agent_commission_type
        agent_commission_type = row.get('agent_commission_type', '').lower()
        if 'agent_commission_percent' in row:
            if agent_commission_type == 'percentage':
                row['agent_commission_percent'] = format_percentage_value(row['agent_commission_percent'])
            elif agent_commission_type in ['fixed', 'flat']:
                # For fixed/flat commissions, if agent_commission_percent is 0, 
                # display the actual amount from revenue_recognized instead
                agent_commission_percent_val = str(row.get('agent_commission_percent', '0')).strip()
                if agent_commission_percent_val in ['0', '0.00', '0.0', '']:
                    # Use revenue_recognized as the display value for fixed commissions
                    revenue_recognized = row.get('revenue_recognized')
                    if revenue_recognized is not None:
                        row['agent_commission_percent'] = format_fixed_value(revenue_recognized)
                    else:
                        row['agent_commission_percent'] = format_fixed_value(row['agent_commission_percent'])
                else:
                    row['agent_commission_percent'] = format_fixed_value(row['agent_commission_percent'])
        
        # Format revised_amount_percent based on revised_amount_type
        revised_amount_type = row.get('revised_amount_type', '').lower()
        if 'revised_amount_percent' in row:
            if revised_amount_type == 'percentage':
                row['revised_amount_percent'] = format_percentage_value(row['revised_amount_percent'])
            elif revised_amount_type in ['fixed', 'flat']:
                row['revised_amount_percent'] = format_fixed_value(row['revised_amount_percent'])
        
        # Format brokerage_revenue_percent based on brokerage_revenue_type
        brokerage_revenue_type = row.get('brokerage_revenue_type', '').lower()
        if 'brokerage_revenue_percent' in row:
            if brokerage_revenue_type == 'percentage':
                row['brokerage_revenue_percent'] = format_percentage_value(row['brokerage_revenue_percent'])
            elif brokerage_revenue_type in ['fixed', 'flat']:
                row['brokerage_revenue_percent'] = format_fixed_value(row['brokerage_revenue_percent'])
    return row

def get_all_agent_commissions(request):
    params = get_filter_params(request)
    query = build_base_query()
    # Apply date range filters
    filter_json = json.loads(params['filter_json'])
    query, filter_json = apply_date_filters(query, filter_json)
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

    # Format percentage values and add status fields in the response
    if data and 'data' in data and isinstance(data['data'], list):
        for row in data['data']:
            # ========== DEBUG: Use status from database (NOT calculated) ==========
            ac_id = row.get('id')
            status_in_db = row.get('status')  # Status from database
            revenue_recognized = row.get('revenue_recognized', 0) or 0
            revenue_realized = row.get('revenue_realized', 0) or 0
            
            print(f"\n{'='*60}")
            print(f"DEBUG AGENT_COMMISSION_LIST: Processing Agent Commission ID {ac_id}")
            print(f"{'='*60}")
            print(f"  - Status in Database: '{status_in_db}'")
            print(f"  - Revenue Recognized: {revenue_recognized}")
            print(f"  - Revenue Realized: {revenue_realized}")
            
            # IMPORTANT: Use status from database, NOT calculated status
            # Status should only change when payments are made via api/agent-commission-payments endpoint
            # Even if revenue_realized > 0, status remains "pending" until agent payment is made
            if status_in_db:
                # Normalize status to lowercase with underscores for format_commission_status_with_metadata
                # It expects: "pending", "partially_paid", "fully_paid"
                # Handle various formats: "PENDING", "Pending", "PARTIALLY PAID", "partially_paid", etc.
                status_normalized = str(status_in_db).lower().strip().replace(" ", "_")
                # Map common variations to expected format
                status_map = {
                    "pending": "pending",
                    "partially_paid": "partially_paid",
                    "partiallypaid": "partially_paid",
                    "fully_paid": "fully_paid",
                    "fullypaid": "fully_paid",
                }
                status_normalized = status_map.get(status_normalized, status_normalized)
                print(f"  - Using Database Status: '{status_in_db}' (normalized: '{status_normalized}')")
                print(f"  - ⚠️  IMPORTANT: Status from database is used, NOT calculated from revenue_realized")
                
                # Calculate what status WOULD be (for debugging only)
                calculated_status = calculate_agent_commission_status(
                    revenue_recognized,
                    revenue_realized
                )
                print(f"  - Calculated Status (for reference only): '{calculated_status}'")
                
                if status_normalized != calculated_status:
                    print(f"  - ⚠️  NOTE: Database status '{status_in_db}' differs from calculated '{calculated_status}'")
                    print(f"  - ⚠️  This is CORRECT - status only changes via agent-commission-payments endpoint")
                
                # Format status with metadata using database status
                status_metadata = format_commission_status_with_metadata(status_normalized, commission_type="agent")
                row['status'] = status_metadata.get('status')  # Use database status
                row['status_type'] = status_metadata.get('status_type')
                row['status_id'] = status_metadata.get('status_id')
                row['status_color'] = status_metadata.get('status_color')
                
                print(f"  - Status in Response: '{row['status']}' (from database)")
            else:
                # Fallback: if no status in DB, calculate it (shouldn't happen)
                print(f"  - ⚠️  WARNING: No status in database, calculating status")
                calculated_status = calculate_agent_commission_status(
                    revenue_recognized,
                    revenue_realized
                )
                status_metadata = format_commission_status_with_metadata(calculated_status, commission_type="agent")
                row['status'] = status_metadata.get('status')
            row['status_type'] = status_metadata.get('status_type')
            row['status_id'] = status_metadata.get('status_id')
            row['status_color'] = status_metadata.get('status_color')
            
            print(f"{'='*60}\n")
            
            # Format percentages
            row = format_commission_percentages(row)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def agent_commission_totals(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    params = get_filter_params(request)
    query = build_base_query()

    # Apply date range filters
    filter_json = json.loads(params['filter_json'])
    query, filter_json = apply_date_filters(query, filter_json)
    params['filter_json'] = json.dumps(filter_json)

    # Apply other conditions
    query = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    )
    
    totals = get_commission_totals(query)
    return ResponseService.response("SUCCESS", totals, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def agent_commission_detail(request, commission_id):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    commission = build_base_query().where("crmf_agent_commission.id", commission_id).first()

    if not commission:
        return ResponseService.response("NOT_FOUND", None, Error.DATA_NOT_FOUND)

    # ========== DEBUG: Use status from database (NOT calculated) ==========
    status_in_db = commission.get('status')  # Status from database
    revenue_recognized = commission.get('revenue_recognized', 0) or 0
    revenue_realized = commission.get('revenue_realized', 0) or 0
    
    print(f"\n{'='*60}")
    print(f"DEBUG AGENT_COMMISSION_DETAIL: Agent Commission ID {commission_id}")
    print(f"{'='*60}")
    print(f"  - Status in Database: '{status_in_db}'")
    print(f"  - Revenue Recognized: {revenue_recognized}")
    print(f"  - Revenue Realized: {revenue_realized}")
    
    # IMPORTANT: Use status from database, NOT calculated status
    # Status should only change when payments are made via api/agent-commission-payments endpoint
    if status_in_db:
        # Normalize status to lowercase for format_commission_status_with_metadata
        # It expects: "pending", "partially_paid", "fully_paid"
        status_normalized = status_in_db.lower().replace(" ", "_")
        print(f"  - Using Database Status: '{status_in_db}' (normalized: '{status_normalized}')")
        print(f"  - ⚠️  IMPORTANT: Status from database is used, NOT calculated from revenue_realized")
        
        # Calculate what status WOULD be (for debugging only)
        calculated_status = calculate_agent_commission_status(
            revenue_recognized,
            revenue_realized
        )
        print(f"  - Calculated Status (for reference only): '{calculated_status}'")
        
        if status_normalized != calculated_status:
            print(f"  - ⚠️  NOTE: Database status '{status_in_db}' differs from calculated '{calculated_status}'")
            print(f"  - ⚠️  This is CORRECT - status only changes via agent-commission-payments endpoint")
        
        # Format status with metadata using database status
        status_metadata = format_commission_status_with_metadata(status_normalized, commission_type="agent")
        commission['status'] = status_metadata.get('status')  # Use database status
        commission['status_type'] = status_metadata.get('status_type')
        commission['status_id'] = status_metadata.get('status_id')
        commission['status_color'] = status_metadata.get('status_color')
        
        print(f"  - Status in Response: '{commission['status']}' (from database)")
    else:
        # Fallback: if no status in DB, calculate it (shouldn't happen)
        print(f"  - ⚠️  WARNING: No status in database, calculating status")
        calculated_status = calculate_agent_commission_status(
            revenue_recognized,
            revenue_realized
        )
        status_metadata = format_commission_status_with_metadata(calculated_status, commission_type="agent")
        commission['status'] = status_metadata.get('status')
    commission['status_type'] = status_metadata.get('status_type')
    commission['status_id'] = status_metadata.get('status_id')
    commission['status_color'] = status_metadata.get('status_color')
    
    print(f"{'='*60}\n")

    # Format percentage values
    commission = format_commission_percentages(commission)

    return ResponseService.response("SUCCESS", commission, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def my_commission_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_my_commissions(request)

def get_my_commissions(request):
    params = get_filter_params(request)
    query = build_base_query()

    # Apply date range filters
    filter_json = json.loads(params['filter_json'])
    query, filter_json = apply_date_filters(query, filter_json)
    params['filter_json'] = json.dumps(filter_json)

    # Add user filter - only show commissions for the logged-in user
    query = query.where("crmf_agent_commission.agent_id", request.user.id)

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

    # Format percentage values and add status fields in the response
    if data and 'data' in data and isinstance(data['data'], list):
        for row in data['data']:
            # ========== DEBUG: Use status from database (NOT calculated) ==========
            ac_id = row.get('id')
            status_in_db = row.get('status')  # Status from database
            revenue_recognized = row.get('revenue_recognized', 0) or 0
            revenue_realized = row.get('revenue_realized', 0) or 0
            
            print(f"\n{'='*60}")
            print(f"DEBUG MY_COMMISSION_LIST: Processing Agent Commission ID {ac_id}")
            print(f"{'='*60}")
            print(f"  - Status in Database: '{status_in_db}'")
            print(f"  - Revenue Recognized: {revenue_recognized}")
            print(f"  - Revenue Realized: {revenue_realized}")
            
            # IMPORTANT: Use status from database, NOT calculated status
            # Status should only change when payments are made via api/agent-commission-payments endpoint
            # Even if revenue_realized > 0, status remains "pending" until agent payment is made
            if status_in_db:
                # Normalize status to lowercase with underscores for format_commission_status_with_metadata
                # It expects: "pending", "partially_paid", "fully_paid"
                # Handle various formats: "PENDING", "Pending", "PARTIALLY PAID", "partially_paid", etc.
                status_normalized = str(status_in_db).lower().strip().replace(" ", "_")
                # Map common variations to expected format
                status_map = {
                    "pending": "pending",
                    "partially_paid": "partially_paid",
                    "partiallypaid": "partially_paid",
                    "fully_paid": "fully_paid",
                    "fullypaid": "fully_paid",
                }
                status_normalized = status_map.get(status_normalized, status_normalized)
                print(f"  - Using Database Status: '{status_in_db}' (normalized: '{status_normalized}')")
                print(f"  - ⚠️  IMPORTANT: Status from database is used, NOT calculated from revenue_realized")
                
                # Calculate what status WOULD be (for debugging only)
                calculated_status = calculate_agent_commission_status(
                    revenue_recognized,
                    revenue_realized
                )
                print(f"  - Calculated Status (for reference only): '{calculated_status}'")
                
                if status_normalized != calculated_status:
                    print(f"  - ⚠️  NOTE: Database status '{status_in_db}' differs from calculated '{calculated_status}'")
                    print(f"  - ⚠️  This is CORRECT - status only changes via agent-commission-payments endpoint")
                
                # Format status with metadata using database status
                status_metadata = format_commission_status_with_metadata(status_normalized, commission_type="agent")
                row['status'] = status_metadata.get('status')  # Use database status
                row['status_type'] = status_metadata.get('status_type')
                row['status_id'] = status_metadata.get('status_id')
                row['status_color'] = status_metadata.get('status_color')
                
                print(f"  - Status in Response: '{row['status']}' (from database)")
            else:
                # Fallback: if no status in DB, calculate it (shouldn't happen)
                print(f"  - ⚠️  WARNING: No status in database, calculating status")
                calculated_status = calculate_agent_commission_status(
                    revenue_recognized,
                    revenue_realized
                )
                status_metadata = format_commission_status_with_metadata(calculated_status, commission_type="agent")
                row['status'] = status_metadata.get('status')
            row['status_type'] = status_metadata.get('status_type')
            row['status_id'] = status_metadata.get('status_id')
            row['status_color'] = status_metadata.get('status_color')
            
            print(f"{'='*60}\n")
            
            # Format percentages
            row = format_commission_percentages(row)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def my_commission_totals(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    params = get_filter_params(request)
    query = build_base_query()

    # Apply date range filters
    filter_json = json.loads(params['filter_json'])
    query, filter_json = apply_date_filters(query, filter_json)
    params['filter_json'] = json.dumps(filter_json)

    # Add user filter - only show commissions for the logged-in user
    query = query.where("crmf_agent_commission.agent_id", request.user.id)

    # Apply other conditions
    query = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    )
    
    totals = get_commission_totals(query)
    return ResponseService.response("SUCCESS", totals, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def my_commission_policy_stats(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    params = get_filter_params(request)
    query = build_base_query()

    # Add user filter - only show commissions for the logged-in user
    query = query.where("crmf_agent_commission.agent_id", request.user.id)

    # Apply conditions
    query = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    )
    
    stats = get_policy_stats(query)
    return ResponseService.response("SUCCESS", stats, Message.DATA_FETCHED) 

@csrf_exempt
@api_view(["POST"])
@parser_classes([JSONParser])
def multi_agent_commission_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    agent_ids = request.data.get("agent_ids", None)
    params = get_filter_params(request)
    # Also check request.data for status (in case it's sent in POST body)
    status_filter = params.get('status') or request.data.get("status", None)
    # Check for download parameter (from GET or POST)
    download_param = request.GET.get("download", None) or request.data.get("download", None)
    should_download = download_param in ['true', '1', True, 1, 'True']
    query = build_base_query()
    filter_json = json.loads(params['filter_json'])

    # Apply date filters first
    query, filter_json = apply_date_filters(query, filter_json)
    params['filter_json'] = json.dumps(filter_json)

    # Apply other filters
    query = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    )

    # Now apply the agent filter directly if agent_ids is provided and non-empty
    if agent_ids is not None and len(agent_ids) > 0:
        query = query.whereIn("agent.id", agent_ids)
    # else: do not add any filter for agent.id, so all agents are included

    # Get all records first (without pagination) to filter by is_payable
    # Then we'll paginate the filtered results manually
    all_data = query.get()
    
    # Format percentage values, add status fields, and calculate is_payable for all records
    payable_records = []
    if all_data and isinstance(all_data, list):
        for row in all_data:
            # ========== DEBUG: Use status from database (NOT calculated) ==========
            ac_id = row.get('id')
            status_in_db = row.get('status')  # Status from database
            revenue_recognized = row.get('revenue_recognized', 0) or 0
            revenue_realized = row.get('revenue_realized', 0) or 0
            
            print(f"\n{'='*60}")
            print(f"DEBUG MULTI_AGENT_COMMISSION_LIST: Processing Agent Commission ID {ac_id}")
            print(f"{'='*60}")
            print(f"  - Status in Database: '{status_in_db}'")
            print(f"  - Revenue Recognized: {revenue_recognized}")
            print(f"  - Revenue Realized: {revenue_realized}")
            
            # IMPORTANT: Use status from database, NOT calculated status
            # Status should only change when payments are made via api/agent-commission-payments endpoint
            # Even if revenue_realized > 0, status remains "pending" until agent payment is made
            if status_in_db:
                # Normalize status to lowercase with underscores for format_commission_status_with_metadata
                # It expects: "pending", "partially_paid", "fully_paid"
                # Handle various formats: "PENDING", "Pending", "PARTIALLY PAID", "partially_paid", etc.
                status_normalized = str(status_in_db).lower().strip().replace(" ", "_")
                # Map common variations to expected format
                status_map = {
                    "pending": "pending",
                    "partially_paid": "partially_paid",
                    "partiallypaid": "partially_paid",
                    "fully_paid": "fully_paid",
                    "fullypaid": "fully_paid",
                }
                status_normalized = status_map.get(status_normalized, status_normalized)
                print(f"  - Using Database Status: '{status_in_db}' (normalized: '{status_normalized}')")
                print(f"  - ⚠️  IMPORTANT: Status from database is used, NOT calculated from revenue_realized")
                
                # Calculate what status WOULD be (for debugging only)
                calculated_status = calculate_agent_commission_status(
                    revenue_recognized,
                    revenue_realized
                )
                print(f"  - Calculated Status (for reference only): '{calculated_status}'")
                
                if status_normalized != calculated_status:
                    print(f"  - ⚠️  NOTE: Database status '{status_in_db}' differs from calculated '{calculated_status}'")
                    print(f"  - ⚠️  This is CORRECT - status only changes via agent-commission-payments endpoint")
                
                # Format status with metadata using database status
                status_metadata = format_commission_status_with_metadata(status_normalized, commission_type="agent")
                row['status'] = status_metadata.get('status')  # Use database status
                row['status_type'] = status_metadata.get('status_type')
                row['status_id'] = status_metadata.get('status_id')
                row['status_color'] = status_metadata.get('status_color')
                
                print(f"  - Status in Response: '{row['status']}' (from database)")
            else:
                # Fallback: if no status in DB, calculate it (shouldn't happen)
                print(f"  - ⚠️  WARNING: No status in database, calculating status")
                calculated_status = calculate_agent_commission_status(
                    revenue_recognized,
                    revenue_realized
                )
                status_metadata = format_commission_status_with_metadata(calculated_status, commission_type="agent")
                row['status'] = status_metadata.get('status')
            row['status_type'] = status_metadata.get('status_type')
            row['status_id'] = status_metadata.get('status_id')
            row['status_color'] = status_metadata.get('status_color')
            
            print(f"{'='*60}\n")
            
            # Calculate is_payable parameter
            # is_payable = 0 if:
            #   1. Status is fully_paid, OR
            #   2. recognized_amount - deductible - paid_amount = 0
            # Otherwise, is_payable = 1
            from decimal import Decimal
            
            revenue_recognized_decimal = Decimal(str(revenue_recognized or 0))
            commission_deductible_decimal = Decimal(str(row.get('commission_deductible', 0) or 0))
            paid_amount_decimal = Decimal(str(row.get('paid_amount', 0) or 0))
            
            # Check if status is fully_paid
            status_normalized_for_payable = str(status_in_db or "").lower().strip().replace(" ", "_")
            status_map_for_payable = {
                "pending": "pending",
                "partially_paid": "partially_paid",
                "partiallypaid": "partially_paid",
                "fully_paid": "fully_paid",
                "fullypaid": "fully_paid",
            }
            status_normalized_for_payable = status_map_for_payable.get(status_normalized_for_payable, status_normalized_for_payable)
            is_fully_paid = (status_normalized_for_payable == "fully_paid")
            
            # Calculate available amount: realized_amount - deductible - paid_amount
            revenue_realized_decimal = Decimal(str(revenue_realized or 0))
            available_amount = revenue_realized_decimal - commission_deductible_decimal - paid_amount_decimal
            is_zero_available = (available_amount <= Decimal("0.00"))
            
            # Set is_payable: 0 if fully_paid OR available_amount is 0, otherwise 1
            is_payable = 0 if (is_fully_paid or is_zero_available) else 1
            
            row['is_payable'] = is_payable
            
            print(f"DEBUG is_payable calculation for Agent Commission ID {ac_id}:")
            print(f"  - Revenue Realized: {revenue_realized_decimal}")
            print(f"  - Commission Deductible: {commission_deductible_decimal}")
            print(f"  - Paid Amount: {paid_amount_decimal}")
            print(f"  - Available Amount: {available_amount} (realized - deductible - paid)")
            print(f"  - Status: '{status_normalized_for_payable}' (is_fully_paid: {is_fully_paid})")
            print(f"  - is_payable: {is_payable} (0 = not payable, 1 = payable)")
            
            # Format percentages
            row = format_commission_percentages(row)
            
            # If status filter is provided, include all records (skip is_payable filter)
            # If status filter is NOT provided, only include records where is_payable = 1
            if status_filter:
                # When filtering by status, include all records (will filter by status later)
                payable_records.append(row)
            else:
                # When no status filter, only include payable records
                if row.get('is_payable', 0) != 0:
                    payable_records.append(row)
    
    # Apply status filter if provided
    # Note: The status parameter should be the status_type value (e.g., "agent_comm_pending", "agent_comm_part_paid", "agent_comm_full_paid")
    if status_filter:
        # Normalize status filter (handle case variations)
        status_filter_normalized = str(status_filter).lower().strip()
        
        # Filter records by status_type
        # The status_type in row is set from format_commission_status_with_metadata
        # Expected values: "agent_comm_pending", "agent_comm_part_paid", "agent_comm_full_paid"
        filtered_by_status = []
        for row in payable_records:
            row_status_type = row.get('status_type', '')
            # Normalize row status_type for comparison
            row_status_type_normalized = str(row_status_type).lower().strip()
            
            # Match if status_type matches
            if row_status_type_normalized == status_filter_normalized:
                filtered_by_status.append(row)
        
        payable_records = filtered_by_status
    
    # Apply sorting to payable records (default: descending order)
    sort_by = params.get('sort_by', '')
    sort_dir = params.get('sort_dir', 'desc')
    # If sort_by is empty, use default sort by id in descending order
    if not sort_by or sort_by.strip() == '':
        sort_by = 'id'
    # Multi-agent commission list: always order in descending order (newest/latest first)
    sort_dir = 'desc'
    if sort_by:
        # Map DB column names to actual row keys (from get_columns() aliases)
        sort_column_to_row_key = {
            'id': 'id',
            'crmf_agent_commission.id': 'id',
            'core_entities.created_at': 'created_at',
        }
        sort_key = sort_column_to_row_key.get(sort_by) or sort_by
        reverse = sort_dir.lower() == 'desc'
        try:
            payable_records.sort(key=lambda x: x.get(sort_key), reverse=reverse)
        except Exception as e:
            print(f"DEBUG: Error sorting records: {e}")
    
    # Check if download is requested
    if should_download:
        try:
            # IMPORTANT: For PDF download, use ALL filtered records (no pagination)
            # payable_records contains all records that match:
            # - is_payable = 1 filter
            # - status filter (if provided)
            # - All other filters (search, date range, agent_ids, etc.)
            # No pagination is applied - all matching records are included in PDF
            all_filtered_records_for_pdf = payable_records.copy()  # Use all filtered records
            
            print(f"DEBUG: Generating PDF with {len(all_filtered_records_for_pdf)} total records (all filtered data, no pagination)")
            
            # Generate PDF with all filtered records (no pagination)
            pdf_service = PDFDownloadService()
            
            # Define columns for PDF export
            pdf_columns = [
                {'key': 'id', 'header': 'ID'},
                {'key': 'agent_name', 'header': 'Agent Name'},
                {'key': 'invoice_number', 'header': 'Invoice Number'},
                {'key': 'insurer_name', 'header': 'Insurer'},
                {'key': 'product_name', 'header': 'Product'},
                {'key': 'revenue_recognized', 'header': 'Revenue Recognized'},
                {'key': 'revenue_realized', 'header': 'Revenue Realized'},
                {'key': 'paid_amount', 'header': 'Paid Amount'},
                {'key': 'outstanding', 'header': 'Outstanding'},
                {'key': 'status', 'header': 'Status'},
                {'key': 'created_at', 'header': 'Created At'},
            ]
            
            # Generate filename with timestamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agent_commission_list_{timestamp}.pdf"
            
            # Generate PDF as bytes (use landscape for better table fit)
            # Use all_filtered_records_for_pdf which contains ALL matching records (no pagination)
            pdf_content = pdf_service.generate_pdf(
                data=all_filtered_records_for_pdf,  # All filtered records, not paginated
                columns=pdf_columns,
                title=f"Agent Commission List ({len(all_filtered_records_for_pdf)} records)",
                filename=filename,
                orientation='landscape',  # Use landscape for wide tables
                return_bytes=True
            )
            
            # Upload PDF to S3
            s3_data = S3PresignedService.upload_file_to_s3(
                file_content=pdf_content,
                file_name=filename,
                folder="exports/commissions"
            )
            
            # Generate CDN URL
            cdn_base_url = os.getenv("CDN_BASE_URL", "")
            download_link = f"{cdn_base_url}/{s3_data['file_key']}" if cdn_base_url else s3_data.get('file_url', '')
            
            # Return JSON response with PDF document info
            return ResponseService.response(
                "SUCCESS",
                {
                    "pdf_document": {
                        "download_link": download_link,
                        "file_key": s3_data['file_key'],
                        "file_name": s3_data['file_name']
                    }
                },
                Message.PDF_GENERATED
            )
            
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": str(e)},
                "Failed to generate PDF"
            )
    
    # Normal pagination response
    total_payable_records = len(payable_records)
    page = params['page']
    limit = params['limit']
    
    # Calculate pagination
    start_index = (page - 1) * limit
    end_index = start_index + limit
    paginated_data = payable_records[start_index:end_index]
    
    # Calculate last page
    last_page = (total_payable_records // limit) + (1 if total_payable_records % limit > 0 else 0) if limit > 0 else 1
    
    # Build response with correct pagination metadata
    data = {
        "total_records": total_payable_records,
        "per_page": limit,
        "current_page": page,
        "last_page": last_page,
        "data": paginated_data
    }
    
    print(f"DEBUG: Pagination - total_payable_records: {total_payable_records}, page: {page}, limit: {limit}, returning {len(paginated_data)} records")

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["POST"])
@parser_classes([JSONParser])
def multi_agent_commission_totals(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    agent_ids = request.data.get("agent_ids", None)
    params = get_filter_params(request)
    query = build_base_query()
    filter_json = json.loads(params['filter_json'])

    # Apply date filters first
    query, filter_json = apply_date_filters(query, filter_json)
    params['filter_json'] = json.dumps(filter_json)

    # Apply other filters
    query = query.apply_conditions(
        params['filter_json'],
        get_allowed_filters(),
        params['search_string'],
        get_search_columns()
    )

    # Now apply the agent filter directly if agent_ids is provided and non-empty
    if agent_ids is not None and len(agent_ids) > 0:
        query = query.whereIn("agent.id", agent_ids)
    # else: do not add any filter for agent.id, so all agents are included

    totals = get_commission_totals(query)
    
    # Calculate total deductibles and net revenue
    # Get total deductibles (SUM of commission_deductible)
    total_deductibles_query = query.select(
        "SUM(COALESCE(crmf_agent_commission.commission_deductible, 0)) as total_deductibles"
    ).first()
    
    total_deductibles = float(total_deductibles_query.get('total_deductibles', 0) or 0)
    gross_revenue = float(totals.get('total_commission_earned', 0) or 0)
    net_revenue = gross_revenue - total_deductibles
    
    # Add net revenue and total deductibles to totals
    totals['total_deductibles'] = total_deductibles
    totals['net_revenue'] = net_revenue
    
    return ResponseService.response("SUCCESS", totals, Message.DATA_FETCHED) 
