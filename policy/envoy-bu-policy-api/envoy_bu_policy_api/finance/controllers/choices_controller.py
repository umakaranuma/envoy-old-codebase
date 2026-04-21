import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_policy_api.finance.models.crmf_general_ledger import GeneralLedger
from envoy_bu_policy_api.finance.models.crmf_chart_of_accounts import ChartOfAccount
from mServices import QueryBuilderService

@csrf_exempt
@api_view(["GET"])
def get_payment_methods(request):
    """
    Get available payment methods
    """
    action_type = "VIEW"
    action = ActionService.getAction("Payment", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    payment_methods = [
        {"value": choice[0], "label": choice[1]}
        for choice in GeneralLedger.PAYMENT_METHOD_CHOICES
    ]
    
    return ResponseService.response("SUCCESS", payment_methods, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def get_account_types(request):
    """
    Get available account types
    """
    action_type = "VIEW"
    action = ActionService.getAction("Payment", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    account_types = [
        {"value": choice[0], "label": choice[1]}
        for choice in ChartOfAccount.ACCOUNT_TYPE_CHOICES
    ]
    
    return ResponseService.response("SUCCESS", account_types, Message.DATA_FETCHED) 


@csrf_exempt
@api_view(["GET"])
def get_transaction_types(request):

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmf_transaction_types.id")
    sort_dir = request.GET.get("sort_dir", "desc")
    allowed_filters = ["crmf_transaction_types.id", "crmf_transaction_types.name"]
    search_columns = ["crmf_transaction_types.id", "crmf_transaction_types.name",]
    allowed_sorting_columns = ["crmf_transaction_types.id", "crmf_transaction_types.name",]


    data = (

        
        QueryBuilderService("crmf_transaction_types")
        .select('crmf_transaction_types.*')
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

    return ResponseService.response("SUCCESS", data, "data_get")