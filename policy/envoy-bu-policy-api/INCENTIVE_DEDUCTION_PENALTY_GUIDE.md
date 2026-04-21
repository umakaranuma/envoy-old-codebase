# Incentive Deduction/Penalty Guide

## How to Indicate a Deduction in Incentive Setup

### Answer: YES, `-5%` will work!

The system automatically detects negative `reward_type_value` and treats it as a penalty/deduction.

## Two Ways to Indicate Deduction

### Method 1: Negative reward_type_value (Recommended)

**Use negative value in `reward_type_value`**

```json
{
    "reward_type": "percentage",
    "reward_type_id": 2,
    "reward_type_value": "-5"
}
```

**How it works:**
- System detects `reward_type_value < 0`
- Calculates: `commission × 5% = deduction_amount`
- Stores as **negative** in `incentive_amount`: `-500`
- Reduces agent's commission

### Method 2: is_penalty flag (Alternative)

**Use positive value with `is_penalty` flag**

```json
{
    "reward_type": "percentage",
    "reward_type_id": 2,
    "reward_type_value": "5",
    "is_penalty": true
}
```

**Note**: The `is_penalty` flag needs to be stored in the database. Check if your model supports it.

## Complete Payload Examples

### Example 1: Percentage Deduction (5% Penalty)

```json
POST /api/incentive-setups

{
    "name": "Target Achievement Penalty",
    "description": "5% deduction if achievement below 100%",
    "performance_fields": {
        "logic": "AND",
        "conditions": [
            {
                "field": "sum_of_agent_achieved",
                "operator": "<",
                "value": "sum_of_agent_sales_target",
                "label": "Achievement Below Target"
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

**How it works:**
- Condition: `sum_of_agent_achieved < sum_of_agent_sales_target`
- If true: Calculate 5% of `sum_of_agent_commission_recognized`
- Result: Negative amount (e.g., `-500` if commission is 10,000)
- Effect: Reduces agent's commission by 500

### Example 2: Fixed Amount Deduction

```json
{
    "name": "Low Performance Penalty",
    "description": "Fixed 1000 deduction for low premium",
    "performance_fields": {
        "logic": "AND",
        "conditions": [
            {
                "field": "sum_of_premium_amount",
                "operator": "<",
                "value": "500000",
                "label": "Premium Below 500K"
            }
        ]
    },
    "reward_type": "fixed",
    "reward_type_id": 1,
    "reward_type_value": "-1000",
    "incentive_base_field": "sum_of_premium_amount",
    "repeation_type": "Monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
```

**How it works:**
- Condition: `sum_of_premium_amount < 500000`
- If true: Fixed deduction of 1000
- Result: `incentive_amount = -1000`
- Effect: Reduces agent's commission by 1000

### Example 3: Target Achievement Deduction (Your Scenario)

**Scenario**: If sales target achievement is below 100%, hold 5% from commission income

```json
{
    "name": "Below Target Achievement Penalty",
    "description": "5% deduction if achievement below 100%",
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

**Calculation Example:**
- Agent Commission: 10,000
- Achievement: 80% (below 100%)
- Condition: `80000 < 100000` → **True**
- Deduction: `10,000 × 5% = 500`
- `incentive_amount`: `-500` (stored as negative)
- Agent receives: `10,000 - 500 = 9,500`

## How the System Detects Penalties

The code automatically detects penalties:

```python
# From incentive_utils.py lines 1981-1992
is_penalty = incentive_setup.get("is_penalty", False)
# Also check if reward_type_value is negative (indicates penalty)
if reward_type_value and float(reward_type_value) < 0:
    is_penalty = True

if is_penalty:
    # Make the reward amount negative for penalties
    reward_amount = -abs(reward_amount)
    print(f"Penalty incentive: Converting to negative amount: {reward_amount}")
```

## Key Points

### ✅ DO Use Negative Values

- **Percentage deduction**: `"reward_type_value": "-5"` (5% deduction)
- **Fixed deduction**: `"reward_type_value": "-1000"` (1000 deduction)

### ❌ DON'T Use Positive Values for Deductions

- ❌ `"reward_type_value": "5"` with `reward_type: "percentage"` → This is a **reward**, not a deduction
- ✅ `"reward_type_value": "-5"` with `reward_type: "percentage"` → This is a **deduction**

## Comparison: Reward vs Deduction

### Reward (Positive Value)

```json
{
    "reward_type": "percentage",
    "reward_type_id": 2,
    "reward_type_value": "5"
}
```
- Result: `incentive_amount = +500` (adds to commission)
- Agent receives: `10,000 + 500 = 10,500`

### Deduction (Negative Value)

```json
{
    "reward_type": "percentage",
    "reward_type_id": 2,
    "reward_type_value": "-5"
}
```
- Result: `incentive_amount = -500` (reduces commission)
- Agent receives: `10,000 - 500 = 9,500`

## Complete Payload for Your Scenario

**Scenario**: If sales target achievement is below 100%, hold 5% from commission income

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
                "label": "Achievement Below Target"
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

1. **Setup Created**: Incentive setup saved with `reward_type_value: "-5"`

2. **Period Processing**: System processes each month (if Monthly)

3. **Agent Evaluation**: For each agent:
   - Calculates `sum_of_agent_achieved` (actual sales)
   - Calculates `sum_of_agent_sales_target` (target sales)
   - Checks: `sum_of_agent_achieved < sum_of_agent_sales_target`

4. **Condition Result**:
   - If **True** (achievement < 100%): Agent is eligible for penalty
   - If **False** (achievement >= 100%): Agent is not eligible

5. **Penalty Calculation** (if eligible):
   - Gets agent's commission: `sum_of_agent_commission_recognized = 10,000`
   - Calculates: `10,000 × 5% = 500`
   - Detects negative value: `is_penalty = True`
   - Converts to negative: `reward_amount = -500`

6. **Incentive Record Created**:
   ```json
   {
       "incentive_setup_id": 123,
       "agent_id": 456,
       "incentive_amount": -500,
       "commission_date": "2024-01-31"
   }
   ```

7. **Effect**: Agent's commission is reduced by 500

## Important Notes

1. **Negative value = Deduction**: `-5` means "deduct 5%"
2. **Positive value = Reward**: `5` means "add 5% bonus"
3. **incentive_base_field is required**: Even for fixed deductions, provide a base field
4. **Percentage calculations**: Always based on `incentive_base_field`
5. **Fixed deductions**: Use negative fixed amount (e.g., `-1000`)

## Summary

**Q: How do I indicate a deduction? Will -5% work?**

**A: YES! Use negative value: `"reward_type_value": "-5"`**

- ✅ `-5` = 5% deduction
- ✅ `-1000` = 1000 fixed deduction
- ❌ `5` = 5% reward (not deduction)

The system automatically:
1. Detects negative value
2. Calculates the amount
3. Stores as negative in `incentive_amount`
4. Reduces agent's commission

