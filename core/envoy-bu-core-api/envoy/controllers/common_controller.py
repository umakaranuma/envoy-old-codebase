import json
from datetime import datetime, timedelta
from math import ceil
from rest_framework.decorators import api_view
from django.core.exceptions import ValidationError

from envoy.models.channel import Channel
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
from envoy.models.currency import Currency
from envoy.models.entity_flag import EntityFlag
from envoy.models.global_setting import GlobalSetting
from envoy.models.interaction import Intraction
from envoy.models.setting_key import SettingKey
from envoy.utils import get_message
from envoy.models.flag import Flag
from django.db import connection
from django.http import StreamingHttpResponse
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from envoy.models.user import User


@api_view(["GET"])
def list_customer_requests(request):
    try:
        # Request parameters
        filter_json = request.GET.get("filters", "{}")
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by") or "cr.id"
        sort_dir = request.GET.get("sort_dir") or "desc"

        # Filter and search field config
        allowed_filters = [
            "cr.type",
            "cr.code",
            "rrt.risk_type_id",
            "rvp.vendor_product_id",
            "rvp.product_group_id",
        ]
        search_columns = [
            "cr.code",
            "cr.type",
            "st.name",
            "rt.title",
            "vp.name",
            "pg.name",
            "cu.name",
        ]
        allowed_sorting_columns = [
            "cr.id",
            "cr.code",
            "cr.type",
            "cr.submitted_at",
        ]

        # Query with joins (no pagination here)
        raw_data = (
            QueryBuilderService("cus_requests as cr")
            .leftJoin("core_status as st", "st.id", "cr.status_id")
            .leftJoin("cus_request_risk_types as rrt", "rrt.customer_request_id", "cr.id")
            .leftJoin("crm_opportunity_types as rt", "rt.id", "rrt.risk_type_id")
            .leftJoin("cus_request_vendor_products as rvp", "rvp.customer_request_id", "cr.id")
            .leftJoin("core_vendor_products as vp", "vp.id", "rvp.vendor_product_id")
            .leftJoin("core_product_groups as pg", "pg.id", "rvp.product_group_id")
            .leftJoin("core_customers as cu", "cu.id", "cr.created_by_id")
            .select(
                "cr.*",
                "st.name as status_name",
                "st.color as status_color",
                "rt.id as risk_type_id",
                "rt.title as risk_type_name",
                "vp.id as vendor_product_id",
                "vp.name as vendor_product_name",
                "pg.id as product_group_id",
                "pg.name as product_group_name",
                "cu.name as customer_name",
            )
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .orderBy(sort_by, sort_dir)
            .get()
        )

        grouped = {}
        for row in raw_data:
            rid = row["id"]
            if rid not in grouped:
                grouped[rid] = {
                    "id": row["id"],
                    "code": row["code"],
                    "type": row["type"],
                    "submitted_at": row["submitted_at"],
                    "is_draft": row["is_draft"],
                    "created_by_id": row["created_by_id"],
                    "form_submission_id": row["form_submission_id"],
                    "status_id": row["status_id"],
                    "status_name": row["status_name"],
                    "status_color": row["status_color"],
                    "customer_name": row["customer_name"],
                    "risk_types": [],
                    "vendor_products": [],
                }

            # Append unique risk_types
            if row["risk_type_id"] and not any(
                rt["id"] == row["risk_type_id"] for rt in grouped[rid]["risk_types"]
            ):
                grouped[rid]["risk_types"].append(
                    {
                        "id": row["risk_type_id"],
                        "name": row["risk_type_name"],
                    }
                )

            # Append unique vendor_products to vendor_products array
            if row["vendor_product_id"] and not any(
                p["id"] == row["vendor_product_id"] and p["type"] == "vendor_product"
                for p in grouped[rid]["vendor_products"]
            ):
                grouped[rid]["vendor_products"].append(
                    {
                        "id": row["vendor_product_id"],
                        "name": row["vendor_product_name"],
                        "type": "vendor_product",
                    }
                )

            # Append unique product_groups to vendor_products array
            if row["product_group_id"] and not any(
                p["id"] == row["product_group_id"] and p["type"] == "product_group"
                for p in grouped[rid]["vendor_products"]
            ):
                grouped[rid]["vendor_products"].append(
                    {
                        "id": row["product_group_id"],
                        "name": row["product_group_name"],
                        "type": "product_group",
                    }
                )

        # Pagination
        all_data = list(grouped.values())
        total = len(all_data)
        start = (page - 1) * limit
        end = start + limit
        paginated_data = all_data[start:end]

        result = {
            "total_records": total,
            "per_page": limit,
            "current_page": page,
            "last_page": ceil(total / limit) if limit else 1,
            "data": paginated_data,
        }

        return ResponseService.response(
            "SUCCESS", result, "Customer requests fetched successfully!"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def _create_lead_from_customer_request(request, customer_request, request_type: str):
    """
    Lightweight opportunity creation from a customer request.
    Only runs when request_type == 'quotation'.
    """
    try:
        print("DEBUG: _create_lead_from_customer_request called")
        print(f"DEBUG: request_type={request_type}")
        print(f"DEBUG: customer_request.id={customer_request.get('id')}, created_by_id={customer_request.get('created_by_id')}")
        # Resolve current user id (creator of the lead)
        user = getattr(request, "user", None)
        if isinstance(user, dict):
            created_by_id = user.get("id")
        else:
            created_by_id = getattr(user, "id", None)

        customer_id = customer_request.get("created_by_id")
        print(f"DEBUG: derived customer_id from request={customer_id}")

        # Fetch basic customer details (for type/name and optional contact info)
        customer = None
        if customer_id:
            customer = (
                QueryBuilderService("core_customers")
                .select("*")
                .where("id", customer_id)
                .first()
            )

        # Derive opportunity "type" from customer.type when available
        customer_type = (customer.get("type") if customer else "") or ""
        opp_type = customer_type.title() if customer_type else "Corporate"

        # Determine base currency (fallback to first currency if setting is not configured)
        base_currency_id = None
        try:
            base_currency_key = SettingKey.objects.filter(name="BASE_CURRENCY").first()
            if base_currency_key:
                global_setting = GlobalSetting.objects.filter(
                    setting_key=base_currency_key
                ).first()
                if global_setting and global_setting.value:
                    base_currency_id = int(global_setting.value)
        except Exception:
            base_currency_id = None

        print(f"DEBUG: initial base_currency_id from settings={base_currency_id}")

        if base_currency_id is None:
            first_currency = Currency.objects.first()
            if first_currency:
                base_currency_id = first_currency.id
        print(f"DEBUG: final base_currency_id={base_currency_id}")

        # Determine default stage (LEAD) from crm_opportunity_statuses
        stage_row = (
            QueryBuilderService("crm_opportunity_statuses")
            .select("id")
            .where("name", "LEAD")
            .first()
        )
        if not stage_row:
            stage_row = (
                QueryBuilderService("crm_opportunity_statuses")
                .select("id")
                .orderBy("id", "asc")
                .first()
            )
        stage_id = stage_row["id"] if stage_row else None

        # If we cannot determine critical references, skip lead creation
        if not base_currency_id or not stage_id or not customer_id:
            print(
                "DEBUG: Skipping lead creation due to missing references",
                f"base_currency_id={base_currency_id}, stage_id={stage_id}, customer_id={customer_id}",
            )
            return None

        # Compute sort_index so new lead appears first in the stage
        lowest_sort = (
            QueryBuilderService("crm_opportunities")
            .where("stage_id", stage_id)
            .orderBy("sort_index", "asc")
            .select("sort_index")
            .first()
        )
        if lowest_sort and lowest_sort.get("sort_index") is not None:
            sort_index = lowest_sort["sort_index"] / 2
        else:
            sort_index = 1

        # Generate a simple code and title based on last id
        last_row = (
            QueryBuilderService("crm_opportunities")
            .orderBy("id", "desc")
            .select("id")
            .first()
        )
        last_id = last_row["id"] if last_row else 0
        seq_no = last_id + 1

        title = f"Lead {seq_no}"
        if customer and customer.get("name") and customer_request.get("code"):
            title = f"Lead for {customer.get('name')} - {customer_request.get('code')}"

        # Generate ORD-style code (e.g. ORD-000217)
        code = f"ORD-{seq_no:06d}"

        # Optionally map product info (first linked product / group)
        product_map = (
            QueryBuilderService("cus_request_vendor_products")
            .select("vendor_product_id", "product_group_id")
            .where("customer_request_id", customer_request.get("id"))
            .first()
        )

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Create core_entities row for this opportunity (required for non-null entity_id)
        entity_payload = {
            "type": "Opportunity",
            "approvel_status": 0,
        }
        if created_by_id:
            entity_payload["created_by_id"] = created_by_id

        print("DEBUG: creating core_entities row for opportunity with", entity_payload)
        entity_row = QueryBuilderService("core_entities").insert(entity_payload)
        print("DEBUG: created core_entities row:", entity_row)

        if not entity_row or "id" not in entity_row:
            print("ERROR: Failed to create core_entities row for opportunity; aborting lead creation")
            return None

        opp_data = {
            "title": title,
            "code": code,
            "type": opp_type,
            "contact_info_type": "customer",
            "customer_id": customer_id,
            "stage_id": stage_id,
            "currency_id": base_currency_id,
            "transaction_type": "new",
            "created_by_id": created_by_id,
            "entity_id": entity_row["id"],
            "sort_index": sort_index,
            "created_at": now_str,
            "updated_at": now_str,
        }

        # Auto-assign sales_agent_id and account_manager_id similar to main create_opportunity flow
        sales_agent_id = created_by_id
        account_manager_id = None

        if sales_agent_id:
            try:
                team_user = (
                    QueryBuilderService("core_team_users")
                    .where("user_id", sales_agent_id)
                    .select("team_id")
                    .first()
                )
                if team_user and team_user.get("team_id"):
                    team = (
                        QueryBuilderService("core_teams")
                        .where("id", team_user["team_id"])
                        .select("manager_id")
                        .first()
                    )
                    if team and team.get("manager_id"):
                        account_manager_id = team["manager_id"]
                        print(
                            "DEBUG: Auto-assigned account_manager_id from team manager:",
                            account_manager_id,
                        )
            except Exception as e:
                print(
                    "WARNING: Failed to auto-assign account_manager_id for lead:",
                    type(e).__name__,
                    str(e),
                )

        if sales_agent_id:
            opp_data["sales_agent_id"] = sales_agent_id
        if account_manager_id:
            opp_data["account_manager_id"] = account_manager_id

        # Try to set country_id from customer row if column exists
        if customer and customer.get("country_id"):
            opp_data["country_id"] = customer["country_id"]

        if customer:
            contact_no = customer.get("contact_no")
            email = customer.get("email")
            if contact_no:
                opp_data["contact_number"] = contact_no
            if email:
                opp_data["email"] = email

        if product_map:
            if product_map.get("vendor_product_id"):
                opp_data["product_id"] = product_map["vendor_product_id"]
            if product_map.get("product_group_id"):
                opp_data["product_group_id"] = product_map["product_group_id"]

        print(f"DEBUG: opp_data to insert into crm_opportunities: {opp_data}")
        new_opportunity = QueryBuilderService("crm_opportunities").insert(opp_data)
        print(f"DEBUG: new_opportunity from insert: {new_opportunity}")

        # Generate tasks for this lead (same as "already set" flow: TaskService or in-repo default tasks)
        if new_opportunity and new_opportunity.get("id"):
            _generate_tasks_for_lead(
                opportunity_id=new_opportunity["id"],
                stage_id=stage_id,
                sales_agent_id=sales_agent_id,
                entity_id=new_opportunity.get("entity_id"),
            )

        return new_opportunity

    except Exception as e:
        print(
            "ERROR: Exception in _create_lead_from_customer_request:",
            type(e).__name__,
            str(e),
        )
        return None


def _generate_tasks_for_lead(opportunity_id, stage_id, sales_agent_id, entity_id=None):
    """
    Generate tasks for a newly created lead/opportunity.
    Tries TaskService.saveOppourinityTask / saveOpportunityTask if available (e.g. from envoy_bu_crm_api);
    otherwise creates default LEAD-stage tasks in core_tasks and links them via core_intractions.
    """
    try:
        # 1) Optional: call external TaskService if available
        try:
            from services.TaskService import TaskService
            TaskService.saveOppourinityTask(opportunity_id, stage_id, sales_agent_id)
            print("DEBUG: Tasks generated for lead via TaskService.saveOppourinityTask")
            return
        except (ImportError, AttributeError):
            pass
        try:
            from services.TaskService import TaskService
            if hasattr(TaskService, "saveOpportunityTask"):
                TaskService.saveOpportunityTask(opportunity_id, stage_id, sales_agent_id)
                print("DEBUG: Tasks generated for lead via TaskService.saveOpportunityTask")
                return
            if hasattr(TaskService, "saveOppourinityTask"):
                TaskService.saveOppourinityTask(opportunity_id, stage_id, sales_agent_id)
                print("DEBUG: Tasks generated for lead via TaskService.saveOppourinityTask")
                return
        except ImportError:
            pass

        # 2) In-repo fallback: create default tasks for LEAD and link to opportunity
        todo_status = (
            QueryBuilderService("core_task_status")
            .select("id")
            .where("type", "Todo")
            .first()
        )
        if not todo_status:
            todo_status = (
                QueryBuilderService("core_task_status")
                .select("id")
                .orderBy("id", "asc")
                .first()
            )
        task_status_id = todo_status.get("id") if todo_status else 1

        if not entity_id and opportunity_id:
            opp = (
                QueryBuilderService("crm_opportunities")
                .select("entity_id")
                .where("id", opportunity_id)
                .first()
            )
            entity_id = opp.get("entity_id") if opp else None
        if not entity_id:
            print("DEBUG: _generate_tasks_for_lead: no entity_id; skipping in-repo task creation")
            return

        channel_row = (
            QueryBuilderService("core_channels")
            .select("id")
            .orderBy("id", "asc")
            .first()
        )
        channel_id = channel_row.get("id") if channel_row else None
        if not channel_id:
            print("DEBUG: _generate_tasks_for_lead: no channel; skipping in-repo task creation")
            return

        contact_by_id = sales_agent_id or 1
        today = datetime.now().strftime("%Y-%m-%d")
        due = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")

        default_tasks = [
            ("Follow up - Lead", "Follow up on new lead"),
            ("Send quotation", "Prepare and send quotation to customer"),
        ]
        for i, (title, desc) in enumerate(default_tasks):
            task_code = f"TASK-{opportunity_id}-{i + 1}"
            task_row = QueryBuilderService("core_tasks").insert({
                "code": task_code,
                "task": title,
                "description": desc or "",
                "assigned_to_id": sales_agent_id,
                "assigned_date": today,
                "start_date": today,
                "due_date": due,
                "task_status_id": task_status_id,
                "sort_index": i + 1,
            })
            task_id = task_row.get("id") if isinstance(task_row, dict) else task_row
            if not task_id:
                continue
            QueryBuilderService("core_intractions").insert({
                "channel_id": channel_id,
                "contact_by_id": contact_by_id,
                "date": today,
                "entity_id": entity_id,
                "opportunity_id": opportunity_id,
                "task_id": task_id,
                "opportunity_status_id": stage_id,
            })
        print("DEBUG: Tasks generated for lead via in-repo default tasks")
    except Exception as e:
        print(
            "WARNING: _generate_tasks_for_lead failed:",
            type(e).__name__,
            str(e),
        )


def _create_risks_for_lead_from_customer_request(customer_request, created_lead):
    """
    Create crm_risks and crm_risk_submissions records for the confirmed request.
    - Uses cus_request_risk_types to get risk_type_ids.
    - Uses cus_requests.form_submission_id as submission_id.
    - Uses created_lead['id'] as lead_id.
    """
    try:
        if not created_lead or not created_lead.get("id"):
            print("DEBUG: _create_risks_for_lead_from_customer_request: no lead created; skipping risk creation")
            return []

        request_id = customer_request.get("id")
        customer_id = customer_request.get("created_by_id")
        submission_id = customer_request.get("form_submission_id")
        lead_id = created_lead["id"]

        print(
            "DEBUG: _create_risks_for_lead_from_customer_request",
            "request_id=", request_id,
            "customer_id=", customer_id,
            "submission_id=", submission_id,
            "lead_id=", lead_id,
        )

        if not customer_id or not submission_id:
            print("DEBUG: Missing customer_id or submission_id; skipping risk creation")
            return []

        # Get all risk_type_ids linked to this customer_request
        risk_type_rows = (
            QueryBuilderService("cus_request_risk_types")
            .select("risk_type_id")
            .where("customer_request_id", request_id)
            .get()
            or []
        )
        risk_type_ids = [
            r["risk_type_id"] for r in risk_type_rows if r.get("risk_type_id")
        ]

        if not risk_type_ids:
            print("DEBUG: No risk_type_ids found for customer_request; skipping risk creation")
            return []

        created_risks = []
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for rt_id in risk_type_ids:
            # 1) ALWAYS create a new crm_risks record for this confirmation
            last_risk = (
                QueryBuilderService("crm_risks")
                .orderBy("id", "desc")
                .select("id")
                .first()
            )
            last_risk_id = last_risk["id"] if last_risk else 0
            risk_seq = last_risk_id + 1
            # Match existing style like RISK-0038
            risk_code = f"RISK-{risk_seq:04d}"

            risk = QueryBuilderService("crm_risks").insert(
                {
                    "code": risk_code,
                    "customer_id": customer_id,
                    "risk_type_id": rt_id,
                    "is_deleted": 0,
                    "deleted_at": None,
                    "deleted_by_id": None,
                    "created_at": now_str,
                    "updated_at": now_str,
                }
            )
            print("DEBUG: Created new crm_risks row for confirmation:", risk)

            risk_id = risk.get("id")
            if not risk_id:
                continue

            # 2) Create crm_risk_submissions entry for this new risk + submission + lead
            latest_version_row = (
                QueryBuilderService("crm_risk_submissions")
                .select("version")
                .where("risk_id", risk_id)
                .orderBy("version", "desc")
                .first()
            )
            latest_version = (
                latest_version_row["version"]
                if latest_version_row and latest_version_row.get("version") is not None
                else 0
            )
            new_version = latest_version + 1

            submission_row = QueryBuilderService("crm_risk_submissions").insert(
                {
                    "risk_id": risk_id,
                    "submission_id": submission_id,
                    "lead_id": lead_id,
                    "version": new_version,
                    "created_at": now_str,
                    "updated_at": now_str,
                }
            )
            print("DEBUG: Created crm_risk_submissions row:", submission_row)

            created_risks.append(
                {
                    "risk_id": risk_id,
                    "risk_type_id": rt_id,
                    "submission_id": submission_id,
                    "lead_id": lead_id,
                    "version": new_version,
                }
            )

        return created_risks

    except Exception as e:
        print(
            "ERROR: Exception in _create_risks_for_lead_from_customer_request:",
            type(e).__name__,
            str(e),
        )
        return []


def _create_policy_request_from_customer_request(request, customer_request, payload: dict):
    """
    Create a minimal policy request (crmp_policy_base + crmp_request_policies)
    directly from a confirmed customer request, with an approved approval status.
    """
    try:
        now = datetime.now()
        user = getattr(request, "user", None)
        user_id = user.id if getattr(user, "is_authenticated", False) else None

        request_id = customer_request.get("id")
        customer_id = customer_request.get("created_by_id")
        form_submission_id = customer_request.get("form_submission_id")

        print(
            "DEBUG: _create_policy_request_from_customer_request",
            "request_id=",
            request_id,
            "customer_id=",
            customer_id,
            "form_submission_id=",
            form_submission_id,
        )

        if not customer_id:
            print("DEBUG: No customer_id on customer_request; skipping policy creation")
            return None

        # 1) Coverage details (sum_insured, dates) from cus_coverage_request_details
        coverage = (
            QueryBuilderService("cus_coverage_request_details as cov")
            .select("cov.sum_insured", "cov.start_date", "cov.end_date")
            .where("cov.customer_request_id", request_id)
            .first()
        ) or {}

        sum_insured = coverage.get("sum_insured")
        policy_start_date = coverage.get("start_date")
        policy_expiry_date = coverage.get("end_date")

        # 2) Primary risk_type_id from cus_request_risk_types
        risk_type_row = (
            QueryBuilderService("cus_request_risk_types")
            .select("risk_type_id")
            .where("customer_request_id", request_id)
            .first()
        )
        risk_type_id = risk_type_row.get("risk_type_id") if risk_type_row else None

        # 3) Product / group / insurer from cus_request_vendor_products
        vp_row = (
            QueryBuilderService("cus_request_vendor_products as cpvp")
            .leftJoin("core_vendor_products as vp", "vp.id", "cpvp.vendor_product_id")
            .select(
                "cpvp.vendor_product_id",
                "cpvp.product_group_id",
                "vp.vendor_id as insurer_id",
            )
            .where("cpvp.customer_request_id", request_id)
            .first()
        ) or {}

        product_id = vp_row.get("vendor_product_id")
        product_group_id = vp_row.get("product_group_id")
        insurer_id = vp_row.get("insurer_id")

        # 4) Determine sales_agent_id and account_manager_id
        sales_agent_id = user_id
        account_manager_id = None

        if sales_agent_id:
            try:
                team_user = (
                    QueryBuilderService("core_team_users")
                    .where("user_id", sales_agent_id)
                    .select("team_id")
                    .first()
                )
                if team_user and team_user.get("team_id"):
                    team = (
                        QueryBuilderService("core_teams")
                        .where("id", team_user["team_id"])
                        .select("manager_id")
                        .first()
                    )
                    if team and team.get("manager_id"):
                        account_manager_id = team["manager_id"]
                        print(
                            "DEBUG: _create_policy_request_from_customer_request auto-assigned account_manager_id:",
                            account_manager_id,
                        )
            except Exception as e:
                print(
                    "WARNING: Failed to auto-assign account_manager_id in policy creation:",
                    type(e).__name__,
                    str(e),
                )

        # 5) Resolve initial policy status for policy_base (PENDING ISSUANCE)
        policy_status_row = (
            QueryBuilderService("core_status")
            .select("id")
            .where("module", "policy")
            .where("type", "pol_pending_iss")
            .first()
        )
        if not policy_status_row:
            policy_status_row = (
                QueryBuilderService("core_status")
                .select("id")
                .where("module", "policy")
                .where("name", "PENDING ISSUANCE")
                .first()
            )
        policy_status_id = policy_status_row.get("id") if policy_status_row else None

        # 6) Insert into crmp_policy_base
        policy_base_data = {
            "customer_id": customer_id,
            "risk_type_id": risk_type_id,
            "insurer_id": insurer_id,
            "request_type_id": 1,  # 1 = New Request (per external convention)
            "product_id": product_id,
            "product_group_id": product_group_id,
            "sum_insured": sum_insured,
            "policy_start_date": policy_start_date,
            "policy_expiry_date": policy_expiry_date,
            "sales_agent_id": sales_agent_id,
            "account_manager_id": account_manager_id,
            "request_by_id": user_id,
            "status_id": policy_status_id,
            "created_at": now,
            "updated_at": now,
        }

        print("DEBUG: Inserting crmp_policy_base with", policy_base_data)
        policy_base = QueryBuilderService("crmp_policy_base").insert(policy_base_data)
        policy_base_id = policy_base.get("id") if isinstance(policy_base, dict) else policy_base
        print("DEBUG: Created crmp_policy_base row id=", policy_base_id)

        if not policy_base_id:
            print("ERROR: Failed to create crmp_policy_base; aborting policy request creation")
            return None

        # 6) Create entity + approvals (approved)
        entity = QueryBuilderService("core_entities").insert(
            {
                "type": "policy",
                "approvel_status": True,
                "created_at": now,
                "updated_at": now,
                "created_by_id": user_id,
            }
        )
        entity_id = entity.get("id") if isinstance(entity, dict) else entity
        print("DEBUG: Created core_entities row for policy entity_id=", entity_id)

        QueryBuilderService("core_entity_approvals").insert(
            {
                "entity_id": entity_id,
                "user": user_id,
                "role": None,
                "level": 1,
                "status": "approved",
                "remarks": "",
                "date": now,
            }
        )
        print("DEBUG: Inserted core_entity_approvals row with status=approved for entity_id=", entity_id)

        # 7) Resolve status_id for policy request (use PENDING ISSUANCE as default lifecycle status)
        status_row = (
            QueryBuilderService("core_status")
            .select("id")
            .where("module", "policy")
            .where("name", "PENDING ISSUANCE")
            .first()
        )
        status_id = status_row.get("id") if status_row else None

        # 8) Insert into crmp_request_policies
        policy_request_code = f"PR-{policy_base_id}"
        request_policy_row = QueryBuilderService("crmp_request_policies").insert(
            {
                "policy_request_id": policy_request_code,
                "policy_request_date": now.date().isoformat(),
                "entity_id": entity_id,
                "status_id": status_id,
                "policy_base_id": policy_base_id,
            }
        )
        request_policy_id = (
            request_policy_row.get("id")
            if isinstance(request_policy_row, dict)
            else request_policy_row
        )

        print(
            "DEBUG: Created crmp_request_policies row id=",
            request_policy_id,
            "policy_request_id=",
            policy_request_code,
        )

        return {
            "policy_base_id": policy_base_id,
            "request_policy_id": request_policy_id,
            "policy_request_code": policy_request_code,
        }

    except Exception as e:
        print(
            "ERROR: Exception in _create_policy_request_from_customer_request:",
            type(e).__name__,
            str(e),
        )
        return None


@api_view(["GET"])
def get_customer_requests_by_type(request):
    """
    Returns all rows from cus_requests (CustomerRequest)
    filtered by type (policy / quotation / claim), including related details.
    """
    try:
        request_type = request.GET.get("type")
        if not request_type:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"type": ["This query parameter is required."]},
                "Validation Error",
            )

        allowed_types = ["policy", "quotation", "claim"]
        if request_type not in allowed_types:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {
                    "type": [
                        f"Invalid type '{request_type}'. Expected one of {allowed_types}."
                    ]
                },
                "Validation Error",
            )

        all_columns = [
            # CustomerRequest fields
            "cus_requests.id",
            "cus_requests.code",
            "cus_requests.type",
            "cus_requests.submitted_at",
            "cus_requests.is_draft",
            "cus_requests.form_submission_id",
            "cus_requests.created_by_id",
            "cus_requests.status_id",
            # Customer details
            "core_customers.id as customer_id",
            "core_customers.code as customer_code",
            "core_customers.name as customer_name",
            "core_customers.type as customer_type",
            "core_customers.logo as customer_logo",
            "core_customers.remarks as customer_remarks",
            # Status details
            "core_status.id as status_id",
            "core_status.name as status_name",
            "core_status.description as status_description",
            "core_status.type as status_type",
            "core_status.module as status_module",
            "core_status.color as status_color",
            "core_status.sort_index as status_sort_index",
            # Form submission details
            "core_form_submissionss.id as form_submission_id",
            "core_form_submissionss.form_id as form_id",
            "core_form_submissionss.user_id as form_user_id",
            "core_form_submissionss.customer_id as form_customer_id",
        ]

        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by") or "cus_requests.id"
        sort_dir = request.GET.get("sort_dir") or "desc"
        allowed_sorting_columns = [
            "cus_requests.id",
            "cus_requests.code",
            "cus_requests.submitted_at",
        ]

        query = (
            QueryBuilderService("cus_requests")
            .select(*all_columns)
            .leftJoin(
                "core_customers",
                "core_customers.id",
                "cus_requests.created_by_id",
            )
            .leftJoin(
                "core_status",
                "core_status.id",
                "cus_requests.status_id",
            )
            .leftJoin(
                "core_form_submissionss",
                "core_form_submissionss.id",
                "cus_requests.form_submission_id",
            )
            .where("cus_requests.type", request_type)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        # Enrich each request with vendor product information (same structure as single view)
        if query and isinstance(query, dict) and query.get("data"):
            request_ids = [
                row.get("id") for row in query["data"] if row.get("id") is not None
            ]

            if request_ids:
                vendor_product_rows = (
                    QueryBuilderService("cus_request_vendor_products as cpvp")
                    .leftJoin(
                        "core_vendor_products as vp", "vp.id", "cpvp.vendor_product_id"
                    )
                    .leftJoin(
                        "core_product_groups as pg", "pg.id", "cpvp.product_group_id"
                    )
                    .leftJoin(
                        "core_service_providers as sp", "sp.id", "vp.vendor_id"
                    )
                    .select(
                        "cpvp.customer_request_id",
                        "cpvp.vendor_product_id",
                        "vp.name as vendor_product_name",
                        "cpvp.product_group_id",
                        "pg.name as product_group_name",
                        "sp.id as insurer_id",
                        "sp.name as insurer_name",
                        "sp.email as insurer_email",
                        "sp.contact_no as insurer_contact_no",
                    )
                    .whereIn("cpvp.customer_request_id", request_ids)
                    .get()
                    or []
                )

                products_by_request = {}
                insurers_by_request = {}
                for r in vendor_product_rows:
                    rid = r.get("customer_request_id")
                    if rid is None:
                        continue

                    products_by_request.setdefault(rid, []).append(
                        {
                            "vendor_product_id": r.get("vendor_product_id"),
                            "vendor_product_name": r.get("vendor_product_name"),
                            "product_group_id": r.get("product_group_id"),
                            "product_group_name": r.get("product_group_name"),
                        }
                    )

                    insurer_id = r.get("insurer_id")
                    if insurer_id:
                        insurers_by_request.setdefault(rid, {})
                        if insurer_id not in insurers_by_request[rid]:
                            insurers_by_request[rid][insurer_id] = {
                                "id": insurer_id,
                                "name": r.get("insurer_name"),
                                "email": r.get("insurer_email"),
                                "contact_no": r.get("insurer_contact_no"),
                            }

                for item in query["data"]:
                    rid = item.get("id")
                    item["vendor_products"] = products_by_request.get(rid, [])
                    insurers_map = insurers_by_request.get(rid, {})
                    item["insurers"] = list(insurers_map.values()) if insurers_map else []

        return ResponseService.response(
            "SUCCESS",
            query,
            "Customer requests fetched successfully.",
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to fetch customer requests.",
        )


# --------------------------------------------------------
# FULL DETAILS FOR A SINGLE CUSTOMER REQUEST
# Tables: cus_requests, cus_request_document_submissions, cus_coverage_request_details,
#         cus_policy_holders, cus_banks_details, cus_payment_request_details,
#         cus_request_risk_types, cus_request_vendor_products, cus_request_risk_details
# Filtered by customer_id (from request user) and request_id.
@api_view(["GET"])
def get_customer_request_full_details(request, request_id):
    try:
        # 1. Main request: cus_requests by request_id AND created_by_id (customer_id)
        #    Left join core_status, cus_policy_holders, cus_payment_request_details, cus_coverage_request_details
        customer_request = (
            QueryBuilderService("cus_requests as cr")
            .leftJoin("core_status as st", "st.id", "cr.status_id")
            .leftJoin("cus_policy_holders as ph", "ph.customer_request_id", "cr.id")
            .leftJoin("cus_payment_request_details as pd", "pd.customer_request_id", "cr.id")
            .leftJoin("cus_coverage_request_details as cov", "cov.customer_request_id", "cr.id")
            .select(
                "cr.id",
                "cr.code",
                "cr.type",
                "cr.form_submission_id",
                "cr.submitted_at",
                "cr.is_draft",
                "cr.created_by_id",
                "cr.status_id",
                "st.name as status_name",
                "ph.id as ph_id",
                "ph.policy_holder_name",
                "ph.date_of_birth",
                "ph.gender",
                "ph.nic",
                "ph.phone_number",
                "ph.email",
                "ph.address",
                "ph.contact_method",
                "pd.payment_method",
                "pd.payment_frequency",
                "pd.bank_number",
                "pd.account_holder_name",
                "pd.branch",
                "pd.bank_name",
                "pd.iban_swift_code",
                "pd.estimated_amount",
                "pd.created_at as payment_created_at",
                "cov.sum_insured",
                "cov.start_date",
                "cov.end_date",
                "cov.created_at as coverage_created_at",
            )
            .where("cr.id", request_id)
            .first()
        )

        if not customer_request:
            return ResponseService.response("NOT_FOUND", None, "Customer request not found")

        form_submission_id = customer_request.get("form_submission_id")

        # Build policy_holder object from joined columns
        policy_holder = None
        if customer_request.get("ph_id") is not None:
            policy_holder = {
                "id": customer_request.get("ph_id"),
                "policy_holder_name": customer_request.get("policy_holder_name"),
                "date_of_birth": customer_request.get("date_of_birth"),
                "gender": customer_request.get("gender"),
                "nic": customer_request.get("nic"),
                "phone_number": customer_request.get("phone_number"),
                "email": customer_request.get("email"),
                "address": customer_request.get("address"),
                "contact_method": customer_request.get("contact_method"),
            }

        # Build payment_details from joined columns
        payment_details = None
        if customer_request.get("payment_method") is not None:
            payment_details = {
                "payment_method": customer_request.get("payment_method"),
                "payment_frequency": customer_request.get("payment_frequency"),
                "bank_number": customer_request.get("bank_number"),
                "account_holder_name": customer_request.get("account_holder_name"),
                "branch": customer_request.get("branch"),
                "bank_name": customer_request.get("bank_name"),
                "iban_swift_code": customer_request.get("iban_swift_code"),
                "estimated_amount": str(customer_request.get("estimated_amount"))
                if customer_request.get("estimated_amount") is not None
                else None,
                "created_at": customer_request.get("payment_created_at"),
            }

        # Build coverages from joined columns
        coverages = None
        if customer_request.get("sum_insured") is not None or customer_request.get("start_date") is not None:
            coverages = {
                "sum_insured": customer_request.get("sum_insured"),
                "start_date": customer_request.get("start_date"),
                "end_date": customer_request.get("end_date"),
                "created_at": customer_request.get("coverage_created_at"),
            }

        # 2. Form values: core_form_submission_valuess left join custom/form elements
        form_values = []
        if form_submission_id:
            form_values_rows = (
                QueryBuilderService("core_form_submission_valuess as fsv")
                .leftJoin("core_form_custom_form_elements as cfe", "cfe.id", "fsv.custom_form_element_id")
                .leftJoin("core_form_elements as fe", "fe.id", "fsv.form_element_id")
                .select(
                    "fsv.custom_form_element_id",
                    "fsv.form_element_id",
                    "fsv.value",
                    "cfe.label",
                    "cfe.code as element_code",
                    "fe.title as element_title",
                    "fe.category as element_category",
                )
                .where("fsv.form_submission_id", form_submission_id)
                .get()
            )
            if form_values_rows:
                form_values = [
                    {
                        "custom_form_element_id": r.get("custom_form_element_id"),
                        "form_element_id": r.get("form_element_id"),
                        "value": r.get("value"),
                        "label": r.get("label"),
                        "code": r.get("element_code"),
                        "element_title": r.get("element_title"),
                        "element_category": r.get("element_category"),
                    }
                    for r in form_values_rows
                ]

        # 3. Documents: cus_request_document_submissions left join core_product_document_types (document_type)
        documents_raw = (
            QueryBuilderService("cus_request_document_submissions as dr")
            .leftJoin("core_product_document_types as pdt", "pdt.id", "dr.document_type_id")
            .select(
                "dr.document_type_id",
                "pdt.name as document_type__name",
                "dr.value",
                "dr.uploaded_at",
            )
            .where("dr.customer_request_id", request_id)
            .get()
        )
        documents = (
            [
                {
                    "document_type_id": d.get("document_type_id"),
                    "document_type__name": d.get("document_type__name"),
                    "value": d.get("value"),
                    "uploaded_at": d.get("uploaded_at"),
                }
                for d in documents_raw
            ]
            if documents_raw
            else []
        )

        # 4. Risk type objects: cus_request_risk_types left join crm_opportunity_types (risk_type_id, risk_type_name)
        risk_type_rows = (
            QueryBuilderService("cus_request_risk_types as crt")
            .leftJoin("crm_opportunity_types as ot", "ot.id", "crt.risk_type_id")
            .select("crt.risk_type_id", "ot.title as risk_type_name")
            .where("crt.customer_request_id", request_id)
            .get()
        )
        risk_types = (
            [
                {
                    "risk_type_id": r.get("risk_type_id"),
                    "risk_type_name": r.get("risk_type_name"),
                }
                for r in (risk_type_rows or [])
                if r.get("risk_type_id") is not None
            ]
            if risk_type_rows
            else []
        )

        # 5. Vendor product objects & insurers: cus_request_vendor_products + vendor & insurer details
        vendor_product_rows = (
            QueryBuilderService("cus_request_vendor_products as cpvp")
            .leftJoin("core_vendor_products as vp", "vp.id", "cpvp.vendor_product_id")
            .leftJoin("core_product_groups as pg", "pg.id", "cpvp.product_group_id")
            .leftJoin("core_service_providers as sp", "sp.id", "vp.vendor_id")
            .select(
                "cpvp.vendor_product_id",
                "vp.name as vendor_product_name",
                "cpvp.product_group_id",
                "pg.name as product_group_name",
                "sp.id as insurer_id",
                "sp.name as insurer_name",
                "sp.email as insurer_email",
                "sp.contact_no as insurer_contact_no",
            )
            .where("cpvp.customer_request_id", request_id)
            .get()
        )
        vendor_products = (
            [
                {
                    "vendor_product_id": r.get("vendor_product_id"),
                    "vendor_product_name": r.get("vendor_product_name"),
                    "product_group_id": r.get("product_group_id"),
                    "product_group_name": r.get("product_group_name"),
                }
                for r in (vendor_product_rows or [])
            ]
            if vendor_product_rows
            else []
        )

        # Build unique insurers list from joined rows
        insurers_map = {}
        for r in (vendor_product_rows or []):
            insurer_id = r.get("insurer_id")
            if insurer_id and insurer_id not in insurers_map:
                insurers_map[insurer_id] = {
                    "id": insurer_id,
                    "name": r.get("insurer_name"),
                    "email": r.get("insurer_email"),
                    "contact_no": r.get("insurer_contact_no"),
                }
        insurers = list(insurers_map.values())

        # 6. Risk details documents: cus_request_risk_details
        risk_docs_raw = (
            QueryBuilderService("cus_request_risk_details")
            .select("type", "document_name", "document_link", "uploaded_at")
            .where("customer_request_id", request_id)
            .get()
        )
        risk_documents = (
            [
                {
                    "type": r.get("type"),
                    "document_name": r.get("document_name"),
                    "document_link": r.get("document_link"),
                    "uploaded_at": r.get("uploaded_at"),
                }
                for r in risk_docs_raw
            ]
            if risk_docs_raw
            else []
        )

        # 7. Bank details: cus_banks_details by customer_id derived from the request itself
        bank_details = None
        request_customer_id = customer_request.get("created_by_id")
        if request_customer_id is not None:
            bank_details = (
                QueryBuilderService("cus_banks_details")
                .select(
                    "id",
                    "customer_id",
                    "account_holder_name",
                    "bank_name",
                    "bank_branch",
                    "account_number",
                    "iban_swift_code",
                    "doc",
                    "doc_type",
                    "doc_name",
                    "created_at",
                    "updated_at",
                )
                .where("customer_id", request_customer_id)
                .whereNull("deleted_at")
                .first()
            )

        return ResponseService.response(
            "SUCCESS",
            {
                "request_id": customer_request.get("id"),
                "request_code": customer_request.get("code"),
                "type": customer_request.get("type"),
                "status": customer_request.get("status_name"),
                "risk_types": risk_types,
                "vendor_products": vendor_products,
                "insurers": insurers,
                "form_submission_id": form_submission_id,
                "form_values": form_values,
                "documents": documents,
                "coverages": coverages,
                "policy_holder": policy_holder,
                "payment_details": payment_details,
                "risk_documents": risk_documents,
                "bank_details": bank_details,
            },
            "Customer request full details fetched successfully",
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to fetch request details",
        )


@api_view(["POST"])
def confirm_customer_request(request, request_id):
    try:
        try:
            payload = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "Invalid JSON format"},
                "Validation Error",
            )

        request_type = (payload.get("type") or "").lower()
        print(
            "DEBUG: confirm_customer_request payload=",
            payload,
            "resolved request_type=",
            request_type,
        )

        customer_request = (
            QueryBuilderService("cus_requests as cr")
            .select("cr.*")
            .where("cr.id", request_id)
            .first()
        )
        print("DEBUG: confirm_customer_request loaded customer_request=", customer_request)

        if not customer_request:
            return ResponseService.response(
                "NOT_FOUND", None, "Customer request not found"
            )

        # Resolve approved status id for customer requests
        status_row = (
            QueryBuilderService("core_status")
            .select("id")
            .where("module", "customer")
            .where("type", "customer_request_approved")
            .first()
        )
        if not status_row:
            status_row = (
                QueryBuilderService("core_status")
                .select("id")
                .where("module", "customer")
                .where("name", "APPROVED")
                .first()
            )

        new_status_id = status_row["id"] if status_row else None
        print("DEBUG: confirm_customer_request resolved new_status_id=", new_status_id)

        update_payload = {
            "is_draft": 0,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        if new_status_id is not None:
            update_payload["status_id"] = new_status_id

        QueryBuilderService("cus_requests").where("id", request_id).update(
            update_payload
        )
        print("DEBUG: confirm_customer_request updated cus_requests with", update_payload)

        created_lead = None
        created_risks = []
        created_policy = None
        if request_type == "quotation":
            print("DEBUG: request_type is quotation, attempting to create lead")
            created_lead = _create_lead_from_customer_request(
                request, customer_request, request_type
            )
            created_risks = _create_risks_for_lead_from_customer_request(
                customer_request, created_lead
            )
        elif request_type == "policy":
            print("DEBUG: request_type is policy, creating policy request instead of lead")
            created_policy = _create_policy_request_from_customer_request(
                request, customer_request, payload
            )
        else:
            print("DEBUG: request_type is neither quotation nor policy; skipping lead/risk/policy creation")

        result = {
            "request_id": request_id,
            "status_id": new_status_id,
            "lead": created_lead,
            "risks": created_risks,
            "policy_request": created_policy,
        }
        print("DEBUG: confirm_customer_request final result payload=", result)

        return ResponseService.response(
            "SUCCESS",
            result,
            "Customer request confirmed successfully",
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to confirm customer request",
        )


# --------------------------------------------------------
# GET /channels & POST /channels - List all channels or create a new channel
@api_view(["GET", "POST"])
def channels(request):
    """Handle GET (List all) and POST (Create) operations for Channels"""
    if request.method == "GET":
        return get_channels(request)
    elif request.method == "POST":
        return create_channel(request)

# --------------------------------------------------------

def get_channels(request):
    """Retrieve all channels"""
    try:
        all_columns = ["*"]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["name", "description"]
        search_columns = ["name", "description"]
        allowed_sorting_columns = ["name","description"]

        
        query = (
            QueryBuilderService("core_channels")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response(
            "SUCCESS",
            query,
            get_message("RETRIEVED", entity="Channels")
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            get_message("SERVER_ERROR", entity="Channels")
        )


def create_channel(request):
    try:
        data = json.loads(request.body)

        # Validation rules
        rules = {
            "name": "required|max:255|unique:core_channels,name",
            
            # "description": "max:255",  # You can add this if needed
        }

        custom_messages = {
            "name.unique": "This channel name already exists.",
            "name.required": "Channel Name is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Create the channel
        channel = Channel.objects.create(
            name=data["name"],
            description=data.get("description", ""),  # <-- safer access
        )

        response_data = {
            "id": channel.id,
            "name": channel.name,
            "description": channel.description,
        }

        return ResponseService.response(
            "SUCCESS", response_data, "channel_created_successfully"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )



@api_view(["GET", "PUT", "DELETE"])
def channel_detail(request, id):
    if request.method == "GET":
        return get_channel(request, id)
    elif request.method == "PUT":
        return update_channel(request, id)
    elif request.method == "DELETE":
        return delete_channel(request, id)

def get_channel(request, id):
    try:
        channel = (
            QueryBuilderService("core_channels")
            .select("*",)
            .where("id", id)
            .first()
        )

        if not channel:
            return ResponseService.response(
                "NOT_FOUND", None, f"Channel with ID {id} does not exist"
            )

        return ResponseService.response(
            "SUCCESS", channel, "Channel retrieved successfully!"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def update_channel(request, id):
    try:
        channel = Channel.objects.filter(id=id).first()
        if not channel:
            return ResponseService.response(
                "NOT_FOUND", {}, "Channel not found"
            )

        data = json.loads(request.body)

        # Validation rules
        rules = {
            "name": f"required|max:255|unique:core_channels,name,{id}",
        }

        custom_messages = {
            "name.unique": "This channel name already exists.",
            "name.required": "Channel Name is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        
        channel.name = data.get("name", channel.name)
        channel.description = data.get("description", channel.description)
        channel.save()

        response_data = {
            "id": channel.id,
            "name": channel.name,
            "description": channel.description,
        }

        return ResponseService.response(
            "SUCCESS", response_data, "channel_updated_successfully"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def delete_channel(request, id):
    try:
        # Validation Rules
        rules = {
            "id": "required|exists:core_channels,id"
        }
        custom_messages = {
            "id.required": "Channel ID is required.",
            "id.exists": "Channel with the given ID does not exist.",
        }

        errors = ValidatorService.validate({"id": id}, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Check if channel exists
        channel = Channel.objects.filter(id=id).first()
        if not channel:
            return ResponseService.response("VALIDATION_ERROR", [], "data_not_found")

        # Prevent deletion if referenced in Intraction
        if Intraction.objects.filter(channel_id=id).exists():
            return ResponseService.response("CONFLICT", [], "channel_delete_conflict_msg")

        # Delete the channel
        channel.delete()

        return ResponseService.response("SUCCESS", "Deleted", "channel_delete_error_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")





# --------------------------------------------------------
# GET /currencies - Retrieve all currencies
@api_view(["GET"])
def get_currencies(request):
    try:

        all_columns = ["*"]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_filters = ["symbol", "name", "code"]
        search_columns = ["symbol", "name", "code"]
        allowed_sorting_columns = ["symbol", "name", "code"]

        query = (
            QueryBuilderService("core_currencies")
            .select(*all_columns)
            .apply_conditions(
                filter_json, allowed_filters, search_string, search_columns
            )
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response(
            "SUCCESS", query, "Currencies fetched successfully."
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )


@api_view(["GET"])
def get_statuses(request):
    """Retrieve all statuses with optional pagination, filtering, and search."""
    try:
        all_columns = ["*"]
        # Use "{}" default so filter is always a string (QueryBuilderService expects JSON string)
        filter_raw = request.GET.get("filter", "{}")
        if isinstance(filter_raw, str):
            try:
                filter_json = json.loads(filter_raw) if filter_raw.strip() else {}
            except (json.JSONDecodeError, TypeError):
                filter_json = {}
        else:
            filter_json = {}
        # Support direct ?module= param to filter by module (apply via .where() so it always works)
        module_param = request.GET.get("module")
        if module_param is not None and module_param != "":
            filter_json["module"] = module_param
        filter_for_query = json.dumps(filter_json)
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "sort_index")
        sort_dir = request.GET.get("sort_dir", "asc")
        allowed_filters = ["name", "type", "module", "description"]
        search_columns = ["name", "type", "module", "description"]
        allowed_sorting_columns = ["id", "name", "type", "module", "sort_index", "color"]

        query = (
            QueryBuilderService("core_status")
            .select(*all_columns)
            .apply_conditions(
                filter_for_query, allowed_filters, search_string, search_columns
            )
        )
        if module_param is not None and module_param != "":
            query = query.where("module", module_param)
        # For claim module, return only these 3 status types
        if module_param and str(module_param).strip().lower() == "claim":
            query = query.whereIn("type", ["Claim_draft", "Claim_notified", "Claim_submitted"])
        query = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

        return ResponseService.response(
            "SUCCESS", query, "Statuses fetched successfully."
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )


@api_view(["GET"])
def get_currency_by_id(request, id):
    """
    Retrieve a specific currency by its ID using QueryBuilderService.
    """
    try:
        # Fetch the currency by ID using QueryBuilderService
        currency = (
            QueryBuilderService("core_currencies")
            .select("id", "symbol", "name", "decimal_digits", "rounding", "code")
            .where("id", id)
            .first()
        )

        if not currency:
            return ResponseService.response(
                "NOT_FOUND", None, f"Currency with ID {id} does not exist"
            )

        return ResponseService.response(
            "SUCCESS", currency, "Currency fetched successfully."
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )

# --------------------------------------------------------
# GET /flags - Get all flags

@api_view(["GET", "POST"])
def flag_get(request):
    if request.method == "GET":
        return get_flags(request)
    elif request.method == "POST":
        return create_flag(request)
    
    
def get_flags(request):
    try:
        all_columns = ["*"]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        entity_id = request.GET.get("entity_id", "")

        allowed_filters = ["name", "color"]
        search_columns = ["name", "description"]
        allowed_sorting_columns = ["name", "color"]

        # Step 1: Get related flag IDs
        excluded_flag_ids = []
        if entity_id:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT flag_id FROM core_entity_flags WHERE entity_id = %s",
                    [entity_id]
                )
                rows = cursor.fetchall()
                excluded_flag_ids = [row[0] for row in rows]

        # Step 2: Build the query with .whereNotIn()
        query_builder = (
            QueryBuilderService("core_flags")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        )

        if excluded_flag_ids:
            query_builder.whereNotIn("id", excluded_flag_ids)

        query = query_builder.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

        return ResponseService.response("SUCCESS", query, "Flags retrieved successfully.")
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


# --------------------------------------------------------
# GET /flags/<id>, PUT /flags/<id>, DELETE /flags/<id>
@api_view(["GET", "PUT", "DELETE"])
def flag_detail(request, id):
    if request.method == "GET":
        return get_flag(request, id)
    elif request.method == "PUT":
        return update_flag(request, id)
    elif request.method == "DELETE":
        return delete_flag(request, id)

# --------------------------------------------------------
def get_flag(request, id):
    try:
        flag = (
            QueryBuilderService("core_flags")
            .select("core_flags.id", "core_flags.name", "core_flags.description", "core_flags.color")
            .where("core_flags.id", id)
            .first()
        )

        if not flag:
            return ResponseService.response(
                "NOT_FOUND", None, f"Flag with ID {id} does not exist"
            )

        return ResponseService.response(
            "SUCCESS", flag, "Flag retrieved successfully."
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )

# --------------------------------------------------------
def create_flag(request):
    try:
        data = json.loads(request.body)

        rules = {
            "name": "required|unique:core_flags,name|max:255",
            # "color": "required|max:100",  # Hex color like #FF0000
            "description": "nullable",
        }

        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        flag = Flag.objects.create(
            name=data["name"],
            description=data.get("description", ""),
            color=data.get("color",""),
        )

        response_data = {
            "id": flag.id,
            "name": flag.name,
            "description": flag.description,
            "color": flag.color,
        }

        return ResponseService.response(
            "SUCCESS", response_data, "default_create_success_msg"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )

# --------------------------------------------------------
def update_flag(request, id):
    try:
        data = json.loads(request.body)

        flag = Flag.objects.filter(id=id).first()
        if not flag:
            return ResponseService.response("NOT_FOUND", {}, "Flag not found.")

        # Apply validation
        rules = {
            "name": f"required|unique:core_flags,name,{id}|max:255",
            "description": "nullable",
        }

        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Safe assignment with fallback to existing values
        flag.name = data.get("name", flag.name)
        flag.description = data.get("description", flag.description)
        flag.color = data.get("color", flag.color)
        flag.save()

        response_data = {
            "id": flag.id,
            "name": flag.name,
            "description": flag.description,
            "color": flag.color,
        }

        return ResponseService.response("SUCCESS", response_data, "default_update_success_msg")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


# --------------------------------------------------------
def delete_flag(request, id):
    try:
        # Validation rules
        rules = {
            "id": "required|exists:core_flags,id"
        }
        custom_messages = {
            "id.required": "Flag ID is required.",
            "id.exists": "The specified flag does not exist.",
        }

        errors = ValidatorService.validate({"id": id}, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        flag = Flag.objects.filter(id=id).first()
        if not flag:
            return ResponseService.response("NOT_FOUND", {}, "Flag not found.")

        # Check if this flag is referenced by any EntityFlag (foreign key constraint)
        if EntityFlag.objects.filter(flag_id=id).exists():
            return ResponseService.response("CONFLICT", [], "flag_delete_error_msg")

        flag.delete()
        return ResponseService.response("SUCCESS", {}, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET"])
def get_current_user(request):
    """
    Retrieve the details of the currently authenticated user using QueryBuilderService.
    """
    try:
        user = getattr(request, "user", None)
        

        user_data = (
            QueryBuilderService("core_users")
            .select(
                "core_users.id",
                "core_users.email",
                "core_users.first_name",
                "core_users.last_name",
                "core_users.display_name",
                "core_users.contact_no",
                "core_users.picture",
                "core_users.idp_user_id",
                "core_roles.id as role_id",
                "core_roles.name as role_name",
                "core_entities.id as entity_id",
                "core_entities.type as entity_type"
            )
            .leftJoin("core_roles", "core_roles.id", "core_users.role_id")
            .leftJoin("core_entities", "core_entities.id", "core_users.entity_id")
            .where("core_users.id", user.id)
            .first()
        )

        if not user_data:
            return ResponseService.response(
                "NOT_FOUND", {}, "User not found."
            )

        formatted_user = {
                "id": user_data["id"],
                "email": user_data["email"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "display_name": user_data["display_name"],
                "contact_no": user_data["contact_no"],
                "picture": user_data["picture"],
                "idp_user_id": user_data["idp_user_id"],
                "is_active": True,  # Always true from your property
                "role": {
                    "id": user_data["role_id"],
                    "name": user_data["role_name"]
                },
                "entity": {
                    "id": user_data["entity_id"],
                    "type": user_data["entity_type"]
                }
            }


        return ResponseService.response(
            "SUCCESS",
            formatted_user,
            "User details retrieved successfully."
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )


@api_view(["GET"])
def get_user_permissions(request):
    """
    Get a flat list of permissions (e.g., 'TASK_VIEW') based on the current user's role.
    Optional: Filter by module keys using ?module_key=core,crm
    """
    try:
        user = getattr(request, "user", None)
        if not user or not getattr(user, "role_id", None):
            return ResponseService.response("FORBIDDEN", {}, "User role not found.")

        # Optional module key filtering
        module_keys_param = request.GET.get("module_key", None)
        module_ids = []

        if module_keys_param:
            module_keys = [key.strip() for key in module_keys_param.split(",") if key.strip()]
            if module_keys:
                modules = (
                    QueryBuilderService("core_modules")
                    .select("id", "`key`")
                    .whereIn("`key`", module_keys)
                    .get()
                )
                module_ids = [mod["id"] for mod in modules]

                # If module keys were passed but none matched, return empty list
                if not module_ids:
                    return ResponseService.response("SUCCESS", [], "no_permissions_found")

        # Step 1: Get all action_ids for the role
        role_actions = (
            QueryBuilderService("core_role_authorities")
            .select("action_id")
            .where("role_id", user.role_id)
            .get()
        )
        action_ids = [ra["action_id"] for ra in role_actions]

        if not action_ids:
            return ResponseService.response("SUCCESS", [], "no_permissions_found")

        # Step 2: Fetch actions from core_actions with optional module_id filter
        action_query = QueryBuilderService("core_actions").select("entity", "action").whereIn("id", action_ids)

        if module_ids:
            action_query = action_query.whereIn("module_id", module_ids)

        actions = action_query.get()

        # Step 3: Format into 'ENTITY_ACTION' strings
        permission_list = [f"{a['entity'].upper()}_{a['action'].upper()}" for a in actions]

        return ResponseService.response("SUCCESS", permission_list, "permission_fetch_success_msg")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )
# --------------------------------Service Providers------------------------

@api_view(["GET","POST"])
def service_providers(request):

    if request.method == 'GET':
        return get_service_providers(request)
    
    elif request.method == 'POST':
        return create_service_provider(request)
    
def get_service_providers(request):
    all_columns = [
        "core_service_providers.id",
        "core_service_providers.name",
        "core_service_providers.description",
        "core_service_providers.status",
        "core_service_providers.email",
    ]   

    filter_json = request.GET.get("filter", {}) 
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_service_providers.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["core_service_providers.id", "core_service_providers.name"]
    search_columns = ["core_service_providers.id", "core_service_providers.name"]
    allowed_sorting_columns = ["core_service_providers.id", "core_service_providers.name"]

    query = QueryBuilderService("core_service_providers")\
            .select(*all_columns)\
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    
    return ResponseService.response('SUCCESS',query, "data_fatched")

def create_service_provider(request):

    data = request.data
    
    # Set default status to 'active' if not provided
    if 'status' not in data:
        data['status'] = 'active'
    
    rules = {
        "name": "required|unique:core_service_providers,name",
        "description": "max:255",
        "email": "required|email",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
    
    new_data = QueryBuilderService("core_service_providers").insert(data)

    return ResponseService.response("SUCCESS", new_data, "default_create_success_msg")


@api_view(["GET","PUT","DELETE"])
def manage_service_provider(request, id):

    if request.method == 'GET':
        return get_single_service_provider(id)
    
    elif request.method == 'PUT':
        return update_service_provider(request, id)
    
    elif request.method == 'DELETE':
        return delete_service_provider(id)
    
def get_single_service_provider(id):

    all_columns = [
        "core_service_providers.id",
        "core_service_providers.name",
        "core_service_providers.description",
        "core_service_providers.status",
        "core_service_providers.email",

    ]

    query = QueryBuilderService("core_service_providers")\
            .select(*all_columns)\
            .where("core_service_providers.id", id)\
            .first()
    
    if not query:
        return ResponseService.response('NOT_FOUND',[], "Error.NOT_FOUND")
    
    return ResponseService.response('SUCCESS',query, "data_fatched")

def update_service_provider(request, id):
    data = request.data

    rules = {
        "name": "required|unique:core_service_providers,name," + str(id),
        "description": "max:255",
        "email": "required|email",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    # Update the service provider
    updated_data = QueryBuilderService("core_service_providers").where("id", id).update(data)

    return ResponseService.response("SUCCESS", updated_data, "default_update_success_msg")

def delete_service_provider(id):

    exisiting_data = QueryBuilderService("core_service_providers").where("id", id).first()
    if not exisiting_data:
        return ResponseService.response('NOT_FOUND',[], "data_not_found")
    
    using_data = QueryBuilderService("crmq_quotation_service_providers").where("service_provider_id", id).first()

    if using_data:
        return ResponseService.response('CONFLICT',[], "service_provider_delete_error_msg")
    # Delete the service provider
    deleted_data = QueryBuilderService("core_service_providers").where("id", id).delete()

    if not deleted_data:
        return ResponseService.response('NOT_FOUND',[], "Error.NOT_FOUND")

    return ResponseService.response("SUCCESS", deleted_data, "default_delete_success_msg")

# -------------------------------------------------------------------------------------------




@api_view(['GET'])
def get_all_countries(request):
    """Retrieve all countries with optional pagination, filtering, and search."""
    try:
        all_columns = ["*"]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        
        allowed_filters = ["name", "code"]
        search_columns = ["name", "code"]
        allowed_sorting_columns = ["name", "code"]

        query = (
            QueryBuilderService("core_countries")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response(
            "SUCCESS",
            query,
            get_message("RETRIEVED", entity="Countries")
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            get_message("SERVER_ERROR", entity="Countries")
        )


@api_view(['GET'])
def get_country_by_id(request, id):
    """Retrieve a specific country by ID."""
    try:
        country = QueryBuilderService("core_countries") \
            .select("*") \
            .where("id", id) \
            .first()
        
        if not country:
            return ResponseService.response(
                "NOT_FOUND",
                None,
                get_message("NOT_FOUND", entity="Country")
            )
        
        return ResponseService.response(
            "SUCCESS",
            country,
            get_message("RETRIEVED", entity="Country")
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            get_message("SERVER_ERROR", entity="Country")
        )


@api_view(["GET"])
def get_base_currency(request):
    try:
        # Step 1: Find SettingKey for BASE_CURRENCY
        base_currency_key = SettingKey.objects.filter(name="BASE_CURRENCY").first()
        if not base_currency_key:
            return ResponseService.response("NOT_FOUND", None, "BASE_CURRENCY setting key not found.")

        # Step 2: Find GlobalSetting value for this key
        global_setting = GlobalSetting.objects.filter(setting_key=base_currency_key).first()
        if not global_setting or not global_setting.value:
            return ResponseService.response("NOT_FOUND", None, "BASE_CURRENCY value not configured.")

        base_currency_value = global_setting.value

        # Step 3: Fetch currency details from Currency table
        currency = Currency.objects.filter(id=base_currency_value).first()
        if not currency:
            return ResponseService.response("NOT_FOUND", None, "Currency not found for BASE_CURRENCY.")

        currency_data = {
            "id": currency.id,
            "symbol": currency.symbol,
            "name": currency.name,
            "decimal_digits": currency.decimal_digits,
            "rounding": currency.rounding,
            "code": currency.code
        }

        return ResponseService.response("SUCCESS", currency_data, "Base currency fetched successfully.")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )


@api_view(["GET"])
def notification_unread_count(request):
    """
    Lightweight endpoint for live polling: returns unread notification count for the current user.
    Frontend can poll this every 15-30 seconds to show a badge; when count > 0 or user opens
    the notifications panel, call GET /api/all-notifications to fetch the list.
    """
    try:
        user_id = getattr(request.user, "id", None)
        if not user_id:
            return Response({
                "is_success": False,
                "message": "User not authenticated",
                "unread_count": 0,
            }, status=401)
        data = (
            QueryBuilderService("core_notification_users")
            .select("id", "is_read")
            .where("user_id", user_id)
            .where("is_clear", 0)
            .get()
        )
        rows = data.get("data", []) if isinstance(data, dict) else (data or [])
        unread_count = sum(1 for r in rows if str(r.get("is_read")) not in ("1", 1))
        return Response({
            "is_success": True,
            "message": "unread_count",
            "unread_count": unread_count,
        })
    except Exception as e:
        return Response({
            "is_success": False,
            "message": str(e),
            "unread_count": 0,
        }, status=500)


def _get_user_for_notification_stream(request):
    """
    For GET /api/notifications/stream we accept token in query (EventSource cannot send headers).
    Returns (user_id, None) on success or (None, response) to return an error response.
    """
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        raw_token = auth_header.split(" ")[1]
    else:
        raw_token = request.GET.get("token", "").strip()
    if not raw_token:
        return None, Response({
            "is_success": False,
            "message": "Token required (header Authorization: Bearer <token> or query param token=)",
        }, status=401)
    try:
        jwt_auth = JWTAuthentication()
        validated = jwt_auth.get_validated_token(raw_token)
        user_id = validated.get("user_id")
        if not user_id:
            return None, Response({"is_success": False, "message": "Invalid token"}, status=401)
        user = User.objects.filter(id=user_id).first()
        if not user:
            return None, Response({"is_success": False, "message": "User not found"}, status=401)
        return user_id, None
    except InvalidToken:
        return None, Response({"is_success": False, "message": "Invalid or expired token"}, status=401)


def _notification_stream_generator(user_id):
    """Generator that yields SSE lines. Pushes new_notification when backend creates one."""
    from envoy.controllers.notification_live import (
        subscribe,
        unsubscribe,
        HEARTBEAT_INTERVAL,
    )
    import queue
    q = subscribe(user_id)
    try:
        while True:
            try:
                event = q.get(timeout=HEARTBEAT_INTERVAL)
                # SSE format: data: {...}\n\n
                yield f"data: {json.dumps(event)}\n\n"
            except queue.Empty:
                # Heartbeat so client and proxies keep connection alive
                yield ": heartbeat\n\n"
    finally:
        unsubscribe(user_id, q)


@api_view(["GET"])
def notification_stream(request):
    """
    Server-Sent Events (SSE) stream for real-time notification updates.
    When a new notification is created (e.g. from Gmail webhook), backend pushes
    a 'new_notification' event; frontend should then call GET /api/all-notifications.
    Auth: Bearer token in Authorization header, or in query param 'token' (for EventSource).
    """
    user_id, err_response = _get_user_for_notification_stream(request)
    if err_response is not None:
        return err_response
    response = StreamingHttpResponse(
        _notification_stream_generator(user_id),
        content_type="text/event-stream",
    )
    response["Cache-Control"] = "no-cache"
    response["X-Accel-Buffering"] = "no"
    return response


@api_view(["GET"])
def all_notifications(request):
    user = request.user.id
    user_id = user
    print("user",user_id)
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by") or "core_notification_users.id"
    sort_dir = request.GET.get("sort_dir") or "desc"
    allowed_sorting_columns = ["core_notification_users.id"]
    read_status = request.GET.get("read_status", "")

    all_columns = [
        "core_notification_users.id",
        "core_notification_users.notification_id",
        "core_notification_users.user_id",
        "core_notification_users.customer_id",
        "core_notification_users.is_read",
        "core_notification_users.is_clear",
        "core_notification_users.read_at",
        "core_notifications.id as notification_id",
        "core_notifications.type_id",
        "core_notifications.title",
        "core_notifications.message",
        "core_notifications.sent_at",
        "core_notifications.metadata",
        "core_notifications.created_at",
        "core_notifications.updated_at",
        "core_notification_types.code as notification_code",
        "core_notification_types.name as notification_name",
        "core_notification_types.color as type_color",
        "core_notification_types.code as type_name",

    ]

    query = (
        QueryBuilderService("core_notification_users")
        .select(*all_columns)
        .leftJoin(
            "core_notifications",
            "core_notifications.id",
            "core_notification_users.notification_id"
        )
        .leftJoin(
            "core_notification_types",
            "core_notification_types.id",
            "core_notifications.type_id"
        )
        .where("core_notification_users.user_id", user_id)
        .where("core_notification_users.is_clear", 0)
    )

    data = (
        query
        .orderBy(sort_by, sort_dir)
        .get()
    )
    print("data",data)

    notif_data = data.get('data', []) if isinstance(data, dict) else data

    # Get date filter from request
    date_filter = request.GET.get("filter", "")
    
    # Filter in Python for robust read/unread handling based only on core_notification_users.is_read
    if read_status == "read":
        notif_data = [n for n in notif_data if str(n.get('is_read')) in ['1', 1]]
    elif read_status == "unread":
        notif_data = [n for n in notif_data if str(n.get('is_read')) in ['0', 0, '', 'None', None]]

    # Apply date filtering
    if date_filter:
        current_time = datetime.now()
        
        if date_filter == "today":
            # Filter for today (00:00:00 to 23:59:59)
            today_start = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = current_time.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            notif_data = [n for n in notif_data if _is_date_in_range(n.get('created_at'), today_start, today_end)]
            
        elif date_filter == "last_week":
            # Filter for last 7 days
            week_ago = current_time - timedelta(days=7)
            notif_data = [n for n in notif_data if _is_date_in_range(n.get('created_at'), week_ago, current_time)]
            
        elif date_filter == "last_month":
            # Filter for last 30 days
            month_ago = current_time - timedelta(days=30)
            notif_data = [n for n in notif_data if _is_date_in_range(n.get('created_at'), month_ago, current_time)]

 # Ensure notif_data is a list and handle empty data
    if not isinstance(notif_data, list):
        notif_data = []
        
    # Add read_status field based strictly on core_notification_users.is_read
    for notif in notif_data:
        is_read_val = notif.get('is_read')
        # Only treat as read if is_read is exactly 1 (int or string)
        notif['read_status'] = 'read' if str(is_read_val) == '1' or is_read_val == 1 else 'unread'

        # --- Begin: Add link_id as top-level key from metadata.id ---
        metadata = notif.get('metadata')
        notif['link_id'] = None
        if metadata and isinstance(metadata, str):
            try:
                import json as _json
                meta_obj = _json.loads(metadata)
                if isinstance(meta_obj, dict) and 'id' in meta_obj:
                    notif['link_id'] = meta_obj['id']
            except Exception:
                notif['link_id'] = None
        # --- End: Add link_id as top-level key from metadata.id ---

    # Group by date (core_notifications.created_at or core_notification_users.created_at)
    grouped = {}
    for notif in notif_data:
        created_at = notif.get('created_at')
        if created_at:
            if isinstance(created_at, str):
                try:
                    dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    dt = datetime.fromisoformat(created_at)
            else:
                dt = created_at
            notif_date = dt.strftime("%d %b %Y")
        else:
            notif_date = "Unknown"
        if notif_date not in grouped:
            grouped[notif_date] = []
        grouped[notif_date].append(notif)

    # Prepare grouped list
    grouped_list = [
        {"date": date, "notification_data": notifs}
        for date, notifs in grouped.items()
    ]
    # Sort by date descending
    grouped_list.sort(key=lambda x: datetime.strptime(x['date'], "%d %b %Y") if x['date'] != "Unknown" else datetime.min, reverse=True)

    # Pagination on grouped_list
    total_records = len(grouped_list)
    last_page = (total_records + limit - 1) // limit
    start = (page - 1) * limit
    end = start + limit
    paginated_grouped = grouped_list[start:end]

    result = {
        "total_records": total_records,
        "per_page": limit,
        "current_page": page,
        "last_page": last_page,
        "data": paginated_grouped
    }
    return Response({
        "is_success": True,
        "message": "notifications_retrieved",
        "result": result
    })


def _is_date_in_range(created_at, start_date, end_date):
    """
    Helper function to check if a notification's created_at date falls within a given range
    """
    if not created_at:
        return False
    
    try:
        if isinstance(created_at, str):
            # Try different date formats
            try:
                dt = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                dt = datetime.fromisoformat(created_at)
        else:
            dt = created_at
        
        return start_date <= dt <= end_date
    except Exception:
        return False



@api_view(["POST"])
def read_notifications(request, ids):
    try:
        # ids: comma-separated string of core_notification_users.id values
       
        user_id = request.user.id
        
        if not user_id:
            return ResponseService.response("FORBIDDEN", {}, "User not authenticated")
        
        id_list = [int(i) for i in ids.split(',') if i.strip().isdigit()]
        
        if not id_list:
            return ResponseService.response("VALIDATION_ERROR", {}, "No valid IDs provided")
        
        now = datetime.now()
        
        QueryBuilderService("core_notification_users") \
            .where("user_id", user_id) \
            .whereIn("id", id_list) \
            .update({"is_read": 1, "read_at": now})
            
        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
        
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Error marking notifications as read")


@api_view(["GET"])
def get_notification_detail(request, notification_id):
    """
    Get a single notification by notification_id with extracted policy and quotation details from metadata
    """
    try:
        user_id = request.user.id
        
        if not user_id:
            return ResponseService.response("FORBIDDEN", {}, "User not authenticated")
        
        all_columns = [
            "core_notification_users.id",
            "core_notification_users.notification_id",
            "core_notification_users.user_id",
            "core_notification_users.customer_id",
            "core_notification_users.is_read",
            "core_notification_users.is_clear",
            "core_notification_users.read_at",
            "core_notifications.id as notification_id",
            "core_notifications.type_id",
            "core_notifications.title",
            "core_notifications.message",
            "core_notifications.sent_at",
            "core_notifications.metadata",
            "core_notifications.created_at",
            "core_notifications.updated_at",
            "core_notification_types.code as notification_code",
            "core_notification_types.name as notification_name",
            "core_notification_types.color as type_color",
            "core_notification_types.code as type_name",
            # Customer object (from core_customers)
            "core_customers.id as cust_id",
            "core_customers.code as cust_code",
            "core_customers.name as cust_name",
            "core_customers.type as cust_type",
            "core_customers.logo as cust_logo",
            "core_customers.remarks as cust_remarks",
            # User object (from core_users)
            "core_users.id as usr_id",
            "core_users.display_name as usr_display_name",
            "core_users.email as usr_email",
            "core_users.first_name as usr_first_name",
            "core_users.last_name as usr_last_name",
            "core_users.contact_no as usr_contact_no",
            "core_users.picture as usr_picture",
            "core_users.code as usr_code",
        ]
        
        # Get notification by notification_id (from core_notifications table)
        notification = (
            QueryBuilderService("core_notification_users")
            .select(*all_columns)
            .leftJoin(
                "core_notifications",
                "core_notifications.id",
                "core_notification_users.notification_id"
            )
            .leftJoin(
                "core_notification_types",
                "core_notification_types.id",
                "core_notifications.type_id"
            )
            .leftJoin(
                "core_customers",
                "core_customers.id",
                "core_notifications.customer_id"
            )
            .leftJoin(
                "core_users",
                "core_users.id",
                "core_notification_users.user_id"
            )
            .where("core_notifications.id", notification_id)
            # .where("core_notification_users.user_id", user_id)
            .first()
        )
        
        if not notification:
            return ResponseService.response(
                "NOT_FOUND", 
                None, 
                f"Notification with ID {notification_id} not found"
            )
        
        # Add read_status field
        is_read_val = notification.get('is_read')
        notification['read_status'] = 'read' if str(is_read_val) == '1' or is_read_val == 1 else 'unread'
        
        # Build customer object from joined core_customers
        cust_id = notification.pop('cust_id', None)
        if cust_id is not None:
            notification['customer'] = {
                "id": cust_id,
                "code": notification.pop('cust_code', None),
                "name": notification.pop('cust_name', None),
                "type": notification.pop('cust_type', None),
                "logo": notification.pop('cust_logo', None),
                "remarks": notification.pop('cust_remarks', None),
            }
        else:
            notification['customer'] = None
            for k in ['cust_code', 'cust_name', 'cust_type', 'cust_logo', 'cust_remarks']:
                notification.pop(k, None)
        
        # Build user object from joined core_users
        usr_id = notification.pop('usr_id', None)
        if usr_id is not None:
            notification['user'] = {
                "id": usr_id,
                "display_name": notification.pop('usr_display_name', None),
                "email": notification.pop('usr_email', None),
                "first_name": notification.pop('usr_first_name', None),
                "last_name": notification.pop('usr_last_name', None),
                "contact_no": notification.pop('usr_contact_no', None),
                "picture": notification.pop('usr_picture', None),
                "code": notification.pop('usr_code', None),
            }
        else:
            notification['user'] = None
            for k in ['usr_display_name', 'usr_email', 'usr_first_name', 'usr_last_name', 'usr_contact_no', 'usr_picture', 'usr_code']:
                notification.pop(k, None)
        
        # Extract link_id from metadata
        metadata = notification.get('metadata')
        notification['link_id'] = None
        
        # Initialize extracted fields
        policy_id = None
        policy_code = None
        quotation_id = None
        quotation_code = None
        
        # Parse metadata if it exists
        if metadata:
            try:
                if isinstance(metadata, str):
                    meta_obj = json.loads(metadata)
                else:
                    meta_obj = metadata
                
                if isinstance(meta_obj, dict):
                    # Extract link_id from metadata.id
                    if 'id' in meta_obj:
                        notification['link_id'] = meta_obj['id']
                    
                    # Extract policy_id and policy_code
                    if 'policy_id' in meta_obj:
                        policy_id = meta_obj['policy_id']
                    elif 'policies' in meta_obj and isinstance(meta_obj['policies'], list) and len(meta_obj['policies']) > 0:
                        # If policies is an array, get the first policy's id
                        first_policy = meta_obj['policies'][0]
                        if isinstance(first_policy, dict) and 'id' in first_policy:
                            policy_id = first_policy['id']
                        elif isinstance(first_policy, (int, str)):
                            policy_id = first_policy
                    
                    # Extract quotation_id and quotation_code
                    if 'quotation_id' in meta_obj:
                        quotation_id = meta_obj['quotation_id']
                    elif 'quotation_request_id' in meta_obj:
                        quotation_id = meta_obj['quotation_request_id']
                    
                    # Fetch policy_code from database if policy_id exists
                    if policy_id:
                        try:
                            policy_record = (
                                QueryBuilderService("crmp_request_policies")
                                .select("id", "code")
                                .where("id", policy_id)
                                .first()
                            )
                            if policy_record:
                                policy_code = policy_record.get('code')
                        except Exception as e:
                            print(f"Error fetching policy code: {e}")
                    
                    # Fetch quotation_code from database if quotation_id exists
                    if quotation_id:
                        try:
                            quotation_record = (
                                QueryBuilderService("crmq_quotations")
                                .select("id", "code")
                                .where("id", quotation_id)
                                .first()
                            )
                            if quotation_record:
                                quotation_code = quotation_record.get('code')
                        except Exception as e:
                            print(f"Error fetching quotation code: {e}")
                
            except Exception as e:
                print(f"Error parsing metadata: {e}")
        
        # Add extracted fields to notification response
        notification['policy_id'] = policy_id
        notification['policy_code'] = policy_code
        notification['quotation_id'] = quotation_id
        notification['quotation_code'] = quotation_code
        
        return Response({
            "is_success": True,
            "message": "notification_retrieved",
            "result": notification
        })
        
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            {"error": str(e)}, 
            "Error retrieving notification details"
        )  