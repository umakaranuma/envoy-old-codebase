# Target Achievement Commission Deduction - How to Indicate Deduction vs Reward

## Your Question

**Q: If I just enter 5, it's a reward right? How do I indicate it's a deduction?**

**A: The field name itself indicates it's a deduction, but you enter a positive value (5).**

## How the System Distinguishes Deductions from Rewards

### Current System Design

The system uses **field names** to distinguish between rewards and deductions:

1. **`bonus_commission_percent`** → **REWARD** (adds to commission)
   - Stored in `bonus_amount` field (positive value)
   - Adds to agent's commission

2. **`target_achievement_commission_percent`** → **DEDUCTION** (reduces commission)
   - Should be stored in `commission_deductible` field (negative value)
   - Reduces agent's commission

### How to Enter Values

#### For Target Achievement Deduction (Below 100% Achievement)

**Enter: `5` (positive value)**

- Field: `target_achievement_commission_percent`
- Value: `5` (means "hold 5% of commission")
- Type: `"percentage"`

**The code implementation will:**
1. Read the positive value (5)
2. Calculate: `commission × 5% = deduction_amount`
3. Store as **negative** in `commission_deductible`: `-500`
4. Reduce `revenue_realized` accordingly

#### For Bonus (Reward)

**Enter: `5` (positive value)**

- Field: `bonus_commission_percent`
- Value: `5` (means "add 5% bonus")
- Type: `"percentage"`

**The code implementation will:**
1. Read the positive value (5)
2. Calculate: `commission × 5% = bonus_amount`
3. Store as **positive** in `bonus_amount`: `500`
4. Add to agent's commission

## Example Comparison

### Scenario: Agent has 10,000 commission, achievement is 80% (< 100%)

#### If Using `target_achievement_commission_percent = 5` (Deduction)
```
Commission: 10,000
Achievement: 80% (< 100%, so deduction applies)
Deduction: 10,000 × 5% = 500
commission_deductible: -500 (stored as negative)
revenue_realized: 9,500 (10,000 - 500)
Agent receives: 9,500
```

#### If Using `bonus_commission_percent = 5` (Reward)
```
Commission: 10,000
Bonus: 10,000 × 5% = 500
bonus_amount: 500 (stored as positive)
revenue_realized: 10,500 (10,000 + 500)
Agent receives: 10,500
```

## Answer to Your Question

**Q: If I just enter 5, it's a reward right?**

**A: NO - it depends on which field you use:**

- **`target_achievement_commission_percent = 5`** → **DEDUCTION** (reduces commission)
- **`bonus_commission_percent = 5`** → **REWARD** (adds to commission)

**The field name determines whether it's a deduction or reward, not the value itself.**

## Important Notes

### 1. Always Use Positive Values
- ✅ Enter `5` (positive)
- ❌ Do NOT enter `-5` (negative)

The system will automatically:
- Store deductions as negative in `commission_deductible`
- Store rewards as positive in `bonus_amount`

### 2. Field Name is the Key
The system distinguishes by field name:
- `target_achievement_commission_percent` → Always treated as deduction
- `bonus_commission_percent` → Always treated as reward

### 3. Current Implementation Status
**⚠️ IMPORTANT**: `target_achievement_commission_percent` is currently **NOT implemented** in the commission calculation code. You need to:

1. **Implement the logic** to check target achievement
2. **Apply the deduction** when achievement < 100%
3. **Store in `commission_deductible`** as negative value

## Implementation Pattern

When implementing, follow this pattern:

```python
# Get target achievement commission percent from setup
target_achievement_data = commission_values.get(
    "target_achievement_commission_percent", 
    [{"value": "0", "type": "percentage"}]
)[0]
target_achievement_percent = Decimal(str(target_achievement_data.get("value", "0")))

# Calculate agent's actual achievement
agent_achievement = calculate_agent_target_achievement(agent_id, period)

# If achievement < 100%, apply deduction
if agent_achievement < 100 and target_achievement_percent > 0:
    # Calculate deduction (positive value from setup)
    deduction_amount = revenue_recognized * target_achievement_percent / Decimal("100")
    
    # Store as NEGATIVE in commission_deductible
    commission_deductible = -deduction_amount
    
    # Reduce revenue_realized
    revenue_realized = revenue_recognized - deduction_amount
else:
    # No deduction
    commission_deductible = Decimal("0.00")
    revenue_realized = revenue_recognized
```

## Summary

| Field Name | Value Entered | What It Does | Stored Where | Sign |
|------------|---------------|--------------|--------------|------|
| `target_achievement_commission_percent` | `5` (positive) | Holds 5% of commission | `commission_deductible` | Negative (-500) |
| `bonus_commission_percent` | `5` (positive) | Adds 5% bonus | `bonus_amount` | Positive (+500) |

**Key Point**: Enter positive values (5), and the system handles the sign based on the field name and implementation logic.

