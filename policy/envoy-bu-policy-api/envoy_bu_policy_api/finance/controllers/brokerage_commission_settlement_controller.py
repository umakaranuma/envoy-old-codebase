from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from ..models.brokerage_commission_settlement import BrokerageCommissionSettlement
from ..models.crmf_brokerage_commission import BrokerageCommission
from envoy_bu_policy_api.service import handle_entity
from envoy_bu_policy_api.finance.controllers.utils.brokerage_commission_settlement_journal_utils import (
    create_brokerage_commission_settlement_journal_entries,
)
from envoy_bu_policy_api.finance.controllers.utils.general_ledger_utils import create_commission_general_ledger
from envoy_bu_policy_api.finance.controllers.utils.commission_status_utils import update_brokerage_commission_status
from datetime import datetime
from decimal import Decimal

def get_columns():
    return [
        "crmf_brokerage_commission_settlements.id",
        "crmf_brokerage_commission_settlements.settlement_amount",
        "crmf_brokerage_commission_settlements.settlement_date",
        "crmf_brokerage_commission_settlements.commission_type",
        "crmf_brokerage_commission_settlements.settlement_type",
        "crmf_brokerage_commission.id as commission_id",
        "crmf_brokerage_commission.revenue_recognized as gross_revenue",
        "crmf_brokerage_commission.commission_deductible as total_deductible",
        "crmf_brokerage_commission.revenue_realized as total_realized_commission",
        "(crmf_brokerage_commission.revenue_recognized - COALESCE(crmf_brokerage_commission.commission_deductible, 0)) as net_revenue",
        # Period information from policy
        "crmp_issued_policies.start_date as period_start",
        "crmp_issued_policies.end_date as period_end",
        # Processed date from invoice
        "crmf_invoices.invoice_date as processed_date",
        # Insurer information
        "core_service_providers.id as insurer_id",
        "core_service_providers.name as insurer_name",
        "core_service_providers.logo as insurer_logo",
        # "core_service_providers.code as insurer_code",
        # # Additional commission fields
        "crmf_brokerage_commission.revenue_recognized",
        "crmf_brokerage_commission.revenue_realized",
        "crmf_brokerage_commission.commission_deductible",
        # Invoice information
        "crmf_invoices.invoice_number",
        "crmf_invoices.invoice_amount",
        # Policy information
        "crmp_issued_policies.brokerage_policy_id",
        "crmp_issued_policies.premium_amount",
        "crmp_issued_policies.policy_effective_date",
        # Entity and audit fields
        "core_entities.created_at",
        "core_entities.updated_at",
        "created_by.display_name as created_by",
        "created_by.picture as created_by_logo",
        "updated_by.display_name as updated_by",
        "updated_by.picture as updated_by_logo"
    ]

def build_base_query():
    return (
        QueryBuilderService("crmf_brokerage_commission_settlements")
        .select(*get_columns())
        .leftJoin(
            "crmf_brokerage_commission",
            "crmf_brokerage_commission.id",
            "crmf_brokerage_commission_settlements.brokerage_commission_id"
        )
        .leftJoin(
            "crmf_invoices",
            "crmf_invoices.id",
            "crmf_brokerage_commission.invoice_id"
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id"
        )
        .leftJoin(
            "core_service_providers",
            "core_service_providers.id",
            "crmf_invoices.insurer_id"
        )
        .leftJoin("core_entities", "core_entities.id", "crmf_brokerage_commission_settlements.entity_id")
        .leftJoin("core_users as created_by", "created_by.id", "core_entities.created_by_id")
        .leftJoin("core_users as updated_by", "updated_by.id", "core_entities.updated_by_id")
    )

def get_filter_params(request):
    try:
        filter_json = json.loads(request.GET.get("filter", "{}"))
        
        # Add commission filter if provided
        commission_id = request.GET.get("commission_id", None)
        if commission_id:
            filter_json["crmf_brokerage_commission.id"] = {
                "o": "=",
                "v": commission_id
            }

        return {
            'filter_json': json.dumps(filter_json),
            'search_string': request.GET.get("search", ""),
            'page': int(request.GET.get("page", 1)),
            'limit': int(request.GET.get("limit", 10)),
            'sort_by': request.GET.get("sort_by", "core_entities.created_at"),
            'sort_dir': request.GET.get("sort_dir", "desc")
        }
    except Exception as e:
        return {
            'filter_json': "{}",
            'search_string': "",
            'page': 1,
            'limit': 10,
            'sort_by': "core_entities.created_at",
            'sort_dir': "desc"
        }

def get_allowed_filters():
    return [
        "crmf_brokerage_commission_settlements.id",
        "crmf_brokerage_commission_settlements.settlement_amount",
        "crmf_brokerage_commission_settlements.settlement_date",
        "crmf_brokerage_commission_settlements.commission_type",
        "crmf_brokerage_commission.id",
        "crmf_invoices.insurer_id",
        "crmp_issued_policies.start_date",
        "crmp_issued_policies.end_date",
        "crmf_invoices.invoice_date",
        "core_entities.created_at",
        "core_entities.updated_at"
    ]

def get_search_columns():
    return [
        "crmf_brokerage_commission_settlements.id",
        "crmf_brokerage_commission_settlements.settlement_amount",
        "crmf_invoices.invoice_number",
        "crmp_issued_policies.brokerage_policy_id",
        "core_service_providers.name"
    ]

def get_sort_columns():
    return [
        "crmf_brokerage_commission_settlements.id",
        "crmf_brokerage_commission_settlements.settlement_amount",
        "crmf_brokerage_commission_settlements.settlement_date",
        "crmf_brokerage_commission_settlements.commission_type",
        "crmf_brokerage_commission.id",
        "crmf_invoices.invoice_date",
        "crmp_issued_policies.start_date",
        "crmp_issued_policies.end_date",
        "core_service_providers.name",
        "core_entities.created_at",
        "core_entities.updated_at"
    ]

@csrf_exempt
@api_view(["GET", "POST"])
def brokerage_commission_settlement_list(request):
    try:
        action_type = "VIEW" if request.method == "GET" else "CREATE"
        action = ActionService.getAction("BrokerageCommissionSettlement", action_type)

        # If no action is configured, skip authority check (same pattern as other controllers)
        if action and not AuthService.hasAuthority(request, action):
            return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

        if request.method == "GET":
            params = get_filter_params(request)
            query = build_base_query()

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

            return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
        else:
            return create_brokerage_commission_settlement(request)
    except Exception as e:
        return ResponseService.response("ERROR", str(e), Error.NOT_FOUND)

@csrf_exempt
@api_view(["GET"])
def commission_settlements(request, commission_id):
    try:
        action_type = "VIEW"
        action = ActionService.getAction("BrokerageCommissionSettlement", action_type)

        if action and not AuthService.hasAuthority(request, action):
            return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

        params = get_filter_params(request)
        query = build_base_query().where("crmf_brokerage_commission.id", commission_id)

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

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
    except Exception as e:
        return ResponseService.response("ERROR", str(e), Error.NOT_FOUND)

@csrf_exempt
@api_view(["GET"])
def brokerage_commission_settlement_detail(request, settlement_id):
    try:
        action_type = "VIEW"
        action = ActionService.getAction("BrokerageCommissionSettlement", action_type)

        if action and not AuthService.hasAuthority(request, action):
            return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

        settlement = build_base_query().where("crmf_brokerage_commission_settlements.id", settlement_id).first()

        if not settlement:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

        return ResponseService.response("SUCCESS", settlement, Message.DATA_FETCHED)
    except Exception as e:
        return ResponseService.response("ERROR", str(e), Error.NOT_FOUND)

@csrf_exempt
@api_view(["GET"])
def get_commission_outstanding(request, commission_id):
    action_type = "VIEW"
    action = ActionService.getAction("BrokerageCommissionSettlement", action_type)

    if action and not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    summary = BrokerageCommissionSettlement.get_commission_settlement_summary(commission_id)
    return ResponseService.response("SUCCESS", summary, Message.DATA_FETCHED)

def create_brokerage_commission_settlement(request):
    try:
        data = json.loads(request.body)
        commission_ids = data.get('commission_ids', [])
        if not isinstance(commission_ids, list):
            commission_ids = [commission_ids]

        # Validation rules
        rules = {
            "commission_ids": "required|array"
        }

        # Validate input data
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

        if not commission_ids:
            return ResponseService.response("VALIDATION_ERROR", {"commission_ids": ["No commission IDs provided"]}, Error.VALIDATION_ERROR)

        created_settlements = []
        for commission_id in commission_ids:
            # Get the commission
            try:
                commission = BrokerageCommission.objects.get(id=commission_id)
            except BrokerageCommission.DoesNotExist:
                return ResponseService.response("NOT_FOUND", f"Commission {commission_id} not found", Error.NOT_FOUND)

            # Check if commission status is "completed" - if so, it's already settled
            commission_status = str(getattr(commission, 'status', '') or '').lower().strip()
            if commission_status == 'completed':
                return ResponseService.response("VALIDATION_ERROR", {
                    "commission_ids": [f"Commission {commission_id} is already settled"]
                }, "This commission is already settled")

            # Get total settled so far for this commission
            summary = BrokerageCommissionSettlement.get_commission_settlement_summary(commission_id)
            total_settled = summary.get('total_settled', 0) if summary else 0
            print(f"DEBUG: Total settled so far: {total_settled}, Summary: {summary}")
            print(f"DEBUG: Commission revenue_realized: {commission.revenue_realized}")
            print(f"DEBUG: Commission revenue_recognized: {commission.revenue_recognized}")
            
            # Calculate outstanding amount: revenue_recognized - revenue_realized - commission_deductible
            commission_deductible = Decimal(str(getattr(commission, 'commission_deductible', 0) or 0))
            revenue_realized = Decimal(str(commission.revenue_realized or "0.00"))
            revenue_recognized = Decimal(str(commission.revenue_recognized or "0.00"))
            total_settled_decimal = Decimal(str(total_settled or "0.00"))
            
            # Calculate outstanding amount
            outstanding = revenue_recognized - revenue_realized - commission_deductible
            
            # If outstanding is negative, store the absolute value as settlement_amount
            # Otherwise, calculate settlement amount normally: revenue_realized - deductible - already settled
            if outstanding < 0:
                # Outstanding is negative - store the absolute value (positive)
                settlement_amount = abs(outstanding)
                print(f"DEBUG: Outstanding is negative ({outstanding}), storing absolute value as settlement_amount: {settlement_amount}")
            else:
                # Normal settlement: revenue_realized - deductible - already settled
                settlement_amount = revenue_realized - commission_deductible - total_settled_decimal
                # Ensure we don't settle negative amounts for normal settlements
                settlement_amount = max(Decimal("0.00"), settlement_amount)
            
            print(f"DEBUG: Settlement Calculation for Commission ID {commission_id}:")
            print(f"  - Revenue Recognized: {revenue_recognized}")
            print(f"  - Revenue Realized: {revenue_realized}")
            print(f"  - Commission Deductible: {commission_deductible}")
            print(f"  - Outstanding = {revenue_recognized} - {revenue_realized} - {commission_deductible} = {outstanding}")
            print(f"  - Total Settled (already settled): {total_settled_decimal}")
            print(f"  - Settlement Amount: {settlement_amount}")
            
            # Only skip if outstanding is not negative AND settlement_amount is 0 or less
            if outstanding >= 0 and settlement_amount <= 0:
                print(f"DEBUG: Skipping commission {commission_id} - no amount available to settle")
                print(f"  (revenue_realized: {revenue_realized}, deductible: {commission_deductible}, already_settled: {total_settled_decimal})")
                continue

            # Create entity for settlement
            entity_data = {
                "type": "brokerage_commission_settlement",
                "approvel_status": False,
                "description": f"Settlement for commission {commission_id}"
            }
            entity_id = handle_entity(entity_data, user=request.user if hasattr(request, 'user') else None)
            if not entity_id:
                return ResponseService.response("ERROR", "Failed to create entity", Error.NOT_FOUND)

            # Determine settlement type based on outstanding amount
            settlement_type_value = 'physical_credit_note' if outstanding < 0 else 'settlement'

            # Create settlement record using QueryBuilderService
            # Store settlement_date as datetime to capture accurate time
            settlement_data = {
                'brokerage_commission_id': commission.id,
                'settlement_amount': str(settlement_amount),  # Settle only the realized amount available
                'entity_id': entity_id,
                'settlement_date': datetime.now(),  # Store as datetime with accurate time
                'settlement_type': settlement_type_value,
                'commission_type': 'BROKERAGE_COMMISSION',
            }
            print(f"DEBUG: Settlement data: {settlement_data}")
            # Insert settlement record
            result = QueryBuilderService("crmf_brokerage_commission_settlements").insert(settlement_data)
            if not result:
                return ResponseService.response("ERROR", "Failed to create settlement record", Error.NOT_FOUND)

            # Get the settlement ID from result
            settlement_id = None
            if isinstance(result, dict):
                settlement_id = result.get('id')
            elif isinstance(result, (int, str)):
                settlement_id = result
            
            if not settlement_id:
                return ResponseService.response("ERROR", "Failed to get settlement ID", Error.NOT_FOUND)

            # Get created settlement using QueryBuilder
            settlement = QueryBuilderService("crmf_brokerage_commission_settlements").where("id", settlement_id).first()
            if not settlement:
                return ResponseService.response("ERROR", "Failed to retrieve created settlement", Error.NOT_FOUND)

            # Update commission status based on settlement
            # If outstanding was negative, set status to "completed"
            if outstanding < 0:
                QueryBuilderService("crmf_brokerage_commission").where("id", commission.id).update({"status": "completed"})
            else:
                update_brokerage_commission_status(commission.id)
            
            # Create journal entries for commission settlement
            create_brokerage_commission_settlement_journal_entries(settlement, user=request.user)
            
            # Create general ledger entry
            create_commission_general_ledger(
                commission_data=commission.__dict__,
                commission_type="brokerage",
                user=request.user
            )

            # Get settlement summary
            try:
                summary = BrokerageCommissionSettlement.get_commission_settlement_summary(commission_id)
            except Exception as e:
                # Calculate outstanding: revenue_recognized - revenue_realized - deductible (if negative, return 0)
                commission_deductible = float(getattr(commission, 'commission_deductible', 0) or 0)
                outstanding_calc = max(0, float(commission.revenue_recognized) - float(commission.revenue_realized) - commission_deductible)
                summary = {
                    'commission_id': commission_id,
                    'revenue_recognized': float(commission.revenue_recognized),
                    'revenue_realized': float(commission.revenue_realized),
                    'commission_deductible': commission_deductible,
                    'total_settled': float(settlement_amount),  # Use settlement_amount instead of outstanding
                    'outstanding': outstanding_calc,
                    'settlement_count': 1
                }

            created_settlements.append({
                'settlement': settlement,
                'summary': summary
            })

        return ResponseService.response("SUCCESS", {
            'created_settlements': created_settlements
        }, Message.DATA_CREATED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), Error.NOT_FOUND)


