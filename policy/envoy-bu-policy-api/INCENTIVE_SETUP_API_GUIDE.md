# Incentive Setup API Guide

## API Endpoint

**POST** `/api/incentive-setups`

## Complete Request Structure

### Example Request Body

```json
{
    "name": "Premium Below Threshold Incentive",
    "description": "Fixed reward for agents with premium below threshold",
    "performance_fields": {
        "logic": "AND",
        "conditions": [
            {
                "field": "sum_of_premium_amount",
                "operator": "<",
                "value": "500000",
                "label": "Premium Below 500K"
            }
        ]
    },
    "reward_type": "fixed",
    "reward_type_id": 1,
    "reward_type_value": "10000",
    "incentive_base_field": "sum_of_premium_amount",
    "repeation_type": "Monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
```

## Required Fields

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `name` | string | ✅ Yes | Name of the incentive setup | "Premium Below Threshold Incentive" |
| `incentive_base_field` | string | ✅ Yes | Base field for percentage calculations | "sum_of_premium_amount" |
| `performance_fields` | object | ✅ Yes | Conditions structure (see below) | See structure below |
| `reward_type_value` | number | ✅ Yes | Reward amount or percentage | "10000" or "5" |
| `repeation_type` | string | ✅ Yes | One of: "One-Time", "Monthly", "Quarterly", "Annually" | "Monthly" |
| `start_date` | date | ✅ Yes | Start date (YYYY-MM-DD) | "2024-01-01" |
| `end_date` | date | ✅ Yes | End date (YYYY-MM-DD) | "2024-12-31" |
| `description` | string | ❌ No | Description of the incentive | "Fixed reward for agents..." |
| `reward_type` | string | ❌ No* | "fixed", "percentage", or "tiered" | "fixed" |
| `reward_type_id` | integer | ❌ No* | 1=Fixed, 2=Percentage, 3=Tiered | 1 |

*Either `reward_type` or `reward_type_id` must be provided. If both are provided, they must match.

## Performance Fields Structure

### Basic Structure (AND Logic)

```json
{
    "logic": "AND",
    "conditions": [
        {
            "field": "sum_of_premium_amount",
            "operator": "<",
            "value": "500000",
            "label": "Premium Below 500K"
        }
    ]
}
```

### Multiple Conditions (AND Logic)

```json
{
    "logic": "AND",
    "conditions": [
        {
            "field": "sum_of_premium_amount",
            "operator": "<",
            "value": "500000",
            "label": "Premium Below 500K"
        },
        {
            "field": "role",
            "operator": "=",
            "value": 2,
            "label": "Sales Agent"
        }
    ]
}
```

### OR Logic

```json
{
    "logic": "OR",
    "conditions": [
        {
            "field": "sum_of_premium_amount",
            "operator": "<",
            "value": "500000"
        },
        {
            "field": "sum_of_commission_deductible",
            "operator": "<",
            "value": "20000"
        }
    ]
}
```

### Nested Logic (Complex Conditions)

```json
{
    "logic": "AND",
    "conditions": [
        {
            "field": "role",
            "operator": "=",
            "value": 2
        },
        {
            "logic": "OR",
            "conditions": [
                {
                    "field": "sum_of_premium_amount",
                    "operator": "<",
                    "value": "500000"
                },
                {
                    "field": "sum_of_commission_deductible",
                    "operator": "<",
                    "value": "20000"
                }
            ]
        }
    ]
}
```

## Condition Fields

Each condition must have:

| Field | Type | Required | Description | Example |
|-------|------|----------|-------------|---------|
| `field` | string | ✅ Yes | Performance field name | "sum_of_premium_amount" |
| `operator` | string | ✅ Yes | Comparison operator | "<", ">", "=", ">=", "<=", "between" |
| `value` | string/number | ✅ Yes | Value to compare against | "500000" or 500000 |
| `label` | string | ❌ No | Human-readable label | "Premium Below 500K" |

## Available Operators

| Operator | Description | Value Type | Example |
|----------|-------------|------------|---------|
| `<` | Less than | number | `"value": "500000"` |
| `<=` | Less than or equal | number | `"value": "500000"` |
| `>` | Greater than | number | `"value": "500000"` |
| `>=` | Greater than or equal | number | `"value": "500000"` |
| `=` | Equal to | number/string | `"value": 2` or `"value": "500000"` |
| `!=` | Not equal to | number/string | `"value": 2` |
| `between` | Between two values | array | `"value": [500000, 1000000]` |
| `in` | In list | array | `"value": [1, 2, 3]` |
| `not in` | Not in list | array | `"value": [1, 2, 3]` |

## Available Performance Fields

Common fields you can use in conditions:

- `sum_of_premium_amount` - Total premium amount
- `sum_of_commission_deductible` - Total commission deductible
- `sum_of_agent_commission_realized` - Agent commission realized
- `sum_of_agent_commission_recognized` - Agent commission recognized
- `sum_of_agent_achieved` - Agent sales achievement
- `sum_of_agent_sales_target` - Agent sales target
- `role` or `role_id` - Agent role (filter field)
- `product` or `product_id` - Product (filter field)
- `insurer` or `insurer_id` - Insurer (filter field)

**Note**: Use the `/api/performance-field-definitions` endpoint to get the complete list of available fields.

## Reward Types

### 1. Fixed Reward (`reward_type_id: 1`)

- **reward_type**: `"fixed"` or `"flat"`
- **reward_type_value**: Fixed amount (e.g., `"10000"` = 10,000)
- **Example**: Agent gets exactly 10,000 if conditions are met

```json
{
    "reward_type": "fixed",
    "reward_type_id": 1,
    "reward_type_value": "10000"
}
```

### 2. Percentage Reward (`reward_type_id: 2`)

- **reward_type**: `"percentage"` or `"percent"`
- **reward_type_value**: Percentage (e.g., `"5"` = 5%)
- **incentive_base_field**: Required - field to calculate percentage from
- **Example**: Agent gets 5% of their `sum_of_premium_amount`

```json
{
    "reward_type": "percentage",
    "reward_type_id": 2,
    "reward_type_value": "5",
    "incentive_base_field": "sum_of_premium_amount"
}
```

### 3. Tiered Reward (`reward_type_id: 3`)

- **reward_type**: `"tiered"` or `"tier"`
- **reward_type_value**: Varies by tier
- **Note**: Tiered rewards require additional configuration

## Repetition Types

| Value | Description |
|-------|-------------|
| `"One-Time"` | Runs once for the entire date range |
| `"Monthly"` | Runs monthly within the date range |
| `"Quarterly"` | Runs quarterly within the date range |
| `"Annually"` | Runs annually within the date range |

## How the Logic Works

### AND Logic

**All conditions must be True** for the agent to be eligible.

**Example**:
```json
{
    "logic": "AND",
    "conditions": [
        {"field": "sum_of_premium_amount", "operator": "<", "value": "500000"},
        {"field": "role", "operator": "=", "value": 2}
    ]
}
```

**Result**: Agent is eligible ONLY if:
- `sum_of_premium_amount < 500000` **AND**
- `role = 2`

### OR Logic

**At least one condition must be True** for the agent to be eligible.

**Example**:
```json
{
    "logic": "OR",
    "conditions": [
        {"field": "sum_of_premium_amount", "operator": "<", "value": "500000"},
        {"field": "sum_of_commission_deductible", "operator": "<", "value": "20000"}
    ]
}
```

**Result**: Agent is eligible if:
- `sum_of_premium_amount < 500000` **OR**
- `sum_of_commission_deductible < 20000`

### Nested Logic

You can combine AND and OR logic for complex conditions.

**Example**:
```json
{
    "logic": "AND",
    "conditions": [
        {"field": "role", "operator": "=", "value": 2},
        {
            "logic": "OR",
            "conditions": [
                {"field": "sum_of_premium_amount", "operator": "<", "value": "500000"},
                {"field": "sum_of_commission_deductible", "operator": "<", "value": "20000"}
            ]
        }
    ]
}
```

**Result**: Agent is eligible if:
- `role = 2` **AND**
- (`sum_of_premium_amount < 500000` **OR** `sum_of_commission_deductible < 20000`)

## Complete Example Request

### Example 1: Simple Fixed Reward

```json
{
    "name": "Low Premium Incentive",
    "description": "10,000 fixed reward for agents with premium below 500K",
    "performance_fields": {
        "logic": "AND",
        "conditions": [
            {
                "field": "sum_of_premium_amount",
                "operator": "<",
                "value": "500000",
                "label": "Premium Below 500K"
            }
        ]
    },
    "reward_type": "fixed",
    "reward_type_id": 1,
    "reward_type_value": "10000",
    "incentive_base_field": "sum_of_premium_amount",
    "repeation_type": "Monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
```

### Example 2: Percentage Reward with Multiple Conditions

```json
{
    "name": "High Performance Incentive",
    "description": "5% bonus for agents with premium > 1M and role = Sales Agent",
    "performance_fields": {
        "logic": "AND",
        "conditions": [
            {
                "field": "sum_of_premium_amount",
                "operator": ">",
                "value": "1000000",
                "label": "Premium Above 1M"
            },
            {
                "field": "role",
                "operator": "=",
                "value": 2,
                "label": "Sales Agent"
            }
        ]
    },
    "reward_type": "percentage",
    "reward_type_id": 2,
    "reward_type_value": "5",
    "incentive_base_field": "sum_of_premium_amount",
    "repeation_type": "Monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
}
```

## Response

### Success Response

```json
{
    "is_success": true,
    "message": "incentive_setup_created_successfully",
    "result": {
        "id": 123
    },
    "system_code": ""
}
```

### Error Response

```json
{
    "is_success": false,
    "message": "validation_error",
    "result": {
        "name": ["name is required"],
        "reward_type_value": ["reward_type_value is required and cannot be empty"]
    },
    "system_code": ""
}
```

## How It Works - Step by Step

1. **Setup Created**: The incentive setup is saved with your conditions
2. **Period Calculation**: System calculates periods based on `repeation_type`:
   - Monthly: Jan, Feb, Mar, etc.
   - Quarterly: Q1, Q2, Q3, Q4
   - Annually: Full year
   - One-Time: Entire date range
3. **Agent Finding**: For each period, system finds agents who:
   - Have records matching the conditions
   - Meet the role/product/insurer filters (if any)
4. **Performance Aggregation**: For each agent, system calculates:
   - Sum of premium amounts
   - Sum of commissions
   - Other performance metrics
5. **Condition Evaluation**: System checks if agent meets ALL conditions (AND) or ANY condition (OR)
6. **Reward Calculation**: If eligible:
   - Fixed: Uses `reward_type_value` directly
   - Percentage: Calculates `incentive_base_field × reward_type_value / 100`
7. **Incentive Record**: Creates incentive record in `crmf_incentives` table

## Running the Incentive

After creating the setup, run:

**POST** `/api/incentives/run-all`

This will:
- Process all incentive setups
- Find eligible agents for each period
- Calculate rewards
- Create incentive records

## Tips

1. **Always provide `incentive_base_field`**: Even for fixed rewards, it's required
2. **Use proper date format**: `YYYY-MM-DD` (e.g., "2024-01-01")
3. **Value as string or number**: Both work, but strings are safer for large numbers
4. **Test with simple conditions first**: Start with one condition, then add more
5. **Check field definitions**: Use `/api/performance-field-definitions` to see available fields and operators

