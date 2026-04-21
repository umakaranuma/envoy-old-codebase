#!/usr/bin/env python
"""
Script to get actual incentive calculation values from the database
Based on Incentive Setup ID: 43
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
import json

def execute_query(query, params=None):
    """Execute a SQL query and return results"""
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [col[0] for col in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        return results

def format_currency(value):
    """Format decimal value as currency"""
    if value is None:
        return "0.00"
    return f"{float(value):,.2f}"

def get_incentive_values():
    """Get all incentive calculation values for eligible agents"""
    
    print("=" * 80)
    print("INCENTIVE CALCULATION VALUES")
    print("Incentive Setup: sales bonus - december (ID: 43)")
    print("Period: 2025-12-01 to 2025-12-10")
    print("=" * 80)
    print()
    
    # Query 4: Complete Calculation for All Eligible Agents
    query = """
    SELECT 
        cu.id AS agent_id,
        cu.display_name AS agent_name,
        cu.email AS agent_email,
        cu.role_id,
        
        -- Premium Amount Check
        COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) AS sum_of_premium_amount,
        
        -- Commission Realized (Base for Calculation)
        COALESCE(SUM(DISTINCT commission_data.revenue_realized), 0) AS sum_of_agent_commission_realized,
        
        -- Eligibility Checks
        CASE 
            WHEN cu.role_id = 2 THEN 'PASS'
            ELSE 'FAIL'
        END AS role_check,
        CASE 
            WHEN COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) >= 600000 THEN 'PASS'
            ELSE 'FAIL'
        END AS premium_check,
        
        -- Final Eligibility
        CASE 
            WHEN cu.role_id = 2 
             AND COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) >= 600000 
            THEN 'ELIGIBLE'
            ELSE 'NOT ELIGIBLE'
        END AS eligibility_status,
        
        -- Incentive Calculation: (sum_of_agent_commission_realized × 3.0) / 100
        CASE 
            WHEN cu.role_id = 2 
             AND COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) >= 600000 
            THEN ROUND((COALESCE(SUM(DISTINCT commission_data.revenue_realized), 0) * 3.0) / 100.0, 2)
            ELSE 0.00
        END AS incentive_amount
        
    FROM core_users cu
    
    -- Get Premium Amount
    LEFT JOIN (
        SELECT 
            pb.sales_agent_id,
            SUM(ip.premium_amount) AS premium_amount
        FROM crmp_issued_policies ip
        INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
        WHERE ip.policy_effective_date >= '2025-12-01'
          AND ip.policy_effective_date <= '2025-12-10'
        GROUP BY pb.sales_agent_id
    ) premium_data ON premium_data.sales_agent_id = cu.id
    
    -- Get Commission Realized
    LEFT JOIN (
        SELECT 
            pb.sales_agent_id,
            SUM(ac.revenue_realized) AS revenue_realized
        FROM crmf_agent_commission ac
        INNER JOIN crmf_brokerage_commission bc ON bc.id = ac.brokerage_commission_id
        INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
        INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
        INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
        WHERE ip.policy_effective_date >= '2025-12-01'
          AND ip.policy_effective_date <= '2025-12-10'
        GROUP BY pb.sales_agent_id
    ) commission_data ON commission_data.sales_agent_id = cu.id
    
    WHERE cu.role_id = 2
      AND (
          premium_data.premium_amount IS NOT NULL 
          OR commission_data.revenue_realized IS NOT NULL
      )
    GROUP BY 
        cu.id, 
        cu.display_name, 
        cu.email, 
        cu.role_id,
        premium_data.premium_amount,
        commission_data.revenue_realized
    HAVING 
        COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) >= 600000
    ORDER BY incentive_amount DESC, cu.display_name;
    """
    
    results = execute_query(query)
    
    if not results:
        print("No eligible agents found matching the criteria.")
        print("\nCriteria:")
        print("  - Role ID = 2 (Sales Agent)")
        print("  - Premium Amount >= 600,000")
        print("  - Period: 2025-12-01 to 2025-12-10")
        return
    
    print(f"Found {len(results)} eligible agent(s):\n")
    print("-" * 80)
    
    total_incentive = Decimal('0.00')
    
    for idx, agent in enumerate(results, 1):
        print(f"\nAgent #{idx}:")
        print(f"  Agent ID: {agent['agent_id']}")
        print(f"  Name: {agent['agent_name']}")
        print(f"  Email: {agent['agent_email'] or 'N/A'}")
        print(f"  Role ID: {agent['role_id']}")
        print(f"  Role Check: {agent['role_check']}")
        print(f"  Premium Amount: ${format_currency(agent['sum_of_premium_amount'])}")
        print(f"  Premium Check: {agent['premium_check']}")
        print(f"  Commission Realized: ${format_currency(agent['sum_of_agent_commission_realized'])}")
        print(f"  Eligibility Status: {agent['eligibility_status']}")
        print(f"  Incentive Amount: ${format_currency(agent['incentive_amount'])}")
        
        # Calculation breakdown
        if agent['eligibility_status'] == 'ELIGIBLE':
            commission = float(agent['sum_of_agent_commission_realized'])
            percentage = 3.0
            calculated = (commission * percentage) / 100.0
            print(f"  Calculation: (${format_currency(commission)} × {percentage}%) / 100 = ${format_currency(calculated)}")
            total_incentive += Decimal(str(agent['incentive_amount']))
        
        print("-" * 80)
    
    print(f"\n{'=' * 80}")
    print(f"TOTAL INCENTIVE AMOUNT: ${format_currency(total_incentive)}")
    print(f"{'=' * 80}\n")
    
    # Also get detailed breakdown for first agent
    if results:
        print("\n" + "=" * 80)
        print("DETAILED BREAKDOWN FOR FIRST ELIGIBLE AGENT")
        print("=" * 80)
        first_agent_id = results[0]['agent_id']
        get_agent_details(first_agent_id)

def get_agent_details(agent_id):
    """Get detailed breakdown for a specific agent"""
    
    query = """
    SELECT 
        cu.id AS agent_id,
        cu.display_name AS agent_name,
        cu.role_id,
        
        -- Query 1: Premium Amount
        (SELECT COALESCE(SUM(ip.premium_amount), 0)
         FROM crmp_issued_policies ip
         INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
         WHERE pb.sales_agent_id = cu.id
           AND ip.policy_effective_date >= '2025-12-01'
           AND ip.policy_effective_date <= '2025-12-10'
        ) AS sum_of_premium_amount,
        
        -- Query 2: Commission Realized
        (SELECT COALESCE(SUM(ac.revenue_realized), 0)
         FROM crmf_agent_commission ac
         INNER JOIN crmf_brokerage_commission bc ON bc.id = ac.brokerage_commission_id
         INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
         INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
         INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
         WHERE pb.sales_agent_id = cu.id
           AND ip.policy_effective_date >= '2025-12-01'
           AND ip.policy_effective_date <= '2025-12-10'
        ) AS sum_of_agent_commission_realized,
        
        -- Eligibility Check
        CASE 
            WHEN cu.role_id = 2 THEN 'PASS' ELSE 'FAIL'
        END AS role_check,
        CASE 
            WHEN (SELECT COALESCE(SUM(ip.premium_amount), 0)
                  FROM crmp_issued_policies ip
                  INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
                  WHERE pb.sales_agent_id = cu.id
                    AND ip.policy_effective_date >= '2025-12-01'
                    AND ip.policy_effective_date <= '2025-12-10'
                 ) >= 600000 
            THEN 'PASS' 
            ELSE 'FAIL'
        END AS premium_check,
        
        -- Final Calculation
        CASE 
            WHEN cu.role_id = 2 
             AND (SELECT COALESCE(SUM(ip.premium_amount), 0)
                  FROM crmp_issued_policies ip
                  INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
                  WHERE pb.sales_agent_id = cu.id
                    AND ip.policy_effective_date >= '2025-12-01'
                    AND ip.policy_effective_date <= '2025-12-10'
                 ) >= 600000 
            THEN ROUND(
                ((SELECT COALESCE(SUM(ac.revenue_realized), 0)
                  FROM crmf_agent_commission ac
                  INNER JOIN crmf_brokerage_commission bc ON bc.id = ac.brokerage_commission_id
                  INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
                  INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
                  INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
                  WHERE pb.sales_agent_id = cu.id
                    AND ip.policy_effective_date >= '2025-12-01'
                    AND ip.policy_effective_date <= '2025-12-10'
                 ) * 3.0) / 100.0, 
                 2
            )
            ELSE 0.00
        END AS incentive_amount

    FROM core_users cu
    WHERE cu.id = %s;
    """
    
    results = execute_query(query, [agent_id])
    
    if results:
        agent = results[0]
        print(f"\nAgent ID: {agent['agent_id']}")
        print(f"Agent Name: {agent['agent_name']}")
        print(f"Role ID: {agent['role_id']}")
        print(f"\nValues:")
        print(f"  sum_of_premium_amount: ${format_currency(agent['sum_of_premium_amount'])}")
        print(f"  sum_of_agent_commission_realized: ${format_currency(agent['sum_of_agent_commission_realized'])}")
        print(f"\nChecks:")
        print(f"  Role Check (role_id = 2): {agent['role_check']}")
        print(f"  Premium Check (>= 600,000): {agent['premium_check']}")
        print(f"\nFinal Result:")
        print(f"  Incentive Amount: ${format_currency(agent['incentive_amount'])}")
        
        # Get policy-level details
        print(f"\nPolicy Details:")
        detail_query = """
        SELECT 
            ip.id AS policy_id,
            ip.brokerage_policy_id,
            ip.premium_amount AS policy_premium,
            ip.policy_effective_date,
            COALESCE(SUM(ac.revenue_realized), 0) AS commission_realized
        FROM crmp_issued_policies ip
        INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
        LEFT JOIN crmf_invoices inv ON inv.issued_policy_id = ip.id
        LEFT JOIN crmf_brokerage_commission bc ON bc.invoice_id = inv.id
        LEFT JOIN crmf_agent_commission ac ON ac.brokerage_commission_id = bc.id
        WHERE pb.sales_agent_id = %s
          AND ip.policy_effective_date >= '2025-12-01'
          AND ip.policy_effective_date <= '2025-12-10'
        GROUP BY ip.id, ip.brokerage_policy_id, ip.premium_amount, ip.policy_effective_date
        ORDER BY ip.policy_effective_date, ip.id;
        """
        
        policy_details = execute_query(detail_query, [agent_id])
        if policy_details:
            print(f"  Found {len(policy_details)} policy/policies:")
            for policy in policy_details:
                print(f"    - Policy #{policy['policy_id']}: {policy['brokerage_policy_id'] or 'N/A'}")
                print(f"      Premium: ${format_currency(policy['policy_premium'])}")
                print(f"      Date: {policy['policy_effective_date']}")
                print(f"      Commission: ${format_currency(policy['commission_realized'])}")
        else:
            print("  No policies found in the period")

if __name__ == "__main__":
    try:
        get_incentive_values()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

