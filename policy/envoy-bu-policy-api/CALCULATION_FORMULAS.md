# Commission Calculation Formulas

This document provides a comprehensive overview of all calculation formulas used in the commission system, including deductible calculations and other related formulas.

---

## Table of Contents
1. [Outstanding Amount Calculation](#outstanding-amount-calculation)
2. [Deductible Calculations](#deductible-calculations)
3. [Revenue Realized Calculation](#revenue-realized-calculation)
4. [Settlement Amount Calculation](#settlement-amount-calculation)
5. [Commission Deduction Formulas](#commission-deduction-formulas)

---

## Outstanding Amount Calculation

### Formula
```
Outstanding = Revenue Recognized - Revenue Realized - Commission Deductible
```

### Details
- **For Brokerage Commission:**
  ```python
  outstanding = revenue_recognized - revenue_realized - commission_deductible
  ```

- **For Agent Commission:**
  ```python
  outstanding = revenue_recognized - revenue_realized - commission_deductible
  ```

### Notes
- Outstanding can be negative for premium invoices (allowed)
- For addition invoices, if outstanding is negative, it is typically set to 0
- Outstanding represents the amount that is still pending settlement

### Code Reference
- **File:** `deduction_utils.py` (lines 99-134)
- **File:** `brokerage_commission_settlement_controller.py` (lines 232-239)
- **File:** `brokerage_commission_settlement.py` (lines 38-43, 54-56)

---

## Deductible Calculations

### Overview
Deductible amounts are calculated when refunds or cancellations occur. The calculation method depends on whether the commission is **Fixed/Flat** or **Percentage**.

---

### 1. Fixed/Flat Brokerage Commission Deductible (Refund/Cancellation)

#### Formula
```
Ratio = Refund Amount / Original Premium Amount
Brokerage Deductible = Original Revenue Recognized × Ratio
```

#### Example
- Premium: 100,000
- Refund: 20,000
- Original Brokerage Revenue Recognized: 10,000
- **Calculation:**
  - Ratio = 20,000 / 100,000 = 0.2 (20%)
  - Brokerage Deductible = 10,000 × 0.2 = **2,000**

#### Code Reference
- **File:** `deduction_utils.py` (lines 1061-1087)

```python
# For fixed/flat brokerage commission (refund)
ratio = (refund_amount / premium_for_ratio).quantize(Decimal(".0001"))
brokerage_amount = original_brokerage.get("revenue_recognized")
brokerage_deduction = (abs(brokerage_amount) * ratio).quantize(Decimal(".01"))
```

---

### 2. Percentage Brokerage Commission Deductible (Refund/Cancellation)

#### Formula
```
Brokerage Deductible = Refund Amount × (Commission Percentage / 100)
```

#### Example
- Refund: 20,000
- Commission: 10%
- **Calculation:**
  - Brokerage Deductible = 20,000 × (10 / 100) = **2,000**

#### Code Reference
- **File:** `deduction_utils.py` (lines 1106-1113)

```python
# For percentage brokerage commission (refund)
base_amount = calculate_commission_base_amount(refund_amount, Decimal("0.00"), calculation_mode)
brokerage_deduction = (base_amount * brokerage_percent / Decimal("100")).quantize(Decimal(".01"))
```

---

### 3. Agent Commission Deductible

The agent commission deductible calculation depends on:
1. Whether the agent commission is **Fixed** or **Percentage**
2. Whether there is a **revised commission** in the database
3. Whether the brokerage commission is **Fixed** or **Percentage**

---

#### 3.1 Fixed Agent Commission Deductible (with Fixed Brokerage)

#### Formula
```
Ratio = Refund Amount / Original Premium Amount
Agent Deductible = Original Agent Revenue Recognized × Ratio
```

#### Example
- Premium: 100,000
- Refund: 20,000
- Original Agent Revenue Recognized: 4,000
- **Calculation:**
  - Ratio = 20,000 / 100,000 = 0.2 (20%)
  - Agent Deductible = 4,000 × 0.2 = **800**

#### Code Reference
- **File:** `deduction_utils.py` (lines 1089-1102)

```python
# For fixed agent commission (refund with fixed brokerage)
ratio = (refund_amount / premium_for_ratio).quantize(Decimal(".0001"))
agent_amount = original_agent_comm.get("revenue_recognized")
agent_deduction = -(abs(agent_amount) * ratio).quantize(Decimal(".01"))
```

---

#### 3.2 Percentage Agent Commission Deductible

#### Formula
```
Agent Deductible = Brokerage Deductible × (Agent Commission Percentage / 100)
```

**IMPORTANT:** Agent commission deductible is calculated as a percentage of the **brokerage deductible**, NOT the refund amount or original premium.

#### Example
- Brokerage Deductible: 2,000
- Agent Commission: 40% of brokerage
- **Calculation:**
  - Agent Deductible = 2,000 × (40 / 100) = **800**

#### Code Reference
- **File:** `deduction_utils.py` (lines 368-374, 314-320)

```python
# For percentage agent commission
brokerage_deduction_abs = abs(brokerage_deduction)
agent_deduction = -(brokerage_deduction_abs * agent_percent / Decimal("100")).quantize(Decimal(".01"))
# Ensure agent deductible never exceeds brokerage deductible
if abs(agent_deduction) > brokerage_deduction_abs:
    agent_deduction = -brokerage_deduction_abs
```

---

#### 3.3 Fixed Agent Commission with Revised Amount (from Database)

#### Formula
```
Deduction Ratio = Brokerage Deductible / Original Brokerage Amount
Agent Deductible = Revised Amount × Deduction Ratio
```

#### Example
- Original Brokerage Amount: 10,000
- Brokerage Deductible: 2,000
- Agent Revised Amount (from DB): 6,000
- **Calculation:**
  - Deduction Ratio = 2,000 / 10,000 = 0.2
  - Agent Deductible = 6,000 × 0.2 = **1,200**

#### Code Reference
- **File:** `deduction_utils.py` (lines 289-307)

```python
# For fixed/flat revised amount from database
if original_brokerage and brokerage_amount > 0:
    deduction_ratio = abs(brokerage_deduction) / brokerage_amount
    agent_deduction = -(revised_amount_db * deduction_ratio).quantize(Decimal(".01"))
```

---

#### 3.4 Percentage Agent Commission with Revised Amount (from Database)

#### Formula
```
Agent Deductible = Brokerage Deductible × (Revised Commission Percentage / 100)
```

#### Example
- Brokerage Deductible: 9,000
- Agent Revised Commission Percentage: 20%
- **Calculation:**
  - Agent Deductible = 9,000 × (20 / 100) = **1,800**

#### Code Reference
- **File:** `deduction_utils.py` (lines 314-320)

```python
# For percentage revised amount from database
if revised_amount_percent_db > 0:
    brokerage_deduction_abs = abs(brokerage_deduction)
    agent_deduction = -(brokerage_deduction_abs * revised_amount_percent_db / Decimal("100")).quantize(Decimal(".01"))
```

---

### 4. General Commission Deduction Calculation

#### For Fixed/Flat Commission
```python
brokerage_deduction = brokerage_percent  # Use value directly
```

#### For Percentage Commission
```python
brokerage_deduction = (base_amount * brokerage_percent / Decimal("100")).quantize(Decimal(".01"))
```

#### Code Reference
- **File:** `deduction_utils.py` (lines 207-214)

---

## Revenue Realized Calculation

### Overview
Revenue realized is calculated proportionally when a customer makes a payment. The calculation differs for **Fixed** and **Percentage** commissions.

---

### 1. Fixed Commission Revenue Realized

#### Formula
```
Incremental Realized = (Revenue Recognized / Invoice Amount) × Incremental Payment
New Revenue Realized = Current Revenue Realized + Incremental Realized
```

#### Example
- Revenue Recognized: 10,000
- Invoice Amount: 25,000
- Incremental Payment: 25,000
- **Calculation:**
  - Incremental Realized = (10,000 / 25,000) × 25,000 = **10,000**

#### Code Reference
- **File:** `commission_pay_utils.py` (lines 53-57, 121-126)

```python
# For fixed commission
base_amount_for_calculation = invoice_amount
incremental_realized = (recognized_value / base_amount_for_calculation) * incremental_payment
new_value = current_value + incremental_realized
```

---

### 2. Percentage Commission Revenue Realized

#### For Addition Invoices (transaction_type_id = 2)
```
Incremental Realized = (Revenue Recognized / Invoice Amount) × Incremental Payment
```

#### For Other Invoices (Premium, Renewal, etc.)
```
Incremental Realized = (Revenue Recognized / Current Premium Amount) × Incremental Payment
```

#### Example (Non-Addition Invoice)
- Revenue Recognized: 10,000 (10% of 100,000 premium)
- Current Premium Amount: 100,000
- Incremental Payment: 20,000
- **Calculation:**
  - Incremental Realized = (10,000 / 100,000) × 20,000 = **2,000**

#### Code Reference
- **File:** `commission_pay_utils.py` (lines 58-79, 121-126)

```python
# For percentage commission
if transaction_type_id == 2:  # Addition
    base_amount_for_calculation = invoice_amount
else:
    # Use current premium amount from policy
    base_amount_for_calculation = current_policy.get("premium_amount")
    
incremental_realized = (recognized_value / base_amount_for_calculation) * incremental_payment
new_value = current_value + incremental_realized
```

---

## Settlement Amount Calculation

### Formula
```
Outstanding = Revenue Recognized - Revenue Realized - Commission Deductible

If Outstanding < 0:
    Settlement Amount = |Outstanding|  (absolute value)
Else:
    Settlement Amount = Revenue Realized - Commission Deductible - Total Already Settled
    Settlement Amount = max(0, Settlement Amount)  (cannot be negative)
```

### Example 1: Normal Settlement
- Revenue Recognized: 10,000
- Revenue Realized: 8,000
- Commission Deductible: 1,000
- Total Already Settled: 2,000
- **Calculation:**
  - Outstanding = 10,000 - 8,000 - 1,000 = 1,000
  - Settlement Amount = 8,000 - 1,000 - 2,000 = **5,000**

### Example 2: Negative Outstanding
- Revenue Recognized: 10,000
- Revenue Realized: 12,000
- Commission Deductible: 1,000
- **Calculation:**
  - Outstanding = 10,000 - 12,000 - 1,000 = -3,000
  - Settlement Amount = |-3,000| = **3,000**

### Code Reference
- **File:** `brokerage_commission_settlement_controller.py` (lines 232-259)

```python
# Calculate outstanding amount
outstanding = revenue_recognized - revenue_realized - commission_deductible

# If outstanding is negative, store the absolute value as settlement_amount
if outstanding < 0:
    settlement_amount = abs(outstanding)
else:
    # Normal settlement: revenue_realized - deductible - already settled
    settlement_amount = revenue_realized - commission_deductible - total_settled_decimal
    # Ensure we don't settle negative amounts for normal settlements
    settlement_amount = max(Decimal("0.00"), settlement_amount)
```

---

## Commission Deduction Formulas

### Summary Table

| Commission Type | Brokerage Deductible | Agent Deductible |
|----------------|---------------------|------------------|
| **Fixed Brokerage + Fixed Agent** | `Original Revenue × Ratio` | `Original Agent Revenue × Ratio` |
| **Fixed Brokerage + % Agent** | `Original Revenue × Ratio` | `Brokerage Deductible × Agent %` |
| **% Brokerage + Fixed Agent** | `Refund Amount × Brokerage %` | `Original Agent Revenue × Ratio` |
| **% Brokerage + % Agent** | `Refund Amount × Brokerage %` | `Brokerage Deductible × Agent %` |

Where:
- **Ratio** = `Refund Amount / Original Premium Amount`
- **Brokerage Deductible** is calculated first, then used for agent calculation if agent is percentage

---

## Key Principles

### 1. Deductible Distribution
Deductible is distributed across invoices in the following order:
1. Newest addition invoice first (transaction_type_id = 2)
2. Older addition invoices (newest to oldest)
3. Premium invoice last (transaction_type_id = 1 or 3) - can have negative outstanding

### 2. Outstanding Calculation After Deductible
After storing deductible amounts:
```
Outstanding = Revenue Recognized - Revenue Realized - Commission Deductible
```
- For addition invoices: If result is negative, it is set to 0
- For premium invoice: Outstanding can be negative

### 3. Agent Commission Priority
When calculating agent deductible, the system checks in this order:
1. **Priority 1:** Revised amount from database (if exists)
2. **Priority 2:** Revised commission from commission setup
3. **Priority 3:** Regular agent commission from setup

### 4. Percentage Agent Commission Rule
**IMPORTANT:** Agent commission deductible (when percentage) is calculated as a percentage of the **brokerage commission deductible**, NOT the base amount or refund amount.

---

## Code File References

### Main Calculation Files
- `deduction_utils.py` - Deductible calculations
- `commission_pay_utils.py` - Revenue realized calculations
- `brokerage_commission_settlement_controller.py` - Settlement calculations
- `main.py` - Commission amount calculations

### Model Files
- `brokerage_commission_settlement.py` - Settlement summary calculations
- `crmf_brokerage_commission.py` - Commission model
- `crmf_agent_commission.py` - Agent commission model

---

## Examples

### Complete Example: Refund Scenario

**Given:**
- Premium: 100,000
- Refund: 20,000
- Brokerage Commission: Fixed 10,000
- Agent Commission: Fixed 4,000

**Step 1: Calculate Ratio**
```
Ratio = 20,000 / 100,000 = 0.2 (20%)
```

**Step 2: Calculate Brokerage Deductible**
```
Brokerage Deductible = 10,000 × 0.2 = 2,000
```

**Step 3: Calculate Agent Deductible**
```
Agent Deductible = 4,000 × 0.2 = 800
```

**Step 4: Update Outstanding**
```
Brokerage Outstanding = 10,000 - 0 - 2,000 = 8,000
Agent Outstanding = 4,000 - 0 - 800 = 3,200
```

---

### Complete Example: Percentage Commission

**Given:**
- Premium: 100,000
- Refund: 20,000
- Brokerage Commission: 10%
- Agent Commission: 40% of brokerage

**Step 1: Calculate Brokerage Deductible**
```
Brokerage Deductible = 20,000 × (10 / 100) = 2,000
```

**Step 2: Calculate Agent Deductible**
```
Agent Deductible = 2,000 × (40 / 100) = 800
```

**Step 3: Update Outstanding**
```
Brokerage Outstanding = 10,000 - 0 - 2,000 = 8,000
Agent Outstanding = 4,000 - 0 - 800 = 3,200
```

---

## Notes

1. All calculations use `Decimal` type for precision
2. All amounts are quantized to 2 decimal places (`.01`)
3. Ratios are quantized to 4 decimal places (`.0001`)
4. Deductible amounts are stored as absolute values in the database
5. Revenue recognized remains unchanged when deductible is applied
6. Outstanding can be negative for premium invoices but is typically set to 0 for addition invoices

