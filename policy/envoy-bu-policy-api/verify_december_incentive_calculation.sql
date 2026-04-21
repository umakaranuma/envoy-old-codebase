-- ============================================================================
-- VERIFY DECEMBER INCENTIVE CALCULATION
-- Scenario: If December target is achieved, agents get 1% of brokerage commission (recognized amount)
-- ============================================================================

-- This query verifies the correct calculation for December incentive
-- It checks:
-- 1. If agent achieved December target
-- 2. Calculates 1% of brokerage commission recognized amount
-- 3. Compares with current incentive records in the system

-- ============================================================================
-- QUERY: Complete Verification for December Incentive
-- ============================================================================

SELECT 
    cu.id AS agent_id,
    cu.display_name AS agent_name,
    cu.email AS agent_email,
    cu.role_id,
    
    -- December Target Information
    COALESCE(ast.target_amount, 0) AS december_target,
    ast.month AS target_month,
    ast.year AS target_year,
    
    -- December Achievement (premium amount in December)
    COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) AS december_achieved,
    
    -- Target Achievement Status
    CASE 
        WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
             AND COALESCE(ast.target_amount, 0) > 0
        THEN 'TARGET ACHIEVED'
        ELSE 'TARGET NOT ACHIEVED'
    END AS target_status,
    
    -- Brokerage Commission Recognized (for December period)
    COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) AS sum_of_brokerage_revenue_recognized,
    
    -- Correct Incentive Calculation: 1% of brokerage commission recognized (if target achieved)
    CASE 
        WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
             AND COALESCE(ast.target_amount, 0) > 0
        THEN ROUND((COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) * 1.0) / 100.0, 2)
        ELSE 0.00
    END AS correct_incentive_amount,
    
    -- Current Incentive Record (if exists)
    ci.incentive_amount AS current_incentive_amount,
    ci.id AS current_incentive_id,
    
    -- Difference
    CASE 
        WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
             AND COALESCE(ast.target_amount, 0) > 0
        THEN ROUND((COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) * 1.0) / 100.0, 2) 
             - COALESCE(ci.incentive_amount, 0)
        ELSE 0.00 - COALESCE(ci.incentive_amount, 0)
    END AS difference,
    
    -- Status
    CASE 
        WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
             AND COALESCE(ast.target_amount, 0) > 0
             AND ABS(ROUND((COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) * 1.0) / 100.0, 2) 
                 - COALESCE(ci.incentive_amount, 0)) < 0.01
        THEN 'CORRECT'
        WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
             AND COALESCE(ast.target_amount, 0) > 0
             AND ABS(ROUND((COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) * 1.0) / 100.0, 2) 
                 - COALESCE(ci.incentive_amount, 0)) >= 0.01
        THEN 'INCORRECT - NEEDS FIX'
        WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) < COALESCE(ast.target_amount, 0)
             AND ci.incentive_amount IS NOT NULL
             AND ci.incentive_amount > 0
        THEN 'INCORRECT - SHOULD BE 0'
        ELSE 'OK'
    END AS verification_status

FROM core_users cu

-- Get December Target (month = 12)
LEFT JOIN crmf_agent_sales_targets ast ON ast.agent_id = cu.id
    AND ast.month = 12
    AND ast.year = 2025  -- Adjust year as needed
    AND ast.period_type = 'monthly'
    AND ast.deleted_at IS NULL

-- Get December Achievement (premium amount in December)
LEFT JOIN (
    SELECT 
        pb.sales_agent_id,
        SUM(ip.premium_amount) AS premium_amount
    FROM crmp_issued_policies ip
    INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
    WHERE ip.policy_effective_date >= '2025-12-01'
      AND ip.policy_effective_date <= '2025-12-31'
    GROUP BY pb.sales_agent_id
) dec_premium ON dec_premium.sales_agent_id = cu.id

-- Get Brokerage Commission Recognized (for December period)
LEFT JOIN (
    SELECT 
        pb.sales_agent_id,
        SUM(bc.revenue_recognized) AS revenue_recognized
    FROM crmf_brokerage_commission bc
    INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
    INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
    INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
    WHERE ip.policy_effective_date >= '2025-12-01'
      AND ip.policy_effective_date <= '2025-12-31'
    GROUP BY pb.sales_agent_id
) brokerage_recognized ON brokerage_recognized.sales_agent_id = cu.id

-- Get Current Incentive Record (for incentive setup ID 43 - adjust as needed)
LEFT JOIN crmf_incentives ci ON ci.agent_id = cu.id
    AND ci.incentive_setup_id = 43  -- Adjust incentive setup ID as needed
    AND ci.deleted_at IS NULL

WHERE cu.role_id = 2  -- Sales agents only
  AND (
      dec_premium.premium_amount IS NOT NULL 
      OR brokerage_recognized.revenue_recognized IS NOT NULL
      OR ast.target_amount IS NOT NULL
  )

GROUP BY 
    cu.id, 
    cu.display_name, 
    cu.email, 
    cu.role_id,
    ast.target_amount,
    ast.month,
    ast.year,
    ci.incentive_amount,
    ci.id

HAVING 
    -- Only show agents with December target OR December activity
    (ast.target_amount IS NOT NULL OR december_achieved > 0)

ORDER BY 
    verification_status DESC,
    correct_incentive_amount DESC,
    cu.display_name;

-- ============================================================================
-- SUMMARY QUERY: Count of Correct vs Incorrect Calculations
-- ============================================================================

SELECT 
    COUNT(*) AS total_agents,
    SUM(CASE WHEN verification_status = 'CORRECT' THEN 1 ELSE 0 END) AS correct_count,
    SUM(CASE WHEN verification_status LIKE 'INCORRECT%' THEN 1 ELSE 0 END) AS incorrect_count,
    SUM(CASE WHEN verification_status = 'OK' THEN 1 ELSE 0 END) AS ok_count,
    SUM(ABS(difference)) AS total_difference_amount
FROM (
    -- Use the main query above as subquery
    SELECT 
        cu.id AS agent_id,
        COALESCE(ast.target_amount, 0) AS december_target,
        COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) AS december_achieved,
        COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) AS sum_of_brokerage_revenue_recognized,
        CASE 
            WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
                 AND COALESCE(ast.target_amount, 0) > 0
            THEN ROUND((COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) * 1.0) / 100.0, 2)
            ELSE 0.00
        END AS correct_incentive_amount,
        ci.incentive_amount AS current_incentive_amount,
        CASE 
            WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
                 AND COALESCE(ast.target_amount, 0) > 0
            THEN ROUND((COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) * 1.0) / 100.0, 2) 
                 - COALESCE(ci.incentive_amount, 0)
            ELSE 0.00 - COALESCE(ci.incentive_amount, 0)
        END AS difference,
        CASE 
            WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
                 AND COALESCE(ast.target_amount, 0) > 0
                 AND ABS(ROUND((COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) * 1.0) / 100.0, 2) 
                     - COALESCE(ci.incentive_amount, 0)) < 0.01
            THEN 'CORRECT'
            WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) >= COALESCE(ast.target_amount, 0)
                 AND COALESCE(ast.target_amount, 0) > 0
                 AND ABS(ROUND((COALESCE(SUM(DISTINCT brokerage_recognized.revenue_recognized), 0) * 1.0) / 100.0, 2) 
                     - COALESCE(ci.incentive_amount, 0)) >= 0.01
            THEN 'INCORRECT - NEEDS FIX'
            WHEN COALESCE(SUM(DISTINCT dec_premium.premium_amount), 0) < COALESCE(ast.target_amount, 0)
                 AND ci.incentive_amount IS NOT NULL
                 AND ci.incentive_amount > 0
            THEN 'INCORRECT - SHOULD BE 0'
            ELSE 'OK'
        END AS verification_status
    FROM core_users cu
    LEFT JOIN crmf_agent_sales_targets ast ON ast.agent_id = cu.id
        AND ast.month = 12
        AND ast.year = 2025
        AND ast.period_type = 'monthly'
        AND ast.deleted_at IS NULL
    LEFT JOIN (
        SELECT 
            pb.sales_agent_id,
            SUM(ip.premium_amount) AS premium_amount
        FROM crmp_issued_policies ip
        INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
        WHERE ip.policy_effective_date >= '2025-12-01'
          AND ip.policy_effective_date <= '2025-12-31'
        GROUP BY pb.sales_agent_id
    ) dec_premium ON dec_premium.sales_agent_id = cu.id
    LEFT JOIN (
        SELECT 
            pb.sales_agent_id,
            SUM(bc.revenue_recognized) AS revenue_recognized
        FROM crmf_brokerage_commission bc
        INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
        INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
        INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
        WHERE ip.policy_effective_date >= '2025-12-01'
          AND ip.policy_effective_date <= '2025-12-31'
        GROUP BY pb.sales_agent_id
    ) brokerage_recognized ON brokerage_recognized.sales_agent_id = cu.id
    LEFT JOIN crmf_incentives ci ON ci.agent_id = cu.id
        AND ci.incentive_setup_id = 43
        AND ci.deleted_at IS NULL
    WHERE cu.role_id = 2
      AND (
          dec_premium.premium_amount IS NOT NULL 
          OR brokerage_recognized.revenue_recognized IS NOT NULL
          OR ast.target_amount IS NOT NULL
      )
    GROUP BY 
        cu.id,
        ast.target_amount,
        ci.incentive_amount,
        ci.id
    HAVING 
        (ast.target_amount IS NOT NULL OR december_achieved > 0)
) AS verification_data;

