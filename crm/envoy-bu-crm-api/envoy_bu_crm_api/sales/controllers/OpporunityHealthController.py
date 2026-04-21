import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message,Error
from django.views.decorators.csrf import csrf_exempt

@api_view(['GET'])
def get_all_health(request):
    action = ActionService.getAction("Opportunity_Health","VIEW")
    has_authority = AuthService.hasAuthority(request , action)
    
    if(not has_authority):
        return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
    
    return getAll(request)
    
@csrf_exempt
@api_view(['GET', 'POST'])
def get_opportunity_health(request,opp_id):
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Type","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return getAll(request,opp_id)
    
    elif request.method == 'POST':
        action = ActionService.getAction("Opportunity_Type","Create")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return manage_opportunity_health(request,opp_id)
    
def getAll(request , oppournity_id=None):
    all_columns = ['*']

    filter_json = request.GET.get('filters', '{}')  # must be string
    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by', 'date')
    sort_dir = request.GET.get('sort_dir', 'desc')
    ids = request.GET.get('ids', None)

    # Add allowed filterable fields (match DB column names!)
    allowed_filters = ["health", "opportunity_id"]
    search_columns = []
    allowed_sorting_columns = ["health"]

    data = (
        QueryBuilderService("crm_opportunity_health")
        .select(*all_columns)
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
    )

    if oppournity_id:
        data = data.where("opportunity_id", oppournity_id)

    if ids:
        data = data.whereIn("id", ids.split(',')).get()
    else:
        data = data.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

    return ResponseService.response('SUCCESS', data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def single_opportunity_health(request,opp_id, health_id):   
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Type","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return getSingle(health_id)
    
    elif request.method == 'PUT':
        action = ActionService.getAction("Opportunity_Type","UPDATE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return manage_opportunity_health(request,opp_id, health_id)
    
    elif request.method == 'DELETE':
        action = ActionService.getAction("Opportunity_Type","DELETE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return delete(health_id)
    
def getSingle(id):
    data = QueryBuilderService("crm_opportunity_health")\
            .where("id",id) \
            .first()
            
    if data:
        return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)
    else:
        return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)

def manage_opportunity_health(request,opp_id,id=None):
    if not request.body or request.body == b'':
        data = {}  
    else:
        data = json.loads(request.body)
    
    rules = {
        'date': 'required',
        'health': 'required',
    }
    
    errors = ValidatorService.validate(data, rules, {})
    if errors:
        return ResponseService.response('VALIDATION_ERROR',errors,Error.VALIDATION_ERROR)
    
    if id:
        updated_data = QueryBuilderService("crm_opportunity_health")\
                    .where("id",id) \
                    .update(data)
        
        if updated_data:
            return ResponseService.response('SUCCESS',updated_data,Message.DATA_UPDATED)        
        else:
            return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)
    else:
        data['opportunity_id'] = opp_id
        new_data = QueryBuilderService("crm_opportunity_health").insert(data)
        return ResponseService.response('SUCCESS',new_data,Message.DATA_CREATED)
    
def delete(id):
    deleted_data = QueryBuilderService("crm_opportunity_health")\
                    .where("id",id) \
                    .delete()           
    if deleted_data:
        return ResponseService.response('SUCCESS',deleted_data,Message.DATA_DELETED)
    else:
        return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)