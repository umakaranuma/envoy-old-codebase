import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from services.ActionService import ActionService
from services.AuthService import AuthService
from services.SettingService import SettingService
from messages import Message,Error
from setting_keys import SettingKeys
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict

@api_view(['GET'])
def get_opportunity_status(request):
    all_columns = ['*']
    filter_json = request.GET.get('filter', {})
    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by', 'id')
    sort_dir = request.GET.get('sort_dir', 'desc')
    ids = request.GET.get('ids', None)
    assigned_to = request.GET.get('assigned_to', None)
    ignore = request.GET.get('ignore', None)  # New parameter to exclude types
    allowed_filters = ['type']
    search_columns = ["name", "type"]
    allowed_sorting_columns = ["name", 'type']

    data = QueryBuilderService("crm_opportunity_statuses")\
            .select(*all_columns) \
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)

    # Exclude types specified in the `ignore` parameter
    if ignore:
        ignore_types = ignore.split(',')  # Split the ignore parameter into a list
        data = data.whereNotIn("type", ignore_types)

    if ids:
        data = data.whereIn("id", ids.split(','))

    data = data.get()

    # Loop through the data and add the `total_opportunity_count` parameter to each status
    for status in data:
        status["total_opportunity_count"] = 0

        count_data = QueryBuilderService("crm_opportunities") \
                                            .where("stage_id", status["id"])

        if assigned_to is not None:
            count_data = count_data.where("sales_agent_id", assigned_to)

        status["total_opportunity_count"] = count_data.count()

    return ResponseService.response('SUCCESS', data, Message.DATA_FETCHED)


@api_view(['GET'])
def get_opportunity_status_by_id(request, id):
    """Fetch a single opportunity status by its ID."""
    try:
        # Fetch the opportunity status by ID
        opportunity_status = QueryBuilderService("crm_opportunity_statuses")\
            .select("*")\
            .where("id", id)\
            .first()

        # Check if the opportunity status exists
        if not opportunity_status:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

        # Add the `total_opportunity_count` parameter
        opportunity_status["total_opportunity_count"] = QueryBuilderService("crm_opportunities")\
            .where("stage_id", id)\
            .count()

        return ResponseService.response("SUCCESS", opportunity_status, Message.DATA_FETCHED)

    except Exception as e:
        return ResponseService.response("ERROR", None, Error.DEFAULT)


@api_view(['GET'])
def get_sales_agents(request):
    all_columns = ['core_users.*','core_roles.name as role']
    filter_json = request.GET.get('filter', {})
    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by', 'core_users.id')
    sort_dir = request.GET.get('sort_dir', 'desc')
    ids = request.GET.get('ids', None)
    allowed_filters = ['type']
    search_columns = ["first_name", "last_name","display_name"]
    allowed_sorting_columns = ["first_name",'role_id',"display_name"]

    roles=[]
    setting_value = SettingService.getSettingKeyValue(SettingKeys.SALES_AGENT_ROLES)
    if setting_value:
        roles=setting_value.split(',')

    data = QueryBuilderService("core_users")\
            .leftJoin('core_roles','core_roles.id','core_users.role_id') \
            .select(*all_columns) \
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
            
    if roles:
        data = data.whereIn("core_users.role_id", roles)
        
    data = data.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \
  
    return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)


@api_view(['GET'])
def get_team_members(request):
    """
    Get users who are members of teams (exist in core_team_users table)
    """
    all_columns = ['core_users.*','core_roles.name as role']
    filter_json = request.GET.get('filter', {})
    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by', 'core_users.id')
    sort_dir = request.GET.get('sort_dir', 'desc')
    ids = request.GET.get('ids', None)
    allowed_filters = ['type']
    search_columns = ["first_name", "last_name","display_name"]
    allowed_sorting_columns = ["first_name",'role_id',"display_name"]

    # First, get unique user IDs from core_team_users table
    team_user_ids = QueryBuilderService("core_team_users")\
            .select("DISTINCT user_id") \
            .get()
    
    # Extract just the user IDs
    user_ids = [row['user_id'] for row in team_user_ids]
    
    # Get users who exist in core_team_users table
    data = QueryBuilderService("core_users")\
            .leftJoin('core_roles','core_roles.id','core_users.role_id') \
            .select(*all_columns) \
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
            .whereIn('core_users.id', user_ids) \
            
    data = data.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \
  
    return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)


@api_view(['GET'])
def get_opportunity_get_types(request):
    ids = request.GET.get('ids', None)

    data=[]
    if ids:
        data = QueryBuilderService("crm_oppor_opportunity_types as oppo_oppo_types")\
                .leftJoin('crm_opportunity_types oppo_types','oppo_types.id','oppo_oppo_types.opportunity_type_id') \
                .select('*') \
                .whereIn("oppo_oppo_types.opportunity_id", ids.split(',')) \
                .get()
        
        grouped_data = defaultdict(list)

        for item in data:
            grouped_data[item["opportunity_id"]].append(item)

        grouped_data = dict(grouped_data)
        
    return ResponseService.response('SUCCESS',grouped_data,Message.DATA_FETCHED)
