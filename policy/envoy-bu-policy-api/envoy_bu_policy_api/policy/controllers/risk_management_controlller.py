import json
from datetime import date, datetime
from rest_framework.decorators import api_view
from rest_framework import status
from mServices.QueryBuilderService import QueryBuilderService
from mServices.ResponseService import ResponseService
from core_models.core_models import CoreFormSubmission, CoreFormSubmissionValue, CoreTemplate
from django.views.decorators.csrf import csrf_exempt
from core_models.crm_models import Risk, RiskSubmission
from mServices.ValidatorService import ValidatorService
from django.db import transaction
import time
import os
import requests
import pandas as pd
from io import BytesIO

from messages import Error, Message
from services.ActionService import ActionService
from services.AuthService import AuthService
from services.excel_exporter import SQLToExcelExporter
from services.s3_presigned_service import S3PresignedService
# from utils.template_utils import fetch_template_data




@api_view(["GET"])
def get_opportunities_by_customer(request, customer_id):
    try:
        # Validate customer_id
        errors = ValidatorService.validate(
            {"customer_id": customer_id},
            {"customer_id": "required|exists:core_customers,id"}
        )
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
        
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "opp.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        opportunities = QueryBuilderService("crm_opportunities as opp") \
            .select(
                "opp.*", "status.name as stage_name", "status.color as stage_color","status.type as stage_type"
            ) \
            .leftJoin("crm_opportunity_statuses as status", "status.id", "opp.stage_id") \
            .where("opp.customer_id", customer_id) \
            .paginate(page, limit, ["opp.code", "opp.id"], sort_by, sort_dir)


        return ResponseService.response("SUCCESS", opportunities, "Opportunities retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve opportunities.")



@api_view(["GET"])
def get_risk_types_by_opportunity(request, opportunity_id):
    try:
        # 1. Validate opportunity_id
        # errors = ValidatorService.validate(
        #     {"opportunity_id": opportunity_id},
        #     {"opportunity_id": "required|exists:crm_oppor_opportunity_types,opportunity_id"}
        # )
        # if errors:
        #     return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # 2. Build query to fetch linked opportunity_types
        result = QueryBuilderService("crm_oppor_opportunity_types as ot") \
            .leftJoin("crm_opportunity_types as rt", "rt.id", "ot.opportunity_type_id") \
            .select("rt.id", "rt.title", "rt.description") \
            .where("ot.opportunity_id", opportunity_id) \
            .get()

        return ResponseService.response("SUCCESS", result, "Risk types retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve risk types.")


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
def get_risk_form_template_detail(request, risk_type_id):
    try:
        config = QueryBuilderService("crm_opportunity_form_config") \
            .select("form_id") \
            .where("opportunity_type_id", risk_type_id) \
            .where("data_gethering_type", "onboarding") \
            .first()

        if not config:
            return ResponseService.response("NOT_FOUND", None, "Form config not found for this risk type.",system_code=404)

        template = CoreTemplate.objects.filter(id=config["form_id"]).first()
        if not template:
            return ResponseService.response("NOT_FOUND", None, "Template not found.")

        return build_template_response(template)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



@api_view(["GET"])
def get_risks_by_type_and_customer(request, risk_type_id):
    try:
        # Get query parameters
        customer_id = request.query_params.get("customer_id")
        approval_id = request.query_params.get("approval_id")
        lead_id = request.query_params.get("lead_id")
        policy_base_id = request.query_params.get("policy_base_id")
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        sort_by = request.query_params.get("sort_by", "")
        sort_dir = request.query_params.get("sort_dir", "desc")
        
        # Validate required parameters
        if not customer_id:
            return ResponseService.response("BAD_REQUEST", None, "Customer ID is required.", system_code=400)

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
            .select(*risk_columns, "rs.submission_id") \
            .leftJoin("crm_risk_submissions as rs", "rs.risk_id", "rd.id") \
            .where("rd.risk_type_id", risk_type_id) \
            .where("rd.customer_id", customer_id) \
            .where("rd.is_deleted", False)

        # Handle direct filtering parameters first (lead_id or policy_base_id)
        if lead_id and lead_id.strip() and lead_id.lower() not in ['null', 'undefined', '']:
            # Direct lead_id filtering - filter risks by lead_id from crm_risk_submissions
            base_query = base_query.where("rs.lead_id", lead_id)
            
        elif policy_base_id and policy_base_id.strip() and policy_base_id.lower() not in ['null', 'undefined', '']:
            # Direct policy_base_id filtering - get risk_submission_id from crmp_policy_risk_config
            try:
                risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                    .select("risk_submission_id") \
                    .where("policy_base_id", policy_base_id) \
                    .get()
                
                if risk_configs:
                    # Extract the submission IDs
                    submission_ids = [rc["risk_submission_id"] for rc in risk_configs if rc.get("risk_submission_id")]
                    
                    if submission_ids:
                        # Filter risks by submission IDs
                        base_query = base_query.whereIn("rs.id", submission_ids)
                    else:
                        return ResponseService.response("SUCCESS", [], "No risk submissions found for this policy_base_id.")
                else:
                    return ResponseService.response("SUCCESS", [], "No risk configurations found for this policy_base_id.")
                    
            except Exception as e:
                return ResponseService.response("SUCCESS", [], f"Unable to access crmp_policy_risk_config table: {str(e)}")
                
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
            
            if entity_type in ("quotation approval", "quotation"):
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
                
            elif entity_type == "policy":
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
                try:
                    risk_configs = QueryBuilderService("crmp_policy_risk_config") \
                        .select("risk_submission_id") \
                        .where("policy_base_id", policy_base_id) \
                        .get()
                    
                    if risk_configs:
                        # Extract the submission IDs
                        submission_ids = [rc["risk_submission_id"] for rc in risk_configs if rc.get("risk_submission_id")]
                        
                        if submission_ids:
                            # Filter risks by submission IDs
                            base_query = base_query.whereIn("rs.id", submission_ids)
                        else:
                            return ResponseService.response("SUCCESS", [], "No risk submissions found for this policy.")
                    else:
                        return ResponseService.response("SUCCESS", [], "No risk configurations found for this policy.")
                        
                except Exception as e:
                    return ResponseService.response("SUCCESS", [], f"Unable to access crmp_policy_risk_config table: {str(e)}")

        # Define allowed sorting columns
        allowed_sorting_columns = ["id", "code", "risk_code", "risk_type_title", "customer_name"]
        
        # Use QueryBuilderService pagination method
        paginated_result = base_query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        
        if not paginated_result or not paginated_result.get("data"):
            return ResponseService.response("SUCCESS", 
            [],
             "No risk details found for this type and customer.")

        # Process risk data - ensure we get the latest submission for each risk
        results = []
        for risk in paginated_result["data"]:
            risk_id = risk.get("id")
            if not risk_id:
                continue
                
            # Get the latest submission for this risk_id
            latest_submission = QueryBuilderService("crm_risk_submissions")\
                .select("submission_id", "version")\
                .where("risk_id", risk_id)\
                .orderBy("version", "desc")\
                .orderBy("created_at", "desc")\
                .first()
            
            if not latest_submission or not latest_submission.get("submission_id"):
                continue
                
            submission_id = latest_submission["submission_id"]
            version = latest_submission.get("version", 1)
            print(f"DEBUG: Risk {risk_id} - Using latest submission_id: {submission_id}, version: {version}")

            submission = CoreFormSubmission.objects.select_related("form").filter(id=submission_id).first()
            if submission and submission.form:
                _, _, elements = fetch_elements_data(submission.form.id, submission_id=submission.id)
                result_item = {str(ele["id"]): ele.get("value") for ele in elements}
                result_item["submission_id"] = submission.id
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
        # Get the latest risk submission for this risk_id (highest version or latest created)
        risk_detail = QueryBuilderService("crm_risk_submissions") \
            .select("submission_id", "version", "created_at") \
            .where("risk_id", risk_detail_id) \
            .orderBy("version", "desc") \
            .orderBy("created_at", "desc") \
            .first()

        if not risk_detail or not risk_detail.get("submission_id"):
            return ResponseService.response("NOT_FOUND", None, "Submission not found.")

        submission_id = risk_detail["submission_id"]
        version = risk_detail.get("version", 1)
        print(f"DEBUG: Risk {risk_detail_id} - Using latest submission_id: {submission_id}, version: {version}")
        
        submission = CoreFormSubmission.objects.select_related("form").filter(id=submission_id).first()

        if not submission or not submission.form:
            return ResponseService.response("NOT_FOUND", None, "Form or template not found.")

        # Get risk information (id and code)
        risk_info = QueryBuilderService("crm_risks") \
            .select("id", "code") \
            .where("id", risk_detail_id) \
            .first()

        # Build the template response with risk information
        return build_template_response_with_risk(submission.form, submission_id=submission.id, risk_info=risk_info, risk_detail_id=risk_detail_id)

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


def build_template_response_with_risk(template, submission_id=None, risk_info=None, risk_detail_id=None):
    try:
        steps, panels, elements = fetch_template_data(template.id, submission_id=submission_id)

        # Find latest policy for this risk
        latest_policy = None
        if submission_id:
            try:
                # First get the risk_submission record to get its id (not submission_id)
                risk_submission = QueryBuilderService("crm_risk_submissions") \
                    .select("id") \
                    .where("submission_id", submission_id) \
                    .first()
                
                if risk_submission and risk_submission.get("id"):
                    risk_submission_id = risk_submission["id"]
                    
                    # Get policy_base_id from crmp_policy_risk_config using the risk_submission.id
                    policy_config = QueryBuilderService("crmp_policy_risk_config") \
                        .select("policy_base_id") \
                        .where("risk_submission_id", risk_submission_id) \
                        .first()
                
                    if policy_config and policy_config.get("policy_base_id"):
                        policy_base_id = policy_config["policy_base_id"]
                        
                        # Get latest issued policy for this policy_base_id
                        latest_policy_data = QueryBuilderService("crmp_issued_policies") \
                            .select("id", "brokerage_policy_id") \
                            .where("policy_base_id", policy_base_id) \
                            .orderBy("id", "desc") \
                            .first()
                        
                        if latest_policy_data:
                            latest_policy = {
                                "brokerage_policy_id": latest_policy_data.get("brokerage_policy_id"),
                                "issued_policy_id": latest_policy_data.get("id")
                            }
            except Exception as e:
                print(f"WARNING: Failed to fetch latest policy for risk {risk_detail_id}: {e}")

        result = {
            "risk": {
                "id": risk_info.get("id") if risk_info else risk_detail_id,
                "code": risk_info.get("code") if risk_info else None,
                "latest_policy": latest_policy.get("brokerage_policy_id") if latest_policy else None,
                "issued_policy_id": latest_policy.get("issued_policy_id") if latest_policy else None
            },
            "template": {
                "id": template.id,
                "name": template.title,
                "description": template.description,
                "type": template.type,
            },
            "steps": steps,
            "panels": panels,
            "elements": elements,
            
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
        risk = Risk.objects.select_related("risk_type").get(id=risk_detail_id)
        
        # Check if risk is soft deleted
        if risk.is_deleted:
            return ResponseService.response("NOT_FOUND", None, "Risk has been deleted and cannot be updated.")
        
        risk_submission = RiskSubmission.objects.select_related("risk_id").filter(risk_id=risk_detail_id).order_by('-created_at').first()
        if not risk_submission:
            return ResponseService.response("NOT_FOUND", None, "Risk submission not found.")
    except Risk.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Risk not found.")

    # Step 2: Get template from risk_type
    config = QueryBuilderService("crm_opportunity_form_config") \
        .select("form_id") \
        .where("opportunity_type_id", risk.risk_type.id) \
        .where("data_gethering_type", "ONBOARDING") \
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
    form_submission = CoreFormSubmission.objects.get(id=risk_submission.submission_id)
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

    # Step 6: Update Risk and RiskSubmission metadata if needed
    if "lead_id" in data:
        lead_id = data.get("lead_id")
        if lead_id:
            from core_models.crm_models import Opportunity
            lead = Opportunity.objects.get(id=lead_id)
            risk_submission.lead_id = lead
        else:
            risk_submission.lead_id = None
        risk_submission.save()
    # Note: Risk table doesn't have status_id or customer_id fields, they're in RiskSubmission

    return ResponseService.response("SUCCESS", {
        "risk_id": risk.id,
        "risk_code": risk.code,
        "submission_id": form_submission.id
    }, Message.DATA_UPDATED)


def delete_risk(request, risk_detail_id):
    try:
        # Validation
        rules = {
            "risk_id": "required|exists:crm_risks,id"
        }
        custom_messages = {
            "risk_id.required": "Risk ID is required.",
            "risk_id.exists": "Risk with the given ID does not exist."
        }

        errors = ValidatorService.validate({"risk_id": risk_detail_id}, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Check if risk is already soft deleted
        risk = Risk.objects.get(id=risk_detail_id)
        if risk.is_deleted:
            return ResponseService.response("NOT_FOUND", None, "Risk has already been deleted.")

        # Get current user for deleted_by field
        user = request.user if request.user.is_authenticated else None
        current_time = datetime.now()

        # Soft delete risk - set is_deleted to True and add audit fields
        risk.is_deleted = True
        risk.deleted_at = current_time
        risk.deleted_by_id = user.id if user else None
        risk.save()

        print(f"DEBUG: Soft deleted risk {risk_detail_id} by user {user.id if user else 'Anonymous'} at {current_time}")

        return ResponseService.response("SUCCESS", None, Message.DATA_DELETED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, Error.INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['GET', 'POST'])
def risk(request):
    if request.method == 'GET':
        action = ActionService.getAction("RISK", "VIEW_ALL")
        if not AuthService.hasAuthority(request, action):
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        return get_all_risks(request)

    elif request.method == 'POST':
        action = ActionService.getAction("RISK", "CREATE")
        if not AuthService.hasAuthority(request, action):
            return ResponseService.response('FORBIDDEN', None, Error.UN_AUTHORIZED)
        return create_risk_detail(request)


def get_all_risks(request):
    try:
        # Request params
        search_string = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        sort_by = request.GET.get('sort_by')
        sort_dir = request.GET.get('sort_dir')
        sort_by = "r.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        ids = request.GET.get('ids', None)
        filter_json = request.GET.get('filters', '{}')

        # Fields to fetch - excluding policy fields that cause duplication
        all_columns = [
            "r.id",
            "r.code",
            "r.updated_at",
            "r.created_at",
            "MAX(rs.lead_id) AS lead_id",
            "r.risk_type_id",
            "MAX(rs.submission_id) AS submission_id",
            "MAX(rs.id) AS risk_submission_id",
            "rt.title AS risk_type_title",
            "cust.id AS customer_id",
            "cust.name AS customer_name",
            "cust.logo AS customer_logo",
            "MAX(opt.title) AS opportunity_title",
            "r.code AS risk_code",
            # "status.name AS status_name",
            # "status.color AS status_color",
            "con.primary_contact AS customer_primary_contact",
            # "MAX(prc.policy_id) AS policy_id",  
            # "MAX(rp.policy_request_id) AS policy_request_id", 
            # "MAX(rp.status_id) AS policy_status_id", 
            # "MAX(policy_status.name) AS policy_status_name", 
            # "MAX(policy_status.color) AS policy_status_color"
        ]

        query = (
            QueryBuilderService("crm_risks AS r")
            .leftJoin("crm_opportunity_types AS rt", "rt.id", "r.risk_type_id")
            .leftJoin("core_customers AS cust", "cust.id", "r.customer_id")
            .leftJoin("crm_risk_submissions AS rs", "rs.risk_id", "r.id")
            .leftJoin("crm_opportunities AS opt", "opt.id", "rs.lead_id")
            .leftJoin("core_contacts AS con", "con.id", "cust.primary_contact_id")
            .where("r.is_deleted", False)
            # .leftJoin("core_status AS status", "status.id", "rs.status_id")
            # .leftJoin("crmp_policy_risk_config AS prc", "prc.risk_id", "r.id")
            # .leftJoin("crmp_request_policies AS rp", "rp.id", "prc.policy_id")
            # .leftJoin("core_status AS policy_status", "policy_status.id", "rp.status_id")
            .groupBy("r.id")
            .select(*all_columns)
            .apply_conditions(filter_json, [], search_string, ["r.code", "cust.name", "rt.title"])
        )

        if ids:
            id_list = list(map(int, ids.split(',')))
            data = query.whereIn("r.id", id_list).get()
        else:
            data = query.paginate(page, limit, ['r.code', 'r.id'], sort_by, sort_dir)

        # Fetch policy base information for each risk
        risks_data = data.get("data", []) if isinstance(data, dict) else data
        
        for risk in risks_data:
            # Get the risk_submissions_id from the risk data (this is the id from crm_risk_submissions table)
            risk_submissions_id = risk.get("risk_submission_id")
            
            if risk_submissions_id:
                print(f"DEBUG: Processing risk {risk.get('id')} with risk_submissions_id: {risk_submissions_id}")
                
                # Find policy_base_id from crmp_policy_risk_config using the id from crm_risk_submissions table
                policy_risk_config = QueryBuilderService("crmp_policy_risk_config")\
                    .select("policy_base_id")\
                    .where("risk_submission_id", risk_submissions_id)\
                    .first()
                
                if policy_risk_config and policy_risk_config.get("policy_base_id"):
                    policy_base_id = policy_risk_config.get("policy_base_id")
                    print(f"DEBUG: Found policy_base_id: {policy_base_id} for risk_submissions_id: {risk_submissions_id}")
                    
                    # Get all data from crmp_policy_base table
                    policy_base_data = QueryBuilderService("crmp_policy_base")\
                        .select("*")\
                        .where("id", policy_base_id)\
                        .first()
                    
                    if policy_base_data:
                        print(f"DEBUG: Found policy base data for policy_base_id: {policy_base_id}")
                        # Add policy base data as an object to the risk
                        risk["policy_base"] = policy_base_data
                    else:
                        print(f"DEBUG: No policy base data found for policy_base_id: {policy_base_id}")
                        risk["policy_base"] = None
                else:
                    print(f"DEBUG: No policy_risk_config found for risk_submissions_id: {risk_submissions_id}")
                    risk["policy_base"] = None
            else:
                print(f"DEBUG: No risk_submissions_id found for risk {risk.get('id')}")
                risk["policy_base"] = None

        return ResponseService.response("SUCCESS", data, "Risks retrieved successfully.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to fetch risks.")



@transaction.atomic
def create_risk_detail(request):
    data = request.data
    risk_type_id = data.get("risk_type_id")
    customer_id = data.get("customer_id")
    submitted_values = data.get("values", {})

    # Step 1: Validate input
    rules = {
        "risk_type_id": "required|exists:crm_opportunity_types,id",
        "customer_id": "required|exists:core_customers,id",
        "values": "dict"
    }
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.INTERNAL_SERVER_ERROR)

    # Step 2: Get form_id from onboarding config
    config = QueryBuilderService("crm_opportunity_form_config") \
        .select("form_id") \
        .where("opportunity_type_id", risk_type_id) \
        .where("data_gethering_type", "onboarding") \
        .first()

    if not config:
        return ResponseService.response("NOT_FOUND", None, "No onboarding form config found for this risk type.")

    form_id = config["form_id"]
    template = CoreTemplate.objects.get(id=form_id)
    user = request.user

    # Step 3: Parse and validate template fields
    template_response = build_template_response(template)
    try:
        template_data = json.loads(template_response.content)
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Template parsing failed")

    if not template_data.get("is_success"):
        return template_response

    elements = template_data.get("result", {}).get("elements", [])

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

    # Step 4: Create form submission and values
    submission = CoreFormSubmission.objects.create(
        form=template,
        user=user if user.is_authenticated else None,
        customer_id=customer_id
    )

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
    CoreFormSubmissionValue.objects.bulk_create(values_to_create)

    # Step 5: Create Risk and RiskSubmission records
    last_risk = Risk.objects.order_by("-id").first()
    next_id = (last_risk.id + 1) if last_risk else 1
    code = f"RISK-{str(next_id).zfill(4)}"  # Generate code like RISK-0001

    # Get Customer and OpportunityType instances
    from core_models.core_models import Customer, OpportunityType
    customer = Customer.objects.get(id=customer_id)
    risk_type = OpportunityType.objects.get(id=risk_type_id)

    risk = Risk.objects.create(
        code=code,
        customer=customer,
        risk_type=risk_type,
        is_deleted=False,
        deleted_at=None,
        deleted_by=None
    )

    # Get lead instance if provided
    lead = None
    if data.get("lead_id"):
        from core_models.crm_models import Opportunity
        lead = Opportunity.objects.get(id=data.get("lead_id"))

    risk_submission = RiskSubmission.objects.create(
        risk_id=risk,
        submission_id=submission.id,
        lead_id=lead,
        version=1
    )

    return ResponseService.response("SUCCESS", {
        "risk_id": risk.id,
        "risk_code": risk.code,
        "submission_id": submission.id
    }, Message.DATA_CREATED)


@api_view(["GET"])
def get_risk_details_by_lead_and_types(request):
    try:
        # Request params
        lead_id = request.GET.get("lead_id")
        risk_type_ids_str = request.GET.get("risk_type_ids", "")
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "r.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        filter_json = request.GET.get("filters", "{}")

        # Parse comma-separated risk_type_ids
        risk_type_ids = [id.strip() for id in risk_type_ids_str.split(",") if id.strip().isdigit()]

        # Validation
        errors = ValidatorService.validate(
            {"lead_id": lead_id, "risk_type_ids": risk_type_ids},
            {"lead_id": "required|integer", "risk_type_ids": "required|list"}
        )
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Fields to fetch
        all_columns = [
            "r.*",
            "MAX(rs.lead_id) AS lead_id",
            "MAX(rs.submission_id) AS submission_id",
            "MAX(rs.version) AS version",
            "rt.title AS risk_type_title",
            "cust.name AS customer_name",
            "MAX(opt.title) AS opportunity_title"
        ]

        query = (
            QueryBuilderService("crm_risks AS r")
            .leftJoin("crm_risk_submissions AS rs", "rs.risk_id", "r.id")
            .leftJoin("crm_opportunity_types AS rt", "rt.id", "r.risk_type_id")
            .leftJoin("core_customers AS cust", "cust.id", "r.customer_id")
            .leftJoin("crm_opportunities AS opt", "opt.id", "rs.lead_id")
            .select(*all_columns)
            .where("rs.lead_id", lead_id)
            .whereIn("r.risk_type_id", risk_type_ids)
            .where("r.is_deleted", False)
            .groupBy("r.id")
            .apply_conditions(filter_json, [], search_string, ["r.code", "cust.name", "rt.title"])
        )

        paginated = query.paginate(page, limit, ['r.code', 'r.id'], sort_by, sort_dir)
        risks = paginated.get("data", [])

        for risk in risks:
            submission_id = risk.get("submission_id")
            if not submission_id:
                continue

            submission = CoreFormSubmission.objects.select_related("form").filter(id=submission_id).first()
            if not submission or not submission.form:
                continue

            steps, panels, elements = fetch_template_data(submission.form.id, submission_id=submission.id)

            risk["template"] = {
                "id": submission.form.id,
                "name": submission.form.title,
                "description": submission.form.description,
                "type": submission.form.type
            }
            risk["steps"] = steps
            risk["panels"] = panels
            risk["elements"] = elements

        return ResponseService.response("SUCCESS", risks, "Risk details retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_ERROR", None, f"Something went wrong: {str(e)}")

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




@api_view(["GET"])
def get_risk_submission_values(request, risk_id):
    """
    Get all submission values for all versions of a specific risk ID.
    
    Parameters:
    - risk_id: ID of the risk to get submission values for
    
    Returns:
    - Array of submission values for all versions
    """
    try:
        # Validate risk_id
        errors = ValidatorService.validate(
            {"risk_id": risk_id},
            {"risk_id": "required|integer|exists:crm_risks,id"}
        )
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Get all versions for this risk_id from crm_risk_submissions
        risk_versions = QueryBuilderService("crm_risk_submissions as rs") \
            .select(
                "rs.id",
                "rs.submission_id", 
                "rs.version",
                "rs.created_at",
                "rs.updated_at"
            ) \
            .leftJoin("core_form_submissions as cfs", "cfs.id", "rs.submission_id") \
            .where("rs.risk_id", risk_id) \
            .orderBy("rs.version", "desc") \
            .orderBy("rs.created_at", "desc") \
            .get()

        if not risk_versions:
            return ResponseService.response("NOT_FOUND", [], "No versions found for this risk.")

        # Process each version to get submission values
        result = []
        for version in risk_versions:
            risk_submission_id = version.get("id")
            if not risk_submission_id:
                continue

            submission_id = version.get("submission_id")
            if not submission_id:
                continue
                
            # Get submission values
            submission_values = QueryBuilderService("core_form_submission_valuess") \
                .select("custom_form_element_id", "value") \
                .where("form_submission_id", submission_id) \
                .get()
            
            # Convert to dictionary format with element IDs as keys
            values_dict = {str(v["custom_form_element_id"]): v["value"] for v in submission_values}
            
            # Trace risk_submissions_id through crmp_policy_risk_config to get base_id
            policy_risk_config = QueryBuilderService("crmp_policy_risk_config as prc") \
                .select("prc.policy_base_id") \
                .where("prc.risk_submission_id", risk_submission_id) \
                .first()
            
            brokerage_policy_id = None
            issued_policy_id = None
            insurer_id = None
            insurer_name = None
            if policy_risk_config and policy_risk_config.get("policy_base_id"):
                policy_base_id = policy_risk_config.get("policy_base_id")
                
                # Get insurer_id from crmp_policy_base table
                policy_base = QueryBuilderService("crmp_policy_base as pb") \
                    .select("pb.insurer_id") \
                    .where("pb.id", policy_base_id) \
                    .first()
                
                if policy_base and policy_base.get("insurer_id"):
                    insurer_id = policy_base.get("insurer_id")
                    
                    # Get insurer name from core_service_providers table
                    insurer = QueryBuilderService("core_service_providers as sp") \
                        .select("sp.name") \
                        .where("sp.id", insurer_id) \
                        .first()
                    
                    if insurer:
                        insurer_name = insurer.get("name")
                
                # Get brokerage_policy_id from crmp_issued_policies using base_id
                issued_policy = QueryBuilderService("crmp_issued_policies as ip") \
                    .select("ip.brokerage_policy_id","ip.id") \
                    .where("ip.policy_base_id", policy_base_id) \
                    .first()
                
                if issued_policy:
                    brokerage_policy_id = issued_policy.get("brokerage_policy_id")
                    issued_policy_id = issued_policy.get("id")
            
            # Add metadata
            values_dict["submission_id"] = submission_id
            values_dict["risk_detail_id"] = risk_id
            values_dict["version"] = version.get("version")
            values_dict["risk_submissions_id"] = risk_submission_id
            values_dict["brokerage_policy_id"] = brokerage_policy_id
            values_dict["issued_policy_id"] = issued_policy_id
            values_dict["insurer_id"] = insurer_id
            values_dict["insurer_name"] = insurer_name
            
            result.append(values_dict)

        return ResponseService.response("SUCCESS", result, "Risk submission values retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve risk submission values.")


@api_view(["GET"])
def get_risk_detail_versions(request, risk_detail_id):
    """
    Get all versions for a specific risk detail ID from crm_risk_submissions table.
    
    Parameters:
    - risk_detail_id: ID of the risk detail to get versions for
    
    Returns:
    - List of all versions with submission details
    """
    try:
        # Validate risk_detail_id
        errors = ValidatorService.validate(
            {"risk_detail_id": risk_detail_id},
            {"risk_detail_id": "required|integer|exists:crm_risks,id"}
        )
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Get all versions for this risk_id from crm_risk_submissions
        risk_versions = QueryBuilderService("crm_risk_submissions as rs") \
            .select(
                "rs.id",
                "rs.submission_id", 
                "rs.version",
                "rs.created_at",
                "rs.updated_at",
                "rs.lead_id",
                "cfs.form_id",
                "ct.title as form_title",
                "ct.description as form_description"
            ) \
            .leftJoin("core_form_submissions as cfs", "cfs.id", "rs.submission_id") \
            .leftJoin("core_templates as ct", "ct.id", "cfs.form_id") \
            .where("rs.risk_id", risk_detail_id) \
            .orderBy("rs.version", "desc") \
            .orderBy("rs.created_at", "desc") \
            .get()

        if not risk_versions:
            return ResponseService.response("NOT_FOUND", [], "No versions found for this risk detail.")

        return ResponseService.response("SUCCESS", risk_versions, "Risk detail versions retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to retrieve risk detail versions.")


@api_view(["GET"])
def get_vendor_products_by_risk_type(request):
    try:
        # Get and parse params
        raw_ids = request.GET.get("risk_type_id", "")
        risk_type_ids = [int(x) for x in raw_ids.split(",") if x.strip().isdigit()]

        # Validate
        if not risk_type_ids:
            return ResponseService.response("VALIDATION_ERROR", {"risk_type_id": "At least one valid risk_type_id is required."}, "Validation Error")

        # Check if it's a single risk_type_id or multiple
        if len(risk_type_ids) == 1:
            # Single risk_type_id: Get data directly from core_vendor_products table
            vendor_products = QueryBuilderService("core_vendor_products")\
                .whereIn("category_id", risk_type_ids)\
                .get()

            if not vendor_products:
                return ResponseService.response("NOT_FOUND", [], "No vendor products found for the provided risk type.")

            return ResponseService.response(
                "SUCCESS",
                vendor_products,
                "Vendor products fetched successfully."
            )
        else:
            # Multiple risk_type_ids: Use complex logic with core_products table
            # Step 1: Find products in core_products where category_id matches risk_type_ids
            products = QueryBuilderService("core_products")\
                .select("id", "category_id")\
                .whereIn("category_id", risk_type_ids)\
                .get()

            if not products:
                return ResponseService.response("NOT_FOUND", [], "No products found for the provided risk types.")

            # Extract product IDs and group by risk type
            product_ids = [product["id"] for product in products]
            products_by_risk_type = {}
            for product in products:
                risk_type = product["category_id"]
                if risk_type not in products_by_risk_type:
                    products_by_risk_type[risk_type] = []
                products_by_risk_type[risk_type].append(product["id"])

            # Step 2: Find product_group_ids in core_product_group_products that have these product_ids
            product_group_products = QueryBuilderService("core_product_group_products")\
                .select("product_group_id", "product_id")\
                .whereIn("product_id", product_ids)\
                .get()

            if not product_group_products:
                return ResponseService.response("NOT_FOUND", [], "No product groups found for the provided products.")

            # Step 3: Find product groups that contain products from ALL risk types
            product_group_counts = {}
            for pgp in product_group_products:
                group_id = pgp["product_group_id"]
                if group_id not in product_group_counts:
                    product_group_counts[group_id] = set()
                product_group_counts[group_id].add(pgp["product_id"])

            # Find groups that have products from ALL risk types
            common_group_ids = []
            for group_id, group_products in product_group_counts.items():
                # Check if this group has products from all risk types
                has_all_risk_types = True
                for risk_type, risk_products in products_by_risk_type.items():
                    # Check if this group has at least one product from this risk type
                    if not any(product_id in group_products for product_id in risk_products):
                        has_all_risk_types = False
                        break
                
                if has_all_risk_types:
                    common_group_ids.append(group_id)

            if not common_group_ids:
                return ResponseService.response("NOT_FOUND", [], "No product groups found that contain products from all specified risk types.")

            # Step 4: Get product groups from core_product_groups table
            product_groups = QueryBuilderService("core_product_groups")\
                .whereIn("id", common_group_ids)\
                .get()

            if not product_groups:
                return ResponseService.response("NOT_FOUND", [], "No product groups found in core_product_groups table.")

            return ResponseService.response(
                "SUCCESS",
                product_groups,
                f"Found {len(common_group_ids)} product groups containing products from all {len(risk_type_ids)} risk types."
            )

    except Exception as e:
        return ResponseService.response("INTERNAL_ERROR", None, f"Something went wrong: {str(e)}")


@api_view(["GET"])
def export_risks_by_type_ids(request):
    """
    Export form elements for specified risk types to Excel.
    Endpoint: policy/risk-export?risk_type_ids=1,2,3
    """
    # Get risk_type_ids from query parameters
    risk_type_ids_param = request.GET.get('risk_type_ids', '')
    if not risk_type_ids_param:
        return ResponseService.response("VALIDATION_ERROR", None, "risk_type_ids parameter is required")
    
    # Parse risk_type_ids
    try:
        risk_type_ids = [int(id.strip()) for id in risk_type_ids_param.split(',') if id.strip()]
    except ValueError:
        return ResponseService.response("VALIDATION_ERROR", None, "Invalid risk_type_ids format. Use comma-separated integers like: 1,2,3")
    
    if not risk_type_ids:
        return ResponseService.response("VALIDATION_ERROR", None, "No valid risk_type_ids provided")

    queries = []

    for rt_id in risk_type_ids:
        # Get opportunity type
        opp = QueryBuilderService("crm_opportunity_types").where("id", rt_id).first()
        if not opp:
            continue
        title = (opp.get("title") or f"Risk_{rt_id}")[:31]

        # Get form config
        config = QueryBuilderService("crm_opportunity_form_config")\
            .where("opportunity_type_id", rt_id)\
            .where("data_gethering_type", "onboarding")\
            .first()
        
        if not config or not config.get("form_id"):
            continue

        # Get form elements
        elements = QueryBuilderService("core_form_custom_form_elements as ele")\
            .leftJoin("core_form_custom_form_panels as panel", "panel.id", "ele.panel_id")\
            .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id")\
            .select("ele.*", "fe.title as element_title")\
            .where("panel.form_id", config["form_id"])\
            .orderBy("ele.order_number")\
            .get()

        if not elements:
            continue

        select_parts = []
        for el in elements:
            label = el.get("label") or el.get("element_title") or f"Field_{el['id']}"
            safe_label = label.replace('"', '""')
            select_parts.append(f'NULL AS "{safe_label}"')

        if not select_parts:
            continue

        sql = f"""SELECT {', '.join(select_parts)} LIMIT 1"""
        queries.append({"query": sql, "title": title})

    if not queries:
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, "No valid data found")

    payload = {
        "queries": queries,
        "styles": {
            "common": {
                "header": {
                    "font": {"bold": True, "color": "0000FF"},
                    "alignment": {"horizontal": "center"}
                }
            }
        }
    }

    exporter = SQLToExcelExporter()
    export_response = exporter.export(payload)

    if export_response["status"] == "SUCCESS":
        return ResponseService.response("SUCCESS", export_response["data"], export_response["message"])

    return ResponseService.response("INTERNAL_SERVER_ERROR", None, export_response["message"])


@api_view(["POST"])
def process_uploaded_risk_excel(request):
    """
    Process uploaded Excel file with form values.
    Endpoint: policy/process-risk-excel
    
    Expected payload:
    {
        "file_key": "path/to/uploaded/excel/file.xlsx",
        "customer_id": 123,  // Optional
        "policy_base_id": 456,  // Optional
        "lead_id": 789  // Optional
    }
    
    This will:
    1. Download the Excel file from S3 using the file_key
    2. Parse the Excel data to extract form values
    3. Process and store the form values
    4. Create Risk records with optional customer/lead/policy_base associations
    """
    try:
        data = request.data
        
        # Validate required and optional fields
        validation_rules = {
            "file_key": "required|string",
            "customer_id": "nullable|integer|exists:core_customers,id",
            "policy_base_id": "nullable|integer|exists:crmp_policy_base,id", 
            "lead_id": "nullable|integer|exists:crm_opportunities,id"
        }
        
        custom_messages = {
            "file_key.required": "file_key is required",
            "customer_id.exists": "Customer with the given ID does not exist",
            "policy_base_id.exists": "Policy base with the given ID does not exist",
            "lead_id.exists": "Lead/Opportunity with the given ID does not exist"
        }
        
        errors = ValidatorService.validate(data, validation_rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)
        
        file_key = data.get('file_key')
        customer_id = data.get('customer_id')
        policy_base_id = data.get('policy_base_id')
        lead_id = data.get('lead_id')
        
        # Generate CDN URL from file_key
        cdn_base_url = os.getenv("CDN_BASE_URL")
        file_url = f"{cdn_base_url}/{file_key}"
        
        print(f"Processing uploaded Excel file: {file_url}")
        print(f"Customer ID: {customer_id}, Policy Base ID: {policy_base_id}, Lead ID: {lead_id}")
        
        # Download and process the Excel file
        result = _process_excel_file(file_url, file_key, customer_id, policy_base_id, lead_id)
        
        return result
        
    except Exception as e:
        print(f"Error processing uploaded Excel: {str(e)}")
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to process Excel file")


def _process_excel_file(file_url, file_key, customer_id=None, policy_base_id=None, lead_id=None):
    """
    Download Excel file from S3 and process the form values
    """
    try:
        import requests
        import pandas as pd
        from io import BytesIO
        
        # Download the Excel file
        response = requests.get(file_url)
        response.raise_for_status()
        
        # Read Excel file
        excel_data = pd.read_excel(BytesIO(response.content), sheet_name=None)
        
        processed_data = []
        
        # Process each sheet
        for sheet_name, df in excel_data.items():
            print(f"Processing sheet: {sheet_name}")
            
            # Try to extract risk type from sheet name
            risk_type_id = None
            
            # Method 1: Try "Risk_Type_X" format
            try:
                if sheet_name.startswith("Risk_Type_"):
                    risk_type_id = int(sheet_name.split('_')[-1])
            except (ValueError, IndexError):
                pass
            
            # Method 2: Try to find risk type by matching sheet name with opportunity type titles
            if not risk_type_id:
                # Get all opportunity types and try to match by title
                opportunity_types = QueryBuilderService("crm_opportunity_types")\
                    .select("id", "title")\
                    .get()
                
                for opp_type in opportunity_types:
                    if opp_type.get("title") and opp_type["title"].lower().strip() == sheet_name.lower().strip():
                        risk_type_id = opp_type["id"]
                        break
            
            if not risk_type_id:
                print(f"Could not extract risk_type_id from sheet name: {sheet_name}")
                continue
            
            print(f"Found risk_type_id: {risk_type_id} for sheet: {sheet_name}")
            
            # Get form config for this risk type
            config = QueryBuilderService("crm_opportunity_form_config")\
                .where("opportunity_type_id", risk_type_id)\
                .where("data_gethering_type", "onboarding")\
                .first()
            
            if not config or not config.get("form_id"):
                print(f"No form config found for risk_type_id: {risk_type_id}")
                continue
            
            print(f"Found form config: form_id={config['form_id']} for risk_type_id: {risk_type_id}")
            
            # Get form elements to map column names to element IDs
            elements = QueryBuilderService("core_form_custom_form_elements as ele")\
                .leftJoin("core_form_custom_form_panels as panel", "panel.id", "ele.panel_id")\
                .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id")\
                .select("ele.*", "fe.title as element_title")\
                .where("panel.form_id", config["form_id"])\
                .orderBy("ele.order_number")\
                .get()
            
            # Create mapping from column names to element IDs
            column_to_element = {}
            required_elements = {}
            for el in elements:
                label = el.get("label") or el.get("element_title") or f"Field_{el['id']}"
                column_to_element[label] = el['id']
                # Check if this element is required
                if el.get("is_required"):
                    required_elements[label] = el['id']
            
            print(f"Column to element mapping: {column_to_element}")
            print(f"Required elements: {required_elements}")
            print(f"DataFrame columns: {list(df.columns)}")
            print(f"DataFrame shape: {df.shape}")
            print(f"DataFrame head:\n{df.head()}")
            
            # Check if DataFrame is empty
            if df.empty:
                print(f"Warning: Sheet '{sheet_name}' is empty - no data to process")
                continue
            
            # Process each row in the sheet
            for index, row in df.iterrows():
                if row.isnull().all():  # Skip empty rows
                    continue
                
                print(f"Processing row {index}: {row.to_dict()}")
                
                # Validate required fields
                missing_required_fields = []
                for required_label, element_id in required_elements.items():
                    if required_label in row:
                        value = row[required_label]
                        if pd.isna(value) or value == "" or str(value).strip() == "":
                            missing_required_fields.append(required_label)
                    else:
                        missing_required_fields.append(required_label)
                
                if missing_required_fields:
                    print(f"Row {index} missing required fields: {missing_required_fields}")
                    return ResponseService.response(
                        "VALIDATION_ERROR",
                        {
                            "error": "Missing required fields",
                            "missing_fields": missing_required_fields,
                            "row_index": index,
                            "sheet_name": sheet_name
                        },
                        Error.VALIDATION_ERROR,
                        "VALIDATION_ERROR"
                       
                    )
                
                print(f"Row {index} passed required field validation")
                
                # Create form submission
                submission = CoreFormSubmission.objects.create(
                    form_id=config["form_id"],
                    customer_id=customer_id,
                    user=None
                )
                
                # Process form values
                form_values = []
                for column_name, value in row.items():
                    if pd.isna(value) or value == "":
                        continue
                    
                    print(f"Processing column: {column_name}, value: {value}")
                    
                    if column_name in column_to_element:
                        element_id = column_to_element[column_name]
                        
                        # Get the form_element_id from the element
                        element = next((el for el in elements if el['id'] == element_id), None)
                        form_element_id = element.get('element_id') if element else None
                        
                        if form_element_id:
                            form_values.append({
                                "form_submission": submission,
                                "custom_form_element_id": element_id,
                                "form_element_id": form_element_id,
                                "value": str(value)
                            })
                            print(f"Mapped to element_id: {element_id}, form_element_id: {form_element_id}")
                        else:
                            print(f"Warning: No form_element_id found for custom_form_element_id: {element_id}")
                    else:
                        print(f"No mapping found for column: {column_name}")
                
                # Bulk create form values
                if form_values:
                    CoreFormSubmissionValue.objects.bulk_create([
                        CoreFormSubmissionValue(**fv) for fv in form_values
                    ])
                    print(f"Created {len(form_values)} form values")
                
                # Create Risk record for this row
                from core_models.crm_models import Risk, RiskSubmission
                from core_models.core_models import Customer, OpportunityType
                
                # Generate risk code
                last_risk = Risk.objects.order_by("-id").first()
                next_id = (last_risk.id + 1) if last_risk else 1
                risk_code = f"RISK-{str(next_id).zfill(4)}"
                
                # Get risk type instance
                risk_type = OpportunityType.objects.get(id=risk_type_id)
                
                # Get customer instance if customer_id is provided
                customer_instance = None
                if customer_id:
                    customer_instance = Customer.objects.get(id=customer_id)
                
                # Create Risk record
                risk = Risk.objects.create(
                    code=risk_code,
                    customer=customer_instance,
                    risk_type=risk_type,
                    is_deleted=False,
                    deleted_at=None,
                    deleted_by=None
                )
                
                # Get lead instance if lead_id is provided
                lead_instance = None
                if lead_id:
                    from core_models.crm_models import Opportunity
                    lead_instance = Opportunity.objects.get(id=lead_id)
                
                # Create RiskSubmission record
                risk_submission = RiskSubmission.objects.create(
                    risk_id=risk,
                    submission_id=submission.id,
                    lead_id=lead_instance,
                    version=1
                )
                
                print(f"Created Risk: {risk.code} (ID: {risk.id}) with RiskSubmission: {risk_submission.id}")
                
                processed_data.append({
                    "submission_id": submission.id,
                    "risk_id": risk.id,
                    "risk_code": risk.code,
                    "risk_type_id": risk_type_id,
                    "form_id": config["form_id"],
                    "values_count": len(form_values),
                    "customer_id": customer_id,
                    "lead_id": lead_id,
                    "policy_base_id": policy_base_id
                })
        
        # Check if any data was processed
        if len(processed_data) == 0:
            return ResponseService.response(
                "VALIDATION_ERROR",
                None,
                "Excel file contains no data to process. Please ensure the file has data rows in the sheets.",
                "VALIDATION_ERROR"
            )
        
        return ResponseService.response(
            "SUCCESS",
            {
                "processed_submissions": len(processed_data),
                "submissions": processed_data,
                "file_key": file_key,
                "total_risks_created": len(processed_data)
            },
            Message.DATA_CREATED
        )
        
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Failed to process Excel file")


# @api_view(["POST"])
# def process_risk_form_submission(request):
#     """
#     Process uploaded risk form data from Excel template.
#     Endpoint: policy/risk-form-submission
    
#     Expected payload:
#     {
#         "document_key": "path/to/uploaded/excel/file.xlsx",
#         "risk_type_ids": [1, 2, 3],
#         "customer_id": 123
#     }
#     """
#     try:
#         data = request.data
        
#         # Validate required fields
#         required_fields = ["document_key", "risk_type_ids", "customer_id"]
#         for field in required_fields:
#             if field not in data:
#                 return ResponseService.response("VALIDATION_ERROR", {field: ["This field is required"]}, "Missing required field")
        
#         document_key = data["document_key"]
#         risk_type_ids = data["risk_type_ids"]
#         customer_id = data["customer_id"]
        
#         # Validate risk_type_ids is a list
#         if not isinstance(risk_type_ids, list):
#             return ResponseService.response("VALIDATION_ERROR", {"risk_type_ids": ["Must be a list"]}, "Invalid risk_type_ids format")
        
#         print(f"Processing risk form submission for customer {customer_id}, risk types: {risk_type_ids}")
#         print(f"Document key: {document_key}")
        
#         # Get the document from S3 using the document key
#         cdn_base_url = os.getenv("CDN_BASE_URL")
#         document_url = f"{cdn_base_url}/{document_key}"
        
#         print(f"Document URL: {document_url}")
        
#         # Here you would typically:
#         # 1. Download the Excel file from the URL
#         # 2. Parse the Excel data
#         # 3. Extract form values
#         # 4. Create form submissions in the database
#         # 5. Link them to the customer and risk types
        
#         # For now, return success with the document info
#         return ResponseService.response(
#             "SUCCESS",
#             {
#                 "document_url": document_url,
#                 "document_key": document_key,
#                 "customer_id": customer_id,
#                 "risk_type_ids": risk_type_ids,
#                 "message": "Form submission received and will be processed"
#             },
#             "Risk form submission received successfully"
#         )
        
#     except Exception as e:
#         print(f"Error processing risk form submission: {str(e)}")
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

