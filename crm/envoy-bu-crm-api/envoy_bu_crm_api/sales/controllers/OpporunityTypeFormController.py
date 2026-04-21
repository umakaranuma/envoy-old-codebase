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
def opportunity_form(request,opp_type_id):
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Type_Form","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return getAll(request,opp_type_id)
    
    elif request.method == 'POST':
        action = ActionService.getAction("Opportunity_Type_Form","Create")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return manage_opportunity_type_form(request,opp_type_id)
    
def getAll(request,opp_type_id):
    all_columns = ['oppo_f_config.*', 'cf.title as form']

    filter_json = request.GET.get('filter', {})
    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by', 'id')
    sort_dir = request.GET.get('sort_dir', 'desc')
    allowed_filters = ['oppo_f_config.opportunity_type_id',"oppo_f_config.data_gethering_type"]
    search_columns = ["oppo_f_config.title", "cf.title"]
    allowed_sorting_columns = ["oppo_f_config.data_gethering_type"]

    data = QueryBuilderService("crm_opportunity_form_config as oppo_f_config")\
            .leftJoin('core_templates as cf','cf.id','oppo_f_config.form_id') \
            .select(*all_columns) \
            .where("oppo_f_config.opportunity_type_id",opp_type_id) \
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \
            
    return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def single_opportunity_form(request, opp_type_id, form_id):   
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Type","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return getSingle(form_id)
    
    elif request.method == 'PUT':
        action = ActionService.getAction("Opportunity_Type","UPDATE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return manage_opportunity_type_form(request,opp_type_id, form_id)
    
    elif request.method == 'DELETE':
        action = ActionService.getAction("Opportunity_Type","DELETE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        return delete(form_id)
    
def getSingle(form_id):
    data = QueryBuilderService("crm_opportunity_form_config")\
            .where("id",form_id) \
            .first()    
            
    if data:
        return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)
    else:
        return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)

def manage_opportunity_type_form(request, opp_type_id, form_id=None):
    try:
        data = json.loads(request.body) if request.body else {}
    except json.JSONDecodeError:
        return ResponseService.response('VALIDATION_ERROR', None, Error.VALIDATION_ERROR)

    # Add opportunity_type_id from URL into data if not already included
    data.setdefault('opportunity_type_id', opp_type_id)

    rules = {
        'title': 'required',
        'opportunity_type_id': 'required',
        'data_gethering_type': 'required',
        'form_id': 'required',
    }

    errors = ValidatorService.validate(data, rules, {})
    if errors:
        return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)

    # Enforce uniqueness of (opportunity_type_id, data_gethering_type)
    existing = QueryBuilderService("crm_opportunity_form_config")\
        .where("opportunity_type_id", data["opportunity_type_id"])\
        .where("data_gethering_type", data["data_gethering_type"])

    if form_id:
        existing = existing.where("id", "!=", form_id)

    if existing.first():
        return ResponseService.response(
            "VALIDATION_ERROR",
            {
                "data_gethering_type": [
                    {
                        "error_type": "unique",
                        "tokens": {
                            "_attribute": "data_gethering_type"
                        }
                    }
                ]
            },
            Error.VALIDATION_ERROR
        )

    if form_id:
        updated_data = QueryBuilderService("crm_opportunity_form_config")\
            .where("id", form_id)\
            .update(data)

        if updated_data:
            return ResponseService.response('SUCCESS', updated_data, Message.DATA_UPDATED)
        else:
            return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)
    else:
        new_data = QueryBuilderService("crm_opportunity_form_config").insert(data)
        return ResponseService.response('SUCCESS', new_data, Message.DATA_CREATED)


def delete(form_id):
    # Step 0: Check if the form config is used in crm_oppor_form_submissions
    usage_count = QueryBuilderService("crm_oppor_form_submissions") \
        .where("oppor_form_config_id", form_id) \
        .count()

    if usage_count > 0:
        return ResponseService.response(
            "CONFLICT",
            [],
            Error.DEFAULT_CONFLICT_MSG,
            system_code="CONFLICT"
        )

    # Step 1: Safe to delete form config
    deleted_data = QueryBuilderService("crm_opportunity_form_config") \
        .where("id", form_id) \
        .delete()

    if deleted_data:
        return ResponseService.response('SUCCESS', deleted_data, Message.DATA_DELETED)
    else:
        return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)
