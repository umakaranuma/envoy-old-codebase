from django.db import Error
import mServices.QueryBuilderService as QueryBuilderService
from rest_framework.decorators import api_view

from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService

from core_models.core_models import CoreFormSubmission, CoreTemplate, Status


@api_view(["GET"])
def opportunity_type(request):
    try:
        all_columns = [
            "crm_opportunity_types.id",
            "crm_opportunity_types.title",
            "crm_opportunity_types.description",
        ]
        
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        # Extract query parameters for filtering, sorting, and pagination
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "crm_opportunity_types.id")
        sort_dir = request.GET.get("sort_dir", "asc")

        allowed_filters = ["crm_opportunity_types.id", "crm_opportunity_types.title"]
        search_columns = ["crm_opportunity_types.id", "crm_opportunity_types.title"]
        allowed_sorting_columns = ["crm_opportunity_types.id", "crm_opportunity_types.title"]

        query = QueryBuilderService("crm_opportunity_types")\
                .select(*all_columns)\
                .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
                .paginate(page, limit,allowed_sorting_columns, sort_by, sort_dir)

        return ResponseService.response('SUCCESS',query, "Type retrieved successfully!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")



@api_view(['GET'])
def get_vendor_products_by_risk_type(request):
    try:
        risk_type_param = request.GET.get("risk_type_id")

        if not risk_type_param:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "risk_type_id parameter is required"},
                "Validation error"
            )

        # Convert to list of integers
        try:
            risk_type_ids = [int(x.strip()) for x in risk_type_param.split(",") if x.strip().isdigit()]
        except ValueError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "All risk_type_id values must be integers"},
                "Validation error"
            )

        if not risk_type_ids:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "No valid risk_type_id values provided"},
                "Validation error"
            )

        # Query vendor products matching any of the provided category_ids (risk types)
        vendor_products = (
            QueryBuilderService("core_vendor_products")
            .select("*")
            .whereIn("category_id", risk_type_ids)
            .whereNull("deleted_at")
            .get()
        )

        return ResponseService.response(
            "SUCCESS",
            vendor_products,
            "Vendor products retrieved successfully"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to retrieve vendor products"
        )



#-----------------------------------------------
#FORM RELATED ENDPOINTS
#-----------------------------------------------

@api_view(["GET", "PUT", "DELETE"])
def template_detail(request, id):
    try:
        template = CoreTemplate.objects.get(id=id)
    except CoreTemplate.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Template not found.")

    if request.method == "GET":
        return get_template_detail(template)

    elif request.method == "PUT":
        return update_template(request, template)

    elif request.method == "DELETE":
        return delete_template(template)


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
            .orderBy("order_number")
            .get()
        )

        panel_ids = [panel["id"] for panel in panels]

        # Elements ordered by order_number
        elements_query = (
            QueryBuilderService("core_form_custom_form_elements as ele")
            .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id")
            .select(
                "ele.*",
                # "fe.code as element_code",
                # "fe.group_id as group_id",
            )
            .whereIn("ele.panel_id", panel_ids if panel_ids else [0])
            .orderBy("ele.order_number")
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


def resolve_draft_status(form_type):
    """
    Resolve the initial draft Status for a given customer request type/module.
    For policy and quotation customer requests, use the common
    customer-request status:
      module='customer', type='customer_request_requested'
    For claims, keep using the claim draft status:
      module='claim', type='Claim_draft'
    """
    if not form_type:
        return None

    request_type = str(form_type).lower()

    # Map request types to the (module, type) pair in Status
    # Both policy and quotation use the same customer-request status.
    mapping = {
        "quotation": ("customer", "customer_requested"),
        "policy": ("customer", "customer_requested"),
        "claim": ("claim", "Claim_draft"),
        "payment": ("payment", "payment_pending"),
        "invoice": ("invoice", "invoice_pending"),
    }

    module, type_code = mapping.get(request_type, (None, None))
    if not module or not type_code:
        return None

    # Look up by module + type (case-insensitive on type to tolerate 'Claim_draft')
    return Status.objects.filter(module__iexact=module, type__iexact=type_code).first()

def update_template(request, template):
    try:
        data = request.data
        if not isinstance(data, dict):
            return ResponseService.response("VALIDATION_ERROR", {}, "Invalid data format. JSON object expected.")

        rules = {
            "title": f"required|max:200|unique:core_templates,title,{template.id}",
            "type": "required|in:single_form,multi_step_form",
            "description": "max:250"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.unique": "Template with this title already exists.",
            "type.required": "Form type is required.",
            "type.in": "Type must be 'single_form' or 'multi_step_form'."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        template.title = data["title"]
        template.type = data["type"]
        template.description = data.get("description", None)
        template.save()

        return ResponseService.response(
            "SUCCESS",
            {
                "id": template.id,
                "title": template.title,
                "type": template.type,
                "description": template.description,
            },
            "default_update_success_msg"
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_template(template):
    try:
        template.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



@api_view(["GET"])
def get_risk_types_by_policy_base(request, policy_base_id):
    """
    Get risk types associated with a policy base.
    
    Parameters:
    - policy_base_id: ID of the policy base to get risk types for
    
    Returns:
    - List of risk types with id, title, and description
    """
    try:
        # 1. Validate policy_base_id
        errors = ValidatorService.validate(
            {"policy_base_id": policy_base_id},
            {"policy_base_id": "required|integer|exists:crmp_policy_base,id"}
        )
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # 2. Build query to fetch unique risk types from crmp_policy_risk_config
        result = QueryBuilderService("crmp_policy_risk_config as prc") \
            .leftJoin("crm_risk_submissions as rs", "rs.id", "prc.risk_submission_id") \
            .leftJoin("crm_risks as r", "r.id", "rs.risk_id") \
            .leftJoin("crm_opportunity_types as rt", "rt.id", "r.risk_type_id") \
            .select("rt.id", "rt.title", "rt.description") \
            .where("prc.policy_base_id", policy_base_id) \
            .groupBy("rt.id", "rt.title", "rt.description") \
            .get()

        if not result:
            return ResponseService.response("NOT_FOUND", [], "No risk types found for this policy base.")

        return ResponseService.response("SUCCESS", result, "Risk types retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve risk types.")




@api_view(["GET"])
def get_risks_by_type_and_customer(request, risk_type_id):
    try:
        # Get query parameters
        customer_id = request.query_params.get("customer_id")
        approval_id = request.query_params.get("approval_id")
        lead_id = request.query_params.get("lead_id")
        policy_base_id = request.query_params.get("policy_base_id")
        sort_by = request.query_params.get("sort_by", "")
        sort_dir = request.query_params.get("sort_dir", "desc")
        
        # Validate required parameters
        if not customer_id:
            return ResponseService.response("VALIDATION_ERROR", None, "Customer ID is required.")

        # Fields for risk data
        risk_columns = [
            "rd.id",
            "rd.code AS risk_code",
            "rt.title AS risk_type_title",
            "cust.id AS customer_id",
            "cust.name AS customer_name",
            "cust.logo AS customer_logo"
        ]

        # Initialize base query
        base_query = QueryBuilderService("crm_risks as rd") \
            .leftJoin("crm_opportunity_types AS rt", "rt.id", "rd.risk_type_id") \
            .leftJoin("core_customers AS cust", "cust.id", "rd.customer_id") \
            .select(*risk_columns, "rs.submission_id", "rs.id as risk_submission_id") \
            .leftJoin("crm_risk_submissions as rs", "rs.risk_id", "rd.id") \
            .where("rd.risk_type_id", risk_type_id) \
            .where("rd.customer_id", customer_id)\
            .where("rd.is_deleted", False)

        # Handle direct filtering parameters first (lead_id or policy_base_id)
        if lead_id and lead_id.strip() and lead_id.lower() not in ['null', 'undefined', '']:
            # Direct lead_id filtering - filter risks by lead_id from crm_risk_submissions
            base_query = base_query.where("rs.lead_id", lead_id)
            
        elif policy_base_id and policy_base_id.strip() and policy_base_id.lower() not in ['null', 'undefined', '']:
            # Direct policy_base_id filtering - get risk_submissions_id from crmp_policy_risk_config
            try:
                risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                    .select("risk_submission_id") \
                    .where("policy_base_id", policy_base_id) \
                    .get()
            except:
                try:
                    risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                        .select("risk_submissions_id") \
                        .where("policy_base_id", policy_base_id) \
                        .get()
                except:
                    try:
                        risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                            .select("submission_id") \
                            .where("policy_base_id", policy_base_id) \
                            .get()
                    except:
                        try:
                            risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                                .select("risk_id") \
                                .where("policy_base_id", policy_base_id) \
                                .get()
                        except:
                            return ResponseService.response("SUCCESS", [], "Unable to access crmp_policy_risk_config table.")
            
            if risk_configs:
                # Extract the submission IDs (try different possible column names)
                submission_ids = []
                for rc in risk_configs:
                    if rc.get("risk_submission_id"):
                        submission_ids.append(rc["risk_submission_id"])
                    elif rc.get("risk_submissions_id"):
                        submission_ids.append(rc["risk_submissions_id"])
                    elif rc.get("submission_id"):
                        submission_ids.append(rc["submission_id"])
                    elif rc.get("risk_id"):
                        submission_ids.append(rc["risk_id"])
                
                if submission_ids:
                    # Filter risks by submission IDs
                    base_query = base_query.whereIn("rs.id", submission_ids)
                else:
                    return ResponseService.response("SUCCESS", [], "No risk submissions found for this policy_base_id.")
            else:
                return ResponseService.response("SUCCESS", [], "No risk configurations found for this policy_base_id.")
                
        # Handle approval_id logic for different approval types (only if no direct filtering)
        # Only process if approval_id has a meaningful value (not null, empty, or undefined)
        elif approval_id and approval_id.strip() and approval_id.lower() not in ['null', 'undefined', '']:
            # Get approval details to determine entity type
            approval = QueryBuilderService("core_entity_approvals as ea") \
                .select("ea.entity_id", "ce.type as entity_type") \
                .leftJoin("core_entities as ce", "ce.id", "ea.entity_id") \
                .where("ea.id", approval_id) \
                .first()
            
            if not approval:
                return ResponseService.response("NOT_FOUND", None, "Approval not found.", system_code=404)
            
            entity_id = approval["entity_id"]
            entity_type = approval["entity_type"]
            
            if entity_type and entity_type.lower() in ("quotation approval", "quotation"):
                # For quotation: find opportunity_id, then find risks in crm_risk_submissions by lead_id
                qrow = (
                    QueryBuilderService("crmq_quotations as q")
                    .select(
                        "q.id as quotation_id",
                        "q.opportunity_id as opportunity_id",
                        "crm_opportunities.id as lead_id",
                    )
                    .leftJoin("crm_opportunities", "crm_opportunities.id", "q.opportunity_id")
                    .where("q.entity_id", entity_id)
                    .first()
                )
                
                if not qrow or not qrow.get("lead_id"):
                    return ResponseService.response(
                        "NOT_FOUND",
                        {"entity_id": entity_id, "entity_type": entity_type},
                        "Lead not found for this quotation."
                    )
                
                lead_id = qrow["lead_id"]
                # Filter risks by lead_id from crm_risk_submissions
                base_query = base_query.where("rs.lead_id", lead_id)
                
            elif entity_type and entity_type.lower() == "policy":
                # For policy: find policy_base_id from crmp_request_policies, then find risk_submissions_id from crmp_policy_risk_config
                prow = (
                    QueryBuilderService("crmp_request_policies")
                    .select("id as policy_id", "policy_base_id")
                    .where("entity_id", entity_id)
                    .first()
                )
                
                if not prow or not prow.get("policy_id"):
                    return ResponseService.response(
                        "NOT_FOUND",
                        {"entity_id": entity_id, "entity_type": entity_type},
                        "Policy request not found for this approval."
                    )
                
                policy_base_id = prow.get("policy_base_id")
                if not policy_base_id:
                    return ResponseService.response(
                        "NOT_FOUND",
                        {"entity_id": entity_id, "entity_type": entity_type, "policy_id": prow["policy_id"]},
                        "Policy base not found for this policy request."
                    )
                
                # Get risk_submissions_id from crmp_policy_risk_config table
                # Try different possible column names
                try:
                    risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                        .select("risk_submission_id") \
                        .where("policy_base_id", policy_base_id) \
                        .get()
                except:
                    try:
                        risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                            .select("risk_submissions_id") \
                            .where("policy_base_id", policy_base_id) \
                            .get()
                    except:
                        try:
                            risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                                .select("submission_id") \
                                .where("policy_base_id", policy_base_id) \
                                .get()
                        except:
                            try:
                                risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                                    .select("risk_id") \
                                    .where("policy_base_id", policy_base_id) \
                                    .get()
                            except:
                                return ResponseService.response("SUCCESS", [], "Unable to access crmp_policy_risk_config table.")
                
                if risk_configs:
                    # Extract the submission IDs (try different possible column names)
                    submission_ids = []
                    for rc in risk_configs:
                        if rc.get("risk_submission_id"):
                            submission_ids.append(rc["risk_submission_id"])
                        elif rc.get("risk_submissions_id"):
                            submission_ids.append(rc["risk_submissions_id"])
                        elif rc.get("submission_id"):
                            submission_ids.append(rc["submission_id"])
                        elif rc.get("risk_id"):
                            submission_ids.append(rc["risk_id"])
                    
                    if submission_ids:
                        # Filter risks by submission IDs
                        base_query = base_query.whereIn("rs.id", submission_ids)
                    else:
                        return ResponseService.response("SUCCESS", [], "No risk submissions found for this policy.")
                else:
                    return ResponseService.response("SUCCESS", [], "No risk configurations found for this policy.")

        # Define allowed sorting columns
        allowed_sorting_columns = ["id", "code", "risk_code", "risk_type_title", "customer_name"]
        
        # Apply sorting if specified
        if sort_by and sort_by in allowed_sorting_columns:
            if sort_dir.lower() == "desc":
                base_query = base_query.orderBy(f"{sort_by}", "DESC")
            else:
                base_query = base_query.orderBy(f"{sort_by}", "ASC")
        
        # Get all results without pagination
        all_risks = base_query.get()
        
        if not all_risks:
            return ResponseService.response("SUCCESS", [], "No risk details found for this type and customer.")

        # Process risk data and group by risk_id to get only the latest submission
        risk_submissions = {}  # Dictionary to store latest submission for each risk_id
        
        for risk in all_risks:
            submission_id = risk.get("submission_id")
            risk_id = risk["id"]
            
            if not submission_id:
                continue

            # Keep only the latest submission for each risk_id
            if risk_id not in risk_submissions or submission_id > risk_submissions[risk_id]["submission_id"]:
                risk_submissions[risk_id] = risk

        # Process the latest submissions
        results = []
        for risk_id, risk in risk_submissions.items():
            submission_id = risk.get("submission_id")
            
            submission = CoreFormSubmission.objects.select_related("form").filter(id=submission_id).first()
            if submission and submission.form:
                _, _, elements = fetch_elements_data(submission.form.id, submission_id=submission.id)
                result_item = {str(ele["id"]): ele.get("value") for ele in elements}
                result_item["form_submission_id"] = submission.id
                result_item["submission_id"] = risk.get("risk_submission_id")
                result_item["template_id"] = submission.form.id
                result_item["risk_id"] = risk["id"]
                result_item["risk_code"] = risk["risk_code"]
                result_item["risk_type_title"] = risk["risk_type_title"]
                result_item["customer_id"] = risk["customer_id"]
                result_item["customer_name"] = risk["customer_name"]
                result_item["customer_logo"] = risk["customer_logo"]
                results.append(result_item)

        return ResponseService.response("SUCCESS", results,
         "Risk details retrieved successfully.")

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

