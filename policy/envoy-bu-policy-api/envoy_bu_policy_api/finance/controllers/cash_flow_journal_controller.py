from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
import json
from decimal import Decimal

@csrf_exempt
@api_view(["GET"])
def cash_flow_journal_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("CashFlowJournal", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_all_cash_flows(request)

@csrf_exempt
@api_view(["GET"])
def cash_flow_journal_totals(request):
    action_type = "VIEW"
    action = ActionService.getAction("CashFlowJournal", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return get_cash_flow_totals(request)

def get_cash_flow_totals(request):
    # Base query to get journal entries with their amounts
    query = (
        QueryBuilderService("crmf_journal_entries")
        .select(
            "crmf_journal_entries.debit_amount",
            "crmf_journal_entries.credit_amount"
        )
    )

    # Get filter parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")

    allowed_filters = ["date"]
    search_columns = ["crmf_journal_entries.description", "crmf_journal_entries.entry_number", "crmf_chart_of_account.account_name"]

    # Apply filters and search
    query = query.apply_conditions(
        filter_json,
        allowed_filters,
        search_string,
        search_columns
    )

    # Get all entries
    entries = query.get()

    # Calculate totals
    total_inflows = Decimal('0.00')
    total_outflows = Decimal('0.00')

    for entry in entries:
        debit = Decimal(str(entry["debit_amount"]))
        credit = Decimal(str(entry["credit_amount"]))
        
        total_inflows += credit
        total_outflows += debit

    total_net = total_inflows - total_outflows

    totals_data = {
        "total_cash_inflows": str(total_inflows),
        "total_cash_outflows": str(total_outflows),
        "total_net_cash_flow": str(total_net)
    }

    return ResponseService.response("SUCCESS", totals_data, Message.DATA_FETCHED)

def get_all_cash_flows(request):
    # Base query to get journal entries with their amounts
    query = (
        QueryBuilderService("crmf_journal_entries")
        .select(
            "crmf_journal_entries.date",
            "crmf_journal_entries.debit_amount",
            "crmf_journal_entries.credit_amount"
        )
    )

    # Get filter parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmf_journal_entries.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["date"]
    search_columns = ["crmf_journal_entries.entry_number", "crmf_chart_of_account.account_name"]
    sort_columns = ["date"]

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

    # Process the data to calculate cash flows by date
    rows = data.get("data", [])
    cash_flow_data = {}

    for entry in rows:
        date = entry["date"]
        if date not in cash_flow_data:
            cash_flow_data[date] = {
                "date": date,
                "cash_inflows": Decimal('0.00'),
                "cash_outflows": Decimal('0.00'),
                "net_cash_flow": Decimal('0.00')
            }
        
        # Calculate cash flows
        debit = Decimal(str(entry["debit_amount"]))
        credit = Decimal(str(entry["credit_amount"]))
        
        cash_flow_data[date]["cash_inflows"] += credit
        cash_flow_data[date]["cash_outflows"] += debit
        cash_flow_data[date]["net_cash_flow"] = cash_flow_data[date]["cash_inflows"] - cash_flow_data[date]["cash_outflows"]

    # Convert the dictionary to a list and sort by date
    processed_data = list(cash_flow_data.values())
    processed_data.sort(key=lambda x: x["date"], reverse=(sort_dir == "desc"))

    # Convert Decimal to string for JSON serialization
    for item in processed_data:
        item["cash_inflows"] = str(item["cash_inflows"])
        item["cash_outflows"] = str(item["cash_outflows"])
        item["net_cash_flow"] = str(item["net_cash_flow"])

    # Update the response data
    data["data"] = processed_data
    data["total"] = len(processed_data)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) 