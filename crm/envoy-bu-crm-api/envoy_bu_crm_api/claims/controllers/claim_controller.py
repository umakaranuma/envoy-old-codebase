# from asyncio.log import logger
# from django.utils import timezone
# import json
# from math import ceil
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from mServices import ResponseService, QueryBuilderService, ValidatorService

# from envoy_bu_crm_api.claims.models.claim import Claim
# from envoy_bu_crm_api.claims.models.claim_form_config import ClaimFormConfig
# from envoy_bu_crm_api.claims.models.claim_form_submission import ClaimFormSubmission
# from envoy_bu_crm_api.policy.models.crmp_issued_policies import IssuedPolicy
# from envoy_bu_crm_api.policy.models.crmp_policy_base import PolicyBase
# from envoy_bu_crm_api.sales.models.core_models import ServiceProvider
# from envoy_bu_crm_api.quotation.services.send_mail_service import SendMail
# from envoy_bu_crm_api.sales.models.core_models import Contact, CoreFormSubmission, CoreFormSubmissionValue, CoreTemplate, CustomerAdditionalContact, FormAttribute, Status
# from envoy_bu_crm_api.sales.models.opportunity_form_config import OpportunityFormConfig
# from messages import Error
# from django.db import transaction

# from services.ActionService import ActionService
# from services.AuthService import AuthService
# from django.views.decorators.csrf import csrf_exempt


# #-------------Get Customer List-------------------
# @api_view(["GET"])
# def get_all_customers(request):
#     try:
#         # Extract query parameters
#         fields = request.GET.get('fields', None)
#         search_string = request.GET.get('search', '')
#         page = int(request.GET.get('page', 1))
#         limit = int(request.GET.get('limit', 10))
#         sort_by = request.GET.get('sort_by', 'customer.id')
#         sort_dir = request.GET.get('sort_dir', 'asc')
#         ids = request.GET.get('ids', None)

#         # Define columns to select
#         all_columns = [
#             "customer.id",
#             "customer.code",
#             "customer.name",
#             "customer.type",
#             "customer.logo",
#             "customer.remarks",
#             "customer.primary_contact_id",
#             "contact.name AS contact_name",
#             "contact.email AS contact_email",
#             "contact.primary_contact AS contact_primary_contact",
#             "contact.address AS contact_address",
#             "contact.picture AS contact_picture"
#         ]

#         # Initialize query builder
#         data = (
#             QueryBuilderService("core_customers as customer")
#             .leftJoin("core_contacts as contact", "contact.id", "customer.primary_contact_id")
#         )

#         # Apply filters and search
#         allowed_filters = ['customer.name', 'customer.type']
#         search_columns = ["customer.name", "contact.name", "contact.primary_contact"]
#         filter_json = request.GET.get('filters', '{}')
#         data = data.select(*all_columns).apply_conditions(filter_json, allowed_filters, search_string, search_columns)

#         # Filter by IDs if provided
#         if ids:
#             id_list = ids.split(',')
#             data = data.whereIn("customer.id", id_list).get()
#         else:
#             data = data.paginate(page, limit, allowed_sorting_columns=['customer.name', 'customer.id'], sort_by=sort_by, sort_dir=sort_dir)

#         # If 'fields=additional', fetch related policies
#         if fields == 'additional' and isinstance(data, dict) and 'data' in data:
#             items = data['data']
#             for item in items:
#                 customer_id = item.get('id')
#                 # Fetch related policies for the customer
#                 policies = (
#                     QueryBuilderService("crmp_issued_policies as issued")
#                     .leftJoin("crmp_policy_base as base", "base.id", "issued.policy_base_id")
#                     .leftJoin("crm_opportunity_types as risk", "risk.id", "base.risk_type_id")
#                     .select(
#                         "issued.id",
#                         "issued.brokerage_policy_id",
#                         "issued.start_date",
#                         "issued.end_date",
#                         "issued.premium_amount",
#                         "issued.sum_insured",
#                         "issued.policy_base_id",
#                         "base.risk_type_id",
#                         "risk.title AS risk_type_title"
#                     )
#                     .where("base.customer_id", customer_id)
#                     .get()
#                 )
#                 item['policies'] = policies

#         return ResponseService.response("SUCCESS", data, "Customers retrieved successfully.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server error")



# #-------------Get Customer Policies-------------------
# @api_view(["GET"])
# def get_customer_policies(request, customer_id):
#     try:
#         # Extract and validate pagination and sorting parameters
#         page = int(request.GET.get("page", 1))
#         limit = int(request.GET.get("limit", 10))
#         sort_by = request.GET.get("sort_by") or "issued.id"
#         sort_dir = request.GET.get("sort_dir") or "asc"

#         # Fetch data with JOINs and additional form_id
#         raw_data = (
#             QueryBuilderService("crmp_issued_policies as issued")
#             .leftJoin("crmp_policy_base as base", "base.id", "issued.policy_base_id")
#             .leftJoin("crm_opportunity_types as risk", "risk.id", "base.risk_type_id")
#             .leftJoin("crm_opportunity_form_config as config", "config.opportunity_type_id", "base.risk_type_id")
#             .select(
#                 "issued.id",
#                 "issued.brokerage_policy_id",
#                 "issued.start_date",
#                 "issued.end_date",
#                 "issued.premium_amount",
#                 "issued.sum_insured",
#                 "issued.policy_base_id",
#                 "base.risk_type_id",
#                 "risk.title AS risk_type_title",
#                 "config.data_gethering_type AS data_gathering_type",
#                 "config.form_id"
#             )
#             .where("base.customer_id", customer_id)
#             .orderBy(sort_by, sort_dir)
#             .get()
#         )

#         # Group and transform data by policy id
#         policy_map = {}
#         for item in raw_data:
#             policy_id = item["id"]
#             if policy_id not in policy_map:
#                 policy_map[policy_id] = {
#                     "id": item["id"],
#                     "brokerage_policy_id": item["brokerage_policy_id"],
#                     "start_date": item["start_date"],
#                     "end_date": item["end_date"],
#                     "premium_amount": item["premium_amount"],
#                     "sum_insured": item["sum_insured"],
#                     "policy_base_id": item["policy_base_id"],
#                     "risk_type_id": item["risk_type_id"],
#                     "risk_type_title": item["risk_type_title"]
#                 }
#             if item["data_gathering_type"] and item["form_id"]:
#                 key = f'{item["data_gathering_type"]}_template_id'
#                 policy_map[policy_id][key] = item["form_id"]

#         # Manual pagination
#         transformed_data = list(policy_map.values())
#         total_records = len(transformed_data)
#         start = (page - 1) * limit
#         end = start + limit
#         paginated_data = transformed_data[start:end]

#         # Build final response structure
#         result = {
#             "total_records": total_records,
#             "per_page": limit,
#             "current_page": page,
#             "last_page": ceil(total_records / limit),
#             "data": paginated_data
#         }

#         return ResponseService.response("SUCCESS", result, "default_get_success_msg")

#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server error")
# #-------------Get Template by Policy_Id-------------------
# @api_view(["GET"])
# def get_template_by_policy(request, policy_id):
#     try:
#         policy = IssuedPolicy.objects.select_related(
#             "policy_base__risk_type",
#             "policy_base__insurer",
#             "policy_base__customer",
#             "policy_base__product",
#             "policy_base__request_by",
#             "policy_base__request_type",
#             "policy_base__coverage_type",
#             "policy_base__payment_mode",
#             "entity__created_by",
#             "entity__updated_by"
#         ).get(id=policy_id)

#         risk_type = policy.policy_base.risk_type if policy.policy_base else None

#         form_id = None
#         if risk_type:
#             try:
#                 form_config = OpportunityFormConfig.objects.filter(
#                     opportunity_type=risk_type,
#                     data_gethering_type=OpportunityFormConfig.CLAIM
#                 ).first()
#                 form_id = form_config.form_id if form_config else None
#             except OpportunityFormConfig.DoesNotExist:
#                 pass

#         data = build_template_response(policy, form_id)
#         return ResponseService.response("SUCCESS", data, "Template and policy details retrieved successfully.")

#     except IssuedPolicy.DoesNotExist:
#         return ResponseService.response("NOT_FOUND", {"policy_id": "Policy not found."}, "Invalid policy ID.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve template and policy details.")



# #-------------Get Template by Claim_Id-------------------


# @api_view(["GET"])
# def get_template_by_claim(request, claim_id):
#     try:
#         claim = Claim.objects.select_related(
#             "policy__policy_base__risk_type",
#             "policy__policy_base__insurer",
#             "policy__policy_base__customer",
#             "policy__policy_base__product",
#             "policy__policy_base__request_by",
#             "policy__policy_base__request_type",
#             "policy__policy_base__coverage_type",
#             "policy__policy_base__payment_mode",
#             "policy__entity__created_by",
#             "policy__entity__updated_by"
#         ).get(id=claim_id)

#         policy = claim.policy
#         risk_type = policy.policy_base.risk_type if policy and policy.policy_base else None

#         form_id = None
#         if risk_type:
#             try:
#                 form_config = OpportunityFormConfig.objects.get(
#                     opportunity_type=risk_type,
#                     data_gethering_type=OpportunityFormConfig.CLAIM_EVALUATION
#                 )
#                 form_id = form_config.form_id
#             except OpportunityFormConfig.DoesNotExist:
#                 logger.warning(f"No OpportunityFormConfig for risk_type ID {risk_type.id} and CLAIM_EVALUATION")

#         data = build_template_response(policy, form_id)
#         return ResponseService.response("SUCCESS", data, "Template and policy details retrieved successfully.")

#     except Claim.DoesNotExist:
#         return ResponseService.response("NOT_FOUND", {"claim_id": "Claim not found."}, "Invalid claim ID.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve template and policy details.")

# @api_view(['GET', 'PUT'])
# def claim_evaluation_details(request, claim_id):
#     if request.method == 'GET':
#         return get_claim_detail(request, claim_id, ClaimFormSubmission.EVALUATION)
#     elif request.method == 'PUT':
#         return update_claim_submission(request, claim_id, ClaimFormSubmission.EVALUATION)
#     # elif request.method == 'DELETE':
#     #     return delete_claim(request, claim_id, ClaimFormSubmission.EVALUATION)


# @api_view(['POST'])
# @transaction.atomic
# def submit_claim_evaluation(request, claim_id, submission_type):
#     data = request.data
#     form_id = data.get("form_id")
#     submitted_values = data.get("values", {})

#     # Step 1: Basic validation
#     rules = {
#         "form_id": "required|exists:core_templates,id",
#         "values": "required|dict",
#     }

#     errors = ValidatorService.validate(data, rules)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#     try:
#         claim = Claim.objects.get(id=claim_id)
#     except Claim.DoesNotExist:
#         return ResponseService.response("NOT_FOUND", {"claim_id": "Claim not found."}, "Invalid claim ID.")

#     template = CoreTemplate.objects.get(id=form_id)
#     user = request.user

#     # Step 2: Get and parse template
#     template_response = get_template_detail(template)
#     try:
#         template_data = json.loads(template_response.content)
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

#     if not template_data.get("is_success"):
#         return template_response

#     elements = template_data.get("result", {}).get("elements", [])

#     # Step 3: Validate required fields
#     dynamic_rules = {}
#     custom_messages = {}
#     for element in elements:
#         eid = str(element["id"])
#         label = element.get("label") or f"Element {eid}"
#         if element.get("is_required"):
#             dynamic_rules[eid] = "required"
#             custom_messages[f"{eid}.required"] = f"{label} is required."

#     errors = ValidatorService.validate(submitted_values, dynamic_rules, custom_messages)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Form validation failed")

#     # Step 4: Create form submission and values
#     submission = CoreFormSubmission.objects.create(form=template, user=user)

#     values_to_create = [
#         CoreFormSubmissionValue(
#             form_submission=submission,
#             custom_form_element_id=element["id"],
#             form_element_id=element["element_id"],
#             value=submitted_values[str(element["id"])]
#         )
#         for element in elements if str(element["id"]) in submitted_values
#     ]
#     CoreFormSubmissionValue.objects.bulk_create(values_to_create)

#     # Step 5: Link to claim as EVALUATION
#     ClaimFormSubmission.objects.create(
#         claim=claim,
#         form_submission=submission,
#         submission_type=submission_type
#     )

#     return ResponseService.response("SUCCESS", {
#         "submission_id": submission.id,
#         "claim_id": claim.id,
#         "claim_code": claim.code,
#     }, "Evaluation submitted successfully.")


# #----------------------Claim Get-All & Create ----------------------------
# @csrf_exempt
# @api_view(['GET', 'POST'])
# def claim(request):
#     if request.method == 'GET':
#         action = ActionService.getAction("CLAIM", "VIEW_ALL")
#         has_authority = AuthService.hasAuthority(request, action)
        
#         if not has_authority:
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        
#         return get_all_claims(request)
    
#     elif request.method == 'POST':
#         action = ActionService.getAction("CLAIM", "CREATE")
#         has_authority = AuthService.hasAuthority(request, action)
        
#         if not has_authority:
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        
#         return create_claim(request)

# #----------------------Claim Get-All ----------------------------
# def get_all_claims(request):
#     try:
#         # Query parameters
#         search_string = request.GET.get('search', '')
#         page = int(request.GET.get('page', 1))
#         limit = int(request.GET.get('limit', 10))
#         sort_by = request.GET.get('sort_by', 'claim.id')
#         sort_dir = request.GET.get('sort_dir', 'desc')
#         ids = request.GET.get('ids', None)
#         filter_json = request.GET.get('filters', '{}')

#         # Select fields
#         all_columns = [
#             "claim.*",
#             "policy.brokerage_policy_id",
#             "risk.title as risk_type_title",
#             "insurer.name as insurer_name",
#             "form.title as template_title",
#             "customer.id as customer_id",

#             "customer.name as customer_name",
#             "status.name as status_name",
#             "status.color as status_color",
#         ]

#         # Build base query
#         query = (
#             QueryBuilderService("crmp_claims as claim")
#             .leftJoin("crmp_issued_policies as policy", "policy.id", "claim.policy_id")
#             .leftJoin("crmp_policy_base as base", "base.id", "policy.policy_base_id")
#             .leftJoin("core_customers as customer", "customer.id", "base.customer_id")
#             .leftJoin("crm_opportunity_types as risk", "risk.id", "claim.risk_type_id")
#             .leftJoin("core_service_providers as insurer", "insurer.id", "claim.insurer_id")
#             .leftJoin("core_templates as form", "form.id", "claim.template_id")
#             .leftJoin("core_status as status", "status.id", "claim.status_id")
#             .select(*all_columns)
#             .apply_conditions(filter_json, [], search_string, ["claim.code", "status.name", "risk.title", "insurer.name"])
#         )

#         # Filter by IDs if provided
#         if ids:
#             id_list = ids.split(',')
#             data = query.whereIn("claim.id", id_list).get()
#         else:
#             data = query.paginate(page, limit, ['claim.code', 'claim.id'], sort_by, sort_dir)

#         return ResponseService.response("SUCCESS", data, "Claims retrieved successfully.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch claims.")



# #----------------------Claim Create ----------------------------
# @transaction.atomic
# def create_claim(request):
#     data = request.data
#     form_id = data.get("form_id")
#     submitted_values = data.get("values", {})

#     # Step 1: Validate required input
#     rules = {
#         "form_id": "required|exists:core_templates,id",
#         "policy_id": "required|exists:crmp_issued_policies,id",
#         "is_myself": "required|boolean",
#         "remarks": "nullable|string",
#         "values": "required|dict",
#         "reporter_name": "nullable|string",
#         "reporter_contact": "nullable|string",
#         "reporter_relationship": "nullable|string"
#     }

#     errors = ValidatorService.validate(data, rules)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#     user = request.user
#     template = CoreTemplate.objects.get(id=form_id)

#     # Step 2: Get template details and elements
#     template_response = get_template_detail(template)
#     try:
#         template_data = json.loads(template_response.content)
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

#     if not template_data.get("is_success"):
#         return template_response

#     elements = template_data.get("result", {}).get("elements", [])

#     # Step 3: Validate required fields from template
#     dynamic_rules = {}
#     custom_messages = {}
#     for element in elements:
#         eid = str(element["id"])
#         label = element.get("label") or f"Element {eid}"
#         if element.get("is_required"):
#             dynamic_rules[eid] = "required"
#             custom_messages[f"{eid}.required"] = f"{label} is required."

#     errors = ValidatorService.validate(submitted_values, dynamic_rules, custom_messages)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Form validation failed")

#     # Step 4: Create submission record
#     submission = CoreFormSubmission.objects.create(form=template, user=user)

#     values_to_create = [
#         CoreFormSubmissionValue(
#             form_submission=submission,
#             custom_form_element_id=element["id"],
#             form_element_id=element["element_id"],
#             value=submitted_values[str(element["id"])]
#         )
#         for element in elements if str(element["id"]) in submitted_values
#     ]
#     CoreFormSubmissionValue.objects.bulk_create(values_to_create)

#     # Step 5: Create related claim
#     policy = IssuedPolicy.objects.select_related("policy_base__risk_type", "policy_base__insurer").get(id=data["policy_id"])
#     policy_base = policy.policy_base
#     risk_type = policy_base.risk_type if policy_base else None
#     insurer = policy_base.insurer if policy_base else None
#     customer = policy_base.customer.id if policy_base and policy_base.customer else None

#     # Step 6: Get evaluation form based on OpportunityFormConfig
#     evaluation_template = None
#     if risk_type:
#         try:
#             form_config = OpportunityFormConfig.objects.get(
#                 opportunity_type=risk_type,
#                 data_gethering_type=OpportunityFormConfig.CLAIM_EVALUATION
#             )
#             evaluation_template = CoreTemplate.objects.get(id=form_config.form_id)
#         except (OpportunityFormConfig.DoesNotExist, CoreTemplate.DoesNotExist):
#             evaluation_template = None  # Optionally log this

#     draft_status = Status.objects.filter(name="Draft", module="Claim").first()
#     if not draft_status:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Draft status not found.")

#     # Step 7: Save the claim
#     claim = Claim.objects.create(
#         policy=policy,
#         customer_id=customer,
#         remarks=data.get("remarks", ""),
#         risk_type=risk_type,
#         insurer=insurer,
#         template=template,
#         evaluation_form=evaluation_template,
#         is_myself=data.get("is_myself", True),
#         reporter_name=data.get("reporter_name"),
#         reporter_contact=data.get("reporter_contact"),
#         reporter_relationship=data.get("reporter_relationship"),
#         status=draft_status,
#     )

#     # Step 8: Link the submission to the claim
#     ClaimFormSubmission.objects.create(
#         claim=claim,
#         form_submission=submission,
#         submission_type=ClaimFormSubmission.INCIDENT_INFO
#     )

#     # Create empty submission for evaluation form
#     if evaluation_template:
#         evaluation_submission = CoreFormSubmission.objects.create(form=evaluation_template, user=user)

#         # Link to the claim
#         ClaimFormSubmission.objects.create(
#             claim=claim,
#             form_submission=evaluation_submission,
#             submission_type=ClaimFormSubmission.EVALUATION
#         )

#     # Step 9: Return success response
#     return ResponseService.response("SUCCESS", {
#         "submission_id": submission.id,
#         "claim_id": claim.id,
#         "claim_code": claim.code,
#         "claim_status": claim.status.name,
#         "claim_status_id": claim.status.id,
#     }, "default_create_success_msg")


 
# #----------------------Claim Get-By-ID, Update & Delete ----------------------------
# @csrf_exempt
# @api_view(['GET', 'PUT', 'DELETE'])
# def claim_details(request,claim_id):
#     submission_type= ClaimFormSubmission.INCIDENT_INFO
#     if request.method == 'GET':
#         action = ActionService.getAction("CLAIM", "VIEW")
#         has_authority = AuthService.hasAuthority(request, action)
        
#         if not has_authority:
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        
#         return get_claim_detail(request,claim_id, submission_type)
    
#     elif request.method == 'PUT':
#         action = ActionService.getAction("CLAIM", "EDIT")
#         has_authority = AuthService.hasAuthority(request, action)
        
#         if not has_authority:
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        
#         return update_claim_submission(request,claim_id,submission_type)
    
#     elif request.method == 'DELETE':
#         action = ActionService.getAction("CLAIM", "DELETE")
#         has_authority = AuthService.hasAuthority(request, action)
#         if not has_authority:
#             return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
#         return delete_claim(request, claim_id, submission_type)



# #----------------------Claim Get-By-ID ----------------------------
# def get_claim_detail(request, claim_id, submission_type):
#     try:
#         # Step 1: Validate claim_id
#         rules = {"claim_id": "required|exists:crmp_claims,id"}
#         errors = ValidatorService.validate({"claim_id": claim_id}, rules)
#         if errors:
#             return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#         # Step 2: Retrieve the claim with related entities
#         claim = Claim.objects.select_related(
#             "policy__policy_base__risk_type",
#             "policy__policy_base__insurer",
#             "policy__policy_base__customer",
#             "policy__policy_base__product",
#             "template",
#             "evaluation_form"
#         ).get(id=claim_id)

#         # Step 3: Determine the appropriate template based on submission_type
#         if submission_type == ClaimFormSubmission.EVALUATION:
#             template = claim.evaluation_form
#         else:
#             template = claim.template

#         if not template:
#             return ResponseService.response("NOT_FOUND", None, "Template not found for this claim.")

#         # Step 4: Retrieve the associated form submission
#         claim_submission = ClaimFormSubmission.objects.select_related("form_submission").filter(
#             claim=claim,
#             submission_type=submission_type
#         ).first()

#         if not claim_submission:
#             return ResponseService.response("NOT_FOUND", None, "Form submission not found for this claim.")

#         form_submission = claim_submission.form_submission

#         # Step 5: Retrieve all submission values
#         submission_values = CoreFormSubmissionValue.objects.filter(form_submission=form_submission)

#         # Step 6: Build a dictionary of values keyed by custom_form_element_id
#         values_dict = {
#             str(value.custom_form_element_id): value.value
#             for value in submission_values
#         }

#         # Step 7: Retrieve the template details
#         template_response = get_template_detail(template)
#         try:
#             template_data = json.loads(template_response.content.decode('utf-8'))
#         except Exception as e:
#             return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

#         if not template_data.get("is_success"):
#             return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Failed to retrieve template details.")

#         result = template_data.get("result", {})
#         elements = result.get("elements", [])

#         # Step 8: Attach the stored values to the corresponding elements
#         for element in elements:
#             element_id_str = str(element["id"])
#             element["value"] = values_dict.get(element_id_str)

#         # Step 9: Construct the response data
#         response_data = {
#             "claim_id": claim.id,
#             "claim_code": claim.code,
#             "claim_status": claim.status.name,
#             "claim_status_color": claim.status.color,
#             "template": {
#                 "id": template.id,
#                 "name": template.title,
#                 "description": template.description,
#                 "type": template.type,
#             },
#             "steps": result.get("steps", []),
#             "panels": result.get("panels", []),
#             "elements": elements
#         }

#         return ResponseService.response("SUCCESS", response_data, "Claim details retrieved successfully.")

#     except Claim.DoesNotExist:
#         return ResponseService.response("NOT_FOUND", None, "Claim not found.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve claim details.")


# #----------------------Claim Update ----------------------------
# @transaction.atomic
# def update_claim_submission(request, claim_id, submission_type):
#     data = request.data

#     # Step 1: Validate input
#     rules = {
#         "values": "required|dict",
#         "is_completed": "boolean"
#     }
#     errors = ValidatorService.validate(data, rules)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#     try:
#         claim = Claim.objects.select_related("template", "evaluation_form").get(id=claim_id)
#     except Claim.DoesNotExist:
#         return ResponseService.response("NOT_FOUND", None, "Claim not found.")

#     # Prevent update if claim is already submitted
#     if claim.status and claim.status.name == "Submitted":
#         return ResponseService.response("FORBIDDEN", None, "default_update_forbidden_msg")

#     # Step 2: Determine the correct template based on submission_type
#     template = claim.evaluation_form if submission_type == ClaimFormSubmission.EVALUATION else claim.template
#     if not template:
#         return ResponseService.response("NOT_FOUND", None, "Template not found for this claim.")

#     # Step 3: Retrieve the associated form submission
#     claim_submission = ClaimFormSubmission.objects.select_related("form_submission").filter(
#         claim=claim, submission_type=submission_type
#     ).first()
#     if not claim_submission:
#         return ResponseService.response("NOT_FOUND", None, "Form submission not found for this claim.")

#     form_submission = claim_submission.form_submission

#     # Step 4: Load form elements to match `custom_form_element_id` to `form_element_id`
#     template_response = get_template_detail(template)
#     try:
#         template_data = json.loads(template_response.content.decode("utf-8"))
#         elements = template_data.get("result", {}).get("elements", [])
#         element_id_map = {
#             str(el["id"]): el["element_id"]
#             for el in elements if "id" in el and "element_id" in el
#         }
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

#     # Step 5: Update or create values
#     submitted_values = data.get("values", {})
#     existing_values_qs = CoreFormSubmissionValue.objects.filter(form_submission=form_submission)
#     existing_values_dict = {
#         str(v.custom_form_element_id): v for v in existing_values_qs
#     }

#     for element_id_str, value in submitted_values.items():
#         form_element_id = element_id_map.get(element_id_str)
#         if not form_element_id:
#             continue  # Skip if no valid form_element_id found

#         if element_id_str in existing_values_dict:
#             entry = existing_values_dict[element_id_str]
#             entry.value = value
#             entry.save()
#         else:
#             CoreFormSubmissionValue.objects.create(
#                 form_submission=form_submission,
#                 custom_form_element_id=element_id_str,
#                 form_element_id=form_element_id,
#                 value=value
#             )

#     # Step 6: Update claim status if is_completed is True
#     if data.get("is_completed") is True:
#         submitted_status = Status.objects.filter(name="Submitted", module="Claim").first()
#         if not submitted_status:
#             return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Submitted status not found.")
#         claim.status = submitted_status
#         claim.save(update_fields=["status"])

#         send_claim_emails(request._request.__class__(data={"claim_ids": [claim_id]}))

#     return ResponseService.response("SUCCESS", {"claim_id": claim.id}, "default_update_success_msg")


# #----------------------Claim Delete ----------------------------
# @transaction.atomic
# def delete_claim(request, claim_id,submission_type):
#     try:
#         claim = Claim.objects.get(id=claim_id)

#         # Delete related form submission if exists
#         claim_submission = ClaimFormSubmission.objects.filter(claim=claim,submission_type=submission_type).first()
#         if claim_submission:
#             CoreFormSubmissionValue.objects.filter(form_submission=claim_submission.form_submission).delete()
#             claim_submission.form_submission.delete()
#             claim_submission.delete()

#         # Delete the claim
#         claim.delete()

#         return ResponseService.response("SUCCESS", {"claim_id": claim_id}, "default_delete_success_msg")

#     except Claim.DoesNotExist:
#         return ResponseService.response("NOT_FOUND", None, "Claim not found.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "default_delete_error_msg")


# @api_view(["POST"])
# def send_claim_emails(request):
#     data = request.data

#     # Validate claim_ids with ValidatorService
#     rules = {
#         "claim_ids": "required|array|min:1"
#     }

#     errors = ValidatorService.validate(data, rules, {})
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Validation failed.")

#     claim_ids = data.get("claim_ids", [])

#     claims = Claim.objects.filter(id__in=claim_ids).select_related(
#         "policy__policy_base__risk_type",
#         "policy__policy_base__customer",
#         "policy__policy_base__product",
#         "policy__policy_base__request_by",
#         "policy__policy_base__request_type",
#         "policy__policy_base__coverage_type",
#         "policy__policy_base__payment_mode",
#         "policy__policy_base__insurer",
#         "policy__entity__created_by",
#         "policy__entity__updated_by",
#     )

#     email_data = []
#     claims_sent = []

#     for claim in claims:
#         policy = claim.policy
#         policy_base = policy.policy_base if policy else None
#         insurer = policy_base.insurer if policy_base else None

#         service_provider = ServiceProvider.objects.filter(id=insurer.id).first() if insurer else None
#         service_provider_email = getattr(service_provider, "email", None)

#         if not service_provider_email:
#             continue

#         subject = f"Claim Details for {policy_base.customer.name if policy_base and policy_base.customer else 'Unknown Customer'}"
#         body = build_claim_email_body(claim, service_provider)

#         email_data.append({
#             "recipient_email": service_provider_email,
#             "subject": subject,
#             "body": body,
#             "priority": "high"
#         })

#         claims_sent.append(claim)

#     if not email_data:
#         return ResponseService.response("NOT_FOUND", None, "No emails to send.")

#     mailer = SendMail()
#     result = mailer.send_email(email_data)

#     if not result.get("success"):
#         return ResponseService.response("INTERNAL_SERVER_ERROR", result, "default_email_error_msg")

#     for claim in claims_sent:
#         claim.indimation_time = timezone.now()
#         claim.save(update_fields=["indimation_time"])

#     return ResponseService.response("SUCCESS", result, "default_email_success_msg")






# #--------------------------------------------------
# #---------------Helper Functions-------------------
# #--------------------------------------------------

# #---------------Template Response-------------------

# def build_template_response(policy, form_id=None):
#     policy_base = policy.policy_base
#     risk_type = policy_base.risk_type if policy_base else None
#     insurer = policy_base.insurer if policy_base else None
#     customer = policy_base.customer if policy_base else None
#     product = policy_base.product if policy_base else None
#     request_type = policy_base.request_type if policy_base else None
#     coverage_type = policy_base.coverage_type if policy_base else None
#     payment_plan = policy_base.payment_mode if policy_base else None
#     requested_by = policy_base.request_by if policy_base else None
#     created_by = policy.entity.created_by if policy.entity else None
#     updated_by = policy.entity.updated_by if policy.entity else None

#     contact = Contact.objects.filter(id=customer.primary_contact_id).first() if customer and customer.primary_contact_id else None
#     additional_contact = CustomerAdditionalContact.objects.filter(customer_id=customer.id, is_primary=True).first() if customer else None

#     return {
#         "form_id": form_id,
#         "policy_holder_info": {
#             "customer_id": customer.id if customer else None,
#             "customer_name": customer.name if customer else None,
#             "customer_logo": customer.logo if customer else None,
#             "customer_contact_name": contact.name if contact else None,
#             "customer_contact_email": contact.email if contact else None,
#             "customer_contact_primary": contact.primary_contact if contact else None,
#             "customer_contact_address": contact.address if contact else None,
#             "customer_title": additional_contact.title if additional_contact else None,
#         },
#         "policy_info": {
#             "policy_id": policy.id,
#             "brokerage_policy_id": policy.brokerage_policy_id,
#             "insurer_policy_id": policy.insurer_policy_id,
#             "insurer_invoice_id": policy.insurer_invoice_id,
#             "start_date": policy.start_date,
#             "end_date": policy.end_date,
#             "premium_amount": policy.premium_amount,
#             "sum_insured": policy.sum_insured,
#             "quotation_document": policy_base.quotation_document if policy_base else None,
#             "quotation_document_name": policy_base.quotation_document_name if policy_base else None,
#         },
#         "request_info": {
#             "request_type_id": request_type.id if request_type else None,
#             "request_type_name": request_type.name if request_type else None,
#             "coverage_type_id": coverage_type.id if coverage_type else None,
#             "coverage_type_name": coverage_type.name if coverage_type else None,
#             "payment_plan_id": payment_plan.id if payment_plan else None,
#             "payment_plan_name": payment_plan.name if payment_plan else None,
#         },
#         "insurer_info": {
#             "insurer_id": insurer.id if insurer else None,
#             "insurer_name": insurer.name if insurer else None,
#             "insurer_logo": insurer.logo if insurer else None,
#             "insurer_mail": insurer.email if insurer else None,
#             "insurer_description": insurer.description if insurer else None,
#             "insurer_contact_number": None,
#         },
#         "risk_info": {
#             "risk_type_id": risk_type.id if risk_type else None,
#             "risk_type_title": risk_type.title if risk_type else None,
#         },
#         "product_info": {
#             "product_id": product.id if product else None,
#             "product_name": product.name if product else None,
#         },
#         "user_info": {
#             "requested_by_id": requested_by.id if requested_by else None,
#             "requested_by_name": requested_by.display_name if requested_by else None,
#             "requested_by_logo": requested_by.picture if requested_by else None,
#             "created_by_id": created_by.id if created_by else None,
#             "created_by_name": created_by.display_name if created_by else None,
#             "created_by_logo": created_by.picture if created_by else None,
#             "updated_by_id": updated_by.id if updated_by else None,
#             "updated_by_name": updated_by.display_name if updated_by else None,
#             "updated_by_logo": updated_by.picture if updated_by else None,
#         }
#     }


# #---------------Template Detail-------------------

# def get_template_detail(template):
#     try:
#         template_data = {
#             "id": template.id,
#             "name": template.title,
#             "description": template.description,
#             "type": template.type,
#         }

#         # Steps
#         steps = (
#             QueryBuilderService("core_form_custom_form_steps")
#             .select("*")
#             .where("form_id", template.id)
#             .get()
#         )

#         # Panels
#         panels = (
#             QueryBuilderService("core_form_custom_form_panels")
#             .select("*")
#             .where("form_id", template.id)
#             .get()
#         )

#         panel_ids = [panel["id"] for panel in panels]

#         # Elements with joined element code
#         elements_query = (
#             QueryBuilderService("core_form_custom_form_elements as ele")
#             .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id")
#             .select(
#                 "ele.*",
#                 "fe.code as element_code"
#             )
#             .whereIn("ele.panel_id", panel_ids if panel_ids else [0])
#             .get()
#         )

#         element_ids = [e["id"] for e in elements_query]

#         # Fetch element values in bulk
#         values_data = (
#             QueryBuilderService("core_form_display_element_values")
#             .select("element_id", "value")
#             .whereIn("element_id", element_ids if element_ids else [0])
#             .get()
#         )
#         values_dict = {v["element_id"]: v["value"] for v in values_data}

#         elements = []
#         for element in elements_query:
#             # Get options for element
#             options = (
#                 QueryBuilderService("core_form_custom_form_element_options")
#                 .select("*")
#                 .where("element_id", element["id"])
#                 .get()
#             )
#             # Attach value to element
#             element["value"] = values_dict.get(element["id"], None)
#             element["options"] = options
#             elements.append(element)

#         result = {
#             "template": template_data,
#             "steps": steps,
#             "panels": panels,
#             "elements": elements
#         }

#         return ResponseService.response("SUCCESS", result, "Template details retrieved successfully.")

#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")




# #---------------Email Body-------------------

# def build_claim_email_body(claim, service_provider):
#     policy = claim.policy
#     policy_base = policy.policy_base if policy else None
#     risk_type = policy_base.risk_type if policy_base else None
#     customer = policy_base.customer if policy_base else None
#     product = policy_base.product if policy_base else None

#     created_by = policy.entity.created_by if policy and policy.entity else None

#     return f"""
# <html>
# <body>
# <p>Dear <strong>{service_provider.name if service_provider else 'Service Provider'}</strong>,</p>

# <p>I hope this email finds you well.</p>

# <p>We would like to provide you with detailed information regarding the <strong>{risk_type.title if risk_type else 'N/A'}</strong> risk:</p>

# <h3>Policy Information:</h3>
# <ul>
# <li><strong>Policyholder name:</strong> {customer.name if customer else 'N/A'}</li>
# <li><strong>Policy Number:</strong> {policy.brokerage_policy_id if policy else 'N/A'}</li>
# <li><strong>Policy Type:</strong> {product.name if product else 'N/A'}</li>
# </ul>

# <h3>Claim Information:</h3>
# <ul>
# <li><strong>Claim ID:</strong> {claim.code}</li>
# <li><strong>Description:</strong> {getattr(claim, 'description', 'N/A')}</li>
# <li><strong>Date of loss:</strong> {claim.date_of_loss.strftime('%d %B %Y') if hasattr(claim, 'date_of_loss') else 'N/A'}</li>
# <li><strong>Time of loss:</strong> {claim.time_of_loss.strftime('%I:%M %p') if hasattr(claim, 'time_of_loss') else 'N/A'}</li>
# </ul>

# <p>Best regards,<br>
# {created_by.display_name if created_by else '[Your Full Name]'}<br>
# [Your Position]<br>
# [Your Company Name]<br>
# [Your Contact Information]</p>
# </body>
# </html>
# """
