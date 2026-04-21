from decimal import Decimal
from django.utils import timezone
from mServices import QueryBuilderService
from envoy_bu_policy_api.service import handle_entity

def create_journal_entries(transaction_data, user=None):
    """
    Create journal entries for various financial transactions
    
    Args:
        transaction_data (dict): Dictionary containing transaction details
            Required keys:
            - transaction_type: str (policy_premium, endorsement, payment, service, commission)
            - amount: Decimal
            - description: str
            - reference_id: int (ID of the related record)
            - reference_type: str (policy, endorsement, payment, service, commission)
            - debit_account: str (account number to debit)
            - credit_account: str (account number to credit)
        user: User object (optional)
    
    Returns:
        tuple: (success: bool, message: str, entry_ids: list)
    """
    try:
        # Validate required fields
        required_fields = ['transaction_type', 'amount', 'description', 'reference_id', 
                         'reference_type', 'debit_account', 'credit_account','invoice_id']
        for field in required_fields:
            if field not in transaction_data:
                return False, f"Missing required field: {field}", []

        # Get account details
        debit_account = QueryBuilderService("crmf_chart_of_account").where(
            "account_number", transaction_data['debit_account']
        ).first()
        credit_account = QueryBuilderService("crmf_chart_of_account").where(
            "account_number", transaction_data['credit_account']
        ).first()

        if not debit_account or not credit_account:
            return False, "Invalid account numbers", []

        # Create entity for the journal entry
        entity_data = {
            "type": "journal_entry",
            "approvel_status": False,
        }
        entity_id = handle_entity(entity_data, user=user)

        # Generate entry number for the transaction
        last_entry = QueryBuilderService("crmf_journal_entries").orderBy("entry_number", "desc").first()
        if last_entry:
            last_num = int(last_entry["entry_number"].replace("JE", ""))
            new_num = last_num + 1
        else:
            new_num = 1
        entry_number = f"JE{new_num:06d}"

        # Create debit entry
        debit_entry = {
            "entry_number": entry_number,
            "date": timezone.now().date(),
            "account_id": debit_account['id'],
            "debit_amount": transaction_data['amount'],
            "invoice_id": transaction_data['invoice_id'],
            "credit_amount": Decimal('0.00'),
            "description": f"{debit_account['account_name']} ",
            "entity_id": entity_id
        }
# | {transaction_data['description']}
        # Create credit entry with same entry number
        credit_entry = {
            "entry_number": entry_number,
            "date": timezone.now().date(),
            "account_id": credit_account['id'],
            "debit_amount": Decimal('0.00'),
            "invoice_id": transaction_data['invoice_id'],
            "credit_amount": transaction_data['amount'],
            "description": f"{credit_account['account_name']} ",
            "entity_id": entity_id
        }

        # Insert entries
        debit_result = QueryBuilderService("crmf_journal_entries").insert(debit_entry)
        credit_result = QueryBuilderService("crmf_journal_entries").insert(credit_entry)

        if not debit_result or not credit_result:
            return False, "Failed to create journal entries", []

        return True, "Journal entries created successfully", [debit_result, credit_result]

    except Exception as e:
        print(f"Error creating journal entries: {str(e)}")
        return False, str(e), []

def get_account_number_by_type(transaction_type, is_debit=True):
    """
    Get the appropriate account number based on transaction type
    
    Args:
        transaction_type (str): Type of transaction
        is_debit (bool): Whether to get debit or credit account
    
    Returns:
        str: Account number
    """
    # Only accounts and transaction types 
    account_mapping = {
        # Commission Payable – Agent
        'commission_payable_agent': {
            'debit': '50001',   # Agent Commission Expense
            'credit': '20003',  # Commission Payable – Agent
        },
        # Commission Income – New Business
        'commission_income_new_business': {
            'debit': '10002',   # Accounts Receivable – Insurer
            'credit': '40005',  # Commission Income – New Business
        },
        # Commission Income – Renewals
        'commission_income_renewals': {
            'debit': '10002',
            'credit': '40006',  # Commission Income – Renewals
        },
        # Commission Income – Endorsements
        'commission_income_endorsements': {
            'debit': '10002',
            'credit': '40007',  # Commission Income – Endorsements
        },
        # Commission Income – Adjusted (Contra)
        'commission_income_adjusted': {
            'debit': '40008',   # Commission Income – Adjusted (Contra)
            'credit': '10002',
        },
        # Service Charge Income
        'service_charge_income': {
            'debit': '10002',
            'credit': '40009',  # Service Charge Income
        },
        # Agent Commission Expense
        'agent_commission_expense': {
            'debit': '50001',   # Agent Commission Expense
            'credit': '20003',  # Commission Payable – Agent
        },
        # Bank Account (for payments)
        'bank_payment': {
            'debit': '10001',   # Bank Account
            'credit': '10002',  # Accounts Receivable – Insurer
        },
        # Commission Reversal Payable – Insurer
        'commission_reversal_payable_insurer': {
            'debit': '40008',   # Commission Income – Adjusted (Contra)
            'credit': '20005',  # Commission Reversal Payable – Insurer
        },
        # Policy Premium (New Business)
        'policy_premium': {
            'debit': '10002',   # Accounts Receivable – Insurer
            'credit': '40005',  # Commission Income – New Business
        },
        # Policy Renewal
        'policy_renewal': {
            'debit': '10002',
            'credit': '40006',  # Commission Income – Renewals
        },
        # Policy Refund/Cancellation
        'policy_refund': {
            'debit': '40008',   # Commission Income – Adjusted (Contra)
            'credit': '10002',
        },
        # Endorsement Premium
        'endorsement_premium': {
            'debit': '10002',
            'credit': '40007',  # Commission Income – Endorsements
        },
        # Premium Payment
        'premium_payment': {
            'debit': '10001',   # Bank Account
            'credit': '10002',  # Accounts Receivable – Insurer
        },
        # Service Revenue
        'service_revenue': {
            'debit': '10002',   # Accounts Receivable – Insurer
            'credit': '40009',  # Service Charge Income
        },
        # Service Payment
        'service_payment': {
            'debit': '10001',   # Bank Account
            'credit': '10002',  # Accounts Receivable – Insurer
        },
    }

    if transaction_type not in account_mapping:
        raise ValueError(f"Invalid transaction type: {transaction_type}")
    return account_mapping[transaction_type]['debit' if is_debit else 'credit']

def create_commission_journal_entries_for_commissions(commissions, invoice, user=None, realized=False, adjustment=False, forced_transaction_type=None):
    """
    Create journal entries for a list of commission records (brokerage and/or agent),
    handling new business, renewal, endorsement, and adjustment (deduction) cases.
    Args:
        commissions (list): List of commission records (dicts)
        invoice (dict): Invoice record
        user (User, optional): User creating the journal entry
        realized (bool): If True, use revenue_realized; else use revenue_recognized
        adjustment (bool): If True, this is an adjustment (deduction/reversal)
        forced_transaction_type (str, optional): If provided, use this transaction type for all entries
    Returns:
        list: List of all created journal entry IDs
    """
    entry_ids = []
    for commission in commissions:
        # Determine if brokerage or agent commission
        is_brokerage = 'brokerage_revenue_percent' in commission or commission.get('type') == 'brokerage_commission'
        is_agent = 'agent_commission_percent' in commission or commission.get('type') == 'agent_commission'
        # Determine transaction type
        if forced_transaction_type:
            transaction_type = forced_transaction_type
        else:
            if invoice.get('endorsement_id'):
                transaction_type = 'commission_income_endorsements'
            elif invoice.get('transaction_type_id') == 3:  # Renewal
                transaction_type = 'commission_income_renewals'
            else:
                transaction_type = 'commission_income_new_business'
        # Amount
        amount = Decimal(str(commission['revenue_realized'] if realized else commission['revenue_recognized']))
        if adjustment:
            amount = -abs(amount)
        if amount == 0:
            continue
        # Account mapping
        if is_brokerage:
            debit_account_num = get_account_number_by_type(transaction_type, True)
            credit_account_num = get_account_number_by_type(transaction_type, False)
            ref_type = 'brokerage_commission'
        elif is_agent:
            debit_account_num = get_account_number_by_type('commission_payable_agent', True)
            credit_account_num = get_account_number_by_type('commission_payable_agent', False)
            ref_type = 'agent_commission'
        else:
            continue
        debit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', debit_account_num).first()
        credit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', credit_account_num).first()
        desc = f"{debit_account['account_name']} to {credit_account['account_name']} | {'Adjustment ' if adjustment else ''}{'Realized' if realized else 'Recognized'} commission for invoice {invoice['invoice_number']}"
        data = {
            'transaction_type': transaction_type if is_brokerage else 'commission_payable_agent',
            'amount': str(amount),
            'description': desc,
            'reference_id': commission['id'],
            'reference_type': ref_type,
            'debit_account': debit_account_num,
            'credit_account': credit_account_num,
            "invoice_id":invoice.get("id")

        }
        success, message, ids = create_journal_entries(data, user)
        if success and ids:
            entry_ids.extend(ids)
    return entry_ids 

def create_commission_deduction_journal_entries(commissions, invoice, user=None):
    """
    Create journal entries for commission deductions (refund/cancellation),
    handling both revenue recognized and revenue realized, using correct account mappings.
    Args:
        commissions (list): List of commission records (dicts)
        invoice (dict): Invoice record
        user (User, optional): User creating the journal entry
    Returns:
        list: List of all created journal entry IDs
    """
    if not invoice:
        print(f"WARNING: Invoice is None. Cannot create journal entries.")
        return []
    
    entry_ids = []
    for commission in commissions:
        # Determine if brokerage or agent commission
        is_brokerage = 'brokerage_revenue_percent' in commission or commission.get('type') == 'brokerage_commission'
        is_agent = 'agent_commission_percent' in commission or commission.get('type') == 'agent_commission'
        # --- Revenue Recognized (policy_refund) ---
        recognized_amount = abs(Decimal(str(commission.get('revenue_recognized', '0.00'))))
        if recognized_amount > 0:
            if is_brokerage:
                debit_account_num = get_account_number_by_type('policy_refund', True)
                credit_account_num = get_account_number_by_type('policy_refund', False)
                ref_type = 'brokerage_commission'
            elif is_agent:
                debit_account_num = get_account_number_by_type('commission_payable_agent', True)
                credit_account_num = get_account_number_by_type('commission_payable_agent', False)
                ref_type = 'agent_commission'
            else:
                continue
            debit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', debit_account_num).first()
            credit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', credit_account_num).first()
            if not debit_account or not credit_account:
                print(f"WARNING: Account not found - debit: {debit_account_num}, credit: {credit_account_num}. Skipping journal entry.")
                continue
            desc = f"{debit_account['account_name']} to {credit_account['account_name']} | Recognized commission deduction for invoice {invoice['invoice_number']}"
            data = {
                'transaction_type': 'policy_refund' if is_brokerage else 'commission_payable_agent',
                'amount': str(recognized_amount),
                'description': desc,
                'reference_id': commission['id'],
                'reference_type': ref_type,
                'debit_account': debit_account_num,
                'credit_account': credit_account_num,
                "invoice_id":invoice.get("id")

            }
            success, message, ids = create_journal_entries(data, user)
            if success and ids:
                entry_ids.extend(ids)
        # --- Revenue Realized (commission_reversal_payable_insurer + commission_income_adjusted) ---
        realized_amount = abs(Decimal(str(commission.get('revenue_realized', '0.00'))))
        if realized_amount > 0:
            if is_brokerage:
                # 1. Commission Reversal Payable – Insurer
                debit_account_num = get_account_number_by_type('commission_reversal_payable_insurer', True)
                credit_account_num = get_account_number_by_type('commission_reversal_payable_insurer', False)
                ref_type = 'brokerage_commission'
                debit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', debit_account_num).first()
                credit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', credit_account_num).first()
                if not debit_account or not credit_account:
                    print(f"WARNING: Account not found - debit: {debit_account_num}, credit: {credit_account_num}. Skipping journal entry.")
                    continue
                desc = f"{debit_account['account_name']} to {credit_account['account_name']} | Realized commission reversal for invoice {invoice['invoice_number']}"
                data = {
                    'transaction_type': 'commission_reversal_payable_insurer',
                    'amount': str(realized_amount),
                    'description': desc,
                    'reference_id': commission['id'],
                    'reference_type': ref_type,
                    'debit_account': debit_account_num,
                    'credit_account': credit_account_num,
                            "invoice_id":invoice.get("id")

                }
                success, message, ids = create_journal_entries(data, user)
                if success and ids:
                    entry_ids.extend(ids)
                # 2. Commission Income Adjusted (Contra)
                debit_account_num = get_account_number_by_type('commission_income_adjusted', True)
                credit_account_num = get_account_number_by_type('commission_income_adjusted', False)
                debit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', debit_account_num).first()
                credit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', credit_account_num).first()
                if not debit_account or not credit_account:
                    print(f"WARNING: Account not found - debit: {debit_account_num}, credit: {credit_account_num}. Skipping journal entry.")
                    continue
                desc = f"{debit_account['account_name']} to {credit_account['account_name']} | Realized commission income adjusted for invoice {invoice['invoice_number']}"
                data = {
                    'transaction_type': 'commission_income_adjusted',
                    'amount': str(realized_amount),
                    'description': desc,
                    'reference_id': commission['id'],
                    'reference_type': ref_type,
                    'debit_account': debit_account_num,
                    'credit_account': credit_account_num,
                            "invoice_id":invoice.get("id")

                }
                success, message, ids = create_journal_entries(data, user)
                if success and ids:
                    entry_ids.extend(ids)
            elif is_agent:
                # Agent commission reversal (use commission_payable_agent mapping)
                debit_account_num = get_account_number_by_type('commission_payable_agent', True)
                credit_account_num = get_account_number_by_type('commission_payable_agent', False)
                ref_type = 'agent_commission'
                debit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', debit_account_num).first()
                credit_account = QueryBuilderService('crmf_chart_of_account').where('account_number', credit_account_num).first()
                if not debit_account or not credit_account:
                    print(f"WARNING: Account not found - debit: {debit_account_num}, credit: {credit_account_num}. Skipping journal entry.")
                    continue
                desc = f"{debit_account['account_name']} to {credit_account['account_name']} | Realized agent commission deduction for invoice {invoice['invoice_number']}"
                data = {
                    'transaction_type': 'commission_payable_agent',
                    'amount': str(realized_amount),
                    'description': desc,
                    'reference_id': commission['id'],
                    'reference_type': ref_type,
                    'debit_account': debit_account_num,
                    'credit_account': credit_account_num,
                            "invoice_id":invoice.get("id")

                }
                success, message, ids = create_journal_entries(data, user)
                if success and ids:
                    entry_ids.extend(ids)
    return entry_ids 