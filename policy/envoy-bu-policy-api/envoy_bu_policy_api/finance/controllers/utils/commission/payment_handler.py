from mServices import QueryBuilderService
from .main import calculate_commission_amounts

def update_commission_for_payment(brokerage_commission_id, paid_amount, calculation_mode):
    """
    Update commission amounts when payment is received
    
    Args:
        brokerage_commission_id (int): ID of the brokerage commission
        paid_amount (Decimal): New paid amount
        calculation_mode (str): Calculation mode
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get existing brokerage commission
        brokerage = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission_id).first()
        if not brokerage:
            return False
            
        # Get invoice details
        invoice = QueryBuilderService("crmf_invoices").where("id", brokerage["invoice_id"]).first()
        if not invoice:
            return False
            
        # Recalculate commissions with new paid amount
        result = calculate_commission_amounts(
            invoice_id=brokerage["invoice_id"],
            transaction_type_id=invoice["transaction_type_id"],
            product_id=invoice["product_id"],
            insurer_id=invoice["insurer_id"],
            sales_agent_id=invoice.get("sales_agent_id"),
            invoice_amount=invoice["amount"],
            paid_amount=paid_amount,
            calculation_mode=calculation_mode
        )
        
        if not result:
            return False
            
        new_brokerage_id, new_agent_ids = result
        
        # Update status of old commissions
        QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission_id).update({"status": "superseded"})
        QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", brokerage_commission_id).update({"status": "superseded"})
        
        return True
        
    except Exception as e:
        print(f"Error updating commission for payment: {str(e)}")
        return False 