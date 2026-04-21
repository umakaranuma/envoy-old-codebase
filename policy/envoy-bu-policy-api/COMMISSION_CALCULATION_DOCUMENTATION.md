# Commission Calculation Documentation

## Overview
This document explains how brokerage commissions and agent commissions are calculated in the finance module, including how they handle fixed vs percentage types and different transaction types (refund, cancellation, additions).

## Transaction Types
- **Transaction Type 1**: New Business
- **Transaction Type 2**: Additions
- **Transaction Type 3**: Renewals
- **Transaction Type 4**: Refunds
- **Transaction Type 5**: Cancellations

## Commission Types
- **Fixed/Flat**: A fixed amount regardless of premium
- **Percentage**: A percentage of the base amount

---

## 1. Brokerage Commission Calculation

### Location
`envoy_bu_policy_api/finance/controllers/utils/commission/main.py`

### For New Business, Additions, and Renewals (Transaction Types 1, 2, 3)

#### Fixed/Flat Type
```python
if brokerage_type in ["flat", "fixed"]:
    brokerage_amount = brokerage_percent  # Use the value directly
```
- **Example**: If fixed value is 10,000, brokerage commission = 10,000 (regardless of premium)

#### Percentage Type
```python
else:  # percentage
    brokerage_amount = (invoice_amount * brokerage_percent / Decimal("100")).quantize(Decimal(".01"))
```
- **Example**: If premium is 100,000 and percentage is 10%, brokerage commission = 10,000

### For Refunds and Cancellations (Transaction Types 4, 5)

#### Fixed/Flat Type
1. Calculate commission on **FULL original premium** (before refund/cancellation)
2. Calculate ratio: `ratio = refund_or_cancellation_amount / original_premium_amount`
3. Apply ratio to the commission: `brokerage_deduction = full_commission * ratio`

**Example**:
- Original Premium: 1,000,000
- Fixed Commission: 10,000
- Cancellation Amount: 200,000
- Ratio: 200,000 / 1,000,000 = 0.2
- Deduction: 10,000 * 0.2 = 2,000

#### Percentage Type
1. Calculate directly on the refund/cancellation amount (no ratio needed)
2. `brokerage_deduction = (refund_or_cancellation_amount * brokerage_percent / 100)`

**Example**:
- Cancellation Amount: 200,000
- Commission Percentage: 10%
- Deduction: 200,000 * 10% = 20,000

**Key Code Location**: `deduction_utils.py` lines 1045-1206

---

## 2. Agent Commission Calculation

### Location
`envoy_bu_policy_api/finance/controllers/utils/commission/main.py`

### For New Business, Additions, and Renewals (Transaction Types 1, 2, 3)

#### Priority Order:
1. **Revised Commission** (if exists) - highest priority
2. **Regular Agent Commission** (from commission setup)

#### Fixed/Flat Type
```python
if type_ == "fixed":
    revenue_recognized = value  # Use the fixed value directly
```
- **Example**: If fixed value is 1,000, agent commission = 1,000

#### Percentage Type
```python
else:  # percentage
    # Calculate as percentage of BROKERAGE commission, not invoice amount
    revenue_recognized = (brokerage_amount * value / Decimal("100")).quantize(Decimal(".01"))
```
- **Example**: If brokerage commission is 10,000 and agent percentage is 20%, agent commission = 2,000

**Important**: Agent commission percentage is calculated based on **brokerage commission amount**, not the invoice/premium amount.

#### Revised Commission Logic
- If `revised_amount > 0` exists in database, it takes priority
- For fixed revised: `revenue_recognized = revised_amount` (proportional to payment if paid_amount > 0)
- For percentage revised: `revenue_recognized = (brokerage_amount * revised_percent / 100)`

### For Refunds and Cancellations (Transaction Types 4, 5)

#### Priority Order:
1. **Revised Amount from Database** (if exists and > 0)
2. **Revised Commission from Setup** (if exists)
3. **Regular Agent Commission** (fallback)

#### Fixed/Flat Type
1. Calculate commission on **FULL original premium** (before refund/cancellation)
2. Calculate ratio: `ratio = refund_or_cancellation_amount / original_premium_amount`
3. Apply ratio: `agent_deduction = full_commission * ratio`

**Example**:
- Original Premium: 1,000,000
- Fixed Agent Commission: 1,000
- Cancellation Amount: 200,000
- Ratio: 200,000 / 1,000,000 = 0.2
- Deduction: 1,000 * 0.2 = 200

#### Percentage Type
1. Calculate as percentage of **brokerage deduction**, not the refund/cancellation amount
2. `agent_deduction = (brokerage_deduction * agent_percent / 100)`

**Example**:
- Brokerage Deduction: 20,000
- Agent Commission Percentage: 10%
- Agent Deduction: 20,000 * 10% = 2,000

**Special Case**: Even if brokerage is percentage type, **fixed agent commissions still need ratio applied**:
```python
# IMPORTANT: For FIXED agent commissions, we still need to apply ratio
# even when brokerage is percentage type
if agent_type in ["flat", "fixed"]:
    agent_ratio = (refund_or_cancellation_amount / original_premium_amount)
    agent_deduction = agent_deduction * agent_ratio
```

**Key Code Location**: `deduction_utils.py` lines 177-376 (calculate_commission_deduction function)

---

## 3. Base Amount Calculation

### Location
`envoy_bu_policy_api/finance/controllers/utils/commission/base_calculator.py`

The base amount depends on the `calculation_mode`:
- **"premium" mode**: Uses `invoice_amount` (total premium)
- **"paid" mode**: Uses `paid_amount` (amount paid so far)

```python
def calculate_commission_base_amount(invoice_amount, paid_amount, calculation_mode=None):
    mode = get_commission_calculation_mode(calculation_mode)
    if mode == 'paid':
        return paid_amount
    return invoice_amount
```

**Note**: For `revenue_recognized`, always uses `invoice_amount`. The `calculation_mode` affects `revenue_realized` calculations.

---

## 4. Additions (Transaction Type 2)

### Commission Setup
- If no commission setup found for Addition, falls back to New Business (transaction_type_id = 1) setup
- Uses the same calculation logic as New Business

### Calculation
- Uses the same logic as New Business (transaction_type_id = 1)
- Fixed: Uses fixed value directly
- Percentage: Calculates percentage of invoice amount

**Key Code Location**: `main.py` lines 77-85

---

## 5. Deductible Distribution for Refunds/Cancellations

### Location
`envoy_bu_policy_api/finance/controllers/utils/commission/deduction_utils.py`

### Distribution Order
When a refund or cancellation occurs, deductible amounts are distributed across invoices in this order:
1. **Newest Addition invoice first** (transaction_type_id = 2, sorted by id desc)
2. **Older Addition invoices** (newest to oldest)
3. **Premium invoice last** (transaction_type_id = 1 or 3)

### Distribution Logic
- For **Addition invoices**: Deductible is applied to equalize outstanding to 0 (cannot go negative)
- For **Premium invoice**: Deductible can make outstanding negative

### Outstanding Calculation
```
outstanding = revenue_recognized - revenue_realized - commission_deductible
```

**Key Code Location**: `deduction_utils.py` lines 570-857 (store_commission_deductible_only function)

---

## 6. Key Functions

### Main Calculation Function
- **File**: `main.py`
- **Function**: `calculate_commission_amounts()`
- **Purpose**: Calculates commissions for New Business, Additions, and Renewals

### Deduction Function
- **File**: `deduction_utils.py`
- **Function**: `handle_commission_deduction()`
- **Purpose**: Handles commission deductions for Refunds and Cancellations

### Deduction Calculation
- **File**: `deduction_utils.py`
- **Function**: `calculate_commission_deduction()`
- **Purpose**: Calculates the actual deduction amounts based on commission type

### Deductible Storage
- **File**: `deduction_utils.py`
- **Function**: `store_commission_deductible_only()`
- **Purpose**: Stores deductible amounts across invoices without modifying revenue_recognized

---

## 7. Examples

### Example 1: New Business with Fixed Brokerage and Percentage Agent
- Premium: 100,000
- Brokerage: Fixed 10,000
- Agent: 20% of brokerage
- **Result**: 
  - Brokerage Commission: 10,000
  - Agent Commission: 2,000 (20% of 10,000)

### Example 2: New Business with Percentage Brokerage and Fixed Agent
- Premium: 100,000
- Brokerage: 10% of premium
- Agent: Fixed 1,000
- **Result**:
  - Brokerage Commission: 10,000 (10% of 100,000)
  - Agent Commission: 1,000

### Example 3: Cancellation with Fixed Brokerage
- Original Premium: 1,000,000
- Fixed Brokerage: 10,000
- Cancellation Amount: 200,000
- **Calculation**:
  - Ratio: 200,000 / 1,000,000 = 0.2
  - Brokerage Deduction: 10,000 * 0.2 = 2,000

### Example 4: Cancellation with Percentage Brokerage
- Cancellation Amount: 200,000
- Brokerage: 10% of cancellation
- **Calculation**:
  - Brokerage Deduction: 200,000 * 10% = 20,000

### Example 5: Cancellation with Percentage Brokerage and Fixed Agent
- Original Premium: 1,000,000
- Cancellation Amount: 200,000
- Brokerage: 10% (percentage) → Deduction: 20,000
- Agent: Fixed 1,000
- **Calculation**:
  - Agent Ratio: 200,000 / 1,000,000 = 0.2
  - Agent Deduction: 1,000 * 0.2 = 200

---

## 8. Important Notes

1. **Agent commission percentage is always calculated based on brokerage commission**, not the invoice/premium amount
2. **For fixed commissions in refunds/cancellations**, the ratio method is used (calculate on full premium, then apply ratio)
3. **For percentage commissions in refunds/cancellations**, calculate directly on the refund/cancellation amount
4. **Fixed agent commissions still need ratio applied** even when brokerage is percentage type
5. **Revised commissions take priority** over regular agent commissions
6. **Deductible amounts are stored** but don't modify `revenue_recognized` until payment is made
7. **Additions fall back to New Business** commission setup if no Addition setup exists

---

## 9. Database Fields

### Brokerage Commission Table (`crmf_brokerage_commission`)
- `brokerage_revenue_percent`: Commission percentage or fixed value
- `brokerage_revenue_type`: "flat"/"fixed" or "percentage"
- `revenue_recognized`: Expected total commission
- `revenue_realized`: Commission realized based on payments
- `commission_deductible`: Deductible amount for refunds/cancellations
- `base_amount`: Invoice amount used as base for calculation

### Agent Commission Table (`crmf_agent_commission`)
- `agent_commission_percent`: Commission percentage (0 for fixed)
- `agent_commission_type`: "flat"/"fixed" or "percentage"
- `revised_amount`: Revised commission amount (if exists)
- `revised_amount_percent`: Revised commission percentage
- `revised_amount_type`: Type of revised commission
- `revenue_recognized`: Expected total commission
- `revenue_realized`: Commission realized based on payments
- `commission_deductible`: Deductible amount for refunds/cancellations
- `base_amount`: Invoice amount used as base for calculation

