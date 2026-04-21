from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from ..models.agent_commission_payment import AgentCommissionPayment
from ..models.crmf_agent_commission import AgentCommission
from envoy_bu_policy_api.service import handle_entity
from envoy_bu_policy_api.finance.controllers.utils.agent_commission_payment_journal_utils import (
    create_agent_commission_payment_journal_entries,
)
from envoy_bu_policy_api.finance.controllers.utils.general_ledger_utils import create_commission_general_ledger
from envoy_bu_policy_api.finance.controllers.utils.commission_status_utils import update_agent_commission_status
from datetime import datetime
from decimal import Decimal

def get_columns():
    return [
        "crmf_agent_commission_payments.id",
        "crmf_agent_commission_payments.payment_amount",
        # payment_date is now DateTimeField, so it returns datetime format directly
        "crmf_agent_commission_payments.payment_date",
        "crmf_agent_commission.id as commission_id",
        "crmf_agent_commission.agent_id",
        "crmf_agent_commission.revenue_recognized",
        "crmf_agent_commission.revenue_realized",
        "agent.display_name as agent_name",
        "agent.picture as agent_picture",
        "core_entities.created_at",
        "core_entities.updated_at",
        "created_by.display_name as created_by",
        "created_by.picture as created_by_logo",
        "updated_by.display_name as updated_by",
        "updated_by.picture as updated_by_logo"
    ]

def build_base_query():
    return (
        QueryBuilderService("crmf_agent_commission_payments")
        .select(*get_columns())
        .leftJoin(
            "crmf_agent_commission",
            "crmf_agent_commission.id",
            "crmf_agent_commission_payments.agent_commission_id"
        )
        .leftJoin("core_users as agent", "agent.id", "crmf_agent_commission.agent_id")
        .leftJoin("core_entities", "core_entities.id", "crmf_agent_commission_payments.entity_id")
        .leftJoin("core_users as created_by", "created_by.id", "core_entities.created_by_id")
        .leftJoin("core_users as updated_by", "updated_by.id", "core_entities.updated_by_id")
    )

def get_filter_params(request):
    try:
        filter_json = json.loads(request.GET.get("filter", "{}"))
        
        # Add commission filter if provided
        commission_id = request.GET.get("commission_id", None)
        if commission_id:
            filter_json["crmf_agent_commission.id"] = {
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
        "crmf_agent_commission_payments.id",
        "crmf_agent_commission_payments.payment_amount",
        "crmf_agent_commission.id",
        "crmf_agent_commission.agent_id",
        "core_entities.created_at",
        "core_entities.updated_at"
    ]

def get_search_columns():
    return [
        "crmf_agent_commission_payments.id",
        "crmf_agent_commission_payments.payment_amount",
        "agent.display_name"
    ]

def get_sort_columns():
    return [
        "crmf_agent_commission_payments.id",
        "crmf_agent_commission_payments.payment_amount",
        "crmf_agent_commission.id",
        "crmf_agent_commission.agent_id",
        "core_entities.created_at",
        "core_entities.updated_at"
    ]

@csrf_exempt
@api_view(["GET", "POST"])
def agent_commission_payment_list(request):
    try:
        action_type = "VIEW" if request.method == "GET" else "CREATE"
        action = ActionService.getAction("AgentCommissionPayment", action_type)

        if not AuthService.hasAuthority(request, action):
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
            return create_agent_commission_payment(request)
    except Exception as e:
        return ResponseService.response("ERROR", str(e), Error.NOT_FOUND)

@csrf_exempt
@api_view(["GET"])
def commission_payments(request, commission_id):
    try:
        action_type = "VIEW"
        action = ActionService.getAction("AgentCommissionPayment", action_type)

        if not AuthService.hasAuthority(request, action):
            return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

        params = get_filter_params(request)
        query = build_base_query().where("crmf_agent_commission.id", commission_id)

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
def agent_commission_payment_detail(request, payment_id):
    try:
        action_type = "VIEW"
        action = ActionService.getAction("AgentCommissionPayment", action_type)

        if not AuthService.hasAuthority(request, action):
            return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

        payment = build_base_query().where("crmf_agent_commission_payments.id", payment_id).first()

        if not payment:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

        return ResponseService.response("SUCCESS", payment, Message.DATA_FETCHED)
    except Exception as e:
        return ResponseService.response("ERROR", str(e), Error.NOT_FOUND)

@csrf_exempt
@api_view(["GET"])
def get_commission_outstanding(request, commission_id):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommissionPayment", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    summary = AgentCommissionPayment.get_commission_payment_summary(commission_id)
    return ResponseService.response("SUCCESS", summary, Message.DATA_FETCHED)

def create_agent_commission_payment(request):
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

        created_payments = []
        for commission_id in commission_ids:
            # Get the commission
            try:
                commission = AgentCommission.objects.get(id=commission_id)
            except AgentCommission.DoesNotExist:
                return ResponseService.response("NOT_FOUND", f"Commission {commission_id} not found", Error.NOT_FOUND)

            # Get total paid so far for this commission
            summary = AgentCommissionPayment.get_commission_payment_summary(commission_id)
            total_paid = summary.get('total_paid', 0) if summary else 0
            print(f"DEBUG: Total paid so far: {total_paid}, Summary: {summary}")
            print(f"DEBUG: Commission revenue_realized: {commission.revenue_realized}")
            print(f"DEBUG: Commission revenue_recognized: {commission.revenue_recognized}")
            
            # Calculate payment amount: revenue_realized - commission_deductible - total_paid
            # This is the amount available to pay to the agent
            commission_deductible = Decimal(str(getattr(commission, 'commission_deductible', 0) or 0))
            revenue_realized = Decimal(str(commission.revenue_realized or "0.00"))
            total_paid_decimal = Decimal(str(total_paid or "0.00"))
            
            # Payment amount = revenue_realized - deductible - already paid
            payment_amount = revenue_realized - commission_deductible - total_paid_decimal
            
            # Ensure we don't pay negative amounts
            payment_amount = max(Decimal("0.00"), payment_amount)
            
            print(f"DEBUG: Payment Calculation for Commission ID {commission_id}:")
            print(f"  - Revenue Realized (from customer payments): {revenue_realized}")
            print(f"  - Commission Deductible: {commission_deductible}")
            print(f"  - Total Paid (already paid to agent): {total_paid_decimal}")
            print(f"  - Payment Amount = {revenue_realized} - {commission_deductible} - {total_paid_decimal} = {payment_amount}")
            
            if payment_amount <= 0:
                print(f"DEBUG: Skipping commission {commission_id} - no amount available to pay")
                print(f"  (revenue_realized: {revenue_realized}, deductible: {commission_deductible}, already_paid: {total_paid_decimal})")
                continue

            # Create entity for payment
            entity_data = {
                "type": "agent_commission_payment",
                "approvel_status": False,
                "description": f"Payment for commission {commission_id}"
            }
            entity_id = handle_entity(entity_data, user=request.user if hasattr(request, 'user') else None)
            if not entity_id:
                return ResponseService.response("ERROR", "Failed to create entity", Error.NOT_FOUND)

            # Create payment record using QueryBuilderService
            # Store payment_date as datetime to capture accurate time
            payment_data = {
                'agent_commission_id': commission.id,
                'payment_amount': str(payment_amount),  # Pay only the realized amount available
                'entity_id': entity_id,
                'payment_date': datetime.now(),  # Store as datetime with accurate time
                'payment_type': 'commission'  # Added required field
            }
            print(f"DEBUG: Payment data: {payment_data}")
            # Insert payment record
            result = QueryBuilderService("crmf_agent_commission_payments").insert(payment_data)
            if not result:
                return ResponseService.response("ERROR", "Failed to create payment record", Error.NOT_FOUND)

            # Get the payment ID from result
            payment_id = None
            if isinstance(result, dict):
                payment_id = result.get('id')
            elif isinstance(result, (int, str)):
                payment_id = result
            
            if not payment_id:
                return ResponseService.response("ERROR", "Failed to get payment ID", Error.NOT_FOUND)

            # Get created payment using QueryBuilder
            payment = QueryBuilderService("crmf_agent_commission_payments").where("id", payment_id).first()
            if not payment:
                return ResponseService.response("ERROR", "Failed to retrieve created payment", Error.NOT_FOUND)

            # Create unified commission settlement record for agent commission history
            try:
                settlement_data = {
                    'commission_type': 'AGENT_COMMISSION',
                    'agent_commission_id': commission.id,
                    'settlement_amount': str(payment_amount),
                    'entity_id': entity_id,
                    'settlement_date': datetime.now(),
                    'settlement_type': 'settlement',
                }
                QueryBuilderService("crmf_brokerage_commission_settlements").insert(settlement_data)
            except Exception as e:
                # Do not fail the payment flow if settlement history insert fails
                print(f"WARNING: Failed to create agent commission settlement history record: {str(e)}")

            # Update paid_amount in agent commission record
            # Note: revenue_realized should NOT be updated here - it's already set from customer payments
            # We only update paid_amount to track how much has been paid to the agent
            # Use total_paid from payment summary (sum of all payments) instead of commission.paid_amount
            # to ensure consistency
            new_paid = total_paid_decimal + payment_amount
            
            print(f"DEBUG: Update paid_amount for Commission ID {commission.id}:")
            print(f"  - Total Paid (from payment summary): {total_paid_decimal}")
            print(f"  - Current Payment Amount: {payment_amount}")
            print(f"  - New Total Paid Amount: {new_paid}")
            print(f"  - Revenue realized (from customer payments): {revenue_realized}")
            print(f"  - Revenue recognized (total commission): {commission.revenue_recognized}")
            print(f"  - Commission paid_amount in DB (before update): {commission.paid_amount}")
            
            # IMPORTANT: Only update paid_amount, NOT revenue_realized
            # revenue_realized is updated when customer payments are made (via api/payments)
            # paid_amount tracks how much of the realized amount has been paid to the agent
            # We use total_paid + payment_amount to ensure consistency with payment records
            update_result = QueryBuilderService("crmf_agent_commission").where("id", commission.id).update({
                "paid_amount": str(new_paid)
                # DO NOT update revenue_realized here - it's already correct from customer payments
            })
            print(f"  - Update result: {update_result}")
            
            # Verify the update
            updated_commission = QueryBuilderService("crmf_agent_commission").where("id", commission.id).first()
            if updated_commission:
                print(f"  - Verified paid_amount after update: {updated_commission.get('paid_amount')}")
            
            # Update commission status based on payment
            update_agent_commission_status(commission.id)
            
            # Create journal entries for commission payment
            create_agent_commission_payment_journal_entries(payment, user=request.user)
            
            # Create general ledger entry
            create_commission_general_ledger(
                commission_data=commission.__dict__,
                commission_type="agent",
                user=request.user
            )

            # Get payment summary
            try:
                summary = AgentCommissionPayment.get_commission_payment_summary(commission_id)
            except Exception as e:
                # Calculate outstanding: revenue_recognized - revenue_realized - deductible (if negative, return 0)
                commission_deductible = float(getattr(commission, 'commission_deductible', 0) or 0)
                outstanding_calc = max(0, float(commission.revenue_recognized) - float(commission.revenue_realized) - commission_deductible)
                summary = {
                    'commission_id': commission_id,
                    'revenue_recognized': float(commission.revenue_recognized),
                    'revenue_realized': float(commission.revenue_realized),
                    'commission_deductible': commission_deductible,
                    'total_paid': float(payment_amount),  # Use payment_amount instead of outstanding
                    'outstanding': outstanding_calc,
                    'payment_count': 1
                }

            created_payments.append({
                'payment': payment,
                'summary': summary
            })

        return ResponseService.response("SUCCESS", {
            'created_payments': created_payments
        }, Message.DATA_CREATED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), Error.NOT_FOUND)

@csrf_exempt
@api_view(["POST"])
def create_single_agent_commission_payment(request, commission_id):
    """
    Create a payment for a specific commission with a specified pay_amount
    POST /api/agent-commission-payments/{commission_id}
    Payload: {"pay_amount": 100.00}
    """
    try:
        # Authorization check (optional - only if action exists in database)
        action_type = "CREATE"
        action = ActionService.getAction("AgentCommissionPayment", action_type)
        if action and not AuthService.hasAuthority(request, action):
            return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

        try:
            data = json.loads(request.body or "{}")
        except json.JSONDecodeError:
            return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON data"}, Error.VALIDATION_ERROR)

        pay_amount = data.get('pay_amount')
        payment_date_str = data.get('payment_date') or data.get('paid_date')

        # Validation rules - numeric accepts both string and numeric values
        rules = {
            "pay_amount": "required|numeric|gt:0"
        }

        # Collect all validation errors in ValidatorService format
        validation_errors = {}
        
        # Validate input data using ValidatorService
        errors = ValidatorService.validate(data, rules)
        if errors:
            validation_errors.update(errors)

        # Convert pay_amount to Decimal (handles both string and numeric)
        pay_amount_decimal = None
        if pay_amount is not None:
            try:
                pay_amount_decimal = Decimal(str(pay_amount))
            except (ValueError, TypeError):
                if "pay_amount" not in validation_errors:
                    validation_errors["pay_amount"] = []
                ValidatorService._add_error(validation_errors, "pay_amount", "invalid", {
                    "_attribute": "pay_amount",
                    "value": str(pay_amount)
                })
        elif "pay_amount" not in validation_errors:
            # This case is already handled by ValidatorService required rule, but ensure we have it
            pass

        # Parse payment_date if provided, otherwise use current datetime
        payment_date = None
        if payment_date_str:
            try:
                # Try parsing different date formats
                if 'T' in payment_date_str:
                    # ISO format with T separator (e.g., 2024-01-15T10:30:00 or 2024-01-15T10:30:00Z)
                    date_str = payment_date_str.replace('Z', '').split('T')[0]
                    time_str = payment_date_str.split('T')[1].replace('Z', '').split('.')[0]  # Remove microseconds and Z
                    if len(time_str) == 5:  # HH:MM format
                        payment_date = datetime.strptime(f"{date_str} {time_str}:00", "%Y-%m-%d %H:%M:%S")
                    else:  # HH:MM:SS format
                        payment_date = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                elif ' ' in payment_date_str:
                    # Format: YYYY-MM-DD HH:MM:SS or YYYY-MM-DD HH:MM
                    if len(payment_date_str.split(' ')[1]) == 5:  # HH:MM format
                        payment_date = datetime.strptime(f"{payment_date_str}:00", "%Y-%m-%d %H:%M:%S")
                    else:
                        payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d %H:%M:%S")
                else:
                    # Format: YYYY-MM-DD (set time to current time)
                    payment_date = datetime.strptime(payment_date_str, "%Y-%m-%d")
                    # Keep the date but use current time
                    now = datetime.now()
                    payment_date = payment_date.replace(hour=now.hour, minute=now.minute, second=now.second, microsecond=now.microsecond)
            except (ValueError, TypeError) as e:
                if "payment_date" not in validation_errors:
                    validation_errors["payment_date"] = []
                ValidatorService._add_error(validation_errors, "payment_date", "invalid", {
                    "_attribute": "payment_date",
                    "value": payment_date_str
                })
        else:
            # Use current datetime if not provided
            payment_date = datetime.now()

        # Return validation errors if any found so far
        if validation_errors:
            return ResponseService.response("VALIDATION_ERROR", validation_errors, Error.VALIDATION_ERROR)

        # Get the commission
        try:
            commission = AgentCommission.objects.get(id=commission_id)
        except AgentCommission.DoesNotExist:
            return ResponseService.response("NOT_FOUND", f"Commission {commission_id} not found", Error.NOT_FOUND)

        # Get total paid so far for this commission
        summary = AgentCommissionPayment.get_commission_payment_summary(commission_id)
        total_paid = summary.get('total_paid', 0) if summary else 0

        # Calculate available amount: revenue_realized - commission_deductible - total_paid
        commission_deductible = Decimal(str(getattr(commission, 'commission_deductible', 0) or 0))
        revenue_realized = Decimal(str(commission.revenue_realized or "0.00"))
        total_paid_decimal = Decimal(str(total_paid or "0.00"))

        # Available amount = revenue_realized - deductible - already paid
        available_amount = revenue_realized - commission_deductible - total_paid_decimal
        available_amount = max(Decimal("0.00"), available_amount)

        # Validate that pay_amount doesn't exceed available amount (only if we have a valid pay_amount_decimal)
        if pay_amount_decimal is not None:
            if pay_amount_decimal <= 0:
                if "pay_amount" not in validation_errors:
                    validation_errors["pay_amount"] = []
                ValidatorService._add_error(validation_errors, "pay_amount", "gt_numeric", {
                    "_attribute": "pay_amount",
                    "value": "0"
                })
            elif pay_amount_decimal > available_amount:
                if "pay_amount" not in validation_errors:
                    validation_errors["pay_amount"] = []
                ValidatorService._add_error(validation_errors, "pay_amount", "max_numeric", {
                    "_attribute": "pay_amount",
                    "value": str(available_amount),
                    "max": str(available_amount)
                })

        # Return all validation errors if any found
        if validation_errors:
            return ResponseService.response("VALIDATION_ERROR", validation_errors, Error.VALIDATION_ERROR)

        # At this point, all validations passed, so pay_amount_decimal should be set
        if pay_amount_decimal is None:
            return ResponseService.response("VALIDATION_ERROR", {
                "pay_amount": [{"error_type": "required", "tokens": {"_attribute": "pay_amount"}}]
            }, Error.VALIDATION_ERROR)

        # Create entity for payment
        entity_data = {
            "type": "agent_commission_payment",
            "approvel_status": False,
            "description": f"Payment for commission {commission_id}"
        }
        entity_id = handle_entity(entity_data, user=request.user if hasattr(request, 'user') else None)
        if not entity_id:
            return ResponseService.response("ERROR", "Failed to create entity", Error.NOT_FOUND)

        # Create payment record using QueryBuilderService
        payment_data = {
            'agent_commission_id': commission.id,
            'payment_amount': str(pay_amount_decimal),
            'entity_id': entity_id,
            'payment_date': payment_date,
            'payment_type': 'commission'
        }

        # Insert payment record
        result = QueryBuilderService("crmf_agent_commission_payments").insert(payment_data)
        if not result:
            return ResponseService.response("ERROR", "Failed to create payment record", Error.NOT_FOUND)

        # Get the payment ID from result
        payment_id = None
        if isinstance(result, dict):
            payment_id = result.get('id')
        elif isinstance(result, (int, str)):
            payment_id = result

        if not payment_id:
            return ResponseService.response("ERROR", "Failed to get payment ID", Error.NOT_FOUND)

        # Get created payment using QueryBuilder
        payment = QueryBuilderService("crmf_agent_commission_payments").where("id", payment_id).first()
        if not payment:
            return ResponseService.response("ERROR", "Failed to retrieve created payment", Error.NOT_FOUND)

        # Create unified commission settlement record for agent commission history
        try:
            settlement_data = {
                'commission_type': 'AGENT_COMMISSION',
                'agent_commission_id': commission.id,
                'settlement_amount': str(pay_amount_decimal),
                'entity_id': entity_id,
                'settlement_date': payment_date,
                'settlement_type': 'settlement',
            }
            QueryBuilderService("crmf_brokerage_commission_settlements").insert(settlement_data)
        except Exception as e:
            # Do not fail the payment flow if settlement history insert fails
            print(f"WARNING: Failed to create agent commission settlement history record: {str(e)}")

        # Update paid_amount in agent commission record
        new_paid = total_paid_decimal + pay_amount_decimal
        update_result = QueryBuilderService("crmf_agent_commission").where("id", commission.id).update({
            "paid_amount": str(new_paid)
        })

        # Verify the update
        updated_commission = QueryBuilderService("crmf_agent_commission").where("id", commission.id).first()

        # Update commission status based on payment
        update_agent_commission_status(commission.id)

        # Create journal entries for commission payment
        user = request.user if hasattr(request, 'user') and request.user.is_authenticated else None
        create_agent_commission_payment_journal_entries(payment, user=user)

        # Create general ledger entry
        create_commission_general_ledger(
            commission_data=commission.__dict__,
            commission_type="agent",
            user=user
        )

        # Get payment summary
        try:
            summary = AgentCommissionPayment.get_commission_payment_summary(commission_id)
        except Exception as e:
            # Calculate outstanding: revenue_recognized - revenue_realized - deductible (if negative, return 0)
            commission_deductible = float(getattr(commission, 'commission_deductible', 0) or 0)
            outstanding_calc = max(0, float(commission.revenue_recognized) - float(commission.revenue_realized) - commission_deductible)
            summary = {
                'commission_id': commission_id,
                'revenue_recognized': float(commission.revenue_recognized),
                'revenue_realized': float(commission.revenue_realized),
                'commission_deductible': commission_deductible,
                'total_paid': float(pay_amount_decimal),
                'outstanding': outstanding_calc,
                'payment_count': 1
            }

        return ResponseService.response("SUCCESS", {
            'payment': payment,
            'summary': summary
        }, Message.DATA_CREATED)

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"ERROR in create_single_agent_commission_payment: {str(e)}")
        print(f"Traceback: {error_trace}")
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), Error.NOT_FOUND)

