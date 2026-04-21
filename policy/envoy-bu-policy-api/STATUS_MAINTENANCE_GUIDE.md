# Status Maintenance Guide - Brokerage & Agent Commission

## Overview
This guide explains how to maintain and update statuses for both Brokerage Commission and Agent Commission throughout the application lifecycle.

---

## 1. Brokerage Commission Status Maintenance

### 1.1 Status Calculation Function

**Location:** `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`

```python
def calculate_brokerage_commission_status(customer_settlements, revenue_realized, revenue_recognized):
    """
    Calculate status based on customer settlements and insurer payments.
    
    Status Logic:
    - "pending": No commission received yet (no customer settlements OR customer settled but insurer hasn't paid)
    - "partially_received": Customer partial payment, insurer partial payment
    - "received_in_full": Customer full payment, commission received in full
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
        # Fallback
        return "pending"
```

### 1.2 When to Update Status

#### A. When Customer Makes Payment
**Location:** `envoy_bu_policy_api/finance/controllers/payment_controller.py`

**Current Code (Line ~719):**
```python
# After updating customer_settlements
update_customer_settlements('crmf_brokerage_commission', brokerage_commission["id"], 
                          invoice_id=data["invoice_id"], paid_amount=total_paid_amount)

# ADD: Recalculate and update status
brokerage_commission_updated = QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission["id"]).first()
if brokerage_commission_updated:
    status = calculate_brokerage_commission_status(
        brokerage_commission_updated.get("customer_settlements", 0),
        brokerage_commission_updated.get("revenue_realized", 0),
        brokerage_commission_updated.get("revenue_recognized", 0)
    )
    QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission["id"]).update({"status": status})
```

#### B. When Insurer Payment is Recorded (Manual Update)
**Location:** `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`

**In the `brokerage_commission_update()` function:**
```python
@csrf_exempt
@api_view(["PUT", "PATCH"])
@parser_classes([JSONParser])
def brokerage_commission_update(request, commission_id):
    # ... existing code ...
    
    if "revenue_realized" in data:
        revenue_realized = Decimal(str(data["revenue_realized"]))
        customer_settlements = Decimal(str(commission.get("customer_settlements", 0)))
        revenue_recognized = Decimal(str(commission.get("revenue_recognized", 0)))
        
        # Calculate and set status
        status = calculate_brokerage_commission_status(
            customer_settlements,
            revenue_realized,
            revenue_recognized
        )
        update_data["revenue_realized"] = str(revenue_realized)
        update_data["status"] = status  # Update status automatically
```

#### C. When Commission is Created
**Location:** `envoy_bu_policy_api/finance/controllers/utils/commission/main.py`

**After creating brokerage commission:**
```python
# After creating brokerage commission record
brokerage_commission_id = QueryBuilderService("crmf_brokerage_commission").insert(commission_data)

# Set initial status
from envoy_bu_policy_api.finance.controllers.brokerage_commission_controller import calculate_brokerage_commission_status

initial_status = calculate_brokerage_commission_status(
    customer_settlements=0,  # No customer settlements yet
    revenue_realized=0,      # No insurer payment yet
    revenue_recognized=commission_data.get("revenue_recognized", 0)
)

QueryBuilderService("crmf_brokerage_commission").where("id", brokerage_commission_id).update({"status": initial_status})
```

#### D. In List/Detail Endpoints (On-the-fly Calculation)
**Location:** `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`

**In `get_all_brokerage_commissions()` and `brokerage_commission_detail()`:**
```python
# Option 1: Calculate on-the-fly (for display only, doesn't update DB)
for row in data['data']:
    status = calculate_brokerage_commission_status(
        row.get('customer_settlements', 0),
        row.get('revenue_realized', 0),
        row.get('revenue_recognized', 0)
    )
    row['status'] = status  # Override status in response

# Option 2: Update database status (recommended for consistency)
for row in data['data']:
    status = calculate_brokerage_commission_status(
        row.get('customer_settlements', 0),
        row.get('revenue_realized', 0),
        row.get('revenue_recognized', 0)
    )
    # Update in database if status changed
    if row.get('status') != status:
        QueryBuilderService("crmf_brokerage_commission").where("id", row['id']).update({"status": status})
    row['status'] = status
```

### 1.3 Helper Function to Update Status

**Location:** `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`

```python
def update_brokerage_commission_status(commission_id):
    """
    Recalculate and update brokerage commission status.
    Call this whenever customer_settlements or revenue_realized changes.
    """
    commission = QueryBuilderService("crmf_brokerage_commission").where("id", commission_id).first()
    if not commission:
        return False
    
    status = calculate_brokerage_commission_status(
        commission.get("customer_settlements", 0),
        commission.get("revenue_realized", 0),
        commission.get("revenue_recognized", 0)
    )
    
    result = QueryBuilderService("crmf_brokerage_commission").where("id", commission_id).update({"status": status})
    return bool(result)
```

---

## 2. Agent Commission Status Maintenance

### 2.1 Status Calculation Function

**Location:** `envoy_bu_policy_api/finance/controllers/agent_commission_controller.py`

```python
def calculate_agent_commission_status(revenue_recognized, revenue_realized):
    """
    Calculate status based on payment made to agent by broker.
    
    Status Logic:
    - "pending": Broker hasn't done any settlements to agent
    - "partially_paid": Broker has done partial settlements to agent
    - "fully_paid": Broker has done full settlement to agent
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

### 2.2 When to Update Status

#### A. When Agent Commission Payment is Made
**Location:** `envoy_bu_policy_api/finance/controllers/agent_commission_payment_controller.py`

**In `create_agent_commission_payment()` function:**
```python
# After creating agent commission payment
# Update revenue_realized for the agent commission
agent_commission = QueryBuilderService("crmf_agent_commission").where("id", commission_id).first()
current_realized = Decimal(str(agent_commission.get("revenue_realized", 0)))
new_realized = current_realized + Decimal(str(payment_amount))

# Update revenue_realized
QueryBuilderService("crmf_agent_commission").where("id", commission_id).update({
    "revenue_realized": str(new_realized)
})

# ADD: Recalculate and update status
from envoy_bu_policy_api.finance.controllers.agent_commission_controller import calculate_agent_commission_status

status = calculate_agent_commission_status(
    agent_commission.get("revenue_recognized", 0),
    new_realized
)
QueryBuilderService("crmf_agent_commission").where("id", commission_id).update({"status": status})
```

#### B. When Customer Payment Updates Agent Commission
**Location:** `envoy_bu_policy_api/finance/controllers/utils/commission/commission_pay_utils.py`

**In `update_agent_commission_revenue_realized_for_brokerage_payment()` function:**
```python
# After updating revenue_realized for agent commission
update_data = {
    "revenue_realized": str(new_realized),
    "paid_amount": str(new_realized)
}

update_result = QueryBuilderService("crmf_agent_commission").where("id", agent_comm["id"]).update(update_data)

# ADD: Update status
from envoy_bu_policy_api.finance.controllers.agent_commission_controller import calculate_agent_commission_status

status = calculate_agent_commission_status(
    recognized_value,  # revenue_recognized
    new_realized       # revenue_realized
)
QueryBuilderService("crmf_agent_commission").where("id", agent_comm["id"]).update({"status": status})
```

#### C. When Agent Commission is Created
**Location:** `envoy_bu_policy_api/finance/controllers/utils/commission/main.py`

**After creating agent commission record:**
```python
# After creating agent commission record
agent_commission_id = QueryBuilderService("crmf_agent_commission").insert(agent_commission_data)

# Set initial status
from envoy_bu_policy_api.finance.controllers.agent_commission_controller import calculate_agent_commission_status

initial_status = calculate_agent_commission_status(
    revenue_recognized=agent_commission_data.get("revenue_recognized", 0),
    revenue_realized=0  # No payment to agent yet
)

QueryBuilderService("crmf_agent_commission").where("id", agent_commission_id).update({"status": initial_status})
```

#### D. In List/Detail Endpoints (On-the-fly Calculation)
**Location:** `envoy_bu_policy_api/finance/controllers/agent_commission_controller.py`

**In `agent_commission_list()` and `agent_commission_detail()`:**
```python
# Option 1: Calculate on-the-fly (for display only)
for row in data['data']:
    status = calculate_agent_commission_status(
        row.get('revenue_recognized', 0),
        row.get('revenue_realized', 0)
    )
    row['status'] = status  # Override status in response

# Option 2: Update database status (recommended)
for row in data['data']:
    status = calculate_agent_commission_status(
        row.get('revenue_recognized', 0),
        row.get('revenue_realized', 0)
    )
    # Update in database if status changed
    if row.get('status') != status:
        QueryBuilderService("crmf_agent_commission").where("id", row['id']).update({"status": status})
    row['status'] = status
```

### 2.3 Helper Function to Update Status

**Location:** `envoy_bu_policy_api/finance/controllers/agent_commission_controller.py`

```python
def update_agent_commission_status(commission_id):
    """
    Recalculate and update agent commission status.
    Call this whenever revenue_realized changes.
    """
    commission = QueryBuilderService("crmf_agent_commission").where("id", commission_id).first()
    if not commission:
        return False
    
    status = calculate_agent_commission_status(
        commission.get("revenue_recognized", 0),
        commission.get("revenue_realized", 0)
    )
    
    result = QueryBuilderService("crmf_agent_commission").where("id", commission_id).update({"status": status})
    return bool(result)
```

---

## 3. Status Update Flow Diagrams

### 3.1 Brokerage Commission Status Update Flow

```
Customer Payment
    ↓
update_customer_settlements()
    ↓
customer_settlements updated
    ↓
calculate_brokerage_commission_status()
    ↓
status updated in DB
    ↓
Response with updated status

OR

Insurer Payment Recorded
    ↓
PUT /brokerage-commissions/{id}
    ↓
revenue_realized updated
    ↓
calculate_brokerage_commission_status()
    ↓
status updated in DB
    ↓
Response with updated status
```

### 3.2 Agent Commission Status Update Flow

```
Agent Commission Payment
    ↓
create_agent_commission_payment()
    ↓
revenue_realized updated
    ↓
calculate_agent_commission_status()
    ↓
status updated in DB
    ↓
Response with updated status

OR

Customer Payment (affects agent commission)
    ↓
update_agent_commission_revenue_realized_for_brokerage_payment()
    ↓
revenue_realized updated
    ↓
calculate_agent_commission_status()
    ↓
status updated in DB
```

---

## 4. Best Practices

### 4.1 Always Update Status When Values Change

**DO:**
```python
# Update the value
QueryBuilderService("crmf_brokerage_commission").where("id", id).update({
    "revenue_realized": new_value
})

# Immediately update status
status = calculate_brokerage_commission_status(...)
QueryBuilderService("crmf_brokerage_commission").where("id", id).update({"status": status})
```

**DON'T:**
```python
# Update the value but forget to update status
QueryBuilderService("crmf_brokerage_commission").where("id", id).update({
    "revenue_realized": new_value
})
# Status is now out of sync!
```

### 4.2 Use Helper Functions

Instead of duplicating status calculation logic, use helper functions:

```python
# Good
from envoy_bu_policy_api.finance.controllers.brokerage_commission_controller import update_brokerage_commission_status
update_brokerage_commission_status(commission_id)

# Bad - Duplicated logic
status = calculate_brokerage_commission_status(...)
QueryBuilderService(...).update({"status": status})
```

### 4.3 Update Status in Database, Not Just in Response

**Option 1: Update in DB (Recommended)**
```python
# Calculate and persist status
status = calculate_status(...)
QueryBuilderService(...).update({"status": status})
```

**Option 2: Calculate on-the-fly (Only for display)**
```python
# Only for display, doesn't persist
status = calculate_status(...)
row['status'] = status  # Only in response
```

**Recommendation:** Use Option 1 to maintain data consistency. Use Option 2 only if you need real-time calculation without DB writes.

### 4.4 Handle Edge Cases

```python
def calculate_brokerage_commission_status(customer_settlements, revenue_realized, revenue_recognized):
    from decimal import Decimal
    
    # Handle None values
    customer_settlements = Decimal(str(customer_settlements or 0))
    revenue_realized = Decimal(str(revenue_realized or 0))
    revenue_recognized = Decimal(str(revenue_recognized or 0))
    
    # Handle negative values (shouldn't happen, but be safe)
    if customer_settlements < 0:
        customer_settlements = Decimal("0")
    if revenue_realized < 0:
        revenue_realized = Decimal("0")
    
    # ... rest of logic
```

### 4.5 Batch Status Updates

If updating multiple records, consider batch updates:

```python
# For multiple brokerage commissions
commissions = QueryBuilderService("crmf_brokerage_commission").whereIn("id", commission_ids).get()
for commission in commissions:
    status = calculate_brokerage_commission_status(...)
    QueryBuilderService("crmf_brokerage_commission").where("id", commission['id']).update({"status": status})
```

---

## 5. Status Update Checklist

### When Implementing Status Updates:

- [ ] Status calculation function is defined
- [ ] Status is updated when `customer_settlements` changes (brokerage)
- [ ] Status is updated when `revenue_realized` changes (both)
- [ ] Status is updated when commission is created
- [ ] Status is updated in list/detail endpoints (either on-the-fly or in DB)
- [ ] Helper functions are used to avoid code duplication
- [ ] Edge cases (None, negative values) are handled
- [ ] Status choices are updated in model
- [ ] Database migration includes new status values
- [ ] Tests cover all status scenarios

---

## 6. Example: Complete Implementation

### Brokerage Commission Update in Payment Controller

```python
# In payment_controller.py - create_payment()
from envoy_bu_policy_api.finance.controllers.brokerage_commission_controller import (
    update_brokerage_commission_status
)

# After customer payment
brokerage_commission = QueryBuilderService("crmf_brokerage_commission").where("invoice_id", data["invoice_id"]).first()
if brokerage_commission:
    # Update customer_settlements
    update_customer_settlements('crmf_brokerage_commission', brokerage_commission["id"], 
                               invoice_id=data["invoice_id"], paid_amount=total_paid_amount)
    
    # Update status
    update_brokerage_commission_status(brokerage_commission["id"])
```

### Agent Commission Update in Payment Controller

```python
# In payment_controller.py - create_payment()
from envoy_bu_policy_api.finance.controllers.agent_commission_controller import (
    update_agent_commission_status
)

# After updating agent commission revenue_realized
update_agent_commission_revenue_realized_for_brokerage_payment(...)

# Update status for all affected agent commissions
agent_commissions = QueryBuilderService("crmf_agent_commission").where("brokerage_commission_id", brokerage_commission["id"]).get()
for agent_comm in agent_commissions:
    update_agent_commission_status(agent_comm["id"])
```

---

## 7. Testing Status Updates

### Test Cases for Brokerage Commission:

1. **Initial State:**
   - `customer_settlements = 0, revenue_realized = 0` → status = "pending"

2. **Customer Partial Payment:**
   - `customer_settlements = 5000, revenue_realized = 0` → status = "pending"

3. **Customer Full, Insurer Partial:**
   - `customer_settlements = 10000, revenue_realized = 3000` → status = "partially_received"

4. **Customer Full, Insurer Full:**
   - `customer_settlements = 10000, revenue_realized = 10000` → status = "received_in_full"

5. **Customer Full, Insurer Overpaid:**
   - `customer_settlements = 10000, revenue_realized = 12000` → status = "received_in_full"

### Test Cases for Agent Commission:

1. **Initial State:**
   - `revenue_recognized = 10000, revenue_realized = 0` → status = "pending"

2. **Partial Payment:**
   - `revenue_recognized = 10000, revenue_realized = 5000` → status = "partially_paid"

3. **Full Payment:**
   - `revenue_recognized = 10000, revenue_realized = 10000` → status = "fully_paid"

4. **Overpaid:**
   - `revenue_recognized = 10000, revenue_realized = 12000` → status = "fully_paid"

---

## Summary

**Key Points:**
1. Status should be updated whenever the underlying values change
2. Use helper functions to avoid code duplication
3. Update status in database, not just in API response
4. Handle edge cases (None, negative values)
5. Test all status scenarios
6. Status calculation is independent for brokerage vs agent commission

**Maintenance Points:**
- Brokerage status depends on `customer_settlements` and `revenue_realized`
- Agent status depends only on `revenue_realized` vs `revenue_recognized`
- Always recalculate status after updating these values
- Use helper functions for consistency

