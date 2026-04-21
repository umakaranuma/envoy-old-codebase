from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
import json
from collections import defaultdict

def get_columns():
    return [
        "core_users.id as agent_id",
        "core_users.display_name as agent_name",
        "core_users.email as agent_email",
        "core_users.picture as agent_picture",
        "crmp_issued_policies.id as policy_id",
        "crmp_issued_policies.premium_amount",
        "crmf_agent_commission.id as agent_commission_id",
        "crmf_brokerage_commission.id as brokerage_commission_id",
        "crmf_agent_commission.revenue_recognized as commission_amount",
        "crmf_agent_commission.revenue_realized as commission_received",
        "crmf_agent_commission.revenue_recognized - crmf_agent_commission.revenue_realized as commission_pending",
        "crmf_agent_commission.bonus_amount",
        "crmf_agent_commission.target_achievement_amount as target_achievement",
        "crmf_agent_commission.revised_amount",
        "core_service_providers.id as insurer_id"
    ]

def build_base_query():
    return (
        QueryBuilderService("core_users")
        .select(*get_columns())
        .leftJoin(
            "crmf_agent_commission",
            "crmf_agent_commission.agent_id",
            "core_users.id"
        )
        .leftJoin(
            "crmf_brokerage_commission",
            "crmf_brokerage_commission.id",
            "crmf_agent_commission.brokerage_commission_id"
        )
        .leftJoin(
            "crmf_invoices",
            "crmf_invoices.id",
            "crmf_brokerage_commission.invoice_id"
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id"
        )
        .leftJoin(
            "core_service_providers",
            "core_service_providers.id",
            "crmf_invoices.insurer_id"
        )
    )

def build_totals_query():
    return (
        QueryBuilderService("core_users")
        .select(
            "core_users.id as agent_id",
            "crmp_issued_policies.id as policy_id",
            "crmp_issued_policies.premium_amount",
            "crmf_agent_commission.id as agent_commission_id",
            "crmf_brokerage_commission.id as brokerage_commission_id",
            "crmf_agent_commission.revenue_recognized as commission_amount",
            "crmf_agent_commission.revenue_realized as commission_received",
            "crmf_agent_commission.revenue_recognized - crmf_agent_commission.revenue_realized as commission_pending",
            "crmf_agent_commission.bonus_amount",
            "crmf_agent_commission.target_achievement_amount as target_achievement",
            "crmf_agent_commission.revised_amount"
        )
        .leftJoin(
            "crmf_agent_commission",
            "crmf_agent_commission.agent_id",
            "core_users.id"
        )
        .leftJoin(
            "crmf_brokerage_commission",
            "crmf_brokerage_commission.id",
            "crmf_agent_commission.brokerage_commission_id"
        )
        .leftJoin(
            "crmf_invoices",
            "crmf_invoices.id",
            "crmf_brokerage_commission.invoice_id"
        )
        .leftJoin(
            "crmp_issued_policies",
            "crmp_issued_policies.id",
            "crmf_invoices.issued_policy_id"
        )
        .leftJoin(
            "core_service_providers",
            "core_service_providers.id",
            "crmf_invoices.insurer_id"
        )
    )

def get_filter_params(request):
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "agent_name")
    sort_dir = request.GET.get("sort_dir", "desc")
    
    return filter_json, search_string, page, limit, sort_by, sort_dir

def get_allowed_filters():
    return [
        "start_date",
        "end_date",
        "status",
        "agent_id",
        "insurer_id"
    ]

def get_search_columns():
    return [
        "core_users.display_name",
        "core_users.email",
        "crmp_issued_policies.policy_number"
    ]

def get_sort_columns():
    return [
        "agent_name",
        "agent_email",
        "total_policies",
        "total_premium",
        "total_commission_earned",
        "total_commission_received",
        "total_commission_pending"
    ]

@csrf_exempt
@api_view(["GET"])
def agent_commission_summary_list(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    try:
        # Get filter parameters
        filter_json, search_string, page, limit, sort_by, sort_dir = get_filter_params(request)
        
        # Build base query
        query = build_base_query()
        
        # Apply filters
        if filter_json.get("agent_id"):
            query = query.where("crmf_agent_commission.agent_id", int(filter_json["agent_id"]))
        if filter_json.get("insurer_id"):
            query = query.where("core_service_providers.id", int(filter_json["insurer_id"]))
        if filter_json.get("start_date"):
            query = query.whereRaw("crmf_invoices.invoice_date >= %s", [filter_json["start_date"]])
        if filter_json.get("end_date"):
            query = query.whereRaw("crmf_invoices.invoice_date <= %s", [filter_json["end_date"]])
        if filter_json.get("status"):
            query = query.where("crmf_agent_commission.status", filter_json["status"])

        # Apply search
        if search_string:
            query = query.apply_conditions(
                {},
                [],
                search_string,
                get_search_columns()
            )

        all_records = query.get()

        # Aggregate data by agent
        agent_data = defaultdict(lambda: {
            "agent_id": None,
            "agent_name": "",
            "agent_email": "",
            "agent_picture": "",
            "total_policies": set(),
            "total_premium": 0,
            "total_commission_earned": 0,
            "total_commission_received": 0,
            "total_commission_pending": 0,
            "total_bonus": 0,
            "total_target_achievement": 0,
            "total_revised_amount": 0,
            "total_insurers": set(),
            "agent_commission_ids": set(),
            "brokerage_commission_ids": set()
        })

        for record in all_records:
            agent_id = record.get('agent_id')
            if agent_id:
                agent_data[agent_id]['agent_id'] = agent_id
                agent_data[agent_id]['agent_name'] = record.get('agent_name', '')
                agent_data[agent_id]['agent_email'] = record.get('agent_email', '')
                agent_data[agent_id]['agent_picture'] = record.get('agent_picture', '')
                
                if record.get('policy_id'):
                    agent_data[agent_id]['total_policies'].add(record['policy_id'])
                
                agent_data[agent_id]['total_premium'] += float(record.get('premium_amount', 0) or 0)
                agent_data[agent_id]['total_commission_earned'] += float(record.get('commission_amount', 0) or 0)
                agent_data[agent_id]['total_commission_received'] += float(record.get('commission_received', 0) or 0)
                agent_data[agent_id]['total_commission_pending'] += float(record.get('commission_pending', 0) or 0)
                agent_data[agent_id]['total_bonus'] += float(record.get('bonus_amount', 0) or 0)
                agent_data[agent_id]['total_target_achievement'] += float(record.get('target_achievement', 0) or 0)
                agent_data[agent_id]['total_revised_amount'] += float(record.get('revised_amount', 0) or 0)
                
                if record.get('insurer_id'):
                    agent_data[agent_id]['total_insurers'].add(record['insurer_id'])
                
                if record.get('agent_commission_id'):
                    agent_data[agent_id]['agent_commission_ids'].add(record['agent_commission_id'])
                
                if record.get('brokerage_commission_id'):
                    agent_data[agent_id]['brokerage_commission_ids'].add(record['brokerage_commission_id'])

        # Convert to list format
        aggregated_data = []
        for agent_id, data in agent_data.items():
            aggregated_data.append({
                "agent_id": data['agent_id'],
                "agent_name": data['agent_name'],
                "agent_email": data['agent_email'],
                "agent_picture": data['agent_picture'],
                "total_policies": len(data['total_policies']),
                "total_premium": round(data['total_premium'], 2),
                "total_commission_earned": round(data['total_commission_earned'], 2),
                "total_commission_received": round(data['total_commission_received'], 2),
                "total_commission_pending": round(data['total_commission_pending'], 2),
                "total_bonus": round(data['total_bonus'], 2),
                "total_target_achievement": round(data['total_target_achievement'], 2),
                "total_revised_amount": round(data['total_revised_amount'], 2),
                "total_insurers": len(data['total_insurers']),
                # "agent_commission_ids": list(data['agent_commission_ids']),
                # "brokerage_commission_ids": list(data['brokerage_commission_ids'])
            })

        # Sort data
        sort_columns = [
            "agent_name",
            "agent_email",
            "total_policies",
            "total_premium",
            "total_commission_earned",
            "total_commission_received",
            "total_commission_pending"
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
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), "Error retrieving agent commission summary")

@csrf_exempt
@api_view(["GET"])
def agent_commission_summary_totals(request):
    action_type = "VIEW"
    action = ActionService.getAction("AgentCommission", action_type)

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    try:
        # Get filter parameters
        filter_json, search_string, _, _, _, _ = get_filter_params(request)
        
        # Build totals query
        query = build_totals_query()
        
        # Apply filters and search
        all_records = query.apply_conditions(
            filter_json,
            get_allowed_filters(),
            search_string,
            get_search_columns()
        ).get()

        # Calculate totals manually
        total_agents = set()
        total_policies = set()
        total_premium = 0
        total_commission_earned = 0
        total_commission_received = 0
        total_commission_pending = 0
        total_bonus = 0
        total_target_achievement = 0
        total_revised_amount = 0

        for record in all_records:
            if record.get('agent_id'):
                total_agents.add(record['agent_id'])
            
            if record.get('policy_id'):
                total_policies.add(record['policy_id'])
            
            total_premium += float(record.get('premium_amount', 0) or 0)
            total_commission_earned += float(record.get('commission_amount', 0) or 0)
            total_commission_received += float(record.get('commission_received', 0) or 0)
            total_commission_pending += float(record.get('commission_pending', 0) or 0)
            total_bonus += float(record.get('bonus_amount', 0) or 0)
            total_target_achievement += float(record.get('target_achievement', 0) or 0)
            total_revised_amount += float(record.get('revised_amount', 0) or 0)
        
        totals = {
            "total_agents": len(total_agents),
            "total_policies": len(total_policies),
            "total_premium": round(total_premium, 2),
            "total_commission_earned": round(total_commission_earned, 2),
            "total_commission_received": round(total_commission_received, 2),
            "total_commission_pending": round(total_commission_pending, 2),
            "total_bonus": round(total_bonus, 2),
            "total_target_achievement": round(total_target_achievement, 2),
            "total_revised_amount": round(total_revised_amount, 2)
        }
        
        return ResponseService.response("SUCCESS", totals, Message.DATA_FETCHED)
        
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", str(e), "Error retrieving agent commission totals") 