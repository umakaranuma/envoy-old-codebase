# How Incentive Setup ID 85 Works with `run_all_incentive_awards`

## Your Incentive Setup Configuration

```json
{
    "id": 85,
    "name": "MBSL bonus",
    "description": "team lead receives a bonus of 10% out of agent commission if the team members achieve their target for the month of February",
    "repeation_type": "One-Time",
    "start_date": "2026-02-01",
    "end_date": "2026-02-28",
    "incentive_base_field": "sum_of_agent_commission_recognized",
    "performance_fields": {
        "logic": "AND",
        "conditions": [
            {
                "field": "sum_of_agent_achieved",
                "label": "Sum of Agent Sales Target",
                "value": "sum_of_agent_sales_target",
                "operator": ">="
            },
            {
                "field": "team_role",
                "label": "Account Manager",
                "value": "team lead",
                "operator": "="
            },
            {
                "field": "product",
                "label": "3 OPTION MOTOR - MBSL",
                "value": 31,
                "operator": "="
            }
        ],
        "reward_type": "percentage"
    },
    "reward_type_id": 2,
    "reward_type_value": 10.0,
    "reward_type": "Percentage",
    "reward_type_name": "Total Premium"
}
```

## Step-by-Step Processing Flow

### Step 1: Setup Retrieval and Validation
- `run_all_incentive_awards` retrieves all active incentive setups (where `deleted_at IS NULL`)
- Your setup (ID 85) will be included in the processing queue
- The function validates the table structure and database connection

### Step 2: Period Calculation
- Since `repeation_type = "One-Time"` and dates are `2026-02-01` to `2026-02-28`
- The system creates **one period**: `(2026-02-01, 2026-02-28)`
- It checks if incentives already exist for this setup and period (skips if already processed)

### Step 3: Finding Eligible Agents
The system uses `find_agents_for_period()` to identify agents who match the conditions:

1. **Target-Based Detection**: 
   - Detects `sum_of_agent_achieved >= sum_of_agent_sales_target` condition
   - Queries `crmf_agent_sales_targets` table for agents with:
     - Sales targets for February 2026
     - Matching the filter conditions (team_role, product)

2. **Filter Conditions Applied**:
   - `team_role = "team lead"` - Finds agents with role "team lead"
   - `product = 31` - Filters for product ID 31 (3 OPTION MOTOR - MBSL)

3. **Result**: Returns a list of agent IDs that have sales targets and match the filters

### Step 4: Team-Based Detection
- The system checks if this is a team-based incentive using `is_team_based_incentive()`
- **Note**: Your setup uses `sum_of_agent_achieved` (not `sum_of_team_achieved`), so it will be treated as an **individual agent incentive**, not team-based
- This means each team lead is evaluated individually, not as a team

### Step 5: Performance Data Aggregation
For each agent found, the system calls `aggregate_performance_data()` which:

1. **Aggregates `sum_of_agent_achieved`**:
   - Queries `crmp_issued_policies` table
   - Sums `premium_amount` for policies where:
     - `sales_agent_id = agent_id`
     - `product_id = 31` (from filter)
     - Policy date within `2026-02-01` to `2026-02-28`
     - Joins through: `policy_base → issued_policies → invoices → brokerage_commission → agent_commission`

2. **Aggregates `sum_of_agent_sales_target`**:
   - Queries `crmf_agent_sales_targets` table
   - Gets the target amount for:
     - `agent_id = agent_id`
     - `product_id = 31` (if applicable)
     - `sales_target_month = 2` (February)
     - `sales_target_year = 2026`

3. **Aggregates `sum_of_agent_commission_recognized`** (base field):
   - Queries `crmf_agent_commission` table
   - Sums `revenue_recognized` for commissions where:
     - Agent matches the agent_id
     - Product = 31 (from filter)
     - Date within period `2026-02-01` to `2026-02-28`

**Example Performance Data Result**:
```python
{
    "sum_of_agent_achieved": 50000.00,        # Total premium from policies
    "sum_of_agent_sales_target": 40000.00,    # Target from sales_targets table
    "sum_of_agent_commission_recognized": 5000.00  # Commission recognized
}
```

### Step 6: Condition Evaluation
The system calls `calculate_incentive_reward()` to evaluate if the agent qualifies:

1. **Evaluates Condition 1**: `sum_of_agent_achieved >= sum_of_agent_sales_target`
   - Compares: `50000.00 >= 40000.00` → **TRUE** ✅

2. **Evaluates Condition 2**: `team_role = "team lead"`
   - Checks agent's role from database → **TRUE** ✅ (if agent is team lead)

3. **Evaluates Condition 3**: `product = 31`
   - Already filtered during aggregation → **TRUE** ✅

4. **Logic**: All conditions use `AND` logic, so all must be true
   - Result: **ELIGIBLE** ✅

### Step 7: Reward Calculation
Since `reward_type_id = 2` (Percentage) and `reward_type_value = 10.0`:

**Formula**: `reward_amount = (incentive_base_field_value × reward_type_value) / 100`

**Calculation**:
```
reward_amount = (sum_of_agent_commission_recognized × 10.0) / 100
reward_amount = (5000.00 × 10.0) / 100
reward_amount = 500.00
```

**Result**: The team lead receives **$500.00** bonus (10% of $5,000 commission)

### Step 8: Saving Incentive Record
If the agent is eligible and reward amount > 0:

1. Creates a record in `crmf_incentives` table with:
   - `incentive_setup_id = 85`
   - `agent_id = [team lead's agent ID]`
   - `reward_amount = 500.00`
   - `commission_date = [current date when run]`
   - `period_start = 2026-02-01`
   - `period_end = 2026-02-28`
   - Performance data stored in JSON format

2. Skips if:
   - Record already exists for this setup/agent/period
   - Reward amount is 0 (no commission to calculate from)
   - Agent has no sales/commission in the period

## Important Notes

### ⚠️ Team vs Individual Processing
- Your description says "team lead receives bonus if **team members** achieve target"
- However, your conditions use `sum_of_agent_achieved` (individual agent achievement)
- This means it evaluates **each team lead individually**, not as a team
- If you want team-based evaluation, you should use `sum_of_team_achieved` instead

### ⚠️ Target Achievement Check
- The condition `sum_of_agent_achieved >= sum_of_agent_sales_target` checks if the **team lead themselves** achieved their target
- It does NOT check if their **team members** achieved targets
- To check team member targets, you'd need different conditions

### ⚠️ Commission Base Field
- The reward is calculated from `sum_of_agent_commission_recognized`
- This is the commission **recognized** (revenue recognized), not just earned
- Only policies/products matching the filters (product = 31) are included

## Expected Output

When you run `run_all_incentive_awards`, you should see logs like:

```
================================================================================
Processing Setup ID: 85
================================================================================
Setup 85: {...setup details...}
Periods for setup 85: [(2026-02-01, 2026-02-28)]
Found 3 agent IDs for period: [123, 456, 789]
Processing agent 123 for period {'start_date': '2026-02-01', 'end_date': '2026-02-28'}
Performance data for agent 123: {...}
Incentive calculation result: {'eligible': True, 'reward_amount': 500.00}
Successfully saved incentive record for agent 123
```

## Summary

For your incentive setup (ID 85):
1. ✅ Finds team leads with product 31 sales targets for Feb 2026
2. ✅ Aggregates their individual achievement vs target
3. ✅ Aggregates their commission recognized for product 31
4. ✅ Checks if they achieved their individual target (>=)
5. ✅ If yes, awards 10% of their commission recognized
6. ✅ Saves incentive record for each eligible team lead

**Result**: Each team lead who achieved their individual target gets 10% bonus on their commission for product 31 in February 2026.

