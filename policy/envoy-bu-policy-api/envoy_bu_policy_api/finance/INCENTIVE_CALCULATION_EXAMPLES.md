# Incentive calculation examples (with amounts)

This document shows how incentive amounts are calculated for different setups, with concrete numbers.

---

## 1. Percentage reward (standard agent)

**Setup:** Conditions: role = Sales Agent, sum_of_agent_achieved >= sum_of_agent_sales_target. Reward: 2% of `sum_of_agent_commission_recognized`.

**Formula:** `incentive_amount = (base_field_value × reward_percentage) / 100`

| Step | Value | Source |
|------|--------|--------|
| Base field | `sum_of_agent_commission_recognized` | Commission recognized for the agent in the period |
| Base value example | 42,500 | From performance data (aggregated by policy’s sales_agent_id) |
| Reward % | 2 | From setup reward_type_value |
| **Calculation** | (42,500 × 2) / 100 | **= 850.00** |

**Result:** Incentive amount = **850.00**

---

## 2. Team lead + product (percentage of commission received)

**Setup:** Conditions: team_role = Team Lead, product = 31 (e.g. 3 OPTION MOTOR - MBSL), sum_of_agent_achieved >= sum_of_agent_sales_target. Reward: 10% of `sum_of_agent_commission_recognized`.

**Important:** For team leads, the base is commission **received** by the team lead (including override from team sales), not commission from policies they personally sold. Aggregation uses `crmf_agent_commission.agent_id` (recipient) instead of `sales_agent_id` (policy seller).

| Step | Value | Source |
|------|--------|--------|
| Base field | `sum_of_agent_commission_recognized` | Commission **received** by team lead for product 31 in period |
| Base value example | 12,000 | Override + any direct commission, filtered by product_id = 31 |
| Reward % | 10 | From setup |
| **Calculation** | (12,000 × 10) / 100 | **= 1,200.00** |

**Result:** Incentive amount = **1,200.00**

If we had used “commission from policies sold by team lead” (sales_agent_id), the base would often be 0 and the amount wrong.

---

## 3. Team-based validation (all members achieved target)

**Setup:** Team lead incentive; team is eligible only if **all** team members (excluding manager) meet their target in the period.

**Target per member:** Sum of **monthly** targets in `crmf_agent_sales_targets` over the full period (all months between start_date and end_date). Targets are **not** product-specific.

**Achieved per member:** Sum of premium from issued policies in the period. If the setup has a product filter, achieved is **only** premium for that product.

**Example:** Period 2025-01-28 to 2026-03-05, product_id = 31.

| Member | Target (sum of months in period) | Achieved (product 31 only) | Met? |
|--------|-----------------------------------|----------------------------|------|
| 9 | 500,000 | 1,040,000 | Yes (1,040,000 ≥ 500,000) |
| 8 | 30,000 | 30,000 | Yes |
| 5 | 0 (no target rows) | 0 | No (target missing → fail) |

If **any** member has target = 0 or achieved &lt; target, the team fails and the team lead gets no incentive for that team.

---

## 4. Fixed reward

**Setup:** Reward type = fixed (e.g. 10.0). No base field used for the amount.

**Formula:** `incentive_amount = reward_type_value`

| Step | Value |
|------|--------|
| Reward value | 10.0 |
| **Result** | **10.00** |

---

## 5. Summary of formulas

| Reward type | Formula | Example |
|-------------|---------|--------|
| Percentage | `(base_field_value × reward_%) / 100` | (42,500 × 2) / 100 = **850.00** |
| Team lead % (with product) | Same; base = commission **received** (agent_id) for that product | (12,000 × 10) / 100 = **1,200.00** |
| Fixed | `reward_type_value` | **10.00** |

Base field values come from bulk aggregation (and for team lead + commission, from aggregation by `crmf_agent_commission.agent_id` when `team_role = "team lead"`).
