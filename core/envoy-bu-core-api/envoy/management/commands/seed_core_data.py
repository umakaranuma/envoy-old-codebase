import json
from django.core.management.base import BaseCommand
from django.utils import timezone
from envoy.models import (
    TaskStatus, Currency, FlexField, SettingKey, Module,
    Status, NotificationType, Service, Action
)
from envoy.models.entity_approval_rule import EntityApprovalRule
from envoy.models.global_setting import GlobalSetting

class Command(BaseCommand):
    help = 'Seed all core_* tables including actions'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding core tables...")

        # 1. Task Statuses
        task_statuses = [
            (1, "TODO", "Todo", "task_todo", "#0E7090", 1),
            (2, "IN PROGRESS", "In Progress", "task_inprogress", "#175CD3", 2),
            (3, "DONE", "Done", "task_done", "#067647", 3),
        ]
        for id, name, desc, typ, color, idx in task_statuses:
            TaskStatus.objects.update_or_create(id=id, defaults={
                "name": name, "description": desc, "type": typ,
                "color": color, "sort_index": idx
            })

        # 2. Currencies
        Currency.objects.update_or_create(code="USD", defaults={
            "symbol": "$", "name": "US Dollar",
            "decimal_digits": 2, "rounding": 0
        })
        Currency.objects.update_or_create(code="LKR", defaults={
            "symbol": "Rs.", "name": "Sri Lankan Rupee",
            "decimal_digits": 2, "rounding": 0
        })

        # 3. Flex Fields
        FlexField.objects.update_or_create(
            entity_type="CUSTOMER", field_code="number_of_employees",
            defaults={
                "field_label": "Number of Employees",
                "data_type": "TEXT", "is_mandatory": False,
                "is_enabled": True, "is_fixed": True
            }
        )
        FlexField.objects.update_or_create(
            entity_type="CUSTOMER", field_code="br_no",
            defaults={
                "field_label": "BR NUMBER",
                "data_type": "TEXT", "is_mandatory": False,
                "is_enabled": True, "is_fixed": True
            }
        )

        # 4. Setting Keys
        setting_keys = [
            ("SALES_AGENT_ROLES", None, "sales_agent_roles"),
            ("OPPORTUNITY_CUSTOMER_REQUIRED_STAGE", None, "opportunity_customer_required_stage"),
            ("BASE_CURRENCY", None, "base_currency"),
            ("BASE_COUNTRY", None, "base_country"),
            ("COMMISSION_CONFIG", None, None),
            ("POLICY_LIFECYCLE_NOTIFICATIONS",
                "Covers everything related to your insurance policies...", "policy_lifecycle_notifications"),
            ("PAYMENTS_AND_REMINDERS",
                "Payment due reminders...", "payments_and_reminders"),
            ("ACCOUNT_AND_SECURITY",
                "Important alerts about your login...", "account_and_security"),
            ("PROMOTIONS_AND_UPDATES",
                "News, offers, and promotions...", "promotions_and_updates"),
            # Approval settings (policy / quotation request approvals)
            ("APPROVAL_PERMISSIONS",
                "Approval settings for policy and quotation requests",
                "approval_permissions"),
            ("CUSTOMER_CONFIG","Customer configuration settings", "customer_config"),
        ]
        for name, desc, attr in setting_keys:
            SettingKey.objects.update_or_create(
                name=name,
                defaults={"description": desc, "attribute_name": attr}
            )

        # 5. Modules
        crm_module, _ = Module.objects.update_or_create(key="CRM", defaults={"name": "CRM"})
        policy_module, _ = Module.objects.update_or_create(key="POLICY", defaults={"name": "Policy"})
        core_module, _ = Module.objects.update_or_create(key="CORE", defaults={"name": "Core"})

        # 6. Actions
        actions = [
            (crm_module.id, "TASK", "VIEW_ALL", True),
            (crm_module.id, "TASK", "VIEW", True),
            (crm_module.id, "TASK", "UPDATE", True),
            (crm_module.id, "TASK", "ADD", True),
            (crm_module.id, "TASK", "DELETE", True),

            (core_module.id, "USER", "VIEW_ALL", True),
            (core_module.id, "USER", "VIEW", True),
            (core_module.id, "USER", "UPDATE", True),
            (core_module.id, "USER", "ADD", True),
            (core_module.id, "USER", "DELETE", True),

            (core_module.id, "ROLE", "VIEW_ALL", True),
            (core_module.id, "ROLE", "VIEW", True),
            (core_module.id, "ROLE", "UPDATE", True),
            (core_module.id, "ROLE", "ADD", True),
            (core_module.id, "ROLE", "DELETE", True),
        ]
        for module_id, entity, action_name, can_be_permission in actions:
            Action.objects.update_or_create(
                module_id=module_id,
                entity=entity,
                action=action_name,
                defaults={"can_be_permission": can_be_permission}
            )

        # 7. Statuses (Quotation, Policy, Endorsement, Payment, Invoice)
        statuses = [
            # Quotation statuses
            ("REQUESTED ", "Quotation is being prepared", "quotation_draft", "quotation", "#6c757d", 1),
            ("SENT", "Quotation has been sent", "quotation_sent", "quotation", "#0E7090", 2),
            ("INPROGRESS", "Client accepted the quotation", "quotation_inprogress", "quotation", "#175CD3", 3),
            ("REJECTED", "Client rejected the quotation", "quotation_rejected", "quotation", "#B42318", 4),
            ("PENDING", "Pending quotation", "quotation_pending", "quotation", "#B54708", 5),
            ("CONFIRMED", "Confirmed quotation", "quotation_confirmed", "quotation", "#067647", 6),
            ("EXPIRED", "Expired quotation", "quotation_expired", "quotation", "#344054", 7),

            ("REQUESTED", "customer request status", "customer_requested", "customer", "#6c757d", 1),
            ("APPROVED", "customer request status", "customer_approved", "customer", "#067647", 2),
            ("REJECTED", "customer request status", "customer_rejected", "customer", "#B42318", 3),

            # Policy statuses
            ("REQUESTED", "policyStatus", "policy_requested", "policy", "#6c757d", 1),
            ("PENDING ISSUANCE", "policyStatus", "pol_pending_iss", "policy", "#B54708", 2),
            ("ACTIVE", "policyStatus", "policy_active", "policy", "#067647", 3),
            ("DUE FOR RENEWAL", "policyStatus", "pol_due_renewal", "policy", "#175CD3", 4),
            ("EXPIRED", "policyStatus", "policy_expired", "policy", "#344054", 5    ),
            ("RENEWAL IN PROGRESS", "policyStatus", "pol_renewal_progress", "policy", "#0E7090", 6),
            ("CANCELLED", "policyStatus", "policy_cancelled", "policy", "#B42318", 6),
            ("RENEWED", "policyStatus", "policy_renewed", "policy", "#175CD3", 8),

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
            ("DRAFT", "Claim is being drafted by the user", "claim_draft", "claim", "#344054", 1),
            ("EVALUATED", "Claim has been submitted for review", "claim_submitted", "claim", "#0E7090", 2),
            ("NOTIFIED", "Claim is being notified to the user", "claim_notified", "claim", "#363F72", 3),
            ("APPROVED", "Claim has been approved after evaluation", "claim_approved", "claim", "#228b22", 3),
            ("SETTLED", "Claim has been settled and closed", "claim_settled", "claim", "#067647", 4),
            ("REJECTED", "Claim has been rejected", "claim_rejected", "claim", "#B42318", 5),
        ]
        for name, desc, typ, mod, color, idx in statuses:
            Status.objects.update_or_create(
                name=name,
                module=mod,
                defaults={
                    "description": desc, "type": typ,
                     "color": color,
                    "sort_index": idx
                }
            )

        # 8. Notification Types
        notification_types = [
            ("policy_issued","Policy Issued","Notification when a policy is issued","#4CAF50"),
            ("policy_expiry","Policy Expiry","Notification when a policy is about to expire","#FF9800"),
            ("policy_renewal","Policy Renewal","Reminder for policy renewal","#2196F3"),
            ("quotation_created","Quotation Created","Quotation was created","#9C27B0"),
            ("quotation_approved","Quotation Approved","Quotation approved","#00BCD4"),
            ("quotation_rejected","Quotation Rejected","Quotation rejected","#F44336"),
            ("claim_submitted","Claim Submitted","New claim submitted","#FFC107"),
            ("claim_approved","Claim Approved","Claim approved","#8BC34A"),
            ("claim_rejected","Claim Rejected","Claim rejected","#E91E63"),
            ("payment_due","Payment Due","Upcoming payment","#FF5722"),
            ("payment_reminder","Payment Reminder","Upcoming payment reminder","#607D8B"),
            ("account_update","Account Update","Account updated","#3F51B5"),
            ("maintenance","Maintenance Alert","Maintenance alert","#795548"),
            ("general","General","General notification","#9E9E9E"),
        ]
        for code, name, desc, color in notification_types:
            NotificationType.objects.update_or_create(
                code=code,
                defaults={
                    "name": name,
                    "description": desc,
                    "color": color,
                    "created_at": timezone.now(),
                    "updated_at": timezone.now()
                }
            )

        # 9. Services
        services = [
            ("Claim Investigation", 2500.00, "Investigation services", "service render"),
            ("Claim Documentation", 1800.50, "Documentation services", "service render"),
            ("Legal Advice", 3500.00, "Legal consultation", "service render"),
            ("Fraud Investigation", 4200.75, "Fraud detection services", "service render"),
            ("Outsourced Resource Person", 2800.25, "Resource personnel", "service render"),
        ]
        for title, fee, desc, typ in services:
            Service.objects.update_or_create(
                title=title,
                defaults={
                    "fee": fee,
                    "description": desc,
                    "type": typ,
                    "module": "core",
                    "created_at": timezone.now(),
                    "updated_at": timezone.now()
                }
            )

        # 10. Global Settings
        global_settings = [
            ("OPPORTUNITY_CUSTOMER_REQUIRED_STAGE", "3"),
            ("SALES_AGENT_ROLES", "2"),
            ("COMMISSION_CONFIG", json.dumps({
                "agent_commission_config": "totalPremium",
                "payment_frequency": "monthly"
            })),
            ("BASE_CURRENCY", "2"),
            ("BASE_COUNTRY", "178"),
            
            # Approval setting JSON blob
            (
                "APPROVAL_PERMISSIONS",
                json.dumps(
                    {
                        "policy_request_approval": "true",
                        "quotation_request_approval": "true",
                    }
                ),
            ),
            ("CUSTOMER_CONFIG", json.dumps({"Policy management controller":"[Allow auto renewal, pdf]"}))
        ]

        for key_name, value in global_settings:
            try:
                setting_key_obj = SettingKey.objects.get(name=key_name)
                GlobalSetting.objects.update_or_create(
                    setting_key=setting_key_obj,
                    defaults={
                        "value": value
                    }
                )
            except SettingKey.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"⚠️ SettingKey '{key_name}' not found. Skipping global setting."))\
                    
            
        # 11. Entity Approval Rules
        entity_approval_rules = [
            (
                1,                            
                "common_approval",         
                "approval",                  
                {"other": [], "rules": [
                    {"role": None, "user": 1, "level": None}
                ]},                           
                "open",                       
            ),
        ]

        for id_, entity_type, action, rule_obj, default_status in entity_approval_rules:
            EntityApprovalRule.objects.update_or_create(
                id=id_,
                defaults={
                    "entity_type": entity_type,
                    "action": action,
                    "rule": rule_obj,         
                    "default_status": default_status,
                },
            )


        self.stdout.write(self.style.SUCCESS("✅ All core_* tables seeded successfully."))
