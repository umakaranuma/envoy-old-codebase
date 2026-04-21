from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_policy_api.service import  _format_date_fields
import json
from envoy_bu_policy_api.finance.controllers.utils.general_ledger_utils import (
    create_general_ledger_entry,

)

@csrf_exempt
@api_view(["GET", "POST"])
def general_ledger_list(request):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("GeneralLedger", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_entries(request)

    return create_entry(request)

@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def general_ledger_detail(request, entry_id):
    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("GeneralLedger", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_entries(request, entry_id=entry_id)
    elif request.method == "PUT":
        return update_entry(request, entry_id)
    elif request.method == "DELETE":
        return delete_entry(entry_id)

@csrf_exempt
@api_view(["GET"])
def get_all_entries(request):
    """Get all general ledger entries with filtering and pagination"""
    action_type = "VIEW"
    action = ActionService.getAction("GeneralLedger", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    try:
        columns = [
            "crmf_general_ledger.*",
            "core_entities.created_at as created_at",
            "core_users.display_name as created_by",
            "core_users.picture as created_by_logo",
            "core_entities.updated_at as updated_at",
            "up_users.display_name as updated_by",
            "up_users.picture as updated_by_logo",
            "insurer.name as insurer_name",
            "insurer.logo as insurer_logo"
        ]

        query = (
            QueryBuilderService("crmf_general_ledger")
            .select(*columns)
            .leftJoin("core_entities", "core_entities.id", "crmf_general_ledger.entity_id")
            .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
            .leftJoin("core_users as up_users", "up_users.id", "core_entities.updated_by_id")
            .leftJoin("core_service_providers as insurer", "insurer.id", "crmf_general_ledger.payer_id")
        )

        # Get filter parameters
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "crmf_general_ledger.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_filters = [
            "invoice_number",
            "transaction_date",
            "payment_method",
            "ledger_status",
            "payer_id",
            "core_entities.created_at"
        ]
        search_columns = [
            "invoice_number",
            "payment_id",
            "remarks",
            "insurer.name"
        ]
        sort_columns = [
            "invoice_number",
            "transaction_date",
            "payment_amount",
            "payment_method",
            "ledger_status",
            "created_at"
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

        # Format date fields for each record
        rows = data.get("data", [])
        for item in rows:
            _format_date_fields(item)
        data["data"] = rows

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    except Exception as e:
        return ResponseService.response("ERROR", str(e), "Error retrieving entries")

def create_entry(request):
    """Create a new general ledger entry"""
    try:
        data = json.loads(request.body or "{}")
        errors = ValidatorService.validate(data, get_general_ledger_rules())
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation failed")

        entry = create_general_ledger_entry(data, user=request.user)
        if not entry:
            return ResponseService.response("ERROR", None, "Failed to create entry")

        return ResponseService.response("SUCCESS", entry, "Entry created successfully")

    except Exception as e:
        return ResponseService.response("ERROR", str(e), "Error creating entry")

def update_entry(request, entry_id):
    """Update an existing general ledger entry"""
    try:
        data = json.loads(request.body or "{}")
        errors = ValidatorService.validate(data, get_general_ledger_rules(True))
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation failed")

        # Get existing entry
        existing_entry = QueryBuilderService("crmf_general_ledger").where("id", entry_id).first()
        if not existing_entry:
            return ResponseService.response("NOT_FOUND", None, "Entry not found")

        # Update entry
        updated = QueryBuilderService("crmf_general_ledger").where("id", entry_id).update(data)
        if not updated:
            return ResponseService.response("ERROR", None, "Failed to update entry")

        return ResponseService.response("SUCCESS", updated, "Entry updated successfully")

    except Exception as e:
        return ResponseService.response("ERROR", str(e), "Error updating entry")

def delete_entry(entry_id):
    # Delete general ledger entry
    entry = QueryBuilderService("crmf_general_ledger").where("id", entry_id).delete()
    if not entry:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    return ResponseService.response("SUCCESS", None, Message.DATA_DELETED)

def get_general_ledger_rules(is_update=False):
    """Get validation rules for general ledger entries"""
    rules = {
        "invoice_number": "required|string|max:50",
        "transaction_date": "required|date",
        "payment_amount": "required|decimal",
        "payer_id": "required|integer|exists:core_service_providers,id",
        "payment_method": "required|string|in:cash,bank_transfer,cheque,credit_card,other",
        "ledger_status": "required|string|in:pending,completed,failed,cancelled",
        "remarks": "string"
    }
    return rules

@csrf_exempt
@api_view(["GET"])
def general_ledger_account_report(request):
    """Account-wise General Ledger report (journal entries)"""
    action_type = "VIEW"
    action = ActionService.getAction("GeneralLedger", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    try:
        columns = [
            "crmf_journal_entries.entry_number as payment_id",
            "crmf_journal_entries.date as transaction_date",
            "crmf_chart_of_account.account_name as account_name",
            "crmf_journal_entries.debit_amount",
            "crmf_journal_entries.credit_amount",
            "insurer.name as payer_details",
            "insurer.logo as payer_logo",
            "crmf_journal_entries.description as remarks",
            # "crmf_journal_entries.ledger_status",
            "crmf_invoices.invoice_number"
        ]
        query = (
            QueryBuilderService("crmf_journal_entries")
            .select(*columns)
            .leftJoin("crmf_chart_of_account", "crmf_chart_of_account.id", "crmf_journal_entries.account_id")
            .leftJoin("crmf_invoices", "crmf_invoices.id", "crmf_journal_entries.invoice_id")
            .leftJoin("core_service_providers as insurer", "insurer.id", "crmf_invoices.insurer_id")
            .leftJoin("crmp_issued_policies", "crmp_issued_policies.id", "crmf_invoices.issued_policy_id")
            .leftJoin("crmp_policy_base", "crmp_policy_base.id", "crmp_issued_policies.policy_base_id")
            .leftJoin("core_vendor_products", "core_vendor_products.id", "crmp_policy_base.product_id")
            .leftJoin("core_product_groups", "core_product_groups.id", "crmp_policy_base.product_group_id")
            .leftJoin("core_product_group_products", "core_product_group_products.product_group_id", "core_product_groups.id")
        )
        # Optional: Add filters, pagination, etc.
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "crmf_general_ledger.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_filters = [
            "invoice_number", "transaction_date", "account_name", "payer_details"
        ]
        search_columns = [
            "invoice_number", "account_name", "payer_details", "remarks"
        ]
        sort_columns = [
            "invoice_number", "transaction_date", "account_name"
        ]
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
        rows = data.get("data", [])
        for item in rows:
            _format_date_fields(item)
        data["data"] = rows
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), "Error retrieving account-wise ledger entries")

@csrf_exempt
@api_view(["GET"])
def general_ledger_account_balances(request):
    """Return account balances (total debit, credit, and balance) for each account, including insurer details and business type."""
    action_type = "VIEW"
    action = ActionService.getAction("GeneralLedger", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    try:
        # Aggregate debit and credit by account, include insurer details
        columns = [
            "crmf_chart_of_account.id as account_id",
            "crmf_chart_of_account.account_name as account_name",
            "crmf_chart_of_account.account_number as account_number",
            "SUM(crmf_journal_entries.debit_amount) as total_debit",
            "SUM(crmf_journal_entries.credit_amount) as total_credit",
            "insurer.name as insurer_name",
            "insurer.logo as insurer_logo"
        ]
        query = (
            QueryBuilderService("crmf_journal_entries")
            .select(*columns)
            .leftJoin("crmf_chart_of_account", "crmf_chart_of_account.id", "crmf_journal_entries.account_id")
            .leftJoin("crmf_invoices", "crmf_invoices.id", "crmf_journal_entries.invoice_id")
            .leftJoin("core_service_providers as insurer", "insurer.id", "crmf_invoices.insurer_id")
            .leftJoin("crmp_issued_policies", "crmp_issued_policies.id", "crmf_invoices.issued_policy_id")
            .leftJoin("crmp_policy_base", "crmp_policy_base.id", "crmp_issued_policies.policy_base_id")
            .leftJoin("core_vendor_products", "core_vendor_products.id", "crmp_policy_base.product_id")
            .leftJoin("core_product_groups", "core_product_groups.id", "crmp_policy_base.product_group_id")
            .leftJoin("core_product_group_products", "core_product_group_products.product_group_id", "core_product_groups.id")
            .groupBy("crmf_chart_of_account.id", "crmf_chart_of_account.account_name", "crmf_chart_of_account.account_number", "insurer.name", "insurer.logo")
        )

        # Get all aggregated data first
        data = query.get()
        
        # Apply post-query filtering and pagination for aggregated data
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "").lower()
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "account_name")
        sort_dir = request.GET.get("sort_dir", "desc")

        # Filter data based on search string
        if search_string:
            filtered_data = []
            for item in data:
                if (search_string in str(item.get("account_name", "")).lower() or
                    search_string in str(item.get("account_number", "")).lower() or
                    search_string in str(item.get("insurer_name", "")).lower()):
                    filtered_data.append(item)
            data = filtered_data

        # Filter data based on filter_json
        if filter_json:
            filtered_data = []
            for item in data:
                include_item = True
                for key, value in filter_json.items():
                    if key == "account_name" and value and str(item.get("account_name", "")).lower() != str(value).lower():
                        include_item = False
                        break
                    elif key == "account_number" and value and str(item.get("account_number", "")) != str(value):
                        include_item = False
                        break
                    elif key == "insurer_name" and value and str(item.get("insurer_name", "")).lower() != str(value).lower():
                        include_item = False
                        break
                if include_item:
                    filtered_data.append(item)
            data = filtered_data

        # Sort data
        reverse_sort = sort_dir.lower() == "desc"
        if sort_by == "account_name":
            data.sort(key=lambda x: str(x.get("account_name", "")), reverse=reverse_sort)
        elif sort_by == "account_number":
            data.sort(key=lambda x: str(x.get("account_number", "")), reverse=reverse_sort)
        elif sort_by == "total_debit":
            data.sort(key=lambda x: float(x.get("total_debit", 0) or 0), reverse=reverse_sort)
        elif sort_by == "total_credit":
            data.sort(key=lambda x: float(x.get("total_credit", 0) or 0), reverse=reverse_sort)
        else:
            # Default sort by account_name
            data.sort(key=lambda x: str(x.get("account_name", "")), reverse=reverse_sort)

        # Calculate pagination
        total_count = len(data)
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = data[start_index:end_index]

        # Create response structure matching other endpoints
        data = {
            "total_records": total_count,
            "per_page": limit,
            "current_page": page,
            "last_page": (total_count + limit - 1) // limit,
            "data": paginated_data
        }

        # Mapping from account_number to business type (from journal_entry_utils.py)
        account_number_to_type = {
            '50001': 'commission_payable_agent',
            '20003': 'commission_payable_agent',
            '10002': 'commission_income_new_business',
            '40005': 'commission_income_new_business',
            '40006': 'commission_income_renewals',
            '40007': 'commission_income_endorsements',
            '40008': 'commission_income_adjusted',
            '40009': 'service_charge_income',
            '10001': 'bank_payment',
            '20005': 'commission_reversal_payable_insurer',
        }

        # Calculate balance and business type for each account
        rows = data.get("data", [])
        for item in rows:
            item["balance"] = float(item.get("total_debit", 0) or 0) - float(item.get("total_credit", 0) or 0)
            acc_num = str(item.get("account_number", ""))
            item["business_type"] = account_number_to_type.get(acc_num, "other")

        # Add friendly label and formatted string for each item
        friendly_type = {
            'commission_payable_agent': 'Payable (Agent)',
            'commission_income_new_business': 'New Business  Income',
            'commission_income_renewals': 'Renewal  Income',
            'commission_income_endorsements': 'Endorsement  Income',
            'commission_income_adjusted': 'Adjusted/Contra ',
            'service_charge_income': 'Service Charge Income',
            'bank_payment': 'Bank Payment',
            'commission_reversal_payable_insurer': ' Reversal Payable (Insurer)',
            'other': 'Other'
        }
        for item in rows:
            item['business_type_label'] = friendly_type.get(item['business_type'], 'Other')
        
        data["data"] = rows
     
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), "Error retrieving account balances") 