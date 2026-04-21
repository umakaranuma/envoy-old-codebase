# Overdue Invoice Management

This document explains how to manage overdue invoices using the provided utilities and SQL queries.

## 📁 **File Structure**

- **`envoy_bu_policy_api/finance/controllers/utils/overdue_invoice_utils.py`** - Python utilities for overdue invoice management
- **`envoy_bu_policy_api/policy/controllers/endorsement_request_controller.py`** - Endorsement-specific status updates (Cancelled, Refunded)

## 🎯 **What Each Module Handles**

### **1. Endorsement Controller (Endorsement-Specific Status Updates)**
- **Cancelled**: Automatically sets invoice status to "Cancelled" when endorsement type is "Cancellations" (ID: 3)
- **Refunded**: Automatically sets invoice status to "Refunded" when endorsement type is "Refund" (ID: 2)

### **2. Overdue Invoice Utils (Finance Invoice Overdue Management)**
- **Overdue**: Updates finance invoice status to "Overdue" when payment deadline has passed and invoice remains unpaid
- **Bulk Updates**: Mass update all overdue finance invoices in the system
- **SQL Queries**: Ready-to-run SQL queries for DevOps team

## 🚀 **For DevOps Team - Live Server Operations**

### **Quick Overdue Check (Safe Read-Only)**
```sql
-- Check how many invoices are overdue
SELECT 
    'Finance Invoices' as invoice_type,
    COUNT(*) as overdue_count,
    SUM(outstanding_amount) as total_outstanding
FROM crmf_invoices 
WHERE due_date < CURDATE() 
AND outstanding_amount > 0
UNION ALL
SELECT 
    'Policy Invoices' as invoice_type,
    COUNT(*) as overdue_count,
    SUM(outstanding_amount) as total_outstanding
FROM crmp_invoices 
WHERE due_date < CURDATE() 
AND outstanding_amount > 0;
```

### **Check Overdue Finance Invoices**
```sql
-- Check overdue finance invoices
SELECT 
    id,
    invoice_number,
    due_date,
    outstanding_amount,
    status_id,
    CASE 
        WHEN status_id = (SELECT id FROM core_status WHERE name = 'Overdue' AND module = 'finance_invoice') 
        THEN 'Already Overdue'
        ELSE 'Needs Update'
    END as status_check
FROM crmf_invoices 
WHERE due_date < CURDATE() 
AND outstanding_amount > 0
ORDER BY due_date ASC;
```

### **Update Overdue Finance Invoices**
```sql
-- Update overdue finance invoices
UPDATE crmf_invoices 
SET status_id = (SELECT id FROM core_status WHERE name = 'Overdue' AND module = 'finance_invoice')
WHERE due_date < CURDATE() 
AND outstanding_amount > 0
AND status_id != (SELECT id FROM core_status WHERE name = 'Overdue' AND module = 'finance_invoice');
```

### **Check Invoice Status Summary**
```sql
-- Get summary of finance invoice statuses
SELECT 
    'Finance Invoices' as invoice_type,
    cs.name as status_name,
    COUNT(*) as count
FROM crmf_invoices fi
JOIN core_status cs ON fi.status_id = cs.id
GROUP BY cs.name, cs.id
ORDER BY count DESC;
```

## 🔧 **For Developers - Python Functions**

### **Quick Overdue Check**
```python
from envoy_bu_policy_api.finance.controllers.utils.overdue_invoice_utils import run_overdue_check

# Safe read-only operation
summary = run_overdue_check()
print(summary)
```

### **Bulk Update Overdue Invoices**
```python
from envoy_bu_policy_api.finance.controllers.utils.overdue_invoice_utils import bulk_update_overdue_invoices

# Update all overdue invoices
result = bulk_update_overdue_invoices()
print(result)
```

### **Get SQL Queries**
```python
from envoy_bu_policy_api.finance.controllers.utils.overdue_invoice_utils import get_overdue_invoices_sql_queries

# Get all SQL queries
queries = get_overdue_invoices_sql_queries()
for name, query in queries.items():
    print(f"\n--- {name} ---")
    print(query)
```

## 📋 **Recommended Workflow for DevOps**

1. **First**: Run the "Quick Overdue Check" to see how many invoices are overdue
2. **Second**: Run the "Check Overdue" queries to see which specific invoices need updates
3. **Third**: Run the "Update Overdue" queries to set the correct status
4. **Fourth**: Run the "Check Invoice Status Summary" to verify the updates

## ⚠️ **Important Notes**

- **Backup**: Always backup the database before running UPDATE queries
- **Test**: Test queries on a staging environment first
- **Timing**: Consider running these queries during low-traffic periods
- **Monitoring**: Monitor the system after running updates to ensure no issues

##  **Troubleshooting**

If you encounter issues:
1. Check that the `core_status` table has the "Overdue" status for both modules
2. Verify that `due_date` and `outstanding_amount` fields contain valid data
3. Ensure you have proper database permissions
4. Check the database logs for any constraint violations
