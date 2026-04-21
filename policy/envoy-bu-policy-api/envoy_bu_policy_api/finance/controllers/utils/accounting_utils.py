from decimal import Decimal
from django.utils import timezone
from mServices import QueryBuilderService
from envoy_bu_policy_api.service import handle_entity

def generate_chart_of_account(account_data, is_update=False, user=None):
    """
    Generate or update a chart of account entry
    """
    try:
        entity_data = {
            "type": "chart_of_account",
            "approvel_status": False,
        }
        entity_id = handle_entity(
            entity_data,
            entity_id=None if not is_update else account_data.get("entity_id"),
            user=user,
        )
        account_data["entity_id"] = entity_id

        if is_update:
            account = QueryBuilderService("crmf_chart_of_account").where("id", account_data.get("id")).update(account_data)
        else:
            account = QueryBuilderService("crmf_chart_of_account").insert(account_data)

        return account
    except Exception as e:
        print(f"Error generating chart of account: {str(e)}")
        return None

def generate_journal_entry(entry_data, is_update=False, user=None):
    """
    Generate or update a journal entry
    """
    try:
        # Validate account exists
        account = QueryBuilderService("crmf_chart_of_account").where("id", entry_data.get("account_id")).first()
        if not account:
            return None

        entity_data = {
            "type": "journal_entry",
            "approvel_status": False,
        }
        entity_id = handle_entity(
            entity_data,
            entity_id=None if not is_update else entry_data.get("entity_id"),
            user=user,
        )
        entry_data["entity_id"] = entity_id

        if is_update:
            entry = QueryBuilderService("crmf_journal_entries").where("id", entry_data.get("id")).update(entry_data)
        else:
            entry = QueryBuilderService("crmf_journal_entries").insert(entry_data)

        # Update chart of account balance
        if entry:
            debit_amount = Decimal(str(entry_data.get("debit_amount", 0)))
            credit_amount = Decimal(str(entry_data.get("credit_amount", 0)))
            balance_change = debit_amount - credit_amount
            
            current_balance = Decimal(str(account.get("balance", 0)))
            new_balance = current_balance + balance_change
            
            QueryBuilderService("crmf_chart_of_account").where("id", account.get("id")).update({
                "balance": new_balance
            })

        return entry
    except Exception as e:
        print(f"Error generating journal entry: {str(e)}")
        return None

def generate_general_ledger_entry(payment_data, is_update=False, user=None):
    """
    Generate or update a general ledger entry for payments
    """
    try:
        # Validate payer (insurer) exists
        payer = QueryBuilderService("core_service_providers").where("id", payment_data.get("payer_id")).first()
        if not payer:
            return None

        entity_data = {
            "type": "general_ledger",
            "approvel_status": False,
        }
        entity_id = handle_entity(
            entity_data,
            entity_id=None if not is_update else payment_data.get("entity_id"),
            user=user,
        )
        payment_data["entity_id"] = entity_id

        if is_update:
            entry = QueryBuilderService("crmf_general_ledger").where("id", payment_data.get("id")).update(payment_data)
        else:
            entry = QueryBuilderService("crmf_general_ledger").insert(payment_data)

        return entry
    except Exception as e:
        print(f"Error generating general ledger entry: {str(e)}")
        return None

def create_accounting_entries_for_payment(invoice_id, payment_data, user=None):
    """
    Create all necessary accounting entries when a payment is made
    """
    try:
        # Get invoice details
        invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()
        if not invoice:
            return None

        # Create general ledger entry
        ledger_data = {
            "invoice_number": invoice.get("invoice_number"),
            "transaction_date": timezone.now().date(),
            "payment_amount": payment_data.get("paid_amount"),
            "payer_id": invoice.get("insurer_id"),
            "payment_method": payment_data.get("payment_method", "bank_transfer"),
            "ledger_status": "completed",
            "remarks": f"Payment for invoice {invoice.get('invoice_number')}"
        }
        ledger_entry = generate_general_ledger_entry(ledger_data, user=user)
        if not ledger_entry:
            return None

        # Create journal entries for the payment
        # Debit Bank/Cash account
        bank_account = QueryBuilderService("crmf_chart_of_account").where("account_type", "asset").first()
        if bank_account:
            debit_entry = {
                "date": timezone.now().date(),
                "account_id": bank_account.get("id"),
                "debit_amount": payment_data.get("paid_amount"),
                "credit_amount": 0,
                "description": f"Payment received for invoice {invoice.get('invoice_number')}"
            }
            generate_journal_entry(debit_entry, user=user)

        # Credit Accounts Receivable
        ar_account = QueryBuilderService("crmf_chart_of_account").where("account_type", "asset").first()
        if ar_account:
            credit_entry = {
                "date": timezone.now().date(),
                "account_id": ar_account.get("id"),
                "debit_amount": 0,
                "credit_amount": payment_data.get("paid_amount"),
                "description": f"Payment received for invoice {invoice.get('invoice_number')}"
            }
            generate_journal_entry(credit_entry, user=user)

        return ledger_entry
    except Exception as e:
        print(f"Error creating accounting entries for payment: {str(e)}")
        return None 