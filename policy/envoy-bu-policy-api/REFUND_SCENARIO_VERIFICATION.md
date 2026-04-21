# Refund Scenario Verification

## Given Scenario

- **Premium Amount**: 260,000
- **Premium Brokerage**: 10,000 (fixed)
- **Premium Agent**: 4,000 (fixed)
- **Addition Amount**: 20,000
- **Addition Brokerage**: 8,000 (fixed)
- **Addition Agent**: 3,000 (fixed)
- **Refund**: 60,000

---

## ❌ Error Found: Ratio Calculation

### User's Calculation
```
Ratio = 260,000 : 60,000 = 1/13
```

### ✅ Correct Calculation
```
Ratio = Refund Amount / Original Premium Amount
Ratio = 60,000 / 260,000
Ratio = 3/13 (or 0.230769...)
```

**The ratio is 3/13, NOT 1/13**

---

## ✅ Correct Calculations

### Step 1: Calculate Refund Ratio
```
Ratio = 60,000 / 260,000 = 3/13 = 0.230769...
```

### Step 2: Premium Commission Deductions

Since both are **FIXED**, apply the ratio:

**Premium Brokerage Deduction:**
```
Deduction = 10,000 × (60,000 / 260,000)
Deduction = 10,000 × 3/13
Deduction = 2,307.69
```

**Premium Agent Deduction:**
```
Deduction = 4,000 × (60,000 / 260,000)
Deduction = 4,000 × 3/13
Deduction = 923.08
```

### Step 3: Addition Commission

✅ **YES, the addition commission is 8,000 for brokerage** (this is correct)

The addition invoice has:
- **Addition Brokerage**: 8,000 (fixed) ✅
- **Addition Agent**: 3,000 (fixed) ✅

---

## ⚠️ Important: Deductible Distribution

When a refund occurs, the **deductible is calculated on the ORIGINAL premium (260,000)**, then **distributed across invoices** in this order:

1. **Newest Addition invoice first** (transaction_type_id = 2)
2. **Older Addition invoices** (newest to oldest)
3. **Premium invoice last** (transaction_type_id = 1 or 3)

### Distribution Logic

**Total Deductible Calculated:**
- Total Brokerage Deductible: 2,307.69 (from premium 10,000 × 3/13)
- Total Agent Deductible: 923.08 (from premium 4,000 × 3/13)

**Distribution:**
1. First, apply to Addition invoice commission (if outstanding > 0)
   - Addition Brokerage Outstanding: 8,000
   - Addition Agent Outstanding: 3,000
   - Apply deductible up to outstanding amount
   
2. Then, apply remaining to Premium invoice
   - Premium Brokerage Outstanding: 10,000
   - Premium Agent Outstanding: 4,000
   - Apply remaining deductible

---

## Summary Table

| Commission Type | Original Amount | Ratio | Deduction Amount |
|----------------|-----------------|-------|-----------------|
| **Premium Brokerage** | 10,000 | 3/13 | **2,307.69** |
| **Premium Agent** | 4,000 | 3/13 | **923.08** |
| **Addition Brokerage** | 8,000 | - | **8,000** (correct, but may receive deductible) |
| **Addition Agent** | 3,000 | - | **3,000** (correct, but may receive deductible) |

---

## Corrections Needed

1. ❌ **Ratio is 3/13, NOT 1/13**
2. ✅ **Addition brokerage of 8,000 is correct** (for the addition itself)
3. ⚠️ **But when refund happens, deductible is calculated on original premium (260,000)**
4. ⚠️ **Deductible is then distributed: Addition invoices first, then Premium invoice**

---

## Example: Full Deductible Distribution

### Scenario:
- Premium Brokerage: 10,000 (outstanding: 10,000)
- Addition Brokerage: 8,000 (outstanding: 8,000)
- Total Deductible: 2,307.69

### Distribution:
1. **Addition Invoice** (processed first):
   - Outstanding: 8,000
   - Deductible to apply: min(2,307.69, 8,000) = 2,307.69
   - New Outstanding: 8,000 - 2,307.69 = 5,692.31
   - Remaining Deductible: 0

2. **Premium Invoice** (processed second):
   - Outstanding: 10,000
   - Deductible to apply: 0 (all used in addition)
   - New Outstanding: 10,000

**Result**: All deductible goes to Addition invoice first (newest addition first rule)

---

## Final Answer

✅ **Addition brokerage of 8,000 is CORRECT** for the addition commission itself.

❌ **But the ratio calculation is WRONG**: It should be **3/13**, not 1/13.

✅ **Premium brokerage deduction**: 10,000 × 3/13 = **2,307.69**

✅ **Premium agent deduction**: 4,000 × 3/13 = **923.08**

⚠️ **When refund happens, the deductible (2,307.69) is distributed to Addition invoice first, then Premium invoice.**

