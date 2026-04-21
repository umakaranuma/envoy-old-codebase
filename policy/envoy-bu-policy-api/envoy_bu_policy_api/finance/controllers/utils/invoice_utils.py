from decimal import Decimal, InvalidOperation
from django.utils import timezone
from mServices import QueryBuilderService
from envoy_bu_policy_api.service import handle_entity
from envoy_bu_policy_api.finance.config.transaction_types import (
    get_transaction_type_by_name,
    get_note_type_for_transaction,
    is_commissionable,
)
from envoy_bu_policy_api.finance.controllers.utils.commission.main import calculate_commission_amounts
from envoy_bu_policy_api.finance.controllers.utils.general_ledger_utils import create_invoice_general_ledger
from envoy_bu_policy_api.finance.controllers.utils.commission.base_calculator import get_commission_calculation_mode


def ensure_finance_invoice_statuses_exist():
    """
    Ensure all required finance invoice statuses exist in the core_status table.
    Creates them if they don't exist.
    """
    required_statuses = [
        {
            "name": "Pending",
            "description": "Not paid any amount against it",
            "type": "invoice",
            "module": "finance_invoice",
            "color": "#FFA500",
            "sort_index": 1
        },
        {
            "name": "Partially Paid",
            "description": "A portion of the invoice amount has been received",
            "type": "invoice",
            "module": "finance_invoice",
            "color": "#FFD700",
            "sort_index": 2
        },
        {
            "name": "Paid",
            "description": "Full payment has been received",
            "type": "invoice",
            "module": "finance_invoice",
            "color": "#28a745",
            "sort_index": 3
        },
        {
            "name": "Overdue",
            "description": "Payment deadline has passed and the invoice remains unpaid",
            "type": "invoice",
            "module": "finance_invoice",
            "color": "#dc3545",
            "sort_index": 4
        },
        {
            "name": "Cancelled",
            "description": "When a policy has been cancelled",
            "type": "invoice",
            "module": "finance_invoice",
            "color": "#343a40",
            "sort_index": 5
        },
        {
            "name": "Refunded",
            "description": "When a refund endorsement is done",
            "type": "invoice",
            "module": "finance_invoice",
            "color": "#6c757d",
            "sort_index": 6
        }
    ]
    
    for status_data in required_statuses:
        # Check if status with this name already exists
        existing_status = QueryBuilderService("core_status")\
            .where("name", status_data["name"])\
            .first()
        
        if existing_status:
            print(f"Status already exists: {status_data['name']}")
        else:
            # Status doesn't exist, create it
            QueryBuilderService("core_status").insert(status_data)
            print(f"Created status: {status_data['name']}")


def get_finance_invoice_status_id(status_name):
    """
    Get the status ID for a given finance invoice status name.
    Returns None if status doesn't exist.
    """
    # Find status by name (ignore module)
    status = QueryBuilderService("core_status")\
        .where("name", status_name)\
        .first()
    
    return status["id"] if status else None


def get_or_create_finance_invoice_status(status_name):
    """
    Get a finance invoice status ID, creating it if it doesn't exist.
    This is a safer way to ensure statuses exist before using them.
    
    Args:
        status_name (str): Name of the status to get or create
        
    Returns:
        int: Status ID
    """
    # First try to get existing status
    status_id = get_finance_invoice_status_id(status_name)
    if status_id:
        return status_id
    
    # If not found, ensure all statuses exist and try again
    ensure_finance_invoice_statuses_exist()
    status_id = get_finance_invoice_status_id(status_name)
    
    if status_id:
        return status_id
    
    # If still not found, something went wrong
    print(f"Warning: Could not find or create finance invoice status '{status_name}'")
    return None


def update_existing_finance_invoices_with_status():
    """
    Update existing finance invoices that don't have a status.
    This function should be run after seeding the statuses.
    """
    try:
        # Ensure statuses exist
        ensure_finance_invoice_statuses_exist()
        
        # Get pending status ID
        pending_status_id = get_or_create_finance_invoice_status("Pending")
        
        if not pending_status_id:
            print("Could not get pending status ID")
            return
        
        # Update invoices without status to have "Pending" status
        updated_count = QueryBuilderService("crmf_invoices")\
            .whereNull("status_id")\
            .update({"status_id": pending_status_id})
        
        print(f"Updated {updated_count} existing finance invoices with 'Pending' status")
        
        # Update invoices with payment amounts to have appropriate status
        # Fully paid invoices
        paid_status_id = get_or_create_finance_invoice_status("Paid")
        if paid_status_id:
            paid_count = QueryBuilderService("crmf_invoices")\
                .where("paid_amount", ">", 0)\
                .where("outstanding_amount", "=", 0)\
                .update({"status_id": paid_status_id})
            print(f"Updated {paid_count} fully paid invoices with 'Paid' status")
        
        # Partially paid invoices
        partially_paid_status_id = get_or_create_finance_invoice_status("Partially Paid")
        if partially_paid_status_id:
            partially_paid_count = QueryBuilderService("crmf_invoices")\
                .where("paid_amount", ">", 0)\
                .where("outstanding_amount", ">", 0)\
                .update({"status_id": partially_paid_status_id})
            print(f"Updated {partially_paid_count} partially paid invoices with 'Partially Paid' status")
        
        # Overdue invoices (past due date)
        overdue_status_id = get_or_create_finance_invoice_status("Overdue")
        if overdue_status_id:
            from django.utils import timezone
            today = timezone.now().date()
            overdue_count = QueryBuilderService("crmf_invoices")\
                .where("due_date", "<", today)\
                .where("outstanding_amount", ">", 0)\
                .update({"status_id": overdue_status_id})
            print(f"Updated {overdue_count} overdue invoices with 'Overdue' status")
        
        return True
        
    except Exception as e:
        print(f"Error updating existing finance invoices: {str(e)}")
        return False


def update_invoice_status_after_payment(invoice_id):
    """
    Safely update invoice status based on payment amounts.
    This function should be called after any payment is created or updated.
    
    Args:
        invoice_id (int): The ID of the invoice to update
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure statuses exist
        ensure_finance_invoice_statuses_exist()
        
        # Get current invoice data
        invoice = QueryBuilderService("crmf_invoices")\
            .select("id", "paid_amount", "outstanding_amount", "status_id")\
            .where("id", invoice_id)\
            .first()
        
        if not invoice:
            print(f"Invoice {invoice_id} not found")
            return False
        
        # Debug: Print invoice data to see the actual format
        print(f"Debug - Invoice {invoice_id} data: {invoice}")
        print(f"Debug - paid_amount type: {type(invoice.get('paid_amount'))}, value: {invoice.get('paid_amount')}")
        print(f"Debug - outstanding_amount type: {type(invoice.get('outstanding_amount'))}, value: {invoice.get('outstanding_amount')}")
        
        # Safely extract and convert amounts
        paid_amount_raw = invoice.get("paid_amount")
        outstanding_amount_raw = invoice.get("outstanding_amount")
        
        # Handle different data types safely
        if isinstance(paid_amount_raw, dict):
            paid_amount_raw = paid_amount_raw.get('value', '0.00') if 'value' in paid_amount_raw else '0.00'
        elif paid_amount_raw is None:
            paid_amount_raw = '0.00'
            
        if isinstance(outstanding_amount_raw, dict):
            outstanding_amount_raw = outstanding_amount_raw.get('value', '0.00') if 'value' in outstanding_amount_raw else '0.00'
        elif outstanding_amount_raw is None:
            outstanding_amount_raw = '0.00'
        
        # Convert amounts to Decimal for accurate comparison
        try:
            paid_amount = Decimal(str(paid_amount_raw))
            outstanding_amount = Decimal(str(outstanding_amount_raw))
        except (ValueError, TypeError) as e:
            print(f"Error converting amounts to Decimal: {e}")
            print(f"paid_amount_raw: {paid_amount_raw}, outstanding_amount_raw: {outstanding_amount_raw}")
            # Fallback to safe defaults
            paid_amount = Decimal('0.00')
            outstanding_amount = Decimal('0.00')
        
        print(f"Debug - Converted amounts: paid_amount={paid_amount}, outstanding_amount={outstanding_amount}")
        
        # Determine appropriate status
        if paid_amount == 0:
            # No payment received
            status_name = "Pending"
        elif outstanding_amount == 0:
            # Fully paid
            status_name = "Paid"
        elif paid_amount > 0 and outstanding_amount > 0:
            # Partially paid
            status_name = "Partially Paid"
        else:
            # Fallback to Pending
            status_name = "Pending"
        
        print(f"Debug - Determined status: {status_name}")
        
        # Get status ID
        status_id = get_or_create_finance_invoice_status(status_name)
        if not status_id:
            print(f"Could not get status ID for '{status_name}'")
            return False
        
        # Update invoice status if it's different from current
        current_status_id = invoice.get("status_id")
        if current_status_id != status_id:
            update_result = QueryBuilderService("crmf_invoices")\
                .where("id", invoice_id)\
                .update({"status_id": status_id})
            
            # QueryBuilderService.update() returns the filtered_data dict, not row count
            # Check if update_result is truthy (dict with data) to confirm update was attempted
            if update_result and isinstance(update_result, dict) and len(update_result) > 0:
                print(f"Updated invoice {invoice_id} status to '{status_name}' (ID: {status_id})")
            else:
                print(f"No rows updated for invoice {invoice_id}")
        else:
            print(f"Invoice {invoice_id} already has correct status: {status_name}")
        
        return True
        
    except Exception as e:
        print(f"Error updating invoice status for invoice {invoice_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def cleanup_complex_status_names():
    """
    Clean up the complex status names like "Pending (Finance Invoice)" and replace them with simple names.
    This function should be run once to fix the existing complex status names.
    """
    try:
        # Define the mapping of complex names to simple names
        name_mapping = {
            "Pending (Finance Invoice)": "Pending",
            "Partially Paid (Finance Invoice)": "Partially Paid",
            "Paid (Finance Invoice)": "Paid",
            "Overdue (Finance Invoice)": "Overdue",
            "Cancelled (Finance Invoice)": "Cancelled",
            "Refunded (Finance Invoice)": "Refunded"
        }
        
        updated_count = 0
        
        for complex_name, simple_name in name_mapping.items():
            # Check if complex name exists
            existing_complex = QueryBuilderService("core_status")\
                .where("name", complex_name)\
                .first()
            
            if existing_complex:
                # Check if simple name already exists
                existing_simple = QueryBuilderService("core_status")\
                    .where("name", simple_name)\
                    .first()
                
                if existing_simple:
                    # Simple name exists, delete the complex one
                    QueryBuilderService("core_status")\
                        .where("id", existing_complex["id"])\
                        .delete()
                    print(f"Deleted complex status: {complex_name} (simple name already exists)")
                else:
                    # Simple name doesn't exist, rename complex to simple
                    QueryBuilderService("core_status")\
                        .where("id", existing_complex["id"])\
                        .update({"name": simple_name})
                    print(f"Renamed complex status: {complex_name} → {simple_name}")
                    updated_count += 1
        
        print(f"Cleanup completed. Updated {updated_count} status names.")
        return True
        
    except Exception as e:
        print(f"Error cleaning up complex status names: {str(e)}")
        return False


def safe_decimal(value):
    """Convert value to Decimal, return None if invalid"""
    try:
        if value is None or value == "":
            return None
        return Decimal(str(value)).quantize(Decimal(".01"))
    except (InvalidOperation, ValueError, TypeError):
        return None


def safe_int(value):
    """Convert value to integer, return None if invalid"""
    try:
        if value is None or value == "":
            return None
        return int(float(str(value)))
    except (ValueError, TypeError):
        return None


def generate_invoice_id():
    try:
        last = QueryBuilderService("crmf_invoices").select("MAX(id) as max_id").first()
        last_id = last.get("max_id")
        if last_id is None:
            return "INV-1"
        current_num = int(last_id or 0) + 1
        while True:
            candidate = f"INV-{current_num}"
            exists = QueryBuilderService("crmf_invoices").select("id").where("invoice_number", candidate).first()
            if not exists:
                return candidate
            current_num += 1
        #if the invoice number already exists, increment the current number
        # invoice_number = f"INV-{last_id + 1}"
        # exists = QueryBuilderService("crmf_invoices").select("id").where("invoice_number", invoice_number).first()
        # if exists:
        #     generate_invoice_id()
        # return invoice_number
    except Exception as e:
        try:
            count = QueryBuilderService("crmf_invoices").select("COUNT(*) as count").first()
            count_value = count.get("count")
            if count_value is None:
                return "INV-1"
            return f"INV-{count_value + 1}"
        except:
            return "INV-1"

def generate_invoice_for_issued_policy(issued_id, is_update=False, user=None, sales_agent_id=None):
    """
    Generate or update an invoice for an issued policy
    """
    
    try:
        print(f"DEBUG: Starting invoice generation for issued policy {issued_id}")
        print(f"DEBUG: Parameters - is_update: {is_update}, user: {user}, sales_agent_id: {sales_agent_id}")
        
        # Enhanced debug logging for the query
        print(f"DEBUG: Querying issued policy data for ID: {issued_id}")
        instance = (
            QueryBuilderService("crmp_issued_policies as ip")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .select(
                "ip.id",
                "ip.credit_period_days",
                "ip.credit_age_days",
                "ip.premium_amount",
                "ip.policy_effective_date",
                "ip.policy_base_id",
                "pb.insurer_id",
                "pb.customer_id",
                "pb.product_id",
                "pb.product_group_id",
                "pb.sales_agent_id",
                "ip.is_renewal",
            )
            .where("ip.id", issued_id)
            .first()
        )

        if not instance:
            print(f"DEBUG: No instance found for issued policy {issued_id}")
            return None
        
        print(f"DEBUG: Found instance: {instance}")
        
        # Validate required fields from instance
        required_fields = ['premium_amount', 'policy_effective_date', 'policy_base_id']
        missing_fields = []
        for field in required_fields:
            if field not in instance or instance[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"ERROR: Missing required fields in issued policy data: {missing_fields}")
            print(f"DEBUG: Cannot generate invoice without these fields")
            return None
        
        # Validate premium amount is valid
        try:
            premium_amount = Decimal(str(instance.get("premium_amount", 0)))
            if premium_amount <= 0:
                print(f"ERROR: Invalid premium amount: {premium_amount}")
                return None
            print(f"DEBUG: Premium amount validated: {premium_amount}")
        except (ValueError, TypeError) as e:
            print(f"ERROR: Invalid premium amount format: {instance.get('premium_amount')} - {str(e)}")
            return None
        
        # Get transaction type based on is_renewal
        is_renewal_flag = instance.get("is_renewal")
        if is_renewal_flag:
            transaction_type = get_transaction_type_by_name("Renewal")
            print(f"DEBUG: Policy is a renewal (is_renewal={is_renewal_flag}) - using Renewal transaction type")
        else:
            transaction_type = get_transaction_type_by_name("New Business")
            print(f"DEBUG: Policy is new business (is_renewal={is_renewal_flag}) - using New Business transaction type")
        
        if not transaction_type:
            print(f"ERROR: No transaction type found for is_renewal: {is_renewal_flag}")
            return None
        
        print(f"DEBUG: Found transaction type: {transaction_type} (id={transaction_type['id']}, name={transaction_type['name']})")
        
        # Get note type from configuration
        note_type = get_note_type_for_transaction(transaction_type["id"])
        if not note_type:
            print(f"DEBUG: No note type found for transaction_type_id: {transaction_type['id']}")
            return None
        
        print(f"DEBUG: Found note type: {note_type}")
        

        # Validate required fields
        premium_amount = safe_decimal(instance.get("premium_amount"))
        if premium_amount is None:
            print(f"DEBUG: Premium amount is None for instance: {instance.get('premium_amount')}")
            return None
        
        print(f"DEBUG: Premium amount: {premium_amount}")

        insurer_id = instance.get("insurer_id")
        customer_id = instance.get("customer_id")
        product_id = instance.get("product_id")
        # Use the passed sales_agent_id if provided, otherwise fallback to instance value
        effective_sales_agent_id = sales_agent_id if sales_agent_id is not None else instance.get("sales_agent_id")
        
        # Use enhanced product mapping to resolve native_product_id from policy_base
        from .product_mapping_utils import resolve_native_product_id, validate_commission_setup_exists
        
        # Prepare policy base data for mapping
        policy_base_data = {
            'product_id': product_id,
            'product_group_id': instance.get("product_group_id"),
            'insurer_id': insurer_id
        }
        
        print(f"DEBUG: Policy base data for mapping: {policy_base_data}")
        
        # Resolve native product ID with comprehensive mapping
        mapping_result = resolve_native_product_id(
            policy_base_data, 
            insurer_id, 
            None  # We'll get transaction_type later
        )
        
        if mapping_result['error']:
            print(f"ERROR: Product mapping failed: {mapping_result['error']}")
            print(f"DEBUG: Cannot create finance invoice due to product mapping failure")
            return None
        
        # Update product_id with resolved native product ID
        product_id = mapping_result['native_product_id']
        print(f"DEBUG: Resolved native product: {mapping_result['product_name']} (ID: {product_id}) via {mapping_result['mapping_type']}")
        
        # Enhanced validation with better error handling
        missing_fields = []
        if not insurer_id:
            missing_fields.append("insurer_id")
        if not customer_id:
            missing_fields.append("customer_id")
        if not product_id:
            missing_fields.append("product_id")
        
        if missing_fields:
            print(f"DEBUG: Missing required fields - {missing_fields}")
            print(f"DEBUG: Current values - insurer_id: {insurer_id}, customer_id: {customer_id}, product_id: {product_id}")
            
            # Try to get missing fields from policy base if available
            if not product_id or not insurer_id or not customer_id:
                print(f"DEBUG: Attempting to fetch missing fields from policy base...")
                policy_base_id = instance.get("policy_base_id")
                print(f"DEBUG: Policy base ID: {policy_base_id}")
                
                if policy_base_id:
                    policy_base_data = (
                        QueryBuilderService("crmp_policy_base")
                        .select("product_id", "insurer_id", "customer_id")
                        .where("id", policy_base_id)
                        .first()
                    )
                    
                    if policy_base_data:
                        if not product_id:
                            product_id = policy_base_data.get("product_id")
                            print(f"DEBUG: Retrieved product_id from policy_base: {product_id}")
                        if not insurer_id:
                            insurer_id = policy_base_data.get("insurer_id")
                            print(f"DEBUG: Retrieved insurer_id from policy_base: {insurer_id}")
                        if not customer_id:
                            customer_id = policy_base_data.get("customer_id")
                            print(f"DEBUG: Retrieved customer_id from policy_base: {customer_id}")
                    else:
                        print(f"DEBUG: No policy base data found for policy_base_id: {policy_base_id}")
                else:
                    print(f"DEBUG: No policy_base_id found in instance data")
            
            # Final validation after fallback attempts
            if not all([insurer_id, customer_id, product_id]):
                print(f"DEBUG: Still missing required fields after fallback - insurer_id: {insurer_id}, customer_id: {customer_id}, product_id: {product_id}")
                
                # Additional fallback: Try to get the data from the issued policy record directly
                print(f"DEBUG: Attempting final fallback - getting data from issued policy record...")
                issued_policy_data = (
                    QueryBuilderService("crmp_issued_policies")
                    .select("policy_base_id")
                    .where("id", issued_id)
                    .first()
                )
                
                if issued_policy_data and issued_policy_data.get("policy_base_id"):
                    final_policy_base_data = (
                        QueryBuilderService("crmp_policy_base")
                        .select("product_id", "insurer_id", "customer_id")
                        .where("id", issued_policy_data.get("policy_base_id"))
                        .first()
                    )
                    
                    if final_policy_base_data:
                        if not product_id:
                            product_id = final_policy_base_data.get("product_id")
                        if not insurer_id:
                            insurer_id = final_policy_base_data.get("insurer_id")
                        if not customer_id:
                            customer_id = final_policy_base_data.get("customer_id")
                        print(f"DEBUG: Final fallback successful - product_id: {product_id}, insurer_id: {insurer_id}, customer_id: {customer_id}")
                
                # If still missing required fields, return None
                if not all([insurer_id, customer_id, product_id]):
                    print(f"DEBUG: All fallback attempts failed. Cannot generate invoice.")
                    print(f"DEBUG: Final state - insurer_id: {insurer_id}, customer_id: {customer_id}, product_id: {product_id}")
                    return None
        
        print(f"DEBUG: All required fields present - insurer_id: {insurer_id}, customer_id: {customer_id}, product_id: {product_id}, sales_agent_id: {effective_sales_agent_id}")

        # Use enhanced product mapping to resolve native_product_id
        from .product_mapping_utils import resolve_native_product_id, get_product_mapping_summary, validate_commission_setup_exists
        
        # Prepare policy base data for mapping
        policy_base_data = {
            'product_id': product_id,
            'product_group_id': instance.get("product_group_id"),
            'insurer_id': insurer_id
        }
        
        # Resolve native product ID with comprehensive mapping
        mapping_result = resolve_native_product_id(
            policy_base_data, 
            insurer_id, 
            transaction_type.get("id") if transaction_type else None
        )
        
        if mapping_result['error']:
            print(f"ERROR: {mapping_result['error']}")
            print(f"DEBUG: Cannot create finance invoice due to product mapping failure")
            return None
        
        # Update product_id with resolved native product ID
        product_id = mapping_result['native_product_id']
        print(f"DEBUG: Resolved native product: {mapping_result['product_name']} (ID: {product_id}) via {mapping_result['mapping_type']}")
        
        # Validate that commission setup exists for this product
        # Skip validation for deduction types (Refund=4, Cancellation=5) as they use original invoice's commission setup
        transaction_type_id = transaction_type.get("id") if transaction_type else None
        is_deduction = transaction_type_id in [4, 5]  # Refund or Cancellation
        if not is_deduction and not validate_commission_setup_exists(product_id, insurer_id, transaction_type_id):
            print(f"WARNING: No commission setup found for product_id {product_id}, insurer_id {insurer_id}, transaction_type {transaction_type_id}")
            print(f"DEBUG: Commission calculations may fail, but invoice will be created")
        elif is_deduction:
            print(f"DEBUG: Skipping commission setup validation for deduction type (transaction_type={transaction_type_id}) - will use original invoice's commission setup")
        
        # Validate that the insurer_id exists in core_service_providers table
        if insurer_id:
            insurer_exists = (
                QueryBuilderService("core_service_providers")
                .where("id", insurer_id)
                .first()
            )
            if not insurer_exists:
                print(f"ERROR: Insurer ID {insurer_id} does not exist in core_service_providers table")
                print(f"DEBUG: Cannot create finance invoice due to foreign key constraint")
                return None
            else:
                print(f"DEBUG: Insurer ID {insurer_id} validated successfully")

        # Validate that the customer_id exists in core_customers table
        if customer_id:
            customer_exists = (
                QueryBuilderService("core_customers")
                .where("id", customer_id)
                .first()
            )
            if not customer_exists:
                print(f"ERROR: Customer ID {customer_id} does not exist in core_customers table")
                print(f"DEBUG: Cannot create finance invoice due to foreign key constraint")
                return None
            else:
                print(f"DEBUG: Customer ID {customer_id} validated successfully")

        invoice_number = generate_invoice_id()
        credit_period_days = safe_int(instance.get("credit_period_days"))
        if credit_period_days is None:
            credit_period_days = 0

        due_date = timezone.now().date() + timezone.timedelta(days=credit_period_days)
        invoice_type = note_type.lower().replace(" ", "_")
        
        # Ensure finance invoice statuses exist
        ensure_finance_invoice_statuses_exist()
        
        # Get pending status ID for new invoices
        pending_status_id = get_or_create_finance_invoice_status("Pending")
        
        invoice_data = {
            "invoice_number": invoice_number,
            "transaction_type_id": transaction_type["id"],
            "invoice_date": instance.get("policy_effective_date"),
            "invoice_type": invoice_type,
            "invoice_amount": premium_amount,
            "issued_policy_id": issued_id,
            "paid_amount": Decimal("0.00"),
            "outstanding_amount": premium_amount,
            "remarks": "Updated" if is_update else "Created",
            "credit_age_days": safe_int(instance.get("credit_age_days")) or 0,
            "credit_period_days": credit_period_days,
            "due_date": due_date,
            "last_paid_date": None,
            "insurer_id": insurer_id,
            "insured_id": customer_id,
            "product_id": product_id,
            "status_id": pending_status_id,  # Set initial status to Pending
        }
        
        print(f"DEBUG: Invoice data being created with issued_policy_id: {issued_id}")
        print(f"DEBUG: Full invoice data: {invoice_data}")

        entity_data = {"type": "invoice", "approvel_status": False}
        entity_id = handle_entity(
            entity_data,
            entity_id=None if not is_update else instance.get("entity_id"),
            user=user,
        )
        invoice_data["entity_id"] = entity_id

        if is_update:
            update_result = QueryBuilderService("crmf_invoices").where("issued_policy_id", issued_id).update(invoice_data)
            # Ensure invoice_id is the integer primary key, not the updated data dict
            existing = QueryBuilderService("crmf_invoices").select("id").where("issued_policy_id", issued_id).first()
            invoice_id = existing.get("id") if isinstance(existing, dict) else existing
            print(f"DEBUG: Updated invoice. Resolved invoice_id: {invoice_id}; update_result: {update_result}")
            # If no existing invoice to update, create a new one now
            if not invoice_id:
                print("DEBUG: No existing invoice found for update; creating a new invoice")
                # Regenerate a unique invoice number to avoid duplicates
                base_number = generate_invoice_id()
                try:
                    # Ensure uniqueness by incrementing if needed
                    current_num = int(str(base_number).split("-")[-1]) if base_number and "-" in str(base_number) else 1
                except Exception:
                    current_num = 1
                while True:
                    candidate = f"INV-{current_num}"
                    existing_num = QueryBuilderService("crmf_invoices").select("id").where("invoice_number", candidate).first()
                    if not existing_num:
                        invoice_data["invoice_number"] = candidate
                        break
                    current_num += 1
                insert_result = QueryBuilderService("crmf_invoices").insert(invoice_data)
                invoice_id = insert_result.get("id") if isinstance(insert_result, dict) else insert_result
                print(f"DEBUG: Created invoice with ID: {invoice_id}")
        else:
            invoice_result = QueryBuilderService("crmf_invoices").insert(invoice_data)
            invoice_id = invoice_result.get("id") if isinstance(invoice_result, dict) else invoice_result
            print(f"DEBUG: Created invoice with ID: {invoice_id}")
            print(f"DEBUG: Invoice created with issued_policy_id: {issued_id}")

            # Create general ledger entry with proper data structure
            if invoice_id:
                ledger_data = {
                    "id": invoice_id,
                    "invoice_number": invoice_data["invoice_number"]
                }
                create_invoice_general_ledger(
                    invoice_data=ledger_data,
                    transaction_type=transaction_type,
                    amount=premium_amount,
                    user=user
                )
        
        # Always calculate commissions for commissionable transactions.
        # Strict matching is enforced inside calculate_commission_amounts using policy_base.product_id/product_group_id.
        if invoice_id and is_commissionable(transaction_type["id"]):
            # Check if commissions already exist for this invoice
            existing_brokerage = QueryBuilderService("crmf_brokerage_commission").where("invoice_id", invoice_id).first()
            commissions_exist = existing_brokerage is not None
            
            if not commissions_exist:
                print(f"DEBUG: Transaction is commissionable (type_id={transaction_type['id']}, name={transaction_type['name']}) and no commissions exist - calculating commission amounts")
                print(f"DEBUG: Commission calculation parameters - product_id: {product_id}, insurer_id: {insurer_id}, sales_agent_id: {effective_sales_agent_id}, invoice_amount: {premium_amount}")
                try:
                    calculation_mode = get_commission_calculation_mode()
                    commission_result = calculate_commission_amounts(
                        invoice_id=invoice_id,
                        transaction_type_id=transaction_type["id"],
                        product_id=product_id,
                        insurer_id=insurer_id,
                        sales_agent_id=effective_sales_agent_id,
                        invoice_amount=premium_amount,
                        paid_amount=Decimal("0.00"),
                        calculation_mode=calculation_mode,
                        user=user,
                    )
                    if commission_result and commission_result[0]:
                        print(f"DEBUG: Commission amounts calculated successfully - brokerage_commission_id: {commission_result[0]}")
                    else:
                        print(f"WARNING: Commission calculation returned no result - commissions may not have been created")
                except Exception as commission_error:
                    print(f"ERROR: Failed to calculate commission amounts: {str(commission_error)}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"DEBUG: Commissions already exist for invoice_id {invoice_id} - skipping commission generation")
        else:
            if not invoice_id:
                print(f"DEBUG: No invoice_id available - skipping commission calculation")
            elif not is_commissionable(transaction_type["id"]):
                print(f"DEBUG: Transaction type {transaction_type['name']} (id={transaction_type['id']}) is not commissionable - skipping commission calculation")

        print(f"DEBUG: Invoice generation completed successfully for issued policy {issued_id}")
        return invoice_id
    except Exception as e:
        print(f"Error generating invoice for issued policy {issued_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def generate_invoice_for_endorsement(endorsement_id, is_update=False, user=None, invoice_data=None):
    print(f"DEBUG: generate_invoice_for_endorsement called with endorsement_id: {endorsement_id}")
    print(f"DEBUG: is_update: {is_update}, user: {user}, invoice_data: {invoice_data}")
    
    try:
        print(f"DEBUG: Querying endorsement details for ID: {endorsement_id}")
        instance = (
            QueryBuilderService("crmp_endorsements_details as ed")
            .leftJoin("crmp_endorsement_requests as er", "er.id", "ed.endorsement_request_id")
            .leftJoin("crmp_endorsement_types as et", "et.id", "er.endorsement_type_id")
            .leftJoin("crmp_issued_policies as ip", "ip.id", "er.issued_policy_id")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .select(
                "ed.id",
                "ed.credit_period_days",
                "ed.credit_age_days",
                "ed.endorsement_id",
                "er.requested_amount",
                "er.cover_value",
                "er.credit_period",
                "pb.customer_id as insured_id",
                "er.issued_policy_id",
                "et.name as endorsement_type",
                "pb.product_id",
                "pb.insurer_id",
            )
            .where("ed.id", endorsement_id)
            .first()
        )
        print(f"DEBUG: Endorsement instance found: {instance}")

        if not instance:
            print(f"ERROR: No endorsement instance found for ID: {endorsement_id}")
            return None

        # Get transaction type - default to Addition if not found
        endorsement_type = str(instance.get("endorsement_type", "")).lower()
        print(f"DEBUG: Endorsement type: {endorsement_type}")
        transaction_type = get_transaction_type_by_name(endorsement_type) or get_transaction_type_by_name("Addition")
        print(f"DEBUG: Transaction type: {transaction_type}")
        if not transaction_type:
            print(f"ERROR: No transaction type found for endorsement type: {endorsement_type}")
            return None

        # Get note type from configuration
        note_type = get_note_type_for_transaction(transaction_type["id"])
        print(f"DEBUG: Note type: {note_type}")
        if not note_type:
            print(f"ERROR: No note type found for transaction type: {transaction_type['id']}")
            return None

        # Validate required fields
        base_amount = safe_decimal(instance.get("requested_amount") or instance.get("cover_value"))
        print(f"DEBUG: Base amount: {base_amount}")
        if base_amount is None:
            print(f"ERROR: No base amount found (requested_amount: {instance.get('requested_amount')}, cover_value: {instance.get('cover_value')})")
            return None

        insurer_id = instance.get("insurer_id")
        insured_id = instance.get("insured_id")
        product_id = instance.get("product_id")
        print(f"DEBUG: insurer_id: {insurer_id}, insured_id: {insured_id}, product_id: {product_id}")
        
        issued_policy_id = instance.get("issued_policy_id")
        
        # Use enhanced product mapping to resolve native_product_id
        from .product_mapping_utils import resolve_native_product_id, validate_commission_setup_exists
        
        # Get product_group_id from policy_base if needed
        product_group_id = None
        if not product_id and issued_policy_id:
            print(f"DEBUG: No product_id found, getting product_group_id from policy_base")
            policy_base_data = (
                QueryBuilderService("crmp_issued_policies as ip")
                .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
                .select("pb.product_group_id")
                .where("ip.id", issued_policy_id)
                .first()
            )
            
            if policy_base_data:
                product_group_id = policy_base_data.get("product_group_id")
                print(f"DEBUG: Found product_group_id: {product_group_id}")
        
        # Prepare policy base data for mapping
        policy_base_data = {
            'product_id': product_id,
            'product_group_id': product_group_id,
            'insurer_id': insurer_id
        }
        
        print(f"DEBUG: Policy base data for mapping: {policy_base_data}")
        
        # Resolve native product ID with comprehensive mapping
        mapping_result = resolve_native_product_id(
            policy_base_data, 
            insurer_id, 
            transaction_type.get("id") if transaction_type else None
        )
        
        if mapping_result['error']:
            print(f"ERROR: Product mapping failed: {mapping_result['error']}")
            print(f"DEBUG: Cannot create finance invoice due to product mapping failure")
            return None
        
        # Update product_id with resolved native product ID
        product_id = mapping_result['native_product_id']
        print(f"DEBUG: Resolved native product: {mapping_result['product_name']} (ID: {product_id}) via {mapping_result['mapping_type']}")
        
        # Validate that commission setup exists for this product
        # Skip validation for deduction types (Refund=4, Cancellation=5) as they use original invoice's commission setup
        transaction_type_id = transaction_type.get("id") if transaction_type else None
        is_deduction = transaction_type_id in [4, 5]  # Refund or Cancellation
        if not is_deduction and not validate_commission_setup_exists(product_id, insurer_id, transaction_type_id):
            print(f"WARNING: No commission setup found for product_id {product_id}, insurer_id {insurer_id}, transaction_type {transaction_type_id}")
            print(f"DEBUG: Commission calculations may fail, but invoice will be created")
        elif is_deduction:
            print(f"DEBUG: Skipping commission setup validation for deduction type (transaction_type={transaction_type_id}) - will use original invoice's commission setup")
        
        # Get sales_agent_id from the policy base
        sales_agent_id = None
        if issued_policy_id:
            policy_info = QueryBuilderService("crmp_issued_policies as ip")\
                .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")\
                .select("pb.sales_agent_id")\
                .where("ip.id", issued_policy_id)\
                .first()
            if policy_info:
                sales_agent_id = policy_info.get("sales_agent_id")
                print(f"DEBUG: Found sales_agent_id: {sales_agent_id}")
            else:
                print(f"DEBUG: No policy info found for issued_policy_id: {issued_policy_id}")
        
        if not all([insurer_id, insured_id, product_id, issued_policy_id]):
            print(f"ERROR: Missing required fields - insurer_id: {insurer_id}, insured_id: {insured_id}, product_id: {product_id}, issued_policy_id: {issued_policy_id}")
            return None

        invoice_number = generate_invoice_id()
        # Get credit_period_days from endorsement details, fallback to request if not set
        credit_period_days = safe_int(instance.get("credit_period_days"))
        if credit_period_days is None or credit_period_days == 0:
            # Fallback to request's credit_period
            request_credit_period = safe_int(instance.get("credit_period"))
            if request_credit_period and request_credit_period > 0:
                credit_period_days = request_credit_period
            else:
                credit_period_days = 0

        due_date = timezone.now().date() + timezone.timedelta(days=credit_period_days)
        invoice_type = note_type.lower().replace(" ", "_")

        # Ensure finance invoice statuses exist
        ensure_finance_invoice_statuses_exist()
        
        # Handle payment amounts based on transaction type
        if invoice_data and "paid_amount" in invoice_data and "outstanding_amount" in invoice_data:
            # Use the provided invoice_data from endorsement processing
            paid_amount = Decimal(str(invoice_data["paid_amount"]))
            outstanding_amount = Decimal(str(invoice_data["outstanding_amount"]))
            total_amount = Decimal(str(invoice_data.get("total_amount", base_amount)))
        else:
            # Fallback to default logic
            if transaction_type["id"] == 5:  # Cancellations
                paid_amount = base_amount
                outstanding_amount = Decimal("0.00")
                total_amount = base_amount
            elif transaction_type["id"] == 4:  # Refund
                paid_amount = Decimal("0.00")
                outstanding_amount = base_amount
                total_amount = base_amount
            else:
                paid_amount = Decimal("0.00")
                outstanding_amount = base_amount
                total_amount = base_amount

        # Get appropriate status based on transaction type
        if transaction_type["id"] == 5:  # Cancellations
            status_id = get_or_create_finance_invoice_status("Cancelled")
        elif transaction_type["id"] == 4:  # Refund
            status_id = get_or_create_finance_invoice_status("Refunded")
        else:
            status_id = get_or_create_finance_invoice_status("Pending")

        invoice_data = {
            "invoice_number": invoice_number,
            "transaction_type_id": transaction_type["id"],
            "invoice_date": timezone.now().date(),
            "invoice_type": invoice_type,
            "invoice_amount": total_amount,
            "endorsement_id": endorsement_id,
            "issued_policy_id": issued_policy_id,
            "product_id": product_id,
            "insured_id": insured_id,
            "insurer_id": insurer_id,
            "paid_amount": paid_amount,
            "outstanding_amount": outstanding_amount,
            "credit_age_days": safe_int(instance.get("credit_age_days")) or 0,
            "credit_period_days": credit_period_days,
            "due_date": due_date,
            "last_paid_date": None,
            "remarks": f"Endorsement {instance.get('endorsement_id', '')} - {'Updated' if is_update else 'Created'}",
            "status_id": status_id,  # Set appropriate status based on transaction type
        }

        print(f"DEBUG: Creating entity for invoice")
        entity_data = {"type": "invoice", "approvel_status": False}
        print(f"DEBUG: Entity data: {entity_data}")
        entity_id = handle_entity(
            entity_data,
            entity_id=None if not is_update else instance.get("entity_id"),
            user=user,
        )
        print(f"DEBUG: Created entity with ID: {entity_id}")
        invoice_data["entity_id"] = entity_id

        print(f"DEBUG: About to create/update invoice")
        print(f"DEBUG: Invoice data before database operation: {invoice_data}")
        
        if is_update:
            print(f"DEBUG: Updating existing invoice for endorsement_id: {endorsement_id}")
            invoice_result = QueryBuilderService("crmf_invoices").where("endorsement_id", endorsement_id).update(invoice_data)
            # Normalize invoice_id - handle both dict and int returns
            if isinstance(invoice_result, dict):
                invoice_id = invoice_result.get("id")
            else:
                # If update returns the invoice, fetch it
                invoice_record = QueryBuilderService("crmf_invoices").where("endorsement_id", endorsement_id).first()
                invoice_id = invoice_record.get("id") if invoice_record else None
            print(f"DEBUG: Updated invoice with ID: {invoice_id}")
        else:
            print(f"DEBUG: Creating new invoice in database")
            try:
                invoice_result = QueryBuilderService("crmf_invoices").insert(invoice_data)
                # Normalize invoice_id - handle both dict and int returns
                invoice_id = invoice_result.get("id") if isinstance(invoice_result, dict) else invoice_result
                print(f"DEBUG: Successfully created invoice with ID: {invoice_id}")
            except Exception as insert_error:
                print(f"ERROR: Failed to insert invoice into database: {str(insert_error)}")
                import traceback
                traceback.print_exc()
                return None

            if invoice_id:
                print(f"DEBUG: Creating general ledger entry for invoice_id: {invoice_id}")
                try:
                    # Create general ledger entry
                    ledger_data = {
                        "id": invoice_id,
                        "invoice_number": invoice_data.get("invoice_number")
                    }
                    create_invoice_general_ledger(
                        invoice_data=ledger_data,
                        transaction_type=transaction_type,
                        amount=base_amount,
                        user=user
                    )
                    print(f"DEBUG: General ledger entry created successfully")
                except Exception as ledger_error:
                    print(f"ERROR: Failed to create general ledger entry: {str(ledger_error)}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"ERROR: No invoice_id returned from database insert")
                return None

        # Calculate commissions only if transaction is commissionable
        if invoice_id:
            print(f"DEBUG: Processing commissions for invoice_id: {invoice_id}")
            is_deduction = transaction_type["id"] in [4, 5]  # Refund or Cancellation
            print(f"DEBUG: Is deduction: {is_deduction}, transaction_type_id: {transaction_type['id']}")
            
            # Check if commissions already exist for this invoice
            existing_brokerage = QueryBuilderService("crmf_brokerage_commission").where("invoice_id", invoice_id).first()
            commissions_exist = existing_brokerage is not None
            
            if is_commissionable(transaction_type["id"]):
                # For Addition type (transaction_type_id = 2) and other commissionable types
                if not commissions_exist:
                    print(f"DEBUG: Transaction is commissionable (type_id={transaction_type['id']}) and no commissions exist - calculating commission amounts")
                    try:
                        # For commissionable transactions (Additions, New Business, Renewals)
                        calculation_mode = get_commission_calculation_mode()
                        calculate_commission_amounts(
                            invoice_id=invoice_id,
                            transaction_type_id=transaction_type["id"],
                            product_id=product_id,
                            insurer_id=insurer_id,
                            sales_agent_id=sales_agent_id,
                            invoice_amount=base_amount,
                            paid_amount=Decimal("0.00"),
                            calculation_mode=calculation_mode,
                            user=user,
                        )
                        print(f"DEBUG: Commission amounts calculated successfully")
                    except Exception as commission_error:
                        print(f"ERROR: Failed to calculate commission amounts: {str(commission_error)}")
                        import traceback
                        traceback.print_exc()
                else:
                    print(f"DEBUG: Commissions already exist for invoice_id {invoice_id} - skipping commission generation")
            elif is_deduction:
                print(f"DEBUG: Transaction is deduction - handling commission deduction")
                try:
                    # For deductions (Refunds, Cancellations) - handle commission deductions
                    from .commission.deduction_utils import handle_commission_deduction
                    # Normalize invoice_id for deduction handler
                    invoice_id_for_deduction = {"id": invoice_id} if isinstance(invoice_id, int) else invoice_id
                    
                    # Get the actual paid_amount from invoice_data if available
                    # For cancellations, paid_amount is set to base_amount when invoice is created
                    # For refunds, paid_amount is 0.00 when invoice is created
                    actual_paid_amount = Decimal("0.00")
                    if invoice_data and "paid_amount" in invoice_data:
                        actual_paid_amount = Decimal(str(invoice_data["paid_amount"]))
                    elif transaction_type["id"] == 5:  # Cancellations - already marked as paid
                        actual_paid_amount = base_amount
                    
                    print(f"DEBUG: Handling commission deduction with paid_amount: {actual_paid_amount} for transaction_type: {transaction_type['id']}")
                    handle_commission_deduction(
                        invoice_id=invoice_id_for_deduction,
                        transaction_type_id=transaction_type["id"],
                        product_id=product_id,
                        insurer_id=insurer_id,
                        sales_agent_id=sales_agent_id,
                        invoice_amount=base_amount,
                        paid_amount=actual_paid_amount,
                        calculation_mode=get_commission_calculation_mode(),
                        user=user,
                    )
                    print(f"DEBUG: Commission deduction handled successfully")
                except Exception as deduction_error:
                    print(f"ERROR: Failed to handle commission deduction: {str(deduction_error)}")
                    import traceback
                    traceback.print_exc()
            else:
                print(f"DEBUG: Transaction is not commissionable and not a deduction - skipping commission processing")
        else:
            print(f"ERROR: No invoice_id available for commission processing")

        print(f"DEBUG: Invoice generation completed - returning invoice_id: {invoice_id}")
        return invoice_id
    except Exception as e:
        print(f"Error in invoice generation for endorsement {endorsement_id}: {str(e)}")
        return None


def update_invoice_payment_details(invoice_id, paid_amount):
    """
    Update invoice payment details after a payment
    """
    if not invoice_id:
        return None

    try:
        invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()
        if not invoice:
            return None

        paid_amount = safe_decimal(paid_amount)
        current_paid = safe_decimal(invoice.get("paid_amount"))
        total_amount = safe_decimal(invoice.get("invoice_amount"))

        if any(amount is None for amount in [paid_amount, current_paid, total_amount]):
            return None

        new_paid_amount = (current_paid + paid_amount).quantize(Decimal(".01"))
        new_outstanding = (total_amount - new_paid_amount).quantize(Decimal(".01"))

        update_data = {
            "paid_amount": new_paid_amount,
            "outstanding_amount": new_outstanding,
            "last_paid_date": timezone.now().date(),
        }


        return QueryBuilderService("crmf_invoices").where("id", invoice_id).update(update_data)
    except Exception as e:
        print(f"Error updating invoice payment details: {str(e)}")
        return None
