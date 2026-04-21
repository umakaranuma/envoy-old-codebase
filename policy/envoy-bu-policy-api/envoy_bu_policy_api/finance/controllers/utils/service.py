from mServices import QueryBuilderService


def get_commission_setup_service(product_id, insurer_id, transaction_type, product_group_id=None):
    
    # Columns to select from commission setups and related tables
    all_columns = [
        "crmf_commission_setups.id",
        "crmf_commission_setups.product_id",
        "crmf_commission_setups.insurer_id",
        "crmf_commission_setups.transaction_type",
        "crmf_commission_setups.brokerage_revenue_percent",
        "crmf_commission_setups.agent_commission_percent",
        "core_service_providers.name as insurer_name",
        "core_vendor_products.name as product_name"
    ]

    # Try product-level commission setup first (by product_id)
    commission = (
        QueryBuilderService("crmf_commission_setups")
        .select(*all_columns)
        .leftJoin(
            "crmf_commission_field_values",
            "crmf_commission_field_values.commission_setup_id",
            "crmf_commission_setups.id"
        )
        .leftJoin(
            "core_users",
            "crmf_commission_field_values.user_id",
            "core_users.id"
        )
        .leftJoin(
            "crmf_commission_setup_teams",
            "crmf_commission_setups.id",
            "crmf_commission_setup_teams.commission_setup_id"
        )
        .leftJoin(
            "core_teams",
            "crmf_commission_setup_teams.team_id",
            "core_teams.id"
        )
        .leftJoin(
            "core_service_providers",
            "crmf_commission_setups.insurer_id",
            "core_service_providers.id"
        )
        .leftJoin(
            "core_vendor_products",
            "crmf_commission_setups.product_id",
            "core_vendor_products.id"
        )
        .whereNull("crmf_commission_setups.deleted_at")
            .where("product_id", product_id)
        .where("transaction_type", transaction_type)
        .first()
    )

    # Native product fallback removed per requirement: only match on policy_base.product_id or product_group_id

    # If no product-level setup, try product-group-level setup fallback
    if not commission and product_group_id:
        commission = (
            QueryBuilderService("crmf_commission_setups")
            .select(*all_columns)
            .leftJoin(
                "crmf_commission_field_values",
                "crmf_commission_field_values.commission_setup_id",
                "crmf_commission_setups.id"
            )
            .leftJoin(
                "core_users",
                "crmf_commission_field_values.user_id",
                "core_users.id"
            )
            .leftJoin(
                "crmf_commission_setup_teams",
                "crmf_commission_setups.id",
                "crmf_commission_setup_teams.commission_setup_id"
            )
            .leftJoin(
                "core_teams",
                "crmf_commission_setup_teams.team_id",
                "core_teams.id"
            )
            .leftJoin(
                "core_service_providers",
                "crmf_commission_setups.insurer_id",
                "core_service_providers.id"
            )
            .leftJoin(
                "core_vendor_products",
                "crmf_commission_setups.product_id",
                "core_vendor_products.id"
            )
            .whereNull("crmf_commission_setups.deleted_at")
            .where("crmf_commission_setups.product_group_id", product_group_id)
            .where("transaction_type", transaction_type)
            .first()
        )

    if not commission:
        return ("NOT_FOUND",)

    # Get commission field values in a single optimized query
    commission_values = (
        QueryBuilderService("crmf_commission_field_values")
        .select(
            "crmf_commission_field_values.value",
            "crmf_commission_field_values.type",
            "crmf_commission_field_values.user_id",
            "crmf_commission_fields.attribute_name as field_attribute",
            "core_users.display_name as user_name",
            "core_users.email as user_email"
        )
        .leftJoin(
            "crmf_commission_fields",
            "crmf_commission_fields.id",
            "crmf_commission_field_values.commission_field_id"
        )
        .leftJoin("core_users", "core_users.id", "crmf_commission_field_values.user_id")
        .where("commission_setup_id", commission.get("id"))
        .get()
    )

    # Get team users if any (simplified to avoid column issues)
    team_users = []

    commission["commission_values"] = {}
    for value in commission_values:
        field_attr = value.get("field_attribute")
        if not field_attr:
            continue
        if field_attr not in commission["commission_values"]:
            commission["commission_values"][field_attr] = []
        commission["commission_values"][field_attr].append({
            "value": value.get("value"),
            "type": value.get("type"),
            "user_id": value.get("user_id"),
            "user_name": value.get("user_name"),
            "user_email": value.get("user_email")
        })
    

    # Expand to team users if no user-specific agent commissions defined
    if "agent_commission_percent" in commission["commission_values"]:
        agent_commissions = commission["commission_values"]["agent_commission_percent"]
        if not any(comm.get("user_id") for comm in agent_commissions) and team_users:
            base_commission = agent_commissions[0] if agent_commissions else {"value": "0", "type": "flat"}
            commission["commission_values"]["agent_commission_percent"] = [
                {
                    "value": base_commission["value"],
                    "type": base_commission["type"],
                    "user_id": user["user_id"],
                    "user_name": user["user_name"],
                    "user_email": user["user_email"]
                }
                for user in team_users
            ]

    return commission

def status_update_service(status_name, base_table=None, base_id=None, status_color=None):
    """
    Common service to update status for various entities.
    
    Args:
        status_name (str): Name of the status (e.g., 'Pending', 'Paid', 'Overdue')
        base_table (str): Table name to update (e.g., 'invoices', 'policies')
        base_id (int): ID of the record to update
        status_color (str): Color for the status (optional, will use default if not provided)
        
    Returns:
        dict: Status data if successful, None if failed
    """
    # Default colors for common invoice statuses
    default_colors = {
        'Pending': '#FFA500',        # Orange
        'Partially Paid': '#FFD700', # Gold
        'Paid': '#32CD32',           # Lime Green
        'Overdue': '#FF0000',        # Red
        'Cancelled': '#808080',      # Gray
        'Refunded': '#87CEEB'        # Sky Blue
    }
    
    # Use provided color or default color
    if not status_color:
        status_color = default_colors.get(status_name, '#eeeeef')
    
    # Check if status already exists
    status_data = (
        QueryBuilderService("core_statuses")
        .where("name", status_name)
        .first()
    )
    
    if not status_data:
        # Create new status if it doesn't exist
        status_data = (
            QueryBuilderService("core_statuses")
            .insert({
                "name": status_name,
                "type": "finance",  # Changed from "policy" to "finance" for invoice statuses
                "module": "Finance", # Changed from "Policy" to "Finance"
                "color": status_color,
                "sort_index": 0
            })
        )
    
    # Update the specified table with the status
    if base_table and base_id and status_data:
        try:
            if base_table == "invoices":
                QueryBuilderService("crmf_invoices").where("id", base_id).update({
                    "status_id": status_data["id"]
                })
            elif base_table == "policies":
                QueryBuilderService("crmp_issued_policies").where("id", base_id).update({
                    "status_id": status_data["id"]
                })
            # Add more table types as needed
            else:
                print(f"Warning: Table '{base_table}' not supported for status updates")
        except Exception as e:
            print(f"Error updating status for {base_table} ID {base_id}: {str(e)}")
            return None
    
    return status_data

def set_invoice_status(invoice_id, status_name, custom_color=None):
    """
    Helper function to set invoice status using predefined status names.
    
    Args:
        invoice_id (int): ID of the invoice to update
        status_name (str): One of the predefined status names
        custom_color (str): Optional custom color override
        
    Returns:
        dict: Status data if successful, None if failed
    """
    return status_update_service(
        status_name=status_name,
        base_table="invoices",
        base_id=invoice_id,
        status_color=custom_color
    )

def initialize_invoice_statuses():
    """
    Initialize all required invoice statuses in the database.
    This function should be called during system setup or migration.
    
    Returns:
        dict: Dictionary of created/retrieved statuses
    """
    statuses = {}
    
    # Define all required invoice statuses with their colors
    invoice_statuses = {
        'Pending': '#FFA500',        # Orange - not paid any amount
        'Partially Paid': '#FFD700', # Gold - portion paid
        'Paid': '#32CD32',           # Lime Green - full payment received
        'Overdue': '#FF0000',        # Red - payment deadline passed
        'Cancelled': '#808080',      # Gray - policy cancelled
        'Refunded': '#87CEEB'        # Sky Blue - refund endorsement done
    }
    
    for status_name, color in invoice_statuses.items():
        status_data = status_update_service(
            status_name=status_name,
            status_color=color
        )
        if status_data:
            statuses[status_name] = status_data
    
    return statuses
