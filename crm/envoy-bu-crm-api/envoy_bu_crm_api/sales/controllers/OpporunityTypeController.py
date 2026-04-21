import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message,Error
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@api_view(['GET', 'POST'])
def opportunity_types(request):
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Type","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return getAll(request)
    
    elif request.method == 'POST':
        action = ActionService.getAction("Opportunity_Type","Create")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return manage_opportunity_types(request)
    
def getAll(request):
    all_columns = ['id', 'title', 'description']

    filter_json = request.GET.get('filter', {})
    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by')
    sort_dir = request.GET.get('sort_dir', 'desc')
    # Normalize empty values to defaults
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    allowed_sorting_columns = ["id", "title", "description"]
    ids = request.GET.get('ids', None)
    allowed_filters = []
    search_columns = ["title", "description"]

    data = QueryBuilderService("crm_opportunity_types")\
            .select(*all_columns) \
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
            
    if ids:
        data = data.whereIn("id", ids.split(',')) \
                .orderBy(sort_by, sort_dir) \
                .get()
    else:
        data = data.orderBy(sort_by, sort_dir) \
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \
            
    return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def single_opportunity_types(request, id):   
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Type","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return getSingle(request, id)
    
    elif request.method == 'PUT':
        action = ActionService.getAction("Opportunity_Type","UPDATE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return manage_opportunity_types(request, id)
    
    elif request.method == 'DELETE':
        action = ActionService.getAction("Opportunity_Type","DELETE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return delete(request, id)
    
def getSingle(request, id):
    data = QueryBuilderService("crm_opportunity_types")\
            .where("id",id) \
            .first()
            
    if data:
        return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)
    else:
        return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)

def manage_opportunity_types(request,id=None):
    if not request.body or request.body == b'':
        data = {}  
    else:
        data = json.loads(request.body)
    
    rules = {
        'title': 'required|unique:crm_opportunity_types,title',
    }
    custom_messages = {
        'title.required': 'The title field is required.',
    }

    rules['title'] += f",{id}" if id else ""

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response('VALIDATION_ERROR',errors,Error.VALIDATION_ERROR)
    
    if id:
        updated_data = QueryBuilderService("crm_opportunity_types")\
                    .where("id",id) \
                    .update(data)
        if updated_data:
            return ResponseService.response('SUCCESS',updated_data,Message.DATA_UPDATED)        
        else:
            return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)
    else:
        new_data = QueryBuilderService("crm_opportunity_types").insert(data)
        return ResponseService.response('SUCCESS',new_data,Message.DATA_CREATED)
    
def delete(request, id):
    # Step 1: Validation: Check if record exists
    opportunity_type = QueryBuilderService("crm_opportunity_types").where("id", id).first()
    if not opportunity_type:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Step 2: Check if it's linked in crm_opportunity_form_config
    is_used_in_form_config = QueryBuilderService("crm_opportunity_form_config")\
        .where("opportunity_type_id", id).first()

    if is_used_in_form_config:
        return ResponseService.response("CONFLICT", None, Error.CONFLICT)

    # Step 3: Optionally delete dependent mapping/bridge rows first
    QueryBuilderService("crm_oppor_opportunity_types")\
        .where("opportunity_type_id", id).delete()

    # Step 4: Delete the main record
    deleted_data = QueryBuilderService("crm_opportunity_types")\
        .where("id", id).delete()

    if deleted_data:
        return ResponseService.response("SUCCESS", deleted_data, Message.DATA_DELETED)
    else:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
