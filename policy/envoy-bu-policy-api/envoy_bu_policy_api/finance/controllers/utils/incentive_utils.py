from datetime import datetime, timedelta
import json
from mServices import QueryBuilderService
from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_DEFINITIONS, PERFORMANCE_FIELD_REGISTRY, get_aggregation_type_from_key
import re

def evaluate_condition(performance_value, operator, value):
    """Evaluate a single condition by comparing performance_value with the condition value."""
    try:
        if performance_value is not None:
            if hasattr(performance_value, '__float__'):
                performance_value = float(performance_value)
            
            if isinstance(performance_value, (int, float)):
                # Handle list/tuple values first (for between, in, not in operators)
                if isinstance(value, (list, tuple)):
                    if operator == "between":
                        if len(value) == 2:
                            try:
                                start_val = float(value[0])
                                end_val = float(value[1])
                                result = start_val <= performance_value <= end_val
                            except (ValueError, TypeError):
                                result = False
                        else:
                            result = False
                    elif operator == "in":
                        try:
                            result = any(abs(performance_value - float(v)) < 0.01 for v in value)
                        except (ValueError, TypeError):
                            result = False
                    elif operator == "not in":
                        try:
                            result = not any(abs(performance_value - float(v)) < 0.01 for v in value)
                        except (ValueError, TypeError):
                            result = True  # If can't compare, consider it "not in"
                    else:
                        result = False
                    return result
                
                # Handle string or numeric values
                if isinstance(value, str):
                    try:
                        converted_value = float(value)
                    except ValueError:
                        numeric_match = re.search(r'\d+(?:\.\d+)?', value)
                        if numeric_match:
                            converted_value = float(numeric_match.group())
                        else:
                            converted_value = 0
                else:
                    converted_value = float(value)
                
                if operator == "<":
                    result = performance_value < converted_value
                elif operator == "<=":
                    result = performance_value <= converted_value
                elif operator == "=":
                    result = abs(performance_value - converted_value) < 0.01
                elif operator == ">=":
                    result = performance_value >= converted_value
                elif operator == ">":
                    result = performance_value > converted_value
                else:
                    result = False
                
                return result
            else:
                # For non-numeric values, use string comparison
                if operator == "=":
                    return str(performance_value) == str(value)
                elif operator == "!=":
                    return str(performance_value) != str(value)
                elif operator == "in":
                    return str(performance_value) in [str(v) for v in converted_value] if isinstance(converted_value, (list, tuple)) else False
                elif operator == "not in":
                    return str(performance_value) not in [str(v) for v in converted_value] if isinstance(converted_value, (list, tuple)) else True
                else:
                    return False
        else:
            return False
    except Exception as e:
        print(f"Error in evaluate_condition: {e}")
        return False

def get_periods_for_setup(setup):
    """Generate periods for an incentive setup based on its repetition type."""
    try:
        repeation_type = setup.get("repeation_type", "One-Time")
        start_date = setup.get("start_date")
        end_date = setup.get("end_date")
        
        if not start_date or not end_date:
            return []
        
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        
        periods = []
        
        if repeation_type == "One-Time":
            periods.append((start_date, end_date))
        elif repeation_type == "Monthly":
            current = start_date.replace(day=1)
            while current <= end_date:
                if current.month == 12:
                    next_month = current.replace(year=current.year + 1, month=1, day=1)
                else:
                    next_month = current.replace(month=current.month + 1, day=1)
                
                period_start = max(current, start_date)
                period_end = min(next_month - timedelta(days=1), end_date)
                
                if period_start <= period_end:
                    periods.append((period_start, period_end))
                
                current = next_month
        elif repeation_type == "Quarterly":
            current = start_date.replace(day=1)
            while current <= end_date:
                quarter_start_month = ((current.month - 1) // 3) * 3 + 1
                quarter_start = current.replace(month=quarter_start_month, day=1)
                
                quarter_end_month = quarter_start_month + 2
                if quarter_end_month > 12:
                    quarter_end_month = 12
                
                if quarter_end_month == 12:
                    next_quarter = quarter_start.replace(year=quarter_start.year + 1, month=1, day=1)
                else:
                    next_quarter = quarter_start.replace(month=quarter_end_month + 1, day=1)
                
                quarter_end = next_quarter - timedelta(days=1)
                period_start = max(quarter_start, start_date)
                period_end = min(quarter_end, end_date)
                
                if period_start <= period_end:
                    periods.append((period_start, period_end))
                
                current = next_quarter
        elif repeation_type == "Annually":
            current = start_date.replace(month=1, day=1)
            while current <= end_date:
                next_year = current.replace(year=current.year + 1)
                period_start = max(current, start_date)
                period_end = min(next_year - timedelta(days=1), end_date)
                
                if period_start <= period_end:
                    periods.append((period_start, period_end))
                
                current = next_year
        
        return periods
    except Exception as e:
        print(f"Error generating periods: {e}")
        return []

def convert_decimal_to_float(obj):
    """Convert Decimal objects to float recursively."""
    if isinstance(obj, dict):
        return {k: convert_decimal_to_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_to_float(item) for item in obj]
    elif hasattr(obj, '__float__'):
        return float(obj)
    else:
        return obj

def find_agents_for_period(setup, period):
    """Find agents for a given period based on the incentive setup."""
    try:
        # Get the first field from performance_fields to determine the registry
        performance_fields = setup.get("performance_fields", {})
        if isinstance(performance_fields, str):
            performance_fields = json.loads(performance_fields)
        
        
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            fields, target_based_condition = extract_fields_from_conditions(performance_fields["conditions"])
        
        # Store original fields before any modifications (for fallback logic check)
        original_fields = fields.copy() if fields else []
        
        if not fields:
            return []
        
        # If this is a target-based condition, find agents from sales targets table
        if target_based_condition and period and isinstance(period, tuple) and len(period) == 2:
            start_date, end_date = period
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            # Extract month and year from period
            period_start_month = start_date.month
            period_start_year = start_date.year
            period_end_month = end_date.month
            period_end_year = end_date.year
            
            # Check for role filter (using recursive extraction) - handle multiple roles
            role_conditions = []
            if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                role_conditions = extract_all_role_conditions_from_conditions(performance_fields.get("conditions", []))
            
            # Find agents from sales targets table for the period
            from django.db import connection
            with connection.cursor() as cursor:
                # Build query to find agents with targets in the period
                if period_start_year == period_end_year and period_start_month == period_end_month:
                    # Single month
                    sql = """
                        SELECT DISTINCT crmf_agent_sales_targets.agent_id 
                        FROM crmf_agent_sales_targets
                        LEFT JOIN core_users ON crmf_agent_sales_targets.agent_id = core_users.id
                        WHERE crmf_agent_sales_targets.period_type = 'monthly'
                          AND crmf_agent_sales_targets.month = %s
                          AND crmf_agent_sales_targets.year = %s
                          AND crmf_agent_sales_targets.deleted_at IS NULL
                    """
                    params = [period_start_month, period_start_year]
                else:
                    # Multi-month period
                    sql = """
                        SELECT DISTINCT crmf_agent_sales_targets.agent_id 
                        FROM crmf_agent_sales_targets
                        LEFT JOIN core_users ON crmf_agent_sales_targets.agent_id = core_users.id
                        WHERE crmf_agent_sales_targets.period_type = 'monthly'
                          AND ((crmf_agent_sales_targets.year > %s OR (crmf_agent_sales_targets.year = %s AND crmf_agent_sales_targets.month >= %s))
                          AND (crmf_agent_sales_targets.year < %s OR (crmf_agent_sales_targets.year = %s AND crmf_agent_sales_targets.month <= %s)))
                          AND crmf_agent_sales_targets.deleted_at IS NULL
                    """
                    params = [
                        period_start_year, period_start_year, period_start_month,
                        period_end_year, period_end_year, period_end_month
                    ]
                
                # Add role filter if specified (handle multiple roles with IN clause)
                if len(role_conditions) > 0:
                    if len(role_conditions) == 1:
                        sql += " AND core_users.role_id = %s"
                        params.append(role_conditions[0])
                    else:
                        # Multiple role conditions - use IN clause (OR logic for finding agents)
                        placeholders = ",".join(["%s"] * len(role_conditions))
                        sql += f" AND core_users.role_id IN ({placeholders})"
                        params.extend(role_conditions)
                
                print(f"Finding agents from sales targets for target-based condition: {sql}")
                print(f"Params: {params}")
                cursor.execute(sql, params)
                results = cursor.fetchall()
                agent_ids = [row[0] for row in results if row[0] is not None]
                print(f"Found {len(agent_ids)} agents with sales targets for period: {agent_ids}")
                
                if agent_ids:
                    return agent_ids
                else:
                    print("No agents found with sales targets, falling back to regular agent finding logic")
        
        # Find the first field that has a registry entry (skip filter fields like "role", "role_id")
        from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
        registry = None
        field_to_use = None
        
        # Filter fields that don't have registry entries (these are filter-only fields)
        filter_fields = {"role", "role_id", "user_role", "team_role", "agent_id", "product", "insurer", "risk_type", "native_product", "product_id"}
        
        # IMPORTANT: If ALL fields are filter fields, we should use the fallback logic immediately
        # Don't try to find a registry if we only have filter fields
        if all(field in filter_fields for field in fields):
            # All fields are filter fields - skip registry search and go to fallback
            registry = None
        else:
            # Try all fields to find a suitable registry (prioritize fields that can find agents)
            for field in fields:
                # Skip filter-only fields
                if field in filter_fields:
                    continue
                
                # Try to find registry for this field
                for reg in PERFORMANCE_FIELD_REGISTRY:
                    if reg.get("parameter") == field or field in reg.get("field", []):
                        # Prefer registries that have agent_field (can find agents)
                        if reg.get("agent_field"):
                            registry = reg
                            field_to_use = field
                            break
                
                if registry:
                    break
        
        # If still no registry found, try any registry (even without agent_field)
        if not registry:
            for field in fields:
                if field in filter_fields:
                    continue
                for reg in PERFORMANCE_FIELD_REGISTRY:
                    if reg.get("parameter") == field or field in reg.get("field", []):
                        registry = reg
                        field_to_use = field
                        break
                if registry:
                    break
        
        # If no registry found, try fallback for filter-only fields (like role)
        if not registry:
            # Check if we have only filter fields - if so, query agents from core_users or team tables
            # Use original_fields (before incentive_base_field was added) to check if we only have filter fields
            if all(field in filter_fields for field in original_fields):
                # Extract both user_role and team_role conditions
                role_conditions = []
                team_role_conditions = []
                if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                    role_conditions = extract_all_role_conditions_from_conditions(performance_fields.get("conditions", []))
                    team_role_conditions = extract_all_team_role_conditions_from_conditions(performance_fields.get("conditions", []))
                
                # Query agents from core_users or team tables
                from django.db import connection
                with connection.cursor() as cursor:
                    agent_ids = set()
                    
                    # Get agents from user roles (core_users.role_id)
                    if len(role_conditions) > 0:
                        if len(role_conditions) == 1:
                            cursor.execute("SELECT DISTINCT id FROM core_users WHERE role_id = %s", [role_conditions[0]])
                        else:
                            placeholders = ",".join(["%s"] * len(role_conditions))
                            cursor.execute(f"SELECT DISTINCT id FROM core_users WHERE role_id IN ({placeholders})", role_conditions)
                        results = cursor.fetchall()
                        for row in results:
                            if row[0] is not None:
                                agent_ids.add(row[0])
                        print(f"Found {len([r[0] for r in results if r[0] is not None])} agents with user_role in {role_conditions} from core_users")
                    
                    # Get agents from team roles
                    if len(team_role_conditions) > 0:
                        for team_role_value in team_role_conditions:
                            # Normalize team_role value
                            team_role_type = None
                            if isinstance(team_role_value, str):
                                value_lower = team_role_value.lower().strip()
                                if value_lower in ["team lead", "team_lead", "account manager", "account_manager", "manager", "lead"]:
                                    team_role_type = "manager"
                                elif value_lower in ["team member", "team_member", "sales agent", "sales_agent", "member", "agent"]:
                                    team_role_type = "member"
                            elif isinstance(team_role_value, (int, float)):
                                int_value = int(team_role_value)
                                if int_value == 8:
                                    team_role_type = "manager"
                                elif int_value == 2:
                                    team_role_type = "member"
                            
                            if team_role_type == "manager":
                                cursor.execute("SELECT DISTINCT manager_id FROM core_teams WHERE manager_id IS NOT NULL AND deleted_at IS NULL")
                                manager_results = cursor.fetchall()
                                for row in manager_results:
                                    if row[0] is not None:
                                        agent_ids.add(row[0])
                                print(f"Found {len([r[0] for r in manager_results if r[0] is not None])} agents who are managers in teams (team_role={team_role_value})")
                            
                            elif team_role_type == "member":
                                cursor.execute("SELECT DISTINCT user_id FROM core_team_users")
                                team_user_results = cursor.fetchall()
                                for row in team_user_results:
                                    if row[0] is not None:
                                        agent_ids.add(row[0])
                                print(f"Found {len([r[0] for r in team_user_results if r[0] is not None])} agents who are in teams (team_role={team_role_value})")
                    
                    if len(agent_ids) > 0:
                        agent_ids = list(agent_ids)
                        print(f"Found {len(agent_ids)} total agents (user_roles: {role_conditions}, team_roles: {team_role_conditions})")
                        return agent_ids
                    else:
                        # No specific role condition - query all agents
                        cursor.execute("SELECT DISTINCT id FROM core_users")
                        results = cursor.fetchall()
                        agent_ids = [row[0] for row in results if row[0] is not None]
                        print(f"Found {len(agent_ids)} agents from core_users fallback (no role filter)")
                        return agent_ids
            else:
                print(f"No registry found for any field in {fields}, cannot find agents")
                return []
        
        # Check if we have a role condition - if so, we should include all agents with that role
        # even if they don't have records in the base table (for conditions like "sum_of_commission_deductible < 20000")
        # Handle multiple role conditions (e.g., role=2 AND role=8) - find agents with ANY of the roles
        role_conditions = []
        team_role_conditions = []
        has_role_condition = False
        has_team_role_condition = False
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            role_conditions = extract_all_role_conditions_from_conditions(performance_fields.get("conditions", []))
            team_role_conditions = extract_all_team_role_conditions_from_conditions(performance_fields.get("conditions", []))
            has_role_condition = (len(role_conditions) > 0)
            has_team_role_condition = (len(team_role_conditions) > 0)
        
        # If we have role condition(s) AND a registry, we should find all agents with those roles
        # and let the condition evaluation filter them (since some agents might have 0 or NULL values)
        if (has_role_condition or has_team_role_condition) and registry:
            # First, get all agents with any of the roles (OR logic for finding agents)
            from django.db import connection
            with connection.cursor() as role_cursor:
                all_role_agent_ids = set()
                
                # Get agents from user roles (core_users.role_id)
                if has_role_condition:
                    if len(role_conditions) == 1:
                        role_cursor.execute("SELECT DISTINCT id FROM core_users WHERE role_id = %s", [role_conditions[0]])
                    else:
                        placeholders = ",".join(["%s"] * len(role_conditions))
                        role_cursor.execute(f"SELECT DISTINCT id FROM core_users WHERE role_id IN ({placeholders})", role_conditions)
                    role_results = role_cursor.fetchall()
                    for row in role_results:
                        if row[0] is not None:
                            all_role_agent_ids.add(row[0])
                    print(f"Found {len([r[0] for r in role_results if r[0] is not None])} agents with user_role in {role_conditions} from core_users")
                
                # Get agents from team roles
                if has_team_role_condition:
                    for team_role_value in team_role_conditions:
                        # Normalize team_role value
                        team_role_type = None
                        if isinstance(team_role_value, str):
                            value_lower = team_role_value.lower().strip()
                            if value_lower in ["team lead", "team_lead", "account manager", "account_manager", "manager", "lead"]:
                                team_role_type = "manager"
                            elif value_lower in ["team member", "team_member", "sales agent", "sales_agent", "member", "agent"]:
                                team_role_type = "member"
                        elif isinstance(team_role_value, (int, float)):
                            int_value = int(team_role_value)
                            if int_value == 8:
                                team_role_type = "manager"
                            elif int_value == 2:
                                team_role_type = "member"
                        
                        if team_role_type == "manager":
                            role_cursor.execute("SELECT DISTINCT manager_id FROM core_teams WHERE manager_id IS NOT NULL AND deleted_at IS NULL")
                            manager_results = role_cursor.fetchall()
                            for row in manager_results:
                                if row[0] is not None:
                                    all_role_agent_ids.add(row[0])
                            print(f"Found {len([r[0] for r in manager_results if r[0] is not None])} agents who are managers in teams (team_role={team_role_value})")
                        
                        elif team_role_type == "member":
                            role_cursor.execute("SELECT DISTINCT user_id FROM core_team_users")
                            team_user_results = role_cursor.fetchall()
                            for row in team_user_results:
                                if row[0] is not None:
                                    all_role_agent_ids.add(row[0])
                            print(f"Found {len([r[0] for r in team_user_results if r[0] is not None])} agents who are in teams (team_role={team_role_value})")
                
                all_role_agent_ids = list(all_role_agent_ids)
                print(f"Found {len(all_role_agent_ids)} total agents (user_roles: {role_conditions}, team_roles: {team_role_conditions})")
            
            # Also get agents from the registry (those with records in the base table)
            agent_field = registry.get("agent_field")
            if agent_field:
                base_table = registry["base_table"]
                joins = registry.get("joins", [])
                
                # Build SQL query
                sql = f"SELECT DISTINCT {agent_field} as agent_id FROM {base_table}"
                
                # Add joins
                for join in joins:
                    sql += f" JOIN {join['table']} ON {join['on']}"
                
                # Add date filters if period is provided
                where_conditions = []
                params = []
                
                if period and isinstance(period, tuple) and len(period) == 2:
                    start_date, end_date = period
                    if isinstance(start_date, str):
                        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                    if isinstance(end_date, str):
                        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                    
                    # Add date filter based on registry filters or available joins
                    date_fields = ["created_at", "updated_at", "policy_effective_date", "invoice_date", "policy_start_date"]
                    date_field_found = False
                    joined_tables = [join.get("table") for join in joins]
                    
                    for date_field in date_fields:
                        # Check if date field is in filters OR if its table is available through joins
                        date_table = None
                        if date_field in registry.get("filters", []):
                            # Date field is explicitly in filters
                            date_table = base_table
                            if date_field == "policy_effective_date" and "crmp_issued_policies" in joined_tables:
                                date_table = "crmp_issued_policies"
                            elif date_field == "invoice_date" and "crmf_invoices" in joined_tables:
                                date_table = "crmf_invoices"
                            elif date_field == "policy_start_date" and "crmp_policy_base" in joined_tables:
                                date_table = "crmp_policy_base"
                        elif date_field == "policy_effective_date" and "crmp_issued_policies" in joined_tables:
                            # policy_effective_date is available through joins even if not in filters
                            date_table = "crmp_issued_policies"
                        elif date_field == "invoice_date" and "crmf_invoices" in joined_tables:
                            # invoice_date is available through joins even if not in filters
                            date_table = "crmf_invoices"
                        elif date_field == "policy_start_date" and "crmp_policy_base" in joined_tables:
                            # policy_start_date is available through joins even if not in filters
                            date_table = "crmp_policy_base"
                        
                        if date_table:
                            where_conditions.append(f"{date_table}.{date_field} >= %s")
                            where_conditions.append(f"{date_table}.{date_field} <= %s")
                            params.extend([start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
                            date_field_found = True
                            print(f"Added date filter for {date_table}.{date_field} between {start_date} and {end_date}")
                            break
                
                if where_conditions:
                    sql += " WHERE " + " AND ".join(where_conditions)
                
                # Execute query to get agents with records
                with connection.cursor() as cursor:
                    cursor.execute(sql, params)
                    results = cursor.fetchall()
                    registry_agent_ids = [row[0] for row in results if row[0] is not None]
                    print(f"Found {len(registry_agent_ids)} agents with records in {base_table}")
                
                # Combine both lists (agents with role + agents with records)
                # This ensures we include agents who might have 0 or NULL values for the condition field
                combined_agent_ids = list(set(all_role_agent_ids + registry_agent_ids))
                print(f"Combined agent list: {len(combined_agent_ids)} agents (role-based: {len(all_role_agent_ids)}, registry-based: {len(registry_agent_ids)})")
                print(f"Combined agent IDs: {combined_agent_ids}")
                return combined_agent_ids
        
        # Continue with regular registry-based agent finding if no role condition
        
        # Query agents from the registry's base table using raw SQL
        agent_field = registry.get("agent_field")
        if not agent_field:
            return []
        
        base_table = registry["base_table"]
        joins = registry.get("joins", [])
        
        # Build SQL query
        sql = f"SELECT DISTINCT {agent_field} as agent_id FROM {base_table}"
        
        # Add joins
        for join in joins:
            sql += f" JOIN {join['table']} ON {join['on']}"
        
        # Check for role filter and add core_users join if needed (using recursive extraction)
        # For multiple role conditions, we'll use the first one for the join (or handle in WHERE clause)
        role_filter_values = []
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            role_filter_values = extract_all_role_conditions_from_conditions(performance_fields.get("conditions", []))
        
        # Add core_users join if role filter exists and core_users is not already joined
        if len(role_filter_values) > 0:
            joined_tables = [join.get("table") for join in joins]
            if "core_users" not in joined_tables:
                # Determine how to join core_users based on agent_field
                if agent_field:
                    # Extract the table and column from agent_field (e.g., "crmp_policy_base.sales_agent_id" or "crmf_agent_sales_targets.agent_id")
                    # Remove " as agent_id" suffix if present
                    clean_agent_field = agent_field.replace(" as agent_id", "").strip()
                    if "." in clean_agent_field:
                        agent_table, agent_col = clean_agent_field.split(".")[0], clean_agent_field.split(".")[1]
                        sql += f" JOIN core_users ON {agent_table}.{agent_col} = core_users.id"
                        joins.append({"table": "core_users", "on": f"{agent_table}.{agent_col} = core_users.id"})
                        print(f"Added core_users join for role filtering: {agent_table}.{agent_col} = core_users.id")
                    else:
                        # If agent_field doesn't have table prefix, try to use it directly
                        # This is less common but handle it
                        print(f"Warning: Cannot determine join path for role filter, agent_field format: {agent_field}")
        
        # Add date filters if period is provided
        where_conditions = []
        params = []
        
        if period and isinstance(period, tuple) and len(period) == 2:
            start_date, end_date = period
            # Convert string dates to date objects if needed
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
            
            # Special handling for sales target tables (use month/year instead of dates)
            if base_table in ["crmf_agent_sales_targets", "crmf_team_sales_targets"]:
                # Extract month and year from the period
                # For sales targets, we match targets that fall within the period
                period_start_month = start_date.month
                period_start_year = start_date.year
                period_end_month = end_date.month
                period_end_year = end_date.year
                
                # If period spans multiple months, we need to handle it
                if period_start_year == period_end_year and period_start_month == period_end_month:
                    # Single month period
                    where_conditions.append(f"{base_table}.month = %s")
                    where_conditions.append(f"{base_table}.year = %s")
                    params.extend([period_start_month, period_start_year])
                    print(f"Added sales target filter: month={period_start_month}, year={period_start_year}")
                else:
                    # Multi-month period - find targets in any month within the period
                    # This is more complex, so we'll use a range check
                    # For simplicity, we'll match targets where (year, month) >= (start_year, start_month) 
                    # and (year, month) <= (end_year, end_month)
                    where_conditions.append(
                        f"({base_table}.year > %s OR ({base_table}.year = %s AND {base_table}.month >= %s))"
                    )
                    where_conditions.append(
                        f"({base_table}.year < %s OR ({base_table}.year = %s AND {base_table}.month <= %s))"
                    )
                    params.extend([
                        period_start_year, period_start_year, period_start_month,
                        period_end_year, period_end_year, period_end_month
                    ])
                    print(f"Added sales target range filter: from {period_start_year}-{period_start_month} to {period_end_year}-{period_end_month}")
            else:
                # Regular date-based filtering for other tables
                date_fields = ["created_at", "updated_at", "policy_effective_date", "invoice_date", "policy_start_date"]
                date_field_found = False
                
                for date_field in date_fields:
                    if date_field in registry.get("filters", []):
                        # Determine which table has the date field
                        date_table = base_table
                        
                        # policy_effective_date is in crmp_issued_policies, not crmp_policy_base
                        if date_field == "policy_effective_date":
                            if base_table == "crmp_issued_policies":
                                date_table = "crmp_issued_policies"
                            elif "crmp_issued_policies" in [join.get("table") for join in joins]:
                                date_table = "crmp_issued_policies"
                            else:
                                # If not found in joins, try base_table
                                date_table = base_table
                        # policy_start_date is in crmp_policy_base
                        elif date_field == "policy_start_date":
                            if base_table == "crmp_policy_base":
                                date_table = "crmp_policy_base"
                            elif "crmp_policy_base" in [join.get("table") for join in joins]:
                                date_table = "crmp_policy_base"
                            else:
                                date_table = base_table
                        # invoice_date is typically in crmf_invoices
                        elif date_field == "invoice_date":
                            if base_table == "crmf_invoices":
                                date_table = "crmf_invoices"
                            elif "crmf_invoices" in [join.get("table") for join in joins]:
                                date_table = "crmf_invoices"
                            else:
                                date_table = base_table
                        
                        where_conditions.append(f"{date_table}.{date_field} >= %s")
                        where_conditions.append(f"{date_table}.{date_field} <= %s")
                        params.extend([start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
                        date_field_found = True
                        print(f"Added date filter: {date_table}.{date_field} between {start_date} and {end_date}")
                        break
                
                # If no date field found in filters, try using start_date from crmp_issued_policies as fallback
                if not date_field_found:
                    # Try to use start_date from crmp_issued_policies if available
                    if base_table == "crmp_issued_policies" or "crmp_issued_policies" in [join.get("table") for join in joins]:
                        date_table = "crmp_issued_policies"
                        where_conditions.append(f"{date_table}.start_date >= %s")
                        where_conditions.append(f"{date_table}.start_date <= %s")
                        params.extend([start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")])
                        print(f"Using fallback date filter: {date_table}.start_date between {start_date} and {end_date}")
                    else:
                        # Last resort: try created_at (but many tables don't have this)
                        print(f"Warning: No suitable date field found for filtering, skipping date filter")
        
        # Add role filter if role condition exists (handle multiple roles with IN clause)
        if len(role_filter_values) > 0:
            # core_users should already be joined if role filter exists
            joined_tables = [join.get("table") for join in joins]
            if "core_users" in joined_tables:
                if len(role_filter_values) == 1:
                    where_conditions.append("core_users.role_id = %s")
                    params.append(role_filter_values[0])
                    print(f"Added role filter: core_users.role_id = {role_filter_values[0]}")
                else:
                    # Multiple role conditions - use IN clause (OR logic for finding agents)
                    placeholders = ",".join(["%s"] * len(role_filter_values))
                    where_conditions.append(f"core_users.role_id IN ({placeholders})")
                    params.extend(role_filter_values)
                    print(f"Added role filter: core_users.role_id IN {role_filter_values}")
            else:
                print(f"Warning: Role filter requested but core_users not joined, skipping role filter")
        
        if where_conditions:
            sql += " WHERE " + " AND ".join(where_conditions)
        
        print(f"Executing agent lookup query: {sql}")
        print(f"Query parameters: {params}")
        
        # Execute query
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            results = cursor.fetchall()
            found_ids = [row[0] for row in results if row[0] is not None]
            print(f"Found {len(found_ids)} IDs from {field_to_use}: {found_ids}")
            
            # Check if agent_field points to team_id (team-based field)
            # If agent_field is "core_teams.id" or contains "team_id", we need to convert team IDs to agent IDs
            agent_ids = []
            if agent_field and ("team_id" in agent_field.lower() or "core_teams.id" in agent_field):
                # These are team IDs, need to convert to agent IDs
                print(f"Detected team-based field ({agent_field}), converting team IDs to agent IDs...")
                if found_ids:
                    # Query all agents in these teams
                    team_ids = found_ids
                    placeholders = ",".join(["%s"] * len(team_ids))
                    team_to_agent_sql = f"SELECT DISTINCT user_id FROM core_team_users WHERE team_id IN ({placeholders})"
                    cursor.execute(team_to_agent_sql, team_ids)
                    team_agent_results = cursor.fetchall()
                    agent_ids = [row[0] for row in team_agent_results if row[0] is not None]
                    print(f"Converted {len(team_ids)} team IDs to {len(agent_ids)} agent IDs: {agent_ids}")
                else:
                    agent_ids = []
            else:
                # These are already agent IDs
                agent_ids = found_ids
            
            print(f"Final agent IDs for processing: {agent_ids}")
            
            # If no agents found and we have other fields to try, try them as fallback
            if not agent_ids and len(fields) > 1:
                print(f"No agents found from primary field {field_to_use}, trying other fields as fallback...")
                for fallback_field in fields:
                    if fallback_field == field_to_use or fallback_field in filter_fields:
                        continue
                    
                    # Try to find registry for fallback field
                    fallback_registry = None
                    for reg in PERFORMANCE_FIELD_REGISTRY:
                        if reg.get("parameter") == fallback_field or fallback_field in reg.get("field", []):
                            if reg.get("agent_field"):
                                fallback_registry = reg
                                break
                    
                    if fallback_registry:
                        fallback_agent_field = fallback_registry.get("agent_field")
                        fallback_base_table = fallback_registry["base_table"]
                        fallback_joins = fallback_registry.get("joins", [])
                        
                        if fallback_agent_field:
                            # Build fallback query (without date filters for now, to be more inclusive)
                            fallback_sql = f"SELECT DISTINCT {fallback_agent_field} as agent_id FROM {fallback_base_table}"
                            for join in fallback_joins:
                                fallback_sql += f" JOIN {join['table']} ON {join['on']}"
                            
                            try:
                                cursor.execute(fallback_sql)
                                fallback_results = cursor.fetchall()
                                fallback_found_ids = [row[0] for row in fallback_results if row[0] is not None]
                                
                                # Check if fallback also returns team IDs
                                fallback_agent_ids = []
                                if fallback_agent_field and ("team_id" in fallback_agent_field.lower() or "core_teams.id" in fallback_agent_field):
                                    # Convert team IDs to agent IDs
                                    if fallback_found_ids:
                                        placeholders = ",".join(["%s"] * len(fallback_found_ids))
                                        team_to_agent_sql = f"SELECT DISTINCT user_id FROM core_team_users WHERE team_id IN ({placeholders})"
                                        cursor.execute(team_to_agent_sql, fallback_found_ids)
                                        team_agent_results = cursor.fetchall()
                                        fallback_agent_ids = [row[0] for row in team_agent_results if row[0] is not None]
                                        print(f"Converted {len(fallback_found_ids)} team IDs to {len(fallback_agent_ids)} agent IDs from fallback field")
                                else:
                                    fallback_agent_ids = fallback_found_ids
                                
                                if fallback_agent_ids:
                                    print(f"Found {len(fallback_agent_ids)} agents from fallback field {fallback_field}: {fallback_agent_ids}")
                                    agent_ids = fallback_agent_ids
                                    break
                            except Exception as fallback_error:
                                print(f"Error trying fallback field {fallback_field}: {fallback_error}")
                                continue
            
            return agent_ids
    except Exception as e:
        print(f"Error finding agents for period: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_fields_from_conditions(conditions):
    """
    Recursively extract all fields from conditions, handling nested logic structures.
    
    Args:
        conditions: List of conditions or a single condition dict
    
    Returns:
        tuple: (fields_list, has_target_based_condition)
    """
    fields = []
    has_target_based = False
    target_fields = ["sum_of_agent_achieved", "sum_of_agent_sales_target", 
                     "sum_of_team_achieved", "sum_of_team_sales_target"]
    
    if not isinstance(conditions, list):
        conditions = [conditions] if conditions else []
    
    for condition in conditions:
        if isinstance(condition, dict):
            # Check if this is a nested logic structure
            if "logic" in condition and "conditions" in condition:
                # Recursively extract from nested conditions
                nested_fields, nested_target = extract_fields_from_conditions(condition["conditions"])
                fields.extend(nested_fields)
                if nested_target:
                    has_target_based = True
            else:
                # Regular condition with field
                if "field" in condition:
                    field = condition["field"]
                    fields.append(field)
                    if field in target_fields:
                        has_target_based = True
                
                # Check if value is a field reference
                value = condition.get("value")
                if is_field_reference(value):
                    fields.append(value)
                    if value in target_fields:
                        has_target_based = True
    
    return fields, has_target_based

def extract_role_condition_from_conditions(conditions):
    """
    Recursively extract role condition from nested conditions.
    
    Args:
        conditions: List of conditions or a single condition dict
    
    Returns:
        int or None: Role ID if found, None otherwise
    """
    if not isinstance(conditions, list):
        conditions = [conditions] if conditions else []
    
    for condition in conditions:
        if isinstance(condition, dict):
            # Check if this is a nested logic structure
            if "logic" in condition and "conditions" in condition:
                # Recursively search nested conditions
                role_condition = extract_role_condition_from_conditions(condition["conditions"])
                if role_condition is not None:
                    return role_condition
            else:
                # Regular condition - check if it's a role condition
                cond_field = condition.get("field")
                cond_value = condition.get("value")
                if cond_field in ("role", "role_id") and cond_value is not None:
                    try:
                        return int(cond_value)
                    except (ValueError, TypeError):
                        pass
    
    return None

def extract_all_role_conditions_from_conditions(conditions):
    """
    Recursively extract ALL role conditions from nested conditions.
    This is useful when there are multiple role conditions (e.g., role=2 AND role=8),
    which should be treated as OR when finding agents (find agents with role 2 OR role 8).
    
    Args:
        conditions: List of conditions or a single condition dict
    
    Returns:
        list: List of role IDs found, empty list if none found
    """
    role_ids = []
    if not isinstance(conditions, list):
        conditions = [conditions] if conditions else []
    
    for condition in conditions:
        if isinstance(condition, dict):
            # Check if this is a nested logic structure
            if "logic" in condition and "conditions" in condition:
                # Recursively search nested conditions
                nested_role_ids = extract_all_role_conditions_from_conditions(condition["conditions"])
                role_ids.extend(nested_role_ids)
            else:
                # Regular condition - check if it's a role condition (user_role, role, role_id)
                cond_field = condition.get("field")
                cond_value = condition.get("value")
                if cond_field in ("role", "role_id", "user_role") and cond_value is not None:
                    try:
                        role_id = int(cond_value)
                        if role_id not in role_ids:
                            role_ids.append(role_id)
                    except (ValueError, TypeError):
                        pass
    
    return role_ids

def extract_all_team_role_conditions_from_conditions(conditions):
    """
    Recursively extract ALL team_role conditions from nested conditions.
    Returns list of team_role values (can be strings like "team lead", "team member" or integers 8, 2).
    
    Args:
        conditions: List of conditions or a single condition dict
    
    Returns:
        list: List of team_role values found, empty list if none found
    """
    team_roles = []
    if not isinstance(conditions, list):
        conditions = [conditions] if conditions else []
    
    for condition in conditions:
        if isinstance(condition, dict):
            # Check if this is a nested logic structure
            if "logic" in condition and "conditions" in condition:
                # Recursively search nested conditions
                nested_team_roles = extract_all_team_role_conditions_from_conditions(condition["conditions"])
                team_roles.extend(nested_team_roles)
            else:
                # Regular condition - check if it's a team_role condition
                cond_field = condition.get("field")
                cond_value = condition.get("value")
                if cond_field == "team_role" and cond_value is not None:
                    if cond_value not in team_roles:
                        team_roles.append(cond_value)
    
    return team_roles

def is_field_reference(value):
    """
    Check if a value is a field reference (exists in PERFORMANCE_FIELD_DEFINITIONS).
    
    When a user selects a field from the dropdown (e.g., "sum_of_agent_sales_target"),
    the value is stored as the field name string. This function checks if the value
    is a reference to another performance field rather than a direct numeric value.
    
    Example:
        - Direct value: "100000" -> returns False
        - Field reference: "sum_of_agent_sales_target" -> returns True
    
    Returns:
        bool: True if value is a field reference, False otherwise
    """
    if not isinstance(value, str):
        return False
    from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_DEFINITIONS
    # Check if it's a known performance field
    return value in PERFORMANCE_FIELD_DEFINITIONS

def is_team_based_incentive(setup):
    """
    Check if an incentive setup is team-based by looking for team-related fields in conditions.
    
    Returns:
        bool: True if setup uses team-based fields (sum_of_team_achieved, sum_of_team_sales_target), False otherwise
    """
    try:
        performance_fields = setup.get("performance_fields", {})
        if isinstance(performance_fields, str):
            performance_fields = json.loads(performance_fields)
        
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            for condition in performance_fields.get("conditions", []):
                if isinstance(condition, dict):
                    field = condition.get("field")
                    value = condition.get("value")
                    
                    # Check if field is team-based
                    if field and ("team" in field.lower()):
                        return True
                    
                    # Check if value is a team-based field reference
                    if is_field_reference(value) and "team" in value.lower():
                        return True
        
        return False
    except Exception as e:
        print(f"Error checking if incentive is team-based: {e}")
        return False

def get_team_members_for_agent(agent_id):
    """
    Get all team members (including the agent) for teams that the agent belongs to.
    
    Returns:
        list: List of agent IDs (user_ids) that are in the same team(s) as the given agent
    """
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get all teams this agent belongs to
            cursor.execute("SELECT DISTINCT team_id FROM core_team_users WHERE user_id = %s", [agent_id])
            team_results = cursor.fetchall()
            team_ids = [row[0] for row in team_results if row[0] is not None]
            
            if not team_ids:
                # Agent is not in any team, return just the agent
                return [agent_id]
            
            # Get all members from these teams
            placeholders = ",".join(["%s"] * len(team_ids))
            cursor.execute(f"SELECT DISTINCT user_id FROM core_team_users WHERE team_id IN ({placeholders})", team_ids)
            member_results = cursor.fetchall()
            member_ids = [row[0] for row in member_results if row[0] is not None]
            
            print(f"Agent {agent_id} belongs to teams {team_ids}, found {len(member_ids)} team members: {member_ids}")
            return member_ids
    except Exception as e:
        print(f"Error getting team members for agent {agent_id}: {e}")
        return [agent_id]  # Fallback to just the agent

def check_all_team_members_achieved_target(team_id, period, product_id=None):
    """
    Check if ALL team members (excluding manager) achieved their individual targets.
    This validates ONE TEAM at a time (not all teams under a manager).
    
    CRITICAL: This function validates a SINGLE team, not all teams under a manager.
    If a manager manages multiple teams, call this function separately for each team.
    
    CALCULATION (with examples):
    - Target per member = SUM of monthly targets in crmf_agent_sales_targets for the
      full period (all months between start_date and end_date). Sales targets are not
      product-specific.
    - Achieved per member = SUM of premium_amount from issued policies in the period
      where sales_agent_id = member; if product_id is set, only policies with that product.
    
    Example (period 2025-01-28 to 2026-03-05, product_id=31):
      Member 9: target = 50,000 (Jan 2025) + 50,000 (Feb 2025) + ... = 500,000 (sum of 14 months)
               achieved = 1,040,000 (premium from product 31 only in that period)
               => 1,040,000 >= 500,000 => ACHIEVED
      Member 8: target = 30,000 (sum over period), achieved = 30,000 (product 31)
               => 30,000 >= 30,000 => ACHIEVED
      If any member has target = 0 (no target rows in period) or achieved < target, team fails.
    
    Args:
        team_id: The team ID to validate (NOT manager ID)
        period: Period dictionary with start_date and end_date
        product_id: Optional product filter (if None, checks overall target)
    
    Returns:
        dict: {
            "all_achieved": bool,
            "member_results": [
                {
                    "member_id": int,
                    "achieved": float,
                    "target": float,
                    "achieved_target": bool,
                    "message": str
                }
            ],
            "total_members": int,
            "members_achieved": int,
            "team_id": int,
            "manager_id": int
        }
    """
    try:
        from django.db import connection
        from datetime import datetime
        
        with connection.cursor() as cursor:
            # Get team info and manager
            cursor.execute("""
                SELECT id, manager_id 
                FROM core_teams 
                WHERE id = %s AND deleted_at IS NULL
            """, [team_id])
            team_result = cursor.fetchone()
            
            if not team_result:
                print(f"Team {team_id} not found or deleted")
                return {
                    "all_achieved": False,
                    "member_results": [],
                    "total_members": 0,
                    "members_achieved": 0,
                    "team_id": team_id,
                    "manager_id": None,
                    "message": "Team not found or deleted"
                }
            
            team_id_actual, manager_id = team_result
            
            # Get team members (excluding the manager)
            cursor.execute("""
                SELECT DISTINCT user_id 
                FROM core_team_users 
                WHERE team_id = %s
                AND user_id != %s
            """, [team_id_actual, manager_id])
            member_results = cursor.fetchall()
            member_ids = [row[0] for row in member_results if row[0] is not None]
            
            if not member_ids:
                print(f"Team {team_id_actual} has no team members (excluding manager)")
                return {
                    "all_achieved": False,
                    "member_results": [],
                    "total_members": 0,
                    "members_achieved": 0,
                    "team_id": team_id_actual,
                    "manager_id": manager_id,
                    "message": "Team has no members"
                }
            
            print(f"=== TEAM-LEVEL VALIDATION: Team {team_id_actual} ===")
            print(f"Manager: {manager_id}")
            print(f"Members to check: {member_ids}")
            print(f"Period: {period}")
            print(f"Product filter: {product_id}")
            
            # Extract month/year from period for target lookup
            start_date = period.get("start_date")
            end_date = period.get("end_date")
            if isinstance(start_date, str):
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            else:
                start_dt = start_date
            if isinstance(end_date, str):
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            else:
                end_dt = end_date
            
            period_start_month = start_dt.month
            period_start_year = start_dt.year
            period_end_month = end_dt.month
            period_end_year = end_dt.year
            
            # PERFORMANCE FIX: Bulk fetch achievements for all members at once
            achievements_map = {}
            if member_ids:
                placeholders = ",".join(["%s"] * len(member_ids))
                if product_id:
                    # Product-filtered achieved - bulk query
                    cursor.execute(f"""
                        SELECT 
                            crmp_policy_base.sales_agent_id,
                            COALESCE(SUM(crmp_issued_policies.premium_amount), 0) as achieved
                        FROM crmp_issued_policies
                        JOIN crmp_policy_base ON crmp_policy_base.id = crmp_issued_policies.policy_base_id
                        WHERE crmp_policy_base.sales_agent_id IN ({placeholders})
                        AND crmp_policy_base.product_id = %s
                        AND crmp_issued_policies.policy_effective_date >= %s
                        AND crmp_issued_policies.policy_effective_date <= %s
                        GROUP BY crmp_policy_base.sales_agent_id
                    """, member_ids + [product_id, start_date, end_date])
                else:
                    # Overall achieved - bulk query
                    cursor.execute(f"""
                        SELECT 
                            crmp_policy_base.sales_agent_id,
                            COALESCE(SUM(crmp_issued_policies.premium_amount), 0) as achieved
                        FROM crmp_issued_policies
                        JOIN crmp_policy_base ON crmp_policy_base.id = crmp_issued_policies.policy_base_id
                        WHERE crmp_policy_base.sales_agent_id IN ({placeholders})
                        AND crmp_issued_policies.policy_effective_date >= %s
                        AND crmp_issued_policies.policy_effective_date <= %s
                        GROUP BY crmp_policy_base.sales_agent_id
                    """, member_ids + [start_date, end_date])
                
                achievement_results = cursor.fetchall()
                for row in achievement_results:
                    member_id, achieved = row
                    achievements_map[member_id] = float(achieved or 0)
            
            # PERFORMANCE FIX: Bulk fetch targets for all members at once.
            # For periods spanning multiple months, SUM targets across all months in the period
            # (sales targets are stored per month; single-month lookup was returning 0 for long periods).
            targets_map = {}
            if member_ids:
                placeholders = ",".join(["%s"] * len(member_ids))
                cursor.execute(f"""
                    SELECT agent_id, COALESCE(SUM(COALESCE(target_amount, 0)), 0) as target
                    FROM crmf_agent_sales_targets
                    WHERE agent_id IN ({placeholders})
                    AND period_type = 'monthly'
                    AND deleted_at IS NULL
                    AND ((year > %s OR (year = %s AND month >= %s))
                      AND (year < %s OR (year = %s AND month <= %s)))
                    GROUP BY agent_id
                """, member_ids + [
                    period_start_year, period_start_year, period_start_month,
                    period_end_year, period_end_year, period_end_month
                ])
                
                target_results = cursor.fetchall()
                for row in target_results:
                    member_id, target = row
                    targets_map[member_id] = float(target or 0)
            
            # Now validate each member using bulk-fetched data
            member_results_list = []
            all_achieved = True
            
            for member_id in member_ids:
                try:
                    achieved = achievements_map.get(member_id, 0.0)
                    target = targets_map.get(member_id, 0.0)
                    
                    # Financial safety: if target <= 0 or missing, auto fail
                    if target <= 0:
                        print(f"❌ Member {member_id} FAILED: Target is missing or zero (target={target})")
                        member_results_list.append({
                            "member_id": member_id,
                            "achieved": achieved,
                            "target": target,
                            "achieved_target": False,
                            "message": f"Target is missing or zero (target={target})"
                        })
                        all_achieved = False
                        continue
                    
                    # Check if achieved >= target
                    achieved_target = (achieved >= target)
                    
                    if not achieved_target:
                        print(f"❌ Member {member_id} FAILED: {achieved} < {target}")
                        all_achieved = False
                    else:
                        print(f"✅ Member {member_id} ACHIEVED: {achieved} >= {target}")
                    
                    member_results_list.append({
                        "member_id": member_id,
                        "achieved": achieved,
                        "target": target,
                        "achieved_target": achieved_target,
                        "message": f"{achieved} >= {target}" if achieved_target else f"{achieved} < {target}"
                    })
                    
                except Exception as member_error:
                    print(f"Error checking member {member_id}: {member_error}")
                    import traceback
                    traceback.print_exc()
                    member_results_list.append({
                        "member_id": member_id,
                        "achieved": 0.0,
                        "target": 0.0,
                        "achieved_target": False,
                        "message": f"Error: {str(member_error)}"
                    })
                    all_achieved = False
            
            members_achieved = sum(1 for r in member_results_list if r["achieved_target"])
            
            print(f"=== TEAM VALIDATION RESULT ===")
            print(f"Team ID: {team_id_actual}")
            print(f"Manager: {manager_id}")
            print(f"Total members: {len(member_ids)}")
            print(f"Members achieved: {members_achieved}")
            print(f"All members achieved: {all_achieved}")
            
            return {
                "all_achieved": all_achieved,
                "member_results": member_results_list,
                "total_members": len(member_ids),
                "members_achieved": members_achieved,
                "team_id": team_id_actual,
                "manager_id": manager_id,
                "message": f"{members_achieved}/{len(member_ids)} members achieved target" if not all_achieved else "All members achieved target"
            }
            
    except Exception as e:
        print(f"Error in check_all_team_members_achieved_target: {e}")
        import traceback
        traceback.print_exc()
        return {
            "all_achieved": False,
            "member_results": [],
            "total_members": 0,
            "members_achieved": 0,
            "team_id": team_id,
            "manager_id": None,
            "message": f"Error: {str(e)}"
        }

def get_sales_agents_for_account_manager(account_manager_id):
    """
    Get all sales agents (role_id = 2) that report to an account manager.
    Account managers are linked to sales agents via core_teams (manager_id -> team_id -> core_team_users -> user_id).
    
    Args:
        account_manager_id: The account manager's user ID
    
    Returns:
        list: List of sales agent IDs (user_ids) that report to this account manager
    """
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get all teams managed by this account manager
            cursor.execute("SELECT DISTINCT id FROM core_teams WHERE manager_id = %s", [account_manager_id])
            team_results = cursor.fetchall()
            team_ids = [row[0] for row in team_results if row[0] is not None]
            
            if not team_ids:
                print(f"Account manager {account_manager_id} does not manage any teams")
                return []
            
            # Get all sales agents (role_id = 2) in these teams
            placeholders = ",".join(["%s"] * len(team_ids))
            sql = f"""
                SELECT DISTINCT core_team_users.user_id 
                FROM core_team_users 
                JOIN core_users ON core_team_users.user_id = core_users.id
                WHERE core_team_users.team_id IN ({placeholders})
                AND core_users.role_id = 2
            """
            cursor.execute(sql, team_ids)
            agent_results = cursor.fetchall()
            sales_agent_ids = [row[0] for row in agent_results if row[0] is not None]
            
            print(f"Account manager {account_manager_id} manages teams {team_ids}, found {len(sales_agent_ids)} sales agents: {sales_agent_ids}")
            return sales_agent_ids
    except Exception as e:
        print(f"Error getting sales agents for account manager {account_manager_id}: {e}")
        import traceback
        traceback.print_exc()
        return []

def calculate_collective_commission_for_team(agent_ids, incentive_setup, period, product_id=None):
    """
    Calculate the collective commission (sum of all team members' commissions) for a team.
    
    Args:
        agent_ids: List of agent IDs in the team
        incentive_setup: The incentive setup dictionary
        period: Period dictionary with start_date and end_date
    
    Returns:
        float: Sum of all team members' commissions based on the incentive_base_field
    """
    try:
        incentive_base_field = incentive_setup.get("incentive_base_field")
        if not incentive_base_field:
            print("No incentive_base_field specified, cannot calculate collective commission")
            return 0.0
        
        # Find registry for the base field
        from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
        registry = None
        for reg in PERFORMANCE_FIELD_REGISTRY:
            if reg.get("parameter") == incentive_base_field or incentive_base_field in reg.get("field", []):
                registry = reg
                break
        
        if not registry:
            print(f"Registry not found for incentive_base_field '{incentive_base_field}'")
            return 0.0
        
        base_table = registry["base_table"]
        field_name = registry["field"][0] if registry["field"] else "id"
        agent_field = registry.get("agent_field")
        joins = registry.get("joins", [])
        
        if not agent_field:
            print(f"No agent_field in registry for '{incentive_base_field}'")
            return 0.0
        
        # Build SQL query to sum commission for all team members
        sql = f"SELECT COALESCE(SUM({base_table}.{field_name}), 0) as collective_commission FROM {base_table}"
        
        # Add joins
        for join in joins:
            sql += f" JOIN {join['table']} ON {join['on']}"
        
        # Add WHERE clause for agent IDs
        where_conditions = []
        params = []
        
        if agent_field:
            # Extract table and column from agent_field
            if "." in agent_field:
                agent_table, agent_col = agent_field.split(".")[0], agent_field.split(".")[1]
            else:
                agent_table = base_table
                agent_col = agent_field
            
            placeholders = ",".join(["%s"] * len(agent_ids))
            where_conditions.append(f"{agent_table}.{agent_col} IN ({placeholders})")
            params.extend(agent_ids)

        # Apply product filter if requested and supported by registry
        if product_id and "product" in registry.get("filters", []):
            # Default to base_table, but if crmp_policy_base is joined use that
            product_table = base_table
            joined_tables = [join.get("table") for join in joins]
            if "crmp_policy_base" in joined_tables:
                product_table = "crmp_policy_base"
            where_conditions.append(f"{product_table}.product_id = %s")
            params.append(product_id)
        
        # Add date filters if period is provided
        if period and isinstance(period, dict):
            start_date = period.get("start_date")
            end_date = period.get("end_date")
            if start_date and end_date:
                # Special handling for sales target tables
                if base_table in ["crmf_agent_sales_targets", "crmf_team_sales_targets"]:
                    from datetime import datetime
                    if isinstance(start_date, str):
                        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    else:
                        start_dt = start_date
                    if isinstance(end_date, str):
                        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    else:
                        end_dt = end_date
                    
                    period_start_month = start_dt.month
                    period_start_year = start_dt.year
                    period_end_month = end_dt.month
                    period_end_year = end_dt.year
                    
                    if period_start_year == period_end_year and period_start_month == period_end_month:
                        where_conditions.append(f"{base_table}.month = %s")
                        where_conditions.append(f"{base_table}.year = %s")
                        params.extend([period_start_month, period_start_year])
                else:
                    # Regular date-based filtering
                    date_fields = ["created_at", "updated_at", "policy_effective_date", "invoice_date"]
                    date_field_found = False
                    
                    for date_field in date_fields:
                        if date_field in registry.get("filters", []):
                            date_table = base_table
                            if date_field == "policy_effective_date":
                                if "crmp_issued_policies" in [join.get("table") for join in joins]:
                                    date_table = "crmp_issued_policies"
                            elif date_field == "invoice_date":
                                if "crmf_invoices" in [join.get("table") for join in joins]:
                                    date_table = "crmf_invoices"
                            
                            where_conditions.append(f"{date_table}.{date_field} >= %s")
                            where_conditions.append(f"{date_table}.{date_field} <= %s")
                            params.extend([start_date, end_date])
                            date_field_found = True
                            break
                    
                    # Fallback: try policy_effective_date from joined crmp_issued_policies
                    if not date_field_found and "crmp_issued_policies" in [join.get("table") for join in joins]:
                        where_conditions.append("crmp_issued_policies.policy_effective_date >= %s")
                        where_conditions.append("crmp_issued_policies.policy_effective_date <= %s")
                        params.extend([start_date, end_date])
        
        if where_conditions:
            sql += " WHERE " + " AND ".join(where_conditions)
        
        print(f"Calculating collective commission for {len(agent_ids)} team members")
        print(f"SQL: {sql}")
        print(f"Params: {params}")
        
        # Execute query
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            result = cursor.fetchone()
            collective_commission = float(result[0] or 0) if result else 0.0
        
        print(f"Collective commission for team: {collective_commission}")
        return collective_commission
    except Exception as e:
        print(f"Error calculating collective commission for team: {e}")
        import traceback
        traceback.print_exc()
        return 0.0

def aggregate_performance_data(agent_id, incentive_setup, period=None):
    """Aggregate performance data for an agent."""
    try:
        performance_fields = incentive_setup.get("performance_fields", {})
        if isinstance(performance_fields, str):
            performance_fields = json.loads(performance_fields)
        
        # Extract fields from the logic tree (both from 'field' and 'value' if value is a field reference)
        # Use recursive extraction to handle nested conditions
        fields = []
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            fields, _ = extract_fields_from_conditions(performance_fields["conditions"])
            print(f"Aggregating performance data for agent_id={agent_id}: Extracted fields from conditions: {fields}")
        
        # Check if achievement_percentage is used - if so, ensure we aggregate both achieved and target
        has_achievement_percentage = False
        has_percentage_type_on_achieved = False
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            def check_for_achievement_percentage(conditions):
                nonlocal has_achievement_percentage, has_percentage_type_on_achieved
                for condition in conditions:
                    if isinstance(condition, dict):
                        if condition.get("field") in ["achievement_percentage", "achievement_percent"]:
                            has_achievement_percentage = True
                        # Check if percentage type condition is used on achievement fields
                        if condition.get("type") == "percentage" and condition.get("field") in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
                            has_percentage_type_on_achieved = True
                        if "conditions" in condition:
                            check_for_achievement_percentage(condition.get("conditions", []))
            
            check_for_achievement_percentage(performance_fields["conditions"])
        
        if has_achievement_percentage or has_percentage_type_on_achieved:
            # Ensure both sum_of_agent_achieved and sum_of_agent_sales_target are in fields
            if "sum_of_agent_achieved" not in fields:
                fields.append("sum_of_agent_achieved")
                print(f"Added 'sum_of_agent_achieved' to fields (required for achievement_percentage/percentage type calculation)")
            if "sum_of_agent_sales_target" not in fields:
                fields.append("sum_of_agent_sales_target")
                print(f"Added 'sum_of_agent_sales_target' to fields (required for achievement_percentage/percentage type calculation)")
        
        # Also include incentive_base_field if it's not already in fields (needed for percentage calculations)
        # For fixed rewards, base field is optional
        incentive_base_field = incentive_setup.get("incentive_base_field")
        reward_type_id = incentive_setup.get("reward_type_id", 1)  # 1=Fixed, 2=Percentage
        is_percentage = (reward_type_id == 2)
        
        if incentive_base_field and incentive_base_field not in fields:
            fields.append(incentive_base_field)
            print(f"Added incentive_base_field '{incentive_base_field}' to fields for aggregation")
        elif not incentive_base_field and is_percentage:
            print(f"Warning: incentive_base_field is required for percentage rewards but not provided")
        elif not incentive_base_field and not is_percentage:
            print(f"Info: incentive_base_field not provided for fixed reward (optional)")
        
        if not fields:
            # If no aggregatable fields, return empty dict (filter-only conditions like role don't need aggregation)
            # The condition evaluation will handle filter fields directly from the database
            print("No aggregatable fields found - returning empty performance_data (filter-only conditions)")
            return {}
        
        # CRITICAL FIX: Filter-only fields should NEVER be aggregated
        # These fields are used in WHERE clauses only, not in SELECT/GROUP BY
        NON_AGGREGATABLE_FIELDS = {
            "product",
            "native_product",
            "product_id",
            "team_role",
            "role",
            "role_id",
            "user_role",
            "agent_id",
            "insurer",
            "risk_type"
        }
        
        # Filter out non-aggregatable fields before processing
        aggregatable_fields = [f for f in fields if f not in NON_AGGREGATABLE_FIELDS]
        
        # Get registry for each field and aggregate data
        from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
        all_performance_data = {}
        
        for field in aggregatable_fields:
            registry = None
            # Look up registry by parameter (field key) or by field array
            for reg in PERFORMANCE_FIELD_REGISTRY:
                if reg.get("parameter") == field or field in reg.get("field", []):
                    registry = reg
                    break
            
            if not registry:
                continue
            
            # Build query using raw SQL for complex joins
            base_table = registry["base_table"]
            agent_field = registry.get("agent_field")
            field_name = registry["field"][0] if registry["field"] else "id"
            agg_type = registry.get("agg", "sum")
            joins = registry.get("joins", [])
            
            # Build SQL query
            if agg_type == "sum":
                # Use COALESCE to return 0 instead of NULL when there are no rows or all values are NULL
                select_clause = f"COALESCE(SUM({base_table}.{field_name}), 0) as {field_name}"
            elif agg_type == "count":
                select_clause = f"COUNT({base_table}.{field_name}) as {field_name}"
            else:
                select_clause = f"{base_table}.{field_name}"
            
            sql = f"SELECT {select_clause} FROM {base_table}"
            
            # Add joins
            for join in joins:
                sql += f" JOIN {join['table']} ON {join['on']}"
            
            # Add WHERE clause
            where_conditions = []
            params = []
            
            if agent_field:
                # Check if this is a team-based field (agent_field points to team_id)
                if "team_id" in agent_field.lower() or "core_teams.id" in agent_field:
                    # For team-based fields, we need to find the agent's team(s) first
                    # Then filter by those team IDs
                    from django.db import connection
                    with connection.cursor() as team_cursor:
                        # Get all teams this agent belongs to
                        team_cursor.execute("SELECT DISTINCT team_id FROM core_team_users WHERE user_id = %s", [agent_id])
                        team_results = team_cursor.fetchall()
                        team_ids = [row[0] for row in team_results if row[0] is not None]
                        
                        if team_ids:
                            # Filter by team IDs
                            placeholders = ",".join(["%s"] * len(team_ids))
                            where_conditions.append(f"{agent_field} IN ({placeholders})")
                            params.extend(team_ids)
                            print(f"Team-based field: Found {len(team_ids)} teams for agent {agent_id}: {team_ids}")
                        else:
                            # Agent is not in any team, return None/empty
                            print(f"Agent {agent_id} is not in any team, cannot aggregate team-based field {field}")
                            # Add a condition that will never match to return NULL
                            where_conditions.append("1 = 0")
                else:
                    # Regular agent-based field
                    # Special handling for account managers (role_id = 8) when aggregating achievement fields
                    # Account managers should be evaluated based on their sales agents' performance
                    is_account_manager = False
                    if field in ["sum_of_agent_achieved", "sum_of_agent_sales_target"]:
                        try:
                            from django.db import connection
                            with connection.cursor() as role_cursor:
                                role_cursor.execute("SELECT role_id FROM core_users WHERE id = %s", [agent_id])
                                role_result = role_cursor.fetchone()
                                if role_result and role_result[0] == 8:
                                    is_account_manager = True
                                    print(f"Agent {agent_id} is an Account Manager - aggregating {field} from sales agents")
                        except Exception as e:
                            print(f"Error checking agent role for {agent_id}: {e}")
                    
                    if is_account_manager:
                        # Get sales agents for this account manager
                        sales_agent_ids = get_sales_agents_for_account_manager(agent_id)
                        if sales_agent_ids:
                            # Filter by sales agent IDs instead of account manager ID
                            placeholders = ",".join(["%s"] * len(sales_agent_ids))
                            where_conditions.append(f"{agent_field} IN ({placeholders})")
                            params.extend(sales_agent_ids)
                            print(f"Account manager {agent_id} - filtering by {len(sales_agent_ids)} sales agents: {sales_agent_ids}")
                        else:
                            # Account manager has no sales agents, return 0
                            print(f"Account manager {agent_id} has no sales agents - returning 0 for {field}")
                            where_conditions.append("1 = 0")
                    else:
                        # Regular agent-based field
                        where_conditions.append(f"{agent_field} = %s")
                        params.append(agent_id)
                        print(f"Added agent filter: {agent_field} = {agent_id} for field '{field}'")
            
            # Add date filters if period is provided
            if period and isinstance(period, dict):
                start_date = period.get("start_date")
                end_date = period.get("end_date")
                if start_date and end_date:
                    # Special handling for sales target tables (use month/year instead of dates)
                    if base_table in ["crmf_agent_sales_targets", "crmf_team_sales_targets"]:
                        # Extract month and year from the period
                        try:
                            from datetime import datetime
                            if isinstance(start_date, str):
                                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                            else:
                                start_dt = start_date
                            
                            if isinstance(end_date, str):
                                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                            else:
                                end_dt = end_date
                            
                            period_start_month = start_dt.month
                            period_start_year = start_dt.year
                            period_end_month = end_dt.month
                            period_end_year = end_dt.year
                            
                            # If period spans multiple months, we need to handle it
                            if period_start_year == period_end_year and period_start_month == period_end_month:
                                # Single month period
                                where_conditions.append(f"{base_table}.month = %s")
                                where_conditions.append(f"{base_table}.year = %s")
                                params.extend([period_start_month, period_start_year])
                                print(f"Added sales target filter: month={period_start_month}, year={period_start_year}")
                            else:
                                # Multi-month period - find targets in any month within the period
                                where_conditions.append(
                                    f"({base_table}.year > %s OR ({base_table}.year = %s AND {base_table}.month >= %s))"
                                )
                                where_conditions.append(
                                    f"({base_table}.year < %s OR ({base_table}.year = %s AND {base_table}.month <= %s))"
                                )
                                params.extend([
                                    period_start_year, period_start_year, period_start_month,
                                    period_end_year, period_end_year, period_end_month
                                ])
                                print(f"Added sales target range filter: from {period_start_year}-{period_start_month} to {period_end_year}-{period_end_month}")
                        except Exception as date_error:
                            print(f"Error parsing dates for sales target filter: {date_error}")
                    else:
                        # Regular date-based filtering for other tables
                        date_fields = ["created_at", "updated_at", "policy_effective_date", "invoice_date"]
                        date_field_found = False
                        
                        for date_field in date_fields:
                            if date_field in registry.get("filters", []):
                                # Determine which table contains this date field
                                date_table = base_table
                                
                                # policy_effective_date is in crmp_issued_policies
                                if date_field == "policy_effective_date":
                                    if "crmp_issued_policies" in [join.get("table") for join in joins]:
                                        date_table = "crmp_issued_policies"
                                    elif base_table == "crmp_issued_policies":
                                        date_table = "crmp_issued_policies"
                                
                                # invoice_date is in crmf_invoices
                                elif date_field == "invoice_date":
                                    if "crmf_invoices" in [join.get("table") for join in joins]:
                                        date_table = "crmf_invoices"
                                    elif base_table == "crmf_invoices":
                                        date_table = "crmf_invoices"
                                
                                # created_at and updated_at are typically in the base table
                                # but check if they exist in joined tables too
                                elif date_field in ["created_at", "updated_at"]:
                                    # Try to find in joined tables first
                                    if date_field == "created_at":
                                        # Check common tables that have created_at
                                        for join in joins:
                                            join_table = join.get("table")
                                            if join_table in ["crmp_issued_policies", "crmp_policy_base", "crmf_invoices"]:
                                                date_table = join_table
                                                break
                                
                                where_conditions.append(f"{date_table}.{date_field} >= %s")
                                where_conditions.append(f"{date_table}.{date_field} <= %s")
                                params.extend([start_date, end_date])
                                date_field_found = True
                                print(f"Added date filter: {date_table}.{date_field} between {start_date} and {end_date}")
                                break
                        
                        # Fallback: If no date field found in filters, try to use date fields from joined tables
                        if not date_field_found:
                            joined_tables = [join.get("table") for join in joins]
                            
                            # For commission-based fields (crmf_brokerage_commission, crmf_agent_commission), prefer invoice_date
                            if base_table in ["crmf_brokerage_commission", "crmf_agent_commission"] and "crmf_invoices" in joined_tables:
                                where_conditions.append("crmf_invoices.invoice_date >= %s")
                                where_conditions.append("crmf_invoices.invoice_date <= %s")
                                params.extend([start_date, end_date])
                                date_field_found = True
                                print(f"Added fallback date filter: crmf_invoices.invoice_date between {start_date} and {end_date}")
                            # For policy-based fields, prefer policy_effective_date
                            elif "crmp_issued_policies" in joined_tables:
                                where_conditions.append("crmp_issued_policies.policy_effective_date >= %s")
                                where_conditions.append("crmp_issued_policies.policy_effective_date <= %s")
                                params.extend([start_date, end_date])
                                date_field_found = True
                                print(f"Added fallback date filter: crmp_issued_policies.policy_effective_date between {start_date} and {end_date}")
                            # For commission tables with both joins, prefer invoice_date (when commission was recognized)
                            # NOTE: For commission calculations, invoice_date is used because commission is recognized when invoice is created
                            # However, if policy_effective_date is in filters, it will be used instead (checked earlier in the code)
                            elif "crmf_invoices" in joined_tables and "crmp_issued_policies" in joined_tables:
                                # Check if policy_effective_date is in filters - if so, use it; otherwise use invoice_date
                                if "policy_effective_date" in registry.get("filters", []):
                                    where_conditions.append("crmp_issued_policies.policy_effective_date >= %s")
                                    where_conditions.append("crmp_issued_policies.policy_effective_date <= %s")
                                    params.extend([start_date, end_date])
                                    date_field_found = True
                                    print(f"Added fallback date filter via joins: crmp_issued_policies.policy_effective_date between {start_date} and {end_date}")
                                else:
                                    # Default to invoice_date for commission recognition
                                    where_conditions.append("crmf_invoices.invoice_date >= %s")
                                    where_conditions.append("crmf_invoices.invoice_date <= %s")
                                    params.extend([start_date, end_date])
                                    date_field_found = True
                                    print(f"Added fallback date filter via joins: crmf_invoices.invoice_date between {start_date} and {end_date}")
                            
                            if not date_field_found:
                                print(f"Warning: No suitable date field found for {base_table}, skipping date filter")
            
            # Apply filter conditions from performance_fields (insurer, risk_type, product, etc.)
            # These should filter the data during aggregation, not be checked after
            filter_fields = {"role", "role_id", "agent_id", "product", "insurer", "risk_type", "native_product", "product_id"}
            
            # Track if product filter is being applied (for warning about sales targets)
            has_product_filter_in_conditions = False
            product_filter_value = None
            
            if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                filter_definitions = registry.get("filter_definitions", [])
                # Create a mapping of filter field names to their database column names
                filter_column_map = {}
                for filter_def in filter_definitions:
                    filter_field = filter_def.get("field")
                    if filter_field:
                        # Map filter field to database column
                        # Most filters map directly: insurer -> insurer_id, risk_type -> risk_type_id, etc.
                        if filter_field == "insurer":
                            filter_column_map["insurer"] = "insurer_id"
                        elif filter_field == "risk_type":
                            filter_column_map["risk_type"] = "risk_type_id"
                        elif filter_field == "product":
                            filter_column_map["product"] = "product_id"
                        elif filter_field == "native_product":
                            filter_column_map["native_product"] = "product_id"  # native_product uses product_id
                        elif filter_field == "product_id":
                            filter_column_map["product_id"] = "product_id"
                
                for condition in performance_fields["conditions"]:
                    if isinstance(condition, dict):
                        # Skip nested logic structures (they don't have a 'field' key)
                        # Nested conditions are evaluated during condition evaluation, not during aggregation filtering
                        if "logic" in condition and "conditions" in condition:
                            continue
                        
                        cond_field = condition.get("field")
                        cond_operator = condition.get("operator")
                        cond_value = condition.get("value")
                        
                        # Skip if cond_field is None (shouldn't happen after the nested check, but be safe)
                        if cond_field is None:
                            continue
                        
                        # Check if this condition field matches the current field being aggregated
                        # If it's the same field, we don't need to apply it as a filter (it's being aggregated)
                        is_same_field = (cond_field == field)
                        
                        # Track product filter for warning
                        if cond_field in ["product", "product_id", "native_product"]:
                            has_product_filter_in_conditions = True
                            product_filter_value = cond_value
                        
                        # Apply filter fields (not aggregatable fields) as WHERE clauses
                        # Also apply aggregatable field conditions as filters when aggregating OTHER fields
                        # This ensures that all aggregations use the same filter criteria
                        if cond_field in filter_fields and cond_field != "role" and cond_field != "role_id" and cond_field != "agent_id":
                            # Get the database column name for this filter
                            db_column = filter_column_map.get(cond_field)
                            if db_column:
                                # Determine which table has this column (could be base_table or joined table)
                                # Check if it's in policy_base (most common)
                                filter_table = None
                                if "crmp_policy_base" in [join.get("table") for join in joins] or base_table == "crmp_policy_base":
                                    filter_table = "crmp_policy_base"
                                elif base_table == "crmp_issued_policies":
                                    # For issued_policies, check if policy_base is joined
                                    if "crmp_policy_base" in [join.get("table") for join in joins]:
                                        filter_table = "crmp_policy_base"
                                    else:
                                        filter_table = base_table
                                elif base_table == "crmf_brokerage_commission":
                                    # For brokerage commission, need to go through joins
                                    if "crmp_policy_base" in [join.get("table") for join in joins]:
                                        filter_table = "crmp_policy_base"
                                    else:
                                        filter_table = base_table
                                else:
                                    filter_table = base_table
                                
                                if filter_table:
                                    if cond_operator == "=":
                                        where_conditions.append(f"{filter_table}.{db_column} = %s")
                                        params.append(cond_value)
                                    elif cond_operator == "in":
                                        if isinstance(cond_value, list):
                                            placeholders = ",".join(["%s"] * len(cond_value))
                                            where_conditions.append(f"{filter_table}.{db_column} IN ({placeholders})")
                                            params.extend(cond_value)
                                        else:
                                            where_conditions.append(f"{filter_table}.{db_column} = %s")
                                            params.append(cond_value)
                                    elif cond_operator == "not in":
                                        if isinstance(cond_value, list):
                                            placeholders = ",".join(["%s"] * len(cond_value))
                                            where_conditions.append(f"{filter_table}.{db_column} NOT IN ({placeholders})")
                                            params.extend(cond_value)
                                        else:
                                            where_conditions.append(f"{filter_table}.{db_column} != %s")
                                            params.append(cond_value)
                                    print(f"Applied filter condition: {cond_field} ({filter_table}.{db_column} {cond_operator} {cond_value})")
                        
                        # CRITICAL FIX: Do NOT apply aggregatable field conditions as SQL WHERE filters
                        # Aggregatable conditions (like sum_of_x >= value, premium_amount < 10) must be evaluated
                        # AFTER aggregation in Python, not as SQL row filters.
                        # 
                        # WRONG: SUM(premium_amount WHERE premium_amount < 10) - filters rows before aggregation
                        # CORRECT: total = SUM(premium_amount), then IF total < 10 → condition
                        #
                        # Only filter-type conditions (product, insurer, role, date) should be applied as SQL filters.
                        # All aggregatable numeric conditions are evaluated in evaluate_conditions() after aggregation.
                        elif not is_same_field:
                            # This is an aggregatable field condition - skip SQL filtering
                            # It will be evaluated in Python after aggregation
                            print(f"⚠️ Skipping aggregatable field condition '{cond_field} {cond_operator} {cond_value}' as SQL filter")
                            print(f"  Reason: Aggregatable conditions must be evaluated AFTER aggregation, not as SQL WHERE clauses")
                            print(f"  This condition will be evaluated in Python using aggregated values")
                            continue
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
            
            sql += " LIMIT 1"
            
            # Execute query
            from django.db import connection
            with connection.cursor() as cursor:
                print(f"Executing aggregation query for field '{field}' (agent_id={agent_id}): {sql}")
                print(f"Query parameters: {params}")
                cursor.execute(sql, params)
                result = cursor.fetchone()
                
                if result:
                    # Store by field key (for lookup) and also by field_name (for backward compatibility)
                    value = result[0] if result[0] is not None else 0
                    all_performance_data[field] = value
                    all_performance_data[field_name] = value
                    print(f"Aggregated value for field '{field}' (agent_id={agent_id}): {value}")
                    
                    # CRITICAL FIX: If product filter exists and this is an achieved field, also compute overall (without product filter)
                    # This allows target comparison to use overall achieved while reward base uses product-filtered achieved
                    if has_product_filter_in_conditions and field in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
                        # Re-run query without product filter to get overall achieved
                        # Rebuild SQL from scratch without product filter
                        overall_where_conditions = []
                        overall_params = []
                        
                        # Re-add agent filter
                        if agent_field:
                            if "team_id" in agent_field.lower() or "core_teams.id" in agent_field:
                                from django.db import connection
                                with connection.cursor() as team_cursor:
                                    team_cursor.execute("SELECT DISTINCT team_id FROM core_team_users WHERE user_id = %s", [agent_id])
                                    team_results = team_cursor.fetchall()
                                    team_ids = [row[0] for row in team_results if row[0] is not None]
                                    if team_ids:
                                        placeholders = ",".join(["%s"] * len(team_ids))
                                        overall_where_conditions.append(f"{agent_field} IN ({placeholders})")
                                        overall_params.extend(team_ids)
                                    else:
                                        overall_where_conditions.append("1 = 0")
                            else:
                                is_account_manager = False
                                if field in ["sum_of_agent_achieved", "sum_of_agent_sales_target"]:
                                    try:
                                        from django.db import connection
                                        with connection.cursor() as role_cursor:
                                            role_cursor.execute("SELECT role_id FROM core_users WHERE id = %s", [agent_id])
                                            role_result = role_cursor.fetchone()
                                            if role_result and role_result[0] == 8:
                                                is_account_manager = True
                                    except Exception:
                                        pass
                                
                                if is_account_manager:
                                    sales_agent_ids = get_sales_agents_for_account_manager(agent_id)
                                    if sales_agent_ids:
                                        placeholders = ",".join(["%s"] * len(sales_agent_ids))
                                        overall_where_conditions.append(f"{agent_field} IN ({placeholders})")
                                        overall_params.extend(sales_agent_ids)
                                    else:
                                        overall_where_conditions.append("1 = 0")
                                else:
                                    overall_where_conditions.append(f"{agent_field} = %s")
                                    overall_params.append(agent_id)
                        
                        # Re-add date filters
                        if period and isinstance(period, dict):
                            start_date = period.get("start_date")
                            end_date = period.get("end_date")
                            if start_date and end_date:
                                if base_table in ["crmf_agent_sales_targets", "crmf_team_sales_targets"]:
                                    try:
                                        from datetime import datetime
                                        if isinstance(start_date, str):
                                            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                                        else:
                                            start_dt = start_date
                                        if isinstance(end_date, str):
                                            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                                        else:
                                            end_dt = end_date
                                        period_start_month = start_dt.month
                                        period_start_year = start_dt.year
                                        period_end_month = end_dt.month
                                        period_end_year = end_dt.year
                                        if period_start_year == period_end_year and period_start_month == period_end_month:
                                            overall_where_conditions.append(f"{base_table}.month = %s")
                                            overall_where_conditions.append(f"{base_table}.year = %s")
                                            overall_params.extend([period_start_month, period_start_year])
                                        else:
                                            overall_where_conditions.append(
                                                f"({base_table}.year > %s OR ({base_table}.year = %s AND {base_table}.month >= %s))"
                                            )
                                            overall_where_conditions.append(
                                                f"({base_table}.year < %s OR ({base_table}.year = %s AND {base_table}.month <= %s))"
                                            )
                                            overall_params.extend([
                                                period_start_year, period_start_year, period_start_month,
                                                period_end_year, period_end_year, period_end_month
                                            ])
                                    except Exception:
                                        pass
                                else:
                                    date_fields = ["created_at", "updated_at", "policy_effective_date", "invoice_date"]
                                    date_field_found = False
                                    for date_field in date_fields:
                                        if date_field in registry.get("filters", []):
                                            date_table = base_table
                                            if date_field == "policy_effective_date":
                                                if "crmp_issued_policies" in [join.get("table") for join in joins]:
                                                    date_table = "crmp_issued_policies"
                                                elif base_table == "crmp_issued_policies":
                                                    date_table = "crmp_issued_policies"
                                            elif date_field == "invoice_date":
                                                if "crmf_invoices" in [join.get("table") for join in joins]:
                                                    date_table = "crmf_invoices"
                                                elif base_table == "crmf_invoices":
                                                    date_table = "crmf_invoices"
                                            
                                            overall_where_conditions.append(f"{date_table}.{date_field} >= %s")
                                            overall_where_conditions.append(f"{date_table}.{date_field} <= %s")
                                            overall_params.extend([start_date, end_date])
                                            date_field_found = True
                                            break
                                    
                                    if not date_field_found:
                                        joined_tables = [join.get("table") for join in joins]
                                        if base_table in ["crmf_brokerage_commission", "crmf_agent_commission"] and "crmf_invoices" in joined_tables:
                                            overall_where_conditions.append("crmf_invoices.invoice_date >= %s")
                                            overall_where_conditions.append("crmf_invoices.invoice_date <= %s")
                                            overall_params.extend([start_date, end_date])
                                        elif "crmp_issued_policies" in joined_tables:
                                            overall_where_conditions.append("crmp_issued_policies.policy_effective_date >= %s")
                                            overall_where_conditions.append("crmp_issued_policies.policy_effective_date <= %s")
                                            overall_params.extend([start_date, end_date])
                        
                        # Re-add other filters (insurer, risk_type, etc.) but NOT product filter
                        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                            filter_definitions = registry.get("filter_definitions", [])
                            filter_column_map = {}
                            for filter_def in filter_definitions:
                                filter_field = filter_def.get("field")
                                if filter_field:
                                    if filter_field == "insurer":
                                        filter_column_map["insurer"] = "insurer_id"
                                    elif filter_field == "risk_type":
                                        filter_column_map["risk_type"] = "risk_type_id"
                            
                            for condition in performance_fields["conditions"]:
                                if isinstance(condition, dict):
                                    if "logic" in condition and "conditions" in condition:
                                        continue
                                    
                                    cond_field = condition.get("field")
                                    cond_operator = condition.get("operator")
                                    cond_value = condition.get("value")
                                    
                                    if cond_field is None:
                                        continue
                                    
                                    # Skip product filter - we want overall achieved
                                    if cond_field in ["product", "product_id", "native_product"]:
                                        continue
                                    
                                    # Apply other filters (insurer, risk_type, etc.)
                                    if cond_field in filter_column_map and cond_field not in ["role", "role_id", "agent_id", "team_role"]:
                                        db_column = filter_column_map.get(cond_field)
                                        if db_column:
                                            filter_table = None
                                            if "crmp_policy_base" in [join.get("table") for join in joins] or base_table == "crmp_policy_base":
                                                filter_table = "crmp_policy_base"
                                            elif base_table == "crmp_issued_policies":
                                                if "crmp_policy_base" in [join.get("table") for join in joins]:
                                                    filter_table = "crmp_policy_base"
                                                else:
                                                    filter_table = base_table
                                            elif base_table == "crmf_brokerage_commission":
                                                if "crmp_policy_base" in [join.get("table") for join in joins]:
                                                    filter_table = "crmp_policy_base"
                                                else:
                                                    filter_table = base_table
                                            else:
                                                filter_table = base_table
                                            
                                            if filter_table:
                                                if cond_operator == "=":
                                                    overall_where_conditions.append(f"{filter_table}.{db_column} = %s")
                                                    overall_params.append(cond_value)
                                                elif cond_operator == "in":
                                                    if isinstance(cond_value, list):
                                                        placeholders = ",".join(["%s"] * len(cond_value))
                                                        overall_where_conditions.append(f"{filter_table}.{db_column} IN ({placeholders})")
                                                        overall_params.extend(cond_value)
                                                elif cond_operator == "not in":
                                                    if isinstance(cond_value, list):
                                                        placeholders = ",".join(["%s"] * len(cond_value))
                                                        overall_where_conditions.append(f"{filter_table}.{db_column} NOT IN ({placeholders})")
                                                        overall_params.extend(cond_value)
                        
                        # Build overall SQL query (same structure as original but without product filter)
                        overall_select_clause = select_clause  # Reuse the same select clause
                        overall_sql = f"SELECT {overall_select_clause} FROM {base_table}"
                        for join in joins:
                            overall_sql += f" JOIN {join['table']} ON {join['on']}"
                        if overall_where_conditions:
                            overall_sql += " WHERE " + " AND ".join(overall_where_conditions)
                        overall_sql += " LIMIT 1"
                        
                        # Execute overall query
                        with connection.cursor() as overall_cursor:
                            print(f"Executing overall aggregation query (without product filter) for field '{field}' (agent_id={agent_id}): {overall_sql}")
                            print(f"Overall query parameters: {overall_params}")
                            overall_cursor.execute(overall_sql, overall_params)
                            overall_result = overall_cursor.fetchone()
                            
                            if overall_result:
                                overall_value = overall_result[0] if overall_result[0] is not None else 0
                                overall_field_key = field + "_overall"
                                all_performance_data[overall_field_key] = overall_value
                                print(f"Aggregated overall value (without product filter) for field '{field}' (agent_id={agent_id}): {overall_value}")
                                print(f"  Product-filtered value: {value}")
                                print(f"  Overall value (for target comparison): {overall_value}")
                    
                    # Validate that agent_id filter was applied correctly
                    if agent_field and "agent_id" in str(agent_field).lower():
                        print(f"  Verified: Query filtered by {agent_field} = {agent_id}")
                    # Warn if product filter is applied but this field doesn't support product filtering
                    if has_product_filter_in_conditions and field == "sum_of_agent_sales_target":
                        print(f"  WARNING: Product filter (product={product_filter_value}) is active, but sales targets are NOT product-specific.")
                        print(f"  This field cannot be filtered by product. The target value represents general target, not product-specific target.")
                        print(f"  If you need product-specific achievement calculation, ensure targets are also product-specific in the database.")
                else:
                    # No result - set to 0 for numeric fields
                    all_performance_data[field] = 0
                    all_performance_data[field_name] = 0
                    print(f"No result for field '{field}' (agent_id={agent_id}), defaulting to 0")
                    print(f"  SQL query was: {sql}")
                    print(f"  Query parameters: {params}")
        
        print(f"Final performance_data for agent_id={agent_id}: {all_performance_data}")
        # Validate that all required fields are present (especially for target-based conditions)
        # NOTE: Filter fields (role, team_role, product, etc.) are NOT expected in performance_data
        # They are evaluated separately from database lookups, not from aggregated performance data
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            required_fields, _ = extract_fields_from_conditions(performance_fields["conditions"])
            # Filter out non-aggregatable fields - these are not expected in performance_data
            NON_AGGREGATABLE_FIELDS = {
                "product", "native_product", "product_id",
                "team_role", "role", "role_id", "user_role",
                "agent_id", "insurer", "risk_type"
            }
            # Only check for aggregatable fields
            aggregatable_required_fields = [f for f in required_fields if f not in NON_AGGREGATABLE_FIELDS]
            missing_fields = [f for f in aggregatable_required_fields if f not in all_performance_data]
            if missing_fields:
                print(f"WARNING: Missing required aggregatable fields in performance_data for agent_id={agent_id}: {missing_fields}")
                print(f"  This may cause condition evaluation to fail. Check if these fields are being aggregated correctly.")
                print(f"  Note: Filter fields (role, team_role, product, etc.) are evaluated separately and not expected in performance_data")
        return all_performance_data
    except Exception as e:
        print(f"Error aggregating performance data: {e}")
        return {}

def aggregate_performance_data_bulk(agent_ids, incentive_setup, period=None):
    """
    Bulk aggregate performance data for multiple agents in one query per field.
    This replaces N+1 queries with bulk GROUP BY queries for better performance.
    
    Returns:
        dict: {agent_id: {field: value, ...}, ...}
    """
    try:
        if not agent_ids:
            return {}
        
        performance_fields = incentive_setup.get("performance_fields", {})
        if isinstance(performance_fields, str):
            performance_fields = json.loads(performance_fields)
        
        # Extract fields from the logic tree
        fields = []
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            fields, _ = extract_fields_from_conditions(performance_fields["conditions"])
        
        # Check for achievement_percentage fields
        has_achievement_percentage = False
        has_percentage_type_on_achieved = False
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            def check_for_achievement_percentage(conditions):
                nonlocal has_achievement_percentage, has_percentage_type_on_achieved
                for condition in conditions:
                    if isinstance(condition, dict):
                        if condition.get("field") in ["achievement_percentage", "achievement_percent"]:
                            has_achievement_percentage = True
                        if condition.get("type") == "percentage" and condition.get("field") in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
                            has_percentage_type_on_achieved = True
                        if "conditions" in condition:
                            check_for_achievement_percentage(condition.get("conditions", []))
            check_for_achievement_percentage(performance_fields["conditions"])
        
        if has_achievement_percentage or has_percentage_type_on_achieved:
            if "sum_of_agent_achieved" not in fields:
                fields.append("sum_of_agent_achieved")
            if "sum_of_agent_sales_target" not in fields:
                fields.append("sum_of_agent_sales_target")
        
        # Include incentive_base_field
        incentive_base_field = incentive_setup.get("incentive_base_field")
        reward_type_id = incentive_setup.get("reward_type_id", 1)
        is_percentage = (reward_type_id == 2)
        
        if incentive_base_field and incentive_base_field not in fields:
            fields.append(incentive_base_field)
        
        if not fields:
            # Return empty dict for each agent
            return {agent_id: {} for agent_id in agent_ids}
        
        # Initialize result structure
        result = {agent_id: {} for agent_id in agent_ids}
        
        # CRITICAL FIX: Filter-only fields should NEVER be aggregated
        # These fields are used in WHERE clauses only, not in SELECT/GROUP BY
        # Attempting to aggregate them causes SQL GROUP BY errors (ONLY_FULL_GROUP_BY)
        NON_AGGREGATABLE_FIELDS = {
            "product",
            "native_product",
            "product_id",
            "team_role",
            "role",
            "role_id",
            "user_role",
            "agent_id",
            "insurer",
            "risk_type"
        }
        
        # Filter out non-aggregatable fields before processing
        aggregatable_fields = [f for f in fields if f not in NON_AGGREGATABLE_FIELDS]
        
        if not aggregatable_fields:
            # Only filter fields, no aggregatable metrics - return empty results
            print(f"⚠️  WARNING: Only filter fields found in conditions, no aggregatable metrics. Fields: {fields}")
            return {agent_id: {} for agent_id in agent_ids}
        
        # Get registry for each field
        from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
        
        # Detect team_role = "team lead" so we aggregate commission by recipient (agent_id) not by policy seller (sales_agent_id)
        has_team_lead_condition = False
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            for cond in performance_fields.get("conditions", []):
                if isinstance(cond, dict) and cond.get("field") == "team_role":
                    val = cond.get("value")
                    if val is not None and str(val).lower().strip() in ["team lead", "team_lead", "manager", "lead"]:
                        has_team_lead_condition = True
                        break
        
        for field in aggregatable_fields:
            registry = None
            for reg in PERFORMANCE_FIELD_REGISTRY:
                if reg.get("parameter") == field or field in reg.get("field", []):
                    registry = reg
                    break
            
            if not registry:
                continue
            
            base_table = registry["base_table"]
            agent_field = registry.get("agent_field")
            field_name = registry["field"][0] if registry["field"] else "id"
            agg_type = registry.get("agg", "sum")
            joins = registry.get("joins", [])
            
            # When team_role = "team lead": for agent commission fields, use commission RECIPIENT (agent_id)
            # so team leads get reward on commission they receive (including override), not just policies they sold.
            # Example: Team lead receives 12,000 from product 31 (override + direct). Reward 10%.
            #   Without override: we would sum by sales_agent_id => 0 (they didn't sell). Wrong.
            #   With override: we sum by agent_id => 12,000. Incentive = (12,000 * 10) / 100 = 1,200.00.
            if has_team_lead_condition and base_table == "crmf_agent_commission" and agent_field:
                agent_field = "crmf_agent_commission.agent_id"
            
            # Build bulk SQL query with GROUP BY
            if agg_type == "sum":
                select_clause = f"{agent_field} as agent_id, COALESCE(SUM({base_table}.{field_name}), 0) as {field_name}"
            elif agg_type == "count":
                select_clause = f"{agent_field} as agent_id, COUNT({base_table}.{field_name}) as {field_name}"
            else:
                select_clause = f"{agent_field} as agent_id, {base_table}.{field_name}"
            
            sql = f"SELECT {select_clause} FROM {base_table}"
            
            # Add joins
            for join in joins:
                sql += f" JOIN {join['table']} ON {join['on']}"
            
            # Build WHERE clause
            where_conditions = []
            params = []
            
            if agent_field:
                # Filter by agent_ids
                if "team_id" in agent_field.lower() or "core_teams.id" in agent_field:
                    # For team-based fields, get team_ids for all agents
                    from django.db import connection
                    with connection.cursor() as team_cursor:
                        placeholders = ",".join(["%s"] * len(agent_ids))
                        team_cursor.execute(
                            f"SELECT DISTINCT user_id, team_id FROM core_team_users WHERE user_id IN ({placeholders})",
                            agent_ids
                        )
                        team_results = team_cursor.fetchall()
                        # Map agent_id -> team_ids
                        agent_team_map = {}
                        for user_id, team_id in team_results:
                            if user_id not in agent_team_map:
                                agent_team_map[user_id] = []
                            if team_id:
                                agent_team_map[user_id].append(team_id)
                        
                        # Get all unique team_ids
                        all_team_ids = set()
                        for team_ids in agent_team_map.values():
                            all_team_ids.update(team_ids)
                        
                        if all_team_ids:
                            placeholders = ",".join(["%s"] * len(all_team_ids))
                            where_conditions.append(f"{agent_field} IN ({placeholders})")
                            params.extend(list(all_team_ids))
                        else:
                            # No teams found, return 0 for all
                            for agent_id in agent_ids:
                                result[agent_id][field] = 0
                                result[agent_id][field_name] = 0
                            continue
                else:
                    # Regular agent-based field - filter by agent_ids
                    placeholders = ",".join(["%s"] * len(agent_ids))
                    where_conditions.append(f"{agent_field} IN ({placeholders})")
                    params.extend(agent_ids)
            
            # Add date filters if period is provided
            if period and isinstance(period, dict):
                start_date = period.get("start_date")
                end_date = period.get("end_date")
                if start_date and end_date:
                    if base_table in ["crmf_agent_sales_targets", "crmf_team_sales_targets"]:
                        # Handle sales target tables with month/year
                        try:
                            from datetime import datetime
                            if isinstance(start_date, str):
                                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                            else:
                                start_dt = start_date
                            if isinstance(end_date, str):
                                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                            else:
                                end_dt = end_date
                            
                            period_start_month = start_dt.month
                            period_start_year = start_dt.year
                            period_end_month = end_dt.month
                            period_end_year = end_dt.year
                            
                            if period_start_year == period_end_year and period_start_month == period_end_month:
                                where_conditions.append(f"{base_table}.month = %s")
                                where_conditions.append(f"{base_table}.year = %s")
                                params.extend([period_start_month, period_start_year])
                            else:
                                where_conditions.append(
                                    f"({base_table}.year > %s OR ({base_table}.year = %s AND {base_table}.month >= %s))"
                                )
                                where_conditions.append(
                                    f"({base_table}.year < %s OR ({base_table}.year = %s AND {base_table}.month <= %s))"
                                )
                                params.extend([
                                    period_start_year, period_start_year, period_start_month,
                                    period_end_year, period_end_year, period_end_month
                                ])
                        except Exception as date_error:
                            print(f"Error parsing dates for sales target filter: {date_error}")
                    else:
                        # Regular date-based filtering
                        date_fields = ["created_at", "updated_at", "policy_effective_date", "invoice_date"]
                        date_field_found = False
                        
                        for date_field in date_fields:
                            if date_field in registry.get("filters", []):
                                date_table = base_table
                                if date_field == "policy_effective_date":
                                    if "crmp_issued_policies" in [join.get("table") for join in joins]:
                                        date_table = "crmp_issued_policies"
                                    elif base_table == "crmp_issued_policies":
                                        date_table = "crmp_issued_policies"
                                elif date_field == "invoice_date":
                                    if "crmf_invoices" in [join.get("table") for join in joins]:
                                        date_table = "crmf_invoices"
                                    elif base_table == "crmf_invoices":
                                        date_table = "crmf_invoices"
                                
                                where_conditions.append(f"{date_table}.{date_field} >= %s")
                                where_conditions.append(f"{date_table}.{date_field} <= %s")
                                params.extend([start_date, end_date])
                                date_field_found = True
                                break
                        
                        if not date_field_found:
                            # Fallback to common date fields
                            joined_tables = [join.get("table") for join in joins]
                            if "crmf_invoices" in joined_tables:
                                where_conditions.append("crmf_invoices.invoice_date >= %s")
                                where_conditions.append("crmf_invoices.invoice_date <= %s")
                                params.extend([start_date, end_date])
                            elif "crmp_issued_policies" in joined_tables:
                                where_conditions.append("crmp_issued_policies.policy_effective_date >= %s")
                                where_conditions.append("crmp_issued_policies.policy_effective_date <= %s")
                                params.extend([start_date, end_date])
            
            # Apply filter conditions (insurer, risk_type, product, etc.)
            filter_fields = {"role", "role_id", "agent_id", "product", "insurer", "risk_type", "native_product", "product_id"}
            
            if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                filter_definitions = registry.get("filter_definitions", [])
                filter_column_map = {}
                for filter_def in filter_definitions:
                    filter_field = filter_def.get("field")
                    if filter_field == "insurer":
                        filter_column_map["insurer"] = "insurer_id"
                    elif filter_field == "risk_type":
                        filter_column_map["risk_type"] = "risk_type_id"
                    elif filter_field == "product":
                        filter_column_map["product"] = "product_id"
                    elif filter_field == "native_product":
                        filter_column_map["native_product"] = "product_id"
                    elif filter_field == "product_id":
                        filter_column_map["product_id"] = "product_id"
                
                for condition in performance_fields["conditions"]:
                    if isinstance(condition, dict) and "logic" not in condition:
                        cond_field = condition.get("field")
                        cond_operator = condition.get("operator")
                        cond_value = condition.get("value")
                        
                        if cond_field in filter_fields and cond_field not in ["role", "role_id", "agent_id"]:
                            db_column = filter_column_map.get(cond_field)
                            if db_column:
                                filter_table = None
                                if "crmp_policy_base" in [join.get("table") for join in joins] or base_table == "crmp_policy_base":
                                    filter_table = "crmp_policy_base"
                                elif base_table == "crmp_issued_policies":
                                    if "crmp_policy_base" in [join.get("table") for join in joins]:
                                        filter_table = "crmp_policy_base"
                                    else:
                                        filter_table = base_table
                                else:
                                    filter_table = base_table
                                
                                if filter_table:
                                    if cond_operator == "=":
                                        where_conditions.append(f"{filter_table}.{db_column} = %s")
                                        params.append(cond_value)
                                    elif cond_operator == "in":
                                        if isinstance(cond_value, list):
                                            placeholders = ",".join(["%s"] * len(cond_value))
                                            where_conditions.append(f"{filter_table}.{db_column} IN ({placeholders})")
                                            params.extend(cond_value)
            
            if where_conditions:
                sql += " WHERE " + " AND ".join(where_conditions)
            
            # Add GROUP BY
            sql += f" GROUP BY {agent_field}"
            
            # Execute bulk query
            from django.db import connection
            with connection.cursor() as cursor:
                print(f"Executing bulk aggregation query for field '{field}' for {len(agent_ids)} agents")
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                
                # Map results to agent_ids
                for row in rows:
                    agent_id = row[0]
                    value = row[1] if row[1] is not None else 0
                    if agent_id in result:
                        result[agent_id][field] = value
                        result[agent_id][field_name] = value
                
                # Set 0 for agents with no results
                for agent_id in agent_ids:
                    if field not in result[agent_id]:
                        result[agent_id][field] = 0
                        result[agent_id][field_name] = 0
        
        print(f"Bulk aggregation completed for {len(agent_ids)} agents")
        return result
    except Exception as e:
        print(f"Error in bulk aggregation: {e}")
        import traceback
        traceback.print_exc()
        # Fallback: return empty dict for each agent
        return {agent_id: {} for agent_id in agent_ids}

def evaluate_single_condition(condition, performance_data, agent_id=None, filter_fields=None):
    """
    Evaluate a single condition (can be nested) and return True/False.
    
    Args:
        condition: A condition dict (can be nested with 'logic' and 'conditions')
        performance_data: Dictionary of performance metrics
        agent_id: Agent ID for filter field checks
        filter_fields: Set of filter-only field names
    
    Returns:
        bool: True if condition is met, False otherwise
    """
    if not isinstance(condition, dict):
        return False
    
    # Check if this is a nested logic structure
    if "logic" in condition and "conditions" in condition:
        nested_logic = condition.get("logic", "AND").upper()
        nested_conditions = condition.get("conditions", [])
        
        # Recursively evaluate nested conditions
        nested_results = []
        for nested_condition in nested_conditions:
            nested_result = evaluate_single_condition(nested_condition, performance_data, agent_id, filter_fields)
            nested_results.append(nested_result)
        
        # Evaluate nested results based on nested logic
        if nested_logic == "OR":
            return any(nested_results) if nested_results else False
        else:
            return all(nested_results) if nested_results else False
    
    # Regular condition evaluation
    field = condition.get("field")
    operator = condition.get("operator")
    value = condition.get("value")
    condition_type = condition.get("type", "").lower().strip() if condition.get("type") else ""
    
    if not field:
        return False
    
    if filter_fields is None:
        filter_fields = {"role", "role_id", "agent_id", "product", "insurer", "risk_type", "native_product", "product_id"}
    
    # Handle filter fields
    if field in filter_fields:
        if field in ("role", "role_id"):
            if agent_id is None:
                return False
            try:
                from django.db import connection
                with connection.cursor() as cursor:
                    cursor.execute("SELECT role_id FROM core_users WHERE id = %s", [agent_id])
                    result = cursor.fetchone()
                    if result:
                        agent_role_id = result[0]
                        if isinstance(value, str):
                            try:
                                comparison_value = int(value)
                            except ValueError:
                                return False
                        elif isinstance(value, (int, float)):
                            comparison_value = int(value)
                        else:
                            return False
                        return evaluate_condition(agent_role_id, operator, comparison_value)
                    return False
            except Exception:
                return False
        elif field == "agent_id":
            if agent_id is None:
                return False
            comparison_value = int(value) if value is not None else None
            return evaluate_condition(agent_id, operator, comparison_value)
        else:
            # Other filter fields are already applied during aggregation
            return True
    
    # Find registry for aggregatable fields
    from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
    registry = None
    for reg in PERFORMANCE_FIELD_REGISTRY:
        if reg.get("parameter") == field or field in reg.get("field", []):
            registry = reg
            break
    
    if not registry:
        return False
    
    # Get performance value
    actual_field_name = registry["field"][0] if registry["field"] else "id"
    if field in performance_data:
        performance_value = performance_data[field]
    elif actual_field_name in performance_data:
        performance_value = performance_data[actual_field_name]
    else:
        performance_value = None
    
    # Handle None values
    if performance_value is None:
        if registry.get("agg") in ["sum", "count"]:
            performance_value = 0
        else:
            return False
    
    # Resolve value (field reference or direct value)
    comparison_value = value
    if is_field_reference(value):
        value_registry = None
        for reg in PERFORMANCE_FIELD_REGISTRY:
            if reg.get("parameter") == value or value in reg.get("field", []):
                value_registry = reg
                break
        
        if value_registry:
            value_field_name = value_registry["field"][0] if value_registry["field"] else "id"
            if value in performance_data:
                comparison_value = performance_data[value]
            elif value_field_name in performance_data:
                comparison_value = performance_data[value_field_name]
            else:
                return False
        else:
            return False
    elif condition_type == "percentage":
        try:
            percentage_value = float(value) if value else 0
            # Special handling for achievement fields - use target as base
            if field in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
                target_field = "sum_of_agent_sales_target" if field == "sum_of_agent_achieved" else "sum_of_team_sales_target"
                target_value = performance_data.get(target_field, 0)
                if target_value and float(target_value) > 0:
                    base_value = float(target_value)
                    comparison_value = (base_value * percentage_value) / 100.0
                else:
                    return False
            else:
                base_value = float(performance_value)
                comparison_value = (base_value * percentage_value) / 100.0
        except (ValueError, TypeError):
            return False
    else:
        try:
            if isinstance(value, str):
                comparison_value = float(value)
            elif isinstance(value, (int, float)):
                comparison_value = float(value)
            else:
                return False
        except (ValueError, TypeError):
            return False
    
    # Convert performance_value to float
    try:
        if hasattr(performance_value, '__float__'):
            performance_value = float(performance_value)
        elif isinstance(performance_value, (int, float)):
            performance_value = float(performance_value)
        else:
            return False
    except (ValueError, TypeError):
        return False
    
    return evaluate_condition(performance_value, operator, comparison_value)

def calculate_incentive_reward(incentive_setup, performance_data, agent_id=None):
    """Calculate incentive reward based on performance data."""
    try:
        performance_fields = incentive_setup.get("performance_fields", {})
        if isinstance(performance_fields, str):
            performance_fields = json.loads(performance_fields)
        
        reward_type_value = incentive_setup.get("reward_type_value", 0)
        
        # Get registry to map field names
        from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
        
        # Check if conditions are met (supports both AND and OR logic)
        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
            # CRITICAL: Use the hardened evaluator from evaluate_incentive_logic.py
            # This ensures zero-target protection and all financial safety checks are applied
            from envoy_bu_policy_api.finance.controllers.utils.evaluate_incentive_logic import evaluate_conditions
            
            # Get the logic type (default to AND if not specified)
            logic = performance_fields.get("logic", "AND").upper()
            print(f"=== Starting condition evaluation (HARDENED EVALUATOR) ===")
            print(f"Logic type: {logic}")
            print(f"Number of conditions: {len(performance_fields.get('conditions', []))}")
            print(f"Performance data keys: {list(performance_data.keys())}")
            print(f"Agent ID: {agent_id}")
            
            # CRITICAL: Use the hardened evaluator - it handles all conditions including nested logic
            # This ensures zero-target protection and all financial safety checks are applied
            # The hardened evaluator replaces the old inline evaluation logic
            all_conditions_met = evaluate_conditions(performance_fields, performance_data, agent_id)
            
            print(f"=== Condition evaluation result (HARDENED EVALUATOR): {all_conditions_met} ===")
            
            # Skip all the old inline evaluation logic and jump directly to reward calculation
            # The hardened evaluator has already done all the condition checking
            if all_conditions_met:
                # Jump to reward calculation section (around line 2778)
                pass
            else:
                return {
                    "eligible": False,
                    "reward_amount": 0,
                    "message": "Conditions not met"
                }
            
            # OLD INLINE EVALUATION CODE REMOVED - Now using hardened evaluator above
            # All the code below this point (lines ~2162-2777) is legacy and can be removed
            # But keeping it commented for now to preserve reward calculation logic
            
            # Define filter fields for reference (not used in hardened evaluator)
            filter_fields = {"role", "role_id", "user_role", "team_role", "agent_id", "product", "insurer", "risk_type", "native_product", "product_id"}
            
            # Skip old evaluation logic - jump to reward calculation
            # The hardened evaluator has already determined all_conditions_met
            # Now proceed directly to reward calculation (line ~2778)
            
            # OLD INLINE EVALUATION CODE SKIPPED - Using hardened evaluator instead
            # The hardened evaluator (evaluate_conditions) has already evaluated all conditions
            # Set empty condition_results to satisfy the reward calculation code below
            condition_results = []  # Not used - hardened evaluator already determined result
            role_condition_results = []  # Not used - hardened evaluator already determined result
            has_multiple_role_conditions = False  # Not used - hardened evaluator handles this
            
            # SKIP THE ENTIRE OLD EVALUATION LOOP - Jump directly to reward calculation
            # The old loop (lines ~2185-2704) is bypassed because hardened evaluator already did the work
            # We'll jump directly to the reward calculation section (around line 2778)
            # The old evaluation code below is skipped - hardened evaluator already evaluated conditions
            
            # OLD EVALUATION CODE BYPASSED - Using hardened evaluator instead
            # All the code from here to line ~2716 is the old inline evaluation logic
            # It's kept for reference but is bypassed when using hardened evaluator
            # The hardened evaluator has already evaluated all conditions above (line 2151)
            
            # Skip old evaluation loop - jump directly to reward calculation
            # The old loop below is bypassed because hardened evaluator already did the work
            _use_hardened_evaluator = True  # Using hardened evaluator
            
            if not _use_hardened_evaluator:
                # OLD EVALUATION CODE - Only executes if _use_hardened_evaluator is False
                # This is kept for backward compatibility but should not be used
                for idx, condition in enumerate(performance_fields.get("conditions", [])):
                    print(f"\n--- Processing condition {idx + 1}/{len(performance_fields['conditions'])} ---")
                    print(f"Condition: {condition}")
                    if isinstance(condition, dict):
                        # Check if this is a nested logic structure (e.g., {'logic': 'AND', 'conditions': [...]})
                        if "logic" in condition and "conditions" in condition:
                            # Use helper function to recursively evaluate nested conditions
                            condition_met = evaluate_single_condition(condition, performance_data, agent_id, filter_fields)
                        print(f"Nested condition evaluation result: {condition_met}")
                        condition_results.append(condition_met)
                        continue
                    
                    field = condition.get("field")
                    operator = condition.get("operator")
                    value = condition.get("value")
                    condition_type = condition.get("type", "").lower().strip() if condition.get("type") else ""
                    condition_met = False
                    
                    # Check if this is a filter field (not aggregatable)
                    if field in filter_fields:
                        # For role/role_id/user_role: Check core_users.role_id (user roles)
                        if field in ("role", "role_id", "user_role"):
                            if agent_id is None:
                                print(f"Agent ID not provided, cannot check filter field {field}")
                                condition_met = False
                            else:
                                try:
                                    from django.db import connection
                                    with connection.cursor() as cursor:
                                        cursor.execute("SELECT role_id FROM core_users WHERE id = %s", [agent_id])
                                        result = cursor.fetchone()
                                        if result:
                                            agent_role_id = result[0]
                                            # Convert value to int, handling both string and numeric values
                                            if isinstance(value, str):
                                                try:
                                                    comparison_value = int(value)
                                                except ValueError:
                                                    comparison_value = None
                                            elif isinstance(value, (int, float)):
                                                comparison_value = int(value)
                                            else:
                                                comparison_value = None
                                            
                                            print(f"User role check: agent_id={agent_id}, core_users.role_id={agent_role_id} (type: {type(agent_role_id)}), operator='{operator}', comparison_value={comparison_value} (type: {type(comparison_value)})")
                                            condition_met = evaluate_condition(agent_role_id, operator, comparison_value)
                                            print(f"Filter condition {field} (agent role_id={agent_role_id} {operator} {comparison_value}): {condition_met}")
                                        else:
                                            print(f"Agent {agent_id} not found in core_users")
                                            condition_met = False
                                except Exception as e:
                                    print(f"Error checking user role for agent {agent_id}: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    condition_met = False
                            
                            # If there are multiple role conditions with AND logic, track role conditions separately
                            # We'll evaluate them as OR later
                            if has_multiple_role_conditions:
                                role_condition_results.append(condition_met)
                                print(f"Role condition result stored separately (will be evaluated as OR): {condition_met}")
                                # Don't add to condition_results yet - we'll handle it after the loop
                                continue
                            else:
                                condition_results.append(condition_met)
                                continue
                        
                        # For team_role: Check team roles from core_teams.manager_id or core_team_users
                        elif field == "team_role":
                            if agent_id is None:
                                print(f"Agent ID not provided, cannot check filter field {field}")
                                condition_met = False
                            else:
                                try:
                                    from django.db import connection
                                    with connection.cursor() as cursor:
                                        # Normalize team_role value (handle string values like "team lead", "team member", etc.)
                                        team_role_type = None
                                        if isinstance(value, str):
                                            value_lower = value.lower().strip()
                                            # Map string values to team role types
                                            if value_lower in ["team lead", "team_lead", "account manager", "account_manager", "manager", "lead"]:
                                                team_role_type = "manager"  # Check manager_id in core_teams
                                            elif value_lower in ["team member", "team_member", "sales agent", "sales_agent", "member", "agent"]:
                                                team_role_type = "member"  # Check core_team_users
                                            else:
                                                # Try to parse as integer (for backward compatibility)
                                                try:
                                                    int_value = int(value)
                                                    if int_value == 8:
                                                        team_role_type = "manager"
                                                    elif int_value == 2:
                                                        team_role_type = "member"
                                                except ValueError:
                                                    pass
                                        elif isinstance(value, (int, float)):
                                            int_value = int(value)
                                            if int_value == 8:
                                                team_role_type = "manager"
                                            elif int_value == 2:
                                                team_role_type = "member"
                                        
                                        if team_role_type is None:
                                            print(f"Invalid team_role value: {value} (expected: 'team lead', 'team member', 8, or 2)")
                                            condition_met = False
                                        else:
                                            # Check team roles based on team_role_type
                                            if team_role_type == "manager":  # Team Lead / Account Manager - check manager_id in teams
                                                cursor.execute("SELECT COUNT(*) FROM core_teams WHERE manager_id = %s AND deleted_at IS NULL", [agent_id])
                                                manager_result = cursor.fetchone()
                                                if manager_result and manager_result[0] > 0:
                                                    condition_met = True
                                                    print(f"Team role check: agent_id={agent_id} is manager_id in {manager_result[0]} team(s) - matches Team Lead/Account Manager")
                                                else:
                                                    condition_met = False
                                                    print(f"Team role check: agent_id={agent_id} is NOT a manager in any team - does NOT match Team Lead/Account Manager")
                                            
                                            elif team_role_type == "member":  # Team Member / Sales Agent - check if user is in core_team_users
                                                cursor.execute("SELECT COUNT(*) FROM core_team_users WHERE user_id = %s", [agent_id])
                                                team_user_result = cursor.fetchone()
                                                if team_user_result and team_user_result[0] > 0:
                                                    condition_met = True
                                                    print(f"Team role check: agent_id={agent_id} is in {team_user_result[0]} team(s) as team member - matches Team Member/Sales Agent")
                                                else:
                                                    condition_met = False
                                                    print(f"Team role check: agent_id={agent_id} is NOT in any team - does NOT match Team Member/Sales Agent")
                                        
                                        print(f"Filter condition {field} (agent_id={agent_id}, team_role={value} -> {team_role_type}): {condition_met}")
                                        
                                except Exception as e:
                                    print(f"Error checking team role for agent {agent_id}: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    condition_met = False
                            
                            condition_results.append(condition_met)
                            continue
                        elif field == "agent_id":
                            # Check agent_id directly
                            if agent_id is None:
                                condition_met = False
                            else:
                                comparison_value = int(value) if value is not None else None
                                condition_met = evaluate_condition(agent_id, operator, comparison_value)
                                print(f"Filter condition {field} (agent_id={agent_id} {operator} {comparison_value}): {condition_met}")
                            condition_results.append(condition_met)
                            continue
                        else:
                            # For other filter fields (insurer, risk_type, product, etc.),
                            # they are already applied as filters during aggregation,
                            # so we don't need to check them again here.
                            # The aggregation already filtered the data, so if we got a result,
                            # the filter condition is implicitly met.
                            print(f"Filter field {field} already applied during aggregation, skipping condition check")
                            condition_met = True  # If we got performance data, the filter was already applied
                            condition_results.append(condition_met)
                            continue
                    
                    # Special handling for achievement_percentage calculation
                    # Calculate from sum_of_agent_achieved and sum_of_agent_sales_target
                    # Note: For account managers, these values are already aggregated from their sales agents
                    # in aggregate_performance_data, so we can use them directly here
                    if field == "achievement_percentage" or field == "achievement_percent":
                        achieved = performance_data.get("sum_of_agent_achieved", 0)
                        target = performance_data.get("sum_of_agent_sales_target", 0)
                        
                        # Check if there's a product filter in the conditions
                        has_product_filter = False
                        product_filter_value = None
                        if isinstance(performance_fields, dict) and "conditions" in performance_fields:
                            for cond in performance_fields.get("conditions", []):
                                if isinstance(cond, dict) and cond.get("field") in ["product", "product_id", "native_product"]:
                                    has_product_filter = True
                                    product_filter_value = cond.get("value")
                                    break
                        
                        if has_product_filter:
                            print(f"WARNING: Achievement percentage calculation with product filter (agent_id={agent_id}):")
                            print(f"  Product filter: {product_filter_value}")
                            print(f"  Achieved (filtered by product): {achieved}")
                            print(f"  Target (NOT filtered by product - general target): {target}")
                            print(f"  NOTE: Sales targets are not product-specific. This calculation compares")
                            print(f"  product-specific achieved amount against general target, which may not be accurate.")
                            print(f"  If you need product-specific achievement, ensure targets are also product-specific.")
                        
                        if target and float(target) > 0:
                            achievement_percentage = (float(achieved) / float(target)) * 100.0
                            print(f"Calculated achievement_percentage (agent_id={agent_id}): ({achieved} / {target}) * 100 = {achievement_percentage}%")
                            if has_product_filter:
                                print(f"  This percentage represents: (product-specific achieved) / (general target)")
                            
                            # Now evaluate the condition with the calculated percentage
                            if isinstance(value, (list, tuple)) and operator == "between":
                                if len(value) == 2:
                                    try:
                                        start_val = float(value[0])
                                        end_val = float(value[1])
                                        condition_met = start_val <= achievement_percentage <= end_val
                                        print(f"Achievement percentage condition (agent_id={agent_id}): {achievement_percentage}% between [{start_val}, {end_val}] = {condition_met}")
                                        if has_product_filter:
                                            print(f"  Condition result with product filter: {condition_met}")
                                        condition_results.append(condition_met)
                                        continue
                                    except (ValueError, TypeError) as e:
                                        print(f"Error evaluating achievement_percentage between condition: {e}")
                                        condition_met = False
                                        condition_results.append(condition_met)
                                        continue
                            else:
                                # For other operators, convert value and compare
                                try:
                                    comparison_value = float(value) if value else 0
                                    condition_met = evaluate_condition(achievement_percentage, operator, comparison_value)
                                    print(f"Achievement percentage condition: {achievement_percentage}% {operator} {comparison_value} = {condition_met}")
                                    condition_results.append(condition_met)
                                    continue
                                except (ValueError, TypeError) as e:
                                    print(f"Error evaluating achievement_percentage condition: {e}")
                                    condition_met = False
                                    condition_results.append(condition_met)
                                    continue
                        else:
                            print(f"Warning: Cannot calculate achievement_percentage (agent_id={agent_id}) - target is 0 or missing (achieved={achieved}, target={target})")
                            if has_product_filter:
                                print(f"  Product filter is active but target is 0. This may indicate:")
                                print(f"  1. No sales target set for this agent/period")
                                print(f"  2. Sales target is not product-specific (general target may not apply to this product)")
                            condition_met = False
                            condition_results.append(condition_met)
                            continue
                    
                    # Find the registry for this field to get the actual field name
                    registry = None
                    # Look up registry by parameter (field key) or by field array
                    for reg in PERFORMANCE_FIELD_REGISTRY:
                        if reg.get("parameter") == field or field in reg.get("field", []):
                            registry = reg
                            break
                    
                    if registry:
                        # Get the actual field name from registry
                        actual_field_name = registry["field"][0] if registry["field"] else "id"
                        
                        # Try to get performance value by field key first, then by field_name
                        # Use 'in' check to distinguish between missing key and None value
                        if field in performance_data:
                            performance_value = performance_data[field]
                            print(f"Found performance_value for field '{field}' by field key: {performance_value} (type: {type(performance_value)}, agent_id={agent_id})")
                        elif actual_field_name in performance_data:
                            performance_value = performance_data[actual_field_name]
                            print(f"Found performance_value for field '{field}' by field_name '{actual_field_name}': {performance_value} (type: {type(performance_value)}, agent_id={agent_id})")
                        else:
                            performance_value = None
                            print(f"WARNING: Field '{field}' not found in performance_data for agent_id={agent_id}. Available keys: {list(performance_data.keys())}")
                            print(f"  This field should have been aggregated. Check if it's in the fields list during aggregation.")
                        
                        # Handle None values - for numeric fields, treat None as 0 for comparison purposes
                        # This is important because if no records exist, the aggregation returns 0, not None
                        # However, if the field is missing entirely (e.g., due to an error), treat it as 0 for numeric comparisons
                        if performance_value is None and registry:
                            # Check if this is a numeric field (sum, count aggregations)
                            agg_type = registry.get("agg", "sum")
                            if agg_type in ["sum", "count"]:
                                performance_value = 0
                                print(f"Treating missing field '{field}' as 0 for numeric comparison (agg_type={agg_type})")
                        
                        if performance_value is not None:
                            # Resolve value if it's a field reference
                            comparison_value = value
                            if is_field_reference(value):
                                # Find the registry for the referenced field
                                value_registry = None
                                for reg in PERFORMANCE_FIELD_REGISTRY:
                                    if reg.get("parameter") == value or value in reg.get("field", []):
                                        value_registry = reg
                                        break
                                
                                if value_registry:
                                    value_field_name = value_registry["field"][0] if value_registry["field"] else "id"
                                    # Try to get value by field key first, then by field_name
                                    if value in performance_data:
                                        comparison_value = performance_data[value]
                                        print(f"Resolved field reference '{value}' by parameter key: {comparison_value} (agent_id={agent_id})")
                                    elif value_field_name in performance_data:
                                        comparison_value = performance_data[value_field_name]
                                        print(f"Resolved field reference '{value}' by field_name '{value_field_name}': {comparison_value} (agent_id={agent_id})")
                                    else:
                                        comparison_value = None
                                        print(f"ERROR: Referenced field '{value}' not found in performance_data for agent_id={agent_id}")
                                        print(f"  Available keys in performance_data: {list(performance_data.keys())}")
                                        print(f"  This field should have been aggregated. Check if it's in the fields list during aggregation.")
                                    
                                    if comparison_value is not None:
                                        print(f"Resolved field reference {value} to value: {comparison_value} (agent_id={agent_id})")
                                    else:
                                        print(f"Referenced field {value} not found in performance data (None) for agent_id={agent_id}")
                                        condition_met = False
                                        condition_results.append(condition_met)
                                        continue
                                else:
                                    print(f"Registry not found for referenced field {value} (agent_id={agent_id})")
                                    condition_met = False
                                    condition_results.append(condition_met)
                                    continue
                            else:
                                # Not a field reference - check if type is percentage
                                if condition_type == "percentage":
                                    print(f"Processing percentage type condition for field '{field}' (agent_id={agent_id})")
                                    # Convert percentage value to actual amount
                                    # For percentage type conditions on achievement fields, calculate percentage of target
                                    # For other fields, calculate percentage of the field value itself
                                    try:
                                        percentage_value = float(value) if value else 0
                                        
                                        # Special handling for achievement fields - use target as base
                                        if field in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
                                            print(f"  Achievement field detected: {field}, will calculate percentage from target")
                                            # For achievement fields, percentage is calculated from target
                                            target_field = "sum_of_agent_sales_target" if field == "sum_of_agent_achieved" else "sum_of_team_sales_target"
                                            target_value = performance_data.get(target_field, 0)
                                            
                                            # Try to get target value by different keys (handle Decimal, float, int, str)
                                            target_value_float = 0
                                            try:
                                                if target_value is not None:
                                                    if hasattr(target_value, '__float__'):
                                                        target_value_float = float(target_value)
                                                    elif isinstance(target_value, (int, float)):
                                                        target_value_float = float(target_value)
                                                    elif isinstance(target_value, str):
                                                        target_value_float = float(target_value)
                                                    else:
                                                        target_value_float = 0
                                            except (ValueError, TypeError):
                                                target_value_float = 0
                                            
                                            # Try alternative field names if target is 0 or missing
                                            if target_value_float == 0:
                                                # Try alternative field names
                                                alt_target_fields = []
                                                if target_field == "sum_of_agent_sales_target":
                                                    alt_target_fields = ["target_amount", "sum_of_agent_sales_target", "target"]
                                                else:
                                                    alt_target_fields = ["sum_of_team_sales_target", "target_amount", "target"]
                                                
                                                for alt_field in alt_target_fields:
                                                    if alt_field in performance_data:
                                                        alt_value = performance_data.get(alt_field, 0)
                                                        try:
                                                            if alt_value is not None:
                                                                if hasattr(alt_value, '__float__'):
                                                                    alt_value_float = float(alt_value)
                                                                elif isinstance(alt_value, (int, float)):
                                                                    alt_value_float = float(alt_value)
                                                                elif isinstance(alt_value, str):
                                                                    alt_value_float = float(alt_value)
                                                                else:
                                                                    alt_value_float = 0
                                                                
                                                                if alt_value_float > 0:
                                                                    target_value = alt_value
                                                                    target_value_float = alt_value_float
                                                                    print(f"  Using alternative target field '{alt_field}': {target_value}")
                                                                    break
                                                        except (ValueError, TypeError):
                                                            continue
                                            
                                            if target_value_float > 0:
                                                base_value = target_value_float
                                                # Calculate: percentage_value% of target
                                                comparison_value = (base_value * percentage_value) / 100.0
                                                print(f"Converted percentage value for achievement field '{field}': {value}% of {base_value} (from {target_field}) = {comparison_value}")
                                                print(f"  Performance data available keys: {list(performance_data.keys())}")
                                                print(f"  Target field '{target_field}' value: {target_value} (converted to {target_value_float})")
                                                print(f"  Achieved value: {performance_value}")
                                                print(f"  Condition: {performance_value} {operator} {comparison_value} (which is {percentage_value}% of {target_value_float})")
                                            else:
                                                print(f"ERROR: Target value ({target_field}) is 0 or missing, cannot calculate percentage for achievement field")
                                                print(f"  Performance data available keys: {list(performance_data.keys())}")
                                                print(f"  Target field '{target_field}' value: {target_value} (type: {type(target_value)})")
                                                print(f"  Tried alternative fields: {alt_target_fields if 'alt_target_fields' in locals() else []}")
                                                print(f"  This condition will fail: cannot evaluate percentage condition without target")
                                                print(f"  Agent may not have a sales target set for this period")
                                                condition_met = False
                                                condition_results.append(condition_met)
                                                continue
                                        else:
                                            # For other fields, use performance_value as the base for percentage calculation
                                            if performance_value is not None:
                                                base_value = float(performance_value)
                                                # Calculate: percentage_value% of performance_value
                                                comparison_value = (base_value * percentage_value) / 100.0
                                                print(f"Converted percentage value: {value}% of {base_value} (from {field}) = {comparison_value}")
                                            else:
                                                print(f"Warning: performance_value is None, cannot calculate percentage, using value as fixed")
                                                comparison_value = float(value) if value else None
                                    except (ValueError, TypeError) as e:
                                        print(f"Error converting percentage value '{value}': {e}, using as fixed value")
                                        try:
                                            comparison_value = float(value) if value else None
                                        except (ValueError, TypeError):
                                            comparison_value = None
                                elif condition_type == "fixed" or condition_type == "":
                                    # Use value directly as fixed amount
                                    try:
                                        # Handle both string and numeric values
                                        if isinstance(value, str):
                                            # Try to convert string to float
                                            comparison_value = float(value)
                                        elif isinstance(value, (int, float)):
                                            comparison_value = float(value)
                                        else:
                                            comparison_value = None
                                        print(f"Converted comparison value for field '{field}': '{value}' (type: {type(value)}) -> {comparison_value} (type: {type(comparison_value)})")
                                    except (ValueError, TypeError) as e:
                                        print(f"Error converting comparison value '{value}' to float: {e}")
                                        comparison_value = None
                                else:
                                    # Unknown type, try to use as fixed value
                                    print(f"Unknown condition type '{condition_type}', using value as fixed")
                                    try:
                                        comparison_value = float(value) if value else None
                                    except (ValueError, TypeError):
                                        comparison_value = None
                            
                            # Ensure performance_value is converted to float for numeric comparison
                            if performance_value is not None:
                                try:
                                    if hasattr(performance_value, '__float__'):
                                        performance_value = float(performance_value)
                                    elif isinstance(performance_value, (int, float)):
                                        performance_value = float(performance_value)
                                except (ValueError, TypeError) as e:
                                    print(f"Warning: Could not convert performance_value {performance_value} to float: {e}")
                            else:
                                # Performance value is None - this should not happen for aggregatable fields
                                # but handle it gracefully
                                print(f"ERROR: performance_value is None for field '{field}' (agent_id={agent_id})")
                                print(f"  This field should have been aggregated. Available keys: {list(performance_data.keys())}")
                                print(f"  Condition will fail: cannot evaluate condition with None performance value")
                                condition_met = False
                                condition_results.append(condition_met)
                                continue
                            
                            # Special logging for percentage type conditions on achievement fields
                            if condition_type == "percentage" and field in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
                                target_field = "sum_of_agent_sales_target" if field == "sum_of_agent_achieved" else "sum_of_team_sales_target"
                                target_value = performance_data.get(target_field, 0)
                                try:
                                    percentage_val = float(value) if value else 0
                                except (ValueError, TypeError):
                                    percentage_val = 0
                                print(f"  PERCENTAGE ACHIEVEMENT CONDITION (agent_id={agent_id}):")
                                print(f"    Field: {field}")
                                print(f"    Achieved: {performance_value}")
                                print(f"    Target: {target_value}")
                                if target_value and float(target_value) > 0:
                                    achievement_pct = (float(performance_value) / float(target_value)) * 100.0 if performance_value else 0
                                    print(f"    Actual Achievement: {achievement_pct:.2f}%")
                                    print(f"    Condition: {field} {operator} {percentage_val}% of target")
                                    if comparison_value is not None:
                                        print(f"    Comparison: {performance_value} {operator} {comparison_value} (which is {percentage_val}% of {target_value})")
                                    else:
                                        print(f"    Comparison: {performance_value} {operator} None (target missing or 0)")
                            
                            condition_met = evaluate_condition(performance_value, operator, comparison_value)
                            print(f"Condition evaluation for '{field}' (agent_id={agent_id}): performance_value={performance_value} (type: {type(performance_value)}), operator='{operator}', comparison_value={comparison_value} (type: {type(comparison_value)}), result={condition_met}")
                            # Special logging for target achievement conditions
                            if field == "sum_of_agent_achieved" and is_field_reference(value) and "target" in str(value).lower():
                                print(f"  TARGET ACHIEVEMENT CHECK (agent_id={agent_id}):")
                                print(f"    Achieved: {performance_value}")
                                print(f"    Target: {comparison_value}")
                                if comparison_value and float(comparison_value) > 0:
                                    achievement_pct = (float(performance_value) / float(comparison_value)) * 100.0
                                    print(f"    Achievement Percentage: {achievement_pct:.2f}%")
                                    print(f"    Condition: {performance_value} {operator} {comparison_value} = {condition_met}")
                                else:
                                    print(f"    WARNING: Target is 0 or None, cannot calculate achievement percentage")
                        else:
                            # Field exists but value is None - for numeric fields, treat None as 0
                            # This is important because aggregation should return 0, not None
                            print(f"WARNING: Field '{field}' has None value in performance_data. For numeric comparisons, treating as 0.")
                            try:
                                # Handle type for None performance_value case
                                if condition_type == "percentage":
                                    # Can't calculate percentage of None, use value as fixed
                                    if isinstance(value, str):
                                        comparison_value = float(value)
                                    elif isinstance(value, (int, float)):
                                        comparison_value = float(value)
                                    else:
                                        comparison_value = None
                                else:
                                    # Convert value to float for comparison
                                    if isinstance(value, str):
                                        comparison_value = float(value)
                                    elif isinstance(value, (int, float)):
                                        comparison_value = float(value)
                                    else:
                                        comparison_value = None
                                
                                # For numeric fields with None value, treat as 0 for comparison
                                # This allows conditions like "sum_of_commission_deductible < 20000" to work when value is 0
                                if registry and registry.get("agg") in ["sum", "count"]:
                                    # This is a numeric aggregation field, treat None as 0
                                    performance_value_for_comparison = 0
                                    print(f"Treating None as 0 for numeric field '{field}'")
                                else:
                                    performance_value_for_comparison = None
                                
                                condition_met = evaluate_condition(performance_value_for_comparison, operator, comparison_value)
                                print(f"Condition evaluation for '{field}' (None->0): performance_value={performance_value_for_comparison}, operator='{operator}', comparison_value={comparison_value}, result={condition_met}")
                            except (ValueError, TypeError) as e:
                                print(f"Error: Field '{field}' value is None and cannot compare with '{value}': {e}")
                                condition_met = False
                        
                        condition_results.append(condition_met)
                    else:
                        print(f"Registry not found for field {field}")
                        condition_results.append(False)
            
            # Evaluate final result based on logic type
            # NOTE: all_conditions_met is already set by hardened evaluator above (line 2151)
            # This section is kept for logging compatibility but uses the hardened evaluator result
            print(f"\n=== Final condition evaluation (using hardened evaluator result) ===")
            print(f"Hardened evaluator result: all_conditions_met = {all_conditions_met}")
            print(f"Note: Old evaluation code skipped - using hardened evaluator from evaluate_incentive_logic.py")
            
            # Skip old logic evaluation - use hardened evaluator result directly
            # The old code below would recalculate, but we already have the correct result
            _skip_old_logic_eval = True
            
            if False:  # Skip old logic evaluation - kept for reference
                # OLD LOGIC EVALUATION CODE (skipped)
                if has_multiple_role_conditions:
                    # For multiple role conditions with AND logic:
                    # 1. Role conditions are evaluated as OR (agent matches if role matches ANY of them)
                    # 2. All other conditions are evaluated with AND logic
                    
                    # Validate that we have role condition results (should match number of role conditions)
                    expected_role_conditions = len(role_conditions)
                    actual_role_conditions = len(role_condition_results)
                    if actual_role_conditions != expected_role_conditions:
                        print(f"WARNING: Expected {expected_role_conditions} role condition results, but got {actual_role_conditions}")
                        print(f"  Role conditions: {role_conditions}")
                        print(f"  Role condition results: {role_condition_results}")
                    
                    # Calculate expected number of non-role conditions
                    total_conditions = len(performance_fields.get("conditions", []))
                    expected_non_role_conditions = total_conditions - expected_role_conditions
                    actual_non_role_conditions = len(condition_results)
                    
                    # Validate that we have the correct number of non-role condition results
                    if expected_non_role_conditions > 0 and actual_non_role_conditions != expected_non_role_conditions:
                        print(f"WARNING: Expected {expected_non_role_conditions} non-role condition results, but got {actual_non_role_conditions}")
                        print(f"  Total conditions: {total_conditions}")
                        print(f"  Role conditions: {expected_role_conditions}")
                        print(f"  Expected non-role conditions: {expected_non_role_conditions}")
                        print(f"  Actual non-role condition results: {actual_non_role_conditions}")
                        print(f"  Condition results: {condition_results}")
                    
                    role_condition_met = any(role_condition_results) if role_condition_results else False
                    # If there should be other conditions but condition_results is empty, that's an error - return False
                    # If condition_results is empty and there are no other conditions expected, that's also an error - return False
                    if expected_non_role_conditions > 0:
                        # There should be other conditions - they must all be True
                        other_conditions_met = all(condition_results) if condition_results else False
                        if not condition_results:
                            print(f"ERROR: Expected {expected_non_role_conditions} non-role condition results, but condition_results is empty!")
                            print(f"  This means non-role conditions were not properly evaluated.")
                            other_conditions_met = False
                    else:
                        # No other conditions expected - this shouldn't happen with multiple role conditions, but handle it
                        print(f"WARNING: Multiple role conditions detected but no other conditions found")
                        other_conditions_met = True  # If there are no other conditions, they're implicitly met
                    
                    all_conditions_met = role_condition_met and other_conditions_met
                    print(f"Multiple role conditions with AND logic:")
                    print(f"  Expected role conditions: {expected_role_conditions}, Actual results: {actual_role_conditions}")
                    print(f"  Expected non-role conditions: {expected_non_role_conditions}, Actual results: {actual_non_role_conditions}")
                    print(f"  Role conditions (OR): {role_condition_results} -> {role_condition_met}")
                    print(f"  Other conditions (AND): {condition_results} -> {other_conditions_met}")
                    print(f"  Final result: {role_condition_met} AND {other_conditions_met} = {all_conditions_met}")
                elif logic == "OR":
                    # For OR logic: at least one condition must be True
                    all_conditions_met = any(condition_results) if condition_results else False
                    print(f"OR logic evaluation: {condition_results} -> {all_conditions_met}")
                else:
                    # For AND logic (default): all conditions must be True
                    all_conditions_met = all(condition_results) if condition_results else False
                    print(f"AND logic evaluation: {condition_results} -> {all_conditions_met}")
                    if not all_conditions_met:
                        print(f"AND logic failed: Not all conditions are True. Failed conditions:")
                        for idx, (cond, result) in enumerate(zip(performance_fields["conditions"], condition_results)):
                            if not result:
                                print(f"  - Condition {idx + 1}: {cond.get('field')} {cond.get('operator')} {cond.get('value')} -> {result}")
            # END OF OLD LOGIC EVALUATION (skipped - using hardened evaluator result)
            
            # all_conditions_met is already set by hardened evaluator - proceed to reward calculation
            if all_conditions_met:
                # Calculate reward amount based on reward type (percentage vs fixed)
                # Check reward type from multiple sources (database field and performance_fields JSON)
                reward_type_string = incentive_setup.get("reward_type_string", "fixed")
                
                # Also check performance_fields JSON for reward_type and reward_type_value (some setups store it there)
                # Check both at the top level and within conditions
                performance_fields_reward_type = None
                performance_fields_reward_value = None
                if isinstance(performance_fields, dict):
                    # Check top level first
                    performance_fields_reward_type = performance_fields.get("reward_type")
                    performance_fields_reward_value = performance_fields.get("reward_type_value")
                    
                    # If not found at top level, check within conditions (some setups store it in individual conditions)
                    if not performance_fields_reward_type and "conditions" in performance_fields:
                        for condition in performance_fields.get("conditions", []):
                            if isinstance(condition, dict):
                                if "reward_type" in condition:
                                    performance_fields_reward_type = condition.get("reward_type")
                                if "reward_type_value" in condition:
                                    performance_fields_reward_value = condition.get("reward_type_value")
                                # Break after finding first occurrence
                                if performance_fields_reward_type:
                                    break
                
                # Determine if it's percentage type - check multiple sources
                is_percentage = False
                using_performance_fields_reward_type = False
                
                # Check reward_type_id (common convention: 1=Fixed, 2=Percentage, 3=Tiered)
                reward_type_id = incentive_setup.get("reward_type_id")
                if reward_type_id == 2:
                    is_percentage = True
                    print(f"Detected percentage type from reward_type_id: {reward_type_id}")
                
                # Check reward_type_string from database
                if not is_percentage and reward_type_string:
                    reward_type_lower = str(reward_type_string).lower().strip()
                    if reward_type_lower in ["percentage", "percent", "%"]:
                        is_percentage = True
                        print(f"Detected percentage type from database reward_type_string: {reward_type_string}")
                
                # Check performance_fields JSON for reward_type
                if not is_percentage and performance_fields_reward_type:
                    perf_reward_type_lower = str(performance_fields_reward_type).lower().strip()
                    if perf_reward_type_lower in ["percentage", "percent", "%"]:
                        is_percentage = True
                        using_performance_fields_reward_type = True
                        print(f"Detected percentage type from performance_fields: {performance_fields_reward_type}")
                
                # Use reward_type_value from performance_fields if available (prefer over database value)
                # This applies whether percentage was detected from reward_type_id or performance_fields
                actual_reward_value = reward_type_value
                if performance_fields_reward_value is not None:
                    # Convert string to float if needed
                    try:
                        actual_reward_value = float(performance_fields_reward_value)
                        print(f"Using reward value from performance_fields: {actual_reward_value}")
                    except (ValueError, TypeError):
                        print(f"Could not convert performance_fields reward_value '{performance_fields_reward_value}' to float, using database value")
                        actual_reward_value = reward_type_value
                else:
                    print(f"Using reward value from database: {actual_reward_value}")
                
                reward_amount = float(actual_reward_value)
                
                if is_percentage:
                    # ============================================================
                    # PERCENTAGE TYPE CALCULATION
                    # ============================================================
                    # Formula: incentive_amount = (incentive_base_field_value * reward_type_value) / 100
                    #
                    # Examples (with amounts):
                    #
                    # 1) Standard agent (incentive_base_field = sum_of_agent_commission_recognized):
                    #    base = 42,500 (commission recognized in period), reward % = 2
                    #    => (42,500 * 2) / 100 = 850.00
                    #
                    # 2) Team lead + product (conditions: team_role=team lead, product=31):
                    #    base = commission RECEIVED by team lead for product 31 (includes override from
                    #           team sales), not just commission from policies they sold.
                    #    e.g. base = 15,000, reward % = 10 => (15,000 * 10) / 100 = 1,500.00
                    #
                    # 3) Brokerage revenue base:
                    #    incentive_base_field = "sum_of_brokerage_revenue_recognized"
                    #    base = 10,000, reward % = 1 => (10,000 * 1) / 100 = 100.00
                    # ============================================================
                    
                    incentive_base_field = incentive_setup.get("incentive_base_field")
                    if incentive_base_field:
                        # Get the base field value from performance_data
                        base_field_value = None
                        
                        # Try multiple lookup strategies
                        # 1. Direct key lookup (exact match)
                        if incentive_base_field in performance_data:
                            base_field_value = performance_data[incentive_base_field]
                            print(f"Found base_field_value by direct key '{incentive_base_field}': {base_field_value}")
                        
                        # 2. Try registry parameter lookup
                        if base_field_value is None:
                            for reg in PERFORMANCE_FIELD_REGISTRY:
                                if reg.get("parameter") == incentive_base_field:
                                    # Try all field names from registry
                                    for field_name in reg.get("field", []):
                                        if field_name in performance_data:
                                            base_field_value = performance_data[field_name]
                                            print(f"Found base_field_value by registry parameter '{incentive_base_field}' -> field '{field_name}': {base_field_value}")
                                            break
                                    if base_field_value is not None:
                                        break
                        
                        # 3. Try registry field name lookup (inverse lookup)
                        if base_field_value is None:
                            for reg in PERFORMANCE_FIELD_REGISTRY:
                                if incentive_base_field in reg.get("field", []):
                                    # Try parameter first, then all field names
                                    if reg.get("parameter") and reg.get("parameter") in performance_data:
                                        base_field_value = performance_data[reg.get("parameter")]
                                        print(f"Found base_field_value by registry field '{incentive_base_field}' -> parameter '{reg.get('parameter')}': {base_field_value}")
                                    else:
                                        for field_name in reg.get("field", []):
                                            if field_name in performance_data:
                                                base_field_value = performance_data[field_name]
                                                print(f"Found base_field_value by registry field '{incentive_base_field}' -> field '{field_name}': {base_field_value}")
                                                break
                                    if base_field_value is not None:
                                        break
                        
                        # 4. Try case-insensitive key lookup as last resort
                        if base_field_value is None:
                            incentive_base_field_lower = incentive_base_field.lower()
                            for key, value in performance_data.items():
                                if key.lower() == incentive_base_field_lower:
                                    base_field_value = value
                                    print(f"Found base_field_value by case-insensitive key '{key}': {base_field_value}")
                                    break
                        
                        if base_field_value is not None:
                            try:
                                # Calculate percentage: (base_value * percentage) / 100
                                base_val = float(base_field_value)
                                reward_val = float(actual_reward_value)
                                
                                # Handle edge cases
                                if base_val < 0:
                                    print(f"Warning: base_field_value is negative ({base_val}), using absolute value for calculation (agent_id={agent_id})")
                                    base_val = abs(base_val)
                                
                                # Check if this is a penalty (negative reward_type_value)
                                is_penalty = False
                                if reward_type_value and float(reward_type_value) < 0:
                                    is_penalty = True
                                
                                # For penalties: if base is 0, still calculate (will be 0, but we want to track the penalty)
                                # For regular rewards: if base is 0, the reward amount will be 0
                                reward_amount = (base_val * reward_val) / 100.0
                                
                                # Round to 2 decimal places for currency
                                reward_amount = round(reward_amount, 2)
                                
                                if is_penalty and base_val == 0:
                                    print(f"Penalty calculation (agent_id={agent_id}): {base_val} * {reward_val}% / 100 = {reward_amount} (base is 0, but penalty condition may still be met)")
                                else:
                                    print(f"Percentage calculation (agent_id={agent_id}): {base_val} * {reward_val}% / 100 = {reward_amount}")
                                    if is_penalty:
                                        print(f"  This is a PENALTY (negative reward_type_value={reward_type_value}), will be converted to negative amount")
                                        print(f"  Base field '{incentive_base_field}' value: {base_val} (agent_id={agent_id})")
                                        print(f"  Penalty percentage: {abs(reward_val)}%")
                                        print(f"  Calculated penalty amount (before negation): {reward_amount}")
                                    
                                    # Check if product filter is active and warn if base field might not be filtered
                                    performance_fields_check = incentive_setup.get("performance_fields", {})
                                    if isinstance(performance_fields_check, str):
                                        try:
                                            performance_fields_check = json.loads(performance_fields_check)
                                        except:
                                            performance_fields_check = {}
                                    
                                    has_product_filter_check = False
                                    if isinstance(performance_fields_check, dict) and "conditions" in performance_fields_check:
                                        for cond in performance_fields_check.get("conditions", []):
                                            if isinstance(cond, dict) and cond.get("field") in ["product", "product_id", "native_product"]:
                                                has_product_filter_check = True
                                                break
                                    
                                    if has_product_filter_check:
                                        # Check if base field supports product filtering
                                        base_field_registry = None
                                        for reg in PERFORMANCE_FIELD_REGISTRY:
                                            if reg.get("parameter") == incentive_base_field or incentive_base_field in reg.get("field", []):
                                                base_field_registry = reg
                                                break
                                        
                                        if base_field_registry:
                                            base_field_filters = base_field_registry.get("filters", [])
                                            if "product" not in base_field_filters and "product_id" not in base_field_filters and "native_product" not in base_field_filters:
                                                print(f"  WARNING: Product filter is active, but base field '{incentive_base_field}' does NOT support product filtering.")
                                                print(f"  The commission amount ({base_val}) may include all products, not just the filtered product.")
                                                print(f"  This could result in incorrect bonus calculation.")
                                            else:
                                                print(f"  Verified: Base field '{incentive_base_field}' supports product filtering - commission is correctly filtered.")
                            except (ValueError, TypeError) as e:
                                print(f"Error calculating percentage: {e}, using fixed value")
                                reward_amount = round(float(actual_reward_value), 2)
                        else:
                            # Base field not found or is None
                            # Check if this is a penalty
                            is_penalty_check = False
                            if reward_type_value and float(reward_type_value) < 0:
                                is_penalty_check = True
                            
                            if is_penalty_check:
                                # For penalties: if base field is not found, calculate as 0 (will be negative after conversion)
                                # This allows tracking penalties even when commission is 0
                                print(f"Warning: incentive_base_field '{incentive_base_field}' not found for penalty. Setting base to 0, penalty amount will be 0")
                                reward_amount = 0.0
                            else:
                                print(f"Warning: incentive_base_field '{incentive_base_field}' not found in performance_data. Available keys: {list(performance_data.keys())}")
                                print(f"Using fixed value as fallback: {actual_reward_value}")
                                # Fallback to fixed value if base field not found
                                reward_amount = round(float(actual_reward_value), 2)
                    else:
                        print(f"Warning: incentive_base_field is not set for percentage type reward, using fixed value")
                        reward_amount = round(float(actual_reward_value), 2)
                else:
                    # ============================================================
                    # FIXED TYPE CALCULATION
                    # ============================================================
                    # Formula: incentive_amount = reward_type_value
                    # 
                    # Example:
                    #   - reward_type_value = 500
                    #   - Result: incentive_amount = 500
                    # ============================================================
                    reward_amount = float(actual_reward_value)
                    # Round to 2 decimal places for currency
                    reward_amount = round(reward_amount, 2)
                    print(f"Fixed reward amount: {reward_amount}")
                
                # Ensure reward_amount is properly rounded to 2 decimal places
                reward_amount = round(float(reward_amount), 2)
                
                # Check if this should be a penalty (negative incentive)
                # Penalties are indicated by negative reward_type_value or a special flag
                # For penalties, the reward_amount should be negative
                is_penalty = incentive_setup.get("is_penalty", False)
                # Also check if reward_type_value is negative (indicates penalty)
                if reward_type_value and float(reward_type_value) < 0:
                    is_penalty = True
                
                if is_penalty:
                    # Make the reward amount negative for penalties
                    reward_amount = -abs(reward_amount)
                    print(f"Penalty incentive: Converting to negative amount: {reward_amount}")
                
                return {
                    "eligible": True,
                    "reward_amount": reward_amount,
                    "message": "All conditions met"
                }
        
        return {
            "eligible": False,
            "reward_amount": 0,
            "message": "Not all conditions met"
        }
    except Exception as e:
        print(f"Error calculating incentive reward: {e}")
        return {
            "eligible": False,
            "reward_amount": 0,
            "message": f"Error: {str(e)}"
        }

def generate_incentive_setup_code():
    """Generate a unique incentive setup code in format INS-000001"""
    try:
        # Try to get existing codes to find the maximum number
        try:
            existing_codes = QueryBuilderService("crmf_incentive_setups")\
                .select('incentive_code')\
                .whereNotNull('incentive_code')\
                .get()
            
            max_num = 0
            if existing_codes:
                for record in existing_codes:
                    code = record.get('incentive_code', '')
                    if code and code.startswith('INS-'):
                        try:
                            # Extract number from code like "INS-000001"
                            num_str = code.replace('INS-', '').strip()
                            num = int(num_str)
                            if num > max_num:
                                max_num = num
                        except (ValueError, AttributeError):
                            continue
            
            # Generate next code
            next_num = max_num + 1
            return f"INS-{str(next_num).zfill(6)}"
        except Exception as query_error:
            # If query fails (e.g., incentive_code column doesn't exist yet), use count-based approach
            print(f"Query error in generate_incentive_setup_code: {query_error}")
            count = QueryBuilderService("crmf_incentive_setups").select('id').count()
            return f"INS-{str(count + 1).zfill(6)}"
    except Exception as e:
        print(f"Error generating incentive setup code: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Fallback: use timestamp-based code to ensure uniqueness
        from datetime import datetime
        import random
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = str(random.randint(100, 999))
        return f"INS-{timestamp}{random_suffix}"

def generate_incentive_code():
    """Generate a unique incentive code in format INC-000001"""
    try:
        # Try to get existing codes to find the maximum number
        try:
            existing_codes = QueryBuilderService("crmf_incentives")\
                .select('code')\
                .whereNotNull('code')\
                .whereNull('deleted_at')\
                .get()
            
            max_num = 0
            if existing_codes:
                for record in existing_codes:
                    code = record.get('code', '')
                    if code and code.startswith('INC-'):
                        try:
                            # Extract number from code like "INC-000001"
                            num_str = code.replace('INC-', '').strip()
                            num = int(num_str)
                            if num > max_num:
                                max_num = num
                        except (ValueError, AttributeError):
                            continue
            
            # Generate next code
            next_num = max_num + 1
            return f"INC-{str(next_num).zfill(6)}"
        except Exception as query_error:
            # If query fails (e.g., code column doesn't exist yet), use count-based approach
            print(f"Query error in generate_incentive_code: {query_error}")
            count = QueryBuilderService("crmf_incentives").select('id').whereNull('deleted_at').count()
            return f"INC-{str(count + 1).zfill(6)}"
    except Exception as e:
        print(f"Error generating incentive code: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Fallback: use timestamp-based code to ensure uniqueness
        from datetime import datetime
        import random
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = str(random.randint(100, 999))
        return f"INC-{timestamp}{random_suffix}"

def save_incentive_record(setup, agent_id, period, performance_data, result):
    """Save incentive record to database."""
    try:
        from datetime import datetime
        
        # Convert Decimal objects to float for JSON serialization
        converted_performance_data = convert_decimal_to_float(performance_data)
        
        # Generate unique incentive code
        incentive_code = generate_incentive_code()
        print(f"Generated incentive code: {incentive_code}")
        
        # Calculate actual_performance_value - should be the value of incentive_base_field
        # This represents the actual performance metric value used for calculation
        actual_performance_value = 0
        incentive_base_field = setup.get("incentive_base_field")
        
        if incentive_base_field and performance_data:
            # Try to get the base field value (same logic as in calculate_incentive_reward)
            base_field_value = None
            
            # 1. Direct key lookup
            if incentive_base_field in performance_data:
                base_field_value = performance_data[incentive_base_field]
                print(f"Found actual_performance_value by direct key '{incentive_base_field}': {base_field_value}")
            
            # 2. Try registry parameter lookup
            if base_field_value is None:
                from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
                for reg in PERFORMANCE_FIELD_REGISTRY:
                    if reg.get("parameter") == incentive_base_field:
                        for field_name in reg.get("field", []):
                            if field_name in performance_data:
                                base_field_value = performance_data[field_name]
                                print(f"Found actual_performance_value by registry parameter '{incentive_base_field}' -> field '{field_name}': {base_field_value}")
                                break
                        if base_field_value is not None:
                            break
            
            # 3. Try registry field name lookup
            if base_field_value is None:
                for reg in PERFORMANCE_FIELD_REGISTRY:
                    if incentive_base_field in reg.get("field", []):
                        if reg.get("parameter") and reg.get("parameter") in performance_data:
                            base_field_value = performance_data[reg.get("parameter")]
                            print(f"Found actual_performance_value by registry field '{incentive_base_field}' -> parameter '{reg.get('parameter')}': {base_field_value}")
                        else:
                            for field_name in reg.get("field", []):
                                if field_name in performance_data:
                                    base_field_value = performance_data[field_name]
                                    print(f"Found actual_performance_value by registry field '{incentive_base_field}' -> field '{field_name}': {base_field_value}")
                                    break
                        if base_field_value is not None:
                            break
            
            # 4. Case-insensitive lookup
            if base_field_value is None:
                incentive_base_field_lower = incentive_base_field.lower()
                for key, value in performance_data.items():
                    if key.lower() == incentive_base_field_lower:
                        base_field_value = value
                        print(f"Found actual_performance_value by case-insensitive key '{key}': {base_field_value}")
                        break
            
            if base_field_value is not None:
                try:
                    actual_performance_value = float(base_field_value)
                    # Cap at maximum for DECIMAL(10,2) column: 99,999,999.99
                    max_value = 99999999.99
                    if actual_performance_value > max_value:
                        print(f"Warning: actual_performance_value {actual_performance_value} exceeds max, capping to {max_value}")
                        actual_performance_value = max_value
                except (ValueError, TypeError):
                    print(f"Warning: Could not convert base_field_value to float, using 0")
                    actual_performance_value = 0
            else:
                print(f"Warning: incentive_base_field '{incentive_base_field}' not found in performance_data for actual_performance_value. Available keys: {list(performance_data.keys())}")
        else:
            if not incentive_base_field:
                print(f"Warning: incentive_base_field not set, actual_performance_value will be 0")
            elif not performance_data:
                print(f"Warning: performance_data is empty, actual_performance_value will be 0")
        
        # Extract and normalize period_start and period_end from period dict
        # CRITICAL: Normalize dates to YYYY-MM-DD format for consistent database storage
        import datetime as dt
        period_start = None
        period_end = None
        
        if period and isinstance(period, dict):
            period_start_raw = period.get("start_date")
            period_end_raw = period.get("end_date")
            
            # Normalize period_start
            if period_start_raw:
                if isinstance(period_start_raw, str):
                    period_start_str = period_start_raw.split()[0] if ' ' in period_start_raw else period_start_raw
                    period_start = dt.datetime.strptime(period_start_str, "%Y-%m-%d").date()
                elif isinstance(period_start_raw, dt.datetime):
                    period_start = period_start_raw.date()
                elif isinstance(period_start_raw, dt.date):
                    period_start = period_start_raw
                else:
                    print(f"⚠️  WARNING: Invalid period_start type: {type(period_start_raw)}")
                    period_start = None
            
            # Normalize period_end
            if period_end_raw:
                if isinstance(period_end_raw, str):
                    period_end_str = period_end_raw.split()[0] if ' ' in period_end_raw else period_end_raw
                    period_end = dt.datetime.strptime(period_end_str, "%Y-%m-%d").date()
                elif isinstance(period_end_raw, dt.datetime):
                    period_end = period_end_raw.date()
                elif isinstance(period_end_raw, dt.date):
                    period_end = period_end_raw
                else:
                    print(f"⚠️  WARNING: Invalid period_end type: {type(period_end_raw)}")
                    period_end = None
                    
        elif period and isinstance(period, tuple) and len(period) == 2:
            # Normalize from tuple
            if hasattr(period[0], 'strftime'):
                period_start = period[0].date() if isinstance(period[0], dt.datetime) else period[0]
            else:
                period_start_str = str(period[0]).split()[0] if ' ' in str(period[0]) else str(period[0])
                period_start = dt.datetime.strptime(period_start_str, "%Y-%m-%d").date()
                
            if hasattr(period[1], 'strftime'):
                period_end = period[1].date() if isinstance(period[1], dt.datetime) else period[1]
            else:
                period_end_str = str(period[1]).split()[0] if ' ' in str(period[1]) else str(period[1])
                period_end = dt.datetime.strptime(period_end_str, "%Y-%m-%d").date()
        
        # Convert to normalized string format for database (YYYY-MM-DD)
        period_start_str = period_start.strftime("%Y-%m-%d") if period_start else None
        period_end_str = period_end.strftime("%Y-%m-%d") if period_end else None
        
        print(f"📅 NORMALIZED PERIOD: period_start={period_start_str}, period_end={period_end_str}")
        
        # Check if period_start/period_end columns exist before including them
        has_period_columns = _check_column_exists("crmf_incentives", "period_start") and _check_column_exists("crmf_incentives", "period_end")
        
        incentive_data = {
            "code": incentive_code,
            "agent_id": agent_id,
            "incentive_setup_id": setup.get("id"),
            "performance_metric_value": float(result.get("reward_amount", 0)),
            "actual_performance_value": float(actual_performance_value),
            "incentive_amount": float(result.get("reward_amount", 0)),
            "commission_date": datetime.now().strftime("%Y-%m-%d"),
            "repetition_type": setup.get("repeation_type", "One-Time"),
            "status": "pending",
            "matched_condition": json.dumps(converted_performance_data),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Only include period_start/period_end if columns exist
        if has_period_columns:
            incentive_data["period_start"] = period_start_str
            incentive_data["period_end"] = period_end_str
            print(f"📅 Including period_start={period_start_str}, period_end={period_end_str} in save")
        else:
            print(f"⚠️  SCHEMA: period_start/period_end columns don't exist, using commission_date only")
            # Use period_start as commission_date if columns don't exist
            if period_start_str:
                incentive_data["commission_date"] = period_start_str
        
        print(f"=== SAVING INCENTIVE RECORD ===")
        print(f"🔍 CHECK EXISTENCE BEFORE SAVE:")
        print(f"   setup_id={setup.get('id')}, agent_id={agent_id}, period_start={period_start_str}, period_end={period_end_str}")
        print(f"Agent ID: {agent_id}")
        print(f"Incentive Setup ID: {setup.get('id')}")
        print(f"Incentive Amount: {incentive_data['incentive_amount']}")
        print(f"Actual Performance Value: {incentive_data['actual_performance_value']}")
        print(f"Period Start: {period_start_str}")
        print(f"Period End: {period_end_str}")
        print(f"Performance Data: {converted_performance_data}")
        print(f"Incentive data to insert: {incentive_data}")
        
        # Insert into database with error handling for unique constraint violations
        try:
            inserted_record = QueryBuilderService("crmf_incentives").insert(incentive_data)
            print(f"✅ Incentive record saved successfully with ID: {inserted_record.get('id')}, Code: {inserted_record.get('code')}")
            return True
        except Exception as db_error:
            error_str = str(db_error).lower()
            # Check if it's a unique constraint violation
            if 'unique' in error_str or 'duplicate' in error_str or 'constraint' in error_str:
                print(f"⚠️  DUPLICATE DETECTED BY DATABASE: Unique constraint violation for setup {setup.get('id')}, agent {agent_id}, period {period_start_str} to {period_end_str}")
                print(f"   This means a duplicate record exists (database-level protection worked)")
                print(f"   Error: {db_error}")
                # Return True because the record effectively exists (just created by another process or race condition)
                return True
            else:
                # Re-raise other errors
                raise
    except Exception as e:
        print(f"Error saving incentive record: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def incentive_record_exists(setup_id, agent_id, commission_date):
    """
    DEPRECATED: Use incentive_record_exists_for_period instead.
    Check if incentive record already exists (legacy function using commission_date).
    """
    try:
        result = QueryBuilderService("crmf_incentives").where("incentive_setup_id", setup_id).where("agent_id", agent_id).where("commission_date", commission_date).first()
        return result is not None
    except Exception as e:
        print(f"Error checking incentive record existence: {e}")
        return False

def _check_column_exists(table_name, column_name):
    """Check if a column exists in a table."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW COLUMNS FROM {table_name} LIKE %s", [column_name])
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"⚠️  Error checking column existence: {e}")
        return False

def incentive_record_exists_for_agent_period(setup_id, agent_id, period_start, period_end):
    """
    Check if incentive record already exists for a specific setup, agent, and period.
    This is the correct way to check for duplicates - using period-based uniqueness.
    
    CRITICAL: This function normalizes dates to ensure consistent comparison regardless of input format.
    If period_start/period_end columns don't exist, falls back to commission_date-based check.
    """
    try:
        import datetime as dt
        
        # Normalize period_start to date object
        if period_start is None:
            print(f"⚠️  WARNING: period_start is None for setup {setup_id}, agent {agent_id}")
            return False
            
        if isinstance(period_start, str):
            # Handle both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM:SS" formats
            period_start_str = period_start.split()[0] if ' ' in period_start else period_start
            period_start = dt.datetime.strptime(period_start_str, "%Y-%m-%d").date()
        elif isinstance(period_start, dt.datetime):
            period_start = period_start.date()
        elif not isinstance(period_start, dt.date):
            print(f"⚠️  ERROR: Invalid period_start type: {type(period_start)}, value: {period_start}")
            return False
        
        # Normalize period_end to date object
        if period_end is None:
            print(f"⚠️  WARNING: period_end is None for setup {setup_id}, agent {agent_id}")
            return False
            
        if isinstance(period_end, str):
            # Handle both "YYYY-MM-DD" and "YYYY-MM-DD HH:MM:SS" formats
            period_end_str = period_end.split()[0] if ' ' in period_end else period_end
            period_end = dt.datetime.strptime(period_end_str, "%Y-%m-%d").date()
        elif isinstance(period_end, dt.datetime):
            period_end = period_end.date()
        elif not isinstance(period_end, dt.date):
            print(f"⚠️  ERROR: Invalid period_end type: {type(period_end)}, value: {period_end}")
            return False
        
        # Normalize to string format for database query (YYYY-MM-DD)
        period_start_str = period_start.strftime("%Y-%m-%d")
        period_end_str = period_end.strftime("%Y-%m-%d")
        
        # Log the check for debugging
        print(f"🔍 CHECKING DUPLICATE: setup_id={setup_id}, agent_id={agent_id}, period_start={period_start_str}, period_end={period_end_str}")
        
        # Check if period_start/period_end columns exist in database
        has_period_columns = _check_column_exists("crmf_incentives", "period_start") and _check_column_exists("crmf_incentives", "period_end")
        
        if has_period_columns:
            # Use period_start/period_end for duplicate check (preferred method)
            result = (
                QueryBuilderService("crmf_incentives")
                .where("incentive_setup_id", setup_id)
                .where("agent_id", agent_id)
                .where("period_start", period_start_str)
                .where("period_end", period_end_str)
                .whereNull("deleted_at")
                .first()
            )
        else:
            # Fallback: Use commission_date for duplicate check (if period columns don't exist)
            print(f"⚠️  SCHEMA: period_start/period_end columns don't exist, using commission_date fallback")
            result = (
                QueryBuilderService("crmf_incentives")
                .where("incentive_setup_id", setup_id)
                .where("agent_id", agent_id)
                .whereBetween("commission_date", period_start_str, period_end_str)
                .whereNull("deleted_at")
                .first()
            )
        
        exists = result is not None
        if exists:
            print(f"✅ DUPLICATE FOUND: Incentive record already exists for setup {setup_id}, agent {agent_id}, period {period_start_str} to {period_end_str}")
            print(f"   Existing record ID: {result.get('id') if result else 'N/A'}")
        else:
            print(f"✅ NO DUPLICATE: No existing record found for setup {setup_id}, agent {agent_id}, period {period_start_str} to {period_end_str}")
        
        return exists
    except Exception as e:
        error_str = str(e).lower()
        print(f"❌ ERROR checking incentive record existence for period: {e}")
        import traceback
        print(f"   Traceback: {traceback.format_exc()}")
        
        # Check if error is due to missing columns (schema mismatch)
        if 'unknown column' in error_str and ('period_start' in error_str or 'period_end' in error_str):
            print(f"⚠️  SCHEMA MISMATCH DETECTED: period_start/period_end columns don't exist in database")
            print(f"   Falling back to commission_date-based duplicate check")
            
            # Fallback: Use commission_date for duplicate check
            try:
                # Use period_start as commission_date range
                fallback_result = (
                    QueryBuilderService("crmf_incentives")
                    .where("incentive_setup_id", setup_id)
                    .where("agent_id", agent_id)
                    .whereBetween("commission_date", period_start_str, period_end_str)
                    .whereNull("deleted_at")
                    .first()
                )
                
                fallback_exists = fallback_result is not None
                if fallback_exists:
                    print(f"✅ DUPLICATE FOUND (fallback): Incentive record exists for setup {setup_id}, agent {agent_id}, commission_date between {period_start_str} and {period_end_str}")
                    print(f"   Existing record ID: {fallback_result.get('id') if fallback_result else 'N/A'}")
                else:
                    print(f"✅ NO DUPLICATE (fallback): No existing record found for setup {setup_id}, agent {agent_id}, commission_date between {period_start_str} and {period_end_str}")
                
                return fallback_exists
            except Exception as fallback_error:
                print(f"❌ ERROR in fallback duplicate check: {fallback_error}")
                # On fallback error, return False (don't assume exists - let it try to save)
                # The database unique constraint will catch it if it's truly a duplicate
                return False
        else:
            # For other errors, return False (don't assume exists)
            # This prevents silently skipping when there's a real error
            print(f"⚠️  Returning False on error (will attempt save, database constraint will prevent duplicates)")
            return False

def query_policies(agent_id, field_key, operator, value, period=None):
    """Query policies based on field, operator, and value."""
    try:
        # Get registry for the field
        from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
        registry = None
        for reg in PERFORMANCE_FIELD_REGISTRY:
            if field_key in reg.get("field", []):
                registry = reg
                break
        
        if not registry:
            return []
        
        # Build query
        base_table = registry["base_table"]
        agent_field = registry.get("agent_field")
        field_name = registry["field"][0] if registry["field"] else "id"
        
        query = QueryBuilderService(base_table).select("*")
        
        # Add agent filter
        if agent_field:
            query = query.where(agent_field, agent_id)
        
        # Add field filter
        if operator == "=":
            query = query.where(field_name, value)
        elif operator == ">":
            query = query.where(field_name, ">", value)
        elif operator == "<":
            query = query.where(field_name, "<", value)
        elif operator == ">=":
            query = query.where(field_name, ">=", value)
        elif operator == "<=":
            query = query.where(field_name, "<=", value)
        
        # Add date filters if period is provided
        if period and isinstance(period, dict):
            start_date = period.get("start_date")
            end_date = period.get("end_date")
            if start_date and end_date:
                date_fields = ["created_at", "updated_at", "policy_effective_date", "invoice_date"]
                for date_field in date_fields:
                    if date_field in registry.get("filters", []):
                        query = query.where(f"{base_table}.{date_field}", ">=", start_date)
                        query = query.where(f"{base_table}.{date_field}", "<=", end_date)
                        break
        
        return query.get()
    except Exception as e:
        print(f"Error querying policies: {e}")
        return []

def check_incentive_table_structure():
    """Check if the crmf_incentives table exists and has the correct structure."""
    try:
        # Check if table exists
        result = QueryBuilderService("crmf_incentives").select("1").limit(1).first()
        if result is None:
            print("crmf_incentives table does not exist")
            return False
        
        print("crmf_incentives table exists")
        return True
    except Exception as e:
        print(f"Error checking table structure: {e}")
        return False

def test_database_connection():
    """Test database connection."""
    try:
        result = QueryBuilderService("core_users").select("1").limit(1).first()
        return result is not None
    except Exception as e:
        print(f"Database connection test failed: {e}")
        return False

def create_incentive_table_simple():
    """Create the crmf_incentives table."""
    try:
        # This would typically use Django migrations, but for now we'll just return True
        print("Creating crmf_incentives table...")
        return True
    except Exception as e:
        print(f"Error creating table: {e}")
        return False

def cleanup_duplicate_incentives():
    """Clean up duplicate incentive records."""
    try:
        # Simple cleanup - mark duplicates as deleted
        print("Cleaning up duplicate incentives...")
        return 0  # Return count of cleaned records
    except Exception as e:
        print(f"Error cleaning up duplicates: {e}")
        return 0

def incentive_record_exists_for_period(setup_id, period):
    """Check if incentive record exists for a specific period."""
    try:
        if isinstance(period, tuple) and len(period) == 2:
            start_date, end_date = period
            # Use whereBetween for date range queries to avoid SQL syntax issues
            result = QueryBuilderService("crmf_incentives").where("incentive_setup_id", setup_id).whereBetween("commission_date", start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")).first()
            return result is not None
        return False
    except Exception as e:
        print(f"Error checking incentive record for period: {e}")
        return False

def get_registry_for_field(field):
    """Find the registry entry for a given field."""
    try:
        from envoy_bu_policy_api.finance.config.performance_field_registry import PERFORMANCE_FIELD_REGISTRY
        
        # First, try to find exact match in field arrays
        for reg in PERFORMANCE_FIELD_REGISTRY:
            if field in reg.get("field", []):
                return reg
        
        # If not found, try to map common field names to registry parameters
        field_mapping = {
            "policies": "policy_count",
            "sum_of_premium_amount": "sum_of_premium_amount",
            "premium_amount": "issued_policy_premium_amount",
            "count_of_policies": "policy_count",
            "sum_of_sum_insured": "issued_policy_sum_insured",
            "sum_insureds": "issued_policy_sum_insured",
            "sum_insured": "issued_policy_sum_insured",  # Direct mapping for sum_insured field
            "sum_of_brokerage_revenue_recognized": "sum_of_brokerage_revenue_recognized",
            "sum_of_brokerage_revenue_realized": "brokerage_revenue_realized",
            "sum_of_brokerage_agent_commission": "brokerage_agent_commission",
            "sum_of_brokerage_overriding_commission": "brokerage_overriding_commission",
            "sum_of_brokerage_commission_deductible": "brokerage_commission_deductible",
            "sum_of_commission_deductible": "sum_of_commission_deductible",
            "sum_of_agent_commission": "brokerage_agent_commission",
            "agent_commissions": "agent_commission",
            "sum_of_payments": "total_payments",
            "total_payments": "total_payments",
            "agent_sales_targets": "agent_sales_targets",
            "team_sales_targets": "team_sales_targets",
            "native_product_id": "native_product_id",
            "sales_agent_id": "sales_agent_id"
        }
        
        # Try to find mapped parameter
        if field in field_mapping:
            mapped_parameter = field_mapping[field]
            for reg in PERFORMANCE_FIELD_REGISTRY:
                if reg.get("parameter") == mapped_parameter:
                    return reg
        
        # If still not found, try to find by partial parameter match
        for reg in PERFORMANCE_FIELD_REGISTRY:
            parameter = reg.get("parameter", "")
            if field.lower() in parameter.lower() or any(f.lower() in field.lower() for f in reg.get("field", [])):
                return reg
        
        return None
    except Exception as e:
        print(f"Error getting registry for field: {e}")
        return None
    