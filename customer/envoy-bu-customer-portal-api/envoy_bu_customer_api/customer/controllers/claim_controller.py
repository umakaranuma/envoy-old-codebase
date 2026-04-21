
from datetime import timezone
import json
from math import ceil
from django.views.decorators.csrf import csrf_exempt
from django.db import Error, transaction
from rest_framework.decorators import api_view
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ResponseService as ResponseService
from mServices.ValidatorService import ValidatorService
from core_models.claim_models import Claim, ClaimFormSubmission 
from core_models.core_models import Contact, CoreFormSubmission, CoreFormSubmissionValue, CoreTemplate, Customer, CustomerAdditionalContact, IssuedPolicy, OpportunityFormConfig, RequestPolicy, ServiceProvider, Status
from services.ActionService import ActionService
from services.AuthService import AuthService
from services.send_mail_services import SendMail


@api_view(["GET"])
def get_customer_policies(request):
    
    try:
        
        user = request.user
        if isinstance(request.user, dict):
            customer_id = request.user.get("id")
        else:
            customer_id = getattr(request.user, "id", None)


        
        if not customer_id:
            return ResponseService.response("UNAUTHORIZED", None, "Customer ID missing in token")

        customer_exists = Customer.objects.filter(id=customer_id).exists()
        if not customer_exists:
            return ResponseService.response("NOT_FOUND", None, "Customer not found.")


        # Validate if customer exists
        customer_exists = Customer.objects.filter(id=customer_id).exists()
        if not customer_exists:
            return ResponseService.response("Customer not found.", None, Error.NOT_FOUND)

        # Extract and validate pagination and sorting parameters
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by") or "issued.id"
        sort_dir = request.GET.get("sort_dir") or "desc"

        # Fetch data with comprehensive JOINs
        columns = [
            "issued.*",
            "issued.id AS policy_id",
            "issued.remarks AS insurer_notes",
            "products.id AS product_id",
            "risk.title AS risk_type_name",
            "risk.id AS risk_type_id",
            "insurer_sp.name AS insurer_info_full_name",
            "insurer_sp.id AS insurer_id",
            "insurer_sp.logo AS insurer_info_logo",
            "customers.name as customer_name",
            "customers.logo as customer_logo",
            "customers.id as customer_id",
            "products.name as product",
            "request_policy.policy_request_id as policy_request_code",
            "request_policy.id as policy_request_id",
            "request_status.name AS policy_request_status",
            "request_status.color AS policy_request_status_color",
            "base.quotation_document as quotation_document",
            "base.quotation_document_name as quotation_document_name",
            "request_by.display_name AS requested_by",
            "request_by.picture AS requested_by_logo",
            "request_type.name AS request_type",
            "request_type.id AS request_type_id",
            "request_customer_contact.email AS customer_email",
            "request_customer_contact.address AS customer_address",
            "request_customer_contact.primary_contact AS customer_primary_contact",
            "coverage_type.name AS coverage_type",
            "coverage_type.id AS coverage_type_id",
            "payment_plan.name AS payment_plan",
            "payment_plan.id AS payment_plan_id",
            "created_by.display_name AS created_by",
            "created_by.picture AS created_by_logo",
            "updated_by.display_name AS updated_by",
            "updated_by.picture AS updated_by_logo",
            "entity.created_at AS created_at",
            "entity.updated_at AS updated_at",
            "invoices.invoice_number AS invoice_number",
            "config.data_gethering_type AS data_gathering_type",
            "config.form_id"
        ]

        # First get the base policy data without the problematic joins
        base_columns = [
            "issued.*",
            "issued.id AS policy_id",
            "issued.remarks AS insurer_notes",
            "products.id AS product_id",
            "risk.title AS risk_type_name",
            "risk.id AS risk_type_id",
            "insurer_sp.name AS insurer_info_full_name",
            "insurer_sp.id AS insurer_id",
            "insurer_sp.logo AS insurer_info_logo",
            "customers.name as customer_name",
            "customers.logo as customer_logo",
            "customers.id as customer_id",
            "products.name as product",
            "request_policy.policy_request_id as policy_request_code",
            "request_policy.id as policy_request_id",
            "request_status.name AS policy_request_status",
            "request_status.color AS policy_request_status_color",
            "base.quotation_document as quotation_document",
            "base.quotation_document_name as quotation_document_name",
            "request_by.display_name AS requested_by",
            "request_by.picture AS requested_by_logo",
            "request_type.name AS request_type",
            "request_type.id AS request_type_id",
            "request_customer_contact.email AS customer_email",
            "request_customer_contact.address AS customer_address",
            "request_customer_contact.primary_contact AS customer_primary_contact",
            "coverage_type.name AS coverage_type",
            "coverage_type.id AS coverage_type_id",
            "payment_plan.name AS payment_plan",
            "payment_plan.id AS payment_plan_id",
            "created_by.display_name AS created_by",
            "created_by.picture AS created_by_logo",
            "updated_by.display_name AS updated_by",
            "updated_by.picture AS updated_by_logo",
            "entity.created_at AS created_at",
            "entity.updated_at AS updated_at"
        ]

        raw_data = (
            QueryBuilderService("crmp_issued_policies as issued")
            .select(*base_columns)
            .leftJoin("crmp_policy_base as base", "base.id", "issued.policy_base_id")
            .leftJoin("crm_opportunity_types as risk", "risk.id", "base.risk_type_id")
            .leftJoin("core_service_providers as insurer_sp", "insurer_sp.id", "base.insurer_id")
            .leftJoin("core_customers as customers", "customers.id", "base.customer_id")
            .leftJoin("core_vendor_products as products", "products.id", "base.product_id")
            .leftJoin("core_users as request_by", "request_by.id", "base.request_by_id")
            .leftJoin("crmp_request_policies as request_policy", "request_policy.id", "issued.policy_request_id")
            .leftJoin("core_status as request_status", "request_status.id", "request_policy.status_id")
            .leftJoin("crmp_request_types as request_type", "request_type.id", "base.request_type_id")
            .leftJoin("core_contacts as request_customer_contact", "request_customer_contact.id", "customers.primary_contact_id")
            .leftJoin("crmp_coverage_types as coverage_type", "coverage_type.id", "base.coverage_type_id")
            .leftJoin("crmp_payment_plans as payment_plan", "payment_plan.id", "base.payment_mode_id")
            .leftJoin("core_entities as entity", "entity.id", "issued.entity_id")
            .leftJoin("core_users as created_by", "created_by.id", "entity.created_by_id")
            .leftJoin("core_users as updated_by", "updated_by.id", "entity.updated_by_id")
            .where("base.customer_id", customer_id)
            .orderBy(sort_by, sort_dir)
            .get()
        )

        # Get invoice numbers separately
        policy_ids = [item["id"] for item in raw_data]
        invoice_data = {}
        if policy_ids:
            invoice_records = (
                QueryBuilderService("crmf_invoices")
                .select("issued_policy_id", "invoice_number")
                .whereIn("issued_policy_id", policy_ids)
                .get()
            )
            for record in invoice_records:
                policy_id = record["issued_policy_id"]
                if policy_id not in invoice_data:
                    invoice_data[policy_id] = record["invoice_number"]

        # Get form configuration data separately
        risk_type_ids = list(set([item["risk_type_id"] for item in raw_data if item["risk_type_id"]]))
        form_config_data = {}
        if risk_type_ids:
            form_records = (
                QueryBuilderService("crm_opportunity_form_config")
                .select("opportunity_type_id", "data_gethering_type", "form_id")
                .whereIn("opportunity_type_id", risk_type_ids)
                .get()
            )
            for record in form_records:
                risk_type_id = record["opportunity_type_id"]
                if risk_type_id not in form_config_data:
                    form_config_data[risk_type_id] = {
                        "data_gathering_type": record["data_gethering_type"],
                        "form_id": record["form_id"]
                    }

        # Transform data - each row is already a complete policy record
        transformed_data = []
        for item in raw_data:
            # Get invoice number for this policy
            invoice_number = invoice_data.get(item["id"])
            
            # Get form configuration for this risk type
            form_config = form_config_data.get(item["risk_type_id"], {})
            data_gathering_type = form_config.get("data_gathering_type")
            form_id = form_config.get("form_id")
            
            policy_data = {
                "id": item["id"],
                "policy_id": item["policy_id"],
                "brokerage_policy_id": item["brokerage_policy_id"],
                "start_date": item["start_date"],
                "end_date": item["end_date"],
                "premium_amount": item["premium_amount"],
                "sum_insured": item["sum_insured"],
                "policy_base_id": item["policy_base_id"],
                "insurer_notes": item["insurer_notes"],
                
                # Risk type information
                "risk_type_id": item["risk_type_id"],
                "risk_type_name": item["risk_type_name"],
                
                # Product information
                "product_id": item["product_id"],
                "product": item["product"],
                
                # Insurer information
                "insurer_id": item["insurer_id"],
                "insurer_info_full_name": item["insurer_info_full_name"],
                "insurer_info_logo": item["insurer_info_logo"],
                
                # Customer information
                "customer_id": item["customer_id"],
                "customer_name": item["customer_name"],
                "customer_logo": item["customer_logo"],
                "customer_email": item["customer_email"],
                "customer_address": item["customer_address"],
                "customer_primary_contact": item["customer_primary_contact"],
                
                # Request policy information
                "policy_request_id": item["policy_request_id"],
                "policy_request_code": item["policy_request_code"],
                "policy_request_status": item["policy_request_status"],
                "policy_request_status_color": item["policy_request_status_color"],
                
                # Quotation information
                "quotation_document": item["quotation_document"],
                "quotation_document_name": item["quotation_document_name"],
                
                # Request information
                "requested_by": item["requested_by"],
                "requested_by_logo": item["requested_by_logo"],
                "request_type": item["request_type"],
                "request_type_id": item["request_type_id"],
                
                # Coverage and payment information
                "coverage_type": item["coverage_type"],
                "coverage_type_id": item["coverage_type_id"],
                "payment_plan": item["payment_plan"],
                "payment_plan_id": item["payment_plan_id"],
                
                # Entity and audit information
                "created_by": item["created_by"],
                "created_by_logo": item["created_by_logo"],
                "updated_by": item["updated_by"],
                "updated_by_logo": item["updated_by_logo"],
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
                
                # Invoice information
                "invoice_number": invoice_number,
                
                # Form configuration
                "data_gathering_type": data_gathering_type,
                "form_id": form_id
            }
            
            # Add template IDs for different data gathering types
            if data_gathering_type and form_id:
                key = f'{data_gathering_type}_template_id'
                policy_data[key] = form_id
                
            transformed_data.append(policy_data)
        total_records = len(transformed_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = transformed_data[start:end]

        # Build final response structure
        result = {
            "total_records": total_records,
            "per_page": limit,
            "current_page": page,
            "last_page": ceil(total_records / limit),
            "data": paginated_data
        }

        return ResponseService.response("SUCCESS", result, "default_get_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server error")
@api_view(["GET"])
def get_template_by_policy(request, policy_id):
    try:
        policy = IssuedPolicy.objects.select_related(
            "policy_base__risk_type",
            "policy_base__insurer",
            "policy_base__customer",
            "policy_base__product",
            "policy_base__request_by",
            "policy_base__request_type",
            "policy_base__coverage_type",
            "policy_base__payment_mode",
            "entity__created_by",
            "entity__updated_by"
        ).get(id=policy_id)

        risk_type = policy.policy_base.risk_type if policy.policy_base else None

        form_id = None
        if risk_type:
            try:
                form_config = OpportunityFormConfig.objects.filter(
                    opportunity_type=risk_type,
                    data_gethering_type=OpportunityFormConfig.CLAIM
                ).first()
                form_id = form_config.form_id if form_config else None
            except OpportunityFormConfig.DoesNotExist:
                pass

        data = build_template_response(policy, form_id)
        return ResponseService.response("SUCCESS", data, "Template and policy details retrieved successfully.")

    except IssuedPolicy.DoesNotExist:
        return ResponseService.response("NOT_FOUND", {"policy_id": "Policy not found."}, "Invalid policy ID.", system_code=404)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve template and policy details.")




@csrf_exempt
@api_view(['GET', 'POST'])
def claim(request):
    if request.method == 'GET':
        action = ActionService.getAction("CLAIM", "VIEW_ALL")
        has_authority = AuthService.hasAuthority(request, action)
        
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        
        return get_all_claims(request)
    
    elif request.method == 'POST':
        action = ActionService.getAction("CLAIM", "CREATE")
        has_authority = AuthService.hasAuthority(request, action)
        
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        
        return create_claim(request)

#----------------------Claim Get-All ----------------------------
def get_all_claims(request):
    try:
        user = request.user

        # Determine customer_id
        # if not user or user.is_anonymous:
        #     customer_id = 1  # fallback
        # else:
        #     customer = getattr(user, "entity", None)
        #     customer = customer.customers.first() if customer and hasattr(customer, "customers") else None
        #     customer_id = customer.id if customer else 1

        customer_id = user.get('id', 66)



        # Query parameters
        search_string = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        sort_by = request.GET.get('sort_by', 'claim.id')
        sort_dir = request.GET.get('sort_dir', 'desc')
        
        # Handle empty parameters - use defaults if empty strings are passed
        if not sort_by or sort_by.strip() == "":
            sort_by = "claim.id"
        if not sort_dir or sort_dir.strip() == "":
            sort_dir = "desc"
            
        ids = request.GET.get('ids', None)
        filter_json = request.GET.get('filters', '{}')

        # Selected columns
        all_columns = [
            "claim.*",
            "policy.brokerage_policy_id",
            "risk.title as risk_type_title",
            "insurer.name as insurer_name",
            "form.title as template_title",
            "customer.id as customer_id",
            "customer.name as customer_name",
            "status.name as status_name",
            "status.color as status_color",
            "product.name as product_name",
            "product.code as product_code",
        ]

        # Build base query
        query = (
            QueryBuilderService("crmp_claims as claim")
            .leftJoin("crmp_issued_policies as policy", "policy.id", "claim.policy_id")
            .leftJoin("crmp_policy_base as base", "base.id", "policy.policy_base_id")
            .leftJoin("core_vendor_products as product", "product.id", "base.product_id")
            .leftJoin("core_customers as customer", "customer.id", "base.customer_id")
            .leftJoin("crm_opportunity_types as risk", "risk.id", "claim.risk_type_id")
            .leftJoin("core_service_providers as insurer", "insurer.id", "claim.insurer_id")
            .leftJoin("core_templates as form", "form.id", "claim.template_id")
            .leftJoin("core_status as status", "status.id", "claim.status_id")
            .select(*all_columns)
            .where("base.customer_id", customer_id)
            .apply_conditions(filter_json, [], search_string, ["claim.code", "status.name", "risk.title", "insurer.name"])
        )

        # Filter by IDs if provided
        if ids:
            id_list = ids.split(',')
            data = query.whereIn("claim.id", id_list).get()
        else:
            data = query.paginate(page, limit, ['claim.code', 'claim.id'], sort_by, sort_dir)

        return ResponseService.response("SUCCESS", data, "Claims retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch claims.")

#----------------------Claim Create ----------------------------
@transaction.atomic
def create_claim(request):
    data = request.data
    form_id = data.get("form_id")
    submitted_values = data.get("values", {})
    user = request.user
    if isinstance(user, dict):
        print("user", user.get("id"))
    else:
        print("user", getattr(user, "id", None))
    
 # Step 1: Validate required input
    rules = {
        "form_id": "required|exists:core_templates,id",
        "policy_id": "required|exists:crmp_issued_policies,id",
        "is_myself": "required|boolean",
        "remarks": "nullable|string",
        "values": "required|dict",
        "reporter_name": "nullable|string",
        "reporter_contact": "nullable|string",
        "reporter_relationship": "nullable|string",
        "risk_info_ids": "required|array|min:1"
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    user = request.user
    if isinstance(user, dict):
        customer_id = user.get("id")
    else:
        customer_id = getattr(user, "id", None)

    if not customer_id:
        return ResponseService.response("UNAUTHORIZED", None, "Customer ID missing in token")
    
    template = CoreTemplate.objects.get(id=form_id)

    # Step 2: Get template details and elements
    template_response = get_template_detail(template)
    try:
        template_data = json.loads(template_response.content)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

    if not template_data.get("is_success"):
        return template_response

    elements = template_data.get("result", {}).get("elements", [])

    # Step 3: Validate required fields from template
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

    customer_instance = Customer.objects.filter(id=customer_id).first()
    if not customer_instance:
        return ResponseService.response("NOT_FOUND", None, "Customer not found.")

    submission = CoreFormSubmission.objects.create(form=template, user=None, customer=customer_instance)


    values_to_create = [
        CoreFormSubmissionValue(
            form_submission=submission,
            custom_form_element_id=element["id"],
            form_element_id=element["element_id"],
            value=submitted_values[str(element["id"])]
        )
        for element in elements if str(element["id"]) in submitted_values
    ]
    CoreFormSubmissionValue.objects.bulk_create(values_to_create)

    # Step 5: Create related claim
    policy = IssuedPolicy.objects.select_related("policy_base__risk_type", "policy_base__insurer").get(id=data["policy_id"])
    policy_base = policy.policy_base
    risk_type = policy_base.risk_type if policy_base else None
    insurer = policy_base.insurer if policy_base else None
    customer = policy_base.customer if policy_base and policy_base.customer else None

    # Step 6: Get evaluation form based on OpportunityFormConfig
    evaluation_template = None
    if risk_type:
        try:
            form_config = OpportunityFormConfig.objects.get(
                opportunity_type=risk_type,
                data_gethering_type=OpportunityFormConfig.CLAIM_EVALUATION
            )
            evaluation_template = CoreTemplate.objects.get(id=form_config.form_id)
        except (OpportunityFormConfig.DoesNotExist, CoreTemplate.DoesNotExist):
            evaluation_template = None  # Optionally log this

    draft_status = Status.objects.filter(name="Draft", module="Claim").first()
    if not draft_status:
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Draft status not found.")

    # Step 7: Save the claim
    claim = Claim.objects.create(
        policy=policy,
        customer=customer,
        remarks=data.get("remarks", ""),
        risk_type=risk_type,
        insurer=insurer,
        template=template,
        evaluation_form=evaluation_template,
        is_myself=data.get("is_myself", True),
        reporter_name=data.get("reporter_name"),
        reporter_contact=data.get("reporter_contact"),
        reporter_relationship=data.get("reporter_relationship"),
        status=draft_status,
    )

    # Step 8: Link the submission to the claim
    ClaimFormSubmission.objects.create(
        claim=claim,
        form_submission=submission,
        submission_type=ClaimFormSubmission.INCIDENT_INFO
    )



    # Create empty submission for evaluation form
    if evaluation_template:
        evaluation_submission = CoreFormSubmission.objects.create(form=evaluation_template, user=None, customer=customer_instance)


        # Link to the claim
        ClaimFormSubmission.objects.create(
            claim=claim,
            form_submission=evaluation_submission,
            submission_type=ClaimFormSubmission.EVALUATION
        )

 
    # Step 9: Handle risk_info_ids if provided
    risk_info_ids = data.get("risk_info_ids", [])
    if risk_info_ids:
        from core_models.claim_models import ClaimRisk
        from core_models.crm_models import RiskSubmission
        
        # Create relationship records for each risk submission ID
        for risk_submission_id in risk_info_ids:
            try:
                # Get the RiskSubmission object
                risk_submission = RiskSubmission.objects.get(id=int(risk_submission_id))
                
                # Create ClaimRisk relationship
                ClaimRisk.objects.create(
                    claim=claim,
                    risk_submission=risk_submission
                )
                print(f"✅ Created claim-risk relationship: Claim {claim.id} -> Risk Submission {risk_submission.id}")
            except RiskSubmission.DoesNotExist:
                print(f"⚠️ Warning: RiskSubmission {risk_submission_id} not found")
            except Exception as e:
                print(f"⚠️ Warning: Error creating claim-risk relationship for risk submission {risk_submission_id}: {str(e)}")

    # Step 10: Return success response
    return ResponseService.response("SUCCESS", {
        "submission_id": submission.id,
        "claim_id": claim.id,
        "claim_code": claim.code,
        "claim_status": claim.status.name,
        "claim_status_id": claim.status.id,
    }, "default_create_success_msg")


@csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])
def claim_details(request,claim_id):
    submission_type= ClaimFormSubmission.INCIDENT_INFO
    if request.method == 'GET':
        action = ActionService.getAction("CLAIM", "VIEW")
        has_authority = AuthService.hasAuthority(request, action)
        
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        
        return get_claim_detail(request,claim_id, submission_type)
    
    elif request.method == 'PUT':
        action = ActionService.getAction("CLAIM", "EDIT")
        has_authority = AuthService.hasAuthority(request, action)
        
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        
        return update_claim_submission(request,claim_id,submission_type)
    
    elif request.method == 'DELETE':
        action = ActionService.getAction("CLAIM", "DELETE")
        has_authority = AuthService.hasAuthority(request, action)
        if not has_authority:
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        return delete_claim(request, claim_id, submission_type)




@api_view(['GET'])
def claim_evaluation_details(request, claim_id):
    if request.method == 'GET':
        return get_claim_detail(request, claim_id, ClaimFormSubmission.EVALUATION)



#----------------------Claim Get-By-ID ----------------------------
def get_claim_detail(request, claim_id, submission_type):
    try:
        # Step 1: Validate claim_id
        rules = {"claim_id": "required|exists:crmp_claims,id"}
        errors = ValidatorService.validate({"claim_id": claim_id}, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Step 2: Retrieve the claim with related entities
        claim = Claim.objects.select_related(
            "policy__policy_base__risk_type",
            "policy__policy_base__insurer",
            "policy__policy_base__customer",
            "policy__policy_base__product",
            "template",
            "evaluation_form"
        ).get(id=claim_id)

        # Step 3: Determine the appropriate template based on submission_type
        if submission_type == ClaimFormSubmission.EVALUATION:
            template = claim.evaluation_form
        else:
            template = claim.template

        if not template:
            return ResponseService.response("NOT_FOUND", None, "Template not found for this claim.", system_code=404)

        # Step 4: Retrieve the associated form submission
        claim_submission = ClaimFormSubmission.objects.select_related("form_submission").filter(
            claim=claim,
            submission_type=submission_type
        ).first()

        if not claim_submission:
            return ResponseService.response("NOT_FOUND", None, "Form submission not found for this claim.", system_code=404)

        form_submission = claim_submission.form_submission

        # Step 5: Retrieve all submission values
        submission_values = CoreFormSubmissionValue.objects.filter(form_submission=form_submission)

        # Step 6: Build a dictionary of values keyed by custom_form_element_id
        values_dict = {
            str(value.custom_form_element_id): value.value
            for value in submission_values
        }

        # Step 7: Retrieve the template details
        template_response = get_template_detail(template)
        try:
            template_data = json.loads(template_response.content.decode('utf-8'))
        except Exception as e:
            return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

        if not template_data.get("is_success"):
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Failed to retrieve template details.")

        result = template_data.get("result", {})
        elements = result.get("elements", [])

        # Step 8: Attach the stored values to the corresponding elements
        for element in elements:
            element_id_str = str(element["id"])
            element["value"] = values_dict.get(element_id_str)

        # Step 9: Construct the response data
        response_data = {
            "claim_id": claim.id,
            "claim_code": claim.code,
            "claim_status": claim.status.name,
            "claim_status_color": claim.status.color,
            "template": {
                "id": template.id,
                "name": template.title,
                "description": template.description,
                "type": template.type,
            },
            "steps": result.get("steps", []),
            "panels": result.get("panels", []),
            "elements": elements
        }

        return ResponseService.response("SUCCESS", response_data, "Claim details retrieved successfully.")

    except Claim.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Claim not found.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve claim details.")

#----------------------Claim Update ----------------------------
@transaction.atomic
def update_claim_submission(request, claim_id, submission_type):
    data = request.data

    # Step 1: Validate input
    rules = {
        "values": "required|dict",
        "is_completed": "boolean"
    }
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        claim = Claim.objects.select_related("template", "evaluation_form").get(id=claim_id)
    except Claim.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Claim not found.", system_code=404)

    # Prevent update if claim is already submitted
    if claim.status and claim.status.name == "Submitted":
        return ResponseService.response("FORBIDDEN", None, "default_update_forbidden_msg","FORBIDDEN")

    # Step 2: Determine the correct template based on submission_type
    template = claim.evaluation_form if submission_type == ClaimFormSubmission.EVALUATION else claim.template
    if not template:
        return ResponseService.response("NOT_FOUND", None, "Template not found for this claim.", system_code=404)

    # Step 3: Retrieve the associated form submission
    claim_submission = ClaimFormSubmission.objects.select_related("form_submission").filter(
        claim=claim, submission_type=submission_type
    ).first()
    if not claim_submission:
        return ResponseService.response("NOT_FOUND", None, "Form submission not found for this claim.", system_code=404)

    form_submission = claim_submission.form_submission

    # Step 4: Load form elements to match `custom_form_element_id` to `form_element_id`
    template_response = get_template_detail(template)
    try:
        template_data = json.loads(template_response.content.decode("utf-8"))
        elements = template_data.get("result", {}).get("elements", [])
        element_id_map = {
            str(el["id"]): el["element_id"]
            for el in elements if "id" in el and "element_id" in el
        }
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

    # Step 5: Update or create values
    submitted_values = data.get("values", {})
    existing_values_qs = CoreFormSubmissionValue.objects.filter(form_submission=form_submission)
    existing_values_dict = {
        str(v.custom_form_element_id): v for v in existing_values_qs
    }

    for element_id_str, value in submitted_values.items():
        form_element_id = element_id_map.get(element_id_str)
        if not form_element_id:
            continue  # Skip if no valid form_element_id found

        if element_id_str in existing_values_dict:
            entry = existing_values_dict[element_id_str]
            entry.value = value
            entry.save()
        else:
            CoreFormSubmissionValue.objects.create(
                form_submission=form_submission,
                custom_form_element_id=element_id_str,
                form_element_id=form_element_id,
                value=value
            )

    # Step 6: Update claim status if is_completed is True
    if data.get("is_completed") is True:
        submitted_status = Status.objects.filter(name="Submitted", module="Claim").first()
        if not submitted_status:
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Submitted status not found.")
        claim.status = submitted_status
        claim.save(update_fields=["status"])

        send_claim_emails(request._request.__class__(data={"claim_ids": [claim_id]}))

    return ResponseService.response("SUCCESS", {"claim_id": claim.id}, "default_update_success_msg")


#----------------------Claim Delete ----------------------------
@transaction.atomic
def delete_claim(request, claim_id,submission_type):
    try:
        claim = Claim.objects.get(id=claim_id)

        # Delete related form submission if exists
        claim_submission = ClaimFormSubmission.objects.filter(claim=claim,submission_type=submission_type).first()
        if claim_submission:
            CoreFormSubmissionValue.objects.filter(form_submission=claim_submission.form_submission).delete()
            claim_submission.form_submission.delete()
            claim_submission.delete()

        # Delete the claim
        claim.delete()

        return ResponseService.response("SUCCESS", {"claim_id": claim_id}, "default_delete_success_msg")

    except Claim.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Claim not found.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "default_delete_error_msg")











































#--------------Template Response Builder-------------------

def build_template_response(policy, form_id=None):
    policy_base = policy.policy_base
    risk_type = policy_base.risk_type if policy_base else None
    insurer = policy_base.insurer if policy_base else None
    customer = policy_base.customer if policy_base else None
    product = policy_base.product if policy_base else None
    request_type = policy_base.request_type if policy_base else None
    coverage_type = policy_base.coverage_type if policy_base else None
    payment_plan = policy_base.payment_mode if policy_base else None
    requested_by = policy_base.request_by if policy_base else None
    created_by = policy.entity.created_by if policy.entity else None
    updated_by = policy.entity.updated_by if policy.entity else None

    contact = Contact.objects.filter(id=customer.primary_contact_id).first() if customer and customer.primary_contact_id else None
    additional_contact = CustomerAdditionalContact.objects.filter(customer_id=customer.id, is_primary=True).first() if customer else None

    return {
        "form_id": form_id,
        "policy_holder_info": {
            "customer_id": customer.id if customer else None,
            "customer_name": customer.name if customer else None,
            "customer_logo": customer.logo if customer else None,
            "customer_contact_name": contact.name if contact else None,
            "customer_contact_email": contact.email if contact else None,
            "customer_contact_primary": contact.primary_contact if contact else None,
            "customer_contact_address": contact.address if contact else None,
            "customer_title": additional_contact.title if additional_contact else None,
        },
        "policy_info": {
            "policy_id": policy.id,
            "brokerage_policy_id": policy.brokerage_policy_id,
            "insurer_policy_id": policy.insurer_policy_id,
            "insurer_invoice_id": policy.insurer_invoice_id,
            "start_date": policy.start_date,
            "end_date": policy.end_date,
            "premium_amount": policy.premium_amount,
            "sum_insured": policy.sum_insured,
            "quotation_document": policy_base.quotation_document if policy_base else None,
            "quotation_document_name": policy_base.quotation_document_name if policy_base else None,
        },
        "request_info": {
            "request_type_id": request_type.id if request_type else None,
            "request_type_name": request_type.name if request_type else None,
            "coverage_type_id": coverage_type.id if coverage_type else None,
            "coverage_type_name": coverage_type.name if coverage_type else None,
            "payment_plan_id": payment_plan.id if payment_plan else None,
            "payment_plan_name": payment_plan.name if payment_plan else None,
        },
        "insurer_info": {
            "insurer_id": insurer.id if insurer else None,
            "insurer_name": insurer.name if insurer else None,
            "insurer_logo": insurer.logo if insurer else None,
            "insurer_mail": insurer.email if insurer else None,
            "insurer_description": insurer.description if insurer else None,
            "insurer_contact_number": None,
        },
        "risk_info": {
            "risk_type_id": risk_type.id if risk_type else None,
            "risk_type_title": risk_type.title if risk_type else None,
        },
        "product_info": {
            "product_id": product.id if product else None,
            "product_name": product.name if product else None,
        },
        "user_info": {
            "requested_by_id": requested_by.id if requested_by else None,
            "requested_by_name": requested_by.display_name if requested_by else None,
            "requested_by_logo": requested_by.picture if requested_by else None,
            "created_by_id": created_by.id if created_by else None,
            "created_by_name": created_by.display_name if created_by else None,
            "created_by_logo": created_by.picture if created_by else None,
            "updated_by_id": updated_by.id if updated_by else None,
            "updated_by_name": updated_by.display_name if updated_by else None,
            "updated_by_logo": updated_by.picture if updated_by else None,
        }
    }




#------------------------------------

#---------------Template Detail-------------------

def get_template_detail(template):
    try:
        template_data = {
            "id": template.id,
            "name": template.title,
            "description": template.description,
            "type": template.type,
        }

        # Steps
        steps = (
            QueryBuilderService("core_form_custom_form_steps")
            .select("*")
            .where("form_id", template.id)
            .get()
        )

        # Panels
        panels = (
            QueryBuilderService("core_form_custom_form_panels")
            .select("*")
            .where("form_id", template.id)
            .get()
        )

        panel_ids = [panel["id"] for panel in panels]

        # Elements with joined element code
        elements_query = (
            QueryBuilderService("core_form_custom_form_elements as ele")
            .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id")
            .select(
                "ele.*",
                "fe.code as element_code"
            )
            .whereIn("ele.panel_id", panel_ids if panel_ids else [0])
            .get()
        )

        element_ids = [e["id"] for e in elements_query]

        # Fetch element values in bulk
        values_data = (
            QueryBuilderService("core_form_display_element_values")
            .select("element_id", "value")
            .whereIn("element_id", element_ids if element_ids else [0])
            .get()
        )
        values_dict = {v["element_id"]: v["value"] for v in values_data}

        elements = []
        for element in elements_query:
            # Get options for element
            options = (
                QueryBuilderService("core_form_custom_form_element_options")
                .select("*")
                .where("element_id", element["id"])
                .get()
            )
            # Attach value to element
            element["value"] = values_dict.get(element["id"], None)
            element["options"] = options
            elements.append(element)

        result = {
            "template": template_data,
            "steps": steps,
            "panels": panels,
            "elements": elements
        }

        return ResponseService.response("SUCCESS", result, "Template details retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

#------------------------------------

@api_view(["POST"])
def send_claim_emails(request):
    data = request.data

    # Validate claim_ids with ValidatorService
    rules = {
        "claim_ids": "required|array|min:1"
    }

    errors = ValidatorService.validate(data, rules, {})
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation failed.")

    claim_ids = data.get("claim_ids", [])

    claims = Claim.objects.filter(id__in=claim_ids).select_related(
        "policy__policy_base__risk_type",
        "policy__policy_base__customer",
        "policy__policy_base__product",
        "policy__policy_base__request_by",
        "policy__policy_base__request_type",
        "policy__policy_base__coverage_type",
        "policy__policy_base__payment_mode",
        "policy__policy_base__insurer",
        "policy__entity__created_by",
        "policy__entity__updated_by",
    )

    email_data = []
    claims_sent = []

    for claim in claims:
        policy = claim.policy
        policy_base = policy.policy_base if policy else None
        insurer = policy_base.insurer if policy_base else None

        service_provider = ServiceProvider.objects.filter(id=insurer.id).first() if insurer else None
        service_provider_email = getattr(service_provider, "email", None)

        if not service_provider_email:
            continue

        subject = f"Claim Details for {policy_base.customer.name if policy_base and policy_base.customer else 'Unknown Customer'}"
        body = build_claim_email_body(claim, service_provider)

        email_data.append({
            "recipient_email": service_provider_email,
            "subject": subject,
            "body": body,
            "priority": "high"
        })

        claims_sent.append(claim)

    if not email_data:
        return ResponseService.response("NOT_FOUND", None, "No emails to send.")

    mailer = SendMail()
    result = mailer.send_email(email_data)

    if not result.get("success"):
        return ResponseService.response("INTERNAL_SERVER_ERROR", result, "default_email_error_msg")

    for claim in claims_sent:
        claim.indimation_time = timezone.now()
        claim.save(update_fields=["indimation_time"])

    return ResponseService.response("SUCCESS", result, "default_email_success_msg")


#---------------Email Body-------------------

def build_claim_email_body(claim, service_provider):
    policy = claim.policy
    policy_base = policy.policy_base if policy else None
    risk_type = policy_base.risk_type if policy_base else None
    customer = policy_base.customer if policy_base else None
    product = policy_base.product if policy_base else None

    created_by = policy.entity.created_by if policy and policy.entity else None

    return f"""
<html>
<body>
<p>Dear <strong>{service_provider.name if service_provider else 'Service Provider'}</strong>,</p>

<p>I hope this email finds you well.</p>

<p>We would like to provide you with detailed information regarding the <strong>{risk_type.title if risk_type else 'N/A'}</strong> risk:</p>

<h3>Policy Information:</h3>
<ul>
<li><strong>Policyholder name:</strong> {customer.name if customer else 'N/A'}</li>
<li><strong>Policy Number:</strong> {policy.brokerage_policy_id if policy else 'N/A'}</li>
<li><strong>Policy Type:</strong> {product.name if product else 'N/A'}</li>
</ul>

<h3>Claim Information:</h3>
<ul>
<li><strong>Claim ID:</strong> {claim.code}</li>
<li><strong>Description:</strong> {getattr(claim, 'description', 'N/A')}</li>
<li><strong>Date of loss:</strong> {claim.date_of_loss.strftime('%d %B %Y') if hasattr(claim, 'date_of_loss') else 'N/A'}</li>
<li><strong>Time of loss:</strong> {claim.time_of_loss.strftime('%I:%M %p') if hasattr(claim, 'time_of_loss') else 'N/A'}</li>
</ul>

<p>Best regards,<br>
{created_by.display_name if created_by else '[Your Full Name]'}<br>
[Your Position]<br>
[Your Company Name]<br>
[Your Contact Information]</p>
</body>
</html>
"""
