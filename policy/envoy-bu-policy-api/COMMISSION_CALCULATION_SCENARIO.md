# Commission Calculation Scenario

## Given Scenario
- **Policy Premium Amount**: 100,000
- **Refund Amount**: 20,000
- **Brokerage Commission**: Fixed 10,000
- **Agent Commission**: 4,000

---

## Scenario Analysis

The agent commission of 4,000 could be either:
1. **Fixed 4,000** (fixed amount)
2. **Percentage** that equals 4,000 (which would be 40% of brokerage 10,000)

I'll calculate both scenarios below.

---

## Scenario 1: Agent Commission is FIXED 4,000

### Step-by-Step Calculation

#### Step 1: Calculate Refund Ratio
```
Ratio = Refund Amount / Original Premium Amount
Ratio = 20,000 / 100,000
Ratio = 0.2 (20%)
```

#### Step 2: Calculate Brokerage Deduction
Since brokerage is **FIXED**, the system:
1. Calculates commission on **FULL original premium** (100,000)
2. Gets the fixed brokerage commission: **10,000**
3. Applies the ratio to get the deduction:

```
Brokerage Deduction = Fixed Brokerage × Ratio
Brokerage Deduction = 10,000 × 0.2
Brokerage Deduction = 2,000
```

**Result**: Brokerage Deduction = **2,000**

#### Step 3: Calculate Agent Deduction
Since agent commission is also **FIXED**, the system:
1. Uses the fixed agent commission: **4,000**
2. Applies the same ratio:

```
Agent Deduction = Fixed Agent Commission × Ratio
Agent Deduction = 4,000 × 0.2
Agent Deduction = 800
```

**Result**: Agent Deduction = **800**

---

## Scenario 2: Agent Commission is PERCENTAGE (40% of Brokerage)

### Assumption
If agent commission is 4,000 and brokerage is 10,000, then:
- Agent Percentage = 4,000 / 10,000 = 40%

### Step-by-Step Calculation

#### Step 1: Calculate Refund Ratio
```
Ratio = 20,000 / 100,000 = 0.2 (20%)
```

#### Step 2: Calculate Brokerage Deduction
Same as Scenario 1:
```
Brokerage Deduction = 10,000 × 0.2 = 2,000
```

#### Step 3: Calculate Agent Deduction
Since agent commission is **PERCENTAGE**, the system:
1. Calculates as percentage of **brokerage deduction** (not original premium)
2. Uses the brokerage deduction amount: **2,000**

```
Agent Deduction = Brokerage Deduction × Agent Percentage
Agent Deduction = 2,000 × 40%
Agent Deduction = 800
```

**Result**: Agent Deduction = **800**

---

## Summary Table

| Scenario | Brokerage Type | Agent Type | Brokerage Deduction | Agent Deduction |
|----------|---------------|------------|---------------------|-----------------|
| Scenario 1 | Fixed 10,000 | Fixed 4,000 | **2,000** | **800** |
| Scenario 2 | Fixed 10,000 | Percentage 40% | **2,000** | **800** |

**Note**: In this specific case, both scenarios yield the same result (800), but the calculation method differs.

---

## How It's Stored in Database

### Brokerage Commission Record
- `revenue_recognized`: 10,000 (original commission)
- `revenue_realized`: (unchanged, based on payments)
- `commission_deductible`: 2,000 (the deduction amount)
- `outstanding`: `revenue_recognized - revenue_realized - commission_deductible`

### Agent Commission Record
- `revenue_recognized`: 4,000 (original commission)
- `revenue_realized`: (unchanged, based on payments)
- `commission_deductible`: 800 (the deduction amount)
- `outstanding`: `revenue_recognized - revenue_realized - commission_deductible`

---

## Key Code References

### For Fixed Brokerage Commission (Refund)
**File**: `deduction_utils.py`  
**Lines**: 1061-1085

```python
if brokerage_type in ["flat", "fixed"]:
    # Calculate ratio
    ratio = (refund_amount / premium_for_ratio).quantize(Decimal(".0001"))
    # Calculate on full premium, then apply ratio
    brokerage_deduction = (brokerage_deduction * ratio).quantize(Decimal(".01"))
```

### For Fixed Agent Commission (Refund)
**File**: `deduction_utils.py`  
**Lines**: 1080-1083

```python
for agent_data in agent_deductions:
    original_deduction = agent_data["deduction"]
    agent_data["deduction"] = (agent_data["deduction"] * ratio).quantize(Decimal(".01"))
```

### For Percentage Agent Commission (Refund)
**File**: `deduction_utils.py`  
**Lines**: 368-374

```python
else:  # percentage
    # Calculate as percentage of brokerage deduction
    brokerage_deduction_abs = abs(brokerage_deduction)
    agent_deduction = -(brokerage_deduction_abs * value / Decimal("100")).quantize(Decimal(".01"))
```

---

## Example with Different Values

### Example: Refund 50,000 (50% of premium)

**Given**:
- Premium: 100,000
- Refund: 50,000
- Brokerage: Fixed 10,000
- Agent: Fixed 4,000

**Calculation**:
- Ratio = 50,000 / 100,000 = 0.5 (50%)
- Brokerage Deduction = 10,000 × 0.5 = **5,000**
- Agent Deduction = 4,000 × 0.5 = **2,000**

---

## Important Notes

1. **Fixed commissions use ratio method**: The ratio is always calculated as `refund_amount / original_premium_amount`

2. **Percentage agent commissions**: Are calculated based on **brokerage deduction**, not the refund amount or original premium

3. **Deductible storage**: The deductible amounts are stored in the `commission_deductible` field but do NOT modify `revenue_recognized`. The `revenue_recognized` remains the original commission amount.

4. **Outstanding calculation**: 
   ```
   Outstanding = revenue_recognized - revenue_realized - commission_deductible
   ```

5. **For your scenario**: Both fixed and percentage agent commission types will result in the same deduction (800) because:
   - Fixed: 4,000 × 0.2 = 800
   - Percentage: 2,000 × 40% = 800

