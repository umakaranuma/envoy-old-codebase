from mServices import QueryBuilderService
from .product_mapping_utils import resolve_native_product_id, validate_commission_setup_exists

def fix_invoice_product_mappings(batch_size=100, dry_run=True):
    """
    Fix product_id mappings for existing invoices that have incorrect product_id values.
    This function identifies invoices with invalid product_id values and attempts to fix them.
    
    Args:
        batch_size (int): Number of invoices to process at once
        dry_run (bool): If True, only identify issues without fixing them
        
    Returns:
        dict: Summary of fixes applied
    """
    
    summary = {
        'total_invoices_checked': 0,
        'invalid_product_ids': 0,
        'successful_fixes': 0,
        'failed_fixes': 0,
        'errors': []
    }
    
    try:
        print(f"Starting invoice product mapping fix (dry_run={dry_run})")
        
        # Get invoices with potentially invalid product_id values
        invalid_invoices = get_invoices_with_invalid_product_ids(batch_size)
        summary['total_invoices_checked'] = len(invalid_invoices)
        summary['invalid_product_ids'] = len(invalid_invoices)
        
        print(f"Found {len(invalid_invoices)} invoices with potentially invalid product_id values")
        
        for invoice in invalid_invoices:
            try:
                fix_result = fix_single_invoice_product_mapping(invoice, dry_run)
                
                if fix_result['success']:
                    summary['successful_fixes'] += 1
                    print(f"✅ Fixed invoice {invoice['id']}: {fix_result['message']}")
                else:
                    summary['failed_fixes'] += 1
                    summary['errors'].append(f"Invoice {invoice['id']}: {fix_result['error']}")
                    print(f"❌ Failed to fix invoice {invoice['id']}: {fix_result['error']}")
                    
            except Exception as e:
                summary['failed_fixes'] += 1
                summary['errors'].append(f"Invoice {invoice['id']}: {str(e)}")
                print(f"❌ Error processing invoice {invoice['id']}: {str(e)}")
        
        print(f"Fix summary: {summary['successful_fixes']} successful, {summary['failed_fixes']} failed")
        return summary
        
    except Exception as e:
        summary['errors'].append(f"Batch processing error: {str(e)}")
        print(f"ERROR: Batch processing failed: {str(e)}")
        return summary


def get_invoices_with_invalid_product_ids(batch_size=100):
    """
    Get invoices that have product_id values that don't exist in core_products table.
    
    Args:
        batch_size (int): Maximum number of invoices to return
        
    Returns:
        list: List of invoice records with invalid product_id values
    """
    
    try:
        # Find invoices where product_id doesn't exist in core_products
        invalid_invoices = (
            QueryBuilderService("crmf_invoices as ci")
            .leftJoin("core_products as cp", "cp.id", "ci.product_id")
            .leftJoin("crmp_issued_policies as ip", "ip.id", "ci.issued_policy_id")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .select(
                "ci.id",
                "ci.product_id",
                "ci.insurer_id",
                "ci.issued_policy_id",
                "pb.product_group_id",
                "pb.insurer_id as policy_insurer_id"
            )
            .whereNull("cp.id")  # product_id doesn't exist in core_products
            .whereNotNull("ci.product_id")  # but product_id is not null
            .limit(batch_size)
            .get()
        )
        
        return invalid_invoices
        
    except Exception as e:
        print(f"ERROR: Failed to get invalid invoices: {str(e)}")
        return []


def fix_single_invoice_product_mapping(invoice, dry_run=True):
    """
    Fix product_id mapping for a single invoice.
    
    Args:
        invoice (dict): Invoice record with invalid product_id
        dry_run (bool): If True, only identify the fix without applying it
        
    Returns:
        dict: Result of the fix attempt
    """
    
    result = {
        'success': False,
        'message': '',
        'error': None,
        'old_product_id': invoice['product_id'],
        'new_product_id': None,
        'mapping_type': None
    }
    
    try:
        # Prepare policy base data for mapping
        policy_base_data = {
            'product_id': invoice['product_id'],
            'product_group_id': invoice.get('product_group_id'),
            'insurer_id': invoice.get('policy_insurer_id') or invoice.get('insurer_id')
        }
        
        # Resolve native product ID
        mapping_result = resolve_native_product_id(
            policy_base_data,
            invoice.get('insurer_id'),
            None  # We don't have transaction_type for existing invoices
        )
        
        if mapping_result['error']:
            result['error'] = f"Could not resolve native product: {mapping_result['error']}"
            return result
        
        new_product_id = mapping_result['native_product_id']
        mapping_type = mapping_result['mapping_type']
        
        # Validate that the new product_id exists in core_products
        product_exists = (
            QueryBuilderService("core_products")
            .where("id", new_product_id)
            .first()
        )
        
        if not product_exists:
            result['error'] = f"Resolved product_id {new_product_id} does not exist in core_products"
            return result
        
        # Apply the fix if not in dry run mode
        if not dry_run:
            update_result = (
                QueryBuilderService("crmf_invoices")
                .where("id", invoice['id'])
                .update({"product_id": new_product_id})
            )
            
            if not update_result:
                result['error'] = "Failed to update invoice product_id"
                return result
        
        result.update({
            'success': True,
            'new_product_id': new_product_id,
            'mapping_type': mapping_type,
            'message': f"Product ID {invoice['product_id']} → {new_product_id} via {mapping_type}"
        })
        
        return result
        
    except Exception as e:
        result['error'] = f"Error fixing invoice: {str(e)}"
        return result


def validate_invoice_product_mappings():
    """
    Validate all invoice product_id mappings and return a comprehensive report.
    
    Returns:
        dict: Validation report
    """
    
    report = {
        'total_invoices': 0,
        'valid_mappings': 0,
        'invalid_mappings': 0,
        'missing_product_ids': 0,
        'invalid_product_ids': 0,
        'commission_setup_issues': 0,
        'details': []
    }
    
    try:
        # Get all invoices with their product information
        all_invoices = (
            QueryBuilderService("crmf_invoices as ci")
            .leftJoin("core_products as cp", "cp.id", "ci.product_id")
            .leftJoin("crmp_issued_policies as ip", "ip.id", "ci.issued_policy_id")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .select(
                "ci.id",
                "ci.product_id",
                "ci.insurer_id",
                "ci.issued_policy_id",
                "pb.product_group_id",
                "cp.name as product_name",
                "cp.id as core_product_id"
            )
            .get()
        )
        
        report['total_invoices'] = len(all_invoices)
        
        for invoice in all_invoices:
            invoice_id = invoice['id']
            product_id = invoice['product_id']
            core_product_id = invoice['core_product_id']
            
            detail = {
                'invoice_id': invoice_id,
                'product_id': product_id,
                'status': 'valid',
                'issues': []
            }
            
            # Check if product_id is missing
            if not product_id:
                report['missing_product_ids'] += 1
                detail['status'] = 'invalid'
                detail['issues'].append('Missing product_id')
            
            # Check if product_id exists in core_products
            elif not core_product_id:
                report['invalid_product_ids'] += 1
                detail['status'] = 'invalid'
                detail['issues'].append(f'Product_id {product_id} does not exist in core_products')
            
            # Check if commission setup exists
            elif invoice.get('insurer_id'):
                commission_exists = validate_commission_setup_exists(
                    product_id, 
                    invoice['insurer_id'], 
                    None  # We don't have transaction_type for validation
                )
                
                if not commission_exists:
                    report['commission_setup_issues'] += 1
                    detail['issues'].append('No commission setup found')
            
            if detail['status'] == 'valid':
                report['valid_mappings'] += 1
            else:
                report['invalid_mappings'] += 1
            
            report['details'].append(detail)
        
        return report
        
    except Exception as e:
        print(f"ERROR: Validation failed: {str(e)}")
        return report


def get_product_mapping_statistics():
    """
    Get statistics about product mappings in the system.
    
    Returns:
        dict: Mapping statistics
    """
    
    stats = {
        'total_invoices': 0,
        'direct_mappings': 0,
        'insurer_mappings': 0,
        'group_mappings': 0,
        'invalid_mappings': 0,
        'missing_mappings': 0
    }
    
    try:
        # Get all invoices
        all_invoices = (
            QueryBuilderService("crmf_invoices")
            .select("id", "product_id")
            .get()
        )
        
        stats['total_invoices'] = len(all_invoices)
        
        for invoice in all_invoices:
            product_id = invoice['product_id']
            
            if not product_id:
                stats['missing_mappings'] += 1
                continue
            
            # Check if it's a direct mapping (exists in core_products)
            product_exists = (
                QueryBuilderService("core_products")
                .where("id", product_id)
                .first()
            )
            
            if product_exists:
                stats['direct_mappings'] += 1
            else:
                # Check if it's a vendor mapping
                vendor_mapping = (
                    QueryBuilderService("core_product_vendor_products")
                    .where("vendor_product_id", product_id)
                    .first()
                )
                
                if vendor_mapping:
                    stats['insurer_mappings'] += 1
                else:
                    stats['invalid_mappings'] += 1
        
        return stats
        
    except Exception as e:
        print(f"ERROR: Failed to get statistics: {str(e)}")
        return stats
