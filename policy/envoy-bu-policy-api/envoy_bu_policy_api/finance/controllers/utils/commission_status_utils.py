"""
Commission Status Utilities
Handles status configuration and maintenance for Brokerage and Agent Commissions
All status data is fetched from core_status table - no hardcoded configs needed.
"""
from mServices import QueryBuilderService
from core_models.core_models import Status


def ensure_commission_statuses_exist():
    """
    Ensure all commission statuses exist in core_status table.
    Creates statuses if they don't exist.
    Uses the same pattern as other statuses in the application.
    """
    try:
        # Brokerage Commission statuses
        # Statuses are based on payment that brokerage receives from insurer
        brokerage_statuses = [
            ("PENDING", "No commission has received yet since there were no settlements done by the customer", "brkg_comm_pending", "finance", "#B54708", 1),
            ("PARTIALLY RECEIVED", "Customer has done a part payment so the insurer has paid us partially", "brkg_comm_part_recv", "finance", "#175CD3", 2),
            ("RECEIVED IN FULL", "Customer has done the complete payment and the commission is received in full", "brkg_comm_recv_full", "finance", "#067647", 3),
        ]
        
        # Agent Commission statuses
        # Statuses are based on payment made to agent by broker
        agent_statuses = [
            ("PENDING", "Broker might or might not have received brokerage commission but hasn't done any settlements to the agent", "agent_comm_pending", "finance", "#B54708", 1),
            ("PARTIALLY PAID", "Broker might or might not have received brokerage commission and has done partial settlements to the agent", "agent_comm_part_paid", "finance", "#175CD3", 2),
            ("FULLY PAID", "Broker might or might not have received brokerage commission and has done the full settlement to the agent", "agent_comm_full_paid", "finance", "#067647", 3),
        ]
        
        # Create/update all statuses
        all_statuses = brokerage_statuses + agent_statuses
        
        for name, desc, typ, mod, color, idx in all_statuses:
            # First try to find by type+module (preferred lookup)
            existing_status = Status.objects.filter(type=typ, module=mod).first()
            
            if existing_status:
                # Update existing status
                existing_status.name = name
                existing_status.description = desc
                existing_status.color = color
                existing_status.sort_index = idx
                existing_status.save()
            else:
                # Check if status exists with same name+module but different type
                existing_by_name = Status.objects.filter(name=name, module=mod).first()
                
                if existing_by_name:
                    # Update the type of existing status
                    existing_by_name.type = typ
                    existing_by_name.description = desc
                    existing_by_name.color = color
                    existing_by_name.sort_index = idx
                    existing_by_name.save()
                else:
                    # Create new status
                    Status.objects.create(
                        name=name,
                        description=desc,
                        type=typ,
                        module=mod,
                        color=color,
                        sort_index=idx
                    )
        
        return True
    except Exception as e:
        print(f"Error ensuring commission statuses exist: {str(e)}")
        return False


def calculate_brokerage_commission_status(customer_settlements, revenue_realized, revenue_recognized):
    """
    Calculate brokerage commission status based on customer settlements and insurer payments.
    
    Status Logic (based on payment brokerage receives from insurer):
    - "pending": No commission received yet (no customer settlements OR insurer hasn't paid)
    - "partially_received": Insurer has paid partially (less than recognized commission)
    - "received_in_full": Insurer has paid the full commission (revenue_realized >= revenue_recognized)
    
    Args:
        customer_settlements (Decimal/float/str): Amount settled by customer (paid_amount from invoice)
        revenue_realized (Decimal/float/str): Amount paid by insurer to broker
        revenue_recognized (Decimal/float/str): Total commission amount recognized
        
    Returns:
        str: Status key (e.g., "pending", "partially_received", "received_in_full")
    """
    from decimal import Decimal
    
    customer_settlements = Decimal(str(customer_settlements or 0))
    revenue_realized = Decimal(str(revenue_realized or 0))
    revenue_recognized = Decimal(str(revenue_recognized or 0))
    
    # Handle negative values (shouldn't happen, but be safe)
    if customer_settlements < 0:
        customer_settlements = Decimal("0")
    if revenue_realized < 0:
        revenue_realized = Decimal("0")
    if revenue_recognized < 0:
        revenue_recognized = Decimal("0")
    
    # No customer settlements = no commission expected from insurer
    if customer_settlements == 0:
        return "pending"
    
    # Check insurer payment status against recognized commission
    if revenue_realized == 0:
        # Customer settled but insurer hasn't paid yet
        return "pending"
    elif revenue_realized > 0 and revenue_realized < revenue_recognized:
        # Insurer paid partially (less than recognized commission)
        return "partially_received"
    elif revenue_realized >= revenue_recognized:
        # Insurer paid in full (at least the recognized commission amount)
        return "received_in_full"
    else:
        # Fallback
        return "pending"


def calculate_agent_commission_status(revenue_recognized, revenue_realized):
    """
    Calculate agent commission status based on payment made to agent by broker.
    
    Status Logic (based on payment made to agent by broker):
    - "pending": No settlements to agent (regardless of broker commission status)
    - "partially_paid": Partial settlements to agent
    - "fully_paid": Full settlement to agent
    
    Args:
        revenue_recognized (Decimal/float/str): Total commission amount recognized
        revenue_realized (Decimal/float/str): Amount paid to agent by broker
        
    Returns:
        str: Status key (e.g., "pending", "partially_paid", "fully_paid")
    """
    from decimal import Decimal
    
    revenue_recognized = Decimal(str(revenue_recognized or 0))
    revenue_realized = Decimal(str(revenue_realized or 0))
    
    # Handle negative values
    if revenue_realized < 0:
        revenue_realized = Decimal("0")
    
    if revenue_realized == 0:
        return "pending"
    elif revenue_realized > 0 and revenue_realized < revenue_recognized:
        return "partially_paid"
    elif revenue_realized >= revenue_recognized:
        return "fully_paid"
    else:
        return "pending"  # Fallback


def update_brokerage_commission_status(commission_id):
    """
    Recalculate and update brokerage commission status.
    Call this whenever invoice paid_amount or revenue_realized changes.
    
    Args:
        commission_id (int): ID of the brokerage commission
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        commission = QueryBuilderService("crmf_brokerage_commission").where("id", commission_id).first()
        if not commission:
            return False
        
        # Get customer settlements from invoice paid_amount
        invoice = QueryBuilderService("crmf_invoices").where("id", commission.get("invoice_id")).first()
        customer_settlements = invoice.get("paid_amount", 0) if invoice else 0
        
        status = calculate_brokerage_commission_status(
            customer_settlements,
            commission.get("revenue_realized", 0),
            commission.get("revenue_recognized", 0)
        )
        
        result = QueryBuilderService("crmf_brokerage_commission").where("id", commission_id).update({"status": status})
        return bool(result)
    except Exception as e:
        print(f"Error updating brokerage commission status: {str(e)}")
        return False


def update_agent_commission_status(commission_id):
    """
    Recalculate and update agent commission status.
    Call this whenever revenue_realized changes.
    
    Args:
        commission_id (int): ID of the agent commission
        
    Returns:
        bool: True if update was successful, False otherwise
    """
    try:
        commission = QueryBuilderService("crmf_agent_commission").where("id", commission_id).first()
        if not commission:
            return False
        
        status = calculate_agent_commission_status(
            commission.get("revenue_recognized", 0),
            commission.get("revenue_realized", 0)
        )
        
        result = QueryBuilderService("crmf_agent_commission").where("id", commission_id).update({"status": status})
        return bool(result)
    except Exception as e:
        print(f"Error updating agent commission status: {str(e)}")
        return False


def format_commission_status_with_metadata(status_key, commission_type="brokerage"):
    """
    Format status with metadata (status, status_type, status_id, status_color).
    Fetches all data directly from core_status table.
    Returns the status name from database in the 'status' field.
    
    Args:
        status_key (str): Status key (e.g., "pending", "partially_received")
        commission_type (str): "brokerage" or "agent"
        
    Returns:
        dict: Status with simplified metadata
    """
    # Map status_key to type (for database lookup)
    if commission_type == "brokerage":
        status_type_map = {
            "pending": "brkg_comm_pending",
            "partially_received": "brkg_comm_part_recv",
            "received_in_full": "brkg_comm_recv_full",
        }
    else:
        status_type_map = {
            "pending": "agent_comm_pending",
            "partially_paid": "agent_comm_part_paid",
            "fully_paid": "agent_comm_full_paid",
        }
    
    status_type = status_type_map.get(status_key)
    
    # Fetch status from database
    status_id = None
    status_type_value = None
    status_name = status_key.title()  # Default to capitalized status_key if not found
    status_color = "#6c757d"  # Default color
    
    try:
        if status_type:
            status_record = QueryBuilderService("core_status")\
                .where("type", status_type)\
                .where("module", "finance")\
                .first()
            
            if status_record:
                status_id = status_record.get("id")
                status_type_value = status_record.get("type", status_type)
                status_name = status_record.get("name")  # Get name from database
                status_color = status_record.get("color", "#6c757d")
            else:
                # Status not found - try to find by name as fallback (might exist with different type)
                # For brokerage: "pending" -> "PENDING", "partially_received" -> "PARTIALLY RECEIVED", etc.
                status_name_map = {
                    "pending": "PENDING",
                    "partially_received": "PARTIALLY RECEIVED",
                    "received_in_full": "RECEIVED IN FULL",
                    "partially_paid": "PARTIALLY PAID",
                    "fully_paid": "FULLY PAID",
                }
                fallback_name = status_name_map.get(status_key, status_key.upper().replace("_", " "))
                
                # Try to find by name+module
                status_record = QueryBuilderService("core_status")\
                    .where("name", fallback_name)\
                    .where("module", "finance")\
                    .first()
                
                if status_record:
                    # Found by name, use it but update type if needed
                    status_id = status_record.get("id")
                    status_type_value = status_record.get("type")
                    status_name = status_record.get("name")
                    status_color = status_record.get("color", "#6c757d")
                    
                    # If type doesn't match, try to update it (but don't fail if it doesn't work)
                    if status_type_value != status_type:
                        try:
                            ensure_commission_statuses_exist()
                            # Try querying again by type
                            status_record = QueryBuilderService("core_status")\
                                .where("type", status_type)\
                                .where("module", "finance")\
                                .first()
                            if status_record:
                                status_id = status_record.get("id")
                                status_type_value = status_record.get("type", status_type)
                                status_name = status_record.get("name")
                                status_color = status_record.get("color", "#6c757d")
                        except Exception as e:
                            # If update fails, just use what we found by name
                            pass
    except Exception as e:
        print(f"Error fetching status from database: {str(e)}")
    
    return {
        "status": status_name,  # Return name from database instead of status_key
        "status_type": status_type_value or status_type,
        "status_id": status_id,
        "status_color": status_color
    }

