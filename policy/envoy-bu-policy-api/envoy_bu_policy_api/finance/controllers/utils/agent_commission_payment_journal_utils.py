from mServices import QueryBuilderService
from envoy_bu_policy_api.finance.controllers.utils.journal_entry_utils import create_journal_entries, get_account_number_by_type

def create_agent_commission_payment_journal_entries(commission_payment, user=None):
    """
    Create journal entries for agent commission payment (debit Commission Payable – Agent, credit Bank Account).
    Args:
        commission_payment (dict): Commission payment details
        user (User, optional): User creating the journal entry
    Returns:
        list: List of journal entry IDs or None if failed
    """
    try:
        commission = QueryBuilderService("crmf_agent_commission") \
            .where("id", commission_payment["agent_commission_id"]).first()
        if not commission:
            return None
        agent = QueryBuilderService("core_users") \
            .where("id", commission["agent_id"]).first()
        if not agent:
            return None
        payment_amount = commission_payment["payment_amount"]
        debit_account_num = get_account_number_by_type("commission_payable_agent", False)
        credit_account_num = get_account_number_by_type("bank_payment", True)
        desc = (
            f"Pay agent commission: {agent['display_name']} | "
            f"Payment ID: {commission_payment['id']} | Commission ID: {commission['id']}"
        )
        brokerage_commission = QueryBuilderService("crmf_brokerage_commission") \
            .where("id", commission["brokerage_commission_id"]).first()
        invoice_id = brokerage_commission["invoice_id"] if brokerage_commission else ""
        payment_data = {
            "transaction_type": "agent_commission_payment",
            "amount": str(payment_amount),
            "description": desc,
            "reference_id": commission_payment["id"],
            "reference_type": "agent_commission_payment",
            "debit_account": debit_account_num,
            "credit_account": credit_account_num,
            "invoice_id": invoice_id
        }
        success, _, ids = create_journal_entries(payment_data, user)
        return ids if success and ids else None
    except Exception as e:
        print(f"Error creating agent commission payment journal: {str(e)}")
        return None

