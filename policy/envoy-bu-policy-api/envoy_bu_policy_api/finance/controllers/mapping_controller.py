from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from django.db import transaction
import datetime
from mServices import ResponseService, QueryBuilderService, ValidatorService
from decimal import Decimal


@csrf_exempt
@api_view(["GET"])
def mapping_attribute_single(request, id):
    return get_attributes(request, id)



@csrf_exempt
@api_view(["GET","POST"])
def mapping_attributes(request):
    try:
        print("Received request method:", request.method)
        print("Request path:", request.path)
        print("Request body:", request.body)
        
        if request.method == "GET":
            return get_attributes(request)
        if request.method == "POST":
            return attributes_process(request)
    except Exception as e:
        print("Error in mapping_attributes:", str(e))
        print("Error type:", type(e))
        return ResponseService.response("NOT_FOUND", str(e), "processing_error")
  
def get_attributes(request, id=None):
    try:
        # Define all columns to select
        all_columns = [
            "crmf_update_histories.*",
            "core_users.display_name as uploaded_by_name",
            "crmf_payments.invoice_id",
            "crmf_payments.paid_amount",
            "crmf_payments.outstanding_amount",
            "core_entities.created_at as entity_created_at"
        ]

        # Initialize base query
        query = (
            QueryBuilderService("crmf_update_histories")
            .select(*all_columns)
            .leftJoin(
                "core_users",
                "crmf_update_histories.uploaded_by",
                "core_users.id"
            )
            .leftJoin(
                "crmf_payments",
                "crmf_update_histories.payment_id",
                "crmf_payments.id"
            )
            .leftJoin(
                "core_entities",
                "core_entities.id",
                "crmf_payments.entity_id"
            )
        )

        created_date = request.GET.get("date")
        if created_date:
            query = query.where("core_entities.created_at", "like", f"{created_date}%")

        if id:
            # Get single history record
            history = query.where("crmf_update_histories.id", id).first()
            if not history:
                return ResponseService.response("NOT_FOUND", "History record not found", "not_found")
            
            # Parse old and new data
            old_data = json.loads(history.get('old_data', '{}'))
            new_data = json.loads(history.get('new_data', '{}'))
            
            # Find updated fields
            updated_fields = {}
            for key, new_value in new_data.items():
                old_value = old_data.get(key)
                if old_value != new_value:
                    updated_fields[key] = {
                        "old_value": old_value,
                        "new_value": new_value
                    }
            
            # Calculate counts
            add_count = 0
            update_count = 1 if updated_fields else 0
            ignore_count = 0 if updated_fields else 1
            total_count = 1
            
            response_data = {
                "id": history.get('id'),
                "version_name": history.get('version'),
                "uploaded_by": history.get('uploaded_by_name', 'System'),
                "date": history.get('created_at'),
                "invoice_id": history.get('invoice_id'),
                "old_data": old_data,
                "new_data": new_data,
                "updated_fields": updated_fields,
                "counts": {
                    "add_count": add_count,
                    "update_count": update_count,
                    "ignore_count": ignore_count,
                    "total_count": total_count
                }
            }
            
            return ResponseService.response("SUCCESS", response_data, "data_get")
        else:
            # Get list with pagination and filters
            filter_json = request.GET.get("filter", {})
            search_string = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            sort_by = request.GET.get("sort_by", "crmf_update_histories.created_at")
            sort_dir = request.GET.get("sort_dir", "desc")

            allowed_filters = [
                "crmf_update_histories.version",
                "crmf_update_histories.uploaded_by",
                "crmf_payments.invoice_id"
            ]
            
            search_columns = [
                "crmf_update_histories.version",
                "core_users.username",
                "crmf_payments.invoice_id"
            ]

            allowed_sorting_columns = [
                "crmf_update_histories.created_at",
                "crmf_update_histories.version",
                "core_users.username",
                "crmf_payments.invoice_id"
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

            # Process each record to include updated fields
            add_count = 0
            update_count = 0
            ignore_count = 0
            total_count = len(data.get('data', []))

            for record in data.get('data', []):
                old_data = json.loads(record.get('old_data', '{}'))
                new_data = json.loads(record.get('new_data', '{}'))
                
                updated_fields = {}
                for key, new_value in new_data.items():
                    old_value = old_data.get(key)
                    if old_value != new_value:
                        updated_fields[key] = {
                            "old_value": old_value,
                            "new_value": new_value
                        }
                
                if updated_fields:
                    update_count += 1
                else:
                    ignore_count += 1
                
                record['updated_fields'] = updated_fields
                record['uploaded_by'] = record.get('uploaded_by_name', 'System')
                record['version_name'] = record.get('version')
                record['date'] = record.get('created_at')
                
                # Remove unnecessary fields
                record.pop('old_data', None)
                record.pop('new_data', None)
                record.pop('uploaded_by_name', None)

            data['counts'] = {
                "add_count": add_count,
                "update_count": update_count,
                "ignore_count": ignore_count,
                "total_count": total_count
            }

            return ResponseService.response("SUCCESS", data, "data_get")
            
    except Exception as e:
        print("Error in get_attributes:", str(e))
        return ResponseService.response("NOT_FOUND", str(e), "processing_error")


# Helper to convert Decimals to float for JSON serialization
def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj


def lookup_id_by_name(table, name_column, name_value, id_column="id"):
    """
    Looks up the ID for a given name in the specified table.
    """
    if not name_value:
        return None
    record = QueryBuilderService(table).where(name_column, name_value).first()
    if record:
        return record.get(id_column)
    return None


def attributes_process(request):
    try:
        print("Starting attributes_process")
        data = json.loads(request.body)
        print("Parsed request data:", data)
   
        rules = {
           "mapping": "required|array",
           "flex_fields": "optional|array",
           "data": "required|array",
           "type": "required",
           "file_name": "optional"
        }

        print("Validating data against rules")
        errors = ValidatorService.validate(data, rules)
        if errors:
            print("Validation errors:", errors)
            return ResponseService.response("NOT_FOUND", errors, "validation_error")

        if data.get('type') == "payments":
            try:
                print("Processing invoice type data (optimized, no invoice_id required)")
                with transaction.atomic():
                    results = []
                    add_count = 0
                    update_count = 0
                    ignore_count = 0
                    total_count = len(data.get('data', []))
                    mapping_ids = []
                    for row in data.get('data', []):
                        print("Processing row:", row)
                        row_id = row.get('row_id', row.get('invoice_number') or row.get('insurer_invoice_id') or str(len(results)+1))
                        receipt_number = row.get('receipt_number')
                        payments = QueryBuilderService("crmf_payments").where("receipt_number", receipt_number).get() if receipt_number else []
                        # Prepare incoming values for comparison
                        incoming_paid_amount = float(row.get('paid_amount', 0))
                        incoming_insurer_policy_number = row.get('insurer_policy_number')
                        incoming_insurer_invoice_id = row.get('insurer_invoice_id')
                        found_match = False
                        # Helper to fetch invoice and issued policy for a payment
                        def fetch_invoice_and_policy(invoice_id):
                            invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()
                            issued_policy = None
                            if invoice and invoice.get('issued_policy_id'):
                                issued_policy = QueryBuilderService("crmp_issued_policies").where("id", invoice.get('issued_policy_id')).first()
                            return invoice, issued_policy
                        # Check for existing payments with this receipt_number
                        for payment in payments:
                            invoice, issued_policy = fetch_invoice_and_policy(payment.get('invoice_id'))
                            all_match = (
                                (issued_policy and issued_policy.get('insurer_policy_id') == incoming_insurer_policy_number) and
                                (float(payment.get('paid_amount', 0)) == incoming_paid_amount) and
                                (issued_policy and issued_policy.get('insurer_invoice_id') == incoming_insurer_invoice_id)
                            )
                            if all_match:
                                # log as ignored
                                mapping_update = {
                                    "payment_id": payment.get('id'),
                                    "old_data": json.dumps(convert_decimal(payment)),
                                    "new_data": json.dumps(convert_decimal(payment)),
                                    "version": data.get('file_name', ''),
                                    "uploaded_by": request.user.id if request.user and request.user.id else 1
                                }
                                mapping_record = QueryBuilderService("crmf_update_histories").insert(mapping_update)
                                result = {
                                    "row_id": row_id,
                                    "receipt_number": receipt_number,
                                    "status": "ignored",
                                    "details": {
                                        "history_id": mapping_record.get('id') if mapping_record else None,
                                        "ignored": "Duplicate payment found with matching fields."
                                    }
                                }
                                results.append(result)
                                ignore_count += 1
                                found_match = True
                                break
                            else:
                                # log as mismatch
                                mapping_update = {
                                    "payment_id": payment.get('id'),
                                    "old_data": json.dumps(convert_decimal(payment)),
                                    "new_data": json.dumps(convert_decimal(row)),
                                    "version": data.get('file_name', ''),
                                    "uploaded_by": request.user.id if request.user and request.user.id else 1
                                }
                                mapping_record = QueryBuilderService("crmf_update_histories").insert(mapping_update)
                                result = {
                                    "row_id": row_id,
                                    "receipt_number": receipt_number,
                                    "status": "mismatch",
                                    "details": {
                                        "history_id": mapping_record.get('id') if mapping_record else None,
                                        "mismatch": "Payment found with receipt_number but fields differ."
                                    }
                                }
                                results.append(result)
                                update_count += 1
                                found_match = True
                                break
                        if not found_match:
                            # No payment with this receipt_number, find issued policy by insurer_policy_number and insurer_invoice_id
                            issued_policy = QueryBuilderService("crmp_issued_policies")\
                                .where("insurer_policy_id", incoming_insurer_policy_number)\
                                .where("insurer_invoice_id", incoming_insurer_invoice_id).first()
                            if issued_policy:
                                # Find invoice by issued_policy id
                                invoice = QueryBuilderService("crmf_invoices").where("issued_policy_id", issued_policy.get('id')).first()
                                if invoice:
                                    # Create new payment using found invoice id
                                    new_payment_data = {
                                        "invoice_id": invoice.get('id'),
                                        "paid_amount": incoming_paid_amount,
                                        "outstanding_amount": float(row.get('outstanding_amount', 0)),
                                        "entity_id": row.get('entity_id', 1),
                                        "method": row.get('method', 'mapping_import'),
                                        "receipt_number": receipt_number
                                    }
                                    new_payment = QueryBuilderService("crmf_payments").insert(new_payment_data)
                                    mapping_update = {
                                        "payment_id": new_payment.get('id') if new_payment else None,
                                        "old_data": json.dumps({}),
                                        "new_data": json.dumps(convert_decimal(new_payment_data)),
                                        "version": data.get('file_name', ''),
                                        "uploaded_by": request.user.id if request.user and request.user.id else 1
                                    }
                                    mapping_record = QueryBuilderService("crmf_update_histories").insert(mapping_update)
                                    result = {
                                        "row_id": row_id,
                                        "receipt_number": receipt_number,
                                        "status": "created",
                                        "details": {
                                            "new_payment_id": new_payment.get('id') if new_payment else None,
                                            "history_id": mapping_record.get('id') if mapping_record else None,
                                            "created": "Data Created Successfully"
                                        }
                                    }
                                    results.append(result)
                                    add_count += 1
                                else:
                                    # Invoice not found for issued policy
                                    result = {
                                        "row_id": row_id,
                                        "receipt_number": receipt_number,
                                        "status": "error",
                                        "details": {
                                            "error": "Invoice not found for issued policy. Cannot create payment."
                                        }
                                    }
                                    results.append(result)
                                    update_count += 1
                            else:
                                # Issued policy not found
                                result = {
                                    "row_id": row_id,
                                    "receipt_number": receipt_number,
                                    "status": "error",
                                    "details": {
                                        "error": "Issued policy not found for given insurer_policy_number and insurer_invoice_id. Cannot create payment."
                                    }
                                }
                                results.append(result)
                                update_count += 1
                response_result = {
                    "message": "mapping_updated",
                    "processed_rows": len(data.get('data', [])),
                    "mappings": len(data.get('mapping', [])),
                    "flex_fields": len(data.get('flex_fields', [])),
                    "mapping_ids": mapping_ids,
                    "results": results,
                    "counts": {
                        "add_count": add_count,
                        "update_count": update_count,
                        "ignore_count": ignore_count,
                        "total_count": total_count
                    }
                }
                return ResponseService.response(
                    "SUCCESS",
                    response_result,
                    "mapping_updated"
                )
            
   

            except Exception as e:
                print("Error in transaction (optimized, no invoice_id required):", str(e))
                print("Error type:", type(e))
                return ResponseService.response("NOT_FOUND", str(e), "processing_error")
            
#--------------------------------------------------commission_setup-----------------------------------------
        if data.get('type') == "commission_setup":
            try:
                print("Processing commission setup data (name-based lookup)")
                with transaction.atomic():
                    results = []
                    add_count = 0
                    update_count = 0
                    ignore_count = 0
                    total_count = len(data.get('data', []))
                    mapping_ids = []  # Track mapping IDs
                    
                    for row in data.get('data', []):
                        print("Processing row:", row)
                        result = {
                            "row_id": row.get('row_id'),
                            "status": "",
                            "details": {}
                        }
                        try:
                            # Lookup IDs from names or use IDs if provided
                            product_id = row.get("product_id")
                            if not product_id:
                                product_name = row.get("product_name")
                                if not product_name:
                                    result["status"] = "error"
                                    result["details"] = {"error": "Either 'product_id' or 'product_name' must be provided."}
                                    results.append(result)
                                    ignore_count += 1
                                    continue
                                product_id = lookup_id_by_name("core_vendor_products", "name", product_name)
                            if not product_id:
                                result["status"] = "error"
                                result["details"] = {"error": f"Product name '{row.get('product_name')}' does not exist in core_vendor_products."}
                                results.append(result)
                                ignore_count += 1
                                continue

                            native_product_id = row.get("native_product_id")
                            if not native_product_id:
                                native_product_name = row.get("native_product_name")
                                if not native_product_name:
                                    result["status"] = "error"
                                    result["details"] = {"error": "Either 'native_product_id' or 'native_product_name' must be provided."}
                                    results.append(result)
                                    ignore_count += 1
                                    continue
                                native_product_id = lookup_id_by_name("core_products", "name", native_product_name)
                            if not native_product_id:
                                result["status"] = "error"
                                result["details"] = {"error": f"Native Product name '{row.get('native_product_name')}' does not exist in core_products."}
                                results.append(result)
                                ignore_count += 1
                                continue
                            
                            insurer_id = row.get("insurer_id")
                            if not insurer_id:
                                insurer_name = row.get("insurer_name")
                                if not insurer_name:
                                    result["status"] = "error"
                                    result["details"] = {"error": "Either 'insurer_id' or 'insurer_name' must be provided."}
                                    results.append(result)
                                    ignore_count += 1
                                    continue
                                insurer_id = lookup_id_by_name("core_service_providers", "name", insurer_name)
                            if not insurer_id:
                                result["status"] = "error"
                                result["details"] = {"error": f"Insurer name '{row.get('insurer_name')}' does not exist in core_service_providers."}
                                results.append(result)
                                ignore_count += 1
                                continue

                            transaction_type_id = row.get("transaction_type_id")
                            if not transaction_type_id:
                                transaction_type_name = row.get("transaction_type_name")
                                if not transaction_type_name:
                                    result["status"] = "error"
                                    result["details"] = {"error": "Either 'transaction_type_id' or 'transaction_type_name' must be provided."}
                                    results.append(result)
                                    ignore_count += 1
                                    continue
                                transaction_type_id = lookup_id_by_name("crmf_transaction_types", "name", transaction_type_name)
                            if not transaction_type_id:
                                result["status"] = "error"
                                result["details"] = {"error": f"Transaction type name '{row.get('transaction_type_name')}' does not exist in crmf_transaction_types."}
                                results.append(result)
                                ignore_count += 1
                                continue

                            # Handle team IDs - now optional in request
                            team_ids = row.get('sales_team_ids')
                            if not team_ids:
                                team_names_str = row.get('sales_team_names')
                                if team_names_str:
                                    team_names = [name.strip() for name in team_names_str.split(',') if name.strip()]
                                    team_ids = []
                                    has_error = False
                                    for team_name in team_names:
                                        team_id = lookup_id_by_name("core_teams", "name", team_name)
                                        if not team_id:
                                            result["status"] = "error"
                                            result["details"] = {"error": f"Sales Team name '{team_name}' does not exist in core_teams."}
                                            has_error = True
                                            break
                                        team_ids.append(str(team_id))
                                    
                                    if has_error:
                                        results.append(result)
                                        ignore_count += 1
                                        continue
                                else:
                                    # If no team info is provided, find all teams for the native product from core_product_teams
                                    product_teams = QueryBuilderService("core_product_teams").where("product_id", native_product_id).get()
                                    team_ids = [str(pt["team_id"]) for pt in product_teams]
                            
                            if not team_ids:
                                result["status"] = "error"
                                result["details"] = {"error": "Team information is required but was not provided and could not be found for the native product."}
                                results.append(result)
                                ignore_count += 1
                                continue
                            
                            # Modify this section to require commission_type
                            commission_type = row.get('commission_type')
                            if not commission_type:
                                result["status"] = "error"
                                result["details"] = {"error": "commission_type is required"}
                                results.append(result)
                                ignore_count += 1
                                continue
                                
                            # Validate commission_type value (optional but recommended)
                            valid_types = ['percent', 'fixed']  # Add any other valid types
                            if commission_type not in valid_types:
                                result["status"] = "error" 
                                result["details"] = {"error": f"Invalid commission_type. Must be one of: {', '.join(valid_types)}"}
                                results.append(result)
                                ignore_count += 1
                                continue

                            brokerage_revenue_percent_val = row.get('brokerage_revenue_percent')
                            agent_commission_percent_val = row.get('agent_commission_percent')
# ...existing code...
                            bonus_commission_percent_data = row.get('bonus_commission_percent')
                            target_achievement_commission_percent_data = row.get('target_achievement_commission_percent')

                            # Prepare commission data
                            commission_data = {
                                "product_id": int(product_id),
                                "native_product_id": int(native_product_id),
                                "insurer_id": int(insurer_id),
                                "transaction_type": int(transaction_type_id),
                                # Remove sales_team_id as it's now handled by join table
                                "brokerage_revenue_percent": Decimal(brokerage_revenue_percent_val or 0),
                                "agent_commission_percent": Decimal(agent_commission_percent_val or 0),
                                "bonus_commission_percent": Decimal(bonus_commission_percent_data or 0),
                                "target_achievement_commission_percent": Decimal(target_achievement_commission_percent_data or 0),
                                "created_at": datetime.datetime.now()
                            }
                            # Duplicate check - check if any of the team IDs already have a commission setup
                            for team_id in team_ids:
                                existing_setup = (
                                    QueryBuilderService("crmf_commission_setups")
                                        .leftJoin("crmf_commission_setup_teams", "crmf_commission_setups.id", "crmf_commission_setup_teams.commission_setup_id")
                                        .where("product_id", int(commission_data["product_id"]))
                                        .where("crmf_commission_setup_teams.team_id", int(team_id))
                                        .where("transaction_type", int(commission_data["transaction_type"]))
                                        .whereNull("crmf_commission_setups.deleted_at")
                                        .first()
                                )
                                if existing_setup:
                                    # Use team_name if available, else fallback to team_id
                                    error_team_name = None
                                    if 'team_names' in locals() and len(team_names) == len(team_ids):
                                        idx = team_ids.index(str(team_id)) if str(team_id) in team_ids else None
                                        if idx is not None:
                                            error_team_name = team_names[idx]
                                    result["status"] = "error"
                                    if error_team_name:
                                        result["details"] = {"error": f"Commission setup already exists for this product and team {error_team_name}"}
                                    else:
                                        result["details"] = {"error": f"Commission setup already exists for this product and team ID {team_id}"}
                                    results.append(result)
                                    ignore_count += 1
                                    break
                            if result["status"] == "error":
                                continue
                            # Check for existing record with any of the team IDs
                            existing_record = None
                            for team_id in team_ids:
                                existing_record = QueryBuilderService("crmf_commission_setups").where(
                                    "product_id", commission_data['product_id']
                                ).where(
                                    "insurer_id", commission_data['insurer_id']
                                ).where(
                                    "transaction_type", commission_data['transaction_type']
                                ).leftJoin(
                                    "crmf_commission_setup_teams", 
                                    "crmf_commission_setups.id", 
                                    "crmf_commission_setup_teams.commission_setup_id"
                                ).where(
                                    "crmf_commission_setup_teams.team_id", int(team_id)
                                ).first()
                                if existing_record:
                                    break
                            if existing_record:
                                has_changes = (
                                    float(existing_record.get('brokerage_revenue_percent', 0)) != float(commission_data['brokerage_revenue_percent']) or
                                    float(existing_record.get('agent_commission_percent', 0)) != float(commission_data['agent_commission_percent']) or
                                    float(existing_record.get('bonus_commission_percent', 0)) != float(commission_data['bonus_commission_percent']) or
                                    float(existing_record.get('target_achievement_commission_percent', 0)) != float(commission_data['target_achievement_commission_percent'])
                                )
                                if has_changes:
                                    old_data = existing_record.copy()
                                    update_result = QueryBuilderService("crmf_commission_setups").where(
                                        "id", existing_record.get('id')
                                    ).update(commission_data)
                                    if update_result:
                                        # Hard delete related field values and re-insert
                                        QueryBuilderService("crmf_commission_field_values").where("commission_setup_id", existing_record.get('id')).delete()
                                        
                                        commission_fields_to_process = {
                                            "brokerage_revenue_percent": brokerage_revenue_percent_val,
                                            "agent_commission_percent": agent_commission_percent_val
                                        }
                                        commission_fields = QueryBuilderService("crmf_commission_fields").get()
                                        field_map = {field["attribute_name"]: field["id"] for field in commission_fields}

                                        for field_name, value in commission_fields_to_process.items():
                                            if value is not None and field_name in field_map:
                                                field_id = field_map[field_name]
                                                QueryBuilderService("crmf_commission_field_values").insert({
                                                    "commission_field_id": field_id,
                                                    "commission_setup_id": existing_record.get('id'),
                                                    "value": value,
                                                    "type": commission_type,
                                                    "created_at": datetime.datetime.now(),
                                                    "updated_at": datetime.datetime.now()
                                                })

                                        old_data_serializable = {
                                            'id': old_data.get('id'),
                                            'product_id': old_data.get('product_id'),
                                            'native_product_id': old_data.get('native_product_id'),
                                            'insurer_id': old_data.get('insurer_id'),
                                            'transaction_type': old_data.get('transaction_type'),
                                            'brokerage_revenue_percent': float(old_data.get('brokerage_revenue_percent', 0)),
                                            'agent_commission_percent': float(old_data.get('agent_commission_percent', 0)),
                                            'bonus_commission_percent': float(old_data.get('bonus_commission_percent', 0)),
                                            'target_achievement_commission_percent': float(old_data.get('target_achievement_commission_percent', 0))
                                        }
                                        updated_fields = {}
                                        for key, new_value in commission_data.items():
                                            if key != 'created_at':
                                                old_value = old_data_serializable.get(key)
                                                if old_value != new_value:
                                                    updated_fields[key] = {
                                                        "old_value": old_value,
                                                        "new_value": new_value
                                                    }
                                        # Insert revised_commission_percent values if present (for update)
                                        revised_list = row.get("revised_commission_percent", [])
                                        if revised_list:
                                            field = QueryBuilderService("crmf_commission_fields").where("attribute_name", "revised_commission_percent").first()
                                            if field:
                                                field_id = field["id"]
                                                now = datetime.datetime.now()
                                                for item in revised_list:
                                                    # Lookup user_id and team_id if names provided
                                                    user_id = item.get("user_id")
                                                    if not user_id and item.get("user_name"):
                                                        user_id = lookup_id_by_name("core_users", "display_name", item["user_name"])
                                                    team_id_val = item.get("team_id")
                                                    if not team_id_val and item.get("team_name"):
                                                        team_id_val = lookup_id_by_name("core_teams", "name", item["team_name"])
                                                    QueryBuilderService("crmf_commission_field_values").insert({
                                                        "commission_field_id": field_id,
                                                        "commission_setup_id": existing_record.get('id'),
                                                        "user_id": user_id,
                                                        "team_id": team_id_val,
                                                        "value": item["value"],
                                                        "type": item["type"],
                                                        "created_at": now,
                                                        "updated_at": now
                                                    })
                                        mapping_update = {
                                            "commission_setup_id": existing_record.get('id'),
                                            "old_data": json.dumps(old_data_serializable),
                                            "new_data": json.dumps({
                                                "product_id": commission_data['product_id'],
                                                "native_product_id": commission_data['native_product_id'],
                                                "insurer_id": commission_data['insurer_id'],
                                                "transaction_type": commission_data['transaction_type'],
                                                "brokerage_revenue_percent": float(commission_data['brokerage_revenue_percent']),
                                                "agent_commission_percent": float(commission_data['agent_commission_percent']),
                                                "bonus_commission_percent": float(commission_data['bonus_commission_percent']),
                                                "target_achievement_commission_percent": float(commission_data['target_achievement_commission_percent']),
                                                "created_at": str(commission_data['created_at'])
                                            }),
                                            "version": data.get('file_name', ''),
                                            "uploaded_by": request.user.id if request.user and request.user.id else 1
                                        }
                                        mapping_record = QueryBuilderService("crmf_update_histories").insert(mapping_update)
                                        if mapping_record and mapping_record.get('id'):
                                            mapping_ids.append(mapping_record.get('id'))
                                        result["status"] = "updated"
                                        result["details"] = {
                                            "updated_fields": updated_fields,
                                            "mapping_id": mapping_record.get('id') if mapping_record else None,
                                            "commission_setup_id": existing_record.get('id')
                                        }
                                        update_count += 1
                                    else:
                                        result["status"] = "error"
                                        result["details"] = {"error": "Failed to update commission setup"}
                                else:
                                    result["status"] = "ignored"
                                    result["details"] = {
                                        "current_values": {
                                            'brokerage_revenue_percent': float(existing_record.get('brokerage_revenue_percent', 0)),
                                            'agent_commission_percent': float(existing_record.get('agent_commission_percent', 0)),
                                            'bonus_commission_percent': float(existing_record.get('bonus_commission_percent', 0)),
                                            'target_achievement_commission_percent': float(existing_record.get('target_achievement_commission_percent', 0)),
                                        },
                                        "ignored": "Cannot add this Commission setup"
                                    }
                                    ignore_count += 1
                            else:
                                new_commission = QueryBuilderService("crmf_commission_setups").insert(commission_data)
                                if new_commission:
                                    for team_id in team_ids:
                                        team_data = {
                                            "commission_setup_id": new_commission.get('id'),
                                            "team_id": int(team_id),
                                            "created_at": datetime.datetime.now()
                                        }
                                        QueryBuilderService("crmf_commission_setup_teams").insert(team_data)

                                    commission_fields_to_process = {
                                        "brokerage_revenue_percent": brokerage_revenue_percent_val,
                                        "agent_commission_percent": agent_commission_percent_val
                                    }
                                    commission_fields = QueryBuilderService("crmf_commission_fields").get()
                                    field_map = {field["attribute_name"]: field["id"] for field in commission_fields}

                                    for field_name, value in commission_fields_to_process.items():
                                        if value is not None and field_name in field_map:
                                            field_id = field_map[field_name]
                                            QueryBuilderService("crmf_commission_field_values").insert({
                                                "commission_field_id": field_id,
                                                "commission_setup_id": new_commission.get('id'),
                                                "value": value,
                                                "type": commission_type,
                                                "created_at": datetime.datetime.now(),
                                                "updated_at": datetime.datetime.now()
                                            })
                                            
                                    # Insert revised_commission_percent values if present
                                    revised_list = row.get("revised_commission_percent", [])
                                    if revised_list:
                                        field = QueryBuilderService("crmf_commission_fields").where("attribute_name", "revised_commission_percent").first()
                                        if field:
                                            field_id = field["id"]
                                            now = datetime.datetime.now()
                                            for item in revised_list:
                                                user_id = item.get("user_id")
                                                if not user_id and item.get("user_name"):
                                                    user_id = lookup_id_by_name("core_users", "display_name", item["user_name"])
                                                team_id_val = item.get("team_id")
                                                if not team_id_val and item.get("team_name"):
                                                    team_id_val = lookup_id_by_name("core_teams", "name", item["team_name"])
                                                QueryBuilderService("crmf_commission_field_values").insert({
                                                    "commission_field_id": field_id,
                                                    "commission_setup_id": new_commission.get('id'),
                                                    "value": item["value"],
                                                    "type": item["type"],
                                                    "created_at": now,
                                                    "updated_at": now
                                                })
                                    mapping_update = {
                                        "commission_setup_id": new_commission.get('id'),
                                        "old_data": json.dumps({}),
                                        "new_data": json.dumps({
                                            "product_id": commission_data['product_id'],
                                            "native_product_id": commission_data['native_product_id'],
                                            "insurer_id": commission_data['insurer_id'],
                                            "transaction_type": commission_data['transaction_type'],
                                            "sales_team_ids": ",".join(team_ids),
                                            "brokerage_revenue_percent": float(commission_data['brokerage_revenue_percent']),
                                            "agent_commission_percent": float(commission_data['agent_commission_percent']),
                                            "bonus_commission_percent": float(commission_data['bonus_commission_percent']),
                                            "target_achievement_commission_percent": float(commission_data['target_achievement_commission_percent'])
                                        }),
                                        "version": data.get('file_name', ''),
                                        "uploaded_by": request.user.id if request.user and request.user.id else 1
                                    }
                                    mapping_record = QueryBuilderService("crmf_update_histories").insert(mapping_update)
                                    if mapping_record and mapping_record.get('id'):
                                        mapping_ids.append(mapping_record.get('id'))
                                    result["status"] = "created"
                                    result["details"] = {
                                        "new_values": {
                                            "product_id": commission_data['product_id'],
                                            "native_product_id": commission_data['native_product_id'],
                                            "insurer_id": commission_data['insurer_id'],
                                            "transaction_type": commission_data['transaction_type'],
                                            "sales_team_ids": ",".join(team_ids),
                                            "brokerage_revenue_percent": float(commission_data['brokerage_revenue_percent']),
                                            "agent_commission_percent": float(commission_data['agent_commission_percent']),
                                            "bonus_commission_percent": float(commission_data['bonus_commission_percent']),
                                            "target_achievement_commission_percent": float(commission_data['target_achievement_commission_percent'])
                                        },
                                        "commission_setup_id": new_commission.get('id'),
                                        "created" : "Data Created Successfully"
                                    }
                                    add_count += 1
                                else:
                                    result["status"] = "error"
                                    result["details"] = {"error": "Failed to create commission setup"}
                        except Exception as e:
                            result["status"] = "error"
                            result["details"] = {"error": str(e)}
                        results.append(result)
                    return ResponseService.response("SUCCESS", {
                        "message": "commission_setup_updated",
                        "processed_rows": len(data.get('data', [])),
                        "mappings": len(data.get('mapping', [])),
                        "flex_fields": len(data.get('flex_fields', [])),
                        "mapping_ids": mapping_ids,  # Include mapping IDs in response
                        "results": results,
                        "counts": {
                            "add_count": add_count,
                            "update_count": update_count,
                            "ignore_count": ignore_count,
                            "total_count": total_count
                        }
                    }, "commission_setup_updated")
            except Exception as e:
                print("Error in commission setup processing:", str(e))
                print("Error type:", type(e))
                return ResponseService.response("NOT_FOUND", str(e), "processing_error")

        print("Invalid type specified:", data.get('type'))
        return ResponseService.response("NOT_FOUND", "Invalid type specified", "validation_error")

    except Exception as e:
        print("Error in attributes_process:", str(e))
        print("Error type:", type(e))
        return ResponseService.response("NOT_FOUND", str(e), "processing_error")


@csrf_exempt
@api_view(["GET"])
def payment_uploads(request):



    return ResponseService.response("SUCCESS",[],"data_get") 


@csrf_exempt
@api_view(["GET"])
def mapping_attribute_history(request, ids):
    try:
        # Parse the IDs parameter - it could be comma-separated or a single ID
        if isinstance(ids, str):
            # Handle comma-separated string of IDs
            id_list = [int(id.strip()) for id in ids.split(',') if id.strip().isdigit()]
        elif isinstance(ids, int):
            # Handle single ID
            id_list = [ids]
        else:
            return ResponseService.response("NOT_FOUND", "Invalid ID format", "validation_error")
        
        if not id_list:
            return ResponseService.response("NOT_FOUND", "No valid IDs provided", "validation_error")
        
        print(f"Fetching mapping history for IDs: {id_list}")
        
        # Define all columns to select
        all_columns = [
            "crmf_update_histories.*",
            "core_users.display_name as uploaded_by_name",
            "crmf_payments.invoice_id",
            "crmf_payments.paid_amount",
            "crmf_payments.outstanding_amount"
        ]

        # Initialize base query
        query = (
            QueryBuilderService("crmf_update_histories")
            .select(*all_columns)
            .leftJoin(
                "core_users",
                "crmf_update_histories.uploaded_by",
                "core_users.id"
            )
            .leftJoin(
                "crmf_payments",
                "crmf_update_histories.payment_id",
                "crmf_payments.id"
            )
        )
        
        # Add WHERE clause for multiple IDs
        if len(id_list) == 1:
            query = query.where("crmf_update_histories.id", id_list[0])
        else:
            query = query.whereIn("crmf_update_histories.id", id_list)
        
        # Get the records
        history_records = query.get()
        
        if not history_records:
            return ResponseService.response("NOT_FOUND", "No mapping history records found for the provided IDs", "not_found")
        
        # Process each record to include updated fields
        processed_records = []
        add_count = 0
        update_count = 0
        ignore_count = 0
        total_count = len(history_records)

        for record in history_records:
            old_data = json.loads(record.get('old_data', '{}'))
            new_data = json.loads(record.get('new_data', '{}'))
            
            updated_fields = {}
            for key, new_value in new_data.items():
                old_value = old_data.get(key)
                if old_value != new_value:
                    updated_fields[key] = {
                        "old_value": old_value,
                        "new_value": new_value
                    }
            
            if updated_fields:
                update_count += 1
            else:
                ignore_count += 1
            
            processed_record = {
                'id': record.get('id'),
                'version_name': record.get('version'),
                'uploaded_by': record.get('uploaded_by_name', 'System'),
                'date': record.get('created_at'),
                'invoice_id': record.get('invoice_id'),
                'old_data': old_data,
                'new_data': new_data,
                'updated_fields': updated_fields
            }
            
            processed_records.append(processed_record)

        response_data = {
            "records": processed_records,
            "counts": {
                "add_count": add_count,
                "update_count": update_count,
                "ignore_count": ignore_count,
                "total_count": total_count
            },
            "requested_ids": id_list,
            "found_ids": [record.get('id') for record in processed_records]
        }
        
        return ResponseService.response("SUCCESS", response_data, "data_get")
            
    except Exception as e:
        print("Error in mapping_attribute_history:", str(e))
        print("Error type:", type(e))
        return ResponseService.response("NOT_FOUND", str(e), "processing_error")



@csrf_exempt
@api_view(["GET"])
def single_payment_uploads(request,id):



    return ResponseService.response("SUCCESS",[],"data_get") 


