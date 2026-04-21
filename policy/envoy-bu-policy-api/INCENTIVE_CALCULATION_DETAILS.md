# Incentive Calculation Details

## Overview
This document explains how incentive calculations work in the `incentives/run-all` endpoint, including which tables are used and the calculation scenarios.

## Your Example Incentive Setup

Based on your provided incentive setup:
- **Name**: "sales bonus - december"
- **Period**: 2025-12-01 to 2025-12-10
- **Performance Conditions** (AND logic):
  - `sum_of_premium_amount >= 600000`
  - `role = 2` (Sales Agent)
- **Reward Type**: Percentage (3.0%)
- **Incentive Base Field**: `sum_of_agent_commission_realized`
- **Reward Type Name**: "Total Premium"

## Calculation Flow in `incentives/run-all` Endpoint

### Step 1: Get All Active Incentive Setups
**Location**: `incentive_controller.py:798`
```python
setups = QueryBuilderService("crmf_incentive_setups").whereNull("deleted_at").get()
```
**Table**: `crmf_incentive_setups`

### Step 2: For Each Setup, Get Periods
**Location**: `incentive_controller.py:865`
```python
periods = get_periods_for_setup(setup_dict)
```
- Extracts periods based on `start_date`, `end_date`, and `repeation_type`
- For your example: Single period from 2025-12-01 to 2025-12-10

### Step 3: Find Eligible Agents
**Location**: `incentive_controller.py:926`
```python
agent_ids = find_agents_for_period(setup_dict, (period_start, period_end))
```
- Finds agents who match the performance field conditions
- For your example: Agents with `role_id = 2` who have policies in the period

### Step 4: For Each Agent, Aggregate Performance Data
**Location**: `incentive_controller.py:1011`
```python
performance_data = aggregate_performance_data(agent_id, setup_dict, period)
```

## Performance Data Aggregation

### Tables Used for Your Example

#### 1. `sum_of_premium_amount` (Performance Condition)
**Registry Entry**: `performance_field_registry.py:547-560`

**Base Table**: `crmp_issued_policies`
- **Field Aggregated**: `premium_amount` (SUM)
- **Joins**:
  - `crmp_policy_base` ON `crmp_issued_policies.policy_base_id = crmp_policy_base.id`
  - `core_users` ON `crmp_policy_base.sales_agent_id = core_users.id`

**SQL Query Generated**:
```sql
SELECT COALESCE(SUM(crmp_issued_policies.premium_amount), 0) as premium_amount
FROM crmp_issued_policies
JOIN crmp_policy_base ON crmp_issued_policies.policy_base_id = crmp_policy_base.id
JOIN core_users ON crmp_policy_base.sales_agent_id = core_users.id
WHERE crmp_policy_base.sales_agent_id = [agent_id]
  AND crmp_issued_policies.policy_effective_date >= '2025-12-01'
  AND crmp_issued_policies.policy_effective_date <= '2025-12-10'
```

**What It Does**: Sums all premium amounts from issued policies for the agent within the date range.

#### 2. `sum_of_agent_commission_realized` (Incentive Base Field)
**Registry Entry**: `performance_field_registry.py:831-847`

**Base Table**: `crmf_agent_commission`
- **Field Aggregated**: `revenue_realized` (SUM)
- **Joins**:
  - `crmf_brokerage_commission` ON `crmf_brokerage_commission.id = crmf_agent_commission.brokerage_commission_id`
  - `crmf_invoices` ON `crmf_invoices.id = crmf_brokerage_commission.invoice_id`
  - `crmp_issued_policies` ON `crmp_issued_policies.id = crmf_invoices.issued_policy_id`
  - `crmp_policy_base` ON `crmp_policy_base.id = crmp_issued_policies.policy_base_id`
  - `core_users` ON `crmp_policy_base.sales_agent_id = core_users.id`

**SQL Query Generated**:
```sql
SELECT COALESCE(SUM(crmf_agent_commission.revenue_realized), 0) as revenue_realized
FROM crmf_agent_commission
JOIN crmf_brokerage_commission ON crmf_brokerage_commission.id = crmf_agent_commission.brokerage_commission_id
JOIN crmf_invoices ON crmf_invoices.id = crmf_brokerage_commission.invoice_id
JOIN crmp_issued_policies ON crmp_issued_policies.id = crmf_invoices.issued_policy_id
JOIN crmp_policy_base ON crmp_policy_base.id = crmp_issued_policies.policy_base_id
JOIN core_users ON crmp_policy_base.sales_agent_id = core_users.id
WHERE crmp_policy_base.sales_agent_id = [agent_id]
  AND crmp_issued_policies.policy_effective_date >= '2025-12-01'
  AND crmp_issued_policies.policy_effective_date <= '2025-12-10'
```

**What It Does**: Sums all realized agent commission revenue from agent commission records linked to policies for the agent within the date range.

#### 3. `role` (Filter Condition)
**Location**: `incentive_utils.py:836-857`

**Table**: `core_users`
- **Field Checked**: `role_id`
- **Query**: Direct check against agent's role_id in `core_users` table

**What It Does**: Verifies the agent has `role_id = 2` (Sales Agent).

## Calculation Scenarios

### Scenario 1: Agent Meets All Conditions

**Example**:
- Agent ID: 100
- Role: 2 (Sales Agent) ✓
- `sum_of_premium_amount` (Dec 1-10): 750,000 ✓ (>= 600,000)
- `sum_of_agent_commission_realized` (Dec 1-10): 10,000

**Calculation**:
1. **Check Conditions**:
   - `sum_of_premium_amount >= 600000`: 750,000 >= 600,000 → **TRUE**
   - `role = 2`: Agent role_id = 2 → **TRUE**
   - All conditions met → **ELIGIBLE**

2. **Calculate Reward** (Percentage Type):
   ```
   incentive_amount = (incentive_base_field_value × reward_type_value) / 100
   incentive_amount = (10,000 × 3.0) / 100
   incentive_amount = 300.00
   ```

3. **Result**: Agent receives **$300.00** incentive

### Scenario 2: Agent Doesn't Meet Premium Threshold

**Example**:
- Agent ID: 101
- Role: 2 (Sales Agent) ✓
- `sum_of_premium_amount` (Dec 1-10): 500,000 ✗ (< 600,000)
- `sum_of_agent_commission_realized` (Dec 1-10): 8,000

**Calculation**:
1. **Check Conditions**:
   - `sum_of_premium_amount >= 600000`: 500,000 >= 600,000 → **FALSE**
   - `role = 2`: Agent role_id = 2 → **TRUE**
   - Not all conditions met → **NOT ELIGIBLE**

2. **Result**: Agent receives **$0.00** (not eligible)

### Scenario 3: Agent Has Wrong Role

**Example**:
- Agent ID: 102
- Role: 3 (Manager) ✗
- `sum_of_premium_amount` (Dec 1-10): 800,000 ✓
- `sum_of_agent_commission_realized` (Dec 1-10): 12,000

**Calculation**:
1. **Check Conditions**:
   - `sum_of_premium_amount >= 600000`: 800,000 >= 600,000 → **TRUE**
   - `role = 2`: Agent role_id = 3 → **FALSE**
   - Not all conditions met → **NOT ELIGIBLE**

2. **Result**: Agent receives **$0.00** (not eligible)

### Scenario 4: Agent Meets Conditions but Has Zero Commission

**Example**:
- Agent ID: 103
- Role: 2 (Sales Agent) ✓
- `sum_of_premium_amount` (Dec 1-10): 650,000 ✓
- `sum_of_agent_commission_realized` (Dec 1-10): 0

**Calculation**:
1. **Check Conditions**:
   - `sum_of_premium_amount >= 600000`: 650,000 >= 600,000 → **TRUE**
   - `role = 2`: Agent role_id = 2 → **TRUE**
   - All conditions met → **ELIGIBLE**

2. **Calculate Reward** (Percentage Type):
   ```
   incentive_amount = (0 × 3.0) / 100
   incentive_amount = 0.00
   ```

3. **Result**: Agent receives **$0.00** (eligible but no commission to calculate percentage from)

## Calculation Formula Details

### Percentage Type Calculation
**Location**: `incentive_utils.py:1075-1166`

**Formula**:
```
incentive_amount = (incentive_base_field_value × reward_type_value) / 100
```

**Where**:
- `incentive_base_field_value` = Value from `sum_of_agent_commission_realized`
- `reward_type_value` = 3.0 (percentage)

**Example**:
- Base field value: 10,000
- Reward percentage: 3.0%
- Calculation: (10,000 × 3.0) / 100 = 300.00

### Fixed Type Calculation
**Location**: `incentive_utils.py:1167-1180`

**Formula**:
```
incentive_amount = reward_type_value
```

**Example**:
- Reward value: 500
- Calculation: 500.00 (fixed amount)

## Date Filtering

### Period-Based Filtering
**Location**: `incentive_utils.py:639-694`

The system applies date filters based on the incentive setup's period:

1. **For Policy-Based Tables** (`crmp_issued_policies`, `crmp_policy_base`):
   - Uses `policy_effective_date` field
   - Filters: `policy_effective_date >= start_date AND policy_effective_date <= end_date`

2. **For Commission Tables** (`crmf_agent_commission`, `crmf_brokerage_commission`):
   - Uses `policy_effective_date` from joined `crmp_issued_policies` table
   - Filters through the join chain

3. **For Sales Target Tables** (`crmf_agent_sales_targets`, `crmf_team_sales_targets`):
   - Uses `month` and `year` fields instead of dates
   - Filters: `month = period_month AND year = period_year`

## Complete Table Chain for Your Example

### For `sum_of_premium_amount`:
```
crmp_issued_policies (premium_amount)
  ↓ JOIN
crmp_policy_base (sales_agent_id)
  ↓ JOIN
core_users (role_id, id)
```

### For `sum_of_agent_commission_realized`:
```
crmf_agent_commission (revenue_realized)
  ↓ JOIN
crmf_brokerage_commission (id)
  ↓ JOIN
crmf_invoices (issued_policy_id)
  ↓ JOIN
crmp_issued_policies (policy_base_id)
  ↓ JOIN
crmp_policy_base (sales_agent_id)
  ↓ JOIN
core_users (role_id, id)
```

## Key Points

1. **Performance Conditions** are evaluated using AND/OR logic (your example uses AND)
2. **Date Filtering** is applied during aggregation, not after
3. **Role Filtering** is checked directly from `core_users.role_id`
4. **Percentage Calculation** uses the `incentive_base_field` value multiplied by the percentage
5. **All aggregations** use `COALESCE(SUM(...), 0)` to return 0 instead of NULL when no data exists

## Summary for Your Example

**Your Incentive**: "sales bonus - december"

**Calculation Process**:
1. Find all agents with `role_id = 2` who have policies in December 2025
2. For each agent, calculate:
   - Total premium amount (Dec 1-10): Must be >= 600,000
   - Total realized commission (Dec 1-10): Used for percentage calculation
3. If premium >= 600,000 AND role = 2:
   - Calculate: `(realized_commission × 3.0) / 100`
   - Save incentive record
4. If conditions not met:
   - Skip agent (no incentive awarded)

**Tables Involved**:
- `crmf_incentive_setups` - Incentive configuration
- `crmp_issued_policies` - Premium amounts
- `crmf_agent_commission` - Commission realized amounts
- `crmp_policy_base` - Links policies to agents
- `core_users` - Agent role information
- `crmf_brokerage_commission` - Brokerage commission (join path)
- `crmf_invoices` - Invoices (join path)
- `crmf_incentives` - Final incentive records saved

## Direct SQL Queries

For direct database queries to get values for sales agents, see **`INCENTIVE_SQL_QUERIES.sql`** file.

This file contains ready-to-run SQL queries including:

1. **Query 1**: Get all sales agents with policies in the period
2. **Query 2**: Get `sum_of_premium_amount` for each agent
3. **Query 3**: Get `sum_of_agent_commission_realized` for each agent
4. **Query 4**: Complete calculation for all eligible agents (recommended)
5. **Query 5**: Get values for a specific agent (replace agent ID)
6. **Query 6**: Detailed breakdown showing individual policies and commissions
7. **Query 7**: Summary statistics for all eligible agents

### Quick Example - Get Values for Agent ID 100:

```sql
-- Replace 100 with your agent ID
SELECT 
    cu.id AS agent_id,
    cu.display_name AS agent_name,
    cu.role_id,
    
    -- Premium Amount
    (SELECT COALESCE(SUM(ip.premium_amount), 0)
     FROM crmp_issued_policies ip
     INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
     WHERE pb.sales_agent_id = cu.id
       AND ip.policy_effective_date >= '2025-12-01'
       AND ip.policy_effective_date <= '2025-12-10'
    ) AS sum_of_premium_amount,
    
    -- Commission Realized
    (SELECT COALESCE(SUM(ac.revenue_realized), 0)
     FROM crmf_agent_commission ac
     INNER JOIN crmf_brokerage_commission bc ON bc.id = ac.brokerage_commission_id
     INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
     INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
     INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
     WHERE pb.sales_agent_id = cu.id
       AND ip.policy_effective_date >= '2025-12-01'
       AND ip.policy_effective_date <= '2025-12-10'
    ) AS sum_of_agent_commission_realized,
    
    -- Incentive Calculation
    CASE 
        WHEN cu.role_id = 2 
         AND (SELECT COALESCE(SUM(ip.premium_amount), 0)
              FROM crmp_issued_policies ip
              INNER JOIN crmp_policy_base pb ON ip.policy_base_id = pb.id
              WHERE pb.sales_agent_id = cu.id
                AND ip.policy_effective_date >= '2025-12-01'
                AND ip.policy_effective_date <= '2025-12-10'
             ) >= 600000 
        THEN ROUND(
            ((SELECT COALESCE(SUM(ac.revenue_realized), 0)
              FROM crmf_agent_commission ac
              INNER JOIN crmf_brokerage_commission bc ON bc.id = ac.brokerage_commission_id
              INNER JOIN crmf_invoices inv ON inv.id = bc.invoice_id
              INNER JOIN crmp_issued_policies ip ON ip.id = inv.issued_policy_id
              INNER JOIN crmp_policy_base pb ON pb.id = ip.policy_base_id
              WHERE pb.sales_agent_id = cu.id
                AND ip.policy_effective_date >= '2025-12-01'
                AND ip.policy_effective_date <= '2025-12-10'
             ) * 3.0) / 100.0, 
             2
        )
        ELSE 0.00
    END AS incentive_amount

FROM core_users cu
WHERE cu.id = 100  -- REPLACE WITH ACTUAL AGENT ID
  AND cu.deleted_at IS NULL;
```

