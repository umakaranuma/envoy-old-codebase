# your_app/management/commands/seed_crmp_crm_data.py

from django.core.management.base import BaseCommand
from envoy_bu_policy_api.policy.models import EndorsementType, CoverageType, RequestType, PaymentPlan,ReasonCode


class Command(BaseCommand):
    help = 'Seed crmp_ and crm_ tables'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding CRMP & CRM tables...")

        # 1. Endorsement Types
        etypes = ["Additions", "Refund", "Cancellations", "Non-Financials"]
        for name in etypes:
            EndorsementType.objects.update_or_create(name=name)

        # 2. Endorsement Reason Codes
        reasons = [
            ("ADD01", "Adding a dependent", "Additions"),
            ("ADD02", "Plan upgrade", "Additions"),
            ("REF01", "Policy refund due to cancellation", "Refund"),
            ("REF02", "Excess premium payment refund", "Refund"),
            ("CAN01", "Customer requested cancellation", "Cancellations"),
            ("CAN02", "Policy cancelled due to non-payment", "Cancellations"),
            ("NF01", "Update address", "Non-Financials"),
            ("NF02", "Correction of personal details", "Non-Financials"),
        ]
        for code, desc, et_name in reasons:
            et = EndorsementType.objects.get(name=et_name)
            ReasonCode.objects.update_or_create(
                code=code,
                defaults={"description": desc, "endorsement_type": et}
            )

        # 3. Coverage Types
        for name, desc in [
            ("Basic Coverage", "Basic plan covering essential services."),
            ("Standard Coverage", "Standard plan with additional benefits."),
            ("Premium Coverage", "Full coverage with premium features."),
        ]:
            CoverageType.objects.update_or_create(name=name, defaults={"description": desc})

        # 4. Request Types
        for name, desc in [
            ("New Request", "Request for new service."),
            ("Renewal", "Request to renew existing service."),
            ("Cancellation", "Request to cancel the service."),
        ]:
            RequestType.objects.update_or_create(name=name, defaults={"description": desc})

        # 5. Payment Plans
        for name, desc, duration in [
            ("Monthly", "Monthly payment plan.", 1),
            ("Quarterly", "Quarterly payment plan.", 3),
            ("Annually", "Annual payment plan.", 12),
        ]:
            PaymentPlan.objects.update_or_create(name=name, defaults={"description": desc, "duration_months": duration})

        self.stdout.write(self.style.SUCCESS(" crmp_ & crm_ tables seeded successfully"))
