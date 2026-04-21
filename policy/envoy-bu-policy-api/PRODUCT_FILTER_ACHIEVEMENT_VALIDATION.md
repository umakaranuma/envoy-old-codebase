# Product Filter with Achievement Percentage - Validation Guide

## Scenario
**Condition**: If product is "marine liability" AND achievement percentage is between 90-100%, then bonus is 6% of brokerage commission.

## Potential Issues Identified

### ✅ Issue 1: Sales Targets Are NOT Product-Specific
**Problem**: 
- Sales targets table (`crmf_agent_sales_targets`) does NOT have a `product_id` field
- Targets are general (for all products combined), not product-specific
- When product filter is applied:
  - `sum_of_agent_achieved` = marine liability premiums only ✅ (filtered correctly)
  - `sum_of_agent_sales_target` = general target (all products) ⚠️ (NOT filtered)

**Impact**: 
- Achievement percentage = (marine liability achieved) / (general target)
- This may not be the intended calculation if you want product-specific achievement

**Solution Options**:
1. **If targets are meant to be general**: The calculation is correct - it compares product-specific achievement against general target
2. **If targets should be product-specific**: You need to add `product_id` to sales targets table, or use a different approach

### ✅ Issue 2: Brokerage Commission Base Field
**Status**: ✅ **WORKING CORRECTLY**
- Brokerage commission fields (`sum_of_brokerage_revenue_recognized`, `sum_of_brokerage_revenue_realized`) **DO support product filtering**
- When product filter is active, commission will be correctly filtered to marine liability only
- The 6% bonus calculation will use the correct (filtered) commission amount

## Enhanced Logging Added

The code now includes enhanced logging to detect and warn about these issues:

### 1. Product Filter Detection
- Logs when product filter is detected during aggregation
- Warns if sales target field cannot be filtered by product

### 2. Achievement Percentage Calculation
- Logs the calculated percentage with context
- Warns if product filter is active but target is general
- Shows: `(product-specific achieved) / (general target)`

### 3. Base Field Validation
- Checks if base field (commission) supports product filtering
- Warns if product filter is active but base field doesn't support it
- Confirms if base field correctly supports product filtering

## How to Verify

When running `run_all_incentive_awards`, check the logs for:

### ✅ Correct Setup (Product-Specific Commission)
```
Aggregated value for field 'sum_of_brokerage_revenue_recognized' (agent_id=X): 5000
  Verified: Query filtered by crmp_policy_base.sales_agent_id = X
  Applied filter condition: product (crmp_policy_base.product_id = marine_liability_id)
  Verified: Base field 'sum_of_brokerage_revenue_recognized' supports product filtering - commission is correctly filtered.
```

### ⚠️ Warning (Sales Target Not Product-Specific)
```
Aggregated value for field 'sum_of_agent_sales_target' (agent_id=X): 100000
  WARNING: Product filter (product=marine_liability_id) is active, but sales targets are NOT product-specific.
  This field cannot be filtered by product. The target value represents general target, not product-specific target.
```

### ⚠️ Warning (Achievement Calculation)
```
Calculated achievement_percentage (agent_id=X): (45000 / 100000) * 100 = 45.0%
  WARNING: Achievement percentage calculation with product filter:
    Product filter: marine_liability_id
    Achieved (filtered by product): 45000
    Target (NOT filtered by product - general target): 100000
    NOTE: Sales targets are not product-specific. This calculation compares
    product-specific achieved amount against general target, which may not be accurate.
```

## Recommendations

1. **Verify Business Logic**: Confirm if achievement should be:
   - Product-specific achieved vs. general target (current behavior)
   - Product-specific achieved vs. product-specific target (requires database changes)

2. **Use Correct Base Field**: Ensure `incentive_base_field` is a brokerage commission field that supports product filtering:
   - ✅ `sum_of_brokerage_revenue_recognized`
   - ✅ `sum_of_brokerage_revenue_realized`
   - ✅ `sum_of_agent_commission_recognized`
   - ✅ `sum_of_agent_commission_realized`

3. **Monitor Logs**: Check logs for warnings about product filter compatibility

## Example Setup

```json
{
  "name": "Marine Liability Achievement Bonus",
  "performance_fields": {
    "logic": "AND",
    "conditions": [
      {
        "field": "product",
        "operator": "=",
        "value": "marine_liability_product_id"
      },
      {
        "field": "achievement_percentage",
        "operator": "between",
        "value": [90, 100]
      }
    ]
  },
  "reward_type": "percentage",
  "reward_type_id": 2,
  "reward_type_value": 6,
  "incentive_base_field": "sum_of_brokerage_revenue_recognized",
  "repeation_type": "Monthly"
}
```

This setup will:
- ✅ Filter by marine liability product
- ✅ Calculate achievement: (marine liability achieved) / (general target)
- ✅ Calculate 6% bonus from marine liability commission only

