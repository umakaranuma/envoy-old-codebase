from mServices import QueryBuilderService
from core_models.core_models import Status
from envoy_bu_policy_api.policy.models.crmp_policy_base import PolicyBase
import json


def ensure_policy_statuses_exist():
    """
    Ensure all required policy statuses exist in the core_status table.
    Creates them if they don't exist.
    """
    required_statuses = [
        {
            "name": "DRAFT",
            "description": "policyStatus",
            "type": "policy_draft",
            "module": "policy",
            "color": "#6c757d",
            "sort_index": 0
        },
        {
            "name": "PENDING ISSUANCE",
            "description": "policyStatus",
            "type": "pol_pending_iss",
            "module": "policy",
            "color": "#B54708",
            "sort_index": 1
        },
        {
            "name": "ACTIVE",
            "description": "policyStatus",
            "type": "policy_active",
            "module": "policy",
            "color": "#067647",
            "sort_index": 2
        },
        {
            "name": "DUE FOR RENEWAL",
            "description": "policyStatus",
            "type": "pol_due_renewal",
            "module": "policy",
            "color": "#175CD3",
            "sort_index": 3
        },
        {
            "name": "EXPIRED",
            "description": "policyStatus",
            "type": "policy_expired",
            "module": "policy",
            "color": "#344054",
            "sort_index": 4
        },
        {
            "name": "RENEWAL IN PROGRESS",
            "description": "policyStatus",
            "type": "pol_renewal_progress",
            "module": "policy",
            "color": "#0E7090",
            "sort_index": 5
        },
        {
            "name": "CANCELLED",
            "description": "policyStatus",
            "type": "policy_cancelled",
            "module": "policy",
            "color": "#B42318",
            "sort_index": 6
        },
        {
            "name": "RENEWED",
            "description": "policyStatus",
            "type": "policy_renewed",
            "module": "policy",
            "color": "#175CD3",
            "sort_index": 7
        }
    ]
    
    for status_data in required_statuses:
        # Check if status with this immutable type already exists
        existing_status = QueryBuilderService("core_status")\
            .where("type", status_data["type"])\
            .where("module", status_data["module"])\
            .first()
        
        if existing_status:
            print(f"Policy status already exists: {status_data['name']}")
        else:
            # Status doesn't exist, create it
            QueryBuilderService("core_status").insert(status_data)
            print(f"Created policy status: {status_data['name']}")


def get_policy_status_id(status_name):
    """
    Get the status ID for a given policy status name.
    Uses type+module for immutable lookup, with name+module as fallback.
    If status doesn't exist, creates it automatically and returns the ID.
    
    Args:
        status_name (str): Name of the policy status (e.g., "PENDING_ISSUANCE", "ACTIVE")
        
    Returns:
        int: Status ID if found or created, None if creation failed
    """
    # Get status config to determine the type value
    status_config = get_status_config_by_name(status_name)
    status_type = status_config.get("type")
    module = status_config.get("module", "policy")
    
    # First try to find existing status by type+module (immutable lookup)
    status = QueryBuilderService("core_status")\
        .where("type", status_type)\
        .where("module", module)\
        .first()
    
    if status:
        return status["id"]
    
    # Fallback: try to find by name+module (for backward compatibility)
    status_name_actual = status_config.get("name", status_name)
    status = QueryBuilderService("core_status")\
        .where("name", status_name_actual)\
        .where("module", module)\
        .first()
    
    if status:
        # Found by name, but should have type - return it
        return status["id"]
    
    # Status doesn't exist, create it automatically
    print(f"Status '{status_name}' not found, creating it automatically...")
    
    try:
        # Create the new status with the config
        new_status = QueryBuilderService("core_status").insert(status_config)
        print(f"Created new status '{status_name}' with ID: {new_status['id']}")
        return new_status["id"]
        
    except Exception as e:
        print(f"Error creating status '{status_name}': {str(e)}")
        return None


def get_status_config_by_name(status_name):
    """
    Get status configuration based on status name.
    Provides default values for unknown statuses.
    
    Args:
        status_name (str): Name of the status
        
    Returns:
        dict: Status configuration
    """
    # Default status configuration
    default_config = {
        "name": status_name,
        "description": f"Policy status: {status_name}",
        "type": "policy_active",
        "module": "policy",
        "color": "#6c757d",
        "sort_index": 99
    }
    
    # Known status configurations
    known_statuses = {
        "DRAFT": {
            "name": "DRAFT",
            "description": "policyStatus",
            "type": "policy_draft",
            "module": "policy",
            "color": "#6c757d",
            "sort_index": 0
        },
        "PENDING_ISSUANCE": {
            "name": "PENDING ISSUANCE",
            "description": "policyStatus",
            "type": "pol_pending_iss",
            "module": "policy",
            "color": "#B54708",
            "sort_index": 1
        },
        "ACTIVE": {
            "name": "ACTIVE",
            "description": "policyStatus",
            "type": "policy_active",
            "module": "policy",
            "color": "#067647",
            "sort_index": 2
        },
        "DUE_FOR_RENEWAL": {
            "name": "DUE FOR RENEWAL",
            "description": "policyStatus",
            "type": "pol_due_renewal",
            "module": "policy",
            "color": "#175CD3",
            "sort_index": 3
        },
        "EXPIRED": {
            "name": "EXPIRED",
            "description": "policyStatus",
            "type": "policy_expired",
            "module": "policy",
            "color": "#344054",
            "sort_index": 4
        },
        "RENEWAL_IN_PROGRESS": {
            "name": "RENEWAL IN PROGRESS",
            "description": "policyStatus",
            "type": "pol_renewal_progress",
            "module": "policy",
            "color": "#0E7090",
            "sort_index": 5
        },
        "CANCELLED": {
            "name": "CANCELLED",
            "description": "policyStatus",
            "type": "policy_cancelled",
            "module": "policy",
            "color": "#B42318",
            "sort_index": 6
        },
        "RENEWED": {
            "name": "RENEWED",
            "description": "policyStatus",
            "type": "policy_renewed",
            "module": "policy",
            "color": "#175CD3",
            "sort_index": 7
        }
    }
    
    # Handle both formats: with spaces (database format) and with underscores (code format)
    # First try the exact match
    if status_name in known_statuses:
        return known_statuses.get(status_name)
    
    # If not found, try converting spaces to underscores for lookup
    # This allows "PENDING ISSUANCE" to match "PENDING_ISSUANCE" key
    status_name_with_underscores = status_name.replace(" ", "_")
    if status_name_with_underscores in known_statuses:
        return known_statuses.get(status_name_with_underscores)
    
    # If still not found, try converting underscores to spaces for lookup
    # This allows "PENDING_ISSUANCE" to match "PENDING ISSUANCE" key (if it existed)
    status_name_with_spaces = status_name.replace("_", " ")
    if status_name_with_spaces in known_statuses:
        return known_statuses.get(status_name_with_spaces)
    
    # Return default config if not found
    return default_config


def get_or_create_policy_status(status_name):
    """
    Get a policy status ID, creating it if it doesn't exist.
    This is a safer way to ensure statuses exist before using them.
    
    Args:
        status_name (str): Name of the status to get or create
        
    Returns:
        int: Status ID
    """
    # Use the updated get_policy_status_id which now auto-creates
    status_id = get_policy_status_id(status_name)
    
    if status_id:
        return status_id
    
    # If still not found, something went wrong
    print(f"Warning: Could not find or create policy status '{status_name}'")
    return None


# NOTE: Previously, updating policy base status was disabled because `crmp_policy_base` had no `status_id`.
#       The model now contains a `status` FK (column `status_id`). Safe helpers for policy base are provided below.


# def get_policy_status_info(policy_base_id):
#     """
#     Get current status information for a policy base.
    
#     Args:
#         policy_base_id (int): ID of the policy base
        
#     Returns:
#         dict: Status information or None if not found
#     """
#     try:
#         # Get policy base with status information
#         policy_data = QueryBuilderService("crmp_policy_base")\
#             .select(
#                 "crmp_policy_base.id",
#                 "crmp_policy_base.status_id",
#                 "core_status.name as status_name",
#                 "core_status.description as status_description",
#                 "core_status.color as status_color",
#                 "core_status.sort_index as status_sort_index"
#             )\
#             .leftJoin("core_status", "core_status.id", "crmp_policy_base.status_id")\
#             .where("crmp_policy_base.id", policy_base_id)\
#             .first()
        
#         if not policy_data:
#             return None
        
#         return {
#             "policy_base_id": policy_base_id,
#             "status_id": policy_data.get("status_id"),
#             "status_name": policy_data.get("status_name"),
#             "status_description": policy_data.get("status_description"),
#             "status_color": policy_data.get("status_color"),
#             "status_sort_index": policy_data.get("status_sort_index")
#         }
        
#     except Exception as e:
#         print(f"Error getting policy status info: {str(e)}")
#         return None


def check_existing_policy_statuses():
    """
    Check what policy statuses already exist in the core_status table.
    Useful for debugging and understanding the current status structure.
    """
    print("=== Current Policy Statuses in core_status Table ===")
    
    # Get all policy statuses
    policy_statuses = QueryBuilderService("core_status")\
        .select("id", "name", "description", "type", "module", "color", "sort_index")\
        .where("module", "policy")\
        .orderBy("sort_index", "asc")\
        .get()
    
    if not policy_statuses:
        print("No policy statuses found in core_status table")
        return
    
    # Display policy statuses
    print(f"\n📁 Policy Statuses:")
    print("-" * 80)
    print(f"{'ID':<3} | {'Name':<20} | {'Description':<40} | {'Color':<7} | {'Sort'}")
    print("-" * 80)
    
    for status in policy_statuses:
        description = status.get("description", "")[:40] + "..." if len(status.get("description", "")) > 40 else status.get("description", "")
        print(f"{status['id']:<3} | {status['name']:<20} | {description:<40} | {status['color']:<7} | {status['sort_index']}")
    
    print(f"\nTotal Policy Statuses: {len(policy_statuses)}")
    print("=" * 80)


def bulk_update_request_policy_statuses(request_policy_ids, status_name):
    """
    Update status for multiple request policies at once.
    
    Args:
        request_policy_ids (list): List of request policy IDs to update
        status_name (str): Name of the status to set
        
    Returns:
        dict: Result with success count and details
    """
    try:
        # Ensure statuses exist
        ensure_policy_statuses_exist()
        
        # Get status ID
        status_id = get_or_create_policy_status(status_name)
        if not status_id:
            return {
                "success": False,
                "message": f"Status '{status_name}' not found or could not be created",
                "updated_count": 0,
                "failed_ids": request_policy_ids
            }
        
        # Update multiple request policies
        update_result = QueryBuilderService("crmp_request_policies")\
            .whereIn("id", request_policy_ids)\
            .update({"status_id": status_id})
        
        print(f"Bulk updated {update_result} request policies to status '{status_name}'")
        
        return {
            "success": True,
            "message": f"Successfully updated {update_result} request policies to '{status_name}'",
            "updated_count": update_result,
            "status_id": status_id,
            "request_policy_ids": request_policy_ids
        }
        
    except Exception as e:
        print(f"Error in bulk update: {str(e)}")
        return {
            "success": False,
            "message": f"Error in bulk update: {str(e)}",
            "updated_count": 0,
            "failed_ids": request_policy_ids
        }


#-------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------
# REQUEST POLICY STATUS MANAGEMENT (Only for crmp_request_policies table)
#-------------------------------------------------------------------------------------------------------------------------

def get_request_policy_status_id(status_name):
    """
    Get the status ID for request policy status (same as policy status).
    
    Args:
        status_name (str): Name of the policy status
        
    Returns:
        int: Status ID if found, None otherwise
    """
    return get_or_create_policy_status(status_name)


def get_request_policy_id_by_policy_base_id(policy_base_id):
    """
    Get the request policy ID from policy base ID.
    
    Args:
        policy_base_id (int): ID of the policy base
        
    Returns:
        int: Request policy ID if found, None otherwise
    """
    try:
        request_policy = QueryBuilderService("crmp_request_policies")\
            .where("policy_base_id", policy_base_id)\
            .first()
        
        return request_policy["id"] if request_policy else None
        
    except Exception as e:
        print(f"Error getting request policy ID from policy base ID {policy_base_id}: {str(e)}")
        return None


def update_request_policy_status(request_policy_id, status_name):
    """
    Update the status of a request policy.
    
    Args:
        request_policy_id (int): ID of the request policy to update
        status_name (str): Name of the status to set (e.g., "PENDING_ISSUANCE", "CANCELLED")
        
    Returns:
        dict: Result with success status and message
    """
    try:
        # Ensure statuses exist
        ensure_policy_statuses_exist()
        
        # Get status ID
        status_id = get_or_create_policy_status(status_name)
        if not status_id:
            return {
                "success": False,
                "message": f"Status '{status_name}' not found or could not be created",
                "status_id": None
            }
        
        # CRITICAL: Verify the status ID exists in core_status table
        existing_status = QueryBuilderService("core_status")\
            .where("id", status_id)\
            .where("module", "policy")\
            .first()
        
        if not existing_status:
            return {
                "success": False,
                "message": f"Status ID {status_id} does not exist in core_status table",
                "status_id": None
            }
        
        # Check if request policy exists
        request_policy = QueryBuilderService("crmp_request_policies")\
            .where("id", request_policy_id)\
            .first()
        
        if not request_policy:
            return {
                "success": False,
                "message": f"Request policy with ID {request_policy_id} not found",
                "status_id": None
            }
        
        # Update the request policy status
        update_result = QueryBuilderService("crmp_request_policies")\
            .where("id", request_policy_id)\
            .update({"status_id": status_id})
        
        if update_result > 0:
            print(f"Updated request policy {request_policy_id} status to '{status_name}' (ID: {status_id})")
            return {
                "success": True,
                "message": f"Request policy status updated to '{status_name}' successfully",
                "status_id": status_id,
                "request_policy_id": request_policy_id
            }
        else:
            return {
                "success": False,
                "message": f"No rows updated for request policy {request_policy_id}",
                "status_id": None
            }
            
    except Exception as e:
        print(f"Error updating request policy status: {str(e)}")
        return {
            "success": False,
            "message": f"Error updating request policy status: {str(e)}",
            "status_id": None
        }


def get_request_policy_status_info(request_policy_id):
    """
    Get current status information for a request policy.
    
    Args:
        request_policy_id (int): ID of the request policy
        
    Returns:
        dict: Status information or None if not found
    """
    try:
        # Get request policy with status information
        request_policy_data = QueryBuilderService("crmp_request_policies")\
            .select(
                "crmp_request_policies.id",
                "crmp_request_policies.status_id",
                "crmp_request_policies.policy_request_id",
                "crmp_request_policies.policy_request_date",
                "core_status.name as status_name",
                "core_status.description as status_description",
                "core_status.color as status_color",
                "core_status.sort_index as status_sort_index"
            )\
            .leftJoin("core_status", "core_status.id", "crmp_request_policies.status_id")\
            .where("crmp_request_policies.id", request_policy_id)\
            .first()
        
        if not request_policy_data:
            return None
        
        return {
            "request_policy_id": request_policy_id,
            "policy_request_id": request_policy_data.get("policy_request_id"),
            "policy_request_date": request_policy_data.get("policy_request_date"),
            "status_id": request_policy_data.get("status_id"),
            "status_name": request_policy_data.get("status_name"),
            "status_description": request_policy_data.get("status_description"),
            "status_color": request_policy_data.get("status_color"),
            "status_sort_index": request_policy_data.get("status_sort_index")
        }
        
    except Exception as e:
        print(f"Error getting request policy status info: {str(e)}")
        return None


#-------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------
# CONVENIENCE FUNCTIONS FOR REQUEST POLICY STATUS UPDATES
#-------------------------------------------------------------------------------------------------------------------------

def set_request_policy_pending_issuance(request_policy_id):
    """Set request policy status to PENDING ISSUANCE"""
    return update_request_policy_status(request_policy_id, "PENDING ISSUANCE")


def set_request_policy_renewal_in_progress(request_policy_id):
    """Set request policy status to RENEWAL IN PROGRESS"""
    return update_request_policy_status(request_policy_id, "RENEWAL IN PROGRESS")


def set_request_policy_cancelled(request_policy_id):
    """Set request policy status to CANCELLED"""
    return update_request_policy_status(request_policy_id, "CANCELLED")


def update_request_policy_status_by_policy_base_id(policy_base_id, status_name):
    """
    Update request policy status using policy base ID.
    
    Args:
        policy_base_id (int): ID of the policy base
        status_name (str): Name of the status to set
        
    Returns:
        dict: Result with success status and message
    """
    try:
        # Get request policy ID from policy base ID
        request_policy_id = get_request_policy_id_by_policy_base_id(policy_base_id)
        
        if not request_policy_id:
            return {
                "success": False,
                "message": f"No request policy found for policy base ID {policy_base_id}",
                "status_id": None
            }
        
        # Update the request policy status
        return update_request_policy_status(request_policy_id, status_name)
        
    except Exception as e:
        print(f"Error updating request policy status by policy base ID: {str(e)}")
        return {
            "success": False,
            "message": f"Error updating request policy status by policy base ID: {str(e)}",
            "status_id": None
        }


def validate_request_policy_status_ids():
    """
    Validate that all request policies have valid status IDs that exist in core_status table.
    
    Returns:
        dict: Validation results with invalid records
    """
    try:
        # Find request policies with invalid status IDs
        invalid_policies = QueryBuilderService("crmp_request_policies")\
            .select(
                "crmp_request_policies.id as request_policy_id",
                "crmp_request_policies.policy_request_id",
                "crmp_request_policies.status_id as invalid_status_id"
            )\
            .leftJoin("core_status", "core_status.id", "crmp_request_policies.status_id")\
            .where("core_status.id", "IS", None)\
            .get()
        
        # Find request policies with status IDs that don't belong to policy_status module
        wrong_module_policies = QueryBuilderService("crmp_request_policies")\
            .select(
                "crmp_request_policies.id as request_policy_id",
                "crmp_request_policies.policy_request_id",
                "crmp_request_policies.status_id",
                "core_status.name as status_name",
                "core_status.module as status_module"
            )\
            .leftJoin("core_status", "core_status.id", "crmp_request_policies.status_id")\
            .where("core_status.module", "!=", "policy")\
            .where("core_status.id", "IS NOT", None)\
            .get()
        
        total_invalid = len(invalid_policies) + len(wrong_module_policies)
        
        return {
            "success": True,
            "total_request_policies": QueryBuilderService("crmp_request_policies").count(),
            "invalid_status_ids": len(invalid_policies),
            "wrong_module_statuses": len(wrong_module_policies),
            "total_invalid": total_invalid,
            "invalid_policies": invalid_policies,
            "wrong_module_policies": wrong_module_policies,
            "is_valid": total_invalid == 0
        }
        
    except Exception as e:
        print(f"Error validating request policy status IDs: {str(e)}")
        return {
            "success": False,
            "message": f"Error validating request policy status IDs: {str(e)}",
            "total_invalid": -1,
            "is_valid": False
        }


def fix_invalid_request_policy_status_ids():
    """
    Fix request policies that have invalid status IDs by setting them to PENDING_ISSUANCE.
    
    Returns:
        dict: Results of the fix operation
    """
    try:
        # Ensure statuses exist
        ensure_policy_statuses_exist()
        
        # Get PENDING_ISSUANCE status ID
        pending_status_id = get_or_create_policy_status("PENDING_ISSUANCE")
        if not pending_status_id:
            return {
                "success": False,
                "message": "Could not get PENDING_ISSUANCE status ID",
                "fixed_count": 0
            }
        
        # Fix policies with invalid status IDs
        invalid_fix_result = QueryBuilderService("crmp_request_policies")\
            .leftJoin("core_status", "core_status.id", "crmp_request_policies.status_id")\
            .where("core_status.id", "IS", None)\
            .update({"status_id": pending_status_id})
        
        # Fix policies with wrong module status IDs
        wrong_module_fix_result = QueryBuilderService("crmp_request_policies")\
            .leftJoin("core_status", "core_status.id", "crmp_request_policies.status_id")\
            .where("core_status.module", "!=", "policy")\
            .where("core_status.id", "IS NOT", None)\
            .update({"status_id": pending_status_id})
        
        total_fixed = invalid_fix_result + wrong_module_fix_result
        
        print(f"Fixed {total_fixed} request policies with invalid status IDs")
        
        return {
            "success": True,
            "message": f"Fixed {total_fixed} request policies with invalid status IDs",
            "fixed_count": total_fixed,
            "invalid_fixed": invalid_fix_result,
            "wrong_module_fixed": wrong_module_fix_result
        }
        
    except Exception as e:
        print(f"Error fixing invalid request policy status IDs: {str(e)}")
        return {
            "success": False,
            "message": f"Error fixing invalid request policy status IDs: {str(e)}",
            "fixed_count": 0
        }


#-------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------
# POLICY BASE STATUS MANAGEMENT (For crmp_policy_base table)
#-------------------------------------------------------------------------------------------------------------------------

def update_policy_base_status(policy_base_id, status_name):
    """
    Update the status of a policy base (crmp_policy_base.status_id).

    Args:
        policy_base_id (int): ID of the policy base record
        status_name (str): Target status name (e.g., "ACTIVE", "CANCELLED")

    Returns:
        dict: Result with success status and message
    """
    try:
        ensure_policy_statuses_exist()

        status_id = get_or_create_policy_status(status_name)
        if not status_id:
            return {
                "success": False,
                "message": f"Status '{status_name}' not found or could not be created",
                "status_id": None
            }

        existing_status = QueryBuilderService("core_status")\
            .where("id", status_id)\
            .where("module", "policy")\
            .first()

        if not existing_status:
            return {
                "success": False,
                "message": f"Status ID {status_id} does not exist in core_status table",
                "status_id": None
            }

        policy_base = QueryBuilderService("crmp_policy_base")\
            .where("id", policy_base_id)\
            .first()

        if not policy_base:
            return {
                "success": False,
                "message": f"Policy base with ID {policy_base_id} not found",
                "status_id": None
            }

        update_result = QueryBuilderService("crmp_policy_base")\
            .where("id", policy_base_id)\
            .update({"status_id": status_id})

        if update_result:
            print(f"Updated policy base {policy_base_id} status to '{status_name}' (ID: {status_id})")
            return {
                "success": True,
                "message": f"Policy base status updated to '{status_name}' successfully",
                "status_id": status_id,
                "policy_base_id": policy_base_id
            }
        else:
            return {
                "success": False,
                "message": f"No rows updated for policy base {policy_base_id}",
                "status_id": None
            }

    except Exception as e:
        print(f"Error updating policy base status: {str(e)}")
        return {
            "success": False,
            "message": f"Error updating policy base status: {str(e)}",
            "status_id": None
        }


def bulk_update_policy_base_statuses(policy_base_ids, status_name):
    """
    Bulk update status for multiple policy base records.

    Args:
        policy_base_ids (list[int]): List of policy base IDs
        status_name (str): Target status name

    Returns:
        dict: Result with success count and details
    """
    try:
        ensure_policy_statuses_exist()

        status_id = get_or_create_policy_status(status_name)
        if not status_id:
            return {
                "success": False,
                "message": f"Status '{status_name}' not found or could not be created",
                "updated_count": 0,
                "failed_ids": policy_base_ids
            }

        update_result = QueryBuilderService("crmp_policy_base")\
            .whereIn("id", policy_base_ids)\
            .update({"status_id": status_id})

        # For bulk updates, we need to count the number of records updated
        # Since update_result is a dictionary, we'll use the length of policy_base_ids as the count
        updated_count = len(policy_base_ids) if update_result else 0
        print(f"Bulk updated {updated_count} policy base records to status '{status_name}'")

        return {
            "success": True,
            "message": f"Successfully updated {updated_count} policy base records to '{status_name}'",
            "updated_count": updated_count,
            "status_id": status_id,
            "policy_base_ids": policy_base_ids
        }

    except Exception as e:
        print(f"Error in bulk policy base update: {str(e)}")
        return {
            "success": False,
            "message": f"Error in bulk policy base update: {str(e)}",
            "updated_count": 0,
            "failed_ids": policy_base_ids
        }


def get_policy_base_status_info(policy_base_id):
    """
    Get current status information for a policy base.

    Args:
        policy_base_id (int): ID of the policy base

    Returns:
        dict | None: Status information or None if not found
    """
    try:
        policy_base_data = QueryBuilderService("crmp_policy_base")\
            .select(
                "crmp_policy_base.id",
                "crmp_policy_base.status_id",
                "core_status.name as status_name",
                "core_status.description as status_description",
                "core_status.color as status_color",
                "core_status.sort_index as status_sort_index"
            )\
            .leftJoin("core_status", "core_status.id", "crmp_policy_base.status_id")\
            .where("crmp_policy_base.id", policy_base_id)\
            .first()

        if not policy_base_data:
            return None

        return {
            "policy_base_id": policy_base_id,
            "status_id": policy_base_data.get("status_id"),
            "status_name": policy_base_data.get("status_name"),
            "status_description": policy_base_data.get("status_description"),
            "status_color": policy_base_data.get("status_color"),
            "status_sort_index": policy_base_data.get("status_sort_index")
        }

    except Exception as e:
        print(f"Error getting policy base status info: {str(e)}")
        return None


def validate_policy_base_status_ids():
    """
    Validate that all policy base rows have valid status IDs that exist and belong to the policy_status module.

    Returns:
        dict: Validation results
    """
    try:
        invalid_rows = QueryBuilderService("crmp_policy_base")\
            .select(
                "crmp_policy_base.id as policy_base_id",
                "crmp_policy_base.status_id as invalid_status_id"
            )\
            .leftJoin("core_status", "core_status.id", "crmp_policy_base.status_id")\
            .where("core_status.id", "IS", None)\
            .get()

        wrong_module_rows = QueryBuilderService("crmp_policy_base")\
            .select(
                "crmp_policy_base.id as policy_base_id",
                "crmp_policy_base.status_id",
                "core_status.name as status_name",
                "core_status.module as status_module"
            )\
            .leftJoin("core_status", "core_status.id", "crmp_policy_base.status_id")\
            .where("core_status.module", "!=", "policy")\
            .where("core_status.id", "IS NOT", None)\
            .get()

        total_invalid = len(invalid_rows) + len(wrong_module_rows)

        return {
            "success": True,
            "total_policy_base": QueryBuilderService("crmp_policy_base").count(),
            "invalid_status_ids": len(invalid_rows),
            "wrong_module_statuses": len(wrong_module_rows),
            "total_invalid": total_invalid,
            "invalid_rows": invalid_rows,
            "wrong_module_rows": wrong_module_rows,
            "is_valid": total_invalid == 0
        }

    except Exception as e:
        print(f"Error validating policy base status IDs: {str(e)}")
        return {
            "success": False,
            "message": f"Error validating policy base status IDs: {str(e)}",
            "total_invalid": -1,
            "is_valid": False
        }


def fix_invalid_policy_base_status_ids():
    """
    Fix policy base rows with invalid status IDs by setting them to PENDING_ISSUANCE.

    Returns:
        dict: Results of the fix operation
    """
    try:
        ensure_policy_statuses_exist()

        pending_status_id = get_or_create_policy_status("PENDING_ISSUANCE")
        if not pending_status_id:
            return {
                "success": False,
                "message": "Could not get PENDING_ISSUANCE status ID",
                "fixed_count": 0
            }

        invalid_fix_result = QueryBuilderService("crmp_policy_base")\
            .leftJoin("core_status", "core_status.id", "crmp_policy_base.status_id")\
            .where("core_status.id", "IS", None)\
            .update({"status_id": pending_status_id})

        wrong_module_fix_result = QueryBuilderService("crmp_policy_base")\
            .leftJoin("core_status", "core_status.id", "crmp_policy_base.status_id")\
            .where("core_status.module", "!=", "policy")\
            .where("core_status.id", "IS NOT", None)\
            .update({"status_id": pending_status_id})

        total_fixed = invalid_fix_result + wrong_module_fix_result

        print(f"Fixed {total_fixed} policy base rows with invalid status IDs")

        return {
            "success": True,
            "message": f"Fixed {total_fixed} policy base rows with invalid status IDs",
            "fixed_count": total_fixed,
            "invalid_fixed": invalid_fix_result,
            "wrong_module_fixed": wrong_module_fix_result
        }

    except Exception as e:
        print(f"Error fixing policy base status IDs: {str(e)}")
        return {
            "success": False,
            "message": f"Error fixing policy base status IDs: {str(e)}",
            "fixed_count": 0
        }


#-------------------------------------------------------------------------------------------------------------------------
# CONVENIENCE FUNCTIONS FOR POLICY BASE STATUS UPDATES
#-------------------------------------------------------------------------------------------------------------------------

def set_policy_base_pending_issuance(policy_base_id):
    """Set policy base status to PENDING ISSUANCE"""
    return update_policy_base_status(policy_base_id, "PENDING ISSUANCE")


def set_policy_base_renewal_in_progress(policy_base_id):
    """Set policy base status to RENEWAL IN PROGRESS"""
    return update_policy_base_status(policy_base_id, "RENEWAL IN PROGRESS")


def set_policy_base_cancelled(policy_base_id):
    """Set policy base status to CANCELLED"""
    return update_policy_base_status(policy_base_id, "CANCELLED")


def set_policy_base_active(policy_base_id):
    """Set policy base status to ACTIVE"""
    return update_policy_base_status(policy_base_id, "ACTIVE")


def set_policy_base_expired(policy_base_id):
    """Set policy base status to EXPIRED"""
    return update_policy_base_status(policy_base_id, "EXPIRED")


def set_policy_base_due_for_renewal(policy_base_id):
    """Set policy base status to DUE FOR RENEWAL"""
    return update_policy_base_status(policy_base_id, "DUE FOR RENEWAL")


def set_policy_base_renewed(policy_base_id):
    """Set policy base status to RENEWED"""
    return update_policy_base_status(policy_base_id, "RENEWED")


#-------------------------------------------------------------------------------------------------------------------------
# SCENARIO-BASED HELPERS (normalized mapping for common business cases)
#-------------------------------------------------------------------------------------------------------------------------

# Base mapping for scenario to status name conversion (primary keys only)
_SCENARIO_TO_STATUS_MAPPING = {
    "draft": "DRAFT",
    "pending_issuance": "PENDING ISSUANCE",
    "pending": "PENDING ISSUANCE",  # Abbreviated form
    "active": "ACTIVE",
    "renewal_in_progress": "RENEWAL IN PROGRESS",
    "renewal": "RENEWAL IN PROGRESS",  # Abbreviated form
    "cancelled": "CANCELLED",
    "canceled": "CANCELLED",  # Alternative spelling
    "renewed": "RENEWED",
}


def _get_status_name_from_scenario(scenario):
    """
    Convert a scenario label to the corresponding status name.
    Supports multiple input formats: underscores, hyphens, and abbreviated forms.
    
    Args:
        scenario (str): Scenario label (case-insensitive)
        Supports formats like: "pending_issuance", "pending-issuance", "pending"
        
    Returns:
        str: Status name if found, None otherwise
    """
    if not scenario:
        return None
    
    # Normalize input: convert to lowercase and replace hyphens with underscores
    normalized = str(scenario).strip().lower().replace("-", "_")
    
    # First try direct lookup
    if normalized in _SCENARIO_TO_STATUS_MAPPING:
        return _SCENARIO_TO_STATUS_MAPPING[normalized]
    
    # If not found, try abbreviated forms
    # Check if it's an abbreviated form of pending_issuance
    if normalized.startswith("pending"):
        return "PENDING ISSUANCE"
    
    # Check if it's an abbreviated form of renewal_in_progress
    if normalized.startswith("renewal"):
        return "RENEWAL IN PROGRESS"
    
    # Check if it's a cancellation variant
    if normalized.startswith("cancel"):
        return "CANCELLED"
    
    return None


def set_policy_base_status_by_scenario(policy_base_id, scenario):
    """
    Set policy base status using a business scenario label.

    Supported scenarios (case-insensitive):
      - "draft": Policy is being drafted or prepared
      - "pending_issuance": Policy request sent but not yet confirmed by insurer
      - "active": Policy officially issued and in force
      - "renewal_in_progress": Renewal initiated but not completed
      - "cancelled": Policy terminated before end date
      - "renewed": Old policy shows RENEWED when a new one takes ACTIVE

    Args:
        policy_base_id (int): Policy base ID
        scenario (str): Scenario label

    Returns:
        dict: Result from update_policy_base_status
    """
    status_name = _get_status_name_from_scenario(scenario)
    if not status_name:
        return {
            "success": False,
            "message": f"Unsupported scenario '{scenario}'. Supported: "
                       f"draft, pending_issuance, active, renewal_in_progress, cancelled, renewed",
            "status_id": None
        }

    return update_policy_base_status(policy_base_id, status_name)


def bulk_set_policy_base_status_by_scenario(policy_base_ids, scenario):
    """
    Bulk set policy base status using a business scenario label.

    Args:
        policy_base_ids (list[int]): Policy base IDs
        scenario (str): Scenario label (same supported values as single setter)

    Returns:
        dict: Result from bulk_update_policy_base_statuses
    """
    status_name = _get_status_name_from_scenario(scenario)
    if not status_name:
        return {
            "success": False,
            "message": f"Unsupported scenario '{scenario}'. Supported: "
                       f"draft, pending_issuance, active, renewal_in_progress, cancelled, renewed",
            "updated_count": 0,
            "failed_ids": policy_base_ids
        }

    return bulk_update_policy_base_statuses(policy_base_ids, status_name)
