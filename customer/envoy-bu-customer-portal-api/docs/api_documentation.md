# Envoy BU Policy API Documentation

## Overview
This document provides comprehensive documentation for the Envoy BU Policy API endpoints, specifically focusing on financial and commission-related operations.

## Base URL
`/api/customer/`

## Authentication
[Authentication details to be added]

## Endpoints

### General Ledger
- **Endpoint**: `GET /general-ledger`
- **Purpose**: Retrieve all general ledger entries
- **Response**: List of general ledger entries
- **Dev Notes**: 
  - Can be used for charting account balances
  - Supports filtering by date range
  - Useful for financial reporting and analysis

### Commission Setup
- **Endpoint**: `GET /commission-setups`
- **Purpose**: Get all commission setup configurations
- **Response**: List of commission setups
- **Dev Notes**:
  - Used for managing commission structures
  - Supports team-based commission setups

### Service Renders
- **Endpoint**: `GET /service-renders`
- **Purpose**: Get all service render records
- **Response**: List of service renders
- **Dev Notes**:
  - Includes payment and invoice status
  - Supports filtering by service type
  - Useful for service tracking and billing

### Invoices
- **Endpoint**: `GET /invoices`
- **Purpose**: Get all invoices
- **Response**: List of invoices
- **Dev Notes**:
  - Supports filtering by status
  - Includes payment information
  - Can be used for invoice tracking and management

### Payments
- **Endpoint**: `GET /payments`
- **Purpose**: Get all payments
- **Response**: List of payments
- **Dev Notes**:
  - Supports filtering by payment method
  - Includes payment status
  - Useful for payment tracking and reconciliation

### Brokerage Commissions
- **Endpoint**: `GET /brokerage-commissions`
- **Purpose**: Get all brokerage commission records
- **Response**: List of brokerage commissions
- **Dev Notes**:
  - Supports filtering by date range
  - Includes commission totals
  - Useful for brokerage commission tracking

### Agent Commissions
- **Endpoint**: `GET /agent-commissions`
- **Purpose**: Get all agent commission records
- **Response**: List of agent commissions
- **Dev Notes**:
  - Supports filtering by agent
  - Includes commission totals
  - Useful for agent commission tracking

### My Commissions
- **Endpoint**: `GET /my-commissions`
- **Purpose**: Get commission records for the current user
- **Response**: List of personal commission records
- **Dev Notes**:
  - Includes policy statistics
  - Supports filtering by date range
  - Useful for personal commission tracking

### Chart of Accounts
- **Endpoint**: `GET /chart-of-accounts`
- **Purpose**: Get all chart of accounts entries
- **Response**: List of chart of accounts
- **Dev Notes**:
  - Supports hierarchical account structure
  - Useful for financial reporting
  - Can be used for account balance tracking

### Journal Entries
- **Endpoint**: `GET /journal-entries`
- **Purpose**: Get all journal entries
- **Response**: List of journal entries
- **Dev Notes**:
  - Supports filtering by date range
  - Includes entry details
  - Useful for financial tracking

### Cash Flow Journal
- **Endpoint**: `GET /cash-flow-journal`
- **Purpose**: Get cash flow journal entries
- **Response**: List of cash flow entries
- **Dev Notes**:
  - Includes totals
  - Supports filtering by date range
  - Useful for cash flow analysis

### Debtor Aging
- **Endpoint**: `GET /debtor-aging`
- **Purpose**: Get debtor aging report
- **Response**: List of aging records
- **Dev Notes**:
  - Supports aging bucket analysis
  - Useful for accounts receivable tracking
  - Can be used for collection management

### Reports
- **Endpoint**: `GET /policies-made`
- **Purpose**: Get policies made report
- **Response**: List of policy records
- **Dev Notes**:
  - Supports filtering by date range
  - Useful for policy tracking

- **Endpoint**: `GET /commission-earned`
- **Purpose**: Get commission earned report
- **Response**: List of earned commission records
- **Dev Notes**:
  - Supports filtering by date range
  - Useful for commission analysis

- **Endpoint**: `GET /commission-given`
- **Purpose**: Get commission given report
- **Response**: List of given commission records
- **Dev Notes**:
  - Supports filtering by date range
  - Useful for commission distribution analysis

## Charting Capabilities
All endpoints can be used to create various types of charts:

1. **Bar Charts**:
   - Commission comparisons
   - Policy counts
   - Account balances

2. **Line Charts**:
   - Cash flow trends
   - Commission trends
   - Policy growth

3. **Pie Charts**:
   - Commission distribution
   - Account distribution
   - Aging bucket distribution

4. **Area Charts**:
   - Cumulative cash flow
   - Cumulative commissions

## Best Practices
1. Use appropriate date range filters for time-based data
2. Implement pagination for large datasets
3. Cache frequently accessed data
4. Use appropriate chart types for different data types
5. Implement error handling for API responses

## Error Handling
- All endpoints return appropriate HTTP status codes
- Error responses include detailed error messages
- Implement proper error handling in UI components

## Rate Limiting
[Rate limiting details to be added]

## Versioning
[API versioning details to be added]

## Support
For any questions or issues, please contact the development team. 