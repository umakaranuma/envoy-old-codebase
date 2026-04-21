from django.urls import path
from envoy_bu_policy_api.finance.controllers import (
   commission_setup_controller, mapping_controller,service_render_controller,
)
from .controllers.invoice_controller import (
    invoice_list,
    invoice_detail,
    update_payment
)
from .controllers.payment_controller import payment_list, payment_detail,customer_payment_id
from .controllers.choices_controller import get_payment_methods, get_account_types,get_transaction_types
from .controllers import (
    brokerage_commission_controller,
    agent_commission_controller
)
from envoy_bu_policy_api.finance.controllers.chart_of_accounts_controller import (
    chart_of_account_list,
    chart_of_account_detail
)
from .controllers.agent_commission_controller import (
    agent_commission_list,
    agent_commission_detail,
    agent_commission_totals,
    my_commission_list,
    my_commission_totals,
    my_commission_policy_stats,
    multi_agent_commission_list, 
    multi_agent_commission_totals
)
from .controllers.agent_commission_payment_controller import (
    agent_commission_payment_list,
    agent_commission_payment_detail,
    get_commission_outstanding,
    commission_payments,
    create_single_agent_commission_payment
)
from .controllers.brokerage_commission_settlement_controller import (
    brokerage_commission_settlement_list,
    brokerage_commission_settlement_detail,
    get_commission_outstanding as get_brokerage_commission_outstanding,
    commission_settlements,
)
from .controllers.journal_entries_controller import journal_entry_list
from .controllers.cash_flow_journal_controller import cash_flow_journal_list, cash_flow_journal_totals
from .controllers.debtor_aging_controller import debtor_aging_list
from .controllers.policies_made_controller import policies_made_list
from .controllers.commission_earned_controller import commission_earned_list
from .controllers.commission_given_controller import commission_given_list
from .controllers.general_ledger_controller import get_all_entries, general_ledger_account_report, general_ledger_account_balances
from .controllers.insurer_commission_summary_controller import (
    insurer_commission_summary_list,
    insurer_commission_summary_totals
)
from .controllers.agent_commission_summary_controller import (
    agent_commission_summary_list,
    agent_commission_summary_totals
)
from .controllers import (
    incentive_controller
)
from .controllers.payment_controller import (
    get_payments,
    get_agent_payments,
    get_multiple_agent_payments,
 
)
from .controllers.brokerage_commission_controller import (
    multi_brokerage_commission_list,
    multi_brokerage_commission_totals
)
from envoy_bu_policy_api.finance.controllers.incentive_controller import initiate_incentive_award
from envoy_bu_policy_api.finance.controllers.agent_sales_target_controller import agent_sales_target_list, agent_sales_target_detail
from envoy_bu_policy_api.finance.controllers.team_sales_target_controller import team_sales_target_list, team_sales_target_detail
from envoy_bu_policy_api.finance.controllers.incentive_controller import advanced_user_search
from envoy_bu_policy_api.finance.controllers.incentive_controller import get_all_incentives

urlpatterns = [
    # General Ledger URLs
    path('general-ledger', get_all_entries, name='general_ledger_list'),
    path('general-ledger/account-report', general_ledger_account_report, name='general_ledger_account_report'),
    path('general-ledger/account-balances', general_ledger_account_balances, name='general_ledger_account_balances'),

    #commission_setup
    path("tst",commission_setup_controller.tst, name="tst"),
    path("commission-setups", commission_setup_controller.commission_setup, name="commission_setup"),
    path("commission-setups/multi", commission_setup_controller.commission_setup_multi, name="commission_setup_multi"),
    path("commission-setups/bulk-delete", commission_setup_controller.bulk_delete_commission_setups, name="bulk_delete_commission_setups"),
    path("commission-setups/<int:id>", commission_setup_controller.commission_setup_single, name="commission_setup_single"),
    path("commission-setups/<int:id>/teams/<int:team_id>/remove-team", commission_setup_controller.remove_team_from_commission_setup, name="remove_team_from_commission_setup"),
    path("teams", commission_setup_controller.get_teams, name="get_teams"),
    path("teams/<int:id>", commission_setup_controller.get_teams_details, name="get_teams_details"),
    path('commission-setups/<int:commission_setup_id>/teams/<int:team_id>', commission_setup_controller.commission_setup_team_users, name='commission_setup_team_users'),
    path('product-group/<int:id>/insurers', commission_setup_controller.product_group_insurers, name='product_group_insurers'),
    path('product-group/<int:product_group_id>/insurence/<int:id>/teams', commission_setup_controller.insurence_teams, name='insurence_teams'),

   
    #Service Render
  path("service-renders/payment-status", service_render_controller.payment_status, name="payment_status"),
  path("service-renders/invoice-status", service_render_controller.invoice_status, name="invoice_status"),
  path("service-renders", service_render_controller.service_render, name="service_render"),
  path("service-renders/<int:id>", service_render_controller.service_render_details, name="service_render_details"),
  path("service-renders/service/<int:id>/fee", service_render_controller.get_fee, name="get_fee"),
  path("service-renders/services", service_render_controller.get_services, name="get_services"),
  path("service-renders/<int:id>/payments", service_render_controller.service_render_payment, name="service_render_payment"),
  path("service-renders/<int:id>/payments/<int:payment_id>", service_render_controller.service_render_payment_single, name="service_render_payment_single"),
 
    #mapping

  # path("mapping/attributes",mapping_controller.get_attributes,name="get_attributes" ),
  path("mapping/attributes",mapping_controller.mapping_attributes,name="mapping_attributes" ),
  path("mapping/attributes/<int:id>",mapping_controller.mapping_attribute_single,name="mapping_attribute_single" ),
  path("mapping/attributes/<str:ids>/history",mapping_controller.mapping_attribute_history,name="mapping_attribute_history" ),
  path("mapping/payment-uploads/history",mapping_controller.payment_uploads,name="payment_uploads" ),
  path("mapping/payment/<int:id>/payment-uploads/history",mapping_controller.single_payment_uploads,name="single_payment_uploads" ),
  path("mapping/payment/<int:id>/payment-uploads/history",mapping_controller.single_payment_uploads,name="single_payment_uploads" ),

    path('invoices/', invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>/', invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/payment/', update_payment, name='update_payment'),
    path('invoices', invoice_list, name='invoice_list'),
    path('invoices/<int:invoice_id>', invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/payments', payment_list, name='invoice_payment_list'),
    path('invoices/<int:invoice_id>/payment', update_payment, name='update_payment'),
    path('payments', payment_list, name='payments'),
    path('invoice/<int:invoice_id>/customer-payment-id',customer_payment_id,name="customer_payment_id"),
    path('payments/<int:payment_id>', payment_detail, name='payment_detail'),
    path('payment-methods', get_payment_methods, name='get_payment_methods'),
    path('account-types', get_account_types, name='get_account_types'),
    path('transaction-types', get_transaction_types, name='get_transaction_types'),
    
    # Brokerage Commission URLs
    path("brokerage-commissions", brokerage_commission_controller.brokerage_commission_list, name="brokerage_commission_list"),
    path("brokerage-commissions/<int:commission_id>", brokerage_commission_controller.brokerage_commission_detail, name="brokerage_commission_detail"),
    path("invoices/<int:invoice_id>/brokerage-commission", brokerage_commission_controller.brokerage_commission_detail, name="invoice_brokerage_commission"),
    path("brokerage-commissions/totals", brokerage_commission_controller.brokerage_commission_totals, name="brokerage_commission_totals"),
    
    # Agent Commission URLs
    path("agent-commissions", agent_commission_list, name="agent_commission_list"),
    path("agent-commissions/<int:commission_id>", agent_commission_detail, name="agent_commission_detail"),
    path("agent-commissions/totals", agent_commission_totals, name="agent_commission_totals"),
    path("my-commissions", my_commission_list, name="my_commission_list"),
    path("my-commissions/totals", my_commission_totals, name="my_commission_totals"),
    path("my-commissions/policy-stats", my_commission_policy_stats, name="my_commission_policy_stats"),

    # My Commission URLs
    path("my-commissions", agent_commission_controller.my_commission_list, name="my_commission_list"),
    path("my-commissions/totals", agent_commission_controller.my_commission_totals, name="my_commission_totals"),
    path("my-commissions/policy-stats", agent_commission_controller.my_commission_policy_stats, name="my_commission_policy_stats"),

    # Chart of Accounts URLs
    path('chart-of-accounts', chart_of_account_list, name='chart_of_account_list'),
    path('chart-of-accounts/<int:account_id>', chart_of_account_detail, name='chart_of_account_detail'),

    # New agent commission payment URLs
    path("agent-commission-payments", agent_commission_payment_list, name="agent_commission_payment_list"),
    path("agent-commission-payments/<int:commission_id>", create_single_agent_commission_payment, name="create_single_agent_commission_payment"),
    path("agent-commission-payments/<int:payment_id>", agent_commission_payment_detail, name="agent_commission_payment_detail"),
    path("commission/<int:commission_id>/payments", commission_payments, name="commission_payments"),
    path("commission/<int:commission_id>/outstanding", get_commission_outstanding, name="get_commission_outstanding"),

    # Brokerage commission settlement URLs
    path("brokerage-commission-settlements", brokerage_commission_settlement_list, name="brokerage_commission_settlement_list"),
    path("brokerage-commission-settlements/<int:settlement_id>", brokerage_commission_settlement_detail, name="brokerage_commission_settlement_detail"),
    path("brokerage-commission/<int:commission_id>/settlements", commission_settlements, name="commission_settlements"),
    path("brokerage-commission/<int:commission_id>/outstanding", get_brokerage_commission_outstanding, name="get_brokerage_commission_outstanding"),

    # New Payment Controller URLs
    path('payments/all', get_payments, name='get_all_payments'),
    path('payments/agent/<int:agent_id>', get_agent_payments, name='get_agent_payments'),
    path('payments/agent', get_multiple_agent_payments, name='get_multiple_agent_payments'),

    # Journal Entries URLs
    path('journal-entries', journal_entry_list, name='journal_entry_list'),
    path('cash-flow-journal', cash_flow_journal_list, name='cash_flow_journal_list'),
    path('cash-flow-journal/totals', cash_flow_journal_totals, name='cash_flow_journal_totals'),
    
    # Debtor Aging Report URL
    path('debtor-aging', debtor_aging_list, name='debtor_aging_list'),

    # New report endpoints
    path('policies-made', policies_made_list, name='policies_made_list'),
    path('commission-earned', commission_earned_list, name='commission_earned_list'),
    path('commission-given', commission_given_list, name='commission_given_list'),

    # New Commission Summary URLs
    path('insurer-commission-summary', insurer_commission_summary_list, name='insurer_commission_summary_list'),
    path('insurer-commission-summary/totals', insurer_commission_summary_totals, name='insurer_commission_summary_totals'),
    path('agent-commission-summary', agent_commission_summary_list, name='agent_commission_summary_list'),
    path('agent-commission-summary/totals', agent_commission_summary_totals, name='agent_commission_summary_totals'),

    # Incentive URLs
    path('incentive-setups', incentive_controller.incentive_setup, name='incentive_setups'),
    path('incentive-setups/<int:id>', incentive_controller.incentive_setup_single, name='incentive_setup_single'),
    # Incentive Setup Related URLs
    path('performance-field-definitions', incentive_controller.list_performance_field_definitions, name='performance_field_definitions'),
    path('reward-types', incentive_controller.get_all_reward_types, name='get_all_reward_types'),
    path('reward-configs', incentive_controller.get_all_reward_configs, name='get_all_reward_configs'),
    path('repetition-types', incentive_controller.get_repetition_types, name='get_repetition_types'),
    path('multi-agent-commission-list', multi_agent_commission_list),
    path('multi-agent-commission-totals', multi_agent_commission_totals),
    path('multi-brokerage-commission-list', multi_brokerage_commission_list),
    path('multi-brokerage-commission-totals', multi_brokerage_commission_totals),
    path('incentive-base-fields', incentive_controller.list_incentive_base_fields, name='incentive_base_fields'),
    path('incentives', get_all_incentives, name='incentives'),
]

urlpatterns += [
    path('incentives/initiate/<int:setup_id>', initiate_incentive_award, name='initiate_incentive_award'),
    path('incentives/run-all', incentive_controller.run_all_incentive_awards, name='run_all_incentive_awards'),
    path('incentives/create-table', incentive_controller.create_incentive_table, name='create_incentive_table'),
    path('incentives/cleanup-duplicates', incentive_controller.cleanup_duplicates, name='cleanup_duplicates'),
    path('agent-sales-targets', agent_sales_target_list, name='agent_sales_target_list'),
    path('agent-sales-targets/<int:id>', agent_sales_target_detail, name='agent_sales_target_detail'),
    path('team-sales-targets', team_sales_target_list, name='team_sales_target_list'),
    path('team-sales-targets/<int:id>', team_sales_target_detail, name='team_sales_target_detail'),
    path('advanced-user-search', advanced_user_search, name='advanced_user_search'),
]
