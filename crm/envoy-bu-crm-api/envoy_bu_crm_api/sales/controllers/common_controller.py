import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
from rest_framework.decorators import api_view
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from django.views.decorators.csrf import csrf_exempt

def get_all_opportunity_statuses(request):
    

    
    all_columns = ["id", "name", "sort_index"]

    
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "sort_index")
    sort_dir = request.GET.get("sort_dir", "desc")

   
    allowed_filters = []
    search_columns = ["name"]
    allowed_sorting_columns = ["sort_index", "name"]

    
    data = (
        QueryBuilderService("crm_opportunity_statuses")
        .select(*all_columns)
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@csrf_exempt
@api_view(["GET"])
def sales_agents(request):
   
    
    action = ActionService.getAction("SalesAgent", "VIEW")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    return get_all_sales_agents(request)


def get_all_sales_agents(request):
    """ Fetch and return all sales agents with filters, search & pagination"""

    
    all_columns = ["id", "name", "email"]

   
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "name")
    sort_dir = request.GET.get("sort_dir", "desc")

    
    allowed_filters = []
    search_columns = ["name", "email"]
    allowed_sorting_columns = ["name", "email"]

    
    data = (
        QueryBuilderService("core_users")
        .select(*all_columns)
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
