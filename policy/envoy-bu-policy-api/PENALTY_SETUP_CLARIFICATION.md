# Penalty Setup Clarification - 5% Hold from Commission

## Your Scenario
**If sales target achievement is below 100%, 5% will be held from the commission income.**

## ✅ Correct Setup

### Important: Two Different Places

1. **CONDITION** (when to apply): Check if achievement < 100%
2. **REWARD_TYPE_VALUE** (how much to deduct): Put `-5` (negative value)

### ❌ Common Mistake
**DO NOT put -5% in the condition!** The condition is for checking WHEN to apply, not HOW MUCH.

## Complete Setup Example

```json
POST /api/incentive-setups

{
    "name": "Below Target Achievement Penalty",
    "description": "5% deduction from commission if achievement below 100%",
    "performance_fields": {
        "logic": "AND",
        "conditions": [
            {
                "field": "sum_of_agent_achieved",
                "operator": "<",
                "value": "sum_of_agent_sales_target",
                "label": "Achievement Below 100%"
            }
        ]
    },
    "reward_type": "percentage",
    "reward_type_id": 2,
    "reward_type_value": "-5",
    "incentive_base_field": "sum_of_agent_commission_recognized",
    "repeation_type": "Monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
```

## How It Works Step by Step

### Step 1: Condition Check
- **Field**: `sum_of_agent_achieved`
- **Operator**: `<` (less than)
- **Value**: `sum_of_agent_sales_target` (field reference)
- **Meaning**: Check if achieved < target (i.e., achievement < 100%)

**Example**:
- Achieved: 80,000
- Target: 100,000
- Condition: `80000 < 100000` → **TRUE** ✅ (achievement is below 100%)

### Step 2: Penalty Calculation (if condition is TRUE)
- **reward_type_value**: `-5` (negative value = penalty)
- **incentive_base_field**: `sum_of_agent_commission_recognized` (commission income)
- **Calculation**: `commission × 5% = deduction_amount`

**Example**:
- Commission: 10,000
- Calculation: `10,000 × 5% = 500`
- **Result**: `incentive_amount = -500` (stored as negative)

### Step 3: Effect
- Agent's commission is **reduced by 500**
- Agent receives: `10,000 - 500 = 9,500`

## Key Points

### ✅ Correct Setup

| Field | Value | Purpose |
|-------|-------|---------|
| **Condition Field** | `sum_of_agent_achieved` | What to check |
| **Condition Operator** | `<` | Less than |
| **Condition Value** | `sum_of_agent_sales_target` | Compare against target |
| **reward_type_value** | `-5` | **5% deduction (negative = penalty)** |
| **incentive_base_field** | `sum_of_agent_commission_recognized` | Commission to deduct from |

### ❌ Wrong Setup (Common Mistakes)

1. **Putting -5 in condition value**:
   ```json
   {
       "field": "sum_of_agent_achieved",
       "operator": "<",
       "value": "-5"  // ❌ WRONG! This doesn't make sense
   }
   ```

2. **Using positive value for penalty**:
   ```json
   {
       "reward_type_value": "5"  // ❌ WRONG! This is a reward, not a penalty
   }
   ```

3. **Missing incentive_base_field**:
   ```json
   {
       "reward_type": "percentage",
       "reward_type_value": "-5"
       // ❌ Missing incentive_base_field - system won't know what to calculate 5% from
   }
   ```

## Verification Checklist

When you create the setup, verify:

- [ ] **Condition checks achievement < target**: `sum_of_agent_achieved < sum_of_agent_sales_target`
- [ ] **reward_type_value is NEGATIVE**: `-5` (not `5`)
- [ ] **incentive_base_field is commission field**: `sum_of_agent_commission_recognized` or similar
- [ ] **reward_type is percentage**: `"percentage"` or `reward_type_id: 2`

## How to Test

1. **Create the setup** with the JSON above
2. **Run incentive calculation**: `POST /api/incentives/run-all`
3. **Check the logs** for:
   ```
   Penalty calculation (agent_id=X): 10000 * -5% / 100 = -500
   This is a PENALTY (negative reward_type_value=-5), will be converted to negative amount
   ```
4. **Verify the result**:
   - Check `crmf_incentives` table
   - `incentive_amount` should be **negative** (e.g., `-500`)
   - `agent_id` should be correct
   - `performance_metric_value` should match `incentive_amount`

## Summary

**Q: Should I put -5% in the condition?**

**A: NO!** 
- **Condition**: Use `sum_of_agent_achieved < sum_of_agent_sales_target` (checks if achievement < 100%)
- **reward_type_value**: Use `-5` (negative value = 5% deduction)

**The system will:**
1. ✅ Check if achievement < 100% (condition)
2. ✅ If true, calculate 5% of commission (from `reward_type_value: -5`)
3. ✅ Store as negative amount (e.g., `-500`)
4. ✅ Deduct from agent's commission

**It works correctly!** Just make sure:
- Condition checks achievement < target
- reward_type_value is **negative** (`-5`)
- incentive_base_field is the commission field

