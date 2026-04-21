"""
Complete Logic Evaluator for Incentive Engine
Recursively evaluates AND/OR conditions with nested logic support.
"""


def evaluate_conditions(block, performance_data, agent_id=None, has_product_filter=None):
    """
    Recursively evaluate AND/OR conditions.
    Supports nested logic.
    
    Args:
        block: Dict with 'logic' (AND/OR) and 'conditions' list, or a single condition dict
        performance_data: Dict of aggregated performance metrics
        agent_id: Optional agent ID for filter field checks
        has_product_filter: Whether product filter is active (auto-detected if None)
    
    Returns:
        bool: True if conditions are met, False otherwise
    """
    try:
        # Auto-detect product filter if not provided
        if has_product_filter is None:
            has_product_filter = _detect_product_filter(block)
        
        # Handle single condition (not wrapped in logic block)
        if not isinstance(block, dict):
            return False
        
        # If it's a single condition (has field, operator, value but no logic/conditions)
        if "field" in block and "operator" in block and "value" in block and "logic" not in block:
            return evaluate_single_condition(block, performance_data, agent_id, has_product_filter)
        
        # If it's a logic block (has logic and conditions)
        if "logic" not in block or "conditions" not in block:
            return False
        
        logic = block.get("logic", "AND").upper()
        conditions = block.get("conditions", [])
        
        if not conditions:
            return False
        
        # CRITICAL FIX: Detect multiple role conditions with AND logic
        # When conditions have "role = 2 AND role = 8", a user can't have both roles
        # So we need to evaluate role conditions as OR, while keeping other conditions as AND
        role_conditions = []
        non_role_conditions = []
        role_condition_indices = []
        
        for idx, cond in enumerate(conditions):
            if isinstance(cond, dict) and "field" in cond:
                field = cond.get("field")
                # Check if this is a role condition
                if field in ("role", "role_id", "user_role"):
                    role_conditions.append(cond)
                    role_condition_indices.append(idx)
                else:
                    non_role_conditions.append((idx, cond))
        
        # If we have multiple role conditions with AND logic, handle them specially
        has_multiple_role_conditions = len(role_conditions) > 1 and logic == "AND"
        
        if has_multiple_role_conditions:
            print(f"⚠️  DETECTED: Multiple role conditions with AND logic - converting role conditions to OR")
            print(f"  Role conditions found: {[c.get('field') + ' = ' + str(c.get('value')) for c in role_conditions]}")
            print(f"  Business Rule: A user cannot have multiple roles simultaneously")
            print(f"  Solution: Evaluating role conditions as OR (user matches if they have ANY of the roles)")
            
            # Evaluate role conditions as OR
            role_results = []
            for role_cond in role_conditions:
                role_result = evaluate_single_condition(role_cond, performance_data, agent_id, has_product_filter)
                role_results.append(role_result)
            
            role_condition_met = any(role_results) if role_results else False
            print(f"  Role conditions (OR): {role_results} -> {role_condition_met}")
            
            # Evaluate non-role conditions as AND
            non_role_results = []
            for idx, non_role_cond in non_role_conditions:
                # Handle nested conditions
                if isinstance(non_role_cond, dict) and ("logic" in non_role_cond or ("conditions" in non_role_cond and "field" not in non_role_cond)):
                    non_role_result = evaluate_conditions(non_role_cond, performance_data, agent_id, has_product_filter)
                else:
                    non_role_result = evaluate_single_condition(non_role_cond, performance_data, agent_id, has_product_filter)
                non_role_results.append(non_role_result)
            
            other_conditions_met = all(non_role_results) if non_role_results else True
            print(f"  Other conditions (AND): {non_role_results} -> {other_conditions_met}")
            
            # Final result: role conditions (OR) AND other conditions (AND)
            final_result = role_condition_met and other_conditions_met
            print(f"  Final result: {role_condition_met} AND {other_conditions_met} = {final_result}")
            return final_result
        
        # Normal evaluation (no special role condition handling needed)
        results = []
        
        for cond in conditions:
            # Nested logic support
            if isinstance(cond, dict) and ("logic" in cond or ("conditions" in cond and "field" not in cond)):
                results.append(evaluate_conditions(cond, performance_data, agent_id, has_product_filter))
                continue
            
            # Single condition
            if isinstance(cond, dict) and "field" in cond:
                results.append(evaluate_single_condition(cond, performance_data, agent_id, has_product_filter))
            else:
                results.append(False)
        
        # Apply logic
        if logic == "OR":
            return any(results) if results else False
        else:  # AND
            return all(results) if results else False
            
    except Exception as e:
        print(f"ERROR in evaluate_conditions: {e}")
        import traceback
        traceback.print_exc()
        return False


def evaluate_single_condition(condition, performance_data, agent_id=None, has_product_filter=False):
    """
    Evaluate a single condition.
    
    Args:
        condition: Dict with 'field', 'operator', 'value'
        performance_data: Dict of aggregated performance metrics
        agent_id: Optional agent ID for filter field checks
        has_product_filter: Whether product filter is active in conditions
    
    Returns:
        bool: True if condition is met, False otherwise
    """
    print("🔥 HARDENED EVALUATOR LOADED 🔥")
    try:
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")
        
        if not field or operator is None or value is None:
            return False
        
        # Filter fields that need special handling
        filter_fields = {"role", "role_id", "team_role", "agent_id", "product", "insurer", "risk_type", "native_product"}
        
        # Handle filter fields
        if field in filter_fields:
            return evaluate_filter_field(field, operator, value, agent_id)
        
        # CRITICAL FIX: Handle product-filtered achieved vs general target comparison
        # If product filter is active and we're comparing achieved vs target, we need to use
        # overall achieved (without product filter) for the target comparison, but keep
        # product filter for reward base calculation
        if has_product_filter and field in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
            target_field = "sum_of_agent_sales_target" if field == "sum_of_agent_achieved" else "sum_of_team_sales_target"
            # Check if value is a field reference to target or if we're doing target comparison
            is_target_comparison = (
                (isinstance(value, str) and value == target_field) or
                (isinstance(value, str) and value in performance_data and value == target_field)
            )
            if is_target_comparison:
                # Check if we have overall achieved (without product filter) in performance_data
                # The aggregation function should provide both: field (product-filtered) and field + "_overall" (without filter)
                overall_field = field + "_overall"
                if overall_field in performance_data:
                    # Use overall achieved for target comparison (correct scale)
                    print(f"✅ Using overall achieved (without product filter) for target comparison")
                    print(f"  Product-filtered {field}: {performance_data.get(field, 0)}")
                    print(f"  Overall {overall_field}: {performance_data.get(overall_field, 0)}")
                    print(f"  Target: {target_field} = {performance_data.get(target_field, 0)}")
                    print(f"  Reason: Target is general (all products), so comparing against overall achieved (all products)")
                    # Replace field with overall_field for this comparison
                    actual = performance_data.get(overall_field, 0)
                else:
                    # Fallback: If overall not available, use the product-filtered value but warn
                    # This should not happen if aggregation is correct, but handle gracefully
                    print(f"⚠️  WARNING: Product filter is active, but overall achieved not available")
                    print(f"  Field: {field} (product-filtered achieved) = {performance_data.get(field, 0)}")
                    print(f"  Target: {target_field} (general target) = {performance_data.get(target_field, 0)}")
                    print(f"  Note: Comparing product-specific achievement against general target may be inaccurate")
                    print(f"  Using product-filtered value for comparison (may result in false negatives)")
                    actual = performance_data.get(field, 0)
        
        # Get actual value from performance_data (if not already set above)
        if 'actual' not in locals() or actual is None:
            actual = performance_data.get(field)
        
        # Handle percentage type conditions on achievement fields
        condition_type = condition.get("type", "").lower().strip() if condition.get("type") else ""
        if condition_type == "percentage" and field in ["sum_of_agent_achieved", "sum_of_team_achieved"]:
            # Calculate achievement percentage and compare
            target_field = "sum_of_agent_sales_target" if field == "sum_of_agent_achieved" else "sum_of_team_sales_target"
            achieved = performance_data.get(field, 0)
            target = performance_data.get(target_field, 0)
            
            # CRITICAL FIX: Team target mismatch detection for percentage conditions
            if field == "sum_of_team_achieved":
                # Ensure we're using team target, not agent target
                team_target = performance_data.get("sum_of_team_sales_target")
                agent_target = performance_data.get("sum_of_agent_sales_target")
                
                if (team_target is None or (isinstance(team_target, (int, float)) and float(team_target) == 0)):
                    if agent_target is not None and float(agent_target) > 0:
                        print(f"❌ BLOCKED: Team percentage condition using agent target instead of team target")
                        print(f"  Field: sum_of_team_achieved (team achieved) = {achieved}")
                        print(f"  Missing: sum_of_team_sales_target (team target)")
                        print(f"  Found: sum_of_agent_sales_target = {agent_target} (agent target - wrong!)")
                        print(f"  Reason: Cannot calculate team achievement percentage using agent target")
                        print(f"  Solution: Ensure team targets exist in database for team-based percentage incentives")
                        return False
            
            # CRITICAL FIX: Block zero or invalid targets from passing
            # NOTE: This check is also performed in the final validation block below for consistency
            # This is intentional defensive programming - multiple validation layers for financial safety
            if target is None or float(target) <= 0:
                print(f"❌ BLOCKED: Zero or invalid target for '{field}' - target={target}, condition automatically False")
                print(f"  Reason: In finance, zero target means no target set - incentive condition must fail")
                return False
            
            achievement_percentage = (float(achieved) / float(target)) * 100.0
            percentage_value = float(value) if value else 0
            print(f"✅ Percentage type on achievement field '{field}': {achievement_percentage}% {operator} {percentage_value}%")
            print(f"  Using target: {target_field} = {target}")
            return evaluate_operator(achievement_percentage, operator, percentage_value)
        
        # Handle field-to-field comparison
        original_value_str = value  # Keep original for target field detection
        value_is_target_field = False  # Track if value came from target field
        
        if isinstance(value, str) and value in performance_data:
            # Check if this is a target field reference
            target_fields = ["sum_of_agent_sales_target", "sum_of_team_sales_target"]
            if value in target_fields:
                value_is_target_field = True
                # CRITICAL FINANCIAL SAFETY: Block zero or missing targets IMMEDIATELY
                # This check happens BEFORE any comparison logic to ensure financial safety
                target_value = performance_data.get(value)
                if target_value is None:
                    print(f"❌ BLOCKED: Target is zero or missing for target-based comparison")
                    print(f"  Target field: {value} = None (missing)")
                    print(f"  Condition field: {field} = {performance_data.get(field, 0)}")
                    print(f"  Condition: {field} {operator} {value}")
                    print(f"  Reason: In finance, zero target means no target set - incentive condition must fail")
                    print(f"  Business Rule: Any comparison against target requires target > 0")
                    return False
                try:
                    if float(target_value) <= 0:
                        print(f"❌ BLOCKED: Target is zero or missing for target-based comparison")
                        print(f"  Target field: {value} = {target_value}")
                        print(f"  Condition field: {field} = {performance_data.get(field, 0)}")
                        print(f"  Condition: {field} {operator} {value}")
                        print(f"  Reason: In finance, zero target means no target set - incentive condition must fail")
                        print(f"  Business Rule: Any comparison against target requires target > 0")
                        return False
                except (ValueError, TypeError):
                    print(f"❌ BLOCKED: Invalid target value type for target-based comparison")
                    print(f"  Target field: {value} = {target_value}")
                    print(f"  Condition field: {field} = {performance_data.get(field, 0)}")
                    print(f"  Condition: {field} {operator} {value}")
                    return False
            value = performance_data[value]
        
        # CRITICAL FIX: Team target mismatch detection (before zero target check)
        # If using team achieved but only agent target exists, that's wrong
        if field == "sum_of_team_achieved":
            team_target = performance_data.get("sum_of_team_sales_target")
            agent_target = performance_data.get("sum_of_agent_sales_target")
            
            # Check if we're comparing against target
            target_fields = ["sum_of_agent_sales_target", "sum_of_team_sales_target"]
            is_target_comparison = (
                value_is_target_field or
                (isinstance(original_value_str, str) and original_value_str in target_fields) or
                condition_type == "percentage"
            )
            
            if is_target_comparison:
                if team_target is None or (isinstance(team_target, (int, float)) and float(team_target) == 0):
                    if agent_target is not None and float(agent_target) > 0:
                        print(f"❌ BLOCKED: Team incentive using agent target instead of team target")
                        print(f"  Field: sum_of_team_achieved (team achieved)")
                        print(f"  Missing: sum_of_team_sales_target (team target)")
                        print(f"  Found: sum_of_agent_sales_target = {agent_target} (agent target - wrong!)")
                        print(f"  Reason: Cannot compare team achieved against agent target - data mismatch")
                        print(f"  Solution: Ensure team targets exist in database for team-based incentives")
                        return False
        
        # Handle None values
        if actual is None:
            # For numeric fields, treat None as 0
            try:
                float(value)  # If value is numeric, treat missing actual as 0
                actual = 0
            except (ValueError, TypeError):
                return False
        
        # CRITICAL FIX: Final check before evaluation - block zero target for target-based comparisons
        # This is the last line of defense before the actual comparison happens
        # NOTE: This validation also appears in the percentage block above - this is intentional defensive programming
        # Multiple validation layers ensure financial safety even if one check is missed
        target_fields = ["sum_of_agent_sales_target", "sum_of_team_sales_target"]
        achieved_fields = ["sum_of_agent_achieved", "sum_of_team_achieved"]
        
        # ARCHITECTURAL DECISION: Only validate target if we're actually comparing against target
        # This allows pure volume-based incentives (e.g., sum_of_agent_achieved > 500000) without requiring targets
        # If business rule requires ALL achieved-based incentives to have targets, change is_target_comparison logic below
        if field in achieved_fields:
            target_field = "sum_of_agent_sales_target" if field == "sum_of_agent_achieved" else "sum_of_team_sales_target"
            
            # Determine if this is a target-based comparison
            # Check if value is a target field reference or if we're comparing against target
            # CRITICAL: This detection must catch ALL cases where we're comparing achieved vs target
            is_target_comparison = (
                value_is_target_field or  # Value was originally a target field string reference
                (isinstance(original_value_str, str) and original_value_str in target_fields) or
                (isinstance(value, (int, float)) and target_field in performance_data and 
                 abs(float(value) - float(performance_data.get(target_field, 0))) < 0.01)  # Value matches target
            )
            
            # ADDITIONAL SAFETY: If value is numeric and target exists, check if they match
            # This catches edge cases where target comparison detection might fail
            if not is_target_comparison and isinstance(value, (int, float)) and target_field in performance_data:
                target_val = performance_data.get(target_field)
                if target_val is not None:
                    try:
                        if abs(float(value) - float(target_val)) < 0.01:
                            is_target_comparison = True
                    except (ValueError, TypeError):
                        pass
            
            # Only validate target if we're actually comparing against it
            # For pure volume-based incentives (e.g., sum_of_agent_achieved > 500000), target is not required
            if is_target_comparison:
                target_value = performance_data.get(target_field)
                
                # HARD BLOCK: Financial safety - zero or missing targets MUST fail
                # This applies to ANY comparison operator (>=, <=, >, <, =) when comparing achieved vs target
                # No warnings, no exceptions - immediate False return
                if target_value is None:
                    print(f"❌ BLOCKED: Target '{target_field}' is missing")
                    print(f"  Achieved: {actual}")
                    print(f"  Target: None")
                    print(f"  Condition: {field} {operator} {original_value_str if isinstance(original_value_str, str) else value}")
                    print(f"  Financial Rule: Target must be > 0")
                    return False
                
                try:
                    target_float = float(target_value)
                    if target_float <= 0:
                        print(f"❌ BLOCKED: Target is zero or negative for target-based comparison")
                        print(f"  Achieved: {actual}")
                        print(f"  Target: {target_float}")
                        print(f"  Condition: {field} {operator} {original_value_str if isinstance(original_value_str, str) else value}")
                        print(f"  Financial Rule: Target must be > 0")
                        return False
                except (ValueError, TypeError):
                    print(f"❌ BLOCKED: Invalid target type")
                    print(f"  Target field: {target_field} = {target_value}")
                    print(f"  Achieved: {actual}")
                    return False
            # Note: If is_target_comparison is False, this is a pure volume-based incentive
            # (e.g., sum_of_agent_achieved > 500000) and target validation is not required
        
        # FINAL SAFETY CHECK: Even if target comparison wasn't detected above, if value equals target and target is 0, block it
        # This is a last-resort check to ensure zero targets never pass, even if detection logic fails
        if field in achieved_fields:
            target_field = "sum_of_agent_sales_target" if field == "sum_of_agent_achieved" else "sum_of_team_sales_target"
            if target_field in performance_data:
                target_val = performance_data.get(target_field)
                if target_val is not None:
                    try:
                        target_float = float(target_val)
                        # If target is 0 and value equals target, this is a zero-target comparison - block it
                        if target_float <= 0 and isinstance(value, (int, float)) and abs(float(value) - target_float) < 0.01:
                            print(f"❌ BLOCKED: Zero target detected in final safety check")
                            print(f"  Achieved: {actual}")
                            print(f"  Target: {target_float}")
                            print(f"  Value: {value}")
                            print(f"  Condition: {field} {operator} {original_value_str if isinstance(original_value_str, str) else value}")
                            print(f"  Financial Rule: Target must be > 0")
                            return False
                    except (ValueError, TypeError):
                        pass
        
        # Evaluate condition
        return evaluate_operator(actual, operator, value)
        
    except Exception as e:
        print(f"ERROR in evaluate_single_condition: {e}")
        return False


def evaluate_filter_field(field, operator, value, agent_id):
    """
    Evaluate filter fields (role, team_role, etc.) from database.
    """
    try:
        if field == "team_role":
            if agent_id is None:
                return False
            
            from django.db import connection
            with connection.cursor() as cursor:
                value_lower = str(value).lower().strip()
                if value_lower in ["team lead", "team_lead", "manager", "lead"]:
                    cursor.execute("SELECT COUNT(*) FROM core_teams WHERE manager_id = %s AND deleted_at IS NULL", [agent_id])
                    result = cursor.fetchone()
                    return (result and result[0] > 0) if result else False
                elif value_lower in ["team member", "team_member", "member", "agent"]:
                    cursor.execute("SELECT COUNT(*) FROM core_team_users WHERE user_id = %s", [agent_id])
                    result = cursor.fetchone()
                    return (result and result[0] > 0) if result else False
                else:
                    return False
                    
        elif field in ("role", "role_id"):
            if agent_id is None:
                return False
            
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT role_id FROM core_users WHERE id = %s", [agent_id])
                result = cursor.fetchone()
                if result:
                    agent_role_id = result[0]
                    try:
                        comparison_value = int(value) if value is not None else None
                        return evaluate_operator(agent_role_id, operator, comparison_value)
                    except (ValueError, TypeError):
                        return False
                else:
                    return False
                    
        elif field == "agent_id":
            if agent_id is None:
                return False
            try:
                comparison_value = int(value) if value is not None else None
                return evaluate_operator(agent_id, operator, comparison_value)
            except (ValueError, TypeError):
                return False
        else:
            # Other filter fields (product, insurer, risk_type) are applied during aggregation
            # NOTE: This returns True because filter fields are validated during the aggregation phase,
            # not during condition evaluation. If this evaluator is reused without aggregation,
            # filter field conditions will pass by default - ensure aggregation is performed first.
            return True
            
    except Exception as e:
        print(f"ERROR in evaluate_filter_field: {e}")
        return False


def _detect_product_filter(block):
    """Detect if product filter is active in conditions."""
    try:
        if not isinstance(block, dict):
            return False
        
        # Check single condition
        if "field" in block:
            field = block.get("field")
            if field in ["product", "product_id", "native_product"]:
                return True
        
        # Check nested conditions
        if "conditions" in block:
            for cond in block.get("conditions", []):
                if _detect_product_filter(cond):
                    return True
        
        return False
    except:
        return False

def evaluate_operator(actual, operator, value):
    """
    Evaluate a comparison operator.
    
    Args:
        actual: Actual value
        operator: Operator string (=, >=, <=, >, <, !=, in, not in)
        value: Comparison value
    
    Returns:
        bool: True if condition is met, False otherwise
    """
    try:
        # Convert to comparable types
        # NOTE: This handles string numbers like "100" but will fall back to string comparison
        # for invalid strings like "100abc". This is intentional - allows flexible input while
        # maintaining type safety for valid numeric comparisons.
        try:
            actual_float = float(actual) if actual is not None else 0
            value_float = float(value) if value is not None else 0
            use_numeric = True
        except (ValueError, TypeError):
            # If conversion fails, fall back to string comparison
            # This handles edge cases like "100abc" gracefully
            use_numeric = False
        
        if operator == "=":
            if use_numeric:
                return abs(actual_float - value_float) < 0.01  # Float comparison tolerance
            return actual == value
        elif operator == ">=":
            if use_numeric:
                return actual_float >= value_float
            return actual >= value
        elif operator == "<=":
            if use_numeric:
                return actual_float <= value_float
            return actual <= value
        elif operator == ">":
            if use_numeric:
                return actual_float > value_float
            return actual > value
        elif operator == "<":
            if use_numeric:
                return actual_float < value_float
            return actual < value
        elif operator == "!=":
            if use_numeric:
                return abs(actual_float - value_float) >= 0.01
            return actual != value
        elif operator == "in":
            if isinstance(value, (list, tuple)):
                return actual in value
            return False
        elif operator == "not in":
            if isinstance(value, (list, tuple)):
                return actual not in value
            return True
        else:
            return False
            
    except Exception as e:
        print(f"ERROR in evaluate_operator: {e}")
        return False

