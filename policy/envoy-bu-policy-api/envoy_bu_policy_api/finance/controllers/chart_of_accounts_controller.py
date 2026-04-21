from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from envoy_bu_policy_api.finance.models.crmf_chart_of_accounts import ChartOfAccount
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_policy_api.service import handle_entity, _format_date_fields
import json

def generate_account_number():
    # Get the last account number
    last_account = (
        QueryBuilderService("crmf_chart_of_account")
        .select("account_number")
        .orderBy("account_number", "desc")
        .first()
    )
    
    if last_account:
        # Extract the number and increment
        last_num = int(last_account["account_number"].replace("ACC", ""))
        new_num = str(last_num + 1).zfill(6)
    else:
        # Start with 000001 if no accounts exist
        new_num = "000001"
    
    return f"ACC{new_num}"

@csrf_exempt
@api_view(["GET", "POST"])
def chart_of_account_list(request):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("ChartOfAccounts", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_accounts(request)

    return create_account(request)

@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def chart_of_account_detail(request, account_id):
    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("ChartOfAccounts", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_accounts(request, account_id=account_id)
    elif request.method == "PUT":
        return update_account(request, account_id)
    elif request.method == "DELETE":
        return delete_account(account_id)

def get_all_accounts(request, account_id=None):
    columns = [
        "crmf_chart_of_account.*",
    ]

    query = (
        QueryBuilderService("crmf_chart_of_account")
        .select(*columns)
    )

    if account_id:
        data = query.where("crmf_chart_of_account.id", account_id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        _format_date_fields(data)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    # Get filter parameters
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "account_number" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    allowed_filters = ["account_number", "account_name", "account_type"]
    search_columns = ["account_number", "account_name", "description"]
    sort_columns = ["account_number", "account_name", "account_type"]

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

def create_account(request):
    data = json.loads(request.body or "{}")
    errors = ValidatorService.validate(data, get_chart_of_account_rules())
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    user = request.user if request.user.is_authenticated else None
    entity_data = {
        "type": "chart_of_account",
        "approvel_status": False,
    }
    entity_id = handle_entity(entity_data, entity_id=data.get("entity_id"), user=user)
    data["entity_id"] = entity_id
    
    # Generate account number
    data["account_number"] = generate_account_number()

    # Create chart of account
    account = QueryBuilderService("crmf_chart_of_account").insert(data)
    return ResponseService.response("SUCCESS", account, Message.DATA_CREATED)

def update_account(request, account_id):
    data = json.loads(request.body or "{}")
    errors = ValidatorService.validate(data, get_chart_of_account_rules(True))
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Get existing account data
    account_data = QueryBuilderService("crmf_chart_of_account").where("id", account_id).first()
    if not account_data:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Update entity record
    if account_data.get("entity_id"):
        user = request.user if request.user.is_authenticated else None
        entity_data = {
            "type": "chart_of_account",
            "approvel_status": False,
        }
        handle_entity(entity_data, entity_id=account_data["entity_id"], user=user)

    # Update chart of account
    account = QueryBuilderService("crmf_chart_of_account").where("id", account_id).update(data)
    return ResponseService.response("SUCCESS", account, Message.DATA_UPDATED)

def delete_account(account_id):
    # Delete chart of account
    account = QueryBuilderService("crmf_chart_of_account").where("id", account_id).delete()
    if not account:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    return ResponseService.response("SUCCESS", None, Message.DATA_DELETED)

def get_chart_of_account_rules(is_update=False):
    rules = {
        "account_name": "required|string|max:255",
        "account_type": "required|string|in:asset,liability,equity,revenue,expense",
        "description": "string",
    }
    
    return rules 