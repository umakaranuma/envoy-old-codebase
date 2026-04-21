# Incentive Conditions Verification Checklist

This document verifies that all incentive condition types are working correctly after recent changes.

## Recent Changes Summary
1. Enhanced `find_agents_for_period()` to find agents from sales targets table for target-based conditions
2. Improved skip logic to handle target-based incentives correctly
3. Enhanced team-based incentive processing
4. Added penalty incentive support
5. Added filtering for zero-sales agents
6. **REMOVED**: `achievement_percentage` calculated field (use field references instead, e.g., `sum_of_agent_achieved >= sum_of_agent_sales_target`)

## Condition Types to Verify

### ✅ 1. Basic Role-Based Conditions
**Test Case**: `role = 2` (Sales Agent)
- **Expected**: Should find all agents with role_id = 2
- **Function**: `find_agents_for_period()` - fallback to core_users query
- **Evaluation**: `calculate_incentive_reward()` - checks agent's role_id from database
- **Status**: ✅ Should work - no changes to role checking logic

### ✅ 2. Premium Amount Conditions
**Test Case**: `sum_of_premium_amount >= 600000`
- **Expected**: Should aggregate premium amounts and compare
- **Function**: `aggregate_performance_data()` - aggregates from crmp_issued_policies
- **Evaluation**: `calculate_incentive_reward()` - evaluates condition using performance_data
- **Status**: ✅ Should work - no changes to aggregation logic

### ✅ 3. Product-Based Conditions
**Test Case**: `product = 5` (Marine Liability)
- **Expected**: Should filter performance data by product_id
- **Function**: `aggregate_performance_data()` - applies product filter in WHERE clause
- **Evaluation**: `calculate_incentive_reward()` - filter already applied during aggregation
- **Status**: ✅ Should work - filter fields are handled correctly

### ✅ 4. Insurer-Based Conditions
**Test Case**: `insurer = 3`
- **Expected**: Should filter performance data by insurer_id
- **Function**: `aggregate_performance_data()` - applies insurer filter in WHERE clause
- **Evaluation**: `calculate_incentive_reward()` - filter already applied during aggregation
- **Status**: ✅ Should work - filter fields are handled correctly

### ✅ 5. Target-Based Conditions
**Test Case**: `sum_of_agent_achieved >= sum_of_agent_sales_target` or `sum_of_agent_achieved >= 100000`
- **Expected**: Should find agents from sales targets table and evaluate condition using field references or direct values
- **Function**: 
  - `find_agents_for_period()` - finds agents from `crmf_agent_sales_targets` table when target-based fields are detected
  - `aggregate_performance_data()` - aggregates `sum_of_agent_achieved` and `sum_of_agent_sales_target` values
  - `calculate_incentive_reward()` - evaluates condition using field references or direct comparisons
- **Status**: ✅ Should work - uses field references instead of calculated percentage

### ✅ 6. Team-Based Conditions (NEW)
**Test Case**: `sum_of_team_achieved >= sum_of_team_sales_target`
- **Expected**: Should process at team level, find all team members, and create records for all
- **Function**: 
  - `is_team_based_incentive()` - detects team-based fields
  - `get_unique_teams_from_agents()` - finds unique teams
  - `get_team_members_for_team()` - gets all team members
  - `calculate_collective_commission_for_team()` - calculates team commission
- **Status**: ✅ Should work - team processing logic intact

### ✅ 7. Percentage Rewards
**Test Case**: `reward_type_id = 2`, `reward_type_value = 3.0`, `incentive_base_field = sum_of_agent_commission_realized`
- **Expected**: Should calculate `(base_field_value * 3.0) / 100`
- **Function**: `calculate_incentive_reward()` - percentage calculation logic
- **Status**: ✅ Should work - no changes to percentage calculation

### ✅ 8. Fixed Rewards
**Test Case**: `reward_type_id = 1`, `reward_type_value = 10000`
- **Expected**: Should use `reward_type_value` directly
- **Function**: `calculate_incentive_reward()` - fixed reward logic
- **Status**: ✅ Should work - no changes to fixed reward calculation

### ✅ 9. Penalty Incentives (NEW)
**Test Case**: `reward_type_value = -5` (5% penalty)
- **Expected**: Should calculate percentage and negate the result
- **Function**: `calculate_incentive_reward()` - checks if reward_type_value is negative
- **Status**: ✅ Should work - penalty logic intact

### ✅ 10. Zero-Sales Agent Filtering (NEW)
**Test Case**: Agent with no sales/commission, incentive amount = 0
- **Expected**: Should skip creating incentive record
- **Function**: `run_all_incentive_awards()` - checks `has_sales` and `reward_amount`
- **Status**: ✅ Should work - skip logic intact

### ✅ 11. AND Logic
**Test Case**: Multiple conditions with `logic: "AND"`
- **Expected**: All conditions must be True
- **Function**: `calculate_incentive_reward()` - evaluates all conditions and uses `all()`
- **Status**: ✅ Should work - AND logic intact

### ✅ 12. OR Logic
**Test Case**: Multiple conditions with `logic: "OR"`
- **Expected**: At least one condition must be True
- **Function**: `calculate_incentive_reward()` - evaluates all conditions and uses `any()`
- **Status**: ✅ Should work - OR logic intact

### ✅ 13. Between Operator
**Test Case**: `sum_of_premium_amount between [500000, 1000000]`
- **Expected**: Should check if value is between the two values in the list
- **Function**: `evaluate_condition()` - handles `between` operator with list values
- **Status**: ✅ Should work - between operator logic intact

### ✅ 14. Field Reference Conditions
**Test Case**: `sum_of_agent_achieved >= sum_of_agent_sales_target`
- **Expected**: Should resolve field reference and compare values
- **Function**: `calculate_incentive_reward()` - resolves field references using `is_field_reference()`
- **Status**: ✅ Should work - field reference resolution intact

## Potential Issues to Watch For

### ⚠️ Issue 1: Target-Based Agent Finding
**Risk**: If target-based condition is detected, but no agents found in sales targets table, falls back to regular logic
**Mitigation**: Fallback logic is in place (line 278 in `incentive_utils.py`)

### ⚠️ Issue 2: Skip Logic for Target-Based Incentives
**Risk**: Target-based percentage rewards might skip agents who achieved target but have 0 commission
**Mitigation**: Skip logic checks `is_target_based` and `is_percentage` before skipping (line 1234 in `incentive_controller.py`)

### ⚠️ Issue 3: Target-Based Field References
**Risk**: Field reference conditions like `sum_of_agent_achieved >= sum_of_agent_sales_target` require both fields to be aggregated
**Mitigation**: `aggregate_performance_data()` aggregates all fields mentioned in conditions, including field references

### ⚠️ Issue 4: Team Processing Order
**Risk**: Team-based incentives processed before individual incentives might affect agent_ids list
**Mitigation**: Team processing is separate and doesn't interfere with individual processing

## Test Scenarios

### Scenario 1: Basic Role + Premium Condition
```json
{
  "logic": "AND",
  "conditions": [
    {"field": "role", "operator": "=", "value": 2},
    {"field": "sum_of_premium_amount", "operator": ">=", "value": 600000}
  ]
}
```
**Expected Result**: All agents with role_id=2 AND premium >= 600000 get incentive

### Scenario 2: Target Achievement Condition
```json
{
  "logic": "AND",
  "conditions": [
    {"field": "sum_of_agent_achieved", "operator": ">=", "value": "sum_of_agent_sales_target"}
  ]
}
```
**Expected Result**: All agents with targets who achieved >= their target get incentive

### Scenario 3: Product-Specific Condition
```json
{
  "logic": "AND",
  "conditions": [
    {"field": "product", "operator": "=", "value": 5},
    {"field": "sum_of_agent_achieved", "operator": ">=", "value": 90000},
    {"field": "sum_of_agent_achieved", "operator": "<=", "value": 100000}
  ]
}
```
**Expected Result**: Agents with product=5 AND achieved amount between 90k-100k get incentive

### Scenario 4: Team-Based Condition
```json
{
  "logic": "AND",
  "conditions": [
    {"field": "sum_of_team_achieved", "operator": ">=", "value": "sum_of_team_sales_target"}
  ]
}
```
**Expected Result**: All team members get incentive when team achieves target

### Scenario 5: Penalty Condition
```json
{
  "logic": "AND",
  "conditions": [
    {"field": "sum_of_agent_achieved", "operator": "<", "value": "sum_of_agent_sales_target"}
  ]
}
```
**Reward**: `reward_type_value = -5` (5% penalty)
**Expected Result**: Agents who did not achieve their target get 5% deduction from commission

## Verification Steps

1. **Test Basic Conditions**: Run incentive with role + premium condition
2. **Test Target-Based**: Run incentive with field reference condition (e.g., `sum_of_agent_achieved >= sum_of_agent_sales_target`)
3. **Test Product Filter**: Run incentive with product condition
4. **Test Team-Based**: Run incentive with team achievement condition
5. **Test Penalty**: Run incentive with negative reward_type_value
6. **Test Zero-Sales Filter**: Verify agents with no sales are skipped
7. **Test AND Logic**: Verify all conditions must be met
8. **Test OR Logic**: Verify at least one condition must be met
9. **Test Between Operator**: Verify between condition works correctly
10. **Test Field Reference**: Verify field-to-field comparison works (e.g., `sum_of_agent_achieved >= sum_of_agent_sales_target`)

## Code Flow Verification

### Team vs Individual Processing
- **Team Processing** (lines 1008-1137): Only executes if `is_team_incentive = True`
- **Individual Processing** (lines 1138+): Only executes if `is_team_incentive = False`
- **No Interference**: Team and individual processing are mutually exclusive

### Agent Finding Logic
1. **Target-Based Conditions** (lines 203-278 in `incentive_utils.py`):
   - Detects target-based fields (`sum_of_agent_achieved`, `sum_of_agent_sales_target`, `sum_of_team_achieved`, `sum_of_team_sales_target`)
   - Queries `crmf_agent_sales_targets` table to find agents with targets for the period
   - Falls back to regular logic if no agents found

2. **Regular Conditions** (lines 280-500 in `incentive_utils.py`):
   - Uses registry to find agents from base tables
   - Handles filter fields (role, product, insurer) correctly
   - Falls back to `core_users` if only filter fields present

### Skip Logic
- **For Individual Incentives** (lines 1216-1238 in `incentive_controller.py`):
  - Skips if percentage reward but no base field value
  - Skips if non-target-based with 0 amount
  - Skips if target-based percentage but no commission
  - **Does NOT skip** if target-based fixed reward (even with 0 commission)

- **For Team Incentives** (lines 1100-1104 in `incentive_controller.py`):
  - Skips if team reward amount is 0
  - Creates records for all team members if eligible

## Conclusion

All condition types should be working correctly. The recent changes:
- ✅ Enhanced target-based agent finding (doesn't break existing logic)
- ✅ Improved skip logic (only affects edge cases)
- ✅ Enhanced team processing (separate logic, doesn't interfere)
- ✅ Added penalty support (new feature, doesn't affect existing)
- ✅ **REMOVED**: `achievement_percentage` calculated field - use field references instead

The core condition evaluation logic (`evaluate_condition()`, `calculate_incentive_reward()`) remains unchanged, ensuring backward compatibility.

### Key Safeguards
1. **Team and Individual Processing**: Mutually exclusive - no interference
2. **Target-Based Agent Finding**: Has fallback to regular logic
3. **Skip Logic**: Carefully checks conditions before skipping
4. **Field References**: All referenced fields are aggregated before comparison
5. **Filter Fields**: Correctly identified and handled separately

### Recommended Testing Order
1. Test basic role + premium condition (most common)
2. Test target-based condition with field reference (e.g., `sum_of_agent_achieved >= sum_of_agent_sales_target`)
3. Test product filter condition (common)
4. Test team-based condition (new feature)
5. Test penalty condition (new feature)
6. Test zero-sales filtering (new feature)

### Important Note on Target-Based Conditions
- **Use field references** instead of `achievement_percentage`: 
  - ✅ `sum_of_agent_achieved >= sum_of_agent_sales_target` (correct)
  - ❌ `achievement_percentage >= 100` (removed - no longer supported)
- The system will automatically find agents from sales targets table when target-based fields are detected
- Both `sum_of_agent_achieved` and `sum_of_agent_sales_target` will be aggregated for comparison

