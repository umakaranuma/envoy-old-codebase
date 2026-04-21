from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
import json
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error

@csrf_exempt
@api_view(["GET"])
def get_confirmed_leads_with_qualified_stage(request, customer_id):
    action = ActionService.getAction("Opportunity", "VIEW")
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    query = (
        QueryBuilderService("crmq_quotation_service_providers")
        .select(
            "crm_opportunities.title AS lead_title",
            "crm_opportunities.id AS lead_id",
            "core_customers.name AS customer_name",
            "core_customers.id AS customer_id",
            "crm_opportunity_types.title AS risk_type_name",
            "crm_opportunity_types.id AS risk_type_id",
            "core_service_providers.name AS insurer_name",
            "core_service_providers.id AS insurer_id",
        )
        .leftJoin(
            "crmq_quotations",
            "crmq_quotations.id",
            "crmq_quotation_service_providers.quotation_id",
        )
        .leftJoin(
            "core_customers",
            "core_customers.id",
            "crmq_quotations.customer_id",
        )
        .leftJoin(
            "core_service_providers",
            "core_service_providers.id",
            "crmq_quotation_service_providers.service_provider_id",
        )
        .leftJoin(
            "crm_opportunities",
            "crm_opportunities.id",
            "crmq_quotations.opportunity_id",
        )
        .leftJoin(
            "crm_opportunity_types",
            "crm_opportunity_types.id",
            "crmq_quotations.opportunity_type_id",
        )
        .leftJoin(
            "crm_opportunity_statuses AS crm_opportunity_statuses_stage",
            "crm_opportunity_statuses_stage.id",
            "crm_opportunities.stage_id",
        )
        .leftJoin(
            "crm_opportunity_statuses",
            "crm_opportunity_statuses.id",
            "crmq_quotation_service_providers.status",
        )
        .where(
            "crmq_quotation_service_providers.status", 1
        )  # Quotation status CONFIRMED
        .where(
            "crm_opportunity_statuses_stage.name", "QUALIFIED"
        )  # Opportunity stage QUALIFIED
        .where("core_customers.id", customer_id)
    )

    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 20))
    sort_by = request.GET.get("sort_by", "crmq_quotation_service_providers.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = [
        "crmq_quotation_service_providers.status",
        "crm_opportunity_statuses.name",
        "crm_opportunity_statuses_stage.name",
    ]
    search_columns = ["crm_opportunities.title", "crmq_quotation_service_providers.id"]
    sort_columns = ["crmq_quotation_service_providers.id", "crm_opportunities.title"]

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
