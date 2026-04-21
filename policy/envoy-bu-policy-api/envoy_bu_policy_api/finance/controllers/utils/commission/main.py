from decimal import Decimal
from mServices import QueryBuilderService
from envoy_bu_policy_api.service import handle_entity
from envoy_bu_policy_api.finance.controllers.utils.service import get_commission_setup_service
from envoy_bu_policy_api.finance.config.transaction_types import is_commissionable
from .base_calculator import calculate_commission_base_amount
from .deduction_utils import handle_commission_deduction
from .commission_journal_utils import create_brokerage_commission_journal_entry, create_agent_commission_journal_entry
from envoy_bu_policy_api.finance.controllers.utils.journal_entry_utils import create_commission_journal_entries_for_commissions

def calculate_commission_amounts(invoice_id, transaction_type_id, product_id, insurer_id, sales_agent_id,
                               invoice_amount, paid_amount, calculation_mode=None, user=None):
    """
    Calculate brokerage and agent commission amounts for an invoice
    
    Args:
        invoice_id (int): ID of the invoice
        transaction_type_id (int): ID of the transaction type
        product_id (int): ID of the product
        insurer_id (int): ID of the insurer
        invoice_amount (Decimal): Total invoice amount
        paid_amount (Decimal): Amount paid so far
        calculation_mode (str): "premium" or "paid"
        user (User, optional): User creating the commission
        
    Returns:
        tuple: (brokerage_commission_id, agent_commission_id) or (None, None) if not commissionable
    """
    from .base_calculator import get_commission_calculation_mode
    calculation_mode = get_commission_calculation_mode(calculation_mode)
    
    # Handle refunds and cancellations using deduction utils
    if transaction_type_id in [4, 5]:  # Refund or Cancellation
        return handle_commission_deduction(
            invoice_id=invoice_id,
            transaction_type_id=transaction_type_id,
            product_id=product_id,
            insurer_id=insurer_id,
            sales_agent_id=sales_agent_id,
            invoice_amount=invoice_amount,
            paid_amount=paid_amount,
            calculation_mode=calculation_mode,
            user=user
        )
        
    if not is_commissionable(transaction_type_id):
        return None, None
    try:
        # Normalize invoice_id to ensure it's an integer
        if isinstance(invoice_id, dict):
            invoice_id_value = invoice_id.get('id')
        else:
            invoice_id_value = invoice_id
        
        if not invoice_id_value:
            print(f"ERROR: Invalid invoice_id: {invoice_id}")
            return None, None
        
        # Get product_id and product_group_id from policy base via invoice
        policy_product_id = None
        policy_product_group_id = None
        
        # Invoice → Issued Policy → Policy Base
        invoice = QueryBuilderService("crmf_invoices").select("issued_policy_id").where("id", invoice_id_value).first()
        if invoice and invoice.get("issued_policy_id"):
            policy_base = QueryBuilderService("crmp_issued_policies").select("policy_base_id").where("id", invoice["issued_policy_id"]).first()
            if policy_base and policy_base.get("policy_base_id"):
                policy_base_data = QueryBuilderService("crmp_policy_base").select("product_id", "product_group_id").where("id", policy_base["policy_base_id"]).first()
                if policy_base_data:
                    policy_product_id = policy_base_data.get("product_id")
                    policy_product_group_id = policy_base_data.get("product_group_id")
        
        # Use policy base data for commission setup matching (NOT invoice data)
        print(f"Fetching commission setup for: policy_product_id={policy_product_id}, insurer_id={insurer_id}, transaction_type_id={transaction_type_id}, policy_product_group_id={policy_product_group_id}")
        commission_setup = get_commission_setup_service(policy_product_id, insurer_id, transaction_type_id, policy_product_group_id)
        
        # For Addition (transaction_type_id=2): If no setup found, do NOT calculate commissions (no fallback to New Business)
        if commission_setup == ("NOT_FOUND",) and transaction_type_id == 2:
            print(f"WARNING: Commission setup NOT FOUND for Addition (transaction_type_id=2)")
            print(f"  - No commission will be calculated for this Addition invoice")
            print(f"  - SOLUTION: Create a commission setup for Addition type (transaction_type_id=2) for this product/insurer combination")
            return None, None
        
        if commission_setup == ("NOT_FOUND",):
            print(f"ERROR: Commission setup NOT FOUND for policy_product_id={policy_product_id}, insurer_id={insurer_id}, transaction_type_id={transaction_type_id}, policy_product_group_id={policy_product_group_id}")
            print(f"  - SOLUTION: Create a commission setup for this product/insurer/transaction combination")
            return None, None
            
        print(f"Commission setup found: ID={commission_setup.get('id')}")
        print("Commission setup:", commission_setup)
        
        # Get commission values from the setup 
        commission_values = commission_setup.get("commission_values", {}) #multi
        print("Commission values:", commission_values)
        
        # Calculate base amount for commission
        # For revenue_recognized, always use invoice_amount to show expected total commission
        # The calculation_mode will be used later for revenue_realized
        base_amount = calculate_commission_base_amount(invoice_amount, paid_amount, calculation_mode)
        
        # Calculate brokerage commission (brokerage_revenue_percent)
        brokerage_data = commission_values.get("brokerage_revenue_percent", [{"value": "0", "type": "flat"}])[0]
        print("Brokerage data:", brokerage_data)
        
        # Handle empty strings - convert to "0" before Decimal conversion
        raw_brokerage_value = brokerage_data.get("value", "0")
        if raw_brokerage_value == "" or raw_brokerage_value is None:
            raw_brokerage_value = "0"
        brokerage_percent = Decimal(str(raw_brokerage_value))
        print("Brokeragexxpercent:", brokerage_percent)
        brokerage_type = brokerage_data.get("type", "flat")
        print("brokerage_type:", brokerage_type)
        if brokerage_type in ["flat", "fixed"]:
            brokerage_amount = brokerage_percent
        else:
            # Always calculate based on invoice_amount for revenue_recognized
            brokerage_amount = (invoice_amount * brokerage_percent / Decimal("100")).quantize(Decimal(".01"))
        
        print("brokerage_amounttype:", brokerage_amount)
        print(f"Brokerage commission calculated: percent={brokerage_percent}, type={brokerage_type}, amount={brokerage_amount}")
        # Create entity for brokerage commission
        entity_data = {"type": "brokerage_commission", "approvel_status": False}
        entity_id = handle_entity(entity_data, user=user)
        
        # Use normalized invoice_id_value
        invoice = invoice_id_value
        
        # Insert brokerage commission
        brokerage_insert_data = {
            "invoice_id": invoice,
            "brokerage_revenue_percent": str(brokerage_percent),
            "brokerage_revenue_type": brokerage_type,
            "revenue_recognized": str(brokerage_amount),
            "commission_deductible": "0.00",
            "revenue_realized": "0.00",
            "overriding_commission_amount": "0.00",
            "agent_commission": "0.00",
            "status": "issued",
            "entity_id": entity_id,
            "base_amount": str(invoice_amount),  # Store invoice amount as base
            "commission_setup_id":commission_setup.get("id"),
            "calculation_mode": calculation_mode
        }
        print(f"Creating brokerage commission record: {brokerage_insert_data}")
        brokerage_result = QueryBuilderService("crmf_brokerage_commission").insert(brokerage_insert_data)
        
        if not brokerage_result:
            return None, None
            
        # Extract the ID from the result
        if isinstance(brokerage_result, dict):
            brokerage_commission_id = brokerage_result.get('id')
        else:
            brokerage_commission_id = brokerage_result
            
        if not brokerage_commission_id:
            return None, None
        
        #-------- before agent commission calculation
        # Calculate agent commissions
        agent_commissions = []
        revised_data_list = commission_values.get("revised_commission_percent", [])
        agent_data_list = commission_values.get("agent_commission_percent", []) #produt array
        print("Agent data list:", agent_data_list)
        print("Revised data list:", revised_data_list)
        print("Processing user_id:", sales_agent_id)
        
        # NEW: Fallback - if agent_data_list has no user-specific entries, apply to current sales_agent_id
        if sales_agent_id and agent_data_list and not any(item.get("user_id") for item in agent_data_list):
            base_agent = agent_data_list[0]
            agent_data_list = [{"value": base_agent.get("value"), "type": base_agent.get("type"), "user_id": sales_agent_id}]
        
        # Only use agent_data_list for agent commission calculation
        for user_data in agent_data_list:
            user_id = user_data.get("user_id")
            if user_id is None:
                continue
            
            # Check if sales_agent_id matches
            agent_matches = False
            try:
                if sales_agent_id and int(user_id) == int(sales_agent_id):
                    agent_matches = True
            except (ValueError, TypeError):
                pass
            
            # If sales_agent_id is provided but doesn't match, skip
            if sales_agent_id and not agent_matches:
                continue
                
            # Handle empty strings - convert to "0" before Decimal conversion
            raw_value = user_data.get("value", "0")
            if raw_value == "" or raw_value is None:
                raw_value = "0"
            value = Decimal(str(raw_value))
            type_ = user_data.get("type", "flat")
            print("type_type_:", type_)
            
            # Calculate revised_amount and revised_commission_percent if a revised commission exists for this user
            # --- NEW LOGIC: pick the highest revised commission for this user ---
            # First, calculate brokerage commission amount once (needed for revised commission calculation)
            if brokerage_type in ["flat", "fixed"]:
                brokerage_amount = brokerage_percent
            else:
                brokerage_amount = (invoice_amount * brokerage_percent / Decimal("100")).quantize(Decimal(".01"))
            
            user_revised_entries = [r for r in revised_data_list if r.get("user_id") == user_id]
            highest_revised = None
            highest_amount = Decimal("0.00")
            revised_commission_percent = "0"
            revised_amount = "0.00"
            revised_type = "percentage"
            
            for entry in user_revised_entries:
                # Handle empty strings - convert to "0" before Decimal conversion
                raw_revised_value = entry.get("value", "0")
                if raw_revised_value == "" or raw_revised_value is None:
                    raw_revised_value = "0"
                revised_value = Decimal(str(raw_revised_value))
                revised_type_entry = entry.get("type", "flat")
                if revised_type_entry == "fixed":
                    amount = revised_value
                else:
                    # Revised commission should be calculated based on brokerage commission amount, not invoice amount
                    # Calculate revised commission as percentage of brokerage commission
                    amount = (brokerage_amount * revised_value / Decimal("100")).quantize(Decimal(".01"))
                if amount > highest_amount:
                    highest_amount = amount
                    highest_revised = entry
                    revised_commission_percent = str(revised_value)
                    revised_type = revised_type_entry
                    if revised_type_entry == "fixed":
                        revised_amount = str(revised_value)
                    else:
                        revised_amount = str(amount)
            
            # Always calculate the expected commission amount for revenue_recognized
            # This shows what the agent should earn based on the total invoice
            # If revised_amount is available and > 0, use revised commission for ALL calculations
            if Decimal(revised_amount) > 0:
                # Use revised commission for calculation - don't use regular agent commission
                # If revised type is fixed and there's a payment, calculate proportionally
                if revised_type == "fixed" and paid_amount > 0 and invoice_amount > 0:
                    # Calculate proportional recognized amount: revised_fixed * (paid_amount / invoice_amount)
                    # Example: 6,000 * (20,000 / 100,000) = 1,200
                    revenue_recognized = (Decimal(revised_amount) * paid_amount / invoice_amount).quantize(Decimal(".01"))
                    print(f"Using revised fixed commission (proportional to payment): user_id={user_id}, revised_amount={revised_amount}, paid_amount={paid_amount}, invoice_amount={invoice_amount}, revenue_recognized={revenue_recognized}")
                else:
                    revenue_recognized = Decimal(revised_amount)
                    print(f"Using revised commission: user_id={user_id}, revised_amount={revised_amount}, revised_percent={revised_commission_percent}, brokerage_amount={brokerage_amount}")
                
                # When revised commission exists, use revised values for agent_commission_percent and agent_commission_type
                # This ensures the commission is calculated based on revised commission, not regular agent commission
                if revised_type == "fixed":
                    agent_commission_percent = "0"
                else:
                    agent_commission_percent = revised_commission_percent
                # Use revised_type for agent_commission_type when revised commission exists
                type_ = revised_type
                print(f"Using revised commission values: agent_commission_percent={agent_commission_percent}, agent_commission_type={revised_type}")
            else:
                # No revised commission - use regular agent commission calculation
                if type_ == "fixed":
                    revenue_recognized = value
                else:
                    # Agent commission percentage should be calculated based on brokerage amount, not invoice amount
                    # Calculate agent commission as percentage of brokerage commission
                    revenue_recognized = (brokerage_amount * value / Decimal("100")).quantize(Decimal(".01"))
                print(f"Agent commission calculated: user_id={user_id}, value={value}, type={type_}, revenue_recognized={revenue_recognized}")
                
                # For fixed type, agent_commission_percent should be 0 (not the fixed amount value)
                # The fixed amount is stored in revenue_recognized, not in the percentage field
                if type_ == "fixed":
                    agent_commission_percent = "0"
                else:
                    agent_commission_percent = str(value)
            bonus_amount = "0.00"
            target_amount = "0.00"
            # Create entity for agent commission
            entity_data = {"type": "agent_commission", "approvel_status": False}
            entity_id = handle_entity(entity_data, user=user)
            insert_data = {
                "brokerage_commission_id": int(brokerage_commission_id),
                "agent_id": int(user_id),
                "agent_commission_percent": agent_commission_percent,
                "agent_commission_type": type_,
                "revised_amount_percent": revised_commission_percent,
                "revised_amount_type": revised_type,
                "target_achievement_amount": target_amount,
                "bonus_amount": bonus_amount,
                "revised_amount": revised_amount,
                "revenue_recognized": str(revenue_recognized),
                "revenue_realized": "0.00",
                "paid_amount":"0.00",
                "commission_deductible": "0.00",
                "status": "PENDING",
                "entity_id": int(entity_id),
                "base_amount": str(invoice_amount),  # Store invoice amount as base
                "commission_setup_id":commission_setup.get("id"),
                "calculation_mode": calculation_mode
            }
            print(f"Creating agent commission record: {insert_data}")
            result = QueryBuilderService("crmf_agent_commission").insert(insert_data)
            if result:
                agent_id = result.get('id') if isinstance(result, dict) else result
                agent_commissions.append(agent_id)
                print(f"Successfully created agent commission with ID: {agent_id}")
            else:
                print(f"ERROR: Failed to create agent commission for user_id={user_id}")
        
        # Check if any agent commissions were created
        if len(agent_commissions) == 0 and sales_agent_id:
            print(f"WARNING: No agent commissions created for sales_agent_id {sales_agent_id}!")
            print(f"  - agent_data_list: {agent_data_list}")
            print(f"  - Available user_ids in commission setup: {[d.get('user_id') for d in agent_data_list]}")
            print(f"  - Creating fallback agent commission with default rate")
            
            # Create a fallback agent commission with default rate
            fallback_value = Decimal("0.00")
            fallback_type = "percentage"
            if agent_data_list:
                # Use the first agent's rate as fallback
                fallback_agent = agent_data_list[0]
                # Handle empty strings - convert to "0" before Decimal conversion
                raw_fallback_value = fallback_agent.get("value", "0")
                if raw_fallback_value == "" or raw_fallback_value is None:
                    raw_fallback_value = "0"
                fallback_value = Decimal(str(raw_fallback_value))
                fallback_type = fallback_agent.get("type", "percentage")
            
            # Calculate revenue_recognized for fallback
            # First, ensure brokerage_amount is calculated (reuse the calculation from above)
            if brokerage_type in ["flat", "fixed"]:
                fallback_brokerage_amount = brokerage_percent
            else:
                fallback_brokerage_amount = (invoice_amount * brokerage_percent / Decimal("100")).quantize(Decimal(".01"))
            
            if fallback_type == "fixed":
                fallback_revenue = fallback_value
            else:
                # Agent commission percentage should be calculated based on brokerage amount, not invoice amount
                # Calculate agent commission as percentage of brokerage commission
                fallback_revenue = (fallback_brokerage_amount * fallback_value / Decimal("100")).quantize(Decimal(".01"))
            
            # Create entity for fallback agent commission
            entity_data = {"type": "agent_commission", "approvel_status": False}
            entity_id = handle_entity(entity_data, user=user)
            # For fixed type, agent_commission_percent should be 0 (not the fixed amount value)
            if fallback_type == "fixed":
                fallback_agent_commission_percent = "0"
            else:
                fallback_agent_commission_percent = str(fallback_value)
            fallback_insert_data = {
                "brokerage_commission_id": int(brokerage_commission_id),
                "agent_id": int(sales_agent_id),
                "agent_commission_percent": fallback_agent_commission_percent,
                "agent_commission_type": fallback_type,
                "revised_amount_percent": "0",
                "revised_amount_type": "percentage",
                "target_achievement_amount": "0.00",
                "bonus_amount": "0.00",
                "revised_amount": "0.00",
                "revenue_recognized": str(fallback_revenue),
                "revenue_realized": "0.00",
                "paid_amount": "0.00",
                "commission_deductible": "0.00",
                "status": "PENDING",
                "entity_id": int(entity_id),
                "base_amount": str(invoice_amount),
                "commission_setup_id": commission_setup.get("id"),
                "calculation_mode": calculation_mode
            }
            print(f"Creating fallback agent commission record: {fallback_insert_data}")
            result = QueryBuilderService("crmf_agent_commission").insert(fallback_insert_data)
            if result:
                agent_id = result.get('id') if isinstance(result, dict) else result
                agent_commissions.append(agent_id)
                print(f"Successfully created fallback agent commission with ID: {agent_id}")
            else:
                print(f"ERROR: Failed to create fallback agent commission for sales_agent_id={sales_agent_id}")
        
        # Update total agent commission in brokerage record
        total_agent_commission = Decimal("0.00")
        for agent_id in agent_commissions:
            revenue_result = QueryBuilderService("crmf_agent_commission").where("id", agent_id).first()
            if revenue_result and "revenue_recognized" in revenue_result:
                total_agent_commission += Decimal(str(revenue_result["revenue_recognized"]))
        
        # Convert total to string before updating
        update_data = {
            "agent_commission": str(total_agent_commission)
        }
        
        QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission_id).update(update_data)
        
        # Create journal entries for recognized commissions
        brokerage_commission = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission_id).first()
        invoice_obj = QueryBuilderService("crmf_invoices").where("id", invoice_id_value).first()
        create_brokerage_commission_journal_entry(brokerage_commission, invoice_obj, user, realized=False)
        for agent_id in agent_commissions:
            agent_commission = QueryBuilderService("crmf_agent_commission").where("id", agent_id).first()
            create_agent_commission_journal_entry(agent_commission, invoice_obj, user, realized=False)
        
        # After all commission records are created:
        all_commissions = []
        # Add brokerage commission
        brokerage_commission_record = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission_id).first()
        if brokerage_commission_record:
            all_commissions.append(brokerage_commission_record)
        # Add agent commissions
        for agent_id in agent_commissions:
            agent_commission_record = QueryBuilderService("crmf_agent_commission").where("id", agent_id).first()
            if agent_commission_record:
                all_commissions.append(agent_commission_record)
        # Create recognized journal entries for all commissions
        invoice_record = QueryBuilderService("crmf_invoices").where("id", invoice_id_value).first() if invoice_id_value else None
        if invoice_record:
            create_commission_journal_entries_for_commissions(all_commissions, invoice_record, user=user, realized=False, adjustment=False)
        
        return brokerage_commission_id, agent_commissions
        
    except Exception as e:
        print(f"Error calculating commissions: {str(e)}")
        return None, None 

