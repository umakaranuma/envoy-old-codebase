from mServices import QueryBuilderService

def resolve_native_product_id(policy_base_data, insurer_id=None, transaction_type_id=None):
    """
    Comprehensive function to resolve native_product_id from policy_base data.
    Handles all mapping scenarios: insurer_product_id, product_group_id, and direct product_id.
    
    Args:
        policy_base_data (dict): Data from policy_base containing product information
        insurer_id (int, optional): Insurer ID for commission setup matching
        transaction_type_id (int, optional): Transaction type for commission setup matching
        
    Returns:
        dict: {
            'native_product_id': int or None,
            'mapping_type': str,  # 'direct', 'insurer_mapped', 'group_mapped', 'commission_matched', 'fallback'
            'original_id': int,   # Original ID that was mapped
            'product_name': str,  # Name of the resolved product
            'error': str or None  # Error message if mapping failed
        }
    """
    
    result = {
        'native_product_id': None,
        'mapping_type': None,
        'original_id': None,
        'product_name': None,
        'error': None
    }
    
    try:
        # Extract data from policy_base
        product_id = policy_base_data.get('product_id')
        product_group_id = policy_base_data.get('product_group_id')
        
        print(f"DEBUG: Resolving native product - product_id: {product_id}, product_group_id: {product_group_id}")
        
        # Scenario 1: Direct native_product_id (already in core_products)
        if product_id:
            native_product = (
                QueryBuilderService("core_products")
                .select("id", "name")
                .where("id", product_id)
                .first()
            )
            
            if native_product:
                result.update({
                    'native_product_id': native_product['id'],
                    'mapping_type': 'direct',
                    'original_id': product_id,
                    'product_name': native_product['name']
                })
                print(f"DEBUG: Direct native product found: {native_product['name']} (ID: {native_product['id']})")
                return result
        
        # Scenario 2: Map insurer_product_id to native_product_id
        if product_id:
            print(f"DEBUG: Attempting to map insurer_product_id {product_id} to native_product_id")
            
            # Try vendor product mapping
            vendor_mapping = (
                QueryBuilderService("core_product_vendor_products as cpvp")
                .leftJoin("core_products as cp", "cp.id", "cpvp.product_id")
                .select("cpvp.product_id as native_product_id", "cp.name as product_name")
                .where("cpvp.vendor_product_id", product_id)
                .whereNotNull("cp.id")
                .first()
            )
            
            if vendor_mapping:
                result.update({
                    'native_product_id': vendor_mapping['native_product_id'],
                    'mapping_type': 'insurer_mapped',
                    'original_id': product_id,
                    'product_name': vendor_mapping['product_name']
                })
                print(f"DEBUG: Mapped insurer_product_id {product_id} to native_product_id {vendor_mapping['native_product_id']} ({vendor_mapping['product_name']})")
                return result
        
        # Scenario 3: Use product_group_id to find native product
        if product_group_id:
            print(f"DEBUG: Using product_group_id {product_group_id} to find native product")
            
            # If we have commission setup parameters, try to find a product that matches commission setup
            if insurer_id and transaction_type_id:
                commission_matched_product = find_commission_matched_product(
                    product_group_id, insurer_id, transaction_type_id
                )
                if commission_matched_product:
                    result.update({
                        'native_product_id': commission_matched_product['id'],
                        'mapping_type': 'commission_matched',
                        'original_id': product_group_id,
                        'product_name': commission_matched_product['name']
                    })
                    print(f"DEBUG: Found commission-matched product: {commission_matched_product['name']} (ID: {commission_matched_product['id']})")
                    return result
            
            # Fallback: Get first available product from group
            group_product = (
                QueryBuilderService("core_product_group_products as cpgp")
                .leftJoin("core_products as cp", "cp.id", "cpgp.product_id")
                .select("cpgp.product_id", "cp.name as product_name")
                .where("cpgp.product_group_id", product_group_id)
                .whereNotNull("cp.id")
                .first()
            )
            
            if group_product:
                result.update({
                    'native_product_id': group_product['product_id'],
                    'mapping_type': 'group_mapped',
                    'original_id': product_group_id,
                    'product_name': group_product['product_name']
                })
                print(f"DEBUG: Using first product from group: {group_product['product_name']} (ID: {group_product['product_id']})")
                return result
        
        # Scenario 4: Fallback - try to find any product that has commission setup
        if insurer_id and transaction_type_id:
            fallback_product = find_fallback_commission_product(insurer_id, transaction_type_id)
            if fallback_product:
                result.update({
                    'native_product_id': fallback_product['id'],
                    'mapping_type': 'fallback',
                    'original_id': None,
                    'product_name': fallback_product['name']
                })
                print(f"DEBUG: Using fallback commission product: {fallback_product['name']} (ID: {fallback_product['id']})")
                return result
        
        # If all scenarios fail
        result['error'] = f"Could not resolve native product ID. product_id: {product_id}, product_group_id: {product_group_id}"
        print(f"ERROR: {result['error']}")
        return result
        
    except Exception as e:
        result['error'] = f"Error resolving native product ID: {str(e)}"
        print(f"ERROR: {result['error']}")
        return result


def find_commission_matched_product(product_group_id, insurer_id, transaction_type_id):
    """
    Find a product from the product group that has a commission setup for the given insurer and transaction type.
    
    Args:
        product_group_id (int): Product group ID
        insurer_id (int): Insurer ID
        transaction_type_id (int): Transaction type ID
        
    Returns:
        dict or None: Product data if found, None otherwise
    """
    try:
        # Find products in the group that have commission setups
        commission_products = (
            QueryBuilderService("core_product_group_products as cpgp")
            .leftJoin("core_products as cp", "cp.id", "cpgp.product_id")
            .leftJoin("crmf_commission_setups as cs", "cs.product_id", "cp.id")
            .select("cp.id", "cp.name")
            .where("cpgp.product_group_id", product_group_id)
            .where("cs.insurer_id", insurer_id)
            .where("cs.transaction_type", transaction_type_id)
            .whereNotNull("cp.id")
            .whereNull("cs.deleted_at")
            .first()
        )
        
        return commission_products
        
    except Exception as e:
        print(f"ERROR: Failed to find commission-matched product: {str(e)}")
        return None


def find_fallback_commission_product(insurer_id, transaction_type_id):
    """
    Find any product that has a commission setup for the given insurer and transaction type.
    This is used as a last resort fallback.
    
    Args:
        insurer_id (int): Insurer ID
        transaction_type_id (int): Transaction type ID
        
    Returns:
        dict or None: Product data if found, None otherwise
    """
    try:
        fallback_product = (
            QueryBuilderService("crmf_commission_setups as cs")
            .leftJoin("core_products as cp", "cp.id", "cs.product_id")
            .select("cp.id", "cp.name")
            .where("cs.insurer_id", insurer_id)
            .where("cs.transaction_type", transaction_type_id)
            .whereNotNull("cp.id")
            .whereNull("cs.deleted_at")
            .first()
        )
        
        return fallback_product
        
    except Exception as e:
        print(f"ERROR: Failed to find fallback commission product: {str(e)}")
        return None


def validate_commission_setup_exists(native_product_id, insurer_id, transaction_type_id):
    """
    Validate that a commission setup exists for the resolved native product.
    
    Args:
        native_product_id (int): Native product ID
        insurer_id (int): Insurer ID
        transaction_type_id (int): Transaction type ID
        
    Returns:
        bool: True if commission setup exists, False otherwise
    """
    try:
        commission_setup = (
            QueryBuilderService("crmf_commission_setups")
            .where("product_id", native_product_id)
            .where("insurer_id", insurer_id)
            .where("transaction_type", transaction_type_id)
            .whereNull("deleted_at")
            .first()
        )
        
        return commission_setup is not None
        
    except Exception as e:
        print(f"ERROR: Failed to validate commission setup: {str(e)}")
        return False


def get_product_mapping_summary(policy_base_data, insurer_id=None, transaction_type_id=None):
    """
    Get a comprehensive summary of product mapping for debugging and reporting.
    
    Args:
        policy_base_data (dict): Policy base data
        insurer_id (int, optional): Insurer ID
        transaction_type_id (int, optional): Transaction type ID
        
    Returns:
        dict: Comprehensive mapping summary
    """
    result = resolve_native_product_id(policy_base_data, insurer_id, transaction_type_id)
    
    # Add additional information
    result['policy_base_data'] = {
        'product_id': policy_base_data.get('product_id'),
        'product_group_id': policy_base_data.get('product_group_id'),
        'insurer_id': policy_base_data.get('insurer_id')
    }
    
    result['commission_setup_exists'] = False
    if result['native_product_id'] and insurer_id and transaction_type_id:
        result['commission_setup_exists'] = validate_commission_setup_exists(
            result['native_product_id'], insurer_id, transaction_type_id
        )
    
    return result
