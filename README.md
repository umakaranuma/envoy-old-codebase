# Envoy — Insurance Brokerage System

## What is Envoy?

Envoy is a comprehensive, web-based **Insurance Brokerage Management Platform** designed for insurance agency companies. It streamlines the complete lifecycle of insurance operations — from managing users, customers, and leads all the way through to policy management, claims, and financial settlements.

Envoy acts as the central hub for insurance brokerage operations, connecting sales teams, policy officers, and finance staff under one unified platform — while giving customers their own dedicated self-service portal.

---

## Who is it for?

The platform is built for two groups of users:

- **Internal Staff** — Agents, managers, policy officers, and finance teams who manage the day-to-day operations of the brokerage through the main web application.
- **Customers** — Policyholders who access their own dedicated portal to request quotations, manage policies, submit claims, and make payments.

---

## Why Envoy?

Managing an insurance brokerage involves juggling multiple workflows — leads, quotations, policies, risks, claims, commissions, and more. Envoy brings all of these under one roof with:

- **Role-Based Access Control (RBAC)** — Users only see and interact with what their job role permits.
- **Separate Customer Portal** — Customers are fully isolated from internal operations for security and simplicity.
- **End-to-End Workflow** — Full lifecycle coverage from lead capture → quotation → policy → claim → financial settlement.
- **Modular Architecture** — Each module operates independently but integrates seamlessly across the platform.

---

## Dev Environment Credentials

Use the following credentials to access the development environment UI panels:
- **Email:** `relepor245@binafex.com`
- **Password:** `12345678@`

---

## Platform Modules

The Envoy platform is made up of the following key modules:

1. **Envoy Core** — Manages users, roles, permissions, customers, contacts, and sales teams
2. **Envoy CRM** — Manages leads, quotation requests, and follow-ups
3. **Envoy Policy** — Manages policy creation, risk management, and confirmed policies
4. **Envoy Finance** — Manages commissions, payments, incentives, DR/CR notes, and the general ledger
5. **Envoy Customer Portal** — A self-service portal for customers to request quotations, manage policies, submit claims, and make payments

---

## How Does It Work?

1. **User Setup** — Admins create internal users and assign roles and permissions via the Core module.
2. **Customer Onboarding** — Customer records are created and customers are given access to their dedicated portal.
3. **Lead & Quotation** — Sales agents capture leads and manage quotation requests through the CRM module.
4. **Policy Creation** — Policies are created from confirmed quotations, leads, or independently via the Policy module.
5. **Risk Management** — Customer risk items (vehicles, houses, etc.) are registered and managed against policies.
6. **Claims** — Once a policy is confirmed, customers can submit claims through the customer portal or internally.
7. **Finance & Settlement** — Commissions, payments, and incentives are calculated and settled through the Finance module.

---

## Tech Stack & Project Structure

The platform is built using a modern, scalable tech stack and organized into module-based directories — each with its own dedicated API and UI.

---

### 📁 Project Structure

```
envoy/
├── envoy_core/
│   ├── envoy_core_api/          # Core module API (Django)
│   └── envoy_core_ui/           # Core module UI (Next.js)
│
├── envoy_crm/
│   ├── envoy_crm_api/           # CRM module API — Leads & Follow-ups (Django)
│   └── envoy_crm_ui/            # CRM module UI (Next.js)
│
├── envoy_policy/
│   ├── envoy_policy_api/        # Policy management API (Django)
│   ├── envoy_policy_ui/         # Policy management UI (Next.js)
│   ├── envoy_finance_api/       # Finance module API (Django)
│   └── envoy_finance_ui/        # Finance module UI (Next.js)
│
└── envoy_customer/
    ├── envoy_customer_api/      # Customer portal API (Django)
    └── envoy_customer_ui/       # Customer portal UI (Next.js)
```

---

### Backend

All APIs are built with **Django (Django REST Framework)** and follow a RESTful architecture.

| Directory | Module | Responsibility |
|---|---|---|
| `envoy_core/envoy_core_api` | Core | Users, roles, permissions, customers, contacts, sales teams |
| `envoy_crm/envoy_crm_api` | CRM | Leads, quotations, and follow-up management |
| `envoy_policy/envoy_policy_api` | Policy | Policy creation, risk management, and claims |
| `envoy_policy/envoy_finance_api` | Finance | Commissions, payments, incentives, ledger |
| `envoy_customer/envoy_customer_api` | Customer Portal | Customer login, requests, claims, payments |

---

### Frontend (Web)

All UIs are built with **Next.js**.

| Directory | Module | Responsibility |
|---|---|---|
| `envoy_core/envoy_core_ui` | Core | User management, roles, customer records, sales teams |
| `envoy_crm/envoy_crm_ui` | CRM | Leads, quotations, and follow-ups |
| `envoy_policy/envoy_policy_ui` | Policy | Policy creation, risk management, and claims |
| `envoy_policy/envoy_finance_ui` | Finance | Commissions, payments, incentives, DR/CR notes, general ledger |
| `envoy_customer/envoy_customer_ui` | Customer Portal | Customer self-service portal |

---

## Module Overview

### 1. Envoy Core
Manages the foundational entities of the platform — users, permissions, customers, and teams.

- User creation and management
- Role-based access control and permissions
- Customer records management
- Contact management
- Sales team configuration

---

### 2. Envoy CRM
Handles the sales pipeline and customer relationship management.

- Lead capture and tracking
- Quotation request management
- Follow-up scheduling and management
- Quotation confirmations

---

### 3. Envoy Policy
Covers the full policy lifecycle from creation through to risk management.

- Policy creation (from leads, quotations, or independently)
- Risk management — customer assets such as vehicles, houses, and other insurable items
- Confirmed policy tracking

---

### 4. Envoy Finance
Manages all financial operations of the brokerage.

- Sales team and member commission management
- Payment tracking and management
- Incentive setup and configuration
- Automated incentive generation based on business logic
- Customer financial report generation
- Debit / Credit (DR/CR) notes
- General ledger management

---

### 5. Envoy Customer Portal
A dedicated self-service portal for customers, completely separate from the internal application.

- Secure customer login
- Quotation requests
- Policy requests
- Quotation confirmation
- Claims submission against active policies
- Payment processing

---

## Our Commitment

Envoy is built to give insurance brokerages a reliable, secure, and scalable platform that grows with their business — ensuring every customer gets the right coverage and every team member has the tools they need to deliver exceptional service.

---

*Envoy — Powering Insurance Brokerages from Lead to Settlement.*
