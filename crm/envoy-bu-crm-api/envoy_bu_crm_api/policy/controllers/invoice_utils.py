from envoy_bu_crm_api.service import handle_entity
from datetime import datetime
from decimal import Decimal
from mServices import QueryBuilderService
from envoy_bu_crm_api.policy.models.crmp_request_policy_invoices import RequestPolicyInvoice
from envoy_bu_crm_api.policy.models.crmp_request_policies import RequestPolicy
from envoy_bu_crm_api.policy.models.crmp_issued_policies import IssuedPolicy
from envoy_bu_crm_api.policy.models.crmp_endorsements_details import Endorsement
from envoy_bu_crm_api.policy.models.crmp_endorsement_request import EndorsementRequest

def generate_invoice_for_request_policy(policy_id, is_update=False, user=None):
    instance = RequestPolicy.objects.get(id=policy_id)
    invoice, created = RequestPolicyInvoice.objects.update_or_create(
        request_policy=instance, defaults={"invoice_type": "request"}
    )
    invoice.invoice_type = "request"
    invoice.total_amount = Decimal("0.00")  # instance.policy_document_size or
    invoice.paid_amount = Decimal("0.00")
    invoice.outstanding_amount = invoice.total_amount
    invoice.remarks = "Updated" if is_update or not created else "Created"

    # Handle entity creation or update
    entity_data = {"type": "invoice", "approvel_status": False}
    entity_id = handle_entity(entity_data, entity_id=user.entity_id if is_update else None, user=user)
    invoice.entity_id = entity_id

    invoice.save()
    return invoice

def generate_invoice_for_issued_policy(issued_id, is_update=False, user=None):
    instance = IssuedPolicy.objects.get(id=issued_id)
    invoice, created = RequestPolicyInvoice.objects.update_or_create(
        issued_policy=instance, defaults={"invoice_type": "issued"}
    )
    invoice.invoice_type = "issued"
    invoice.total_amount = Decimal(str(instance.premium_amount or "0.00")).quantize(Decimal('.01'))
    # Only set initial amounts if this is a new invoice
    if created:
        invoice.paid_amount = Decimal("0.00")
        invoice.outstanding_amount = invoice.total_amount
    invoice.remarks = "Updated" if is_update or not created else "Created"

    # Handle entity creation or update
    entity_data = {"type": "invoice", "approvel_status": False}
    entity_id = handle_entity(entity_data, entity_id=invoice.entity_id if is_update else None, user=user)
    invoice.entity_id = entity_id

    invoice.save()
    return invoice

def generate_invoice_for_endorsement(endorsement_id, is_update=False, user=None, invoice_data=None):
    instance = Endorsement.objects.get(id=endorsement_id)
    instance_req = instance.endorsement_request
    
    invoice, created = RequestPolicyInvoice.objects.update_or_create(
        endorsement=instance, defaults={"invoice_type": "endorsement"}
    )
    
    invoice.invoice_type = "endorsement"
    
    if invoice_data:
        # Use the calculated amounts from invoice_data
        invoice.total_amount = Decimal(str(invoice_data.get("total_amount", "0.00"))).quantize(Decimal('.01'))
        # Only set paid and outstanding for new invoices or when explicitly provided
        if created or ("paid_amount" in invoice_data and "outstanding_amount" in invoice_data):
            invoice.paid_amount = Decimal(str(invoice_data.get("paid_amount", "0.00"))).quantize(Decimal('.01'))
            invoice.outstanding_amount = Decimal(str(invoice_data.get("outstanding_amount", "0.00"))).quantize(Decimal('.01'))
    else:
        # Fallback to request amount if no invoice_data provided
        invoice.total_amount = Decimal(str(instance_req.cover_value or "0.00")).quantize(Decimal('.01'))
        # Only set initial amounts if this is a new invoice
        if created:
            invoice.paid_amount = Decimal("0.00")
            invoice.outstanding_amount = invoice.total_amount
    
    invoice.issued_policy_id = instance_req.issued_policy_id or ''
    invoice.remarks = "Updated" if is_update or not created else "Created"
    
    # Handle entity creation or update
    entity_data = {"type": "invoice", "approvel_status": False}
    entity_id = handle_entity(entity_data, entity_id=invoice.entity_id if is_update else None, user=user)
    invoice.entity_id = entity_id

    invoice.save()
    return invoice

def generate_invoice_for_endorsement_request(endorsement_request_id, is_update=False, user=None):
    instance = EndorsementRequest.objects.get(id=endorsement_request_id)
    invoice, created = RequestPolicyInvoice.objects.update_or_create(
        endorsement_request=instance, defaults={}
    )
    invoice.invoice_type = "endorsement_request"
    invoice.total_amount = Decimal(str(instance.cover_value or "0.00")).quantize(Decimal('.01'))
    # Only set initial amounts if this is a new invoice
    if created:
        invoice.paid_amount = Decimal("0.00")
        invoice.outstanding_amount = invoice.total_amount
    invoice.remarks = "Updated" if is_update or not created else "Created"

    # Handle entity creation or update
    entity_data = {"type": "invoice", "approvel_status": False}
    entity_id = handle_entity(entity_data, entity_id=invoice.entity_id if is_update else None, user=user)
    invoice.entity_id = entity_id

    invoice.save()
    return invoice

def update_invoice_payment_details(invoice_id, paid_amount):
    """Update invoice totals after a payment"""
    if not invoice_id:
        return
        
    invoice = RequestPolicyInvoice.objects.get(id=invoice_id)
    
    # Convert amounts to Decimal for accurate calculations
    paid_amount = Decimal(str(paid_amount)).quantize(Decimal('.01'))
    current_paid = Decimal(str(invoice.paid_amount or "0.00")).quantize(Decimal('.01'))
    total_amount = Decimal(str(invoice.total_amount or "0.00")).quantize(Decimal('.01'))
    
    # Update paid amount
    new_paid_amount = (current_paid + paid_amount).quantize(Decimal('.01'))
    
    # Calculate new outstanding amount
    new_outstanding = (total_amount - new_paid_amount).quantize(Decimal('.01'))
    
    # Update invoice
    invoice.paid_amount = new_paid_amount
    invoice.outstanding_amount = new_outstanding
    invoice.save()
