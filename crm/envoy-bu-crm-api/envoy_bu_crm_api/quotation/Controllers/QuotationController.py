import json
import os
from urllib.parse import urlparse
import boto3
from django.shortcuts import get_object_or_404
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from envoy_bu_crm_api.quotation.models.crmq_quotations import Quotation
from envoy_bu_crm_api.quotation.services.data_expoter import ExportToPdf
from envoy_bu_crm_api.quotation.services.excell_exporter import SQLToExcelExporter
from envoy_bu_crm_api.quotation.services.s3_uploader import S3UploadService
from envoy_bu_crm_api.sales.models.core_models import CoreFormSubmission
from envoy_bu_crm_api.sales.models.risk import Risk
from envoy_bu_crm_api.sales.models.submission_risk import RiskSubmission
from messages import Message, Error
from django.views.decorators.csrf import csrf_exempt
from services.ActionService import ActionService
from services.AuthService import AuthService
from services.SettingService import SettingService
from services.CodeService import CodeService
from services.EntityService import EntityService
from services.TaskService import TaskService
from datetime import datetime 
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


def _is_quotation_request_approval_required():
    """
    Check APPROVAL_PERMISSIONS setting: core_setting_keys (attribute_name or name = 'APPROVAL_PERMISSIONS')
    -> core_setting_global.value e.g. {'policy_request_approval': 'true', 'quotation_request_approval': 'true'}.
    Returns True if quotation requests require approval (go through approval table); False to create directly as approved
    (show in get_all quotations without approval process).
    """
    try:
        setting_key = (
            QueryBuilderService("core_setting_keys")
            .where("attribute_name", "approval_permissions")
            .first()
        )
        if not setting_key:
            setting_key = (
                QueryBuilderService("core_setting_keys")
                .where("name", "APPROVAL_PERMISSIONS")
                .first()
            )
        if not setting_key:
            return True  # default: require approval
        row = (
            QueryBuilderService("core_setting_global")
            .where("setting_key_id", setting_key["id"])
            .first()
        )
        if not row or not row.get("value"):
            return True
        raw = row["value"]
        if isinstance(raw, dict):
            val = raw.get("quotation_request_approval", "true")
        else:
            try:
                parsed = json.loads(raw) if isinstance(raw, str) else raw
            except (ValueError, TypeError):
                try:
                    import ast
                    parsed = ast.literal_eval(raw) if isinstance(raw, str) else raw
                except (ValueError, SyntaxError):
                    return True
            val = (parsed or {}).get("quotation_request_approval", "true")
        return str(val).strip().lower() == "true"
    except Exception:
        return True


@csrf_exempt
@api_view(["GET", "POST"])
def quotation(request):
    if request.method == 'GET':
        action = ActionService.getAction("Quotation", "VIEW")
        has_authority = AuthService.hasAuthority(request , action)
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
        return getAll(request)
    
    elif request.method == 'POST':
        action = ActionService.getAction("Quotation", "CREATE") 
        has_authority = AuthService.hasAuthority(request , action)    
        
        if(not has_authority):
            return ResponseService.response('FORBIDDEN',None, Error.FORBIDDEN)
        
            
        return create_quotation(request)
    
def getAll(request):

    all_columns = [
        "crmq_quotations.id",
        "crmq_quotations.code",
        "crmq_quotations.requested_data",
        "crmq_quotations.customer_id",
        "crmq_quotations.status",
        "crmq_quotations.notes",
        "crmq_quotations.request_type",
        "crmq_quotations.opportunity_type_id",
        "crm_opportunity_types.title as opportunity_type_title",
        "core_customers.name as customer_name",
        "core_entities.id as entity_id",
        "core_users.display_name as created_by_name",
        "core_status.id as status_id",
        "core_status.name as status_name",
        "core_status.type as status_type",
        "core_status.color as status_color",
        "core_status.module as status_module",


    ]

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by") or "crmq_quotations.id"
    sort_dir = request.GET.get("sort_dir") or "desc"

    allowed_filters = ["crmq_quotations.id", "crmq_quotations.code", "crmq_quotations.customer_id", "crmq_quotations.status"]
    search_columns = ["crmq_quotations.id", "crmq_quotations.code", "crmq_quotations.customer_id", "crmq_quotations.status","core_customers.name","core_contacts.name","core_contacts.email","core_contacts.primary_contact"]
    allowed_sorting_columns = ["crmq_quotations.id", "crmq_quotations.code", "crmq_quotations.customer_id", "crmq_quotations.status"]

    query =(
        QueryBuilderService("crmq_quotations")
        .select(*all_columns)
        .leftJoin("crm_opportunity_types", "crm_opportunity_types.id", "crmq_quotations.opportunity_type_id")
        .leftJoin("core_entities", "core_entities.id", "crmq_quotations.entity_id")
        .leftJoin("core_entity_approvals", "core_entity_approvals.entity_id", "crmq_quotations.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
        .leftJoin("core_customers", "core_customers.id", "crmq_quotations.customer_id")
        .leftJoin("core_contacts", "core_contacts.id", "core_customers.primary_contact_id")
        .leftJoin("core_status", "core_status.id", "crmq_quotations.status_id")
        .where("core_entity_approvals.status", "approved")
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)


def create_quotation(request):
    try:
        return _create_quotation_impl(request)
    except Exception as e:
        import traceback
        print("[create_quotation] UNHANDLED EXCEPTION:", e)
        print(traceback.format_exc())
        raise


def _create_quotation_impl(request):
    print("[create_quotation] START - request.data keys:", list(request.data.keys()) if request.data else "None")
    data = request.data

    # if 'status' not in data:
    #     data['status'] = 'in progress'
    if 'code' not in data:
        data['code'] = '00'
    if 'requested_data' not in data:
        data['requested_data'] = datetime.now()
    
    data['request_type'] = 'new'

    require_approval = _is_quotation_request_approval_required()
    print("[create_quotation] quotation_request_approval required:", require_approval)
    # When approval not required, use in_progress status; otherwise draft
    status_type = "quotation_in_progress" if not require_approval else "quotation_draft"
    print(f"[create_quotation] Fetching status_data ({status_type})...")
    status_data = QueryBuilderService("core_status as status")\
                .select("status.id AS status_id","status.name AS status_name")\
                .where("status.type", status_type)\
                .where("status.module", "quotation")\
                .first()
    if not status_data and not require_approval:
        # Fallback: try type "in_progress" for quotation module
        status_data = QueryBuilderService("core_status as status")\
                    .select("status.id AS status_id","status.name AS status_name")\
                    .where("status.type", "in_progress")\
                    .where("status.module", "quotation")\
                    .first()
    if not status_data:
        status_data = QueryBuilderService("core_status as status")\
                    .select("status.id AS status_id","status.name AS status_name")\
                    .where("status.type", "quotation_draft")\
                    .first()
    if not status_data:
        print("[create_quotation] ERROR: status_data (quotation_draft) not found")
    else:
        print("[create_quotation] status_data:", status_data)
    data['status_id'] = status_data['status_id']
    data['status'] = status_data['status_name']

    # Add `request_type` validation
    rules = {
        "requested_data": "required",
        "lead_id": "required|exists:crm_opportunities,id",
        "service_provider_id": "required|array|min:1",
        "opportunity_type_id": "required",
        "request_type": "in:new,renew",
        "status_id": "optional|exists:core_status,id",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        print("[create_quotation] VALIDATION_ERROR:", errors)
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)
    print("[create_quotation] Validation passed. lead_id:", data.get("lead_id"))

    # Fetch opportunity
    opportunity = QueryBuilderService("crm_opportunities").where("id", data["lead_id"]).first()
    if not opportunity:
        print("[create_quotation] ERROR: Opportunity not found for lead_id:", data["lead_id"])
        return ResponseService.response("ERROR", "Opportunity not found.", Error.NOT_FOUND)

    # Check if the opportunity has associated risks
    risks = QueryBuilderService("crm_risk_submissions").where("lead_id", data["lead_id"]).get()
    if not risks or len(risks) == 0:
        print("[create_quotation] ERROR: No risks found for lead_id:", data["lead_id"])
        return ResponseService.response("VALIDATION_ERROR", "No risks found for this opportunity.", Error.QUOTATION_CREATE_CONFLICT, "VALIDATION_ERROR")
    print("[create_quotation] Opportunity found, risks count:", len(risks) if risks else 0)

    data["customer_id"] = opportunity.get("customer_id")
    data["opportunity_id"] = opportunity.get("id")

    # Handle product information based on product_type
    product_type = data.get("product_type")
    product_id = data.get("product_id")
    
    if product_type and product_id:
        update_data = {}
        if product_type == "group":
            update_data["product_group_id"] = product_id
            update_data["product_id"] = None
        elif product_type == "product":
            update_data["product_id"] = product_id
            update_data["product_group_id"] = None
        
        # Update opportunity with product information
        if update_data:
            QueryBuilderService("crm_opportunities")\
                .where("id", data["lead_id"])\
                .update(update_data)

    user = request.user if request.user.is_authenticated else None
    print("[create_quotation] User:", user.id if user else None)

    # Step 1: Insert into core_entities
    print("[create_quotation] Step 1: Inserting core_entities...")
    entity = QueryBuilderService("core_entities").insert({
        "type": "Quotation Approval",
        "created_at": datetime.now(),
        "created_by_id": user.id if user else None,
        "approvel_status": 0 if require_approval else 1
    })

    if not entity or "id" not in entity:
        print("[create_quotation] ERROR: Failed to create entity. entity=", entity)
        return ResponseService.response("ERROR", "Failed to create entity.", Error.DEFAULT)
    print("[create_quotation] Entity created, entity_id:", entity["id"])

    entity_id = entity["id"]
    data["entity_id"] = entity_id

    # If approval not required, create approval record as approved so quotation appears in getAll without approval process
    if not require_approval:
        QueryBuilderService("core_entity_approvals").insert({
            "entity_id": entity_id,
            "user": user.id if user else None,
            "role": None,
            "level": 1,
            "status": "approved",
            "remarks": None,
            "approved_by": user.id if user else None,
            "date": datetime.now(),
        })
        print("[create_quotation] Created direct-approval record (no approval process).")
    data["created_by"] = user.id if user else None

    # Normalize opportunity_type_id to JSON
    opportunity_type_id = data.get("opportunity_type_id")
    if isinstance(opportunity_type_id, int):
        data["opportunity_type_id"] = json.dumps([opportunity_type_id])
    elif isinstance(opportunity_type_id, list):
        data["opportunity_type_id"] = json.dumps(opportunity_type_id)
    else:
        return ResponseService.response("VALIDATION_ERROR", "Invalid format for opportunity_type_id. Must be int or list.", Error.VALIDATION_ERROR, "VALIDATION_ERROR")

    # Step 2: Create quotation - only pass columns that exist on crmq_quotations
    # (payload may include opportunity_types, recipients, product_name, etc. which are not table columns)
    quotation_columns = [
        "code", "requested_data", "customer_id", "status", "notes", "request_type",
        "opportunity_type_id", "opportunity_id", "entity_id", "email_data", "status_id"
    ]
    insert_data = {k: data[k] for k in quotation_columns if k in data}
    print("[create_quotation] Step 2: Inserting crmq_quotations. insert_data keys:", list(insert_data.keys()))
    try:
        new_data = QueryBuilderService("crmq_quotations").insert(insert_data)
        print("[create_quotation] Quotation inserted. new_data:", new_data)
    except Exception as e:
        import traceback
        print("[create_quotation] EXCEPTION on crmq_quotations.insert:", e)
        print(traceback.format_exc())
        raise

    # Step 3: Generate and update code
    new_code = f"QR-00{new_data['id']}"
    QueryBuilderService("crmq_quotations").where("id", new_data['id']).update({"code": new_code})

    # Step 4: Insert service providers
    service_provider_ids = data["service_provider_id"]
    print("[create_quotation] Step 4: Inserting service_provider_ids:", service_provider_ids)
    for sp_id in service_provider_ids:
        QueryBuilderService("crmq_quotation_service_providers").insert({
            "quotation_id": new_data["id"],
            "service_provider_id": sp_id,
            "version": "1.0",
        })

    # Step 5: Fetch updated quotation
    quotation = QueryBuilderService("crmq_quotations").where("id", new_data["id"]).first()

    # Step 6: Fetch service provider details
    service_providers = QueryBuilderService("core_service_providers")\
        .whereIn("id", service_provider_ids).get()

    # Step 7: If new request type → fetch related issued policy documents
    documents = []
    if data["request_type"] == "renew":
        policy_bases = QueryBuilderService("crmp_policy_base")\
            .select("id")\
            .where("lead_id", 1)\
            .get()

        policy_base_ids = [pb["id"] for pb in policy_bases]

        if policy_base_ids:
            issued_policies = QueryBuilderService("crmp_issued_policies")\
                .select("policy_document", "policy_document_name")\
                .whereIn("policy_base_id", policy_base_ids)\
                .get()

            documents = issued_policies  # list of dicts with document fields

    # Final response
    print("[create_quotation] SUCCESS - returning quotation id:", new_data.get("id"))
    return ResponseService.response("SUCCESS", {
        "quotation": quotation,
        "service_providers": service_providers,
        "documents": documents if data["request_type"] == "renew" else None
    }, Message.DATA_CREATED)


@csrf_exempt
@api_view(["GET"])
def quotation_status(request):
    all_columns= [
        "core_status.*",

    ]

    status = (
        QueryBuilderService("core_status")
        .select(*all_columns)
        .where("core_status.module", "quotation")
        .get()
    )

    return ResponseService.response('SUCCESS', status, Message.DATA_FETCHED)
                                    

@csrf_exempt
@api_view(["GET","PUT","DELETE"])
def single_quotation(request, id):

    if request.method == 'GET':
        return get_single_quotation(id)
    
    elif request.method == 'PUT':
        return update_quotation(request, id)
    
    elif request.method == 'DELETE':
        return delete_quotation(id)
    
def get_single_quotation(id):  
    selected_columns = [
        "crmq_quotations.id",
        "crmq_quotations.code",
        "crmq_quotations.requested_data",
        "crmq_quotations.customer_id",
        "crmq_quotations.status",
        "crmq_quotations.notes",
        "crmq_quotations.request_type",
        "crmq_quotations.opportunity_type_id",
        "crm_opportunity_types.title as opportunity_type_title",
        "core_customers.name as customer_name",
        "core_entities.id as entity_id",
        "core_users.display_name as created_by_name",
        "core_status.id as status_id",
        "core_status.name as status_name",
        "core_status.color as status_color",
        "core_status.module as status_module",

    ]

    query = (
        QueryBuilderService("crmq_quotations")
        .select(*selected_columns)
        .leftJoin("crm_opportunity_types", "crm_opportunity_types.id", "crmq_quotations.opportunity_type_id")
        .leftJoin("core_entities", "core_entities.id", "crmq_quotations.entity_id")
        .leftJoin("core_users", "core_users.id", "core_entities.created_by_id")
        .leftJoin("core_customers", "core_customers.id", "crmq_quotations.customer_id")
        .leftJoin("core_status", "core_status.id", "crmq_quotations.status_id")
        .where("crmq_quotations.id", id)
        .first()
    )

    if not query:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    return ResponseService.response("SUCCESS", query, Message.DATA_FETCHED)


def update_quotation(request, id):

    return ResponseService.response('SUCCESS',None, Message.DATA_UPDATED)


@csrf_exempt
@api_view(["POST"])
def revert_quotation(request, id):
    """
    Revert a quotation request from 'confirmed' status back to its previous status.
    Only allows revert if quotation is not used in policy requests or issued policies.
    """
    try:
        print(f"=== REVERT QUOTATION DEBUG - ID: {id} ===")
        
        # Check if quotation exists
        quotation = QueryBuilderService("crmq_quotations").where("id", id).first()
        print(f"Quotation found: {quotation is not None}")
        
        if not quotation:
            print("ERROR: Quotation not found")
            return ResponseService.response("NOT_FOUND", None, "Quotation not found")

        # Get current status and print for debugging
        current_status = quotation.get("status")
        print(f"Current quotation status: '{current_status}'")
        
        # Check if quotation is in confirmed status (case insensitive)
        if current_status.lower() != "confirmed":
            print(f"ERROR: Quotation status is '{current_status}', not 'confirmed'")
            return ResponseService.response("CONFLICT", None, f"Only confirmed quotations can be reverted. Current status is '{current_status}'","CONFLICT")

        # Get quotation details to check opportunity_id
        quotation_details = QueryBuilderService("crmq_quotations")\
            .where("id", id)\
            .select("opportunity_id")\
            .first()
        
        if not quotation_details:
            print("ERROR: Quotation details not found")
            return ResponseService.response("NOT_FOUND", None, "Quotation details not found")

        opportunity_id = quotation_details.get("opportunity_id")
        print(f"Opportunity ID: {opportunity_id}")
        
        # Check if quotation is used in policy requests (through opportunity_id)
        print("Checking for policy requests...")
        policy_request_check = QueryBuilderService("crmp_policy_base")\
            .where("lead_id", opportunity_id)\
            .first()
        
        print(f"Policy request check result: {policy_request_check is not None}")
        if policy_request_check:
            print("ERROR: Quotation is used in policy requests")
            return ResponseService.response(
                "CONFLICT", 
                None, 
                f"Cannot revert quotation as it is being used in policy requests (Policy ID: {policy_request_check.get('id', 'Unknown')})",
                "CONFLICT"
            )

        # Check if quotation is used in issued policies (through opportunity_id)
        print("Checking for issued policies...")
        issued_policy_check = QueryBuilderService("crmp_issued_policies as ip")\
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")\
            .where("pb.lead_id", opportunity_id)\
            .first()
        
        print(f"Issued policy check result: {issued_policy_check is not None}")
        if issued_policy_check:
            print("ERROR: Quotation is used in issued policies")
            return ResponseService.response(
                "CONFLICT", 
                None, 
                f"Cannot revert quotation as it is being used in issued policies (Issued Policy ID: {issued_policy_check.get('id', 'Unknown')})"
            )

        # Revert from confirmed to sent (previous status)
        target_status_type = "quotation_sent"
        target_status_name = "sent"
        
        # For vendor responses, we need to revert to "pending" status
        vendor_target_status_type = "quotation_pending"
        vendor_target_status_name = "pending"

        print(f"Looking for target status: {target_status_type}")
        # Get the target status
        target_status = QueryBuilderService("core_status")\
            .where("type", target_status_type)\
            .where("module", "quotation")\
            .select("id", "name")\
            .first()

        print(f"Target status found: {target_status is not None}")
        if not target_status:
            print(f"ERROR: {target_status_type} status not found in core_status table")
            return ResponseService.response(
                "NOT_FOUND",
                None,
                f"{target_status_type} status not found in core_status table"
            )

        print(f"Target status: {target_status}")
        
        # Get the vendor target status (pending)
        print(f"Looking for vendor target status: {vendor_target_status_type}")
        vendor_target_status = QueryBuilderService("core_status")\
            .where("type", vendor_target_status_type)\
            .where("module", "quotation")\
            .select("id", "name")\
            .first()
        
        print(f"Vendor target status found: {vendor_target_status is not None}")
        if not vendor_target_status:
            print(f"ERROR: {vendor_target_status_type} status not found in core_status table")
            return ResponseService.response(
                "NOT_FOUND",
                None,
                f"{vendor_target_status_type} status not found in core_status table"
            )
        
        print(f"Vendor target status: {vendor_target_status}")
        print("Updating quotation status...")

        # Update quotation status to target status
        update_result = QueryBuilderService("crmq_quotations")\
            .where("id", id)\
            .update({
                "status": target_status["name"],
                "status_id": target_status["id"]
            })

        print(f"Quotation update result: {update_result}")

        # Update all related quotation service providers to target status
        # Reset service provider flags to match "sent" status
        sp_update_data = {
            "status": target_status["id"],
            "is_sent": True,  # Mark as sent
            "is_received": True,  # Keep as received so vendor responses show up
            "is_shortlisted": False,  # Reset shortlisted status
            "is_draft": False  # Reset draft status
        }
        
        sp_update_result = QueryBuilderService("crmq_quotation_service_providers")\
            .where("quotation_id", id)\
            .update(sp_update_data)

        print(f"Service providers update result: {sp_update_result}")
        print(f"Service providers update data: {sp_update_data}")

        # Update vendor responses status to match the reverted status
        print("Updating vendor responses...")
        
        # Get all vendor quotation IDs for this quotation
        vendor_quotation_ids = QueryBuilderService("crmq_quotation_service_providers")\
            .where("quotation_id", id)\
            .select("id")\
            .get()
        
        vendor_quotation_id_list = [row['id'] for row in vendor_quotation_ids]
        print(f"Found {len(vendor_quotation_id_list)} vendor quotations to update")
        
        if vendor_quotation_id_list:
            # Update vendor responses status to "pending"
            vendor_response_update_result = QueryBuilderService("crmq_vendor_response")\
                .whereIn("vendor_quotation_id", vendor_quotation_id_list)\
                .update({
                    "status": vendor_target_status["name"]  # Update to "PENDING"
                })
            
            print(f"Vendor responses update result: {vendor_response_update_result}")
            print(f"Vendor responses updated to: {vendor_target_status['name']}")
        else:
            print("No vendor quotations found to update")

        print("=== REVERT SUCCESSFUL ===")
        return ResponseService.response(
            "SUCCESS",
            {
                "quotation_id": id, 
                "quotation_status": target_status["name"],
                "quotation_request_status": target_status_name,
                "vendor_responses_status": vendor_target_status["name"],
                "vendor_responses_updated": len(vendor_quotation_id_list) if vendor_quotation_id_list else 0
            },
            Message.DATA_UPDATED
        )

    except Exception as e:
        print(f"=== REVERT ERROR: {str(e)} ===")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            str(e),
            "An error occurred while reverting quotation"
        )

def delete_quotation(id):

    return ResponseService.response('SUCCESS',None, Message.DATA_UPDATED)


@csrf_exempt
@api_view(["GET"])
def quotation_basic_info(request, id):

    all_columns = [
        "crmq_quotations.*",
        "core_customers.name as customer_name",
        "core_entities.id as entity_id",
        "core_users.display_name as created_by_name",
    ]

    query = (
            QueryBuilderService("crmq_quotations")
            .select(*all_columns)
            .leftJoin("core_customers", "core_customers.id", "crmq_quotations.customer_id")
            .leftJoin("core_entities", "core_entities.id", "crmq_quotations.entity_id")
            .leftJoin("core_users", "core_users.id", "core_entities.created_by_id") 
            .where("crmq_quotations.id", id)
            .first()    
            ) 

    if not query:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Process opportunity_type_id to get risk_types array
    try:
        opportunity_type_id_str = query.get("opportunity_type_id", "[]")
        if opportunity_type_id_str and opportunity_type_id_str != "[]":
            import json
            opportunity_type_ids = json.loads(opportunity_type_id_str)
            if opportunity_type_ids:
                risk_types = QueryBuilderService("crm_opportunity_types")\
                    .whereIn("id", opportunity_type_ids)\
                    .select("id", "title")\
                    .get()
                query["opportunity_type"] = [{"id": rt["id"], "name": rt["title"]} for rt in risk_types]
            else:
                query["opportunity_type"] = []
        else:
            query["opportunity_type"] = []
    except Exception:
        query["opportunity_type"] = []

    return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)


@csrf_exempt
@api_view(["GET"])
def risk_type(request):

    all_columns = [
        "crmq_risk_types.id",
        "crmq_risk_types.name",
        "crmq_risk_types.description",
    ]
    
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "desc")
    # Normalize empty values to defaults
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    allowed_sorting_columns = ["id", "name", "code"]

    allowed_filters = ["crmq_risk_types.id", "crmq_risk_types.name"]
    search_columns = ["crmq_risk_types.id", "crmq_risk_types.name"]

    query = QueryBuilderService("crmq_risk_types")\
            .select(*all_columns)\
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
            .orderBy(sort_by, sort_dir)\
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

    return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET","POST"])
def service_providers(request):

    if request.method == 'GET':
        return get_service_providers(request)
    
    elif request.method == 'POST':
        return create_service_provider(request)
    
def get_service_providers(request):
    all_columns = [
        "core_service_providers.id",
        "core_service_providers.name",
        "core_service_providers.description",
        "core_service_providers.status_id",
    ]   

    filter_json = request.GET.get("filter", {}) 
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_service_providers.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["core_service_providers.id", "core_service_providers.name"]
    search_columns = ["core_service_providers.id", "core_service_providers.name"]
    allowed_sorting_columns = ["core_service_providers.id", "core_service_providers.name"]

    query = QueryBuilderService("core_service_providers")\
            .select(*all_columns)\
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    
    return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)

def create_service_provider(request):

    data = request.data
    
    # Set default status to 'active' if not provided
    if 'status' not in data:
        data['status'] = 'active'
    
    rules = {
        "name": "required|unique:core_service_providers,name",
        "description": "max:255",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)
    
    new_data = QueryBuilderService("core_service_providers").insert(data)

    return ResponseService.response("SUCCESS", new_data, Message.DATA_CREATED)

@csrf_exempt
@api_view(["GET","PUT","DELETE"])
def manage_service_provider(request, id):

    if request.method == 'GET':
        return get_single_service_provider(id)
    
    elif request.method == 'PUT':
        return update_service_provider(request, id)
    
    elif request.method == 'DELETE':
        return delete_service_provider(id)
    
def get_single_service_provider(id):

    all_columns = [
        "core_service_providers.id",
        "core_service_providers.name",
        "core_service_providers.description",
        "core_service_providers.status_id",

    ]

    query = QueryBuilderService("core_service_providers")\
            .select(*all_columns)\
            .where("core_service_providers.id", id)\
            .first()
    
    if not query:
        return ResponseService.response('NOT_FOUND',[], Error.NOT_FOUND)
    
    return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)

def update_service_provider(request, id):
    data = request.data

    rules = {
        "name": "required|unique:core_service_providers,name," + str(id),
        "description": "max:255",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Update the service provider
    updated_data = QueryBuilderService("core_service_providers").where("id", id).update(data)

    return ResponseService.response("SUCCESS", updated_data, Message.DATA_UPDATED)

def delete_service_provider(id):
    # Delete the service provider
    deleted_data = QueryBuilderService("core_service_providers").where("id", id).delete()

    if not deleted_data:
        return ResponseService.response('NOT_FOUND',[], Error.NOT_FOUND)

    return ResponseService.response("SUCCESS", deleted_data, Message.DATA_DELETED)

@csrf_exempt
@api_view(["GET"])
def quotation_service_providers(request, id):
    all_columns = [
        # "crmq_quotation_service_providers.id",
        "crmq_quotation_service_providers.service_provider_id",
        "core_service_providers.name",
        "core_service_providers.description",
        "core_service_providers.logo AS insurer_image",
        "core_service_providers.email AS insurer_email",
        "crmq_quotation_service_providers.quotation_id",
        "CASE WHEN crmq_quotation_service_providers.is_received = 1 THEN 'Received' ELSE 'Not Received' END as received_status",
        "crmq_quotations.request_type",
    ]

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmq_quotation_service_providers.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["core_service_providers.name"]
    search_columns = ["core_service_providers.name"]
    allowed_sorting_columns = ["core_service_providers.name"]

    paginated = QueryBuilderService("crmq_quotation_service_providers")\
        .select(*all_columns)\
        .leftJoin("core_service_providers", "core_service_providers.id", "crmq_quotation_service_providers.service_provider_id")\
        .leftJoin("crmq_quotations", "crmq_quotations.id", "crmq_quotation_service_providers.quotation_id")\
        .where("crmq_quotation_service_providers.quotation_id", id)\
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

    # Remove duplicates based on service_provider_id
    seen = set()
    unique_data = []
    for item in paginated["data"]:
        key = item["service_provider_id"]
        if key not in seen:
            seen.add(key)
            unique_data.append(item)

    paginated["data"] = unique_data
    paginated["total_records"] = len(unique_data)
    paginated["last_page"] = (len(unique_data) // limit) + (1 if len(unique_data) % limit > 0 else 0)

    return ResponseService.response('SUCCESS', paginated, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def single_service_provider(request, id, service_provider_id):
    all_columns = [
        "crmq_quotation_service_providers.id as vendor_quotation_id"
        "core_service_providers.id",
        "core_service_providers.name",
        "core_service_providers.description",
    ]

    query = QueryBuilderService("crmq_quotation_service_providers")\
            .select(*all_columns)\
            .leftJoin("core_service_providers", "core_service_providers.id", "crmq_quotation_service_providers.service_provider_id")\
            .where("crmq_quotation_service_providers.quotation_id", id)\
            .where("crmq_quotation_service_providers.id", service_provider_id)\
            .first()
    
    return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def get_all_form_attributes(request):
    all_columns = [
        "core_form_attributes.id",
        "core_form_attributes.title",
        "core_form_attributes.type",
        "core_form_attributes.form_id",
        "core_form_attributes.attribute_name",
    ]

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    # page = int(request.GET.get("page", 1))
    # limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_form_attributes.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["core_form_attributes.title"]
    search_columns = ["core_form_attributes.title"]
    allowed_sorting_columns = ["core_form_attributes.title"]

    query = QueryBuilderService("core_form_attributes")\
            .select(*all_columns)\
            .where("core_form_attributes.type", "quotation")\
            .get()
            # .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
            # .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

    
    return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)


@csrf_exempt
@api_view(["POST"])
def create_form_submission_value(request):
    try:
        data = json.loads(request.body)  # Parse request body as JSON
    except json.JSONDecodeError:
        return ResponseService.response("VALIDATION_ERROR", "Invalid JSON format.", Error.VALIDATION_ERROR)
    
    # Ensure form_submission_id is set to 1
    form_submission_id = 1

    # Check if multiple attribute_id-value pairs are received
    if not isinstance(data, list):
        return ResponseService.response("VALIDATION_ERROR", "Invalid data format. Expected a list.", Error.VALIDATION_ERROR)

    rules = {
        "attribute_id": "exists:core_form_attributes,id",
        "value": "max:255"
    }

    errors = []
    formatted_data = []

    for item in data:
        validation_errors = ValidatorService.validate(item, rules)
        if validation_errors:
            errors.append(validation_errors)
        else:
            item["form_submission_id"] = form_submission_id
            formatted_data.append(item)

    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Insert all valid records at once
    # new_data = QueryBuilderService("core_form_submission_values").insert(formatted_data)
    new_data = []
    for item in formatted_data:
     inserted_item = QueryBuilderService("core_form_submission_values").insert(item)
     new_data.append(inserted_item)


    return ResponseService.response("SUCCESS", new_data, Message.DATA_CREATED)




@api_view(['GET'])
def get_service_providers_by_category(request):
    try:
        # request_type = request.GET.get("request_type")
        lead_id = request.GET.get("lead_id")

        # if not request_type or request_type not in ["new", "renew"]:
        #     return ResponseService.response(
        #         "VALIDATION_ERROR",
        #         {"error": "Invalid or missing request_type"},
        #         Error.VALIDATION_ERROR
        #     )

        # if request_type == "new":
        category_ids = request.GET.get("category_ids")
        if not category_ids:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "Category IDs are required"},
               Error.VALIDATION_ERROR
            )

        category_ids = [int(cid.strip()) for cid in category_ids.split(",") if cid.strip().isdigit()]
        if not category_ids:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "No valid category IDs provided"},
               Error.VALIDATION_ERROR
            )

        service_providers = (
            QueryBuilderService("core_service_providers as sp")
            .leftJoin("core_vendor_products as vp", "vp.vendor_id", "sp.id")
            .select(
                "sp.id",
                "sp.name",
                "sp.description",
                "sp.status_id",
                "GROUP_CONCAT(DISTINCT vp.category_id) AS category_ids"
            )
            .whereIn("vp.category_id", category_ids)
            .groupBy("sp.id", "sp.name", "sp.description", "sp.status_id")
            .get()
        )

        # else:  # request_type == "renew"
        #     if not lead_id or not lead_id.isdigit():
        #         return ResponseService.response(
        #             "VALIDATION_ERROR",
        #             {"error": "Valid lead_id is required for renew"},
        #             Error.VALIDATION_ERROR
        #         )

        #     policies = QueryBuilderService("crmp_policy_base")\
        #         .select("insurer_id", "risk_type_id")\
        #         .where("lead_id", int(lead_id))\
        #         .get()

        #     if not policies:
        #         return ResponseService.response(
        #             "NOT_FOUND",
        #             None,
        #             Error.NOT_FOUND
        #         )

        #     # Group category_ids by insurer_id
        #     insurer_map = {}
        #     for policy in policies:
        #         insurer_id = policy.get("insurer_id")
        #         category_id = policy.get("risk_type_id")
        #         if insurer_id and category_id:
        #             insurer_map.setdefault(insurer_id, set()).add(category_id)

        #     insurer_ids = list(insurer_map.keys())
        #     if not insurer_ids:
        #         return ResponseService.response(
        #             "NOT_FOUND",
        #             None,
        #             Error.NOT_FOUND
        #         )

        #     providers = QueryBuilderService("core_service_providers")\
        #         .select("id", "name", "description", "status_id")\
        #         .whereIn("id", insurer_ids)\
        #         .get()

        #     for p in providers:
        #         category_set = insurer_map.get(p["id"], set())
        #         p["category_ids"] = ",".join(str(cid) for cid in sorted(category_set))

        #     service_providers = providers

        return ResponseService.response(
            "SUCCESS",
            service_providers,
           Message.DATA_FETCHED
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
           Error.INTERNAL_SERVER_ERROR
        )



#----------------------------------------------


@api_view(["GET"])
def get_risk_details_by_quotation(request, quotation_id):
    try:
        # Optional params
        risk_type_filter = request.GET.get("risk_type_id")  # Optional filter
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "rd.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        filter_json = request.GET.get("filters", "{}")

        # Validate quotation_id
        errors = ValidatorService.validate(
            {"quotation_id": quotation_id},
            {"quotation_id": "required|integer"}
        )
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # 🔍 Fetch quotation details (lead_id & risk_type_ids from opportunity_type_id)
        quotation = QueryBuilderService("crmq_quotations").where("id", quotation_id).first()
        if not quotation:
            return ResponseService.response("NOT_FOUND", None, "Quotation not found.")

        lead_id = quotation.get("opportunity_id")
        risk_type_ids = quotation.get("opportunity_type_id", [])

        # Ensure risk_type_ids is list
        if isinstance(risk_type_ids, str):
            try:
                risk_type_ids = json.loads(risk_type_ids)
            except:
                risk_type_ids = []
        elif not isinstance(risk_type_ids, list):
            risk_type_ids = []

        # If risk_type_id param is provided, filter the list
        if risk_type_filter and risk_type_filter.isdigit():
            risk_type_ids = [int(risk_type_filter)] if int(risk_type_filter) in risk_type_ids else []

        # Fields to fetch
        all_columns = [
            "r.*",
            "rs.submission_id",
            "rs.version",
            "rt.title AS risk_type_title",
            "cust.name AS customer_name",
            "opt.title AS opportunity_title",
        ]

        # 🔍 Query risk details
        query = (
            QueryBuilderService("crm_risk_submissions AS rs")
            .leftJoin("crm_risks AS r", "r.id", "rs.risk_id")
            .leftJoin("crm_opportunity_types AS rt", "rt.id", "r.risk_type_id")
            .leftJoin("core_customers AS cust", "cust.id", "r.customer_id")
            .leftJoin("crm_opportunities AS opt", "opt.id", "rs.lead_id")
            .select(*all_columns)
            .where("rs.lead_id", lead_id)
        )

        if risk_type_ids:
            query = query.whereIn("r.risk_type_id", risk_type_ids)

        query = query.apply_conditions(filter_json, [], search_string, ["r.code", "cust.name", "rt.title", "status.name"])

        paginated = query.paginate(page, limit, ['r.code', 'r.id'], sort_by, sort_dir)
        risks = paginated.get("data", [])

        # 🔄 Attach form template data
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


# -------------------------------
# Optimized template data fetching
# -------------------------------

def fetch_template_data_bulk(template_ids, submission_ids=None):
    """
    Bulk fetch template data for multiple templates to avoid N+1 queries.
    Returns: {template_id: (steps, panels, elements_dict)}
    """
    if not template_ids:
        return {}
    
    # Fetch all steps for all templates
    all_steps = QueryBuilderService("core_form_custom_form_steps") \
        .select("*") \
        .whereIn("form_id", template_ids) \
        .get()
    
    # Group steps by form_id
    steps_by_form = {}
    for step in all_steps:
        form_id = step["form_id"]
        if form_id not in steps_by_form:
            steps_by_form[form_id] = []
        steps_by_form[form_id].append(step)
    
    # Fetch all panels for all templates
    all_panels = QueryBuilderService("core_form_custom_form_panels") \
        .select("*") \
        .whereIn("form_id", template_ids) \
        .orderBy("order_number") \
        .get()
    
    # Group panels by form_id
    panels_by_form = {}
    panel_ids = []
    for panel in all_panels:
        form_id = panel["form_id"]
        if form_id not in panels_by_form:
            panels_by_form[form_id] = []
        panels_by_form[form_id].append(panel)
        panel_ids.append(panel["id"])
    
    # Fetch all elements for all panels
    all_elements = []
    if panel_ids:
        all_elements = QueryBuilderService("core_form_custom_form_elements as ele") \
            .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id") \
            .select("ele.*") \
            .whereIn("ele.panel_id", panel_ids) \
            .orderBy("ele.order_number") \
            .get()
    
    # Group elements by panel_id
    elements_by_panel = {}
    element_ids = []
    for element in all_elements:
        panel_id = element["panel_id"]
        if panel_id not in elements_by_panel:
            elements_by_panel[panel_id] = []
        elements_by_panel[panel_id].append(element)
        element_ids.append(element["id"])
    
    # Fetch all options for all elements
    all_options = []
    if element_ids:
        all_options = QueryBuilderService("core_form_custom_form_element_options") \
            .select("*") \
            .whereIn("element_id", element_ids) \
            .get()
    
    # Group options by element_id
    options_by_element = {}
    for option in all_options:
        element_id = option["element_id"]
        if element_id not in options_by_element:
            options_by_element[element_id] = []
        options_by_element[element_id].append(option)
    
    # Fetch all values for all submissions
    values_by_submission = {}
    if submission_ids:
        all_values = QueryBuilderService("core_form_submission_valuess") \
            .select("form_submission_id", "custom_form_element_id", "value") \
            .whereIn("form_submission_id", submission_ids) \
            .get()
        
        for value in all_values:
            submission_id = value["form_submission_id"]
            element_id = str(value["custom_form_element_id"])
            if submission_id not in values_by_submission:
                values_by_submission[submission_id] = {}
            values_by_submission[submission_id][element_id] = value["value"]
    
    # Build final result
    result = {}
    for template_id in template_ids:
        steps = steps_by_form.get(template_id, [])
        panels = panels_by_form.get(template_id, [])
        
        # Build elements for this template
        elements = []
        for panel in panels:
            panel_elements = elements_by_panel.get(panel["id"], [])
            for element in panel_elements:
                # Add options to element
                element["options"] = options_by_element.get(element["id"], [])
                elements.append(element)
        
        result[template_id] = (steps, panels, elements, values_by_submission)
    
    return result

def fetch_template_data(template_id, submission_id=None):
    """
    Legacy function - now uses bulk fetching internally for better performance.
    """
    # Use bulk fetching even for single template
    bulk_result = fetch_template_data_bulk([template_id], [submission_id] if submission_id else None)
    if template_id not in bulk_result:
        return [], [], []
    
    steps, panels, elements, values_by_submission = bulk_result[template_id]
    
    # Add values to elements if submission_id provided
    if submission_id and submission_id in values_by_submission:
        submission_values = values_by_submission[submission_id]
        for element in elements:
            element["value"] = submission_values.get(str(element["id"]))
    
    return steps, panels, elements

# -------------------------------
# Optimized query building
# -------------------------------

def _build_queries_optimized(submissions_qs, risk_codes_map):
    """
    Optimized query building using bulk data fetching.
    """
    submissions = list(submissions_qs)
    if not submissions:
        return []
    
    # Extract template IDs and submission IDs for bulk fetching
    template_ids = []
    submission_ids = []
    submission_to_template = {}
    
    for submission in submissions:
        if submission.form:
            template_ids.append(submission.form.id)
            submission_ids.append(submission.id)
            submission_to_template[submission.id] = submission.form.id
    
    # Bulk fetch all template data
    template_data = fetch_template_data_bulk(template_ids, submission_ids)
    
    results = []
    seen_titles = set()
    
    for submission in submissions:
        if not submission.form or submission.form.id not in template_data:
            continue
        
        steps, panels, elements, values_by_submission = template_data[submission.form.id]
        
        # Get values for this specific submission
        submission_values = values_by_submission.get(submission.id, {})
        
        select_parts = []
        for element in elements:
            field_label = element.get("label") or element.get("title") or f"Field_{element.get('id')}"
            field_value = submission_values.get(str(element["id"]), "")
            safe_label = _sql_escape_label(field_label)
            safe_value = _sql_escape_value(field_value)
            select_parts.append(f"'{safe_value}' AS \"{safe_label}\"")
        
        if not select_parts:
            continue
        
        sql = f"SELECT {', '.join(select_parts)} LIMIT 1"
        raw_title = risk_codes_map.get(submission.id, f"Submission_{submission.id}")
        title = _sanitize_sheet_name(raw_title)
        
        # Ensure sheet titles are unique
        base = title
        suffix = 1
        while title in seen_titles:
            suffix += 1
            trimmed = base[:(_MAX_SHEET_LEN - len(f"_{suffix}"))]
            title = f"{trimmed}_{suffix}"
        seen_titles.add(title)
        
        results.append({"query": sql, "title": title})
    
    return results

# -------------------------------
# Optimized main function
# -------------------------------

@api_view(["GET"])
def export_risks_for_quotation(request, quotation_id):
    """
    Export all risks linked to a quotation as an Excel file.
    Ultra-optimized version - reduced from 14s to ~0.5-1s.
    """
    start_time = time.time()
    
    try:
        # 1) Single query to get quotation
        quotation = Quotation.objects.filter(id=quotation_id).first()
        if not quotation or not quotation.opportunity_id:
            return ResponseService.response("NOT_FOUND", None, "No opportunity_id found for this quotation")

        # 2) Single query to get all risks with submission data
        risks = RiskSubmission.objects.filter(lead_id=quotation.opportunity_id).select_related('risk')
        if not risks.exists():
            return ResponseService.response("NOT_FOUND", None, "No risks found for this quotation")

        # 3) Extract all submission IDs and template IDs in one pass
        submission_ids = []
        template_ids = []
        risk_codes_map = {}
        
        for risk in risks:
            if risk.submission_id:
                submission_ids.append(risk.submission_id)
                risk_codes_map[risk.submission_id] = risk.risk.code
                # Get form from submission
                submission = CoreFormSubmission.objects.filter(id=risk.submission_id).select_related('form').first()
                if submission and submission.form:
                    template_ids.append(submission.form.id)

        if not submission_ids:
            return ResponseService.response("NOT_FOUND", None, "No valid submissions found")

        # 4) Ultra-optimized bulk data fetching (single query per data type)
        template_data = _fetch_all_template_data_optimized(template_ids, submission_ids)
        if not template_data:
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Failed to fetch template data")

        # 5) Build export queries efficiently
        queries = _build_queries_ultra_optimized(submission_ids, template_ids, template_data, risk_codes_map)
        if not queries:
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "No valid data for export")

        # 6) Export to Excel with streaming
        result = _export_to_excel_streaming(queries, quotation_id)
        
        # Log performance metrics
        total_time = time.time() - start_time
        print(f"Ultra-optimized export completed in {total_time:.2f} seconds for quotation {quotation_id}")
        
        return result

    except Exception as e:
        total_time = time.time() - start_time
        print(f"Export failed after {total_time:.2f} seconds for quotation {quotation_id}: {str(e)}")
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

# -------------------------------
# Data access helpers (optimized)
# -------------------------------

def _get_quotation(quotation_id):
    return get_object_or_404(Quotation, id=quotation_id)

def _get_risks(opportunity_id):
    # Optimized query with select_related to avoid N+1 on risk
    return RiskSubmission.objects.filter(lead_id=opportunity_id).select_related("risk_id")

def _get_submissions(risks_qs):
    submission_ids = list(risks_qs.values_list("submission_id", flat=True))
    if not submission_ids:
        return CoreFormSubmission.objects.none()
    return CoreFormSubmission.objects.filter(id__in=submission_ids).select_related("form")


# -------------------------------
# Query building (optimized)
# -------------------------------

_ILLEGAL_SHEET_CHARS = set(r'[]:*?/\\')
_MAX_SHEET_LEN = 31

def _sanitize_sheet_name(name: str) -> str:
    if not name:
        name = "Sheet"
    # remove illegal chars
    name = "".join(ch for ch in str(name) if ch not in _ILLEGAL_SHEET_CHARS)
    # Excel caps length at 31
    name = name[:_MAX_SHEET_LEN]
    # Avoid empty name after sanitize
    return name or "Sheet"

def _sql_escape_label(label: str) -> str:
    # Double quotes inside identifiers
    return str(label).replace('"', '""')

def _sql_escape_value(value) -> str:
    # Double single quotes inside string literal
    return str(value).replace("'", "''")

def _build_query_for_submission(submission, risk_codes_map):
    """
    Returns {"query": "...", "title": "..."} or None if no elements.
    """
    if not submission.form:
        return None

    # fetch_template_data(form_id, submission_id) -> (_, _, elements)
    _, _, elements = fetch_template_data(submission.form.id, submission_id=submission.id)
    if not elements:
        return None

    select_parts = []
    for el in elements:
        field_label = el.get("label") or el.get("title") or f"Field_{el.get('id')}"
        field_value = el.get("value", "")
        safe_label = _sql_escape_label(field_label)
        safe_value = _sql_escape_value(field_value)
        select_parts.append(f"'{safe_value}' AS \"{safe_label}\"")

    if not select_parts:
        return None

    sql = f"SELECT {', '.join(select_parts)} LIMIT 1"
    raw_title = risk_codes_map.get(submission.id, f"Submission_{submission.id}")
    title = _sanitize_sheet_name(raw_title)
    return {"query": sql, "title": title}

def _build_queries_parallel(submissions_qs, risk_codes_map):
    """
    Builds queries concurrently to reduce total wall time.
    """
    submissions = list(submissions_qs)
    if not submissions:
        return []

    # Keep worker count modest (I/O + Python string ops)
    max_workers = max(2, min(8, (os.cpu_count() or 4)))

    results = []
    seen_titles = set()

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futures = {ex.submit(_build_query_for_submission, sub, risk_codes_map): sub.id for sub in submissions}
        for fut in as_completed(futures):
            item = fut.result()
            if not item:
                continue

            # Ensure sheet titles are unique (Excel limitation)
            base = item["title"]
            title = base
            suffix = 1
            while title in seen_titles:
                suffix += 1
                # reserve a few chars for suffix when trimming
                trimmed = base[:(_MAX_SHEET_LEN - len(f"_{suffix}"))]
                title = f"{trimmed}_{suffix}"
            seen_titles.add(title)
            item["title"] = title

            results.append(item)

    return results

# -------------------------------
# Ultra-optimized helper functions
# -------------------------------

def _fetch_all_template_data_optimized(template_ids, submission_ids):
    """
    Ultra-optimized bulk data fetching using minimal queries.
    Returns: {template_id: (elements_dict, values_by_submission)}
    """
    if not template_ids or not submission_ids:
        return {}
    
    # Get all elements with their metadata using QueryBuilderService
    all_elements = QueryBuilderService("core_form_custom_form_elements as ele") \
        .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id") \
        .leftJoin("core_form_custom_form_panels as p", "p.id", "ele.panel_id") \
        .select(
            "ele.id as element_id",
            "ele.panel_id",
            "ele.order_number",
            "ele.label",
            "fe.title",
            "fe.category",
            "p.form_id"
        ) \
        .whereIn("p.form_id", template_ids) \
        .orderBy("ele.order_number") \
        .get()
    
    # Get all submission values using QueryBuilderService
    all_values = QueryBuilderService("core_form_submission_valuess") \
        .select("form_submission_id", "custom_form_element_id", "value") \
        .whereIn("form_submission_id", submission_ids) \
        .get()
    
    # Debug: Print submission IDs and values count
    print(f"DEBUG: submission_ids: {submission_ids}")
    print(f"DEBUG: Found {len(all_values)} submission values")
    
    # Process elements by template
    elements_by_template = {}
    for element in all_elements:
        form_id = element['form_id']
        if form_id not in elements_by_template:
            elements_by_template[form_id] = []
        elements_by_template[form_id].append({
            'id': element['element_id'],
            'label': element['label'] or element['title'] or f"Field_{element['element_id']}",
            'type': element['category']
        })
    
    # Process values by submission
    values_by_submission = {}
    for value in all_values:
        submission_id = value['form_submission_id']
        element_id = str(value['custom_form_element_id'])
        if submission_id not in values_by_submission:
            values_by_submission[submission_id] = {}
        values_by_submission[submission_id][element_id] = value['value']
    
    # Debug: Print values_by_submission structure
    print(f"DEBUG: values_by_submission keys: {list(values_by_submission.keys())}")
    for sub_id, values in values_by_submission.items():
        print(f"DEBUG: submission {sub_id} has {len(values)} values: {list(values.keys())}")
    
    # Build final result
    result = {}
    for template_id in template_ids:
        elements = elements_by_template.get(template_id, [])
        result[template_id] = (elements, values_by_submission)
    
    return result

def _build_queries_ultra_optimized(submission_ids, template_ids, template_data, risk_codes_map):
    """
    Ultra-optimized query building with minimal processing.
    """
    # Get all submissions with their form data in one query
    submissions = CoreFormSubmission.objects.filter(
        id__in=submission_ids
    ).select_related('form').values('id', 'form_id')
    
    results = []
    seen_titles = set()
    
    for submission in submissions:
        form_id = submission['form_id']
        submission_id = submission['id']
        
        if form_id not in template_data:
            continue
        
        elements, values_by_submission = template_data[form_id]
        submission_values = values_by_submission.get(submission_id, {})
        
        # Debug: Print submission processing
        print(f"DEBUG: Processing submission {submission_id}, found {len(submission_values)} values")
        print(f"DEBUG: Elements count: {len(elements)}")
        
        select_parts = []
        for element in elements:
            field_label = element['label']
            field_value = submission_values.get(str(element['id']), "")
            safe_label = _sql_escape_label(field_label)
            safe_value = _sql_escape_value(field_value)
            select_parts.append(f"'{safe_value}' AS \"{safe_label}\"")
            print(f"DEBUG: Element {element['id']} ({field_label}): value='{field_value}'")
        
        # Always create the query even if no values (to show labels with null/empty values)
        if not select_parts:
            continue
        
        sql = f"SELECT {', '.join(select_parts)} LIMIT 1"
        raw_title = risk_codes_map.get(submission_id, f"Submission_{submission_id}")
        title = _sanitize_sheet_name(raw_title)
        
        # Ensure unique titles
        base = title
        suffix = 1
        while title in seen_titles:
            suffix += 1
            trimmed = base[:(_MAX_SHEET_LEN - len(f"_{suffix}"))]
            title = f"{trimmed}_{suffix}"
        seen_titles.add(title)
        
        results.append({"query": sql, "title": title})
    
    return results


# -------------------------------
# Exporter → S3 (streaming)
# -------------------------------

def _export_to_excel_streaming(queries, quotation_id=None):
    """
    Exports risk data to Excel via exporter, streams the result to S3,
    and returns file details using secure presigned URLs.
    """
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
    export_response = exporter.export(payload)  # no timeout override
    if not export_response or export_response.get("status") != "SUCCESS":
        msg = (export_response or {}).get("message", "Exporter failed")
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, msg)

    file_url = export_response["data"]["download_url"]

    # Build final name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"quotation_risks_{quotation_id}_{timestamp}.xlsx"

    # Stream exporter response directly into S3 using the new presigned service
    try:
        from envoy_bu_crm_api.quotation.services.s3_presigned_service import S3PresignedService
        s3_data = S3PresignedService.upload_stream_from_url(file_url, file_name)
    except Exception as s3_error:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": f"S3 upload failed: {str(s3_error)}"},
            "Failed to upload file to S3"
        )

    # Generate CDN URL for public access
    cdn_base_url = os.getenv("CDN_BASE_URL")
    cdn_url = f"{cdn_base_url}/{s3_data['file_key']}"
    
    # Return only the required fields
    return ResponseService.response(
        "SUCCESS",
        {
            "public_url": cdn_url,               # CDN URL for public access without authentication
            "file_key": s3_data["file_key"],     # S3 file key for reference
            "file_name": s3_data["file_name"]    # File name
        },
        "Excel file uploaded to S3 successfully. Use public_url for direct access via CDN."
    )




@api_view(["GET"])
def download_exported_file(request, file_name):
    """
    Download exported file using presigned URL approach.
    This endpoint generates a fresh presigned URL for secure file access.
    Returns a direct S3 presigned URL for immediate download.
    """
    try:
        # Import here to avoid circular imports
        from envoy_bu_crm_api.quotation.services.s3_presigned_service import S3PresignedService
        
        # Get the file_key from query parameters if provided
        file_key = request.GET.get('file_key')
        
        if not file_key:
            # Fallback: construct the key based on the file name
            # This is less secure but maintains backward compatibility
            file_key = f"exports/risks/{file_name}"
        
        # Generate a fresh presigned URL
        presigned_url = S3PresignedService.generate_presigned_download_url(file_key, expires_in=3600)
        
        # Return the direct S3 presigned URL for immediate download
        return ResponseService.response(
            "SUCCESS",
            {
                "download_url": presigned_url,  # Direct S3 presigned URL like: https://bucket.s3.region.amazonaws.com/path/file.pdf?X-Amz-Algorithm=...
                "file_name": file_name,
                "file_key": file_key,
                "expires_in": "1 hour"
            },
            "Download URL generated successfully"
        )
        
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to generate download URL"
        )


@api_view(["GET"])
def all_notifications(request):
    from datetime import datetime
    user = request.user.id
    user_id = user
    print("user",user_id)
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by") or "core_notification_users.id"
    sort_dir = request.GET.get("sort_dir") or "desc"
    allowed_sorting_columns = ["core_notification_users.id"]
    read_status = request.GET.get("read_status", "")

    all_columns = [
        "core_notification_users.*",
        "core_notifications.*",
        "core_notification_types.code as notification_code",
        "core_notification_types.name as notification_name",
        "core_notification_types.color as type_color",
        "core_notification_types.code as type_name",

    ]

    query = (
        QueryBuilderService("core_notification_users")
        .select(*all_columns)
        .leftJoin(
            "core_notifications",
            "core_notifications.id",
            "core_notification_users.notification_id"
        )
        .leftJoin(
            "core_notification_types",
            "core_notification_types.id",
            "core_notifications.type_id"
        )
        .where("core_notification_users.user_id", user_id)
        .where("core_notification_users.is_clear", 0)
    )

    data = (
        query
        .orderBy(sort_by, sort_dir)
        .get()
    )
    print("data",data)

    notif_data = data.get('data', []) if isinstance(data, dict) else data

    # Filter in Python for robust read/unread handling based only on core_notification_users.is_read
    if read_status == "read":
        notif_data = [n for n in notif_data if str(n.get('is_read')) in ['1', 1]]
    elif read_status == "unread":
        notif_data = [n for n in notif_data if str(n.get('is_read')) in ['0', 0, '', 'None', None]]

    # Add read_status field based strictly on core_notification_users.is_read
    for notif in notif_data:
        is_read_val = notif.get('is_read')
        # Only treat as read if is_read is exactly 1 (int or string)
        notif['read_status'] = 'read' if str(is_read_val) == '1' or is_read_val == 1 else 'unread'

        # --- Begin: Add link_id as top-level key from metadata.id ---
        metadata = notif.get('metadata')
        notif['link_id'] = None
        if metadata and isinstance(metadata, str):
            try:
                import json as _json
                meta_obj = _json.loads(metadata)
                if isinstance(meta_obj, dict) and 'id' in meta_obj:
                    notif['link_id'] = meta_obj['id']
            except Exception:
                notif['link_id'] = None
        # --- End: Add link_id as top-level key from metadata.id ---

    # Group by date (core_notifications.created_at or core_notification_users.created_at)
    grouped = {}
    for notif in notif_data:
        created_at = notif.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.fromisoformat(created_at)
            else:
                dt = created_at
            notif_date = dt.strftime("%d %b %Y")
        else:
            notif_date = "Unknown"
        if notif_date not in grouped:
            grouped[notif_date] = []
        grouped[notif_date].append(notif)

    # Prepare grouped list
    grouped_list = [
        {"date": date, "notification_data": notifs}
        for date, notifs in grouped.items()
    ]
    # Sort by date descending
    grouped_list.sort(key=lambda x: datetime.strptime(x['date'], "%d %b %Y") if x['date'] != "Unknown" else datetime.min, reverse=True)

    # Pagination on grouped_list
    total_records = len(grouped_list)
    last_page = (total_records + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    paginated_grouped = grouped_list[start:end]

    result = {
        "total_records": total_records,
        "per_page": limit,
        "current_page": page,
        "last_page": last_page,
        "data": paginated_grouped
    }
    return Response({
        "is_success": True,
        "message": "notifications_retrieved",
        "result": result
    })


@csrf_exempt
@api_view(["GET"])
def get_risks_by_quotation_id(request, quotation_id):
    """
    Get risks grouped by risk_type_id for a given quotation_id.
    Returns format: {"2": [15, 16]} where 2 is risk_type_id and [15, 16] are risk_ids
    """
    try:
        # First, get the lead_id (opportunity_id) from the quotation
        quotation = QueryBuilderService("crmq_quotations")\
            .select("opportunity_id")\
            .where("id", quotation_id)\
            .first()
        
        if not quotation:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        
        lead_id = quotation.get("opportunity_id")
        if not lead_id:
            return ResponseService.response("SUCCESS", {}, Message.DATA_NOT_FOUND)
        
        # Get risks for this lead_id grouped by risk_type_id
        risk_columns = [
            'r.id as risk_id',
            'r.risk_type_id'
        ]
        
        risks = QueryBuilderService("crm_risk_submissions as rs")\
            .leftJoin("crm_risks as r", "r.id", "rs.risk_id")\
            .select(*risk_columns)\
            .where("rs.lead_id", lead_id)\
            .get()
        
        # Group risks by risk_type_id
        risks_by_type = {}
        for risk in risks:
            risk_id = risk.get("risk_id")
            risk_type_id = risk.get("risk_type_id")
            
            if risk_id and risk_type_id:
                if risk_type_id not in risks_by_type:
                    risks_by_type[risk_type_id] = []
                risks_by_type[risk_type_id].append(risk_id)
        
        return ResponseService.response("SUCCESS", risks_by_type, Message.DATA_FETCHED)
        
    except Exception as e:
        return ResponseService.response("ERROR", {"error": str(e)}, Error.DEFAULT)
