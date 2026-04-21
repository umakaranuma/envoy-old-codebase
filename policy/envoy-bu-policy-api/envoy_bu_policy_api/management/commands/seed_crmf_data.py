# your_app/management/commands/seed_crmf_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from envoy_bu_policy_api.finance.models import (
    InvoiceType, TransactionType,
    RewardType, 
    ChartOfAccount, PerformanceMetric
)
from envoy_bu_policy_api.finance.models.crmf_commission_filed import CommissionFiled

class Command(BaseCommand):
    help = 'Seed crmf_ tables'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding CRMF tables...")

        # 1. Invoice Types
        for code, name, description in [
            ("NEW_BUSINESS", "New Business", "New policy issuance"),
            ("ADDITION", "Addition", "Additional coverage or premium"),
            ("RENEWAL", "Renewal", "Policy renewal"),
            ("REFUND", "Refund", "Refund issued"),
            ("CANCELLATIONS", "Cancellations", "Policy cancellation"),
            ("NON_FINANCIALS", "Non-Financials", "Transactions without financial impact"),
        ]:
            InvoiceType.objects.update_or_create(
                code=code,
                defaults={"name": name, "description": description}
            )

        # 2. Transaction Types
        for id, code, name, description in [
            (1, "NEW_BUSINESS", "New Business", "New policy issuance"),
            (2, "ADDITION", "Addition", "Additional coverage or premium"),
            (3, "RENEWAL", "Renewal", "Policy renewal"),
        ]:
            TransactionType.objects.update_or_create(
                id=id,
                defaults={"code": code, "name": name, "description": description}
            )

        # 3. Reward Types & Configs (fixed to match SQL data)
        reward_types = [
            # id, name, description,          reward_type, calculation_method
            (1, "Brokerage Revenue",          "% of brokerage",                     "fixed",    None),
            (2, "Total Premium",              "Based on premium collected",         "fixed",    None),
            (3, "New Customer Acquisition",   "Reward for each new customer added", "variable", "count_based"),
            (4, "Policy Renewal",             "Reward based on number of policies renewed", "variable", "percentage"),
            (5, "Team Performance",           "Reward based on team performance metrics",    "variable", "weighted_score"),
        ]

        for rid, name, desc, rtype, calc in reward_types:
            RewardType.objects.update_or_create(
                id=rid,
                defaults={
                    "name": name,
                    "description": desc,
                    "reward_type": rtype,
                    "calculation_method": calc,
                    "created_at": timezone.now(),   # keep if your model doesn't auto-set
                    "updated_at": timezone.now(),
                    "deleted_at": None,
                },
            )

        # 4. Performance Metrics
        PerformanceMetric.objects.update_or_create(
            id=1,
            defaults={"name": "Leads Converted", "description": "Number of leads converted", "created_at": timezone.now()}
        )
        PerformanceMetric.objects.update_or_create(
            id=2,
            defaults={"name": "Premium Closed", "description": "Total premium closed", "created_at": timezone.now()}
        )

        # 5. Chart of Accounts
        accounts = [
            ("10001", "Bank Account", "asset", "Tracks all actual payments received"),
            ("10002", "Accounts Receivable – Insurer", "asset", "Commission amounts due from insurer"),
            ("20005", "Commission Reversal Payable – Insurer", "liability", "Commission reversals due to insurer"),
            ("20003", "Commission Payable – Agent", "liability", "Commissions owed to agents"),
            ("40005", "Commission Income – New Business", "revenue", "Commission from new policies"),
            ("40006", "Commission Income – Renewals", "revenue", "Commission from renewals"),
            ("40007", "Commission Income – Endorsements", "revenue", "Commission from endorsements"),
            ("40008", "Commission Income – Adjusted", "revenue", "Commission reversal offset"),
            ("40009", "Service Charge Income", "revenue", "Service/admin charges from customers"),
            ("50001", "Agent Commission Expense", "expense", "Expenses related to agent commissions"),
        ]
        for acct_number, name, acct_type, desc in accounts:
            ChartOfAccount.objects.update_or_create(
                account_number=acct_number,
                defaults={"account_name": name, "account_type": acct_type, "description": desc}
            )

        # 6. Commission Fields
        commission_fields = [
            ("Brokerage Revenue Percent", "brokerage_revenue_percent"),
            ("Agent Commission Percent", "agent_commission_percent"),
            ("Bonus Commission Percent", "bonus_commission_percent"),
            ("Target Achievement Commission Percent", "target_achievement_commission_percent"),
            ("Commission Percent", "commission_percent"),
            ("Revised Commission Percent", "revised_commission_percent"),
        ]
        created_count = 0
        for name, attr in commission_fields:
            _, created = CommissionFiled.objects.update_or_create(
                attribute_name=attr,
                defaults={"name": name, "type": "decimal", "module": "commission"}
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f" crmf_ tables seeded successfully — including {created_count} commission fields"))
