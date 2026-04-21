from envoy_bu_policy_api.service import handle_entity
from decimal import Decimal
from envoy_bu_policy_api.policy.models.crmp_request_policy_invoices import (
    RequestPolicyInvoice,
)
from envoy_bu_policy_api.policy.models.crmp_issued_policies import IssuedPolicy
from envoy_bu_policy_api.policy.models.crmp_endorsements_details import Endorsement
from mServices import QueryBuilderService
import json


def ensure_invoice_statuses_exist():
    """
    Ensure all required invoice statuses exist in the core_statuses table.
    Creates them if they don't exist.
    """
    required_statuses = [
        {
            "name": "Pending",
            "description": "Not paid any amount against it",
            "type": "invoice",
            "module": "policy_invoice",
            "color": "#FFA500",
            "sort_index": 1
        },
        {
            "name": "Partially Paid",
            "description": "A portion of the invoice amount has been received",
            "type": "invoice",
            "module": "policy_invoice",
            "color": "#FFD700",
            "sort_index": 2
        },
        {
            "name": "Paid",
            "description": "Full payment has been received",
            "type": "invoice",
            "module": "policy_invoice",
            "color": "#28a745",
            "sort_index": 3
        },
        {
            "name": "Overdue",
            "description": "Payment deadline has passed and the invoice remains unpaid",
            "type": "invoice",
            "module": "policy_invoice",
            "color": "#dc3545",
            "sort_index": 4
        },
        {
            "name": "Cancelled",
            "description": "When a policy has been cancelled",
            "type": "invoice",
            "module": "policy_invoice",
            "color": "#343a40",
            "sort_index": 5
        },
        {
            "name": "Refunded",
            "description": "When a refund endorsement is done",
            "type": "invoice",
            "module": "policy_invoice",
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


def get_invoice_status_id(status_name):
    """
    Get the status ID for a given invoice status name.
    Returns None if status doesn't exist.
    """
    # Find status by name (ignore module)
    status = QueryBuilderService("core_status")\
        .where("name", status_name)\
        .first()
    
    return status["id"] if status else None


def check_existing_statuses():
    """
    Check what statuses already exist in the core_statuses table.
    Useful for debugging and understanding the current status structure.
    """
    print("=== Current Statuses in core_status Table ===")
    
    # Get all statuses
    all_statuses = QueryBuilderService("core_status")\
        .select("id", "name", "description", "type", "module", "color", "sort_index")\
        .orderBy("module", "asc")\
        .orderBy("sort_index", "asc")\
        .get()
    
    if not all_statuses:
        print("No statuses found in core_status table")
        return
    
    # Group by module
    statuses_by_module = {}
    for status in all_statuses:
        module = status.get("module", "Unknown")
        if module not in statuses_by_module:
            statuses_by_module[module] = []
        statuses_by_module[module].append(status)
    
    # Display grouped statuses
    for module, statuses in statuses_by_module.items():
        print(f"\n📁 Module: {module}")
        print("-" * 50)
        for status in statuses:
            print(f"  ID: {status['id']:2d} | {status['name']:20s} | {status['type']:10s} | {status['color']:7s} | {status['sort_index']}")
    
    print(f"\nTotal Statuses: {len(all_statuses)}")
    print("=" * 60)


def get_or_create_invoice_status(status_name):
    """
    Get an invoice status ID, creating it if it doesn't exist.
    This is a safer way to ensure statuses exist before using them.
    
    Args:
        status_name (str): Name of the status to get or create
        
    Returns:
        int: Status ID
    """
    # First try to get existing status
    status_id = get_invoice_status_id(status_name)
    if status_id:
        return status_id
    
    # If not found, ensure all statuses exist and try again
    ensure_invoice_statuses_exist()
    status_id = get_invoice_status_id(status_name)
    
    if status_id:
        return status_id
    
    # If still not found, something went wrong
    print(f"Warning: Could not find or create status '{status_name}'")
    return None


def debug_invoice_creation(issued_id):
    """
    Debug function to help troubleshoot invoice creation issues.
    
    Args:
        issued_id (int): ID of the issued policy to debug
        
    Returns:
        dict: Debug information
    """
    try:
        # Get issued policy
        issued_policy = IssuedPolicy.objects.get(id=issued_id)
        
        # Get policy base
        policy_base = issued_policy.policy_base
        
        # Get product info
        product = policy_base.product if policy_base else None
        
        debug_info = {
            "issued_policy_id": issued_id,
            "brokerage_policy_id": issued_policy.brokerage_policy_id,
            "premium_amount": str(issued_policy.premium_amount) if issued_policy.premium_amount else "None",
            "policy_base_id": policy_base.id if policy_base else "None",
            "product_id": product.id if product else "None",
            "product_name": product.name if product else "None",
            "insurer_id": policy_base.insurer.id if policy_base and policy_base.insurer else "None",
            "customer_id": policy_base.customer.id if policy_base and policy_base.customer else "None",
            "table_name": "crmp_invoices",  # We're using policy invoices, not finance invoices
            "model_class": "RequestPolicyInvoice"
        }
        
        print("=== Invoice Creation Debug Info ===")
        for key, value in debug_info.items():
            print(f"  {key}: {value}")
        print("=" * 40)
        
        return debug_info
        
    except Exception as e:
        print(f"Error in debug function: {str(e)}")
        return {"error": str(e)}


def update_invoice_status(invoice_id, status_name):
    """
    Update the status of a policy invoice.
    
    Args:
        invoice_id (int): ID of the invoice to update
        status_name (str): Name of the status to set
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        status_id = get_invoice_status_id(status_name)
        if not status_id:
            print(f"Status '{status_name}' not found")
            return False
        
        # Update the invoice status
        result = QueryBuilderService("crmp_invoices")\
            .where("id", invoice_id)\
            .update({"status_id": status_id})
        
        if result:
            print(f"Updated invoice {invoice_id} status to '{status_name}'")
            return True
        else:
            print(f"Failed to update invoice {invoice_id} status")
            return False
            
    except Exception as e:
        print(f"Error updating invoice status: {str(e)}")
        return False


def mark_invoice_as_paid(invoice_id, payment_amount=None):
    """
    Mark an invoice as paid and update its status accordingly.
    
    Args:
        invoice_id (int): ID of the invoice to mark as paid
        payment_amount (Decimal, optional): Amount being paid. If None, uses outstanding amount.
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        invoice = RequestPolicyInvoice.objects.get(id=invoice_id)
        
        if payment_amount is None:
            payment_amount = invoice.outstanding_amount
        
        # Update payment details
        update_invoice_payment_details(invoice_id, payment_amount)
        
        # Refresh invoice data
        invoice.refresh_from_db()
        
        # Set status to Paid if fully paid
        if invoice.paid_amount >= invoice.total_amount:
            update_invoice_status(invoice_id, "Paid")
        else:
            update_invoice_status(invoice_id, "Partially Paid")
        
        return True
        
    except Exception as e:
        print(f"Error marking invoice as paid: {str(e)}")
        return False


def mark_invoice_as_cancelled(invoice_id, reason="Policy cancelled"):
    """
    Mark an invoice as cancelled.
    
    Args:
        invoice_id (int): ID of the invoice to cancel
        reason (str): Reason for cancellation
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Update invoice status to Cancelled
        success = update_invoice_status(invoice_id, "Cancelled")
        
        if success:
            # Update remarks with cancellation reason
            QueryBuilderService("crmp_invoices")\
                .where("id", invoice_id)\
                .update({"remarks": f"Cancelled: {reason}"})
            print(f"Invoice {invoice_id} marked as cancelled")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error cancelling invoice: {str(e)}")
        return False


def mark_invoice_as_refunded(invoice_id, refund_amount=None, reason="Refund endorsement"):
    """
    Mark an invoice as refunded.
    
    Args:
        invoice_id (int): ID of the invoice to mark as refunded
        refund_amount (Decimal, optional): Amount being refunded
        reason (str): Reason for refund
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Update invoice status to Refunded
        success = update_invoice_status(invoice_id, "Refunded")
        
        if success:
            # Update remarks with refund reason
            remarks = f"Refunded: {reason}"
            if refund_amount:
                remarks += f" (Amount: {refund_amount})"
            
            QueryBuilderService("crmp_invoices")\
                .where("id", invoice_id)\
                .update({"remarks": remarks})
            print(f"Invoice {invoice_id} marked as refunded")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error marking invoice as refunded: {str(e)}")
        return False


def mark_invoice_as_overdue(invoice_id):
    """
    Mark an invoice as overdue.
    
    Args:
        invoice_id (int): ID of the invoice to mark as overdue
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        success = update_invoice_status(invoice_id, "Overdue")
        
        if success:
            # Update remarks
            QueryBuilderService("crmp_invoices")\
                .where("id", invoice_id)\
                .update({"remarks": "Payment overdue"})
            print(f"Invoice {invoice_id} marked as overdue")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error marking invoice as overdue: {str(e)}")
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
        ensure_invoice_statuses_exist()
        
        # Get current invoice data
        invoice = QueryBuilderService("crmp_invoices")\
            .select("id", "paid_amount", "outstanding_amount", "status_id")\
            .where("id", invoice_id)\
            .first()
        
        if not invoice:
            print(f"Policy invoice {invoice_id} not found")
            return False
        
        # Debug: Print invoice data to see the actual format
        print(f"Debug - Policy Invoice {invoice_id} data: {invoice}")
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
        status_id = get_or_create_invoice_status(status_name)
        if not status_id:
            print(f"Could not get status ID for '{status_name}'")
            return False
        
        # Update invoice status if it's different from current
        current_status_id = invoice.get("status_id")
        if current_status_id != status_id:
            update_result = QueryBuilderService("crmp_invoices")\
                .where("id", invoice_id)\
                .update({"status_id": status_id})
            
            if update_result > 0:
                print(f"Updated policy invoice {invoice_id} status to '{status_name}' (ID: {status_id})")
            else:
                print(f"No rows updated for policy invoice {invoice_id}")
        else:
            print(f"Policy invoice {invoice_id} already has correct status: {status_name}")
        
        return True
        
    except Exception as e:
        print(f"Error updating policy invoice status for invoice {invoice_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def get_invoice_status_summary(invoice_id):
    """
    Get a summary of an invoice's current status and payment information.
    
    Args:
        invoice_id (int): ID of the invoice
        
    Returns:
        dict: Status summary information
    """
    try:
        invoice = RequestPolicyInvoice.objects.get(id=invoice_id)
        
        # Get status information
        status = None
        if invoice.status_id:
            status_record = QueryBuilderService("core_status")\
                .where("id", invoice.status_id)\
                .first()
            if status_record:
                status = {
                    "id": status_record["id"],
                    "name": status_record["name"],
                    "description": status_record["description"],
                    "color": status_record["color"]
                }
        
        return {
            "invoice_id": invoice_id,
            "invoice_number": invoice.invoice_number,
            "total_amount": float(invoice.total_amount),
            "paid_amount": float(invoice.paid_amount),
            "outstanding_amount": float(invoice.outstanding_amount),
            "status": status,
            "remarks": invoice.remarks,
            "created_at": invoice.created_at,
            "updated_at": invoice.updated_at
        }
        
    except Exception as e:
        print(f"Error getting invoice status summary: {str(e)}")
        return None


def generate_invoice_for_issued_policy(issued_id, is_update=False, user=None, sales_agent_id=None):
    # Ensure required statuses exist
    ensure_invoice_statuses_exist()
    
    try:
        instance = IssuedPolicy.objects.get(id=issued_id)
        
        # Get policy base information for additional fields
        policy_base = instance.policy_base
        
        invoice, created = RequestPolicyInvoice.objects.update_or_create(
            issued_policy=instance, 
            defaults={
                "invoice_type": "issued",
                "total_amount": Decimal(str(instance.premium_amount or "0.00")).quantize(Decimal(".01")),
                "paid_amount": Decimal("0.00"),
                "outstanding_amount": Decimal(str(instance.premium_amount or "0.00")).quantize(Decimal(".01")),
                "remarks": "Updated" if is_update else "Created"
            }
        )
        
        # Set invoice type
        invoice.invoice_type = "issued"
        
        # Set amounts
        invoice.total_amount = Decimal(str(instance.premium_amount or "0.00")).quantize(Decimal(".01"))
        
        # Only set initial amounts if this is a new invoice
        if created:
            invoice.paid_amount = Decimal("0.00")
            invoice.outstanding_amount = invoice.total_amount
            # Set initial status to Pending for new invoices
            pending_status_id = get_or_create_invoice_status("Pending")
            if pending_status_id:
                invoice.status_id = pending_status_id
        
        invoice.remarks = "Updated" if is_update or not created else "Created"

        # Handle entity creation or update
        entity_data = {"type": "invoice", "approvel_status": False}
        entity_id = handle_entity(
            entity_data, entity_id=invoice.entity_id if is_update else None, user=user
        )
        invoice.entity_id = entity_id

        invoice.save()
        print(f"Successfully created/updated invoice for issued policy {issued_id}")
        return invoice
        
    except Exception as e:
        print(f"Error generating invoice for issued policy {issued_id}: {str(e)}")
        raise e


def generate_invoice_for_endorsement(
    endorsement_id, is_update=False, user=None, invoice_data=None
):
    # Ensure required statuses exist
    ensure_invoice_statuses_exist()
    
    try:
        instance = Endorsement.objects.get(id=endorsement_id)
        instance_req = instance.endorsement_request

        invoice, created = RequestPolicyInvoice.objects.update_or_create(
            endorsement=instance, 
            defaults={
                "invoice_type": "endorsement",
                "total_amount": Decimal(str(instance_req.cover_value or "0.00")).quantize(Decimal(".01")),
                "paid_amount": Decimal("0.00"),
                "outstanding_amount": Decimal(str(instance_req.cover_value or "0.00")).quantize(Decimal(".01")),
                "remarks": "Updated" if is_update or not created else "Created"
            }
        )

        invoice.invoice_type = "endorsement"

        if invoice_data:
            # Use the calculated amounts from invoice_data
            invoice.total_amount = Decimal(
                str(invoice_data.get("total_amount", "0.00"))
            ).quantize(Decimal(".01"))
            # Only set paid and outstanding for new invoices or when explicitly provided
            if created or (
                "paid_amount" in invoice_data and "outstanding_amount" in invoice_data
            ):
                invoice.paid_amount = Decimal(
                    str(invoice_data.get("paid_amount", "0.00"))
                ).quantize(Decimal(".01"))
                invoice.outstanding_amount = Decimal(
                    str(invoice_data.get("outstanding_amount", "0.00"))
                ).quantize(Decimal(".01"))
        else:
            # Fallback to request amount if no invoice_data provided
            invoice.total_amount = Decimal(
                str(instance_req.cover_value or "0.00")
            ).quantize(Decimal(".01"))
            # Only set initial amounts if this is a new invoice
            if created:
                invoice.paid_amount = Decimal("0.00")
                invoice.outstanding_amount = invoice.total_amount
                # Set initial status to Pending for new invoices
                pending_status_id = get_or_create_invoice_status("Pending")
                if pending_status_id:
                    invoice.status_id = pending_status_id

        invoice.issued_policy_id = instance_req.issued_policy_id or ""
        invoice.remarks = f"Endorsement {instance.endorsement_id} - {'Updated' if is_update or not created else 'Created'}"

        # Handle entity creation or update
        entity_data = {"type": "invoice", "approvel_status": False}
        entity_id = handle_entity(
            entity_data, entity_id=invoice.entity_id if is_update else None, user=user
        )
        invoice.entity_id = entity_id

        invoice.save()
        print(f"Successfully created/updated invoice for endorsement {endorsement_id}")
        return invoice
        
    except Exception as e:
        print(f"Error generating invoice for endorsement {endorsement_id}: {str(e)}")
        raise e


def update_invoice_payment_details(invoice_id, paid_amount):
    """Update invoice totals after a payment"""
    if not invoice_id:
        return

    invoice = RequestPolicyInvoice.objects.get(id=invoice_id)

    # Convert amounts to Decimal for accurate calculations
    paid_amount = Decimal(str(paid_amount)).quantize(Decimal(".01"))
    current_paid = Decimal(str(invoice.paid_amount or "0.00")).quantize(Decimal(".01"))
    total_amount = Decimal(str(invoice.total_amount or "0.00")).quantize(Decimal(".01"))

    # Update paid amount
    new_paid_amount = (current_paid + paid_amount).quantize(Decimal(".01"))

    # Calculate new outstanding amount
    new_outstanding = (total_amount - new_paid_amount).quantize(Decimal(".01"))

    # Update invoice
    invoice.paid_amount = new_paid_amount
    invoice.outstanding_amount = new_outstanding
    
    # Update status based on payment amount
    if new_paid_amount >= total_amount:
        # Full payment received
        paid_status_id = get_or_create_invoice_status("Paid")
        if paid_status_id:
            invoice.status_id = paid_status_id
    elif new_paid_amount > 0:
        # Partial payment received
        partially_paid_status_id = get_or_create_invoice_status("Partially Paid")
        if partially_paid_status_id:
            invoice.status_id = partially_paid_status_id
    
    invoice.save()
