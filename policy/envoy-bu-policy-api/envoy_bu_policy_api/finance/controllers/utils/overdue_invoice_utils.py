"""
Overdue Invoice Management Utilities

This module provides functions and SQL queries for managing overdue invoices.
These functions are designed to be run on the live server by DevOps team.
"""

from datetime import date
from decimal import Decimal
from mServices import QueryBuilderService


def get_overdue_status_id():
    """
    Get the Overdue status ID for finance invoices.
    
    Returns:
        int: Status ID or None if not found
    """
    try:
        from .invoice_utils import get_finance_invoice_status_id
        return get_finance_invoice_status_id("Overdue")
    except Exception as e:
        print(f"Error getting overdue status ID: {str(e)}")
        return None


def bulk_update_overdue_invoices():
    """
    Bulk update all overdue invoices in the system.
    This function can be run manually or via a scheduled task.
    
    Returns:
        dict: Summary of updates performed
    """
    try:
        today = date.today()
        summary = {
            "finance_invoices_updated": 0,
            "errors": []
        }
        
        # Get overdue finance invoices
        overdue_finance_invoices = (
            QueryBuilderService("crmf_invoices")
            .select("id", "invoice_number", "due_date", "outstanding_amount")
            .where("due_date", "<", today)
            .where("outstanding_amount", ">", "0")
            .get()
        )
        
        # Update finance invoices to overdue
        overdue_status_id = get_overdue_status_id()
        if overdue_status_id:
            for invoice in overdue_finance_invoices:
                try:
                    update_result = QueryBuilderService("crmf_invoices").where("id", invoice["id"]).update({
                        "status_id": overdue_status_id
                    })
                    if update_result > 0:
                        summary["finance_invoices_updated"] += 1
                        print(f"Updated finance invoice {invoice['id']} ({invoice['invoice_number']}) to Overdue")
                except Exception as e:
                    error_msg = f"Error updating finance invoice {invoice['id']}: {str(e)}"
                    summary["errors"].append(error_msg)
                    print(error_msg)
        
        print(f"Bulk update completed. Finance invoices updated: {summary['finance_invoices_updated']}")
        return summary
        
    except Exception as e:
        error_msg = f"Error in bulk update: {str(e)}"
        print(error_msg)
        return {"error": error_msg}


def get_overdue_invoices_sql_queries():
    """
    Returns SQL queries for checking and updating overdue invoices.
    These can be run directly on the live server by DevOps.
    
    Returns:
        dict: Dictionary containing SQL queries
    """
    queries = {
        "check_overdue_finance_invoices": """
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
        """,
        

        
        "update_overdue_finance_invoices": """
            -- Update overdue finance invoices
            UPDATE crmf_invoices 
            SET status_id = (SELECT id FROM core_status WHERE name = 'Overdue' AND module = 'finance_invoice')
            WHERE due_date < CURDATE() 
            AND outstanding_amount > 0
            AND status_id != (SELECT id FROM core_status WHERE name = 'Overdue' AND module = 'finance_invoice');
        """,
        

        
        "check_invoice_status_summary": """
            -- Get summary of finance invoice statuses
            SELECT 
                'Finance Invoices' as invoice_type,
                cs.name as status_name,
                COUNT(*) as count
            FROM crmf_invoices fi
            JOIN core_status cs ON fi.status_id = cs.id
            GROUP BY cs.name, cs.id
            ORDER BY count DESC;
        """,
        
        "check_overdue_summary": """
            -- Get summary of overdue finance invoices
            SELECT 
                'Finance Invoices' as invoice_type,
                COUNT(*) as overdue_count,
                SUM(outstanding_amount) as total_outstanding
            FROM crmf_invoices 
            WHERE due_date < CURDATE() 
            AND outstanding_amount > 0;
        """
    }
    
    return queries


def run_overdue_check():
    """
    Run a quick check to see how many invoices are overdue.
    This is a safe read-only operation.
    
    Returns:
        dict: Summary of overdue invoices
    """
    try:
        today = date.today()
        
        # Count overdue finance invoices
        overdue_finance_count = (
            QueryBuilderService("crmf_invoices")
            .where("due_date", "<", today)
            .where("outstanding_amount", ">", "0")
            .count()
        )
        
        summary = {
            "overdue_finance_invoices": overdue_finance_count,
            "total_overdue": overdue_finance_count,
            "check_date": str(today)
        }
        
        print(f"Overdue Check Summary: {summary}")
        return summary
        
    except Exception as e:
        error_msg = f"Error in overdue check: {str(e)}"
        print(error_msg)
        return {"error": error_msg}
