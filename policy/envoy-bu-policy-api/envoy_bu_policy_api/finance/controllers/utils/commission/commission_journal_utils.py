from envoy_bu_policy_api.finance.controllers.utils.journal_entry_utils import create_journal_entries, get_account_number_by_type
from mServices import QueryBuilderService
from decimal import Decimal

def create_brokerage_commission_journal_entry(brokerage_commission, invoice, user=None, realized=False):
    """
    Create a journal entry for brokerage commission (recognized or realized).
    Args:
        brokerage_commission (dict): Brokerage commission record
        invoice (dict): Invoice record
        user (User, optional): User creating the journal entry
        realized (bool): If True, use revenue_realized; else use revenue_recognized
    Returns:
        list: List of journal entry IDs or None if failed
    """
    amount = Decimal(str(brokerage_commission["revenue_realized"] if realized else brokerage_commission["revenue_recognized"]))
    if amount == 0:
        return None
    # Determine transaction type
    if invoice.get("endorsement_id"):
        transaction_type = "commission_income_endorsements"
    elif invoice.get("transaction_type_id") == 3:  # Renewal
        transaction_type = "commission_income_renewals"
    else:
        transaction_type = "commission_income_new_business"
        
    debit_account_num = get_account_number_by_type(transaction_type, True)
    credit_account_num = get_account_number_by_type(transaction_type, False)
    debit_account = QueryBuilderService("crmf_chart_of_account").where("account_number", debit_account_num).first()
    credit_account = QueryBuilderService("crmf_chart_of_account").where("account_number", credit_account_num).first()
    desc = f"{debit_account['account_name']} to {credit_account['account_name']} | Brokerage commission for invoice {invoice['invoice_number']} ({'Realized' if realized else 'Recognized'})"
    data = {
        "transaction_type": transaction_type,
        "amount": str(amount),
        "description": desc,
        "reference_id": brokerage_commission["id"],
        "reference_type": "brokerage_commission",
        "debit_account": debit_account_num,
        "credit_account": credit_account_num,
        "invoice_id":invoice.get("id")

    }
    
    success, message, ids = create_journal_entries(data, user)
    if success and ids:
        return ids
    return None

def create_agent_commission_journal_entry(agent_commission, invoice, user=None, realized=False):
    """
    Create a journal entry for agent commission (recognized or realized).
    Args:
        agent_commission (dict): Agent commission record
        invoice (dict): Invoice record
        user (User, optional): User creating the journal entry
        realized (bool): If True, use revenue_realized; else use revenue_recognized
    Returns:
        list: List of journal entry IDs or None if failed
    """
    amount = Decimal(str(agent_commission["revenue_realized"] if realized else agent_commission["revenue_recognized"]))
    if amount == 0:
        return None
    debit_account_num = get_account_number_by_type("commission_payable_agent", True)
    credit_account_num = get_account_number_by_type("commission_payable_agent", False)
    debit_account = QueryBuilderService("crmf_chart_of_account").where("account_number", debit_account_num).first()
    credit_account = QueryBuilderService("crmf_chart_of_account").where("account_number", credit_account_num).first()
    desc = f"{debit_account['account_name']} to {credit_account['account_name']} | Agent commission for invoice {invoice['invoice_number']} ({'Realized' if realized else 'Recognized'})"
    data = {
        "transaction_type": "commission_payable_agent",
        "amount": str(amount),
        "description": desc,
        "reference_id": agent_commission["id"],
        "reference_type": "agent_commission",
        "debit_account": debit_account_num,
        "credit_account": credit_account_num,
        "invoice_id":invoice.get("id")
    }
    success, message, ids = create_journal_entries(data, user)
    if success and ids:
        return ids
    return None 