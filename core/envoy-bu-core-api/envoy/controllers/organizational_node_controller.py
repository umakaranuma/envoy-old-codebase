from rest_framework.decorators import api_view
from envoy.models.organizational_node import CoreOrganizationalNode
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json

@api_view(["GET", "POST"])
def organizational_node_view(request):
    if request.method == "GET":
        return list_organizational_node(request)
    elif request.method == "POST":
        return create_organizational_node(request)

def list_organizational_node(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = [
            "node.level_id", "node.parent_node_id",
            "node.created_by_id", "node.updated_by_id", "node.created_at"
        ]

        search_columns = ["node.name", "node.code"]

        sort_by = request.GET.get("sort_by", "node.id")
        sort_dir = request.GET.get("sort_dir", "desc")

        allowed_sorting_columns = [
            "node.id", "node.name", "node.level_id",
            "lvl.title as level_name", "node.branch_name", "node.code",
            "node.physical_address", "node.contact_no", "node.email",
            "node.parent_node_id", "node.created_by_id",
            "node.updated_by_id", "node.created_at", "node.updated_at"
        ]

        all_columns = [
            "node.id", "node.name", "node.level_id",
            "node.branch_name", "node.code", "node.physical_address",
            "node.contact_no", "node.email", "node.parent_node_id",
            "node.created_by_id", "node.updated_by_id",
            "node.created_at", "node.updated_at",
            "lvl.title as level_name"
        ]

        query = (
            QueryBuilderService(f"core_organizational_nodes as node")
            .leftJoin("core_organization_levels as lvl", "lvl.id", "node.level_id")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )


        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def create_organizational_node(request):
    try:
        if not request.body:
            return ResponseService.response("VALIDATION_ERROR", {"error": "request_body_empty"}, "Validation Error")
        data = json.loads(request.body)

        rules = {
            "name": "required|max:80",
            "code": "required|unique:core_organizational_nodes,code|max:100",
            "branch_name": "nullable|max:100",
            "description": "nullable|max:250",
            "level_id": "required|exists:core_organization_levels,id",
            "parent_node_id": "nullable|exists:core_organizational_nodes,id",
            "physical_address": "required|max:250",
            "email": "required|email|max:255",
            "contact_no": "nullable|max:80",
        }

        custom_messages = {
            "name.required": "Node name is required.",
            "code.required": "Code is required.",
            "code.unique": "Code must be unique.",
            "level_id.required": "Level is required.",
            "email.required": "Primary email is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        CoreOrganizationalNode.objects.create(
            name=data["name"],
            code=data["code"],
            branch_name=data.get("branch_name"),
            description=data.get("description"),
            level_id=data["level_id"],
            parent_node_id=data.get("parent_node_id"),
            physical_address=data.get("physical_address", ""),
            email=data["email"],
            contact_no=data.get("contact_no"),
            created_by_id=request.user.id if request.user.is_authenticated else None,
        )

        return ResponseService.response("SUCCESS", None, "default_create_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(["GET", "PUT", "DELETE"])
def organizational_node_detail(request, id):
    if request.method == "GET":
        return get_organizational_node(request, id)
    elif request.method == "PUT":
        return update_organizational_node(request, id)
    elif request.method == "DELETE":
        return delete_organizational_node(request, id)

def get_organizational_node(request, id):
    try:
        node = CoreOrganizationalNode.objects.get(id=id)
        from envoy.models.organization_level import CoreOrganizationLevel

        level_title = None
        if node.level_id:
            try:
                level = CoreOrganizationLevel.objects.get(id=node.level_id)
                level_title = level.title
            except CoreOrganizationLevel.DoesNotExist:
                level_title = None
        data = {
            "id": node.id,
            "name": node.name,
            "code": node.code,
            "branch_name": node.branch_name,
            "description": node.description,
            "level_id": node.level_id,
            "level_name": level_title,
            "parent_node_id": node.parent_node_id,
            "physical_address": node.physical_address,
            "email": node.email,
            "contact_no": node.contact_no,
            "created_by_id": node.created_by.id if node.created_by else None,
            "created_by_display_name": getattr(node.created_by, "display_name", None) if node.created_by else None,
            "updated_by_id": node.updated_by.id if node.updated_by else None,
            "updated_by_display_name": getattr(node.updated_by, "display_name", None) if node.updated_by else None,
            "created_at": node.created_at,
            "updated_at": node.updated_at,
        }
        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")
    except CoreOrganizationalNode.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")

def update_organizational_node(request, id):
    try:
        node = CoreOrganizationalNode.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "name": "required|max:80",
            "code": f"required|unique:core_organizational_nodes,code,{id}|max:100",
            "branch_name": "nullable|max:100",
            "description": "nullable|max:250",
            "level_id": "required|exists:core_organization_levels,id",
            "parent_node_id": "required|exists:core_organizational_nodes,id",
            "physical_address": "required|max:250",
            "email": "required|email|max:255",
            "contact_no": "nullable|max:80",
        }

        custom_messages = {
            "name.required": "Node name is required.",
            "code.required": "Code is required.",
            "code.unique": "Code must be unique.",
            "level_id.required": "Level is required.",
            "parent_node_id.required": "Parent node is required.",
            "email.required": "Primary email is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        node.name = data["name"]
        node.code = data["code"]
        node.branch_name = data.get("branch_name")
        node.description = data.get("description")
        node.level_id = data["level_id"]
        node.parent_node_id = data.get("parent_node_id")
        node.physical_address = data.get("physical_address", "")
        node.email = data["email"]
        node.contact_no = data.get("contact_no")
        node.updated_by_id = request.user.id if request.user.is_authenticated else None
        node.save()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
    except CoreOrganizationalNode.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def delete_organizational_node(request, id):
    try:
        node = CoreOrganizationalNode.objects.get(id=id)
        # Check for children
        if CoreOrganizationalNode.objects.filter(parent_node_id=id).exists():
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"error":"can_not_be_delete"},
                "Node has child nodes"
            )
        node.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except CoreOrganizationalNode.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
    
def get_organizational_node_hierarchy():
    from envoy.models.organizational_node import CoreOrganizationalNode

    # Fetch all nodes from the database
    nodes = CoreOrganizationalNode.objects.all().values(
        "id", "code", "name", "parent_node_id", "level_id"
    )

    # Build a dict for quick lookup
    node_dict = {}
    for node in nodes:
        node_dict[node["id"]] = {
            "id": node["id"],
            "code": node["code"],
            "name": node["name"],
            "type": "Corporate" if node.get("level_id") == 1 else "Personal",  # Example logic
            "parent_id": node["parent_node_id"],
            "children": []
        }

    # Build the tree
    root_nodes = []
    for node in node_dict.values():
        parent_id = node["parent_id"]
        if parent_id and parent_id in node_dict:
            node_dict[parent_id]["children"].append(node)
        else:
            root_nodes.append(node)

    return root_nodes

# Example usage in a view:
@api_view(["GET"])
def organizational_node_hierarchy_view(request):
    try:
        data = get_organizational_node_hierarchy()
        return ResponseService.response(
            "SUCCESS",
            data,
            "Node hierarchy fetched successfully."
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )
    
def get_organizational_node_hierarchy():
    from envoy.models.organizational_node import CoreOrganizationalNode

    # Fetch all nodes from the database
    nodes = CoreOrganizationalNode.objects.all().values(
        "id", "code", "name", "parent_node_id", "level_id"
    )

    # Build a dict for quick lookup
    node_dict = {}
    for node in nodes:
        node_dict[node["id"]] = {
            "id": node["id"],
            "code": node["code"],
            "name": node["name"],
            "type": "Corporate" if node.get("level_id") == 1 else "Personal",  # Example logic
            "parent_id": node["parent_node_id"],
            "children": []
        }

    # Build the tree
    root_nodes = []
    for node in node_dict.values():
        parent_id = node["parent_id"]
        if parent_id and parent_id in node_dict:
            node_dict[parent_id]["children"].append(node)
        else:
            root_nodes.append(node)

    return root_nodes