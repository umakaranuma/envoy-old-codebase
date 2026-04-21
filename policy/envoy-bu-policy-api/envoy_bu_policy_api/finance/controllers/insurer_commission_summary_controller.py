from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
import json
from collections import defaultdict

@csrf_exempt
@api_view(["GET"])
def insurer_commission_summary_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("BrokerageCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    try:
        # Get filter parameters
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "")
        sort_dir = request.GET.get("sort_dir", "desc")

        # Define columns for individual records
        columns = [
            "core_service_providers.id as insurer_id",
            "core_service_providers.name as insurer_name",
            "crmf_invoices.id as invoice_id",
            "crmf_invoices.issued_policy_id",
            "crmf_invoices.invoice_amount",
            "crmf_brokerage_commission.id as brokerage_commission_id",
            "crmf_brokerage_commission.revenue_realized",
            "crmf_brokerage_commission.overriding_commission_amount",
            "crmf_brokerage_commission.agent_commission",
            "crmf_agent_commission.agent_id",
            "core_users.id as user_id"
        ]

        # Build query to get individual records
        query = (
            QueryBuilderService("core_service_providers")
            .select(*columns)
            .leftJoin(
                "crmf_invoices",
                "crmf_invoices.insurer_id",
                "core_service_providers.id"
            )
            .leftJoin(
                "crmf_brokerage_commission",
                "crmf_brokerage_commission.invoice_id",
                "crmf_invoices.id"
            )
            .leftJoin(
                "crmf_agent_commission",
                "crmf_agent_commission.brokerage_commission_id",
                "crmf_brokerage_commission.id"
            )
            .leftJoin(
                "core_users",
                "core_users.id",
                "crmf_agent_commission.agent_id"
            )
        )

        # Apply filters
        if filter_json.get("insurer_id"):
            query = query.where("core_service_providers.id", int(filter_json["insurer_id"]))
        if filter_json.get("agent_id"):
            query = query.where("crmf_agent_commission.agent_id", int(filter_json["agent_id"]))
        if filter_json.get("start_date"):
            query = query.whereRaw("crmf_invoices.invoice_date >= %s", [filter_json["start_date"]])
        if filter_json.get("end_date"):
            query = query.whereRaw("crmf_invoices.invoice_date <= %s", [filter_json["end_date"]])
        if filter_json.get("status"):
            query = query.where("crmf_brokerage_commission.status", filter_json["status"])

        # Define allowed filters and search columns
        allowed_filters = [
            "start_date",
            "end_date",
            "status",
            "insurer_id",
            "agent_id"
        ]
        
        search_columns = [
            "core_service_providers.name",
            "crmf_invoices.invoice_number"
        ]

        # Apply search
        if search_string:
            query = query.apply_conditions(
                {},
                [],
                search_string,
                search_columns
            )

        # Get all records
        all_records = query.get()

        # Aggregate data by insurer
        insurer_data = defaultdict(lambda: {
            "insurer_id": None,
            "insurer_name": "",
            "total_policies": set(),
            "total_premium": 0,
            "total_commission": 0,
            "total_revenue_realized": 0,
            "total_overriding_commission": 0,
            "total_agent_commission": 0,
            "total_agents": set(),
            "brokerage_commission_ids": set()
        })

        for record in all_records:
            insurer_id = record.get('insurer_id')
            if insurer_id:
                insurer_data[insurer_id]['insurer_id'] = insurer_id
                insurer_data[insurer_id]['insurer_name'] = record.get('insurer_name', '')
                
                if record.get('issued_policy_id'):
                    insurer_data[insurer_id]['total_policies'].add(record['issued_policy_id'])
                
                insurer_data[insurer_id]['total_premium'] += float(record.get('invoice_amount', 0) or 0)
                insurer_data[insurer_id]['total_commission'] += float(record.get('revenue_realized', 0) or 0)
                insurer_data[insurer_id]['total_revenue_realized'] += float(record.get('revenue_realized', 0) or 0)
                insurer_data[insurer_id]['total_overriding_commission'] += float(record.get('overriding_commission_amount', 0) or 0)
                insurer_data[insurer_id]['total_agent_commission'] += float(record.get('agent_commission', 0) or 0)
                
                if record.get('agent_id'):
                    insurer_data[insurer_id]['total_agents'].add(record['agent_id'])
                
                if record.get('brokerage_commission_id'):
                    insurer_data[insurer_id]['brokerage_commission_ids'].add(record['brokerage_commission_id'])

        # Convert to list format
        aggregated_data = []
        for insurer_id, data in insurer_data.items():
            aggregated_data.append({
                "insurer_id": data['insurer_id'],
                "insurer_name": data['insurer_name'],
                "total_policies": len(data['total_policies']),
                "total_premium": round(data['total_premium'], 2),
                "total_commission": round(data['total_commission'], 2),
                "total_revenue_realized": round(data['total_revenue_realized'], 2),
                "total_overriding_commission": round(data['total_overriding_commission'], 2),
                "total_agent_commission": round(data['total_agent_commission'], 2),
                "total_agents": len(data['total_agents']),
                # "brokerage_commission_ids": list(data['brokerage_commission_ids'])
            })

        # Sort data
        sort_columns = [
            "insurer_name",
            "total_policies",
            "total_premium",
            "total_commission",
            "total_revenue_realized",
            "total_overriding_commission",
            "total_agent_commission"
        ]
        
        if sort_by in sort_columns:
            reverse = sort_dir.lower() == "desc"
            aggregated_data.sort(key=lambda x: x.get(sort_by, 0), reverse=reverse)

        # Paginate data
        total_records = len(aggregated_data)
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = aggregated_data[start_index:end_index]
        
        last_page = (total_records + limit - 1) // limit

        response_data = {
            "total_records": total_records,
            "per_page": limit,
            "current_page": page,
            "last_page": last_page,
            "data": paginated_data
        }

        return ResponseService.response("SUCCESS", response_data, Message.DATA_FETCHED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), "Error retrieving insurer commission summary")

@csrf_exempt
@api_view(["GET"])
def insurer_commission_summary_totals(request):
    action_type = "VIEW"
    action = ActionService.getAction("BrokerageCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    try:
        # Get filter parameters
        filter_json = json.loads(request.GET.get("filter", "{}"))
        search_string = request.GET.get("search", "")

        # Build query to get individual records
        query = (
            QueryBuilderService("core_service_providers")
            .select(
                "core_service_providers.id as insurer_id",
                "crmf_invoices.id as invoice_id",
                "crmf_invoices.issued_policy_id",
                "crmf_invoices.invoice_amount",
                "crmf_brokerage_commission.id as brokerage_commission_id",
                "crmf_brokerage_commission.revenue_realized",
                "crmf_brokerage_commission.overriding_commission_amount",
                "crmf_brokerage_commission.agent_commission",
                "crmf_agent_commission.agent_id"
            )
            .leftJoin(
                "crmf_invoices",
                "crmf_invoices.insurer_id",
                "core_service_providers.id"
            )
            .leftJoin(
                "crmf_brokerage_commission",
                "crmf_brokerage_commission.invoice_id",
                "crmf_invoices.id"
            )
            .leftJoin(
                "crmf_agent_commission",
                "crmf_agent_commission.brokerage_commission_id",
                "crmf_brokerage_commission.id"
            )
        )

        # Define allowed filters and search columns
        allowed_filters = [
            "start_date",
            "end_date",
            "status",
            "insurer_id",
            "agent_id"
        ]
        
        search_columns = [
            "core_service_providers.name",
            "crmf_invoices.invoice_number"
        ]

        # Get all records
        all_records = query.apply_conditions(
            filter_json,
            allowed_filters,
            search_string,
            search_columns
        ).get()

        # Calculate totals
        total_insurers = set()
        total_policies = set()
        total_premium = 0
        total_commission = 0
        total_revenue_realized = 0
        total_overriding_commission = 0
        total_agent_commission = 0
        total_agents = set()

        for record in all_records:
            if record.get('insurer_id'):
                total_insurers.add(record['insurer_id'])
            
            if record.get('issued_policy_id'):
                total_policies.add(record['issued_policy_id'])
            
            total_premium += float(record.get('invoice_amount', 0) or 0)
            total_commission += float(record.get('revenue_realized', 0) or 0)
            total_revenue_realized += float(record.get('revenue_realized', 0) or 0)
            total_overriding_commission += float(record.get('overriding_commission_amount', 0) or 0)
            total_agent_commission += float(record.get('agent_commission', 0) or 0)
            
            if record.get('agent_id'):
                total_agents.add(record['agent_id'])

        totals = {
            "total_insurers": len(total_insurers),
            "total_policies": len(total_policies),
            "total_premium": round(total_premium, 2),
            "total_commission": round(total_commission, 2),
            "total_revenue_realized": round(total_revenue_realized, 2),
            "total_overriding_commission": round(total_overriding_commission, 2),
            "total_agent_commission": round(total_agent_commission, 2),
            "total_agents": len(total_agents)
        }

        return ResponseService.response("SUCCESS", totals, Message.DATA_FETCHED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), "Error retrieving insurer commission totals") 