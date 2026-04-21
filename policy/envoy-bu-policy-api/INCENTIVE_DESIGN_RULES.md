# Incentive System Design Rules & Architecture Decisions

This document explains the **intentional design rules** and architectural decisions in the incentive system. These are **not bugs** - they are deliberate choices to ensure financial accuracy and data integrity.

---

## 🔴 Design Rule 1: Product Filter + General Target Comparison is BLOCKED

### Why This Rule Exists

When a product filter is active, the system correctly filters `sum_of_agent_achieved` to only include that product's premiums. However, `sum_of_agent_sales_target` is a **general target** (not product-specific).

**Mathematical Invalidity**:
```
Product Filter: Private Car Insurance (product_id=28)
sum_of_agent_achieved = 500,000 (only Private Car Insurance premiums)
sum_of_agent_sales_target = 1,000,000 (general target for ALL products)

Condition: sum_of_agent_achieved >= sum_of_agent_sales_target
Result: 500K >= 1M → FALSE (mathematically invalid comparison)
```

Comparing product-specific achievement against general target is **mathematically wrong** because:
- The scales don't match (product-specific vs general)
- It's like comparing "apples sold" against "total fruit target"
- Financial systems require accurate, comparable metrics

### What the System Does

The hardened evaluator **intentionally blocks** this comparison with a clear error message:

```
❌ BLOCKED: Product filter is active, but comparing product-specific achieved against general target
  Reason: Cannot compare product-specific achievement with general target - data scale mismatch
  ✅ Solution Options:
    1. Remove product filter if you want to compare against general target
    2. Add product-specific targets in database (e.g., agent_product_sales_targets table)
    3. Use pure volume-based condition instead: sum_of_agent_achieved >= 500000 (no target comparison)
```

### ✅ Solution Options

**OPTION A (Recommended for Finance-grade system)**:
Add product-specific targets table:
```sql
CREATE TABLE agent_product_sales_targets (
    agent_id INT,
    product_id INT,
    month INT,
    year INT,
    target_amount DECIMAL(15,2),
    PRIMARY KEY (agent_id, product_id, month, year)
);
```

Then compare:
```
product_achieved >= product_target
```

**OPTION B**:
Remove product condition from setups that compare to target:
```json
{
  "field": "sum_of_agent_achieved",
  "operator": ">=",
  "value": "sum_of_agent_sales_target"
}
```

**OPTION C**:
Keep product filter, but use fixed volume comparison (no target):
```json
{
  "logic": "AND",
  "conditions": [
    {"field": "product", "operator": "=", "value": 28},
    {"field": "sum_of_agent_achieved", "operator": ">=", "value": "500000"}
  ]
}
```

### This Applies To

- Individual agent incentives
- Team-based incentives
- Any setup combining product filter + target comparison

---

## 🔴 Design Rule 2: Filter-Only Fields Cannot Be Aggregated

### Why This Rule Exists

Certain fields are **filter-only** - they're used in WHERE clauses to filter data, not as aggregatable metrics. Attempting to aggregate them causes SQL `ONLY_FULL_GROUP_BY` errors.

### Filter-Only Fields

These fields are **NEVER aggregated** in SQL queries:
- `product` / `product_id` / `native_product`
- `role` / `role_id` / `user_role`
- `team_role`
- `agent_id`
- `insurer`
- `risk_type`

### What Happens

**Before Fix**: SQL error when bulk aggregating:
```sql
SELECT agent_id, product_id FROM ...
GROUP BY agent_id
-- ERROR: Expression #2 (product_id) is not in GROUP BY clause
```

**After Fix**: Filter fields are automatically skipped before aggregation:
```python
NON_AGGREGATABLE_FIELDS = {
    "product", "native_product", "product_id",
    "team_role", "role", "role_id", "user_role",
    "agent_id", "insurer", "risk_type"
}

# Filter out before processing
aggregatable_fields = [f for f in fields if f not in NON_AGGREGATABLE_FIELDS]
```

### How Filter Fields Are Used

Filter fields are applied in **WHERE clauses only**:
```sql
SELECT agent_id, SUM(premium_amount) 
FROM crmp_issued_policies
JOIN crmp_policy_base ON ...
WHERE crmp_policy_base.product_id = 28  -- Filter applied here
GROUP BY agent_id
```

They are **never** in SELECT or GROUP BY clauses.

---

## 🔴 Design Rule 3: Zero-Value Incentives Are Skipped

### Why This Rule Exists

Creating incentives with 0.00 value is:
- Meaningless in financial systems
- Creates noise in reports
- Wastes database storage
- Can cause confusion in calculations

### What the System Does

The system **intentionally skips** creating incentives when:
- Percentage reward type but base field value is 0
- Calculated reward amount is 0

**Example**:
```
Reward type: Percentage (2%)
Base field: sum_of_agent_commission_recognized = 0.0
Calculated reward: 0.0
Result: ⏭️ SKIPPED (prevents creating meaningless 0-value incentives)
```

### If You Need 0.00 Incentives

If you have a business requirement to create 0.00 incentives (not recommended), you would need to:
1. Remove the skip condition in the code
2. Document why 0.00 incentives are needed
3. Ensure reports handle 0.00 values correctly

**Recommendation**: Keep the skip behavior - it's correct for financial systems.

---

## 🔴 Design Rule 4: Zero or Missing Targets Always Fail

### Why This Rule Exists

In finance, a zero or missing target means:
- No target has been set
- The incentive condition cannot be evaluated
- Financial safety requires explicit targets

### What the System Does

The hardened evaluator **blocks** any comparison against zero or missing targets:

```
❌ BLOCKED: Target is zero or missing for target-based comparison
  Target field: sum_of_agent_sales_target = None (missing)
  Reason: In finance, zero target means no target set - incentive condition must fail
  Business Rule: Any comparison against target requires target > 0
```

This applies to:
- `sum_of_agent_achieved >= sum_of_agent_sales_target` (when target is 0 or missing)
- `sum_of_team_achieved >= sum_of_team_sales_target` (when target is 0 or missing)
- Percentage-type conditions on achievement fields

### Exception

Pure volume-based conditions (no target comparison) are allowed:
```json
{
  "field": "sum_of_agent_achieved",
  "operator": ">=",
  "value": "500000"
}
```
This doesn't require a target because it's comparing against a fixed threshold.

---

## 📋 Recommended Schema Enhancement: Period-Based Duplicate Prevention

### Current State

The system uses `commission_date` as a fallback when `period_start`/`period_end` columns don't exist:

```python
# Current fallback logic
if period_start/period_end columns exist:
    use period-based duplicate check
else:
    use commission_date BETWEEN start AND end  # Weak fallback
```

### Issue

This is a **weak duplicate prevention mechanism**:
- `commission_date` may change
- Overlapping periods can still create duplicates
- No database-level constraint

### Recommended Fix

Add proper period columns and unique constraint:

```sql
-- Add period columns
ALTER TABLE crmf_incentives 
ADD COLUMN period_start DATE,
ADD COLUMN period_end DATE;

-- Add unique constraint for bulletproof duplicate prevention
ALTER TABLE crmf_incentives
ADD CONSTRAINT unique_incentive_period 
UNIQUE (incentive_setup_id, agent_id, period_start, period_end);
```

### Benefits

- ✅ Bulletproof duplicate prevention at database level
- ✅ Clear period tracking for each incentive
- ✅ Better audit trail
- ✅ No dependency on `commission_date` which may change
- ✅ Database enforces uniqueness (can't be bypassed)

### Migration Path

1. Add columns (nullable initially)
2. Backfill data from existing `commission_date` or setup periods
3. Add unique constraint
4. Update code to always use period columns

**Note**: This is a **recommendation**, not a critical bug. The current fallback mechanism works but is less robust.

---

## Summary

| Rule | Status | Type |
|------|--------|------|
| Product filter + target blocking | ✅ Intentional | Design Rule |
| Filter fields not aggregated | ✅ Fixed | Bug Fix |
| Zero-value incentive skipping | ✅ Intentional | Design Rule |
| Zero target blocking | ✅ Intentional | Design Rule |
| Period-based duplicate prevention | 📋 Recommended | Schema Enhancement |

All blocking behaviors are **intentional** to ensure financial accuracy and data integrity. The system is working as designed.

