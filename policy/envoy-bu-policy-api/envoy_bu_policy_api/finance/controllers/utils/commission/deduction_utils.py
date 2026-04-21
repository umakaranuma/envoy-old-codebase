from decimal import Decimal
from mServices import QueryBuilderService
from .base_calculator import calculate_commission_base_amount, get_commission_calculation_mode
from envoy_bu_policy_api.finance.controllers.utils.service import get_commission_setup_service
from envoy_bu_policy_api.finance.controllers.utils.journal_entry_utils import  create_commission_deduction_journal_entries
from envoy_bu_policy_api.service import handle_entity

def safe_decimal(val, default="0.00"):
    try:
        if val is None or val == "":
            return Decimal(default)
        return Decimal(str(val))
    except Exception:
        return Decimal(default)

def get_invoices_for_policy_ordered(issued_policy_id):
    """
    Get all invoices for an issued_policy_id, ordered by:
    1. Addition invoices (transaction_type_id = 2) - newest first (by id desc)
    2. Premium invoices (transaction_type_id = 1 or 3) - oldest first (by id asc)
    
    This ordering ensures deductible is distributed to newest addition invoices first,
    then moves to older addition invoices, and finally to premium invoice.
    
    Args:
        issued_policy_id (int): ID of the issued policy
        
    Returns:
        list: List of invoice dictionaries, ordered as described
    """
    try:
        # Get all invoices for this policy, excluding refund and cancellation invoices
        all_invoices = (
            QueryBuilderService("crmf_invoices")
            .where("issued_policy_id", issued_policy_id)
            .whereNotIn("transaction_type_id", [4, 5])  # Exclude Refund (4) and Cancellation (5)
            .get()
        )
        
        if not all_invoices:
            return []
        
        # Separate addition invoices and premium invoices
        addition_invoices = [inv for inv in all_invoices if inv.get("transaction_type_id") == 2]
        premium_invoices = [inv for inv in all_invoices if inv.get("transaction_type_id") in [1, 3]]
        
        # Sort addition invoices by id desc (newest first)
        addition_invoices.sort(key=lambda x: x.get("id", 0), reverse=True)
        
        # Sort premium invoices by id asc (oldest first)
        premium_invoices.sort(key=lambda x: x.get("id", 0))
        
        # Combine: addition invoices first (newest to oldest), then premium invoices (oldest first)
        ordered_invoices = addition_invoices + premium_invoices
        
        print(f"DEBUG: Found {len(addition_invoices)} addition invoices and {len(premium_invoices)} premium invoices for issued_policy_id {issued_policy_id}")
        for inv in ordered_invoices:
            print(f"  - Invoice {inv.get('invoice_number')} (ID: {inv.get('id')}, Type: {inv.get('transaction_type_id')}, Outstanding: {inv.get('outstanding_amount')})")
        
        return ordered_invoices
        
    except Exception as e:
        print(f"Error getting invoices for policy: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def get_commission_records_for_invoice(invoice_id):
    """
    Get brokerage and agent commission records for an invoice.
    
    Args:
        invoice_id (int): ID of the invoice
        
    Returns:
        tuple: (brokerage_commission, agent_commissions_list) or (None, []) if not found
    """
    try:
        brokerage = (
            QueryBuilderService("crmf_brokerage_commission")
            .where("invoice_id", invoice_id)
            .first()
        )
        
        agent_commissions = []
        if brokerage:
            agent_commissions = (
                QueryBuilderService("crmf_agent_commission")
                .where("brokerage_commission_id", brokerage.get("id"))
                .get()
            )
        
        return brokerage, agent_commissions
        
    except Exception as e:
        print(f"Error getting commission records for invoice {invoice_id}: {str(e)}")
        return None, []

def calculate_commission_outstanding(brokerage_commission, agent_commissions):
    """
    Calculate outstanding amount for brokerage and agent commissions.
    Outstanding = revenue_recognized - revenue_realized - commission_deductible
    
    Args:
        brokerage_commission (dict): Brokerage commission record
        agent_commissions (list): List of agent commission records
        
    Returns:
        tuple: (brokerage_outstanding, agent_outstanding_dict) where agent_outstanding_dict maps agent_id to outstanding
    """
    try:
        brokerage_outstanding = Decimal("0.00")
        if brokerage_commission:
            revenue_recognized = safe_decimal(brokerage_commission.get("revenue_recognized"), "0.00")
            revenue_realized = safe_decimal(brokerage_commission.get("revenue_realized"), "0.00")
            commission_deductible = safe_decimal(brokerage_commission.get("commission_deductible"), "0.00")
            brokerage_outstanding = revenue_recognized - revenue_realized - commission_deductible
            # Outstanding can be negative for premium invoice, but we'll use it as is
        
        agent_outstanding_dict = {}
        for agent_comm in agent_commissions:
            agent_id = agent_comm.get("agent_id")
            if agent_id:
                revenue_recognized = safe_decimal(agent_comm.get("revenue_recognized"), "0.00")
                revenue_realized = safe_decimal(agent_comm.get("revenue_realized"), "0.00")
                commission_deductible = safe_decimal(agent_comm.get("commission_deductible"), "0.00")
                agent_outstanding = revenue_recognized - revenue_realized - commission_deductible
                agent_outstanding_dict[agent_id] = agent_outstanding
        
        return brokerage_outstanding, agent_outstanding_dict
        
    except Exception as e:
        print(f"Error calculating commission outstanding: {str(e)}")
        return Decimal("0.00"), {}

def find_original_new_business_commission(issued_policy_id):
    """
    Find the original commission invoice (New Business or Renewal) for a policy
    
    Args:
        issued_policy_id (int): ID of the issued policy
        
    Returns:
        tuple: (original_invoice, original_brokerage) or (None, None) if not found
    """
    try:
        # Find the original invoice - prioritize New Business (1), then Renewal (3)
        # These are the initial invoices where commission was calculated
        original_invoice = (
            QueryBuilderService("crmf_invoices")
            .where("issued_policy_id", issued_policy_id)
            .whereIn("transaction_type_id", [1, 3])  # New Business or Renewal
            .orderBy("transaction_type_id", "asc")  # New Business first, then Renewal
            .orderBy("id", "asc")  # Oldest first for same type
            .first()
        )
        
        if not original_invoice:
            return None, None
            
        # Find the original brokerage commission
        original_brokerage = (
            QueryBuilderService("crmf_brokerage_commission")
            .where("invoice_id", original_invoice["id"])
            .first()
        )
        
        if not original_brokerage:
            return None, None
            
        return original_invoice, original_brokerage
        
    except Exception as e:
        print(f"Error finding original commission: {str(e)}")
        return None, None

def calculate_commission_deduction(base_amount, commission_setup, calculation_mode=None, original_brokerage=None, original_agent_commissions=None):
    """
    Calculate commission deduction amounts
    
    Args:
        base_amount (Decimal): Base amount for deduction calculation
        commission_setup (dict): Commission setup configuration
        calculation_mode (str): "premium" or "paid"
        original_brokerage (dict, optional): Original brokerage commission record
        original_agent_commissions (list, optional): List of original agent commission records from database
        
    Returns:
        tuple: (brokerage_deduction, agent_commission_data) or (None, None) if error
    """
    try:
        calculation_mode = get_commission_calculation_mode(calculation_mode)
        commission_values = commission_setup.get("commission_values", {})
        
        # Ensure base amount is negative
        base_amount = -abs(base_amount)
        
        # Calculate brokerage commission deduction
        brokerage_data = commission_values.get("brokerage_revenue_percent", [{"value": "0", "type": "flat"}])[0]
        # Handle empty strings - convert to "0" before Decimal conversion
        raw_brokerage_value = brokerage_data.get("value", "0")
        if raw_brokerage_value == "" or raw_brokerage_value is None:
            raw_brokerage_value = "0"
        brokerage_percent = Decimal(str(raw_brokerage_value))
        brokerage_type = brokerage_data.get("type", "flat")
        print(f"DEBUG: Commission deduction calculation - brokerage_value: {brokerage_percent}, brokerage_type: {brokerage_type}, base_amount: {base_amount}")
        if brokerage_type in ["flat", "fixed"]:
            # For fixed/flat values, use the value directly regardless of base_amount
            brokerage_deduction = brokerage_percent
            print(f"DEBUG: Using fixed/flat value: {brokerage_deduction}")
        else:  # percentage
            # For percentage, calculate based on base_amount
            brokerage_deduction = (base_amount * brokerage_percent / Decimal("100")).quantize(Decimal(".01"))
            print(f"DEBUG: Calculated percentage deduction: {brokerage_deduction} ({brokerage_percent}% of {base_amount})")
            
        # Calculate agent commission deductions
        agent_commission_data = []
        agent_data_list = commission_values.get("agent_commission_percent", [])
        revised_data_list = commission_values.get("revised_commission_percent", [])
        
        # Get original brokerage commission amount from database if available, otherwise calculate
        if original_brokerage:
            brokerage_amount = safe_decimal(original_brokerage.get("revenue_recognized"), default="0.00")
        else:
            # Calculate original brokerage amount from deduction
            original_base = abs(base_amount)
            if brokerage_type in ["flat", "fixed"]:
                brokerage_amount = abs(brokerage_percent)
            else:
                # Calculate original brokerage amount from deduction
                brokerage_amount = abs(brokerage_deduction / (brokerage_percent / Decimal("100")) if brokerage_percent > 0 else original_base)
        
        # Create a map of agent_id to agent commission record for quick lookup
        agent_comm_map = {}
        if original_agent_commissions:
            print(f"DEBUG: Processing {len(original_agent_commissions)} agent commission records for revised_amount check")
            for agent_comm in original_agent_commissions:
                agent_id = agent_comm.get("agent_id")
                if agent_id:
                    revised_amount_check = safe_decimal(agent_comm.get("revised_amount"), default="0.00")
                    print(f"DEBUG: Agent {agent_id} - revised_amount: {revised_amount_check}, revised_amount_percent: {agent_comm.get('revised_amount_percent')}, revised_amount_type: {agent_comm.get('revised_amount_type')}")
                    agent_comm_map[agent_id] = agent_comm
            print(f"DEBUG: Created agent_comm_map with {len(agent_comm_map)} entries: {list(agent_comm_map.keys())}")
        else:
            print(f"DEBUG: No original_agent_commissions provided for revised_amount check")
        
        # First, check all agents in agent_comm_map for revised_amount
        # This ensures we check revised_amount even if user_id is None in agent_data_list
        agents_with_revised_amount = {}
        for agent_id, agent_comm_record in agent_comm_map.items():
            revised_amount_db = safe_decimal(agent_comm_record.get("revised_amount"), default="0.00")
            if revised_amount_db > 0:
                agents_with_revised_amount[agent_id] = {
                    "revised_amount": revised_amount_db,
                    "revised_amount_percent": safe_decimal(agent_comm_record.get("revised_amount_percent"), default="0.00"),
                    "revised_amount_type": agent_comm_record.get("revised_amount_type", "percentage"),
                    "record": agent_comm_record
                }
                print(f"DEBUG: Found agent {agent_id} with revised_amount={revised_amount_db} in database")
        
        for agent_data in agent_data_list:
            # Handle empty strings - convert to "0" before Decimal conversion
            raw_agent_value = agent_data.get("value", "0")
            if raw_agent_value == "" or raw_agent_value is None:
                raw_agent_value = "0"
            value = Decimal(str(raw_agent_value))
            type_ = agent_data.get("type", "flat")
            user_id = agent_data.get("user_id")

            agent_deduction = None
            
            # PRIORITY 1: Check if agent commission record in database has revised_amount > 0
            # If agent can receive commission (has revised_amount), calculate deductible based on revised_amount
            # If user_id is None, we'll check all agents in agent_comm_map later
            print(f"DEBUG: Checking agent {user_id} for revised_amount - in map: {user_id in agent_comm_map if user_id else False}, has revised: {user_id in agents_with_revised_amount if user_id else False}")
            if user_id and user_id in agents_with_revised_amount:
                revised_info = agents_with_revised_amount[user_id]
                revised_amount_db = revised_info["revised_amount"]
                revised_amount_percent_db = revised_info["revised_amount_percent"]
                revised_amount_type_db = revised_info["revised_amount_type"]
                agent_comm_record = revised_info["record"]
                
                print(f"DEBUG: Agent {user_id} - revised_amount_db: {revised_amount_db}, revised_amount_percent_db: {revised_amount_percent_db}, revised_amount_type_db: {revised_amount_type_db}")
                
                # We already know revised_amount_db > 0 from the check above
                if True:  # revised_amount_db > 0 is already checked
                    # Agent has revised commission in database - use it for deductible calculation
                    print(f"DEBUG: Agent {user_id} has revised_amount={revised_amount_db} in database, using it for deductible calculation")
                    if revised_amount_type_db in ["flat", "fixed"]:
                        # For fixed/flat revised amounts, the revised_amount is the total commission the agent should receive
                        # Calculate deductible proportionally: revised_amount * (brokerage_deduction / brokerage_amount)
                        # This ensures the deductible is proportional to the cancellation/refund amount
                        if original_brokerage and brokerage_amount > 0:
                            # Calculate the ratio of brokerage deduction to original brokerage amount
                            # This ratio represents the proportion of cancellation/refund
                            deduction_ratio = abs(brokerage_deduction) / brokerage_amount
                            agent_deduction = -(revised_amount_db * deduction_ratio).quantize(Decimal(".01"))
                            print(f"DEBUG: Fixed/flat revised_amount - calculated deductible: {agent_deduction} (revised_amount={revised_amount_db} * ratio={deduction_ratio})")
                        else:
                            # Fallback: calculate based on brokerage_deduction directly
                            # If we can't get the ratio, use a proportional calculation based on brokerage_deduction
                            brokerage_deduction_abs = abs(brokerage_deduction)
                            # Estimate: if brokerage is typically 10%, then agent commission is typically 10% of brokerage
                            # So agent deductible ≈ brokerage_deductible * (revised_amount / brokerage_amount)
                            # But without brokerage_amount, we'll use a simpler approach
                            agent_deduction = -abs(revised_amount_db)  # This will be adjusted by ratio later
                            print(f"DEBUG: Fixed/flat revised_amount - using full revised_amount (will be adjusted by ratio): {agent_deduction}")
                    else:
                        # Revised commission is percentage - calculate based on brokerage_deduction
                        # IMPORTANT: Agent commission deductible should be calculated as a percentage
                        # of the brokerage commission deductible, NOT the full brokerage_amount.
                        # Example: If brokerage deductible is 9,000 and agent revised commission is 20%,
                        # then agent deductible = 20% of 9,000 = 1,800
                        if revised_amount_percent_db > 0:
                            brokerage_deduction_abs = abs(brokerage_deduction)
                            agent_deduction = -(brokerage_deduction_abs * revised_amount_percent_db / Decimal("100")).quantize(Decimal(".01"))
                            # Ensure agent deductible never exceeds brokerage deductible
                            if abs(agent_deduction) > brokerage_deduction_abs:
                                agent_deduction = -brokerage_deduction_abs
                            print(f"DEBUG: Percentage revised_amount - calculated deductible: {agent_deduction} (brokerage_deduction={brokerage_deduction_abs} * {revised_amount_percent_db}%)")
                        else:
                            # If revised_amount_percent is 0 but revised_amount > 0, calculate proportionally
                            # This means revised_amount was set directly, so calculate based on brokerage_deduction ratio
                            if original_brokerage and brokerage_amount > 0:
                                deduction_ratio = abs(brokerage_deduction) / brokerage_amount
                                agent_deduction = -(revised_amount_db * deduction_ratio).quantize(Decimal(".01"))
                                print(f"DEBUG: Revised_amount without percent - calculated deductible: {agent_deduction} (revised_amount={revised_amount_db} * ratio={deduction_ratio})")
                            else:
                                agent_deduction = -abs(revised_amount_db)
                                print(f"DEBUG: Revised_amount without percent - using full revised_amount: {agent_deduction}")
                    
                    if agent_deduction >= 0:
                        agent_deduction = None  # fallback to normal logic if not negative
                    else:
                        print(f"DEBUG: Final agent deduction using revised_amount from database: {agent_deduction}")
            else:
                if user_id:
                    if user_id in agent_comm_map:
                        print(f"DEBUG: Agent {user_id} found in agent_comm_map but revised_amount <= 0, will use commission setup or regular calculation")
                    else:
                        print(f"DEBUG: Agent {user_id} not found in agent_comm_map, will use commission setup or regular calculation")
                else:
                    print(f"DEBUG: user_id is None in agent_data, will resolve later and check revised_amount then")
            
            # PRIORITY 2: Check commission setup for revised commission (if not found in database)
            if agent_deduction is None:
                revised_entry = next((r for r in revised_data_list if r.get("user_id") == user_id), None)
                if revised_entry:
                    # Handle empty strings - convert to "0" before Decimal conversion
                    raw_revised_value = revised_entry.get("value", "0")
                    if raw_revised_value == "" or raw_revised_value is None:
                        raw_revised_value = "0"
                    revised_value = Decimal(str(raw_revised_value))
                    revised_type = revised_entry.get("type", "flat")
                    if revised_type in ["flat", "fixed"]:
                        agent_deduction = -abs(revised_value)  # Make negative for deduction
                    else:
                        # Revised commission should be calculated based on brokerage commission amount
                        # Use brokerage_amount (positive) for calculation, then make negative
                        agent_deduction = -(brokerage_amount * revised_value / Decimal("100")).quantize(Decimal(".01"))
                    if agent_deduction >= 0:
                        agent_deduction = None  # fallback to normal logic if not negative
            
            # PRIORITY 3: Use regular agent commission (fallback)
            if agent_deduction is None:
                if type_  in ["flat", "fixed"]:
                    agent_deduction = -abs(value)  # Make negative for deduction
                else:  # percentage
                    # IMPORTANT: Agent commission deductible should be calculated as a percentage
                    # of the brokerage commission deductible, NOT the base amount.
                    # Example: If brokerage deductible is 2,000 and agent commission is 10%,
                    # then agent deductible = 10% of 2,000 = 200
                    brokerage_deduction_abs = abs(brokerage_deduction)
                    agent_deduction = -(brokerage_deduction_abs * value / Decimal("100")).quantize(Decimal(".01"))
            
            agent_commission_data.append({
                "user_id": user_id,
                "deduction": agent_deduction
            })
        
        return brokerage_deduction, agent_commission_data
        
    except Exception as e:
        print(f"Error calculating commission deduction: {str(e)}")
        return None, None

def apply_commission_deduction(brokerage_id, brokerage_deduction, agent_deductions, refund_invoice_id=None):
    """
    Apply commission deductions to existing commission records
    
    Args:
        brokerage_id (int): ID of the original brokerage commission
        brokerage_deduction (Decimal): Amount to deduct from brokerage commission
        agent_deductions (list): List of agent deduction data
        refund_invoice_id (int, optional): ID of the refund/cancellation invoice causing this deduction
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the original invoice for this brokerage commission
        brokerage = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_id).first()
        if not brokerage:
            return False
        
        original_invoice_id = brokerage.get("invoice_id")
        original_invoice = QueryBuilderService("crmf_invoices").where("id", original_invoice_id).first() if original_invoice_id else None
        original_invoice_number = original_invoice.get("invoice_number") if original_invoice else f"ID:{original_invoice_id}"
        
        refund_invoice = QueryBuilderService("crmf_invoices").where("id", refund_invoice_id).first() if refund_invoice_id else None
        refund_invoice_number = refund_invoice.get("invoice_number") if refund_invoice else f"ID:{refund_invoice_id}" if refund_invoice_id else "N/A"
        
        print("=" * 80)
        print("COMMISSION DEDUCTIBLE CALCULATION - STORING DEDUCTIBLE AMOUNTS")
        print("=" * 80)
        print(f"Refund/Cancellation Invoice: {refund_invoice_number} (ID: {refund_invoice_id})")
        print(f"Original Premium Invoice: {original_invoice_number} (ID: {original_invoice_id})")
        print(f"Brokerage Commission ID: {brokerage_id}")
        print("-" * 80)
        
        # CRITICAL VERIFICATION: Ensure we're updating the commission for the PREMIUM invoice, not the refund invoice
        if original_invoice_id == refund_invoice_id:
            print(f"✗ ERROR: Original invoice ID ({original_invoice_id}) matches refund invoice ID ({refund_invoice_id})!")
            print(f"✗ ERROR: This should never happen. Deductible should be stored in PREMIUM invoice commission, not refund invoice.")
            return False
        
        # Verify the brokerage commission belongs to the premium invoice, not the refund invoice
        brokerage_invoice_id = brokerage.get("invoice_id")
        if brokerage_invoice_id != original_invoice_id:
            print(f"✗ ERROR: Brokerage commission invoice_id ({brokerage_invoice_id}) does not match original premium invoice_id ({original_invoice_id})!")
            print(f"✗ ERROR: Cannot update deductible - commission record belongs to wrong invoice.")
            return False
        
        if brokerage_invoice_id == refund_invoice_id:
            print(f"✗ ERROR: Brokerage commission belongs to refund invoice ({refund_invoice_id}) instead of premium invoice ({original_invoice_id})!")
            print(f"✗ ERROR: Deductible should be stored in PREMIUM invoice commission, not refund invoice commission.")
            return False
        
        print(f"✓ VERIFIED: Brokerage commission belongs to premium invoice {original_invoice_number} (ID: {original_invoice_id})")
        print(f"✓ VERIFIED: Deductible will be stored in premium invoice commission, NOT in refund invoice commission")
        print("-" * 80)
            
        current_recognized = safe_decimal(brokerage.get("revenue_recognized"), default="0.00")
        current_deductible = safe_decimal(brokerage.get("commission_deductible"), default="0.00")
        new_recognized = current_recognized + brokerage_deduction
        new_deductible = current_deductible + abs(brokerage_deduction)
        
        print(f"BROKERAGE COMMISSION UPDATE (Premium Invoice {original_invoice_number}):")
        print(f"  Commission Record ID: {brokerage_id}")
        print(f"  Current revenue_recognized: {current_recognized}")
        print(f"  Current commission_deductible: {current_deductible}")
        print(f"  Deduction amount: {brokerage_deduction}")
        print(f"  New revenue_recognized: {new_recognized}")
        print(f"  New commission_deductible: {new_deductible} (stored in premium invoice {original_invoice_number} commission)")
        print("-" * 80)
        
        try:
            result = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_id).update({
                "revenue_recognized": str(new_recognized),
                "commission_deductible": str(new_deductible)
            })
            
            if not result:
                print("  ✗ ERROR: Brokerage commission update failed - no data returned")
                return False
            else:
                # Verify the update was successful and belongs to the correct invoice
                updated_brokerage = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_id).first()
                if updated_brokerage:
                    updated_deductible = safe_decimal(updated_brokerage.get("commission_deductible"), default="0.00")
                    updated_invoice_id = updated_brokerage.get("invoice_id")
                    
                    # Final verification that the commission still belongs to the premium invoice
                    if updated_invoice_id != original_invoice_id:
                        print(f"  ✗ ERROR: After update, commission invoice_id changed to {updated_invoice_id} (expected {original_invoice_id})!")
                        return False
                    
                    print(f"  ✓ Verified: Brokerage commission deductible stored as: {updated_deductible}")
                    print(f"  ✓ Verified: Commission still belongs to premium invoice {original_invoice_number} (ID: {original_invoice_id})")
                else:
                    print(f"  ✗ WARNING: Could not verify brokerage commission update")
        except Exception as e:
            print(f"ERROR: Brokerage commission update failed with exception: {str(e)}")
            return False
            
        # Update agent commissions
        agent_update_success = True
        for agent_data in agent_deductions:
            user_id = agent_data.get("user_id")
            deduction = agent_data.get("deduction")
            
            # Check if user_id exists and deduction is not None (deduction can be 0, so we check for None)
            if not user_id or deduction is None:
                print(f"WARNING: Skipping agent deduction - user_id: {user_id}, deduction: {deduction}")
                continue
                
            agent_comm = (
                QueryBuilderService("crmf_agent_commission")
                .where("brokerage_commission_id", brokerage_id)
                .where("agent_id", user_id)
                .first()
            )
            
            if not agent_comm:
                print(f"WARNING: Agent commission not found for brokerage_id: {brokerage_id}, agent_id: {user_id}")
                agent_update_success = False
                continue
                
            current_agent_recognized = safe_decimal(agent_comm.get("revenue_recognized"), default="0.00")
            current_agent_deductible = safe_decimal(agent_comm.get("commission_deductible"), default="0.00")
            new_agent_recognized = current_agent_recognized + deduction
            new_agent_deductible = current_agent_deductible + abs(deduction)
            
            print(f"AGENT COMMISSION UPDATE (Agent ID: {user_id}):")
            print(f"  Agent Commission ID: {agent_comm['id']}")
            print(f"  Current revenue_recognized: {current_agent_recognized}")
            print(f"  Current commission_deductible: {current_agent_deductible}")
            print(f"  Deduction amount: {deduction}")
            print(f"  New revenue_recognized: {new_agent_recognized}")
            print(f"  New commission_deductible: {new_agent_deductible} (stored in premium invoice agent commission)")
            print("-" * 80)
            
            try:
                agent_result = QueryBuilderService("crmf_agent_commission").where("id", agent_comm["id"]).update({
                    "revenue_recognized": str(new_agent_recognized),
                    "commission_deductible": str(new_agent_deductible)
                })
                
                if not agent_result:
                    print(f"ERROR: Agent commission update failed for agent {user_id} - no data returned")
                    agent_update_success = False
                else:
                    # Verify the update was successful by reading back the record
                    updated_agent_comm = QueryBuilderService("crmf_agent_commission").where("id", agent_comm["id"]).first()
                    if updated_agent_comm:
                        updated_deductible = safe_decimal(updated_agent_comm.get("commission_deductible"), default="0.00")
                        print(f"  ✓ Verified: Agent commission deductible stored as: {updated_deductible}")
                        if updated_deductible != new_agent_deductible:
                            print(f"  ✗ ERROR: Agent commission deductible mismatch! Expected: {new_agent_deductible}, Got: {updated_deductible}")
                            agent_update_success = False
            except Exception as e:
                print(f"ERROR: Agent commission update failed for agent {user_id} with exception: {str(e)}")
                import traceback
                traceback.print_exc()
                agent_update_success = False
            
        # Return True if brokerage update succeeded (brokerage update already returned False if it failed)
        # Log agent update status separately
        if not agent_update_success:
            print(f"WARNING: Some agent commission updates failed, but brokerage commission was updated successfully")
        
        # Final summary
        print("=" * 80)
        print(f"SUMMARY: Deductible amounts stored in premium invoice commission:")
        print(f"  - Refund/Cancellation Invoice: {refund_invoice_number} (ID: {refund_invoice_id})")
        print(f"  - Premium Invoice (where deductible is stored): {original_invoice_number} (ID: {original_invoice_id})")
        print(f"  - Brokerage Commission ID: {brokerage_id}")
        print(f"  - Brokerage Commission Deductible: {new_deductible}")
        print(f"  - Agent Commission Updates: {'Success' if agent_update_success else 'Some failures occurred'}")
        print(f"  ✓ IMPORTANT: Deductible is stored in PREMIUM invoice {original_invoice_number} commission, NOT in refund invoice {refund_invoice_number}")
        print("=" * 80)
        
        return True
        
    except Exception as e:
        print(f"Error applying commission deduction: {str(e)}")
        return False


def store_commission_deductible_only(brokerage_id, brokerage_deduction, agent_deductions, refund_invoice_id=None):
    """
    Store commission deductible amounts across invoices (addition and premium) WITHOUT deducting from revenue_recognized.
    This is used when endorsement is created to store the calculated deductible amounts.
    
    DISTRIBUTION LOGIC:
    Deductible is distributed across invoices in the following order:
    1. Newest addition invoice first (transaction_type_id = 2)
    2. Older addition invoices (newest to oldest)
    3. Premium invoice last (transaction_type_id = 1 or 3) - can have negative outstanding
    
    For each invoice:
    - If outstanding > 0, apply deductible up to the outstanding amount
    - If outstanding becomes 0, move remaining deductible to next invoice
    - Premium invoice can have negative outstanding
    
    IMPORTANT: Outstanding Amount Calculation
    After storing deductible amounts, the outstanding amount is calculated as:
        outstanding = revenue_recognized - revenue_realized - commission_deductible
    For addition invoices, if the result is negative, it is set to 0.
    For premium invoice, outstanding can be negative.
    
    Args:
        brokerage_id (int): ID of the original brokerage commission (from premium invoice)
        brokerage_deduction (Decimal): Amount to store as deductible (will be stored as absolute value)
        agent_deductions (list): List of agent deduction data
        refund_invoice_id (int, optional): ID of the refund/cancellation invoice causing this deduction
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Get the original invoice for this brokerage commission
        brokerage = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_id).first()
        if not brokerage:
            return False
        
        original_invoice_id = brokerage.get("invoice_id")
        original_invoice = QueryBuilderService("crmf_invoices").where("id", original_invoice_id).first() if original_invoice_id else None
        if not original_invoice:
            print(f"ERROR: Original invoice {original_invoice_id} not found")
            return False
        
        issued_policy_id = original_invoice.get("issued_policy_id")
        if not issued_policy_id:
            print(f"ERROR: No issued_policy_id found for invoice {original_invoice_id}")
            return False
        
        original_invoice_number = original_invoice.get("invoice_number", f"ID:{original_invoice_id}")
        
        refund_invoice = QueryBuilderService("crmf_invoices").where("id", refund_invoice_id).first() if refund_invoice_id else None
        refund_invoice_number = refund_invoice.get("invoice_number") if refund_invoice else f"ID:{refund_invoice_id}" if refund_invoice_id else "N/A"
        
        print("=" * 80)
        print("COMMISSION DEDUCTIBLE STORAGE - DISTRIBUTING ACROSS INVOICES (NO DEDUCTION FROM REVENUE)")
        print("=" * 80)
        print(f"Refund/Cancellation Invoice: {refund_invoice_number} (ID: {refund_invoice_id})")
        print(f"Issued Policy ID: {issued_policy_id}")
        print(f"Total Brokerage Deduction: {abs(brokerage_deduction)}")
        print("-" * 80)
        
        # CRITICAL VERIFICATION: Ensure we're not updating the refund invoice
        if original_invoice_id == refund_invoice_id:
            print(f"✗ ERROR: Original invoice ID ({original_invoice_id}) matches refund invoice ID ({refund_invoice_id})!")
            return False
        
        # Get all invoices for this policy, ordered correctly
        ordered_invoices = get_invoices_for_policy_ordered(issued_policy_id)
        if not ordered_invoices:
            print(f"WARNING: No invoices found for issued_policy_id {issued_policy_id}, falling back to original invoice only")
            ordered_invoices = [original_invoice]
        
        # Prepare deductible amounts to distribute
        remaining_brokerage_deductible = abs(safe_decimal(brokerage_deduction, "0.00"))
        remaining_agent_deductibles = {}
        for agent_data in agent_deductions:
            user_id = agent_data.get("user_id")
            deduction = agent_data.get("deduction")
            if user_id and deduction is not None:
                remaining_agent_deductibles[user_id] = abs(safe_decimal(deduction, "0.00"))
        
        print(f"DEBUG: Starting deductible distribution")
        print(f"  Remaining brokerage deductible: {remaining_brokerage_deductible}")
        print(f"  Remaining agent deductibles: {remaining_agent_deductibles}")
        print("-" * 80)
        
        # Distribute deductible across invoices
        brokerage_update_success = True
        agent_update_success = True
        
        for invoice in ordered_invoices:
            invoice_id = invoice.get("id")
            invoice_number = invoice.get("invoice_number", f"ID:{invoice_id}")
            transaction_type_id = invoice.get("transaction_type_id")
            is_premium = transaction_type_id in [1, 3]  # New Business or Renewal
            
            print(f"\nProcessing Invoice: {invoice_number} (ID: {invoice_id}, Type: {transaction_type_id})")
            
            # Get commission records for this invoice
            invoice_brokerage, invoice_agent_commissions = get_commission_records_for_invoice(invoice_id)
            
            if not invoice_brokerage:
                print(f"  ⚠ No commission records found for invoice {invoice_number}, skipping")
                continue
            
            # Calculate current outstanding for this invoice
            brokerage_outstanding, agent_outstanding_dict = calculate_commission_outstanding(
                invoice_brokerage, invoice_agent_commissions
            )
            
            # Get current values for calculation
            current_brokerage_deductible = safe_decimal(invoice_brokerage.get("commission_deductible"), "0.00")
            brokerage_revenue_recognized = safe_decimal(invoice_brokerage.get("revenue_recognized"), "0.00")
            brokerage_revenue_realized = safe_decimal(invoice_brokerage.get("revenue_realized"), "0.00")
            
            print(f"  Current brokerage outstanding: {brokerage_outstanding}")
            print(f"  Revenue recognized: {brokerage_revenue_recognized}, Revenue realized: {brokerage_revenue_realized}")
            print(f"  Current deductible: {current_brokerage_deductible}")
            print(f"  Current agent outstanding: {agent_outstanding_dict}")
            
            # Calculate how much deductible to apply to this invoice
            if is_premium:
                # Premium invoice: apply all remaining deductible (can go negative)
                brokerage_deductible_to_apply = remaining_brokerage_deductible
            else:
                # Addition invoice: calculate deductible needed to equalize outstanding to 0
                # Outstanding = revenue_recognized - revenue_realized - commission_deductible
                # We want: revenue_recognized - revenue_realized - new_deductible = 0
                # So: new_deductible = revenue_recognized - revenue_realized
                # Deductible to add = new_deductible - current_deductible
                new_deductible_needed = brokerage_revenue_recognized - brokerage_revenue_realized
                deductible_to_equalize = new_deductible_needed - current_brokerage_deductible
                
                # Only process if outstanding > 0 and we need to add deductible
                if brokerage_outstanding > 0 and deductible_to_equalize > 0:
                    # Apply the amount needed to equalize, but not more than remaining deductible
                    brokerage_deductible_to_apply = min(remaining_brokerage_deductible, deductible_to_equalize)
                    print(f"  Deductible needed to equalize: {deductible_to_equalize}, Applying: {brokerage_deductible_to_apply}")
                else:
                    # Outstanding is already 0 or negative, or no deductible needed
                    if brokerage_outstanding <= 0:
                        print(f"  ⚠ Addition invoice {invoice_number} outstanding is already <= 0, moving to next invoice")
                    else:
                        print(f"  ⚠ Addition invoice {invoice_number} no deductible needed (deductible_to_equalize: {deductible_to_equalize}), moving to next invoice")
                    continue
            
            if brokerage_deductible_to_apply > 0:
                new_brokerage_deductible = current_brokerage_deductible + brokerage_deductible_to_apply
                
                print(f"  Applying brokerage deductible: {brokerage_deductible_to_apply}")
                print(f"    Current deductible: {current_brokerage_deductible}")
                print(f"    New deductible: {new_brokerage_deductible}")
                print(f"    Expected outstanding after: {brokerage_revenue_recognized - brokerage_revenue_realized - new_brokerage_deductible}")
                
                try:
                    result = QueryBuilderService("crmf_brokerage_commission").where("id", invoice_brokerage.get("id")).update({
                        "commission_deductible": str(new_brokerage_deductible)
                    })
                    
                    if not result:
                        print(f"  ✗ ERROR: Failed to update brokerage commission for invoice {invoice_number}")
                        brokerage_update_success = False
                    else:
                        remaining_brokerage_deductible -= brokerage_deductible_to_apply
                        # Recalculate outstanding after applying deductible
                        new_outstanding = brokerage_revenue_recognized - brokerage_revenue_realized - new_brokerage_deductible
                        print(f"  ✓ Brokerage deductible updated. Remaining: {remaining_brokerage_deductible}")
                        print(f"  ✓ Outstanding after deductible: {new_outstanding}")
                        
                        # For addition invoices, if outstanding is now 0 or negative, we've equalized
                        # Continue to next invoice if we've equalized OR if we've run out of deductible
                        if not is_premium and new_outstanding <= 0:
                            print(f"  ✓ Addition invoice {invoice_number} outstanding equalized to 0, moving to next invoice")
                            # Break out of agent commission loop and continue to next invoice
                            # We'll check this after agent commissions are updated
                except Exception as e:
                    print(f"  ✗ ERROR: Exception updating brokerage commission: {str(e)}")
                    brokerage_update_success = False
            
            # Update agent commissions for this invoice
            for agent_comm in invoice_agent_commissions:
                agent_id = agent_comm.get("agent_id")
                if not agent_id or agent_id not in remaining_agent_deductibles:
                    continue
                
                agent_outstanding = agent_outstanding_dict.get(agent_id, Decimal("0.00"))
                
                # Get current values for agent commission
                current_agent_deductible = safe_decimal(agent_comm.get("commission_deductible"), "0.00")
                agent_revenue_recognized = safe_decimal(agent_comm.get("revenue_recognized"), "0.00")
                agent_revenue_realized = safe_decimal(agent_comm.get("revenue_realized"), "0.00")
                
                # Calculate how much deductible to apply to this agent
                if is_premium:
                    # Premium invoice: apply all remaining deductible
                    agent_deductible_to_apply = remaining_agent_deductibles.get(agent_id, Decimal("0.00"))
                else:
                    # Addition invoice: calculate deductible needed to equalize outstanding to 0
                    # Outstanding = revenue_recognized - revenue_realized - commission_deductible
                    # We want: revenue_recognized - revenue_realized - new_deductible = 0
                    # So: new_deductible = revenue_recognized - revenue_realized
                    # Deductible to add = new_deductible - current_deductible
                    new_agent_deductible_needed = agent_revenue_recognized - agent_revenue_realized
                    agent_deductible_to_equalize = new_agent_deductible_needed - current_agent_deductible
                    
                    # Only apply if we need to add deductible and we have remaining deductible
                    if agent_outstanding > 0 and agent_deductible_to_equalize > 0:
                        # Apply the amount needed to equalize, but not more than remaining deductible
                        agent_deductible_to_apply = min(
                            remaining_agent_deductibles.get(agent_id, Decimal("0.00")),
                            agent_deductible_to_equalize
                        )
                    else:
                        # Outstanding is already 0 or negative, or no deductible needed
                        continue
                
                if agent_deductible_to_apply > 0:
                    new_agent_deductible = current_agent_deductible + agent_deductible_to_apply
                    
                    print(f"  Applying agent {agent_id} deductible: {agent_deductible_to_apply}")
                    print(f"    Current deductible: {current_agent_deductible}")
                    print(f"    Revenue recognized: {agent_revenue_recognized}, Revenue realized: {agent_revenue_realized}")
                    print(f"    New deductible: {new_agent_deductible}")
                    print(f"    Expected outstanding after: {agent_revenue_recognized - agent_revenue_realized - new_agent_deductible}")
                    
                    try:
                        agent_result = QueryBuilderService("crmf_agent_commission").where("id", agent_comm.get("id")).update({
                            "commission_deductible": str(new_agent_deductible)
                        })
                        
                        if not agent_result:
                            print(f"  ✗ ERROR: Failed to update agent {agent_id} commission for invoice {invoice_number}")
                            agent_update_success = False
                        else:
                            remaining_agent_deductibles[agent_id] = remaining_agent_deductibles.get(agent_id, Decimal("0.00")) - agent_deductible_to_apply
                            # Recalculate outstanding after applying deductible
                            new_agent_outstanding = agent_revenue_recognized - agent_revenue_realized - new_agent_deductible
                            print(f"  ✓ Agent {agent_id} deductible updated. Remaining: {remaining_agent_deductibles.get(agent_id, Decimal('0.00'))}")
                            print(f"  ✓ Agent {agent_id} outstanding after deductible: {new_agent_outstanding}")
                    except Exception as e:
                        print(f"  ✗ ERROR: Exception updating agent {agent_id} commission: {str(e)}")
                        agent_update_success = False
            
            # Check if we should move to next invoice
            if is_premium:
                # Premium invoice: we've applied all remaining deductible
                print(f"  ✓ Premium invoice processed, all remaining deductible applied")
                break
            else:
                # Addition invoice: check if outstanding is now 0 or negative (equalized)
                # Recalculate outstanding after all updates
                updated_brokerage = QueryBuilderService("crmf_brokerage_commission").where("id", invoice_brokerage.get("id")).first()
                if updated_brokerage:
                    final_brokerage_outstanding = (
                        safe_decimal(updated_brokerage.get("revenue_recognized"), "0.00") -
                        safe_decimal(updated_brokerage.get("revenue_realized"), "0.00") -
                        safe_decimal(updated_brokerage.get("commission_deductible"), "0.00")
                    )
                    if final_brokerage_outstanding <= 0:
                        print(f"  ✓ Addition invoice {invoice_number} outstanding equalized to {final_brokerage_outstanding}, moving to next invoice")
                        # Continue to next invoice in the loop
                    elif remaining_brokerage_deductible <= 0:
                        print(f"  ⚠ No more deductible remaining ({remaining_brokerage_deductible}), moving to next invoice")
                        # Continue to next invoice even though not fully equalized
                    else:
                        print(f"  ⚠ Addition invoice {invoice_number} outstanding not fully equalized ({final_brokerage_outstanding}), but continuing to next invoice")
                        # Continue to next invoice
        
        # Final summary
        print("=" * 80)
        print(f"SUMMARY: Deductible distribution completed")
        print(f"  - Refund/Cancellation Invoice: {refund_invoice_number} (ID: {refund_invoice_id})")
        print(f"  - Issued Policy ID: {issued_policy_id}")
        print(f"  - Brokerage Update: {'Success' if brokerage_update_success else 'Failed'}")
        print(f"  - Agent Update: {'Success' if agent_update_success else 'Failed'}")
        print(f"  - Remaining Brokerage Deductible: {remaining_brokerage_deductible}")
        print(f"  - Remaining Agent Deductibles: {remaining_agent_deductibles}")
        print(f"  ✓ IMPORTANT: Deductible distributed across invoices based on outstanding amounts")
        print(f"  ✓ IMPORTANT: revenue_recognized was NOT modified - only commission_deductible was updated")
        print("=" * 80)
        
        return brokerage_update_success and agent_update_success
        
    except Exception as e:
        print(f"Error storing commission deductible: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def handle_commission_deduction(invoice_id, transaction_type_id, product_id, insurer_id, sales_agent_id,
                              invoice_amount, paid_amount, calculation_mode=None, user=None):
    """
    Main function to handle commission deductions for refunds and cancellations
    
    Args:
        invoice_id (int): ID of the invoice
        transaction_type_id (int): ID of the transaction type
        product_id (int): ID of the product
        insurer_id (int): ID of the insurer
        sales_agent_id (int): ID of the sales agent
        invoice_amount (Decimal): Total invoice amount
        paid_amount (Decimal): Amount paid so far
        calculation_mode (str): "premium" or "paid"
        user (User, optional): User creating the commission
        
    Returns:
        tuple: (brokerage_commission_id, None) or (None, None) if error
    """
    try:
        calculation_mode = get_commission_calculation_mode(calculation_mode)
        
        # Normalize invoice_id to ensure it's an integer
        invoice_id_value = None
        if isinstance(invoice_id, dict):
            invoice_id_value = invoice_id.get('id')
        else:
            invoice_id_value = invoice_id
        
        if not invoice_id_value:
            print(f"ERROR: Invalid invoice_id: {invoice_id}")
            return None, None
        
        print(f"DEBUG: Processing commission deduction for invoice_id: {invoice_id_value}")
        # Get the original policy ID from the invoice
        invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id_value).first()
        print(f"DEBUG: Invoice retrieved: {invoice is not None}")
        
        if not invoice:
            return None, None

        issued_policy_id = invoice.get("issued_policy_id")
        if not issued_policy_id:
            return None, None
        print("original_invoice",issued_policy_id)  
            
        # Find original commission (New Business or Renewal invoice)
        original_invoice, original_brokerage = find_original_new_business_commission(issued_policy_id)
        if not original_invoice or not original_brokerage:
            return None, None
        print("original_invoice",original_invoice)
        
        # Get original agent commission records to check for revised_amount
        original_agent_commissions = []
        if original_brokerage and original_brokerage.get("id"):
            original_agent_commissions = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", original_brokerage["id"]).get()
            print(f"DEBUG: Found {len(original_agent_commissions)} original agent commission records")
        
        # Get the transaction type from the original invoice to use the correct commission setup
        original_transaction_type_id = original_invoice.get("transaction_type_id")
        # Use New Business (1) setup for New Business invoices, Renewal (3) setup for Renewal invoices
        commission_setup_transaction_type = original_transaction_type_id if original_transaction_type_id in [1, 3] else 1
        
        # Use product_id and insurer_id from the original invoice (not the refund/cancellation invoice)
        # This ensures we get the correct commission setup that was used for the original policy
        original_product_id = original_invoice.get("product_id")
        original_insurer_id = original_invoice.get("insurer_id")
        
        # Get product_group_id from policy base for commission setup fallback
        original_product_group_id = None
        if issued_policy_id:
            policy_base = QueryBuilderService("crmp_issued_policies").select("policy_base_id").where("id", issued_policy_id).first()
            if policy_base and policy_base.get("policy_base_id"):
                policy_base_data = QueryBuilderService("crmp_policy_base").select("product_group_id").where("id", policy_base.get("policy_base_id")).first()
                if policy_base_data:
                    original_product_group_id = policy_base_data.get("product_group_id")
        
        print(f"DEBUG: Using original invoice product_id: {original_product_id}, insurer_id: {original_insurer_id}, transaction_type: {commission_setup_transaction_type}, product_group_id: {original_product_group_id}")
        
        # Get commission setup for calculation based on original invoice type
        # Pass product_group_id for fallback lookup if product-level setup not found
        commission_setup = get_commission_setup_service(original_product_id, original_insurer_id, commission_setup_transaction_type, original_product_group_id)
        print(f"DEBUG: Commission setup retrieved - ID: {commission_setup.get('id') if isinstance(commission_setup, dict) else 'N/A'}")
        if isinstance(commission_setup, dict) and commission_setup.get("commission_values"):
            print(f"DEBUG: Commission values structure: {commission_setup.get('commission_values')}")
            brokerage_data = commission_setup.get("commission_values", {}).get("brokerage_revenue_percent", [])
            if brokerage_data:
                print(f"DEBUG: Brokerage commission data from setup: {brokerage_data[0]}")
        
        # If commission setup not found, try to get it from the original brokerage commission's commission_setup_id
        if commission_setup == ("NOT_FOUND",):
            print(f"WARNING: Commission setup not found for product_id={original_product_id}, insurer_id={original_insurer_id}, transaction_type={commission_setup_transaction_type}")
            print(f"Attempting to use commission setup from original brokerage commission...")
            if original_brokerage and original_brokerage.get("commission_setup_id"):
                commission_setup_id = original_brokerage.get("commission_setup_id")
                # Get commission setup record
                commission_setup_record = QueryBuilderService("crmf_commission_setups").where("id", commission_setup_id).first()
                if commission_setup_record:
                    # Get commission field values
                    commission_values = (
                        QueryBuilderService("crmf_commission_field_values")
                        .select(
                            "crmf_commission_field_values.value",
                            "crmf_commission_field_values.type",
                            "crmf_commission_field_values.user_id",
                            "crmf_commission_fields.attribute_name as field_attribute",
                            "core_users.display_name as user_name",
                            "core_users.email as user_email"
                        )
                        .leftJoin(
                            "crmf_commission_fields",
                            "crmf_commission_fields.id",
                            "crmf_commission_field_values.commission_field_id"
                        )
                        .leftJoin("core_users", "core_users.id", "crmf_commission_field_values.user_id")
                        .where("commission_setup_id", commission_setup_id)
                        .get()
                    )
                    
                    # Build commission_values dictionary
                    commission_values_dict = {}
                    for value in commission_values:
                        field_attr = value.get("field_attribute")
                        if not field_attr:
                            continue
                        if field_attr not in commission_values_dict:
                            commission_values_dict[field_attr] = []
                        commission_values_dict[field_attr].append({
                            "value": value.get("value"),
                            "type": value.get("type"),
                            "user_id": value.get("user_id"),
                            "user_name": value.get("user_name"),
                            "user_email": value.get("user_email")
                        })
                    
                    # Add commission_values to commission_setup_record
                    commission_setup_record["commission_values"] = commission_values_dict
                    commission_setup = commission_setup_record
                    print(f"SUCCESS: Using commission setup from original brokerage commission (ID: {commission_setup_id})")
                else:
                    print(f"ERROR: Original brokerage commission setup record not found for ID: {commission_setup_id}")
                    return None, None
            else:
                print(f"ERROR: No commission setup available and original brokerage commission has no commission_setup_id")
                return None, None
        
        print(f"DEBUG: Commission setup found - ID: {commission_setup.get('id') if isinstance(commission_setup, dict) else 'N/A'}")
        print(transaction_type_id,'transaction_type_idx')
        
        # Get current premium amount from issued policy (not original invoice amount)
        # This ensures we use the updated premium amount after endorsements
        current_policy = QueryBuilderService("crmp_issued_policies").select("premium_amount", "paid_amount").where("id", issued_policy_id).first()
        if current_policy:
            current_premium_amount = safe_decimal(current_policy.get("premium_amount"), default="0.0")
            current_paid_amount = safe_decimal(current_policy.get("paid_amount"), default="0.0")
        else:
            # Fallback to original invoice if policy not found
            current_premium_amount = safe_decimal(original_invoice.get("invoice_amount"), default="0.0")
            current_paid_amount = safe_decimal(original_invoice.get("paid_amount"), default="0.0")
        
        # Keep original invoice amounts for reference (used in ratio calculations)
        original_invoice_amount = safe_decimal(original_invoice.get("invoice_amount"), default="0.0")
        original_paid_amount = safe_decimal(original_invoice.get("paid_amount"), default="0.0")
        
        print(f"DEBUG: Current premium amount from policy: {current_premium_amount}, Current paid amount: {current_paid_amount}")
        print(f"DEBUG: Original invoice amount: {original_invoice_amount}, Original paid amount: {original_paid_amount}")
        print(f"DEBUG: Refund/Cancellation invoice amount: {invoice_amount}, Paid amount: {paid_amount}")
        
        # --- Ratio logic for refund/cancellation ---
        # IMPORTANT: Calculation logic based on commission type:
        # 
        # 1. PERCENTAGE commission:
        #    - Calculate directly on endorsement_amount (no ratio needed)
        #    - Example: Refund 50,000, Commission 10% → Deductible = 10% of 50,000 = 5,000
        #
        # 2. FIXED/FLAT commission:
        #    - Calculate on FULL current premium amount, then apply ratio
        #    - Example: Premium 450,000, Refund 50,000, Fixed 10,000
        #      → Calculate on premium: 10,000, Ratio = 50,000/450,000 = 0.1111
        #      → Deductible = 10,000 * 0.1111 = 1,111.11
        #
        # For agents with revised_amount:
        #   - If revised_amount exists, it's used instead of commission percentage
        #   - If revised_amount is fixed/flat: Apply ratio
        #   - If revised_amount is percentage: Calculate directly on endorsement amount
        if transaction_type_id == 4:  # Refund (IGF)
            refund_amount = safe_decimal(invoice_amount, default="0.0")
            endorsement_amount = refund_amount  # Store for later use in revised_amount recalculation
            print(current_premium_amount, refund_amount,'current_premium_refund_amount')
            
            # IMPORTANT: For refunds, use ORIGINAL premium amount (before refund) for ratio calculation
            # The current_premium_amount is already reduced by the refund, so we need to add it back
            # OR use original_invoice_amount which is the premium before the refund
            premium_for_ratio = original_invoice_amount if original_invoice_amount > 0 else (current_premium_amount + refund_amount)
            print(f"DEBUG: Using premium for ratio calculation: {premium_for_ratio} (original invoice amount: {original_invoice_amount}, current premium: {current_premium_amount}, refund: {refund_amount})")
            
            # Get brokerage commission type to determine calculation method
            commission_values = commission_setup.get("commission_values", {})
            brokerage_data = commission_values.get("brokerage_revenue_percent", [{"value": "0", "type": "flat"}])[0]
            brokerage_type = brokerage_data.get("type", "flat")
            
            if brokerage_type in ["flat", "fixed"]:
                # FIXED/FLAT (REFUND):
                # Previously: deductible was based on commission_setup value (e.g. 1000),
                # which is wrong when actual revenue_recognized is different (e.g. 10000).
                #
                # Correct logic:
                #   - Use ORIGINAL commission amounts (revenue_recognized) from database
                #   - Then apply refund ratio (refund_amount / original_premium)
                #
                # Example:
                #   Premium: 100,000
                #   Brokerage revenue_recognized: 10,000
                #   Agent revenue_recognized: 5,000
                #   Refund: 50,000  -> ratio = 0.5
                #   Brokerage deductible: 10,000 * 0.5 = 5,000
                #   Agent deductible:     5,000 * 0.5 = 2,500
                if premium_for_ratio > 0:
                    ratio = (refund_amount / premium_for_ratio).quantize(Decimal(".0001"))
                else:
                    ratio = Decimal("0.0")
                print(f"DEBUG: Fixed/flat commission (REFUND) - using original commission amounts with ratio: {ratio} (using premium: {premium_for_ratio})")

                # Use original brokerage commission revenue_recognized as base
                brokerage_amount = safe_decimal(original_brokerage.get("revenue_recognized"), default="0.00") if original_brokerage else Decimal("0.00")
                # Deductible is proportion of the original commission amount
                brokerage_deduction = (abs(brokerage_amount) * ratio).quantize(Decimal(".01"))
                print(f"DEBUG: Brokerage refund deductible from revenue_recognized: {brokerage_deduction} (original_amount: {brokerage_amount}, ratio: {ratio})")

                # Build agent_deductions list based on original agent commission revenue_recognized
                agent_deductions = []
                if original_agent_commissions:
                    for agent_comm in original_agent_commissions:
                        agent_id = agent_comm.get("agent_id")
                        if not agent_id:
                            continue
                        agent_amount = safe_decimal(agent_comm.get("revenue_recognized"), default="0.00")
                        agent_deduction = -(abs(agent_amount) * ratio).quantize(Decimal(".01"))
                        agent_deductions.append({
                            "user_id": agent_id,
                            "deduction": agent_deduction
                        })
                        print(f"DEBUG: Agent refund deductible from revenue_recognized for user_id {agent_id}: {agent_deduction} (original_amount: {agent_amount}, ratio: {ratio})")

                applied_ratio = ratio
            else:
                # PERCENTAGE: Calculate directly on endorsement amount (no ratio needed for brokerage)
                print(f"DEBUG: Percentage commission - calculating directly on endorsement amount: {refund_amount}")
                base_amount = calculate_commission_base_amount(refund_amount, Decimal("0.00"), calculation_mode)
                print(f"DEBUG: Base amount calculated from endorsement amount: {base_amount}")
                brokerage_deduction, agent_deductions = calculate_commission_deduction(base_amount, commission_setup, calculation_mode, original_brokerage, original_agent_commissions)
                if brokerage_deduction is None:
                    return None, None
                print(f"DEBUG: Calculated brokerage deduction directly on endorsement amount: {brokerage_deduction}")
                
                # No ratio needed for percentage brokerage - already calculated on endorsement amount
                applied_ratio = Decimal("1.0")
                
                # IMPORTANT: For FIXED agent commissions, we still need to apply ratio
                # even when brokerage is percentage type
                # Use ORIGINAL premium amount (before refund) for ratio calculation
                if premium_for_ratio > 0:
                    agent_ratio = (refund_amount / premium_for_ratio).quantize(Decimal(".0001"))
                else:
                    agent_ratio = Decimal("0.0")
                
                # Get agent commission types from commission setup
                agent_data_list = commission_values.get("agent_commission_percent", [])
                for agent_data in agent_deductions:
                    user_id = agent_data.get("user_id")
                    # Find the agent commission type from setup
                    agent_setup = next((a for a in agent_data_list if a.get("user_id") == user_id), None)
                    if agent_setup:
                        agent_type = agent_setup.get("type", "flat")
                        if agent_type in ["flat", "fixed"]:
                            # Apply ratio to fixed agent commission
                            original_deduction = agent_data["deduction"]
                            agent_data["deduction"] = (agent_data["deduction"] * agent_ratio).quantize(Decimal(".01"))
                            print(f"DEBUG: Applied ratio to FIXED agent commission for user_id {user_id}: {original_deduction} * {agent_ratio} = {agent_data['deduction']}")
        elif transaction_type_id == 5:  # Cancellation
            # For cancellations, calculation logic based on commission type (same as refunds):
            # 
            # 1. PERCENTAGE commission:
            #    - Calculate directly on cancellation_amount (no ratio needed)
            #    - Example: Cancellation 20,000, Commission 10% → Deductible = 10% of 20,000 = 2,000
            #
            # 2. FIXED/FLAT commission:
            #    - Calculate on FULL original commission amounts (revenue_recognized), then apply ratio
            #    - Example: Premium 1,000,000, Cancellation 20,000, Brokerage 100,000
            #      → Ratio = 20,000/1,000,000 = 0.02
            #      → Deductible = 100,000 * 0.02 = 2,000
            cancellation_amount = safe_decimal(invoice_amount, default="0.0")
            endorsement_amount = cancellation_amount  # Store for later use in revised_amount recalculation
            print(f"DEBUG: Cancellation amount: {cancellation_amount}")
            print(f"DEBUG: Current premium amount: {current_premium_amount}")
            
            # IMPORTANT: For cancellations, use ORIGINAL premium amount (before cancellation) for ratio calculation
            # The current_premium_amount is already reduced by the cancellation, so we need to add it back
            # OR use original_invoice_amount which is the premium before the cancellation
            premium_for_ratio = original_invoice_amount if original_invoice_amount > 0 else (current_premium_amount + cancellation_amount)
            print(f"DEBUG: Using premium for ratio calculation: {premium_for_ratio} (original invoice amount: {original_invoice_amount}, current premium: {current_premium_amount}, cancellation: {cancellation_amount})")
            
            # Get brokerage commission type to determine calculation method
            commission_values = commission_setup.get("commission_values", {})
            brokerage_data = commission_values.get("brokerage_revenue_percent", [{"value": "0", "type": "flat"}])[0]
            brokerage_type = brokerage_data.get("type", "flat")
            
            if brokerage_type in ["flat", "fixed"]:
                # FIXED/FLAT (CANCELLATION):
                # Use ORIGINAL commission amounts (revenue_recognized) from database
                # then apply cancellation ratio.
                if premium_for_ratio > 0:
                    ratio = (cancellation_amount / premium_for_ratio).quantize(Decimal(".0001"))
                else:
                    ratio = Decimal("0.0")
                print(f"DEBUG: Fixed/flat commission (CANCELLATION) - using original commission amounts with ratio: {ratio} (using premium: {premium_for_ratio})")

                # Use original brokerage commission revenue_recognized as base
                brokerage_amount = safe_decimal(original_brokerage.get("revenue_recognized"), default="0.00") if original_brokerage else Decimal("0.00")
                brokerage_deduction = (abs(brokerage_amount) * ratio).quantize(Decimal(".01"))
                print(f"DEBUG: Brokerage cancellation deductible from revenue_recognized: {brokerage_deduction} (original_amount: {brokerage_amount}, ratio: {ratio})")

                # Build agent_deductions list based on original agent commission revenue_recognized
                agent_deductions = []
                if original_agent_commissions:
                    for agent_comm in original_agent_commissions:
                        agent_id = agent_comm.get("agent_id")
                        if not agent_id:
                            continue
                        agent_amount = safe_decimal(agent_comm.get("revenue_recognized"), default="0.00")
                        agent_deduction = -(abs(agent_amount) * ratio).quantize(Decimal(".01"))
                        agent_deductions.append({
                            "user_id": agent_id,
                            "deduction": agent_deduction
                        })
                        print(f"DEBUG: Agent cancellation deductible from revenue_recognized for user_id {agent_id}: {agent_deduction} (original_amount: {agent_amount}, ratio: {ratio})")

                applied_ratio = ratio
            else:
                # PERCENTAGE: Calculate directly on cancellation amount (no ratio needed for brokerage)
                print(f"DEBUG: Percentage commission - calculating directly on cancellation amount: {cancellation_amount}")
                base_amount = calculate_commission_base_amount(cancellation_amount, Decimal("0.00"), calculation_mode)
                print(f"DEBUG: Base amount calculated from cancellation amount: {base_amount}")
                brokerage_deduction, agent_deductions = calculate_commission_deduction(base_amount, commission_setup, calculation_mode, original_brokerage, original_agent_commissions)
                if brokerage_deduction is None:
                    return None, None
                print(f"DEBUG: Calculated brokerage deduction directly on cancellation amount: {brokerage_deduction}")
                
                # No ratio needed for percentage brokerage - already calculated on cancellation amount
                applied_ratio = Decimal("1.0")
                
                # IMPORTANT: For FIXED agent commissions, we still need to apply ratio
                # even when brokerage is percentage type
                # Use ORIGINAL premium amount (before cancellation) for ratio calculation
                if premium_for_ratio > 0:
                    agent_ratio = (cancellation_amount / premium_for_ratio).quantize(Decimal(".0001"))
                else:
                    agent_ratio = Decimal("0.0")
                
                # Get agent commission types from commission setup
                agent_data_list = commission_values.get("agent_commission_percent", [])
                for agent_data in agent_deductions:
                    user_id = agent_data.get("user_id")
                    # Find the agent commission type from setup
                    agent_setup = next((a for a in agent_data_list if a.get("user_id") == user_id), None)
                    if agent_setup:
                        agent_type = agent_setup.get("type", "flat")
                        if agent_type in ["flat", "fixed"]:
                            # Apply ratio to fixed agent commission
                            original_deduction = agent_data["deduction"]
                            agent_data["deduction"] = (agent_data["deduction"] * agent_ratio).quantize(Decimal(".01"))
                            print(f"DEBUG: Applied ratio to FIXED agent commission for user_id {user_id}: {original_deduction} * {agent_ratio} = {agent_data['deduction']}")
        else:
            # Default case (shouldn't happen for deductions)
            endorsement_amount = safe_decimal(invoice_amount, default="0.0")  # Store for later use
            base_amount = calculate_commission_base_amount(current_premium_amount, current_paid_amount, calculation_mode)
            brokerage_deduction, agent_deductions = calculate_commission_deduction(base_amount, commission_setup, calculation_mode, original_brokerage, original_agent_commissions)
            if brokerage_deduction is None:
                return None, None
            # No ratio for default case
            applied_ratio = Decimal("1.0")
        
        # If agent_deductions have user_id: None, get agent_ids from original agent commission records
        # This happens when commission setup doesn't specify user_id for agent commissions
        if agent_deductions and any(d.get("user_id") is None for d in agent_deductions):
            print(f"DEBUG: Some agent deductions have user_id=None. Getting agent_ids from original agent commission records...")
            original_agent_commissions = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", original_brokerage["id"]).get()
            
            if original_agent_commissions:
                # Map agent deductions to actual agent_ids from original commissions
                updated_agent_deductions = []
                for agent_deduction in agent_deductions:
                    if agent_deduction.get("user_id") is None:
                        # If user_id is None, apply deduction to all agents from original commission
                        # Or use sales_agent_id if provided
                        if sales_agent_id:
                            agent_deduction["user_id"] = sales_agent_id
                            updated_agent_deductions.append(agent_deduction)
                        else:
                            # Apply to all agents from original commission
                            for orig_agent_comm in original_agent_commissions:
                                agent_id = orig_agent_comm.get("agent_id")
                                if agent_id:
                                    updated_agent_deductions.append({
                                        "user_id": agent_id,
                                        "deduction": agent_deduction["deduction"]
                                    })
                    else:
                        updated_agent_deductions.append(agent_deduction)
                
                agent_deductions = updated_agent_deductions
                print(f"DEBUG: Updated agent_deductions with agent_ids: {agent_deductions}")
            else:
                # If no original agent commissions found, use sales_agent_id if provided
                if sales_agent_id:
                    updated_agent_deductions = []
                    for agent_deduction in agent_deductions:
                        if agent_deduction.get("user_id") is None:
                            agent_deduction["user_id"] = sales_agent_id
                        updated_agent_deductions.append(agent_deduction)
                    agent_deductions = updated_agent_deductions
                    print(f"DEBUG: Using sales_agent_id {sales_agent_id} for agent deductions")
        
        # Filter agent deductions for specific sales agent if provided
        if sales_agent_id:
            agent_deductions = [d for d in agent_deductions if str(d.get("user_id")) == str(sales_agent_id)]
        
        # NOW check for revised_amount after user_id is resolved
        # Recalculate deductions for agents with revised_amount > 0
        if original_agent_commissions and agent_deductions:
            # Get brokerage_amount from original brokerage commission for ratio calculation
            brokerage_amount = safe_decimal(original_brokerage.get("revenue_recognized"), default="0.00") if original_brokerage else Decimal("0.00")
            print(f"DEBUG: Re-checking for revised_amount after user_id resolution (brokerage_amount: {brokerage_amount}, applied_ratio: {applied_ratio if 'applied_ratio' in locals() else 'NOT_SET'})")
            for agent_deduction in agent_deductions:
                user_id = agent_deduction.get("user_id")
                if user_id:
                    # Find the agent commission record
                    agent_comm_record = next((ac for ac in original_agent_commissions if ac.get("agent_id") == user_id), None)
                    if agent_comm_record:
                        revised_amount_db = safe_decimal(agent_comm_record.get("revised_amount"), default="0.00")
                        revised_amount_percent_db = safe_decimal(agent_comm_record.get("revised_amount_percent"), default="0.00")
                        revised_amount_type_db = agent_comm_record.get("revised_amount_type", "percentage")
                        
                        print(f"DEBUG: Agent {user_id} - revised_amount_db: {revised_amount_db}, revised_amount_percent_db: {revised_amount_percent_db}, revised_amount_type_db: {revised_amount_type_db}")
                        
                        if revised_amount_db > 0:
                            print(f"DEBUG: Agent {user_id} has revised_amount={revised_amount_db} - recalculating deductible (applied_ratio: {applied_ratio}, endorsement_amount: {endorsement_amount if 'endorsement_amount' in locals() else 'NOT_SET'})")
                            # Recalculate based on revised_amount
                            # IMPORTANT: Calculation logic based on revised_amount type:
                            # - PERCENTAGE: Calculate directly on endorsement_amount (no ratio)
                            # - FIXED/FLAT: Apply ratio (endorsement_amount / current_premium_amount)
                            if revised_amount_type_db in ["flat", "fixed"]:
                                # For fixed/flat, calculate proportionally based on applied_ratio
                                # Calculate base deduction: revised_amount * (refund/cancellation ratio)
                                base_revised_deduction = -(revised_amount_db * applied_ratio).quantize(Decimal(".01"))
                                print(f"DEBUG: Recalculated fixed/flat revised_amount deductible: {base_revised_deduction} (was {agent_deduction['deduction']})")
                                agent_deduction["deduction"] = base_revised_deduction
                            else:
                                # Percentage type - calculate based on brokerage_deduction
                                # IMPORTANT: All agent deductions must be based on brokerage_deduction, not endorsement_amount
                                if revised_amount_percent_db > 0:
                                    # Calculate as percentage of brokerage_deduction
                                    brokerage_deduction_abs = abs(brokerage_deduction)
                                    new_deduction = -(brokerage_deduction_abs * revised_amount_percent_db / Decimal("100")).quantize(Decimal(".01"))
                                    # Ensure agent deductible never exceeds brokerage deductible
                                    if abs(new_deduction) > brokerage_deduction_abs:
                                        new_deduction = -brokerage_deduction_abs
                                    print(f"DEBUG: Recalculated percentage revised_amount deductible from brokerage_deduction: {new_deduction} (brokerage_deduction={brokerage_deduction_abs} * {revised_amount_percent_db}%, was {agent_deduction['deduction']})")
                                    agent_deduction["deduction"] = new_deduction
                                else:
                                    # revised_amount set directly without percent - apply ratio
                                    base_revised_deduction = -(revised_amount_db * applied_ratio).quantize(Decimal(".01"))
                                    print(f"DEBUG: Recalculated revised_amount (no percent) deductible: {base_revised_deduction} (was {agent_deduction['deduction']})")
                                    agent_deduction["deduction"] = base_revised_deduction
                        else:
                            print(f"DEBUG: Agent {user_id} has revised_amount={revised_amount_db} (not > 0), keeping original deduction: {agent_deduction['deduction']}")
                    else:
                        print(f"DEBUG: Agent {user_id} commission record not found in original_agent_commissions")
                else:
                    print(f"DEBUG: user_id is None in agent_deduction, skipping revised_amount check")
        
        print("sssszyy_FINAL", brokerage_deduction, agent_deductions)
        
        # For refund/cancellation types, store deductible amounts immediately when endorsement is created
        # Commission calculations for refund and cancellation should happen in create_endorsement only
        # Store deductible amounts only (do NOT deduct from revenue_recognized)
        success = store_commission_deductible_only(original_brokerage["id"], brokerage_deduction, agent_deductions, invoice.get("id") if invoice else None)
        
        if success:
            # Do NOT create separate commission records for refund/cancellation invoices
            # The deductible amounts are already stored in the premium invoice commission
            # via the store_commission_deductible_only function above
            print(f"DEBUG: Commission deductible amounts stored in premium invoice commission during endorsement creation. No separate commission records created for refund/cancellation invoice {invoice_id_value}")
            print(f"DEBUG: NOTE: revenue_recognized was NOT modified - only commission_deductible was updated")
            
            # After storing deductible amounts, create adjustment journal entries
            all_commissions = []
            brokerage_commission_record = QueryBuilderService("crmf_brokerage_commission").where("id", original_brokerage["id"]).first()
            if brokerage_commission_record:
                all_commissions.append(brokerage_commission_record)
            agent_commissions = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", original_brokerage["id"]).get()
            all_commissions.extend(agent_commissions)
            invoice_record = QueryBuilderService("crmf_invoices").where("id", invoice["id"]).first() if invoice else None
            # Use the new utility for deduction journal entries
            create_commission_deduction_journal_entries(all_commissions, invoice_record, user)
            return original_brokerage["id"], None
        else:
            print(f"ERROR: Failed to store commission deductible amounts for refund/cancellation invoice {invoice_id_value}")
            return None, None
        
    except Exception as e:
        print(f"Error handling commission deduction: {str(e)}")
        return None, None


def update_premium_commission_deductible_for_payment(refund_cancellation_invoice_id, paid_amount, transaction_type_id, user=None):
    """
    Update premium invoice commission deductible when a refund/cancellation invoice is paid.
    The deductible amount is calculated based on the paid amount of the refund/cancellation invoice.
    
    Args:
        refund_cancellation_invoice_id (int): ID of the refund/cancellation invoice being paid
        paid_amount (Decimal): Amount paid for the refund/cancellation invoice
        transaction_type_id (int): Transaction type ID (4 for Refund, 5 for Cancellation)
        user (User, optional): User making the payment
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        from envoy_bu_policy_api.finance.controllers.utils.service import get_commission_setup_service
        
        print(f"DEBUG: Updating premium commission deductible for payment")
        print(f"  - Refund/Cancellation Invoice ID: {refund_cancellation_invoice_id}")
        print(f"  - Paid Amount: {paid_amount}")
        print(f"  - Transaction Type ID: {transaction_type_id}")
        
        # Get the refund/cancellation invoice
        refund_invoice = QueryBuilderService("crmf_invoices").where("id", refund_cancellation_invoice_id).first()
        if not refund_invoice:
            print(f"ERROR: Refund/cancellation invoice {refund_cancellation_invoice_id} not found")
            return False
        
        issued_policy_id = refund_invoice.get("issued_policy_id")
        if not issued_policy_id:
            print(f"ERROR: No issued_policy_id found for refund/cancellation invoice {refund_cancellation_invoice_id}")
            return False
        
        # Find the original premium invoice commission (New Business or Renewal)
        original_invoice, original_brokerage = find_original_new_business_commission(issued_policy_id)
        if not original_invoice or not original_brokerage:
            print(f"ERROR: Could not find original premium invoice commission for issued_policy_id {issued_policy_id}")
            return False
        
        print(f"DEBUG: Found original premium invoice commission - invoice_id: {original_invoice['id']}, brokerage_id: {original_brokerage['id']}")
        
        # Use product_id and insurer_id from the original invoice (not the refund/cancellation invoice)
        # This ensures we get the correct commission setup that was used for the original policy
        original_product_id = original_invoice.get("product_id")
        original_insurer_id = original_invoice.get("insurer_id")
        
        if not original_product_id or not original_insurer_id:
            print(f"ERROR: Missing product_id or insurer_id in original invoice")
            return False
        
        # Get product_group_id from policy base for commission setup fallback
        original_product_group_id = None
        if issued_policy_id:
            policy_base = QueryBuilderService("crmp_issued_policies").select("policy_base_id").where("id", issued_policy_id).first()
            if policy_base and policy_base.get("policy_base_id"):
                policy_base_data = QueryBuilderService("crmp_policy_base").select("product_group_id").where("id", policy_base.get("policy_base_id")).first()
                if policy_base_data:
                    original_product_group_id = policy_base_data.get("product_group_id")
        
        # Get the transaction type from the original invoice to use the correct commission setup
        original_transaction_type_id = original_invoice.get("transaction_type_id")
        commission_setup_transaction_type = original_transaction_type_id if original_transaction_type_id in [1, 3] else 1
        
        print(f"DEBUG: Using original invoice product_id: {original_product_id}, insurer_id: {original_insurer_id}, transaction_type: {commission_setup_transaction_type}, product_group_id: {original_product_group_id}")
        
        # Get commission setup
        # Pass product_group_id for fallback lookup if product-level setup not found
        commission_setup = get_commission_setup_service(original_product_id, original_insurer_id, commission_setup_transaction_type, original_product_group_id)
        if commission_setup == ("NOT_FOUND",):
            print(f"ERROR: Commission setup not found for product_id={original_product_id}, insurer_id={original_insurer_id}, transaction_type={commission_setup_transaction_type}")
            return False
        
        # Get current premium amount from issued policy (not original invoice amount)
        # This ensures we use the updated premium amount after endorsements
        current_policy = QueryBuilderService("crmp_issued_policies").select("premium_amount", "paid_amount").where("id", issued_policy_id).first()
        if current_policy:
            current_premium_amount = safe_decimal(current_policy.get("premium_amount"), default="0.0")
            current_paid_amount = safe_decimal(current_policy.get("paid_amount"), default="0.0")
        else:
            # Fallback to original invoice if policy not found
            current_premium_amount = safe_decimal(original_invoice.get("invoice_amount"), default="0.0")
            current_paid_amount = safe_decimal(original_invoice.get("paid_amount"), default="0.0")
        
        # Keep original invoice amounts for reference (used in ratio calculations)
        original_invoice_amount = safe_decimal(original_invoice.get("invoice_amount"), default="0.0")
        original_paid_amount = safe_decimal(original_invoice.get("paid_amount"), default="0.0")
        
        # Get current paid amount of refund/cancellation invoice to calculate incremental payment
        current_refund_paid = safe_decimal(refund_invoice.get("paid_amount"), default="0.0")
        previous_refund_paid = current_refund_paid - paid_amount  # This is the paid amount before this payment
        
        print(f"DEBUG: Current premium amount from policy: {current_premium_amount}, Current paid amount: {current_paid_amount}")
        print(f"DEBUG: Original invoice amount: {original_invoice_amount}, Original paid amount: {original_paid_amount}")
        print(f"DEBUG: Refund/Cancellation invoice - Previous paid: {previous_refund_paid}, Current paid: {current_refund_paid}, This payment: {paid_amount}")
        
        # Get brokerage commission type to determine calculation method
        commission_values = commission_setup.get("commission_values", {})
        brokerage_data = commission_values.get("brokerage_revenue_percent", [{"value": "0", "type": "flat"}])[0]
        brokerage_type = brokerage_data.get("type", "flat")
        
        # IMPORTANT: Calculation logic based on commission type:
        # 
        # 1. PERCENTAGE commission:
        #    - Calculate directly on paid_amount (incremental payment amount, no ratio needed)
        #    - Example: Payment 10,000, Commission 10% → Deductible = 10% of 10,000 = 1,000
        #
        # 2. FIXED/FLAT commission:
        #    - Calculate on FULL current premium amount, then apply ratio (paid_amount / current_premium_amount)
        #    - Example: Premium 450,000, Payment 10,000, Fixed 10,000
        #      → Calculate on premium: 10,000, Ratio = 10,000/450,000 = 0.0222
        #      → Deductible = 10,000 * 0.0222 = 222.22
        
        calculation_mode = get_commission_calculation_mode()
        
        if brokerage_type in ["flat", "fixed"]:
            # FIXED/FLAT: Calculate on full premium, then apply ratio
            if current_premium_amount > 0:
                incremental_ratio = (paid_amount / current_premium_amount).quantize(Decimal(".0001"))
            else:
                incremental_ratio = Decimal("0.0")
            print(f"DEBUG: Fixed/flat commission - calculating on full premium, then applying ratio: {incremental_ratio}")
            
            # Calculate commission deduction on FULL current premium amount
            base_amount = calculate_commission_base_amount(current_premium_amount, current_paid_amount, calculation_mode)
            print(f"DEBUG: Base amount calculated from current premium amount: {base_amount}")
            brokerage_deduction, agent_deductions = calculate_commission_deduction(base_amount, commission_setup, calculation_mode, original_brokerage, original_agent_commissions)
            if brokerage_deduction is None:
                print(f"ERROR: Failed to calculate commission deductions")
                return False
            
            # Apply incremental ratio to deductions
            incremental_brokerage_deduction = (brokerage_deduction * incremental_ratio).quantize(Decimal(".01"))
            print(f"DEBUG: Applied incremental ratio to brokerage deduction: {incremental_brokerage_deduction} (ratio: {incremental_ratio})")
            
            incremental_agent_deductions = []
            for agent_data in agent_deductions:
                original_deduction = agent_data["deduction"]
                incremental_deduction = (agent_data["deduction"] * incremental_ratio).quantize(Decimal(".01"))
                print(f"DEBUG: Applied incremental ratio to agent deduction for user_id {agent_data.get('user_id')}: {original_deduction} * {incremental_ratio} = {incremental_deduction}")
                incremental_agent_deductions.append({
                    "user_id": agent_data.get("user_id"),
                    "deduction": incremental_deduction
                })
        else:
            # PERCENTAGE: Calculate directly on paid_amount (no ratio needed for brokerage)
            print(f"DEBUG: Percentage commission - calculating directly on paid amount: {paid_amount}")
            base_amount = calculate_commission_base_amount(paid_amount, Decimal("0.00"), calculation_mode)
            print(f"DEBUG: Base amount calculated from paid amount: {base_amount}")
            brokerage_deduction, agent_deductions = calculate_commission_deduction(base_amount, commission_setup, calculation_mode, original_brokerage, original_agent_commissions)
            if brokerage_deduction is None:
                print(f"ERROR: Failed to calculate commission deductions")
                return False
            
            # No ratio needed for percentage brokerage - already calculated on paid amount
            incremental_brokerage_deduction = brokerage_deduction
            print(f"DEBUG: Calculated brokerage deduction directly on paid amount: {incremental_brokerage_deduction}")
            
            # IMPORTANT: For FIXED agent commissions, we still need to apply ratio
            # even when brokerage is percentage type
            # Check if any agent commission is fixed type and apply ratio
            if current_premium_amount > 0:
                agent_ratio = (paid_amount / current_premium_amount).quantize(Decimal(".0001"))
            else:
                agent_ratio = Decimal("0.0")
            
            incremental_agent_deductions = []
            # Get agent commission types from commission setup
            agent_data_list = commission_values.get("agent_commission_percent", [])
            for agent_data in agent_deductions:
                user_id = agent_data.get("user_id")
                # Find the agent commission type from setup
                agent_setup = next((a for a in agent_data_list if a.get("user_id") == user_id), None)
                if agent_setup:
                    agent_type = agent_setup.get("type", "flat")
                    if agent_type in ["flat", "fixed"]:
                        # Apply ratio to fixed agent commission
                        original_deduction = agent_data["deduction"]
                        incremental_deduction = (agent_data["deduction"] * agent_ratio).quantize(Decimal(".01"))
                        print(f"DEBUG: Applied ratio to FIXED agent commission for user_id {user_id}: {original_deduction} * {agent_ratio} = {incremental_deduction}")
                    else:
                        # Percentage agent commission - already calculated correctly
                        incremental_deduction = agent_data["deduction"]
                        print(f"DEBUG: Calculated percentage agent deduction directly on paid amount for user_id {user_id}: {incremental_deduction}")
                else:
                    # If agent setup not found, use deduction as is (shouldn't happen)
                    incremental_deduction = agent_data["deduction"]
                    print(f"DEBUG: Agent setup not found for user_id {user_id}, using deduction as is: {incremental_deduction}")
                
                incremental_agent_deductions.append({
                    "user_id": user_id,
                    "deduction": incremental_deduction
                })
        
        # Get original agent commission records to check for revised_amount (needed for user_id resolution)
        original_agent_commissions = []
        if original_brokerage and original_brokerage.get("id"):
            original_agent_commissions = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", original_brokerage["id"]).get()
            print(f"DEBUG: Found {len(original_agent_commissions)} original agent commission records for payment update")
        
        # If agent_deductions have user_id: None, get agent_ids from original agent commission records
        # This happens when commission setup doesn't specify user_id for agent commissions
        if incremental_agent_deductions and any(d.get("user_id") is None for d in incremental_agent_deductions):
            print(f"DEBUG: Some incremental agent deductions have user_id=None. Getting agent_ids from original agent commission records...")
            original_agent_commissions = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", original_brokerage["id"]).get()
            
            if original_agent_commissions:
                # Map agent deductions to actual agent_ids from original commissions
                updated_agent_deductions = []
                for agent_deduction in incremental_agent_deductions:
                    if agent_deduction.get("user_id") is None:
                        # Apply to all agents from original commission
                        for orig_agent_comm in original_agent_commissions:
                            agent_id = orig_agent_comm.get("agent_id")
                            if agent_id:
                                updated_agent_deductions.append({
                                    "user_id": agent_id,
                                    "deduction": agent_deduction["deduction"]
                                })
                    else:
                        updated_agent_deductions.append(agent_deduction)
                
                incremental_agent_deductions = updated_agent_deductions
                print(f"DEBUG: Updated incremental agent_deductions with agent_ids: {incremental_agent_deductions}")
            else:
                print(f"WARNING: No original agent commissions found for brokerage_id {original_brokerage['id']}. Agent deductions will be skipped.")
        
        print(f"DEBUG: Incremental brokerage deduction: {incremental_brokerage_deduction}")
        print(f"DEBUG: Incremental agent deductions: {incremental_agent_deductions}")
        
        # Apply incremental deductions to premium invoice commission
        success = apply_commission_deduction(original_brokerage["id"], incremental_brokerage_deduction, incremental_agent_deductions, refund_cancellation_invoice_id)
        
        if success:
            print(f"DEBUG: Successfully updated premium invoice commission deductible based on paid amount")
            return True
        else:
            print(f"ERROR: Failed to apply commission deductions")
            return False
            
    except Exception as e:
        print(f"Error updating premium commission deductible for payment: {str(e)}")
        import traceback
        traceback.print_exc()
        return False 