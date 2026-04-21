# December Incentive Calculation Fix

## Issue Description

According to the requirement:
- **If the December target is achieved, agents get an extra 1% of the brokerage commission (recognized amount)**

The current incentive calculation in the system appears to be incorrect.

## Expected Calculation

1. **Check if agent achieved December target:**
   - Get agent's December sales target from `crmf_agent_sales_targets` (month = 12)
   - Get agent's December achievement (premium amount in December) from `crmp_issued_policies`
   - Compare: `december_achieved >= december_target`

2. **If target is achieved, calculate incentive:**
   - Get brokerage commission recognized amount for December period
   - Calculate: `(sum_of_brokerage_revenue_recognized × 1.0) / 100.0`
   - This is the correct incentive amount

## Current Issue

The system may be:
- Using wrong base field (e.g., `sum_of_agent_commission_realized` instead of `sum_of_brokerage_revenue_recognized`)
- Using wrong percentage (e.g., 3% instead of 1%)
- Not checking target achievement correctly
- Using wrong date filter (e.g., `invoice_date` instead of `policy_effective_date` for December period)

## Verification Query

Use the SQL query in `verify_december_incentive_calculation.sql` to:
1. Check which agents achieved December target
2. Calculate the correct incentive amount (1% of brokerage commission recognized)
3. Compare with current incentive records in the system
4. Identify discrepancies

## How to Run Verification

1. **Connect to your database**
2. **Run the verification query:**
   ```sql
   -- Open verify_december_incentive_calculation.sql and run the main query
   ```

3. **Check the results:**
   - `verification_status = 'CORRECT'` → Calculation is correct
   - `verification_status = 'INCORRECT - NEEDS FIX'` → Calculation is wrong, needs fixing
   - `verification_status = 'INCORRECT - SHOULD BE 0'` → Agent didn't achieve target but has incentive

## Fixing the Incentive Setup

If the incentive setup (ID 43) needs to be corrected:

### Option 1: Update Incentive Setup Configuration

Update the incentive setup in the database:

```sql
UPDATE crmf_incentive_setups
SET 
    incentive_base_field = 'sum_of_brokerage_revenue_recognized',
    reward_type_value = '1.0',  -- 1% instead of 3%
    reward_type_id = 2  -- Percentage type
WHERE id = 43;  -- Adjust ID as needed
```

### Option 2: Update Performance Fields to Include Target Check

The performance_fields JSON should include a condition to check if target is achieved:

```json
{
    "logic": "AND",
    "conditions": [
        {
            "field": "sum_of_agent_achieved",
            "operator": ">=",
            "value": "sum_of_agent_sales_target",
            "label": "December Target Achieved"
        },
        {
            "field": "role",
            "operator": "=",
            "value": "2",
            "label": "Sales Agent"
        }
    ]
}
```

### Option 3: Ensure Date Filter Uses Policy Effective Date

For December incentive, the date filter should use `policy_effective_date` to match December policies:

- The registry entry for `sum_of_brokerage_revenue_recognized` currently has `invoice_date` in filters
- The fallback logic in `aggregate_performance_data()` should use `policy_effective_date` when available
- Verify that the date filter is correctly applied to December period (2025-12-01 to 2025-12-31)

## Key Points

1. **Base Field**: Must be `sum_of_brokerage_revenue_recognized` (not `sum_of_agent_commission_realized`)
2. **Percentage**: Must be 1% (not 3%)
3. **Target Check**: Must verify that `sum_of_agent_achieved >= sum_of_agent_sales_target` for December
4. **Date Filter**: Should use `policy_effective_date` for December period (2025-12-01 to 2025-12-31)

## After Fixing

1. **Re-run the incentive calculation:**
   - Delete existing incorrect incentive records for setup ID 43
   - Run the incentive calculation again via API: `POST /api/incentives/run-all`

2. **Verify the results:**
   - Run the verification query again
   - All agents should show `verification_status = 'CORRECT'`

3. **Check specific agents:**
   - Use the verification query to check individual agents
   - Compare `correct_incentive_amount` with `current_incentive_amount`
   - They should match (difference < 0.01)

## Example Calculation

**Agent A:**
- December Target: 600,000
- December Achieved: 750,000 ✅ (Target achieved)
- Brokerage Commission Recognized (December): 50,000
- **Correct Incentive**: 50,000 × 1% = 500.00

**Agent B:**
- December Target: 600,000
- December Achieved: 500,000 ❌ (Target not achieved)
- Brokerage Commission Recognized (December): 40,000
- **Correct Incentive**: 0.00 (target not achieved)

## Files

- `verify_december_incentive_calculation.sql` - SQL query to verify calculations
- `DECEMBER_INCENTIVE_CALCULATION_FIX.md` - This document

