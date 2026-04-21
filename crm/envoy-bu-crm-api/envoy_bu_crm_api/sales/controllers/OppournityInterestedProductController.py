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
def interested_products(request,opp_id):
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Interested_Products","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return getAll(request,opp_id)
    
    elif request.method == 'POST':
        action = ActionService.getAction("Opportunity_Interested_Products","Create")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return create_interested_products(request,opp_id)
    
def getAll(request,opp_id):
    all_columns = [ "crm_oppor_interested_products.*",  # Existing columns
        "core_products.name AS product_name",      # Add product name
        "core_products.code AS product_code"       # Add product code
        ]

    filter_json = request.GET.get('filter', {})
    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by')
    sort_dir = request.GET.get('sort_dir', 'desc')
    # Normalize empty values to defaults
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    allowed_sorting_columns = ["id", "core_products.name", "core_products.code"]
    ids = request.GET.get('ids', None)
    allowed_filters = []
    search_columns = []

    data = QueryBuilderService("crm_oppor_interested_products")\
            .leftJoin("core_products", "core_products.id", "crm_oppor_interested_products.product_id")\
            .select(*all_columns) \
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
            .where("opportunity_id",opp_id) \
            .orderBy(sort_by, sort_dir) \
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \
            
    return ResponseService.response('SUCCESS',data,Message.DATA_FETCHED)

@csrf_exempt
@api_view(['DELETE'])
def single_interested_products(request, opp_id , product_id):   
        action = ActionService.getAction("Opportunity_Interested_Products","DELETE")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        deleted_data = QueryBuilderService("crm_oppor_interested_products")\
                    .where("opportunity_id",opp_id) \
                    .where("id",product_id) \
                    .delete()           
        if deleted_data:
            return ResponseService.response('SUCCESS',deleted_data,Message.DATA_DELETED)
        else:
            return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)
       
def create_interested_products(request,opp_id):
    if not request.body or request.body == b'':
        data = {}  
    else:
        data = json.loads(request.body)
    
    rules = {
        'product_id': 'required',
    }
   
    errors = ValidatorService.validate(data, rules, {})
    if errors:
        return ResponseService.response('VALIDATION_ERROR',errors,Error.VALIDATION_ERROR)
    
    data["opportunity_id"] = opp_id
    new_data = QueryBuilderService("crm_oppor_interested_products").insert(data)
    return ResponseService.response('SUCCESS',new_data,Message.DATA_CREATED)
