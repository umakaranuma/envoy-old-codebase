from rest_framework.decorators import api_view
from envoy.models.service_provider_contact import ServiceProviderContact
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json
from envoy.models.contact import Contact
from django.db import transaction

@api_view(["GET"])
def sp_products(request, sp_id):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        
        all_columns = [
            "core_vendor_products.*",
            "crm_opportunity_types.title as native_risk_type",
            "product_risk.title as partner_risk_type",
            "crm_opportunity_types.id as native_risk_type_id",           
            "product_risk.id as partner_risk_type_id",
            # "core_service_providers.name as insurer",
        ]
        
        allowed_sorting_columns = ["id", "product_name", "insurer"]
        
        products = (
            QueryBuilderService("core_vendor_products")
            .leftJoin("crm_opportunity_types as product_risk", "core_vendor_products.category_id", "product_risk.id")
            .leftJoin("core_product_vendor_products", "core_vendor_products.id", "core_product_vendor_products.vendor_product_id")
            .leftJoin("core_products", "core_product_vendor_products.product_id", "core_products.id")
            .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
            .leftJoin("crm_opportunity_types", "core_products.category_id", "crm_opportunity_types.id")
            .select(*all_columns)
            .where("core_vendor_products.vendor_id", sp_id)
            .apply_conditions(filter_json, [], search_string, ["product_name", "insurer"])
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )
        return ResponseService.response("SUCCESS", products, "Products retrieved successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(["GET"])
def sp_quotation(request, sp_id):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})
        sort_by = request.GET.get("sort_by", "crmq_vendor_response.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "crmq_vendor_response.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        
        # Enhanced columns to include all required data
        all_columns = [
            # Vendor Response (Main quotation data)
            "crmq_vendor_response.id as vendor_response_id",
            "crmq_vendor_response.code as vendor_response_code",
            "crmq_vendor_response.coverage_details",
            "crmq_vendor_response.coverage_details_type",
            "crmq_vendor_response.coverage_details_name",
            "crmq_vendor_response.received_date",
            "crmq_vendor_response.expiry_date",
            "crmq_vendor_response.total_amount",
            "crmq_vendor_response.status as vendor_response_status",
            "crmq_vendor_response.re_request",
            "crmq_vendor_response.version",
            "crmq_vendor_response.created_at as vendor_response_created_at",
            "crmq_vendor_response.updated_at as vendor_response_updated_at",
            "crmq_vendor_response.by_user_id",
            "crmq_vendor_response.quotation_id",
            "crmq_vendor_response.service_provider_id",
            "crmq_vendor_response.vendor_quotation_id",
            
            # Lead/Opportunity data
            "crm_opportunities.id as opportunity_id",
            "crm_opportunities.title as opportunity_title",
            "crm_opportunities.type as opportunity_type",
            "crm_opportunities.contact_number as opportunity_contact_number",
            "crm_opportunities.email as opportunity_email",
            "crm_opportunities.code as opportunity_code",
            "crm_opportunities.last_contacted_date",
            "crm_opportunities.campaign_id",
            "crm_opportunities.remarks as opportunity_remarks",
            "crm_opportunities.sort_index",
            "crm_opportunities.lead_value",
            "crm_opportunities.sale_value",
            "crm_opportunities.account_manager_id",
            "crm_opportunities.channel_id",
            "crm_opportunities.contact_id",
            "crm_opportunities.country_id",
            "crm_opportunities.created_by_id",
            "crm_opportunities.currency_id",
            "crm_opportunities.customer_id",
            "crm_opportunities.entity_id",
            "crm_opportunities.sales_agent_id",
            "crm_opportunities.current_health_id",
            "crm_opportunities.stage_id",
            "crm_opportunities.transaction_type",
            "crm_opportunities.issued_policy_id",
            
            # Account/Customer data
            "core_customers.id as customer_id",
            "core_customers.code as customer_code",
            "core_customers.type as customer_type",
            "core_customers.name as customer_name",
            "core_customers.logo as customer_logo",
            "core_customers.remarks as customer_remarks",
            "core_customers.idp_customer_id",
            "core_customers.portal_id",
            "core_customers.parent_id",
            "core_customers.primary_contact_id",
            "core_customers.entity_id as customer_entity_id",
            "core_customers.is_enrolled",
            
            # Quotation Request data
            "crmq_quotations.id as quotation_id",
            "crmq_quotations.code as quotation_code",
            "crmq_quotations.requested_data",
            "crmq_quotations.customer_id as quotation_customer_id",
            "crmq_quotations.status as quotation_status",
            "crmq_quotations.notes as quotation_notes",
            "crmq_quotations.request_type",
            "crmq_quotations.opportunity_type_id",
            "crmq_quotations.opportunity_id as quotation_opportunity_id",
            "crmq_quotations.entity_id as quotation_entity_id",
            "crmq_quotations.email_data",
            "crmq_quotations.status_id as quotation_status_id",
            
            # Service Provider data
            "core_service_providers.name as service_provider_name",
            "core_service_providers.email as service_provider_email",
            "core_service_providers.contact_no as service_provider_contact_no",
            
            # Status data
            "core_status.name as status_name",
            "crm_opportunity_statuses.name as opportunity_stage_name",
           
        ]
        
        allowed_sorting_columns = [
            "crmq_vendor_response.id", "crmq_vendor_response.code", "crmq_vendor_response.received_date",
            "crmq_vendor_response.expiry_date", "crmq_vendor_response.total_amount", "crmq_vendor_response.status",
            "crm_opportunities.title", "crm_opportunities.code", "core_customers.name", "crmq_quotations.code"
        ]
        
        # Enhanced query with all necessary joins
        quotations = (
            QueryBuilderService("crmq_vendor_response")
            .leftJoin("crmq_quotations", "crmq_vendor_response.quotation_id", "crmq_quotations.id")
            .leftJoin("crm_opportunities", "crmq_quotations.opportunity_id", "crm_opportunities.id")
            .leftJoin("core_customers", "crm_opportunities.customer_id", "core_customers.id")
            .leftJoin("core_service_providers", "crmq_vendor_response.service_provider_id", "core_service_providers.id")
            .leftJoin("core_status", "crmq_quotations.status_id", "core_status.id")
            .leftJoin("crm_opportunity_statuses", "crm_opportunities.stage_id", "crm_opportunity_statuses.id")
            .leftJoin("crm_opportunity_health", "crm_opportunities.current_health_id", "crm_opportunity_health.id")
            .select(*all_columns)
            .where("crmq_vendor_response.service_provider_id", sp_id)
            .apply_conditions(filter_json, [], search_string, ["crmq_vendor_response.code", "crm_opportunities.title", "core_customers.name"])
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )
        
        # Transform the response to include structured objects
        if quotations and "data" in quotations and quotations["data"]:
            for item in quotations["data"]:
                # Structure the response with clear object separation
                item["lead"] = {
                    "id": item.get("opportunity_id"),
                    "title": item.get("opportunity_title"),
                    "type": item.get("opportunity_type"),
                    "contact_number": item.get("opportunity_contact_number"),
                    "email": item.get("opportunity_email"),
                    "code": item.get("opportunity_code"),
                    "last_contacted_date": item.get("last_contacted_date"),
                    "campaign_id": item.get("campaign_id"),
                    "remarks": item.get("opportunity_remarks"),
                    "sort_index": item.get("sort_index"),
                    "lead_value": item.get("lead_value"),
                    "sale_value": item.get("sale_value"),
                    "account_manager_id": item.get("account_manager_id"),
                    "channel_id": item.get("channel_id"),
                    "contact_id": item.get("contact_id"),
                    "country_id": item.get("country_id"),
                    "created_by_id": item.get("created_by_id"),
                    "currency_id": item.get("currency_id"),
                    "customer_id": item.get("customer_id"),
                    "entity_id": item.get("entity_id"),
                    "sales_agent_id": item.get("sales_agent_id"),
                    "current_health_id": item.get("current_health_id"),
                    "stage_id": item.get("stage_id"),
                    "transaction_type": item.get("transaction_type"),
                    "issued_policy_id": item.get("issued_policy_id"),
                    "stage_name": item.get("opportunity_stage_name"),
                    "health_name": item.get("opportunity_health_name")
                }
                
                item["account"] = {
                    "id": item.get("customer_id"),
                    "code": item.get("customer_code"),
                    "type": item.get("customer_type"),
                    "name": item.get("customer_name"),
                    "logo": item.get("customer_logo"),
                    "remarks": item.get("customer_remarks"),
                    "idp_customer_id": item.get("idp_customer_id"),
                    "portal_id": item.get("portal_id"),
                    "parent_id": item.get("parent_id"),
                    "primary_contact_id": item.get("primary_contact_id"),
                    "entity_id": item.get("customer_entity_id"),
                    "is_enrolled": item.get("is_enrolled")
                }
                
                item["quotation_request"] = {
                    "id": item.get("quotation_id"),
                    "code": item.get("quotation_code"),
                    "requested_data": item.get("requested_data"),
                    "customer_id": item.get("quotation_customer_id"),
                    "status": item.get("quotation_status"),
                    "notes": item.get("quotation_notes"),
                    "request_type": item.get("request_type"),
                    "opportunity_type_id": item.get("opportunity_type_id"),
                    "opportunity_id": item.get("quotation_opportunity_id"),
                    "entity_id": item.get("quotation_entity_id"),
                    "email_data": item.get("email_data"),
                    "status_id": item.get("quotation_status_id"),
                    "status_name": item.get("status_name")
                }
                
                item["quotation"] = {
                    "id": item.get("vendor_response_id"),
                    "code": item.get("vendor_response_code"),
                    "coverage_details": item.get("coverage_details"),
                    "coverage_details_type": item.get("coverage_details_type"),
                    "coverage_details_name": item.get("coverage_details_name"),
                    "received_date": item.get("received_date"),
                    "expiry_date": item.get("expiry_date"),
                    "total_amount": item.get("total_amount"),
                    "status": item.get("vendor_response_status"),
                    "re_request": item.get("re_request"),
                    "version": item.get("version"),
                    "created_at": item.get("vendor_response_created_at"),
                    "updated_at": item.get("vendor_response_updated_at"),
                    "by_user_id": item.get("by_user_id"),
                    "quotation_id": item.get("quotation_id"),
                    "service_provider_id": item.get("service_provider_id"),
                    "vendor_quotation_id": item.get("vendor_quotation_id"),
                    "service_provider_name": item.get("service_provider_name"),
                    "service_provider_email": item.get("service_provider_email"),
                    "service_provider_contact_no": item.get("service_provider_contact_no")
                }
                
                # Remove individual fields to avoid duplication
                fields_to_remove = [
                    "opportunity_id", "opportunity_title", "opportunity_type", "opportunity_contact_number",
                    "opportunity_email", "opportunity_code", "last_contacted_date", "campaign_id",
                    "opportunity_remarks", "sort_index", "lead_value", "sale_value", "account_manager_id",
                    "channel_id", "contact_id", "country_id", "created_by_id", "currency_id",
                    "customer_id", "entity_id", "sales_agent_id", "current_health_id", "stage_id",
                    "transaction_type", "issued_policy_id", "opportunity_stage_name", "opportunity_health_name",
                    "customer_code", "customer_type", "customer_name", "customer_logo", "customer_remarks",
                    "idp_customer_id", "portal_id", "parent_id", "primary_contact_id", "customer_entity_id",
                    "is_enrolled", "quotation_id", "quotation_code", "requested_data", "quotation_customer_id",
                    "quotation_status", "quotation_notes", "request_type", "opportunity_type_id",
                    "quotation_opportunity_id", "quotation_entity_id", "email_data", "quotation_status_id",
                    "status_name", "vendor_response_id", "vendor_response_code", "coverage_details",
                    "coverage_details_type", "coverage_details_name", "received_date", "expiry_date",
                    "total_amount", "vendor_response_status", "re_request", "version", "vendor_response_created_at",
                    "vendor_response_updated_at", "by_user_id", "service_provider_id", "vendor_quotation_id",
                    "service_provider_name", "service_provider_email", "service_provider_contact_no"
                ]
                
                for field in fields_to_remove:
                    item.pop(field, None)
        
        return ResponseService.response("SUCCESS", quotations, "Quotations retrieved successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(["GET", "POST"])
def service_provider_contacts_view(request, sp_id):
    if request.method == "GET":
        return list_sp_contacts(request, sp_id)
    elif request.method == "POST":
        return create_sp_contact(request, sp_id)


def list_sp_contacts(request, sp_id):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = [
            "spc.title", "c.name", "c.email", "c.primary_contact", "c.secondary_contact"
        ]
        search_columns = allowed_filters
        sort_by = request.GET.get("sort_by", "spc.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "spc.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        allowed_sorting = [
            "spc.id", "spc.title", "spc.is_primary", "c.name", "c.email", "c.primary_contact"
        ]
        all_columns = [
            "spc.*", 
        ]

        query = (
            QueryBuilderService("core_service_provider_contacts spc")
            .select(*all_columns)
            .where("spc.service_provider_id", sp_id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting, sort_by, sort_dir)
        )
        return ResponseService.response("SUCCESS", query, "Contacts retrieved successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def create_sp_contact(request, sp_id):
    data = json.loads(request.body or "{}")
    data["service_provider_id"] = sp_id  # inject URL param

    rules = {
        "title": "nullable|max:200",
        "name": "required|max:255",
        "primary_contact": "required|max:20",
        "email": "required|email",
        "address": "nullable|max:255",
        "secondary_contact": "nullable|max:20",
        "website_url": "nullable|url",
        "remarks": "nullable|max:1000",
        "role": "nullable|max:100",
        "contact_type": "required|options:primary,secondary,general"
    }
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    # Convert contact_type to is_primary boolean
    contact_type = data["contact_type"]
    if contact_type == "primary":
        is_primary = True
    elif contact_type == "secondary":
        is_primary = False  # Secondary contacts are not primary but have special status
    else:  # general
        is_primary = False

    try:
        with transaction.atomic():
            # If creating a primary or secondary contact, demote existing of same type to 'general'
            if contact_type in ["primary", "secondary"]:
                update_payload = {"contact_type": "general"}
                if contact_type == "primary":
                    update_payload["is_primary"] = False
                QueryBuilderService("core_service_provider_contacts") \
                    .where("service_provider_id", sp_id) \
                    .where("contact_type", contact_type) \
                    .update(update_payload)

            # If this is a primary contact, make all other contacts non-primary (redundant safety)
            if is_primary:
                QueryBuilderService("core_service_provider_contacts")\
                    .where("service_provider_id", sp_id)\
                    .update({"is_primary": False})

            new_contact = ServiceProviderContact.objects.create(
                service_provider_id=sp_id,
                title=data["title"],
                name=data["name"],
                email=data.get("email"),
                primary_contact=data["primary_contact"],
                remarks=data.get("remarks"),
                role=data.get("role"),
                is_primary=is_primary,
                contact_type=contact_type
            )
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

    return ResponseService.response("SUCCESS", {
        "id": new_contact.id,
        "service_provider_id": sp_id,
        "title": new_contact.title,
        "name": new_contact.name,
        "primary_contact": new_contact.primary_contact,
        "email": new_contact.email,
        "remarks": new_contact.remarks,
        "role": new_contact.role,
        "is_primary": new_contact.is_primary,
        "contact_type": new_contact.contact_type,
    }, "default_create_success_msg")


@api_view(["GET", "PUT", "DELETE"])
def service_provider_contact_detail(request, sp_id, id):
    try:
        contact = ServiceProviderContact.objects.get(id=id, service_provider_id=sp_id)
    except ServiceProviderContact.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Contact not found")

    if request.method == "GET":
        return ResponseService.response("SUCCESS", {
            "id": contact.id,
            "title": contact.title,
            "name": contact.name,
            "primary_contact": contact.primary_contact,
            "email": contact.email,
            "remarks": contact.remarks,
            "is_primary": contact.is_primary,
            "role": contact.role,
            "contact_type": contact.contact_type,
            "service_provider_id": contact.service_provider_id
        }, "default_get_success_msg")

    elif request.method == "DELETE":
        # Prevent deletion of primary contact; allow others
        if contact.contact_type in ['primary', 'secondary']:
            return ResponseService.response("NOT_FOUND", None, "prmimary_secondary_contact_delete_error_msg")
        
        contact.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    else:  # PUT
        data = json.loads(request.body or "{}")
        rules = {
            "title": "nullable|max:200",
            "name": "required|max:255",
            "primary_contact": "required|max:20",
            "email": "required|email",
            "address": "nullable|max:255",
            "secondary_contact": "nullable|max:20",
            "website_url": "nullable|url",
            "remarks": "nullable|max:1000",
            "role": "nullable|max:100",
            "contact_type": "required|options:primary,secondary,general"
        }
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Convert contact_type to is_primary boolean
        contact_type = data["contact_type"]
        if contact_type == "primary":
            is_primary = True
        elif contact_type == "secondary":
            is_primary = False  # Secondary contacts are not primary but have special status
        else:  # general
            is_primary = False

        # Handle demotion/primary logic in a transaction
        with transaction.atomic():
            if contact_type == "primary":
                # Demote other primaries to general and clear is_primary
                QueryBuilderService("core_service_provider_contacts")\
                    .where("service_provider_id", sp_id)\
                    .whereNotIn("id", [id])\
                    .where("contact_type", "primary")\
                    .update({"contact_type": "general", "is_primary": False})
            elif contact_type == "secondary":
                # Demote other secondaries to general
                QueryBuilderService("core_service_provider_contacts")\
                    .where("service_provider_id", sp_id)\
                    .whereNotIn("id", [id])\
                    .where("contact_type", "secondary")\
                    .update({"contact_type": "general"})

            contact.title = data["title"]
            contact.name = data["name"]
            contact.primary_contact = data["primary_contact"]
            contact.email = data.get("email")
            contact.remarks = data.get("remarks")
            contact.role = data.get("role")
            contact.contact_type = contact_type
            contact.is_primary = is_primary
            contact.save()

        return ResponseService.response("SUCCESS", {
            "id": contact.id,
            "title": contact.title,
            "name": contact.name,
            "primary_contact": contact.primary_contact,
            "email": contact.email,
            "remarks": contact.remarks,
            "is_primary": contact.is_primary,
            "role": contact.role,
            "contact_type": contact.contact_type,
            "service_provider_id": contact.service_provider_id
        }, "default_update_success_msg")
