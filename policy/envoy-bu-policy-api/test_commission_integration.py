#!/usr/bin/env python3
"""
Test Commission Setup Integration with Policy Creation and Updates
"""

import sys
import os
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envoy_bu_policy_api.settings')
django.setup()

from mServices import QueryBuilderService
from envoy_bu_policy_api.finance.controllers.utils.invoice_utils import generate_invoice_for_issued_policy
from envoy_bu_policy_api.finance.controllers.utils.commission.main import calculate_commission_amounts

def test_commission_setup_integration():
    """Test commission setup integration with policy creation and updates"""
    print("=" * 80)
    print("TESTING: Commission Setup Integration with Policy Creation/Updates")
    print("=" * 80)
    
    # Test 1: Check existing commission setups
    print("\n1. CHECKING EXISTING COMMISSION SETUPS")
    print("-" * 50)
    
    setups = (
        QueryBuilderService("crmf_commission_setups")
        .select(
            "id", "product_id", "product_group_id", "insurer_id", 
            "transaction_type", "brokerage_revenue_percent", "agent_commission_percent"
        )
        .get()
    )
    
    print(f"Found {len(setups)} commission setups:")
    for setup in setups:
        print(f"  - ID: {setup['id']}, Product: {setup['product_id']}, Group: {setup['product_group_id']}, Insurer: {setup['insurer_id']}, Type: {setup['transaction_type']}")
    
    # Test 2: Check recent issued policies
    print("\n2. CHECKING RECENT ISSUED POLICIES")
    print("-" * 50)
    
    policies = (
        QueryBuilderService("crmp_issued_policies")
        .select("id", "policy_base_id", "premium_amount", "policy_effective_date")
        .orderBy("id", "desc")
        .get()
    )
    
    print(f"Found {len(policies)} recent policies:")
    for policy in policies:
        print(f"  - Policy ID: {policy['id']}, Base ID: {policy['policy_base_id']}, Premium: {policy['premium_amount']}")
        
        # Get policy base details
        policy_base = (
            QueryBuilderService("crmp_policy_base")
            .select("product_id", "product_group_id", "insurer_id", "sales_agent_id")
            .where("id", policy['policy_base_id'])
            .first()
        )
        
        if policy_base:
            print(f"    Product ID: {policy_base['product_id']}, Group ID: {policy_base['product_group_id']}, Insurer: {policy_base['insurer_id']}, Sales Agent: {policy_base['sales_agent_id']}")
    
    # Test 3: Check invoices and commissions for recent policies
    print("\n3. CHECKING INVOICES AND COMMISSIONS")
    print("-" * 50)
    
    for policy in policies[:3]:  # Test first 3 policies
        policy_id = policy['id']
        print(f"\nTesting Policy ID: {policy_id}")
        
        # Check invoice
        invoice = (
            QueryBuilderService("crmf_invoices")
            .select("id", "invoice_number", "invoice_amount", "paid_amount")
            .where("issued_policy_id", policy_id)
            .first()
        )
        
        if invoice:
            print(f"  ✅ Invoice found: {invoice['invoice_number']}, Amount: {invoice['invoice_amount']}")
            
            # Check brokerage commission
            brokerage_comm = (
                QueryBuilderService("crmf_brokerage_commission")
                .select("id", "commission_setup_id", "revenue_recognized", "agent_commission")
                .where("invoice_id", invoice['id'])
                .first()
            )
            
            if brokerage_comm:
                print(f"  ✅ Brokerage Commission: ID {brokerage_comm['id']}, Setup {brokerage_comm['commission_setup_id']}, Revenue: {brokerage_comm['revenue_recognized']}")
                
                # Check agent commissions
                agent_comms = (
                    QueryBuilderService("crmf_agent_commission")
                    .select("id", "agent_id", "revenue_recognized")
                    .where("brokerage_commission_id", brokerage_comm['id'])
                    .get()
                )
                
                if agent_comms:
                    print(f"  ✅ Agent Commissions: {len(agent_comms)} records")
                    for ac in agent_comms:
                        print(f"    - Agent ID: {ac['agent_id']}, Amount: {ac['revenue_recognized']}")
                else:
                    print(f"  ❌ No agent commissions found")
            else:
                print(f"  ❌ No brokerage commission found")
        else:
            print(f"  ❌ No invoice found")
    
    # Test 4: Test commission setup service with product group fallback
    print("\n4. TESTING COMMISSION SETUP SERVICE")
    print("-" * 50)
    
    from envoy_bu_policy_api.finance.controllers.utils.service import get_commission_setup_service
    
    # Test with a known product
    test_product_id = 43
    test_insurer_id = 19
    test_transaction_type = 1
    
    print(f"Testing commission setup lookup:")
    print(f"  Product ID: {test_product_id}")
    print(f"  Insurer ID: {test_insurer_id}")
    print(f"  Transaction Type: {test_transaction_type}")
    
    commission_setup = get_commission_setup_service(test_product_id, test_insurer_id, test_transaction_type)
    
    if commission_setup == ("NOT_FOUND",):
        print(f"  ❌ No commission setup found")
    else:
        print(f"  ✅ Commission setup found: ID {commission_setup.get('id')}")
        print(f"  Brokerage Revenue %: {commission_setup.get('brokerage_revenue_percent')}")
        print(f"  Agent Commission %: {commission_setup.get('agent_commission_percent')}")
        
        commission_values = commission_setup.get("commission_values", {})
        print(f"  Commission Values: {list(commission_values.keys())}")
        
        agent_commissions = commission_values.get("agent_commission_percent", [])
        print(f"  Agent Commission Configs: {len(agent_commissions)}")
        for ac in agent_commissions:
            print(f"    - User ID: {ac.get('user_id')}, Value: {ac.get('value')}, Type: {ac.get('type')}")
    
    # Test 5: Test commission calculation directly
    print("\n5. TESTING COMMISSION CALCULATION")
    print("-" * 50)
    
    if invoice and brokerage_comm:
        print(f"Testing commission calculation for invoice {invoice['id']}")
        
        # Get policy base for sales agent
        policy_base = (
            QueryBuilderService("crmp_policy_base")
            .select("product_id", "product_group_id", "insurer_id", "sales_agent_id")
            .where("id", policies[0]['policy_base_id'])
            .first()
        )
        
        if policy_base:
            print(f"Policy Base: Product {policy_base['product_id']}, Group {policy_base['product_group_id']}, Insurer {policy_base['insurer_id']}, Agent {policy_base['sales_agent_id']}")
            
            # Test commission calculation
            try:
                brokerage_id, agent_id = calculate_commission_amounts(
                    invoice_id=invoice['id'],
                    transaction_type_id=test_transaction_type,
                    product_id=policy_base['product_id'],
                    insurer_id=policy_base['insurer_id'],
                    sales_agent_id=policy_base['sales_agent_id'],
                    invoice_amount=invoice['invoice_amount'],
                    paid_amount=invoice['paid_amount'],
                    calculation_mode="premium",
                    user=None
                )
                
                if brokerage_id:
                    print(f"  ✅ Commission calculation successful: Brokerage ID {brokerage_id}")
                else:
                    print(f"  ❌ Commission calculation failed")
                    
            except Exception as e:
                print(f"  ❌ Commission calculation error: {e}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    test_commission_setup_integration()
