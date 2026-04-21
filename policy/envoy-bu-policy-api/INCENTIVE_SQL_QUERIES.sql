-- ============================================================================
-- INCENTIVE CALCULATION SQL QUERIES
-- Based on Incentive Setup ID: 43
-- Name: "sales bonus - december"
-- Period: 2025-12-01 to 2025-12-10
-- ============================================================================

-- ============================================================================
-- QUERY 1: Get All Sales Agents (role_id = 2) with Policies in Period
-- ============================================================================
-- This query finds all agents who have role_id = 2 and have issued policies
-- within the incentive period (2025-12-01 to 2025-12-10)

SELECT DISTINCT
    cu.id AS agent_id,
    cu.display_name AS agent_name,
    cu.email AS agent_email,
    cu.role_id,
    COUNT(DISTINCT ip.id) AS policy_count
FROM core_users cu
INNER JOIN crmp_policy_base pb ON pb.sales_agent_id = cu.id
INNER JOIN crmp_issued_policies ip ON ip.policy_base_id = pb.id
WHERE cu.role_id = 2
  AND cu.deleted_at IS NULL
  AND ip.policy_effective_date >= '2025-12-01'
  AND ip.policy_effective_date <= '2025-12-10'
GROUP BY cu.id, cu.display_name, cu.email, cu.role_id
ORDER BY cu.id;

-- ============================================================================
-- QUERY 2: Get sum_of_premium_amount for Each Sales Agent
-- ============================================================================
-- This calculates the total premium amount for each agent in the period
-- This value must be >= 600,000 for the agent to be eligible

SELECT 
    cu.id AS agent_id,
    cu.display_name AS agent_name,
    cu.role_id,
    COALESCE(SUM(ip.premium_amount), 0) AS sum_of_premium_amount,
    COUNT(ip.id) AS policy_count,
    CASE 
        WHEN COALESCE(SUM(ip.premium_amount), 0) >= 600000 THEN 'ELIGIBLE'
        ELSE 'NOT ELIGIBLE'
    END AS premium_eligibility_status
FROM core_users cu
INNER JOIN crmp_policy_base pb ON pb.sales_agent_id = cu.id
INNER JOIN crmp_issued_policies ip ON ip.policy_base_id = pb.id
WHERE cu.role_id = 2
  AND cu.deleted_at IS NULL
  AND ip.policy_effective_date >= '2025-12-01'
  AND ip.policy_effective_date <= '2025-12-10'
GROUP BY cu.id, cu.display_name, cu.role_id
HAVING COALESCE(SUM(ip.premium_amount), 0) >= 600000  -- Only show eligible agents
ORDER BY sum_of_premium_amount DESC;

-- ============================================================================
-- QUERY 3: Get sum_of_agent_commission_realized for Each Sales Agent
-- ============================================================================
-- This calculates the total realized agent commission for each agent in the period
-- This value is used as the base for percentage calculation (3% of this amount)

SELECT 
    cu.id AS agent_id,
    cu.display_name AS agent_name,
    cu.role_id,
    COALESCE(SUM(ac.revenue_realized), 0) AS sum_of_agent_commission_realized,
    COUNT(DISTINCT ac.id) AS commission_record_count
FROM core_users cu
INNER JOIN crmp_policy_base pb ON pb.sales_agent_id = cu.id
INNER JOIN crmp_issued_policies ip ON ip.policy_base_id = pb.id
INNER JOIN crmf_invoices inv ON inv.issued_policy_id = ip.id
INNER JOIN crmf_brokerage_commission bc ON bc.invoice_id = inv.id
INNER JOIN crmf_agent_commission ac ON ac.brokerage_commission_id = bc.id
WHERE cu.role_id = 2
  AND cu.deleted_at IS NULL
  AND ip.policy_effective_date >= '2025-12-01'
  AND ip.policy_effective_date <= '2025-12-10'
GROUP BY cu.id, cu.display_name, cu.role_id
ORDER BY sum_of_agent_commission_realized DESC;

-- ============================================================================
-- QUERY 4: Complete Calculation for All Eligible Agents
-- ============================================================================
-- This query combines all checks and calculates the final incentive amount
-- Shows: agent info, premium amount, commission realized, eligibility, and incentive amount

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
    END AS incentive_amount,
    
    -- Reward Type Info
    3.0 AS reward_percentage,
    'sum_of_agent_commission_realized' AS incentive_base_field

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
  AND cu.deleted_at IS NULL
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

-- ============================================================================
-- QUERY 5: Get Values for a Specific Agent (Replace [AGENT_ID] with actual ID)
-- ============================================================================
-- Use this query to check a specific agent's values

-- Example: For Agent ID = 100
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
WHERE cu.id = 100  -- REPLACE 100 WITH ACTUAL AGENT ID
  AND cu.deleted_at IS NULL;

-- ============================================================================
-- QUERY 6: Detailed Breakdown for a Specific Agent (Policy-Level Details)
-- ============================================================================
-- Shows individual policies and commissions for an agent

SELECT 
    cu.id AS agent_id,
    cu.display_name AS agent_name,
    ip.id AS policy_id,
    ip.policy_number,
    ip.premium_amount AS policy_premium,
    ip.policy_effective_date,
    ac.id AS commission_id,
    ac.revenue_realized AS commission_realized,
    bc.id AS brokerage_commission_id,
    inv.id AS invoice_id,
    inv.invoice_number
FROM core_users cu
INNER JOIN crmp_policy_base pb ON pb.sales_agent_id = cu.id
INNER JOIN crmp_issued_policies ip ON ip.policy_base_id = pb.id
LEFT JOIN crmf_invoices inv ON inv.issued_policy_id = ip.id
LEFT JOIN crmf_brokerage_commission bc ON bc.invoice_id = inv.id
LEFT JOIN crmf_agent_commission ac ON ac.brokerage_commission_id = bc.id
WHERE cu.id = 100  -- REPLACE 100 WITH ACTUAL AGENT ID
  AND cu.role_id = 2
  AND cu.deleted_at IS NULL
  AND ip.policy_effective_date >= '2025-12-01'
  AND ip.policy_effective_date <= '2025-12-10'
ORDER BY ip.policy_effective_date, ip.id;

-- ============================================================================
-- QUERY 7: Summary Statistics for All Eligible Agents
-- ============================================================================

SELECT 
    COUNT(DISTINCT cu.id) AS total_eligible_agents,
    SUM(CASE 
        WHEN cu.role_id = 2 
         AND COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) >= 600000 
        THEN 1 
        ELSE 0 
    END) AS agents_meeting_criteria,
    SUM(CASE 
        WHEN cu.role_id = 2 
         AND COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) >= 600000 
        THEN ROUND((COALESCE(SUM(DISTINCT commission_data.revenue_realized), 0) * 3.0) / 100.0, 2)
        ELSE 0.00
    END) AS total_incentive_amount,
    AVG(CASE 
        WHEN cu.role_id = 2 
         AND COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) >= 600000 
        THEN COALESCE(SUM(DISTINCT premium_data.premium_amount), 0)
        ELSE NULL
    END) AS avg_premium_amount,
    AVG(CASE 
        WHEN cu.role_id = 2 
         AND COALESCE(SUM(DISTINCT premium_data.premium_amount), 0) >= 600000 
        THEN COALESCE(SUM(DISTINCT commission_data.revenue_realized), 0)
        ELSE NULL
    END) AS avg_commission_realized
FROM core_users cu
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
  AND cu.deleted_at IS NULL
  AND (
      premium_data.premium_amount IS NOT NULL 
      OR commission_data.revenue_realized IS NOT NULL
  )
GROUP BY cu.id;

-- ============================================================================
-- NOTES:
-- ============================================================================
-- 1. Replace [AGENT_ID] or 100 with actual agent IDs when testing
-- 2. Date range: '2025-12-01' to '2025-12-10' (adjust if needed)
-- 3. Premium threshold: 600000 (from performance_fields condition)
-- 4. Role filter: role_id = 2 (Sales Agent)
-- 5. Reward percentage: 3.0% (from reward_type_value)
-- 6. Base field: sum_of_agent_commission_realized (from incentive_base_field)
-- 7. Calculation formula: (sum_of_agent_commission_realized × 3.0) / 100
-- ============================================================================

