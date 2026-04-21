import datetime
import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from collections import defaultdict

from envoy.models.product import Product
from envoy.models.product_team import ProductTeam
from django.db import  connection ,transaction

from envoy.models.team import Team
from envoy.models.vendor_products import VendorProducts
from messages import Message, Error as ErrorMessages


@api_view(["GET"])
def get_all_products(request):
    """Fetch all products with pagination and search functionality."""

    # Define columns to fetch
    all_columns = ["id", "name", "code"]

    # Extract query parameters for filtering, sorting, and pagination
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    allowed_sorting_columns = ["name", "code"]

    # Query database
    data = (
        QueryBuilderService("core_products")
        .select(*all_columns)
        .apply_conditions(filter_json, [], search_string, ["name", "code"])
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)




# ---------------------------- Insurer Products ----------------------------------

@api_view(["GET", "POST",])
def insurer_products(request):

    if request.method == "GET":
        return get_all_insurer_products(request, None)
    
    if request.method == "POST":
        return create_insurer_product(request)
    
def get_all_insurer_products(request, produc_id):
    try:
        """Fetch all products with pagination and search functionality."""

        # Columns to select (including related data via joins)
        all_columns = [
            "core_vendor_products.*",
            "core_currencies.symbol as currency",
            "crm_opportunity_types.title as type",
            "core_service_providers.name as insurer",
            "core_users.display_name as added_by",
            "core_entity_docs.doc as docs",
            "core_entity_docs.name as doc_name",
            "core_entity_docs.type as doc_type",
        ]


        # Query parameters
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["id", "name", "code", "created_at"]
        allowed_filters = ["coverage_level", "product_code"]
        allowed_searching_columns =  ["core_vendor_products.name","crm_opportunity_types.title", "core_service_providers.name", "core_vendor_products.coverage_level", "core_vendor_products.code"]

        # If a specific product ID is provided, get a single record
        if produc_id:
            data = (
                QueryBuilderService("core_vendor_products")
                .leftJoin("core_currencies", "core_vendor_products.currency_id", "core_currencies.id")
                .leftJoin("crm_opportunity_types", "core_vendor_products.category_id", "crm_opportunity_types.id")
                .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
                .leftJoin("core_users", "core_vendor_products.added_by", "core_users.id")
                .leftJoin("core_entity_docs", "core_vendor_products.entity_id", "core_entity_docs.entity_id")
                .select(*all_columns)
                .where("core_vendor_products.id", produc_id)
                .first()
            )

            maped_native_product = (
                QueryBuilderService("core_product_vendor_products")
                .where("vendor_product_id", produc_id)
                .select("product_id")
                .first()
            )


            if maped_native_product and maped_native_product.get("product_id"):
                data["is_mapped_to_native_product"] = True
                data["native_product_id"] = maped_native_product.get("product_id")
                
                native_product = QueryBuilderService("core_products").where("id", maped_native_product.get("product_id")).select("core_products.*").first()
                data["native_product"] = native_product
            else:
                data["is_mapped_to_native_product"] = False
                data["native_product_id"] = None
                data["native_product"] = None

            return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
        else:
        # Otherwise, return paginated results with filters and search
         data = (
             QueryBuilderService("core_vendor_products")
             .leftJoin("core_currencies", "core_vendor_products.currency_id", "core_currencies.id")
             .leftJoin("crm_opportunity_types", "core_vendor_products.category_id", "crm_opportunity_types.id")
             .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
             .leftJoin("core_users", "core_vendor_products.added_by", "core_users.id")
             .leftJoin("core_entity_docs", "core_vendor_products.entity_id", "core_entity_docs.entity_id")
             .select(*all_columns)
             .whereNull("core_vendor_products.deleted_at")
             .apply_conditions(filter_json, allowed_filters, search_string,allowed_searching_columns)
             .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
         )
         
         # Add number_of_products count for each vendor
         if data and "data" in data and data["data"]:
             for item in data["data"]:
                 vendor_id = item.get("vendor_id")
                 if vendor_id:
                     number_of_products = QueryBuilderService("core_vendor_products").where("vendor_id", vendor_id).count()
                     item["number_of_products"] = number_of_products
                 else:
                     item["number_of_products"] = 0
    
         return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


def create_insurer_product(request):
    """Fetch all products with pagination and search functionality."""

    data = json.loads(request.body)

    rules = {
        "name" : "required",
        "category_id" : "required",
        "vendor_id" : "required",
        "coverage_level" : "required",
        "description" : "required|max:255",
        "currency_id" : "required",
        # "premium_amount" : "required",
        # "deductible_amount" : "required",
        # "claim_amount" : "required",
        "date" : "required|date",
        "remarks" : "optional|max:255",
        "docs" : "optional",
        "doc_name": "optional|string|max:255",
        "doc_type": "optional|string|max:100",

    }

    errors = ValidatorService.validate(data, rules)
    if errors:
         return ResponseService.response("VALIDATION_ERROR", errors, ErrorMessages.VALIDATION_ERROR)
      # Initialize entity_id as None
    entity_id = None

    # Handle document entity creation if all required fields are present
    if all(key in data for key in ["docs", "doc_name", "doc_type"]):
        # Create entity record
        entity = QueryBuilderService("core_entities").insert({
            "type": "Product Document",
            "created_by_id": request.user.id,
            "approvel_status": 0
        })
        
        if entity:
            # Create document record
            docs = QueryBuilderService("core_entity_docs").insert({
                "doc": data["docs"],
                "name": data["doc_name"],
                "type": data["doc_type"],
                "entity_id": entity["id"]
            })
            
            if docs:
                entity_id = entity["id"]

    new_data = {
        "name": data["name"],
        "category_id": data["category_id"],
        "vendor_id": data["vendor_id"],
        "coverage_level": data["coverage_level"],
        "description": data["description"],
        "currency_id": data["currency_id"],
        # "premium_amount": data["premium_amount"],
        # "deductible_amount": data["deductible_amount"],
        # "claim_amount": data["claim_amount"],
        "date": data["date"],
        "remarks": data.get("remarks", None),
        "added_by": request.user.id,
        "entity_id": entity_id
    }

    store = QueryBuilderService("core_vendor_products").insert(new_data)
    if store:

          new_code = f"IPR00{store['id']}"

          update = QueryBuilderService("core_vendor_products").where('id',store['id']).update({"code": new_code})

    if update:
         return ResponseService.response("SUCCESS", store, Message.DATA_CREATED)
    else:
        return ResponseService.response("NOT_FOUND", {}, ErrorMessages.NOT_FOUND)



    
# @api_view(["GET", "POST"])
# def product_coverage(request, id):
#     try:
#         if request.method == "GET":
#             # Get coverages for the product
#             all_columns = [
#                 "core_product_coverages.*",
#             ]

#             # Query parameters
#             filter_json = request.GET.get("filter", {})
#             search_string = request.GET.get("search", "")
#             page = int(request.GET.get("page", 1))
#             limit = int(request.GET.get("limit", 10))
#             sort_by = request.GET.get("sort_by", "id")
#             sort_dir = request.GET.get("sort_dir", "desc")
#             allowed_sorting_columns = ["name", "code"]

#             data = (
#                 QueryBuilderService("core_product_coverages")
#                 .select(*all_columns)
#                 .whereNull('deleted_at')
#                 .where('vendor_product_id', id)
#                 .apply_conditions(filter_json, [], search_string, ["name", "code"])
#                 .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
#             )
            
#             return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

#         elif request.method == "POST":
#             data = json.loads(request.body)
            
#             # Validation rules
#             rules = {
#                 "name": "required",
#                 "coverage_amount": "required|numeric",
#                 "excess_amount": "required|numeric",
#                 "limitation": "required",
#                 "is_mandatory": "required|boolean"
#             }

#             errors = ValidatorService.validate(data, rules)
#             if errors:
#                 return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#             new_data = {
#                 "name": data["name"],
#                 "coverage_amount": data["coverage_amount"],
#                 "excess_amount": data["excess_amount"],
#                 "limitation": data["limitation"],
#                 "is_mandatory": data["is_mandatory"],
#                 "vendor_product_id": id
#             }

#             store = QueryBuilderService("core_product_coverages").insert(new_data)
#             if store:
#                 return ResponseService.response("SUCCESS", store, Message.DATA_CREATED)
#             else:
#                 return ResponseService.response("NOT_FOUND", {}, "Failed to create coverage!")

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")



@api_view(["GET", "POST"])
def product_categories(request):
    try:
        if request.method == "GET":
            return get_all_product_categories(request)
        elif request.method == "POST":
            return create_product_category(request)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

def get_all_product_categories(request):
    try:
        all_columns = [
            "core_product_categories.*",
        ]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["id", "name", "code", "created_at"]


        data = QueryBuilderService("core_product_categories").select(*all_columns).apply_conditions(filter_json, [], search_string, ["name", "code"]).paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

def create_product_category(request):
    try:
        data = json.loads(request.body)
        rules = {
            "name": "required",
            "description": "nullable",
            "type": "required"
        }

        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, ErrorMessages.VALIDATION_ERROR)

        new_data = {
            "name": data["name"],
            "description": data.get("description", ""),
            "type": data["type"]
        }

        store = QueryBuilderService("core_product_categories").insert(new_data)
        if store:
            return ResponseService.response("SUCCESS", store, Message.DATA_CREATED)
        else:
            return ResponseService.response("NOT_FOUND", {}, "Failed to create product category!")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

@api_view(["GET", "POST"])
def product_coverage(request, id):
    try:
        if request.method == "GET":
            # Get coverages for the product
            all_columns = [
                "core_product_coverages.*",
                "core_product_categories.title as type"
            ]

            # Query parameters
            filter_json = request.GET.get("filter", {})
            search_string = request.GET.get("search", "")
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            sort_by = request.GET.get("sort_by", "id")
            sort_dir = request.GET.get("sort_dir", "desc")
            # Normalize empty values to defaults
            sort_by = "id" if sort_by in [None, ""] else sort_by
            sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
            allowed_sorting_columns = ["id", "name", "code"]

            data = (
                QueryBuilderService("core_product_coverages")
                .leftJoin("core_product_categories", "core_product_coverages.type_id", "core_product_categories.id")
                .select(*all_columns)
                .whereNull('deleted_at')
                .where('vendor_product_id', id)
                .apply_conditions(filter_json, [], search_string, ["name", "code"])
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
            )
            
            return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

        elif request.method == "POST":
            data = json.loads(request.body)
            
            # # Handle both array format and object with coverages array
            # if isinstance(data, list):
            #     # If data is directly an array, wrap it in coverages
            #     coverages_data = {"coverages": data}
            # else:
            #     # If data is an object with coverages array
            #     coverages_data = data
            
            #   # Validation rules for array of coverages
            # rules = {
            #     "coverages": "required|array"
            # }            
            # errors = ValidatorService.validate(coverages_data, rules)
            # if errors:
            #     return ResponseService.response("VALIDATION_ERROR", errors, ErrorMessages.VALIDATION_ERROR)

            # stored_coverages = []
            # validation_errors = []

            # # Coverage level validation rules (matching database schema)
            # coverage_rules = {
            #     "name": "required",
            #     "description": "nullable|string|max:255",
            #     "type_id": "nullable|integer"
            # }

            # # # Delete all existing coverages for this vendor product first 
            # # delete_result = QueryBuilderService("core_product_coverages").where('vendor_product_id', id).delete()
            # # if not delete_result:
            # #     return ResponseService.response("NOT_FOUND", {}, "Failed to remove existing coverages!")

            # # Process each coverage in the array
            # for coverage in coverages_data["coverages"]:
            #     # Validate each coverage
            #     coverage_errors = ValidatorService.validate(coverage, coverage_rules)
            #     if coverage_errors:
            #         validation_errors.append({
            #             "coverage": coverage.get("name", "Unknown"),
            #             "errors": coverage_errors
            #         })
            #         continue
            

            #     new_coverage = {
            #         "name": coverage["name"],
            #         "description": coverage.get("description", ""),
            #         "type_id": coverage.get("type_id", None),
            #         "vendor_product_id": id
            #     }

            #     store = QueryBuilderService("core_product_coverages").insert(new_coverage)
            #     if store:
            #         stored_coverages.append(store)

            # # Return appropriate response based on results
            # if validation_errors:
            #     return ResponseService.response(
            #         "VALIDATION_ERROR", 
            #         {"validation_errors": validation_errors}, 
            #         ErrorMessages.VALIDATION_ERROR
            #     )

            coverages_data = data

            rules = {
                "name": "required",
                "description": "nullable|string|max:255",
                "type_id": "required|integer"
            }

            errors = ValidatorService.validate(coverages_data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, ErrorMessages.VALIDATION_ERROR)

            new_coverage = {
                "name": coverages_data["name"],
                "description": coverages_data.get("description", ""),
                "type_id": coverages_data.get("type_id", None),
                "vendor_product_id": id
            }

            store = QueryBuilderService("core_product_coverages").insert(new_coverage)
            if store:   return ResponseService.response(
                "SUCCESS", store, Message.DATA_CREATED)
            else:
                return ResponseService.response("NOT_FOUND", {}, "Failed to create coverage!")

        return ResponseService.response(
            "SUCCESS", 
            {
                "created_coverage": store,
            }, 
            Message.DATA_CREATED
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, ErrorMessages.NOT_FOUND)



# @api_view(["GET", "POST"])   
# def product_documents(request, id):   
#     try:
#         if request.method == "GET":
#             # Get documents for the product
#             all_columns = [
#                 "core_product_document_types.*"
#             ]

#             # Query parameters
#             filter_json = request.GET.get("filter", {})
#             search_string = request.GET.get("search", "")
#             page = int(request.GET.get("page", 1))
#             limit = int(request.GET.get("limit", 10))
#             sort_by = request.GET.get("sort_by", "id")
#             sort_dir = request.GET.get("sort_dir", "desc")
#             allowed_sorting_columns = ["name", "code"]

#             data = (
#                 QueryBuilderService("core_product_document_types")
#                 .select(*all_columns)
#                 .where('vendor_product_id', id)
#                 .apply_conditions(filter_json, [], search_string, ["name"])
#                 .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
#             )
            
#             return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

#         elif request.method == "POST":
#             data = json.loads(request.body)
            
#             # Validation rules
#             rules = {
#                 "name": "required",
#                 "is_mandatory": "required|boolean",
#                 "type": "required"
#             }

#             errors = ValidatorService.validate(data, rules)
#             if errors:
#                 return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#             new_data = {
#                 "name": data["name"],
#                 "is_mandatory": data["is_mandatory"],
#                 "type": data["type"],
#                 "vendor_product_id": id
#             }

#             store = QueryBuilderService("core_product_document_types").insert(new_data)
#             if store:
#                 return ResponseService.response("SUCCESS", store, Message.DATA_CREATED)
#             else:
#                 return ResponseService.response("NOT_FOUND", {}, "Failed to create document type!")

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

@api_view(["GET", "POST"])   
def product_documents(request, id):   
    try:
        if request.method == "GET":
            # Get documents for the product
            all_columns = [
                "core_product_document_types.*"
            ]

            # Query parameters
            filter_json = request.GET.get("filter", {})
            search_string = request.GET.get("search",)
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            sort_by = request.GET.get("sort_by", "id")
            sort_dir = request.GET.get("sort_dir", "desc")
            sort_by = "id" if sort_by in [None, ""] else sort_by
            sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
            allowed_sorting_columns = ["name", "code"]

            # Type-wise filter
            doc_type = request.GET.get("type", None)

            query = QueryBuilderService("core_product_document_types")
            query = query.select(*all_columns).where('vendor_product_id', id)
            if doc_type:
                query = query.where('type', doc_type)
            query = query.apply_conditions(filter_json, [], search_string, ["name" ])
            data = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

            return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

        elif request.method == "POST":
            data = json.loads(request.body)
            
            # Validation rules for array of documents
            rules = {
                "documents": "required|array"
            }

            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

            stored_documents = []
            validation_errors = []

            # Document level validation rules
            doc_rules = {
                "name": "required",
                "is_mandatory": "required|boolean",
                "type": "required"
            }

            # Delete all existing doscs for this vendor product first 
            # delete_result = QueryBuilderService("core_product_document_types").where('vendor_product_id', id).delete()
            # if not delete_result:
            #     return ResponseService.response("NOT_FOUND", {}, "Failed to remove existing docs!")


            # Process each document in the array
            for doc in data["documents"]:
                # Validate each document
                doc_errors = ValidatorService.validate(doc, doc_rules)
                if doc_errors:
                    validation_errors.append({
                        "document": doc.get("name", "Unknown"),
                        "errors": doc_errors
                    })
                    continue

                new_doc = {
                    "name": doc["name"],
                    "is_mandatory": doc["is_mandatory"],
                    "type": doc["type"],
                    "vendor_product_id": id
                }

                store = QueryBuilderService("core_product_document_types").insert(new_doc)
                if store:
                    stored_documents.append(store)

            # Return appropriate response based on results
            if validation_errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", 
                    {"validation_errors": validation_errors}, 
                    "Some documents failed validation"
                )

            if not stored_documents:
                return ResponseService.response(
                    "NOT_FOUND", 
                    {}, 
                    "Failed to create any document types!"
                )

            return ResponseService.response(
                "SUCCESS", 
                {
                    "created_documents": stored_documents,
                    "total_created": len(stored_documents)
                }, 
                Message.DATA_CREATED
            )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")



@api_view(["GET", "PUT", "DELETE"])
def product_coverage_detail(request, id):
    try:
        if request.method == "GET":
            all_columns = [
                "core_product_coverages.*",
                "core_product_categories.title as type"
            ]
            data = QueryBuilderService("core_product_coverages").where('core_product_coverages.id', id).leftJoin("core_product_categories", "core_product_coverages.type_id", "core_product_categories.id").select(*all_columns).first()
            if data:
                return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
            return ResponseService.response("NOT_FOUND", {}, "Coverage not found!")

        elif request.method == "PUT":
            data = json.loads(request.body)
            
            rules = {
                "name": "required",
                "type_id": "required|integer",
                "description": "nullable|string|max:255"
            }

            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

            update = QueryBuilderService("core_product_coverages").where('id', id).update(data)
            if update:
                return ResponseService.response("SUCCESS", {}, Message.DATA_UPDATED)
            return ResponseService.response("NOT_FOUND", {}, "Failed to update coverage!")

        elif request.method == "DELETE":
            # now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            # delete = QueryBuilderService("core_product_coverages").where('id', id).update({'deleted_at': now})
            delete = QueryBuilderService("core_product_coverages").where('id', id).delete()
            if delete:
                return ResponseService.response("SUCCESS", {}, Message.DATA_DELETED)
            return ResponseService.response("NOT_FOUND", {}, "Failed to delete coverage!")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")



@api_view(["GET", "PUT", "DELETE"])
def product_document_detail(request, id):
    try:
        if request.method == "GET":
            data = QueryBuilderService("core_product_document_types").where('id', id).first()
            if data:
                return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
            return ResponseService.response("NOT_FOUND", {}, "Document type not found!")

        elif request.method == "PUT":
            data = json.loads(request.body)
            
            rules = {
                "name": "required",
                "is_mandatory": "required|boolean",
                "type": "required"
            }

            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

            update = QueryBuilderService("core_product_document_types").where('id', id).update(data)
            if update:
                return ResponseService.response("SUCCESS", {}, Message.DATA_UPDATED)
            return ResponseService.response("NOT_FOUND", {}, "Failed to update document type!")

        elif request.method == "DELETE":
            delete = QueryBuilderService("core_product_document_types").where('id', id).delete()
            if delete:
                return ResponseService.response("SUCCESS", {}, Message.DATA_DELETED)
            return ResponseService.response("NOT_FOUND", {}, "Failed to delete document type!")

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")




@api_view(["GET", "PUT", "DELETE"])
def product_detail(request, id):

    if request.method == "GET":
        return get_all_insurer_products(request, id)
    if request.method == "PUT":
        return update_insurer_product(request, id)
    if request.method == "DELETE":
        return delete_insurer_product(request, id)


def update_insurer_product(request, id):
    print(f"DEBUG: update_insurer_product called with id={id}")
    
    try:
        # Validate the ID
        print("DEBUG: Checking if product exists")
        product_id = QueryBuilderService("core_vendor_products").where("id", id).first()
        print(f"DEBUG: Product query result: {product_id}")
        if not product_id:
            print("DEBUG: Product not found")
            return ResponseService.response("NOT_FOUND", {}, "Product not found!")

        print("DEBUG: Parsing request body")
        data = json.loads(request.body)
        print(f"DEBUG: Request data: {data}")
    except Exception as e:
        print(f"DEBUG: Error in initial setup: {str(e)}")
        return ResponseService.response("ERROR", {}, f"Error in setup: {str(e)}")

    print("DEBUG: Setting up validation rules")
    rules = {
        "name" : "required",
        "category_id" : "required",
        "vendor_id" : "required",
        "coverage_level" : "required",
        "currency_id" : "required",
        "native_product_id" : "required",
        "date" : "required|date",
        "remarks" : "optional|max:255",
        "description" : "required|max:255",
        "docs" : "optional",
        "doc_name": "optional|string|max:255",
        "doc_type": "optional|string|max:100",
        # "premium_amount" : "required",
        # "deductible_amount" : "required",
        # "claim_amount" : "required",

    }    
    print("DEBUG: Running validation")
    errors = ValidatorService.validate(data, rules)
    print(f"DEBUG: Validation errors: {errors}")
    if errors:
         print("DEBUG: Validation failed, returning error")
         return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
    
    # Handle document updates if all required fields are present
    print("DEBUG: Checking document fields")
    entity_id = None
    if all(key in data and data[key] is not None for key in ["docs", "doc_name", "doc_type"]):
        print("DEBUG: All document fields present, handling documents")
        # Get existing entity_id from the product
        existing_product = QueryBuilderService("core_vendor_products").where("id", id).first()
        print(f"DEBUG: Existing product: {existing_product}")
        if existing_product and existing_product.get("entity_id"):
            print("DEBUG: Updating existing document")
            # Update existing document
            entity_id = existing_product["entity_id"]
            doc_update = QueryBuilderService("core_entity_docs").where("entity_id", entity_id).update({
                "doc": data["docs"],
                "name": data["doc_name"],
                "type": data["doc_type"]
            })
            print(f"DEBUG: Document update result: {doc_update}")
        else:
            print("DEBUG: Creating new entity and document")
            # Create new entity and document
            entity = QueryBuilderService("core_entities").insert({
                "type": "Product Document",
                "created_by_id": request.user.id,
                "approvel_status": 0
            })
            print(f"DEBUG: Entity creation result: {entity}")
            
            if entity:
                print(f"DEBUG: Creating document with entity_id: {entity['id']}")
                print(f"DEBUG: Document data - doc: {data.get('docs')}, name: {data.get('doc_name')}, type: {data.get('doc_type')}")
                try:
                    docs = QueryBuilderService("core_entity_docs").insert({
                        "doc": data["docs"],
                        "name": data["doc_name"],
                        "type": data["doc_type"],
                        "entity_id": entity["id"]
                    })
                    print(f"DEBUG: Document creation result: {docs}")
                    if docs:
                        entity_id = entity["id"]
                        print(f"DEBUG: Entity ID set to: {entity_id}")
                except Exception as e:
                    print(f"DEBUG: Error creating document: {str(e)}")
                    print(f"DEBUG: Document data causing error: doc={data.get('docs')}, name={data.get('doc_name')}, type={data.get('doc_type')}")
                    raise e
    else:
        print("DEBUG: Not all document fields present, skipping document handling")

    print("DEBUG: Preparing update data")
    new_data = {
        "name": data["name"],
        "category_id": data["category_id"],
        "vendor_id": data["vendor_id"],
        "coverage_level": data["coverage_level"],
        "description": data["description"],
        "currency_id": data["currency_id"],
        # "premium_amount": data["premium_amount"],
        # "deductible_amount": data["deductible_amount"],
        # "claim_amount": data["claim_amount"],
        "date": data["date"],
        "remarks": data.get("remarks", None)
    }

    # Only add entity_id to update data if it was set
    if entity_id is not None:
        new_data["entity_id"] = entity_id
        print(f"DEBUG: Added entity_id {entity_id} to update data")
    
    print(f"DEBUG: Update data: {new_data}")
    
    print("DEBUG: Updating native product mapping")
    try:
        native_product_update = QueryBuilderService("core_product_vendor_products").where('vendor_product_id', id).update({"product_id": data["native_product_id"]})
        print(f"DEBUG: Native product update result: {native_product_update}")
    except Exception as e:
        print(f"DEBUG: Error updating native product: {str(e)}")

    print("DEBUG: Updating vendor product")
    try:
        update = QueryBuilderService("core_vendor_products").where('id',id).update(new_data)
        print(f"DEBUG: Vendor product update result: {update}")
    except Exception as e:
        print(f"DEBUG: Error updating vendor product: {str(e)}")
        return ResponseService.response("ERROR", {}, f"Error updating product: {str(e)}")

    if update:
         print("DEBUG: Update successful")
         return ResponseService.response("SUCCESS", update, Message.DATA_UPDATED)
    else:
         print("DEBUG: Update failed")
         return ResponseService.response("NOT_FOUND", {}, f"{id} Failed to update product!")
    

def delete_insurer_product(request, id):
    # Validate the ID
    product_id = QueryBuilderService("core_vendor_products").where("id", id).first()
    if not product_id:
        return ResponseService.response("NOT_FOUND", {}, "Product not found!")
    
    now = datetime.datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    # Delete the product
    delete = QueryBuilderService("core_vendor_products").where('id', id).update({'deleted_at': formatted_now})
    if delete:
        return ResponseService.response("SUCCESS", {}, Message.DATA_DELETED)
    else:
        return ResponseService.response("NOT_FOUND", {}, f"{id} Failed to delete product!")
     
    

# -------------------------------Native Products ----------------------------------


@api_view(["GET", "POST",])
def native_products(request):

    if request.method == "GET":
        return get_all_native_products(request)
    
    if request.method == "POST":
        return create_native_product(request)
    


def get_all_native_products(request):
    try:
        all_columns = [
            "core_products.*",
            "crm_opportunity_types.title as type",
            "core_product_teams.team_id as team_id",
        ]

        # Extract query parameters for filtering, sorting, and pagination
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["name", "code", "created_at"]
        allowed_filters = ["code", "category_id"]
        allowed_searching_columns = ["core_products.name", "core_products.code", "crm_opportunity_types.title"]

        # Get unique products first (without team joins to avoid duplicates in pagination)
        data = (
            QueryBuilderService("core_products")
            .leftJoin("crm_opportunity_types", "core_products.category_id", "crm_opportunity_types.id")
            .select(
                "core_products.id",
                "core_products.name",
                "core_products.code",
                "core_products.category_id",
                "core_products.created_at",
                "core_products.updated_at",
                "core_products.deleted_at",
                "crm_opportunity_types.title as type"
            )
            .whereNull('core_products.deleted_at')
            .apply_conditions(filter_json, allowed_filters, search_string, allowed_searching_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        # Add team_ids for each product by querying separately
        if data and "data" in data:
            for product in data["data"]:
                # Get all team_ids for this product
                teams = QueryBuilderService("core_product_teams")\
                    .select("team_id")\
                    .where("product_id", product["id"])\
                    .get()
                
                product["team_ids"] = [team["team_id"] for team in teams if team.get("team_id") is not None]

        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

      
def create_native_product(request):
    try:        
        data = json.loads(request.body)
        
        # Debug: Print received data
        print("DEBUG - Received data:", data)
        print("DEBUG - vendor_product_ids:", data.get("vendor_product_ids"))
        print("DEBUG - insurer_products:", data.get("insurer_products"))
        
        rules = {
            "name": "required",
            "category_id": "required",
            "vendor_product_ids": "required|array"  # Make array required and non-empty
        }

      

        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
        
        # Validate vendor_product_ids array for empty or null values
        validation_errors = {}
        if "vendor_product_ids" in data:
            if not data["vendor_product_ids"]:
                validation_errors["vendor_product_ids"] = ["insurer_product_ids_required"]
            else:
                # Check each vendor_product_id for empty or null values
                valid_ids = []
                for index, vendor_product_id in enumerate(data["vendor_product_ids"]):
                    # Check if the ID is None, empty string, or only whitespace
                    if vendor_product_id is None or (isinstance(vendor_product_id, str) and not vendor_product_id.strip()):
                        validation_errors[f"vendor_product_ids.{index}"] = [f"Vendor product ID cannot be empty at index {index}"]
                    else:
                        valid_ids.append(vendor_product_id)
                
                # Check if at least one valid ID exists after filtering
                if not valid_ids:
                    validation_errors["vendor_product_ids"] = ["At least one valid vendor product is required"]
        else:
            validation_errors["vendor_product_ids"] = ["vendor_product_ids field is required"]
        
        # Index-wise validation for insurer_products array
        if "insurer_products" in data and isinstance(data["insurer_products"], list):
            valid_products_count = 0
            empty_entries_count = 0
            insurer_products_errors = {}
            
            for index, insurer_product in enumerate(data["insurer_products"]):
                # Check if entry is completely empty
                vendor_id = insurer_product.get("vendor_id")
                product_id = insurer_product.get("product_id")
                vendor_name = insurer_product.get("vendor_name")
                product_name = insurer_product.get("product_name")
                
                # Check if all fields are empty (None or empty string)
                is_completely_empty = (
                    (vendor_id is None or (isinstance(vendor_id, str) and not vendor_id.strip())) and
                    (product_id is None or (isinstance(product_id, str) and not product_id.strip())) and
                    (vendor_name is None or (isinstance(vendor_name, str) and not vendor_name.strip())) and
                    (product_name is None or (isinstance(product_name, str) and not product_name.strip()))
                )
                
                # Initialize index error object
                index_errors = {}
                
                # Check for vendor_id and product_id
                has_vendor_id = vendor_id and (isinstance(vendor_id, int) or (isinstance(vendor_id, str) and vendor_id.strip()))
                has_product_id = product_id and (isinstance(product_id, int) or (isinstance(product_id, str) and product_id.strip()))
                
                # Count empty entries
                if is_completely_empty:
                    empty_entries_count += 1
                    # Even for completely empty entries, show field-specific errors
                    index_errors["vendor_id"] = [{
                        "error_type": "required",
                        "tokens": {
                            "_attribute": "vendor_id"
                        }
                    }]
                    index_errors["product_id"] = [{
                        "error_type": "required",
                        "tokens": {
                            "_attribute": "product_id"
                        }
                    }]
                    insurer_products_errors[str(index)] = index_errors
                    continue
                
                # Validate that both IDs are present if the entry is not completely empty
                if not has_vendor_id:
                    index_errors["vendor_id"] = [{
                        "error_type": "required",
                        "tokens": {
                            "_attribute": "vendor_id"
                        }
                    }]
                
                if not has_product_id:
                    index_errors["product_id"] = [{
                        "error_type": "required",
                        "tokens": {
                            "_attribute": "product_id"
                        }
                    }]
                
                # Add errors for this index if any exist
                if index_errors:
                    insurer_products_errors[str(index)] = index_errors
                
                # Count valid entries
                if has_vendor_id and has_product_id:
                    valid_products_count += 1
            
            # Add insurer_products errors to main validation errors if any exist
            if insurer_products_errors:
                validation_errors["insurer_products"] = insurer_products_errors
            
            # Check if at least one valid insurer product exists (only if insurer_products array has items)
            if len(data["insurer_products"]) > 0 and valid_products_count == 0:
                if "insurer_products" not in validation_errors:
                    validation_errors["insurer_products"] = {}
                validation_errors["insurer_products"]["_error"] = "At least one insurer product with valid vendor and product is required"
        
        if validation_errors:
            return ResponseService.response("VALIDATION_ERROR", validation_errors, "Validation Error")

        new_data = {
            "name": data["name"],
            "category_id": data["category_id"],
            "code": "NPR00",
            # 'added_by': request.user.id,
        }

        store = QueryBuilderService("core_products").insert(new_data)
        if not store or "id" not in store:
            return ResponseService.response("NOT_FOUND", {}, "Insert failed or no ID returned")

        # Insert into core_product_vendor_products
        for vendor_product_id in data["vendor_product_ids"]:
            new_vendor_product = {
                "product_id": store["id"],
                "vendor_product_id": vendor_product_id,
            }
            QueryBuilderService("core_product_vendor_products").insert(new_vendor_product)

        new_code = f"NPR00{store['id']}"
        update = QueryBuilderService("core_products").where("id", store["id"]).update({"code": new_code})

        if update:
            return ResponseService.response("SUCCESS", store, Message.DATA_CREATED)
        else:
            return ResponseService.response("NOT_FOUND", {}, "Failed to update product code")
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


@api_view(["GET", "PUT", "DELETE"])
def native_product_detail(request, id):
    if request.method == "GET":
        return get_native_product(request, id)
    if request.method == "PUT":
        return update_native_product(request, id)
    if request.method == "DELETE":
        return delete_native_product(request, id)
    


def get_native_product(request, id):

    try:
        all_columns = [
            "core_products.*",
            "core_currencies.symbol as currency",
            "crm_opportunity_types.title as type",
            "core_service_providers.name as insurer",
            "core_vendor_products.id as vendor_product_id",
            "core_vendor_products.name as vendor_product_name",
            "core_vendor_products.code as vendor_product_code",
            "core_vendor_products.coverage_level as vendor_product_coverage_level",
            "core_vendor_products.description as vendor_product_description",
            "core_vendor_products.premium_amount as vendor_product_premium_amount",
            "core_vendor_products.deductible_amount as vendor_product_deductible_amount",
            "core_vendor_products.claim_amount as vendor_product_claim_amount",
            "core_vendor_products.remarks as vendor_product_remarks",
            "core_vendor_products.updated_at as vendor_product_updated_at",
            "core_vendor_products.added_by as vendor_product_added_by",
            "core_vendor_products.vendor_id as sp_vendor_id",
            "core_users.display_name as added_by",        
        ]

        # Validate the ID
        product_id = QueryBuilderService("core_products").where("id", id).first()
        if not product_id:
            return ResponseService.response("NOT_FOUND", {}, "Product not found!")
        
        # Extract query parameters for filtering, sorting, and pagination
        filter_json = request.GET.get("filter", {}) 
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["name", "code"]

        # Query database
        data = (
            QueryBuilderService("core_products")
            .leftJoin("core_product_vendor_products", "core_product_vendor_products.product_id", "core_products.id")
            .leftJoin("core_vendor_products", "core_vendor_products.id", "core_product_vendor_products.vendor_product_id")
            .leftJoin("core_currencies", "core_vendor_products.currency_id", "core_currencies.id")
            .leftJoin("crm_opportunity_types", "core_vendor_products.category_id", "crm_opportunity_types.id")
            .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
            .leftJoin("core_users", "core_vendor_products.added_by", "core_users.id")
            .select(*all_columns)
            .where('core_products.id', id)
            .get()
            # .apply_conditions(filter_json, [], search_string, ["name", "code"])
            # .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )                               

        # Group by native product id
        products = {}
        for row in data:
            pid = row["id"]
            if pid not in products:
                # Copy all fields except vendor product fields
                product = {k: v for k, v in row.items() if not k.startswith("vendor_product")}
                product["vendor_products"] = []
                products[pid] = product
            # Add vendor product object if present
            if row.get("vendor_product_id"):
                vendor_product = {
                    "id": row["vendor_product_id"],
                    "name": row["vendor_product_name"],
                    "insurer_id": row["sp_vendor_id"],
                    "insurer": row["insurer"],
                    "currency": row["currency"],
                    "type": row["type"],
                    "coverage_level": row["vendor_product_coverage_level"],
                    "description": row["vendor_product_description"],
                    "premium_amount": row["vendor_product_premium_amount"],
                    "deductible_amount": row["vendor_product_deductible_amount"],
                    "claim_amount": row["vendor_product_claim_amount"],
                    "remarks": row["vendor_product_remarks"],
                    "updated_at": row["vendor_product_updated_at"],
                    "added_by": row["vendor_product_added_by"],
                    "code": row["vendor_product_code"],
                }
                if vendor_product not in products[pid]["vendor_products"]:
                    products[pid]["vendor_products"].append(vendor_product)

        result = list(products.values())
        if result:
            return ResponseService.response("SUCCESS", result, Message.DATA_FETCHED)
        else:
            return ResponseService.response("NOT_FOUND", {}, "Failed to retrieve products!")
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


def update_native_product(request, id):

    # Validate the ID
    product_id = QueryBuilderService("core_products").where("id", id).first()
    if not product_id:
        return ResponseService.response("NOT_FOUND", {}, "Product not found!")

    data = json.loads(request.body)       
    rules = {
            "name": "required",
            "category_id": "required",
            "vendor_product_ids": "required|array",
        }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
          # Add custom validation for non-empty array
    if "vendor_product_ids" not in data or not data["vendor_product_ids"]:
        return ResponseService.response(
            "VALIDATION_ERROR", 
            {"vendor_product_ids": ["vendor_product_ids"]}, 
            "Validation Error"
        )

    new_data = {
        "name": data["name"],
        "category_id": data["category_id"],
        # 'added_by': request.user.id,
    }

    update = QueryBuilderService("core_products").where('id', id).update(new_data)
    if not update:
        return ResponseService.response("NOT_FOUND", {}, f"{id} Failed to update product!")

    # Delete existing vendor products
    QueryBuilderService("core_product_vendor_products").where('product_id', id).delete()

    # Insert new vendor products
    for vendor_product_id in data["vendor_product_ids"]:
        new_vendor_product = {
            "product_id": id,
            "vendor_product_id": vendor_product_id,
        }
        QueryBuilderService("core_product_vendor_products").insert(new_vendor_product)

    return ResponseService.response("SUCCESS", {}, Message.DATA_UPDATED) 


def delete_native_product(request, id):
    # Validate the ID
    product_id = QueryBuilderService("core_products").where("id", id).first()
    if not product_id:
        return ResponseService.response("NOT_FOUND", {}, "Product not found!")

    now = datetime.datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")

    # Delete the product
    delete = QueryBuilderService("core_products").where('id', id).update({'deleted_at': formatted_now})
    if delete:
        return ResponseService.response("SUCCESS", {}, Message.DATA_DELETED)
    else:
        return ResponseService.response("NOT_FOUND", {}, f"{id} Failed to delete product!")
    

@api_view(["GET"])
def opportunity_type_vendors(request, id):
    """Fetch all products with pagination and search functionality."""

    all_columns = [
        "core_service_providers.*",
        
        ]

    # Optional search by vendor name
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")


    # Query database
    data = (
        QueryBuilderService("core_vendor_products")
        .leftJoin("crm_opportunity_types", "core_vendor_products.category_id", "crm_opportunity_types.id")
        .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
        .select(*all_columns)
        .whereNull('core_vendor_products.deleted_at')
        .where('crm_opportunity_types.id', id)
        .apply_conditions(filter_json, [], search_string, ["core_service_providers.name"])
        .get()
    
    )

    unique_vendors = {}
    for vendor in data :
        unique_vendors[vendor["id"]] = vendor
    data = list(unique_vendors.values())
    

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@api_view(["GET"])
def opportunity_type_vendor_product(request, id, vendor_id):
    """Fetch all products with pagination and search functionality."""

    all_columns = [
        "core_vendor_products.*",
        "core_currencies.symbol as currency",
        "crm_opportunity_types.title as type",
        "core_service_providers.name as insurer",
        "core_users.display_name as added_by",

        ]


    # Query database
    data = (
        QueryBuilderService("core_vendor_products")
        .leftJoin("core_currencies", "core_vendor_products.currency_id", "core_currencies.id")
        .leftJoin("crm_opportunity_types", "core_vendor_products.category_id", "crm_opportunity_types.id")
        .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
        .leftJoin("core_users", "core_vendor_products.added_by", "core_users.id")
        .select(*all_columns)
        .whereNull('core_vendor_products.deleted_at')
        .where('crm_opportunity_types.id', id)
        .where('core_service_providers.id', vendor_id)
        .get()
    
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@api_view(["GET"])
def opportunity_products(request,id):
  try:
    all_columns = [
        "core_vendor_products.*",
        "core_currencies.symbol as currency",
        "crm_opportunity_types.title as type",
        "core_service_providers.name as insurer",
        "core_users.display_name as added_by",
    ]

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    allowed_sorting_columns = ["name", ]



    # Query database
    data = (
        QueryBuilderService("core_vendor_products")
        .leftJoin("core_currencies", "core_vendor_products.currency_id", "core_currencies.id")
        .leftJoin("crm_opportunity_types", "core_vendor_products.category_id", "crm_opportunity_types.id")
        .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
        .leftJoin("core_users", "core_vendor_products.added_by", "core_users.id")
        .select(*all_columns)
        .whereNull('core_vendor_products.deleted_at')
        .where('core_vendor_products.category_id', id)
        .apply_conditions(
            filter_json,
            [],
            search_string,
            [
                "core_vendor_products.name",
                "core_service_providers.name",
            ],
        )
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
  except Exception as e:
    import traceback
    traceback.print_exc()
    return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


# ---------------------------------------Product Group------------------------------------
@api_view(["GET", "POST",])
def product_groups(request):
    if request.method == "GET":
        return get_all_product_groups(request)
    if request.method == "POST":
        return create_product_group(request)
    

def get_all_product_groups(request):
    try:
        all_columns = [
            "core_product_groups.*",
            "core_products.id as product_id",
            "core_products.name as native_product_name",
            "core_teams.id as team_id",
            "core_teams.name as team_name",
        ]

        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        
        # Ensure sort_by and sort_dir have proper defaults
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        
        allowed_sorting_columns = ["id","name"]

        # First get the paginated product groups
        paginated_groups = (
            QueryBuilderService("core_product_groups")
            .select("core_product_groups.*")
            .whereNull('core_product_groups.deleted_at')
            .apply_conditions(filter_json, [], search_string, ["core_product_groups.name"])
            .orderBy(f"core_product_groups.{sort_by}", sort_dir)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )
        
        # Get all data for the paginated groups (without pagination)
        group_ids = [group["id"] for group in paginated_groups["data"]]
        
        if not group_ids:
            return ResponseService.response("SUCCESS", {
                "total_records": 0,
                "per_page": limit,
                "current_page": page,
                "last_page": 0,
                "data": []
            }, "Products retrieved successfully!")
        
        raw_data = (
            QueryBuilderService("core_product_groups")
            .leftJoin("core_product_group_products", "core_product_group_products.product_group_id", "core_product_groups.id")
            .leftJoin("core_products", "core_product_group_products.product_id", "core_products.id")
            .leftJoin("core_product_group_teams", "core_product_group_teams.product_group_id", "core_product_groups.id")
            .leftJoin("core_teams", "core_product_group_teams.team_id", "core_teams.id")
            .select(*all_columns)
            .whereIn("core_product_groups.id", group_ids)
            .get()
        )

        grouped_data = {}
        for row in raw_data:
            group_id = row["id"]
            if group_id not in grouped_data:
                group = {k: v for k, v in row.items() if k not in ["product_id", "native_product_name", "team_id", "team_name"]}
                group["products"] = []
                group["teams"] = []
                grouped_data[group_id] = group
            if row.get("product_id"):
                product = {
                    "product_id": row["product_id"],
                    "product_name": row["native_product_name"],
                }
                if product not in grouped_data[group_id]["products"]:
                    grouped_data[group_id]["products"].append(product)

            if row.get("team_id"):
                team = {
                    "team_id": row["team_id"],
                    "team_name": row["team_name"],
                }
                if team not in grouped_data[group_id]["teams"]:
                    grouped_data[group_id]["teams"].append(team)

        # Build the final result with pagination meta and grouped data in the correct order
        ordered_data = []
        for group in paginated_groups["data"]:
            group_id = group["id"]
            if group_id in grouped_data:
                ordered_data.append(grouped_data[group_id])
        
        result = {
            "total_records": paginated_groups["total_records"],
            "per_page": paginated_groups["per_page"],
            "current_page": paginated_groups["current_page"],
            "last_page": paginated_groups["last_page"],
            "data": ordered_data
        }

        return ResponseService.response("SUCCESS", result, Message.DATA_FETCHED)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

    

def create_product_group(request):
    try:
        
        data = json.loads(request.body)
        print ("data", data)
        rules = {
            "name": "required",
            "product_ids": "required|array|min:1",
            "team_ids": "required|array|exists:core_teams,id|min:1",
            "currency_id": "required|exists:core_currencies,id",
        }

        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Add custom validation for non-empty arrays
        if "product_ids" not in data or not data["product_ids"]:
            return ResponseService.response(
                "VALIDATION_ERROR", 
                {"product_ids": ["At least one product is required"]}, 
                "Validation Error"
            )
        
        if "team_ids" not in data or not data["team_ids"]:
            return ResponseService.response(
                "VALIDATION_ERROR", 
                {"team_ids": ["At least one team is required"]}, 
                "Validation Error"
            )

        new_data = {
            "name": data["name"],
            "currency_id": data.get("currency_id"),
        }

        store = QueryBuilderService("core_product_groups").insert(new_data)
        if not store or "id" not in store:
            return ResponseService.response("NOT_FOUND", {}, "Insert failed or no ID returned")
        
        # Insert into core_product_group_products
        for product_id in data["product_ids"]:
            new_product = {
                "product_group_id": store["id"],
                "product_id": product_id,
            }
            QueryBuilderService("core_product_group_products").insert(new_product)
        
        # Insert into core_product_group_teams
        for team_id in data["team_ids"]:
            new_team = {
                "product_group_id": store["id"],
                "team_id": team_id,
            }
            QueryBuilderService("core_product_group_teams").insert(new_team)

        return ResponseService.response("SUCCESS", store, Message.DATA_CREATED)     
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


@api_view(["PUT","GET"])
def product_group_teams(request, id):
    if request.method == "GET":
        return get_product_group_teams(request, id)
    if request.method == "PUT":
     try:
        rules = {
            "team_ids": "required|array|min:1|exists:core_teams,id",
        }
        errors = ValidatorService.validate(request.data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
        
        if "team_ids" not in request.data or not request.data["team_ids"]:
            return ResponseService.response(
                "VALIDATION_ERROR", 
                {"team_ids": ["At least one team is required"]}, 
                "Validation Error"
            )
        
        # Check for existing teams to avoid duplicates
        existing_teams = (QueryBuilderService("core_product_group_teams")
            .where("product_group_id", id)
            .whereIn("team_id", request.data["team_ids"])
            .get())

        if existing_teams:
            existing_team_ids = [team["team_id"] for team in existing_teams]
            return ResponseService.response(
                "VALIDATION_ERROR", 
                {
                    "team_ids": [
                        {
                            "error_type": "teams_already_exist",
                            "tokens": {
                                "_attribute": "team_ids",
                                "existing_teams": existing_team_ids
                            }
                        }
                    ]
                },
                "teams_already_exist"
            )


        # Insert new teams into group
        for team_id in request.data["team_ids"]:
            new_team = {
                "product_group_id": id,
                "team_id": team_id,
            }
            
            update = QueryBuilderService("core_product_group_teams").insert(new_team)
        
        if not update:
            return ResponseService.response("NOT_FOUND", {}, "Failed to update product group teams!")
        
        return ResponseService.response("SUCCESS", update, "default_update_success_msg")
        
     except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


    
def get_product_group_teams(request, id):
    try:
        all_columns = [
          
            "core_teams.*",
            "leader.display_name as leader_name",
        ]
        
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["id","name"]


        data =( QueryBuilderService("core_product_group_teams").where("product_group_id", id)
        .leftJoin("core_teams", "core_product_group_teams.team_id", "core_teams.id")
        .leftJoin("core_users as leader", "leader.id", "core_teams.leader_id")
        .select(*all_columns)
        .apply_conditions(filter_json, [], search_string, ["core_teams.name"])
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
)
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")



@api_view(["PUT","GET"])
def product_group_product_add(request, id):
    try:
        if request.method == "GET":
            return get_product_group_products(request, id)
        if request.method == "PUT":
            data = json.loads(request.body)
            rules = {
                "product_ids": "required|array|min:1",
            }
            errors = ValidatorService.validate(data, rules)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
            
            if "product_ids" not in data or not data["product_ids"]:
                return ResponseService.response(
                    "VALIDATION_ERROR", 
                    {"product_ids": ["At least one product is required"]}, 
                    "Validation Error"
                )

            # Check for existing products
            existing_products = (QueryBuilderService("core_product_group_products")
                .where("product_group_id", id)
                .whereIn("product_id", data["product_ids"])
                .get())
            
            if existing_products:
                existing_product_ids = [product["product_id"] for product in existing_products]
                return ResponseService.response(
                    "VALIDATION_ERROR", 
                    {
                        "product_ids": [
                            {
                                "error_type": "products_already_exist",
                                "tokens": {
                                    "_attribute": "product_ids",
                                    "existing_products": existing_product_ids
                                }
                            }
                        ]
                    },
                    "products_already_exist"
                )
            
            for product_id in data["product_ids"]:
                QueryBuilderService("core_product_group_products").insert({
                    "product_group_id": id,
                    "product_id": product_id
                })
            return ResponseService.response("SUCCESS", {}, "default_update_success_msg")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

def get_product_group_products(request, id):
    try:
        all_columns = [
            "core_products.*",
            "core_users.display_name as added_by",
            "crm_opportunity_types.title as type",
            "core_currencies.id as currency_id",
            "core_currencies.symbol as currency_symbol",
            "core_currencies.name as currency_name",
            "core_currencies.code as currency_code",
        ]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["id","name"]
        
        # Get unique products without vendor product joins to avoid duplicates
        data = (
            QueryBuilderService("core_product_group_products")
            .where("core_product_group_products.product_group_id", id)
            .leftJoin("core_products", "core_product_group_products.product_id", "core_products.id")
            .leftJoin("crm_opportunity_types", "core_products.category_id", "crm_opportunity_types.id")
            .select(
                "core_products.id",
                "core_products.name",
                "core_products.code",
                "core_products.category_id",
                "core_products.created_at",
                "core_products.updated_at",
                "core_products.deleted_at",
                "crm_opportunity_types.title as type"
            )
            .apply_conditions(filter_json, [], search_string, ["core_products.name"])
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )
        
        # Add currency info, added_by, and insurer details for each product by querying vendor products separately
        if data and "data" in data:
            for product in data["data"]:
                # Get currency, added_by, and insurer info from first vendor product for this product
                vendor_product = QueryBuilderService("core_product_vendor_products")\
                    .leftJoin("core_vendor_products", "core_product_vendor_products.vendor_product_id", "core_vendor_products.id")\
                    .leftJoin("core_currencies", "core_vendor_products.currency_id", "core_currencies.id")\
                    .leftJoin("core_users", "core_vendor_products.added_by", "core_users.id")\
                    .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")\
                    .select(
                        "core_currencies.id as currency_id",
                        "core_currencies.symbol as currency_symbol",
                        "core_currencies.name as currency_name",
                        "core_currencies.code as currency_code",
                        "core_users.display_name as added_by",
                        "core_service_providers.id as insurer_id",
                        "core_service_providers.name as insurer_name",
                        "core_service_providers.logo as insurer_logo",
                        "core_service_providers.email as insurer_email",
                        "core_service_providers.contact_no as insurer_contact_no",
                        "core_service_providers.address as insurer_address",
                        "core_service_providers.website as insurer_website"
                    )\
                    .where("core_product_vendor_products.product_id", product["id"])\
                    .first()
                
                if vendor_product:
                    product["currency_id"] = vendor_product.get("currency_id")
                    product["currency_symbol"] = vendor_product.get("currency_symbol")
                    product["currency_name"] = vendor_product.get("currency_name")
                    product["currency_code"] = vendor_product.get("currency_code")
                    product["added_by"] = vendor_product.get("added_by")
                    product["insurer"] = {
                        "id": vendor_product.get("insurer_id"),
                        "name": vendor_product.get("insurer_name"),
                        "logo": vendor_product.get("insurer_logo"),
                        "email": vendor_product.get("insurer_email"),
                        "contact_no": vendor_product.get("insurer_contact_no"),
                        "address": vendor_product.get("insurer_address"),
                        "website": vendor_product.get("insurer_website")
                    }
                else:
                    product["currency_id"] = None
                    product["currency_symbol"] = None
                    product["currency_name"] = None
                    product["currency_code"] = None
                    product["added_by"] = None
                    product["insurer"] = None


        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")



@api_view(["DELETE"])
def delete_product_group_teams(request, id, team_id):
    try:
        QueryBuilderService("core_product_group_teams").where("product_group_id", id).where("team_id", team_id).delete()

        return ResponseService.response("SUCCESS", {}, "default_delete_success_msg")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

@api_view(["DELETE"])
def delete_product_group_products(request, id, product_id):
    try:
        QueryBuilderService("core_product_group_products").where("product_group_id", id).where("product_id", product_id).delete()
        return ResponseService.response("SUCCESS", {}, "default_delete_success_msg")
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")

@api_view(["GET", "PUT", "DELETE"])
def product_group_detail(request, id):
    if request.method == "GET":
        return get_product_group(request, id)
    if request.method == "PUT":
        return update_product_group(request, id)
    if request.method == "DELETE":
        return delete_product_group(request, id)
    
def get_product_group(request, id):
    # Validate the ID
    product_group_id = QueryBuilderService("core_product_groups").where("id", id).first()
    if not product_group_id:
        return ResponseService.response("NOT_FOUND", {}, "Product group not found!")

    all_columns = [
        "core_product_groups.*",
        "core_products.name as native_product_name",
        "core_products.id as native_product_id",
        "core_teams.id as team_id",
        "core_teams.name as team_name",
    ]

    # Query database
    data = (
        QueryBuilderService("core_product_groups")
        .leftJoin("core_product_group_products", "core_product_group_products.product_group_id", "core_product_groups.id")
        .leftJoin("core_products", "core_product_group_products.product_id", "core_products.id")
        .leftJoin("core_product_group_teams", "core_product_group_teams.product_group_id", "core_product_groups.id")
        .leftJoin("core_teams", "core_product_group_teams.team_id", "core_teams.id")
        .select(*all_columns)
        .where('core_product_groups.id', id)
        .whereNull('core_product_groups.deleted_at')
        .get()
    )

    # Ensure data is a list
    if not isinstance(data, list):
        data = [data]
    
    groups = {}
    for row in data:
        group_id = row["id"]
        if group_id not in groups:
            group = {k: v for k, v in row.items() if not k.startswith("native_product")}
            group["native_products"] = []
            group["teams"] = []
            groups[group_id] = group
        if row.get("native_product_id"):
            product = {
                "id": row["native_product_id"],
                "name": row["native_product_name"],
            }
            if product not in groups[group_id]["native_products"]:
                groups[group_id]["native_products"].append(product)
        if row.get("team_id"):
            team = {
                "id": row["team_id"],
                "name": row["team_name"],
            }
            if team not in groups[group_id]["teams"]:
                groups[group_id]["teams"].append(team)
                
    result = list(groups.values()) 

    return ResponseService.response("SUCCESS", result, Message.DATA_FETCHED)



def update_product_group(request, id):

    # Validate the ID
    product_group_id = QueryBuilderService("core_product_groups").where("id", id).first()
    if not product_group_id:
        return ResponseService.response("NOT_FOUND", {}, "Product group not found!")

    data = json.loads(request.body)

    rules = {
        "name": "required",
        "product_ids": "required|array",
        "team_ids": "required|array|exists:core_teams,id",
        "currency_id": "nullable|exists:core_currencies,id",
    }
    if "team_ids" not in data or not data["team_ids"]:
        return ResponseService.response(
            "VALIDATION_ERROR", 
            {"team_ids": ["At least one team is required"]}, 
            "Validation Error"
        )
    if "product_ids" not in data or not data["product_ids"]:
        return ResponseService.response(
            "VALIDATION_ERROR", 
            {"product_ids": ["At least one product is required"]}, 
            "Validation Error"
        )
   

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    new_data = {
        "name": data["name"],
        "currency_id": data["currency_id"] if data["currency_id"] else None,
        # Add more fields as needed
    }

    update = QueryBuilderService("core_product_groups").where('id', id).update(new_data)
    if update:
        # Delete existing products
        QueryBuilderService("core_product_group_products").where('product_group_id', id).delete()

        # Insert new products
        for product_id in data["product_ids"]:
            new_product = {
                "product_group_id": id,
                "product_id": product_id,
            }
            QueryBuilderService("core_product_group_products").insert(new_product)

    team_update = QueryBuilderService("core_product_group_teams").where('product_group_id', id).delete()
    for team_id in data["team_ids"]:
        new_team = {
            "product_group_id": id,
            "team_id": team_id,
        }
        QueryBuilderService("core_product_group_teams").insert(new_team)
        

         # Update the group code
        return ResponseService.response("SUCCESS", {}, Message.DATA_UPDATED)
    else:
        return ResponseService.response("NOT_FOUND", {}, f"{id} Failed to update product group!")
    
    


def delete_product_group(request, id):

    # Validate the ID
    product_group_id = QueryBuilderService("core_product_groups").where("id", id).first()   

    if not product_group_id:
        return ResponseService.response("NOT_FOUND", {}, "Product group not found!")
    now = datetime.datetime.now()
    formatted_now = now.strftime("%Y-%m-%d %H:%M:%S")
    # Delete the product
    delete = QueryBuilderService("core_product_groups").where('id', id).update({'deleted_at': formatted_now})
    if delete:
        return ResponseService.response("SUCCESS", {}, Message.DATA_DELETED)
    else:
        return ResponseService.response("NOT_FOUND", {}, f"{id} Failed to delete product group!")


@api_view(["GET"])
def native_vendor_products(request, id):

 try:
    """Fetch all products with pagination and search functionality."""

    all_columns = [
        "core_vendor_products.*",
        "core_currencies.symbol as currency",
        "crm_opportunity_types.title as type",
        "core_users.display_name as added_by",
        "core_service_providers.id as insurer_id",
        "core_service_providers.name as insurer_name",
        "core_service_providers.logo as insurer_logo",
        "core_service_providers.address as insurer_address",
        "core_service_providers.contact_no as insurer_contact_no",
        "core_service_providers.email as insurer_email",
        "core_service_providers.website as insurer_website",
        "core_service_providers.fax_no as insurer_fax_no",
        "core_service_providers.user_id as insurer_user_id",
        "core_service_providers.created_at as insurer_created_at",
        "core_service_providers.created_by_id as insurer_created_by_id",
        "core_service_providers.description as insurer_description",
        "core_service_providers.status_id as insurer_status_id",
        "core_service_providers.updated_at as insurer_updated_at",
        "core_service_providers.updated_by_id as insurer_updated_by_id",
    ]

    # Extract query parameters for filtering, sorting, and pagination
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    allowed_sorting_columns = ["name"]

    # # Query database
    # data = (
    #     QueryBuilderService("core_product_vendor_products")
    #     .leftJoin("core_vendor_products", "core_product_vendor_products.vendor_product_id", "core_vendor_products.id")
    #     .leftJoin("core_products", "core_product_vendor_products.product_id", "core_products.id")
    #     .leftJoin("core_currencies", "core_vendor_products.currency_id", "core_currencies.id")
    #     .leftJoin("crm_opportunity_types", "core_vendor_products.category_id", "crm_opportunity_types.id")
    #     .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
    #     .leftJoin("core_users", "core_vendor_products.added_by", "core_users.id")
    #     .select(*all_columns)
    #     .whereNull('core_vendor_products.deleted_at')
    #     .where('core_product_vendor_products.product_id', id)
    #     .apply_conditions(filter_json, [], search_string, ["name"])
    #     .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    # )

    data = (
    QueryBuilderService("core_product_vendor_products")
    .leftJoin("core_vendor_products", "core_product_vendor_products.vendor_product_id", "core_vendor_products.id")
    .leftJoin("core_products", "core_product_vendor_products.product_id", "core_products.id")
    .leftJoin("core_currencies", "core_vendor_products.currency_id", "core_currencies.id")
    .leftJoin("crm_opportunity_types", "core_vendor_products.category_id", "crm_opportunity_types.id")
    .leftJoin("core_service_providers", "core_vendor_products.vendor_id", "core_service_providers.id")
    .leftJoin("core_users", "core_vendor_products.added_by", "core_users.id")
    .select(*all_columns)
    # .distinct()
    .whereNull('core_vendor_products.deleted_at')
    .where('core_product_vendor_products.product_id', id)
    .apply_conditions(filter_json, [], search_string, ["name"])
    .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    # Add complete insurer object to each product item
    if data and isinstance(data, dict) and 'data' in data:
        for item in data['data']:
            if item.get('insurer_id'):
                # Create complete insurer object for each product
                item['insurer'] = {
                    'id': item['insurer_id'],
                    'name': item['insurer_name'],
                    'logo': item['insurer_logo'],
                    'address': item['insurer_address'],
                    'contact_no': item['insurer_contact_no'],
                    'email': item['insurer_email'],
                    'website': item['insurer_website'],
                    'fax_no': item['insurer_fax_no'],
                    'user_id': item['insurer_user_id'],
                    'created_at': item['insurer_created_at'],
                    'created_by_id': item['insurer_created_by_id'],
                    'description': item['insurer_description'],
                    'status_id': item['insurer_status_id'],
                    'updated_at': item['insurer_updated_at'],
                    'updated_by_id': item['insurer_updated_by_id'],
                }
                
                # Remove individual insurer fields to clean up the response
                insurer_fields_to_remove = [
                    'insurer_id', 'insurer_name', 'insurer_logo', 'insurer_address',
                    'insurer_contact_no', 'insurer_email', 'insurer_website', 
                    'insurer_fax_no', 'insurer_user_id', 'insurer_created_at',
                    'insurer_created_by_id', 'insurer_description', 'insurer_status_id',
                    'insurer_updated_at', 'insurer_updated_by_id'
                ]
                for field in insurer_fields_to_remove:
                    item.pop(field, None)


    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

 except Exception as e:
    import traceback
    traceback.print_exc()
    return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")



@api_view(["PUT"])
def add_product_in_group(request, id):
    try:
        # Validate the group ID exists
        product_group = QueryBuilderService("core_product_groups").where("id", id).first()
        if not product_group:
            return ResponseService.response("NOT_FOUND", {}, "Product group not found!")

        data = json.loads(request.body)

        # Define validation rules
        rules = {
            "product_ids": "required|array"
        }

        # Validate using ValidatorService
        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Check for existing products
        exist_products = (QueryBuilderService("core_product_group_products")
            .where("product_group_id", id)
            .whereIn("product_id", data["product_ids"])
            .get())

        if exist_products:
            return ResponseService.response(
                "VALIDATION_ERROR", 
                {"product_ids": "Products already exist in this group"},
                "products_already_exist"
            )

        # Validate products exist in core_products
        valid_products = (QueryBuilderService("core_products")
            .whereIn("id", data["product_ids"])
            .whereNull("deleted_at")
            .get())

        if len(valid_products) != len(data["product_ids"]):
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"product_ids": "One or more product IDs do not exist"},
                "Invalid product IDs"
            )

        # Insert new products into group
        for product_id in data["product_ids"]:
            QueryBuilderService("core_product_group_products").insert({
                "product_group_id": id,
                "product_id": product_id
            })

        return ResponseService.response("SUCCESS", {}, Message.DATA_UPDATED)

    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR", 
            {"request": "Invalid JSON format"}, 
            "Invalid request body"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")
# @api_view(["PUT"])
# def add_product_in_group(request, id):
#     try:
#         """Add a product to a product group."""

#         # Validate the ID
#         product_group_id = QueryBuilderService("core_product_groups").where("id", id).first()
#         if not product_group_id:
#             return ResponseService.response("NOT_FOUND", {}, "Product group not found!")

#         data = json.loads(request.body)

#         rules = {
#             "product_ids": "required|array",
#         }

#         exist_products = QueryBuilderService("core_product_group_products").where("product_group_id", id).whereIn("product_id", data["product_ids"]).get()

#         if exist_products:
#             return ResponseService.response("NOT_FOUND", {}, "products_already_exist")

#         errors = ValidatorService.validate(data, rules)
#         if errors:
#             return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#         # Insert new products into the group
#         for product_id in data["product_ids"]:
#             new_product = {
#                 "product_group_id": id,
#                 "product_id": product_id,
#             }
#             QueryBuilderService("core_product_group_products").insert(new_product)

#         return ResponseService.response("SUCCESS", {}, Message.DATA_UPDATED)
#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")






# ----------------------------------------------------------------------------------

@api_view(["GET"])
def coverage_levels(request):
    """Fetch all products with pagination and search functionality."""

    data = [
        {
            "id": 1,
            "name": "Basic",
        },
        {
            "id": 2,
            "name": "Plus",
        },
        {
            "id": 3,
            "name": "Premium",
        },
    ]

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


@api_view(["DELETE"])
def unlink_native_product(request, id, vendor_product_id):
    """Unlink a native product from a vendor product, but keep at least one link."""

    # Validate the product
    native = QueryBuilderService("core_products").where("id", id).first()
    if not native:
        return ResponseService.response("NOT_FOUND", {}, "Product not found!")

    # Count how many vendor-product links this product has
    vendor_links_count = QueryBuilderService("core_product_vendor_products") \
        .where("product_id", id) \
        .count()

    if vendor_links_count <= 1:
        return ResponseService.response(
            "CONFLICT",
            {},
            "Cannot unlink the only vendor product. A product must have at least one vendor association."
        )

    # Proceed to delete the mapping
    deleted = QueryBuilderService("core_product_vendor_products") \
        .where("product_id", id) \
        .where("vendor_product_id", vendor_product_id) \
        .delete()

    if deleted:
        return ResponseService.response("SUCCESS", {}, "Vendor product unlinked successfully.")
    else:
        return ResponseService.response("NOT_FOUND", {}, f"Failed to unlink vendor product {vendor_product_id} from product {id}.")

# -------------------------------------------------------------

@api_view(["GET"])
def opportunity_type(request):
    try:
        all_columns = [
            "crm_opportunity_types.id",
            "crm_opportunity_types.title",
            "crm_opportunity_types.description",
        ]
        
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        # Extract query parameters for filtering, sorting, and pagination
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "crm_opportunity_types.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        allowed_filters = ["crm_opportunity_types.id", "crm_opportunity_types.title"]
        search_columns = ["crm_opportunity_types.id", "crm_opportunity_types.title"]
        allowed_sorting_columns = ["crm_opportunity_types.id", "crm_opportunity_types.title"]

        query = QueryBuilderService("crm_opportunity_types")\
                .select(*all_columns)\
                .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
                .paginate(page, limit,allowed_sorting_columns, sort_by, sort_dir)

        return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


@api_view(["GET"])
def risk_types(request):
    try:
        lead_id = request.GET.get("lead_id")
        
        all_columns = [
            "crm_opportunity_types.id",
            "crm_opportunity_types.title",
            "crm_opportunity_types.description",
        ]
        
        # Extract query parameters for filtering, sorting, and pagination
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "crm_opportunity_types.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        allowed_filters = ["crm_opportunity_types.id", "crm_opportunity_types.title"]
        search_columns = ["crm_opportunity_types.id", "crm_opportunity_types.title"]
        allowed_sorting_columns = ["crm_opportunity_types.id", "crm_opportunity_types.title"]

        # If lead_id is provided, filter opportunity types based on that lead
        if lead_id:
            # Use JOIN to get opportunity types directly with proper pagination
            query = QueryBuilderService("crm_opportunity_types")\
                .select(*all_columns)\
                .leftJoin("crm_oppor_opportunity_types", "crm_oppor_opportunity_types.opportunity_type_id", "crm_opportunity_types.id")\
                .where("crm_oppor_opportunity_types.opportunity_id", lead_id)\
                .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        else:
            # If no lead_id provided, return all opportunity types
            query = QueryBuilderService("crm_opportunity_types")\
                    .select(*all_columns)\
                    .apply_conditions(filter_json, allowed_filters, search_string, search_columns)\
                    .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

        return ResponseService.response('SUCCESS', query, Message.DATA_FETCHED)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


@api_view(["GET"])
def get_all_service_providers(request):
  
    all_columns = [
        "core_service_providers.id",
        "core_service_providers.name",
        "core_service_providers.description",
        "core_service_providers.status",
    ]   

    filter_json = request.GET.get("filter", {}) 
    search_string = request.GET.get("search", "name")
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
    
    return ResponseService.response('SUCCESS',query, Message.DATA_FETCHED)

@api_view(["GET"])
def policy_product_documents(request, id):
    try:
        all_columns = [
            "core_product_document_types.*",
        ]

        # Extract query parameters for filtering, sorting, and pagination
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["name"]

        data = (
            QueryBuilderService("core_product_document_types")
            .select(*all_columns)
            .where('vendor_product_id', id)
            .where('type', 'policy')
            .apply_conditions(filter_json, [], search_string, ["name"])
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )
        
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


@api_view(["GET"])
def risk_product_documents(request, id):
    try:
        all_columns = [
            "core_product_document_types.*",
        ]

        # Extract query parameters for filtering, sorting, and pagination
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["name"]

        data = (
            QueryBuilderService("core_product_document_types")
            .select(*all_columns)
            .where('vendor_product_id', id)
            .where('type', 'risk')
            .apply_conditions(filter_json, [], search_string, ["name"])
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )
        
        return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")


# @api_view(["GET"])
# def coverage_types(request):
#     try:
#         all_columns = [
#             "core_types.*",
#         ]

#         # Extract query parameters for filtering, sorting, and pagination
#         filter_json = request.GET.get("filter", {})
#         search_string = request.GET.get("search", "")
#         page = int(request.GET.get("page", 1))
#         limit = int(request.GET.get("limit", 10))
#         sort_by = request.GET.get("sort_by", "id")
#         sort_dir = request.GET.get("sort_dir", "desc")
#         allowed_sorting_columns = ["name"]

#         data = (
#             QueryBuilderService("core_types")
#             .where('type', 'product')
#             .where('module', 'core')
#             .select(*all_columns)
#             .apply_conditions(filter_json, [], search_string, ["name"])
#             .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
#         )
        
#         return ResponseService.response("SUCCESS", data, "Coverage types retrieved successfully!")

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return ResponseService.response("NOT_FOUND", {}, f"Server Error: {str(e)}")



@api_view(["GET", "POST",])
def product_teams(request,product_id):

    if request.method == "GET":
        return get_product_teams(request, product_id)
    
    if request.method == "POST":
        return assign_team_to_product(request,product_id)


def assign_team_to_product(request, product_id):
    try:
        data = json.loads(request.body)

        # Merge product_id from URL into validation data
        data["product_id"] = product_id

        rules = {
            "product_id": "required|exists:core_products,id",
            "team_id": "required|exists:core_teams,id"
        }

        custom_messages = {
            "product_id.required": "Product ID is required.",
            "product_id.exists": "Product does not exist.",
            "team_id.required": "Team ID is required.",
            "team_id.exists": "Team does not exist."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        with transaction.atomic():
            if not ProductTeam.objects.filter(product_id=product_id, team_id=data["team_id"]).exists():
                ProductTeam.objects.create(product_id=product_id, team_id=data["team_id"])

        return ResponseService.response("SUCCESS", None, Message.DATA_CREATED)

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
    



def get_product_teams(request, product_id):
    try:
        # Validate product_id exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM core_products WHERE id = %s", [product_id])
            if cursor.fetchone() is None:
                return ResponseService.response("VALIDATION_ERROR", {"product_id": ["Product not found"]}, "Validation Error")

        # Pagination params
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))
        sort_by = request.GET.get("sort_by", "core_teams.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        # Columns to select
        all_columns = [
            "core_teams.id",
            "core_teams.name",
            "core_teams.description",
            "core_teams.manager_id",
            "u2.display_name AS manager_name",
            "MAX(core_product_teams.created_at) AS latest_created_at"
        ]

        # Query using core_product_teams
        query = QueryBuilderService("core_product_teams") \
            .leftJoin("core_teams", "core_teams.id", "core_product_teams.team_id") \
            .leftJoin("core_users AS u2", "u2.id", "core_teams.manager_id") \
            .select(*all_columns) \
            .where("core_product_teams.product_id", product_id) \
            .groupBy("core_teams.id") \
            .paginate(
                page,
                per_page,
                allowed_sorting_columns=["core_teams.name", "core_teams.id"],
                sort_by=sort_by,
                sort_dir=sort_dir
            )

        return ResponseService.response(
            "SUCCESS",
            query,
            Message.DATA_FETCHED
        )

    except ValueError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"pagination": ["Invalid pagination parameters"]},
            "Invalid Request"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error"
        )



@api_view(["DELETE"])
def delete_product_team(request, product_id, team_id):
    try:
        # Check if product exists
        if not Product.objects.filter(id=product_id).exists():
            return ResponseService.response(
                "NOT_FOUND",
                {"detail": "Product not found."},
                "Validation Error"
            )

        # Check if team exists
        if not Team.objects.filter(id=team_id).exists():
            return ResponseService.response(
                "NOT_FOUND",
                {"detail": "Team not found."},
                "Validation Error"
            )

        # Check if the relation exists
        if not ProductTeam.objects.filter(product_id=product_id, team_id=team_id).exists():
            return ResponseService.response(
                "NOT_FOUND",
                {"detail": "This team is not assigned to the specified product."},
                "default_error_msg"
            )

        # Delete the relation
        ProductTeam.objects.filter(product_id=product_id, team_id=team_id).delete()

        return ResponseService.response(
            "SUCCESS",
            None,
            Message.DATA_DELETED
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error"
        )
    



@api_view(["GET"])
def get_product_coverages(request, product_id):
    try:
        # Check product exists
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM core_products WHERE id = %s", [product_id])
            if cursor.fetchone() is None:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"product_id": ["Product not found"]},
                    "Validation Error"
                )

        # Pagination
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))
        sort_by = request.GET.get("sort_by", "core_product_coverages.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        # Columns
        all_columns = [
            "core_product_coverages.id",
            "core_product_coverages.name",
            "core_product_coverages.coverage_amount",
            "core_product_coverages.excess_amount",
            "core_product_coverages.limitation",
            "core_product_coverages.is_mandatory",
            "core_vendor_products.name AS vendor_product_name",
            "core_vendor_products.code AS vendor_product_code"
        ]

        # QueryBuilderService chain
        query = QueryBuilderService("core_product_coverages") \
            .select(*all_columns) \
            .leftJoin(
                "core_vendor_products",
                "core_vendor_products.id",
                "core_product_coverages.vendor_product_id"
            ) \
            .leftJoin(
                "core_product_vendor_products",
                "core_product_vendor_products.vendor_product_id",
                "core_vendor_products.id"
            ) \
            .where("core_product_vendor_products.product_id", product_id) \
            .groupBy("core_product_coverages.id") \
            .paginate(
                page,
                per_page,
                allowed_sorting_columns=["core_product_coverages.name", "core_product_coverages.id"],
                sort_by=sort_by,
                sort_dir=sort_dir
            )

        return ResponseService.response(
            "SUCCESS",
            query,
            Message.DATA_FETCHED
        )

    except ValueError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"pagination": ["Invalid pagination parameters"]},
            "Invalid Request"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error"
        )



@api_view(["GET"])
def get_product_document_types(request, product_id):
    try:
        # Pagination parameters
        page = int(request.GET.get("page", 1))
        per_page = int(request.GET.get("per_page", 10))
        sort_by = request.GET.get("sort_by", "core_product_document_types.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        # Support filters via query param like ?type=risk
        filter_aliases = {
            "type": "core_product_document_types.type"
        }

        raw_filter_json = request.GET.get("filters", "{}")
        if raw_filter_json in ["undefined", "", None]:
            raw_filter_json = "{}"

        # Combine filters from ?filters={} and query params like ?type=risk
        filter_dict = json.loads(raw_filter_json)

        # Merge query string filters manually
        for key, column in filter_aliases.items():
            value = request.GET.get(key)
            if value:
                filter_dict[column] = {"o": "=", "v": value}

        mapped_filter_json = json.dumps(filter_dict)

        # Define the columns to fetch
        all_columns = [
            "core_product_document_types.*",
            "core_vendor_products.name as vendor_product_name",
            "core_vendor_products.code as vendor_product_code"
        ]

        # Build the query
        query = QueryBuilderService("core_product_document_types") \
            .select(*all_columns) \
            .leftJoin(
                "core_vendor_products",
                "core_vendor_products.id",
                "core_product_document_types.vendor_product_id"
            ) \
            .leftJoin(
                "core_product_vendor_products",
                "core_product_vendor_products.vendor_product_id",
                "core_vendor_products.id"
            ) \
            .where("core_product_vendor_products.product_id", product_id) \
            .apply_conditions(mapped_filter_json, list(filter_aliases.values()), None, None) \
            .groupBy("core_product_document_types.id") \
            .paginate(
                page,
                per_page,
                allowed_sorting_columns=["core_product_document_types.name", "core_product_document_types.id"],
                sort_by=sort_by,
                sort_dir=sort_dir
            )

        return ResponseService.response(
            "SUCCESS",
            query,
            Message.DATA_FETCHED
        )

    except ValueError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"pagination": ["Invalid pagination parameters"]},
            "Invalid Request"
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error"
        )






@api_view(["DELETE"])
def delete_product_vendor_product(request, product_id, vendor_product_id):
    try:
        # Use QueryBuilderService to check if the record exists
        record = QueryBuilderService("core_product_vendor_products") \
            .where("product_id", product_id) \
            .where("vendor_product_id", vendor_product_id) \
            .first()

        if not record:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"mapping": ["No mapping found for the given product and vendor product."]},
                "Validation Error"
            )

        # Proceed to delete
        QueryBuilderService("core_product_vendor_products") \
            .where("product_id", product_id) \
            .where("vendor_product_id", vendor_product_id) \
            .delete()

        return ResponseService.response(
            "SUCCESS",
            None,
            f"Vendor product {vendor_product_id} removed from product {product_id}."
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Server Error"
        )




@api_view(['GET'])
def get_vendor_products_by_risk_type(request):
    try:
        risk_type_id = request.GET.get("risk_type_id")

        if not risk_type_id or not risk_type_id.isdigit():
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error": "A valid risk_type_id is required"},
                ErrorMessages.VALIDATION_ERROR
            )

        # Convert to integer
        # risk_type_id = int(risk_type_id)

        # Query vendor products where category_id = risk_type_id
        vendor_products = (
            QueryBuilderService("core_vendor_products")
            .select(
                "*",
            )
            .where("category_id", risk_type_id)
            .whereNull("deleted_at")
            .get()
        )

        return ResponseService.response(
            "SUCCESS",
            vendor_products,
            Message.DATA_FETCHED
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "Failed to retrieve vendor products"
        )
    





@api_view(["GET"])
@permission_classes([IsAuthenticated])
def insurer_product_documents(request):
    """Fetch product documents with pagination and search functionality."""

    # Get product IDs from request
    product_ids = request.GET.get("product_id", "").split(",")
    product_ids = [int(pid.strip()) for pid in product_ids if pid.strip().isdigit()]

    if not product_ids:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"product_id": ["product_id is required (comma-separated)."]},
            "Validation Error",
        )

    # Query parameters
    doc_type = request.GET.get("type")
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    allowed_sorting_columns = ["id", "name", "code", "type", "updated_at", "created_at"]
    allowed_searching_columns = ["name", "code"]

    # Build query
    query = (
        QueryBuilderService("core_product_document_types")
        .select("core_product_document_types.*")
        .whereIn("vendor_product_id", product_ids)
    )

    if doc_type:
        query = query.where("type", doc_type)

    # Apply conditions and pagination
    data = (
        query.apply_conditions(filter_json, [], search_string, allowed_searching_columns)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)



@api_view(["GET"])
def get_vendor_products_by_risk_type(request):
    """
    Get vendor products or product groups based on risk type IDs, service provider, or product ID.
    
    For single risk_type_id: Returns vendor products directly with search, pagination, and sorting
    For multiple risk_type_ids: Returns product groups containing products from all requested risk types
    If no risk_type_id: Returns vendor products filtered by service_provider_id and/or product_id
    """
    try:
        # Get and parse params
        raw_ids = request.GET.get("risk_type_id", "")
        risk_type_ids = [int(x) for x in raw_ids.split(",") if x.strip().isdigit()]
        
        # Get other filter parameters and validate them
        service_provider_id_raw = request.GET.get("service_provider_id", "").strip()
        product_id_raw = request.GET.get("product_id", "").strip()
        
        # Convert to integers if provided and valid
        service_provider_id = None
        product_id = None
        
        if service_provider_id_raw and service_provider_id_raw.isdigit():
            service_provider_id = int(service_provider_id_raw)
        
        if product_id_raw and product_id_raw.isdigit():
            product_id = int(product_id_raw)
        
        # Validate that at least one filter is provided
        if not risk_type_ids and not service_provider_id and not product_id:
            return ResponseService.response(
                "VALIDATION_ERROR", 
                {"filters": "At least one filter is required: risk_type_id, service_provider_id, or product_id."}, 
                ErrorMessages.VALIDATION_ERROR
            )

        # Handle single risk_type_id case
        if len(risk_type_ids) == 1:
            return _get_vendor_products_single_risk_type(request, risk_type_ids[0])
        
        # Handle multiple risk_type_ids case
        if len(risk_type_ids) > 1:
            return _get_product_groups_multiple_risk_types(risk_type_ids)
        
        # Handle case where no risk_type_id is provided (filter by service_provider_id and/or product_id only)
        return _get_vendor_products_without_risk_type(request)

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            None, 
            ErrorMessages.INTERNAL_SERVER_ERROR
        )


def _get_vendor_products_single_risk_type(request, risk_type_id):
    """Get vendor products for a single risk type with search, sorting, and pagination."""
    # Extract query parameters for filtering and search
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    
    # Extract and validate additional filter parameters
    service_provider_id_raw = request.GET.get("service_provider_id", "").strip()
    product_id_raw = request.GET.get("product_id", "").strip()
    
    # Convert to integers if provided and valid
    service_provider_id = None
    product_id = None
    
    if service_provider_id_raw and service_provider_id_raw.isdigit():
        service_provider_id = int(service_provider_id_raw)
    
    if product_id_raw and product_id_raw.isdigit():
        product_id = int(product_id_raw)
    
    allowed_filters = []
    allowed_searching_columns = ["core_vendor_products.name", "core_vendor_products.code"]
    allowed_sorting_columns = ["id", "name", "code", "created_at"]
    
    # Start building query
    query = QueryBuilderService("core_vendor_products")
    
    # If product_id is provided, we need to join with core_product_vendor_products
    if product_id:
        query = query.leftJoin(
            "core_product_vendor_products",
            "core_product_vendor_products.vendor_product_id",
            "core_vendor_products.id"
        )
        query = query.where("core_product_vendor_products.product_id", product_id)
    
    # Apply base filters
    query = query.select("core_vendor_products.*")
    query = query.where("core_vendor_products.category_id", risk_type_id)
    query = query.whereNull("core_vendor_products.deleted_at")
    
    # Apply service_provider_id filter if provided
    if service_provider_id:
        query = query.where("core_vendor_products.vendor_id", service_provider_id)
    
    # Apply search and other conditions
    query = query.apply_conditions(filter_json, allowed_filters, search_string, allowed_searching_columns)
    
    # If product_id filter was used, we need to group by to avoid duplicates
    if product_id:
        query = query.groupBy("core_vendor_products.id")
    
    # Apply pagination and sorting; pass list directly in result (same format as before)
    paginated = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    data = paginated.get("data", paginated) if isinstance(paginated, dict) else paginated

    return ResponseService.response(
        "SUCCESS",
        data,
        Message.DATA_FETCHED
    )


def _get_vendor_products_without_risk_type(request):
    """Get vendor products filtered by service_provider_id and/or product_id (without risk_type_id)."""
    # Extract query parameters for filtering and search
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    
    # Extract and validate filter parameters
    service_provider_id_raw = request.GET.get("service_provider_id", "").strip()
    product_id_raw = request.GET.get("product_id", "").strip()
    
    # Convert to integers if provided and valid
    service_provider_id = None
    product_id = None
    
    if service_provider_id_raw and service_provider_id_raw.isdigit():
        service_provider_id = int(service_provider_id_raw)
    
    if product_id_raw and product_id_raw.isdigit():
        product_id = int(product_id_raw)
    
    # Validate that at least one filter is provided
    if not service_provider_id and not product_id:
        return ResponseService.response(
            "VALIDATION_ERROR", 
            {"filters": "At least one valid filter is required: service_provider_id or product_id."}, 
            ErrorMessages.VALIDATION_ERROR
        )
    
    allowed_filters = []
    allowed_searching_columns = ["core_vendor_products.name", "core_vendor_products.code"]
    allowed_sorting_columns = ["id", "name", "code", "created_at"]
    
    # Start building query
    query = QueryBuilderService("core_vendor_products")
    
    # If product_id is provided, we need to join with core_product_vendor_products
    if product_id:
        query = query.leftJoin(
            "core_product_vendor_products",
            "core_product_vendor_products.vendor_product_id",
            "core_vendor_products.id"
        )
        query = query.where("core_product_vendor_products.product_id", product_id)
    
    # Apply base filters
    query = query.select("core_vendor_products.*")
    query = query.whereNull("core_vendor_products.deleted_at")
    
    # Apply service_provider_id filter if provided
    if service_provider_id:
        query = query.where("core_vendor_products.vendor_id", service_provider_id)
    
    # Apply search and other conditions
    query = query.apply_conditions(filter_json, allowed_filters, search_string, allowed_searching_columns)
    
    # If product_id filter was used, we need to group by to avoid duplicates
    if product_id:
        query = query.groupBy("core_vendor_products.id")
    
    # Apply pagination and sorting; pass list directly in result (same format as before)
    paginated = query.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    data = paginated.get("data", paginated) if isinstance(paginated, dict) else paginated

    return ResponseService.response(
        "SUCCESS",
        data,
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
def get_native_products_by_risk_type(request):
    """
    Get native products or product groups based on risk type IDs.
    
    For single risk_type_id: Returns native products directly
    For multiple risk_type_ids: Returns product groups containing products from all requested risk types
    """
    try:
        # Get and parse params
        raw_ids = request.GET.get("risk_type_id", "")
        risk_type_ids = [int(x) for x in raw_ids.split(",") if x.strip().isdigit()]

        # When no risk_type_id is passed, return empty result
        if not risk_type_ids:
            return ResponseService.response(
                "SUCCESS",
                [],
                Message.DATA_FETCHED
            )

        # Handle single risk_type_id case
        if len(risk_type_ids) == 1:
            return _get_native_products_single_risk_type(risk_type_ids[0])
        
        # Handle multiple risk_type_ids case
        return _get_product_groups_multiple_risk_types(risk_type_ids)

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", 
            None, 
            ErrorMessages.INTERNAL_SERVER_ERROR
        )


def _get_native_products_single_risk_type(risk_type_id):
    """Get native products for a single risk type."""
    native_products = QueryBuilderService("core_products")\
        .whereIn("category_id", [risk_type_id])\
        .whereNull("deleted_at")\
        .get()

    if not native_products:
        return ResponseService.response(
            "NOT_FOUND", 
            [], 
            ErrorMessages.NOT_FOUND
        )

    return ResponseService.response(
        "SUCCESS",
        native_products,
        Message.DATA_FETCHED
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

@api_view(["PUT"])
def add_insurer_product(request, id):
    try:
        data = json.loads(request.body)

        rules = {
            "insurer_product_ids": "required|array|exists:core_vendor_products,id"
        }

        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, ErrorMessages.VALIDATION_ERROR)
        
        if "insurer_product_ids" not in data or not data["insurer_product_ids"]:
            return ResponseService.response("VALIDATION_ERROR", {"insurer_product_ids": ["insurer_product_ids is required"]}, ErrorMessages.VALIDATION_ERROR)

        existing_insurer_products = QueryBuilderService("core_product_vendor_products").where("product_id", id).whereIn("vendor_product_id", data["insurer_product_ids"]).get()

        if existing_insurer_products:
            return ResponseService.response("VALIDATION_ERROR", {"insurer_product_ids": ["insurer_product_id_already_exists"]}, ErrorMessages.VALIDATION_ERROR)

        for insurer_product_id in data["insurer_product_ids"]:
            QueryBuilderService("core_product_vendor_products").insert({
                "product_id": id,
                "vendor_product_id": insurer_product_id
            })

        return ResponseService.response("SUCCESS", {}, Message.DATA_CREATED)
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {}, ErrorMessages.INTERNAL_SERVER_ERROR)


@api_view(["PUT"])
def native_product_mapping(request, id):
    try:
        data = json.loads(request.body)
        rules = {
            "native_product_ids": "required|array|exists:core_products,id"
        }

        errors = ValidatorService.validate(data, rules)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, ErrorMessages.VALIDATION_ERROR)
        
        if "native_product_ids" not in data or not data["native_product_ids"]:
            return ResponseService.response("VALIDATION_ERROR", {"native_product_ids": ["native_product_ids is required"]}, ErrorMessages.VALIDATION_ERROR)
            
        existing_native_products = QueryBuilderService("core_product_vendor_products").where("vendor_product_id", id).whereIn("product_id", data["native_product_ids"]).get()

        if existing_native_products:
            return ResponseService.response("VALIDATION_ERROR", {"native_product_ids": ["native_product_id_already_exists"]}, ErrorMessages.VALIDATION_ERROR)

        for native_product_id in data["native_product_ids"]:
            QueryBuilderService("core_product_vendor_products").insert({
                "vendor_product_id": id,
                "product_id": native_product_id
            })

        return ResponseService.response("SUCCESS", {}, Message.DATA_CREATED)
    except Exception as e:
        return ResponseService.response("NOT_FOUND", {}, ErrorMessages.INTERNAL_SERVER_ERROR)