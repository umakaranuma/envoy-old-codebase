from mServices.ValidatorService import ValidatorService
from mServices.ResponseService import ResponseService
from mServices.QueryBuilderService import QueryBuilderService
from rest_framework.decorators import api_view
from messages import Message, Error as ErrorMessages

@api_view(["GET"])
def get_vendor_products_and_groups_by_risk_type(request):
    """
    Get vendor products or product groups based on risk type IDs.
    
    For single risk_type_id: Returns vendor products directly
    For multiple risk_type_ids: Returns product groups containing products from all requested risk types
    """
    try:
        # Get and parse params
        raw_ids = request.GET.get("risk_type_id", "")
        risk_type_ids = [int(x) for x in raw_ids.split(",") if x.strip().isdigit()]

        # Validate input
        if not risk_type_ids:
            return ResponseService.response(
                "VALIDATION_ERROR", 
                {"risk_type_id": "At least one valid risk_type_id is required."}, 
                ErrorMessages.VALIDATION_ERROR
            )

        # Handle single risk_type_id case
        if len(risk_type_ids) == 1:
            return _get_vendor_products_single_risk_type(risk_type_ids[0])
        
        # Handle multiple risk_type_ids case
        return _get_product_groups_multiple_risk_types(risk_type_ids)

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            None, 
            ErrorMessages.INTERNAL_SERVER_ERROR
        )


def _get_vendor_products_single_risk_type(risk_type_id):
    """Get vendor products for a single risk type."""
    vendor_products = QueryBuilderService("core_vendor_products")\
        .whereIn("category_id", [risk_type_id])\
        .whereNull("deleted_at")\
        .get()

    if not vendor_products:
        return ResponseService.response(
            "NOT_FOUND", 
            [], 
            ErrorMessages.NOT_FOUND
        )

    return ResponseService.response(
        "SUCCESS",
        vendor_products,
        Message.DATA_FETCHED
    )


def _get_product_groups_multiple_risk_types(risk_type_ids):
    """Get product groups containing products from all requested risk types."""
    
    # Step 1: Find products in core_products where category_id matches risk_type_ids
    products = QueryBuilderService("core_products")\
        .select("id", "category_id")\
        .whereIn("category_id", risk_type_ids)\
        .get()

    if not products:
        return ResponseService.response(
            "NOT_FOUND", 
            [], 
            "No products found for the provided risk types."
        )

    # Extract product IDs and group by risk type
    product_ids = [product["id"] for product in products]
    products_by_risk_type = {}
    for product in products:
        risk_type = product["category_id"]
        if risk_type not in products_by_risk_type:
            products_by_risk_type[risk_type] = []
        products_by_risk_type[risk_type].append(product["id"])

    # Step 2: Find product_group_ids in core_product_group_products that have these product_ids
    product_group_products = QueryBuilderService("core_product_group_products")\
        .select("product_group_id", "product_id")\
        .whereIn("product_id", product_ids)\
        .get()

    if not product_group_products:
        return ResponseService.response(
            "NOT_FOUND", 
            [], 
            "No product groups found for the provided products."
        )

    # Step 3: Find product groups that contain products from ALL requested risk types
    product_group_counts = {}
    for pgp in product_group_products:
        group_id = pgp["product_group_id"]
        if group_id not in product_group_counts:
            product_group_counts[group_id] = set()
        product_group_counts[group_id].add(pgp["product_id"])

    # Find groups that have products from ALL requested risk types
    common_group_ids = []
    for group_id, group_products in product_group_counts.items():
        # Check if this group has products from ALL requested risk types
        has_all_risk_types = True
        for risk_type, risk_products in products_by_risk_type.items():
            # Check if this group has at least one product from this risk type
            if not any(product_id in group_products for product_id in risk_products):
                has_all_risk_types = False
                break
        
        if has_all_risk_types:
            common_group_ids.append(group_id)

    if not common_group_ids:
        return ResponseService.response(
            "NOT_FOUND", 
            [], 
            "No product groups found that contain products from all specified risk types."
        )

    # Step 4: Get product groups from core_product_groups table
    product_groups = QueryBuilderService("core_product_groups")\
        .whereIn("id", common_group_ids)\
        .get()

    if not product_groups:
        return ResponseService.response(
            "NOT_FOUND", 
            [], 
            "No product groups found in core_product_groups table."
        )

    return ResponseService.response(
        "SUCCESS",
        product_groups,
        f"Found {len(common_group_ids)} product groups containing products from all {len(risk_type_ids)} requested risk types."
    )






@api_view(["GET"])
def product_documents_enhanced(request, id):
    """
    Enhanced product documents endpoint that supports both direct and group-based document retrieval.
    
    Parameters:
    - id: Product ID or Group ID (depending on type parameter)
    - type: 'group' for group-based documents, any other value or missing for direct documents
    """
    try:
        # Get documents for the product
        all_columns = [
            "core_product_document_types.*"
        ]

        # Query parameters
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["name", "code"]

        # Type-wise filter - check if type is 'group'
        doc_type = request.GET.get("type", None)
        
        if doc_type == "group":
            # Group-based document retrieval logic
            # Step 1: Get product_ids from core_product_group_products where product_group_id = id
            group_products = QueryBuilderService("core_product_group_products")\
                .select("product_id")\
                .where("product_group_id", id)\
                .get()
            
            if not group_products:
                return ResponseService.response("NOT_FOUND", [], ErrorMessages.NOT_FOUND)
            
            # Extract product IDs
            product_ids = [gp["product_id"] for gp in group_products]
            
            # Step 2: Get vendor_product_ids from core_products_vendor_products where product_id in product_ids
            vendor_product_mappings = QueryBuilderService("core_product_vendor_products")\
                .select("vendor_product_id")\
                .whereIn("product_id", product_ids)\
                .get()
            
            if not vendor_product_mappings:
                return ResponseService.response("NOT_FOUND", [], ErrorMessages.NOT_FOUND)
            
            # Extract vendor product IDs
            vendor_product_ids = [vpm["vendor_product_id"] for vpm in vendor_product_mappings]
            
            # Step 3: Get documents from core_product_document_types where vendor_product_id in vendor_product_ids
            query = QueryBuilderService("core_product_document_types")\
                .select(*all_columns)\
                .whereIn("vendor_product_id", vendor_product_ids)
            
        else:
            # Direct document retrieval (existing logic)
            query = QueryBuilderService("core_product_document_types")\
                .select(*all_columns)\
                .where('vendor_product_id', id)
        
        # Apply additional filters if provided (but not for 'product' type)
        if doc_type and doc_type != "group" and doc_type != "product":
            query = query.where('type', doc_type)
        
        # Apply conditions and pagination
        data = query.apply_conditions(filter_json, [], search_string, ["name"])\
                   .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, ErrorMessages.INTERNAL_SERVER_ERROR)