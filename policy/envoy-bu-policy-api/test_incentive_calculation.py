#!/usr/bin/env python
"""
Test script to verify incentive calculation for setup ID 43
"""
import os
import sys
import django
from decimal import Decimal

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'envoy_bu_policy_api.settings')
django.setup()

from django.db import connection

def test_commission_calculation():
    """Test the commission calculation with date filter"""
    
    agent_id = 9
    start_date = '2025-12-01'
    end_date = '2025-12-10'
    
    print("=" * 80)
    print("TESTING INCENTIVE CALCULATION FOR SETUP ID 43")
    print("=" * 80)
    print(f"Agent ID: {agent_id}")
    print(f"Period: {start_date} to {end_date}")
    print()
    
    # Query 1: Premium Amount (should be 940,000)
    query1 = """
    SELECT COALESCE(SUM(ip.premium_amount), 0) as sum_of_premium_amount
    FROM crmp_issued_policies ip
    INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
    INNER JOIN core_users cu ON pb.sales_agent_id = cu.id
    WHERE pb.sales_agent_id = %s
      AND ip.policy_effective_date >= %s
      AND ip.policy_effective_date <= %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query1, [agent_id, start_date, end_date])
        result1 = cursor.fetchone()
        premium_amount = float(result1[0]) if result1[0] else 0.0
        print(f"1. Premium Amount (with date filter): ${premium_amount:,.2f}")
        print(f"   Expected: $940,000.00")
        print(f"   Match: {'✓' if abs(premium_amount - 940000) < 1 else '✗'}")
        print()
    
    # Query 2: Commission Realized WITHOUT date filter (what was being calculated)
    query2_no_date = """
    SELECT COALESCE(SUM(ac.revenue_realized), 0) as sum_of_agent_commission_realized
    FROM crmf_agent_commission ac
    INNER JOIN crmf_brokerage_commission bc ON bc.id = ac.brokerage_commission_id
    INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
    INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
    INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
    INNER JOIN core_users cu ON pb.sales_agent_id = cu.id
    WHERE pb.sales_agent_id = %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query2_no_date, [agent_id])
        result2 = cursor.fetchone()
        commission_no_date = float(result2[0]) if result2[0] else 0.0
        print(f"2. Commission Realized (NO date filter): ${commission_no_date:,.2f}")
        print(f"   This is what was being calculated incorrectly: $24,292.68")
        print(f"   Match: {'✓' if abs(commission_no_date - 24292.68) < 1 else '✗'}")
        print()
    
    # Query 3: Commission Realized WITH date filter (correct calculation)
    query3_with_date = """
    SELECT COALESCE(SUM(ac.revenue_realized), 0) as sum_of_agent_commission_realized
    FROM crmf_agent_commission ac
    INNER JOIN crmf_brokerage_commission bc ON bc.id = ac.brokerage_commission_id
    INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
    INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
    INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
    INNER JOIN core_users cu ON pb.sales_agent_id = cu.id
    WHERE pb.sales_agent_id = %s
      AND ip.policy_effective_date >= %s
      AND ip.policy_effective_date <= %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(query3_with_date, [agent_id, start_date, end_date])
        result3 = cursor.fetchone()
        commission_with_date = float(result3[0]) if result3[0] else 0.0
        print(f"3. Commission Realized (WITH date filter): ${commission_with_date:,.2f}")
        print(f"   Expected: $9,653.85")
        print(f"   Match: {'✓' if abs(commission_with_date - 9653.85) < 1 else '✗'}")
        print()
    
    # Query 4: Calculate incentive amount
    incentive_percentage = 3.0
    expected_incentive = (commission_with_date * incentive_percentage) / 100.0
    incorrect_incentive = (commission_no_date * incentive_percentage) / 100.0
    
    print(f"4. Incentive Calculation:")
    print(f"   Correct: (${commission_with_date:,.2f} × {incentive_percentage}%) / 100 = ${expected_incentive:,.2f}")
    print(f"   Expected: $289.62")
    print(f"   Match: {'✓' if abs(expected_incentive - 289.62) < 1 else '✗'}")
    print()
    print(f"   Incorrect (what was calculated): (${commission_no_date:,.2f} × {incentive_percentage}%) / 100 = ${incorrect_incentive:,.2f}")
    print(f"   This matches the wrong result: $728.78")
    print(f"   Match: {'✓' if abs(incorrect_incentive - 728.78) < 1 else '✗'}")
    print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"The issue was that the date filter was NOT being applied to")
    print(f"sum_of_agent_commission_realized, causing it to sum ALL commissions")
    print(f"for the agent instead of just those in the period (Dec 1-10, 2025).")
    print()
    print(f"Fix: Added fallback date filter to use crmp_issued_policies.policy_effective_date")
    print(f"when the registry doesn't include date fields in its filters list.")
    print("=" * 80)

if __name__ == "__main__":
    test_commission_calculation()

