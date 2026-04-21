from rest_framework.decorators import api_view
from envoy.models import ProductItem, Entity
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
from django.utils import timezone
import json


@api_view(["GET", "POST"])
def product_item_view(request):
    if request.method == "GET":
        return list_product_item(request)
    elif request.method == "POST":
        return create_product_item(request)


def list_product_item(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["entity_id"]
        search_columns = ["title", "description"]
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["id", "title", "description", "entity_id", "created_at", "updated_at"]

        all_columns = [
            "core_product_items.id",
            "core_product_items.title",
            "core_product_items.description",
            "core_product_items.entity_id",
            "core_entities.created_by_id",
            "core_entities.updated_by_id",
            "core_entities.created_at",
            "core_entities.updated_at",
            "created_by_user.display_name as created_by_display_name",
            "updated_by_user.display_name as updated_by_display_name"
        ]

        query = (
            QueryBuilderService("core_product_items")
            .leftJoin("core_entities", "core_entities.id", "core_product_items.entity_id")
            .leftJoin("core_users as created_by_user", "created_by_user.id", "core_entities.created_by_id")
            .leftJoin("core_users as updated_by_user", "updated_by_user.id", "core_entities.updated_by_id")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def create_product_item(request):
    try:
        data = json.loads(request.body)

        rules = {
            "title": "required|max:200",
            "description": "nullable"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.max": "Title cannot exceed 200 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Create entity first with created_by, updated_by, created_at, updated_at
        user = request.user if request.user.is_authenticated else None
        entity = Entity.objects.create(
            type="ProductItem",
            created_by=user,
            updated_by=user
        )

        # Create product item with the entity_id
        ProductItem.objects.create(
            title=data["title"],
            description=data.get("description", ""),
            entity=entity,   
        )

        return ResponseService.response("SUCCESS", None, "default_create_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "PUT", "DELETE"])
def product_item_detail(request, id):
    if request.method == "GET":
        return get_product_item(request, id)
    elif request.method == "PUT":
        return update_product_item(request, id)
    elif request.method == "DELETE":
        return delete_product_item(request, id)


def get_product_item(request, id):
    try:
        productItem = ProductItem.objects.get(id=id)
        data = {
            "id": productItem.id,
            "title": productItem.title,
            "description": productItem.description,
            "entity_id": productItem.entity.id if productItem.entity else None,
        }
        
        # Add entity details (created_by, updated_by, created_at, updated_at)
        if productItem.entity:
            data["created_by_id"] = productItem.entity.created_by.id if productItem.entity.created_by else None
            data["created_by_display_name"] = productItem.entity.created_by.display_name if productItem.entity.created_by else None
            data["updated_by_id"] = productItem.entity.updated_by.id if productItem.entity.updated_by else None
            data["updated_by_display_name"] = productItem.entity.updated_by.display_name if productItem.entity.updated_by else None
            data["created_at"] = productItem.entity.created_at
            data["updated_at"] = productItem.entity.updated_at
        
        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")
    except ProductItem.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")


def update_product_item(request, id):
    try:
        productItem = ProductItem.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "title": "required|max:200",
            "description": "nullable"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.max": "Title cannot exceed 200 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Update product item
        productItem.title = data["title"]
        productItem.description = data.get("description", "")
        productItem.save()

        # Update entity's updated_by and updated_at fields
        if productItem.entity:
            user = request.user if request.user.is_authenticated else None
            productItem.entity.updated_by = user
            productItem.entity.updated_at = timezone.now()
            productItem.entity.save()

        # Refresh the product item to get updated entity data
        productItem.refresh_from_db()
        if productItem.entity:
            productItem.entity.refresh_from_db()

        # Build response data with updated values
        response_data = {
            "id": productItem.id,
            "title": productItem.title,
            "description": productItem.description,
            "entity_id": productItem.entity.id if productItem.entity else None,
        }
        
        # Add entity details (created_by, updated_by, created_at, updated_at)
        if productItem.entity:
            response_data["created_by_id"] = productItem.entity.created_by.id if productItem.entity.created_by else None
            response_data["created_by_display_name"] = productItem.entity.created_by.display_name if productItem.entity.created_by else None
            response_data["updated_by_id"] = productItem.entity.updated_by.id if productItem.entity.updated_by else None
            response_data["updated_by_display_name"] = productItem.entity.updated_by.display_name if productItem.entity.updated_by else None
            response_data["created_at"] = productItem.entity.created_at
            response_data["updated_at"] = productItem.entity.updated_at

        return ResponseService.response("SUCCESS", response_data, "default_update_success_msg")
    except ProductItem.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_product_item(request, id):
    try:
        productItem = ProductItem.objects.get(id=id)
        productItem.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except ProductItem.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

