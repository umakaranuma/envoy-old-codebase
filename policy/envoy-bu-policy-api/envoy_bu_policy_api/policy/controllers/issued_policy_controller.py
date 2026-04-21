from datetime import datetime, timedelta, date
import time
import os
from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
from mServices import ResponseService, QueryBuilderService, ValidatorService
from core_models.core_models import CoreFormSubmission, FormSubmissionValue, Task, ProductDocumentType
from core_models.crm_models import (
    OpportunityTask,
    QuotationFormSubmission,
    QuotationServiceProvider,
    Risk,
    RiskSubmission,
)
from envoy_bu_policy_api.policy.models.crmp_risk_config import PolicyRiskConfig
from services.ActionService import ActionService
from services.AuthService import AuthService
from services.ActivityService import ActivityService
from messages import Message, Error
from django.db.models import Max
from envoy_bu_policy_api.policy.models.crmp_issued_policies import IssuedPolicy
from envoy_bu_policy_api.policy.models.crmp_policy_documents import PolicyRequestDocument
from envoy_bu_policy_api.finance.controllers.utils.invoice_utils import (
    generate_invoice_for_issued_policy,
)
from envoy_bu_policy_api.service import handle_entity, _format_date_fields, replace_empty_strings_with_none
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from collections import defaultdict

from services.excel_exporter import SQLToExcelExporter
from services.s3_presigned_service import S3PresignedService
from envoy_bu_policy_api.policy.controllers.policy_status_utils import set_policy_base_active

class OpportunityPolicyService:
    """Service class to handle opportunity policy details operations"""

    def __init__(self):
        self.standard_policy_fields = self._get_standard_policy_fields()

    def _get_standard_policy_fields(self):
        """Define the standard structure for policy_request"""
        return {
            # Basic identification fields
            "id": None,
            "code": None,
            "policy_base_id": None,
            "policy_request_id": None,
            "issued_policy_id": None,
            # Request and status fields
            "requested_data": None,
            "status": None,
            "notes": None,
            "quotation_notes": None,
            "request_type": None,
            "request_type_id": None,
            "request_type_name": None,
            # Entity and relationship fields
            "opportunity_id": None,
            "entity_id": None,
            "lead_id": None,
            # Insurer/Service Provider fields
            "insurer_id": None,
            "insurer_name": None,
            "insurer_notes": None,
            "service_provider_id": None,
            "service_provider_name": None,
            "service_provider_description": None,
            "service_provider_logo": None,
            "service_provider_email": None,
            "service_provider_status": None,
            "sp_status": None,
            # Risk and coverage fields
            "risks": [],
            "risk_type_id": None,
            "risk_type_name": None,
            "risk_details_form_id": None,
            "coverage_type_id": None,
            "coverage_type_name": None,
            "coverage_details": None,
            "coverage_details_name": None,
            # Financial fields
            "sum_insured": None,
            "total_amount": None,
            "premium_amount": None,
            "payment_mode_id": None,
            "payment_mode_name": None,
            # Product fields
            "product_id": None,
            "product_name": None,
            # Date fields
            "received_date": None,
            "quotation_issued_date": None,
            "expiry_date": None,
            "quotation_expiry_date": None,
            "policy_start_date": None,
            "policy_expiry_date": None,
            # Request by fields
            "request_by_id": None,
            "request_by_name": None,
            # Customer fields
            "customer_id": None,
            "customer_name": None,
            "customer_logo": None,
            "customer_email": None,
            "customer_address": None,
            "customer_primary_contact": None,
            # Approval and status fields
            "approval_status": None,
            "approved_user": None,
            "approval_role": None,
            "approval_level": None,
            "approval_remarks": None,
            "approval_date": None,
            # Document fields
            "quotation_document": None,
            "quotation_document_name": None,
            "quotation_document_size": None,
            "policy_document": None,
            "policy_document_name": None,
            "policy_document_size": None,
            # Form submission fields
            "form_submission_id": None,
            "by_user_id": None,
            "attribute_id": None,
            "vendor_quotation_id": None,
            "send_quotation_id": None,
            # Property fields (for quotation)
            "property_id": None,
            "property_name": None,
            "property_description": None,
            # Version and draft fields
            "version": None,
            "is_received": None,
            "is_shortlisted": None,
            "is_draft": None,
            "is_sent": None,
            # Policy type indicator
            "is_policy": False,
            # Quotation details
            "quotation_details": None,
        }

    def _fetch_quotation_details(self, quotation_id):
        """
        Fetch comprehensive quotation details including form submissions and attributes
        Returns structured data with all quotation information
        """
        # First get basic quotation info
        quotation_info = (
            QueryBuilderService("crmq_quotations")
            .select(
                "id",
                "code",
                "requested_data",
                "customer_id",
                "request_type",
                "entity_id",
                "opportunity_id",
                "opportunity_type_id",
                "status",
                "notes",
                "entity_id",
                "email_data",
            )
            .where("id", quotation_id)
            .first()
        )

        if not quotation_info:
            return None

        # Get quotation approvals
        approvals = (
            QueryBuilderService("core_entity_approvals")
            .select(
                "core_entity_approvals.*",
            )
            .where("entity_id", quotation_info["entity_id"])
            .get()
        )

        # Structure the data
        details = {
            "quotation": {
                "id": quotation_info["id"],
                "code": quotation_info["code"],
                "status": quotation_info["status"],
                "notes": quotation_info["notes"],
                "request_type": quotation_info["request_type"],
                "entity_id": quotation_info["entity_id"],
                "opportunity_id": quotation_info["opportunity_id"],
                "opportunity_type_ids": (
                    json.loads(quotation_info["opportunity_type_id"])
                    if quotation_info["opportunity_type_id"]
                    else []
                ),
                "requested_data": quotation_info["requested_data"],
                "email_data": quotation_info["email_data"],
                "customer_id": quotation_info["customer_id"],
            },
            "quotation_approvals": approvals,
        }

    def _get_base_columns(self, fields):
        """Get base columns for the opportunity query"""
        columns = [
            "oppo.*",
            "core_users.display_name AS salse_agent_name",
            "core_users.picture AS sales_agent_picture",
            "stage.name AS stage_name",
            "stage.type AS stage_type",
            "stage.color AS stage_color",
            "curr.name AS currency_name",
            "curr.symbol AS currency_symbol",
            "ch.name AS channel_name",
            "health.health AS current_health",
        ]

        if fields == "additional":
            columns.extend(
                [
                    "oppo.contact_id",
                    "contact.name AS contact_name",
                    "contact.email AS contact_email",
                    "contact.primary_contact AS primary_contact",
                    "customer.name AS customer_name",
                    "customer.logo AS customer_logo",
                    "customer_contact.email AS customer_primary_contact_email",
                    "customer_contact.address AS customer_primary_contact_address",
                    "customer_contact.primary_contact AS customer_primary_contact_number",
                    "policy_risk.opportunity_type_id",
                    "risk.title AS risk_type_name",
                ]
            )

        return columns

    def _build_opportunity_query(self, fields):
        """Build the base opportunity query with joins"""
        query = (
            QueryBuilderService("crm_opportunities as oppo")
            .leftJoin("core_users", "core_users.id", "oppo.sales_agent_id")
            .leftJoin(
                "crm_opportunity_health as health",
                "health.id",
                "oppo.current_health_id",
            )
            .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")
            .leftJoin("core_currencies as curr", "curr.id", "oppo.currency_id")
            .leftJoin("core_channels as ch", "ch.id", "oppo.channel_id")
            .leftJoin("core_contacts as contact", "contact.id", "oppo.contact_id")
        )

        if fields == "additional":
            query = query.leftJoin(
                "core_customers as customer", "customer.id", "oppo.customer_id"
            )
            query = query.leftJoin(
                "core_contacts as customer_contact",
                "customer_contact.id",
                "customer.primary_contact_id",
            )
            query = query.leftJoin(
                "crm_oppor_opportunity_types as policy_risk",
                "policy_risk.opportunity_id",
                "oppo.id",
            )
            query = query.leftJoin(
                "crm_opportunity_types as risk",
                "risk.id",
                "policy_risk.opportunity_type_id",
            )

        return query

    def _apply_filters(self, query, request):
        """Apply various filters to the opportunity query"""
        filter_json = request.GET.get("filters", "{}")
        search_string = request.GET.get("search", "")
        filter_stage_id = request.GET.get("stage_id", None)
        filter_stage = request.GET.get("stage", None)  # New stage filter by name/value
        filter_sales_agent_id = request.GET.get("sales_agent_id", None)
        filter_type = request.GET.get("type", None)
        lead_id = request.GET.get("lead_id", None)
        policy_id = request.GET.get("policy_id", None)
        policy_base_id = request.GET.get("policy_base_id", None)
        customer_id = request.GET.get("customer_id", None)

        allowed_filters = [
            "oppo.title",
            "oppo.type",
            "oppo.stage_id",
            "oppo.sales_agent_id",
            "oppo.contact_id",
            "oppo.customer_id",
        ]
        search_columns = [
            "oppo.title",
            "oppo.type",
            "oppo.code",
            "contact.name",
            "contact.primary_contact",
            "stage.name",
            "curr.name",
        ]

        query = query.apply_conditions(
            filter_json, allowed_filters, search_string, search_columns
        )

        if filter_stage_id:
            query = query.where("oppo.stage_id", filter_stage_id)
        if filter_stage:
            # Filter by stage name/value (e.g., "qualified", "prospecting", etc.)
            query = query.where("stage.name", filter_stage)
        if filter_sales_agent_id:
            query = query.where("oppo.sales_agent_id", filter_sales_agent_id)
        if filter_type == "unassigned":
            query = self._apply_unassigned_filter(query)
        if lead_id:
            query = query.where("oppo.id", lead_id)
        if customer_id:
            query = query.where("oppo.customer_id", customer_id)

        # Handle policy_base_id filter with validation
        if policy_base_id:
            query, lead_id_from_policy = self._apply_policy_base_filter(
                query, policy_base_id
            )
            if lead_id_from_policy is None:
                # policy_base_id doesn't exist, return None to indicate empty result
                return None

        # Handle policy_id filter with validation
        if policy_id:
            query, lead_id_from_policy = self._apply_policy_filter(query, policy_id)
            if lead_id_from_policy is None:
                # policy_id doesn't exist, return None to indicate empty result
                return None

        # Validate that we don't have conflicting filters
        # If both lead_id and policy_base_id/policy_id are provided, they should match
        if lead_id and (policy_base_id or policy_id):
            # This is a validation check - if lead_id is explicitly provided,
            # it should match the lead_id from policy filters
            if policy_base_id:
                _, policy_lead_id = self._apply_policy_base_filter(
                    QueryBuilderService("crm_opportunities"), policy_base_id
                )
                if policy_lead_id and str(policy_lead_id) != str(lead_id):
                    # Conflicting filters - return None
                    return None
            if policy_id:
                _, policy_lead_id = self._apply_policy_filter(
                    QueryBuilderService("crm_opportunities"), policy_id
                )
                if policy_lead_id and str(policy_lead_id) != str(lead_id):
                    # Conflicting filters - return None
                    return None

        return query

    def _apply_unassigned_filter(self, query):
        """Apply filter for unassigned opportunities"""
        policy_base_query = QueryBuilderService("crmp_policy_base").select("lead_id")
        policy_base_ids = policy_base_query.get()

        if policy_base_ids:
            lead_ids = [
                row["lead_id"] for row in policy_base_ids if row["lead_id"] is not None
            ]
            if lead_ids:
                query = query.whereNotIn("oppo.id", lead_ids)

        return query

    def _apply_policy_base_filter(self, query, policy_base_id):
        """Apply filter based on policy_base_id"""
        # Validate that policy_base_id exists and get the corresponding lead_id
        row = (
            QueryBuilderService("crmp_policy_base")
            .select("lead_id")
            .where("id", policy_base_id)
            .first()
        )

        if row and row.get("lead_id"):
            # Apply the filter to get only opportunities that match this policy_base_id
            query = query.where("oppo.id", row["lead_id"])
            return query, row["lead_id"]  # Return both query and lead_id for validation
        else:
            # policy_base_id doesn't exist, return None to indicate empty result
            return query, None

    def _apply_policy_filter(self, query, policy_id):
        """Apply filter based on policy_id"""
        # Validate that policy_id exists and get the corresponding lead_id
        row = (
            QueryBuilderService("crmp_policy_base")
            .select("lead_id")
            .where("id", policy_id)
            .first()
        )

        if row and row.get("lead_id"):
            # Apply the filter to get only opportunities that match this policy_id
            query = query.where("oppo.id", row["lead_id"])
            return query, row["lead_id"]  # Return both query and lead_id for validation
        else:
            # policy_id doesn't exist, return None to indicate empty result
            return query, None

    def _execute_opportunity_query(self, query, request):
        """Execute the opportunity query with pagination"""
        ids = request.GET.get("ids", None)
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "oppo.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["oppo.title", "oppo.id"]

        if ids:
            id_list = ids.split(",")
            return query.whereIn("oppo.id", id_list).get()
        else:
            # Use paginate to get correct total count and pagination
            return query.paginate(
                page, limit, allowed_sorting_columns, sort_by, sort_dir
            )

    def _process_risks_grouping(self, data, fields):
        """Group risks into risk array for each opportunity"""
        if fields == "additional" and isinstance(data, dict) and "data" in data:
            items = data["data"]

            # Group risks by opportunity ID
            risk_map = defaultdict(list)
            for item in items:
                if item.get("opportunity_type_id") and item.get("risk_type_name"):
                    risk_map[item["id"]].append(
                        {
                            "risk_type_id": item["opportunity_type_id"],
                            "risk_type_name": item["risk_type_name"],
                        }
                    )

            # Remove duplicate opportunities and attach risks
            unique_items = {}
            for item in items:
                opp_id = item["id"]
                item["lead_risks"] = risk_map.get(opp_id, [])
                item.pop("opportunity_type_id", None)
                item.pop("risk_type_name", None)
                if opp_id not in unique_items:
                    unique_items[opp_id] = item

            # Replace with deduplicated list
            data["data"] = list(unique_items.values())

        return data

    def _process_contact_data(self, item):
        """Process contact data for an opportunity item"""
        contact_id = item.get("contact_id")
        contact_name = item.pop("contact_name", None)
        primary_contact = item.pop("primary_contact", None)
        item["contact"] = (
            {"name": contact_name, "primary_contact": primary_contact}
            if contact_id
            else None
        )

    def _process_customer_data(self, item):
        """Process customer data for an opportunity item"""
        customer_id = item.get("customer_id")
        customer_name = item.pop("customer_name", None)
        customer_logo = item.pop("customer_logo", None)
        customer_email = item.pop("customer_primary_contact_email", None)
        customer_address = item.pop("customer_primary_contact_address", None)
        customer_contact_number = item.pop("customer_primary_contact_number", None)
        item["customer"] = (
            {
                "name": customer_name,
                "logo": customer_logo,
                "email": customer_email,
                "address": customer_address,
                "primary_contact": customer_contact_number,
            }
            if customer_id
            else None
        )

    def _process_next_task(self, item):
        """Process next task data for an opportunity item"""
        opportunity_id = item.get("id")
        task_ids = OpportunityTask.objects.filter(
            opportunity_id=opportunity_id
        ).values_list("task_id", flat=True)
        tasks = (
            Task.objects.filter(id__in=task_ids)
            .select_related("task_status")
            .order_by("sort_index")
        )
        selected_task = None
        for task in tasks:
            if (
                task.task_status
                and task.task_status.type
                and task.task_status.type.upper() == "TODO"
            ):
                selected_task = task
                break
        item["next_task"] = (
            {
                "task": selected_task.task,
                "start_date": selected_task.start_date,
                "assigned_user_name": (
                    selected_task.assigned_to.display_name
                    if selected_task.assigned_to
                    else None
                ),
                "assigned_user_picture": (
                    selected_task.assigned_to.picture
                    if selected_task.assigned_to
                    else None
                ),
            }
            if selected_task
            else None
        )

    def _fetch_policy_base_data(self, opportunity_id):
        """Fetch policy base data for an opportunity"""
        return (
            QueryBuilderService("crmp_policy_base as policy")
            .leftJoin(
                "crmp_coverage_types as coverage",
                "coverage.id",
                "policy.coverage_type_id",
            )
            .leftJoin(
                "crmp_payment_plans as payment", "payment.id", "policy.payment_mode_id"
            )
            .leftJoin(
                "core_vendor_products as product", "product.id", "policy.product_id"
            )
            .leftJoin(
                "core_service_providers as insurer", "insurer.id", "policy.insurer_id"
            )
            .leftJoin("core_users as requester", "requester.id", "policy.request_by_id")
            .leftJoin(
                "crmp_request_types as request_type",
                "request_type.id",
                "policy.request_type_id",
            )
            .leftJoin("core_customers as customer", "customer.id", "policy.customer_id")
            .leftJoin(
                "core_contacts as customer_contact",
                "customer_contact.id",
                "customer.primary_contact_id",
            )
            .leftJoin(
                "crmp_issued_policies as issued_policy", "issued_policy.policy_base_id", "policy.id"
            )
            .select(
                # Basic identification fields
                "policy.id AS policy_base_id",
                "policy.lead_id AS opportunity_id",
                # Request and status fields
                "policy.quotation_notes as notes",
                "policy.quotation_notes as quotation_notes",
                "policy.request_type_id",
                "request_type.name AS request_type_name",
                # Insurer/Service Provider fields
                "policy.insurer_id",
                "insurer.name AS insurer_name",
                "insurer.description AS insurer_notes",
                "insurer.id AS service_provider_id",
                "insurer.name AS service_provider_name",
                "insurer.description AS service_provider_description",
                "insurer.logo AS service_provider_logo",
                "insurer.email AS service_provider_email",
                "insurer.status_id AS service_provider_status",
                # Risk and coverage fields
                "policy.risk_type_id",
                "policy.risk_details_form_id",
                "policy.coverage_type_id",
                "coverage.name AS coverage_type_name",
                # Financial fields
                "policy.sum_insured",
                "policy.premium_amount AS total_amount",
                "policy.premium_amount AS premium_amount",
                "policy.payment_mode_id",
                "payment.name AS payment_mode_name",
                # Product fields
                "policy.product_id",
                "product.name AS product_name",
                # Date fields
                "policy.quotation_issued_date AS received_date",
                "policy.quotation_issued_date AS quotation_issued_date",
                "policy.quotation_expiry_date AS expiry_date",
                "policy.quotation_expiry_date AS quotation_expiry_date",
                "policy.policy_start_date",
                "policy.policy_expiry_date",
                # Request by fields
                "policy.request_by_id",
                "requester.display_name AS request_by_name",
                # Customer fields
                "policy.customer_id",
                "customer.name AS customer_name",
                "customer.logo AS customer_logo",
                "customer_contact.email AS customer_email",
                "customer_contact.address AS customer_address",
                "customer_contact.primary_contact AS customer_primary_contact",
                # Document fields
                "policy.quotation_document AS coverage_details",
                "policy.quotation_document_name AS coverage_details_name",
                "policy.quotation_document AS quotation_document",
                "policy.quotation_document_name AS quotation_document_name",
                "policy.quotation_document_size",
                # Policy type indicator
                "TRUE AS is_policy",
                # Issued policy fields
                "issued_policy.brokerage_policy_id",
                "issued_policy.id AS issued_policy_id",
                "issued_policy.insurer_policy_id",
            )
            .where("policy.lead_id", opportunity_id)
            .orderBy("policy.id", "asc")
            .first()
        )

    def _fetch_policy_risks(self, policy_base_id):
        """Fetch comprehensive risk details for a policy from crmp_policy_risk_config"""
        return (
            QueryBuilderService("crmp_policy_risk_config as prc")
            .leftJoin(
                "crm_risk_submissions as rs", "rs.id", "prc.risk_submission_id"
            )
            .leftJoin(
                "crm_risks as r", "r.id", "rs.risk_id"
            )
            .leftJoin(
                "crm_opportunity_types as ot", "ot.id", "r.risk_type_id"
            )
            .select(
                "prc.id",
                "prc.policy_base_id",
                "prc.risk_submission_id",
                "rs.risk_id",
                "rs.submission_id",
                "r.code AS risk_code",
                "r.risk_type_id",
                "ot.title AS risk_type_name",
                "ot.description AS risk_type_description",
                # "prc.created_at",
                # "prc.updated_at"
            )
            .where("prc.policy_base_id", policy_base_id)
            .orderBy("prc.id", "asc")
            .get()
        )

    def _process_policy_data(self, item, opportunity_id):
        """Process policy data for an opportunity"""
        policy_base_data = self._fetch_policy_base_data(opportunity_id)

        if policy_base_data:
            # Fetch risks for the policy
            risks = self._fetch_policy_risks(policy_base_data["policy_base_id"])
            policy_base_data["risks"] = risks

            # Store policy_base_id for reference but don't include in final response
            policy_base_id = policy_base_data.pop("policy_base_id", None)

            # Merge with standard fields to ensure consistency
            policy_request = {**self.standard_policy_fields, **policy_base_data}
            policy_request["is_policy"] = True
            policy_request["policy_base_id"] = policy_base_id

            # Ensure proper field mapping for consistency
            self._ensure_field_consistency(policy_request)

            item["policy_request"] = policy_request
            return True

        return False

    def _fetch_quotation_data(self, opportunity_id):
        """Fetch quotation data for an opportunity"""
        return (
            QueryBuilderService("crmq_quotations as q")
            .leftJoin("crmq_quotation_attributes as qa", "qa.quotation_id", "q.id")
            .leftJoin(
                "crmq_quotation_form_submissions as qfs",
                "qfs.form_submission_id",
                "qa.form_submission_id",
            )
            .leftJoin(
                "crmq_quotation_vendor_quotations as qvq",
                "qvq.vendor_quotation_id",
                "qfs.vendor_quotation_id",
            )
            .leftJoin(
                "crmq_quotation_service_providers as qsp", "qsp.quotation_id", "q.id"
            )
            .leftJoin("crmq_quotation_risk_properties as rp", "rp.quotation_id", "q.id")
            .leftJoin("crmq_properties as prop", "prop.id", "rp.property_id")
            .leftJoin(
                "core_entity_approvals as approval", "approval.entity_id", "q.entity_id"
            )
            .leftJoin(
                "core_service_providers as sp", "sp.id", "qsp.service_provider_id"
            )
            .select(
                # Basic identification fields
                "q.id AS quotation_id",
                "q.id AS id",
                "q.code",
                "q.opportunity_id",
                "q.entity_id",
                # Request and status fields
                "q.requested_data",
                "q.status",
                "q.notes",
                "q.notes AS quotation_notes",
                "q.request_type",
                "q.request_type AS request_type_id",
                # Risk and coverage fields
                "q.opportunity_type_id",
                "rp.risk_type_id",
                "rp.property_id",
                "prop.name AS property_name",
                "prop.description AS property_description",
                # Form submission fields
                "qa.attribute_id",
                "qfs.form_submission_id",
                "qfs.by_user_id",
                "qvq.send_quotation_id",
                "qvq.vendor_quotation_id",
                # Service provider fields
                "qsp.service_provider_id",
                "qsp.is_received",
                "qsp.is_shortlisted",
                "qsp.is_draft",
                "qsp.is_sent",
                "qsp.version",
                "qsp.status AS sp_status",
                "sp.name AS service_provider_name",
                "sp.description AS service_provider_description",
                "sp.logo AS service_provider_logo",
                "sp.email AS service_provider_email",
                "sp.status_id AS service_provider_status",
                "sp.id AS insurer_id",
                "sp.name AS insurer_name",
                "sp.description AS insurer_notes",
                # Approval fields
                "approval.user AS approved_user",
                "approval.role AS approval_role",
                "approval.status AS approval_status",
                "approval.level AS approval_level",
                "approval.remarks AS approval_remarks",
                "approval.date AS approval_date",
                # Policy type indicator
                "FALSE AS is_policy",
            )
            .where("q.opportunity_id", opportunity_id)
            .orderBy("q.id", "desc")
            .get()
        )

    def _process_quotation_data(self, item, opportunity_id):
        """Process quotation data for an opportunity"""
        quotation_data = self._fetch_quotation_data(opportunity_id)

        if quotation_data:
            quotation_map = defaultdict(
                lambda: {
                    **self.standard_policy_fields,
                    "risks": [],
                }
            )
            all_opp_type_ids = set()
            quotation_opp_type_lookup = {}

            for row in quotation_data:
                qid = row["quotation_id"]
                qobj = quotation_map[qid]

                # Map all available fields from the row
                self._map_quotation_fields(qobj, row)

                # Handle opportunity type IDs for risks
                opp_type_ids = row.get("opportunity_type_id", [])
                if isinstance(opp_type_ids, str):
                    try:
                        opp_type_ids = json.loads(opp_type_ids)
                    except Exception:
                        opp_type_ids = []
                if isinstance(opp_type_ids, list):
                    all_opp_type_ids.update(opp_type_ids)
                    quotation_opp_type_lookup[qid] = opp_type_ids

            # Get the first quotation (most recent)
            policy_request = list(quotation_map.values())[0]
            quotation_id = policy_request.get("id")
            
            # Ensure policy_base_id is not null - if it's null, set it to quotation_id
            if not policy_request.get("policy_base_id"):
                policy_request["policy_base_id"] = quotation_id

            # Fetch detailed quotation information
            quotation_details = None
            if quotation_id:
                quotation_details = self._fetch_quotation_details(quotation_id)

            # Fetch additional form submission data if available
            self._fetch_form_submission_data(policy_request, quotation_id)

            # Ensure all standard fields are present and properly mapped
            policy_request = {**self.standard_policy_fields, **policy_request}
            policy_request["is_policy"] = False

            # Ensure proper field mapping for consistency
            self._ensure_field_consistency(policy_request)

            # Remove quotation_details from policy_request if it exists
            if "quotation_details" in policy_request:
                del policy_request["quotation_details"]

            # Add both policy_request and quotation_details to the item
            item["policy_request"] = policy_request
            if quotation_details:
                item["quotation_details"] = quotation_details

            return True

        return False

    def _map_quotation_fields(self, qobj, row):
        """Map quotation fields from database row to quotation object"""
        field_mapping = {
            "id": row.get("id"),
            "code": row.get("code"),
            "requested_data": row.get("requested_data"),
            "status": row.get("status"),
            "notes": row.get("notes"),
            "quotation_notes": row.get("quotation_notes"),
            "request_type": row.get("request_type"),
            "request_type_id": row.get("request_type_id"),
            "opportunity_id": row.get("opportunity_id"),
            "entity_id": row.get("entity_id"),
            "risk_type_id": row.get("risk_type_id"),
            "property_id": row.get("property_id"),
            "property_name": row.get("property_name"),
            "property_description": row.get("property_description"),
            "form_submission_id": row.get("form_submission_id"),
            "by_user_id": row.get("by_user_id"),
            "attribute_id": row.get("attribute_id"),
            "vendor_quotation_id": row.get("vendor_quotation_id"),
            "send_quotation_id": row.get("send_quotation_id"),
            "service_provider_id": row.get("service_provider_id"),
            "is_received": row.get("is_received"),
            "is_shortlisted": row.get("is_shortlisted"),
            "is_draft": row.get("is_draft"),
            "is_sent": row.get("is_sent"),
            "version": row.get("version"),
            "sp_status": row.get("sp_status"),
            "service_provider_name": row.get("service_provider_name"),
            "service_provider_description": row.get("service_provider_description"),
            "service_provider_logo": row.get("service_provider_logo"),
            "service_provider_email": row.get("service_provider_email"),
            "service_provider_status": row.get("service_provider_status"),
            "insurer_id": row.get("insurer_id"),
            "insurer_name": row.get("insurer_name"),
            "insurer_notes": row.get("insurer_notes"),
            "approved_user": row.get("approved_user"),
            "approval_role": row.get("approval_role"),
            "approval_status": row.get("approval_status"),
            "approval_level": row.get("approval_level"),
            "approval_remarks": row.get("approval_remarks"),
            "approval_date": row.get("approval_date"),
            "is_policy": row.get("is_policy"),
        }

        # Update only non-None values
        for key, value in field_mapping.items():
            if value is not None:
                qobj[key] = value

    def _process_quotation_risks(
        self, quotation_map, all_opp_type_ids, quotation_opp_type_lookup
    ):
        """Process risks for quotations"""
        if all_opp_type_ids:
            opp_type_details = (
                QueryBuilderService("crm_opportunity_types")
                .select("id", "title")
                .whereIn("id", list(all_opp_type_ids))
                .get()
            )
            opp_type_map = {o["id"]: o["title"] for o in opp_type_details}
            for qid, qobj in quotation_map.items():
                opp_ids = quotation_opp_type_lookup.get(qid, [])
                qobj["risks"] = [
                    {"risk_type_id": oid, "risk_type_name": opp_type_map.get(oid)}
                    for oid in opp_ids
                    if oid in opp_type_map
                ]

    def _fetch_form_submission_data(self, policy_request, quotation_id):
        """Fetch additional form submission data for quotation"""
        latest_sp = (
            QuotationServiceProvider.objects.filter(quotation_id=quotation_id)
            .order_by("-id")
            .first()
        )
        if latest_sp:
            vendor_quotation_id = latest_sp.id
            form_submission = (
                QuotationFormSubmission.objects.filter(
                    vendor_quotation_id=vendor_quotation_id
                )
                .order_by("-id")
                .first()
            )
            if form_submission:
                form_submission_id = form_submission.form_submission_id
                form_values = FormSubmissionValue.objects.filter(
                    form_submission_id=form_submission_id
                ).select_related("attribute")
                for fv in form_values:
                    if fv.attribute and fv.attribute.title:
                        key = fv.attribute.title.strip().lower().replace(" ", "_")
                        policy_request[key] = fv.value

    def _ensure_field_consistency(self, policy_request):
        """Ensure proper field mapping for consistency"""
        if policy_request.get("quotation_notes") and not policy_request.get("notes"):
            policy_request["notes"] = policy_request["quotation_notes"]
        if policy_request.get("service_provider_id") and not policy_request.get(
            "insurer_id"
        ):
            policy_request["insurer_id"] = policy_request["service_provider_id"]
        if policy_request.get("service_provider_name") and not policy_request.get(
            "insurer_name"
        ):
            policy_request["insurer_name"] = policy_request["service_provider_name"]

    def _process_additional_fields(self, data, fields):
        """Process additional fields for opportunities"""
        if fields == "additional" and isinstance(data, dict) and "data" in data:
            items = data["data"]
            for item in items:
                if isinstance(item, dict):
                    self._process_contact_data(item)
                    self._process_customer_data(item)
                    self._process_next_task(item)

                    opportunity_id = item.get("id")
                    # self._process_policy_data(item, opportunity_id)
                    # self._process_quotation_data(item, opportunity_id)

                    # Try to fetch policy data first, if not available, fetch quotation data
                    if not self._process_policy_data(item, opportunity_id):
                        self._process_quotation_data(item, opportunity_id)
                    
                    # Process quotation data for opportunities
                    self._process_quotation_data_for_opportunity(item, opportunity_id)

        return data

    def _exclude_used_opportunities(self, query):
        """
        Exclude opportunities that are already used in policies (request or issued policies)
        """
        try:
            # Get opportunity IDs that are already used in request policies
            used_in_request_policies = QueryBuilderService("crmp_policy_base")\
                .select("lead_id")\
                .whereNotNull("lead_id")\
                .get()
            
            # Get opportunity IDs that are already used in issued policies
            used_in_issued_policies = QueryBuilderService("crmp_issued_policies")\
                .select("policy_base_id")\
                .leftJoin("crmp_policy_base", "crmp_policy_base.id", "crmp_issued_policies.policy_base_id")\
                .whereNotNull("crmp_policy_base.lead_id")\
                .get()
            
            # Combine all used opportunity IDs
            used_opportunity_ids = set()
            
            # Add IDs from request policies
            for item in used_in_request_policies:
                if item.get("lead_id"):
                    used_opportunity_ids.add(item["lead_id"])
            
            # Add IDs from issued policies
            for item in used_in_issued_policies:
                if item.get("policy_base_id"):
                    # Get the lead_id from policy_base
                    policy_base = QueryBuilderService("crmp_policy_base")\
                        .select("lead_id")\
                        .where("id", item["policy_base_id"])\
                        .first()
                    if policy_base and policy_base.get("lead_id"):
                        used_opportunity_ids.add(policy_base["lead_id"])
            
            # Exclude used opportunities from the query
            if used_opportunity_ids:
                query = query.whereNotIn("oppo.id", list(used_opportunity_ids))
            
            return query
            
        except Exception as e:
            print(f"Error excluding used opportunities: {str(e)}")
            # Return original query if there's an error
            return query

    def get_opportunities_with_policy_details(self, request):
        """Main method to get opportunities with policy details"""
        fields = request.GET.get("fields", None)
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))

        # Build and execute opportunity query
        query = self._build_opportunity_query(fields)
        query = query.select(*self._get_base_columns(fields))
        query = self._apply_filters(query, request)
        
        # Add validation to exclude opportunities already used in policies
        query = self._exclude_used_opportunities(query)

        # Check if filters returned None (indicating invalid policy_base_id or policy_id)
        if query is None:
            # Return empty, well-formed response
            empty_response = {
                "data": [],
                "total_records": 0,
                "per_page": limit,
                "current_page": page,
                "last_page": 0,
            }
            return ResponseService.response(
                "SUCCESS", empty_response, Message.DATA_FETCHED
            )

        data = self._execute_opportunity_query(query, request)

        # Process risks grouping
        data = self._process_risks_grouping(data, fields)

        # Process additional fields
        data = self._process_additional_fields(data, fields)

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    def _process_quotation_data_for_opportunity(self, item, opportunity_id):
        """Process quotation data for an opportunity item"""
        print("Processing quotation data for opportunity_id:", opportunity_id)
        try:
            # Fetch quotation data using the chain
            quotation_data = self._fetch_quotation_data_by_opportunity(opportunity_id)
            
            if quotation_data:
                # Add quotation data to the item
                item["quotation"] = {
                    "quotation_id": quotation_data.get("quotation_id"),
                    "quotation_code": quotation_data.get("quotation_code"),
                    "generated_pdf": quotation_data.get("generated_pdf"),
                    "version": quotation_data.get("version"),
                    "coverage_details": quotation_data.get("coverage_details"),
                    "coverage_details_type": quotation_data.get("coverage_details_type"),
                    "coverage_details_name": quotation_data.get("coverage_details_name")
                }
            else:
                # Set quotation data to None if not found
                item["quotation"] = None
                
        except Exception as e:
            print(f"Error processing quotation data: {str(e)}")
            item["quotation"] = None

    def _fetch_quotation_data_by_opportunity(self, opportunity_id):
        """Fetch quotation data by following the chain from opportunity_id"""
        try:
            # Step 1: Get quotation_id and quotation_code from crmq_quotations table
            quotation_data = QueryBuilderService("crmq_quotations as q")\
                .select("q.id AS quotation_id", "q.code AS quotation_code")\
                .where("q.opportunity_id", opportunity_id)\
                .first()
            
            if not quotation_data:
                return None
            
            quotation_id = quotation_data.get("quotation_id")
            quotation_code = quotation_data.get("quotation_code")
            print("quotation_id", quotation_id)

            status_data = QueryBuilderService("core_status as status")\
                .select("status.id AS status_id")\
                .where("status.type", "quotation_confirmed")\
                .where("status.module", "quotation")\
                .first()
            
            if not status_data:
                print(f"No status found for quotation_confirmed in quotation module")
                return None
            
            status_id = status_data.get("status_id")
            print("status_id", status_id)
            # Step 2: Check crmq_quotation_service_providers for status = 3
            service_provider_data = QueryBuilderService("crmq_quotation_service_providers as qsp")\
                .select("qsp.id AS service_provider_id")\
                .where("qsp.quotation_id", quotation_id)\
                .where("qsp.status", status_id)\
                .first()
            
            if not service_provider_data:
                return None
            
            service_provider_id = service_provider_data.get("service_provider_id")
            print("service_provider_id", service_provider_id)
            # Step 3: Get vendor_quotation_id from crmq_quotation_vendor_quotations
            vendor_quotation_data = QueryBuilderService("crmq_quotation_vendor_quotations as qvq")\
                .select("qvq.send_quotation_id")\
                .where("qvq.vendor_quotation_id", service_provider_id)\
                .first()
            print("vendor_quotation_data", vendor_quotation_data)
            if not vendor_quotation_data:
                return None
            
            
            
            send_quotation_id = vendor_quotation_data.get("send_quotation_id")
            
            # Step 4: Get coverage details from crmq_vendor_response table
            coverage_data = QueryBuilderService("crmq_vendor_response as vr")\
                .select(
                    "vr.coverage_details",
                    "vr.coverage_details_type", 
                    "vr.coverage_details_name"
                )\
                .where("vr.quotation_id", quotation_id)\
                .where("vr.vendor_quotation_id", service_provider_id)\
                .first()
            
            # Step 5: Get generated_pdf and version from crmq_send_quotations
            final_data = QueryBuilderService("crmq_send_quotations as sq")\
                .select(
                    "sq.generated_pdf",
                    "sq.version"
                )\
                .where("sq.id", send_quotation_id)\
                .first()
            
            if final_data:
                # Add quotation_id and quotation_code to the response
                final_data["quotation_id"] = quotation_id
                final_data["quotation_code"] = quotation_code
                
                # Add coverage details from vendor response
                if coverage_data:
                    final_data["coverage_details"] = coverage_data.get("coverage_details")
                    final_data["coverage_details_type"] = coverage_data.get("coverage_details_type")
                    final_data["coverage_details_name"] = coverage_data.get("coverage_details_name")
                else:
                    final_data["coverage_details"] = None
                    final_data["coverage_details_type"] = None
                    final_data["coverage_details_name"] = None
                
                return final_data
            
            return None
            
        except Exception as e:
            print(f"Error fetching quotation data: {str(e)}")
            return None


class ApprovedPolicyService:
    """Service class to handle approved policy details operations"""

    def __init__(self):
        self.standard_policy_fields = self._get_standard_policy_fields()

    def _get_standard_policy_fields(self):
        """Define the standard structure for policy_request - same as OpportunityPolicyService"""
        return {
            # Basic identification fields
            "id": None,
            "code": None,
            "policy_base_id": None,
            "policy_request_id": None,
            # Request and status fields
            "requested_data": None,
            "status": None,
            "notes": None,
            "quotation_notes": None,
            "request_type": None,
            "request_type_id": None,
            "request_type_name": None,
            # Entity and relationship fields
            "opportunity_id": None,
            "entity_id": None,
            "lead_id": None,
            # Insurer/Service Provider fields
            "insurer_id": None,
            "insurer_name": None,
            "insurer_notes": None,
            "service_provider_id": None,
            "service_provider_name": None,
            "service_provider_description": None,
            "service_provider_logo": None,
            "service_provider_email": None,
            "service_provider_status": None,
            "sp_status": None,
            # Risk and coverage fields
            "risks": [],
            "risk_type_id": None,
            "risk_type_name": None,
            "risk_details_form_id": None,
            "coverage_type_id": None,
            "coverage_type_name": None,
            "coverage_details": None,
            "coverage_details_name": None,
            # Financial fields
            "sum_insured": None,
            "total_amount": None,
            "premium_amount": None,
            "payment_mode_id": None,
            "payment_mode_name": None,
            # Product fields
            "product_id": None,
            "product_name": None,
            # Date fields
            "received_date": None,
            # Issued policy fields
            "brokerage_policy_id": None,
            "issued_policy_id": None,
            "insurer_policy_id": None,
            "quotation_issued_date": None,
            "expiry_date": None,
            "quotation_expiry_date": None,
            "policy_start_date": None,
            "policy_expiry_date": None,
            # Request by fields
            "request_by_id": None,
            "request_by_name": None,
            # Customer fields
            "customer_id": None,
            "customer_name": None,
            "customer_logo": None,
            "customer_email": None,
            "customer_address": None,
            "customer_primary_contact": None,
            # Approval and status fields
            "approval_status": None,
            "approved_user": None,
            "approval_role": None,
            "approval_level": None,
            "approval_remarks": None,
            "approval_date": None,
            # Document fields
            "quotation_document": None,
            "quotation_document_name": None,
            "quotation_document_size": None,
            "policy_document": None,
            "policy_document_name": None,
            "policy_document_size": None,
            # Form submission fields
            "form_submission_id": None,
            "by_user_id": None,
            "attribute_id": None,
            "vendor_quotation_id": None,
            "send_quotation_id": None,
            # Property fields (for quotation)
            "property_id": None,
            "property_name": None,
            "property_description": None,
            # Version and draft fields
            "version": None,
            "is_received": None,
            "is_shortlisted": None,
            "is_draft": None,
            "is_sent": None,
            # Policy type indicator
            "is_policy": True,
        }

    def _get_base_columns(self, fields):
        """Get base columns for the query - structured like opportunities"""
        base_columns = [
            # Opportunity-like structure (using request policy as the main object)
            "rp.id",
            "rp.policy_request_id AS code",
            "rp.policy_base_id",
            "rp.entity_id",
            "rp.policy_request_date AS start_date",
            "rp.policy_request_date AS end_date",
            "policy_base.premium_amount",
            "policy_base.sum_insured",
            "rp.policy_request_id AS notes",
            "FALSE AS is_renewal",
            # Issued policy fields
            "issued_policy.brokerage_policy_id as brokerage_policy_number",
            "issued_policy.id AS issued_policy_id",
            "issued_policy.insurer_policy_id as insurer_policy_number",
        ]

        if fields == "additional":
            base_columns.extend(
                [
                    "policy_base.lead_id AS opportunity_id",
                    "policy_base.customer_id",
                    "policy_base.product_id",
                    "policy_base.risk_type_id",
                    "policy_base.coverage_type_id",
                    "policy_base.insurer_id",
                    "policy_base.request_type_id",
                    "policy_base.request_by_id",
                    "customer.name AS customer_name",
                    "customer.logo AS customer_logo",
                    "customer_contact.email AS customer_contact_email",
                    "customer_contact.address AS customer_contact_address",
                    "customer_contact.primary_contact AS customer_contact_primary_contact",
                    "product.name AS product_name",
                    "risk_type.title AS risk_type_title",
                    "coverage_type.name AS coverage_type_name",
                    "insurer.name AS insurer_name",
                    "insurer.logo AS insurer_logo",
                    "request_type.name AS request_type_name",
                    "requested_by.display_name AS requested_by_display_name",
                    "requested_by.picture AS requested_by_picture",
                    "status.name AS status_name",
                ]
            )

        return base_columns

    def _build_approved_policy_query(self, fields):
        """Build the base approved policy query with joins - structured like opportunities"""
        query = (
            QueryBuilderService("crmp_request_policies as rp")
            .leftJoin(
                "crmp_policy_base as policy_base", "policy_base.id", "rp.policy_base_id"
            )
            .leftJoin("core_status as status", "status.id", "rp.status_id")
            .leftJoin(
                "crmp_issued_policies as issued_policy", "issued_policy.policy_base_id", "policy_base.id"
            )
        )

        if fields == "additional":
            query = query.leftJoin(
                "core_customers as customer", "customer.id", "policy_base.customer_id"
            )
            query = query.leftJoin(
                "core_contacts as customer_contact",
                "customer_contact.id",
                "customer.primary_contact_id",
            )
            query = query.leftJoin(
                "core_vendor_products as product",
                "product.id",
                "policy_base.product_id",
            )
            query = query.leftJoin(
                "crm_opportunity_types as risk_type",
                "risk_type.id",
                "policy_base.risk_type_id",
            )
            query = query.leftJoin(
                "crmp_coverage_types as coverage_type",
                "coverage_type.id",
                "policy_base.coverage_type_id",
            )
            query = query.leftJoin(
                "core_service_providers as insurer",
                "insurer.id",
                "policy_base.insurer_id",
            )
            query = query.leftJoin(
                "crmp_request_types as request_type",
                "request_type.id",
                "policy_base.request_type_id",
            )
            query = query.leftJoin(
                "core_users as requested_by",
                "requested_by.id",
                "policy_base.request_by_id",
            )

        return query

    def _apply_filters(self, query, request):
        """Apply filters to the query"""
        # Apply policy_base_id filter if provided
        policy_base_id = request.GET.get("policy_base_id", None)
        if policy_base_id:
            query = query.where("rp.policy_base_id", policy_base_id)

        # Apply policy_id filter if provided
        policy_id = request.GET.get("policy_id", None)
        if policy_id:
            query = query.where("rp.id", policy_id)

        # Apply customer_id filter if provided
        customer_id = request.GET.get("customer_id", None)
        if customer_id:
            query = query.where("policy_base.customer_id", customer_id)

        # Apply insurer_id filter if provided
        insurer_id = request.GET.get("insurer_id", None)
        if insurer_id:
            query = query.where("policy_base.insurer_id", insurer_id)

        # Apply date range filters
        start_date = request.GET.get("start_date", None)
        if start_date:
            query = query.where("rp.policy_request_date", ">=", start_date)

        end_date = request.GET.get("end_date", None)
        if end_date:
            query = query.where("rp.policy_request_date", "<=", end_date)

        # Apply search filter
        search = request.GET.get("search", None)
        if search:
            query = query.where("rp.policy_request_id", "LIKE", f"%{search}%")

        return query

    def _execute_approved_policy_query(self, query, request):
        """Execute the approved policy query with pagination"""
        ids = request.GET.get("ids", None)
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "rp.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = [
            "rp.policy_request_id",
            "rp.policy_request_date",
            "policy_base.premium_amount",
        ]

        if ids:
            id_list = ids.split(",")
            return query.whereIn("rp.id", id_list).get()
        else:
            return query.paginate(
                page, limit, allowed_sorting_columns, sort_by, sort_dir
            )

    def _process_additional_fields(self, data, fields):
        """Process additional fields for approved policies - structured like opportunities"""
        if fields == "additional" and isinstance(data, dict) and "data" in data:
            items = data["data"]

            for item in items:
                # Process contact data (similar to opportunities)
                self._process_contact_data(item)
                self._process_customer_data(item)
                self._process_next_task(item)

                # Process policy data (similar to opportunities) - ensure every item has policy_request
                opportunity_id = item.get("opportunity_id")
                if opportunity_id:
                    self._process_policy_data(item, opportunity_id)
                    # Process quotation data
                    self._process_quotation_data(item, opportunity_id)
                else:
                    # If no opportunity_id, still create policy_request from available data
                    policy_request = self._create_policy_request_from_item(item)
                    item["policy_request"] = policy_request

        return data

    def _process_contact_data(self, item):
        """Process contact data for an approved policy item (similar to opportunities)"""
        # For approved policies, we don't have direct contact data like opportunities
        # So we'll set it to None to match the structure
        item["contact"] = None

    def _process_customer_data(self, item):
        """Process customer data for an approved policy item (similar to opportunities)"""
        customer_id = item.get("customer_id")
        customer_name = item.pop("customer_name", None)
        customer_logo = item.pop("customer_logo", None)
        customer_email = item.pop("customer_contact_email", None)
        customer_address = item.pop("customer_contact_address", None)
        customer_contact_number = item.pop("customer_contact_primary_contact", None)
        item["customer"] = (
            {
                "name": customer_name,
                "logo": customer_logo,
                "email": customer_email,
                "address": customer_address,
                "primary_contact": customer_contact_number,
            }
            if customer_id
            else None
        )

    def _process_next_task(self, item):
        """Process next task data for an approved policy item (similar to opportunities)"""
        # For approved policies, we don't have tasks like opportunities
        # So we'll set it to None to match the structure
        item["next_task"] = None

    def _process_policy_data(self, item, opportunity_id):
        """Process policy data for a request policy item (similar to opportunities)"""
        # For request policies, we need to fetch the policy data from request_policies
        # and structure it like the policy_request in opportunities
        policy_data = self._fetch_request_policy_data(opportunity_id)

        # Always create a policy_request object, even if no specific request data is found
        if policy_data:
            # Fetch risks for the policy
            risks = self._fetch_policy_risks(policy_data["policy_base_id"])
            policy_data["risks"] = risks

            # Store policy_base_id for reference but don't include in final response
            policy_base_id = policy_data.pop("policy_base_id", None)

            # Merge with standard fields to ensure consistency
            policy_request = {**self.standard_policy_fields, **policy_data}
            policy_request["is_policy"] = True
            policy_request["policy_base_id"] = policy_base_id

            # Ensure proper field mapping for consistency
            self._ensure_field_consistency(policy_request)

            item["policy_request"] = policy_request
        else:
            # Create policy_request object from available item data
            policy_request = self._create_policy_request_from_item(item)
            item["policy_request"] = policy_request

        return True

    def _process_quotation_data(self, item, opportunity_id):
        print("Processing quotation data for opportunity_id:", opportunity_id)
        """Process quotation data for an approved policy item"""
        try:
            # Fetch quotation data using the chain
            quotation_data = self._fetch_quotation_data_by_opportunity(opportunity_id)
            
            if quotation_data:
                # Add quotation data to the item
                item["quotation"] = {
                    "quotation_id": quotation_data.get("quotation_id"),
                    "quotation_code": quotation_data.get("quotation_code"),
                    "generated_pdf": quotation_data.get("generated_pdf"),
                    "version": quotation_data.get("version"),
                    "coverage_details": quotation_data.get("coverage_details"),
                    "coverage_details_type": quotation_data.get("coverage_details_type"),
                    "coverage_details_name": quotation_data.get("coverage_details_name")
                }
            else:
                # Set quotation data to None if not found
                item["quotation"] = None
                
        except Exception as e:
            print(f"Error processing quotation data: {str(e)}")
            item["quotation"] = None

    def _create_policy_request_from_item(self, item):
        """Create a policy_request object from available item data when no specific request data is found"""
        # Start with standard policy fields
        policy_request = {**self.standard_policy_fields}

        # Map available fields from the main item to policy_request structure
        policy_request.update(
            {
                "id": item.get("id"),
                "code": item.get("code"),
                "policy_base_id": item.get("policy_base_id") or item.get("id"),  # Use id as fallback if policy_base_id is null
                "policy_request_id": item.get("code"),  # Use code as policy_request_id
                "requested_data": None,
                "status": None,
                "notes": item.get("notes"),
                "quotation_notes": item.get("notes"),
                "request_type": None,
                "request_type_id": item.get("request_type_id"),
                "request_type_name": item.get("request_type_name"),
                "opportunity_id": item.get("opportunity_id"),
                "entity_id": item.get("entity_id"),
                "lead_id": item.get("opportunity_id"),
                "insurer_id": item.get("insurer_id"),
                "insurer_name": item.get("insurer_name"),
                "insurer_notes": None,
                "service_provider_id": item.get("insurer_id"),
                "service_provider_name": item.get("insurer_name"),
                "service_provider_description": None,
                "service_provider_logo": item.get("insurer_logo"),
                "service_provider_email": None,
                "service_provider_status": None,
                "sp_status": None,
                "risks": (
                    self._fetch_policy_risks(item.get("policy_base_id"))
                    if item.get("policy_base_id")
                    else []
                ),
                "risk_type_id": item.get("risk_type_id"),
                "risk_type_name": item.get("risk_type_title"),
                "risk_details_form_id": None,
                "coverage_type_id": item.get("coverage_type_id"),
                "coverage_type_name": item.get("coverage_type_name"),
                "coverage_details": None,
                "coverage_details_name": None,
                "sum_insured": item.get("sum_insured"),
                "total_amount": item.get("premium_amount"),
                "premium_amount": item.get("premium_amount"),
                "payment_mode_id": None,
                "payment_mode_name": None,
                "product_id": item.get("product_id"),
                "product_name": item.get("product_name"),
                "received_date": item.get("start_date"),
                "quotation_issued_date": None,
                "expiry_date": item.get("end_date"),
                "quotation_expiry_date": None,
                "policy_start_date": item.get("start_date"),
                "policy_expiry_date": item.get("end_date"),
                "request_by_id": item.get("request_by_id"),
                "request_by_name": item.get("requested_by_display_name"),
                "customer_id": item.get("customer_id"),
                "customer_name": (
                    item.get("customer", {}).get("name")
                    if item.get("customer")
                    else None
                ),
                "customer_logo": (
                    item.get("customer", {}).get("logo")
                    if item.get("customer")
                    else None
                ),
                "customer_email": (
                    item.get("customer", {}).get("email")
                    if item.get("customer")
                    else None
                ),
                "customer_address": (
                    item.get("customer", {}).get("address")
                    if item.get("customer")
                    else None
                ),
                "customer_primary_contact": (
                    item.get("customer", {}).get("primary_contact")
                    if item.get("customer")
                    else None
                ),
                "approval_status": None,
                "approved_user": None,
                "approval_role": None,
                "approval_level": None,
                "approval_remarks": None,
                "approval_date": None,
                "quotation_document": None,
                "quotation_document_name": None,
                "quotation_document_size": None,
                "policy_document": None,
                "policy_document_name": None,
                "policy_document_size": None,
                "form_submission_id": None,
                "by_user_id": None,
                "attribute_id": None,
                "vendor_quotation_id": None,
                "send_quotation_id": None,
                "property_id": None,
                "property_name": None,
                "property_description": None,
                "version": None,
                "is_received": None,
                "is_shortlisted": None,
                "is_draft": None,
                "is_sent": None,
                "is_policy": True,
            }
        )

        # Ensure proper field mapping for consistency
        self._ensure_field_consistency(policy_request)

        return policy_request

    def _fetch_request_policy_data(self, opportunity_id):
        return QueryBuilderService("crmp_request_policies as rp")\
            .leftJoin("crmp_policy_base as policy_base", "policy_base.id", "rp.policy_base_id")\
            .leftJoin("crmp_coverage_types as coverage", "coverage.id", "policy_base.coverage_type_id")\
            .leftJoin("crmp_payment_plans as payment", "payment.id", "policy_base.payment_mode_id")\
            .leftJoin("core_vendor_products as product", "product.id", "policy_base.product_id")\
            .leftJoin("core_service_providers as insurer", "insurer.id", "policy_base.insurer_id")\
            .leftJoin("core_users as requester", "requester.id", "policy_base.request_by_id")\
            .leftJoin("crmp_request_types as request_type", "request_type.id", "policy_base.request_type_id")\
            .leftJoin("core_customers as customer", "customer.id", "policy_base.customer_id")\
            .leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")\
            .leftJoin("core_status as status", "status.id", "rp.status_id")\
            .select(
                "rp.id AS id",                               # request policy id
                "policy_base.id AS policy_base_id",          # ✅ correct
                "rp.policy_request_id AS code",
                "policy_base.lead_id AS opportunity_id",

                "rp.policy_request_id as notes",
                "policy_base.quotation_notes as quotation_notes",
                "policy_base.request_type_id",
                "request_type.name AS request_type_name",
                "policy_base.insurer_id",
                "insurer.name AS insurer_name",
                "insurer.description AS insurer_notes",
                "insurer.id AS service_provider_id",
                "insurer.name AS service_provider_name",
                "insurer.description AS service_provider_description",
                "insurer.logo AS service_provider_logo",
                "insurer.email AS service_provider_email",
                "insurer.status_id AS service_provider_status",
                "policy_base.risk_type_id",
                "policy_base.risk_details_form_id",
                "policy_base.coverage_type_id",
                "coverage.name AS coverage_type_name",
                "policy_base.sum_insured",
                "policy_base.premium_amount AS total_amount",
                "policy_base.premium_amount AS premium_amount",
                "policy_base.payment_mode_id",
                "payment.name AS payment_mode_name",

                "policy_base.product_id",
                "product.name AS product_name",

                "rp.policy_request_date AS received_date",
                "policy_base.quotation_issued_date AS quotation_issued_date",
                "policy_base.quotation_expiry_date AS expiry_date",
                "policy_base.quotation_expiry_date AS quotation_expiry_date",
                "policy_base.policy_start_date AS policy_start_date",
                "policy_base.policy_expiry_date AS policy_expiry_date",

                "policy_base.request_by_id",
                "requester.display_name AS request_by_name",

                "policy_base.customer_id",
                "customer.name AS customer_name",
                "customer.logo AS customer_logo",
                "customer_contact.email AS customer_email",
                "customer_contact.address AS customer_address",
                "customer_contact.primary_contact AS customer_primary_contact",
                "policy_base.quotation_document AS coverage_details",
                "policy_base.quotation_document_name AS coverage_details_name",
                "policy_base.quotation_document AS quotation_document",
                "policy_base.quotation_document_name AS quotation_document_name",
                "policy_base.quotation_document_size AS quotation_document_size",
                "TRUE AS is_policy"
            )\
            .where("policy_base.lead_id", opportunity_id)\
            .orderBy("rp.id", "desc")\
            .first()
        

    def _fetch_policy_risks(self, policy_base_id):
        """Fetch comprehensive risk details for a policy from crmp_policy_risk_config"""
        return (
            QueryBuilderService("crmp_policy_risk_config as prc")
            .leftJoin(
                "crm_risk_submissions as rs", "rs.id", "prc.risk_submission_id"
            )
            .leftJoin(
                "crm_risks as r", "r.id", "rs.risk_id"
            )
            .leftJoin(
                "crm_opportunity_types as ot", "ot.id", "r.risk_type_id"
            )
            .select(
                "prc.id",
                "prc.policy_base_id",
                "prc.risk_submission_id",
                "rs.risk_id",
                "rs.submission_id",
                "r.code AS risk_code",
                "r.risk_type_id",
                "ot.title AS risk_type_name",
                "ot.description AS risk_type_description",
            )
            .where("prc.policy_base_id", policy_base_id)
            .orderBy("prc.id", "asc")
            .get()
        )

    def _ensure_field_consistency(self, policy_request):
        """Ensure proper field mapping for consistency"""
        if policy_request.get("quotation_notes") and not policy_request.get("notes"):
            policy_request["notes"] = policy_request["quotation_notes"]
        if policy_request.get("service_provider_id") and not policy_request.get(
            "insurer_id"
        ):
            policy_request["insurer_id"] = policy_request["service_provider_id"]
        if policy_request.get("service_provider_name") and not policy_request.get(
            "insurer_name"
        ):
            policy_request["insurer_name"] = policy_request["service_provider_name"]

    def get_approved_policies_with_details(self, request):
        """Main method to get request policies with details - structured like opportunities"""
        fields = request.GET.get("fields", None)
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))

        # Build and execute request policy query
        query = self._build_approved_policy_query(fields)
        query = query.select(*self._get_base_columns(fields))
        query = self._apply_filters(query, request)

        data = self._execute_approved_policy_query(query, request)

        # Process additional fields (similar to opportunities)
        data = self._process_additional_fields(data, fields)

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    def _fetch_quotation_data_by_opportunity(self, opportunity_id):
        """Fetch quotation data by following the chain from opportunity_id"""
        try:
            # Step 1: Get quotation_id and quotation_code from crmq_quotations table
            quotation_data = QueryBuilderService("crmq_quotations as q")\
                .select("q.id AS quotation_id", "q.code AS quotation_code")\
                .where("q.opportunity_id", opportunity_id)\
                .first()
            
            if not quotation_data:
                return None
            
            quotation_id = quotation_data.get("quotation_id")
            quotation_code = quotation_data.get("quotation_code")
            print("quotation_id", quotation_id)

            status_data = QueryBuilderService("core_status as status")\
                .select("status.id AS status_id")\
                .where("status.type", "quotation_confirmed")\
                .where("status.module", "quotation")\
                .first()
            
            if not status_data:
                print(f"No status found for quotation_confirmed in quotation module")
                return None
            
            status_id = status_data.get("status_id")
            print("status_id", status_id)
            # Step 2: Check crmq_quotation_service_providers for status = 3
            service_provider_data = QueryBuilderService("crmq_quotation_service_providers as qsp")\
                .select("qsp.id AS service_provider_id")\
                .where("qsp.quotation_id", quotation_id)\
                .where("qsp.status", status_id)\
                .first()
            
            if not service_provider_data:
                return None
            
            service_provider_id = service_provider_data.get("service_provider_id")
            print("service_provider_id", service_provider_id)
            # Step 3: Get vendor_quotation_id from crmq_quotation_vendor_quotations
            vendor_quotation_data = QueryBuilderService("crmq_quotation_vendor_quotations as qvq")\
                .select("qvq.send_quotation_id")\
                .where("qvq.vendor_quotation_id", service_provider_id)\
                .first()
            print("vendor_quotation_data", vendor_quotation_data)
            if not vendor_quotation_data:
                return None
            
            
            
            send_quotation_id = vendor_quotation_data.get("send_quotation_id")
            
            # Step 4: Get coverage details from crmq_vendor_response table
            coverage_data = QueryBuilderService("crmq_vendor_response as vr")\
                .select(
                    "vr.coverage_details",
                    "vr.coverage_details_type", 
                    "vr.coverage_details_name"
                )\
                .where("vr.quotation_id", quotation_id)\
                .where("vr.vendor_quotation_id", service_provider_id)\
                .first()
            
            # Step 5: Get generated_pdf and version from crmq_send_quotations
            final_data = QueryBuilderService("crmq_send_quotations as sq")\
                .select(
                    "sq.generated_pdf",
                    "sq.version"
                )\
                .where("sq.id", send_quotation_id)\
                .first()
            
            if final_data:
                # Add quotation_id and quotation_code to the response
                final_data["quotation_id"] = quotation_id
                final_data["quotation_code"] = quotation_code
                
                # Add coverage details from vendor response
                if coverage_data:
                    final_data["coverage_details"] = coverage_data.get("coverage_details")
                    final_data["coverage_details_type"] = coverage_data.get("coverage_details_type")
                    final_data["coverage_details_name"] = coverage_data.get("coverage_details_name")
                else:
                    final_data["coverage_details"] = None
                    final_data["coverage_details_type"] = None
                    final_data["coverage_details_name"] = None
                
                return final_data
            
            return None
            
        except Exception as e:
            print(f"Error fetching quotation data: {str(e)}")
            return None


# Initialize the service
opportunity_policy_service = OpportunityPolicyService()
approved_policy_service = ApprovedPolicyService()


class QualifiedOpportunityService:
    """Service class to handle opportunities with basic filtering, excluding policy base used ones"""

    def get_qualified_opportunities(self, request):
        """Get opportunities filtered by customer_id, stage, stage_id, and lead_id"""
        customer_id = request.GET.get("customer_id", None)
        stage = request.GET.get("stage", None)
        stage_id = request.GET.get("stage_id", None)
        lead_id = request.GET.get("lead_id", None)
        fields = request.GET.get("fields", None)
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "oppo.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        try:
            # Build base query for opportunities
            query = self._build_opportunity_query(fields)
            
            # Apply basic filters
            if customer_id:
                query = query.where("oppo.customer_id", customer_id)
            
            if stage:
                query = query.where("stage.type", stage)
            
            if stage_id:
                query = query.where("oppo.stage_id", stage_id)
            
            if lead_id:
                query = query.where("oppo.id", lead_id)
            
            # Exclude opportunities used in other tables
            query = self._exclude_used_opportunities(query)

            # Get distinct opportunity count (same filters, minimal joins so one row per opportunity)
            total_distinct = self._get_distinct_opportunity_count(
                customer_id=customer_id,
                stage=stage,
                stage_id=stage_id,
                lead_id=lead_id,
            )

            # Execute query with pagination
            data = query.paginate(
                page,
                limit,
                ["oppo.code", "oppo.id"],
                sort_by,
                sort_dir
            )

            # Deduplicate by opportunity id (joins on quotations/service_providers can duplicate rows)
            if isinstance(data, dict) and "data" in data and data["data"]:
                seen_ids = set()
                unique_data = []
                for row in data["data"]:
                    oid = row.get("id") if isinstance(row, dict) else None
                    if oid is not None and oid not in seen_ids:
                        seen_ids.add(oid)
                        unique_data.append(row)
                data["data"] = unique_data

            # Use distinct count for total and last_page
            if isinstance(data, dict) and total_distinct is not None:
                data["total_records"] = total_distinct
                data["last_page"] = (total_distinct // limit) + (1 if total_distinct % limit > 0 else 0) if limit else 1

            # Process additional fields if requested
            if fields == "additional" and isinstance(data, dict) and "data" in data:
                items = data["data"]
                for item in items:
                    if isinstance(item, dict):
                        self._process_additional_fields(item)

            return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

        except Exception as e:
            print(f"Error fetching opportunities: {str(e)}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", 
                {"error": str(e)}, 
                "Failed to fetch opportunities"
            )

    def _build_opportunity_query(self, fields=None):
        """Build the base query for opportunities"""
        query = (
            QueryBuilderService("crm_opportunities as oppo")
            .leftJoin("core_users", "core_users.id", "oppo.sales_agent_id")
            .leftJoin("crm_opportunity_health as health", "health.id", "oppo.current_health_id")
            .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")
            .leftJoin("core_currencies as curr", "curr.id", "oppo.currency_id")
            .leftJoin("core_channels as ch", "ch.id", "oppo.channel_id")
            .leftJoin("core_contacts as contact", "contact.id", "oppo.contact_id")
            .leftJoin("core_customers as customer", "customer.id", "oppo.customer_id")
            .leftJoin("core_contacts as customer_contact", "customer_contact.id", "customer.primary_contact_id")
            .leftJoin("crmq_quotations as q", "q.opportunity_id", "oppo.id")
            # Join quotation service providers to get service_provider_id
            .leftJoin("crmq_quotation_service_providers as qsp", "qsp.quotation_id", "q.id")
            # Join core_product_vendor_products to map product_id (core product) to vendor_product_id
            # oppo.product_id is from core_products table, so we map it to vendor_products via cpvp
            .leftJoin("core_product_vendor_products as cpvp", "cpvp.product_id", "oppo.product_id")
            # Join core_vendor_products via product mapping (oppo.product_id -> cpvp.product_id -> cpvp.vendor_product_id -> vp.id)
            .leftJoin("core_vendor_products as vp", "vp.id", "cpvp.vendor_product_id")
            .leftJoin("core_products as cp", "cp.id", "oppo.product_id")
            .leftJoin("core_product_groups as cpgp", "cpgp.id", "oppo.product_group_id")
        )

        # Base select fields
        select_fields = [
            "oppo.*",
            "core_users.display_name AS sales_agent_name",
            "core_users.picture AS sales_agent_picture",
            "stage.name AS stage_name",
            "stage.type AS stage_type",
            "stage.color AS stage_color",
            "curr.name AS currency_name",
            "curr.symbol AS currency_symbol",
            "ch.name AS channel_name",
            "health.health AS current_health",
            "contact.name AS contact_name",
            "contact.email AS contact_email",
            "contact.primary_contact AS primary_contact",
            "customer.name AS customer_name",
            "customer.logo AS customer_logo",
            "customer.type AS customer_type",
            "customer_contact.email AS customer_primary_contact_email",
            "customer_contact.address AS customer_primary_contact_address",
            "customer_contact.primary_contact AS customer_primary_contact_number",
            # Get insurer_product_id: use vendor_product that matches service_provider_id
            "(CASE WHEN vp.id IS NOT NULL AND vp.vendor_id = qsp.service_provider_id THEN vp.id ELSE NULL END) AS insurer_product_id",
            "(CASE WHEN vp.id IS NOT NULL AND vp.vendor_id = qsp.service_provider_id THEN vp.name ELSE NULL END) AS insurer_product_name",
            "cpgp.name AS product_group_name",
            "cp.name AS product_name",
        ]

        # Add additional select fields for contact and customer IDs
        if fields == "additional":
            select_fields.extend([
                "contact.id AS contact_id",
                "customer.id AS customer_id",
            ])

        return query.select(*select_fields)

    def _get_distinct_opportunity_count(self, customer_id=None, stage=None, stage_id=None, lead_id=None):
        """Count distinct opportunities with same filters (minimal joins so one row per opportunity)."""
        try:
            query = (
                QueryBuilderService("crm_opportunities as oppo")
                .leftJoin("crm_opportunity_statuses as stage", "stage.id", "oppo.stage_id")
                .select("oppo.id")
            )
            if customer_id:
                query = query.where("oppo.customer_id", customer_id)
            if stage:
                query = query.where("stage.type", stage)
            if stage_id:
                query = query.where("oppo.stage_id", stage_id)
            if lead_id:
                query = query.where("oppo.id", lead_id)
            query = self._exclude_used_opportunities(query)
            return query.count()
        except Exception as e:
            print(f"Error getting distinct opportunity count: {str(e)}")
            return None

    def _exclude_used_opportunities(self, query):
        """Exclude opportunities that are used in crmp_policy_base table only"""
        try:
            # Get opportunity IDs used in policy base (as lead_id)
            used_in_policy_base = QueryBuilderService("crmp_policy_base")\
                .select("lead_id")\
                .whereNotNull("lead_id")\
                .get()
            
            # Collect used opportunity IDs
            used_opportunity_ids = set()
            
            # Add IDs from policy base
            for item in used_in_policy_base:
                if item.get("lead_id"):
                    used_opportunity_ids.add(item["lead_id"])
            
            # Exclude used opportunities from the query
            if used_opportunity_ids:
                query = query.whereNotIn("oppo.id", list(used_opportunity_ids))
            
            return query
            
        except Exception as e:
            print(f"Error excluding used opportunities: {str(e)}")
            # Return original query if there's an error
            return query

    def _process_additional_fields(self, item):
        """Process additional fields for opportunities"""
        opportunity_id = item.get("id")
        issued_policy_id = item.get("issued_policy_id")
        print(f"Error excluding used issued_policies: {str(issued_policy_id)}")
        # Process contact data
        self._process_contact_data(item)
        
        # Process customer data
        self._process_customer_data(item)
        
        # Process lead risks
        self._process_lead_risks(item, opportunity_id)
        
        # Process next task
        self._process_next_task(item, opportunity_id)
        
        # Process quotations
        self._process_quotations(item, opportunity_id)
        # Process issued_policy
        self._process_policies(item, issued_policy_id)

    def _process_contact_data(self, item):
        """Process contact data"""
        item["contact"] = {
            "id": item.get("contact_id"),
            "name": item.get("contact_name"),
            "primary_contact": item.get("primary_contact"),
        }

    def _process_customer_data(self, item):
        """Process customer data"""
        item["customer"] = {
            "id": item.get("customer_id"),
            "name": item.get("customer_name"),
            "logo": item.get("customer_logo"),
            "customer_type": item.get("customer_type"),
            "email": item.get("customer_primary_contact_email"),
            "address": item.get("customer_primary_contact_address"),
            "primary_contact": item.get("customer_primary_contact_number"),
        }

    def _process_lead_risks(self, item, opportunity_id):
        """Process lead risks data"""
        if opportunity_id:
            risks = self._fetch_lead_risks(opportunity_id)
            item["lead_risks"] = risks
        else:
            item["lead_risks"] = []

    def _fetch_lead_risks(self, opportunity_id):
        """Fetch lead risks for an opportunity"""
        try:
            risks = (
                QueryBuilderService("crm_oppor_opportunity_types as policy_risk")
                .leftJoin("crm_opportunity_types as risk", "risk.id", "policy_risk.opportunity_type_id")
                .select(
                    "policy_risk.opportunity_type_id AS risk_type_id",
                    "risk.title AS risk_type_name"
                )
                .where("policy_risk.opportunity_id", opportunity_id)
                .get()
            )
            return risks if risks else []
        except Exception as e:
            print(f"Error fetching lead risks: {str(e)}")
            return []

    def _process_next_task(self, item, opportunity_id):
        """Process next task data"""
        if opportunity_id:
            task = self._fetch_next_task(opportunity_id)
            item["next_task"] = task
        else:
            item["next_task"] = None

    def _fetch_next_task(self, opportunity_id):
        """Fetch next task for an opportunity"""
        try:
            task = (
                QueryBuilderService("crm_opportunity_tasks as ot")
                .leftJoin("core_tasks as task", "task.id", "ot.task_id")
                .leftJoin("core_users as user", "user.id", "task.assigned_to_id")
                .leftJoin("core_task_status as status", "status.id", "task.task_status_id")
                .select(
                    "task.id",
                    "task.task",
                    "task.start_date",
                    "user.display_name AS assigned_user_name",
                    "user.picture AS assigned_user_picture"
                )
                .where("ot.opportunity_id", opportunity_id)
                .where("status.type", "pending")
                .orderBy("task.start_date", "asc")
                .first()
            )
            return task if task else None
        except Exception as e:
            print(f"Error fetching next task: {str(e)}")
            return None

    def _process_quotations(self, item, opportunity_id):
        """Process quotations data"""
        print("Processing quotations data for opportunity_id:", opportunity_id)
        if opportunity_id:
            quotations = self._fetch_quotations(opportunity_id)
            item["quotations"] = quotations
        else:
            item["quotations"] = []

    def _fetch_quotations(self, opportunity_id):
        """Fetch quotations for an opportunity"""
        try:
            quotations = (
                QueryBuilderService("crmq_quotations as q")
                .select(
                    "q.*",
                )
                .where("q.opportunity_id", opportunity_id)
                .orderBy("q.id", "desc")
                .get()
            )
            
            # Add vendor response data for each quotation
            if quotations:
                for quotation in quotations:
                    quotation_id = quotation.get("id")
                    if quotation_id:
                        # Get confirmed vendor response for this quotation
                        vendor_response = self._fetch_confirmed_vendor_response(quotation_id)
                        quotation["crmq_vendor_response"] = vendor_response
                    else:
                        quotation["crmq_vendor_response"] = None
            
            return quotations if quotations else []
        except Exception as e:
            print(f"Error fetching quotations: {str(e)}")
            return []

    def _fetch_confirmed_vendor_response(self, quotation_id):
        """Fetch confirmed vendor response for a quotation"""
        try:
            vendor_response = (
                QueryBuilderService("crmq_vendor_response as vr")
                .leftJoin("crmq_quotation_service_providers as qsp", "qsp.id", "vr.vendor_quotation_id")
                .leftJoin("core_service_providers as sp", "sp.id", "qsp.service_provider_id")
                .select(
                    "vr.*",
                    "sp.name as service_provider_name",
                    "sp.logo as service_provider_logo"
                )
                .where("vr.quotation_id", quotation_id)
                .where("vr.status", "CONFIRMED")  # CONFIRMED status
                .orderBy("vr.id", "desc")
                .first()
            )
            return vendor_response if vendor_response else None
        except Exception as e:
            print(f"Error fetching confirmed vendor response: {str(e)}")
            return None

    def _fetch_policy_base_data(self, policy_base_id):
        """Fetch policy base data for an issued policy"""
        try:
            policy_base = (
                QueryBuilderService("crmp_policy_base as pb")
                .leftJoin("crm_opportunity_types as risk_type", "risk_type.id", "pb.risk_type_id")
                .leftJoin("core_service_providers as insurer", "insurer.id", "pb.insurer_id")
                .leftJoin("core_customers as customer", "customer.id", "pb.customer_id")
                .leftJoin("core_vendor_products as product", "product.id", "pb.product_id")
                .leftJoin("crmp_coverage_types as coverage_type", "coverage_type.id", "pb.coverage_type_id")
                .leftJoin("crmp_payment_plans as payment_plan", "payment_plan.id", "pb.payment_mode_id")
                .leftJoin("crmp_request_types as request_type", "request_type.id", "pb.request_type_id")
                .leftJoin("core_users as request_by", "request_by.id", "pb.request_by_id")
                .leftJoin("core_product_groups as product_group", "product_group.id", "pb.product_group_id")
                .select(
                    "pb.*",
                    "risk_type.title AS risk_type_name",
                    "insurer.name AS insurer_name",
                    "insurer.logo AS insurer_logo",
                    "customer.name AS customer_name",
                    "product.name AS product_name",
                    "coverage_type.name AS coverage_type_name",
                    "payment_plan.name AS payment_plan_name",
                    "request_type.name AS request_type_name",
                    "request_by.display_name AS request_by_name",
                    "product_group.name AS product_group_name"
                )
                .where("pb.id", policy_base_id)
                .first()
            )
            return policy_base if policy_base else None
        except Exception as e:
            print(f"Error fetching policy base data: {str(e)}")
            return None


    def _process_policies(self, item, issued_policy_id):
        """Process policies data"""
        print("Processing policies data for opportunity_id:", issued_policy_id)
        if issued_policy_id:
            policies = self._fetch_policies(issued_policy_id)
            # Add policy_base data to each policy
            for policy in policies:
                policy_base_id = policy.get("policy_base_id")
                if policy_base_id:
                    policy_base_data = self._fetch_policy_base_data(policy_base_id)
                    policy["policy_base"] = policy_base_data
                else:
                    policy["policy_base"] = None
            item["issued_policies"] = policies
        else:
            item["issued_policies"] = []

    def _fetch_policies(self, issued_policy_id):
        """Fetch policies for an opportunity"""
        try:
            policies = (
                QueryBuilderService("crmp_issued_policies as p")
                .select(
                    "p.*",
                )
                .where("p.id", issued_policy_id)
                .orderBy("p.id", "desc")
                .get()
            )
            return policies if policies else []
        except Exception as e:
            print(f"Error fetching policies: {str(e)}")
            return []


# Initialize the qualified opportunity service
qualified_opportunity_service = QualifiedOpportunityService()


@csrf_exempt
@api_view(["GET"])
def get_opportunities_with_policy_details(request):
    """Get opportunities with policy details in a structured way"""
    return opportunity_policy_service.get_opportunities_with_policy_details(request)


@csrf_exempt
@api_view(["GET"])
def get_qualified_opportunities(request):
    """Get opportunities filtered by customer_id and stage"""
    return qualified_opportunity_service.get_qualified_opportunities(request)


@csrf_exempt
@api_view(["GET"])
def get_approved_policies_with_details(request):
    """Get approved policies with details in a structured way"""
    return approved_policy_service.get_approved_policies_with_details(request)


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


def _fetch_policy_risk_types(policy_base_id):
    """Fetch risk types associated with a policy from crmp_policy_base_risk_types"""
    print(f"Fetching risk types for policy_base_id: {policy_base_id}")
    result = (
        QueryBuilderService("crmp_policy_base_risk_types as pbrt")
        .leftJoin(
            "crm_opportunity_types as ot", "ot.id", "pbrt.risk_type_id"
        )
        .select(
            "ot.id AS risk_type_id",
            "ot.title AS risk_type_name",
            "ot.description AS risk_type_description",
        )
        .where("pbrt.policy_base_id", policy_base_id)
        .groupBy("ot.id", "ot.title", "ot.description")
        .orderBy("ot.id", "asc")
        .get()
    )
    print(f"Risk types result: {result}")
    return result


def _fetch_customer_data(customer_id):
    """Fetch customer data with contact information"""
    try:
        customer_data = (
            QueryBuilderService("core_customers as customer")
            .leftJoin("core_contacts as contact", "contact.id", "customer.primary_contact_id")
            .select(
                "customer.id",
                "customer.code",
                "customer.name",
                "customer.type",
                "customer.logo",
                "customer.remarks",
                "customer.primary_contact_id",
                "contact.name AS contact_name",
                "contact.email AS contact_email",
                "contact.primary_contact AS contact_primary_contact",
                "contact.address AS contact_address",
                "contact.picture AS contact_picture"
            )
            .where("customer.id", customer_id)
            .first()
        )
        return customer_data if customer_data else None
    except Exception as e:
        print(f"Error fetching customer data: {str(e)}")
        return None


def get_all_issued_policies(request, policy_id=None):
    columns = [
        "crmp_issued_policies.*",
        "crmp_issued_policies.id AS policy_id",
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
        "customers.type as customer_type",
        "products.name as product",
        "request_policy.policy_request_id as policy_request_code",
        "request_policy.id as policy_request_id",
        "request_policy.policy_request_date",
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
        "sales_agent.display_name AS sales_agent_name",
        "account_manager.display_name AS account_manager",
        "entity.created_at AS created_at",
        "entity.updated_at AS updated_at",
        "invoices.invoice_number AS invoice_number ",
        "invoices.paid_amount AS settled_amount ",
        "(COALESCE(crmp_issued_policies.premium_amount, 0) - COALESCE(invoices.paid_amount, 0)) AS pending_amount ",
        "status.name AS status_name",
        "status.color AS status_color",
        "status.type AS status_type",
        "status.id AS status_id",
        "policy_base.id AS policy_base_id",

        
    ]

    query = (
        QueryBuilderService("crmp_issued_policies")
        .select(*columns)
        .leftJoin(
            "crmp_policy_base as policy_base",
            "policy_base.id",
            "crmp_issued_policies.policy_base_id",
        ).leftJoin(
            "crmp_request_policies as request_policy",
            "request_policy.policy_base_id",
            "crmp_issued_policies.policy_base_id",
        )
        .leftJoin(
            "core_status as status",
            "status.id",
            "policy_base.status_id",
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
        .leftJoin(
            "core_vendor_products as products", "products.id", "policy_base.product_id"
        )
        # Added request policy related joins
        .leftJoin(
            "core_users as request_by", "request_by.id", "policy_base.request_by_id"
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
        .leftJoin("core_users as sales_agent", "sales_agent.id", "policy_base.sales_agent_id")
        .leftJoin("core_users as account_manager", "account_manager.id", "policy_base.account_manager_id")
        .leftJoin(
            "(SELECT issued_policy_id, MIN(invoice_number) as invoice_number, SUM(paid_amount) as paid_amount, SUM(outstanding_amount) as outstanding_amount FROM crmf_invoices GROUP BY issued_policy_id) as invoices",
            "invoices.issued_policy_id",
            "crmp_issued_policies.id",
        )
    )

    # Only fetch credit_age if we have a specific policy_id
    credit_period_days = None
    if policy_id:
        data = (
            QueryBuilderService("crmp_issued_policies")
            .select("crmp_issued_policies.credit_period_days","crmp_issued_policies.start_date","crmp_issued_policies.end_date","crmp_issued_policies.policy_effective_date")
            .where("crmp_issued_policies.id", policy_id)
            .first()
        )

        credit_period_days = data.get("credit_period_days") if data else None
        start_date = data.get("start_date") if data else None
        end_date = data.get("end_date") if data else None
        policy_effective_date = data.get("policy_effective_date") if data else None
        print("start_date",start_date)
        print("end_date",end_date)
        print("policy_effective_date",policy_effective_date)
        print("credit_period_days value", credit_period_days,start_date)

        today = datetime.now().date()
        
        # Convert dates to datetime.date if strings or datetimes
        def _to_date(value):
            if value is None:
                return None
            if isinstance(value, str):
                try:
                    return datetime.strptime(value, "%Y-%m-%d").date()
                except Exception:
                    return None
            if isinstance(value, datetime):
                return value.date()
            return value

        start_date = _to_date(start_date)
        end_date = _to_date(end_date)
        policy_effective_date = _to_date(policy_effective_date)
        
        # Choose base date for credit period: prefer end_date, then policy_effective_date, then start_date
        base_date = end_date or policy_effective_date or start_date

        # Calculate the last payment date by adding credit_period_days to base_date
        # Only calculate if credit_period_days is not None
        if credit_period_days is not None and base_date is not None:
            last_payment_date = base_date + timedelta(days=credit_period_days)
            
            credit_age = 0
            if today > last_payment_date:
                credit_age = (today - last_payment_date).days
                print("credit_age", credit_age)
            else:
                credit_age = 0
                print("credit_age", credit_age)
        else:
            credit_age = 0
            print("credit_age", credit_age, "- credit_period_days or start_date is None")


    if policy_id:
        request_policy_data = QueryBuilderService("crmp_request_policies as request_policy_alt")\
             .leftJoin(
               "crmp_issued_policies","crmp_issued_policies.policy_request_id",
               "request_policy_alt.id",
            )\
            .select("request_policy_alt.*")\
            .where("crmp_issued_policies.id", policy_id)\
            .first()
        print("request_policy_data", request_policy_data)
        data = query.where("crmp_issued_policies.id", policy_id).first()
        if not data:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        _format_date_fields(data)
        data["credit_age"] = credit_age
        # Expose system-calculated last payment date (due date) for UI visibility
        try:
            data["last_payment_date"] = last_payment_date.strftime("%Y-%m-%d") if isinstance(last_payment_date, date) else (last_payment_date.isoformat() if last_payment_date else None)
        except Exception:
            data["last_payment_date"] = None
        # Persist credit_age into DB credit_age_days to keep them in sync
        try:
            QueryBuilderService("crmp_issued_policies").where("id", policy_id).update({
                "credit_age_days": credit_age
            })
        except Exception as e:
            print(f"WARNING: Failed to persist credit_age_days for policy {policy_id}: {e}")
        # Reflect updated value in response
        data["credit_age_days"] = credit_age
        data["policy_request"] = request_policy_data

        # Fetch and add risk_types
        policy_base_id = data.get("policy_base_id")
        if policy_base_id:
            risk_type_data = _fetch_policy_risk_types(policy_base_id)
            data["risk_types"] = risk_type_data
        else:
            data["risk_types"] = []

        status = {}
        status["id"] = data.get("status_id")
        status["name"] = data.get("status_name")
        status["color"] = data.get("status_color")
        status["type"] = data.get("status_type")
        data["status"] = status
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    # List with filters, pagination
    filter_json = json.loads(request.GET.get("filter", "{}"))
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by ="crmp_issued_policies.id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    
    # Add customer_id filter
    customer_id = request.GET.get("customer_id", None)

    allowed_filters = [
        "products.name",
        "crmp_issued_policies.risk_level",
        "coverage_type.name",
        "sales_agent.display_name",
        "account_manager.display_name",
        "insurer_info_full_name",
        "status.name",
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
        "status.name",
    ]
    sort_columns = [
        "crmp_issued_policies.start_date",
        "products.name",
        "crmp_issued_policies.brokerage_policy_id",
        "coverage_type.name",
        "sales_agent.display_name",
        "account_manager.display_name",
        "status.name",
    ]

    # Exclude draft status policies - filter out policies with status type 'policy_draft' and module 'policy'
    draft_status_id = (
        QueryBuilderService("core_status")
        .select("id")
        .where("type", "policy_draft")
        .where("module", "policy")
        .first()
    )
    
    if draft_status_id:
        query = query.whereNotIn("policy_base.status_id", [draft_status_id.get("id")])
    
    data = query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    )
    
    # Apply customer_id filter if provided
    if customer_id:
        data = data.where("customers.id", customer_id)
    
    data = data.paginate(page, limit, sort_columns, sort_by, sort_dir)
    rows = data.get("data", [])
    for item in rows:
        _format_date_fields(item)
        
        # Calculate and attach credit_age and last_payment_date for list view
        try:
            def _to_date(value):
                if value in [None, "", "null"]:
                    return None
                if isinstance(value, str):
                    try:
                        return datetime.strptime(value, "%Y-%m-%d").date()
                    except Exception:
                        return None
                if isinstance(value, datetime):
                    return value.date()
                return value

            credit_period_days = item.get("credit_period_days")
            start_date = _to_date(item.get("start_date"))
            end_date = _to_date(item.get("end_date"))
            policy_effective_date = _to_date(item.get("policy_effective_date"))
            base_date = end_date or policy_effective_date or start_date

            last_payment_date = None
            credit_age = 0

            if credit_period_days is not None and base_date is not None:
                try:
                    days = int(credit_period_days)
                except Exception:
                    days = 0
                last_payment_date = base_date + timedelta(days=days)
                today = datetime.now().date()
                if today > last_payment_date:
                    credit_age = (today - last_payment_date).days

            item["credit_age"] = credit_age
            item["last_payment_date"] = (
                last_payment_date.strftime("%Y-%m-%d") if last_payment_date else None
            )
            # Persist credit_age into DB credit_age_days
            try:
                if item.get("id") is not None:
                    QueryBuilderService("crmp_issued_policies").where("id", item.get("id")).update({
                        "credit_age_days": credit_age
                    })
            except Exception as e:
                print(f"WARNING: Failed to persist credit_age_days for policy {item.get('id')}: {e}")
            # Reflect updated value in response
            item["credit_age_days"] = credit_age
        except Exception:
            item["credit_age"] = item.get("credit_age_days", 0) or 0
            item["last_payment_date"] = None
            
    data["data"] = rows

    for item in rows:
        status = {}
        status["id"] = item.get("status_id")
        status["name"] = item.get("status_name")
        status["color"] = item.get("status_color")
        status["type"] = item.get("status_type")
        item["status"] = status
        
        # Fetch and add risk_types for each policy
        policy_base_id = item.get("policy_base_id")
        if policy_base_id:
            risk_type_data = _fetch_policy_risk_types(policy_base_id)
            item["risk_types"] = risk_type_data
        else:
            item["risk_types"] = []

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def get_all_issued_policies_simple(request):
    """
    Endpoint to get all issued policies from crmp_issued_policies table
    Includes policy base data and supports additional fields parameter
    """
    try:
        # Get parameters
        base_id = request.GET.get("base_id", None)
        fields = request.GET.get("fields", None)
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        
        # Define columns for issued policies
        issued_policy_columns = [
            "crmp_issued_policies.*",
            "sales_agent.display_name AS sales_agent_name",
        ]
        
        # Define columns for policy base with related data
        policy_base_columns = [
            "policy_base.*",
            "risk_type.title AS risk_type_name",
            "insurer.name AS insurer_name",
            "insurer.logo AS insurer_logo",
            "customer.name AS customer_name",
            "product.name AS product_name",
            "coverage_type.name AS coverage_type_name",
            "payment_plan.name AS payment_plan_name",
            "request_type.name AS request_type_name",
            "request_by.display_name AS request_by_name",
            "product_group.name AS product_group_name"
        ]
        
        # Combine columns
        all_columns = issued_policy_columns + policy_base_columns
        
        # Build query with joins to policy base and related tables
        query = (
            QueryBuilderService("crmp_issued_policies")
            .select(*all_columns)
            .leftJoin(
                "crmp_policy_base as policy_base",
                "policy_base.id",
                "crmp_issued_policies.policy_base_id"
            )
            .leftJoin("crm_opportunity_types as risk_type", "risk_type.id", "policy_base.risk_type_id")
            .leftJoin("core_service_providers as insurer", "insurer.id", "policy_base.insurer_id")
            .leftJoin("core_customers as customer", "customer.id", "policy_base.customer_id")
            .leftJoin("core_vendor_products as product", "product.id", "policy_base.product_id")
            .leftJoin("crmp_coverage_types as coverage_type", "coverage_type.id", "policy_base.coverage_type_id")
            .leftJoin("crmp_payment_plans as payment_plan", "payment_plan.id", "policy_base.payment_mode_id")
            .leftJoin("crmp_request_types as request_type", "request_type.id", "policy_base.request_type_id")
            .leftJoin("core_users as request_by", "request_by.id", "policy_base.request_by_id")
            .leftJoin("core_product_groups as product_group", "product_group.id", "policy_base.product_group_id")
            .leftJoin("core_users as sales_agent", "sales_agent.id", "policy_base.sales_agent_id")
        )
        
        # Apply base_id filter if provided
        if base_id:
            query = query.where("crmp_issued_policies.policy_base_id", base_id)
        
        # Apply pagination
        data = query.paginate(page, limit, ["crmp_issued_policies.id"], "crmp_issued_policies.id", "desc")
        
        # Get the rows from paginated data
        rows = data.get("data", [])
        
        # Process each row
        for item in rows:
            # Format date fields
            _format_date_fields(item)
            # Calculate and attach credit_age and last_payment_date for list view
            try:
                def _to_date(value):
                    if value in [None, "", "null"]:
                        return None
                    if isinstance(value, str):
                        try:
                            return datetime.strptime(value, "%Y-%m-%d").date()
                        except Exception:
                            return None
                    if isinstance(value, datetime):
                        return value.date()
                    return value

                credit_period_days = item.get("credit_period_days")
                start_date = _to_date(item.get("start_date"))
                end_date = _to_date(item.get("end_date"))
                policy_effective_date = _to_date(item.get("policy_effective_date"))
                base_date = end_date or policy_effective_date or start_date

                last_payment_date = None
                credit_age = 0

                if credit_period_days is not None and base_date is not None:
                    try:
                        days = int(credit_period_days)
                    except Exception:
                        days = 0
                    last_payment_date = base_date + timedelta(days=days)
                    today = datetime.now().date()
                    if today > last_payment_date:
                        credit_age = (today - last_payment_date).days

                item["credit_age"] = credit_age
                item["last_payment_date"] = (
                    last_payment_date.strftime("%Y-%m-%d") if last_payment_date else None
                )
                # Persist credit_age into DB credit_age_days
                try:
                    if item.get("id") is not None:
                        QueryBuilderService("crmp_issued_policies").where("id", item.get("id")).update({
                            "credit_age_days": credit_age
                        })
                except Exception as e:
                    print(f"WARNING: Failed to persist credit_age_days for policy {item.get('id')}: {e}")
                # Reflect updated value in response
                item["credit_age_days"] = credit_age
            except Exception:
                item["credit_age"] = item.get("credit_age_days", 0) or 0
                item["last_payment_date"] = None
            
            # If fields=additional is requested, create policy_base object
            if fields == "additional":
                # Create policy_base object with all policy_base fields and related data
                policy_base_data = {}
                policy_base_fields = [
                    "id", "policy_request_id", "customer_id", "product_id", "insurer_id", 
                    "risk_type_id", "request_type_id", "coverage_type_id", "payment_mode_id",
                    "sum_insured", "premium_amount", "policy_start_date", "policy_expiry_date",
                    "quotation_issued_date", "quotation_expiry_date", "quotation_document",
                    "quotation_document_name", "quotation_notes", "product_group_id", "request_by_id"
                ]
                
                # Related data fields
                related_fields = [
                    "risk_type_name", "insurer_name", "insurer_logo", "customer_name", 
                    "product_name", "coverage_type_name", "payment_plan_name", 
                    "request_type_name", "request_by_name", "product_group_name"
                ]
                
                # Extract policy_base fields from the item
                for field in policy_base_fields:
                    if field in item:
                        policy_base_data[field] = item[field]
                
                # Extract related data fields
                for field in related_fields:
                    if field in item:
                        policy_base_data[field] = item[field]
                
                # Add customer object if customer_id exists (at top level)
                customer_id = policy_base_data.get("customer_id")
                if customer_id:
                    customer_data = _fetch_customer_data(customer_id)
                    item["customer"] = customer_data
                
                # Add risk_types array if policy_base_id exists (at top level)
                policy_base_id = policy_base_data.get("id")
                if policy_base_id:
                    risk_types_data = _fetch_policy_risk_types(policy_base_id)
                    item["lead_risks"] = risk_types_data
                
                # Create issued_policies array with the current item and policy_base (without customer and lead_risks)
                issued_policy_item = item.copy()
                # Remove customer and lead_risks from the issued_policy_item to avoid duplication
                if "customer" in issued_policy_item:
                    del issued_policy_item["customer"]
                if "lead_risks" in issued_policy_item:
                    del issued_policy_item["lead_risks"]
                issued_policy_item["policy_base"] = policy_base_data
                item["issued_policies"] = [issued_policy_item]
                
                # Remove policy_base and related fields from the main object (keep policy_base_id for reference)
                all_fields_to_remove = policy_base_fields + related_fields
                for field in all_fields_to_remove:
                    if field in item and field != "id":  # Keep the main id field
                        del item[field]

        # Update the data with processed rows
        data["data"] = rows

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    except Exception as e:
        print(f"Error in get_all_issued_policies_simple: {str(e)}")
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server error")


def update_issued_policy(request, policy_id, renewal=False):
    print(f"DEBUG: update_issued_policy called with policy_id: {policy_id}, renewal: {renewal}")
    
    try:
        data = json.loads(request.body or "{}")
        print(f"DEBUG: Parsed request data: {data}")
        data["remarks"] = data.get("insurer_notes")
        
        # Convert empty strings to None for specific fields
        keys_to_check = ['premium_amount', 'sum_insured', 'quotation_expiry_date',
            'quotation_issued_date', 'payment_mode_id', 'coverage_type_id', 'product_id', 
            'product_group_id', 'insurer_id', 'request_type_id', 'risk_type_id',
            'policy_start_date', 'policy_expiry_date']
        print(f"DEBUG: Converting empty strings to None for keys: {keys_to_check}")
        data = replace_empty_strings_with_none(data, keys_to_check)
        print(f"DEBUG: Data after empty string conversion: {data}")
        
        # Remove credit_age_days from data if provided by user (it will be auto-calculated after update)
        # We don't want users to be able to manually set this value
        if 'credit_age_days' in data:
            print(f"DEBUG: Removing credit_age_days from data")
            del data['credit_age_days']
        
        # Get existing policy data to use as defaults for missing date fields
        print(f"DEBUG: Fetching existing policy data for policy_id: {policy_id}")
        existing_policy = (
            QueryBuilderService("crmp_issued_policies").where("id", policy_id).first()
        )
        print(f"DEBUG: Existing policy data: {existing_policy}")
        
        # Use the actual start_date and end_date from the request data
        print(f"DEBUG: Using dates from request data")
        if "start_date" in data and data["start_date"]:
            print(f"DEBUG: Using start_date from request: {data['start_date']}")
        if "end_date" in data and data["end_date"]:
            print(f"DEBUG: Using end_date from request: {data['end_date']}")
        
        # Only use existing policy dates if the request doesn't have them
        if existing_policy:
            if not data.get("start_date"):
                data["start_date"] = existing_policy.get("start_date")
                print(f"DEBUG: Using existing start_date: {data.get('start_date')}")
            if not data.get("end_date"):
                data["end_date"] = existing_policy.get("end_date")
                print(f"DEBUG: Using existing end_date: {data.get('end_date')}")
        
        print(f"DEBUG: Final data before validation: {data}")
        print(f"DEBUG: Calling ValidatorService.validate with rules")
        
        errors = ValidatorService.validate(data, get_issued_policy_rules_with_request_put())
        print(f"DEBUG: Validation errors: {errors}")
        
        if errors:
            print(f"DEBUG: Returning validation error response")
            return ResponseService.response(
                "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
            )
        
        print(f"DEBUG: Validation passed, proceeding with update")
        
    except Exception as e:
        print(f"ERROR: Exception in update_issued_policy: {str(e)}")
        print(f"ERROR: Exception type: {type(e).__name__}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            {"error": f"Failed to process policy update: {str(e)}"}, 
            "Server error"
        )

    print(f"DEBUG: Attempting to update policy with data: {data}")
    updated = (
        QueryBuilderService("crmp_issued_policies").where("id", policy_id).update(data)
    )
    print(f"DEBUG: Update result: {updated}")
    
    # Auto-calculate and update credit age after update
    print(f"DEBUG: Starting credit age calculation for policy {policy_id}")
    try:
        issued_policy = IssuedPolicy.objects.get(id=policy_id)
        print(f"DEBUG: Found issued policy, updating credit age")
        issued_policy.update_credit_age()
        print(f"✅ Credit age auto-calculated: {issued_policy.credit_age_days} days")
    except IssuedPolicy.DoesNotExist:
        print(f"⚠️ Warning: Could not find issued policy {policy_id} to update credit age")
    except Exception as e:
        print(f"⚠️ Warning: Error updating credit age for policy {policy_id}: {str(e)}")
        print(f"ERROR: Credit age calculation traceback: {traceback.format_exc()}")
    
    print(f"DEBUG: Fetching policy data for entity handling")
    policy_data = (
        QueryBuilderService("crmp_issued_policies").where("id", policy_id).first()
    )
    print(f"DEBUG: Policy data: {policy_data}")
    
    if policy_data and policy_data.get("entity_id") is not None:
        print(f"DEBUG: Handling entity update for entity_id: {policy_data.get('entity_id')}")
        user = request.user if request.user.is_authenticated else None
        entity_id = policy_data.get("entity_id")
        entity_data = {
            "approvel_status": False,
        }
        try:
            handle_entity(entity_data, entity_id=entity_id, user=user)
            print(f"DEBUG: Entity handling completed successfully")
        except Exception as e:
            print(f"ERROR: Entity handling failed: {str(e)}")
            print(f"ERROR: Entity handling traceback: {traceback.format_exc()}")
    else:
        print(f"DEBUG: No entity_id found or policy_data is None, skipping entity handling")

    # Generate/update finance invoice and calculate commissions
    print(f"DEBUG: Handling invoice for policy {policy_id}")
    
    try:
        # Get policy data to extract sales_agent_id
        policy_data = (
            QueryBuilderService("crmp_issued_policies")
            .select("policy_base_id")
            .where("id", policy_id)
            .first()
        )
        
        sales_agent_id = None
        if policy_data and policy_data.get("policy_base_id"):
            policy_base = QueryBuilderService("crmp_policy_base").where("id", policy_data["policy_base_id"]).first()
            if policy_base:
                sales_agent_id = policy_base.get("sales_agent_id")
        
        # Generate/update invoice using finance invoice generation function
        # This will also trigger commission calculation
        print(f"DEBUG: Generating/updating finance invoice for policy {policy_id}")
        invoice_result = generate_invoice_for_issued_policy(
            policy_id, 
            is_update=True, 
            user=user, 
            sales_agent_id=sales_agent_id
        )
        
        if invoice_result:
            print(f"DEBUG: Successfully generated/updated invoice for policy {policy_id}")
            print(f"DEBUG: Invoice ID: {invoice_result}")
        else:
            print(f"WARNING: Invoice generation returned None for policy {policy_id}")
            
    except Exception as e:
        print(f"ERROR: Invoice handling failed: {str(e)}")
        print(f"ERROR: Invoice handling traceback: {traceback.format_exc()}")

    if updated:
        if renewal:
            # Set policy base status to renewed for the old policy
            try:
                from envoy_bu_policy_api.policy.controllers.policy_status_utils import set_policy_base_renewed
                
                # Get policy base ID from the updated policy
                policy_base_id = policy_data.get("policy_base_id")
                if policy_base_id:
                    result = set_policy_base_renewed(policy_base_id)
                    if result.get("success"):
                        print(f"Successfully set policy base {policy_base_id} status to RENEWED for renewal")
                    else:
                        print(f"Warning: Failed to set policy base status to renewed: {result.get('message')}")
                else:
                    print("Warning: No policy_base_id found for renewal status update")
            except Exception as e:
                print(f"Error setting policy base status to renewed: {str(e)}")
            
            entity_data = {
                "type": "policy_inheritance",
                "approvel_status": False,
            }
            new_entity_id = handle_entity(entity_data, entity_id=None, user=user)
            inheritance_fields = ["policy_start_date", "policy_effective_date"]
            inheritance_data = {f: data[f] for f in inheritance_fields if f in data}
            
            # Map request field names to database field names for inheritance
            if "policy_start_date" in inheritance_data:
                inheritance_data["start_date"] = inheritance_data.pop("policy_start_date")
            
            inheritance_data.update(
                {
                    "issued_policy_id": policy_id,
                    "entity_id": new_entity_id,
                }
            )
            QueryBuilderService("crmp_issued_policies_inheritance").insert(
                inheritance_data
            )

        print(f"DEBUG: Update successful, returning success response")
        return ResponseService.response(
            "SUCCESS", updated, "default_update_success_msg"
        )
    print(f"DEBUG: Update failed, returning NOT_FOUND")
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
        "policy_issue_date": "required|date|before_or_equal:policy_start_date",
        "policy_start_date": "required|date",
        "policy_expiry_date": "required|date|after:policy_start_date",
        "premium_amount": "required|numeric",
        "credit_period_days": "required|integer",
        # credit_age_days removed - it's auto-calculated
        "product_id": "nullable|required_without:product_group_id|exists:core_vendor_products,id",
        "product_group_id": "nullable|required_without:product_id|exists:core_product_groups,id",
        "product_type": "required|string|in:product,group",
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


def validate_risk_ids_structure(risk_ids, customer_id, risk_type_ids):
    """
    Validate the risk_ids structure: {"risk_type_id": [risk_id1, risk_id2, ...]}
    
    Args:
        risk_ids: Dictionary with risk_type_ids as keys and arrays of risk_ids as values
        customer_id: Customer ID to validate against
        risk_type_ids: Array of risk_type_ids extracted from the risk_ids object keys
    
    Returns:
        dict: Validation errors if any, empty dict if valid
    """
    errors = {}
    
    # 1. Validate that risk_ids is not null/empty
    if not risk_ids:
        errors["risk_ids"] = ["risk_ids cannot be null or empty"]
        return errors
    
    # 2. Validate that risk_ids is a dictionary
    if not isinstance(risk_ids, dict):
        errors["risk_ids"] = ["risk_ids must be an object/dictionary"]
        return errors
    
    # 3. Validate each risk_type_id and its associated risk_ids
    for risk_type_id_str, risk_id_list in risk_ids.items():
        try:
            risk_type_id = int(risk_type_id_str)
        except (ValueError, TypeError):
            if "risk_ids" not in errors:
                errors["risk_ids"] = []
            errors["risk_ids"].append(f"Invalid risk_type_id key: {risk_type_id_str}")
            continue
        
        # Validate that risk_type_id exists in the database
        risk_type_exists = QueryBuilderService("crm_opportunity_types").where("id", risk_type_id).first()
        if not risk_type_exists:
            if "risk_ids" not in errors:
                errors["risk_ids"] = []
            errors["risk_ids"].append(f"risk_type_id {risk_type_id} does not exist")
            continue
        
        # Validate risk_id_list is not null/empty
        if not risk_id_list:
            if "risk_ids" not in errors:
                errors["risk_ids"] = []
            errors["risk_ids"].append(f"risk_ids for risk_type_id {risk_type_id} cannot be null or empty")
            continue
        
        # Validate that risk_id_list is an array
        if not isinstance(risk_id_list, list):
            if "risk_ids" not in errors:
                errors["risk_ids"] = []
            errors["risk_ids"].append(f"risk_ids for risk_type_id {risk_type_id} must be an array")
            continue
        
        # Validate each risk_id in the list
        for risk_id in risk_id_list:
            try:
                risk_id_int = int(risk_id)
            except (ValueError, TypeError):
                if "risk_ids" not in errors:
                    errors["risk_ids"] = []
                errors["risk_ids"].append(f"Invalid risk_id: {risk_id} for risk_type_id {risk_type_id}")
                continue
            
            # Validate that the risk exists and belongs to the correct customer and risk_type
            risk_exists = QueryBuilderService("crm_risks") \
                .where("id", risk_id_int) \
                .where("customer_id", customer_id) \
                .where("risk_type_id", risk_type_id) \
                .first()
            
            if not risk_exists:
                if "risk_ids" not in errors:
                    errors["risk_ids"] = []
                errors["risk_ids"].append(f"risk_id {risk_id_int} does not exist for customer_id {customer_id} and risk_type_id {risk_type_id}")
    
    return errors


def generate_policy_request_id():
    last = IssuedPolicy.objects.aggregate(Max("id"))["id__max"] or 0
    return f"PN-{last + 1}"


def create_issued_policy(request, _from_request=False, request_id=None):
    """
    Create a new issued policy with comprehensive validation and error handling.
    
    This endpoint supports both risk_ids (new format) and risk_type_ids (legacy format).
    
    Args:
        request: HTTP request object
        _from_request: Boolean indicating if this is created from a request policy
        request_id: ID of the request policy if _from_request is True
    
    Returns:
        ResponseService response with created policy data or error details
    """
    data = json.loads(request.body or "{}")

    if not isinstance(data, dict):
        return ResponseService.response(
            "VALIDATION_ERROR", None, "Invalid data format: Expected JSON object."
        )

    # Store original data for validation before any preprocessing
    original_data = data.copy()
    print(f" DEBUG: Original data for validation: {original_data}")
    
    # Determine draft vs convert-draft-to-issued: respect is_draft=true (draft save); only treat as "convert to issued" when is_draft=false with draft_policy_base_id
    draft_policy_base_id = data.get("draft_policy_base_id")
    is_draft = data.get("is_draft", False) or str(data.get("status", "")).upper() == "DRAFT"
    if draft_policy_base_id and not is_draft:
        # Converting draft to issued policy: run validation and create proper issued policy
        is_draft = False
        print(f" DEBUG: draft_policy_base_id provided ({draft_policy_base_id}) with is_draft=false - converting draft to issued policy")
    elif draft_policy_base_id and is_draft:
        # Updating an existing draft: keep is_draft=true, skip required validation, find policy base and update
        print(f" DEBUG: draft_policy_base_id provided ({draft_policy_base_id}) with is_draft=true - updating existing draft (no required validation)")
    
    # Convert empty strings to None for specific fields
    # For drafts, also include date fields to avoid database errors
    keys_to_check = ['premium_amount', 'sum_insured', 'payment_mode_id', 'coverage_type_id', 'product_id', 
        'product_group_id', 'insurer_id', 'request_type_id', 'risk_type_id', 'lead_id', 'sales_agent_id',
         'account_manager_id', 'quotation_id']
    
    # For drafts, also convert empty date fields to None
    if is_draft:
        keys_to_check.extend(['quotation_expiry_date', 'quotation_issued_date', 'policy_start_date', 'policy_expiry_date'])
    else:
        keys_to_check.extend(['quotation_expiry_date', 'quotation_issued_date'])
    
    print(f" DEBUG: Before replace_empty_strings_with_none - data: {data}")
    print(f" DEBUG: Keys to check for empty strings: {keys_to_check}")
    data = replace_empty_strings_with_none(data, keys_to_check)
    print(f" DEBUG: After replace_empty_strings_with_none - data: {data}")
    
    # Validate and format date fields if provided (for both drafts and non-drafts)
    date_fields = ['policy_start_date', 'policy_expiry_date', 'quotation_issued_date', 'quotation_expiry_date', 'policy_effective_date']
    for date_field in date_fields:
        if date_field in data and data[date_field] is not None and data[date_field] != '':
            try:
                # If it's already a string, try to parse and validate format
                if isinstance(data[date_field], str):
                    # Try to parse the date string to validate format (YYYY-MM-DD)
                    parsed_date = datetime.strptime(data[date_field], '%Y-%m-%d')
                    # Keep as string in YYYY-MM-DD format
                    data[date_field] = parsed_date.strftime('%Y-%m-%d')
                    print(f" DEBUG: Validated and formatted {date_field}: {data[date_field]}")
                elif isinstance(data[date_field], date):
                    # If it's already a date object, convert to string
                    data[date_field] = data[date_field].strftime('%Y-%m-%d')
                    print(f" DEBUG: Converted {date_field} from date object to string: {data[date_field]}")
            except (ValueError, TypeError) as e:
                print(f" DEBUG: Invalid date format for {date_field}: {data[date_field]}, error: {str(e)}")
                # For drafts, invalid dates are set to None, for non-drafts this would have been caught in validation
                if is_draft:
                    data[date_field] = None
                    print(f" DEBUG: Draft mode - setting invalid {date_field} to None")
                else:
                    return ResponseService.response(
                        "VALIDATION_ERROR",
                        {date_field: [f"Invalid date format. Expected YYYY-MM-DD format."]},
                        Error.VALIDATION_ERROR
                    )
    
    # Initialize credit_age_days to 0 (will be auto-calculated after creation)
    # This ensures the database has a value during insertion
    data['credit_age_days'] = 0

    # Handle product_id and product_group_id validation
    product_id = data.get("product_id")
    product_group_id = data.get("product_group_id")
    product_type = data.get("product_type")  # Extract product_type early so it's available for drafts
    
    # Enhanced debug logging for product validation
    print(f"DEBUG: Product validation - product_id: {product_id}, product_group_id: {product_group_id}")
    
    # Validate product_id exists if provided
    if product_id:
        # First check if it's a vendor_product_id (since payload contains vendor_product_id)
        vendor_product_exists = (
            QueryBuilderService("core_vendor_products")
            .where("id", product_id)
            .first()
        )
        
        if vendor_product_exists:
            print(f"DEBUG: Vendor Product ID {product_id} validated successfully in core_vendor_products")
            
            # Get the corresponding core_product_id for reference (but don't change the data)
            vendor_product_mapping = (
                QueryBuilderService("core_product_vendor_products as cpvp")
                .leftJoin("core_products as cp", "cp.id", "cpvp.product_id")
                .select("cpvp.product_id as core_product_id", "cp.name as core_product_name")
                .where("cpvp.vendor_product_id", product_id)
                .whereNotNull("cp.id")
                .first()
            )
            
            if vendor_product_mapping:
                core_product_id = vendor_product_mapping.get("core_product_id")
                print(f"DEBUG: Found mapping - vendor_product_id {product_id} maps to core_product_id {core_product_id} ({vendor_product_mapping.get('core_product_name')})")
                print(f"DEBUG: Storing vendor_product_id {product_id} in policy base")
            else:
                print(f"WARNING: Vendor Product ID {product_id} exists but has no mapping to core_product_id")
        else:
            print(f"WARNING: Product ID {product_id} does not exist in core_vendor_products table")
            print(f"DEBUG: This will cause finance invoice generation to fail")
            # Try to find alternative from product_group if available
            if product_group_id:
                print(f"DEBUG: Attempting to find valid product from product_group {product_group_id}")
                valid_product = (
                    QueryBuilderService("core_product_group_products as cpgp")
                    .leftJoin("core_products as cp", "cp.id", "cpgp.product_id")
                    .select("cpgp.product_id")
                    .where("cpgp.product_group_id", product_group_id)
                    .whereNotNull("cp.id")
                    .first()
                )
                if valid_product:
                    data["product_id"] = valid_product.get("product_id")
                    print(f"DEBUG: Updated product_id to {data['product_id']} from product_group")
                else:
                    print(f"ERROR: No valid products found in product_group {product_group_id}")

    # Set request_type_id based on is_renewal
    is_renewal = data.get("is_renewal", 0)
    data["request_type_id"] = 2 if is_renewal == 1 else 1
    
    # Store original policy_base_id from payload for inheritance logic (before it gets overwritten)
    original_policy_base_id = data.get("policy_base_id")

    # Determine validation rules
    print(f" DEBUG: Determining validation rules - _from_request: {_from_request}")
    rules = (
        get_issued_policy_rules_with_request()
        if _from_request
        else get_issued_policy_rules_without_request()
    )
    print(f" DEBUG: Selected validation rules: {rules}")

    # If from request, get related policy base info
    policy_base_id = None
    if _from_request:
        req = (
            QueryBuilderService("crmp_request_policies")
            .select("crmp_request_policies.*", "crmp_policy_base.premium_amount", 
                   "crmp_policy_base.policy_start_date", "crmp_policy_base.policy_expiry_date",
                   "crmp_policy_base.request_by_id")
            .leftJoin(
                "crmp_policy_base",
                "crmp_request_policies.policy_base_id",
                "crmp_policy_base.id",
            )
            .where("crmp_request_policies.id", request_id)
            .first()
        )

        if not req:
            return ResponseService.response("NOT_FOUND", None, "Request not found.")

        policy_base_id = req.get("policy_base_id")
        data["policy_request_id"] = request_id
        if "premium_amount" not in data:
            data["premium_amount"] = req.get("premium_amount", 0)
        
        # Use policy base dates if not provided in request data
        print(f" DEBUG: _from_request override logic - checking dates")
        print(f" DEBUG: Current data policy_start_date: {data.get('policy_start_date')}")
        print(f" DEBUG: Current data policy_expiry_date: {data.get('policy_expiry_date')}")
        print(f" DEBUG: Request policy_start_date: {req.get('policy_start_date')}")
        print(f" DEBUG: Request policy_expiry_date: {req.get('policy_expiry_date')}")
        
        if not data.get("policy_start_date"):
            data["policy_start_date"] = req.get("policy_start_date")
            print(f" DEBUG: Override applied - policy_start_date set to: {data.get('policy_start_date')}")
        if not data.get("policy_expiry_date"):
            data["policy_expiry_date"] = req.get("policy_expiry_date")
            print(f" DEBUG: Override applied - policy_expiry_date set to: {data.get('policy_expiry_date')}")
        
        print(f" DEBUG: Final data after _from_request overrides: {data}")
        
        # Ensure we have the required fields for invoice generation
        print(f"DEBUG: Policy created from request - policy_base_id: {policy_base_id}")
        print(f"DEBUG: Request data: {req}")
        print(f"DEBUG: Request by ID from request policy: {req.get('request_by_id')}")
        
        # Get additional policy base data to ensure invoice generation has all required fields
        if policy_base_id:
            policy_base_data = (
                QueryBuilderService("crmp_policy_base")
                .select("product_id", "insurer_id", "customer_id", "product_group_id","sum_insured")
                .where("id", policy_base_id)
                .first()
            )
            if policy_base_data:
                print(f"DEBUG: Policy base data for sum insured: {policy_base_data['sum_insured']}")
                print(f"DEBUG: Policy base data for invoice generation: {policy_base_data}")
                # Ensure these fields are available for invoice generation
                if not data.get("product_id") and policy_base_data.get("product_id"):
                    data["product_id"] = policy_base_data.get("product_id")
                if not data.get("insurer_id") and policy_base_data.get("insurer_id"):
                    data["insurer_id"] = policy_base_data.get("insurer_id")
                if not data.get("customer_id") and policy_base_data.get("customer_id"):
                    data["customer_id"] = policy_base_data.get("customer_id")
                if not data.get("product_group_id") and policy_base_data.get("product_group_id"):
                    data["product_group_id"] = policy_base_data.get("product_group_id")
                if not data.get("sum_insured") and policy_base_data.get("sum_insured"):
                    data["sum_insured"] = policy_base_data.get("sum_insured")
        
        # Get policy_effective_date from inheritance table and update it if _from_request is true
        if _from_request and req and req.get("entity_id"):
            request_entity_id = req.get("entity_id")
            print(f"DEBUG: Looking for inheritance record with entity_id: {request_entity_id}")
            
            # Find inheritance record using the request policy's entity_id
            inheritance_record = QueryBuilderService("crmp_issued_policies_inheritance")\
                .select("id", "policy_effective_date")\
                .where("entity_id", request_entity_id)\
                .first()
            
            if inheritance_record:
                inheritance_id = inheritance_record.get("id")
                current_policy_effective_date = inheritance_record.get("policy_effective_date")
                print(f"DEBUG: Found inheritance record with ID: {inheritance_id}")
                print(f"DEBUG: Current policy_effective_date: {current_policy_effective_date}")
                
                # Update the policy_effective_date if provided in the request data
                if "policy_effective_date" in data and data["policy_effective_date"]:
                    update_data = {
                        "policy_effective_date": data["policy_effective_date"]
                    }
                    
                    # Update the inheritance record
                    updated_record = QueryBuilderService("crmp_issued_policies_inheritance")\
                        .where("id", inheritance_id)\
                        .update(update_data)
                    
                    if updated_record:
                        print(f"DEBUG: Successfully updated inheritance record {inheritance_id}")
                        print(f"DEBUG: Updated policy_effective_date to: {data['policy_effective_date']}")
                        
                        # Fetch and print the updated record
                        updated_inheritance = QueryBuilderService("crmp_issued_policies_inheritance")\
                            .select("id", "entity_id", "issued_policy_id", "policy_effective_date", "start_date")\
                            .where("id", inheritance_id)\
                            .first()
                        
                        if updated_inheritance:
                            print(f"DEBUG: Updated inheritance record values:")
                            print(f"  - ID: {updated_inheritance.get('id')}")
                            print(f"  - Entity ID: {updated_inheritance.get('entity_id')}")
                            print(f"  - Issued Policy ID: {updated_inheritance.get('issued_policy_id')}")
                            print(f"  - Policy Effective Date: {updated_inheritance.get('policy_effective_date')}")
                            print(f"  - Start Date: {updated_inheritance.get('start_date')}")
                    else:
                        print(f"DEBUG: Failed to update inheritance record {inheritance_id}")
                else:
                    print(f"DEBUG: No policy_effective_date provided in request data to update")
            else:
                print(f"DEBUG: No inheritance record found for entity_id {request_entity_id}")

    # Let ValidatorService handle validation with original data (before any preprocessing)
    # Skip validation if this is a draft
    if not is_draft:
        print(f" DEBUG: Running ValidatorService validation with original data")
        print(f" DEBUG: Original data for validation: {original_data}")
        print(f" DEBUG: Validation rules: {rules}")
        
        # Validate original data with ValidatorService
        try:
            errors = ValidatorService.validate(original_data, rules)
            print(f" DEBUG: ValidatorService.validate returned errors: {errors}")
            if errors:
                print(f" DEBUG: Validation failed, returning VALIDATION_ERROR")
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
                )
            else:
                print(f" DEBUG: Validation passed, proceeding with policy creation")
        except Exception as e:
            print(f" DEBUG: ValidatorService.validate threw an exception: {str(e)}")
            print(f" DEBUG: Exception type: {type(e)}")
            import traceback
            print(f" DEBUG: Full traceback: {traceback.format_exc()}")
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR", 
                {"error": f"ValidatorService validation failed: {str(e)}"}, 
                Error.INTERNAL_SERVER_ERROR
            )
    else:
        print(f" DEBUG: Draft mode - skipping validation")

    # Convert datetime.date objects to strings for processing (after validation)
    print(f" DEBUG: Converting datetime.date objects to strings for processing")
    try:
        for key, value in data.items():
            if isinstance(value, date):
                data[key] = value.strftime('%Y-%m-%d')
                print(f" DEBUG: Converted {key} from {type(value)} to string: {data[key]}")
        print(f" DEBUG: Conversion completed successfully")
    except Exception as e:
        print(f" DEBUG: Error during datetime conversion: {str(e)}")
        print(f" DEBUG: Exception type: {type(e)}")
        import traceback
        print(f" DEBUG: Full traceback: {traceback.format_exc()}")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            {"error": f"Date conversion failed: {str(e)}"}, 
            Error.INTERNAL_SERVER_ERROR
        )

    # Extract risk_type_ids and validate risk_ids structure (same as request policy)
    # Skip risk validation if _from_request is true OR if this is a draft
    customer_id = data.get("customer_id")
    if not _from_request and not is_draft:
        provided_risk_ids = data.get("risk_ids", {})
        
        # Extract risk_type_ids from the risk_ids object keys (same as request policy)
        if provided_risk_ids and isinstance(provided_risk_ids, dict):
            try:
                # Extract risk_type_ids from the keys of risk_ids object
                risk_type_ids = [int(risk_type_id_str) for risk_type_id_str in provided_risk_ids.keys()]
                data["risk_type_ids"] = risk_type_ids
                
                # Use first risk_type_id for backward compatibility
                if risk_type_ids:
                    data["risk_type_id"] = risk_type_ids[0]
                
                # Log multiple risk types for debugging
                if len(risk_type_ids) > 1:
                    print(f"DEBUG: Multiple risk types detected: {risk_type_ids}")
                    print(f"DEBUG: Using first risk_type_id for backward compatibility: {risk_type_ids[0]}")
                
                # Validate risk_ids structure: {"risk_type_id": [risk_id1, risk_id2, ...]}
                validation_errors = validate_risk_ids_structure(provided_risk_ids, customer_id, risk_type_ids)
                if validation_errors:
                    return ResponseService.response("VALIDATION_ERROR", validation_errors, "no_risk_form_validation", "NO_RISK_VALIDATION")
                
                # Set the provided risk_ids for further processing
                data["risk_ids"] = provided_risk_ids
                
                # Log the provided risk_ids for debugging
                print(f"Provided risk_ids: {provided_risk_ids} for customer_id: {customer_id}, extracted risk_type_ids: {risk_type_ids}")
            except (ValueError, TypeError) as e:
                return ResponseService.response(
                    "VALIDATION_ERROR", 
                    {"risk_ids": [f"Invalid risk_ids format: {str(e)}"]}, 
                    Error.VALIDATION_ERROR,
                    "NO_RISK_VALIDATION"
                )
        else:
            return ResponseService.response("VALIDATION_ERROR", {"risk_ids": ["risk_ids object is required and must contain risk_type_id to risk_ids mapping"]}, Error.VALIDATION_ERROR)
    elif not _from_request and is_draft:
        # For drafts, just extract and store risk_ids without validation
        provided_risk_ids = data.get("risk_ids", {})
        if provided_risk_ids and isinstance(provided_risk_ids, dict):
            try:
                # Extract risk_type_ids from the keys of risk_ids object
                risk_type_ids = [int(risk_type_id_str) for risk_type_id_str in provided_risk_ids.keys()]
                data["risk_type_ids"] = risk_type_ids
                
                # Use first risk_type_id for backward compatibility
                if risk_type_ids:
                    data["risk_type_id"] = risk_type_ids[0]
                
                # Set the provided risk_ids for further processing (without validation)
                data["risk_ids"] = provided_risk_ids
                print(f"Draft mode - Storing risk_ids without validation: {provided_risk_ids}")
            except (ValueError, TypeError) as e:
                # For drafts, just log the error but don't fail
                print(f"Draft mode - Warning: Invalid risk_ids format: {str(e)}, but continuing anyway")
                data["risk_ids"] = provided_risk_ids if provided_risk_ids else {}

    # Validate required fields for invoice generation
    required_for_invoice = ["insurer_id", "customer_id"]
    missing_for_invoice = [field for field in required_for_invoice if not data.get(field)]
    
    if missing_for_invoice:
        print(f"WARNING: Missing fields required for invoice generation: {missing_for_invoice}")
        print(f"DEBUG: Current data: {data}")
    
    # Ensure product_id is available for invoice generation
    if not data.get("product_id") and not data.get("product_group_id"):
        print(f"WARNING: Neither product_id nor product_group_id is available for invoice generation")
        print(f"DEBUG: This may cause invoice generation to fail")
    
    # Validate product_id exists if provided
    # Product validation already handled above with enhanced logging

    user = request.user if request.user.is_authenticated else None

    # Handle entity
    if _from_request and req and req.get("entity_id"):
        # Use the entity_id from the request policy when _from_request is true
        entity_id = req.get("entity_id")
        print(f"DEBUG: Using entity_id from request policy: {entity_id}")
        data["entity_id"] = entity_id
    else:
        # Generate new entity_id for direct policy creation
        entity_data = {
            "type": "policy",
            "approvel_status": False,
        }
        entity_id = handle_entity(entity_data, entity_id=data.get("entity_id"), user=user)
        data["entity_id"] = entity_id
        print(f"DEBUG: Generated new entity_id: {entity_id}")

    # Wrap the entire policy creation in a transaction
    try:
        with transaction.atomic():
            # Create policy base if not from request
            if not _from_request:
                # Determine sales_agent_id and account_manager_id similar to request policy creation
                sales_agent_id = None
                account_manager_id = None

                # Prefer values coming from the related lead, if provided
                if data.get("lead_id"):
                    lead_details = QueryBuilderService("crm_opportunities") \
                        .select("sales_agent_id", "account_manager_id") \
                        .where("id", data.get("lead_id")) \
                        .first()
                    if lead_details:
                        sales_agent_id = lead_details.get("sales_agent_id")
                        account_manager_id = lead_details.get("account_manager_id")

                # Override with explicit values from payload when provided (after empty-string normalization)
                if data.get("sales_agent_id"):
                    sales_agent_id = data.get("sales_agent_id")
                if data.get("account_manager_id"):
                    account_manager_id = data.get("account_manager_id")

                # If we have sales_agent_id but not account_manager_id, try to find manager via team
                if sales_agent_id and not account_manager_id:
                    try:
                        team_member = QueryBuilderService("core_team_users") \
                            .leftJoin("core_teams", "core_teams.id", "core_team_users.team_id") \
                            .select("core_teams.manager_id") \
                            .where("core_team_users.user_id", sales_agent_id) \
                            .first()
                        if team_member and team_member.get("manager_id"):
                            account_manager_id = team_member["manager_id"]
                            print(f"DEBUG: Found account_manager_id {account_manager_id} for sales_agent_id {sales_agent_id}")
                        else:
                            print(f"DEBUG: No team manager found for sales_agent_id {sales_agent_id}")
                    except Exception as e:
                        print(f"DEBUG: Error finding account manager for sales_agent_id {sales_agent_id}: {str(e)}")

                # Persist resolved IDs back to data so they are saved in policy base
                if sales_agent_id:
                    data["sales_agent_id"] = sales_agent_id
                if account_manager_id:
                    data["account_manager_id"] = account_manager_id
                base_fields = [
                    "risk_details_form_id",
                    "risk_type_id",
                    "insurer_id",
                    "customer_id",
                    "lead_id",
                    "request_by_id",
                    "premium_amount",
                    "quotation_document_size",
                    "quotation_document",
                    "quotation_document_name",
                    "request_type_id",
                    "product_id",
                    "product_group_id",
                    "payment_mode_id",
                    "coverage_type_id",
                    "sum_insured",
                    "quotation_issued_date",
                    "quotation_expiry_date",
                    "policy_start_date",
                    "policy_expiry_date",
                    "quotation_notes",
                    "entity_id",
                    "sales_agent_id",
                    "account_manager_id",
                    "quotation_id",
                    "quotation_code",
                ]
                
                # draft_policy_base_id can be crmp_request_policies.id or crmp_policy_base.id; resolve to policy_base_id
                provided_draft_id = data.get("draft_policy_base_id")
                provided_policy_base_id = None
                is_draft_update = provided_draft_id is not None and str(provided_draft_id).strip() != ""
                
                if is_draft_update:
                    # Resolve draft_policy_base_id: try crmp_request_policies.id first, then crmp_policy_base.id
                    request_policy_by_id = QueryBuilderService("crmp_request_policies").where("id", provided_draft_id).first()
                    if request_policy_by_id:
                        provided_policy_base_id = request_policy_by_id.get("policy_base_id")
                        print(f" DEBUG: draft_policy_base_id ({provided_draft_id}) resolved as request_policy id -> policy_base_id: {provided_policy_base_id}")
                    if provided_policy_base_id is None:
                        existing_pb = QueryBuilderService("crmp_policy_base").where("id", provided_draft_id).first()
                        if existing_pb:
                            provided_policy_base_id = provided_draft_id
                            print(f" DEBUG: draft_policy_base_id ({provided_draft_id}) treated as policy_base id")
                    if provided_policy_base_id is None:
                        return ResponseService.response("NOT_FOUND", None, f"Draft not found: no request policy or policy base with ID {provided_draft_id}.")
                    
                    # Update existing draft policy_base
                    print(f" DEBUG: Draft update mode - updating existing policy_base_id: {provided_policy_base_id}")
                    
                    existing_policy_base = QueryBuilderService("crmp_policy_base").where("id", provided_policy_base_id).first()
                    if not existing_policy_base:
                        return ResponseService.response("NOT_FOUND", None, f"Policy base with ID {provided_policy_base_id} not found.")
                    
                    # Prepare update data - only include fields that are not None and not empty strings
                    policy_base_data = {f: data[f] for f in base_fields if f in data and data[f] is not None and data[f] != ''}
                    
                    # For draft update (is_draft=true): ensure FK fields reference existing rows to avoid IntegrityError
                    if is_draft:
                        if "customer_id" in policy_base_data:
                            try:
                                cid = int(policy_base_data["customer_id"])
                                if not QueryBuilderService("core_customers").where("id", cid).first():
                                    policy_base_data.pop("customer_id", None)
                                    print(f" DEBUG: Draft update - customer_id {cid} not found in core_customers, keeping existing value")
                                else:
                                    policy_base_data["customer_id"] = cid
                            except (TypeError, ValueError):
                                policy_base_data.pop("customer_id", None)
                        if "insurer_id" in policy_base_data:
                            try:
                                iid = int(policy_base_data["insurer_id"])
                                if not QueryBuilderService("core_service_providers").where("id", iid).first():
                                    policy_base_data.pop("insurer_id", None)
                                    print(f" DEBUG: Draft update - insurer_id {iid} not found in core_service_providers, keeping existing value")
                                else:
                                    policy_base_data["insurer_id"] = iid
                            except (TypeError, ValueError):
                                policy_base_data.pop("insurer_id", None)
                        if "product_id" in policy_base_data:
                            try:
                                policy_base_data["product_id"] = int(policy_base_data["product_id"])
                            except (TypeError, ValueError):
                                policy_base_data.pop("product_id", None)
                        for fk_field in ("sales_agent_id", "account_manager_id"):
                            if fk_field in policy_base_data:
                                try:
                                    policy_base_data[fk_field] = int(policy_base_data[fk_field])
                                except (TypeError, ValueError):
                                    policy_base_data.pop(fk_field, None)
                    
                    # Don't update required date fields if they're not provided (keep existing values)
                    # Only set defaults if the field is completely missing from the update
                    required_date_fields = {
                        'policy_start_date': date.today().strftime('%Y-%m-%d'),
                        'policy_expiry_date': (date.today().replace(year=date.today().year + 1)).strftime('%Y-%m-%d')
                    }
                    
                    for req_field, default_value in required_date_fields.items():
                        # Only set default if field is not in data at all (not provided in request)
                        if req_field not in data:
                            if req_field not in existing_policy_base or not existing_policy_base.get(req_field):
                                policy_base_data[req_field] = default_value
                                # Also update data so it's available for issue_data later
                                data[req_field] = default_value
                                print(f" DEBUG: Draft update - set default {req_field} to {default_value}")
                    
                    print(f" DEBUG: Draft update mode - policy_base_data keys to update: {list(policy_base_data.keys())}")
                    
                    # Update the existing policy_base
                    if policy_base_data:
                        QueryBuilderService("crmp_policy_base").where("id", provided_policy_base_id).update(policy_base_data)
                        print(f" DEBUG: Successfully updated policy_base_id: {provided_policy_base_id}")
                    
                    policy_base_id = provided_policy_base_id
                    print(f" DEBUG: Updating existing policy_base {policy_base_id}" + (" (draft save)" if is_draft else " - converting draft to issued policy"))
                else:
                    # Create new policy_base (original logic)
                    policy_base_data = {f: data[f] for f in base_fields if f in data}
                    
                    # For drafts, provide default values for required date fields if missing
                    if is_draft:
                        required_date_fields = {
                            'policy_start_date': date.today().strftime('%Y-%m-%d'),
                            'policy_expiry_date': (date.today().replace(year=date.today().year + 1)).strftime('%Y-%m-%d')
                        }
                        for req_field, default_value in required_date_fields.items():
                            if req_field not in policy_base_data or policy_base_data[req_field] is None or policy_base_data[req_field] == '':
                                policy_base_data[req_field] = default_value
                                # Also update data so it's available for issue_data later
                                data[req_field] = default_value
                                print(f" DEBUG: Draft mode - set default {req_field} to {default_value}")
                        
                        # For drafts, only include fields that are not None and not empty strings
                        policy_base_data = {k: v for k, v in policy_base_data.items() if v is not None and v != ''}
                        print(f" DEBUG: Draft mode - policy_base_data keys: {list(policy_base_data.keys())}")
                    
                    # Debug logging for policy base creation
                    print(f"DEBUG: Creating policy base with data: {policy_base_data}")
                    print(f"DEBUG: Product ID: {policy_base_data.get('product_id')}")
                    print(f"DEBUG: Product Group ID: {policy_base_data.get('product_group_id')}")
                    print(f"DEBUG: Insurer ID: {policy_base_data.get('insurer_id')}")
                    print(f"DEBUG: Customer ID: {policy_base_data.get('customer_id')}")
                    
                    pb = QueryBuilderService("crmp_policy_base").insert(policy_base_data)
                    policy_base_id = pb["id"]
                    print(f"DEBUG: Created policy base with ID: {policy_base_id}")

                # Policy base status will be set after issued policy creation based on request type

                # Product and product_group are already stored in policy_base table

                # Store risk configurations in crmp_policy_risk_config table
                # Skip storing original risk_ids if request_type_id = 2 (will be handled in duplication logic)
                if "risk_ids" in data and isinstance(data["risk_ids"], dict) and data.get("request_type_id") != 2:
                    # For draft updates, delete existing risk configurations first to avoid duplicates
                    if is_draft_update:
                        QueryBuilderService("crmp_policy_risk_config").where("policy_base_id", policy_base_id).delete()
                        print(f" DEBUG: Draft update - deleted existing risk configurations for policy_base_id: {policy_base_id}")
                    
                    for risk_type_id_str, risk_id_list in data["risk_ids"].items():
                        for risk_id in risk_id_list:
                            # Get risk_submission from crm_risk_submissions table
                            risk_submission = QueryBuilderService("crm_risk_submissions").where("risk_id", risk_id).first()
                            if risk_submission:
                                # Check if this risk_submission_id already exists for this policy_base_id (for non-draft updates)
                                if not is_draft_update:
                                    existing_config = QueryBuilderService("crmp_policy_risk_config")\
                                        .where("policy_base_id", policy_base_id)\
                                        .where("risk_submission_id", risk_submission["id"])\
                                        .first()
                                    if existing_config:
                                        print(f" DEBUG: Risk submission {risk_submission['id']} already exists for policy_base_id {policy_base_id}, skipping insert")
                                        continue
                                
                                # Insert using the risk_submission foreign key
                                QueryBuilderService("crmp_policy_risk_config").insert({
                                    "policy_base_id": policy_base_id,
                                    "risk_submission_id": risk_submission["id"]
                                })

                # Store risk_type_ids in crmp_policy_base_risk_types table
                if "risk_type_ids" in data and isinstance(data["risk_type_ids"], list) and data["risk_type_ids"]:
                    # For draft updates, delete existing risk_type_ids first to avoid duplicates
                    if is_draft_update:
                        QueryBuilderService("crmp_policy_base_risk_types").where("policy_base_id", policy_base_id).delete()
                        print(f" DEBUG: Draft update - deleted existing risk_type_ids for policy_base_id: {policy_base_id}")
                    
                    for risk_type_id in data["risk_type_ids"]:
                        # Check if this risk_type_id already exists for this policy_base_id (for non-draft updates)
                        if not is_draft_update:
                            existing_risk_type = QueryBuilderService("crmp_policy_base_risk_types")\
                                .where("policy_base_id", policy_base_id)\
                                .where("risk_type_id", risk_type_id)\
                                .first()
                            if existing_risk_type:
                                print(f" DEBUG: Risk type {risk_type_id} already exists for policy_base_id {policy_base_id}, skipping insert")
                                continue
                        
                        QueryBuilderService("crmp_policy_base_risk_types").insert({
                            "policy_base_id": policy_base_id,
                            "risk_type_id": risk_type_id
                        })

                # update_customer_contact_info(data)

            # --- Document Validation (similar to create_request_policy) - Skip for drafts ---
            if not is_draft:
                values = data.get("values", {}) if isinstance(data.get("values"), dict) else {}
                # product_type already extracted earlier, no need to get again
                
                if product_type == "product" and product_id:
                    # Direct product document validation
                    all_required_docs = ProductDocumentType.objects.filter(
                        vendor_product_id=product_id, 
                        is_mandatory=True
                    )
                elif product_type == "group" and product_group_id:
                    # Group-based document validation
                    # Step 1: Get product_ids from core_product_group_products where product_group_id = product_group_id
                    group_products = QueryBuilderService("core_product_group_products")\
                        .select("product_id")\
                        .where("product_group_id", product_group_id)\
                        .get()
                    
                    if not group_products:
                        return ResponseService.response("NOT_FOUND", [], "No products found in this group.")
                    
                    # Extract product IDs
                    product_ids = [gp["product_id"] for gp in group_products]
                    
                    # Step 2: Get vendor_product_ids from core_product_vendor_products where product_id in product_ids
                    vendor_product_mappings = QueryBuilderService("core_product_vendor_products")\
                        .select("vendor_product_id")\
                        .whereIn("product_id", product_ids)\
                        .get()
                    
                    if not vendor_product_mappings:
                        return ResponseService.response("NOT_FOUND", [], "No vendor products found for these products.")
                    
                    # Extract vendor product IDs
                    vendor_product_ids = [vpm["vendor_product_id"] for vpm in vendor_product_mappings]
                    
                    # Step 3: Get all required documents from core_product_document_types where vendor_product_id in vendor_product_ids
                    all_required_docs = ProductDocumentType.objects.filter(
                        vendor_product_id__in=vendor_product_ids,
                        is_mandatory=True
                    )
                else:
                    all_required_docs = []

                # Validate required documents
                if all_required_docs and values:
                    missing_docs = []
                    for doc in all_required_docs:
                        # Check if doc is passed in request
                        exists_in_request = str(doc.id) in values
                        
                        if not exists_in_request:
                            missing_docs.append({"id": doc.id, "name": doc.name, "product_id": doc.vendor_product_id})

                    if missing_docs:
                        return ResponseService.response(
                            "VALIDATION_ERROR",
                            {"missing_documents": missing_docs},
                            f"Missing required documents: {[d['name'] for d in missing_docs]}"
                        )
            else:
                print(f"Draft mode - Skipping document validation")

            # Finalize issued policy creation
            data["policy_base_id"] = policy_base_id
            data["brokerage_policy_id"] = generate_policy_request_id()
            data["remarks"] = data.get("insurer_notes")
            
            # Only set policy_request_id if it's provided (for direct issued policy creation, leave it unset)
            # This allows the database to handle the field according to its constraints

            issue_fields = [
                "policy_start_date",
                "policy_expiry_date",
                "premium_amount",
                "credit_period_days",
                "credit_age_days",
                "insurer_invoice_id",
                "sum_insured",
                "policy_effective_date",
                "policy_document",
                "policy_document_size",
                "policy_document_name",
                "policy_base_id",
                "brokerage_policy_id",
                "entity_id",
                "remarks",
                "is_renewal",
                "insurer_policy_id",
                "invoice_document",
                "invoice_document_name",
            ]
            
            # Only include policy_request_id if it's provided and not None
            if "policy_request_id" in data and data["policy_request_id"] is not None:
                issue_fields.append("policy_request_id")
            
            # Determine sales_agent_id and account_manager_id for policy_base
            sales_agent_id = data.get("sales_agent_id")
            account_manager_id = data.get("account_manager_id")
            
            # If account_manager_id is not provided but sales_agent_id is, try to find account manager
            if sales_agent_id and not account_manager_id:
                try:
                    # Find team_id for the sales agent in core_team_users table
                    team_user = QueryBuilderService("core_team_users").where("user_id", sales_agent_id).first()
                    
                    if team_user and team_user.get("team_id"):
                        team_id = team_user["team_id"]
                        
                        # Find manager_id for the team in core_teams table
                        team = QueryBuilderService("core_teams").where("id", team_id).first()
                        
                        if team and team.get("manager_id"):
                            account_manager_id = team["manager_id"]
                            print(f"DEBUG: Found account_manager_id {account_manager_id} for sales_agent_id {sales_agent_id} via team {team_id}")
                        else:
                            print(f"DEBUG: No manager found for team {team_id}")
                    else:
                        print(f"DEBUG: No team found for sales_agent_id {sales_agent_id}")
                        
                except Exception as e:
                    print(f"DEBUG: Error finding account manager for sales_agent_id {sales_agent_id}: {str(e)}")
            
            # If still no account_manager_id, try to get from request_by_id (fallback)
            if not account_manager_id:
                user_id_to_check = None
                
                if _from_request:
                    # When creating from request, use request_by_id from the request policy data
                    if req and req.get("request_by_id"):
                        user_id_to_check = req["request_by_id"]
                        print(f"DEBUG: _from_request=true, using request_by_id from request policy: {user_id_to_check}")
                else:
                    # When creating directly (not from request), use request_by_id from payload
                    if data.get("request_by_id"):
                        user_id_to_check = data["request_by_id"]
                        print(f"DEBUG: _from_request=false, using request_by_id from payload: {user_id_to_check}")
                
                if user_id_to_check:
                    try:
                        # Find team_id for the user in core_team_users table
                        team_user = QueryBuilderService("core_team_users").where("user_id", user_id_to_check).first()
                        
                        if team_user and team_user.get("team_id"):
                            team_id = team_user["team_id"]
                            
                            # Find manager_id for the team in core_teams table
                            team = QueryBuilderService("core_teams").where("id", team_id).first()
                            
                            if team and team.get("manager_id"):
                                account_manager_id = team["manager_id"]
                                print(f"DEBUG: Found account_manager_id {account_manager_id} for user {user_id_to_check} via team {team_id}")
                            else:
                                print(f"DEBUG: No manager found for team {team_id}")
                        else:
                            print(f"DEBUG: No team found for user {user_id_to_check}")
                            
                    except Exception as e:
                        print(f"DEBUG: Error finding account manager for user {user_id_to_check}: {str(e)}")
            
            # Add account_manager_id to data for policy_base if found
            if account_manager_id:
                data["account_manager_id"] = account_manager_id
            
            issue_data = {f: data[f] for f in issue_fields if f in data and data[f] is not None}
            
            # For drafts, convert empty strings to None for integer and required fields
            if is_draft:
                integer_fields = ['credit_period_days', 'credit_age_days', 'policy_document_size']
                for field in integer_fields:
                    if field in issue_data:
                        if issue_data[field] == '':
                            issue_data[field] = None
                            print(f" DEBUG: Draft mode - converted empty string to None for {field}")
                    else:
                        # If field is missing and is credit_period_days, set to None (will be excluded from insert)
                        if field == 'credit_period_days':
                            issue_data[field] = None
                            print(f" DEBUG: Draft mode - set missing {field} to None")
                
                # Also convert empty strings to None for string fields that might be problematic
                string_fields_to_clean = ['insurer_invoice_id', 'insurer_policy_id', 'policy_effective_date', 
                                         'policy_document', 'policy_document_name', 'invoice_document', 
                                         'invoice_document_name', 'premium_amount']
                for field in string_fields_to_clean:
                    if field in issue_data and issue_data[field] == '':
                        issue_data[field] = None
                        print(f" DEBUG: Draft mode - converted empty string to None for {field}")
                
                # Remove None values and empty strings from issue_data for drafts
                issue_data = {k: v for k, v in issue_data.items() if v is not None and v != ''}
                print(f" DEBUG: Draft mode - cleaned issue_data, remaining keys: {list(issue_data.keys())}")
            
            print(f" DEBUG: issue_data before field mapping: {issue_data}")
            
            # Map request field names to database field names
            # Only map if the values are not empty strings
            print(f" DEBUG: Field mapping logic - checking policy_start_date")
            if "policy_start_date" in issue_data and issue_data["policy_start_date"] != "":
                print(f" DEBUG: policy_start_date has value: {issue_data['policy_start_date']}, mapping to start_date")
                issue_data["start_date"] = issue_data.pop("policy_start_date")
            elif "policy_start_date" in issue_data:
                # Remove empty policy_start_date from issue_data
                print(f" DEBUG: policy_start_date is empty/None: {issue_data['policy_start_date']}, removing from issue_data")
                issue_data.pop("policy_start_date")
            else:
                print(f" DEBUG: policy_start_date not in issue_data")
                
            print(f" DEBUG: Field mapping logic - checking policy_expiry_date")
            if "policy_expiry_date" in issue_data and issue_data["policy_expiry_date"] != "":
                print(f" DEBUG: policy_expiry_date has value: {issue_data['policy_expiry_date']}, mapping to end_date")
                issue_data["end_date"] = issue_data.pop("policy_expiry_date")
            elif "policy_expiry_date" in issue_data:
                # Remove empty policy_expiry_date from issue_data
                print(f" DEBUG: policy_expiry_date is empty/None: {issue_data['policy_expiry_date']}, removing from issue_data")
                issue_data.pop("policy_expiry_date")
            else:
                print(f" DEBUG: policy_expiry_date not in issue_data")
            
            # For drafts, provide default values for required date fields and other required fields if missing
            if is_draft:
                # Try to get dates from data (which may have defaults from policy_base)
                if "start_date" not in issue_data:
                    # Try policy_start_date from data
                    if data.get("policy_start_date"):
                        issue_data["start_date"] = data["policy_start_date"]
                        print(f" DEBUG: Draft mode - set start_date from data: {issue_data['start_date']}")
                    else:
                        # Provide default value
                        issue_data["start_date"] = date.today().strftime('%Y-%m-%d')
                        print(f" DEBUG: Draft mode - set default start_date to {issue_data['start_date']}")
                
                if "end_date" not in issue_data:
                    # Try policy_expiry_date from data
                    if data.get("policy_expiry_date"):
                        issue_data["end_date"] = data["policy_expiry_date"]
                        print(f" DEBUG: Draft mode - set end_date from data: {issue_data['end_date']}")
                    else:
                        # Provide default value (1 year from today)
                        issue_data["end_date"] = (date.today().replace(year=date.today().year + 1)).strftime('%Y-%m-%d')
                        print(f" DEBUG: Draft mode - set default end_date to {issue_data['end_date']}")
                
                # Provide default values for required integer fields
                if "credit_period_days" not in issue_data or issue_data.get("credit_period_days") is None:
                    issue_data["credit_period_days"] = 0  # Default to 0 days for drafts
                    print(f" DEBUG: Draft mode - set default credit_period_days to 0")
                
                # Provide default values for required string fields
                if "insurer_invoice_id" not in issue_data or issue_data.get("insurer_invoice_id") is None or issue_data.get("insurer_invoice_id") == '':
                    issue_data["insurer_invoice_id"] = "DRAFT"  # Default placeholder for drafts
                    print(f" DEBUG: Draft mode - set default insurer_invoice_id to 'DRAFT'")
                
                # Provide default value for policy_effective_date if missing (use start_date)
                if "policy_effective_date" not in issue_data or issue_data.get("policy_effective_date") is None or issue_data.get("policy_effective_date") == '':
                    # Use start_date if available, otherwise use today
                    if "start_date" in issue_data:
                        issue_data["policy_effective_date"] = issue_data["start_date"]
                        print(f" DEBUG: Draft mode - set policy_effective_date to start_date: {issue_data['policy_effective_date']}")
                    else:
                        issue_data["policy_effective_date"] = date.today().strftime('%Y-%m-%d')
                        print(f" DEBUG: Draft mode - set default policy_effective_date to {issue_data['policy_effective_date']}")
            
            print(f" DEBUG: issue_data after field mapping: {issue_data}")
            
            # Validate required fields for invoice generation
            required_fields = ['premium_amount', 'policy_effective_date', 'credit_period_days', 'insurer_invoice_id']
            missing_fields = []
            for field in required_fields:
                if field not in issue_data or issue_data[field] is None or issue_data[field] == "":
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"WARNING: Missing required fields for invoice generation: {missing_fields}")
                print(f"DEBUG: This may cause invoice generation to fail")
            
            # Validate date fields and ensure proper date periods
            date_fields = ['policy_effective_date', 'start_date', 'end_date']
            for field in date_fields:
                if field in issue_data and issue_data[field]:
                    try:
                        if isinstance(issue_data[field], str):
                            parsed_date = datetime.strptime(issue_data[field], '%Y-%m-%d')
                            print(f"DEBUG: {field} validated: {issue_data[field]} (parsed: {parsed_date.date()})")
                    except ValueError:
                        print(f"ERROR: Invalid date format for {field}: {issue_data[field]}")
                        print(f"DEBUG: This may cause invoice generation to fail")
            
            # Validate date periods - ensure start_date is before end_date
            if "start_date" in issue_data and "end_date" in issue_data:
                try:
                    start = datetime.strptime(issue_data["start_date"], '%Y-%m-%d').date() if isinstance(issue_data["start_date"], str) else issue_data["start_date"]
                    end = datetime.strptime(issue_data["end_date"], '%Y-%m-%d').date() if isinstance(issue_data["end_date"], str) else issue_data["end_date"]
                    
                    if start > end:
                        # For drafts, adjust end_date to be after start_date (add 1 year)
                        if is_draft:
                            new_end = start + timedelta(days=365)
                            issue_data["end_date"] = new_end.strftime('%Y-%m-%d')
                            print(f"DEBUG: Draft mode - adjusted end_date to be after start_date: {issue_data['end_date']}")
                        else:
                            print(f"WARNING: start_date ({start}) is after end_date ({end})")
                    else:
                        period_days = (end - start).days
                        print(f"DEBUG: Date period validated: {period_days} days from {start} to {end}")
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Could not validate date period: {str(e)}")
            
            # Validate policy_effective_date is on or before start_date
            if "policy_effective_date" in issue_data and "start_date" in issue_data:
                try:
                    effective = datetime.strptime(issue_data["policy_effective_date"], '%Y-%m-%d').date() if isinstance(issue_data["policy_effective_date"], str) else issue_data["policy_effective_date"]
                    start = datetime.strptime(issue_data["start_date"], '%Y-%m-%d').date() if isinstance(issue_data["start_date"], str) else issue_data["start_date"]
                    
                    if effective > start:
                        # For drafts, adjust policy_effective_date to be on or before start_date
                        if is_draft:
                            issue_data["policy_effective_date"] = issue_data["start_date"]
                            print(f"DEBUG: Draft mode - adjusted policy_effective_date to match start_date: {issue_data['policy_effective_date']}")
                        else:
                            print(f"WARNING: policy_effective_date ({effective}) is after start_date ({start})")
                    else:
                        print(f"DEBUG: policy_effective_date ({effective}) is on or before start_date ({start})")
                except (ValueError, TypeError) as e:
                    print(f"DEBUG: Could not validate policy_effective_date against start_date: {str(e)}")
            print(f"DEBUG: Issue data before insert: {issue_data}")
            print(f"DEBUG: Premium amount in issue_data: {issue_data.get('premium_amount')}")
            print(f"DEBUG: Policy effective date: {issue_data.get('policy_effective_date')}")
            print(f"DEBUG: Start date: {issue_data.get('start_date')}")
            print(f"DEBUG: End date: {issue_data.get('end_date')}")
            print(f"DEBUG: Credit period days: {issue_data.get('credit_period_days')}")
            print(f"DEBUG: Credit age days: {issue_data.get('credit_age_days')}")
            print(f"DEBUG: Insurer invoice ID: {issue_data.get('insurer_invoice_id')}")
            print(f"DEBUG: Insurer policy ID: {issue_data.get('insurer_policy_id')}")
            print(f"DEBUG: Sales agent ID: {issue_data.get('sales_agent_id')}")
            print(f"DEBUG: Account manager ID: {issue_data.get('account_manager_id')}")
            print(f"DEBUG: Is renewal: {issue_data.get('is_renewal')}")
            print(f"DEBUG: Policy base ID: {issue_data.get('policy_base_id')}")
            print(f"DEBUG: Entity ID: {issue_data.get('entity_id')}")
            
            print(f" DEBUG: About to insert into crmp_issued_policies with data: {issue_data}")
            print(f" DEBUG: Checking for required fields in issue_data:")
            print(f" DEBUG: - start_date: {issue_data.get('start_date')}")
            print(f" DEBUG: - end_date: {issue_data.get('end_date')}")
            print(f" DEBUG: - premium_amount: {issue_data.get('premium_amount')}")
            print(f" DEBUG: - policy_effective_date: {issue_data.get('policy_effective_date')}")
            
            # Check if issued_policy already exists for this policy_base_id to prevent duplicates
            existing_issued_policy = None
            if policy_base_id:
                existing_issued_policy = QueryBuilderService("crmp_issued_policies").where("policy_base_id", policy_base_id).first()
                if existing_issued_policy:
                    print(f" DEBUG: Found existing issued_policy with ID: {existing_issued_policy.get('id')} for policy_base_id: {policy_base_id}")
                    print(f" DEBUG: Updating existing issued_policy instead of creating duplicate")
            
            if existing_issued_policy:
                # Update existing issued_policy
                QueryBuilderService("crmp_issued_policies").where("id", existing_issued_policy.get("id")).update(issue_data)
                created = existing_issued_policy
                print(f" DEBUG: Successfully updated existing issued policy with ID: {created.get('id')}")
                is_policy_update = True  # Flag to indicate this is an update, not a new creation
            else:
                # Create new issued_policy
                created = QueryBuilderService("crmp_issued_policies").insert(issue_data)
                is_policy_update = False  # Flag to indicate this is a new creation
            print(f" DEBUG: Successfully created/updated issued policy with ID: {created.get('id')}")
            print(f" DEBUG: Created/updated issued policy data: {created}")
            
            # Auto-calculate and update credit age after creation
            try:
                issued_policy = IssuedPolicy.objects.get(id=created.get('id'))
                issued_policy.update_credit_age()
                print(f"✅ Credit age auto-calculated for new policy: {issued_policy.credit_age_days} days")
            except IssuedPolicy.DoesNotExist:
                print(f"⚠️ Warning: Could not find issued policy {created.get('id')} to update credit age")
            except Exception as e:
                print(f"⚠️ Warning: Error updating credit age for new policy {created.get('id')}: {str(e)}")

            # --- Risk Duplication Logic for request_type_id = 2 ---
            if data.get("request_type_id") == 2 and data.get("risk_ids") and isinstance(data.get("risk_ids"), dict):
                try:
                    # Get the lead_id from the data
                    lead_id = data.get("lead_id")
                    
                    if lead_id and lead_id.strip() and lead_id.lower() not in ['null', 'undefined', '']:
                        # If lead_id is provided, directly assign existing risk_ids without duplication
                        print(f"DEBUG: Lead_id provided ({lead_id}), skipping risk duplication and directly assigning existing risks")
                        
                        for risk_type_id_str, risk_id_list in data["risk_ids"].items():
                            for risk_id in risk_id_list:
                                # Get the latest risk submission for this risk_id (highest version or latest created)
                                latest_risk_submission = QueryBuilderService("crm_risk_submissions")\
                                    .where("risk_id", risk_id)\
                                    .orderBy("version", "desc")\
                                    .orderBy("created_at", "desc")\
                                    .first()
                                
                                if latest_risk_submission:
                                    # Directly assign the latest risk_submission to the new policy_base_id
                                    QueryBuilderService("crmp_policy_risk_config").insert({
                                        "policy_base_id": policy_base_id,
                                        "risk_submission_id": latest_risk_submission["id"]
                                    })
                        
                        # Log activity for direct risk assignment
                        total_risks = sum(len(risk_list) for risk_list in data["risk_ids"].values())
                        ActivityService.store_activity(
                            request=request,
                            entity_id=data.get("entity_id"),
                            activity=f"Direct assignment: Assigned {total_risks} existing risk submissions to new policy_base_id {policy_base_id} (lead_id: {lead_id})"
                        )
                        
                    else:
                        # If no lead_id provided, perform the full risk duplication process
                        print(f"DEBUG: No lead_id provided, performing full risk duplication")
                        
                        # Process each risk_type_id and its associated risk_ids
                        for risk_type_id_str, risk_id_list in data["risk_ids"].items():
                            for risk_id in risk_id_list:
                                # Get the latest risk submission for this risk_id (highest version or latest created)
                                existing_risk_submission = QueryBuilderService("crm_risk_submissions")\
                                    .where("risk_id", risk_id)\
                                    .orderBy("version", "desc")\
                                    .orderBy("created_at", "desc")\
                                    .first()
                                
                                if existing_risk_submission:
                                    # Get the original submission to get form_id
                                    original_submission = QueryBuilderService("core_form_submissionss")\
                                        .where("id", existing_risk_submission["submission_id"])\
                                        .select("form_id")\
                                        .first()
                                    
                                    if original_submission:
                                        # Create new submission in core_form_submissionss
                                        new_submission = QueryBuilderService("core_form_submissionss").insert({
                                            "form_id": original_submission["form_id"],
                                            "user_id": request.user.id if request.user.is_authenticated else None,
                                            "customer_id": None
                                        })
                                        
                                        # Copy form submission values from original submission to new submission
                                        original_submission_values = QueryBuilderService("core_form_submission_valuess")\
                                            .where("form_submission_id", existing_risk_submission["submission_id"])\
                                            .get()
                                        
                                        # Insert copied values for the new submission
                                        for value_record in original_submission_values:
                                            QueryBuilderService("core_form_submission_valuess").insert({
                                                "form_submission_id": new_submission["id"],
                                                "custom_form_element_id": value_record["custom_form_element_id"],
                                                "form_element_id": value_record["form_element_id"],
                                                "value": value_record["value"]
                                            })
                                        
                                        # Create new submission risk entry with new submission_id and lead_id
                                        # Increment version count by 1
                                        current_version = existing_risk_submission.get("version", 1)
                                        new_version = current_version + 1
                                        print(f"DEBUG: Risk {risk_id} - Current version: {current_version}, New version: {new_version}")
                                        
                                        new_submission_risk_data = {
                                            "risk_id": existing_risk_submission["risk_id"],
                                            "submission_id": new_submission["id"],
                                            "lead_id": lead_id,
                                            "version": new_version,
                                            "created_at": date.today(),
                                            "updated_at": date.today()
                                        }
                                        
                                        # Insert the new submission risk
                                        new_risk_submission = QueryBuilderService("crm_risk_submissions").insert(new_submission_risk_data)
                                        
                                        # Update crmp_policy_risk_config table with new risk_submission_id
                                        QueryBuilderService("crmp_policy_risk_config").insert({
                                            "policy_base_id": policy_base_id,
                                            "risk_submission_id": new_risk_submission["id"]
                                        })
                        
                        # Log activity for risk duplication
                        total_risks = sum(len(risk_list) for risk_list in data["risk_ids"].values())
                        ActivityService.store_activity(
                            request=request,
                            entity_id=data.get("entity_id"),
                            activity=f"Created {total_risks} new risk submissions with form values for request_type_id = 2 policy"
                        )
                    
                except Exception as e:
                    # Log error but don't fail the policy creation
                    print(f"Error processing risk details for request_type_id = 2: {str(e)}")
                    print(f"Error details: {type(e).__name__}: {str(e)}")
                    ActivityService.store_activity(
                        request=request,
                        entity_id=data.get("entity_id"),
                        activity=f"Warning: Failed to process risk details for request_type_id = 2 - {str(e)}"
                    )

            # --- Document Storage (similar to create_request_policy) ---
            values = data.get("values", {}) if isinstance(data.get("values"), dict) else {}
            stored_documents = {}
            
            if (product_type == "product" and product_id and values) or (product_type == "group" and product_group_id and values):
                if product_type == "product":
                    # Get all documents for the product
                    all_docs = ProductDocumentType.objects.filter(vendor_product_id=product_id)
                else:  # product_type == "group"
                    # Group-based document retrieval for storage
                    # Step 1: Get product_ids from core_product_group_products where product_group_id = product_group_id
                    group_products = QueryBuilderService("core_product_group_products")\
                        .select("product_id")\
                        .where("product_group_id", product_group_id)\
                        .get()
                    
                    if not group_products:
                        return ResponseService.response("NOT_FOUND", [], "No products found in this group.")
                    
                    # Extract product IDs
                    product_ids = [gp["product_id"] for gp in group_products]
                    
                    # Step 2: Get vendor_product_ids from core_product_vendor_products where product_id in product_ids
                    vendor_product_mappings = QueryBuilderService("core_product_vendor_products")\
                        .select("vendor_product_id")\
                        .whereIn("product_id", product_ids)\
                        .get()
                    
                    if not vendor_product_mappings:
                        return ResponseService.response("NOT_FOUND", [], "No vendor products found for these products.")
                    
                    # Extract vendor product IDs
                    vendor_product_ids = [vpm["vendor_product_id"] for vpm in vendor_product_mappings]
                    
                    # Step 3: Get all documents from core_product_document_types where vendor_product_id in vendor_product_ids
                    all_docs = ProductDocumentType.objects.filter(vendor_product_id__in=vendor_product_ids)

                # Store passed docs
                for doc_type_id_str, doc_info in values.items():
                    try:
                        doc_type_id = int(doc_type_id_str)
                        if not all_docs.filter(id=doc_type_id).exists():
                            continue
                        
                        doc_obj, created_doc = PolicyRequestDocument.objects.update_or_create(
                            policy_base_id=policy_base_id,
                            document_type_id=doc_type_id,
                            defaults={"value": doc_info}
                        )
                        
                        # Store the document value in our response object
                        stored_documents[doc_type_id_str] = doc_obj.value
                    except ValueError:
                        continue

            # Generate invoice for the issued policy
            try:
                print(f"DEBUG: About to generate invoice for issued policy ID: {created['id']}")
                print(f"DEBUG: Policy base ID: {policy_base_id}")
                print(f"DEBUG: Issue data: {issue_data}")
                print(f"DEBUG: User: {user}")
                print(f"DEBUG: Sales agent ID: {issue_data.get('sales_agent_id')}")
                
                # Pre-validate data for invoice generation
                print(f"DEBUG: Pre-invoice validation:")
                print(f"DEBUG: - Premium amount: {issue_data.get('premium_amount')}")
                print(f"DEBUG: - Policy effective date: {issue_data.get('policy_effective_date')}")
                print(f"DEBUG: - Credit period days: {issue_data.get('credit_period_days')}")
                print(f"DEBUG: - Credit age days: {issue_data.get('credit_age_days')}")
                print(f"DEBUG: - Insurer invoice ID: {issue_data.get('insurer_invoice_id')}")
                print(f"DEBUG: - Insurer policy ID: {issue_data.get('insurer_policy_id')}")
                print(f"DEBUG: - Is renewal: {issue_data.get('is_renewal')}")
                
                # Get sales_agent_id from policy_base for invoice generation
                sales_agent_id = data.get("sales_agent_id")
                if not sales_agent_id and policy_base_id:
                    # Fetch from policy_base if not in data
                    policy_base = QueryBuilderService("crmp_policy_base").where("id", policy_base_id).first()
                    if policy_base:
                        sales_agent_id = policy_base.get("sales_agent_id")
                
                # Ensure we have the required data for invoice generation
                invoice_result = generate_invoice_for_issued_policy(
                    created["id"], user=user, sales_agent_id=sales_agent_id
                )
                
                if invoice_result:
                    print(f"DEBUG: Successfully generated invoice for issued policy ID: {created['id']}")
                    print(f"DEBUG: Invoice ID: {invoice_result}")
                    
                    # Send detailed policy issued notification to customer
                    try:
                        from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
                        
                        # Get policy details for notification
                        policy_details = (
                            QueryBuilderService("crmp_issued_policies as ip")
                            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
                            .leftJoin("core_customers as c", "c.id", "pb.customer_id")
                            .leftJoin("core_vendor_products as vp", "vp.id", "pb.product_id")
                            .select(
                                "ip.brokerage_policy_id",
                                "ip.premium_amount",
                                "ip.policy_document",
                                "ip.invoice_document",
                                "ip.invoice_document_name",
                                "c.id as customer_id",
                                "c.name as customer_name",
                                "vp.name as product_name"
                            )
                            .where("ip.id", created["id"])
                            .first()
                        )
                        
                        if policy_details and policy_details.get("customer_id"):
                            # Format policy document and debit note URLs
                            policy_doc_url = policy_details.get("policy_document")
                            debit_note_url = policy_details.get("invoice_document")
                            
                            # Create policy link (assuming frontend URL structure)
                            policy_link = f"/policies/{created['id']}"
                            
                            # Format detailed message
                            detailed_message = NotificationService.format_policy_issued_message(
                                policy_number=policy_details.get("brokerage_policy_id", "N/A"),
                                premium_amount=policy_details.get("premium_amount", "0.00"),
                                product_name=policy_details.get("product_name", "Unknown Product"),
                                policy_doc_url=policy_doc_url,
                                debit_note_url=debit_note_url,
                                policy_link=policy_link
                            )
                            
                            # Prepare policy data for metadata
                            policy_data = {
                                "policy_id": created["id"],
                                "brokerage_policy_id": policy_details.get("brokerage_policy_id"),
                                "premium_amount": str(policy_details.get("premium_amount", "0.00")),
                                "product_name": policy_details.get("product_name"),
                                "policy_document_url": policy_doc_url,
                                "debit_note_url": debit_note_url,
                                "debit_note_name": policy_details.get("invoice_document_name")
                            }
                            
                            # Prepare links for metadata
                            links = []
                            if policy_link:
                                links.append({"title": "View Policy", "url": policy_link})
                            if policy_doc_url:
                                links.append({"title": "Policy Document", "url": policy_doc_url})
                            if debit_note_url:
                                links.append({"title": "Debit Note", "url": debit_note_url})
                            
                            # Generate detailed notification
                            NotificationService.generate_detailed_notification(
                                type_code="policy_issued",
                                title="Policy Successfully Issued",
                                detailed_message=detailed_message,
                                customer_id=policy_details.get("customer_id"),
                                user_id=user.id if user else None,
                                policy_data=policy_data,
                                links=links
                            )
                            
                            print(f"✅ Policy issued notification sent to customer {policy_details.get('customer_id')}")
                        else:
                            print(f"⚠️ Could not send policy issued notification - missing policy details or customer_id")
                            
                    except Exception as notify_e:
                        print(f"⚠️ Error sending policy issued notification: {str(notify_e)}")
                        # Don't fail the entire operation for notification errors
                else:
                    print(f"WARNING: Finance invoice generation returned None for policy {created['id']}")
                    print(f"DEBUG: Attempting fallback to policy invoice generation...")
                    
                    # Fallback to policy invoice generation
                    try:
                        from envoy_bu_policy_api.policy.controllers.invoice_utils import generate_invoice_for_issued_policy as policy_generate_invoice
                        policy_invoice_result = policy_generate_invoice(created["id"], user=user, sales_agent_id=sales_agent_id)
                        if policy_invoice_result:
                            print(f"DEBUG: Successfully generated policy invoice for issued policy ID: {created['id']}")
                        else:
                            print(f"WARNING: Policy invoice generation also failed for policy {created['id']}")
                    except Exception as fallback_e:
                        print(f"ERROR: Fallback policy invoice generation also failed: {str(fallback_e)}")
                        import traceback
                        traceback.print_exc()
                    
            except Exception as e:
                print(f"ERROR: Failed to generate invoice for policy {created['id']}: {str(e)}")
                import traceback
                traceback.print_exc()
                
                # Try fallback to policy invoice generation
                try:
                    print(f"DEBUG: Attempting fallback to policy invoice generation after exception...")
                    from envoy_bu_policy_api.policy.controllers.invoice_utils import generate_invoice_for_issued_policy as policy_generate_invoice
                    policy_invoice_result = policy_generate_invoice(created["id"], user=user, sales_agent_id=sales_agent_id)
                    if policy_invoice_result:
                        print(f"DEBUG: Successfully generated policy invoice for issued policy ID: {created['id']} after exception")
                    else:
                        print(f"WARNING: Policy invoice generation also failed for policy {created['id']} after exception")
                except Exception as fallback_e:
                    print(f"ERROR: Fallback policy invoice generation also failed after exception: {str(fallback_e)}")
                
                # Don't fail the entire operation if invoice generation fails

            # Set policy base status based on request type and draft mode
            # Check if this is a renewal (request_type_id = 2 or is_renewal = 1) - needed for later logic
            is_renewal = data.get("is_renewal", 0) == 1 or data.get("request_type_id") == 2
            
            try:
                from envoy_bu_policy_api.policy.controllers.policy_status_utils import set_policy_base_active, set_policy_base_renewed, set_policy_base_status_by_scenario
                
                # For drafts, set status to DRAFT and skip further status logic
                if is_draft:
                    result = set_policy_base_status_by_scenario(policy_base_id, "draft")
                    status_name = "DRAFT"
                    if result.get("success"):
                        print(f"Successfully set policy base {policy_base_id} status to DRAFT (draft mode)")
                    else:
                        print(f"Warning: Failed to set policy base status to DRAFT: {result.get('message')}")
                else:

                    # Check current policy base status
                    base_status = QueryBuilderService("crmp_policy_base").where("id", policy_base_id).select("status_id").first()
                    
                    # Get RENEWAL_IN_PROGRESS status ID using immutable type+module
                    renew_status = QueryBuilderService("core_status")\
                        .where("type", "pol_renewal_progress")\
                        .where("module", "policy")\
                        .select("id").first()

                    # If current status is RENEWAL_IN_PROGRESS, set to RENEWED
                    if base_status and renew_status and base_status.get("status_id") == renew_status.get("id"):
                        result = set_policy_base_renewed(policy_base_id)
                        status_name = "RENEWED"
                    else:
                        # Set status based on request type
                        if is_renewal:
                            result = set_policy_base_renewed(policy_base_id)
                            status_name = "RENEWED"
                        else:
                            result = set_policy_base_active(policy_base_id)
                            status_name = "ACTIVE"
                    
                    if result.get("success"):
                        print(f"Successfully set policy base {policy_base_id} status to {status_name}")
                    else:
                        print(f"Warning: Failed to set policy base status to {status_name}: {result.get('message')}")
            except Exception as e:
                print(f"ERROR: Failed to set policy base status: {str(e)}")
        
        # --- Policy Inheritance Logic ---
        # Store inheritance data if it's a renewal (is_renewal = 1)
        if is_renewal:
            try:
                print(f"DEBUG: Processing renewal inheritance for policy {created.get('id')}")
                
                # Find the original issued_policy_id to inherit from
                original_issued_policy_id = None
                
                # Method 1: Check if opportunity_id is provided
                opportunity_id = data.get("opportunity_id")
                if opportunity_id:
                    print(f"DEBUG: Looking for original policy via opportunity_id: {opportunity_id}")
                    opportunity = QueryBuilderService("crm_opportunities")\
                        .select("issued_policy_id")\
                        .where("id", opportunity_id)\
                        .first()
                    
                    if opportunity and opportunity.get("issued_policy_id"):
                        original_issued_policy_id = opportunity.get("issued_policy_id")
                        print(f"DEBUG: Found original policy via opportunity: {original_issued_policy_id}")
                
                # Method 2: Check if lea_id is provided (alternative field name for opportunity_id)
                if not original_issued_policy_id:
                    lea_id = data.get("lea_id")
                    if lea_id:
                        print(f"DEBUG: Looking for original policy via lea_id: {lea_id}")
                        opportunity = QueryBuilderService("crm_opportunities")\
                            .select("issued_policy_id")\
                            .where("id", lea_id)\
                            .first()
                        
                        if opportunity and opportunity.get("issued_policy_id"):
                            original_issued_policy_id = opportunity.get("issued_policy_id")
                            print(f"DEBUG: Found original policy via lea_id: {original_issued_policy_id}")
                
                # Method 3: Check if lead_id is provided (alternative field name for opportunity_id)
                if not original_issued_policy_id:
                    lead_id = data.get("lead_id")
                    if lead_id:
                        print(f"DEBUG: Looking for original policy via lead_id: {lead_id}")
                        opportunity = QueryBuilderService("crm_opportunities")\
                            .select("issued_policy_id")\
                            .where("id", lead_id)\
                            .first()
                        
                        if opportunity and opportunity.get("issued_policy_id"):
                            original_issued_policy_id = opportunity.get("issued_policy_id")
                            print(f"DEBUG: Found original policy via lead_id: {original_issued_policy_id}")
                
                # Method 4: Check if original policy_base_id is provided (fallback)
                if not original_issued_policy_id:
                    if original_policy_base_id:
                        print(f"DEBUG: Looking for original policy via original_policy_base_id: {original_policy_base_id}")
                        original_policy = QueryBuilderService("crmp_issued_policies")\
                            .select("id")\
                            .where("policy_base_id", original_policy_base_id)\
                            .first()
                        
                        if original_policy:
                            original_issued_policy_id = original_policy.get("id")
                            print(f"DEBUG: Found original policy via original_policy_base_id: {original_issued_policy_id}")
                        else:
                            print(f"DEBUG: No issued policy found for original_policy_base_id: {original_policy_base_id}")
                
                # Create inheritance record if we found the original policy
                if original_issued_policy_id:
                    print(f"DEBUG: Creating inheritance record - ORIGINAL policy: {original_issued_policy_id}, NEW policy: {created.get('id')}")
                    
                    # Use the same entity_id from the newly created issued policy
                    # entity_data = {
                    #     "type": "policy_inheritance",
                    #     "approvel_status": False,
                    # }
                    # inheritance_entity_id = handle_entity(entity_data, entity_id=None, user=user)
                    inheritance_entity_id = created.get("entity_id") if isinstance(created, dict) else created.get("entity_id")
                    print(f"DEBUG: Using entity_id from newly created issued policy: {inheritance_entity_id}")
                    
                    # Prepare inheritance data - CORRECT: issued_policy_id should be the ORIGINAL policy
                    inheritance_data = {
                        "issued_policy_id": original_issued_policy_id,  # This is the OLD/ORIGINAL policy we're inheriting from
                        "entity_id": inheritance_entity_id,  # This should be the SAME entity_id as the issued policy
                    }
                    
                    # Add optional inheritance fields if provided
                    if "start_date" in data:
                        inheritance_data["start_date"] = data["start_date"]
                    if "policy_effective_date" in data:
                        inheritance_data["policy_effective_date"] = data["policy_effective_date"]
                    
                    # Insert inheritance record
                    inheritance_created = QueryBuilderService("crmp_issued_policies_inheritance").insert(inheritance_data)
                    print(f"DEBUG: Created policy inheritance record with ID: {inheritance_created.get('id')}")
                    print(f"DEBUG: Inheritance record links ORIGINAL policy {original_issued_policy_id} to NEW policy {created.get('id')}")
                    print(f"DEBUG: This means policy {original_issued_policy_id} was renewed/replaced by policy {created.get('id')}")
                else:
                    lea_id = data.get("lea_id")
                    lead_id = data.get("lead_id")
                    print(f"WARNING: No original policy found for renewal inheritance. opportunity_id: {opportunity_id}, lea_id: {lea_id}, lead_id: {lead_id}, original_policy_base_id: {original_policy_base_id}")
                
            except Exception as e:
                print(f"ERROR: Failed to create policy inheritance record: {str(e)}")
                # Don't fail the entire operation for inheritance errors
        
        return ResponseService.response("SUCCESS", created, Message.DATA_CREATED)

    except Exception as e:
        # Log the error for debugging
        print(f"Error creating issued policy: {str(e)}")
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            {"error": f"Failed to create issued policy: {str(e)}"}, 
            Error.INTERNAL_SERVER_ERROR
        )


def get_issued_policy_rules_with_request():
    print(" DEBUG: get_issued_policy_rules_with_request() called")
    rules = {
        "premium_amount": "required",
        "credit_period_days": "required|integer",
        # credit_age_days removed - it's auto-calculated
        "insurer_invoice_id": "required|string",
        "sum_insured": "nullable|numeric",
        "policy_effective_date": "required|date",
        "insurer_policy_id": "required|string",
        "policy_document": "nullable",
        "policy_document_size": "nullable|integer",
        "policy_document_name": "nullable|string",
        # Date validations
        "policy_start_date": "required|date",
        "policy_expiry_date": "required|date|after:policy_start_date",
        
        # "policy_request_id": "unique:crmp_issued_policies,policy_base_id",
    }
    print(f" DEBUG: get_issued_policy_rules_with_request() returning rules: {rules}")
    return rules


def get_issued_policy_rules_with_request_put():
    return {
        "policy_start_date": "nullable|date",
        "policy_expiry_date": "nullable|date|after:policy_start_date",
        "start_date": "nullable|date",
        "end_date": "nullable|date|after:start_date",
        "policy_issue_date": "nullable|date|before_or_equal:policy_start_date",
        "premium_amount": "required|numeric",
        "credit_period_days": "required|integer",
        # credit_age_days removed - it's auto-calculated
        "insurer_invoice_id": "required|string",
        "sum_insured": "nullable|numeric",
        "policy_effective_date": "nullable|date",
        "policy_document": "nullable",
        "policy_document_size": "nullable|integer",
        "policy_document_name": "nullable|string",
        # "policy_request_id": "unique:crmp_issued_policies,policy_base_id",
    }


def get_issued_policy_rules_without_request():
    print(" DEBUG: get_issued_policy_rules_without_request() called")
    rules = {
        "lead_id": "integer|exists:crm_opportunities,id",
        "quotation_document_name": "string",
        "quotation_document": "nullable",
        "insurer_id": "integer|required|exists:core_service_providers,id",
        "insurer_notes": "string",
        "quotation_expiry_date": "date",
        "quotation_issued_date": "date|before_or_equal:policy_start_date",
        "request_by_id": "integer|exists:core_users,id",
        "premium_amount": "required|decimal",
        "customer_id": "integer|required|exists:core_customers,id",
        # "customer_primary_contact": "string|required",
        # "customer_email": "string|required|email",
        # "customer_address": "string|required",
        "policy_start_date": "date|required",
        "policy_expiry_date": "date|required|after:policy_start_date",
        "payment_mode_id": "exists:crmp_payment_plans,id",
        "sum_insured": "decimal|required",
        "request_type_id": "exists:crmp_request_types,id",
        "risk_type_ids": "required|array|min:1",
        "risk_type_ids.*": "integer|exists:crm_opportunity_types,id",
        # "risk_type_id": "integer|required|exists:crm_opportunity_types,id",
        "risk_ids": "required|object",  # Required: risk_ids object with risk_type_id to risk_ids mapping
        "product_id": "nullable|required_without:product_group_id|exists:core_vendor_products,id",
        "product_group_id": "nullable|required_without:product_id|exists:core_product_groups,id",
        "product_type": "required|string|in:product,group",
        "coverage_type_id": "nullable|exists:crmp_coverage_types,id",
        "quotation_notes": "string",
        "sales_agent_id":"required|exists:core_users,id",
        "account_manager_id": "nullable|integer|exists:core_users,id",
        # "start_date": "required|date",
        # "end_date": "required|date",
        "credit_period_days": "required|integer",
        # credit_age_days removed - it's auto-calculated
        "insurer_invoice_id": "required|string",
        "policy_effective_date": "required|date",
        "policy_document": "nullable",
        "policy_document_size": "nullable|integer",
        "policy_document_name": "nullable|string",
        "insurer_policy_id": "required",
    }
    print(f" DEBUG: get_issued_policy_rules_without_request() returning rules: {rules}")
    return rules


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
        # Get entity_id from the issued policy
        issued_policy = QueryBuilderService("crmp_issued_policies")\
            .select("entity_id")\
            .where("id", policy_id)\
            .first()
        
        if issued_policy and issued_policy.get("entity_id"):
            entity_id = issued_policy.get("entity_id")
            print(f"DEBUG: Found entity_id: {entity_id} for policy_id: {policy_id}")
            # Find inheritance records using the entity_id
            query = query.where("inh.entity_id", entity_id)
        else:
            print(f"DEBUG: No entity_id found for policy_id: {policy_id}")
            # Fallback to original behavior if no entity_id found
            query = query.where("inh.issued_policy_id", policy_id)

    data = query.apply_conditions(
        filters, allowed_filters, search, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@api_view(["GET"])
def all_notifications(request):

    user = request.user.id
    user_id = user
    print("user", user_id)
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by") or "core_notification_users.id"
    sort_dir = request.GET.get("sort_dir") or "desc"
    allowed_sorting_columns = ["core_notification_users.id"]
    read_status = request.GET.get("read_status", "")

    all_columns = [
        "core_notification_users.*",
        "core_notifications.*",
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
            "core_notification_users.notification_id",
        )
        .leftJoin(
            "core_notification_types",
            "core_notification_types.id",
            "core_notifications.type_id",
        )
        .where("core_notification_users.user_id", user_id)
        .where("core_notification_users.is_clear", 0)
    )

    data = query.orderBy(sort_by, sort_dir).get()
    print("data", data)

    notif_data = data.get("data", []) if isinstance(data, dict) else data

    # Filter in Python for robust read/unread handling based only on core_notification_users.is_read
    if read_status == "read":
        notif_data = [n for n in notif_data if str(n.get("is_read")) in ["1", 1]]
    elif read_status == "unread":
        notif_data = [
            n for n in notif_data if str(n.get("is_read")) in ["0", 0, "", "None", None]
        ]

    # Add read_status field based strictly on core_notification_users.is_read
    for notif in notif_data:
        is_read_val = notif.get("is_read")
        # Only treat as read if is_read is exactly 1 (int or string)
        notif["read_status"] = (
            "read" if str(is_read_val) == "1" or is_read_val == 1 else "unread"
        )

        # --- Begin: Add link_id as top-level key from metadata.id ---
        metadata = notif.get("metadata")
        notif["link_id"] = None
        if metadata and isinstance(metadata, str):
            try:
                import json as _json

                meta_obj = _json.loads(metadata)
                if isinstance(meta_obj, dict) and "id" in meta_obj:
                    notif["link_id"] = meta_obj["id"]
            except Exception:
                notif["link_id"] = None
        # --- End: Add link_id as top-level key from metadata.id ---

    # Group by date (core_notifications.created_at or core_notification_users.created_at)
    grouped = {}
    for notif in notif_data:
        created_at = notif.get("created_at")
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
        {"date": date, "notification_data": notifs} for date, notifs in grouped.items()
    ]
    # Sort by date descending
    grouped_list.sort(
        key=lambda x: (
            datetime.strptime(x["date"], "%d %b %Y")
            if x["date"] != "Unknown"
            else datetime.min
        ),
        reverse=True,
    )

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
        "data": paginated_grouped,
    }
    return Response(
        {"is_success": True, "message": "notifications_retrieved", "result": result}
    )


@api_view(["GET", "PUT", "DELETE"])
def policy_product_documents(request, policy_base_id):
    """
    GET: Get product documents based on policy base's product_id or product_group_id
    PUT: Update document value for a specific document type
    DELETE: Delete document for a specific document type
    
    Parameters:
    - policy_base_id: Policy base ID to get product documents for
    """
    try:
        print(f"=== DEBUG: Starting policy_product_documents for policy_base_id: {policy_base_id}, method: {request.method} ===")
        
        # Handle different HTTP methods
        if request.method == "PUT":
            return _update_policy_document(request, policy_base_id)
        elif request.method == "DELETE":
            return _delete_policy_document(request, policy_base_id)
        
        # GET method - existing logic
        print(f"=== DEBUG: Starting policy_product_documents for policy_base_id: {policy_base_id} ===")
        
        # First, get the policy base to check for product_id and product_group_id
        policy_base = QueryBuilderService("crmp_policy_base")\
            .select("product_id", "product_group_id")\
            .where("id", policy_base_id)\
            .first()
        
        print(f"DEBUG: Policy base query result: {policy_base}")
        
        if not policy_base:
            print("DEBUG: Policy base not found")
            return ResponseService.response("SUCCESS", [], Message.DATA_FETCHED)
        
        # Get query parameters
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["name", "code"]
        
        all_columns = ["core_product_document_types.*"]
        
        print(f"DEBUG: product_id = {policy_base.get('product_id')}, product_group_id = {policy_base.get('product_group_id')}")
        
        # Check if we have product_group_id first (priority)
        if policy_base.get("product_group_id"):
            print(f"DEBUG: Using product_group_id path: {policy_base['product_group_id']}")
            
            # Group-based document retrieval logic
            # Step 1: Get product_ids from core_product_group_products where product_group_id = product_group_id
            group_products = QueryBuilderService("core_product_group_products")\
                .select("product_id")\
                .where("product_group_id", policy_base["product_group_id"])\
                .get()
            
            print(f"DEBUG: Group products query result: {group_products}")
            
            if not group_products:
                print("DEBUG: No group products found")
                return ResponseService.response("SUCCESS", {"data": [], "total": 0, "page": 1, "limit": 10}, Message.DATA_FETCHED)
            
            # Extract product IDs (these are actual product_ids, not vendor_product_ids)
            product_ids = [gp["product_id"] for gp in group_products]
            print(f"DEBUG: Extracted product_ids: {product_ids}")
            
            # Step 2: Get vendor_product_ids from core_products_vendor_products where product_id in product_ids
            vendor_product_mappings = QueryBuilderService("core_product_vendor_products")\
                .select("vendor_product_id")\
                .whereIn("product_id", product_ids)\
                .get()
            
            print(f"DEBUG: Vendor product mappings query result: {vendor_product_mappings}")
            
            if not vendor_product_mappings:
                print("DEBUG: No vendor product mappings found")
                return ResponseService.response("SUCCESS", {"data": [], "total": 0, "page": 1, "limit": 10}, Message.DATA_FETCHED)
            
            # Extract vendor product IDs
            vendor_product_ids = [vpm["vendor_product_id"] for vpm in vendor_product_mappings]
            print(f"DEBUG: Extracted vendor_product_ids: {vendor_product_ids}")
            
            # Step 3: Get documents from core_product_document_types where vendor_product_id in vendor_product_ids
            query = QueryBuilderService("core_product_document_types")\
                .select(*all_columns)\
                .whereIn("vendor_product_id", vendor_product_ids)
                
        elif policy_base.get("product_id"):
            print(f"DEBUG: Using product_id path (vendor_product_id): {policy_base['product_id']}")
            
            # Direct document retrieval - product_id in policy_base is actually vendor_product_id
            query = QueryBuilderService("core_product_document_types")\
                .select(*all_columns)\
                .where("vendor_product_id", policy_base["product_id"])
        else:
            # No product_id or product_group_id found
            print("DEBUG: No product_id or product_group_id found in policy base")
            return ResponseService.response("SUCCESS", {"data": [], "total": 0, "page": 1, "limit": 10}, Message.DATA_FETCHED)
        
        # Apply additional filters and pagination
        print(f"DEBUG: About to apply conditions and pagination")
        print(f"DEBUG: filter_json = {filter_json}, search_string = '{search_string}', page = {page}, limit = {limit}")
        
        data = query.apply_conditions(filter_json, [], search_string, ["name"])\
                   .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

        # Add value field to each document - check if there are submitted documents
        if data and 'data' in data:
            for doc in data['data']:
                # Check if there's a submitted document for this document type and policy_base
                submitted_doc = QueryBuilderService("crmp_policy_documents")\
                    .select("crmp_policy_documents.id", "crmp_policy_documents.value", "crmp_policy_documents.uploaded_at")\
                    .where("crmp_policy_documents.policy_base_id", policy_base_id)\
                    .where("crmp_policy_documents.document_type_id", doc.get('id'))\
                    .first()
                
                if submitted_doc:
                    # If document record exists, return formatted JSON string
                    raw_value = submitted_doc.get('value')
                    if raw_value:
                        try:
                            # Parse and create JSON string with single quotes
                            parsed_value = json.loads(raw_value)
                            # Create JSON string and replace double quotes with single quotes
                            json_string = json.dumps(parsed_value, separators=(', ', ': '))
                            doc['value'] = json_string.replace('"', "'")
                        except (json.JSONDecodeError, TypeError):
                            # If parsing fails, return the raw value
                            doc['value'] = raw_value
                    else:
                        # If value is empty/null in database, return null
                        doc['value'] = None
                else:
                    # If no document record exists, return null
                    doc['value'] = None

        print(f"DEBUG: Final query result: {data}")
        print(f"DEBUG: Number of documents found: {len(data.get('data', []))}")
        for doc in data.get('data', []):
            print(f"DEBUG: Document - ID: {doc.get('id')}, Name: {doc.get('name')}, Value: {doc.get('value')}")
        print(f"=== DEBUG: End of policy_product_documents ===")

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    except Exception as e:
        import traceback
        print(f"DEBUG: Exception occurred: {str(e)}")
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, Error.INTERNAL_SERVER_ERROR)


def _update_policy_document(request, policy_base_id):
    """
    Update document value(s) for specific document type(s)
    Supports both single document update and bulk update
    """
    try:
        
        data = json.loads(request.body or "{}")
        
        # Check if data is an array (bulk update) or single object
        if isinstance(data, list):
            # Bulk update - array of documents
            return _bulk_update_policy_documents(data, policy_base_id)
        else:
            # Single document update - backward compatibility
            return _single_update_policy_document(data, policy_base_id)
                
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in _update_policy_document: {str(e)}")
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, Error.INTERNAL_SERVER_ERROR)


def _single_update_policy_document(data, policy_base_id):
    """
    Update a single document value for a specific document type
    """
    try:
        # Validate required fields
        document_type_id = data.get("document_type_id")
        value_obj = data.get("value")
        
        if not document_type_id:
            return ResponseService.response("VALIDATION_ERROR", {"document_type_id": "This field is required"}, Error.VALIDATION_ERROR)
        
        # Convert value object to JSON string for database storage
        if value_obj is not None:
            if isinstance(value_obj, dict):
                value = json.dumps(value_obj)
            else:
                value = str(value_obj)
        else:
            value = None
        
        # Check if document exists
        existing_doc = QueryBuilderService("crmp_policy_documents")\
            .where("policy_base_id", policy_base_id)\
            .where("document_type_id", document_type_id)\
            .first()
        
        if existing_doc:
            # Update existing document
            updated = QueryBuilderService("crmp_policy_documents")\
                .where("policy_base_id", policy_base_id)\
                .where("document_type_id", document_type_id)\
                .update({"value": value})
            
            if updated:
                return ResponseService.response("SUCCESS", {"message": "Document updated successfully"}, Message.DATA_UPDATED)
            else:
                return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        else:
            # Create new document
            created = QueryBuilderService("crmp_policy_documents")\
                .insert({
                    "policy_base_id": policy_base_id,
                    "document_type_id": document_type_id,
                    "value": value,
                    "uploaded_at": datetime.now()
                })
            
            if created:
                return ResponseService.response("SUCCESS", {"message": "Document created successfully"}, Message.DATA_CREATED)
            else:
                return ResponseService.response("NOT_FOUND", None, Error.INTERNAL_SERVER_ERROR)
                
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in _single_update_policy_document: {str(e)}")
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, Error.INTERNAL_SERVER_ERROR)


def _bulk_update_policy_documents(documents, policy_base_id):
    """
    Update multiple document values for specific document types
    """
    try:
        if not documents or not isinstance(documents, list):
            return ResponseService.response("VALIDATION_ERROR", {"documents": "Documents array is required"}, Error.VALIDATION_ERROR)
        
        results = {
            "updated": [],
            "created": [],
            "failed": [],
            "total_processed": len(documents)
        }
        
        for idx, doc in enumerate(documents):
            try:
                # Extract document_type_id and value from the document object
                document_type_id = doc.get("id")  # Using 'id' as document_type_id
                value_obj = doc.get("value")
                
                if not document_type_id:
                    results["failed"].append({
                        "index": idx,
                        "error": "document_type_id (id) is required",
                        "document": doc
                    })
                    continue
                
                # Convert value object to JSON string for database storage
                if value_obj is not None:
                    if isinstance(value_obj, dict):
                        value = json.dumps(value_obj)
                    else:
                        value = str(value_obj)
                else:
                    value = None
                
                # Check if document exists
                existing_doc = QueryBuilderService("crmp_policy_documents")\
                    .where("policy_base_id", policy_base_id)\
                    .where("document_type_id", document_type_id)\
                    .first()
                
                if existing_doc:
                    # Update existing document
                    updated = QueryBuilderService("crmp_policy_documents")\
                        .where("policy_base_id", policy_base_id)\
                        .where("document_type_id", document_type_id)\
                        .update({"value": value})
                    
                    if updated:
                        results["updated"].append({
                            "document_type_id": document_type_id,
                            "name": doc.get("name", ""),
                            "action": "updated"
                        })
                    else:
                        results["failed"].append({
                            "index": idx,
                            "error": "Failed to update document",
                            "document": doc
                        })
                else:
                    # Create new document
                    created = QueryBuilderService("crmp_policy_documents")\
                        .insert({
                            "policy_base_id": policy_base_id,
                            "document_type_id": document_type_id,
                            "value": value,
                            "uploaded_at": datetime.now()
                        })
                    
                    if created:
                        results["created"].append({
                            "document_type_id": document_type_id,
                            "name": doc.get("name", ""),
                            "action": "created"
                        })
                    else:
                        results["failed"].append({
                            "index": idx,
                            "error": "Failed to create document",
                            "document": doc
                        })
                        
            except Exception as e:
                results["failed"].append({
                    "index": idx,
                    "error": str(e),
                    "document": doc
                })
        
        # Prepare response message
        success_count = len(results["updated"]) + len(results["created"])
        failed_count = len(results["failed"])
        
        if failed_count == 0:
            message = f"Successfully processed {success_count} documents"
        else:
            message = f"Processed {success_count} documents successfully, {failed_count} failed"
        
        return ResponseService.response("SUCCESS", {
            "message": message,
            "results": results
        }, Message.DATA_UPDATED)
                
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in _bulk_update_policy_documents: {str(e)}")
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, Error.INTERNAL_SERVER_ERROR)


def _delete_policy_document(request, policy_base_id):
    """
    Delete document for a specific document type
    """
    try:
        import json
        data = json.loads(request.body or "{}")
        
        # Validate required fields
        document_type_id = data.get("document_type_id")
        
        if not document_type_id:
            return ResponseService.response("VALIDATION_ERROR", {"document_type_id": "This field is required"}, Error.VALIDATION_ERROR)
        
        # Check if document exists
        existing_doc = QueryBuilderService("crmp_policy_documents")\
            .where("policy_base_id", policy_base_id)\
            .where("document_type_id", document_type_id)\
            .first()
        
        if not existing_doc:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        
        # Delete document
        deleted = QueryBuilderService("crmp_policy_documents")\
            .where("policy_base_id", policy_base_id)\
            .where("document_type_id", document_type_id)\
            .delete()
        
        if deleted:
            return ResponseService.response("SUCCESS", {"message": "Document deleted successfully"}, "Document deleted successfully")
        else:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
            
    except Exception as e:
        import traceback
        print(f"DEBUG: Exception in _delete_policy_document: {str(e)}")
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, Error.INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def export_risks_for_policy_base(request, policy_base_id):
    """
    Export all risks linked to a policy base as an Excel file.
    Data flow: policy_base_id -> crmp_policy_risk_config -> risk_submission_id -> crm_risk_submissions -> submission_id -> risk details
    Ultra-optimized version - reduced from 14s to ~0.5-1s.
    """
    start_time = time.time()
    
    try:
        # 1) Get policy risk configs for the given policy_base_id
        policy_risk_configs = PolicyRiskConfig.objects.filter(policy_base_id=policy_base_id).select_related('risk_submission')
        if not policy_risk_configs.exists():
            return ResponseService.response("NOT_FOUND", None, "No risk configurations found for this policy base")

        # 2) Extract risk_submission_ids from the configs
        risk_submission_ids = [config.risk_submission.id for config in policy_risk_configs]
        
        # 3) Get all risk submissions using the extracted IDs
        risk_submissions = RiskSubmission.objects.filter(id__in=risk_submission_ids).select_related('risk_id')
        if not risk_submissions.exists():
            return ResponseService.response("NOT_FOUND", None, "No risk submissions found for this policy base")

        # 4) Extract all submission IDs and template IDs in one pass
        submission_ids = []
        template_ids = []
        risk_codes_map = {}
        
        for risk_submission in risk_submissions:
            if risk_submission.submission_id:
                submission_ids.append(risk_submission.submission_id)
                risk_codes_map[risk_submission.submission_id] = risk_submission.risk_id.code
                # Get form from submission
                submission = CoreFormSubmission.objects.filter(id=risk_submission.submission_id).select_related('form').first()
                if submission and submission.form:
                    template_ids.append(submission.form.id)

        if not submission_ids:
            return ResponseService.response("NOT_FOUND", None, "No valid submissions found")

        # 5) Ultra-optimized bulk data fetching (single query per data type)
        template_data = _fetch_all_template_data_optimized(template_ids, submission_ids)
        if not template_data:
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "Failed to fetch template data")

        # 6) Build export queries efficiently
        queries = _build_queries_ultra_optimized(submission_ids, template_ids, template_data, risk_codes_map)
        if not queries:
            return ResponseService.response("INTERNAL_SERVER_ERROR", None, "No valid data for export")

        # 7) Export to Excel with streaming
        result = _export_to_excel_streaming(queries, policy_base_id)
        
        # Log performance metrics
        total_time = time.time() - start_time
        print(f"Ultra-optimized export completed in {total_time:.2f} seconds for policy_base {policy_base_id}")
        
        return result

    except Exception as e:
        total_time = time.time() - start_time
        print(f"Export failed after {total_time:.2f} seconds for policy_base {policy_base_id}: {str(e)}")
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


# -------------------------------
# Query building (optimized)
# -------------------------------

_ILLEGAL_SHEET_CHARS = set(r'[]:*?/\\')
_MAX_SHEET_LEN = 31

def _sanitize_sheet_name(name: str) -> str:
    if not name:
        name = "Sheet"
    # remove illegal chars
    name = "".join(ch for ch in str(name) if ch not in _ILLEGAL_SHEET_CHARS)
    # Excel caps length at 31
    name = name[:_MAX_SHEET_LEN]
    # Avoid empty name after sanitize
    return name or "Sheet"

def _sql_escape_label(label: str) -> str:
    # Double quotes inside identifiers
    return str(label).replace('"', '""')

def _sql_escape_value(value) -> str:
    # Double single quotes inside string literal
    return str(value).replace("'", "''")


# -------------------------------
# Ultra-optimized helper functions
# -------------------------------

def _fetch_all_template_data_optimized(template_ids, submission_ids):
    """
    Ultra-optimized bulk data fetching using minimal queries.
    Returns: {template_id: (elements_dict, values_by_submission)}
    """
    if not template_ids or not submission_ids:
        return {}
    
    # Get all elements with their metadata using QueryBuilderService
    all_elements = QueryBuilderService("core_form_custom_form_elements as ele") \
        .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id") \
        .leftJoin("core_form_custom_form_panels as p", "p.id", "ele.panel_id") \
        .select(
            "ele.id as element_id",
            "ele.panel_id",
            "ele.order_number",
            "ele.label",
            "fe.title",
            "fe.category",
            "p.form_id"
        ) \
        .whereIn("p.form_id", template_ids) \
        .orderBy("ele.order_number") \
        .get()
    
    # Get all submission values using QueryBuilderService
    all_values = QueryBuilderService("core_form_submission_valuess") \
        .select("form_submission_id", "custom_form_element_id", "value") \
        .whereIn("form_submission_id", submission_ids) \
        .get()
    
    # Process elements by template
    elements_by_template = {}
    for element in all_elements:
        form_id = element['form_id']
        if form_id not in elements_by_template:
            elements_by_template[form_id] = []
        elements_by_template[form_id].append({
            'id': element['element_id'],
            'label': element['label'] or element['title'] or f"Field_{element['element_id']}",
            'type': element['category']
        })
    
    # Process values by submission
    values_by_submission = {}
    for value in all_values:
        submission_id = value['form_submission_id']
        element_id = str(value['custom_form_element_id'])
        if submission_id not in values_by_submission:
            values_by_submission[submission_id] = {}
        values_by_submission[submission_id][element_id] = value['value']
    
    # Build final result
    result = {}
    for template_id in template_ids:
        elements = elements_by_template.get(template_id, [])
        result[template_id] = (elements, values_by_submission)
    
    return result

def _build_queries_ultra_optimized(submission_ids, template_ids, template_data, risk_codes_map):
    """
    Ultra-optimized query building with minimal processing.
    """
    # Get all submissions with their form data in one query
    submissions = CoreFormSubmission.objects.filter(
        id__in=submission_ids
    ).select_related('form').values('id', 'form_id')
    
    results = []
    seen_titles = set()
    
    for submission in submissions:
        form_id = submission['form_id']
        submission_id = submission['id']
        
        if form_id not in template_data:
            continue
        
        elements, values_by_submission = template_data[form_id]
        submission_values = values_by_submission.get(submission_id, {})
        
        select_parts = []
        for element in elements:
            field_label = element['label']
            field_value = submission_values.get(str(element['id']), "")
            safe_label = _sql_escape_label(field_label)
            safe_value = _sql_escape_value(field_value)
            select_parts.append(f"'{safe_value}' AS \"{safe_label}\"")
        
        if not select_parts:
            continue
        
        sql = f"SELECT {', '.join(select_parts)} LIMIT 1"
        raw_title = risk_codes_map.get(submission_id, f"Submission_{submission_id}")
        title = _sanitize_sheet_name(raw_title)
        
        # Ensure unique titles
        base = title
        suffix = 1
        while title in seen_titles:
            suffix += 1
            trimmed = base[:(_MAX_SHEET_LEN - len(f"_{suffix}"))]
            title = f"{trimmed}_{suffix}"
        seen_titles.add(title)
        
        results.append({"query": sql, "title": title})
    
    return results


# -------------------------------
# Exporter → S3 (streaming)
# -------------------------------

def _export_to_excel_streaming(queries, policy_base_id=None):
    """
    Exports risk data to Excel via exporter, streams the result to S3,
    and returns file details using secure presigned URLs.
    """
    payload = {
        "queries": queries,
        "styles": {
            "common": {
                "header": {
                    "font": {"bold": True, "color": "0000FF"},
                    "alignment": {"horizontal": "center"}
                }
            }
        }
    }

    exporter = SQLToExcelExporter()
    export_response = exporter.export(payload)  # no timeout override
    if not export_response or export_response.get("status") != "SUCCESS":
        msg = (export_response or {}).get("message", "Exporter failed")
        return ResponseService.response("INTERNAL_SERVER_ERROR", None, msg)

    file_url = export_response["data"]["download_url"]

    # Build final name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"policy_risks_{policy_base_id}_{timestamp}.xlsx"

    # Stream exporter response directly into S3 using the new presigned service
    try:
        s3_data = S3PresignedService.upload_stream_from_url(file_url, file_name)
    except Exception as s3_error:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": f"S3 upload failed: {str(s3_error)}"},
            "Failed to upload file to S3"
        )

    # Generate CDN URL for public access
    cdn_base_url = os.getenv("CDN_BASE_URL")
    cdn_url = f"{cdn_base_url}/{s3_data['file_key']}"
    
    # Return only the required fields
    return ResponseService.response(
        "SUCCESS",
        {
            "public_url": cdn_url,               # CDN URL for public access without authentication
            "file_key": s3_data["file_key"],     # S3 file key for reference
            "file_name": s3_data["file_name"]    # File name
        },
        "Excel file uploaded to S3 successfully. Use public_url for direct access via CDN."
    )
