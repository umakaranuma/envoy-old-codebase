from datetime import datetime
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from envoy_bu_crm_api.quotation.models.crmq_quotation_form_submissions import QuotationFormSubmission
from envoy_bu_crm_api.quotation.models.crmq_quotation_service_providers import QuotationServiceProvider
from envoy_bu_crm_api.sales.models.core_models import CoreFormSubmissionValue, Task
from envoy_bu_crm_api.sales.models.opprtunity_task import OpportunityTask
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from django.db.models import Max
from envoy_bu_crm_api.policy.models.crmp_issued_policies import IssuedPolicy
from .invoice_utils import generate_invoice_for_issued_policy
from envoy_bu_crm_api.service import handle_entity, _format_date_fields
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view


@csrf_exempt
@api_view(["GET"])
def get_opportunities_with_policy_details(request):

     # Define the standard structure for policy_request
    standard_policy_fields = {
        "id": None,
        "code": None,
        "requested_data": None,
        "status": None,
        "notes": None,
        "request_type": None,
        "opportunity_id": None,
        "entity_id": None,
        "insurer_id": None,
        "insurer_name": None,
        "risks": [],
        "sum_insured": None,
        "total_amount": None,
        "received_date": None,
        "expiry_date": None,
        "policy_start_date": None,
        "policy_expiry_date": None,
        "coverage_type_id": None,
        "coverage_type_name": None,
        "payment_mode_id": None,
        "payment_mode_name": None,
        "product_id": None,
        "product_name": None,
        "request_by_id": None,
        "request_by_name": None,
        "coverage_details": None,
        "coverage_details_name": None,
        "request_type_id": None,
        "request_type_name": None,
        "sp_status": None,
        "approval_status": None,
        "service_provider_status": None,
        "is_policy":False
    }

    all_columns = [
        "oppo.*",
        "core_users.display_name AS salse_agent_name", "core_users.picture AS sales_agent_picture",
        "stage.name AS stage_name", "stage.type AS stage_type", "stage.color AS stage_color",
        "curr.name AS currency_name", "curr.symbol AS currency_symbol",
        "ch.name AS channel_name", "health.health AS current_health"
    ]

    fields = request.GET.get('fields', None)
    if fields == 'additional':
        all_columns.extend([
            "oppo.contact_id",
            "contact.name AS contact_name",
            "contact.email AS contact_email",
            "contact.primary_contact AS primary_contact",
            "customer.name AS customer_name",
            "customer.logo AS customer_logo",
            "customer_contact.email AS customer_primary_contact_email",
            "customer_contact.address AS customer_primary_contact_address",
            "customer_contact.primary_contact AS customer_primary_contact_number",
        ])

    filter_json = request.GET.get('filters', '{}')
    search_string = request.GET.get('search', '')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    sort_by = request.GET.get('sort_by', 'oppo.id')
    sort_dir = request.GET.get('sort_dir', 'desc')
    filter_stage_id = request.GET.get('stage_id', None)
    filter_sales_agent_id = request.GET.get('sales_agent_id', None)
    ids = request.GET.get('ids', None)
    allowed_filters = ['oppo.title', 'oppo.type', 'oppo.stage_id', 'oppo.sales_agent_id', 'oppo.contact_id', 'oppo.customer_id']
    search_columns = ["oppo.title", "oppo.type", "oppo.code", "contact.name", "contact.primary_contact", "stage.name", "curr.name"]
    allowed_sorting_columns = ["oppo.title", "oppo.id"]

    data = (
        QueryBuilderService("crm_opportunities as oppo")
        .leftJoin("core_users", "core_users.id", "oppo.sales_agent_id")
        .leftJoin("crm_opportunity_health as health", "health.id", "oppo.current_health_id")
        .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")
        .leftJoin("core_currencies as curr", "curr.id", "oppo.currency_id")
        .leftJoin("core_channels as ch", "ch.id", "oppo.channel_id")
        .leftJoin("core_contacts as contact", "contact.id", "oppo.contact_id")
    )

    if fields == 'additional':
        data = data.leftJoin("core_customers as customer", "customer.id", "oppo.customer_id")
        data = data.leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")

    data = data.select(*all_columns).apply_conditions(filter_json, allowed_filters, search_string, search_columns)

    if filter_stage_id:
        data = data.where("oppo.stage_id", filter_stage_id)
    if filter_sales_agent_id:
        data = data.where("oppo.sales_agent_id", filter_sales_agent_id)

    if ids:
        id_list = ids.split(',')
        data = data.whereIn("oppo.id", id_list).get()
    else:
        data = data.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

    if fields == 'additional':
        if isinstance(data, dict) and 'data' in data:
            items = data['data']
            for item in items:
                if isinstance(item, dict):
                    # contact
                    contact_id = item.get('contact_id')
                    contact_name = item.pop('contact_name', None)
                    primary_contact = item.pop('primary_contact', None)
                    item['contact'] = {
                        'name': contact_name,
                        'primary_contact': primary_contact
                    } if contact_id else None

                    # customer
                    customer_id = item.get('customer_id')
                    customer_name = item.pop('customer_name', None)
                    customer_logo = item.pop('customer_logo', None)
                    customer_email = item.pop('customer_primary_contact_email', None)
                    customer_address = item.pop('customer_primary_contact_address', None)
                    customer_contact_number = item.pop('customer_primary_contact_number', None)
                    item['customer'] = {
                        'name': customer_name,
                        'logo': customer_logo,
                        'email': customer_email,
                        'address': customer_address,
                        'primary_contact': customer_contact_number
                    } if customer_id else None

                    # next_task
                    opportunity_id = item.get('id')
                    task_ids = OpportunityTask.objects.filter(opportunity_id=opportunity_id).values_list('task_id', flat=True)
                    tasks = (
                        Task.objects
                        .filter(id__in=task_ids)
                        .select_related('task_status')
                        .order_by('sort_index')
                    )
                    selected_task = None
                    for task in tasks:
                        if task.task_status and task.task_status.type and task.task_status.type.lower() == "task_todo":
                            selected_task = task
                            break
                    item['next_task'] = {
                        'task': selected_task.task,
                        'start_date': selected_task.start_date,
                        'assigned_user_name': selected_task.assigned_to.display_name if selected_task.assigned_to else None,
                        'assigned_user_picture': selected_task.assigned_to.picture if selected_task.assigned_to else None
                    } if selected_task else None

                    opportunity_id = item.get('id')

                    # Attempt to fetch policy_base_data
                    policy_base_data = QueryBuilderService("crmp_policy_base as policy")\
                        .leftJoin("crmp_coverage_types as coverage", "coverage.id", "policy.coverage_type_id")\
                        .leftJoin("crmp_payment_plans as payment", "payment.id", "policy.payment_mode_id")\
                        .leftJoin("core_products as product", "product.id", "policy.product_id")\
                        .leftJoin("core_service_providers as insurer", "insurer.id", "policy.insurer_id")\
                        .leftJoin("core_users as requester", "requester.id", "policy.request_by_id")\
                        .leftJoin("crmp_request_types as request_type", "request_type.id", "policy.request_type_id")\
                        .select(
                            "policy.id AS policy_base_id", "policy.premium_amount AS total_amount", "policy.sum_insured",
                            "policy.quotation_issued_date AS received_date", "policy.quotation_expiry_date AS expiry_date",
                            "policy.policy_start_date", "policy.policy_expiry_date", "policy.quotation_notes as notes",
                            "policy.coverage_type_id", "coverage.name AS coverage_type_name",
                            "policy.payment_mode_id", "payment.name AS payment_mode_name",
                            "policy.product_id", "product.name AS product_name",
                            "policy.insurer_id", "insurer.name AS insurer_name", "insurer.description AS insurer_notes",
                            "policy.request_by_id", "requester.display_name AS request_by_name",
                            "policy.quotation_document AS coverage_details", "policy.quotation_document_name AS coverage_details_name",
                            "policy.request_type_id", "request_type.name AS request_type_name","TRUE AS is_policy"
                        )\
                        .where("policy.lead_id", opportunity_id)\
                        .orderBy("policy.id", "asc")\
                        .first()

                    if policy_base_data:
                        risks = QueryBuilderService("crmp_policy_base_risk_types as policy_risk")\
                            .leftJoin("crm_opportunity_types as risk", "risk.id", "policy_risk.risk_type_id")\
                            .select("policy_risk.risk_type_id", "risk.title AS risk_type_name")\
                            .where("policy_risk.policy_base_id", policy_base_data["policy_base_id"])\
                            .get()
                        policy_base_data["risks"] = risks
                        del policy_base_data["policy_base_id"]
                        # Merge with standard fields to ensure consistency
                        policy_request = {**standard_policy_fields, **policy_base_data}
                        policy_request["is_policy"] = True
                        item["policy_request"] = policy_request
                    else:
                        # Fallback to quotation logic
                        quotation_data = QueryBuilderService("crmq_quotations as q")\
                            .leftJoin("crmq_quotation_attributes as qa", "qa.quotation_id", "q.id")\
                            .leftJoin("crmq_quotation_form_submissions as qfs", "qfs.form_submission_id", "qa.form_submission_id")\
                            .leftJoin("crmq_quotation_vendor_quotations as qvq", "qvq.vendor_quotation_id", "qfs.vendor_quotation_id")\
                            .leftJoin("crmq_quotation_service_providers as qsp", "qsp.quotation_id", "q.id")\
                            .leftJoin("crmq_quotation_risk_properties as rp", "rp.quotation_id", "q.id")\
                            .leftJoin("crmq_properties as prop", "prop.id", "rp.property_id")\
                            .leftJoin("core_entity_approvals as approval", "approval.entity_id", "q.entity_id")\
                            .leftJoin("core_service_providers as sp", "sp.id", "qsp.service_provider_id")\
                            .select(
                                "q.id AS quotation_id", "q.code", "q.requested_data", "q.status", "q.notes",
                                "q.request_type", "q.opportunity_id", "q.entity_id", "q.opportunity_type_id",
                                "qa.attribute_id", "qfs.form_submission_id", "qfs.by_user_id",
                                "qvq.send_quotation_id", "qvq.vendor_quotation_id",
                                "qsp.service_provider_id", "qsp.is_received", "qsp.is_shortlisted", "qsp.is_draft", "qsp.is_sent",
                                "qsp.version", "qsp.status AS sp_status",
                                "rp.risk_type_id", "rp.property_id",
                                "prop.name AS property_name", "prop.description AS property_description",
                                "approval.user AS approved_user", "approval.role", "approval.status AS approval_status",
                                "approval.level", "approval.remarks", "approval.date",
                                "sp.name as service_provider_name", "sp.description as service_provider_description",
                                "sp.logo as service_provider_logo", "sp.email as service_provider_email", "sp.status as service_provider_status","FALSE AS is_policy"
                            )\
                            .where("q.opportunity_id", opportunity_id)\
                            .orderBy("q.id", "desc")\
                            .get()

                        if quotation_data:
                            from collections import defaultdict
                            import json

                            quotation_map = defaultdict(lambda: {
                                "id": None, "code": None, "requested_data": None, "status": None, "notes": None,
                                "request_type": None, "opportunity_id": None, "entity_id": None,
                                "insurer_id": None, "insurer_name": None, "risks": []
                            })
                            all_opp_type_ids = set()
                            quotation_opp_type_lookup = {}

                            for row in quotation_data:
                                qid = row["quotation_id"]
                                qobj = quotation_map[qid]
                                qobj.update({
                                    "id": qid, "code": row["code"], "requested_data": row["requested_data"], "status": row["status"],
                                    "notes": row["notes"], "request_type": row["request_type"], "opportunity_id": row["opportunity_id"],
                                    "entity_id": row["entity_id"]
                                })
                                if row["service_provider_id"] and qobj["insurer_id"] is None:
                                    qobj["insurer_id"] = row["service_provider_id"]
                                    qobj["insurer_name"] = row["service_provider_name"]

                                opp_type_ids = row.get("opportunity_type_id", [])
                                if isinstance(opp_type_ids, str):
                                    try:
                                        opp_type_ids = json.loads(opp_type_ids)
                                    except Exception:
                                        opp_type_ids = []
                                if isinstance(opp_type_ids, list):
                                    all_opp_type_ids.update(opp_type_ids)
                                    quotation_opp_type_lookup[qid] = opp_type_ids

                            if all_opp_type_ids:
                                opp_type_details = QueryBuilderService("crm_opportunity_types")\
                                    .select("id", "title")\
                                    .whereIn("id", list(all_opp_type_ids))\
                                    .get()
                                opp_type_map = {o["id"]: o["title"] for o in opp_type_details}
                                for qid, qobj in quotation_map.items():
                                    opp_ids = quotation_opp_type_lookup.get(qid, [])
                                    qobj["risks"] = [{"risk_type_id": oid, "risk_type_name": opp_type_map.get(oid)} for oid in opp_ids if oid in opp_type_map]

                            policy_request = list(quotation_map.values())[0]
                            quotation_id = policy_request.get("id")

                            latest_sp = QuotationServiceProvider.objects.filter(quotation_id=quotation_id).order_by('-id').first()
                            if latest_sp:
                                vendor_quotation_id = latest_sp.id
                                form_submission = QuotationFormSubmission.objects.filter(vendor_quotation_id=vendor_quotation_id).order_by('-id').first()
                                if form_submission:
                                    form_submission_id = form_submission.form_submission_id
                                    form_values = CoreFormSubmissionValue.objects.filter(form_submission_id=form_submission_id).select_related("attribute")
                                    for fv in form_values:
                                        if fv.attribute and fv.attribute.title:
                                            key = fv.attribute.title.strip().lower().replace(" ", "_")
                                            policy_request[key] = fv.value

                            # Merge with standard fields to ensure consistency
                            policy_request = {**standard_policy_fields, **policy_request}
                            policy_request["is_policy"] = False
                            item["policy_request"] = policy_request




    return ResponseService.response('SUCCESS', data, Message.DATA_FETCHED)


@csrf_exempt
@api_view(["GET", "POST"])
def issued_policy_handler(request):
    if request.method == "GET":
        action = ActionService.getAction("IssuedPolicy", "VIEW")
        if not AuthService.hasAuthority(request, action):
            return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
        return get_all_issued_policies(request)

    elif request.method == "POST":
        action = ActionService.getAction("IssuedPolicy", "CREATE")
        if not AuthService.hasAuthority(request, action):
            return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
        return create_issued_policy(request, _from_request=False)


@csrf_exempt
@api_view(["POST"])
def issued_policy_create_from_request(request, request_id):
    action = ActionService.getAction("IssuedPolicy", "CREATE")
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    return create_issued_policy(request, _from_request=True, request_id=request_id)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def issued_policy_detail(request, policy_id):
    """GET: Retrieve | PUT: Update | DELETE: Delete issued policy by ID"""

    action_map = {"GET": "VIEW", "PUT": "UPDATE", "DELETE": "DELETE"}
    action = ActionService.getAction("IssuedPolicy", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    if request.method == "GET":
        return get_all_issued_policies(request, policy_id)
    elif request.method == "PUT":
        return update_issued_policy(request, policy_id)
    elif request.method == "DELETE":
        return delete_issued_policy(policy_id)


@csrf_exempt
@api_view(["PUT"])
def issued_policy_renewal(request, policy_id):
    """GET: Retrieve | PUT: Update | DELETE: Delete issued policy by ID"""

    action_map = {"PUT": "UPDATE"}
    action = ActionService.getAction("IssuedPolicy", action_map[request.method])

    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

    return update_issued_policy(request, policy_id, renewal=True)


def get_all_issued_policies(request, policy_id=None):
    columns = [
        "crmp_issued_policies.*",
        "crmp_issued_policies.remarks AS insurer_notes",
        "products.id AS product_id",
        "risk_type.title AS risk_type_name",
        "risk_type.id AS risk_type_id",
        "insurer_sp.name AS insurer_info_full_name",
        "insurer_sp.id AS insurer_id",
        "insurer_sp.logo AS insurer_info_logo",
        "customers.name as customer_name",
        "customers.logo as customer_logo",
        "customers.id as customer_id",
        "products.name as product",
        "request_policy.policy_request_id as policy_request_code",
        "request_policy.id as policy_request_id",
        "request_status.name AS policy_request_status",
        "request_status.color AS policy_request_status_color",
        "policy_base.quotation_document as quotation_document",
        "policy_base.quotation_document_name as quotation_document_name",
        # Additional Request Policy Info
        "request_by.display_name AS requested_by",
        "request_by.picture AS requested_by_logo",
        "request_type.name AS request_type",
        "request_type.id AS request_type_id",
        "request_customer_contact.email AS customer_email",
        "request_customer_contact.address AS customer_address",
        "request_customer_contact.primary_contact AS customer_primary_contact",
        "coverage_type.name AS coverage_type",
        "coverage_type.id AS coverage_type_id",
        "payment_plan.name AS payment_plan",
        "payment_plan.id AS payment_plan_id",
        "created_by.display_name AS created_by",
        "created_by.picture AS created_by_logo",
        "updated_by.display_name AS updated_by",
        "updated_by.picture AS updated_by_logo",
        "entity.created_at AS created_at",
        "entity.updated_at AS updated_at",
        "invoices.invoice_number AS invoice_number ",
    ]

    query = (
        QueryBuilderService("crmp_issued_policies")
        .select(*columns)
        .leftJoin(
            "crmp_policy_base as policy_base",
            "policy_base.id",
            "crmp_issued_policies.policy_base_id",
        )
        .leftJoin(
            "crm_opportunity_types as risk_type",
            "risk_type.id",
            "policy_base.risk_type_id",
        )
        .leftJoin(
            "core_service_providers as insurer_sp",
            "insurer_sp.id",
            "policy_base.insurer_id",
        )
        .leftJoin(
            "core_customers as customers", "customers.id", "policy_base.customer_id"
        )
        .leftJoin("core_products as products", "products.id", "policy_base.product_id")
        # Added request policy related joins
        .leftJoin(
            "core_users as request_by", "request_by.id", "policy_base.request_by_id"
        )
        .leftJoin(
            "crmp_request_policies as request_policy",
            "request_policy.id",
            "crmp_issued_policies.policy_request_id",
        )
        .leftJoin(
            "core_status as request_status",
            "request_status.id",
            "request_policy.status_id",
        )
        .leftJoin(
            "crmp_request_types as request_type",
            "request_type.id",
            "policy_base.request_type_id",
        )
        .leftJoin(
            "core_contacts as request_customer_contact",
            "request_customer_contact.id",
            "customers.primary_contact_id",
        )
        .leftJoin(
            "crmp_coverage_types as coverage_type",
            "coverage_type.id",
            "policy_base.coverage_type_id",
        )
        .leftJoin(
            "crmp_payment_plans as payment_plan",
            "payment_plan.id",
            "policy_base.payment_mode_id",
        )
        .leftJoin(
            "core_entities as entity", "entity.id", "crmp_issued_policies.entity_id"
        )
        .leftJoin("core_users as created_by", "created_by.id", "entity.created_by_id")
        .leftJoin("core_users as updated_by", "updated_by.id", "entity.updated_by_id")
        .leftJoin(
            "crmp_invoices as invoices",
            "invoices.issued_policy_id",
            "crmp_issued_policies.id",
        )
    )

    if policy_id:
        data = query.where("crmp_issued_policies.id", policy_id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        _format_date_fields(data)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    # List with filters, pagination
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crmp_issued_policies.start_date")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = [
        "products.name",
        "crmp_issued_policies.risk_level",
        "coverage_type.name",
        "sales_agent.display_name",
        "account_manager.display_name",
        "insurer_info_full_name",
    ]
    search_columns = [
        "crmp_issued_policies.brokerage_policy_id",
        "products.name",
        "coverage_type.name",
        "crmp_issued_policies.start_date",
        "crmp_issued_policies.end_date",
        "customers.name",
        "insurer_sp.name",
        "request_by.display_name",
        "request_customer_contact.primary_contact",
        "request_customer_contact.email",
        "request_customer_contact.address",
        "policy_base.quotation_document_name",
        "policy_base.quotation_notes",
        "invoices.invoice_number",
    ]
    sort_columns = [
        "crmp_issued_policies.start_date",
        "products.name",
        "crmp_issued_policies.brokerage_policy_id",
        "coverage_type.name",
        "sales_agent.display_name",
        "account_manager.display_name",
    ]

    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)
    rows = data.get("data", [])
    for item in rows:
        _format_date_fields(item)
    data["data"] = rows

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def update_issued_policy(request, policy_id, renewal=False):
    data = json.loads(request.body or "{}")
    data["remarks"] = data.get("insurer_notes")
    errors = ValidatorService.validate(data, get_issued_policy_rules_with_request_put())
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    updated = (
        QueryBuilderService("crmp_issued_policies").where("id", policy_id).update(data)
    )
    policy_data = (
        QueryBuilderService("crmp_issued_policies").where("id", policy_id).first()
    )
    if policy_data.get("entity_id") is not None:
        user = request.user if request.user.is_authenticated else None
        entity_id = policy_data.get("entity_id")
        entity_data = {
            "approvel_status": False,
        }
        handle_entity(entity_data, entity_id=entity_id, user=user)

    # Replace this call to avoid MultipleObjectsReturned
    from envoy_bu_crm_api.policy.models import RequestPolicyInvoice

    defaults = {
        "modified_by": user,
        "modified_at": datetime.now()
    }

    existing_invoice = (
        RequestPolicyInvoice.objects
        .filter(issued_policy_id=policy_id)
        .order_by('-id')
        .first()
    )

    if existing_invoice:
        for key, value in defaults.items():
            setattr(existing_invoice, key, value)
        existing_invoice.save()
    else:
        RequestPolicyInvoice.objects.create(
            issued_policy_id=policy_id,
            created_by=user,
            **defaults
        )

    if updated:
        if renewal:
            entity_data = {
                "type": "policy_inheritance",
                "approvel_status": False,
            }
            new_entity_id = handle_entity(entity_data, entity_id=None, user=user)
            inheritance_fields = ["start_date", "policy_effective_date"]
            inheritance_data = {f: data[f] for f in inheritance_fields if f in data}
            inheritance_data.update(
                {
                    "issued_policy_id": policy_id,
                    "entity_id": new_entity_id,
                }
            )
            QueryBuilderService("crmp_issued_policies_inheritance").insert(
                inheritance_data
            )

        return ResponseService.response(
            "SUCCESS", updated, "default_update_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_issued_policy(policy_id):
    deleted = (
        QueryBuilderService("crmp_issued_policies").where("id", policy_id).delete()
    )
    if deleted:
        return ResponseService.response(
            "SUCCESS", deleted, "default_delete_success_msg"
        )
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def get_policy_rules():
    return {
        "insurer_invoice_id": "required",
        "policy_issue_date": "required|date",
        "start_date": "required|date",
        "end_date": "required|date",
        "premium_amount": "required|numeric",
        "credit_period_days": "required|integer",
        "credit_age_days": "required|integer",
        "product_id": "required|integer|exists:core_products,id",
        "coverage_type_id": "required|integer|exists:crmp_coverage_types,id",
        "risk_type_id": "required|integer|exists:crm_opportunity_types,id",
        "risk_level": "required|integer",
        "insured_info_salutation": "required",
        "insured_id": "required|integer|exists:core_service_providers,id",
        "insured_info_primary_contact_number": "required|numeric",
        "insured_info_email": "required|email",
        "insurer_info_primary_contact_number": "required|numeric",
        "insurer_info_email": "required|email",
        "sales_agent_id": "required|integer|exists:core_users,id",
        "account_manager_id": "required|integer|exists:core_users,id",
        "policy_document": "nullable",
        "quotation_document": "nullable",
        "remarks_notes": "string",
    }


def generate_policy_request_id():
    last = IssuedPolicy.objects.aggregate(Max("id"))["id__max"] or 0
    return f"PN-{last + 1}"


def create_issued_policy(request, _from_request=False, request_id=None):
    try:
        data = json.loads(request.body or "{}")
    except Exception:
        return ResponseService.response("VALIDATION_ERROR", None, "Invalid JSON format.")

    if not isinstance(data, dict):
        return ResponseService.response("VALIDATION_ERROR", None, "Invalid data format: Expected JSON object.")

    # Convert empty strings to None
    for key, value in data.items():
        if isinstance(value, str) and value.strip() == "":
            data[key] = None

    # Convert list of risk_type_ids to single risk_type_id
    if "risk_type_ids" in data and isinstance(data["risk_type_ids"], list) and data["risk_type_ids"]:
        data["risk_type_id"] = data["risk_type_ids"][0]

    # Provide default for request_type_id if missing
    if "request_type_id" not in data or data["request_type_id"] is None:
        data["request_type_id"] = 1

    # Determine validation rules
    rules = get_issued_policy_rules_with_request() if _from_request else get_issued_policy_rules_without_request()

    # If from request, get related policy base info
    policy_base_id = None
    if _from_request:
        req = QueryBuilderService("crmp_request_policies").select(
            "crmp_request_policies.*",
            "crmp_policy_base.premium_amount"
        ).leftJoin(
            "crmp_policy_base",
            "crmp_request_policies.policy_base_id",
            "crmp_policy_base.id"
        ).where("crmp_request_policies.id", request_id).first()

        if not req:
            return ResponseService.response("NOT_FOUND", None, "Request not found.")

        policy_base_id = req.get("policy_base_id")
        data["policy_request_id"] = request_id
        if "premium_amount" not in data:
            data["premium_amount"] = req.get("premium_amount", 0)

    # Validate input
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    user = request.user if request.user.is_authenticated else None

    # Handle entity
    entity_data = {
        "type": "policy",
        "approvel_status": False,
    }
    entity_id = handle_entity(entity_data, entity_id=data.get("entity_id"), user=user)
    data["entity_id"] = entity_id

    # Create policy base if not from request
    if not _from_request:
        base_fields = [
            "risk_details_form_id", "risk_type_id", "insurer_id", "customer_id", "lead_id",
            "request_by_id", "premium_amount", "quotation_document_size", "quotation_document",
            "quotation_document_name", "request_type_id", "product_id", "payment_mode_id",
            "coverage_type_id", "sum_insured", "quotation_issued_date", "quotation_expiry_date",
            "policy_start_date", "policy_expiry_date", "quotation_notes", "entity_id"
        ]
        policy_base_data = {f: data[f] for f in base_fields if f in data}
        pb = QueryBuilderService("crmp_policy_base").insert(policy_base_data)
        policy_base_id = pb["id"]

        update_customer_contact_info(data)

    # Finalize issued policy creation
    data["policy_base_id"] = policy_base_id
    data["brokerage_policy_id"] = generate_policy_request_id()
    data["remarks"] = data.get("insurer_notes")

    issue_fields = [
        "start_date", "end_date", "premium_amount", "credit_period_days", "credit_age_days",
        "insurer_invoice_id", "sum_insured", "policy_effective_date", "policy_document",
        "policy_document_size", "policy_document_name", "policy_base_id", "brokerage_policy_id",
        "policy_request_id", "entity_id", "remarks"
    ]
    issue_data = {f: data[f] for f in issue_fields if f in data}
    created = QueryBuilderService("crmp_issued_policies").insert(issue_data)

    generate_invoice_for_issued_policy(created["id"], user=user)

    return ResponseService.response("SUCCESS", created, "default_create_success_msg")


def get_issued_policy_rules_with_request():
    return {
        "start_date": "required|date",
        "end_date": "required|date",
        "premium_amount": "nullable|numeric",
        "credit_period_days": "required|integer",
        "credit_age_days": "required|integer",
        "insurer_invoice_id": "required|string",
        "sum_insured": "nullable|numeric",
        "policy_effective_date": "nullable|date",
        "policy_document": "nullable",
        "policy_document_size": "nullable|integer",
        "policy_document_name": "nullable|string",
        # "policy_request_id": "unique:crmp_issued_policies,policy_base_id",
    }
    
def get_issued_policy_rules_with_request_put():
    return {
        "start_date": "required|date",
        "end_date": "required|date",
        "premium_amount": "nullable|numeric",
        "credit_period_days": "required|integer",
        "credit_age_days": "required|integer",
        "insurer_invoice_id": "required|string",
        "sum_insured": "nullable|numeric",
        "policy_effective_date": "nullable|date",
        "policy_document": "nullable",
        "policy_document_size": "nullable|integer",
        "policy_document_name": "nullable|string",
        # "policy_request_id": "unique:crmp_issued_policies,policy_base_id",
    }


def get_issued_policy_rules_without_request():
    return {
        "lead_id": "integer|exists:crm_opportunities,id",
        "quotation_document_name": "string",
        "quotation_document": "nullable",
        "insurer_id": "integer|required|exists:core_service_providers,id",
        "insurer_notes": "string",
        "quotation_expiry_date": "date",
        "quotation_issued_date": "date",
        "request_by_id": "integer|exists:core_users,id",
        "premium_amount": "decimal",
        "customer_id": "integer|required|exists:core_customers,id",
        "customer_primary_contact": "string|required",
        "customer_email": "string|required|email",
        "customer_address": "string|required",
        "policy_start_date": "date|required",
        "policy_expiry_date": "date|required",
        "payment_mode_id": "integer|required|exists:crmp_payment_plans,id",
        "sum_insured": "decimal|required",
        "request_type_id": "integer|required|exists:crmp_request_types,id",
        "risk_type_id": "integer|required|exists:crm_opportunity_types,id",
        "product_id": "integer|required|exists:core_products,id",
        "coverage_type_id": "integer|required|exists:crmp_coverage_types,id",
        "quotation_notes": "string",
        "start_date": "required|date",
        "end_date": "required|date",
        "credit_period_days": "required|integer",
        "credit_age_days": "required|integer",
        "insurer_invoice_id": "required|string",
        "policy_effective_date": "nullable|date",
        "policy_document": "nullable",
        "policy_document_size": "nullable|integer",
        "policy_document_name": "nullable|string",
        "insurer_policy_id": "required",
    }


def update_customer_contact_info(data):
    customer = (
        QueryBuilderService("core_customers")
        .select("primary_contact_id")
        .where("id", data["customer_id"])
        .first()
    )
    customer_update = None
    if customer:
        customer_update = (
            QueryBuilderService("core_contacts")
            .where("id", customer["primary_contact_id"])
            .update(
                {
                    "primary_contact": data["customer_primary_contact"],
                    "email": data["customer_email"],
                    "address": data["customer_address"],
                }
            )
        )
    return {"customer_update": customer_update}


@csrf_exempt
@api_view(["GET"])
def get_all_inheritance_history(
    request, inheritance_id=None, policy_id=None, _created=False
):

    columns = [
        "inh.*",
        "users.display_name     AS created_by",
        "users.picture          AS created_by_logo",
        "entities.created_at    AS created_at",
        "ip.brokerage_policy_id AS policy_id",
        "ip.remarks AS remarks",
        "ip.insurer_policy_id AS insurer_policy_id",
    ]

    query = (
        QueryBuilderService("crmp_issued_policies_inheritance AS inh")
        .select(*columns)
        .leftJoin(
            "crmp_issued_policies AS ip",
            "ip.id",
            "inh.issued_policy_id",
        )
        .leftJoin(
            "crmp_policy_base AS cb",
            "cb.id",
            "ip.policy_base_id",
        )
        .leftJoin(
            "core_service_providers AS ins",
            "ins.id",
            "cb.insurer_id",
        )
        .leftJoin(
            "core_customers AS cust",
            "cust.id",
            "cb.customer_id",
        )
        .leftJoin(
            "core_contacts AS cust_contact",
            "cust_contact.id",
            "cust.primary_contact_id",
        )
        .leftJoin(
            "core_entities AS entities",
            "entities.id",
            "inh.entity_id",
        )
        .leftJoin(
            "core_entity_notes AS notes",
            "notes.entity_id",
            "inh.entity_id",
        )
        .leftJoin(
            "core_users AS users",
            "users.id",
            "entities.created_by_id",
        )
    )

    # Single‐record fetch
    if inheritance_id:
        record = query.where("inh.id", inheritance_id).first()
        if not record:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        if _created:
            return record
        return ResponseService.response("SUCCESS", record, Message.DATA_FETCHED)

    # List + pagination
    filters = json.loads(request.GET.get("filter", "{}"))
    search = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "inh.start_date")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = []
    search_columns = []
    sort_columns = ["inh.start_date", "inh.policy_effective_date"]

    if policy_id:
        query = query.where("inh.issued_policy_id", policy_id)

    data = query.apply_conditions(
        filters, allowed_filters, search, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
