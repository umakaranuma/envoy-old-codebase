
import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from envoy_bu_crm_api.sales.models.core_models import CoreFormSubmission, CoreFormSubmissionValue, CoreTemplate
from envoy_bu_crm_api.sales.models.risk import Risk
from envoy_bu_crm_api.sales.models.submission_risk import RiskSubmission
from envoy_bu_crm_api.sales.models.opportunities import Opportunity
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message,Error
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone

from services.TemplateService import get_template_detail

@csrf_exempt
@api_view(['GET', 'POST'])
def get_form_config_info(request,opp_id,config_id):
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Form_Config_Type","VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return getAll(request,opp_id,config_id)
    
    elif request.method == 'POST':
        action = ActionService.getAction("Opportunity_Type","Create")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return save_oppo_form_sumition(request,opp_id,config_id)
    
def getAll(request, opp_id, config_id):
    # Fetch relevant submissions
    submissions = QueryBuilderService("crm_oppor_form_submissions")\
        .where("oppor_form_config_id", config_id)\
        .where("opportunity_id", opp_id).get()

    results = []

    for submission in submissions:
        form_submission_id = submission["form_submission_id"]

        # Fetch submitted values
        values = QueryBuilderService("core_form_submission_valuess")\
            .select("custom_form_element_id", "value")\
            .where("form_submission_id", form_submission_id).get()

        # Map element IDs to values and include submission ID
        result_item = {str(v["custom_form_element_id"]): v["value"] for v in values}
        result_item["form_submission_id"] = form_submission_id
        results.append(result_item)

    return ResponseService.response("SUCCESS", results, Message.DATA_FETCHED)


@transaction.atomic
def save_oppo_form_sumition(request, opp_id, config_id):
    form_config = QueryBuilderService("crm_opportunity_form_config").where("id", config_id).first()
    if not form_config:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    data = json.loads(request.body)

    rules = {
        "data": "required|dict"
    }
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

            # Fetch form_element_id from custom element table
            element = QueryBuilderService("core_form_custom_form_elements") \
                .select("element_id") \
                .where("id", custom_form_element_id).first()

            if not element:
                continue

            form_element_id = element["element_id"]
            stored_value = json.dumps(input_value) if isinstance(input_value, (list, dict)) else input_value

            QueryBuilderService("core_form_submission_valuess").insert({
                "form_submission_id": form_submission["id"],
                "custom_form_element_id": custom_form_element_id,
                "form_element_id": form_element_id,
                "value": stored_value
            })

        except Exception:
            continue

    # Always get customer_id from the opportunity
    opportunity = QueryBuilderService("crm_opportunities") \
        .select("id", "customer_id","entity_id") \
        .where("id", opp_id).first()
    customer_id = opportunity["customer_id"] if opportunity else None
    # entity_id = opportunity["entity_id"] if opportunity else None

    QueryBuilderService("crm_oppor_form_submissions").insert({
        "form_submission_id": form_submission["id"],
        "oppor_form_config_id": form_config["id"],
        "opportunity_id": opp_id,
        "customer_id": customer_id
    })

        # Create Risk entry
    # risk_type_id = form_config.get("risk_type_id")  # ensure this is part of the config if needed
    print("Form config:", form_config)
    risk_type_id = form_config.get("opportunity_type_id")
    print("risk_type_id:", risk_type_id)

    if customer_id and risk_type_id:
        # Create Risk entry first
        existing_risks = QueryBuilderService("crm_risks") \
            .select("id") \
            .where("is_deleted", False) \
            .orderBy("id", "DESC") \
            .first()

        next_number = existing_risks["id"] + 1 if existing_risks else 1
        risk_code = f"RISK-{str(next_number).zfill(4)}"

        risk_data = QueryBuilderService("crm_risks").insert({
            "id": next_number,
            "code": risk_code,
            "customer_id": customer_id,
            "risk_type_id": risk_type_id,
        })

        # Create RiskSubmission entry
        QueryBuilderService("crm_risk_submissions").insert({
            "risk_id": risk_data["id"],
            "submission_id": form_submission["id"],
            "lead_id": opp_id,
            "version": 1,
        })


    return ResponseService.response("SUCCESS", {
        "form_submission_id": form_submission["id"]
    }, Message.DATA_CREATED)


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def get_single_form_config_info(request, opp_id, config_id, info_id):
    if request.method == 'GET':
        action = ActionService.getAction("Opportunity_Type", "VIEW")
        has_authority = AuthService.hasAuthority(request, action)

        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)

        return getSingle(request, info_id)  # Assuming `info_id` is what you're using as ID

    elif request.method == 'PUT':
        action = ActionService.getAction("Opportunity_Type", "UPDATE")
        has_authority = AuthService.hasAuthority(request, action)

        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)

        return manage_opportunity_types(request, info_id)

    elif request.method == 'DELETE':
        action = ActionService.getAction("Opportunity_Type", "DELETE")
        has_authority = AuthService.hasAuthority(request, action)

        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.FORBIDDEN)

        return delete(request, info_id)

    
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

    QueryBuilderService("crm_oppor_opportunity_types")\
                    .where("opportunity_type_id",id) \
                    .delete()

    deleted_data = QueryBuilderService("crm_opportunity_types")\
                    .where("id",id) \
                    .delete()  
             
    if deleted_data:
        return ResponseService.response('SUCCESS',deleted_data,Message.DATA_CREATED)
    else:
        return ResponseService.response('NOT_FOUND',None,Error.NOT_FOUND)
    



@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def manage_form_submission(request, opp_id, form_submission_id):
    if request.method == 'GET':
        return get_form_submission(request, form_submission_id)

    elif request.method == 'PUT':
        return update_form_submission(request, form_submission_id)

    elif request.method == 'DELETE':
        return delete_form_submission(request, form_submission_id)



def get_form_submission(request, form_submission_id):
    # Step 1: Get form submission
    form_submission = QueryBuilderService("core_form_submissionss")\
        .where("id", form_submission_id).first()

    if not form_submission:
        return ResponseService.response("NOT_FOUND", None,Error.NOT_FOUND)

    form_id = form_submission["form_id"]

    # Step 2: Get full template object using ORM
    try:
        template = CoreTemplate.objects.get(id=form_id)
    except CoreTemplate.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Step 3: Get full template structure
    template_response = get_template_detail(template)
    try:
        template_data = json.loads(template_response.content.decode("utf-8"))
        if not template_data.get("is_success"):
            raise Exception("Template retrieval failed.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)

    template_result = template_data.get("result", {})
    elements = template_result.get("elements", [])

    # Step 4: Get stored values
    submission_values = QueryBuilderService("core_form_submission_valuess")\
        .select("custom_form_element_id", "value")\
        .where("form_submission_id", form_submission_id).get()

    value_dict = {
        str(val["custom_form_element_id"]): val["value"] for val in submission_values
    }

    # Step 5: Attach values to template elements
    for el in elements:
        el_id_str = str(el["id"])
        el["value"] = value_dict.get(el_id_str)

    # Step 6: Final response
    response_data = {
        "form_submission_id": form_submission_id,
        "form_id": form_id,
        "template": {
            "id": template.id,
            "name": template.title,
            "description": template.description,
            "type": template.type,
        },
        "steps": template_result.get("steps", []),
        "panels": template_result.get("panels", []),
        "elements": elements
    }

    return ResponseService.response("SUCCESS", response_data, Message.DATA_FETCHED)



@transaction.atomic
def update_form_submission(request, form_submission_id):
    data = json.loads(request.body)
    rules = { "data": "required|dict" }
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    new_values = data["data"]
    existing = QueryBuilderService("core_form_submission_valuess")\
        .where("form_submission_id", form_submission_id).get()
    existing_map = {str(v["custom_form_element_id"]): v for v in existing}

    for ceid_str, val in new_values.items():
        form_element_id = QueryBuilderService("core_form_custom_form_elements")\
            .select("element_id").where("id", ceid_str).first()["element_id"]
        stored_val = json.dumps(val) if isinstance(val, (list, dict)) else val

        if ceid_str in existing_map:
            QueryBuilderService("core_form_submission_valuess")\
                .where("form_submission_id", form_submission_id)\
                .where("custom_form_element_id", ceid_str)\
                .update({"value": stored_val})
        else:
            QueryBuilderService("core_form_submission_valuess").insert({
                "form_submission_id": form_submission_id,
                "custom_form_element_id": ceid_str,
                "form_element_id": form_element_id,
                "value": stored_val
            })

    return ResponseService.response("SUCCESS", {"form_submission_id": form_submission_id}, Message.DATA_UPDATED)





@transaction.atomic
def delete_form_submission(request, form_submission_id):
    # Delete form values
    QueryBuilderService("core_form_submission_valuess")\
        .where("form_submission_id", form_submission_id).delete()

    # Delete reference from opportunity submission
    QueryBuilderService("crm_oppor_form_submissions")\
        .where("form_submission_id", form_submission_id).delete()

    # Delete the actual form submission record
    deleted = QueryBuilderService("core_form_submissionss")\
        .where("id", form_submission_id).delete()

    if deleted:
        return ResponseService.response("SUCCESS", {"form_submission_id": form_submission_id}, Message.DATA_DELETED)
    else:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)




@api_view(["POST"])
@transaction.atomic
def save_multiple_oppo_form_submissions(request, opp_id, config_id):
    form_config = QueryBuilderService("crm_opportunity_form_config").where("id", config_id).first()
    if not form_config:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    data = json.loads(request.body)

    rules = {
        "data": "required|array"
    }
    error = ValidatorService.validate(data, rules)
    if error:
        return ResponseService.response("VALIDATION_ERROR", error, Error.VALIDATION_ERROR)

    all_submissions = data["data"]
    submission_ids = []

    opportunity = QueryBuilderService("crm_opportunities") \
        .select("id", "customer_id", "entity_id") \
        .where("id", opp_id).first()
    customer_id = opportunity["customer_id"] if opportunity else None
    # entity_id = opportunity["entity_id"] if opportunity else None
    risk_type_id = form_config.get("opportunity_type_id")

    for values in all_submissions:
        form_submission = QueryBuilderService("core_form_submissionss").insert({
            "form_id": form_config["form_id"],
            "user_id": request.user.id if request.user.is_authenticated else None,
            "customer_id": None
        })
        submission_ids.append(form_submission["id"])

        for custom_element_id_str, input_value in values.items():
            try:
                custom_form_element_id = int(custom_element_id_str)
                element = QueryBuilderService("core_form_custom_form_elements") \
                    .select("element_id") \
                    .where("id", custom_form_element_id).first()
                if not element:
                    continue

                form_element_id = element["element_id"]
                stored_value = json.dumps(input_value) if isinstance(input_value, (list, dict)) else input_value

                QueryBuilderService("core_form_submission_valuess").insert({
                    "form_submission_id": form_submission["id"],
                    "custom_form_element_id": custom_form_element_id,
                    "form_element_id": form_element_id,
                    "value": stored_value
                })

            except Exception:
                continue

        # Insert mapping
        QueryBuilderService("crm_oppor_form_submissions").insert({
            "form_submission_id": form_submission["id"],
            "oppor_form_config_id": form_config["id"],
            "opportunity_id": opp_id,
            "customer_id": customer_id
        })

    # Risk creation (only once per batch)
    if customer_id and risk_type_id:
        existing_risks = QueryBuilderService("crm_risks") \
            .select("id") \
            .where("is_deleted", False) \
            .orderBy("id", "DESC") \
            .first()
        next_number = existing_risks["id"] + 1 if existing_risks else 1
        risk_code = f"RISK-{str(next_number).zfill(4)}"

        risk_data = QueryBuilderService("crm_risks").insert({
            "id": next_number,
            "code": risk_code,
            "customer_id": customer_id,
            "risk_type_id": risk_type_id,
        })

        # Create RiskSubmission entry for the last form submission
        QueryBuilderService("crm_risk_submissions").insert({
            "risk_id": risk_data["id"],
            "submission_id": form_submission["id"],
            "lead_id": opp_id,
            "version": 1,
        })

    return ResponseService.response("SUCCESS", {
        "form_submission_ids": submission_ids
    }, Message.DATA_CREATED)





@api_view(["GET"])
def get_risks_by_type_and_lead_id(request, risk_type_id):
    print(f"=== DEBUG: get_risks_by_type_and_lead_id called with risk_type_id: {risk_type_id}")
    try:
        lead_id = request.query_params.get("lead_id")
        print(f"=== DEBUG: lead_id from query params: {lead_id}")
        if not lead_id:
            return ResponseService.response("VALIDATION_ERROR", None, "Lead ID is required.", system_code=400)

        # Fields similar to get_all_risks
        risk_columns = [
            "r.id",
            "r.code AS risk_code",
            "rt.title AS risk_type_title",
            "cust.id AS customer_id",
            "cust.name AS customer_name",
            "cust.logo AS customer_logo",
        ]

        print(f"=== DEBUG: Querying risks for risk_type_id: {risk_type_id}, lead_id: {lead_id}")
        risks = QueryBuilderService("crm_risk_submissions as rs") \
            .leftJoin("crm_risks as r", "r.id", "rs.risk_id") \
            .leftJoin("crm_opportunity_types AS rt", "rt.id", "r.risk_type_id") \
            .leftJoin("core_customers AS cust", "cust.id", "r.customer_id") \
            .select(*risk_columns, "rs.submission_id", "rs.version") \
            .where("r.risk_type_id", risk_type_id) \
            .where("rs.lead_id", lead_id) \
            .where("r.is_deleted", False) \
            .get()

        print(f"=== DEBUG: Found {len(risks)} risks (excluding deleted ones)")
        if not risks:
            return ResponseService.response("SUCCESS", [], "No risk details found for this type and customer.")

        results = []
        for risk in risks:
            submission_id = risk.get("submission_id")
            if not submission_id:
                continue

            submission = CoreFormSubmission.objects.select_related("form").filter(id=submission_id).first()
            if submission and submission.form:
                _, _, elements = fetch_elements_data(submission.form.id, submission_id=submission.id)
                result_item = {str(ele["id"]): ele.get("value") for ele in elements}
                result_item["submission_id"] = submission.id
                result_item["template_id"] = submission.form.id
                result_item["risk_detail_id"] = risk['id']
                results.append(result_item)



        return ResponseService.response("SUCCESS", results, "Risk details retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")




def fetch_elements_data(template_id, submission_id=None):
    steps = QueryBuilderService("core_form_custom_form_steps") \
        .select("*") \
        .where("form_id", template_id) \
        .get()

    panels = QueryBuilderService("core_form_custom_form_panels") \
        .select("*") \
        .where("form_id", template_id) \
        .orderBy("order_number") \
        .get()

    panel_ids = [panel["id"] for panel in panels]

    elements_query = QueryBuilderService("core_form_custom_form_elements as ele") \
        .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id") \
        .select("ele.*") \
        .whereIn("ele.panel_id", panel_ids if panel_ids else [0]) \
        .orderBy("ele.order_number") \
        .get()

    element_ids = [e["id"] for e in elements_query]

    values_dict = {}
    if submission_id:
        values_query = QueryBuilderService("core_form_submission_valuess") \
            .select("custom_form_element_id", "value") \
            .where("form_submission_id", submission_id) \
            .get()
        values_dict = {str(v["custom_form_element_id"]): v["value"] for v in values_query}

    elements = []
    for element in elements_query:
        options = QueryBuilderService("core_form_custom_form_element_options") \
            .select("*") \
            .where("element_id", element["id"]) \
            .get()
        element["options"] = options
        element["value"] = values_dict.get(str(element["id"])) if submission_id else None
        elements.append(element)

    return steps, panels, elements




@api_view(["POST"])
@transaction.atomic
def create_risk_detail(request):
    print("=== DEBUG: create_risk_detail function called ===")
    print(f"Request method: {request.method}")
    print(f"Request user: {request.user}")
    print(f"User authenticated: {request.user.is_authenticated if hasattr(request.user, 'is_authenticated') else 'No user object'}")
    
    data = request.data
    print(f"Request data: {data}")
    
    risk_type_id = data.get("risk_type_id")
    customer_id = data.get("customer_id")
    submitted_values = data.get("values", {})
    
    print(f"Parsed data - risk_type_id: {risk_type_id}, customer_id: {customer_id}, submitted_values: {submitted_values}")

    # Step 1: Validate input
    print("=== DEBUG: Starting validation ===")
    rules = {
        "risk_type_id": "required|exists:crm_opportunity_types,id",
        "customer_id": "exists:core_customers,id",
        "lead_id": "required|exists:crm_opportunities,id",
        "values": "dict"
    }
    print(f"Validation rules: {rules}")
    errors = ValidatorService.validate(data, rules)
    print(f"Validation errors: {errors}")
    if errors:
        print("=== DEBUG: Validation failed, returning error ===")
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation failed")
    
    print("=== DEBUG: Validation passed ===")

    # Step 2: Get form_id from onboarding config
    print("=== DEBUG: Getting form config ===")
    config = QueryBuilderService("crm_opportunity_form_config") \
        .select("form_id") \
        .where("opportunity_type_id", risk_type_id) \
        .where("data_gethering_type", "onboarding") \
        .first()
    
    print(f"Config found: {config}")

    if not config:
        print("=== DEBUG: No config found, returning error ===")
        return ResponseService.response("NOT_FOUND", None, "No onboarding form config found for this risk type.")

    form_id = config["form_id"]
    print(f"Form ID: {form_id}")
    
    template = CoreTemplate.objects.get(id=form_id)
    print(f"Template found: {template}")
    
    user = request.user
    print(f"User: {user}")

    # Step 3: Parse and validate template fields
    print("=== DEBUG: Building template response ===")
    template_response = build_template_response(template)
    print(f"Template response status: {template_response.status_code}")
    try:
        template_data = json.loads(template_response.content)
        print("=== DEBUG: Template data parsed successfully")
    except Exception as e:
        print(f"=== DEBUG: Template parsing failed: {str(e)}")
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

    if not template_data.get("is_success"):
        print("=== DEBUG: Template response not successful")
        return template_response

    elements = template_data.get("result", {}).get("elements", [])
    print(f"=== DEBUG: Found {len(elements)} elements")

    print("=== DEBUG: Building dynamic validation rules ===")
    dynamic_rules = {}
    custom_messages = {}
    for element in elements:
        eid = str(element["id"])
        label = element.get("label") or f"Element {eid}"
        if element.get("is_required"):
            dynamic_rules[eid] = "required"
            custom_messages[f"{eid}.required"] = f"{label} is required."

    print(f"=== DEBUG: Dynamic rules: {dynamic_rules}")
    print(f"=== DEBUG: Custom messages: {custom_messages}")
    
    errors = ValidatorService.validate(submitted_values, dynamic_rules, custom_messages)
    print(f"=== DEBUG: Form validation errors: {errors}")
    if errors:
        print("=== DEBUG: Form validation failed")
        return ResponseService.response("VALIDATION_ERROR", errors, "Form validation failed")
    
    print("=== DEBUG: Form validation passed")

    # Step 4: Create form submission and values
    print("=== DEBUG: Creating form submission ===")
    submission = CoreFormSubmission.objects.create(
        form=template,
        user=user if user.is_authenticated else None,
        customer_id=customer_id
    )
    print(f"=== DEBUG: Form submission created with ID: {submission.id}")

    print("=== DEBUG: Creating form submission values ===")
    values_to_create = [
        CoreFormSubmissionValue(
            form_submission=submission,
            custom_form_element_id=element["id"],
            form_element_id=element["element_id"],
            value=json.dumps(submitted_values[str(element["id"])])
            if isinstance(submitted_values[str(element["id"])], (dict, list))
            else submitted_values[str(element["id"])]
        )
        for element in elements if str(element["id"]) in submitted_values
    ]
    print(f"=== DEBUG: Created {len(values_to_create)} submission values")
    CoreFormSubmissionValue.objects.bulk_create(values_to_create)
    print("=== DEBUG: Form submission values created successfully")

    # Step 5: Create Risk record
    print("=== DEBUG: Creating Risk record ===")
    # Generate a unique code without manual ID assignment
    last_risk = Risk.objects.filter(is_deleted=False).order_by("-id").first()
    next_number = (last_risk.id + 1) if last_risk else 1
    code = f"RISK-{str(next_number).zfill(4)}"
    print(f"=== DEBUG: Next risk number: {next_number}, Code: {code}")

    risk = Risk.objects.create(
        code=code,
        customer_id=customer_id,
        risk_type_id=risk_type_id,
        is_deleted=False,
        deleted_at=None,
        deleted_by=None
    )
    print(f"=== DEBUG: Risk created with ID: {risk.id}")

    # Step 6: Create RiskSubmission record
    print("=== DEBUG: Creating RiskSubmission record ===")
    lead_id = data.get("lead_id")
    lead_instance = None
    if lead_id:
        try:
            lead_instance = Opportunity.objects.get(id=lead_id)
            print(f"=== DEBUG: Lead instance found: {lead_instance}")
        except Opportunity.DoesNotExist:
            print("=== DEBUG: Lead instance not found")
            lead_instance = None
    
    submission_risk = RiskSubmission.objects.create(
        risk=risk,
        submission_id=submission.id,
        lead=lead_instance,
        version=1
    )
    print(f"=== DEBUG: RiskSubmission created with ID: {submission_risk.id}")

    print("=== DEBUG: Returning success response ===")
    return ResponseService.response("SUCCESS", {
        "risk_id": risk.id,
        "risk_code": risk.code,
        "submission_id": submission.id
    }, Message.DATA_CREATED)



def build_template_response(template, submission_id=None):
    try:
        steps, panels, elements = fetch_template_data(template.id, submission_id=submission_id)

        result = {
            "template": {
                "id": template.id,
                "name": template.title,
                "description": template.description,
                "type": template.type,
            },
            "steps": steps,
            "panels": panels,
            "elements": elements
        }

        message = (
            "Template and submission values retrieved successfully."
            if submission_id else "Template details retrieved successfully."
        )

        return ResponseService.response("SUCCESS", result, message)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
from mServices.QueryBuilderService import QueryBuilderService


def fetch_template_data(template_id, submission_id=None):
    steps = QueryBuilderService("core_form_custom_form_steps") \
        .select("*") \
        .where("form_id", template_id) \
        .get()

    panels = QueryBuilderService("core_form_custom_form_panels") \
        .select("*") \
        .where("form_id", template_id) \
        .orderBy("order_number") \
        .get()
    panel_ids = [panel["id"] for panel in panels]

    elements_query = QueryBuilderService("core_form_custom_form_elements as ele") \
        .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id") \
        .select("ele.*") \
        .whereIn("ele.panel_id", panel_ids if panel_ids else [0]) \
        .orderBy("ele.order_number") \
        .get()

    element_ids = [e["id"] for e in elements_query]

    values_dict = {}
    if submission_id:
        values_query = QueryBuilderService("core_form_submission_valuess") \
            .select("custom_form_element_id", "value") \
            .where("form_submission_id", submission_id) \
            .get()
        values_dict = {str(v["custom_form_element_id"]): v["value"] for v in values_query}

    elements = []
    for element in elements_query:
        options = QueryBuilderService("core_form_custom_form_element_options") \
            .select("*") \
            .where("element_id", element["id"]) \
            .get()
        element["options"] = options
        element["value"] = values_dict.get(str(element["id"])) if submission_id else None
        elements.append(element)

    return steps, panels, elements




@csrf_exempt
@api_view(['GET', 'PUT','DELETE'])
def get_risk_detail_template_with_values(request,risk_detail_id):
    if request.method == 'GET':
        action = ActionService.getAction("RISK", "VIEW_ALL")
        if not AuthService.hasAuthority(request, action):
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        return get_risk_detail_template_and_values(request,risk_detail_id)

    elif request.method == 'PUT':
        action = ActionService.getAction("RISK", "EDIT")
        if not AuthService.hasAuthority(request, action):
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        return update_risk_detail(request,risk_detail_id)
    
    elif request.method == 'DELETE':
        action = ActionService.getAction("RISK", "DELETE")
        if not AuthService.hasAuthority(request, action):
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        return delete_risk(request,risk_detail_id)


def get_risk_detail_template_and_values(request, risk_detail_id):
    try:
        # Get submission_id from RiskSubmission table
        submission_risk = QueryBuilderService("crm_risk_submissions") \
            .select("submission_id") \
            .where("risk_id", risk_detail_id) \
            .first()

        if not submission_risk or not submission_risk.get("submission_id"):
            return ResponseService.response("NOT_FOUND", None, "Submission not found.")

        submission_id = submission_risk["submission_id"]
        submission = CoreFormSubmission.objects.select_related("form").filter(id=submission_id).first()

        if not submission or not submission.form:
            return ResponseService.response("NOT_FOUND", None, "Form or template not found.")

        return build_template_response(submission.form, submission_id=submission.id)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def build_template_response(template, submission_id=None):
    try:
        steps, panels, elements = fetch_template_data(template.id, submission_id=submission_id)

        result = {
            "template": {
                "id": template.id,
                "name": template.title,
                "description": template.description,
                "type": template.type,
            },
            "steps": steps,
            "panels": panels,
            "elements": elements
        }

        message = (
            "Template and submission values retrieved successfully."
            if submission_id else "Template details retrieved successfully."
        )

        return ResponseService.response("SUCCESS", result, message)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
from mServices.QueryBuilderService import QueryBuilderService


def fetch_template_data(template_id, submission_id=None):
    steps = QueryBuilderService("core_form_custom_form_steps") \
        .select("*") \
        .where("form_id", template_id) \
        .get()

    panels = QueryBuilderService("core_form_custom_form_panels") \
        .select("*") \
        .where("form_id", template_id) \
        .orderBy("order_number") \
        .get()
    panel_ids = [panel["id"] for panel in panels]

    elements_query = QueryBuilderService("core_form_custom_form_elements as ele") \
        .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id") \
        .select("ele.*") \
        .whereIn("ele.panel_id", panel_ids if panel_ids else [0]) \
        .orderBy("ele.order_number") \
        .get()

    element_ids = [e["id"] for e in elements_query]

    values_dict = {}
    if submission_id:
        values_query = QueryBuilderService("core_form_submission_valuess") \
            .select("custom_form_element_id", "value") \
            .where("form_submission_id", submission_id) \
            .get()
        values_dict = {str(v["custom_form_element_id"]): v["value"] for v in values_query}

    elements = []
    for element in elements_query:
        options = QueryBuilderService("core_form_custom_form_element_options") \
            .select("*") \
            .where("element_id", element["id"]) \
            .get()
        element["options"] = options
        element["value"] = values_dict.get(str(element["id"])) if submission_id else None
        elements.append(element)

    return steps, panels, elements




@transaction.atomic
def update_risk_detail(request, risk_detail_id):
    data = request.data
    submitted_values = data.get("values", {})

    # Step 1: Validate Risk exists
    try:
        risk = Risk.objects.get(id=risk_detail_id, is_deleted=False)
        # Get the submission from RiskSubmission
        submission_risk = RiskSubmission.objects.filter(risk_id=risk_detail_id).first()
        if not submission_risk:
            return ResponseService.response("NOT_FOUND", None, "Risk submission not found.")
    except Risk.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Risk not found.")

    # Step 2: Get template from risk_type
    config = QueryBuilderService("crm_opportunity_form_config") \
        .select("form_id") \
        .where("opportunity_type_id", risk.risk_type_id) \
        .where("data_gethering_type", "onboarding") \
        .first()

    if not config:
        return ResponseService.response("NOT_FOUND", None, "No onboarding form config found for this risk type.")

    form_id = config["form_id"]
    template = CoreTemplate.objects.get(id=form_id)

    # Step 3: Parse template fields
    template_response = build_template_response(template)
    try:
        template_data = json.loads(template_response.content)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

    if not template_data.get("is_success"):
        return template_response

    elements = template_data.get("result", {}).get("elements", [])

    # Step 4: Validation based on template rules
    dynamic_rules = {}
    custom_messages = {}
    for element in elements:
        eid = str(element["id"])
        label = element.get("label") or f"Element {eid}"
        if element.get("is_required"):
            dynamic_rules[eid] = "required"
            custom_messages[f"{eid}.required"] = f"{label} is required."

    errors = ValidatorService.validate(submitted_values, dynamic_rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Form validation failed")

    # Step 5: Update existing CoreFormSubmission values
    form_submission = CoreFormSubmission.objects.get(id=submission_risk.submission_id)
    existing_values_qs = CoreFormSubmissionValue.objects.filter(form_submission=form_submission)
    existing_values_dict = {str(v.custom_form_element_id): v for v in existing_values_qs}

    for element in elements:
        element_id_str = str(element["id"])
        if element_id_str not in submitted_values:
            continue
        value = submitted_values[element_id_str]
        formatted_value = json.dumps(value) if isinstance(value, (dict, list)) else value

        if element_id_str in existing_values_dict:
            # Update
            entry = existing_values_dict[element_id_str]
            entry.value = formatted_value
            entry.save()
        else:
            # Create new value if missing
            CoreFormSubmissionValue.objects.create(
                form_submission=form_submission,
                custom_form_element_id=element["id"],
                form_element_id=element["element_id"],
                value=formatted_value
            )

    # Step 6: Update Risk metadata if needed
    if "customer_id" in data:
        risk.customer_id = data.get("customer_id")
        risk.save()
    
    # Update RiskSubmission if lead_id changes
    if "lead_id" in data:
        submission_risk.lead_id = data.get("lead_id")
        submission_risk.save()

    return ResponseService.response("SUCCESS", {
        "risk_id": risk.id,
        "risk_code": risk.code,
        "submission_id": form_submission.id
    }, Message.DATA_UPDATED)


@transaction.atomic
def delete_risk(request, risk_detail_id):
    print(f"=== DEBUG: delete_risk called with risk_detail_id: {risk_detail_id}")
    try:
        # Validation
        rules = {
            "risk_id": "required|exists:crm_risks,id"
        }
        custom_messages = {
            "risk_id.required": "Risk ID is required.",
            "risk_id.exists": "Risk with the given ID does not exist."
        }

        print(f"=== DEBUG: Validating risk_id: {risk_detail_id}")
        errors = ValidatorService.validate({"risk_id": risk_detail_id}, rules, custom_messages)
        print(f"=== DEBUG: Validation errors: {errors}")
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Get the risk record
        print(f"=== DEBUG: Looking for risk with id: {risk_detail_id}")
        try:
            risk = Risk.objects.get(id=risk_detail_id, is_deleted=False)
            print(f"=== DEBUG: Risk found: {risk}")
        except Risk.DoesNotExist:
            print(f"=== DEBUG: Risk with id {risk_detail_id} does not exist or is already deleted")
            # Check if the risk exists but is deleted
            deleted_risk = Risk.objects.filter(id=risk_detail_id, is_deleted=True).first()
            if deleted_risk:
                return ResponseService.response("NOT_FOUND", None, "Risk has already been deleted.")
            else:
                return ResponseService.response("NOT_FOUND", None, "Risk not found.")

        # Perform soft delete
        risk.is_deleted = True
        risk.deleted_at = timezone.now()
        risk.deleted_by = request.user if request.user.is_authenticated else None
        risk.save()

        return ResponseService.response("SUCCESS", {
            "risk_id": risk.id,
            "risk_code": risk.code,
            "deleted_at": risk.deleted_at,
            "deleted_by": risk.deleted_by.id if risk.deleted_by else None
        }, Message.DATA_DELETED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

