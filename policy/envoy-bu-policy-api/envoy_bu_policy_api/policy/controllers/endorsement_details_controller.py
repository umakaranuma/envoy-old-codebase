from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from datetime import date
from django.db.models import Max
from envoy_bu_policy_api.policy.models.crmp_endorsements_details import Endorsement
from decimal import Decimal
import decimal
from envoy_bu_policy_api.finance.controllers.utils.invoice_utils import generate_invoice_for_endorsement


@csrf_exempt
@api_view(["GET", "POST"])
def endorsement_list(request, policy_id=None):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("Endorsement", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_endorsements(request, endorsement_id=None, policy_id=policy_id)

    return create_endorsement(request)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def endorsement_detail(request, endorsement_id):
    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("Endorsement", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_endorsements(request, endorsement_id=endorsement_id)
    elif request.method == "PUT":
        return update_endorsement(request, endorsement_id)
    elif request.method == "DELETE":
        return delete_endorsement(endorsement_id)


def get_all_endorsements(request, endorsement_id=None, policy_id=None):
    columns = [
        "crmp_endorsements_details.*",
        "crmp_endorsement_types.name AS endorsement_type_name",
        "crmp_endorsement_reason_codes.code AS reason_code",
        "crmp_endorsement_reason_codes.description AS reason_code_description",
        "notes.notes AS remarks",
        "users.display_name AS created_by",
        "users.picture AS created_by_logo",
        "entities.created_at AS created_at",
        "crmp_endorsement_requests.endorsement_request as endorsement_request_code",
        "COALESCE(invoices.invoice_amount, crmp_endorsement_requests.cover_value) as cover_value",
        "CASE WHEN crmp_endorsements_details.credit_period_days IS NOT NULL AND crmp_endorsements_details.credit_period_days > 0 THEN crmp_endorsements_details.credit_period_days WHEN invoices.credit_period_days IS NOT NULL AND invoices.credit_period_days > 0 THEN invoices.credit_period_days ELSE COALESCE(crmp_endorsement_requests.credit_period, 0) END as credit_period",
        "invoices.invoice_number AS invoice_number ",
        "CASE WHEN invoices.outstanding_amount > 0 THEN 'Outstanding' ELSE 'Settled' END AS invoice_status",
        "status.name AS invoice_status_name",
        "status.color AS invoice_status_color",

    ]

    query = (
        QueryBuilderService("crmp_endorsements_details")
        .select(*columns)
        .leftJoin(
            "crmp_endorsement_requests",
            "crmp_endorsement_requests.id",
            "crmp_endorsements_details.endorsement_request_id",
        )
        .leftJoin(
            "crmp_endorsement_types",
            "crmp_endorsement_types.id",
            "crmp_endorsement_requests.endorsement_type_id",
        )
        .leftJoin(
            "crmp_endorsement_reason_codes",
            "crmp_endorsement_reason_codes.id",
            "crmp_endorsement_requests.reason_code_id",
        )
        .leftJoin(
            "core_entities as entities",
            "entities.id",
            "crmp_endorsement_requests.entity_id",
        )
        .leftJoin(
            "core_entity_notes as notes",
            "notes.entity_id",
            "crmp_endorsement_requests.entity_id",
        )
        .leftJoin(
            "core_users as users",
            "users.id",
            "entities.created_by_id",
        )
        .leftJoin(
            "crmf_invoices as invoices",
            "invoices.endorsement_id",
            "crmp_endorsements_details.id",
        )
        .leftJoin(
            "core_status as status",
            "status.id",
            "invoices.status_id",
        )
    )

    if endorsement_id:
        data = query.where("crmp_endorsements_details.id", endorsement_id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    
    # Default to descending order by id (newest first, since id is auto-incrementing)
    # This ensures proper ordering even when created_at is the same
    sort_by = "crmp_endorsements_details.id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    
    # Ensure desc order for default sorting
    if sort_by == "crmp_endorsements_details.id" and sort_dir not in ["asc", "desc"]:
        sort_dir = "desc"

    allowed_filters = ["status", "endorsement_id"]
    search_columns = ["endorsement_id", "remarks"]
    sort_columns = ["crmp_endorsements_details.id", "entities.created_at", "endorsement_date", "amount", "status"]
    if policy_id:
        data = query.leftJoin(
            "crmp_endorsement_requests as er",
            "er.id",
            "crmp_endorsements_details.endorsement_request_id",
        ).where("er.issued_policy_id", policy_id)

        data = query.apply_conditions(
            filter_json, allowed_filters, search_string, search_columns
        ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def create_endorsement(request):
    data = json.loads(request.body or "{}")

    # When type is "cancellation", credit_period is not required
    endorsement_type_from_payload = (data.get("type") or "").strip().lower()
    is_cancellation = endorsement_type_from_payload in ("cancellation", "cancellations")

    if is_cancellation and (data.get("credit_period") is None or data.get("credit_period") == ""):
        data.pop("credit_period", None)

    rules = {
        "cover_value": "required|numeric|min:0",
        "endorsement_request_id": "required|integer|min:1",
        "credit_period": "integer|min:0" if is_cancellation else "required|integer|min:0",
    }
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    # --- Safety check: ensure endorsement_request_id exists to avoid FK violations ---
    try:
        endorsement_request = (
            QueryBuilderService("crmp_endorsement_requests")
            .where("id", data.get("endorsement_request_id"))
            .first()
        )
    except Exception as e:
        endorsement_request = None
        print(f"Error checking endorsement_request existence: {str(e)}")

    if not endorsement_request:
        # If the referenced endorsement request does not exist, return a clear validation error
        return ResponseService.response(
            "VALIDATION_ERROR",
            {
                "endorsement_request_id": [
                    "The selected endorsement_request_id is invalid or does not exist."
                ]
            },
            Error.VALIDATION_ERROR,
        )
    
    # Format cover_value to 2 decimal places
    data["cover_value"] = Decimal(str(data["cover_value"])).quantize(Decimal('.01'))

    # Prepare update data for endorsement request
    update_data = {"cover_value": data["cover_value"]}
    
    # Add credit_period if provided
    if "credit_period" in data and data["credit_period"] is not None:
        update_data["credit_period"] = data["credit_period"]

    # Update the endorsement request with new cover_value and credit_period
    try:
        update_result = QueryBuilderService("crmp_endorsement_requests")\
            .where("id", data["endorsement_request_id"])\
            .update(update_data)
            
    except Exception as e:
        print(f"Error updating endorsement request: {str(e)}")
        pass

    # Prepare data for endorsement creation
    data["endorsement_id"] = generate_endorse_request_id()
    data["status"] = 2
    
    # Store credit_period in credit_period_days field for this endorsement
    # This ensures each endorsement has its own credit_period value
    if "credit_period" in data and data["credit_period"] is not None:
        data["credit_period_days"] = int(data["credit_period"])
    
    errors = ValidatorService.validate(data, get_endorsement_rules())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    # Set default endorsement_date if not provided
    if not data.get("endorsement_date"):
        data["endorsement_date"] = str(date.today())

    # Get endorsement type and policy info
    endorsement_info = (
        QueryBuilderService("crmp_endorsement_requests")
        .select(
            "crmp_endorsement_types.name as endorsement_type",
            "crmp_endorsement_requests.cover_value as amount",
            "crmp_endorsement_requests.issued_policy_id as issued_policy_id"
        )
        .leftJoin(
            "crmp_endorsement_types",
            "crmp_endorsement_types.id",
            "crmp_endorsement_requests.endorsement_type_id"
        )
        .where("crmp_endorsement_requests.id", data["endorsement_request_id"])
        .first()
    )

    # Get initial premium amount from issued policy
    if endorsement_info and endorsement_info.get("issued_policy_id"):
        policy_info = (
            QueryBuilderService("crmp_issued_policies")
            .select(
                "initial_premium_amount",
                "premium_amount",
                "paid_amount"
            )
            .where("id", endorsement_info.get("issued_policy_id"))
            .first()
        )
        
        # Set current premium amount from current premium amount (not initial)
        # This ensures we use the updated premium amount after any previous endorsements
        data["current_premium_amount"] = str(policy_info.get("premium_amount", "0.00"))
        data["paid_amount"] = "0.00"

    # Get endorsement type and amount for calculations
    endorsement_type = endorsement_info.get("endorsement_type") if endorsement_info else None
    
    # Safe amount conversion with proper null handling
    # The amount comes from 'cover_value' in the request body, which was updated in the
    # endorsement_request table. For cancellations, this is the refund amount.
    # Example: If cover_value = 2500.00, then amount = 2500.00 (to be refunded)
    amount_value = endorsement_info.get("amount") if endorsement_info else None
    amount_str = str(amount_value) if amount_value is not None else "0.00"
    
    try:
        amount = Decimal(amount_str).quantize(Decimal('.01'))
    except (decimal.InvalidOperation, TypeError, ValueError):
        amount = Decimal("0.00")
   
    # Handle non-financial endorsements as activities
    if endorsement_type == "Non-Financials":
        # Create the endorsement record first
        user = request.user if request.user.is_authenticated else None
        created = QueryBuilderService("crmp_endorsements_details").insert(data)
        
        # Amount is already stored in the endorsement request, no need to update endorsement details
        
        # For non-financial endorsements, create an activity instead of financial processing
        try:
            from services.ActivityService import ActivityService
            
            # Get policy entity for activity creation
            policy_entity = (
                QueryBuilderService("crmp_issued_policies")
                .select("entity_id")
                .where("id", endorsement_info.get("issued_policy_id"))
                .first()
            )
            
            if policy_entity and policy_entity.get("entity_id"):
                activity_description = f"Non-financial endorsement {created.get('id', '')} processed: {data.get('remarks', 'No remarks provided')}"
                ActivityService.store_activity(
                    request=request,
                    entity_id=policy_entity.get("entity_id"),
                    activity=activity_description
                )
        except Exception as e:
            print(f"Error creating activity for non-financial endorsement: {str(e)}")
        
        # For non-financial endorsements, don't process financial calculations
        return ResponseService.response("SUCCESS", {
            "endorsement_id": created.get("id"),
            "message": "Non-financial endorsement processed as activity"
        }, "Non_financial_endorsement_processed_successfully")
    
    # Update policy premium based on endorsement type
    if endorsement_info and endorsement_info.get("issued_policy_id"):
        current_policy = (
            QueryBuilderService("crmp_issued_policies")
            .select("premium_amount", "initial_premium_amount", "paid_amount")
            .where("id", endorsement_info.get("issued_policy_id"))
            .first()
        )
        
        if current_policy:
            # Safe decimal conversion with proper null handling
            premium_value = current_policy.get("premium_amount")
            paid_value = current_policy.get("paid_amount")
            
            # Convert to string safely, handling None values
            premium_str = str(premium_value) if premium_value is not None else "0.00"
            paid_str = str(paid_value) if paid_value is not None else "0.00"
            
            # Ensure valid decimal conversion
            try:
                current_premium = Decimal(premium_str).quantize(Decimal('.01'))
            except (decimal.InvalidOperation, TypeError, ValueError):
                current_premium = Decimal("0.00")
                
            try:
                current_paid = Decimal(paid_str).quantize(Decimal('.01'))
            except (decimal.InvalidOperation, TypeError, ValueError):
                current_paid = Decimal("0.00")
            
            if endorsement_type == "Additions":
                # Additions increase premium and revenue
                new_premium = current_premium + amount
                QueryBuilderService("crmp_issued_policies")\
                    .where("id", endorsement_info.get("issued_policy_id"))\
                    .update({"premium_amount": str(new_premium)})
                    
            elif endorsement_type == "Cancellations":
                # Cancellations: do NOT reduce the policy premium amount.
                # Only update paid_amount to reflect the refund; premium_amount stays unchanged.
                #
                # Amount: from 'cover_value' in the request body (refund/cancellation amount).
                #   - premium_amount: unchanged (no reduction)
                #   - new_paid = current_paid - amount (refund applied to paid amount)
                #
                # Note: If current_paid_amount < amount, new_paid will be set to 0.00
                new_paid = current_paid - amount if current_paid >= amount else Decimal("0.00")
                QueryBuilderService("crmp_issued_policies")\
                    .where("id", endorsement_info.get("issued_policy_id"))\
                    .update({
                        "paid_amount": str(new_paid)
                    })
                    
            elif endorsement_type == "Refund":
                # Refunds deduct from both premium and paid amount
                new_premium = current_premium - amount
                new_paid = current_paid - amount if current_paid >= amount else Decimal("0.00")
                QueryBuilderService("crmp_issued_policies")\
                    .where("id", endorsement_info.get("issued_policy_id"))\
                    .update({
                        "premium_amount": str(new_premium),
                        "paid_amount": str(new_paid)
                    })
        
    invoice_data = {
        "paid_amount": "0.00",
        "outstanding_amount": "0.00",
        "total_amount": str(amount)
    }
    
    if endorsement_type == "Cancellations":
        # For cancellations, mark full amount as paid (refund); policy premium is not reduced
        invoice_data["paid_amount"] = str(amount)
        invoice_data["outstanding_amount"] = "0.00"
        invoice_data["total_amount"] = str(amount)  # Ensure total amount is set
        
        # IMPORTANT: Commission Deduction Calculation
        # When the invoice is generated via generate_invoice_for_endorsement(),
        # commission deductions are automatically calculated and stored in the 
        # commission_deductible field of the original premium invoice commission records.
        # 
        # The commission deduction calculation:
        # 1. Finds the original premium invoice commission records
        # 2. Calculates the deductible amount based on the cancellation amount
        # 3. Stores the deductible in commission_deductible field (brokerage + agent commissions)
        # 4. Creates adjustment journal entries for the deduction
        #
        # The deductible amounts are stored in the PREMIUM invoice commission records,
        # NOT in the cancellation invoice commission records.
        # This happens automatically when generate_invoice_for_endorsement() is called below.

        # Update policy base status to cancelled when endorsement type is cancellation
        try:
            from envoy_bu_policy_api.policy.controllers.policy_status_utils import set_policy_base_cancelled
            
            issued_policy_id = endorsement_info.get("issued_policy_id")
            if issued_policy_id:
                # Get policy_base_id from issued policy
                issued_policy = QueryBuilderService("crmp_issued_policies")\
                    .select("policy_base_id")\
                    .where("id", issued_policy_id)\
                    .first()
                
                if issued_policy and issued_policy.get("policy_base_id"):
                    result = set_policy_base_cancelled(issued_policy.get("policy_base_id"))
                    if result.get("success"):
                        print(f"Successfully set policy base status to CANCELLED for endorsement")
        except Exception as e:
            print(f"Error updating policy base status to cancelled: {str(e)}")

        
    elif endorsement_type == "Refund":
        # For refunds, deduct from both premium and paid amount
        invoice_data["paid_amount"] = "0.00"
        invoice_data["outstanding_amount"] = str(amount)
        invoice_data["total_amount"] = str(amount)  # Ensure total amount is set

        
    else:
        # For Additions and Non-Financials, add to premium only
        invoice_data["paid_amount"] = "0.00"
        invoice_data["outstanding_amount"] = str(amount)
        invoice_data["total_amount"] = str(amount)  # Ensure total amount is set


    user = request.user if request.user.is_authenticated else None
    created = QueryBuilderService("crmp_endorsements_details").insert(data)
    print(created)

    policy_details = None
    policy_details = (
        QueryBuilderService('crmp_endorsements_details')
        .leftJoin('crmp_endorsement_requests','crmp_endorsement_requests.id','crmp_endorsements_details.endorsement_request_id')
        .leftJoin('crmp_issued_policies','crmp_issued_policies.id','crmp_endorsement_requests.issued_policy_id')
        .leftJoin('crmp_policy_base','crmp_policy_base.id','crmp_issued_policies.policy_base_id')
        .select('crmp_policy_base.customer_id','crmp_issued_policies.id','crmp_issued_policies.brokerage_policy_id')
        .where('crmp_endorsements_details.id',created.get("id"))
        .first()
    )
    # Generate invoice with the calculated amounts
    # NOTE: For cancellations, commission deductions are automatically calculated and stored
    # in commission_deductible fields during invoice generation (inside generate_invoice_for_endorsement)
    print(f"DEBUG: Endorsement created with ID: {created.get('id') if created else 'None'}")
    print(f"DEBUG: Invoice data: {invoice_data}")
    print(f"DEBUG: User: {user}")
    
    if created and created.get("id"):
        print(f"DEBUG: Calling generate_invoice_for_endorsement with endorsement_id: {created['id']}")
        try:
            # This function will automatically handle commission deduction calculation for cancellations
            # and store deductible amounts in the original premium invoice commission records
            result = generate_invoice_for_endorsement(created["id"], is_update=False, user=user, invoice_data=invoice_data)
            print(f"DEBUG: Invoice generation result: {result}")
        except Exception as e:
            print(f"ERROR: Failed to generate invoice for endorsement {created['id']}: {str(e)}")
            import traceback
            print(f"ERROR: Traceback: {traceback.format_exc()}")
    else:
        print(f"ERROR: No endorsement created or no ID returned")


    #----------------NotificationService-----------------------
    try:
        # Get additional policy and product details for enhanced notification
        policy_product_details = (
            QueryBuilderService("crmp_issued_policies as ip")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .leftJoin("core_vendor_products as vp", "vp.id", "pb.product_id")
            .select(
                "ip.brokerage_policy_id",
                "vp.name as product_name"
            )
            .where("ip.id", endorsement_info.get("issued_policy_id"))
            .first()
        )
        
        # Get debit/credit note information from invoice if available
        debit_credit_note = "N/A"
        try:
            # Wait a moment for invoice to be created, then try to get invoice info
            import time
            time.sleep(0.1)  # Small delay to ensure invoice is created
            
            invoice_info = (
                QueryBuilderService("crmf_invoices")
                .select("invoice_number")
                .where("endorsement_id", created.get("id"))
                .first()
            )
            if invoice_info:
                debit_credit_note = invoice_info.get("invoice_number", "N/A")
        except Exception as e:
            print(f"Error getting invoice info: {str(e)}")
            # If invoice not found yet, try to get it from the endorsement request
            try:
                if endorsement_info and endorsement_info.get("issued_policy_id"):
                    # Get invoice from issued policy
                    policy_invoice = (
                        QueryBuilderService("crmf_invoices")
                        .select("invoice_number")
                        .where("issued_policy_id", endorsement_info.get("issued_policy_id"))
                        .orderBy("id", "desc")
                        .first()
                    )
                    if policy_invoice:
                        debit_credit_note = policy_invoice.get("invoice_number", "N/A")
            except Exception as e2:
                print(f"Error getting policy invoice: {str(e2)}")
        
        # Format detailed message
        detailed_message = NotificationService.format_endorsement_message(
            policy_id=policy_product_details.get("brokerage_policy_id", "N/A") if policy_product_details else "N/A",
            product_name=policy_product_details.get("product_name", "Unknown Product") if policy_product_details else "Unknown Product",
            endorsement_type=endorsement_type or "Unknown",
            debit_credit_note=debit_credit_note,
            endorsement_value=str(amount)
        )
        
        # Prepare endorsement data for metadata
        endorsement_data = {
            "endorsement_id": created.get("id"),
            "policy_id": endorsement_info.get("issued_policy_id"),
            "brokerage_policy_id": policy_product_details.get("brokerage_policy_id") if policy_product_details else "N/A",
            "product_name": policy_product_details.get("product_name", "Unknown Product") if policy_product_details else "Unknown Product",
            "endorsement_type": endorsement_type or "Unknown",
            "debit_credit_note": debit_credit_note,
            "value": str(amount)
        }
        
        # Generate detailed notification
        NotificationService.generate_detailed_notification(
            type_code="endorsement_made",
            title="Endorsement Created",
            detailed_message=detailed_message,
            customer_id=policy_details.get("customer_id",""),
            user_id=user.id if user else None,
            endorsement_data=endorsement_data
        )
        
        print(f"Endorsement notification sent to customer {policy_details.get('customer_id')}")
    except Exception as notify_exc:
        print(f"Error sending endorsement notification: {str(notify_exc)}")
        # Don't fail the entire operation for notification errors


    return ResponseService.response("SUCCESS", created, "default_create_success_msg")


def update_endorsement(request, endorsement_id):
    data = json.loads(request.body or "{}")
    rules = get_endorsement_rules_put()
    rules["endorsement_id"] = "string"  # not required for update
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    updated = (
        QueryBuilderService("crmp_endorsements_details")
        .where("id", endorsement_id)
        .update(data)
    )
    user = request.user if request.user.is_authenticated else None

    generate_invoice_for_endorsement(endorsement_id, is_update=True, user=user)
    if updated:
        return ResponseService.response(
            "SUCCESS", updated, "default_update_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_endorsement(endorsement_id):
    deleted = (
        QueryBuilderService("crmp_endorsements_details")
        .where("id", endorsement_id)
        .delete()
    )
    if deleted:
        return ResponseService.response(
            "SUCCESS", deleted, "default_delete_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def get_endorsement_rules():
    return {
        # "endorsement_request_id": "required|integer|unique:crmp_endorsements_details,endorsement_request_id",
        "remarks": "string",
    }
def get_endorsement_rules_put():
    return {
        "remarks": "string",
    }


# |exists:crmp_endorsement_requests,id


def generate_endorse_request_id():
    last = Endorsement.objects.aggregate(Max("id"))["id__max"] or 0
    return f"END-{last + 1}"
