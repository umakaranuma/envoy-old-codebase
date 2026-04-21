# Brokerage Revenue Realized Changes - Analysis Document

## Overview
This document outlines all the changes required to implement the new revenue realization logic for brokerage commissions. The key change is separating customer settlements from insurer payments, and making revenue realized editable.

## Current State Analysis

### Database Schema (crmf_brokerage_commission table)
**Current Fields:**
- `revenue_recognized` (Decimal): The total commission amount recognized
- `revenue_realized` (Decimal): Currently auto-updated when customer makes payment (proportional to invoice payment)
- `commission_deductible` (Decimal): Deductible amounts
- `status` (CharField): Static choices (draft, issued, paid, overdue, cancelled)
- `outstanding` (Calculated): `revenue_recognized - revenue_realized - commission_deductible`

### Current Flow
1. When a customer makes a payment (via `create_payment()` in `payment_controller.py`):
   - `update_revenue_realized()` is called
   - `revenue_realized` is updated proportionally: `revenue_recognized × (paid_amount / invoice_amount)`
   - This happens automatically in `payment_controller.py` line 719

2. Status is currently static and not dynamically calculated based on outstanding amounts.

---

## Required Changes

### 1. Database Schema Changes

#### 1.1 Rename `revenue_realized` to `customer_settlements`
**File:** Database migration needed

**SQL Migration:**
```sql
-- Step 1: Add new column for customer settlements
ALTER TABLE crmf_brokerage_commission 
ADD COLUMN customer_settlements DECIMAL(20, 2) DEFAULT 0.00;

-- Step 2: Migrate existing revenue_realized data to customer_settlements
UPDATE crmf_brokerage_commission 
SET customer_settlements = revenue_realized;

-- Step 3: Add new revenue_realized column (editable, tracks insurer payments)
ALTER TABLE crmf_brokerage_commission 
ADD COLUMN revenue_realized DECIMAL(20, 2) DEFAULT 0.00;

-- Step 4: (Optional) Rename old column if you want to keep it for reference
-- Or drop it if not needed:
-- ALTER TABLE crmf_brokerage_commission DROP COLUMN revenue_realized_old;
```

**Note:** The new `revenue_realized` will start at 0.00 and be manually editable to track insurer payments.

#### 1.2 Update Outstanding Calculation
**New Outstanding Formula:**
```sql
outstanding = revenue_recognized - revenue_realized - commission_deductible
```

Where:
- `revenue_recognized`: Total commission amount
- `revenue_realized`: Amount paid by insurer to broker (NEW - editable)
- `commission_deductible`: Deductible amounts
- `customer_settlements`: Amount paid by customer (for reference, not used in outstanding)

#### 1.3 Update Status Column Choices

**For Brokerage Commission:**
**Current Status Choices:**
- draft, issued, paid, overdue, cancelled

**New Status Choices:**
- draft, issued, paid, overdue, cancelled, **pending**, **partially_received**, **received_in_full**

**SQL:**
```sql
-- Update status column to allow new values
-- Note: This depends on your database. For MySQL:
ALTER TABLE crmf_brokerage_commission 
MODIFY COLUMN status VARCHAR(30);
```

**For Agent Commission:**
**Current Status Choices:**
- draft, issued, paid, overdue, cancelled

**New Status Choices:**
- draft, issued, paid, overdue, cancelled, **pending**, **partially_paid**, **fully_paid**

**SQL:**
```sql
-- Update status column to allow new values
ALTER TABLE crmf_agent_commission 
MODIFY COLUMN status VARCHAR(30);
```

---

### 2. Django Model Changes

#### 2.1 Update BrokerageCommission Model
**File:** `envoy_bu_policy_api/finance/models/crmf_brokerage_commission.py`

**Changes Required:**
```python
class BrokerageCommission(models.Model):
    # ... existing fields ...
    
    # RENAME: revenue_realized → customer_settlements
    customer_settlements = models.DecimalField(
        max_digits=20, 
        decimal_places=2,
        default=0.00,
        help_text="Amount settled by customer (auto-updated on customer payment)"
    )
    
    # NEW: revenue_realized (editable, tracks insurer payments)
    revenue_realized = models.DecimalField(
        max_digits=20, 
        decimal_places=2,
        default=0.00,
        help_text="Amount paid by insurer to broker (editable)"
    )
    
    # Update STATUS_CHOICES
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending"),                    # NEW - No commission received yet (no customer settlements)
        ("partially_received", "Partially Received"), # NEW - Customer partial payment, insurer partial payment
        ("received_in_full", "Received in Full"),   # NEW - Customer full payment, commission received in full
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="draft")
```

---

### 3. Controller Changes

#### 3.1 Update Payment Controller
**File:** `envoy_bu_policy_api/finance/controllers/payment_controller.py`

**Current Code (Line ~719):**
```python
update_revenue_realized('crmf_brokerage_commission', brokerage_commission["id"], 
                       invoice_id=data["invoice_id"], paid_amount=total_paid_amount)
```

**Change To:**
```python
# Update customer_settlements instead of revenue_realized
update_customer_settlements('crmf_brokerage_commission', brokerage_commission["id"], 
                            invoice_id=data["invoice_id"], paid_amount=total_paid_amount)
```

**New Function Needed:**
Create `update_customer_settlements()` function (similar to `update_revenue_realized()` but updates `customer_settlements` field).

#### 3.2 Update Commission Pay Utils
**File:** `envoy_bu_policy_api/finance/controllers/utils/commission/commission_pay_utils.py`

**Changes:**
1. **Rename function:** `update_revenue_realized()` → `update_customer_settlements()` (for customer payments)
2. **Update field name:** Change `revenue_realized` to `customer_settlements` in the update logic
3. **Keep existing logic:** The proportional calculation remains the same, just updating a different field

**New Function Structure:**
```python
def update_customer_settlements(table_name, record_id, amount=None, invoice_id=None, paid_amount=None):
    """
    Update customer_settlements field (renamed from revenue_realized).
    This tracks customer payments, not insurer payments.
    """
    # Same logic as current update_revenue_realized, but update customer_settlements
    # ...
```

#### 3.3 Update Brokerage Commission Controller
**File:** `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`

**Changes Required:**

1. **Update Column Selection (Line ~40):**
```python
# OLD:
"crmf_brokerage_commission.revenue_realized as brokerage_revenue_realized",

# NEW:
"crmf_brokerage_commission.customer_settlements as customer_settlements",
"crmf_brokerage_commission.revenue_realized as brokerage_revenue_realized",
```

2. **Update Outstanding Calculation (Line ~43):**
```python
# OLD:
"(crmf_brokerage_commission.revenue_recognized - COALESCE(crmf_brokerage_commission.revenue_realized, 0) - COALESCE(crmf_brokerage_commission.commission_deductible, 0)) as outstanding",

# NEW: (Same formula, but ensure it uses the new revenue_realized)
"(crmf_brokerage_commission.revenue_recognized - COALESCE(crmf_brokerage_commission.revenue_realized, 0) - COALESCE(crmf_brokerage_commission.commission_deductible, 0)) as outstanding",
```

3. **Update Totals Queries (Lines ~344, ~463):**
```python
# Update to include customer_settlements in totals if needed
"SUM(crmf_brokerage_commission.customer_settlements) as total_customer_settlements",
"SUM(crmf_brokerage_commission.revenue_realized) as total_revenue_realized",
```

4. **Add Status Calculation Logic:**
Create a new function to calculate status based on customer settlements and insurer payments:
```python
def calculate_brokerage_commission_status(customer_settlements, revenue_realized, revenue_recognized):
    """
    Calculate status based on customer settlements and insurer payments.
    
    Status Logic (based on payment brokerage receives from insurer):
    - "pending": No commission received yet (no customer settlements done)
      → customer_settlements = 0
    - "partially_received": Customer has done part payment, so insurer has paid partially
      → customer_settlements > 0 AND revenue_realized > 0 AND revenue_realized < customer_settlements
    - "received_in_full": Customer has done complete payment, commission received in full
      → customer_settlements > 0 AND revenue_realized >= customer_settlements
    """
    from decimal import Decimal
    
    customer_settlements = Decimal(str(customer_settlements or 0))
    revenue_realized = Decimal(str(revenue_realized or 0))
    revenue_recognized = Decimal(str(revenue_recognized or 0))
    
    # No customer settlements = no commission expected from insurer
    if customer_settlements == 0:
        return "pending"
    
    # Customer has settled, check insurer payment status
    if revenue_realized == 0:
        # Customer settled but insurer hasn't paid yet
        return "pending"
    elif revenue_realized > 0 and revenue_realized < customer_settlements:
        # Insurer paid partially (less than customer settled)
        return "partially_received"
    elif revenue_realized >= customer_settlements:
        # Insurer paid in full (at least what customer settled)
        return "received_in_full"
    else:
        # Fallback (shouldn't happen)
        return "pending"
```

5. **Apply Status in List/Detail Functions:**
Update `get_all_brokerage_commissions()` and `brokerage_commission_detail()` to calculate and include status:
```python
# In get_all_brokerage_commissions() and brokerage_commission_detail()
for row in data['data']:
    # Calculate status based on customer settlements and revenue_realized
    status = calculate_brokerage_commission_status(
        row.get('customer_settlements', 0),
        row.get('revenue_realized', 0),
        row.get('revenue_recognized', 0)
    )
    row['status'] = status
    # Also update in database if needed
    # QueryBuilderService("crmf_brokerage_commission").where("id", row['id']).update({"status": status})
```

#### 3.4 Create Update Endpoint for Brokerage Commission
**File:** `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`

**New Function:**
```python
@csrf_exempt
@api_view(["PUT", "PATCH"])
@parser_classes([JSONParser])
def brokerage_commission_update(request, commission_id):
    """
    Update brokerage commission, specifically revenue_realized (insurer payment).
    This allows manual editing of revenue_realized when insurer pays.
    """
    action_type = "EDIT"
    action = ActionService.getAction("BrokerageCommission", action_type)
    
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    
    try:
        data = json.loads(request.body or "{}")
        
        # Validate commission exists
        commission = QueryBuilderService("crmf_brokerage_commission").where("id", commission_id).first()
        if not commission:
            return ResponseService.response("NOT_FOUND", None, Error.DATA_NOT_FOUND)
        
        # Prepare update data
        update_data = {}
        
        # Allow updating revenue_realized (insurer payment)
        if "revenue_realized" in data:
            revenue_realized = Decimal(str(data["revenue_realized"]))
            # Validate: revenue_realized should not exceed revenue_recognized (unless negative for credit notes)
            revenue_recognized = Decimal(str(commission.get("revenue_recognized", 0)))
            commission_deductible = Decimal(str(commission.get("commission_deductible", 0)))
            
            # Get customer_settlements for status calculation
            customer_settlements = Decimal(str(commission.get("customer_settlements", 0)))
            revenue_recognized = Decimal(str(commission.get("revenue_recognized", 0)))
            
            # Calculate and set status based on customer settlements and insurer payment
            status = calculate_brokerage_commission_status(
                customer_settlements,
                revenue_realized,
                revenue_recognized
            )
            update_data["revenue_realized"] = str(revenue_realized)
            update_data["status"] = status
        
        # Update the commission
        if update_data:
            result = QueryBuilderService("crmf_brokerage_commission").where("id", commission_id).update(update_data)
            
            if result:
                # Return updated commission
                updated_commission = build_base_query().where("crmf_brokerage_commission.id", commission_id).first()
                updated_commission = format_brokerage_commission_percentages(updated_commission)
                return ResponseService.response("SUCCESS", updated_commission, Message.DATA_UPDATED)
            else:
                return ResponseService.response("ERROR", None, "Update failed")
        else:
            return ResponseService.response("VALIDATION_ERROR", {"error": "No valid fields to update"}, "validation_error")
            
    except Exception as e:
        return ResponseService.response("ERROR", {"error": str(e)}, "default_error")
```

**Add to URLs:**
**File:** `envoy_bu_policy_api/finance/urls.py`

```python
# Add PUT endpoint for updating brokerage commission
path("brokerage-commissions/<int:commission_id>", 
     brokerage_commission_controller.brokerage_commission_update, 
     name="brokerage_commission_update"),
```

**Note:** The existing GET endpoint at line 126 uses the same path pattern. You may need to handle both GET and PUT in the same function or use separate paths.

---

### 4. Update Outstanding Calculation Logic

#### 4.1 Update Deduction Utils
**File:** `envoy_bu_policy_api/finance/controllers/utils/commission/deduction_utils.py`

**Current Code (Line ~102, ~115):**
```python
Outstanding = revenue_recognized - revenue_realized - commission_deductible
```

**No Change Needed:** The formula remains the same, but now `revenue_realized` represents insurer payments instead of customer payments.

**However, ensure all references use the correct field:**
- Outstanding calculation: Uses `revenue_realized` (insurer payment)
- Customer settlements: Separate field, not used in outstanding calculation

---

### 5. Update Performance Field Registry
**File:** `envoy_bu_policy_api/finance/config/performance_field_registry.py`

**Current Code (Lines ~430-445):**
```python
{
    "parameter": "brokerage_revenue_realized",
    "base_table": "crmf_brokerage_commission",
    "field": ["revenue_realized"],
    # ...
}
```

**Changes:**
1. Keep existing `brokerage_revenue_realized` pointing to `revenue_realized` (insurer payment)
2. Optionally add new parameter for customer settlements:
```python
{
    "parameter": "brokerage_customer_settlements",
    "base_table": "crmf_brokerage_commission",
    "field": ["customer_settlements"],
    # ... same joins and filters ...
}
```

---

### 6. Update Agent Commission Logic

#### 6.1 Update Agent Commission Model
**File:** `envoy_bu_policy_api/finance/models/crmf_agent_commission.py`

**Changes Required:**
```python
class AgentCommission(models.Model):
    # ... existing fields ...
    
    # Update STATUS_CHOICES
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending"),                    # NEW - No settlements to agent
        ("partially_paid", "Partially Paid"),      # NEW - Partial settlements to agent
        ("fully_paid", "Fully Paid"),              # NEW - Full settlement to agent
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="draft")
```

#### 6.2 Add Agent Commission Status Calculation
**File:** `envoy_bu_policy_api/finance/controllers/agent_commission_controller.py`

**New Function:**
```python
def calculate_agent_commission_status(revenue_recognized, revenue_realized):
    """
    Calculate status based on payment made to agent by broker.
    
    Status Logic (based on payment made to agent by broker):
    - "pending": Broker hasn't done any settlements to agent
      → revenue_realized = 0
    - "partially_paid": Broker has done partial settlements to agent
      → revenue_realized > 0 AND revenue_realized < revenue_recognized
    - "fully_paid": Broker has done full settlement to agent
      → revenue_realized >= revenue_recognized
    
    Note: Status is independent of whether broker received brokerage commission.
    """
    from decimal import Decimal
    
    revenue_recognized = Decimal(str(revenue_recognized or 0))
    revenue_realized = Decimal(str(revenue_realized or 0))
    
    if revenue_realized == 0:
        return "pending"
    elif revenue_realized > 0 and revenue_realized < revenue_recognized:
        return "partially_paid"
    elif revenue_realized >= revenue_recognized:
        return "fully_paid"
    else:
        return "pending"  # Fallback
```

**Update List/Detail Functions:**
Apply status calculation in `agent_commission_list()` and `agent_commission_detail()`:
```python
# In agent commission list/detail functions
for row in data['data']:
    status = calculate_agent_commission_status(
        row.get('revenue_recognized', 0),
        row.get('revenue_realized', 0)
    )
    row['status'] = status
    # Optionally update in database
    # QueryBuilderService("crmf_agent_commission").where("id", row['id']).update({"status": status})
```

#### 6.3 Update Agent Commission Payment Logic
**File:** `envoy_bu_policy_api/finance/controllers/utils/commission/commission_pay_utils.py`

**Current Code (Line ~124):**
The function `update_agent_commission_revenue_realized_for_brokerage_payment()` updates agent commissions when customer makes payment.

**Note:** This function should continue to update `revenue_realized` for agent commissions based on customer payments. The status will be calculated based on the `revenue_realized` value.

**When agent commission payment is made (via agent_commission_payment_controller):**
- Update `revenue_realized` field
- Recalculate status using `calculate_agent_commission_status()`

---

### 7. Frontend/API Response Changes

#### 7.1 Update API Response Structure
**Files:** All brokerage commission endpoints

**Current Response:**
```json
{
  "revenue_recognized": 10000.00,
  "revenue_realized": 5000.00,  // Currently customer settlements
  "outstanding": 5000.00,
  "status": "paid"
}
```

**New Response:**
```json
{
  "revenue_recognized": 10000.00,
  "customer_settlements": 5000.00,  // Customer payments
  "revenue_realized": 3000.00,      // Insurer payments (editable)
  "outstanding": 7000.00,            // revenue_recognized - revenue_realized - commission_deductible
  "status": "partially_settled"     // Calculated based on outstanding
}
```

---

## Status Calculation Logic Details

### Brokerage Commission Status

**Status is based on payment that brokerage receives from insurer.**

| Condition | Status | Description |
|-----------|--------|-------------|
| `customer_settlements = 0` | **pending** | No customer settlements done, so no commission expected from insurer |
| `customer_settlements > 0 AND revenue_realized = 0` | **pending** | Customer has settled but insurer hasn't paid yet |
| `customer_settlements > 0 AND revenue_realized > 0 AND revenue_realized < customer_settlements` | **partially_received** | Customer paid partially, insurer paid partially (less than customer settled) |
| `customer_settlements > 0 AND revenue_realized >= customer_settlements` | **received_in_full** | Customer paid fully, commission received in full from insurer |

**When Status is Updated:**
1. When customer makes payment → `customer_settlements` updated → Recalculate status
2. When insurer payment is recorded → `revenue_realized` updated → Recalculate status

### Agent Commission Status

**Status is based on payment made to agent by broker.**

| Condition | Status | Description |
|-----------|--------|-------------|
| `revenue_realized = 0` | **pending** | Broker hasn't done any settlements to agent |
| `revenue_realized > 0 AND revenue_realized < revenue_recognized` | **partially_paid** | Broker has done partial settlements to agent |
| `revenue_realized >= revenue_recognized` | **fully_paid** | Broker has done full settlement to agent |

**When Status is Updated:**
1. When agent commission payment is made → `revenue_realized` updated → Recalculate status
2. Status is independent of whether broker received brokerage commission

**Note:** Agent commission status reflects payments made to agent, regardless of broker's commission status.

---

## Summary of Changes

### Database Level:
1. ✅ Add `customer_settlements` column
2. ✅ Migrate existing `revenue_realized` data to `customer_settlements`
3. ✅ Reset `revenue_realized` to 0.00 (or keep existing if you want to preserve data)
4. ✅ Update status column to allow new values

### Code Level:
1. ✅ Update Django models:
   - `crmf_brokerage_commission.py` (add customer_settlements, update status choices)
   - `crmf_agent_commission.py` (update status choices)
2. ✅ Rename `update_revenue_realized()` → `update_customer_settlements()` for customer payments
3. ✅ Update `payment_controller.py` to use `update_customer_settlements()`
4. ✅ Update `brokerage_commission_controller.py`:
   - Update column selections
   - Add status calculation function for brokerage commission
   - Create update endpoint for `revenue_realized`
   - Apply status calculation in list/detail functions
5. ✅ Update `agent_commission_controller.py`:
   - Add status calculation function for agent commission
   - Apply status calculation in list/detail functions
6. ✅ Update outstanding calculations (formula stays same, field meaning changes)
7. ✅ Update performance field registry if needed
8. ✅ Add URL route for PUT/PATCH endpoint for brokerage commission

### Business Logic:

**For Brokerage Commission:**
1. ✅ Customer payments → Update `customer_settlements` (automatic)
2. ✅ Insurer payments → Update `revenue_realized` (manual/editable)
3. ✅ Status calculation based on customer settlements and insurer payments:
   - `customer_settlements = 0` → "pending" (no customer payment, no commission expected)
   - `customer_settlements > 0 AND revenue_realized = 0` → "pending" (customer paid but insurer hasn't)
   - `customer_settlements > 0 AND revenue_realized > 0 AND revenue_realized < customer_settlements` → "partially_received"
   - `customer_settlements > 0 AND revenue_realized >= customer_settlements` → "received_in_full"

**For Agent Commission:**
1. ✅ Agent commission `revenue_realized` tracks payments made to agent by broker
2. ✅ Status calculation based on `revenue_realized` vs `revenue_recognized`:
   - `revenue_realized = 0` → "pending" (no payment to agent)
   - `revenue_realized > 0 AND revenue_realized < revenue_recognized` → "partially_paid"
   - `revenue_realized >= revenue_recognized` → "fully_paid"
3. ✅ Status is independent of whether broker received brokerage commission

---

## Testing Checklist

### Brokerage Commission:
1. ✅ Test customer payment flow (should update `customer_settlements` and recalculate status)
2. ✅ Test manual update of `revenue_realized` via PUT endpoint (should recalculate status)
3. ✅ Test status calculation for all scenarios:
   - No customer settlement → "pending"
   - Customer settled but insurer hasn't paid → "pending"
   - Customer partial, insurer partial → "partially_received"
   - Customer full, insurer full → "received_in_full"
4. ✅ Test outstanding calculation
5. ✅ Test existing commission calculations still work

### Agent Commission:
1. ✅ Test agent commission payment flow (should update `revenue_realized` and recalculate status)
2. ✅ Test status calculation for all scenarios:
   - No payment to agent → "pending"
   - Partial payment to agent → "partially_paid"
   - Full payment to agent → "fully_paid"
3. ✅ Verify status is independent of brokerage commission status

### General:
1. ✅ Test performance field registry queries
2. ✅ Test migration script on staging database
3. ✅ Test API responses include correct status values
4. ✅ Test status updates in database when values change

---

## Migration Strategy

1. **Phase 1:** Database migration (add columns, migrate data)
2. **Phase 2:** Update code to use new field names
3. **Phase 3:** Deploy and test
4. **Phase 4:** Update frontend to show both fields and allow editing `revenue_realized`

---

## Notes

### Brokerage Commission:
- The `customer_settlements` field tracks customer payments (auto-updated on customer payment)
- The `revenue_realized` field tracks insurer payments to broker (editable/manual)
- Status is calculated based on customer settlements and insurer payments
- Outstanding calculation: `revenue_recognized - revenue_realized - commission_deductible`
- Status reflects payment received from insurer, not customer payment status

### Agent Commission:
- The `revenue_realized` field tracks payments made to agent by broker
- Status is calculated based on `revenue_realized` vs `revenue_recognized`
- Status reflects payment made to agent, independent of broker's commission status
- Agent commission status is independent of whether broker received brokerage commission

### Status Summary:

**Brokerage Commission Status:**
- **pending**: No commission received from insurer (no customer settlements OR customer settled but insurer hasn't paid)
- **partially_received**: Insurer paid partially (less than customer settled amount)
- **received_in_full**: Insurer paid in full (at least what customer settled)

**Agent Commission Status:**
- **pending**: No payment made to agent
- **partially_paid**: Partial payment made to agent
- **fully_paid**: Full payment made to agent (at least revenue_recognized)

