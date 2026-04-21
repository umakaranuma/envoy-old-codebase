# Commission Migration Plan: Invoice-Based → Issued Policy-Based

## Overview
This document outlines all changes needed to migrate commission calculations from being based on `invoice_id` to being based on `issued_policy_id`.

## Current Structure
```
Invoice → Brokerage Commission (OneToOne)
Invoice → Agent Commissions (via Brokerage Commission)
```

## Target Structure
```
Issued Policy → Brokerage Commission (OneToOne)
Issued Policy → Agent Commissions (via Brokerage Commission)
```

---

## 1. Database Model Changes

### 1.1 BrokerageCommission Model
**File:** `envoy_bu_policy_api/finance/models/crmf_brokerage_commission.py`

**Current:**
```python
invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name="brokerage_commission")
```

**Change To:**
```python
issued_policy = models.OneToOneField(
    "policy.IssuedPolicy", 
    on_delete=models.CASCADE, 
    related_name="brokerage_commission",
    db_column="issued_policy_id"
)
# Keep invoice_id as optional for backward compatibility during migration
invoice_id = models.IntegerField(null=True, blank=True, help_text="Legacy field - use issued_policy_id")
```

**Migration SQL:**
```sql
-- Add new column
ALTER TABLE crmf_brokerage_commission 
ADD COLUMN issued_policy_id INT NULL;

-- Populate from invoice
UPDATE crmf_brokerage_commission bc
INNER JOIN crmf_invoices inv ON bc.invoice_id = inv.id
SET bc.issued_policy_id = inv.issued_policy_id
WHERE inv.issued_policy_id IS NOT NULL;

-- Add foreign key constraint
ALTER TABLE crmf_brokerage_commission
ADD CONSTRAINT fk_brokerage_issued_policy 
FOREIGN KEY (issued_policy_id) REFERENCES crmp_issued_policies(id) ON DELETE CASCADE;

-- Make it NOT NULL after data migration
ALTER TABLE crmf_brokerage_commission 
MODIFY COLUMN issued_policy_id INT NOT NULL;

-- Add unique constraint
ALTER TABLE crmf_brokerage_commission
ADD UNIQUE KEY unique_issued_policy_commission (issued_policy_id);
```

---

## 2. Commission Calculation Changes

### 2.1 Main Calculation Function
**File:** `envoy_bu_policy_api/finance/controllers/utils/commission/main.py`

**Current Function Signature:**
```python
def calculate_commission_amounts(invoice_id, transaction_type_id, product_id, insurer_id, sales_agent_id,
                               invoice_amount, paid_amount, calculation_mode=None, user=None):
```

**Change To:**
```python
def calculate_commission_amounts(issued_policy_id, transaction_type_id, product_id, insurer_id, sales_agent_id,
                               invoice_amount, paid_amount, calculation_mode=None, user=None):
```

**Changes in Function Body:**

**Line 49-64:** Change invoice lookup to issued_policy lookup
```python
# OLD:
invoice = QueryBuilderService("crmf_invoices").select("issued_policy_id").where("id", invoice_id_value).first()
if invoice and invoice.get("issued_policy_id"):
    policy_base = QueryBuilderService("crmp_issued_policies").select("policy_base_id").where("id", invoice["issued_policy_id"]).first()

# NEW:
issued_policy = QueryBuilderService("crmp_issued_policies").select("policy_base_id").where("id", issued_policy_id).first()
if issued_policy and issued_policy.get("policy_base_id"):
    policy_base_data = QueryBuilderService("crmp_policy_base").select("product_id", "product_group_id").where("id", issued_policy["policy_base_id"]).first()
```

**Line 132-146:** Change brokerage commission insert
```python
# OLD:
brokerage_insert_data = {
    "invoice_id": invoice,
    ...
}

# NEW:
brokerage_insert_data = {
    "issued_policy_id": issued_policy_id,
    "invoice_id": None,  # Optional for backward compatibility
    ...
}
```

**Line 379-399:** Update journal entry creation
```python
# OLD:
invoice_obj = QueryBuilderService("crmf_invoices").where("id", invoice_id_value).first()
create_brokerage_commission_journal_entry(brokerage_commission, invoice_obj, user, realized=False)

# NEW:
issued_policy_obj = QueryBuilderService("crmp_issued_policies").where("id", issued_policy_id).first()
# Get invoice for journal entry if needed
invoice_obj = QueryBuilderService("crmf_invoices").where("issued_policy_id", issued_policy_id).first()
create_brokerage_commission_journal_entry(brokerage_commission, invoice_obj, user, realized=False)
```

---

### 2.2 Invoice Generation Call
**File:** `envoy_bu_policy_api/finance/controllers/utils/invoice_utils.py`

**Line 763-773:** Change function call
```python
# OLD:
commission_result = calculate_commission_amounts(
    invoice_id=invoice_id,
    transaction_type_id=transaction_type["id"],
    ...
)

# NEW:
commission_result = calculate_commission_amounts(
    issued_policy_id=issued_id,  # Use issued_policy_id instead
    transaction_type_id=transaction_type["id"],
    ...
)
```

**Line 755:** Change commission existence check
```python
# OLD:
existing_brokerage = QueryBuilderService("crmf_brokerage_commission").where("invoice_id", invoice_id).first()

# NEW:
existing_brokerage = QueryBuilderService("crmf_brokerage_commission").where("issued_policy_id", issued_id).first()
```

---

## 3. Payment Update Changes

### 3.1 Payment Controller
**File:** `envoy_bu_policy_api/finance/controllers/payment_controller.py`

**Line 682-690:** Change commission lookup
```python
# OLD:
brokerage_commission = QueryBuilderService("crmf_brokerage_commission").where("invoice_id", data["invoice_id"]).first()

# NEW:
# Get issued_policy_id from invoice first
invoice = QueryBuilderService("crmf_invoices").where("id", data["invoice_id"]).first()
if invoice and invoice.get("issued_policy_id"):
    brokerage_commission = QueryBuilderService("crmf_brokerage_commission").where("issued_policy_id", invoice["issued_policy_id"]).first()
```

**Update function calls:**
```python
# OLD:
update_revenue_realized('crmf_brokerage_commission', brokerage_commission["id"], invoice_id=data["invoice_id"], paid_amount=total_paid_amount)
update_agent_commission_revenue_realized_for_brokerage_payment(brokerage_commission["id"], data["invoice_id"], total_paid_amount, calculation_mode)

# NEW:
update_revenue_realized('crmf_brokerage_commission', brokerage_commission["id"], issued_policy_id=invoice["issued_policy_id"], paid_amount=total_paid_amount)
update_agent_commission_revenue_realized_for_brokerage_payment(brokerage_commission["id"], invoice["issued_policy_id"], total_paid_amount, calculation_mode)
```

---

### 3.2 Revenue Realized Update Function
**File:** `envoy_bu_policy_api/finance/controllers/utils/commission/commission_pay_utils.py`

**Function:** `update_revenue_realized()`

**Change signature:**
```python
# OLD:
def update_revenue_realized(table_name, record_id, amount=None, invoice_id=None, paid_amount=None):

# NEW:
def update_revenue_realized(table_name, record_id, amount=None, invoice_id=None, issued_policy_id=None, paid_amount=None):
```

**Update logic:**
```python
# OLD:
if table_name == 'crmf_brokerage_commission':
    if invoice_id is None or paid_amount is None:
        return False
    invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()

# NEW:
if table_name == 'crmf_brokerage_commission':
    if issued_policy_id is None or paid_amount is None:
        return False
    
    # Get invoice from issued_policy to get invoice_amount
    issued_policy = QueryBuilderService("crmp_issued_policies").where("id", issued_policy_id).first()
    if not issued_policy:
        return False
    
    # Get invoice for this policy (may have multiple invoices for same policy)
    # Use the latest invoice or sum all invoices
    invoice = QueryBuilderService("crmf_invoices").where("issued_policy_id", issued_policy_id).orderBy("created_at", "desc").first()
    if not invoice:
        # Fallback: use premium_amount from issued_policy
        invoice_amount = Decimal(str(issued_policy.get("premium_amount", "0.00")))
    else:
        invoice_amount = Decimal(str(invoice.get("invoice_amount", "0.00")))
```

**Function:** `update_agent_commission_revenue_realized_for_brokerage_payment()`

**Change signature:**
```python
# OLD:
def update_agent_commission_revenue_realized_for_brokerage_payment(brokerage_commission_id, invoice_id, paid_amount, calculation_mode=None):

# NEW:
def update_agent_commission_revenue_realized_for_brokerage_payment(brokerage_commission_id, issued_policy_id, paid_amount, calculation_mode=None):
```

**Update logic:**
```python
# OLD:
invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id).first()
invoice_amount = Decimal(str(invoice["invoice_amount"]))

# NEW:
issued_policy = QueryBuilderService("crmp_issued_policies").where("id", issued_policy_id).first()
invoice = QueryBuilderService("crmf_invoices").where("issued_policy_id", issued_policy_id).orderBy("created_at", "desc").first()
if invoice:
    invoice_amount = Decimal(str(invoice.get("invoice_amount", "0.00")))
else:
    invoice_amount = Decimal(str(issued_policy.get("premium_amount", "0.00")))
```

---

## 4. Commission Query Changes

### 4.1 Brokerage Commission Controller
**File:** `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`

**Line 55:** Change join
```python
# OLD:
.leftJoin("crmf_invoices", "crmf_invoices.id", "crmf_brokerage_commission.invoice_id")
.leftJoin("crmp_issued_policies", "crmp_issued_policies.id", "crmf_invoices.issued_policy_id")

# NEW:
.leftJoin("crmp_issued_policies", "crmp_issued_policies.id", "crmf_brokerage_commission.issued_policy_id")
.leftJoin("crmf_invoices", "crmf_invoices.issued_policy_id", "crmp_issued_policies.id")  # Optional join for invoice data
```

**Line 69:** Update insurer join
```python
# OLD:
.leftJoin("core_service_providers", "crmf_invoices.insurer_id", "core_service_providers.id")

# NEW:
.leftJoin("core_service_providers", "crmp_issued_policies.insurer_id", "core_service_providers.id")
```

**Line 84:** Update filter
```python
# OLD:
.whereNotIn("crmf_invoices.transaction_type_id", [4, 5])

# NEW:
# Filter by policy status or get transaction_type from invoice if needed
# Option 1: Filter via invoice join
.leftJoin("crmf_invoices as inv", "inv.issued_policy_id", "crmp_issued_policies.id")
.whereNotIn("inv.transaction_type_id", [4, 5])
# Option 2: Filter by policy status if available
```

---

### 4.2 Agent Commission Controller
**File:** `envoy_bu_policy_api/finance/controllers/agent_commission_controller.py`

**Line 78:** Change join
```python
# OLD:
.leftJoin("crmf_invoices", "crmf_invoices.id", "crmf_brokerage_commission.invoice_id")
.leftJoin("crmp_issued_policies", "crmp_issued_policies.id", "crmf_invoices.issued_policy_id")

# NEW:
.leftJoin("crmp_issued_policies", "crmp_issued_policies.id", "crmf_brokerage_commission.issued_policy_id")
.leftJoin("crmf_invoices", "crmf_invoices.issued_policy_id", "crmp_issued_policies.id")
```

---

## 5. Deduction Utils Changes

### 5.1 Deduction Handler
**File:** `envoy_bu_policy_api/finance/controllers/utils/commission/deduction_utils.py`

**Function:** `handle_commission_deduction()`

**Line 545:** Change signature
```python
# OLD:
def handle_commission_deduction(invoice_id, transaction_type_id, product_id, insurer_id, sales_agent_id,
                              invoice_amount, paid_amount, calculation_mode=None, user=None):

# NEW:
def handle_commission_deduction(issued_policy_id, transaction_type_id, product_id, insurer_id, sales_agent_id,
                              invoice_amount, paid_amount, calculation_mode=None, user=None):
```

**Line 580-592:** Update lookup logic
```python
# OLD:
invoice = QueryBuilderService("crmf_invoices").where("id", invoice_id_value).first()
issued_policy_id = invoice.get("issued_policy_id")
original_invoice, original_brokerage = find_original_new_business_commission(issued_policy_id)

# NEW:
issued_policy = QueryBuilderService("crmp_issued_policies").where("id", issued_policy_id).first()
original_invoice, original_brokerage = find_original_new_business_commission(issued_policy_id)
```

**Function:** `find_original_new_business_commission()`

**Line 16-44:** Update to use issued_policy_id directly
```python
# OLD:
def find_original_new_business_commission(issued_policy_id):
    # Find New Business or Renewal invoice
    original_invoice = (
        QueryBuilderService("crmf_invoices")
        .where("issued_policy_id", issued_policy_id)
        .whereIn("transaction_type_id", [1, 3])  # New Business (1) or Renewal (3)
        .orderBy("created_at", "asc")
        .first()
    )
    if not original_invoice:
        return None, None
    
    original_brokerage = QueryBuilderService("crmf_brokerage_commission").where("invoice_id", original_invoice["id"]).first()

# NEW:
def find_original_new_business_commission(issued_policy_id):
    # Find commission directly by issued_policy_id
    original_brokerage = QueryBuilderService("crmf_brokerage_commission").where("issued_policy_id", issued_policy_id).first()
    
    if not original_brokerage:
        return None, None
    
    # Get invoice for reference if needed
    original_invoice = (
        QueryBuilderService("crmf_invoices")
        .where("issued_policy_id", issued_policy_id)
        .whereIn("transaction_type_id", [1, 3])
        .orderBy("created_at", "asc")
        .first()
    )
    
    return original_invoice, original_brokerage
```

**Function:** `apply_commission_deduction()`

**Line 180-213:** Update references
```python
# OLD:
original_invoice_id = brokerage.get("invoice_id")
original_invoice = QueryBuilderService("crmf_invoices").where("id", original_invoice_id).first()

# NEW:
issued_policy_id = brokerage.get("issued_policy_id")
issued_policy = QueryBuilderService("crmp_issued_policies").where("id", issued_policy_id).first()
original_invoice = QueryBuilderService("crmf_invoices").where("issued_policy_id", issued_policy_id).first()
```

---

## 6. Additional Considerations

### 6.1 Multiple Invoices Per Policy
**Issue:** One policy can have multiple invoices (New Business, Renewal, Addition, etc.)

**Solution Options:**

**Option A: One Commission Per Policy (Recommended)**
- Create commission once when policy is issued
- Update `revenue_realized` based on total payments across all invoices
- Sum all invoice amounts for calculation

**Option B: Commission Per Invoice**
- Keep current structure but link via issued_policy_id
- Each invoice creates/updates commission separately
- More complex but maintains invoice-level tracking

**Recommended: Option A** - One commission per policy simplifies tracking

### 6.2 Payment Calculation
**Current:** `revenue_realized = revenue_recognized × (paid_amount / invoice_amount)`

**New Approach:**
```python
# Sum all payments for this policy
total_paid = sum of all payments for all invoices of this policy
total_invoice_amount = sum of all invoice amounts for this policy
revenue_realized = revenue_recognized × (total_paid / total_invoice_amount)
```

### 6.3 Journal Entries
**Update:** Journal entries may need to reference issued_policy instead of invoice
- Check `create_brokerage_commission_journal_entry()` function
- Check `create_agent_commission_journal_entry()` function

---

## 7. Migration Steps

### Step 1: Database Migration
1. Add `issued_policy_id` column to `crmf_brokerage_commission`
2. Populate from existing `invoice_id` → `issued_policy_id` mapping
3. Add foreign key constraint
4. Add unique constraint

### Step 2: Code Changes
1. Update models
2. Update calculation functions
3. Update payment handlers
4. Update query builders
5. Update controllers

### Step 3: Testing
1. Test commission creation for new policies
2. Test payment updates
3. Test refund/cancellation deductions
4. Test commission queries and displays

### Step 4: Data Validation
1. Verify all commissions have `issued_policy_id`
2. Verify payment calculations are correct
3. Verify historical data integrity

### Step 5: Cleanup (Optional)
1. Remove `invoice_id` column after migration period
2. Update all references to use `issued_policy_id` only

---

## 8. Files to Modify

### Models
- [ ] `envoy_bu_policy_api/finance/models/crmf_brokerage_commission.py`

### Commission Calculation
- [ ] `envoy_bu_policy_api/finance/controllers/utils/commission/main.py`
- [ ] `envoy_bu_policy_api/finance/controllers/utils/commission/deduction_utils.py`
- [ ] `envoy_bu_policy_api/finance/controllers/utils/commission/commission_pay_utils.py`
- [ ] `envoy_bu_policy_api/finance/controllers/utils/invoice_utils.py`

### Controllers
- [ ] `envoy_bu_policy_api/finance/controllers/payment_controller.py`
- [ ] `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`
- [ ] `envoy_bu_policy_api/finance/controllers/agent_commission_controller.py`

### Journal Entries
- [ ] `envoy_bu_policy_api/finance/controllers/utils/commission/commission_journal_utils.py`

---

## 9. Benefits of This Change

1. **Simpler Structure:** One commission per policy instead of per invoice
2. **Better Tracking:** Commissions tied directly to policies
3. **Easier Aggregation:** Sum payments across all invoices for one policy
4. **Clearer Logic:** Policy is the source of truth, not individual invoices

---

## 10. Potential Issues & Solutions

### Issue 1: Multiple Invoices Per Policy
**Solution:** Sum all invoice amounts and payments for calculation

### Issue 2: Refund/Cancellation Invoices
**Solution:** Still link to same `issued_policy_id`, use invoice for transaction type

### Issue 3: Historical Data
**Solution:** Keep `invoice_id` as optional field during migration period

---

## Summary

This migration changes the commission structure from invoice-centric to policy-centric. The main changes are:
1. Database: Add `issued_policy_id` to `crmf_brokerage_commission`
2. Models: Change OneToOneField from Invoice to IssuedPolicy
3. Calculations: Use `issued_policy_id` instead of `invoice_id`
4. Payments: Aggregate payments across all invoices for a policy
5. Queries: Join via `issued_policy_id` instead of `invoice_id`

