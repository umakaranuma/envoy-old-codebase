"""
Utility: PERFORMANCE_FIELD_REGISTRY & PERFORMANCE_FIELD_DEFINITIONS

- PERFORMANCE_FIELD_REGISTRY: Defines how to aggregate, join, and filter for a specific metric.
- PERFORMANCE_FIELD_DEFINITIONS: UI/validation metadata for each field (operators, widget, type, description, etc.)
"""

# Utility to determine aggregation type from key

def get_aggregation_type_from_key(key):
    if key.startswith("sum_of_"):
        return "sum"
    elif key.startswith("count_of_"):
        return "count"
    elif key.startswith("select_"):
        return "select"
    else:
        # fallback to definition or default
        return PERFORMANCE_FIELD_DEFINITIONS.get(key, {}).get("aggregation", "sum")

# PERFORMANCE_FIELD_DEFINITIONS: Defines available metrics and their aggregation types for incentives and reporting.
# Naming convention:
#   - sum_of_<metric>: Sum aggregation
#   - count_of_<entity>: Count aggregation
#   - select_<entity>: Select all matching records
#   - <field>: For direct field filters (no aggregation)

PERFORMANCE_FIELD_DEFINITIONS = {
    # --- Core Performance Fields (Command Fields) ---
    # These fields are commonly used for performance metrics and reporting:
    # - native_product_id: Filter by native product ID
    # - sum_of_premium_amount: Total premium amount across policies
    # - premium_amount: Premium amount across policies
    # - policy_count: Number of policies
    # - sum_insured: Sum insured amount
    # - sales_agent_id: Filter by sales agent
    # - sum_of_agent_sales_target: Total agent sales target amount
    # - sum_of_brokerage_revenue_recognized: Total brokerage commission recognized
    # - sum_of_commission_deductible: Total commission deductible amount
    
    # --- Policy Premium ---
    "sum_of_premium_amount": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SUM AGGREGATION: Calculates the total premium amount by adding up premium_amount values from all issued policies that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 50000.00). Used for incentive calculations, performance metrics, and reporting totals. Example: If 3 policies have premiums $10k, $20k, $30k, this returns $60,000.00.",
        "aggregation": "sum"
    },
    "premium_amount": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">" ],
        "widget": "number",
        "description": "SELECT AGGREGATION: Retrieves individual premium_amount values from issued policies that match the filter criteria. Uses SQL SELECT statement. Returns a list of decimal numbers (e.g., [10000.00, 20000.00, 30000.00]). Used for detailed policy analysis, filtering by premium ranges, and retrieving specific policy premium values. Example: Returns all premium amounts for policies issued in January 2024.",
        "aggregation": "select"
    },
    # "count_of_policies": {
    #     "type": "Integer",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "number",
    #     "description": "Number of policies",
    #     "aggregation": "count"
    # },
    # "policies": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of policies matching criteria",
    #     "aggregation": "select"
    # },
    # --- Sum Insured ---
    # "sum_of_sum_insured": {
    #     "type": "Decimal",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "number",
    #     "description": "Total sum insured across policies",
    #     "aggregation": "sum"
    # },
    # "sum_insureds": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of sum insured records matching criteria",
    #     "aggregation": "select"
    # },
    # --- Commission & Revenue ---
    "sum_of_brokerage_revenue_recognized": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SUM AGGREGATION: Calculates the total brokerage commission revenue recognized by adding up revenue_recognized values from all brokerage commission records that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 15000.00). Used for financial reporting, commission tracking, and revenue analysis. Example: If 3 commissions have recognized revenue $5k, $7k, $3k, this returns $15,000.00.",
        "aggregation": "sum"
    },
    # "brokerage_revenue_recognized": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of brokerage revenue recognized records matching criteria",
    #     "aggregation": "select"
    # },
    "sum_of_brokerage_revenue_realized": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SUM AGGREGATION: Calculates the total brokerage commission revenue realized by adding up revenue_realized values from all brokerage commission records that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 12000.00). Used for financial reporting, commission tracking, and revenue analysis. Example: If 3 commissions have realized revenue $4k, $5k, $3k, this returns $12,000.00.",
        "aggregation": "sum"
    },
    # "brokerage_revenue_realized": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of brokerage revenue realized records matching criteria",
    #     "aggregation": "select"
    # },
    # "sum_of_agent_commission": {
    #     "type": "Decimal",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "number",
    #     "description": "Total agent commission from brokerage",
    #     "aggregation": "sum"
    # },
    # "agent_commission": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of agent commission records matching criteria",
    #     "aggregation": "select"
    # },
    "sum_of_commission_deductible": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SUM AGGREGATION: Calculates the total commission deductible amount by adding up commission_deductible values from all brokerage commission records that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 2500.00). Used for commission adjustments, financial reporting, and calculating net commission amounts. Example: If 3 commissions have deductibles $500, $1000, $1000, this returns $2,500.00.",
        "aggregation": "sum"
    },
    # "commission_deductible": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of commission deductible records matching criteria",
    #     "aggregation": "select"
    # },
    # --- Payments ---
    # "sum_of_paid_amount": {
    #     "type": "Decimal",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "number",
    #     "description": "Total paid amount in payments",
    #     "aggregation": "sum"
    # },
    # "paid_amount": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of payment records matching criteria",
    #     "aggregation": "select"
    # },
    # --- Sales Targets ---
    "sum_of_agent_sales_target": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SUM AGGREGATION: Calculates the total agent sales target amount by adding up target_amount values from all agent sales target records that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 100000.00). Used for performance tracking, target vs achievement comparisons, and incentive calculations. Example: If an agent has monthly targets $50k, $30k, $20k, this returns $100,000.00.",
        "aggregation": "sum"
    },
    # "agent_sales_targets": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of agent sales target records",
    #     "aggregation": "select"
    # },
    "sum_of_team_sales_target": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SUM AGGREGATION: Calculates the total team sales target amount by adding up target_amount values from all team sales target records that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 500000.00). Used for team performance tracking, target vs achievement comparisons, and team incentive calculations. Example: If a team has monthly targets $200k, $150k, $150k, this returns $500,000.00.",
        "aggregation": "sum"
    },
    # "team_sales_targets": {
    #     "type": "ObjectList",
    #     "operators": ["<", "<=", "=", ">=", ">"],
    #     "widget": "table",
    #     "description": "List of team sales target records",
    #     "aggregation": "select"
    # },
    "sum_of_agent_achieved": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number_with_options",
        "description": "SUM AGGREGATION: Calculates the total achieved premium amount for an agent by adding up premium_amount values from all issued policies that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 75000.00). Used for performance tracking, target vs achievement comparisons, and incentive calculations. Example: If an agent has policies with premiums $25k, $30k, $20k, this returns $75,000.00.",
        "aggregation": "sum",
        "value_options": [
            {
                "id": "sum_of_agent_sales_target",
                "label": "Sum of Agent Sales Target"
            },
            {
                "id": "sum_of_team_sales_target",
                "label": "Sum of Team Sales Target"
            }
        ]
    },
    "sum_of_team_achieved": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number_with_options",
        "description": "SUM AGGREGATION: Calculates the total achieved premium amount for a team by adding up premium_amount values from all issued policies for all agents in the team that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 200000.00). Used for team performance tracking, target vs achievement comparisons, and team incentive calculations. Example: If a team has agents with total premiums $80k, $70k, $50k, this returns $200,000.00.",
        "aggregation": "sum",
        "value_options": [
            {
                "id": "sum_of_agent_sales_target",
                "label": "Sum of Agent Sales Target"
            },
            {
                "id": "sum_of_team_sales_target",
                "label": "Sum of Team Sales Target"
            }
        ]
    },
    # Filters for sales targets (user-friendly keys)
    # "sales_target_team_id": {
    #     "type": "Integer/FK",
    #     "operators": ["=", "in"],
    #     "widget": "dropdown",
    #     "description": "Filter by team (for sales targets)"
    # },
    # "sales_target_agent_id": {
    #     "type": "Integer/FK",
    #     "operators": ["=", "in"],
    #     "widget": "dropdown",
    #     "description": "Filter by agent (for sales targets)"
    # },
    # "sales_target_period_type": {
    #     "type": "Enum",
    #     "operators": ["=", "in"],
    #     "widget": "dropdown",
    #     "description": "Filter by period type (monthly/yearly) for sales targets"
    # },
    # "sales_target_month": {
    #     "type": "Integer",
    #     "operators": ["=", "in"],
    #     "widget": "number",
    #     "description": "Filter by month (1-12) for sales targets"
    # },
    # "sales_target_year": {
    #     "type": "Integer",
    #     "operators": ["=", "in"],
    #     "widget": "number",
    #     "description": "Filter by year for sales targets"
    # },
    # --- Policy Filters (for direct filtering, not aggregation) ---
    "risk_type": {
        "type": "Integer/FK",
        "operators": ["=", "in"],
        "widget": "dropdown",
        "description": "FILTER FIELD: Filters performance metrics by risk type (product type) ID from policy_base or issued_policies records. Uses SQL WHERE clause with risk_type_id field. Returns filtered results based on the specified risk type ID(s). Used for risk-specific reporting, filtering policies by product type, and analyzing performance by risk category. Example: Filter to show only metrics for risk type ID 3 or risk types in [1, 2, 3].",
        "aggregation": "select"
    },
    "product": {
        "type": "Integer/FK",
        "operators": ["=", "in", "not in"],
        "widget": "dropdown",
        "description": "FILTER FIELD: Filters performance metrics by product ID from policy_base, issued_policies, or invoice records. Uses SQL WHERE clause with product_id field. Returns filtered results based on the specified product ID(s). Used for product-specific reporting, filtering policies by product type, and analyzing performance by product category. Example: Filter to show only metrics for product ID 5 or products in [1, 2, 3].",
        "aggregation": "select"
    },
    "insurer": {
        "type": "Integer/FK",
        "operators": ["=", "in"],
        "widget": "dropdown",
        "description": "FILTER FIELD: Filters performance metrics by insurer ID from policy_base, issued_policies, or invoice records. Uses SQL WHERE clause with insurer_id field. Returns filtered results based on the specified insurer ID(s). Used for insurer-specific reporting, filtering policies by insurer, and analyzing performance by insurer. Example: Filter to show only metrics for insurer ID 5 or insurers in [1, 2, 3].",
        "aggregation": "select"
    },
    # "policy_effective_date": {
    #     "type": "Date",
    #     "operators": ["=", "<", ">"],
    #     "widget": "date",
    #     "description": "Filter by policy effective date"
    # },
    # "policy_start_date": {
    #     "type": "Date",
    #     "operators": ["=", "<", ">"],
    #     "widget": "date",
    #     "description": "Filter by policy start date"
    # },
    # "created_at": {
    #     "type": "DateTime",
    #     "operators": ["=", "<", ">"],
    #     "widget": "date",
    #     "description": "Filter by creation date"
    # },
    # "status": {
    #     "type": "Enum",
    #     "operators": ["=", "in"],
    #     "widget": "dropdown",
    #     "description": "Filter by status"
    # },
    # "invoice_date": {
    #     "type": "Date",
    #     "operators": ["=", "<", ">"],
    #     "widget": "date",
    #     "description": "Filter by invoice date"
    # },
    "role": {
        "type": "Integer/FK",
        "operators": ["=", "in"],
        "widget": "dropdown",
        "description": "FILTER FIELD: Filters performance metrics by user role ID from core_users records. Uses SQL WHERE clause with role_id field. Returns filtered results based on the specified role ID(s). Used for role-specific reporting, filtering metrics by user role, and analyzing performance by role type. Example: Filter to show only metrics for role ID 2 or roles in [1, 2, 3].",
        "aggregation": "select"
    },
    "team_role": {
        "type": "String",
        "operators": ["=", "in"],
        "widget": "dropdown",
        "description": "FILTER FIELD: Filters performance metrics by team role from core_teams or core_team_users tables. Values: 'team lead' (checks core_teams.manager_id), 'team member' (checks core_team_users.user_id). Used for team-based role filtering, distinguishing between team managers and team members. Example: Filter to show only metrics for team leads or team members.",
        "aggregation": "select"
    },
    # "agent_id": {
    #     "type": "Integer/FK",
    #     "operators": ["=", "in", "not in"],
    #     "widget": "dropdown",
    #     "description": "Filter by agent"
    # },
    # "native_product": {
    #     "type": "Integer/FK",
    #     "operators": ["=", "in", "not in"],
    #     "widget": "dropdown",
    #     "description": "FILTER FIELD: Filters performance metrics by native product ID from policy_base records. Uses SQL WHERE clause with product_id field. Returns filtered results based on the specified product ID(s). Used for product-specific reporting, filtering policies by product type, and analyzing performance by product category. Example: Filter to show only metrics for product ID 5 or products in [1, 2, 3].",
    #     "aggregation": "select"
    # },
    # --- Additional fields mentioned by user ---
    "policy_count": {
        "type": "Integer",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "COUNT AGGREGATION: Calculates the total number of issued policies that match the filter criteria by counting policy IDs. Uses SQL COUNT() function. Returns a single integer number (e.g., 25). Used for policy volume tracking, performance metrics, and reporting policy counts. Example: If 25 policies match the criteria, this returns 25.",
        "aggregation": "count"
    },
    "sum_insured": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SELECT AGGREGATION: Retrieves individual sum_insured values from issued policies that match the filter criteria. Uses SQL SELECT statement. Returns a list of decimal numbers (e.g., [50000.00, 100000.00, 250000.00]). Used for coverage analysis, filtering by sum insured ranges, and retrieving specific policy coverage amounts. Example: Returns all sum insured amounts for policies with premium greater than $10,000.",
        "aggregation": "select"
    },
    "sales_agent": {
        "type": "Integer/FK",
        "operators": ["=", "in"],
        "widget": "dropdown",
        "description": "FILTER FIELD: Filters performance metrics by sales agent ID from policy_base records. Uses SQL WHERE clause with sales_agent_id field. Returns filtered results based on the specified agent ID(s). Used for agent-specific reporting, performance tracking by agent, and analyzing individual agent metrics. Example: Filter to show only metrics for agent ID 10 or agents in [5, 10, 15].",
        "aggregation": "select"
    },
    # --- Agent Commission Fields ---
    "sum_of_agent_commission_realized": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SUM AGGREGATION: Calculates the total agent commission revenue realized by adding up revenue_realized values from all agent commission records that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 8000.00). Used for financial reporting, agent commission tracking, and payment analysis. Example: If 3 agent commissions have realized revenue $2k, $3k, $3k, this returns $8,000.00.",
        "aggregation": "sum"
    },
    "sum_of_agent_commission_recognized": {
        "type": "Decimal",
        "operators": ["<", "<=", "=", ">=", ">"],
        "widget": "number",
        "description": "SUM AGGREGATION: Calculates the total agent commission revenue recognized by adding up revenue_recognized values from all agent commission records that match the filter criteria. Uses SQL SUM() function. Returns a single decimal number (e.g., 10000.00). Used for financial reporting, agent commission tracking, and revenue analysis. Example: If 3 agent commissions have recognized revenue $3k, $4k, $3k, this returns $10,000.00.",
        "aggregation": "sum"
    },
    # "business_type": {
    #     "type": "String",
    #     "operators": ["=", "in", "like"],
    #     "widget": "dropdown",
    #     "description": "Filter by business type"
    # },
    # "product_type": {
    #     "type": "String",
    #     "operators": ["=", "in", "like"],
    #     "widget": "dropdown",
    #     "description": "Filter by product type (risk category)"
    # },
    # "channel": {
    #     "type": "String",
    #     "operators": ["=", "in", "like"],
    #     "widget": "dropdown",
    #     "description": "Filter by channel"
    # },
    # "payment_frequency": {
    #     "type": "String",
    #     "operators": ["=", "in"],
    #     "widget": "dropdown",
    #     "description": "Filter by payment frequency"
    # },
    # "policy_number": {
    #     "type": "String",
    #     "operators": ["=", "in", "like"],
    #     "widget": "text",
    #     "description": "Filter by policy number"
    # },
    # "risk_category": {
    #     "type": "String",
    #     "operators": ["=", "in", "like"],
    #     "widget": "dropdown",
    #     "description": "Filter by risk category"
    # },
    # "currency_code": {
    #     "type": "String",
    #     "operators": ["=", "in"],
    #     "widget": "dropdown",
    #     "description": "Filter by currency code"
    # }
}

def get_filter_definitions(filters):
    """Return a list of filter field definitions for the given filter keys."""
    return [
        {"field": f, **PERFORMANCE_FIELD_DEFINITIONS.get(f, {"type": "Unknown", "operators": [], "widget": "text", "description": f})}
        for f in filters
    ]

PERFORMANCE_FIELD_REGISTRY = [
    # Sum Insured (Issued Policy)
    {
        "parameter": "issued_policy_sum_insured",
        "base_table": "crmp_issued_policies",
        "field": ["sum_insured"],
        "agg": "sum",
        "joins": [
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["risk_type", "product", "native_product", "insurer", "policy_effective_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["risk_type", "product", "native_product", "insurer", "policy_effective_date", "role", "agent_id"])
    },
    # Sum Insured (Policy Base)
    {
        "parameter": "policy_base_sum_insured",
        "base_table": "crmp_policy_base",
        "field": ["sum_insured"],
        "agg": "sum",
        "joins": [
            {"table": "core_users", "on": "crmp_policy_base.request_by_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.request_by_id",
        "filters": ["risk_type", "product", "native_product", "insurer", "policy_start_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["risk_type", "product", "native_product", "insurer", "policy_start_date", "role", "agent_id"])
    },
    # Premium Amount (Issued Policy)
    {
        "parameter": "issued_policy_premium_amount",
        "base_table": "crmp_issued_policies",
        "field": ["premium_amount"],
        "agg": "sum",
        "joins": [
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["risk_type", "product", "native_product", "insurer", "policy_effective_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["risk_type", "product", "native_product", "insurer", "policy_effective_date", "role", "agent_id"])
    },
    # Policy Count (Issued Policy)
    {
        "parameter": "policy_count",
        "base_table": "crmp_issued_policies",
        "field": ["id"],
        "agg": "count",
        "joins": [
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["product", "native_product", "insurer", "risk_type", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["product", "native_product", "insurer", "risk_type", "role", "agent_id"])
    },
    # Brokerage Commission: revenue recognized
    {
        "parameter": "brokerage_revenue_recognized",
        "base_table": "crmf_brokerage_commission",
        "field": ["revenue_recognized"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"])
    },
    # Brokerage Commission: revenue realized
    {
        "parameter": "brokerage_revenue_realized",
        "base_table": "crmf_brokerage_commission",
        "field": ["revenue_realized"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"])
    },
    # Brokerage Commission: agent commission
    {
        "parameter": "brokerage_agent_commission",
        "base_table": "crmf_brokerage_commission",
        "field": ["agent_commission"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"])
    },
    # Brokerage Commission: commission deductible
    {
        "parameter": "brokerage_commission_deductible",
        "base_table": "crmf_brokerage_commission",
        "field": ["commission_deductible"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"])
    },
    # Payments (crmf_payments): total paid amount
    {
        "parameter": "total_payments",
        "base_table": "crmf_payments",
        "field": ["paid_amount"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_payments.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["product", "native_product", "insurer", "risk_type", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["product", "native_product", "insurer", "risk_type", "role", "agent_id"])
    },
    # Sum of Premium Amount (Direct mapping for sum_of_premium_amount)
    {
        "parameter": "sum_of_premium_amount",
        "base_table": "crmp_issued_policies",
        "field": ["premium_amount", "sum_of_premium_amount"],
        "agg": "sum",
        "joins": [
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["risk_type", "product", "insurer", "policy_effective_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["risk_type", "product", "insurer", "policy_effective_date", "role", "agent_id"])
    },
    # Native Product ID (maps to product_id in crmp_policy_base)
    {
        "parameter": "native_product",
        "base_table": "crmp_policy_base",
        "field": ["product_id", "native_product_id"],
        "agg": "select",
        "joins": [
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["risk_type", "product", "insurer", "policy_start_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["risk_type", "product", "insurer", "policy_start_date", "role", "agent_id"])
    },
    # Policy Commission Amount (Agent Commission)
    {
        "parameter": "policy_commission_amount",
        "base_table": "crmf_agent_commission",
        "field": ["revenue_recognized"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_brokerage_commission", "on": "crmf_brokerage_commission.id = crmf_agent_commission.brokerage_commission_id"},
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["product", "native_product", "insurer", "risk_type", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["product", "native_product", "insurer", "risk_type", "role", "agent_id"])
    },
    # --- Added select/list registry entries for full coverage ---
    # Policies (select)
    {
        "parameter": "policies",
        "base_table": "crmp_issued_policies",
        "field": ["id"],
        "agg": "select",
        "joins": [
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["product", "native_product", "insurer", "risk_type", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["product", "native_product", "insurer", "risk_type", "role", "agent_id"])
    },
    # Sum Insureds (select)
    {
        "parameter": "sum_insureds",
        "base_table": "crmp_issued_policies",
        "field": ["sum_insured"],
        "agg": "select",
        "joins": [
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["risk_type", "product", "native_product", "insurer", "policy_effective_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["risk_type", "product", "native_product", "insurer", "policy_effective_date", "role", "agent_id"])
    },
    # Brokerage Revenue Recognized (select)
    {
        "parameter": "brokerage_revenue_recognized",
        "base_table": "crmf_brokerage_commission",
        "field": ["revenue_recognized"],
        "agg": "select",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date",  "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date",  "role", "agent_id"])
    },
    # Brokerage Revenue Realized (select)
    {
        "parameter": "brokerage_revenue_realized",
        "base_table": "crmf_brokerage_commission",
        "field": ["revenue_realized"],
        "agg": "select",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date",  "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date",  "role", "agent_id"])
    },
    # Overriding Commission (select)
    {
        "parameter": "overriding_commission",
        "base_table": "crmf_brokerage_commission",
        "field": ["overriding_commission_amount"],
        "agg": "select",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date",  "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date",  "role", "agent_id"])
    },
    # Commission Deductible (select)
    {
        "parameter": "commission_deductible",
        "base_table": "crmf_brokerage_commission",
        "field": ["commission_deductible"],
        "agg": "select",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"])
    },
    # Paid Amount (select)
    {
        "parameter": "paid_amount",
        "base_table": "crmf_payments",
        "field": ["paid_amount"],
        "agg": "select",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_payments.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["product", "native_product", "insurer", "risk_type", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["product", "native_product", "insurer", "risk_type", "role", "agent_id"])
    },
    # Agent Sales Target (sum)
    {
        "parameter": "sum_of_agent_sales_target",
        "base_table": "crmf_agent_sales_targets",
        "field": ["target_amount"],
        "agg": "sum",
        "joins": [
            {"table": "core_users", "on": "crmf_agent_sales_targets.agent_id = core_users.id"}
        ],
        "agent_field": "crmf_agent_sales_targets.agent_id",
        "filters": ["sales_target_agent_id", "sales_target_period_type", "sales_target_month", "sales_target_year"],
        "filter_definitions": get_filter_definitions(["sales_target_agent_id", "sales_target_period_type", "sales_target_month", "sales_target_year"])
    },
    # Agent Sales Target (select)
    {
        "parameter": "agent_sales_targets",
        "base_table": "crmf_agent_sales_targets",
        "field": ["id", "agent_id", "period_type", "month", "year", "target_amount"],
        "agg": "select",
        "joins": [
            {"table": "core_users", "on": "crmf_agent_sales_targets.agent_id = core_users.id"}
        ],
        "agent_field": "crmf_agent_sales_targets.agent_id",
        "filters": ["sales_target_agent_id", "sales_target_period_type", "sales_target_month", "sales_target_year"],
        "filter_definitions": get_filter_definitions(["sales_target_agent_id", "sales_target_period_type", "sales_target_month", "sales_target_year"])
    },
    # Agent Achieved (sum of premium_amount for agent)
    {
        "parameter": "sum_of_agent_achieved",
        "base_table": "crmp_issued_policies",
        "field": ["premium_amount"],
        "agg": "sum",
        "joins": [
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["product", "native_product", "insurer", "risk_type", "policy_effective_date", "sales_target_agent_id", "sales_target_period_type", "sales_target_month", "sales_target_year"],
        "filter_definitions": get_filter_definitions(["product", "native_product", "insurer", "risk_type", "policy_effective_date", "sales_target_agent_id", "sales_target_period_type", "sales_target_month", "sales_target_year"])
    },
    # Team Sales Target (sum)
    {
        "parameter": "sum_of_team_sales_target",
        "base_table": "crmf_team_sales_targets",
        "field": ["target_amount"],
        "agg": "sum",
        "joins": [
            {"table": "core_teams", "on": "crmf_team_sales_targets.team_id = core_teams.id"}
        ],
        "agent_field": "crmf_team_sales_targets.team_id",
        "filters": ["sales_target_team_id", "sales_target_period_type", "sales_target_month", "sales_target_year"],
        "filter_definitions": get_filter_definitions(["sales_target_team_id", "sales_target_period_type", "sales_target_month", "sales_target_year"])
    },
    # Team Sales Target (select)
    {
        "parameter": "team_sales_targets",
        "base_table": "crmf_team_sales_targets",
        "field": ["id", "team_id", "period_type", "month", "year", "target_amount"],
        "agg": "select",
        "joins": [
            {"table": "core_teams", "on": "crmf_team_sales_targets.team_id = core_teams.id"}
        ],
        "agent_field": "crmf_team_sales_targets.team_id",
        "filters": ["sales_target_team_id", "sales_target_period_type", "sales_target_month", "sales_target_year"],
        "filter_definitions": get_filter_definitions(["sales_target_team_id", "sales_target_period_type", "sales_target_month", "sales_target_year"])
    },
    # Team Achieved (sum of premium_amount for all agents in team)
    {
        "parameter": "sum_of_team_achieved",
        "base_table": "crmp_issued_policies",
        "field": ["premium_amount"],
        "agg": "sum",
        "joins": [
            {"table": "crmp_policy_base", "on": "crmp_issued_policies.policy_base_id = crmp_policy_base.id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"},
            {"table": "core_team_users", "on": "core_team_users.user_id = crmp_policy_base.sales_agent_id"},
            {"table": "core_teams", "on": "core_teams.id = core_team_users.team_id"}
        ],
        "agent_field": "core_teams.id",
        "filters": ["sales_target_team_id", "sales_target_period_type", "sales_target_month", "sales_target_year"],
        "filter_definitions": get_filter_definitions(["sales_target_team_id", "sales_target_period_type", "sales_target_month", "sales_target_year"])
    },
    # --- Additional missing registry entries ---
    # Sum of Commission Deductible (sum)
    {
        "parameter": "sum_of_commission_deductible",
        "base_table": "crmf_brokerage_commission",
        "field": ["commission_deductible", "sum_of_commission_deductible"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_policy_base.id = crmp_issued_policies.policy_base_id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "role", "agent_id"])
    },
    # Sum of Brokerage Revenue Recognized (sum)
    {
        "parameter": "sum_of_brokerage_revenue_recognized",
        "base_table": "crmf_brokerage_commission",
        "field": ["revenue_recognized", "sum_of_brokerage_revenue_recognized"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_policy_base.id = crmp_issued_policies.policy_base_id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "invoice_date", "role", "agent_id"])
    },
    # Sum of Brokerage Revenue Realized (sum)
    {
        "parameter": "sum_of_brokerage_revenue_realized",
        "base_table": "crmf_brokerage_commission",
        "field": ["revenue_realized", "sum_of_brokerage_revenue_realized"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_policy_base.id = crmp_issued_policies.policy_base_id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "role", "agent_id"])
    },
    # Sum of Agent Commission Realized (sum)
    {
        "parameter": "sum_of_agent_commission_realized",
        "base_table": "crmf_agent_commission",
        "field": ["revenue_realized", "sum_of_agent_commission_realized"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_brokerage_commission", "on": "crmf_brokerage_commission.id = crmf_agent_commission.brokerage_commission_id"},
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_policy_base.id = crmp_issued_policies.policy_base_id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "risk_type", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "risk_type", "role", "agent_id"])
    },
    # Sum of Agent Commission Recognized (sum)
    {
        "parameter": "sum_of_agent_commission_recognized",
        "base_table": "crmf_agent_commission",
        "field": ["revenue_recognized", "sum_of_agent_commission_recognized"],
        "agg": "sum",
        "joins": [
            {"table": "crmf_brokerage_commission", "on": "crmf_brokerage_commission.id = crmf_agent_commission.brokerage_commission_id"},
            {"table": "crmf_invoices", "on": "crmf_invoices.id = crmf_brokerage_commission.invoice_id"},
            {"table": "crmp_issued_policies", "on": "crmp_issued_policies.id = crmf_invoices.issued_policy_id"},
            {"table": "crmp_policy_base", "on": "crmp_policy_base.id = crmp_issued_policies.policy_base_id"},
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["status", "product", "native_product", "insurer", "risk_type", "role", "agent_id"],
        "filter_definitions": get_filter_definitions(["status", "product", "native_product", "insurer", "risk_type", "role", "agent_id"])
    },
    # Sales Agent ID (select) - from policy_base
    {
        "parameter": "sales_agent",
        "base_table": "crmp_policy_base",
        "field": ["sales_agent_id"],
        "agg": "select",
        "joins": [
            {"table": "core_users", "on": "crmp_policy_base.sales_agent_id = core_users.id"}
        ],
        "agent_field": "crmp_policy_base.sales_agent_id",
        "filters": ["product", "native_product", "insurer", "risk_type", "role"],
        "filter_definitions": get_filter_definitions(["product", "native_product", "insurer", "risk_type", "role"])
    },
] 

