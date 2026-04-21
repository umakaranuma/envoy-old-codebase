from decimal import Decimal
from mServices import QueryBuilderService
from envoy_bu_policy_api.finance.controllers.utils.journal_entry_utils import create_commission_journal_entries_for_commissions

def update_revenue_realized(table_name, record_id, amount=None, invoice_id=None, paid_amount=None):
    """
    Increment the revenue_realized field for a given record in the specified table.
    For crmf_brokerage_commission, realize commission proportionally to invoice payment.
    For crmf_agent_commission, increment by amount (default logic).
    Args:
        table_name (str): Name of the table (e.g., 'crmf_brokerage_commission', 'crmf_agent_commission')
        record_id (int): ID of the record to update
        amount (Decimal or float or str, optional): Amount to add to revenue_realized (for agent commission)
        invoice_id (int, optional): Invoice ID (required for brokerage commission)
        paid_amount (Decimal or float or str, optional): Amount paid (required for brokerage commission)
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        record = QueryBuilderService(table_name).where("id", record_id).first()
        if not record or "revenue_realized" not in record or "revenue_recognized" not in record:
            return False
            
        current_value = Decimal(str(record["revenue_realized"]))
        recognized_value = Decimal(str(record["revenue_recognized"]))
        commission_deductible = Decimal(str(record.get("commission_deductible", "0.00")))
        
        if table_name == 'crmf_brokerage_commission':
            # Require invoice_id and paid_amount
            if invoice_id is None or paid_amount is None:
                print("invoice_id and paid_amount are required for brokerage commission realization.")
                return False
                
            invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()
            if not invoice or "invoice_amount" not in invoice:
                print("Invoice or invoice_amount not found.")
                return False
                
            paid_amount = Decimal(str(paid_amount))
            transaction_type_id = invoice.get("transaction_type_id")
            
            # Get brokerage commission type (fixed or percentage)
            brokerage_revenue_type = record.get("brokerage_revenue_type", "percentage")
            is_fixed_commission = brokerage_revenue_type in ["flat", "fixed"]
            
            # Keep invoice_amount for reference
            invoice_amount = Decimal(str(invoice["invoice_amount"]))
            
            # For FIXED commissions: Always use invoice_amount as the base
            # For PERCENTAGE commissions: 
            #   - For Addition invoices (transaction_type_id = 2): Use invoice_amount (same as fixed)
            #   - For other invoices: Use current premium amount from policy
            if is_fixed_commission:
                # Fixed commission: Calculate based on invoice amount
                # Example: Fixed 10,000, Invoice 25,000, Paid 25,000 → Realized = 10,000
                base_amount_for_calculation = invoice_amount
                print(f"DEBUG: Fixed commission detected - using invoice_amount ({invoice_amount}) as base for calculation")
            else:
                # Percentage commission: Check if this is an addition invoice
                if transaction_type_id == 2:  # Addition
                    # For addition invoices, use invoice_amount (same as fixed commissions)
                    base_amount_for_calculation = invoice_amount
                    print(f"DEBUG: Percentage commission detected for Addition invoice - using invoice_amount ({invoice_amount}) as base for calculation")
                else:
                    # For non-addition invoices, use current premium amount from policy
                    # Get current premium amount from issued policy (not original invoice amount)
                    # This ensures we use the updated premium amount after endorsements
                    issued_policy_id = invoice.get("issued_policy_id") or invoice.get("issued_policyId")
                    if issued_policy_id:
                        current_policy = QueryBuilderService("crmp_issued_policies").select("premium_amount").where("id", issued_policy_id).first()
                        if current_policy and current_policy.get("premium_amount"):
                            base_amount_for_calculation = Decimal(str(current_policy.get("premium_amount")))
                        else:
                            # Fallback to invoice amount if policy not found
                            base_amount_for_calculation = invoice_amount
                    else:
                        # Fallback to invoice amount if no issued_policy_id
                        base_amount_for_calculation = invoice_amount
                    print(f"DEBUG: Percentage commission detected for non-Addition invoice - using current_premium_amount ({base_amount_for_calculation}) as base for calculation")
            
            if base_amount_for_calculation <= 0:
                print("Base amount for calculation must be positive.")
                return False
                
            # Get current total paid amount from invoice (this is the total after the payment)
            current_total_paid = Decimal(str(invoice.get("paid_amount", "0.00")))
            
            # Get the actual payment amount from the most recent payment record for this invoice
            # This gives us the incremental payment for this transaction
            latest_payment = (
                QueryBuilderService("crmf_payments")
                .select("paid_amount")
                .where("invoice_id", invoice_id)
                .orderBy("id", "desc")
                .first()
            )
            
            if latest_payment and latest_payment.get("paid_amount"):
                # Use the actual payment amount from the payment record
                incremental_payment = Decimal(str(latest_payment.get("paid_amount")))
                previous_total_paid = current_total_paid - incremental_payment
            else:
                # Fallback: Calculate previous total paid from current realized amount
                # For fixed: If current_realized = (recognized / invoice_amount) * previous_total_paid
                # Then previous_total_paid = (current_realized * invoice_amount) / recognized
                # For percentage: If current_realized = (recognized / premium) * previous_total_paid
                # Then previous_total_paid = (current_realized * premium) / recognized
                if recognized_value > 0 and base_amount_for_calculation > 0:
                    previous_total_paid = (current_value * base_amount_for_calculation) / recognized_value
                    # Round to avoid precision issues
                    previous_total_paid = previous_total_paid.quantize(Decimal(".01"))
                else:
                    previous_total_paid = Decimal("0.00")
                
                # Calculate incremental payment amount for this transaction
                incremental_payment = current_total_paid - previous_total_paid
                if incremental_payment < 0:
                    incremental_payment = Decimal("0.00")
            
            # Calculate incremental realized amount
            # For FIXED: (recognized / invoice_amount) * incremental_payment
            #   Example: Fixed 10,000, Invoice 25,000, Payment 25,000 → (10,000 / 25,000) * 25,000 = 10,000
            # For PERCENTAGE: (recognized / premium) * incremental_payment
            #   Example: 10% commission, Premium 100,000, Payment 20,000 → (10,000 / 100,000) * 20,000 = 2,000
            incremental_realized = (recognized_value / base_amount_for_calculation) * incremental_payment if base_amount_for_calculation > 0 else Decimal("0.00")
            incremental_realized = incremental_realized.quantize(Decimal(".01"))
            
            # Add incremental to existing realized amount
            new_value = current_value + incremental_realized
            
            # IMPORTANT: Commission calculations for refund/cancellation types (transaction_type_id 4, 5)
            # are handled ONLY in create_endorsement, NOT in create_payment
            # This function should never be called for refund/cancellation invoices
            if transaction_type_id in [4, 5]:  # Refund (4) or Cancellation (5)
                print(f"ERROR: update_revenue_realized should NOT be called for refund/cancellation invoices (transaction_type_id: {transaction_type_id})")
                print(f"ERROR: All commission calculations for refund/cancellation must happen in create_endorsement only")
                return False
            
            # For premium invoices, deductible is stored but not applied here
            # Deductible is only applied when refund/cancellation invoice is paid, which happens in create_endorsement
            if commission_deductible > 0:
                print(f"DEBUG: Deductible {commission_deductible} exists but NOT applying - deductible is only applied when refund/cancellation invoice is paid (handled in create_endorsement)")
            
            print(f"DEBUG: Brokerage revenue_realized calculation:")
            print(f"  - Record ID: {record_id}")
            print(f"  - Commission Type: {brokerage_revenue_type} ({'FIXED' if is_fixed_commission else 'PERCENTAGE'})")
            print(f"  - Transaction Type ID: {transaction_type_id}")
            print(f"  - Recognized: {recognized_value}")
            base_source = 'invoice_amount' if (is_fixed_commission or transaction_type_id == 2) else 'current_premium_amount'
            print(f"  - Base amount for calculation: {base_amount_for_calculation} ({base_source})")
            print(f"  - Invoice amount: {invoice_amount}")
            print(f"  - Previous total paid amount: {previous_total_paid}")
            print(f"  - Current total paid amount: {current_total_paid}")
            print(f"  - Incremental payment: {incremental_payment}")
            print(f"  - Incremental realized: ({recognized_value}/{base_amount_for_calculation}) * {incremental_payment} = {incremental_realized}")
            print(f"  - Current realized: {current_value}")
            print(f"  - New realized: {current_value} + {incremental_realized} = {new_value}")
            print(f"  - Commission deductible: {commission_deductible}")
            
            # Update revenue_realized and paid_amount
            update_data = {
                "revenue_realized": str(new_value)
            }
            
            # For brokerage commission, also update paid_amount based on proportion
            if table_name == 'crmf_brokerage_commission':
                paid_amount_proportion = new_value  # The realized amount is what's been "paid" to the brokerage
                update_data["paid_amount"] = str(paid_amount_proportion)
            
            update_result = QueryBuilderService(table_name).where("id", record_id).update(update_data)
            print(f"DEBUG: Updated {table_name} record {record_id} with data: {update_data}")
            return bool(update_result)
        else:
            # Default: use amount
            if amount is None:
                print("Amount is required for agent commission realization.")
                return False
                
            increment = Decimal(str(amount))
            
            # If there's a deduction, apply it proportionally
            if commission_deductible > 0:
                invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()
                if invoice:
                    # Get current premium amount from issued policy
                    # Check for both issued_policy_id and issued_policyId (from JOIN alias)
                    issued_policy_id = invoice.get("issued_policy_id") or invoice.get("issued_policyId")
                    if issued_policy_id:
                        current_policy = QueryBuilderService("crmp_issued_policies").select("premium_amount").where("id", issued_policy_id).first()
                        if current_policy and current_policy.get("premium_amount"):
                            current_premium_amount = Decimal(str(current_policy.get("premium_amount")))
                        else:
                            current_premium_amount = Decimal(str(invoice.get("invoice_amount", "0")))
                    else:
                        current_premium_amount = Decimal(str(invoice.get("invoice_amount", "0")))
                    
                    if current_premium_amount > 0 and "paid_amount" in invoice:
                        proportion_paid = Decimal(str(invoice["paid_amount"])) / current_premium_amount
                        deduction = commission_deductible * proportion_paid
                        increment -= deduction
        
        new_value = current_value + increment
        
        # Clamp to [0, recognized_value] or [recognized_value, 0]
        if recognized_value >= 0:
            if new_value > recognized_value:
                new_value = recognized_value
            elif new_value < 0:
                new_value = Decimal("0.00")
        else:  # recognized_value is negative
            if new_value < recognized_value:
                new_value = recognized_value
            elif new_value > 0:
                new_value = Decimal("0.00")
                
        update_result = QueryBuilderService(table_name).where("id", record_id).update({
            "revenue_realized": str(new_value)
        })
        return bool(update_result)
    except Exception as e:
        print(f"Error updating revenue_realized: {e}")
        return False

def update_agent_commission_revenue_realized_for_brokerage_payment(brokerage_commission_id, invoice_id, paid_amount, calculation_mode=None):
    """
    Update all related agent commissions' revenue_realized when a brokerage commission is realized.
    
    IMPORTANT: This function does NOT update agent commission status.
    Agent commission status should only be updated at api/agent-commission-payments endpoint,
    not when customer payments are made at api/payments endpoint.
    
    Args:
        brokerage_commission_id (int): ID of the brokerage commission
        invoice_id (int): ID of the invoice
        paid_amount (Decimal/float/str): Amount paid on the invoice
        calculation_mode (str): 'premium' or 'paid'
    Returns:
        bool: True if all updates were successful, False otherwise
    """
    from envoy_bu_policy_api.finance.controllers.utils.service import get_commission_setup_service
    from .base_calculator import calculate_commission_base_amount, get_commission_calculation_mode
    from decimal import Decimal
    try:
        brokerage = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission_id).first()
        if not brokerage:
            print("Brokerage commission not found.")
            return False
        commission_setup_id = brokerage.get("commission_setup_id") or brokerage.get("commission_setup_id_id")
        if not commission_setup_id:
            print("No commission_setup_id on brokerage commission.")
            return False
        invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()
        if not invoice or "invoice_amount" not in invoice:
            print("Invoice or invoice_amount not found.")
            return False
        
        paid_amount = Decimal(str(paid_amount))
        
        # Get current premium amount from issued policy (not original invoice amount)
        # This ensures we use the updated premium amount after endorsements
        # Check for both issued_policy_id and issued_policyId (from JOIN alias)
        issued_policy_id = invoice.get("issued_policy_id") or invoice.get("issued_policyId")
        if issued_policy_id:
            current_policy = QueryBuilderService("crmp_issued_policies").select("premium_amount").where("id", issued_policy_id).first()
            if current_policy and current_policy.get("premium_amount"):
                current_premium_amount = Decimal(str(current_policy.get("premium_amount")))
            else:
                # Fallback to invoice amount if policy not found
                current_premium_amount = Decimal(str(invoice["invoice_amount"]))
        else:
            # Fallback to invoice amount if no issued_policy_id
            current_premium_amount = Decimal(str(invoice["invoice_amount"]))
        
        if current_premium_amount <= 0:
            print("Current premium amount must be positive.")
            return False
        
        # Keep invoice_amount for reference
        invoice_amount = Decimal(str(invoice["invoice_amount"]))
        # Get commission setup and values
        product_id = invoice.get("product_id")
        insurer_id = invoice.get("insurer_id")
        transaction_type = invoice.get("transaction_type_id")
        commission_setup = get_commission_setup_service(product_id, insurer_id, transaction_type)
        commission_values = commission_setup.get("commission_values", {}) if commission_setup and commission_setup != ("NOT_FOUND",) else {}
        agent_commission_percent_list = commission_values.get("agent_commission_percent", [])
        # Get all agent commissions for this brokerage commission
        agent_commissions = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", brokerage_commission_id).get()
        all_success = True
        calculation_mode = get_commission_calculation_mode(calculation_mode)
        for agent_comm in agent_commissions:
            agent_id = agent_comm.get("agent_id")
            # Check for revised commission for this agent
            revised_amount = Decimal(str(agent_comm.get("revised_amount", "0")))
            revised_amount_percent = Decimal(str(agent_comm.get("revised_amount_percent", "0")))
            revised_amount_type = agent_comm.get("revised_amount_type", "percentage")
            agent_commission_type = agent_comm.get("agent_commission_type", "percentage")
            recognized_value = Decimal(str(agent_comm["revenue_recognized"]))
            current_realized = Decimal(str(agent_comm["revenue_realized"]))
            
            # Determine agent commission type (revised takes priority)
            # If revised commission exists and has a type, use that; otherwise use regular agent_commission_type
            if revised_amount > 0 or revised_amount_percent > 0:
                agent_type = revised_amount_type
            else:
                agent_type = agent_commission_type
            
            # Get transaction type to determine if this is an addition invoice
            transaction_type_id = invoice.get("transaction_type_id")
            
            # Determine base amount for calculation based on agent commission type and transaction type
            # For FIXED agent commissions: Always use invoice_amount (like brokerage fixed does)
            # For PERCENTAGE agent commissions:
            #   - For Addition invoices (transaction_type_id = 2): Use invoice_amount (same as fixed)
            #   - For other invoices: Use current_premium_amount (from policy)
            is_fixed_agent_commission = agent_type in ["flat", "fixed"]
            if is_fixed_agent_commission:
                # Fixed agent commission: Use invoice_amount as base (same as brokerage fixed)
                base_amount_for_calculation = invoice_amount
                print(f"DEBUG: Fixed agent commission detected - using invoice_amount ({invoice_amount}) as base for calculation")
            else:
                # Percentage agent commission: Check if this is an addition invoice
                if transaction_type_id == 2:  # Addition
                    # For addition invoices, use invoice_amount (same as fixed commissions)
                    base_amount_for_calculation = invoice_amount
                    print(f"DEBUG: Percentage agent commission detected for Addition invoice - using invoice_amount ({invoice_amount}) as base for calculation")
                else:
                    # For non-addition invoices, use current_premium_amount from policy
                    base_amount_for_calculation = current_premium_amount
                    print(f"DEBUG: Percentage agent commission detected for non-Addition invoice - using current_premium_amount ({current_premium_amount}) as base for calculation")
            
            # Always use the stored revenue_recognized value for realization calculation
            # This ensures consistency with what was originally calculated (including revised commission if applicable)
            # Calculate incremental realized amount: (recognized / base) * incremental_payment
            # Example (Fixed): Agent commission = 10 (fixed), Invoice = 25000, Payment = 25000
            # Incremental realized = (10 / 25000) * 25000 = 10
            # Example (Percentage): Agent commission = 10% of brokerage, Premium = 60000, Payment = 20000
            # Incremental realized = (recognized / 60000) * 20000
            
            # Get current total paid amount from invoice (this is the total after the payment)
            current_total_paid = Decimal(str(invoice.get("paid_amount", "0.00")))
            
            # Get the actual payment amount from the most recent payment record for this invoice
            # This gives us the incremental payment for this transaction
            latest_payment = (
                QueryBuilderService("crmf_payments")
                .select("paid_amount")
                .where("invoice_id", invoice_id)
                .orderBy("id", "desc")
                .first()
            )
            
            if latest_payment and latest_payment.get("paid_amount"):
                # Use the actual payment amount from the payment record
                incremental_payment = Decimal(str(latest_payment.get("paid_amount")))
                previous_total_paid = current_total_paid - incremental_payment
            else:
                # Fallback: Calculate previous total paid from current realized amount
                # If current_realized = (recognized / base) * previous_total_paid
                # Then previous_total_paid = (current_realized * base) / recognized
                if recognized_value > 0 and base_amount_for_calculation > 0:
                    previous_total_paid = (current_realized * base_amount_for_calculation) / recognized_value
                    # Round to avoid precision issues
                    previous_total_paid = previous_total_paid.quantize(Decimal(".01"))
                else:
                    previous_total_paid = Decimal("0.00")
                
                # Calculate incremental payment amount for this transaction
                incremental_payment = current_total_paid - previous_total_paid
                if incremental_payment < 0:
                    incremental_payment = Decimal("0.00")
            
            # Calculate incremental realized: (recognized / base) * incremental_payment
            incremental_realized = (recognized_value / base_amount_for_calculation) * incremental_payment if base_amount_for_calculation > 0 else Decimal("0.00")
            incremental_realized = incremental_realized.quantize(Decimal(".01"))
            
            # Add incremental to existing realized amount
            new_realized = current_realized + incremental_realized
            
            # Log debug information
            if revised_amount > 0 or revised_amount_percent > 0:
                print(f"DEBUG: Using revised commission for agent {agent_id}:")
                print(f"  - Revised amount: {revised_amount}")
                print(f"  - Revised percent: {revised_amount_percent}")
                print(f"  - Revised type: {revised_amount_type}")
                print(f"  - Agent commission type: {agent_type} ({'FIXED' if is_fixed_agent_commission else 'PERCENTAGE'})")
                print(f"  - Transaction Type ID: {transaction_type_id}")
                print(f"  - Recognized value: {recognized_value}")
                base_source = 'invoice_amount' if (is_fixed_agent_commission or transaction_type_id == 2) else 'current_premium_amount'
                print(f"  - Base amount for calculation: {base_amount_for_calculation} ({base_source})")
                print(f"  - Current premium amount (from policy): {current_premium_amount}")
                print(f"  - Invoice amount: {invoice_amount}")
                print(f"  - Previous total paid amount: {previous_total_paid}")
                print(f"  - Current total paid amount: {current_total_paid}")
                print(f"  - Incremental payment: {incremental_payment}")
                print(f"  - Incremental realized: ({recognized_value}/{base_amount_for_calculation}) * {incremental_payment} = {incremental_realized}")
                print(f"  - Current realized: {current_realized}")
                print(f"  - New realized: {current_realized} + {incremental_realized} = {new_realized}")
            else:
                print(f"DEBUG: Using original commission for agent {agent_id}:")
                print(f"  - Agent commission type: {agent_type} ({'FIXED' if is_fixed_agent_commission else 'PERCENTAGE'})")
                print(f"  - Transaction Type ID: {transaction_type_id}")
                print(f"  - Recognized value: {recognized_value}")
                base_source = 'invoice_amount' if (is_fixed_agent_commission or transaction_type_id == 2) else 'current_premium_amount'
                print(f"  - Base amount for calculation: {base_amount_for_calculation} ({base_source})")
                print(f"  - Current premium amount (from policy): {current_premium_amount}")
                print(f"  - Invoice amount: {invoice_amount}")
                print(f"  - Previous total paid amount: {previous_total_paid}")
                print(f"  - Current total paid amount: {current_total_paid}")
                print(f"  - Incremental payment: {incremental_payment}")
                print(f"  - Incremental realized: ({recognized_value}/{base_amount_for_calculation}) * {incremental_payment} = {incremental_realized}")
                print(f"  - Current realized: {current_realized}")
                print(f"  - New realized: {current_realized} + {incremental_realized} = {new_realized}")
            
            # IMPORTANT: Commission calculations for refund/cancellation types (transaction_type_id 4, 5)
            # are handled ONLY in create_endorsement, NOT in create_payment
            # This function should never be called for refund/cancellation invoices
            # transaction_type_id is already retrieved earlier in the loop
            if transaction_type_id in [4, 5]:  # Refund (4) or Cancellation (5)
                print(f"ERROR: update_agent_commission_revenue_realized_for_brokerage_payment should NOT be called for refund/cancellation invoices (transaction_type_id: {transaction_type_id})")
                print(f"ERROR: All commission calculations for refund/cancellation must happen in create_endorsement only")
                return
            
            # For premium invoices, deductible is stored but not applied here
            # Deductible is only applied when refund/cancellation invoice is paid, which happens in create_endorsement
            commission_deductible = Decimal(str(agent_comm.get("commission_deductible", "0.00")))
            if commission_deductible > 0:
                print(f"DEBUG: Agent deductible {commission_deductible} exists but NOT applying - deductible is only applied when refund/cancellation invoice is paid (handled in create_endorsement)")
            
            # Clamp to [0, recognized_value] or [recognized_value, 0]
            if recognized_value >= 0:
                if new_realized > recognized_value:
                    new_realized = recognized_value
                elif new_realized < 0:
                    new_realized = Decimal("0.00")
            else:
                if new_realized < recognized_value:
                    new_realized = recognized_value
                elif new_realized > 0:
                    new_realized = Decimal("0.00")

            # Calculate proportion for display purposes
            proportion_paid = (incremental_payment / base_amount_for_calculation * 100) if base_amount_for_calculation > 0 else Decimal("0")
            print(f"Agent commission revenue_realized: agent_id={agent_id}, agent_type={agent_type}, recognized_value={recognized_value}, base_amount={base_amount_for_calculation}, incremental_payment={incremental_payment}, incremental_proportion={proportion_paid:.2f}%, new_realized={new_realized}")

            # ========== DEBUG: Get current status BEFORE update ==========
            print(f"\n{'='*60}")
            print(f"DEBUG COMMISSION_PAY_UTILS: Agent Commission ID {agent_comm['id']}")
            print(f"{'='*60}")
            current_status = agent_comm.get("status", "pending")
            current_revenue_realized = agent_comm.get("revenue_realized", 0)
            print(f"  - Current Status (BEFORE update): '{current_status}'")
            print(f"  - Current Revenue Realized (BEFORE): {current_revenue_realized}")
            print(f"  - New Revenue Realized (to be set): {new_realized}")
            print(f"  - Revenue Recognized: {recognized_value}")
            
            # IMPORTANT: Status should NOT be updated here - it only updates at api/agent-commission-payments endpoint
            # This ensures status reflects actual payments made to agents, not just customer payments
            print(f"  - ⚠️  IMPORTANT: Status will be PRESERVED as '{current_status}' (not recalculated)")
            
            # Update revenue_realized and paid_amount, but explicitly preserve status
            # By including status in update_data with the current value, we prevent any automatic recalculation
            update_data = {
                "revenue_realized": str(new_realized),
                "paid_amount": str(new_realized),  # The realized amount is what's been "paid" to the agent
                "status": current_status  # Explicitly preserve current status to prevent automatic changes
            }
            print(f"  - Update Data: {update_data}")
            print(f"{'='*60}\n")
            
            update_result = QueryBuilderService("crmf_agent_commission").where("id", agent_comm["id"]).update(update_data)
            
            # ========== DEBUG: Verify status after update ==========
            print(f"DEBUG COMMISSION_PAY_UTILS: After update for Agent Commission ID {agent_comm['id']}")
            print(f"  - Update Result: {update_result}")
            
            # Immediately verify the status was preserved
            ac_after_update = QueryBuilderService("crmf_agent_commission").where("id", agent_comm["id"]).first()
            if ac_after_update:
                status_after = ac_after_update.get("status")
                revenue_realized_after = ac_after_update.get("revenue_realized", 0)
                print(f"  - Status AFTER update: '{status_after}'")
                print(f"  - Revenue Realized AFTER update: {revenue_realized_after}")
                
                if status_after != current_status:
                    print(f"  - ❌ ERROR: Status changed from '{current_status}' to '{status_after}'!")
                    print(f"  - Attempting to restore status to '{current_status}'...")
                    restore_result = QueryBuilderService("crmf_agent_commission").where("id", agent_comm["id"]).update({"status": current_status})
                    print(f"  - Restore result: {restore_result}")
                    
                    # Verify again
                    ac_restored = QueryBuilderService("crmf_agent_commission").where("id", agent_comm["id"]).first()
                    if ac_restored:
                        final_status = ac_restored.get("status")
                        print(f"  - Final status after restore attempt: '{final_status}'")
                        if final_status == current_status:
                            print(f"  - ✅ Status successfully restored")
                        else:
                            print(f"  - ❌ FAILED to restore status!")
                else:
                    print(f"  - ✅ Status correctly preserved as '{current_status}'")
            else:
                print(f"  - ⚠️  Could not retrieve commission after update")
            
            print(f"DEBUG: Agent commission status preserved as '{current_status}' - status only updates at api/agent-commission-payments endpoint\n")
            if not update_result:
                all_success = False
        # After updating revenue_realized, create realization journal entries
        all_commissions = []
        brokerage_commission_record = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission_id).first()
        if brokerage_commission_record:
            all_commissions.append(brokerage_commission_record)
        agent_commissions = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", brokerage_commission_id).get()
        all_commissions.extend(agent_commissions)
        invoice_record = QueryBuilderService("crmf_invoices").where("id", invoice_id).first() if invoice_id else None
        if invoice_record:
            create_commission_journal_entries_for_commissions(all_commissions, invoice_record, realized=True, adjustment=False)
        return all_success
    except Exception as e:
        print(f"Error updating agent commission revenue_realized: {e}")
        return False


