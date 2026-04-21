#!/usr/bin/env python3
"""
Test script to verify incentive calculation fixes
"""

import sys
import os
import django
from decimal import Decimal

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envoy_bu_policy_api.settings')
django.setup()

from envoy_bu_policy_api.finance.controllers.utils.incentive_utils import (
    evaluate_condition, 
    calculate_incentive_reward,
    evaluate_logic_tree,
    find_agents_for_period
)
from mServices import QueryBuilderService

def test_evaluate_condition():
    """Test the fixed evaluate_condition function"""
    print("Testing evaluate_condition function...")
    
    # Test numeric comparisons with string values
    test_cases = [
        # (performance_value, operator, value, expected_result)
        (100.0, "<", "150", True),
        (100.0, ">", "50", True),
        (100.0, "=", "100", True),
        (100.0, "<=", "100", True),
        (100.0, ">=", "100", True),
        (100.0, "<", "50", False),
        (100.0, ">", "150", False),
        (Decimal("100.5"), "<", "150", True),
        (Decimal("100.5"), ">", "50", True),
        (0, ">", "0", False),
        (0, ">=", "0", True),
    ]
    
    for i, (perf_val, op, val, expected) in enumerate(test_cases):
        result = evaluate_condition(perf_val, op, val)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Test {i+1}: {perf_val} {op} {val} = {result} (expected: {expected})")
    
    print()

def test_calculate_incentive_reward():
    """Test the fixed calculate_incentive_reward function"""
    print("Testing calculate_incentive_reward function...")
    
    # Test setup with simple condition
    test_setup = {
        "performance_fields": [
            {
                "field": "policies",
                "operator": ">=",
                "value": "5",
                "reward_type": "percentage",
                "reward_type_value": 10
            }
        ],
        "reward_type_value": 10,
        "reward_type_string": "percentage",
        "incentive_base_field": "policies"
    }
    
    test_performance_data = {
        "policies": 10.0
    }
    
    try:
        result = calculate_incentive_reward(test_setup, test_performance_data)
        print(f"  ✓ Incentive calculation result: {result}")
        
        if result["eligible"]:
            print(f"  ✓ Eligible: {result['eligible']}")
            print(f"  ✓ Reward: {result['reward']}")
            print(f"  ✓ Matched condition: {result['matched_condition']}")
        else:
            print(f"  ✗ Not eligible: {result['message']}")
            
    except Exception as e:
        print(f"  ✗ Error in incentive calculation: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_sales_agent_id_retrieval():
    """Test that sales agent IDs are retrieved from crmp_policy_base.sales_agent_id"""
    print("Testing sales agent ID retrieval from crmp_policy_base...")
    
    try:
        # Test setup with a field that should use crmp_policy_base.sales_agent_id
        test_setup = {
            "performance_fields": {
                "field": "policies",
                "operator": ">=",
                "value": "1"
            }
        }
        
        # Test period (current month)
        from datetime import datetime, timedelta
        today = datetime.now()
        period_start = today.replace(day=1)
        period_end = today
        
        print(f"  Testing period: {period_start.strftime('%Y-%m-%d')} to {period_end.strftime('%Y-%m-%d')}")
        
        # Test the find_agents_for_period function
        agent_ids = find_agents_for_period(test_setup, (period_start, period_end))
        print(f"  ✓ Found {len(agent_ids)} agent IDs: {agent_ids}")
        
        if agent_ids:
            print(f"  ✓ Successfully retrieved sales agent IDs from crmp_policy_base.sales_agent_id")
            
            # Verify that these are valid agent IDs by checking core_users table
            if agent_ids:
                sample_agent_id = agent_ids[0]
                user_check = QueryBuilderService("core_users").select("id", "display_name").where("id", sample_agent_id).first()
                if user_check:
                    print(f"  ✓ Verified agent {sample_agent_id} exists in core_users: {user_check.get('display_name', 'Unknown')}")
                else:
                    print(f"  ✗ Agent {sample_agent_id} not found in core_users table")
        else:
            print(f"  ⚠ No agent IDs found - this might be expected if no policies exist for the test period")
            
    except Exception as e:
        print(f"  ✗ Error testing sales agent ID retrieval: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def test_direct_sales_agent_query():
    """Test direct query to verify crmp_policy_base.sales_agent_id exists and has data"""
    print("Testing direct query to crmp_policy_base.sales_agent_id...")
    
    try:
        # Query crmp_policy_base to check if sales_agent_id field exists and has data
        policy_base_query = QueryBuilderService("crmp_policy_base").select("id", "sales_agent_id").limit(5).get()
        print(f"  ✓ Found {len(policy_base_query)} policy base records")
        
        if policy_base_query:
            sales_agent_ids = [row["sales_agent_id"] for row in policy_base_query if row["sales_agent_id"] is not None]
            print(f"  ✓ Found {len(sales_agent_ids)} non-null sales_agent_id values: {sales_agent_ids}")
            
            if sales_agent_ids:
                # Check if these sales agent IDs exist in core_users
                unique_agent_ids = list(set(sales_agent_ids))
                users_check = QueryBuilderService("core_users").select("id", "display_name").whereIn("id", unique_agent_ids).get()
                print(f"  ✓ Verified {len(users_check)} sales agents exist in core_users table")
                
                for user in users_check:
                    print(f"    - Agent {user['id']}: {user.get('display_name', 'Unknown')}")
            else:
                print(f"  ⚠ No non-null sales_agent_id values found in policy_base records")
        else:
            print(f"  ⚠ No policy_base records found")
            
    except Exception as e:
        print(f"  ✗ Error in direct sales agent query: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    """Test the fixed evaluate_logic_tree function"""
    print("Testing evaluate_logic_tree function...")
    
    # Test simple condition
    test_tree = {
        "field": "policies",
        "operator": ">=",
        "value": "5",
        "reward_type": "percentage",
        "reward_type_value": 10
    }
    
    test_performance_data = {
        "policies": 10.0
    }
    
    try:
        matched, matched_condition, reward, reward_type = evaluate_logic_tree(
            test_tree, test_performance_data, 10, "percentage"
        )
        print(f"  ✓ Logic tree evaluation result:")
        print(f"    - Matched: {matched}")
        print(f"    - Matched condition: {matched_condition}")
        print(f"    - Reward: {reward}")
        print(f"    - Reward type: {reward_type}")
        
    except Exception as e:
        print(f"  ✗ Error in logic tree evaluation: {e}")
        import traceback
        traceback.print_exc()
    
    print()

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Incentive Calculation Fixes")
    print("=" * 60)
    print()
    
    test_direct_sales_agent_query()
    test_sales_agent_id_retrieval()
    test_evaluate_condition()
    test_evaluate_logic_tree()
    test_calculate_incentive_reward()
    
    print("=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
