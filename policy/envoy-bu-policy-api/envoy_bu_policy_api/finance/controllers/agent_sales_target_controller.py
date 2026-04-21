from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from mServices import ResponseService, QueryBuilderService, ValidatorService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from django.utils import timezone
import json


def get_agent_sales_target_validation_rules():
    return {
        "agent_id": "required|list",
        "period_type": "required|in:monthly,yearly",
        # "year": "required|integer",  # Make year optional
        "year": "integer",
        "target_amount": "required|numeric",
    }


def get_agent_sales_target_update_rules():
    return {
        "agent_id": "required|integer|exists:core_users,id",
        "period_type": "required|in:monthly,yearly",
        # "year": "required|integer",  # Make year optional
        "year": "integer",
        "target_amount": "required|numeric",
    }


def calculate_agent_achieved(agent_id, period_type, month, year):
    # Sum premium_amount from crmp_issued_policies for the agent and period
    # Need to join with crmp_policy_base to get sales_agent_id
    query = QueryBuilderService("crmp_issued_policies as ip").select(
        "SUM(ip.premium_amount) as achieved"
    ).leftJoin(
        "crmp_policy_base as pb", 
        "pb.id", 
        "ip.policy_base_id"
    )
    query = query.where("pb.sales_agent_id", agent_id)
    if period_type == "monthly" and month:
        query = query.where("MONTH(ip.policy_effective_date)", month)
    query = query.where("YEAR(ip.policy_effective_date)", year)
    result = query.first()
    return float(result["achieved"] or 0)


@csrf_exempt
@api_view(["GET", "POST"])
def agent_sales_target_list(request):
    action_type = "VIEW" if request.method == "GET" else "CREATE"
    action = ActionService.getAction("AgentSalesTarget", action_type)
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    table = "crmf_agent_sales_targets"

    if request.method == "GET":
        agent_id = request.GET.get("agent_id")
        period_type = request.GET.get("period_type")
        month = request.GET.get("month")
        year = request.GET.get("year")
        filter_json = request.GET.get("filter", "{}")
        # Use actual search input; default to empty string
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 50))
        sort_by = request.GET.get("sort_by" )
        sort_dir = request.GET.get("sort_dir")
        sort_by = f"{table}.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["agent_id", "period_type", "month", "year"]
        # Allow searching by agent id, name and email
        search_columns = [
            "core_users.display_name",
            "core_users.email",
            "period_type",
        ]
        allowed_sorting_columns = [
            "id",
            "agent_id",
            "period_type",
            "month",
            "year",
            "target_amount",
        ]
        query = QueryBuilderService(table)
        query = query.select(
            f"{table}.*",
            "core_users.display_name as agent_name",
            "core_users.email as agent_email",
        )
        query = query.leftJoin("core_users", f"{table}.agent_id", "core_users.id")
        if agent_id:
            query = query.where("agent_id", agent_id)
        if period_type:
            query = query.where("period_type", period_type)
        if month:
            query = query.where("month", month)
        if year:
            query = query.where("year", year)
        query = query.whereNull(f"{table}.deleted_at")
        query = query.apply_conditions(
            filter_json=filter_json,
            allowed_filters=allowed_filters,
            search_string=search_string,
            search_columns=search_columns,
        )
        data = query.paginate(
            page=page,
            limit=limit,
            allowed_sorting_columns=allowed_sorting_columns,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        # Add achieved to each record
        for item in data.get("data", []):
            achieved_value = calculate_agent_achieved(
                item["agent_id"], item["period_type"], item.get("month"), item["year"]
            )
            item["achieved"] = f"{achieved_value:.2f}"
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    if request.method == "POST":
        data = json.loads(request.body or "{}")
        targets = data if isinstance(data, list) else [data]
        rules = get_agent_sales_target_validation_rules()
        validation_errors = []
        duplicate_errors = []
        records_to_create = []
        for idx, target in enumerate(targets):
            agent_ids = target.get("agent_id")
            # Validate agent_id is present and not empty
            if not agent_ids:
                # Record agent_id required error
                validation_errors.append(
                    {"index": idx, "agent_id": ["Agent ID is required"]}
                )
                # Also validate remaining fields so caller gets full error map
                target_for_validation = target.copy()
                errors = ValidatorService.validate(
                    target_for_validation,
                    {k: v for k, v in rules.items() if k != "agent_id"},
                )
                if errors:
                    validation_errors.append({"index": idx, **errors})
                continue
            # Flatten agent_ids if nested (shouldn't be, but just in case)
            if isinstance(agent_ids, int):
                agent_ids = [agent_ids]
            elif isinstance(agent_ids, list):
                flat_agent_ids = []
                for a in agent_ids:
                    if isinstance(a, list):
                        flat_agent_ids.extend(a)
                    else:
                        flat_agent_ids.append(a)
                agent_ids = flat_agent_ids
            else:
                validation_errors.append(
                    {"index": idx, "agent_id": ["Must be a list or int."]}
                )
                continue
            # Validate all other fields except agent_id
            target_for_validation = target.copy()
            target_for_validation["agent_id"] = [1]  # dummy for validation
            errors = ValidatorService.validate(
                target_for_validation,
                {k: v for k, v in rules.items() if k != "agent_id"},
            )
            if errors:
                validation_errors.append({"index": idx, **errors})
                continue
            # Now check each agent_id for existence
            missing_agent_ids = []
            for agent_id in agent_ids:
                exists = QueryBuilderService("core_users").where("id", agent_id).first()
                if not exists:
                    missing_agent_ids.append(agent_id)
            if missing_agent_ids:
                validation_errors.append(
                    {
                        "index": idx,
                        "agent_id": [f"Agent(s) {missing_agent_ids} do not exist."],
                    }
                )
                continue
            for agent_id in agent_ids:
                record = target.copy()
                record["agent_id"] = agent_id
                record["created_at"] = timezone.now()
                record["updated_at"] = timezone.now()
                record["deleted_at"] = None
                exists = (
                    QueryBuilderService(table)
                    .where("agent_id", agent_id)
                    .where("period_type", record["period_type"])
                    .where("month", record.get("month"))
                    .where("year", record["year"])
                    .whereNull("deleted_at")
                    .first()
                )
                if exists:
                    duplicate_errors.append(
                        {
                            "index": idx,
                            "agent_id": agent_id,
                            "period_type": record["period_type"],
                            "month": record.get("month"),
                            "year": record["year"],
                            "error": f"Target for agent {agent_id}, period {record['period_type']}, month {record.get('month')}, year {record['year']} already exists.",
                            "existing": exists,
                        }
                    )
                else:
                    records_to_create.append(record)
        if validation_errors or duplicate_errors:
            # Transform errors to index-keyed format for bulk creation
            def add_error(field_name, message):
                msg_lower = str(message).strip().lower()
                if "required" in msg_lower:
                    error_type = "required"
                elif "must be" in msg_lower or "invalid" in msg_lower:
                    error_type = "invalid"
                elif "do not exist" in msg_lower or "not found" in msg_lower:
                    error_type = "not_found"
                elif "duplicate" in msg_lower or "already exists" in msg_lower:
                    error_type = "duplicate"
                else:
                    error_type = msg_lower.split(" ")[0] if msg_lower else "invalid"
                return {
                    "error_type": error_type,
                    "tokens": {"_attribute": field_name}
                }

            formatted_errors = {}

            # Process validation_errors: group by index
            for err in validation_errors:
                idx = err.get("index", 0)
                if idx not in formatted_errors:
                    formatted_errors[idx] = {}
                
                for key, value in err.items():
                    if key == "index":
                        continue
                    if key not in formatted_errors[idx]:
                        formatted_errors[idx][key] = []
                    if isinstance(value, list):
                        for msg in value:
                            formatted_errors[idx][key].append(add_error(key, msg))
                    else:
                        formatted_errors[idx][key].append(add_error(key, value))

            # Process duplicate_errors: group by index
            for dup in duplicate_errors:
                idx = dup.get("index", 0)
                if idx not in formatted_errors:
                    formatted_errors[idx] = {}
                
                target_fields = [k for k in ["agent_id", "period_type", "month", "year"] if k in dup]
                if not target_fields:
                    target_fields = ["agent_id"]
                for fld in target_fields:
                    if fld not in formatted_errors[idx]:
                        formatted_errors[idx][fld] = []
                    formatted_errors[idx][fld].append(add_error(fld, dup.get("error", "duplicate")))

            return ResponseService.response(
                "VALIDATION_ERROR",
                formatted_errors,
                Error.VALIDATION_ERROR,
            )
        created = []
        for record in records_to_create:
            obj = QueryBuilderService(table).insert(record)
            created.append(obj)
        return ResponseService.response(
            "SUCCESS", {"created": created}, Message.DATA_CREATED
        )


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def agent_sales_target_detail(request, id):
    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("AgentSalesTarget", action_map[request.method])
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    table = "crmf_agent_sales_targets"
    if request.method == "GET":
        data = QueryBuilderService(table)
        data = data.select(
            f"{table}.*",
            "core_users.display_name as agent_name",
            "core_users.email as agent_email",
        )
        data = data.leftJoin("core_users", f"{table}.agent_id", "core_users.id")
        data = data.where(f"{table}.id", id)
        data = data.first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        achieved_value = calculate_agent_achieved(
            data["agent_id"], data["period_type"], data.get("month"), data["year"]
        )
        data["achieved"] = f"{achieved_value:.2f}"
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
    if request.method == "PUT":
        data = json.loads(request.body or "{}")
        rules = get_agent_sales_target_update_rules()
        if "agent_id" in data and isinstance(data["agent_id"], list):
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"agent_id": ["Only a single value allowed."]},
                Error.VALIDATION_ERROR,
            )
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
            )
        updated = QueryBuilderService(table).where("id", id).update(data)
        if updated:
            return ResponseService.response("SUCCESS", updated, Message.DATA_UPDATED)
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    if request.method == "DELETE":
        now = timezone.now()
        updated = (
            QueryBuilderService(table)
            .where(f"{table}.id", id)
            .whereNull("deleted_at")
            .update({"deleted_at": now})
        )
        if updated:
            return ResponseService.response("SUCCESS", updated, Message.DATA_DELETED)
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
