# Incentive Calculation Fix - Date Filter Issue

## Problem Identified

**Incentive Setup ID: 43** - "sales bonus - december"
- **Expected Result**: $289.62
- **Actual Result**: $728.78
- **Difference**: The calculation was using **$24,292.68** instead of **$9,653.85** for commission realized

## Root Cause

The date filter was **NOT being applied** to `sum_of_agent_commission_realized` during aggregation, causing the system to sum **ALL commissions** for the agent instead of just those in the period (Dec 1-10, 2025).

### Why This Happened

1. The `sum_of_agent_commission_realized` registry entry in `performance_field_registry.py` has:
   - `base_table`: `crmf_agent_commission`
   - `filters`: `["status", "product", "native_product", "insurer", "risk_type", "role", "agent_id"]`
   - **Missing**: `policy_effective_date` or `invoice_date` in the filters list

2. The date filtering logic in `aggregate_performance_data()` (line 688-694) only applies date filters if the date field is in `registry.get("filters", [])`.

3. Since `policy_effective_date` was not in the filters list, **no date filter was applied**, causing the query to sum all commissions for the agent regardless of date.

## The Fix

Added a **fallback mechanism** in `incentive_utils.py` (lines 695-710) that:

1. Checks if a date field was found in the registry's filters
2. If not found, checks if `crmp_issued_policies` is in the join chain
3. If found, applies the date filter to `crmp_issued_policies.policy_effective_date`

This ensures that commission-based aggregations always filter by the policy effective date when available through joins.

## Verification

### Test Results:

**Without Date Filter (Incorrect)**:
- Commission Realized: $24,292.68
- Incentive (3%): $728.78 ❌

**With Date Filter (Correct)**:
- Commission Realized: $9,653.85
- Incentive (3%): $289.62 ✅

## Code Changes

**File**: `envoy_bu_policy_api/finance/controllers/utils/incentive_utils.py`

**Location**: Lines 686-710 (in `aggregate_performance_data` function)

**Change**: Added fallback date filtering logic that checks for `crmp_issued_policies` in joins and applies `policy_effective_date` filter.

## Impact

This fix ensures that:
1. All commission-based incentive calculations properly filter by the incentive period
2. The calculation matches the expected values based on the date range
3. Other incentive setups using commission fields will also benefit from this fix

## Testing

Run the test script to verify:
```bash
python test_incentive_calculation.py
```

Or test the actual incentive calculation:
```bash
# The fix will be applied automatically when incentives/run-all is called
# The next calculation should show $289.62 instead of $728.78
```

