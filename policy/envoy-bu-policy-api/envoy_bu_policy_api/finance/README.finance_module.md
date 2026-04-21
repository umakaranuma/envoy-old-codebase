# Finance Module Documentation

## Overview

The finance module manages all financial operations related to insurance policies, including invoice generation, payments, commissions, general ledger, journal entries, and reporting. The main flow starts from the creation of an issued policy and continues through invoicing, payment processing, commission calculation, and accounting entries.

---

## Folder Structure & Key Files

- **controllers/**: Business logic for API endpoints (views)
- **models/**: Django ORM models for finance-related tables
- **controllers/utils/**: Utility functions for accounting, ledgers, invoices, etc.
- **controllers/utils/commission/**: Commission calculation and related utilities
- **config/**: Static configuration (transaction types, performance fields)
- **migrations/**: Django migrations for schema changes

---

## Main Flow: Issued Policy to Accounting

1. **Issued Policy Creation** (policy module)
2. **Invoice Generation** (`controllers/utils/invoice_utils.py`)
3. **Payment Processing** (`controllers/payment_controller.py`)
4. **Commission Calculation** (`controllers/utils/commission/main.py`)
5. **General Ledger & Journal Entries** (`controllers/utils/general_ledger_utils.py`, `controllers/utils/journal_entry_utils.py`)
6. **Reporting & Summaries** (various controllers)

---

## Sales Target Management

### Agent Sales Targets

- **Model:** `crmf_agent_sales_target.py` (`CrmfAgentSalesTarget`)
  - Stores monthly/yearly sales targets for individual agents.
  - Fields: agent, period_type (monthly/yearly), month, year, target_amount.
- **Controller:** `agent_sales_target_controller.py`
  - Endpoints to create, update, and fetch agent sales targets.
  - Calculates 'achieved' (actual sales) by summing premium amounts from issued policies for the agent and period.
- **Config:** `performance_field_registry.py`
  - Defines aggregation and filtering for agent sales targets and achievements.

### Team Sales Targets

- **Model:** `crmf_team_sales_target.py` (`CrmfTeamSalesTarget`)
  - Stores monthly/yearly sales targets for teams.
  - Fields: team, period_type, month, year, target_amount.
- **Controller:** `team_sales_target_controller.py`
  - Endpoints to create, update, and fetch team sales targets.
  - Calculates 'achieved' (actual sales) by summing premium amounts from issued policies for all agents in the team and period.
- **Config:** `performance_field_registry.py`
  - Defines aggregation and filtering for team sales targets and achievements.

### Flow

1. Admin sets sales targets for agents/teams via API.
2. Achieved values are calculated dynamically based on issued policies.
3. Used in performance dashboards and as criteria for incentives.

---

## Incentive Calculation & Awarding

### Incentive Setup

- **Model:** `crmf_incentive_setups.py` (`IncentiveSetup`)
  - Defines incentive programs: name, period, reward type (fixed/percentage), value, performance fields (logic tree), base field.
- **Model:** `crmf_incentives.py` (`Incentive`)
  - Stores awarded incentives: agent, setup, performance metric, actual value, reward type, amount, status, matched condition.

### Controllers & Utilities

- **Controller:** `incentive_controller.py`
  - Endpoints to initiate incentive award, run all awards, and manage incentive setups.
  - Calls utility functions to aggregate performance, evaluate logic, and save records.
- **Utility:** `utils/incentive_utils.py`
  - `aggregate_performance_data`: Aggregates agent performance for the period and fields defined in the setup.
  - `find_agents_for_period`: Finds eligible agents for a setup and period.
  - `calculate_incentive_reward`: Evaluates the logic tree (AND/OR) to determine eligibility and reward amount.
  - `save_incentive_record`: Saves the awarded incentive to the database.
  - `award_incentives_for_setup`: Orchestrates the full process for a setup and all agents/periods.

### Flow

1. Incentive setups are defined with logic trees (e.g., "If agent achieves X sales, award Y").
2. On award trigger, the system aggregates each agent's performance for the period.
3. The logic tree is evaluated to check eligibility and calculate the reward (fixed or percentage of base).
4. Eligible incentives are saved and can be paid out (status updated to 'paid').

---

## Detailed File & Function Reference

### 1. controllers/utils/invoice_utils.py

- **generate_invoice_for_issued_policy(issued_id, is_update=False, user=None)**
  - Generates or updates an invoice for a given issued policy.
  - Handles transaction type, note type, premium, due date, and links to policy.
  - Triggers general ledger entry and commission calculation if applicable.
- **generate_invoice_for_endorsement(endorsement_id, ...)**
  - Similar to above, but for policy endorsements.

### 2. controllers/payment_controller.py

- **create_payment(request)**
  - Validates and records a payment against an invoice.
  - Updates invoice totals, handles receipts, and triggers commission/ledger updates.
- **update_invoice_payment_details(invoice_id, paid_amount)**
  - Updates paid/outstanding amounts on invoice after payment.

### 3. controllers/utils/commission/main.py

- **calculate_commission_amounts(...)**
  - Calculates brokerage and agent commissions for an invoice.
  - Handles different commission types and inserts records.

### 4. controllers/utils/general_ledger_utils.py

- **create_general_ledger_entry(transaction_data, user=None)**
  - Creates a general ledger entry for a transaction (policy, payment, commission, etc.).
  - Generates unique payment IDs and links to entities.

### 5. controllers/utils/journal_entry_utils.py

- **create_journal_entries(transaction_data, user=None)**
  - Creates debit/credit journal entries for financial transactions.
  - Ensures correct account mapping and entry numbering.
- **get_account_number_by_type(transaction_type, is_debit=True)**
  - Maps transaction types to account numbers for journal entries.

### 6. controllers/utils/accounting_utils.py

- **create_accounting_entries_for_payment(invoice_id, payment_data, user=None)**
  - Orchestrates all accounting entries (ledger, journal) when a payment is made.

### 7. models/crmf_invoices.py

- **Invoice**
  - Model for invoices, linking to issued policies, endorsements, insurer, insured, and entity.
  - Tracks amounts, due dates, and payment status.

### 8. models/crmf_payments.py

- **Payment**
  - Model for payments made against invoices.
  - Tracks paid/outstanding amounts, method, and receipt info.

### 9. models/crmf_brokerage_commission.py, crmf_agent_commission.py

- **BrokerageCommission, AgentCommission**
  - Models for storing commission calculations and payment status.

### 10. models/crmf_general_ledger.py

- **GeneralLedger**
  - Model for general ledger entries, linking to invoices and payers.

### 11. models/crmf_journal_entries.py

- **JournalEntry**
  - Model for journal entries (debit/credit) for accounting.

### 12. config/transaction_types.py

- **TRANSACTION_TYPES**
  - Static config for transaction types (New Business, Renewal, Refund, etc.)
  - Used to determine commissionability and note types.

---

## Additional Controllers (for reporting, summaries, etc.)

- **commission_setup_controller.py**: Manage commission setup and teams.
- **mapping_controller.py**: Bulk import/mapping of payments and data.
- **service_render_controller.py**: Handles service-related financial flows.
- **agent_commission_payment_controller.py**: Agent commission payment processing.
- **general_ledger_controller.py**: Ledger entry APIs and account balances.
- **cash_flow_journal_controller.py**: Cash flow reporting.
- **debtor_aging_controller.py**: Debtor aging reports.
- **incentive_controller.py**: Incentive setup and award logic.

---

## How It All Connects (Flow Diagram)

1. **Issued Policy Created** →
2. **Invoice Generated** (`generate_invoice_for_issued_policy`) →
3. **Payment Made** (`create_payment`) →
4. **Commission Calculated** (`calculate_commission_amounts`) →
5. **Ledger/Journal Entries Created** (`create_general_ledger_entry`, `create_journal_entries`)
6. **Reporting/Queries** (various controllers)

---

## Tips for Developers

- Start by tracing the flow from issued policy creation in the policy module.
- Follow the function calls as described above to see how data moves through the system.
- Use the config files to understand transaction/commission types.
- Each major financial event (invoice, payment, commission) triggers accounting entries.
- Reporting controllers aggregate and present financial data for business needs.

---

For more details, refer to the code in each file as listed above. This document is a high-level map to help you get started quickly.
