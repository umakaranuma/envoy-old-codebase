import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict


import json
import random
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from services.ActionService import ActionService
from services.AuthService import AuthService
from messages import Message, Error
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@api_view(["GET", "POST"])
def task_configs(request):
    """Handles GET (Fetch All) and POST (Create) Task Configs"""

    if request.method == "GET":
        action = ActionService.getAction("TaskConfig", "VIEW")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

        return get_all_task_configs(request)

    elif request.method == "POST":
        action = ActionService.getAction("TaskConfig", "CREATE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

        return create_task_config(request)


def get_all_task_configs(request):
    """ Fetch all Task Configs with filters, search, and pagination"""

    all_columns = [
        "crm_task_configs.*", 
        "stage.name AS stage_name",
        "stage.type AS stage_type",
        "stage.color AS stage_color",
        "type.name AS task_type_name",  
    ]

    # Support both "filters" (frontend) and "filter" (legacy); GET returns string
    raw_filter = request.GET.get("filters", request.GET.get("filter", "{}"))
    try:
        filter_dict = json.loads(raw_filter) if isinstance(raw_filter, str) else (raw_filter or {})
    except (json.JSONDecodeError, TypeError):
        filter_dict = {}
    # Map frontend keys to full column names expected by apply_conditions
    filter_aliases = {
        "task_type_id": "crm_task_configs.task_type_id",
        "opportunity_status_id": "crm_task_configs.opportunity_status_id",
    }
    mapped_filter_dict = {filter_aliases.get(k, k): v for k, v in filter_dict.items()}
    filter_json = json.dumps(mapped_filter_dict)

    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "crm_task_configs.sort_index")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["crm_task_configs.opportunity_status_id", "crm_task_configs.task_type_id"]
    search_columns = ["crm_task_configs.task", "crm_task_configs.code"]
    allowed_sorting_columns = ["crm_task_configs.sort_index", "crm_task_configs.task"]

    data = (
        QueryBuilderService("crm_task_configs")
        .select(*all_columns)
        .leftJoin("crm_opportunity_statuses as stage", "stage.id", "crm_task_configs.opportunity_status_id")
        .leftJoin("crm_task_types as type", "type.id", "crm_task_configs.task_type_id")
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def create_task_config(request):
    """ Create a new Task Config"""

    data = request.data

  
    rules = {
        "task": "required",
        "task_type_id": "required|integer|exists:crm_task_types,id",
        "opportunity_status_id": "required|integer|exists:crm_opportunity_statuses,id",
        "expected_days": "nullable|min",
        "reminder_expected_days": "nullable",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    
    if "expected_days" not in data or data["expected_days"] in ["", None]:
        data["expected_days"] = 1  # Default value is 1


    if "reminder_expected_days" not in data or data["reminder_expected_days"] == "":
        data["reminder_expected_days"] = None  # Set to NULL in DB

    
    if "code" not in data or not data["code"]:
        data["code"] = generate_unique_task_config_code()

    
    new_data = QueryBuilderService("crm_task_configs").insert(data)
    return ResponseService.response("SUCCESS", new_data,Message.DATA_CREATED)


@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def single_task_config(request, id):
    """Handles GET (Fetch One), PUT (Update), DELETE (Delete) Task Config"""

    if request.method == "GET":
        action = ActionService.getAction("TaskConfig", "VIEW")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

        return get_single_task_config(id)

    elif request.method == "PUT":
        action = ActionService.getAction("TaskConfig", "UPDATE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

        return update_task_config(request, id)

    elif request.method == "DELETE":
        action = ActionService.getAction("TaskConfig", "DELETE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

        return delete_task_config(id)


def get_single_task_config(id):
    """ Fetch a single Task Config"""
    data = QueryBuilderService("crm_task_configs").where("id", id).first()
    return (
        ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
        if data
        else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    )


def update_task_config(request, id):
    """ Update an existing Task Config"""

    data = json.loads(request.body) if request.body else {}

    
    rules = {
        "task": "required",
        "task_type_id": "required|integer|exists:crm_task_types,id",
        "opportunity_status_id": "required|integer|exists:crm_opportunity_statuses,id",
        # "expected_days": "integer",
        # "reminder_expected_days": "integer",
    }

    #  Convert Empty Strings to `None` and Set Default Value (1)
    for field in ["expected_days", "reminder_expected_days"]:
        if field in data:
            if data[field] == "" or data[field] is None:
                data[field] = 1  

    # Validate Data
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Update Data
    updated_data = QueryBuilderService("crm_task_configs").where("id", id).update(data)
    return (
        ResponseService.response("SUCCESS", updated_data, Message.DATA_UPDATED)
        if updated_data
        else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    )



def delete_task_config(id):
    """ Delete a Task Config"""
    QueryBuilderService("crm_opportunity_tasks").where("task_config_id", id).delete()

    deleted_data = QueryBuilderService("crm_task_configs").where("id", id).delete()
    return (
        ResponseService.response("SUCCESS", deleted_data, Message.DATA_DELETED)
        if deleted_data
        else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    )


def generate_unique_task_config_code():
    """ Generates a unique 6-digit code"""
    while True:
        new_code = str(random.randint(100000, 999999))  # Generates a 6-digit number
        existing_code = QueryBuilderService("crm_task_configs").where("code", new_code).first()
        if not existing_code:  
            return new_code

@csrf_exempt
@api_view(["POST"])
def update_task_config_order(request):
    """ Update Task Config Order"""

    data = json.loads(request.body) if request.body else {}

    
    if not isinstance(data.get("order"), list):
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"order": "The order field must be an array."},
            Error.VALIDATION_ERROR
        )

    
    rules = {
        "assigned_stage_id": "required|integer|exists:crm_task_configs,id",
        "order": "required|list",
        # "order.*": "required|integer|exists:crm_task_configs,id"  
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response(
            "VALIDATION_ERROR", errors, Error.VALIDATION_ERROR
        )

    
    for index, config_id in enumerate(data["order"]):
        QueryBuilderService("crm_task_configs").where("id", config_id).update(
            {"sort_index": index} 
        )

    return ResponseService.response("SUCCESS", None, Message.DATA_UPDATED)


@csrf_exempt
@api_view(["GET", "POST"])
def task_types(request):
    """ Fetch All Task Types with Filters, Search, and Pagination"""

    if request.method == "GET":
    #  Authorization Check
        action = ActionService.getAction("TaskType", "VIEW")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)
        
        return get_all_task_type(request) 
   
    elif request.method == "POST":
        action = ActionService.getAction("TaskType", "CREATE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

        return create_task_type(request)  

def get_all_task_type(request):

    #  Define Columns to Fetch
    all_columns = [
        "*",
       
    ]
  
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

    
    allowed_filters = []
    search_columns = ["name", "description"]
    allowed_sorting_columns = ["name", "id"]

    
    data = (
        QueryBuilderService("crm_task_types")
        .select(*all_columns)
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

def create_task_type(request):
    
    data = request.data

    rules = {
        "name": "required|unique:crm_task_types,name",
        "description": "max:250",
    }

    errors = ValidatorService.validate(data,rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)
    
    save_data = QueryBuilderService("crm_task_types").insert(data)
    return ResponseService.response("SUCCESS",save_data,Message.DATA_CREATED)

@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def single_task_type(request, id):

    if request.method == "GET":
        action = ActionService.getAction("TaskType", "VIEW")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)       
        return get_single_task_type(id) 
    
    elif request.method == "PUT":
        action = ActionService.getAction("TaskType", "UPDATE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)       
        return update_single_task_type(request,id)
     
    elif request.method == "DELETE":
        action = ActionService.getAction("TaskType", "DELETE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)       
        return delete_single_task_type(id) 


def get_single_task_type(id):

    data = (
        QueryBuilderService("crm_task_types")
        .select("crm_task_types.*")
        .where("crm_task_types.id", id)
        .first()
    )
    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) if data else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def update_single_task_type(request, id):
    request_data = request.data

    # Validation rules
    rules = {
        "name": f"required|unique:crm_task_types,name,{id}|max:255",
        "description": "nullable|max:250",
    }

    custom_messages = {
        "name.required": "Task type name is required.",
        "name.unique": "This task type name is already in use.",
        "name.max": "Task type name must be less than 255 characters.",
        "description.max": "Description cannot exceed max:250 characters.",
    }

    errors = ValidatorService.validate(request_data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Perform update
    updated = (
        QueryBuilderService("crm_task_types")
        .where("id", id)
        .update(request_data)
    )

    if updated:
        return ResponseService.response("SUCCESS", updated, Message.DATA_UPDATED)
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_single_task_type(id):
    #Check if the task type is referenced in crm_task_configs
    reference = QueryBuilderService("crm_task_configs").where("task_type_id", id).first()

    if reference:
        return ResponseService.response(
            "CONFLICT",
            [],
            Error.TASK_TYPE_DELETE_CONFLICT
        )

    # 🗑 Proceed with deletion if not referenced
    deleted = (
        QueryBuilderService("crm_task_types")
        .where("id", id)
        .delete()
    )

    if deleted:
        return ResponseService.response("SUCCESS", None, Message.DATA_DELETED)
    
    return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)



@api_view(['GET'])
def get_opportunity_tasks(request):
    """ Get multiple opportunity tasks by task IDs """

    ids = request.GET.get('ids', None)  # Get comma-separated task IDs

    data = []
    
    if ids:
        task_ids = ids.split(",")  # Convert "1,2,3" → ["1", "2", "3"]
        
        data = (
            QueryBuilderService("crm_opportunity_tasks as tasks")
            .leftJoin("crm_opportunities as opp", "opp.id", "tasks.opportunity_id")  # Join opportunities
            .leftJoin("crm_opportunity_statuses as stage", "stage.id", "opp.stage_id")  # Join opportunity statuses
            .select(
                "tasks.task_id AS task_id",
                "opp.title AS opportunity_title",
                "opp.code AS opportunity_code",
                "opp.stage_id AS stage_id",  # Include stage_id
                "stage.color AS stage_color",  # Include color from statuses
                "stage.type AS stage_type",  # Include type from statuses
                "stage.name AS stage_name", # Include name from statuses
            )
            .whereIn("tasks.task_id", task_ids)
            .get()
        )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)
