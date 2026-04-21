# Commission Status Implementation Summary

## ✅ Completed Implementation

### 1. Status Configuration Utility Created
**File:** `envoy_bu_policy_api/finance/controllers/utils/commission_status_utils.py`

- ✅ Status configuration stored in `core_status` table (consistent with other statuses)
- ✅ Status retrieval from database with fallback to hardcoded config
- ✅ Status initialization function that creates/updates statuses in `core_status` table
- ✅ Status metadata includes: `name`, `module`, `type`, `color_code`, `description`, `sort_index`
- ✅ Status calculation functions
- ✅ Status update helper functions
- ✅ Status metadata formatting function

### 2. Models Updated

#### Brokerage Commission Model
**File:** `envoy_bu_policy_api/finance/models/crmf_brokerage_commission.py`

- ✅ Added new status choices: `pending`, `partially_received`, `received_in_full`
- ✅ Status field max_length increased to 30
- ✅ Default status changed to `pending`

#### Agent Commission Model
**File:** `envoy_bu_policy_api/finance/models/crmf_agent_commission.py`

- ✅ Added new status choices: `pending`, `partially_paid`, `fully_paid`
- ✅ Status field max_length increased to 30
- ✅ Default status changed to `pending`

### 3. Brokerage Commission Controller Updated
**File:** `envoy_bu_policy_api/finance/controllers/brokerage_commission_controller.py`

- ✅ Imported status utility functions
- ✅ Added `customer_settlements` to column selection
- ✅ Status calculation in list endpoint
- ✅ Status calculation in detail endpoint
- ✅ Status metadata added to all responses
- ✅ New PUT/PATCH endpoint for updating `revenue_realized` with automatic status recalculation

### 4. Status Logic

#### Brokerage Commission Status
Based on payment that brokerage receives from insurer:

| Status | Condition | Description |
|--------|-----------|-------------|
| **pending** | `customer_settlements = 0` OR `revenue_realized = 0` | No commission received yet (no customer settlements OR customer settled but insurer hasn't paid) |
| **partially_received** | `customer_settlements > 0 AND revenue_realized > 0 AND revenue_realized < customer_settlements` | Customer partial payment → insurer partial payment |
| **received_in_full** | `customer_settlements > 0 AND revenue_realized >= customer_settlements` | Customer complete payment → commission received in full |

#### Agent Commission Status
Based on payment made to agent by broker:

| Status | Condition | Description |
|--------|-----------|-------------|
| **pending** | `revenue_realized = 0` | No settlements to agent |
| **partially_paid** | `revenue_realized > 0 AND revenue_realized < revenue_recognized` | Partial settlements to agent |
| **fully_paid** | `revenue_realized >= revenue_recognized` | Full settlement to agent |

### 5. Status Metadata Structure

Each commission record now includes `status_metadata`:

```json
{
  "status": "pending",
  "status_metadata": {
    "status": "pending",
    "name": "Pending",
    "description": "No commission has received yet since there were no settlements done by the customer",
    "type": "brokerage_commission_pending",
    "module": "finance",
    "color_code": "#B54708",
    "color": "#B54708",
    "sort_index": 1
  }
}
```

### 6. Status Colors

**Brokerage Commission:**
- `pending`: `#B54708` (Orange/Warning)
- `partially_received`: `#175CD3` (Blue/Info)
- `received_in_full`: `#067647` (Green/Success)

**Agent Commission:**
- `pending`: `#B54708` (Orange/Warning)
- `partially_paid`: `#175CD3` (Blue/Info)
- `fully_paid`: `#067647` (Green/Success)

## 🔄 Next Steps (To Complete Implementation)

### 1. Update Agent Commission Controller
**File:** `envoy_bu_policy_api/finance/controllers/agent_commission_controller.py`

Need to:
- Import status utility functions
- Add status calculation in list/detail endpoints
- Add status metadata to responses
- Update status when agent commission payment is made

### 2. Update Payment Controller
**File:** `envoy_bu_policy_api/finance/controllers/payment_controller.py`

Need to:
- Update `update_revenue_realized()` to `update_customer_settlements()` for brokerage commission
- Call `update_brokerage_commission_status()` after updating customer_settlements
- Call `update_agent_commission_status()` after updating agent commission revenue_realized

### 3. Update Commission Pay Utils
**File:** `envoy_bu_policy_api/finance/controllers/utils/commission/commission_pay_utils.py`

Need to:
- Rename `update_revenue_realized()` to `update_customer_settlements()` for brokerage commission
- Update field name from `revenue_realized` to `customer_settlements` for brokerage commission
- Add status update calls after updating values

### 4. Update URL Routes
**File:** `envoy_bu_policy_api/finance/urls.py`

Need to:
- Add PUT/PATCH route for brokerage commission update:
```python
path("brokerage-commissions/<int:commission_id>", 
     brokerage_commission_controller.brokerage_commission_update, 
     name="brokerage_commission_update"),
```

### 5. Database Migration

Need to:
- Add `customer_settlements` column to `crmf_brokerage_commission` table
- Migrate existing `revenue_realized` data to `customer_settlements`
- Update status column to allow new values (VARCHAR(30))
- Run `ensure_commission_statuses_exist()` to create status records in `core_status` table

### 6. Initialize Statuses

Run the status initialization function to create/update statuses in `core_status` table:
```python
from envoy_bu_policy_api.finance.controllers.utils.commission_status_utils import ensure_commission_statuses_exist
ensure_commission_statuses_exist()
```

**Note:** Statuses are stored in the `core_status` table (same as other statuses like policy, invoice, payment, etc.). The status configuration functions retrieve status metadata from the database, with hardcoded dictionaries as fallback.

## 📋 API Response Example

### Brokerage Commission Response
```json
{
  "id": 1,
  "revenue_recognized": 10000.00,
  "customer_settlements": 5000.00,
  "revenue_realized": 3000.00,
  "outstanding": 7000.00,
  "status": "partially_received",
  "status_metadata": {
    "status": "partially_received",
    "name": "Partially Received",
    "description": "Customer has done a part payment so the insurer has paid us partially",
    "type": "brokerage_commission_partially_received",
    "module": "finance",
    "color_code": "#175CD3",
    "color": "#175CD3",
    "sort_index": 2
  }
}
```

### Agent Commission Response
```json
{
  "id": 1,
  "revenue_recognized": 5000.00,
  "revenue_realized": 3000.00,
  "status": "partially_paid",
  "status_metadata": {
    "status": "partially_paid",
    "name": "Partially Paid",
    "description": "Broker might or might not have received brokerage commission and has done partial settlements to the agent",
    "type": "agent_commission_partially_paid",
    "module": "finance",
    "color_code": "#175CD3",
    "color": "#175CD3",
    "sort_index": 2
  }
}
```

## 🎯 Key Features Implemented

1. ✅ **Status Calculation**: Automatic status calculation based on business rules
2. ✅ **Status Metadata**: Complete metadata (name, module, type, color_code) in API responses
3. ✅ **Status Update Endpoint**: PUT/PATCH endpoint for updating revenue_realized with automatic status recalculation
4. ✅ **Status Configuration**: Centralized status configuration with colors and descriptions
5. ✅ **Status Maintenance**: Helper functions for easy status updates

## 📝 Notes

- **Status Storage**: All statuses are stored in the `core_status` table (same as policy, invoice, payment statuses)
- **Status Retrieval**: Status metadata is retrieved from the database using `type` and `module` fields
- **Fallback**: Hardcoded status configs are used as fallback if database lookup fails
- **Status Calculation**: Status is calculated on-the-fly in list/detail endpoints
- **Status Update**: Status is also updated in database when `revenue_realized` is updated via PUT endpoint
- **Status Metadata**: Status metadata is included in all API responses for easy frontend consumption
- **Status Colors**: Status colors follow the existing color scheme used in the application
- **Consistency**: All statuses follow the same pattern as other statuses in the application (quotation, policy, invoice, payment, claim)

