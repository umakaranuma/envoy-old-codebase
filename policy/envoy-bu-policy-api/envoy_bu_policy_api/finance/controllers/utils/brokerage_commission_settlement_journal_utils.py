from mServices import QueryBuilderService
from envoy_bu_policy_api.finance.controllers.utils.journal_entry_utils import create_journal_entries, get_account_number_by_type

def create_brokerage_commission_settlement_journal_entries(commission_settlement, user=None):
    """
    Create journal entries for brokerage commission settlement (debit Commission Payable – Brokerage, credit Bank Account).
    Args:
        commission_settlement (dict): Commission settlement details
        user (User, optional): User creating the journal entry
    Returns:
        list: List of journal entry IDs or None if failed
    """
    try:
        commission = QueryBuilderService("crmf_brokerage_commission") \
            .where("id", commission_settlement["brokerage_commission_id"]).first()
        if not commission:
            return None
        
        settlement_amount = commission_settlement["settlement_amount"]
        # Use commission_payable_agent account for brokerage commission settlements
        # (debit Commission Payable – Agent, credit Bank Account)
        debit_account_num = get_account_number_by_type("commission_payable_agent", False)
        credit_account_num = get_account_number_by_type("bank_payment", True)
        desc = (
            f"Settle brokerage commission | "
            f"Settlement ID: {commission_settlement['id']} | Commission ID: {commission['id']}"
        )
        # Get invoice_id from commission (Django creates invoice_id field for OneToOneField)
        invoice_id = commission.get("invoice_id", "") if commission else ""
        settlement_data = {
            "transaction_type": "brokerage_commission_settlement",
            "amount": str(settlement_amount),
            "description": desc,
            "reference_id": commission_settlement["id"],
            "reference_type": "brokerage_commission_settlement",
            "debit_account": debit_account_num,
            "credit_account": credit_account_num,
            "invoice_id": invoice_id
        }
        success, _, ids = create_journal_entries(settlement_data, user)
        return ids if success and ids else None
    except Exception as e:
        print(f"Error creating brokerage commission settlement journal: {str(e)}")
        return None

