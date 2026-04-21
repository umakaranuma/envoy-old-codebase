# your_app/management/commands/seed_statuses.py

from django.core.management.base import BaseCommand
from core_models.core_models import Status


class Command(BaseCommand):
    help = 'Seed all statuses in core_status table using type+module as immutable lookup'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding statuses...")

        statuses = [
            # Quotation statuses
            ("DRAFT", "Quotation is being prepared", "quotation_draft", "quotation", "#6c757d", 1),
            ("SENT", "Quotation has been sent", "quotation_sent", "quotation", "#0E7090", 2),
            ("INPROGRESS", "Client accepted the quotation", "quotation_inprogress", "quotation", "#175CD3", 3),
            ("REJECTED", "Client rejected the quotation", "quotation_rejected", "quotation", "#B42318", 4),
            ("PENDING", "Pending quotation", "quotation_pending", "quotation", "#B54708", 5),
            ("CONFIRMED", "Confirmed quotation", "quotation_confirmed", "quotation", "#067647", 6),
            ("EXPIRED", "Expired quotation", "quotation_expired", "quotation", "#344054", 
            7),

            # Policy statuses
            ("DRAFT", "policyStatus", "policy_draft", "policy", "#6c757d", 0),
            ("PENDING ISSUANCE", "policyStatus", "pol_pending_iss", "policy", "#B54708", 1),
            ("ACTIVE", "policyStatus", "policy_active", "policy", "#067647", 2),
            ("DUE FOR RENEWAL", "policyStatus", "pol_due_renewal", "policy", "#175CD3", 3),
            ("EXPIRED", "policyStatus", "policy_expired", "policy", "#344054", 4),
            ("RENEWAL IN PROGRESS", "policyStatus", "pol_renewal_progress", "policy", "#0E7090", 5),
            ("CANCELLED", "policyStatus", "policy_cancelled", "policy", "#B42318", 6),
            ("RENEWED", "policyStatus", "policy_renewed", "policy", "#175CD3", 7),

            # Endorsement statuses
            ("SETTLED", "EndorsementStatus", "endorsement_settled", "policy", "#067647", 1),
            ("PENDING", "EndorsementStatus", "endorsement_pending", "policy", "#B54708", 2),

            # Payment statuses
            ("PENDING", "Payment is awaiting confirmation", "payment_pending", "payment", "#B54708", 1),
            ("PARTIALLY PAID", "Payment is partially settled", "pay_partially_paid", "payment", "#0E7090", 2),
            ("PAID", "Payment is completed", "payment_paid", "payment", "#067647", 3),
            ("FAILED", "Payment has failed", "payment_failed", "payment", "#dc3545", 4),
            ("REFUNDED", "Payment was refunded", "payment_refunded", "payment", "#6c757d", 5),

            # Invoice statuses
            ("PENDING", "Invoice is in draft", "invoice_pending", "invoice", "#175CD3", 1),
            ("PARTIALLY PAID", "Invoice has been sent", "inv_partially_paid", "invoice", "#0E7090", 2),
            ("PAID", "Invoice has been viewed", "invoice_paid", "invoice", "#067647", 3),
            ("OVERDUE", "Invoice payment is overdue", "invoice_overdue", "invoice", "#B54708", 4),
            ("CANCELLED", "Invoice was cancelled", "invoice_cancelled", "invoice", "#B42318", 5),
            ("REFUNDED", "Invoice was refunded", "invoice_refunded", "invoice", "#363F72", 6),

            # Claim statuses
            ("DRAFT", "Claim is being drafted by the user", "Claim_draft", "claim", "#344054", 1),
            ("NOTIFIED", "Claim is being drafted by the user", "Claim_notified", "claim", "#363F72", 2),
            ("EVALUATED", "Claim has been submitted for review", "Claim_submitted", "claim", "#0E7090", 3),
            ("APPROVED", "Claim has been approved after evaluation", "Claim_approved", "claim", "#228b22", 4),
            ("SETTLED", "Claim has been settled and closed", "Claim_settled", "claim", "#067647", 5),
            ("REJECTED", "Claim has been rejected", "Claim_rejected", "claim", "#B42318", 6),

            # Brokerage Commission statuses
            # Statuses are based on payment that brokerage receives from insurer
            ("PENDING", "No commission has received yet since there were no settlements done by the customer", "brkg_comm_pending", "finance", "#B54708", 1),
            ("PARTIALLY RECEIVED", "Customer has done a part payment so the insurer has paid us partially", "brkg_comm_part_recv", "finance", "#175CD3", 2),
            ("RECEIVED IN FULL", "Customer has done the complete payment and the commission is received in full", "brkg_comm_recv_full", "finance", "#067647", 3),

            # Agent Commission statuses
            # Statuses are based on payment made to agent by broker
            ("PENDING", "Broker might or might not have received brokerage commission but hasn't done any settlements to the agent", "agent_comm_pending", "finance", "#B54708", 1),
            ("PARTIALLY PAID", "Broker might or might not have received brokerage commission and has done partial settlements to the agent", "agent_comm_part_paid", "finance", "#175CD3", 2),
            ("FULLY PAID", "Broker might or might not have received brokerage commission and has done the full settlement to the agent", "agent_comm_full_paid", "finance", "#067647", 3),
        ]

        created_count = 0
        updated_count = 0
        migrated_count = 0

        for name, desc, typ, mod, color, idx in statuses:
            # Step 1: Try to find by type+module (new immutable lookup)
            status = Status.objects.filter(type=typ, module=mod).first()
            
            if status:
                # Status exists with correct type+module, just update fields
                status.name = name
                status.description = desc
                status.color = color
                status.sort_index = idx
                status.save()
                updated_count += 1
                self.stdout.write(f"   ↻ Updated: {name} ({typ}) in {mod}")
            else:
                # Step 2: Check if old status exists with name+module (old pattern)
                old_status = Status.objects.filter(name=name, module=mod).first()
                
                if old_status:
                    # Migrate old status: update its type to the new immutable value
                    old_status.type = typ
                    old_status.description = desc
                    old_status.color = color
                    old_status.sort_index = idx
                    old_status.save()
                    migrated_count += 1
                    self.stdout.write(f"   ⟲ Migrated: {name} ({typ}) in {mod} (updated from old pattern)")
                else:
                    # Step 3: Create new status
                    Status.objects.create(
                        name=name,
                        description=desc,
                        type=typ,
                        module=mod,
                        color=color,
                        sort_index=idx
                    )
                    created_count += 1
                    self.stdout.write(f"   ✓ Created: {name} ({typ}) in {mod}")

        self.stdout.write(self.style.SUCCESS(
            f"\nStatus seeding completed:\n"
            f"  • {created_count} created\n"
            f"  • {updated_count} updated\n"
            f"  • {migrated_count} migrated from old pattern"
        ))

