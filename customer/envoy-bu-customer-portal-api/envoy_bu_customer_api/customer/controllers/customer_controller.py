from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.db import transaction
from messages import Message, Error
import datetime
from mServices import ResponseService, QueryBuilderService, ValidatorService
# from envoy_bu_customer_api.customer.controllers.utils.service import get_commission_setup_service
from core_models.core_models import CoreTemplate
from envoy_bu_customer_api.service import handle_entity
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
from rest_framework.response import Response
from django.http import JsonResponse
import requests
from rest_framework.permissions import IsAuthenticated
from envoy_bu_customer_api.customer.service import  _format_date_fields
from envoy_bu_customer_api.custom_auth_user import CustomAuthUser
from services.NotificationService import NotificationService
from decimal import Decimal


# customer_id = 19  # Replace with request.user.get('id') if needed



EXTERNAL_API_URL = settings.EXTERNAL_API_URL

@api_view(["POST"])
def accept_invitations(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # Step 1: Initial validation (only checks if required fields are present)
        rules = {
            "idp_access_token": "required",
            "invitation": "required",
        }

        custom_messages = {
            "idp_access_token.required": "Idp Access Token cannot be empty.",
            "invitation.required": "Invitation ID cannot be empty.",
        }

        try:
            errors = ValidatorService.validate(data, rules, custom_messages)
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )
        except ValidationError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Invitation Not Accepted!",
            )

        user_token = data.get("idp_access_token")
        invitation_uid = data.get("invitation")

        customer_id = QueryBuilderService('core_customer_invitations').select('customer_id').where('uid', invitation_uid).first()

        if not customer_id:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                "Invitation Not Found!",
            )



        # Step 2: Normalize UUID by removing hyphens
        normalized_invitation_uid = invitation_uid.replace("-", "")

        try:
            # Validate UUID format
            invitation_uuid = uuid.UUID(invitation_uid)
        except ValueError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Invalid Invitation UUID format!"
            )

        # Step 3: Use ValidatorService to check if invitation exists
        rules = {
            "invitation": "exists:core_customer_invitations,uid",
        }

        custom_messages = {
            "invitation.exists": "Invitation does not exist.",
        }

        try:
            errors = ValidatorService.validate(
                {"invitation": normalized_invitation_uid}, 
                rules, 
                custom_messages
            )
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )
        except ValidationError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Invitation does not exist!",
            )

        headers = {"Authorization": f"Bearer {user_token}"}
        print("headers" , headers)

        response = requests.get(EXTERNAL_API_URL, headers=headers)
        print("response" , response)
        try:
            response_data = response.json()
        except ValueError:
            return JsonResponse({"error": "Invalid JSON response from IDP"}, status=500)

        if not response_data.get("is_success") or "result" not in response_data:
            return Response(
                {"error": "Invalid Response from IDP"},
            )

        idp_user_id = response_data["result"]["id"]
        name = response_data["result"]["name"]
        email = response_data["result"]["email"]

        user_data = {
            "idp_user_id": idp_user_id,
            "name": name,
            "email": email,
        }
        user_rules = {
            "idp_user_id": "required",
        }

        user_custom_messages = {
            "idp_user_id.required": "Invalid Idp Id."
        }
        
        try:
            errors = ValidatorService.validate(
                user_data, user_rules, user_custom_messages
            )
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )

            # Update idp_customer_id in core_customers
            QueryBuilderService('core_customers').where('id', customer_id['customer_id']).update({
                'idp_customer_id': idp_user_id
            })

            print("Setting request.user to CustomAuthUser:", user_data)
            request.user = CustomAuthUser(user_data)

            return ResponseService.response(
                "SUCCESS",
                result={"customer_id": customer_id['customer_id'], "idp_customer_id": idp_user_id},
                message="Invitation accepted and customer updated."
            )

        except ValidationError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Invitation Not Accepted!",
            )
  


@api_view(["GET"])
def quotations(request):
 try:
        
        user = request.user
        print(user)
        # Get customer ID from user's entity or fallback to 1
        customer_id = user.get('id', 1)
        print(customer_id)

        all_columns = [
           "crmq_quotations.id",
           "crmq_quotations.code",
           "crmq_quotations.requested_data",
           "crmq_quotations.customer_id",
           "crmq_quotations.status",
           "crmq_quotations.notes",
           "crmq_quotations.request_type",
           "crmq_quotations.opportunity_type_id",
           "crmq_quotations.opportunity_id",
           "crmq_quotations.entity_id",
           "crmq_quotations.email_data",
           "crmq_quotations.status_id as quotation_status_id",
           
           "MAX(crmq_send_quotations.id) as send_quotation_id",  
           "MAX(core_status.id) as status_id",
           "MAX(core_status.name) as status_name",
           "MAX(core_status.color) as status_color",
           "MAX(core_status.sort_index) as status_sort_index",
           "MAX(crmq_send_quotations.generated_pdf) as generated_pdf",
        ]

        filter_param = request.GET.get("filter", {})
        
        # Handle filter parameter - convert to JSON string for QueryBuilderService
        if isinstance(filter_param, str):
            if filter_param.strip() == "":
                filter_json = "{}"
            else:
                # If it's a simple string like "shortlisted", wrap it in a dict
                filter_json = '{"status": "' + filter_param + '"}'
        else:
            import json
            filter_json = json.dumps(filter_param)
            
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "crmq_quotations.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        
        # Handle empty parameters - use defaults if empty strings are passed
        if not sort_by or sort_by.strip() == "":
            sort_by = "crmq_quotations.id"
        if not sort_dir or sort_dir.strip() == "":
            sort_dir = "desc"
        allowed_sorting_columns = ["crmq_quotations.code", "crmq_quotations.id"]

        


        data = (
            QueryBuilderService("crmq_quotations")
            .select(*all_columns)
            .leftJoin(
                "core_customers",
                "core_customers.id",
                "crmq_quotations.customer_id"
            )
            .leftJoin(
                "core_status",
                "core_status.id",
                "crmq_quotations.status_id"
            )
            .leftJoin(
                "crmq_send_quotations",
                "crmq_send_quotations.quotation_request_id",
                "crmq_quotations.id"
            )
            .where("crmq_quotations.customer_id", customer_id)
            .where("crmq_send_quotations.status", "sent")
            .apply_conditions(
                filter_json=filter_json,
                allowed_filters=[],
                search_string=search_string,
                search_columns=["crmq_quotations.code", "crmq_quotations.id"]
            )
            .groupBy("crmq_quotations.id")  # Group by quotation ID to prevent duplicates
            .paginate(
                page=page,
                limit=limit,
                allowed_sorting_columns=allowed_sorting_columns,
                sort_by=sort_by,
                sort_dir=sort_dir
            )
        )

        # Enhance each quotation with opportunity_type_id and names
        if data and "data" in data:
            for quotation in data["data"]:
                opp_type_ids = quotation.get("opportunity_type_id")
                if opp_type_ids:
                    try:
                        # Parse JSON field (should be a list of ints)
                        import json as _json
                        ids = _json.loads(opp_type_ids) if isinstance(opp_type_ids, str) else opp_type_ids
                        if not isinstance(ids, list):
                            ids = [ids]
                        # Query titles from crm_opportunity_types
                        type_names = []
                        if ids:
                            rows = QueryBuilderService("crm_opportunity_types").select("id", "title").whereIn("id", ids).get()
                            id_to_title = {row["id"]: row["title"] for row in rows}
                            type_names = [id_to_title.get(i, str(i)) for i in ids]
                        quotation["opportunity_type_id"] = str(ids)
                        quotation["opportunity_type_names"] = ", ".join(type_names)
                    except Exception as e:
                        quotation["opportunity_type_id"] = str(opp_type_ids)
                        quotation["opportunity_type_names"] = ""
                else:
                    quotation["opportunity_type_id"] = "[]"
                    quotation["opportunity_type_names"] = ""

                # Prefer generated_pdf for coverage_details fields if present
                generated_pdf = quotation.get("generated_pdf")
                used_pdf = False
                if generated_pdf:
                    try:
                        import json as _json
                        pdf_data = _json.loads(generated_pdf)
                        # Return the s3_key instead of the full link for coverage_details
                        quotation["coverage_details"] = pdf_data.get("s3_key", pdf_data.get("link"))
                        quotation["coverage_details_type"] = pdf_data.get("type")
                        quotation["coverage_details_name"] = pdf_data.get("name")
                        used_pdf = True
                    except Exception:
                        pass
                if not used_pdf:
                    # Fallback to vendor response fields (latest by received_date or id)
                    vendor_responses = QueryBuilderService("crmq_vendor_response")\
                        .where("quotation_id", quotation["id"]).orderBy("received_date", "desc").orderBy("id", "desc").get()
                    if vendor_responses:
                        latest = vendor_responses[0]
                        quotation["coverage_details"] = None
                        quotation["coverage_details_type"] = None
                        quotation["coverage_details_name"] = None
                        quotation["received_date"] = latest.get("received_date")
                        quotation["expiry_date"] = latest.get("expiry_date")
                        quotation["total_amount"] = latest.get("total_amount")
                    else:
                        quotation["coverage_details"] = None
                        quotation["coverage_details_type"] = None
                        quotation["coverage_details_name"] = None
                        quotation["received_date"] = None
                        quotation["expiry_date"] = None
                        quotation["total_amount"] = None
                # Always set received_date, expiry_date, total_amount from vendor_responses if available
                vendor_responses = QueryBuilderService("crmq_vendor_response")\
                    .where("quotation_id", quotation["id"]).orderBy("received_date", "desc").orderBy("id", "desc").get()
                if vendor_responses:
                    latest = vendor_responses[0]
                    quotation["received_date"] = latest.get("received_date")
                    quotation["expiry_date"] = latest.get("expiry_date")
                    quotation["total_amount"] = latest.get("total_amount")
                else:
                    quotation["received_date"] = None
                    quotation["expiry_date"] = None
                    quotation["total_amount"] = None

        if not data:
            return ResponseService.response(
                "NOT_FOUND", {}, "team_not_found"
            )

        return ResponseService.response("SUCCESS", data, "quotation_details_retrieved")

 except Exception as e:
        return ResponseService.response(
            "NOT_FOUND", {"error": str(e)}, "default_not_found"
        )


@csrf_exempt
@api_view(["GET"])
def get_vendor_responses(request, quotation_id):
    filter_type = request.GET.get("filter", "received")  # values: received, shortlisted, all
    response_ids_param = request.GET.get("ids", "")
    
    try:
        quotation_id = int(quotation_id)
    except ValueError:
        return ResponseService.response("VALIDATION_ERROR", "Invalid quotation_id format.", Error.VALIDATION_ERROR)

    try:
        response_ids = [int(rid) for rid in response_ids_param.split(",") if rid]
    except ValueError:
        return ResponseService.response("VALIDATION_ERROR", "Invalid ids format.", Error.VALIDATION_ERROR)

    base_query = QueryBuilderService("crmq_quotation_service_providers").where("quotation_id", quotation_id)

    if filter_type == "received":
        base_query = base_query.where("is_received", 1)
    elif filter_type == "shortlisted":
        base_query = base_query.where("is_shortlisted", 1)
    elif filter_type != "all":
        return ResponseService.response("VALIDATION_ERROR", "Invalid filter type.", Error.VALIDATION_ERROR)

    vendor_quotations = base_query.get()
    if not vendor_quotations:
        return ResponseService.response("SUCCESS", [], Message.DATA_NOT_FOUND)

    vendor_quotation_ids = [v["id"] for v in vendor_quotations]
    if not vendor_quotation_ids:
        return ResponseService.response("SUCCESS", [], Message.DATA_NOT_FOUND)

    all_columns = [
        'crmq_vendor_response.*',
        'core_service_providers.name as service_provider_name',
        'core_users.display_name as by_user_name',
        'crmq_quotation_service_providers.service_provider_id',
        'crmq_quotation_service_providers.id as vendor_quotation_id',
        'crmq_quotations.code as quotation_code',
        'crmq_quotations.request_type as quotation_request_type',
        'crmq_quotations.opportunity_type_id as opportunity_type_id',
        'core_status.name as status_name',
        'core_status.color as status_color',
    ]

    query = QueryBuilderService("crmq_vendor_response")\
        .select(*all_columns)\
        .leftJoin("crmq_quotation_service_providers", "crmq_quotation_service_providers.id", "crmq_vendor_response.vendor_quotation_id")\
        .leftJoin("core_service_providers", "core_service_providers.id", "crmq_vendor_response.service_provider_id")\
        .leftJoin("core_users", "core_users.id", "crmq_vendor_response.by_user_id")\
        .leftJoin("crmq_quotations", "crmq_quotations.id", "crmq_vendor_response.quotation_id")\
        .leftJoin("core_status", "core_status.name", "crmq_vendor_response.status")\
        .where("core_status.module", "quotation")\
        .whereIn("crmq_vendor_response.vendor_quotation_id", vendor_quotation_ids)\
        .get()

    results = [
        row for row in query if not response_ids or row["id"] in response_ids
    ]

    for row in results:
        try:
            expire_date = datetime.strptime(row["expiry_date"], "%Y-%m-%d").date()
            today = datetime.now().date()
            row["remaining_days"] = max((expire_date - today).days, 0)
        except Exception:
            row["remaining_days"] = 0
        
        # Process opportunity_type_id to get opportunity_type array
        try:
            opportunity_type_id_str = row.get("opportunity_type_id", "[]")
            if opportunity_type_id_str and opportunity_type_id_str != "[]":
                import json
                opportunity_type_ids = json.loads(opportunity_type_id_str)
                if opportunity_type_ids:
                    opportunity_types = QueryBuilderService("crm_opportunity_types")\
                        .whereIn("id", opportunity_type_ids)\
                        .select("id", "title")\
                        .get()
                    row["opportunity_type"] = [{"id": ot["id"], "title": ot["title"]} for ot in opportunity_types]
                else:
                    row["opportunity_type"] = []
            else:
                row["opportunity_type"] = []
        except Exception:
            row["opportunity_type"] = []

    return ResponseService.response("SUCCESS", results, Message.DATA_FETCHED)


 
@api_view(["GET"])
def quotations_details(request, quotation_id):
    try:
        # Pagination and search params
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "crmq_quotation_service_providers.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        search_string = request.GET.get("search", "")
        
        filter_param = request.GET.get("filter", {})
        
        # Handle filter parameter - convert to JSON string for QueryBuilderService
        if isinstance(filter_param, str):
            if filter_param.strip() == "":
                filter_json = "{}"
            else:
                # If it's a simple string like "shortlisted", wrap it in a dict
                filter_json = '{"status": "' + filter_param + '"}'
        else:
            import json
            filter_json = json.dumps(filter_param)

        # Main columns to select (removed crmq_quotations.version)
        all_columns = [
            "crmq_quotation_service_providers.*",
            "crmq_vendor_response.version as vendor_version",
            # No crmq_quotations.version
            "crmq_quotations.id as quotation_id",
            "crmq_quotations.code as quotation_code",
            "core_service_providers.name as service_provider_name",
            "core_service_providers.email as service_provider_email",
            "core_service_providers.contact_no as service_provider_contact_no",
            "crmq_vendor_response.id as vendor_response_id",
            "crmq_vendor_response.total_amount",
            "crmq_vendor_response.coverage_details",
            "crmq_vendor_response.coverage_details_type",
            "crmq_vendor_response.coverage_details_name",
            "crmq_vendor_response.received_date",
            "crmq_vendor_response.expiry_date",
            "crmq_vendor_response.status as vendor_status",
            "crmq_vendor_response.version as vendor_version",
            "core_users.display_name",
            "core_status.name as status_name",
            "core_status.color as status_color",
        ]

        # Query: base is crmq_quotation_service_providers, filter for "shortlist"
        query = (
            QueryBuilderService("crmq_quotation_service_providers")
            .select(*all_columns)
            .leftJoin(
                "crmq_vendor_response",
                "crmq_vendor_response.vendor_quotation_id",
                "crmq_quotation_service_providers.id"
            )
            .leftJoin(
                "crmq_send_quotations",
                "crmq_send_quotations.quotation_request_id",
                "crmq_quotation_service_providers.quotation_id"
            )
            .leftJoin(
                "crmq_quotations",
                "crmq_quotation_service_providers.quotation_id",
                "crmq_quotations.id"
            )
            .leftJoin(
                "core_service_providers",
                "core_service_providers.id",
                "crmq_quotation_service_providers.service_provider_id"
            )
            .leftJoin(
                "core_users",
                "core_users.id",
                "crmq_vendor_response.by_user_id"
            )
            .leftJoin(
                "core_status",
                "core_status.id",
                "crmq_quotation_service_providers.status"
            )
            .where("crmq_send_quotations.quotation_request_id", quotation_id)
            .where("crmq_quotation_service_providers.is_shortlisted", 1)
        )

        # Apply search/filter/pagination
        data = query.apply_conditions(
            filter_json=filter_json,
            allowed_filters=[],
            search_string=search_string,
            search_columns=["crmq_quotations.code", "core_service_providers.name"]
        ).paginate(
            page=page,
            limit=limit,
            allowed_sorting_columns=["crmq_quotation_service_providers.id", "crmq_quotations.code"],
            sort_by=sort_by,
            sort_dir=sort_dir
        )
        print("quotation..:",query)
        items = data["data"] if isinstance(data, dict) and "data" in data else data

        # Format the response as required
        result = []
        for item in items:
            # Parse coverage_details JSON for doc fields
            doc_name = doc_type = doc_link = None
            coverage_details = item.get("coverage_details")
            if coverage_details:
                try:
                    import json
                    details = json.loads(coverage_details)
                    doc_name = details.get("name")
                    doc_type = details.get("type")
                    doc_link = details.get("link")
                except Exception:
                    doc_name = item.get("coverage_details_name")
                    doc_type = item.get("coverage_details_type")
                    doc_link = item.get("coverage_details")

            # Use crmq_quotation_service_providers.version for both version and quotation_version
            version = item.get("version")

            result.append({
                "id": item.get("id"),
                "opportunity_id": item.get("opportunity_id"),
                "entity_id": item.get("entity_id"),
                "status": item.get("status_name"),  # from crmq_quotation_service_providers.status
                "status_color": item.get("status_color"),  # from crmq_quotation_service_providers.status
                "version": version,
                "date": item.get("received_date"),
                "uploaded_by": item.get("uploaded_by"),
                "quotation_request_id": item.get("quotation_id"),
                "selected_columns": item.get("selected_columns"),
                "vendor_version": item.get("vendor_version"),
                "quotation_version": version,  # use the same as version
                "quotation_id": item.get("quotation_id"),
                "quotation_code": item.get("quotation_code"),
                "service_provider_name": item.get("service_provider_name"),
                "service_provider_email": item.get("service_provider_email"),
                "service_provider_contact_no": item.get("service_provider_contact_no"),
                "vendor_quotation_id": item.get("id"),
                "total_amount": str(item.get("total_amount")) if item.get("total_amount") is not None else None,
                "doc_name": doc_name,
                "doc_type": doc_type,
                "doc_link": doc_link,
                "updated_by": item.get("display_name")
            })

        # Pagination info
        total_records = data.get("total_records", len(result))
        last_page = (total_records + limit - 1) // limit

        response = {
            "is_success": True,
            "message": "team_details_retrieved",
            "result": {
                "total_records": total_records,
                "per_page": limit,
                "current_page": page,
                "last_page": last_page,
                "data": result
            }
        }
        return Response(response)

    except Exception as e:
        return ResponseService.response(
            "NOT_FOUND", {"error": str(e)}, "default_not_found"
        )
 

def get_policy_details(request, id=None):
    user = request.user

        # Get customer ID from user's entity or fallback to 1
    customer_id = user.get('id', 1)
    
    all_columns = [
        "crmp_request_policies.*",
        "crm_opportunity_types.title as opportunity_type_name",
        "crmp_policy_base.premium_amount as premium_amount",
        "core_entity_docs.doc as doc",
        "core_entity_docs.name as doc_name",
        "core_entity_docs.type as doc_type",
    ]

#     filter_json = request.GET.get("filter", {})
#     search_string = request.GET.get("search", "")
#     page = int(request.GET.get("page", 1))
#     limit = int(request.GET.get("limit", 10))
#     sort_by = request.GET.get("sort_by", "crmp_request_policies.id")
#     sort_dir = request.GET.get("sort_dir", "desc")
#     allowed_sorting_columns = ["crmp_request_policies.id", ]

    

#     data = (
#         QueryBuilderService("crmp_request_policies")
#         .select(*all_columns)
#         .leftJoin(
#             "crmp_policy_base",
#             "crmp_policy_base.id",
#             "crmp_request_policies.policy_base_id" )
#         .leftJoin(
#             "crm_opportunity_types",
#             "crm_opportunity_types.id",
#             "crmp_policy_base.risk_type_id" )
#         .leftJoin(
#             "core_entity_docs",
#             "core_entity_docs.entity_id",
#             "crmp_request_policies.entity_id"
#         )
#         # .where("crmp_policy_base.customer_id", customer_id)
#     )

#     if id:
#         data = data.where("crmp_request_policies.id", id).first()
#         if not data:
#             return ResponseService.response(
#                 "NOT_FOUND", {}, "policy_not_found"
#             )
#         return ResponseService.response("SUCCESS", data, "policy_details_retrieved")
#     else:
#         data = data.apply_conditions(
#             filter_json=filter_json,
#             allowed_filters=[],
#             search_string=search_string,
#             search_columns=["crmp_request_policies.id", "crmp_request_policies.policy_number"]
#         ).paginate(
#             page=page,
#             limit=limit,
#             allowed_sorting_columns=allowed_sorting_columns,
#             sort_by=sort_by,
#             sort_dir=sort_dir
#         )
#     return ResponseService.response("SUCCESS", data, "policy_data_get")

def _calculate_total_paid_amount(policy_id):
    """
    Calculate total paid amount for a policy by summing all settlements
    from both cus_payments and crmf_payments for all invoices of that policy.
    """
    try:
        # Get all invoice IDs for this policy
        invoice_ids = QueryBuilderService("crmf_invoices").select("id").where("issued_policy_id", policy_id).get()
        invoice_id_list = [inv["id"] for inv in (invoice_ids if isinstance(invoice_ids, list) else invoice_ids.get("data", []))]
        
        if not invoice_id_list:
            return 0
        
        total_paid = 0
        
        # Sum from cus_payments (excluding deleted)
        cus_payments = QueryBuilderService("cus_payments").select("paid_amount").whereIn("invoice_id", invoice_id_list).whereNull("deleted_at").get()
        if isinstance(cus_payments, list):
            for payment in cus_payments:
                total_paid += float(payment.get("paid_amount") or 0)
        elif isinstance(cus_payments, dict) and cus_payments.get("data"):
            for payment in cus_payments["data"]:
                total_paid += float(payment.get("paid_amount") or 0)
        
        # Sum from crmf_payments
        crmf_payments = QueryBuilderService("crmf_payments").select("paid_amount").whereIn("invoice_id", invoice_id_list).get()
        if isinstance(crmf_payments, list):
            for payment in crmf_payments:
                total_paid += float(payment.get("paid_amount") or 0)
        elif isinstance(crmf_payments, dict) and crmf_payments.get("data"):
            for payment in crmf_payments["data"]:
                total_paid += float(payment.get("paid_amount") or 0)
        
        return total_paid
    except Exception as e:
        print(f"Error calculating total paid amount: {e}")
        return 0

def _get_issued_policy_details(request, policy_id=None):
    columns = [
        "crmp_issued_policies.*",
        "crmp_issued_policies.remarks AS insurer_notes",
        "products.id AS product_id",
        "risk_type.title AS risk_type_name",
        "risk_type.id AS risk_type_id",
        "insurer_sp.name AS insurer_info_full_name",
        "insurer_sp.id AS insurer_id",
        "insurer_sp.logo AS insurer_info_logo",
        "customers.name as customer_name",
        "customers.logo as customer_logo",
        "customers.id as customer_id",
        "products.name as product",
        "request_policy.policy_request_id as policy_request_code",
        "request_policy.id as policy_request_id",
        "policy_status.name AS policy_request_status",
        "policy_status.color AS policy_request_status_color",
        "policy_base.quotation_document as quotation_document",
        "policy_base.quotation_document_name as quotation_document_name",
        # Additional Request Policy Info
        "request_by.display_name AS requested_by",
        "request_by.picture AS requested_by_logo",
        "request_type.name AS request_type",
        "request_type.id AS request_type_id",
        "customer_contact.email AS customer_email",
        "customer_contact.address AS customer_address",
        "customer_contact.primary_contact AS customer_primary_contact",
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
        "crmp_issued_policies.sum_insured",
        "crmp_issued_policies.premium_amount as premium_amount",
    ]

    user = request.user
    
    # Get customer ID from user - handle both dict and object types
    if isinstance(user, dict):
        customer_id = user.get("id")
    else:
        customer_id = getattr(user, "id", None)
    
    if not customer_id:
        return ResponseService.response("UNAUTHORIZED", None, "Customer ID missing in token")

    query = (
        QueryBuilderService("crmp_issued_policies")
        .select(*columns)
        .leftJoin(
            "crmp_policy_base as policy_base",
            "policy_base.id",
            "crmp_issued_policies.policy_base_id",
        )
        .leftJoin(
            "core_status as policy_status",
            "policy_status.id",
            "policy_base.status_id",
        )
        .leftJoin(
            "crm_opportunity_types as risk_type",
            "risk_type.id",
            "policy_base.risk_type_id",
        )
        .leftJoin(
            "core_vendor_products as products",
            "products.id",
            "policy_base.product_id",
        )
        .leftJoin(
            "core_service_providers as insurer_sp",
            "insurer_sp.id",
            "policy_base.insurer_id",
        )
        .leftJoin(
            "core_entities as entity",
            "entity.id",
            "crmp_issued_policies.entity_id",
        )
        .leftJoin(
            "core_entity_docs",
            "core_entity_docs.entity_id",
            "crmp_issued_policies.entity_id"
        )
        .leftJoin(
            "core_customers as customers",
            "customers.id",
            "policy_base.customer_id",
        )
        .leftJoin(
            "crmp_request_policies as request_policy",
            "request_policy.id",
            "crmp_issued_policies.policy_request_id",
        )
        .leftJoin(
            "core_status as request_status",
            "request_status.id",
            "request_policy.status_id",
        )
        .leftJoin(
            "core_users as request_by",
            "request_by.id",
            "policy_base.request_by_id",
        )
        .leftJoin(
            "crmp_request_types as request_type",
            "request_type.id",
            "policy_base.request_type_id",
        )
        .leftJoin(
            "core_contacts as customer_contact",
            "customer_contact.id",
            "customers.primary_contact_id",
        )
        .leftJoin(
            "crmp_coverage_types as coverage_type",
            "coverage_type.id",
            "policy_base.coverage_type_id",
        )
        .leftJoin(
            "crmp_payment_plans as payment_plan",
            "payment_plan.id",
            "policy_base.payment_mode_id",
        )
        .leftJoin(
            "core_users as created_by",
            "created_by.id",
            "entity.created_by_id",
        )
        .leftJoin(
            "core_users as updated_by",
            "updated_by.id",
            "entity.updated_by_id",
        )
        .leftJoin(
            "crmf_invoices as invoices",
            "invoices.issued_policy_id",
            "crmp_issued_policies.id",
        )
        .where("policy_base.customer_id", customer_id)
    )

    if policy_id:
        data = query.where("crmp_issued_policies.id", policy_id).first()
        if not data:
            # Check if policy exists but belongs to different customer
            policy_exists = QueryBuilderService("crmp_issued_policies").where("id", policy_id).first()
            if policy_exists:
                return ResponseService.response("FORBIDDEN", None, "Policy exists but does not belong to this customer")
            return ResponseService.response("NOT_FOUND", None, "Policy not found")
        _format_date_fields(data)
        # Calculate total paid amount from all settlements
        total_paid = _calculate_total_paid_amount(policy_id)
        premium_amount = float(data.get("premium_amount") or 0)
        data["paid_amount"] = total_paid
        data["outstanding_amount"] = premium_amount - total_paid
        # Add endorsement_count for single policy
        endorsement_count = QueryBuilderService("crmp_endorsement_requests").where("issued_policy_id", data["id"]).count()
        data["endorsement_count"] = endorsement_count
        return ResponseService.response("SUCCESS", data, "Message.DATA_FETCHED")

    # List with filters, pagination
    filter_param = request.GET.get("filter", "{}")
    
    # Handle filter parameter - if it's a string, convert to proper format
    if isinstance(filter_param, str):
        if filter_param.strip() == "":
            filter_json = {}
        else:
            try:
                filter_json = json.loads(filter_param)
            except json.JSONDecodeError:
                # If it's a simple string like "shortlisted", wrap it in a dict
                filter_json = {"status": filter_param}
    else:
        filter_json = filter_param
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by") or "crmp_issued_policies.policy_effective_date"
    sort_dir = request.GET.get("sort_dir") or "desc"

    allowed_filters = [
        "products.name",
        "crmp_issued_policies.risk_level",
        "coverage_type.name",
        "sales_agent.display_name",
        "account_manager.display_name",
        "insurer_sp.name",
    ]
    search_columns = [
        "crmp_issued_policies.brokerage_policy_id",
        "products.name",
        "coverage_type.name",
        "crmp_issued_policies.start_date",
        "crmp_issued_policies.end_date",
        "customers.name",
        "insurer_sp.name",
        "request_by.display_name",
        "customer_email",
        "customer_address",
        "customer_primary_contact",
        "policy_base.quotation_document_name",
        "policy_base.quotation_notes",
        "invoices.invoice_number",
    ]
    sort_columns = [
        "crmp_issued_policies.start_date",
        "crmp_issued_policies.policy_effective_date",
        "products.name",
        "crmp_issued_policies.brokerage_policy_id",
        "coverage_type.name",
        "sales_agent.display_name",
        "account_manager.display_name",
    ]

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)
    rows = data.get("data", [])
    
    # Remove duplicates by keeping only unique policy IDs
    seen_policies = set()
    unique_rows = []
    for item in rows:
        policy_id = item["id"]
        if policy_id not in seen_policies:
            seen_policies.add(policy_id)
            unique_rows.append(item)
    
    for item in unique_rows:
        _format_date_fields(item)
        # Calculate total paid amount from all settlements for each policy
        total_paid = _calculate_total_paid_amount(item["id"])
        premium_amount = float(item.get("premium_amount") or 0)
        item["paid_amount"] = total_paid
        item["outstanding_amount"] = premium_amount - total_paid
        # Add endorsement_count for each policy in the list
        endorsement_count = QueryBuilderService("crmp_endorsement_requests").where("issued_policy_id", item["id"]).count()
        item["endorsement_count"] = endorsement_count
    
    # Update the data with unique rows
    data["data"] = unique_rows

    return ResponseService.response("SUCCESS", data, "DATA_FETCHED")



@api_view(["GET"])
def get_all_issued_policies(request, policy_id=None):
    return _get_issued_policy_details(request, policy_id=policy_id)

@api_view(["GET"])
def policy_details_single(request, id):
    return _get_issued_policy_details(request, policy_id=id)

@api_view(["GET"])
def claims_details(request, id=None):
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
    allowed_sorting_columns = ["crmp_claims.id", ]

    # Select fields
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
    ]
    # Build base query
    query = (
        QueryBuilderService("crmp_claims as claim")
        .leftJoin("crmp_issued_policies as policy", "policy.id", "claim.policy_id")
        .leftJoin("crmp_policy_base as base", "base.id", "policy.policy_base_id")
        .leftJoin("core_customers as customer", "customer.id", "base.customer_id")
        .leftJoin("crm_opportunity_types as risk", "risk.id", "claim.risk_type_id")
        .leftJoin("core_service_providers as insurer", "insurer.id", "claim.insurer_id")
        .leftJoin("core_templates as form", "form.id", "claim.template_id")
        .leftJoin("core_status as status", "status.id", "claim.status_id")
        .select(*all_columns)
    )

    if id is not None:
        data = query.where("claim.id", id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", {}, "claim_not_found")
        return ResponseService.response("SUCCESS", data, "claim_details_retrieved")
    else:
        data = query.apply_conditions(filter_json, [], search_string, ["claim.code", "status.name", "risk.title", "insurer.name"]).paginate(
            page=page,
            limit=limit,
            allowed_sorting_columns=allowed_sorting_columns,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
        return ResponseService.response("SUCCESS", data, "data_get")


@api_view(["GET"])
def all_notifications(request):
    try:
        from datetime import datetime, timedelta
        user = request.user
        customer_id = user.get('id', 1)
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by") or "core_notification_users.id"
        sort_dir = request.GET.get("sort_dir") or "desc"
        allowed_sorting_columns = ["core_notification_users.id"]
        read_status = request.GET.get("read_status", "")
        search_string = request.GET.get("search", "")
        
        # Handle filter parameter
        filter_param = request.GET.get("filter", "")
        
        # Handle filter parameter - convert to proper format
        if isinstance(filter_param, str):
            if filter_param.strip() == "":
                filter_json = {}
            else:
                # Handle special filter values for date-based filtering
                now = datetime.now()
                
                if filter_param in ["last_month", "last_week", "today", "yesterday"]:
                    # Date filters are handled directly with where clauses, so use empty filter_json
                    filter_json = {}
                else:
                    # If it's a simple string, wrap it in a dict for type filtering
                    filter_json = {"type": filter_param}
        else:
            filter_json = filter_param

        all_columns = [
            "core_notification_users.*",
            "core_notifications.*",
            "core_notification_types.code as notification_code",
            "core_notification_types.name as notification_name",
            "core_notification_types.color as type_color",
            "core_notification_types.name as type_name",
            "core_notification_types.code as type_code",
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
            .where("core_notification_users.customer_id", customer_id)
            .where("core_notification_users.is_clear", 0)
        )

        # Handle date-based filtering directly with where clauses
        if isinstance(filter_param, str) and filter_param.strip():
            now = datetime.now()
            
            if filter_param == "last_month":
                # Calculate date range for last month
                first_day_this_month = now.replace(day=1)
                first_day_last_month = (first_day_this_month - timedelta(days=1)).replace(day=1)
                last_day_last_month = first_day_this_month - timedelta(days=1)
                
                query = query.whereBetween("core_notifications.created_at", first_day_last_month.strftime("%Y-%m-%d 00:00:00"), last_day_last_month.strftime("%Y-%m-%d 23:59:59"))
                
            elif filter_param == "last_week":
                # Calculate date range for last week (7 days ago)
                last_week_start = now - timedelta(days=7)
                query = query.whereBetween("core_notifications.created_at", last_week_start.strftime("%Y-%m-%d 00:00:00"), now.strftime("%Y-%m-%d 23:59:59"))
                
            elif filter_param == "today":
                # Today's notifications
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                query = query.whereBetween("core_notifications.created_at", today_start.strftime("%Y-%m-%d %H:%M:%S"), now.strftime("%Y-%m-%d %H:%M:%S"))
                
            elif filter_param == "yesterday":
                # Yesterday's notifications
                yesterday = now - timedelta(days=1)
                yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
                yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
                query = query.whereBetween("core_notifications.created_at", yesterday_start.strftime("%Y-%m-%d %H:%M:%S"), yesterday_end.strftime("%Y-%m-%d %H:%M:%S"))

        # Apply conditions with filtering for non-date filters
        allowed_filters = [
            "core_notification_types.code",
            "core_notification_types.name",
            "core_notifications.type_id"
        ]
        
        search_columns = [
            "core_notifications.title",
            "core_notifications.message",
            "core_notification_types.name"
        ]

        data = (
            query
            .apply_conditions(
                filter_json=filter_json,
                allowed_filters=allowed_filters,
                search_string=search_string,
                search_columns=search_columns
            )
            .orderBy(sort_by, sort_dir)
            .get()
        )

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
    except Exception as e:
        print(f"Error in all_notifications: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            "is_success": False,
            "message": f"Error: {str(e)}",
            "result": None
        }, status=500)


@api_view(["GET"])
def read_notifications(request):
    user = request.user
    customer_id = user.get('id', 1)
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_notification_users.id")
    sort_dir = request.GET.get("sort_dir", "desc")
    allowed_sorting_columns = ["core_notification_users.id"]

    all_columns = [
        "core_notification_users.*",
        "core_notifications.*"
    ]

    data = (
        QueryBuilderService("core_notification_users")
        .select(*all_columns)
        .leftJoin(
            "core_notifications",
            "core_notifications.id",
            "core_notification_users.notification_id"
        )
        .where("core_notification_users.customer_id", customer_id)
        .where("core_notification_users.is_clear", 0)
        .orderBy(sort_by, sort_dir)
        .paginate(
            page=page,
            limit=limit,
            allowed_sorting_columns=allowed_sorting_columns,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
    )
    return ResponseService.response("SUCCESS", data, "read_notifications_retrieved")

@api_view(["GET"])
def unread_notifications(request):
    user = request.user
    customer_id = user.get('id', 1)
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_notification_users.id")
    sort_dir = request.GET.get("sort_dir", "desc")
    allowed_sorting_columns = ["core_notification_users.id"]

    all_columns = [
        "core_notification_users.*",
        "core_notifications.*"
    ]

    data = (
        QueryBuilderService("core_notification_users")
        .select(*all_columns)
        .leftJoin(
            "core_notifications",
            "core_notifications.id",
            "core_notification_users.notification_id"
        )
        .where("core_notification_users.customer_id", customer_id)
        .where("core_notification_users.is_clear", 0)
        .where("core_notification_users.is_read", 0)
        .orderBy(sort_by, sort_dir)
        .paginate(
            page=page,
            limit=limit,
            allowed_sorting_columns=allowed_sorting_columns,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
    )
    return ResponseService.response("SUCCESS", data, "unread_notifications_retrieved")

 
    
@api_view(["POST"])
def change_notifications_status(request, ids):
    # ids: comma-separated string of core_notification_users.id values
    user = request.user
    customer_id = user.get('id', 1)
    id_list = [int(i) for i in ids.split(',') if i.strip().isdigit()]
    now = datetime.now()
    QueryBuilderService("core_notification_users") \
        .where("customer_id", customer_id) \
        .whereIn("id", id_list) \
        .update({"is_read": 1, "read_at": now})
    return ResponseService.response("SUCCESS", None, "Notification(s) marked as read.")
    
@api_view(["GET"])
def get_claims_detail(request, id):
    return claims_details(request, id=id)


@api_view(["GET", "DELETE"])
def single_notifications(request, id):
    if request.method == "GET":
        return get_one_notification(request, id)
    
    if request.method == "DELETE":
        return delete_notification(request, id)


def get_one_notification(request, id):
    try:
        customer_id = 96  # Or get from request if needed
        all_columns = [
            "core_notifications.*",
            "core_notification_types.name as type_name",
            "core_notification_types.color as type_color"
        ]
        
        data = (
            QueryBuilderService("core_notifications")
            .select(*all_columns)
            .leftJoin(
                "core_notification_types",
                "core_notification_types.id",
                "core_notifications.type_id"
            )
            # .where("core_notifications.customer_id", customer_id)
            .where("core_notifications.id", id)
            .first()
        )
        
        if not data:
            return ResponseService.response(
                "NOT_FOUND", {}, "notification_not_found"
            )
            
        return ResponseService.response("SUCCESS", data, "single_notification_retrieved")
        
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {"error": str(e)}, "error")


def delete_notification(request, id):
    user = request.user
    customer_id = user.get('id', 1)
    # Only update core_notification_users.is_clear using the mapping table PK
    QueryBuilderService("core_notification_users") \
        .where("customer_id", customer_id) \
        .where("id", id) \
        .update({"is_clear": 1})
    return ResponseService.response("SUCCESS", None, "notification_deleted_successfully")

@api_view(["GET","PUT"])
def personal_info(request):
    if request.method == "GET":
        return get_personal_info(request)
    if request.method == "PUT":
        return edit_personal_info(request)
 
def get_personal_info(request):
    user = request.user
    customer_id = user.get('id', 15)  # Use 15 for testing, or user.get('id', 1) for default
    #customer_id = 15# Use 15 for testing, or user.get('id', 1) for default
    print("customer_id",customer_id)
    all_columns = [
        "core_customers.*",
        "core_contacts.name as contact_name",
        "core_contacts.email as contact_email",
        "core_contacts.address as contact_address",
        "core_contacts.primary_contact as contact_primary_contact",
        "core_contacts.secondary_contact as contact_secondary_contact",
        "core_contacts.remarks as contact_remarks",
        "core_contacts.website_url as contact_website_url",
        "core_contacts.picture as contact_picture",
        "cus_banks_details.id as bank_detail_id",
        "cus_banks_details.doc",
        "cus_banks_details.doc_type",
        "cus_banks_details.doc_name",
        "cus_banks_details.account_holder_name",
        "cus_banks_details.bank_name",
        "cus_banks_details.bank_branch",
        "cus_banks_details.account_number",
        "cus_banks_details.iban_swift_code",
        "cus_banks_details.created_at",
        "cus_banks_details.updated_at",
    ]

    customer = (
        QueryBuilderService('core_customers')
        .leftJoin('core_contacts','core_contacts.id','core_customers.primary_contact_id')
        .leftJoin('cus_banks_details','cus_banks_details.customer_id','core_customers.id')
        .select(*all_columns)
        .where('core_customers.id', customer_id)
        .first()
    )

    if not customer:
        return ResponseService.response("NOT_FOUND", [], "data_not_found")

    return ResponseService.response("SUCCESS", customer, "data_get")
 
 
def edit_personal_info(request):
    data = request.data

    rules = {
        "name": "required",
        "logo": "optional",
        "contact_email" : "optional",
        "contact_primary_contact" : "optional",
        "contact_picture" : "optional",
        "contact_address" : "optional",
        # Bank info fields
        "account_holder_name": "required",
        "bank_name": "required",
        "bank_branch": "required",
        "account_number": "required",
        "iban_swift_code": "optional",
        "doc": "required",
        "doc_type": "optional",
        "doc_name": "optional",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        print(errors)  # Debug: print validation errors
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
    
  
    user = request.user
    customer_id = user.get('id', 15)  # Use 15 for testing, or user.get('id', 1) for default
    #customer_id = 15  # Use 15 for testing, or user.get('id', 1) for default
    print("customer_id",customer_id) # You may want to get this from the user/session

    # Get the customer record
    customer = QueryBuilderService('core_customers').where('id', customer_id).first()
    if not customer:
        return ResponseService.response("VALIDATION_ERROR", [], "Validation Error")

    update_customer_data = {
        "name": data.get('name'),
        "logo": data.get('logo')
    }
    QueryBuilderService('core_customers').where('core_customers.id', customer_id).update(update_customer_data)

    update_contact_data = {
        "email": data.get('contact_email'),
        "primary_contact": data.get('contact_primary_contact'),
        "picture": data.get('contact_picture'),
        "address": data.get('contact_address')
    }

    primary_contact_id = customer.get('primary_contact_id')

    if not primary_contact_id:
        # Create new contact and update customer
        new_contact = QueryBuilderService('core_contacts').insert(update_contact_data)
        QueryBuilderService('core_customers').where('core_customers.id', customer_id).update({
            "primary_contact_id": new_contact.id
        })
    else:
        # Update existing contact
        QueryBuilderService('core_contacts').where('id', primary_contact_id).update(update_contact_data)

    # --- BANK DETAILS UPDATE/CREATE ---
    bank_data = {
        "customer_id": customer_id,
        "account_holder_name": data.get("account_holder_name"),
        "bank_name": data.get("bank_name"),
        "bank_branch": data.get("bank_branch"),
        "account_number": data.get("account_number"),
        "iban_swift_code": data.get("iban_swift_code"),
        "doc": data.get("doc"),
        "doc_type": data.get("doc_type"),
        "doc_name": data.get("doc_name"),
    }

    existing_bank = QueryBuilderService('cus_banks_details').where('customer_id', customer_id).first()
    if existing_bank:
        QueryBuilderService('cus_banks_details').where('customer_id', customer_id).update(bank_data)
    else:
        QueryBuilderService('cus_banks_details').insert(bank_data)
    # -----------------------------------

    return ResponseService.response("SUCCESS", [], "data_updated")
    





@api_view(["GET"])
def get_template_by_risk_type_and_type(request, risk_type_id):
    try:
        data_gethering_type = request.GET.get("type")

        if not data_gethering_type:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "Query parameter 'type' is required (e.g., 'claim')"},
                Error.VALIDATION_ERROR
            )

        # Step 1: Get form config by opportunity_type (risk_type) and data_gethering_type
        form_config = (
            QueryBuilderService("crm_opportunity_form_config")
            .where("opportunity_type_id", risk_type_id)
            .where("data_gethering_type", data_gethering_type)
            .first()
        )

        if not form_config or not form_config.get("form_id"):
            return ResponseService.response(
                "NOT_FOUND",
                {"error": "No customer form template found for this risk type"},
                "customer_template_not_found",
                "NOT_FOUND"
            )

        # Step 2: Fetch the CoreTemplate model instance
        form_id = form_config["form_id"]
        try:
            template = CoreTemplate.objects.get(id=form_id)
        except CoreTemplate.DoesNotExist:
            return ResponseService.response(
                "NOT_FOUND",
                {"error": "Referenced form/template does not exist"},
                "Referenced template does not exist",
                "NOT_FOUND"
            )


        return get_template_detail(template)

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Need to assign the valid form template for this risk type."
        )
    
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




@api_view(["GET"]) 
def get_generate_document_forms(request, quotation_id):
    """
  
    """
    # Determine desired status
    status = request.GET.get("status", "draft").lower()
    if status not in ["draft", "sent"]:
        return ResponseService.response(
            "VALIDATION_ERROR",
            "Invalid status value; must be 'draft' or 'sent'.",
            "Error.VALIDATION_ERROR"
        )

    # Fetch send_quotations with matching status
    drafts = QueryBuilderService("crmq_send_quotations")\
        .select(
            "id", "version", "date as uploaded_date", "uploaded_by",
            "opportunity_id", "entity_id", "status",
            "quotation_request_id", "generated_pdf"
        )\
        .where("quotation_request_id", quotation_id)\
        .where("status", status)\
        .get()

    if not drafts:
        msg = f"No {status} quotations found."
        return ResponseService.response("SUCCESS", [], msg)

    # Map user IDs to display names
    user_ids = {d["uploaded_by"] for d in drafts if d.get("uploaded_by")}
    user_map = {}
    if user_ids:
        users = QueryBuilderService("core_users")\
            .select("id", "display_name as uploaded_by_name")\
            .whereIn("id", list(user_ids)).get()
        user_map = {u["id"]: u["uploaded_by_name"] for u in users}

    # Map entity IDs to uploaded docs
    entity_ids = {d["entity_id"] for d in drafts if d.get("entity_id")}
    doc_map = {}
    if entity_ids:
        docs = QueryBuilderService("core_entity_docs")\
            .select("entity_id", "doc", "name", "type")\
            .whereIn("entity_id", list(entity_ids)).get()
        for d in docs:
            doc_map[d["entity_id"]] = {
                "coverage_details": d["doc"],
                "coverage_details_name": d["name"],
                "coverage_details_type": d["type"]
            }

    # Get customer info from main quotation
    customer_obj = {}
    main_quote = QueryBuilderService("crmq_quotations")\
        .select("id", "customer_id")\
        .where("id", quotation_id).first()
    if main_quote and main_quote.get("customer_id"):
        cust = QueryBuilderService("core_customers")\
            .select("id", "name")\
            .where("id", main_quote["customer_id"]).first()
        if cust:
            customer_obj = {
                "customer": {"id": cust["id"], "name": cust["name"]}
            }

    result = []
    all_service_provider_ids = set()
    for draft in drafts:
        send_id = draft["id"]
        vendor_links = QueryBuilderService("crmq_quotation_vendor_quotations")\
            .where("send_quotation_id", send_id).get()
        linked_ids = [v["vendor_quotation_id"] for v in vendor_links]

        values_list, service_provider_ids = [], set()
        if linked_ids:
            vq_map = {
                v["id"]: v["service_provider_id"]
                for v in QueryBuilderService("crmq_quotation_service_providers")\
                    .whereIn("id", linked_ids).get()
            }

            for vqid in linked_ids:
                sp = vq_map.get(vqid)
                if not sp:
                    continue
                service_provider_ids.add(sp)
                all_service_provider_ids.add(sp)

                responses = QueryBuilderService("crmq_vendor_response")\
                    .where("vendor_quotation_id", vqid).get()
                for resp in responses:
                    values_list.append({
                        "quotation_id": resp.get("quotation_id"),
                        "response_value": resp.get("response_value"),
                        "service_provider_id": sp,
                        "expiry_date": resp.get("expiry_date"),
                        "total_amount": resp.get("total_amount"),
                        "received_date": resp.get("received_date")
                    })

        # Collect document links
        docs = []
        ent = draft.get("entity_id")
        if ent in doc_map:
            docs.append(doc_map[ent])
        # Parse generated PDF JSON
        genpdf = draft.get("generated_pdf")
        if genpdf:
            try:
                pdf_data = json.loads(genpdf)
                docs.append({
                    "coverage_details": pdf_data.get("link"),
                    "coverage_details_name": pdf_data.get("name"),
                    "coverage_details_type": pdf_data.get("type")
                })
            except Exception:
                pass

        result.append({
            "send_quotation_id": send_id,
            "version": draft.get("version"),
            "uploaded_date": draft.get("uploaded_date"),
            "uploaded_by": draft.get("uploaded_by"),
            "uploaded_by_name": user_map.get(draft.get("uploaded_by"), "Unknown"),
            "opportunity_id": draft.get("opportunity_id"),
            "entity_id": draft.get("entity_id"),
            "status": draft.get("status"),
            "quotation_request_id": draft.get("quotation_request_id"),
            "service_provider_ids": list(service_provider_ids),
            "vendor_quotation_ids": list(linked_ids),
            "values": values_list,
            "documents": docs,
            **customer_obj
        })
        # Add top-level received_date, total_amount, expiry_date from first value if present
        if values_list:
            first_val = values_list[0]
            result[-1]["received_date"] = first_val.get("received_date")
            result[-1]["total_amount"] = first_val.get("total_amount")
            result[-1]["expiry_date"] = first_val.get("expiry_date")
        else:
            result[-1]["received_date"] = None
            result[-1]["total_amount"] = None
            result[-1]["expiry_date"] = None

    # Map service_provider_id to name
    sp_name_map = {}
    if all_service_provider_ids:
        sp_rows = QueryBuilderService("core_service_providers")\
            .select("id", "name")\
            .whereIn("id", list(all_service_provider_ids)).get()
        sp_name_map = {row["id"]: row["name"] for row in sp_rows}

    # Add service_provider_names to each result
    for r in result:
        r["service_provider_names"] = [sp_name_map.get(spid, "Unknown") for spid in r["service_provider_ids"]]

    return ResponseService.response("SUCCESS", result, "default_get_all_success_msg")


@api_view(["GET"])
def get_single_generate_document_forms(request, send_quotation_id):
    """
    Return a single sent out quotation view, enriched with service provider names, documents, etc.
    """
    # Fetch the single send_quotation
    draft = QueryBuilderService("crmq_send_quotations")\
        .select(
            "id", "version", "date as uploaded_date", "uploaded_by",
            "opportunity_id", "entity_id", "status",
            "quotation_request_id", "generated_pdf"
        )\
        .where("id", send_quotation_id)\
        .first()
    if not draft:
        return ResponseService.response("NOT_FOUND", {}, "No sent quotation found.")

    # Map user ID to display name
    user_map = {}
    if draft.get("uploaded_by"):
        users = QueryBuilderService("core_users")\
            .select("id", "display_name as uploaded_by_name")\
            .whereIn("id", [draft["uploaded_by"]]).get()
        user_map = {u["id"]: u["uploaded_by_name"] for u in users}

    # Map entity ID to uploaded docs
    doc_map = {}
    if draft.get("entity_id"):
        docs = QueryBuilderService("core_entity_docs")\
            .select("entity_id", "doc", "name", "type")\
            .whereIn("entity_id", [draft["entity_id"]]).get()
        for d in docs:
            doc_map[d["entity_id"]] = {
                "coverage_details": d["doc"],
                "coverage_details_name": d["name"],
                "coverage_details_type": d["type"]
            }

    # Get customer info from main quotation
    customer_obj = {}
    main_quote = QueryBuilderService("crmq_quotations")\
        .select("id", "customer_id")\
        .where("id", draft["quotation_request_id"]).first()
    if main_quote and main_quote.get("customer_id"):
        cust = QueryBuilderService("core_customers")\
            .select("id", "name")\
            .where("id", main_quote["customer_id"]).first()
        if cust:
            customer_obj = {
                "customer": {"id": cust["id"], "name": cust["name"]}
            }

    send_id = draft["id"]
    vendor_links = QueryBuilderService("crmq_quotation_vendor_quotations")\
        .where("send_quotation_id", send_id).get()
    linked_ids = [v["vendor_quotation_id"] for v in vendor_links]

    values_list, service_provider_ids = [], set()
    if linked_ids:
        vq_map = {
            v["id"]: v["service_provider_id"]
            for v in QueryBuilderService("crmq_quotation_service_providers")\
                .whereIn("id", linked_ids).get()
        }

        for vqid in linked_ids:
            sp = vq_map.get(vqid)
            if not sp:
                continue
            service_provider_ids.add(sp)

            responses = QueryBuilderService("crmq_vendor_response")\
                .where("vendor_quotation_id", vqid).get()
            for resp in responses:
                values_list.append({
                    "quotation_id": resp.get("quotation_id"),
                    "response_value": resp.get("response_value"),
                    "service_provider_id": sp,
                    "expiry_date": resp.get("expiry_date"),
                    "total_amount": resp.get("total_amount"),
                    "received_date": resp.get("received_date")
                })

    # Collect document links
    docs = []
    ent = draft.get("entity_id")
    if ent in doc_map:
        docs.append(doc_map[ent])
    # Parse generated PDF JSON
    genpdf = draft.get("generated_pdf")
    if genpdf:
        try:
            pdf_data = json.loads(genpdf)
            docs.append({
                "coverage_details": pdf_data.get("link"),
                "coverage_details_name": pdf_data.get("name"),
                "coverage_details_type": pdf_data.get("type")
            })
        except Exception:
            pass

    # Map service_provider_id to name
    sp_name_map = {}
    if service_provider_ids:
        sp_rows = QueryBuilderService("core_service_providers")\
            .select("id", "name")\
            .whereIn("id", list(service_provider_ids)).get()
        sp_name_map = {row["id"]: row["name"] for row in sp_rows}

    result = {
        "send_quotation_id": send_id,
        "version": draft.get("version"),
        "uploaded_date": draft.get("uploaded_date"),
        "uploaded_by": draft.get("uploaded_by"),
        "uploaded_by_name": user_map.get(draft.get("uploaded_by"), "Unknown"),
        "opportunity_id": draft.get("opportunity_id"),
        "entity_id": draft.get("entity_id"),
        "status": draft.get("status"),
        "quotation_request_id": draft.get("quotation_request_id"),
        "service_provider_ids": list(service_provider_ids),
        "service_provider_names": [sp_name_map.get(spid, "Unknown") for spid in service_provider_ids],
        "vendor_quotation_ids": list(linked_ids),
        "values": values_list,
        "documents": docs,
        **customer_obj
    }
    # Add top-level received_date, total_amount, expiry_date from first value if present
    if values_list:
        first_val = values_list[0]
        result["received_date"] = first_val.get("received_date")
        result["total_amount"] = first_val.get("total_amount")
        result["expiry_date"] = first_val.get("expiry_date")
    else:
        result["received_date"] = None
        result["total_amount"] = None
        result["expiry_date"] = None

    return ResponseService.response("SUCCESS", result, "default_get_success_msg")



@api_view(["GET","PUT"])
def contact_email(request):
    if request.method == "GET":
        return get_contact_email(request)
    if request.method == "PUT":
        return update_contact_email(request)


def get_contact_email(request):
    customer_id = request.user.get('id')
    # Get the customer's primary contact id
    customer = QueryBuilderService('core_customers').where('id', customer_id).first()
    if not customer:
        return ResponseService.response("NOT_FOUND", {}, "customer_not_found")
    primary_contact_id = customer.get('primary_contact_id')
    if not primary_contact_id:
        return ResponseService.response("NOT_FOUND", {}, "primary_contact_not_found")
    # Fetch email and contact_email from core_contacts
    contact = QueryBuilderService('core_contacts').where('id', primary_contact_id).first()
    if not contact:
        return ResponseService.response("NOT_FOUND", {}, "contact_not_found")
    result = {
        "email": contact.get('email'),
        "contact_email": contact.get('contact_email')
    }
    return ResponseService.response("SUCCESS", result, "contact_email_retrieved")

def update_contact_email(request):

    # customer_id = 19  # Replace with request.user.get('id') if needed
    customer_id =  request.user.get('id') 

    data = request.data

    rules = { "email" : "required|email"}

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
    
    primary_contact = QueryBuilderService("core_customers").where('id',customer_id).first()
    if primary_contact:
        primary_contact_id = primary_contact.get("primary_contact_id")

    update = (
        QueryBuilderService('core_contacts').where('id',primary_contact_id).update({'contact_email': data.get('email')})
    )

    if not update:
                return ResponseService.response(  "VALIDATION_ERROR", [], "data didnt updated")
    
    return ResponseService.response("SUCCESS", update, "data_updated")

@api_view(["GET"])
def policy_bankinfo(request, id):
    # Step 1: Get the issued policy by id
    issued_policy = QueryBuilderService('crmp_issued_policies').where('id', id).first()
    if not issued_policy:
        return ResponseService.response("SUCCESS", {}, "issued_policy_not_found")
    policy_base_id = issued_policy.get('policy_base_id')
    if not policy_base_id:
        return ResponseService.response("SUCCESS", {}, "policy_base_id_not_found")

    # Step 2: Get the policy base to find insurer_id
    policy_base = QueryBuilderService('crmp_policy_base').where('id', policy_base_id).first()
    if not policy_base:
        return ResponseService.response("SUCCESS", {}, "policy_base_not_found")
    insurer_id = policy_base.get('insurer_id')
    if not insurer_id:
        return ResponseService.response("SUCCESS", {}, "insurer_id_not_found")

    # Step 3: Get the service provider (insurer)
    service_provider = QueryBuilderService('core_service_providers').where('id', insurer_id).first()
    if not service_provider:
        return ResponseService.response("SUCCESS", {}, "service_provider_not_found")

    # Step 4: Get the bank details for the service provider
    bank_details = QueryBuilderService('core_user_bank_details').where('service_provider_id', insurer_id).first()
    if not bank_details:
        return ResponseService.response("SUCCESS", {}, "bank_details_not_found")

    # Optionally, you can include some service provider info in the response
    result = {
        "payment_gateway_url":bank_details.get('payment_gateway_url',""),
        "bank_details": bank_details,
        "service_provider": {
            "id": service_provider.get('id'),
            "name": service_provider.get('name'),
            "email": service_provider.get('email'),
        }
    }
    return ResponseService.response("SUCCESS", result, "bank_info_retrieved")



@api_view(["GET"])
def policy_invoices(request, id):
    """
    Retrieve paginated invoice details for a given issued policy id (crmf_invoices.issued_policy_id).
    """
    try:
        # Query parameters for pagination and filtering
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "crmf_invoices.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filters", "{}")
        allowed_sorting_columns = [
            "crmf_invoices.id", "crmf_invoices.invoice_number", "crmf_invoices.invoice_date",
        ]

        # Select fields from crmf_invoices
        all_columns = [
            "crmf_invoices.*",
            "crmf_invoices.invoice_amount as total_amount"
        ]

        # Build the query
        query = (
            QueryBuilderService("crmf_invoices")
            .select(*all_columns)
            .where("crmf_invoices.issued_policy_id", id)
        )

        # Apply search, filters, and pagination
        data = query.apply_conditions(
            filter_json=filter_json,
            allowed_filters=[],
            search_string=search_string,
            search_columns=["crmf_invoices.invoice_number", "crmf_invoices.invoice_type"]
        ).paginate(
            page=page,
            limit=limit,
            allowed_sorting_columns=allowed_sorting_columns,
            sort_by=sort_by,
            sort_dir=sort_dir
        )

        if not data or (isinstance(data, dict) and not data.get("data")):
            return ResponseService.response("NOT_FOUND", {}, "invoices_not_found")

        return ResponseService.response("SUCCESS", data, "invoices_retrieved")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "error")


@api_view(["GET"])
def policy_based_settlement(request, id):
    try:
        # Define the columns you want to return
        all_columns = [
            "cp.id",
            "cp.customer_id",
            "ci.invoice_amount as total_amount",
            "cp.reference_id",
            "ci.invoice_number",
            "ci.invoice_type",
            "cp.paid_amount",
            "cp.outstanding_amount",
            "cp.receipt",
            "cp.receipt_name",
            "cp.receipt_type",
            "cp.status",
            "cp.created_at",
            "cp.updated_at",
            "cp.deleted_at",
            "cp.confirm_receipt",
            "cp.confirm_receipt_name",
            "cp.confirm_receipt_type",
            "cp.customer_payment_id",
            "cp.invoice_id",    
        ]

        # Pagination and sorting parameters
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "cp.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = [
            "cp.id", "cp.customer_id", "cp.invoice_id", "cp.paid_amount", "cp.outstanding_amount", "cp.status", "cp.created_at"
        ]

        # Query cus_payments
        cus_data = (
            QueryBuilderService("cus_payments as cp")
            .leftJoin("crmf_invoices as ci", "cp.invoice_id", "ci.id")
            .select(*all_columns)
            .where("ci.issued_policy_id", id)
            .whereNull("cp.deleted_at")
            .get()
        )
        print("cus_data",cus_data)
        cus_payments = cus_data if isinstance(cus_data, list) else cus_data.get("data", [])

        # Query crmf_payments
        crmf_columns = [
            "fp.id",
            "ci.invoice_amount as total_amount",
            "ci.invoice_number",
            "ci.invoice_type",
            "fp.paid_amount",
            "fp.outstanding_amount",
            "fp.receipt_number",
            "fp.receipt_number",
            "'pdf' as receipt_type",
            "null as confirm_receipt",
            "null as confirm_receipt_name",
            "null as confirm_receipt_type",
            "fp.customer_payment_id",
            "fp.invoice_id",
            "core_entity_docs.doc as receipt",
            "core_entity_docs.name as receipt_name",
            "core_entity_docs.type as receipt_type",
            "fp.confirmation_payment_receipt_name",
            "fp.confirmation_payment_receipt_type",
            "fp.confirmation_payment_receipt_url",
            "policy.invoice_document",
            "policy.invoice_document_name",
        ]
        crmf_data = (
            QueryBuilderService("crmf_payments as fp")
            .leftJoin("crmf_invoices as ci", "fp.invoice_id", "ci.id")
            .leftJoin("crmp_issued_policies as policy", "ci.issued_policy_id", "policy.id")
            .leftJoin("core_entity_docs", "fp.entity_id", "core_entity_docs.entity_id")
            .select(*crmf_columns)
            .where("ci.issued_policy_id", id)
            .get()
        )
        print("crmf_data",crmf_data)
        crmf_payments = crmf_data if isinstance(crmf_data, list) else crmf_data.get("data", [])

        # crmf_payments.customer_payment_id points to cus_payments.id (same payment).
        # Build set of those cus_payment ids so we don't return the same payment twice.
        cus_payment_ids_in_crmf = set(
            fp["customer_payment_id"] for fp in crmf_payments if fp.get("customer_payment_id")
        )

        # 1. Collect all possible keys from both sources
        all_keys = set()
        for rec in cus_payments + crmf_payments:
            all_keys.update(rec.keys())

        # 2. Include all crmf_payments
        merged = []
        for fp in crmf_payments:
            record = {k: fp.get(k, None) for k in all_keys}
            
            # Add confirmation_doc object
            record["confirmation_doc"] = {
                "name": fp.get("confirmation_payment_receipt_name"),
                "type": fp.get("confirmation_payment_receipt_type"),
                "url": fp.get("confirmation_payment_receipt_url")
            }
            
            # Add invoice_document object
            record["invoice_document"] = {
                "document": fp.get("invoice_document"),
                "name": fp.get("invoice_document_name")
            }
            
            merged.append(record)

        # 3. Include cus_payments only if this payment is NOT already in crmf_payments
        # (i.e. cus_payments.id must not be in crmf_payments.customer_payment_id)
        for cp in cus_payments:
            if cp.get("id") in cus_payment_ids_in_crmf:
                continue  # same payment already returned from crmf_payments
                record = {k: cp.get(k, None) for k in all_keys}
                
                # Add empty confirmation_doc object for cus_payments
                record["confirmation_doc"] = {
                    "name": None,
                    "type": None,
                    "url": None
                }
                
                # Add empty invoice_document object for cus_payments
                record["invoice_document"] = {
                    "document": None,
                    "name": None
                }
                
                merged.append(record)

        # 4. Sort and paginate as before
        merged.sort(key=lambda x: x.get("id", 0), reverse=True)

        # Pagination
        total_records = len(merged)
        last_page = (total_records + limit - 1) // limit
        start = (page - 1) * limit
        end = start + limit
        paginated = merged[start:end]

        data = {
            "total_records": total_records,
            "per_page": limit,
            "current_page": page,
            "last_page": last_page,
            "data": paginated
        }
        return ResponseService.response("SUCCESS", data, "Policy-based payment settlements fetched successfully!")
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


@api_view(["GET", "POST"])
def policy_settlement(request):
    if request.method == "GET":
        return get_policy_settlement(request)
    if request.method == "POST":
        return create_policy_settlement(request)


def get_policy_settlement(request):
    """
    Retrieve all policy settlements (payments) for the current customer (cus_payments by customer_id), paginated.
    """
    try:
        customer_id = request.user.get('id', 19)
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "cus_payments.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filters", "{}")
        allowed_sorting_columns = [
            "cus_payments.id", "cus_payments.invoice_id", "cus_payments.paid_amount",
            "cus_payments.outstanding_amount", "cus_payments.status", "cus_payments.created_at",
            "cus_payments.updated_at",
        ]
        all_columns = ["cus_payments.*","ci.invoice_number",
            "ci.invoice_type","ci.invoice_amount as total_amount"]
        query = (
            QueryBuilderService("cus_payments")
            .leftJoin("crmf_invoices as ci", "cus_payments.invoice_id", "ci.id")
            .select(*all_columns)
            .where("cus_payments.customer_id", customer_id)
        )
        data = query.apply_conditions(
            filter_json=filter_json,
            allowed_filters=[],
            search_string=search_string,
            search_columns=["cus_payments.reference_id", "cus_payments.status"]
        ).paginate(
            page=page,
            limit=limit,
            allowed_sorting_columns=allowed_sorting_columns,
            sort_by=sort_by,
            sort_dir=sort_dir
        )
        if not data or (isinstance(data, dict) and not data.get("data")):
            return ResponseService.response("NOT_FOUND", {}, "settlements_not_found")
        return ResponseService.response("SUCCESS", data, "settlements_retrieved")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "error")

def get_next_customer_payment_id():
    from envoy_bu_customer_api.customer.models.customer_payment import CustomerPayment
    last = CustomerPayment.objects.order_by('-customer_payment_id').first()
    return (last.customer_payment_id or 0) + 1 if last and last.customer_payment_id else 1


def _calculate_invoice_outstanding_amount(invoice_id):
    """
    Calculate outstanding amount for a specific invoice by summing all settlements
    from both cus_payments and crmf_payments for that invoice.
    Returns: (invoice_amount, total_paid, outstanding_amount)
    """
    try:
        # Get invoice details
        invoice = QueryBuilderService("crmf_invoices").select("invoice_amount").where("id", invoice_id).first()
        if not invoice:
            return (0, 0, 0)
        
        invoice_amount = float(invoice.get("invoice_amount") or 0)
        
        total_paid = 0
        
        # Sum from cus_payments (excluding deleted)
        cus_payments = QueryBuilderService("cus_payments").select("paid_amount").where("invoice_id", invoice_id).whereNull("deleted_at").get()
        if isinstance(cus_payments, list):
            for payment in cus_payments:
                total_paid += float(payment.get("paid_amount") or 0)
        elif isinstance(cus_payments, dict) and cus_payments.get("data"):
            for payment in cus_payments["data"]:
                total_paid += float(payment.get("paid_amount") or 0)
        
        # Sum from crmf_payments
        crmf_payments = QueryBuilderService("crmf_payments").select("paid_amount").where("invoice_id", invoice_id).get()
        if isinstance(crmf_payments, list):
            for payment in crmf_payments:
                total_paid += float(payment.get("paid_amount") or 0)
        elif isinstance(crmf_payments, dict) and crmf_payments.get("data"):
            for payment in crmf_payments["data"]:
                total_paid += float(payment.get("paid_amount") or 0)
        
        outstanding_amount = invoice_amount - total_paid
        return (invoice_amount, total_paid, outstanding_amount)
    except Exception as e:
        print(f"Error calculating invoice outstanding amount: {e}")
        return (0, 0, 0)

def create_policy_settlement(request):
    """
    Create a new policy settlement (payment) record in cus_payments. Expects required fields in request.data.
    """
    try:
        data = request.data
        
        # Get customer ID from user
        user = request.user
        if isinstance(user, dict):
            customer_id = user.get("id")
        else:
            customer_id = getattr(user, "id", None)
        
        if not customer_id:
            return ResponseService.response("UNAUTHORIZED", None, "Customer ID missing in token")
        
        # Validation rules for payment creation
        payment_rules = {
            "invoice_id": "required|integer|exists:crmf_invoices,id",
            "paid_amount": "required|numeric",
            "outstanding_amount": "required|numeric|min:0",
            "receipt": "required|string",
            "receipt_name": "nullable|string",
            "receipt_type": "nullable|string",
            "reference_id": "nullable|string",
            "policy_id": "nullable|integer|exists:crmp_issued_policies,id",
        }
        
        # Validate input data
        errors = ValidatorService.validate(data, payment_rules)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR",
                errors,
                "Validation Error"
            )
        
        # Get invoice details
        invoice_id = data.get("invoice_id")
        invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()
        
        if not invoice:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                "Invoice not found"
            )
        
        # Convert amounts to Decimal for accurate calculations
        paid_amount = Decimal(str(data["paid_amount"])).quantize(Decimal('.01'))
        invoice_amount = Decimal(str(invoice.get("invoice_amount", "0.00"))).quantize(Decimal('.01'))
        submitted_outstanding_amount = Decimal(str(data.get("outstanding_amount", "0.00"))).quantize(Decimal('.01'))
        
        # Validate submitted outstanding amount cannot be negative
        if submitted_outstanding_amount < 0:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "outstanding_amount": [
                        f"Outstanding amount cannot be negative ({submitted_outstanding_amount}). "
                        "If outstanding amount is negative, payment is not required."
                    ]
                },
                "Validation Error"
            )
        
        # Get cumulative paid so far for this invoice
        previous_total_row = QueryBuilderService("cus_payments")\
            .select("COALESCE(SUM(paid_amount), 0) as total_paid")\
            .where("invoice_id", invoice_id)\
            .whereNull("deleted_at")\
            .first()
        
        crmf_total_row = QueryBuilderService("crmf_payments")\
            .select("COALESCE(SUM(paid_amount), 0) as total_paid")\
            .where("invoice_id", invoice_id)\
            .first()
        
        previous_total_paid_cus = Decimal(str(previous_total_row.get("total_paid", "0.00"))) if previous_total_row else Decimal("0.00")
        previous_total_paid_crmf = Decimal(str(crmf_total_row.get("total_paid", "0.00"))) if crmf_total_row else Decimal("0.00")
        previous_total_paid = (previous_total_paid_cus + previous_total_paid_crmf).quantize(Decimal('.01'))
        
        # Remaining before this payment
        remaining_before = (invoice_amount - previous_total_paid).quantize(Decimal('.01'))
        
        # Validate outstanding amount is not negative or zero (no payment needed)
        if remaining_before < 0:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "outstanding_amount": [
                        f"Outstanding amount is negative ({remaining_before}). "
                        f"Invoice amount: {invoice_amount}, Already paid: {previous_total_paid}. "
                        "Payment is not required as the invoice is overpaid."
                    ]
                },
                "Validation Error"
            )
        
        if remaining_before == 0:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "outstanding_amount": [
                        f"Invoice is already fully paid. Outstanding amount is 0. "
                        f"Invoice amount: {invoice_amount}, Already paid: {previous_total_paid}. "
                        "No payment is required."
                    ]
                },
                "Validation Error"
            )
        
        # Validate payment amount against remaining using ValidatorService (lte:remaining)
        lte_rule_value = float(remaining_before)
        limit_rules = {
            "paid_amount": f"required|numeric|lte:{lte_rule_value}"
        }
        limit_errors = ValidatorService.validate({"paid_amount": float(paid_amount)}, limit_rules)
        if limit_errors:
            return ResponseService.response(
                "VALIDATION_ERROR",
                limit_errors,
                "Validation Error"
            )
        
        # Calculate cumulative outstanding after this payment
        new_outstanding_amount = (remaining_before - paid_amount).quantize(Decimal('.01'))
        
        customer_payment_id = get_next_customer_payment_id()
        # Use reference_id from request if provided, otherwise generate a unique one
        reference_id = data.get("reference_id") or str(uuid.uuid4())

        # Get payment PENDING status from core_status (module=payment, type=payment_pending)
        payment_status = (
            QueryBuilderService("core_status")
            .where("module", "payment")
            .where("type", "payment_pending")
            .select("id", "name")
            .first()
        )
        if not payment_status:
            return ResponseService.response(
                "NOT_FOUND",
                {"error": "Payment PENDING status not found in core_status table (module=payment, type=payment_pending)."},
                "status_not_found"
            )

        payment_data = {
            "customer_id": customer_id,
            "reference_id": reference_id,
            "invoice_id": int(invoice_id),
            "paid_amount": str(paid_amount),
            "outstanding_amount": str(new_outstanding_amount),  # Use calculated outstanding amount after payment
            "receipt": data.get("receipt"),
            "receipt_name": data.get("receipt_name"),
            "receipt_type": data.get("receipt_type"),
            "status_id": payment_status.get("id"),
            "status": payment_status.get("name"),
            "created_at": timezone.now(),
            "updated_at": timezone.now(),
            "deleted_at": None,
            "customer_payment_id": customer_payment_id
        }
        if data.get("policy_id") is not None:
            payment_data["policy_id"] = int(data["policy_id"])
        print(payment_data)
        result = QueryBuilderService("cus_payments").insert(payment_data)
        if not result:
            return ResponseService.response("INTERNAL_SERVER_ERROR", {}, "Payment not recorded")
        
        # NotificationService call (safe, does not affect main flow)
        try:
            NotificationService.generate_notification(
                type_code="policy",  # Example notification type code
                title="Payment Confirmation Request",
                meta_data={"payment_id": result.get("id"), "amount": data.get("paid_amount"),"invoice_id":data.get('invoice_id')},
                message=f"Payment of amount {data.get('paid_amount')} paid for invoice {data.get('invoice_id')}",
                customer_id=customer_id
            )
        except Exception as notify_exc:
            print(f"NotificationService error: {notify_exc}")

        return ResponseService.response("SUCCESS", {"payment_id": result}, "Payment recorded successfully")
    except Exception as e:
        # Check for duplicate entry error and return a validation error
        if "Duplicate entry" in str(e) and "reference_id" in str(e):
            return ResponseService.response("VALIDATION_ERROR", {"reference_id": ["Reference ID already exists."]}, "Validation Error")
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "error")


@api_view(["PUT"])
def get_single_generate_document_confirm(request, vendor_quotation_id):
    """
    Confirm a sent quotation by setting its status to 'confirmed', if not already confirmed.
    """
    # Check if the record exists
    record = QueryBuilderService("crmq_quotation_service_providers").where("id", vendor_quotation_id).first()
    if not record:
        return ResponseService.response(
            "NOT_FOUND",
            {"error": "No sent quotation found with this id."},
            "not_found"
        )
    if record.get("status") == "confirmed":
        return ResponseService.response(
            "NOT_FOUND",
            {"error": "This quotation is already confirmed."},
            "already_confirmed"
        )

    # Get the quotation_id from the current record to find related quotations
    quotation_id = record.get("quotation_id")
    
   
    # Get the accepted status ID
    accepted_status_id = (
        QueryBuilderService("core_status")
        .where("type", "quotation_confirmed")
        .where("module", "quotation")
        .select("id","name")
        .first()
    )

    if not accepted_status_id:
        return ResponseService.response(
            "NOT_FOUND",
            {"error": "Confirmed status not found in core_status table."},
            "status_not_found"
        )

    # Get the rejected status ID
    rejected_status_id = (
        QueryBuilderService("core_status")
        .where("type", "quotation_rejected")
        .where("module", "quotation")
        .select("id","name")
        .first()
    )

    if not rejected_status_id:
        return ResponseService.response(
            "NOT_FOUND",
            {"error": "Rejected status not found in core_status table."},
            "status_not_found"
        )

    # Update the confirmed quotation in crmq_vendor_response table
    QueryBuilderService("crmq_vendor_response")\
        .where("quotation_id", quotation_id)\
        .where("vendor_quotation_id", vendor_quotation_id)\
        .update({"status": accepted_status_id["name"]})

    # Update all other related quotations to rejected status in crmq_vendor_response table
    QueryBuilderService("crmq_vendor_response")\
        .where("quotation_id", quotation_id)\
        .whereNotIn("vendor_quotation_id", [vendor_quotation_id])\
        .update({"status": rejected_status_id["name"]})

    # Update the confirmed quotation
    QueryBuilderService("crmq_quotation_service_providers").where("id", vendor_quotation_id).update({
        "status": accepted_status_id.get("id")
    })

    # Update all other related quotations to rejected status
    QueryBuilderService("crmq_quotation_service_providers").where("quotation_id", quotation_id).whereNotIn("id", [vendor_quotation_id]).update({
        "status": rejected_status_id.get("id")
    })

    # Update the main quotation record in crmq_quotations table
    QueryBuilderService("crmq_quotations").where("id", quotation_id).update({
        "status_id": accepted_status_id.get("id"),
        "status": accepted_status_id.get("name")
    })

    return ResponseService.response(
        "SUCCESS",
        {"id": vendor_quotation_id, "status": "confirmed"},
        "quotation_confirmed"
    )

@api_view(["GET"])
def get_myself(request):
    try:
        user = request.user
        customer = user.get('id', None)

        # Step 2: Build query with LEFT JOIN to fetch contact details
        result = QueryBuilderService("core_customers as cu") \
            .select(
                "cu.*",
                "co.primary_contact as phone_number",
                "co.email as email",
                "co.address as address",
                # "co.contact_method as contact_method"
            ) \
            .leftJoin("core_contacts as co", "co.id", "cu.primary_contact_id") \
            .where("cu.id", customer) \
            .first()

        if not result:
            return ResponseService.response("NOT_FOUND", None, "Customer not found")

        return ResponseService.response("SUCCESS", result, "Customer profile fetched successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
    

@api_view(["GET"])
def login_history(request):
    if request.method == "GET":
        return get_login_history(request)
    # elif request.method == "DELETE":
    #     return delete_login_history(request ,id)
    # else:
    #     return ResponseService.response("METHOD_NOT_ALLOWED", None, "Method not allowed.")

def get_login_history(request):
    user = request.user
    customer_id = user.get('id', 1)
    print(customer_id)

    filter_param = request.GET.get("filter", {})
    
    # Handle filter parameter - if it's a string, convert to proper format
    if isinstance(filter_param, str):
        if filter_param.strip() == "":
            filter_json = {}
        else:
            # If it's a simple string like "shortlisted", wrap it in a dict
            filter_json = {"status": filter_param}
    else:
        filter_json = filter_param
        
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_login_histories.id")
    sort_dir = request.GET.get("sort_dir", "desc")
    allowed_sorting_columns = ["core_login_histories.id"]

    # Find the last login id for this customer
    last_login = QueryBuilderService('core_login_histories') \
        .where('customer_id', customer_id) \
        .where('module', "customer") \
        .whereNull('deleted_at') \
        .orderBy('id', 'desc') \
        .first()
    last_login_id = last_login['id'] if last_login else None

    data = (
        QueryBuilderService('core_login_histories')
        .where('customer_id', customer_id)
        .where('module', "customer")
        .whereNull('deleted_at')
        .orderBy('created_at', 'desc')
        .apply_conditions(
                filter_json=filter_json,
                allowed_filters=[],
                search_string=search_string,
                search_columns=["core_login_histories.id"]
            )
        .paginate(
                page=page,
                limit=limit,
                allowed_sorting_columns=allowed_sorting_columns,
                sort_by=sort_by,
                sort_dir=sort_dir
            )
    )

    # Add status field: record with last_login_id is 'active', others are 'inactive'
    login_data = data.get('data', []) if isinstance(data, dict) else data
    for record in login_data:
        record['status'] = 'active' if record['id'] == last_login_id else 'inactive'

    # Build the required response format
    result = {
        "total_records": data.get('total_records', len(login_data)),
        "per_page": data.get('per_page', limit),
        "current_page": data.get('current_page', page),
        "last_page": data.get('last_page', 1),
        "data": login_data
    }
    return Response({
        "is_success": True,
        "message": "Customer login history fetched successfully.",
        "result": result
    })

@api_view(["DELETE"])
def login_history_details(request,id):
    user = request.user
    customer_id = user.get('id', 1)
    print(customer_id)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    record = QueryBuilderService('core_login_histories') \
        .where('customer_id', customer_id) \
        .where('module', "customer") \
        .whereNull('deleted_at') \
        .where('id', id) \
        .first()

    if not record:
        return ResponseService.response("NOT_FOUND", None, "Login history record not found.")

    result = QueryBuilderService('core_login_histories') \
        .where('id', id) \
        .update({'deleted_at': now})

    if result:
        return ResponseService.response("SUCCESS", None, "Customer login history deleted successfully.")
    else:
        return ResponseService.response("NOT_FOUND", None, "Failed to update login history.")



@api_view(["GET", "PUT"])
def notification_settings(request):
    if request.method == "GET":
        return get_notification_settings(request)
    if request.method == "PUT":
        return update_notification_settings(request)

def get_notification_settings(request):
    user = request.user
    customer_id = user.get('id', 1)
    settings = (
        QueryBuilderService("cus_settings as cs")
        .leftJoin("core_setting_keys as sk", "cs.setting_key", "sk.id")
        .select("cs.setting_key", "cs.value", "sk.attribute_name")
        .where("cs.customer_id", customer_id)
        .get()
    )
    # Transform to {name: value}
    result_dict = {item["attribute_name"]: item["value"] for item in settings}
    return Response({
        "is_success": True,
        "message": "Notification settings fetched successfully.",
        "result": result_dict
    })

def update_notification_settings(request):
    user = request.user
    customer_id = user.get('id', 1)# Adjust as needed
    updates = request.data  # Expecting a dict as shown above

    rules = {
  "policy_lifecycle_notifications": "required",
  "payments_and_reminders": "required",
  "account_and_security": "required",
  "promotions_and_updates": "required"
}
    errors = ValidatorService.validate(updates,rules ,)
    if errors:
     return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )

    for key_name, value in updates.items():
        # 1. Find the setting key id
        setting_key_row = (
            QueryBuilderService("core_setting_keys")
            .select("id")
            .where("attribute_name", key_name)
            .first()
        )
        if not setting_key_row:
            continue  # Skip if the key is not found

        setting_key_id = setting_key_row["id"]

        # 2. Check if a cus_settings row exists for this customer and setting_key_id
        existing = (
            QueryBuilderService("cus_settings")
            .select("id")
            .where("customer_id", customer_id)
            .where("setting_key", setting_key_id)
            .first()
        )
        if existing:
            # Update
            QueryBuilderService("cus_settings")\
                .where("id", existing["id"])\
                .update({"value": value})
        else:
            # Insert
            QueryBuilderService("cus_settings")\
                .insert({
                    "customer_id": customer_id,
                    "setting_key": setting_key_id,
                    "value": value
                })

    return Response({
        "is_success": True,
        "message": "updated_successfully"
        # "message": "Notification settings updated successfully."
    })




