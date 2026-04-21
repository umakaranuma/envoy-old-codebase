from django.urls import path
from envoy_bu_crm_api.sales.controllers import CustomerFormConfigController, OpporunityTypeController,OpporunityController,OpporunityTypeFormController,CommonController,OpporunityHealthController,OppournityInterestedProductController,OpporunityOpporunityTypeController

urlpatterns = [
     # this function use to one oppounity get risk types
    path('opportunity-types/many', CommonController.get_opportunity_get_types, name='opportunity.get-opportunity-types'),

    path('opportunity-types', OpporunityTypeController.opportunity_types, name='opportunity-types'),
    path('opportunity-types/<str:id>', OpporunityTypeController.single_opportunity_types, name='single-opportunity-types'),

    path('opportunities', OpporunityController.opportunity, name='opportunity'),
    path('opportunities/info', OpporunityController.opportunity_other_info, name='opportunity-other-info'),
    path('opportunities/<str:id>', OpporunityController.single_opportunity, name='single-opportunity'),
    path("opportunities/<int:opportunity_id>/policies", OpporunityController.get_opportunity_policies, name="opportunity_policies"),
    path('opportunities/<str:id>/status', OpporunityController.update_opportunity_status, name='update-opportunity-status'),
    path('opportunities/<str:id>/types', OpporunityController.opportunity_types, name='single-opportunity-types'),
    path('opportunities/<str:id>/types/<str:type_id>', OpporunityController.delete_opportunity_type, name='delete-opportunity-types'),
    path('opportunity-types/<str:type_id>/form-config', OpporunityController.get_opportunity_form_config, name='opportunity_form_config'),
    # path('opportunities/<int:id>/types/<int:type_id>/info', OpporunityController.opportunity_info, name='opportunity_info'),
    # path('opportunities/<str:id>', OpporunityController.update_opportunity, name='update_opportunity'),
    # path('opportunity-types/<int:type_id>/form-config', OpporunityController.get_opportunity_type_form_config, name='get_opportunity_type_form_config'),
    path("opportunities/<int:id>/interactions", OpporunityController.interactions, name="interactions"),
    path("opportunities/<int:id>/interactions/<int:int_id>", OpporunityController.single_interaction, name="single_interaction"),
    # path("opportunities/<int:id>/form-config/<int:config_id>/info", OpporunityController.opportunity_form_config_info, name="opportunity_form_config_info"),
    # path("opportunities/<int:id>/form-config/<int:config_id>/info/<int:info_id>", OpporunityController.opportunity_form_config_info, name="opportunity_form_config_info_detail"),
    path("opportunities/<int:id>/customer", OpporunityController.update_opportunity_customer, name="update_opportunity_customer"),
    path("opportunities/<int:lead_id>/issued-policies", OpporunityController.get_issued_policies_by_lead, name="lead-issued-policies"),
    path("opportunities/<int:id>/sales-agent-history", OpporunityController.get_sales_agent_history, name="sales-agent-history"),




    path('opportunity-types/<str:opp_type_id>/forms', OpporunityTypeFormController.opportunity_form, name='opportunity-types-forms'),
    path('opportunity-types/<str:opp_type_id>/forms/<str:form_id>', OpporunityTypeFormController.single_opportunity_form, name='single-opportunity-types-forms'),
    
    path('opportunity-health', OpporunityHealthController.get_all_health, name='all-opportunity-health'),
    path('opportunities/<str:opp_id>/health', OpporunityHealthController.get_opportunity_health, name='opportunity-health'),
    path('opportunities/<str:opp_id>/health/<str:health_id>', OpporunityHealthController.single_opportunity_health, name='single-opportunity-health'),

    path('opportunities/<str:opp_id>/interested-products', OppournityInterestedProductController.interested_products, name='interested-products'),
    path('opportunities/<str:opp_id>/interested-products/<str:product_id>', OppournityInterestedProductController.single_interested_products, name='single-interested-products'),

    path('opportunity-statuses', CommonController.get_opportunity_status, name='opportunity-statuses'),
    path('sales-agents', CommonController.get_team_members, name='sales-agents'),
    path('team-members', CommonController.get_sales_agents, name='team-members'),
    
    path('opportunity-statuses/<int:id>', CommonController.get_opportunity_status_by_id, name='get_opportunity_status_by_id'),

    #---------------------------------------------
    path('opportunities/<str:opp_id>/form-config/<str:config_id>/info', OpporunityOpporunityTypeController.get_form_config_info, name='oppo-oppo-type-info'),
    path('opportunities/<str:opp_id>/form-config/<str:config_id>/info/<str:info_id>', OpporunityOpporunityTypeController.get_single_form_config_info, name='single-oppo-oppo-type-info'),
    path(
        'opportunities/<str:opp_id>/form-submission/<str:form_submission_id>',
        OpporunityOpporunityTypeController.manage_form_submission,
        name='manage-form-submission'
    ),
    path("opportunities/<str:opp_id>/form-config/<str:config_id>/bulk-submit", OpporunityOpporunityTypeController.save_multiple_oppo_form_submissions),
    path("lead-risk/<int:risk_type_id>", OpporunityOpporunityTypeController.get_risks_by_type_and_lead_id, name="get_risk_details_by_lead"),
    path("lead-risks", OpporunityOpporunityTypeController.create_risk_detail, name="create_risk_detail"),
    path("risk-details/<int:risk_detail_id>", OpporunityOpporunityTypeController.get_risk_detail_template_with_values),


    
    
    
    path('customers/<str:customer_id>/form-config/<str:config_id>/info', CustomerFormConfigController.get_customer_form_config_info, name='customer-form-config-info'),


   
]