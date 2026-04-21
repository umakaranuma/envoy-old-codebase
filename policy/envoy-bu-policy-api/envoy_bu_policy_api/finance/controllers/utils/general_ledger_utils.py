from django.utils import timezone
from mServices import QueryBuilderService
from envoy_bu_policy_api.service import handle_entity

def create_general_ledger_entry(transaction_data, user=None):
    """
    Create a general ledger entry for any transaction
    
    Args:
        transaction_data (dict): Dictionary containing transaction details
            Required keys:
            - transaction_type: str (policy_premium, endorsement, payment, service, commission)
            - amount: Decimal
            - description: str
            - reference_id: int (ID of the related record)
            - reference_type: str (policy, endorsement, payment, service, commission)
            - payer_id: int (ID of the payer)
            - payment_method: str (cash, bank_transfer, cheque, credit_card, other)
        user: User object (optional)
    
    Returns:
        tuple: (success: bool, message: str, entry_id: int)
    """
    try:
        # Validate required fields
        required_fields = ['transaction_type', 'amount', 'description', 'reference_id', 
                         'reference_type', 'payer_id', 'payment_method']
        for field in required_fields:
            if field not in transaction_data:
                return False, f"Missing required field: {field}", None

        # Validate payer exists
        payer = QueryBuilderService("core_service_providers").where("id", transaction_data['payer_id']).first()
        if not payer:
            return False, "Invalid payer ID", None

        # Create entity for the general ledger entry
        entity_data = {
            "type": "general_ledger",
            "approvel_status": False,
        }
        entity_id = handle_entity(entity_data, user=user)

        # Generate payment ID
        last_entry = QueryBuilderService("crmf_general_ledger").orderBy("payment_id", "desc").first()
        if last_entry:
            last_num = int(last_entry["payment_id"].replace("PAY", ""))
            new_num = last_num + 1
        else:
            new_num = 1
        payment_id = f"PAY{new_num:06d}"

        # Create general ledger entry
        entry_data = {
            "payment_id": payment_id,
            "invoice_number": transaction_data.get('invoice_number', f"INV-{transaction_data['reference_id']}"),
            "transaction_date": timezone.now().date(),
            "payment_amount": transaction_data['amount'],
            "payer_id": transaction_data['payer_id'],
            "payment_method": transaction_data['payment_method'],
            "ledger_status": "completed" if transaction_data['transaction_type'] in ['payment', 'refund'] else "pending",
            "remarks": transaction_data['description'],
            "entity_id": entity_id
        }

        # Insert entry
        result = QueryBuilderService("crmf_general_ledger").insert(entry_data)
        if not result:
            return False, "Failed to create general ledger entry", None

        return True, "General ledger entry created successfully", result

    except Exception as e:
        print(f"Error creating general ledger entry: {str(e)}")
        return False, str(e), None

def create_invoice_general_ledger(invoice_data, transaction_type, amount, user=None):
    """
    Create general ledger entry for invoice transactions
    
    Args:
        invoice_data (dict): Invoice data containing invoice_number and id
        transaction_type (dict): Transaction type data
        amount (Decimal): Transaction amount
        user: User object (optional)
    
    Returns:
        tuple: (success: bool, message: str, entry_id: int)
    """
    try:
        transaction_data = {
            "transaction_type": "invoice",
            "amount": amount,
            "description": f"{transaction_type['name']} for invoice {invoice_data['invoice_number']}",
            "reference_id": invoice_data['id'],
            "reference_type": "invoice",
            "payer_id": invoice_data.get("insurer_id"),
            "payment_method": "bank_transfer",  # Default method
            "invoice_number": invoice_data['invoice_number']
        }

        return create_general_ledger_entry(transaction_data, user=user)
    except Exception as e:
        print(f"Error creating invoice general ledger: {str(e)}")
        return False, str(e), None

def create_payment_general_ledger(invoice, payment_data, user=None):
    """
    Create general ledger entry for payment transactions
    
    Args:
        invoice (dict): Invoice data
        payment_data (dict): Payment details including amount and method
        user: User object (optional)
    
    Returns:
        tuple: (success: bool, message: str, entry_id: int)
    """
    try:
        transaction_data = {
            "transaction_type": "payment",
            "amount": payment_data["paid_amount"],
            "description": f"Payment for invoice {invoice['invoice_number']}",
            "reference_id": payment_data['id'],
            "reference_type": "payment",
            "payer_id": invoice.get("insurer_id"),
            "payment_method": payment_data.get("payment_method", "bank_transfer"),
            "invoice_number": invoice['invoice_number']
        }

        return create_general_ledger_entry(transaction_data, user=user)
    except Exception as e:
        print(f"Error creating payment general ledger: {str(e)}")
        return False, str(e), None

def create_service_render_general_ledger(service_render, payment_amount, user=None):
    """
    Create general ledger entry for service render payments
    
    Args:
        service_render (dict): Service render details
        payment_amount (Decimal): Payment amount
        user: User object (optional)
    
    Returns:
        tuple: (success: bool, message: str, entry_id: int)
    """
    try:
        transaction_data = {
            "transaction_type": "service",
            "amount": payment_amount,
            "description": f"Payment for service {service_render['vendor_name']}",
            "reference_id": service_render['id'],
            "reference_type": "service_render",
            "payer_id": service_render.get("customer_id"),
            "payment_method": "bank_transfer",  # Default method
            "invoice_number": service_render['invoice_number']
        }

        return create_general_ledger_entry(transaction_data, user=user)
    except Exception as e:
        print(f"Error creating service render general ledger: {str(e)}")
        return False, str(e), None

def create_commission_general_ledger(commission_data, commission_type, user=None):
    """
    Create general ledger entry for commission transactions
    
    Args:
        commission_data (dict): Commission details
        commission_type (str): Type of commission (brokerage/agent)
        user: User object (optional)
    
    Returns:
        tuple: (success: bool, message: str, entry_id: int)
    """
    try:
        transaction_data = {
            "transaction_type": "commission",
            "amount": commission_data["revenue_recognized"],
            "description": f"{commission_type} commission for {commission_data.get('invoice_number', '')}",
            "reference_id": commission_data['id'],
            "reference_type": "commission",
            "payer_id": commission_data.get("insurer_id"),
            "payment_method": "bank_transfer",  # Default method
            "invoice_number": commission_data.get("invoice_number", f"COMM-{commission_data['id']}")
        }

        return create_general_ledger_entry(transaction_data, user=user)
    except Exception as e:
        print(f"Error creating commission general ledger: {str(e)}")
        return False, str(e), None 