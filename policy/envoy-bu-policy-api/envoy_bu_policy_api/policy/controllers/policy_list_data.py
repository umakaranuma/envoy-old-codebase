from rest_framework.decorators import api_view
from django.views.decorators.csrf import csrf_exempt
from mServices import ResponseService, QueryBuilderService
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error

# Helper function to check if the user has permission
def check_permission(request, action_code):
    action = ActionService.getAction("RequestPolicy", action_code)
    if not AuthService.hasAuthority(request, action):
        return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)
    return None


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


# Request Policy Insurers
@csrf_exempt
@api_view(["GET"])
def request_policy_insurers(request):
    if error := check_permission(request, "VIEW"):
        return error

    # Get the new parameters
    product_id = request.query_params.get("product_id")
    group_id = request.query_params.get("group_id")

    # Check if either parameter is provided (ignore "undefined" values)
    if (product_id and product_id != "undefined") or (group_id and group_id != "undefined"):
        # Logic for getting service providers based on product_id or group_id
        if product_id and product_id != "undefined":
            # If product_id is provided: check core_vendor_products -> core_service_providers
            try:
                # Get vendor_id from core_vendor_products where id = product_id
                vendor_product = QueryBuilderService("core_vendor_products")\
                    .select("vendor_id")\
                    .where("id", int(product_id))\
                    .first()
                
                if not vendor_product:
                    return ResponseService.response("NOT_FOUND", [], "Product not found.")
                
                vendor_id = vendor_product["vendor_id"]
                
                # Get service provider details from core_service_providers
                service_providers = QueryBuilderService("core_service_providers")\
                    .where("id", vendor_id)\
                    .get()
                
                if not service_providers:
                    return ResponseService.response("NOT_FOUND", [], "Service provider not found for this product.")
                
                return ResponseService.response("SUCCESS", service_providers, "Service providers fetched successfully for the specified product.")
                
            except (ValueError, TypeError):
                return ResponseService.response("VALIDATION_ERROR", None, "Invalid product_id format.")
                
        elif group_id and group_id != "undefined":
            # If group_id is provided: check core_product_group_products -> core_product_vendor_products -> core_vendor_products -> core_service_providers
            try:
                # Step 1: Get product_ids from core_product_group_products where product_group_id = group_id
                group_products = QueryBuilderService("core_product_group_products")\
                    .select("product_id")\
                    .where("product_group_id", int(group_id))\
                    .get()
                
                if not group_products:
                    return ResponseService.response("NOT_FOUND", [], "No products found in this group.")
                
                product_ids = [gp["product_id"] for gp in group_products]
                
                # Step 2: Get vendor_product_ids from core_product_vendor_products where product_id in product_ids
                vendor_products = QueryBuilderService("core_product_vendor_products")\
                    .select("vendor_product_id")\
                    .whereIn("product_id", product_ids)\
                    .get()
                
                if not vendor_products:
                    return ResponseService.response("NOT_FOUND", [], "No vendor products found for these products.")
                
                vendor_product_ids = [vp["vendor_product_id"] for vp in vendor_products]
                
                # Step 3: Get vendor_ids from core_vendor_products where id in vendor_product_ids
                vendor_details = QueryBuilderService("core_vendor_products")\
                    .select("vendor_id")\
                    .whereIn("id", vendor_product_ids)\
                    .get()
                
                if not vendor_details:
                    return ResponseService.response("NOT_FOUND", [], "No vendor details found.")
                
                vendor_ids = list(set([vd["vendor_id"] for vd in vendor_details]))  # Remove duplicates
                
                # Step 4: Get service provider details from core_service_providers where id in vendor_ids
                service_providers = QueryBuilderService("core_service_providers")\
                    .whereIn("id", vendor_ids)\
                    .get()
                
                if not service_providers:
                    return ResponseService.response("NOT_FOUND", [], "No service providers found for these vendors.")
                
                return ResponseService.response("SUCCESS", service_providers, f"Service providers fetched successfully for group {group_id}.")
                
            except (ValueError, TypeError):
                return ResponseService.response("VALIDATION_ERROR", None, "Invalid group_id format.")
    else:
        # Original logic: get all service providers
        query = QueryBuilderService("core_service_providers")

        allowed_filters = ["name", "type_id"]
        search_columns = ["name"]
        sort_columns = ["name", "id"]

        data = apply_query_params(
            query, request, allowed_filters, search_columns, sort_columns
        )
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# Request Policy Risk Types
@csrf_exempt
@api_view(["GET"])
def request_policy_risk_types(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crm_opportunity_types").select("id", "title AS name")

    allowed_filters = ["id", "title"]
    search_columns = ["title"]
    sort_columns = ["title", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# Request Policy Request Types
@csrf_exempt
@api_view(["GET"])
def request_policy_coverage_types(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crmp_coverage_types").select("id", "name")

    allowed_filters = ["id", "name"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# Request Policy Statuses
@csrf_exempt
@api_view(["GET"])
def request_policy_statuses(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("core_status").select("id", "name")

    allowed_filters = ["id", "name"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@csrf_exempt
@api_view(["GET"])
def request_types(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crmp_request_types")

    allowed_filters = ["name", "type_id"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# Payment Plans
@csrf_exempt
@api_view(["GET"])
def payment_plans(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crmp_payment_plans")

    allowed_filters = ["name", "type_id"]
    search_columns = ["name"]
    sort_columns = ["name", "id"]

    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)



@csrf_exempt
@api_view(["GET"])
def request_endorsement_types(request):
    if error := check_permission(request, "VIEW"):
        return error

    query = QueryBuilderService("crmp_endorsement_types") \
        .select("id", "name")

    allowed_filters = ["id", "name"]
    search_columns  = ["name"]
    sort_columns    = ["name", "id"]
    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def request_reason_codes_by_type(request, type_id):
    if error := check_permission(request, "VIEW"):
        return error

    query = (
        QueryBuilderService("crmp_endorsement_reason_codes")
        .select("id", "code", "description AS name")
        .where("endorsement_type_id", type_id)
    )

    allowed_filters = ["id", "code", "description"]
    search_columns  = ["code", "description"]
    sort_columns    = ["code", "id"]
    data = apply_query_params(
        query, request, allowed_filters, search_columns, sort_columns
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
