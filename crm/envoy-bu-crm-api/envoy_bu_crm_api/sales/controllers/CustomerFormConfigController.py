import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from messages import Error, Message
from services.ActionService import ActionService
from services.AuthService import AuthService
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction


@csrf_exempt
@api_view(['GET', 'POST'])
def get_customer_form_config_info(request, customer_id, config_id):
    if request.method == 'GET':
        action = ActionService.getAction("Customer_Form_Config_Type", "VIEW")
        has_authority = AuthService.hasAuthority(request, action)
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)

        return get_all_by_customer(request, customer_id, config_id)

    elif request.method == 'POST':
        action = ActionService.getAction("Customer_Form_Config_Type", "CREATE")
        has_authority = AuthService.hasAuthority(request, action)
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)

        return save_form_submission_by_customer(request, customer_id, config_id)



def get_all_by_customer(request, customer_id, config_id):
    submissions = QueryBuilderService("crm_oppor_form_submissions") \
        .where("oppor_form_config_id", config_id) \
        .where("customer_id", customer_id).get()

    results = []
    for submission in submissions:
        values = QueryBuilderService("core_form_submission_valuess") \
            .select("custom_form_element_id", "value") \
            .where("form_submission_id", submission["form_submission_id"]).get()

        result_item = {str(v["custom_form_element_id"]): v["value"] for v in values}
        results.append(result_item)

    return ResponseService.response("SUCCESS", results, Message.DATA_FETCHED)



@transaction.atomic
def save_form_submission_by_customer(request, customer_id, config_id):
    form_config = QueryBuilderService("crm_opportunity_form_config") \
        .where("id", config_id).first()
    if not form_config:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    data = json.loads(request.body)
    rules = {"data": "required|dict"}
    error = ValidatorService.validate(data, rules)
    if error:
        return ResponseService.response("VALIDATION_ERROR", error, Error.VALIDATION_ERROR)

    values = data["data"]

    form_submission = QueryBuilderService("core_form_submissionss").insert({
        "form_id": form_config["form_id"],
        "user_id": request.user.id if request.user.is_authenticated else None,
        "customer_id": None
    })

    for custom_element_id_str, input_value in values.items():
        try:
            custom_form_element_id = int(custom_element_id_str)
            element = QueryBuilderService("core_form_custom_form_elements") \
                .select("element_id").where("id", custom_form_element_id).first()
            if not element:
                continue

            stored_value = json.dumps(input_value) if isinstance(input_value, (list, dict)) else input_value
            QueryBuilderService("core_form_submission_valuess").insert({
                "form_submission_id": form_submission["id"],
                "custom_form_element_id": custom_form_element_id,
                "form_element_id": element["element_id"],
                "value": stored_value
            })
        except Exception:
            continue

    QueryBuilderService("crm_oppor_form_submissions").insert({
        "form_submission_id": form_submission["id"],
        "oppor_form_config_id": form_config["id"],
        "customer_id": customer_id
    })

    return ResponseService.response("SUCCESS", {
        "form_submission_id": form_submission["id"]
    }, Message.DATA_CREATED)
