-- =====================================================================
-- SQL Queries for DevOps: Update Policy Base Statuses
-- =====================================================================
-- Run these queries to automatically update policy statuses based on 
-- policy expiry dates and renewal periods
-- =====================================================================

-- =====================================================================
-- STEP 1: Ensure required statuses exist in core_status table
-- =====================================================================

-- Check if DUE_FOR_RENEWAL status exists, create if not
INSERT INTO core_status (name, description, type, module, color, sort_index)
SELECT 'DUE_FOR_RENEWAL', 
       'Policy is active but within the pre-defined period before expiry', 
       'policy_active', 
       'policy_status', 
       '#FFD700', 
       3
WHERE NOT EXISTS (
    SELECT 1 FROM core_status 
    WHERE name = 'DUE_FOR_RENEWAL' AND module = 'policy_status'
);

-- Check if EXPIRED status exists, create if not
INSERT INTO core_status (name, description, type, module, color, sort_index)
SELECT 'EXPIRED', 
       'Policy has passed its end date and was not renewed', 
       'policy_inactive', 
       'policy_status', 
       '#dc3545', 
       4
WHERE NOT EXISTS (
    SELECT 1 FROM core_status 
    WHERE name = 'EXPIRED' AND module = 'policy_status'
);

-- Check if ACTIVE status exists, create if not
INSERT INTO core_status (name, description, type, module, color, sort_index)
SELECT 'ACTIVE', 
       'Policy has been officially issued and is currently in force', 
       'policy_active', 
       'policy_status', 
       '#28a745', 
       2
WHERE NOT EXISTS (
    SELECT 1 FROM core_status 
    WHERE name = 'ACTIVE' AND module = 'policy_status'
);

-- =====================================================================
-- STEP 2: Get status IDs for use in updates
-- =====================================================================

SET @active_status_id = (SELECT id FROM core_status WHERE name = 'ACTIVE' AND module = 'policy_status');
SET @due_for_renewal_status_id = (SELECT id FROM core_status WHERE name = 'DUE_FOR_RENEWAL' AND module = 'policy_status');
SET @expired_status_id = (SELECT id FROM core_status WHERE name = 'EXPIRED' AND module = 'policy_status');

-- Verify status IDs were found
SELECT 
    @active_status_id AS active_status_id,
    @due_for_renewal_status_id AS due_for_renewal_status_id,
    @expired_status_id AS expired_status_id;

-- =====================================================================
-- STEP 3: Update EXPIRED policies
-- =====================================================================
-- Update policies that have passed their expiry date to EXPIRED status
-- Policy expiry date has already passed (expired)

UPDATE crmp_policy_base
SET status_id = @expired_status_id
WHERE policy_expiry_date < CURDATE()
  AND status_id IN (@active_status_id, @due_for_renewal_status_id)
  AND status_id IS NOT NULL;

-- Check how many policies were updated to EXPIRED
SELECT COUNT(*) AS expired_policies_updated
FROM crmp_policy_base
WHERE status_id = @expired_status_id;

-- =====================================================================
-- STEP 4: Update DUE_FOR_RENEWAL policies
-- =====================================================================
-- Update policies to DUE_FOR_RENEWAL when within 30 days BEFORE expiry
-- This means: TODAY is between (expiry_date - 30 days) and expiry_date
-- Renewal period: 30 days before expiry date

UPDATE crmp_policy_base
SET status_id = @due_for_renewal_status_id
WHERE policy_expiry_date >= CURDATE()
  AND DATE_SUB(policy_expiry_date, INTERVAL 30 DAY) <= CURDATE()
  AND status_id = @active_status_id
  AND status_id IS NOT NULL;

-- Check how many policies were updated to DUE_FOR_RENEWAL
SELECT COUNT(*) AS due_for_renewal_policies_updated
FROM crmp_policy_base
WHERE status_id = @due_for_renewal_status_id;

-- =====================================================================
-- STEP 5: Verification Queries
-- =====================================================================

-- View policy status distribution
SELECT 
    s.name AS status_name,
    s.color AS status_color,
    COUNT(pb.id) AS policy_count
FROM crmp_policy_base pb
LEFT JOIN core_status s ON s.id = pb.status_id
GROUP BY s.name, s.color
ORDER BY s.sort_index;

-- View policies that are expired
SELECT 
    pb.id AS policy_base_id,
    pb.policy_start_date,
    pb.policy_expiry_date,
    DATEDIFF(CURDATE(), pb.policy_expiry_date) AS days_expired,
    s.name AS status_name
FROM crmp_policy_base pb
LEFT JOIN core_status s ON s.id = pb.status_id
WHERE pb.policy_expiry_date < CURDATE()
ORDER BY pb.policy_expiry_date DESC
LIMIT 20;

-- View policies that are due for renewal (within 30 days before expiry)
SELECT 
    pb.id AS policy_base_id,
    pb.policy_start_date,
    pb.policy_expiry_date,
    DATEDIFF(pb.policy_expiry_date, CURDATE()) AS days_until_expiry,
    s.name AS status_name
FROM crmp_policy_base pb
LEFT JOIN core_status s ON s.id = pb.status_id
WHERE pb.policy_expiry_date >= CURDATE()
  AND DATE_SUB(pb.policy_expiry_date, INTERVAL 30 DAY) <= CURDATE()
ORDER BY pb.policy_expiry_date ASC
LIMIT 20;

-- =====================================================================
-- OPTIONAL: Create a scheduled event to run this automatically
-- =====================================================================
-- Uncomment and run this section if you want automatic daily updates

/*
DELIMITER $$

CREATE EVENT IF NOT EXISTS update_policy_statuses_daily
ON SCHEDULE EVERY 1 DAY
STARTS CURRENT_DATE + INTERVAL 1 DAY
DO
BEGIN
    DECLARE active_status INT;
    DECLARE due_renewal_status INT;
    DECLARE expired_status INT;
    
    -- Get status IDs
    SET active_status = (SELECT id FROM core_status WHERE name = 'ACTIVE' AND module = 'policy_status');
    SET due_renewal_status = (SELECT id FROM core_status WHERE name = 'DUE_FOR_RENEWAL' AND module = 'policy_status');
    SET expired_status = (SELECT id FROM core_status WHERE name = 'EXPIRED' AND module = 'policy_status');
    
    -- Update EXPIRED policies
    UPDATE crmp_policy_base
    SET status_id = expired_status
    WHERE policy_expiry_date < CURDATE()
      AND status_id IN (active_status, due_renewal_status)
      AND status_id IS NOT NULL;
    
    -- Update DUE_FOR_RENEWAL policies (30 days before expiry)
    UPDATE crmp_policy_base
    SET status_id = due_renewal_status
    WHERE policy_expiry_date >= CURDATE()
      AND DATE_SUB(policy_expiry_date, INTERVAL 30 DAY) <= CURDATE()
      AND status_id = active_status
      AND status_id IS NOT NULL;
END$$

DELIMITER ;

-- To check if the event was created successfully:
SHOW EVENTS WHERE Name = 'update_policy_statuses_daily';

-- To disable the event:
-- ALTER EVENT update_policy_statuses_daily DISABLE;

-- To enable the event:
-- ALTER EVENT update_policy_statuses_daily ENABLE;

-- To drop the event:
-- DROP EVENT IF EXISTS update_policy_statuses_daily;
*/

