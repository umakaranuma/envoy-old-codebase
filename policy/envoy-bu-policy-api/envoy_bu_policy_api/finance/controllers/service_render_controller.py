from urllib import request
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.db import transaction
import datetime
from mServices import ResponseService, QueryBuilderService, ValidatorService
from envoy_bu_policy_api.finance.models.crmf_commision_setup import CommissionSetup
from envoy_bu_policy_api.finance.models.crmf_commission_filed import CommissionFiled
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from envoy_bu_policy_api.service import handle_entity, handle_entity_notes, handle_entity_docs
from envoy_bu_policy_api.finance.controllers.utils.invoice_utils import generate_invoice_id
from envoy_bu_policy_api.finance.controllers.utils.service_render_journal_utils import (
    create_service_render_journal_entries,
    create_service_render_payment_journal_entries
)
from envoy_bu_policy_api.finance.controllers.utils.general_ledger_utils import create_service_render_general_ledger
from decimal import Decimal
from types import SimpleNamespace
from django.utils import timezone


@csrf_exempt
@api_view(['GET', 'POST'])
def service_render(request):
    if request.method == 'GET':
        return get_service_render(request, id=None)
    if request.method == 'POST':
        return store_service_render(request)

def get_service_render(request, id=None):
    try:
        all_columns = [
            "crmf_services_renders.*",
            "core_users.display_name as created_by_name",
            "users.display_name as user_name",
            "core_status_invoice.name as invoice_status_name",
            "core_status_invoice.color as invoice_status_color",
            "core_status_payment.name as payment_status_name",
            "core_status_payment.color as payment_status_color",
            "core_services.title as service_title",
            "core_entities.created_at",
            "core_customers.name as customer_name",
        ]

        # Initialize base query
        query = (
            QueryBuilderService("crmf_services_renders")
            .select(*all_columns)
            .leftJoin(
                "core_entities",
                "crmf_services_renders.entity_id",
                "core_entities.id"
            )
            .leftJoin(
                "core_users",
                "core_entities.created_by_id",
                "core_users.id"
            )
            .leftJoin(
                "core_users as users",
                "crmf_services_renders.user_id",
                "users.id"
            )    
            .leftJoin(
                "core_status as core_status_invoice",
                "crmf_services_renders.invoice_status",
                "core_status_invoice.id"
            )
            .leftJoin(
                "core_status as core_status_payment",
                "crmf_services_renders.payment_status",
                "core_status_payment.id"
            )
            .leftJoin(
                "core_services",
                "crmf_services_renders.service_id",
                "core_services.id"
            )
            .leftJoin(
                "core_customers",
                "crmf_services_renders.customer_id",
                "core_customers.id"
            )
        )

        if id:
            # Get single record
            service_render = query.where("crmf_services_renders.id", id).first()
            if not service_render:
                return ResponseService.response(
                    "NOT_FOUND", 
                    {}, 
                    "Service render record not found"
                )
            
            # Get total paid amount from all payments
            total_paid = QueryBuilderService("crmf_service_render_payments")\
                .select("SUM(paid_amount) as total_paid")\
                .where("service_render_id", id)\
                .first()
            
            total_paid_amount = Decimal(str(total_paid.get('total_paid', 0) or 0))
            service_fee = Decimal(str(service_render.get('fee', 0)))
            outstanding_amount = service_fee - total_paid_amount
            
            # Add outstanding amount to service render data
            service_render['outstanding_amount'] = str(outstanding_amount)
            service_render['total_paid'] = str(total_paid_amount)

            return ResponseService.response(
                "SUCCESS",
                service_render,
                "Service render record retrieved successfully"
            )
        else:
            # Get list with pagination and filters
            filter_json = request.GET.get("filter", {})
            search_string = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            sort_by = request.GET.get("sort_by" )
            sort_dir = request.GET.get("sort_dir")
            sort_by = "crmf_services_renders.id" if sort_by in [None, ""] else sort_by
            sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

            allowed_filters = [
                "crmf_services_renders.invoice_status",
                "crmf_services_renders.payment_status",
                "crmf_services_renders.service_id",
                "crmf_services_renders.customer_id",
                "crmf_services_renders.invoice_number"
            ]
            
            search_columns = [

                "core_services.title",
                "crmf_services_renders.invoice_number",
                "core_customers.name"
            ]

            allowed_sorting_columns = [

                "crmf_services_renders.service_date",
                "core_services.title",
                "crmf_services_renders.invoice_number",
                "core_customers.name"
            ]

            data = (query
                .apply_conditions(
                    filter_json=filter_json,
                    allowed_filters=allowed_filters,
                    search_string=search_string,
                    search_columns=search_columns
                )
                .paginate(
                    page=page,
                    limit=limit,
                    allowed_sorting_columns=allowed_sorting_columns,
                    sort_by=sort_by,
                    sort_dir=sort_dir
                )
            )

            return ResponseService.response(
                "SUCCESS",
                data,
                "Service render records retrieved successfully"
            )

    except Exception as e:
        return ResponseService.response( "NOT_FOUND", {}, f"Error retrieving service render records: {str(e)}")


def store_service_render(request,id=None):
    try:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response(
                "VALIDATION_ERROR", {"request": ["Invalid JSON format"]}, "validation_error"
            )

        rules = {
            "service_id": "integer|required|exists:core_services,id",
            "service_date": "required",
            "fee": "required|numeric",
            "invoice_status": "required",
            "payment_status": "required|exists:core_status,id",
            "customer_id": "required|integer|exists:core_customers,id",
            "remarks": "string|max:500",
            "user_id" :"required|integer|exists:core_users,id"
        }

        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "validation_error")

        try:
            service_date = datetime.datetime.strptime(data["service_date"], "%m/%d/%Y").date()
        except ValueError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"service_date": ["Invalid date format. Use MM/DD/YYYY"]},
                "validation_error"
            )

        # Check if this is an update operation
        is_update = hasattr(request, 'id') and request.id is not None
        
        if is_update:
            # Verify the record exists
            existing_record = QueryBuilderService("crmf_services_renders").where("id", request.id).first()
            if not existing_record:
                return ResponseService.response(
                    "NOT_FOUND", {}, "Service render record not found"
                )
            
            # Update the record
            update_data = {
                "service_id": int(data["service_id"]),
                "service_date": service_date.strftime("%Y-%m-%d"),
                "fee": float(data["fee"]),
                "invoice_status": int(data["invoice_status"]),
                "payment_status": int(data["payment_status"]),
                "customer_id": int(data["customer_id"]),
                "remarks": str(data.get("remarks", "")).strip(),
                "user_id": int(data["user_id"])
            }
            
            update_result = QueryBuilderService("crmf_services_renders") \
                .where("id", request.id) \
                .update(update_data)
                
            if not update_result:
                return ResponseService.response(
                    "NOT_FOUND", {}, "Failed to update service render record"
                )
                
            return ResponseService.response(
                "SUCCESS", 
                {"id": request.id}, 
                "default_update_success_msg"
            )
        else:
            # Create new record
            entity_data = {"type": "service_render", "approvel_status": False}
            entity_id = handle_entity(entity_data, entity_id=None, user=request.user)
            
            # Create service render record
            insert_data = {
                "service_id": int(data["service_id"]),
                "service_date": service_date.strftime("%Y-%m-%d"),
                "fee": float(data["fee"]),
                "invoice_status": int(data["invoice_status"]),
                "payment_status": int(data["payment_status"]),
                "customer_id": int(data["customer_id"]),
                "remarks": str(data.get("remarks", "")).strip(),
                "entity_id": int(entity_id),
                "user_id": int(data["user_id"])
            }

            result = QueryBuilderService("crmf_services_renders").insert(insert_data)
            
            if not result or not isinstance(result, dict) or 'id' not in result:
                return ResponseService.response(
                    "NOT_FOUND", {}, "Failed to create service render record"
                )

            # Generate invoice number based on ID
            service_render_id = result['id']
            invoice_number = f"INV-SER-{str(service_render_id).zfill(3)}"

            # Update the record with generated invoice number
            update_result = QueryBuilderService("crmf_services_renders")\
                .where("id", service_render_id)\
                .update({"invoice_number": invoice_number})

            if not update_result:
                return ResponseService.response(
                    "NOT_FOUND", {}, "Failed to update invoice number"
                )

            # Create journal entries for service render
            service_render = QueryBuilderService("crmf_services_renders").where("id", service_render_id).first()
            if service_render:
                create_service_render_journal_entries(service_render, user=request.user)

            return ResponseService.response(
                "SUCCESS", 
                {
                    "id": service_render_id,
                    "invoice_number": invoice_number
                }, 
                "default_create_success_msg"
            )

    except Exception as e:
        return ResponseService.response(
            "NOT_FOUND", {"error": str(e)}, "An error occurred while processing the service render record"
        )




@csrf_exempt
@api_view(["GET"])
def payment_status(request):
    try:
        all_columns = [
            "core_status.*"
        ]

        # Get list with pagination and filters
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "core_status.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_filters = [
            "core_status.name",
            "core_status.type",
        ]
        
        search_columns = [
            "core_status.name",
            "core_status.type",
        ]

        allowed_sorting_columns = [
            "core_status.name",
            "core_status.type",
            "core_status.id",
        ]
        
        status = (
            QueryBuilderService("core_status")
            .select(*all_columns)
            .where("core_status.module", "payment")
            .whereNotIn("core_status.type", ["payment_refunded", "payment_failed"])
            .apply_conditions(
                filter_json=filter_json,
                allowed_filters=allowed_filters,
                search_string=search_string,
                search_columns=search_columns
            )
            .paginate(
                page=page,
                limit=limit,
                allowed_sorting_columns=allowed_sorting_columns,
                sort_by=sort_by,
                sort_dir=sort_dir
            )
        )

        # Logic to get payment status
        return ResponseService.response(
            "SUCCESS", status, "Payment status retrieved successfully"
        )
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {}, f"Error retrieving payment status: {str(e)}")

@csrf_exempt
@api_view(["GET"])
def invoice_status(request):
    try:
        all_columns = [
            "core_status.*"
        ]

        # Get list with pagination and filters
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "core_status.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_filters = [
            "core_status.name",
            "core_status.type",
        ]
        
        search_columns = [
            "core_status.name",
            "core_status.type",
        ]

        allowed_sorting_columns = [
            "core_status.name",
            "core_status.type",
            "core_status.id",
        ]
        
        status = (
            QueryBuilderService("core_status")
            .select(*all_columns)
            .where("core_status.module", "invoice")
            .apply_conditions(
                filter_json=filter_json,
                allowed_filters=allowed_filters,
                search_string=search_string,
                search_columns=search_columns
            )
            .paginate(
                page=page,
                limit=limit,
                allowed_sorting_columns=allowed_sorting_columns,
                sort_by=sort_by,
                sort_dir=sort_dir
            )
        )

        # Logic to get payment status
        return ResponseService.response(
            "SUCCESS", status, "Payment status retrieved successfully"
        )
    except Exception as e:
            return ResponseService.response("NOT_FOUND", {}, f"Error retrieving invoice status: {str(e)}")        


@csrf_exempt
@api_view(["GET","PUT","DELETE"])
def service_render_details(request, id):
    if request.method == 'GET':
        return get_service_render(request, id)
    if request.method == 'PUT':
        # Add id to request object for store_service_render to use
        request.id = id
        return store_service_render(request,id)
    if request.method == 'DELETE':
        service_render = QueryBuilderService("crmf_services_renders").where("id", id).first()
        if not service_render:
            return ResponseService.response("NOT_FOUND", [], "NOT_FOUND")
        
        QueryBuilderService("crmf_services_renders").where("id", id).delete()
        return ResponseService.response("SUCCESS", [], "default_delete_success_msg")


@csrf_exempt
@api_view(["GET"])
def get_fee(request, id):
    service = QueryBuilderService("core_services").where("id", id).first()

    if not service:
        return ResponseService.response("NOT_FOUND", [], "not_found")
    
    data = QueryBuilderService("core_services").where("id", id).select("core_services.fee").get()
    return ResponseService.response("SUCCESS", data, "data_get")

@csrf_exempt
@api_view(["GET"])
def get_services(request):

      filter_json = request.GET.get("filter", {})
      search_string = request.GET.get("search", "")
      page = int(request.GET.get("page", 1))
      limit = int(request.GET.get("limit", 10))
      sort_by = request.GET.get("sort_by", "core_services.id")
      sort_dir = request.GET.get("sort_dir", "desc")

      allowed_filters = [
         "core_services.title"
      ]
      
      search_columns = [
         
          "core_services.title"
      ]

      allowed_sorting_columns = [
          "core_services.title"
      ]

      service = (
          QueryBuilderService("core_services").select("core_services.*")
          .apply_conditions(
                filter_json=filter_json,
                    allowed_filters=allowed_filters,
                    search_string=search_string,
                    search_columns=search_columns
                )
                .paginate(
                    page=page,
                    limit=limit,
                    allowed_sorting_columns=allowed_sorting_columns,
                    sort_by=sort_by,
                    sort_dir=sort_dir
                )
      )
      return ResponseService.response("SUCCESS", service, "data_get")


@csrf_exempt
@api_view(["GET","POST"])
def service_render_payment(request, id=None):
    if request.method == 'GET':
        return get_service_render_payment(request, id)
    if request.method == 'POST':
        return store_service_render_payment(request, id)

        # try:
        #     data = json.loads(request.body)
            
        #     print("nnnnnnnnnn")
        #     # Get service render
        #     service_render = QueryBuilderService("crmf_services_renders").where("id", id).first()
        #     if not service_render:
        #         return ResponseService.response("NOT_FOUND", "Service render not found", Error.NOT_FOUND)
               
        #     rules = {
        #         "paid_amount": "required",
        #         "created_by": "required",
        #         "created_at": "required",
        #         "payment_receipt_name": "required",
        #         "payment_receipt_url": "required",
        #         "payment_receipt_type": "required",
        #         "service_render_id": "required",
        #         "remarks": "optional"
        #     }

        #     print("nnnnnnnnn2")
        #     # Create entity for payment
        #     entity_data = {
        #         "type": "service_render_payment",
        #         "approvel_status": False
        #     }
        #     print("nnnnnnnnn3")
        #     entity_id = handle_entity(entity_data, user=request.user if hasattr(request, 'user') else None)
            
        #     # Calculate outstanding amount
        #     paid_amount = Decimal(str(data.get("paid_amount", "0.00")))
        #     fee = Decimal(str(service_render.get("fee", "0.00")))
        #     outstanding_amount = fee - paid_amount
            
        #     # Prepare payment data with only the required fields
        #     payment_data = {
        #         "service_render_id": id,
        #         "paid_amount": paid_amount,
        #         "outstanding_amount": outstanding_amount,
        #         "entity_id": entity_id,
        #         "method": "bank_transfer"
        #     }
            
        #     # Insert payment
        #     payment_id = QueryBuilderService("crmf_service_render_payments").insert(payment_data)
        #     if not payment_id:
        #         return ResponseService.response("NOT_FOUND", "Failed to create payment record", Error.NOT_FOUND)
        #     print("nnnnnnnnn4")
 
        #     # Get created payment
        #     payment = QueryBuilderService("crmf_service_render_payments").where("id", payment_id).first()
            
        #     # Handle optional notes
        #     if "remarks" in data:
        #         handle_entity_notes(entity_id, [{
        #             "note": data["remarks"],
        #             "created_by_id": data.get("created_by"),
        #             "created_at": data.get("created_at")
        #         }], is_update=False)
            
        #     # Handle receipt document
        #     if "payment_receipt_url" in data:
        #         receipt = {
        #             "doc": data["payment_receipt_url"],
        #             "name": data.get("payment_receipt_name", ""),
        #             "type": data.get("payment_receipt_type", "")
        #         }
        #         handle_entity_docs(entity_id=entity_id, docs=[receipt])
            
        #     print(".........", service_render=service_render,
        #         payment_amount=paid_amount,
        #         user=request.user)
        #     # Create journal entries
        #     create_service_render_payment_journal_entries(
        #         service_render=service_render,
        #         payment_amount=paid_amount,
        #         user=request.user
        #     )
        #     print("nnnnnnnnny")

        #     # Create general ledger entry
        #     create_service_render_general_ledger(
        #         service_render=service_render,
        #         payment_amount=paid_amount,
        #         user=request.user
        #     )
        #     print("nnnnnnnnnZ")
            
        #     # Update service render payment status if fully paid
        #     if outstanding_amount == 0:
        #         QueryBuilderService("crmf_services_renders")\
        #             .where("id", id)\
        #             .update({"payment_status": 2})  # Assuming 2 is the status ID for paid
            
        #     return ResponseService.response("SUCCESS", {
        #         "payment": payment,
        #         "service_render": service_render
        #     }, Message.DATA_CREATED)
            
        # except Exception as e:
        #     return ResponseService.response("NOT_FOUND", str(e), Error.NOT_FOUND)

def get_service_render_payment(request,id=None,payment_id=None):
    try:
        all_columns = [
            "crmf_service_render_payments.*",
            "core_entities.created_at",
            "core_entities.created_by_id",
            "core_users.display_name",
            """(
                SELECT doc 
                FROM core_entity_docs 
                WHERE core_entity_docs.entity_id = crmf_service_render_payments.entity_id 
                LIMIT 1
            ) as receipt_url""",
            """(
                SELECT name 
                FROM core_entity_docs 
                WHERE core_entity_docs.entity_id = crmf_service_render_payments.entity_id 
                LIMIT 1
            ) as receipt_name""",
            """(
                SELECT type 
                FROM core_entity_docs 
                WHERE core_entity_docs.entity_id = crmf_service_render_payments.entity_id 
                LIMIT 1
            ) as receipt_type"""
        ]

        # Base query for data
        data_query = (
            QueryBuilderService("crmf_service_render_payments")
            .select(*all_columns)
            .leftJoin(
                "core_entities",
                "crmf_service_render_payments.entity_id",
                "core_entities.id"
            )
            .leftJoin(
                "core_users",
                "core_entities.created_by_id",
                "core_users.id"
            )
        )

        # Separate count query
        count_query = (
            QueryBuilderService("crmf_service_render_payments")
            .select("COUNT(*) as total")
            .leftJoin(
                "core_entities",
                "crmf_service_render_payments.entity_id",
                "core_entities.id"
            )
            .leftJoin(
                "core_users",
                "core_entities.created_by_id",
                "core_users.id"
            )
        )
        
        if id:
            data_query.where("crmf_service_render_payments.service_render_id", id)
            count_query.where("crmf_service_render_payments.service_render_id", id)
            
        if payment_id:
            data_query.where("crmf_service_render_payments.id", payment_id)
            count_query.where("crmf_service_render_payments.id", payment_id)
            
        # Get list with pagination and filters
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "crmf_service_render_payments.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_filters = [
            "crmf_service_render_payments.service_render_id",
            "crmf_service_render_payments.paid_amount",
            "core_entities.created_at"
        ]
        
        search_columns = [
            "crmf_service_render_payments.service_render_id",
            "crmf_service_render_payments.paid_amount",
            "core_users.display_name"
        ]

        allowed_sorting_columns = [
            "crmf_service_render_payments.id",
            "crmf_service_render_payments.paid_amount",
            "core_entities.created_at",
            "core_users.display_name"
        ]

        # Apply conditions to both queries
        data_query = data_query.apply_conditions(
            filter_json=filter_json,
            allowed_filters=allowed_filters,
            search_string=search_string,
            search_columns=search_columns
        )
        
        count_query = count_query.apply_conditions(
            filter_json=filter_json,
            allowed_filters=allowed_filters,
            search_string=search_string,
            search_columns=search_columns
        )

        # Get total count
        total_count = count_query.first().get('total', 0)

        # Get paginated results
        results = data_query.paginate(
            page=page,
            limit=limit,
            allowed_sorting_columns=allowed_sorting_columns,
            sort_by=sort_by,
            sort_dir=sort_dir
        )

        # Format response to match desired structure
        formatted_response = {
            "total_records": total_count,
            "per_page": limit,
            "current_page": page,
            "last_page": (total_count + limit - 1) // limit,
            "data": results.get('data', [])
        }
        
        return ResponseService.response("SUCCESS", formatted_response, "data_get")
    except Exception as e:
        return ResponseService.response(
            "NOT_FOUND",
            str(e),
            "Error.INTERNAL_SERVER_ERROR"
        )

def store_service_render_payment(request,id=None):
    try:
        data = json.loads(request.body or "{}")
        user = request.user if request.user.is_authenticated else None

        # Validation rules for payment creation
        payment_rules = {
            "paid_amount": "required|numeric",
            "created_by": "required|integer|exists:core_users,id",
            "created_at": "required",
            "payment_receipt_name": "required|string",
            "payment_receipt_url": "required|string",
            "payment_receipt_type": "required",
            "service_render_id": "required|integer|exists:crmf_services_renders,id",
        }

        # Validate input data
        errors = ValidatorService.validate(data, payment_rules)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR",
                errors,
                Error.VALIDATION_ERROR,
                'VALIDATION_ERROR'
            )

        # Get service render details
        service_render = QueryBuilderService("crmf_services_renders")\
            .where("id", data["service_render_id"])\
            .first()

        if not service_render:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                "Service render not found"
            )

        # Convert amounts to Decimal for accurate calculations
        paid_amount = Decimal(str(data["paid_amount"])).quantize(Decimal('.01'))
        fee = Decimal(str(service_render.get("fee", "0.00")))

        # Get cumulative paid so far for this service_render
        previous_total_row = QueryBuilderService("crmf_service_render_payments")\
            .select("COALESCE(SUM(paid_amount), 0) as total_paid")\
            .where("service_render_id", data["service_render_id"])\
            .first()
        previous_total_paid = Decimal(str(previous_total_row.get("total_paid", "0.00"))) if previous_total_row else Decimal("0.00")

        # Remaining before this payment
        remaining_before = (fee - previous_total_paid).quantize(Decimal('.01'))

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
                "validation_error",
                'VALIDATION_ERROR'
            )

        # Calculate cumulative outstanding after this payment
        new_outstanding = (remaining_before - paid_amount).quantize(Decimal('.01'))

        # Prepare base entity info
        entity_data = {
            "type": "payment",
            "approvel_status": False,
            "description": "Service render payment creation",
        }
        user_obj = SimpleNamespace(id=data["created_by"])

        # Create entity
        entity_id = handle_entity(
            entity_data,
            entity_id=None,
            user=user_obj,
            created_at=data["created_at"],
        )

        # Prepare payment data
        payment_data = {
            "service_render_id": int(data["service_render_id"]),
            "paid_amount": str(paid_amount),
            "outstanding_amount": str(new_outstanding),
            "entity_id": entity_id,
            "created_by": data["created_by"],
            "created_at": data["created_at"],
            "updated_by": data["created_by"],
            "updated_at": data["created_at"]
        }

        # Insert payment
        created_payment = QueryBuilderService("crmf_service_render_payments").insert(payment_data)

        if not created_payment or not isinstance(created_payment, dict) or 'id' not in created_payment:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                "Failed to create payment record"
            )

        # Handle optional notes
        if "remarks" in data:
            handle_entity_notes(entity_id, [{
                "note": data["remarks"],
                "created_by_id": request.user.id if request.user.is_authenticated else None,
                "created_at": datetime.datetime.now()
            }], is_update=False)

        # Handle attached receipt document
        receipt = None
        if "upload_receipt" in data:
            receipt = data["upload_receipt"]
        elif "payment_receipt_url" in data:
            receipt = {
                "doc": data["payment_receipt_url"],
                "name": data.get("payment_receipt_name", ""),
                "type": data.get("payment_receipt_type", "")
            }

        if receipt and receipt.get("doc"):
            handle_entity_docs(entity_id=entity_id, docs=[receipt])

        # Create journal entries for service render payment
        create_service_render_payment_journal_entries(service_render, paid_amount, user=request.user)

        # Recalculate cumulative paid and update payment_status accordingly
        total_paid_row = QueryBuilderService("crmf_service_render_payments")\
            .select("COALESCE(SUM(paid_amount), 0) as total_paid")\
            .where("service_render_id", data["service_render_id"])\
            .first()
        total_paid_cumulative = Decimal(str(total_paid_row.get("total_paid", "0.00"))) if total_paid_row else paid_amount
        fee_amount = Decimal(str(service_render.get("fee", "0.00")))
        cumulative_outstanding = (fee_amount - total_paid_cumulative).quantize(Decimal('.01'))

        # Resolve status IDs dynamically from core_status using immutable type+module
        paid_status = QueryBuilderService("core_status")\
            .select("id")\
            .where("module", "payment")\
            .where("type", "payment_paid")\
            .first()
        partial_status = QueryBuilderService("core_status")\
            .select("id")\
            .where("module", "payment")\
            .where("type", "pay_partially_paid")\
            .first()
        pending_status = QueryBuilderService("core_status")\
            .select("id")\
            .where("module", "payment")\
            .where("type", "payment_pending")\
            .first()

        new_status_id = None
        if cumulative_outstanding <= Decimal("0.00"):
            new_status_id = (paid_status or {}).get("id")
        elif total_paid_cumulative > Decimal("0.00"):
            new_status_id = (partial_status or {}).get("id")
        else:
            new_status_id = (pending_status or {}).get("id")

        if new_status_id:
            QueryBuilderService("crmf_services_renders")\
                .where("id", data["service_render_id"])\
                .update({
                    "payment_status": int(new_status_id)
                })

        # Create journal entries
        create_service_render_payment_journal_entries(
            service_render=service_render,
            payment_amount=paid_amount,
            user=request.user
        )

        # Create general ledger entry
        create_service_render_general_ledger(
            service_render=service_render,
            payment_amount=paid_amount,
            user=request.user
        )

        return ResponseService.response(
            "SUCCESS",
            created_payment,
            "default_create_success_msg"
        )
    except Exception as e:
        return ResponseService.response(
            "NOT_FOUND",
            str(e),
            "Error.INTERNAL_SERVER_ERROR"
        )

@csrf_exempt
@api_view(["GET","PUT","DELETE"])
def service_render_payment_single(request,id,payment_id):
    if request.method == 'GET':
        return get_service_render_payment(request,id,payment_id)
    if request.method == 'PUT':
        return update_service_render_payment(request,id,payment_id)
    if request.method == 'DELETE':
        return delete_service_render_payment(request,id,payment_id)

def update_service_render_payment(request,id,payment_id):
    try:
        data = json.loads(request.body or "{}")
        
        # Check if payment exists
        existing = QueryBuilderService("crmf_service_render_payments")\
            .where("service_render_id", id)\
            .where("id", payment_id)\
            .first()
            
        if not existing:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                "Service render payment not found"
            )

        # Validation rules
        rules = {
            "paid_amount": "required|numeric",
            "created_by": "required|integer|exists:core_users,id",
            "created_at": "required",
            "payment_receipt_name": "required|string",
            "payment_receipt_url": "required|string",
            "payment_receipt_type": "required",
            "service_render_id": "required|integer|exists:crmf_services_renders,id",
        }

        # Validate input data
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR",
                errors,
                Error.VALIDATION_ERROR
            )

        # Update service render payment
        updated = QueryBuilderService("crmf_service_render_payments")\
            .where("service_render_id", id)\
            .where("id", payment_id)\
            .update(data)
            
        return ResponseService.response(
            "SUCCESS",
            updated,
            "default_update_success_msg"
        )
    except Exception as e:
        return ResponseService.response(
            "NOT_FOUND",
            str(e),
            "Error.INTERNAL_SERVER_ERROR"
        )

def delete_service_render_payment(request,id,payment_id):
    try:
        # Check if payment exists
        existing = QueryBuilderService("crmf_service_render_payments")\
            .where("service_render_id", id)\
            .where("id", payment_id)\
            .first()
            
        if not existing:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                "Service render payment not found"
            )

        # Delete service render payment
        QueryBuilderService("crmf_service_render_payments")\
            .where("service_render_id", id)\
            .where("id", payment_id)\
            .delete()
            
        return ResponseService.response(
            "SUCCESS",
            None,
            "default_delete_success_msg"
        )
    except Exception as e:
        return ResponseService.response(
            "NOT_FOUND",
            str(e),
            "Error.INTERNAL_SERVER_ERROR"
        )

         



     