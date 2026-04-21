from envoy_bu_policy_api.finance.controllers.utils.journal_entry_utils import create_journal_entries, get_account_number_by_type

def create_service_render_journal_entries(service_render, user=None):
    """
    Create journal entries for service render creation (debit Accounts Receivable – Insurer, credit Service Charge Income).
    Args:
        service_render (dict): Service render details
        user (User, optional): User creating the journal entry
    Returns:
        list: List of journal entry IDs or None if failed
    """
    try:
        service_data = {
            "transaction_type": "service_revenue",
            "amount": str(service_render["fee"]),
            "description": f"Service revenue for {service_render['vendor_name']}",
            "reference_id": service_render["id"],
            "reference_type": "service_render",
            "debit_account": get_account_number_by_type("service_revenue", True),
            "credit_account": get_account_number_by_type("service_revenue", False)
        }
        success, _, ids = create_journal_entries(service_data, user)
        return ids if success and ids else None
    except Exception as e:
        print(f"Error creating service render journal: {str(e)}")
        return None

def create_service_render_payment_journal_entries(service_render, payment_amount, user=None):
    """
    Create journal entries for service render payment (debit Bank Account, credit Accounts Receivable – Insurer).
    Args:
        service_render (dict): Service render details
        payment_amount (Decimal): Payment amount
        user (User, optional): User creating the journal entry
    Returns:
        list: List of journal entry IDs or None if failed
    """
    try:
        payment_data = {
            "transaction_type": "service_payment",
            "amount": str(payment_amount),
            "description": f"Payment for service {service_render['vendor_name']}",
            "reference_id": service_render["id"],
            "reference_type": "service_render",
            "debit_account": get_account_number_by_type("service_payment", True),
            "credit_account": get_account_number_by_type("service_payment", False)
        }
        success, _, ids = create_journal_entries(payment_data, user)
        return ids if success and ids else None
    except Exception as e:
        print(f"Error creating service render payment journal: {str(e)}")
        return None 