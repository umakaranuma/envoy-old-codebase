import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt

from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error

@csrf_exempt
@api_view(['GET', 'POST'])
def get_form_config_info(request, policy_id, config_id):
    if request.method == 'GET':
        action = ActionService.getAction("Policy_Risk_Reg_Form_Config_Type", "VIEW")
        has_authority = AuthService.hasAuthority(request, action)
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        return getAll(request, policy_id, config_id)
    elif request.method == 'POST':
        action = ActionService.getAction("Policy_Type", "Create")
        has_authority = AuthService.hasAuthority(request, action)
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        return save_policy_form_submission(request, policy_id, config_id)


def getAll(request, policy_id, config_id):
    data = QueryBuilderService("crmp_policy_risk_reg_form_submissions") \
            .where('policy_id', policy_id) \
            .where('oppor_form_config_id', config_id) \
            .get()

    for item in data:
        config_values = QueryBuilderService("core_form_submission_values") \
                        .where('form_submission_id', item["form_submission_id"]) \
                        .get()

        # Convert the config list to a dictionary and update the item
        config_dict = {conf["attribute_id"]: conf["value"] for conf in config_values}
        item.update(config_dict)

    return ResponseService.response('SUCCESS', data, Message.DATA_FETCHED)


def save_policy_form_submission(request, policy_id, config_id):
    form_config = QueryBuilderService("crmp_claim_form_config") \
        .where('id', config_id) \
        .first()

    if not form_config:
        return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)

    try:
        data = json.loads(request.body)
    except Exception:
        return ResponseService.response('VALIDATION_ERROR', None, "Invalid JSON format.")

    # Accept raw list or { "data": [...] }
    if isinstance(data, list):
        data = { "data": data }
    elif not isinstance(data, dict):
        return ResponseService.response('VALIDATION_ERROR', None, "Invalid request format. Expected object or array.")

    rules = {
        "data": "required|list"
    }

    error = ValidatorService.validate(data, rules)
    if error:
        return ResponseService.response('VALIDATION_ERROR', error, Error.VALIDATION_ERROR)

    for attr in data["data"]:
        attr_rules = {
            "attribute_id": "required|integer",
            "value": "nullable"
        }
        attr_error = ValidatorService.validate(attr, attr_rules)
        if attr_error:
            return ResponseService.response('VALIDATION_ERROR', attr_error, Error.VALIDATION_ERROR)

    form_submission = QueryBuilderService("core_form_submissions").insert({
        "form_id": form_config["form_id"]
    })

    for attr in data["data"]:
        QueryBuilderService("core_form_submission_values").insert({
            "form_submission_id": form_submission["id"],
            "attribute_id": attr["attribute_id"],
            "value": attr["value"],
        })

    QueryBuilderService("crmp_policy_risk_reg_form_submissions").insert({
        "form_submission_id": form_submission["id"],
        "oppor_form_config_id": form_config["id"],
        "policy_id": policy_id,
    })

    return ResponseService.response('SUCCESS', None, "default_create_success_msg")

@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def get_single_form_config_info(request, policy_id, config_id, info_id):
    if request.method == 'GET':
        action = ActionService.getAction("Policy_Type", "VIEW")
        has_authority = AuthService.hasAuthority(request, action)

        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)

        return getSingle(request, info_id)

    elif request.method == 'PUT':
        action = ActionService.getAction("Policy_Type", "UPDATE")
        has_authority = AuthService.hasAuthority(request, action)

        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)

        return manage_policy_types(request, info_id)

    elif request.method == 'DELETE':
        action = ActionService.getAction("Policy_Type", "DELETE")
        has_authority = AuthService.hasAuthority(request, action)

        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)

        return delete(request, info_id)

    
def getSingle(request, id):
    data = QueryBuilderService("crm_opportunity_types")\
            .where("id", id) \
            .first()
            
    if data:
        return ResponseService.response('SUCCESS', data, Message.DATA_FETCHED)
    else:
        return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)


def manage_policy_types(request, id=None):
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
        return ResponseService.response('VALIDATION_ERROR', errors, Error.VALIDATION_ERROR)
    
    if id:
        updated_data = QueryBuilderService("crm_opportunity_types")\
                    .where("id", id) \
                    .update(data)
        if updated_data:
            return ResponseService.response('SUCCESS', updated_data, "default_update_success_msg")        
        else:
            return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)
    else:
        new_data = QueryBuilderService("crm_opportunity_types").insert(data)
        return ResponseService.response('SUCCESS', new_data, "default_create_success_msg")
    
def delete(request, id):

    QueryBuilderService("crm_oppor_opportunity_types")\
                    .where("opportunity_type_id", id) \
                    .delete()

    deleted_data = QueryBuilderService("crm_opportunity_types")\
                    .where("id", id) \
                    .delete()  
             
    if deleted_data:
        return ResponseService.response('SUCCESS', deleted_data, "default_delete_success_msg")
    else:
        return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
def clone_oppo_submissions(request, policy_id):
    data = json.loads(request.body)
    rules = {"opp_ids": "required|list"}
    error = ValidatorService.validate(data, rules)
    if error:
        return ResponseService.response('VALIDATION_ERROR', error, Error.VALIDATION_ERROR)

    opp_ids = data["opp_ids"]
    any_cloned = False

    for opp_id in opp_ids:
        original_rows = QueryBuilderService("crm_oppor_form_submissions") \
                            .where("opportunity_id", opp_id) \
                            .get()
        if not original_rows:
            continue

        any_cloned = True
        for row in original_rows:
            new_row = {k: v for k, v in row.items() if k != "id"}
            new_row["policy_id"] = policy_id
            QueryBuilderService("crmp_policy_risk_reg_form_submissions") \
                .insert(new_row)

    if not any_cloned:
        return ResponseService.response('NOT_FOUND', None, Error.NOT_FOUND)

    return ResponseService.response('SUCCESS', None, "default_create_success_msg")