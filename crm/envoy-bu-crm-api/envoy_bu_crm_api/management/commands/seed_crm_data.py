

from django.core.management.base import BaseCommand
from envoy_bu_crm_api.sales.models import OpportunityStatus  # Replace with your actual model paths

class Command(BaseCommand):
    help = 'Seed crm_ prefixed tables'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding CRM tables...")

        opportunity_statuses = [
            (1, "LEAD", "initial stage", "opportunity_lead", "#344054", 1),
            (2, "PROSPECT", "initial stage", "opportunity_prospect", "#175CD3", 2),
            (3, "QUALIFIED", None, "opportunity_qualified", "#0E7090", 3),
            (4, "WON", None, "opportunity_won", "#067647", 4),
            (5, "LOSS", None, "opportunity_loss", "#B42318", 5),
        ]
        for id, name, desc, typ, color, idx in opportunity_statuses:
            OpportunityStatus.objects.update_or_create(
                id=id,
                defaults={
                    "name": name,
                    "description": desc,
                    "type": typ,
                    "color": color,
                    "sort_index": idx
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ crm_ tables seeded successfully"))
