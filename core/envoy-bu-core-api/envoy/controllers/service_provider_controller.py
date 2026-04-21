from ast import iter_fields
from rest_framework.decorators import api_view
from envoy.models import ServiceProvider,CoreUserBankDetail
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json
from django.views.decorators.csrf import csrf_exempt
from envoy.models.service_provider_contact import ServiceProviderContact
from django.db import transaction

from services import ActionService, AuthService
from messages import Message, Error


# Helper function to handle query conditions, pagination, sorting
def apply_query_params(query, request, allowed_filters, search_columns, sort_columns):
    filter_json = request.query_params.get("filter", {})
    search_string = request.query_params.get("search", "")
    page = int(request.query_params.get("page", 1))
    limit = int(request.query_params.get("limit", 10))
    sort_by = request.query_params.get("sort_by", "name")
    sort_dir = request.query_params.get("sort_dir", "desc")

    return query.apply_conditions(
        filter_json, allowed_filters, search_string, search_columns
    ).paginate(page, limit, sort_columns, sort_by, sort_dir)




@api_view(["GET", "POST"])
def service_provider_view(request):
    if request.method == "GET":
        return list_service_provider(request)
    elif request.method == "POST":
        return create_service_provider(request)
    

def list_service_provider(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["csp.user_id", "csp.email", "csp.contact_no", "csp.created_at"]
        search_columns = ["csp.name", "csp.email", "csp.address", "csp.website"]
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "csp.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        allowed_sorting_columns = [
            "csp.id", "csp.name", "csp.email", "csp.contact_no", "csp.website", "csp.user_id", "csp.created_at"
        ]

        all_columns = [
            "csp.id", "csp.name", "csp.logo", "csp.address", "csp.contact_no", "csp.email","csp.created_by_id","csp.updated_by_id",
            "csp.website", "csp.fax_no", "csp.user_id","cu.display_name as user_name","cr.name as role_name", "csp.created_at", "csp.updated_at"
        ]

        query = (
            QueryBuilderService("core_service_providers csp")
            .select(*all_columns)
            .leftJoin("core_users as cu", "csp.user_id", "cu.id")
            .leftJoin("core_roles cr","cu.role_id", "cr.id")
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        # Add number_of_products count and primary contact info for each service provider
        if query and "data" in query and query["data"]:
            for item in query["data"]:
                vendor_id = item.get("id")
                if vendor_id:
                    # Get number of products
                    number_of_products = QueryBuilderService("core_vendor_products").where("vendor_id", vendor_id).count()
                    item["number_of_products"] = number_of_products
                    
                    # Get primary contact info
                    primary_contact = QueryBuilderService("core_service_provider_contacts")\
                        .where("service_provider_id", vendor_id)\
                        .where("is_primary", True)\
                        .first()
                    
                    if primary_contact:
                        item["primary_contact"] = {
                            "id": primary_contact.get("id"),
                            "title": primary_contact.get("title"),
                            "name": primary_contact.get("name"),
                            "email": primary_contact.get("email"),
                            "primary_contact": primary_contact.get("primary_contact"),
                            "role": primary_contact.get("role"),
                            "remarks": primary_contact.get("remarks"),
                            "is_primary": primary_contact.get("is_primary")
                        }
                    else:
                        item["primary_contact"] = None
                else:
                    item["number_of_products"] = 0
                    item["primary_contact"] = None

        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



def create_service_provider(request):
    if not request.user.is_authenticated:
        return ResponseService.response("UNAUTHORIZED", None, "Authentication required")

    try:
        data = json.loads(request.body)
        user_id = request.user.id

        # Normalize status_id if empty
        if not data.get("status_id"):
            data["status_id"] = None

        rules = {
            "name": "required|max:255",
            "logo": "nullable",
            "address": "required",
            "contact_number": "required|max:20",
            "email": "required|email",
            "website": "nullable",
            "fax_no": "nullable|max:20",
            "description": "nullable|max:200",
            "status_id": "nullable|exists:core_status,id",

            # Bank details - optional fields
            "account_holder_name": "nullable|max:255",
            "bank_name": "nullable|max:100",
            "bank_branch": "nullable|max:100",
            "account_number": "nullable|max:20",
            "iban_swift_code": "nullable|max:50",
            "payment_gateway_url": "nullable|url",

            # Contact details
            "contact_title": "required|max:200",
            "contact_name": "required|max:255",
            "contact_primary": "required|max:20",
            "contact_email": "nullable|email",
            "contact_remarks": "nullable|max:1000",
            "contact_type" : "required|options:primary,secondary,general",
            "contact_role": "nullable|max:255"
        }

        custom_messages = {
            "status_id.exists": "Invalid status.",
            "email.email": "Invalid email.",
            "website.url": "Invalid website URL.",
            "payment_gateway_url.url": "Invalid payment gateway URL.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Atomic transaction for integrity
        with transaction.atomic():
            service_provider = ServiceProvider.objects.create(
                user_id=user_id,
                name=data["name"],
                logo=data.get("logo"),
                address=data["address"],
                contact_no=data["contact_number"],
                email=data["email"],
                website=data.get("website"),
                fax_no=data.get("fax_no"),
                description=data.get("description"),
                status_id=data.get("status_id"),
                created_by_id=user_id,
                updated_by_id=user_id
            )

            if data["contact_type"] == "primary":
                is_primary = True
            elif data["contact_type"] == "secondary":
                is_primary = False  # Secondary contacts are not primary but have special status
            elif data["contact_type"] == "general":
                is_primary = False

            # Create bank details only if provided
            if any([data.get("account_holder_name"), data.get("bank_name"), data.get("bank_branch"), data.get("account_number")]):
                CoreUserBankDetail.objects.create(
                    user_id=user_id,
                    service_provider=service_provider,
                    account_holder_name=data.get("account_holder_name", ""),
                    bank_name=data.get("bank_name", ""),
                    bank_branch=data.get("bank_branch", ""),
                    account_number=data.get("account_number", ""),
                    iban_swift_code=data.get("iban_swift_code"),
                    payment_gateway_url=data.get("payment_gateway_url"),
                )

            ServiceProviderContact.objects.create(
                role=data.get("contact_role"),
                title=data["contact_title"],
                service_provider=service_provider,
                is_primary=is_primary,
                contact_type=data["contact_type"],
                name=data["contact_name"],
                email=data.get("contact_email"),
                primary_contact=data["contact_primary"],
                remarks=data.get("contact_remarks")
            )

        return ResponseService.response("SUCCESS", {"id": service_provider.id}, "default_create_success_msg")

    except Exception as e:
        # Optional: print or log the error for debugging
        print("Error creating service provider:", e)
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
  

@api_view(["GET", "PUT", "DELETE"])
def service_provider_detail(request, id):
    if request.method == "GET":
        return get_service_provider(request, id)
    elif request.method == "PUT":
        return update_service_provider(request, id)
    elif request.method == "DELETE":
        return delete_service_provider(request, id)


def get_service_provider(request, id):
    try:
        provider = ServiceProvider.objects.get(id=id)
        bank_details = CoreUserBankDetail.objects.filter(service_provider_id=id)
        contact_details = ServiceProviderContact.objects.filter(service_provider_id=id)
        data = {
            "id": provider.id,
            "user_id": provider.user_id,
            "name": provider.name,
            "logo": provider.logo,
            "address": provider.address,
            "contact_no": provider.contact_no,
            "email": provider.email,
            "website": provider.website,
            "fax_no": provider.fax_no,
            "status_id": provider.status_id,
            "description": provider.description,
            "created_by_id": provider.created_by_id,
            "updated_by_id": provider.updated_by_id,
            "bank_details": [
                {
                    "id": b.id,
                    "account_holder_name": b.account_holder_name,
                    "bank_name": b.bank_name,
                    "bank_branch": b.bank_branch,
                    "account_number": b.account_number,
                    "iban_swift_code": b.iban_swift_code,
                    "payment_gateway_url": b.payment_gateway_url,
                } for b in bank_details
            ],
            "contact_details": [
                {
                    "id": c.id,
                    "role": c.role,
                    "title": c.title,
                    "is_primary": c.is_primary,
                    "name": c.name,
                    "email": c.email,
                    "primary_contact": c.primary_contact,
                    "remarks": c.remarks
                } for c in contact_details
            ]
        }
        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")
    except ServiceProvider.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")


def update_service_provider(request, id):
    """Update service provider with simplified validation."""
    try:
        data = json.loads(request.body or "{}")
        provider = ServiceProvider.objects.get(id=id)
        
        # Validate all fields directly
        rules = {
            "name": "required|max:255",
            "address": "required",
            "contact_number": "required|max:20",
            "email": "required|email",
            "website": "nullable|url",
            "fax_no": "nullable|max:20",
            "account_holder_name": "nullable|max:255",
            "bank_name": "nullable|max:100",
            "bank_branch": "nullable|max:100",
            "account_number": "nullable|max:20",
            "iban_swift_code": "nullable|max:50",
            "payment_gateway_url": "nullable|url",
            "contact_title": "required|max:200",
            "contact_name": "required|max:255",
            "contact_primary": "required|max:20",
            "contact_email": "nullable|email",
            "contact_remarks": "nullable|max:1000",
            "contact_role": "nullable|max:255",
            "contact_type": "required|options:primary,secondary,general"
        }
        
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
        
        # Execute update transaction
        with transaction.atomic():
            # Update core service provider
            provider.name = data["name"]
            provider.logo = data.get("logo", provider.logo)
            provider.address = data["address"]
            provider.contact_no = data["contact_number"]
            provider.email = data["email"]
            provider.website = data.get("website", provider.website)
            provider.fax_no = data.get("fax_no", provider.fax_no)
            provider.status_id = data.get("status_id", provider.status_id)
            provider.description = data.get("description", provider.description)
            provider.updated_by_id = request.user.id if request.user.is_authenticated else None
            provider.save()
            
            # Update bank details only if provided
            if any([data.get("account_holder_name"), data.get("bank_name"), data.get("bank_branch"), data.get("account_number")]):
                bank_detail, created = CoreUserBankDetail.objects.get_or_create(
                    service_provider=provider,
                    defaults={
                        'user': provider.user,
                        'account_holder_name': data.get("account_holder_name", ""),
                        'bank_name': data.get("bank_name", ""),
                        'bank_branch': data.get("bank_branch", ""),
                        'account_number': data.get("account_number", ""),
                        'iban_swift_code': data.get("iban_swift_code"),
                        'payment_gateway_url': data.get("payment_gateway_url"),
                    }
                )
                
                if not created:
                    bank_detail.account_holder_name = data.get("account_holder_name", bank_detail.account_holder_name)
                    bank_detail.bank_name = data.get("bank_name", bank_detail.bank_name)
                    bank_detail.bank_branch = data.get("bank_branch", bank_detail.bank_branch)
                    bank_detail.account_number = data.get("account_number", bank_detail.account_number)
                    bank_detail.iban_swift_code = data.get("iban_swift_code", bank_detail.iban_swift_code)
                    bank_detail.payment_gateway_url = data.get("payment_gateway_url", bank_detail.payment_gateway_url)
                    bank_detail.save()
            
            # Convert contact_type to is_primary boolean
            contact_type = data["contact_type"]
            if contact_type == "primary":
                is_primary = True
            elif contact_type == "secondary":
                is_primary = False
            else:  # general
                is_primary = False

            # Handle primary contact logic
            if is_primary:
                # If this is being set as primary, make all other contacts non-primary
                ServiceProviderContact.objects.filter(service_provider=provider).update(is_primary=False)

            # Get or create contact - use a more flexible approach
            # First try to get existing contact by service provider (assuming one contact per service provider in this context)
            contact = ServiceProviderContact.objects.filter(service_provider=provider).first()
            
            if contact:
                # Update existing contact
                contact.title = data["contact_title"]
                contact.name = data["contact_name"]
                contact.email = data.get("contact_email")
                contact.primary_contact = data["contact_primary"]
                contact.remarks = data.get("contact_remarks")
                contact.role = data.get("contact_role")
                contact.contact_type = contact_type
                contact.is_primary = is_primary
                contact.save()
            else:
                # Create new contact if none exists
                contact = ServiceProviderContact.objects.create(
                    service_provider=provider,
                    title=data["contact_title"],
                    name=data["contact_name"],
                    email=data.get("contact_email"),
                    primary_contact=data["contact_primary"],
                    remarks=data.get("contact_remarks"),
                    role=data.get("contact_role"),
                    contact_type=contact_type,
                    is_primary=is_primary
                )
        
        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
        
    except ServiceProvider.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")





def delete_service_provider(request, id):
    try:
        provider = ServiceProvider.objects.filter(id=id).first()
        if not provider:
            return ResponseService.response("NOT_FOUND", None, "data_not_found")
        provider.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



def get_received_quotations(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})
        sp_id = request.GET.get("spId", "")


        allowed_filters = [
            "q.code", "q.status", "q.request_type","cspq.service_provider_id"
        ]

        search_columns = [
            "q.code", "q.status"
        ]

        sort_by = request.GET.get("sort_by", "cspq.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_sorting_columns = [
            "cspq.id", "cspq.service_provider_id", "cspq.quotation_id", "cspq.opportunity_id",
            "cspq.is_received", "cspq.is_sent", "cspq.is_shortlisted", "cspq.is_draft", "cspq.version", "cspq.status",
            "q.code", "q.status", "q.request_type", "q.notes",
            "sp.name", "sp.email", "sp.contact_no", "sp.website"
        ]

        all_columns = [
            "cspq.id", "cspq.service_provider_id", "cspq.quotation_id", "cspq.opportunity_id",
            "cspq.is_received", "cspq.is_sent", "cspq.is_shortlisted", "cspq.is_draft", "cspq.version", "cspq.status",
            "q.code as quotation_code", "q.status as quotation_status", "q.request_type", "q.notes",
            "sp.name as service_provider_name"
        ]

       # Build query
        query_builder = (
            QueryBuilderService("crmq_quotation_service_providers cspq")
            .select(*all_columns)
            .leftJoin("core_service_providers as sp", "cspq.service_provider_id", "sp.id")
            .leftJoin("crmq_quotations as q", "cspq.quotation_id", "q.id")
        )

        # Apply fixed condition
        query_builder = query_builder.where("cspq.is_received", 1)

        # Apply optional service provider filter
        if sp_id:
            query_builder = query_builder.where("cspq.service_provider_id", int(sp_id))

        # Apply search & filter, then paginate and execute
        query_result = (
            query_builder
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query_result, "data_retrieved_successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



@api_view(['GET'])
def get_service_providers_by_category(request):
    try:
        category_ids = request.GET.get("category_ids")
        
        if not category_ids:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "Category IDs are required"},
                "VALIDATION_ERROR"
            )

        # Parse comma-separated string to list of ints
        category_ids = [int(cid.strip()) for cid in category_ids.split(",") if cid.strip().isdigit()]

        if not category_ids:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "No valid category IDs provided"},
                "VALIDATION_ERROR"
            )

        # Query service providers matching any of the category IDs
        service_providers = (
            QueryBuilderService("core_service_providers as sp")
            .leftJoin("core_vendor_products as vp", "vp.vendor_id", "sp.id")
            .select(
                "sp.id",
                "sp.name",
                "sp.description",
                "sp.status_id",
                "GROUP_CONCAT(DISTINCT vp.category_id) AS category_ids"
            )
            .whereIn("vp.category_id", category_ids)
            .groupBy("sp.id", "sp.name", "sp.description", "sp.status_id")
            .get()
        )


        return ResponseService.response(
            "SUCCESS",
            service_providers,
            "Service Providers retrieved successfully"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to retrieve service providers"
        )





@csrf_exempt
@api_view(["GET"])
def request_insurers(request):

    # Get the new parameters
    product_id = request.query_params.get("product_id")
    group_id = request.query_params.get("group_id")
    risk_type_ids = request.query_params.get("risk_type_ids")

    # Check if either parameter is provided (ignore "undefined" and empty values)
    if (product_id and product_id.strip() and product_id != "undefined") or (group_id and group_id.strip() and group_id != "undefined"):
        # Logic for getting service providers based on product_id or group_id
        # Extract query parameters for filtering and search
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        sort_by = request.GET.get("sort_by", "name")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "name" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        
        allowed_filters = ["name", "type_id"]
        allowed_searching_columns = ["core_service_providers.name"]
        
        if product_id and product_id.strip() and product_id != "undefined":
            # If product_id is provided: check core_vendor_products -> core_service_providers
            try:
                # Get vendor_id from core_vendor_products where id = product_id
                vendor_product = QueryBuilderService("core_vendor_products")\
                    .select("vendor_id")\
                    .where("id", int(product_id))\
                    .first()
                
                if not vendor_product:
                    return ResponseService.response("NOT_FOUND", [], Error.NOT_FOUND)
                
                vendor_id = vendor_product["vendor_id"]
                
                # Get service provider details from core_service_providers with search and sorting
                query = (
                    QueryBuilderService("core_service_providers")
                    .where("id", vendor_id)
                    .apply_conditions(filter_json, allowed_filters, search_string, allowed_searching_columns)
                )
                
                # Apply sorting if provided
                if sort_by:
                    query = query.orderBy(sort_by, sort_dir)
                
                service_providers = query.get()
                
                if not service_providers:
                    return ResponseService.response("NOT_FOUND", [], Error.NOT_FOUND)
                
                return ResponseService.response("SUCCESS", service_providers, Message.DATA_FETCHED)
                
            except (ValueError, TypeError):
                return ResponseService.response("VALIDATION_ERROR", None, Error.VALIDATION_ERROR)
                
        elif group_id and group_id.strip() and group_id != "undefined":
            # If group_id is provided: check core_product_group_products -> core_product_vendor_products -> core_vendor_products -> core_service_providers
            try:
                # Step 1: Get product_ids from core_product_group_products where product_group_id = group_id
                group_products = QueryBuilderService("core_product_group_products")\
                    .select("product_id")\
                    .where("product_group_id", int(group_id))\
                    .get()
                
                if not group_products:
                    return ResponseService.response("NOT_FOUND", [], Error.NOT_FOUND)
                
                product_ids = [gp["product_id"] for gp in group_products]
                
                # Step 2: Get vendor_product_ids from core_product_vendor_products where product_id in product_ids
                vendor_products = QueryBuilderService("core_product_vendor_products")\
                    .select("vendor_product_id")\
                    .whereIn("product_id", product_ids)\
                    .get()
                
                if not vendor_products:
                    return ResponseService.response("NOT_FOUND", [], Error.NOT_FOUND)
                
                vendor_product_ids = [vp["vendor_product_id"] for vp in vendor_products]
                
                # Step 3: Get vendor_ids from core_vendor_products where id in vendor_product_ids
                vendor_details = QueryBuilderService("core_vendor_products")\
                    .select("vendor_id")\
                    .whereIn("id", vendor_product_ids)\
                    .get()
                
                if not vendor_details:
                    return ResponseService.response("NOT_FOUND", [], Error.NOT_FOUND)
                
                vendor_ids = list(set([vd["vendor_id"] for vd in vendor_details]))  # Remove duplicates
                
                # Step 4: Filter by risk_type_ids if provided
                if risk_type_ids and risk_type_ids.strip():
                    try:
                        # Parse risk_type_ids (comma-separated string like "1,2,3")
                        risk_type_id_list = [int(rt.strip()) for rt in risk_type_ids.split(",") if rt.strip().isdigit()]
                        
                        if risk_type_id_list:
                            # Find vendors who provide ALL the specified risk types within this group
                            # We need to check that each vendor has products for ALL risk types, not just any of them
                            
                            # Get all vendor products for the group vendors with the specified risk types
                            vendor_products_by_risk = QueryBuilderService("core_vendor_products")\
                                .select("vendor_id", "category_id")\
                                .whereIn("vendor_id", vendor_ids)\
                                .whereIn("category_id", risk_type_id_list)\
                                .whereNull("deleted_at")\
                                .get()
                            
                            if not vendor_products_by_risk:
                                return ResponseService.response("NOT_FOUND", [], Error.NOT_FOUND)
                            
                            # Group by vendor_id and count unique risk types each vendor provides
                            vendor_risk_counts = {}
                            for vp in vendor_products_by_risk:
                                vendor_id = vp["vendor_id"]
                                risk_type = vp["category_id"]
                                
                                if vendor_id not in vendor_risk_counts:
                                    vendor_risk_counts[vendor_id] = set()
                                vendor_risk_counts[vendor_id].add(risk_type)
                            
                            # Filter to only vendors who provide ALL the requested risk types
                            required_risk_count = len(risk_type_id_list)
                            filtered_vendor_ids = []
                            
                            for vendor_id, provided_risk_types in vendor_risk_counts.items():
                                if len(provided_risk_types) >= required_risk_count:
                                    # Check if this vendor provides all the required risk types
                                    if all(risk_type in provided_risk_types for risk_type in risk_type_id_list):
                                        filtered_vendor_ids.append(vendor_id)
                            
                            if not filtered_vendor_ids:
                                return ResponseService.response("NOT_FOUND", [], Error.NOT_FOUND)
                            
                            vendor_ids = filtered_vendor_ids
                                
                    except (ValueError, TypeError):
                        return ResponseService.response("VALIDATION_ERROR", None, Error.VALIDATION_ERROR)
                
                # Step 5: Get service provider details from core_service_providers where id in vendor_ids with search and sorting
                query = (
                    QueryBuilderService("core_service_providers")
                    .whereIn("id", vendor_ids)
                    .apply_conditions(filter_json, allowed_filters, search_string, allowed_searching_columns)
                )
                
                # Apply sorting if provided
                if sort_by:
                    query = query.orderBy(sort_by, sort_dir)
                
                service_providers = query.get()
                
                if not service_providers:
                    return ResponseService.response("NOT_FOUND", [], Error.NOT_FOUND)
                
                return ResponseService.response("SUCCESS", service_providers, Message.DATA_FETCHED)
                
            except (ValueError, TypeError):
                return ResponseService.response("VALIDATION_ERROR", None, Error.VALIDATION_ERROR)
    else:
        # Original logic: get all service providers without pagination
        # Extract query parameters for filtering and search
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        sort_by = request.GET.get("sort_by", "name")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "name" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        
        allowed_filters = ["name", "type_id"]
        allowed_searching_columns = ["core_service_providers.name"]
        
        # Query service providers with search and sorting (no pagination)
        query = (
            QueryBuilderService("core_service_providers")
            .apply_conditions(filter_json, allowed_filters, search_string, allowed_searching_columns)
        )
        
        # Apply sorting if provided
        if sort_by:
            query = query.orderBy(sort_by, sort_dir)
        
        data = query.get()

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

