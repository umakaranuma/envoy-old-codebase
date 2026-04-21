from django.apps import AppConfig

class FinanceConfig(AppConfig):
    name = 'envoy_bu_policy_api.finance'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from envoy_bu_policy_api.finance.models.crmf_transaction_types import TransactionType
        TransactionType  # This ensures the model is registered 