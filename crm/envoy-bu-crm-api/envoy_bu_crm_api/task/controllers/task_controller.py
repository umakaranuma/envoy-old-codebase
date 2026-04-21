import random
from datetime import datetime
from django.http import JsonResponse
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService
from rest_framework.decorators import api_view
from envoy_bu_crm_api.sales.models.core_models import Task, User
from envoy_bu_crm_api.sales.models.opportunities import Opportunity
from envoy_bu_crm_api.sales.models.opprtunity_task import OpportunityTask
from services.ActionService import ActionService
from services.ActivityService import ActivityService
from services.AuthService import AuthService
from messages import Message, Error
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction, IntegrityError
import json
from django.db.models import Q
from datetime import datetime, time

from services.EntityService import EntityService

@csrf_exempt
@api_view(["GET", "POST"])
def tasks(request):
    """Handles GET (Fetch All) and POST (Create) Tasks"""

    if request.method == "GET":
        action = ActionService.getAction("Task", "VIEW")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

        return get_all_tasks(request)

    elif request.method == "POST":
        return manage_task(request)


def get_all_tasks(request):
    """Fetch all Tasks including Task Status and Assigned User Data"""

    all_columns = [
        "core_tasks.id",
        "core_tasks.code",
        "core_tasks.task",
        "core_tasks.description",
        "core_tasks.task_status_id",
        "core_tasks.assigned_to_id",
        "core_tasks.assigned_date",
        "core_tasks.start_date",
        "core_tasks.due_date",
        "core_tasks.sort_index",
        "core_task_status.name AS task_status_name",  # Task status name
        "core_task_status.color AS task_status_color",  # Task status color
        "core_task_status.type AS task_status_type",  # Task status type
        "core_users.display_name AS assigned_user_name",  # Assigned user's name
        "core_users.email AS assigned_user_email",  # Assigned user's email
        "core_users.contact_no AS assigned_user_contact",  # Assigned user's contact
        "core_users.picture AS assigned_user_picture",  # Assigned user's picture
    ]
    fields = request.GET.get("fields", None)
    filter_json = request.GET.get("filters", '{}')
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir")
    sort_by = "id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    task_status_id = request.GET.get("task_status_id", None)
    assigned_to = request.GET.get("assigned_to", None)
    opportunity_id = request.GET.get("opportunity_id", None)  # Retrieve opportunity_id from request

    allowed_filters = ["task_status_id", "assigned_to_id", "start_date", "due_date"]
    search_columns = ["core_tasks.task", "core_tasks.description","core_task_status.name", "core_users.display_name","core_task_status.color","core_tasks.code"]
    allowed_sorting_columns = ["core_tasks.task", "core_tasks.assigned_to_id", "core_tasks.start_date"]

    data = (
        QueryBuilderService("core_tasks")
        .leftJoin("core_task_status", "core_task_status.id", "core_tasks.task_status_id")  # Join Task Status
        .leftJoin("core_users", "core_users.id", "core_tasks.assigned_to_id")  # Join Assigned User
        .leftJoin("crm_opportunity_tasks", "crm_opportunity_tasks.task_id", "core_tasks.id")  # Join Opportunity Tasks
        .select(*all_columns)
    )

    if task_status_id is not None:
        data = data.where("core_tasks.task_status_id", task_status_id)

    if assigned_to is not None:
        data = data.where("core_tasks.assigned_to_id", assigned_to)

    if opportunity_id not in [None, "undefined", "null", ""]:
        data = data.where("crm_opportunity_tasks.opportunity_id", opportunity_id)


    data = (
        data.apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    if fields == 'additional' and isinstance(data, dict) and 'data' in data:
        task_items = data['data']

        task_ids = [item['id'] for item in task_items if 'id' in item]

        # Get mapping of task_id → opportunity_id
        opportunity_map = OpportunityTask.objects.filter(task_id__in=task_ids)\
            .values('task_id', 'opportunity_id')

        task_to_opportunity_id = {item['task_id']: item['opportunity_id'] for item in opportunity_map}

        # Fetch related opportunities with stage info
        opportunities = Opportunity.objects.filter(id__in=task_to_opportunity_id.values())\
            .select_related('stage')

        # Build opportunity data
        opportunity_dict = {
            opp.id: {
                "id": opp.id,
                "title": opp.title,
                "code": opp.code,
                "stage_color": opp.stage.color if opp.stage else None,
                "stage_type": opp.stage.type if opp.stage else None,
                "stage_name": opp.stage.name if opp.stage else None,
            }
            for opp in opportunities
        }

        # Attach to each task
        for item in task_items:
            task_id = item.get("id")
            opp_id = task_to_opportunity_id.get(task_id)
            item["opportunity"] = opportunity_dict.get(opp_id) if opp_id else None


    return ResponseService.response("SUCCESS", data, Message.DATA_CREATED)

@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def single_task(request, id):
    """Handles GET (Fetch One), PUT (Update), DELETE (Delete) Task"""

    if request.method == "GET":
        action = ActionService.getAction("Task", "VIEW")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)
        return get_single_task(id)

    elif request.method == "PUT":
        action = ActionService.getAction("Task", "UPDATE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)
        return manage_task(request, id)

    elif request.method == "DELETE":
        action = ActionService.getAction("Task", "DELETE")
        if not AuthService.hasAuthority(request , action):
            return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)
        return delete_task(id)

def generate_unique_task_code():
    """ Generate a unique 6-digit task code"""
    while True:
        new_code = str(random.randint(100000, 999999))  # Generates a 6-digit number
        existing_code = QueryBuilderService("core_tasks").where("code", new_code).first()
        if not existing_code:
            return new_code

def manage_task(request, id=None):
    """ Create or Update Task"""
    action = ActionService.getAction("Task", "CREATE" if not id else "UPDATE")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    data = request.data

    #  Remove Empty Date Values to Prevent Validation Errors
    for date_field in ["assigned_date", "start_date", "due_date"]:
        if not data.get(date_field):
            data.pop(date_field, None)  # Remove empty/null values

    #  Define Validation Rules
    rules = {
        "task": "required",
        "code": "max:20",
        "description": "nullable",
        "task_status_id": "required|integer|exists:core_task_status,id",
        "assigned_to_id": "exists:core_users,id",
        "changed_by_id": "exists:core_users,id",  
        "start_date": "nullable|date",
        "due_date": "nullable|date|after_or_equal:start_date",
        "opportunity_id": "required|integer|exists:crm_opportunities,id",
    }

    #  Ensure `changed_by_id` is set (Defaults to `1` if missing)
    data["changed_by_id"] = request.user.id if request.user.is_authenticated else None

    # Normalize nullable integer fields
    for field in ["assigned_to_id", "changed_by_id"]:
        if field in data and data[field] in ["", None]:
            data[field] = None

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Now it's safe to access `task_status_id`
    task_status_id = data["task_status_id"]

    highest_sort_index = (
        QueryBuilderService("core_tasks")
        .where("task_status_id", task_status_id)
        .orderBy("sort_index", "desc")  
        .select("sort_index")
        .first()
    )

    #  Ensure sort_index is a valid number (default to 0 if None)
    last_sort_index = (
        highest_sort_index["sort_index"] if highest_sort_index and highest_sort_index["sort_index"] is not None else 0
    )

    #  Set `sort_index` to highest found +1
    data["sort_index"] = last_sort_index + 1

    

    #  Validate Input Data
    # errors = ValidatorService.validate(data, rules)
    # if errors:
    #     return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    opportunity_id = data.pop("opportunity_id", None)

    if id:
        #  Update Existing Task
        existing_task = QueryBuilderService("core_tasks").where("id", id).first()
        if not existing_task:
            return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
        
        old_assigned_to = existing_task.get("assigned_to_id") 
        new_assigned_to = data.get("assigned_to_id")  
        old_status_id = existing_task.get("task_status_id")  
        new_status_id = data.get("task_status_id")  

        #  Track Task Assignee Change
        if old_assigned_to and new_assigned_to and old_assigned_to != new_assigned_to:
            # Fetch names
            old_user = QueryBuilderService("core_users").where("id", old_assigned_to).select("display_name").first()
            new_user = QueryBuilderService("core_users").where("id", new_assigned_to).select("display_name").first()

            old_name = old_user["display_name"] if old_user else f"User({old_assigned_to})"
            new_name = new_user["display_name"] if new_user else f"User({new_assigned_to})"

            history_data = {
                "task_id": id,
                "from_assigned_id": old_assigned_to,
                "to_assigned_id": new_assigned_to,
                "remark": f"Task reassigned from {old_name} to {new_name}",
                "changed_by_id": data["changed_by_id"],
            }
            QueryBuilderService("core_task_assignee_histories").insert(history_data)

        #  Track Task Status Change
        if old_status_id and new_status_id and old_status_id != new_status_id:
            # Fetch status names
            old_status = QueryBuilderService("core_task_status").where("id", old_status_id).select("name").first()
            new_status = QueryBuilderService("core_task_status").where("id", new_status_id).select("name").first()

            old_status_name = old_status["name"] if old_status else f"Status({old_status_id})"
            new_status_name = new_status["name"] if new_status else f"Status({new_status_id})"

            status_history_data = {
                "task_id": id,
                "task_status_id": new_status_id,
                "remark": f"Status changed from {old_status_name} to {new_status_name}",
                "changed_by_id": data["changed_by_id"],
            }
            QueryBuilderService("core_task_status_histories").insert(status_history_data)

        #  Update task details
        updated_data = QueryBuilderService("core_tasks").where("id", id).update(data)
        return ResponseService.response("SUCCESS", updated_data, Message.DATA_UPDATED)

    else:
        #  Create New Task
        if "code" not in data or not data["code"]:
            data["code"] = generate_unique_task_code()

        #  Store in ERP Core Task Table first
        inserted_task = QueryBuilderService("core_tasks").insert(data)

        #  Extract only the task ID
        new_task_id = inserted_task.get("id") if isinstance(inserted_task, dict) else inserted_task

        #  Fetch the newly created task safely
        created_task = QueryBuilderService("core_tasks").where("id", new_task_id).first()

        #  Store in CRM Opportunity Task Table only if `opportunity_id` is provided
        if opportunity_id and new_task_id:
            crm_task_data = {
                "opportunity_id": opportunity_id,
                "task_id": new_task_id
            }
            QueryBuilderService("crm_opportunity_tasks").insert(crm_task_data)

        return ResponseService.response("SUCCESS", created_task, Message.DATA_CREATED)


def get_single_task(id):
    """ Fetch a single Task"""
    data = (
        QueryBuilderService("core_tasks")
        .leftJoin("crm_opportunity_tasks", "crm_opportunity_tasks.task_id", "core_tasks.id")
        .leftJoin("core_users", "core_users.id", "core_tasks.assigned_to_id")
        .leftJoin("core_task_status", "core_task_status.id", "core_tasks.task_status_id")
        .leftJoin("crm_opportunities", "crm_opportunities.id", "crm_opportunity_tasks.opportunity_id")
        .leftJoin("crm_opportunity_statuses", "crm_opportunity_statuses.id", "crm_opportunities.stage_id")
        .select(
            "core_tasks.*", 
            "crm_opportunity_tasks.opportunity_id",
            "core_users.first_name AS assigned_to_first_name",  
            "core_users.last_name AS assigned_to_last_name",
            "core_users.display_name AS assigned_to_display_name",
            "core_users.email AS assigned_to_email",
            "core_users.picture AS assigned_to_picture",
            "core_task_status.name AS task_status_name","core_task_status.color AS task_status_color",
            "crm_opportunities.title AS opportunity_title",
            "crm_opportunities.code AS opportunity_code",
            "crm_opportunities.stage_id AS opportunity_stage_id",
            "crm_opportunity_statuses.name AS opportunity_stage_name",
            "crm_opportunity_statuses.color AS opportunity_stage_color",
            "crm_opportunity_statuses.type AS opportunity_stage_type",
        )
        .where("core_tasks.id", id)
        .first()
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) if data else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_task(id):
    # Fetch task with status information
    task = QueryBuilderService("core_tasks")\
        .leftJoin("core_task_status", "core_task_status.id", "core_tasks.task_status_id")\
        .select("core_tasks.*", "core_task_status.type as status_type")\
        .where("core_tasks.id", id).first()
    
    if not task:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Check if task status allows deletion (block "task_inprogress" or "task_done" status)
    status_type = task.get("status_type", "").lower()
    print(f"DEBUG: Task ID {id} - Status Type: '{status_type}'")
    print(f"DEBUG: Task data: {task}")
    
    if status_type in ["task_inprogress", "task_done"]:
        print(f"DEBUG: Task deletion BLOCKED - Status '{status_type}' is not allowed to be deleted")
        return ResponseService.response("FORBIDDEN", None, Message.DEFAULT_CONFLICT_MSG)
    
    print(f"DEBUG: Task deletion ALLOWED - Status '{status_type}' can be deleted")

    try:
        with transaction.atomic():  # Ensures all queries succeed or none are committed
            
            # Step 1: Delete all related records in dependent tables
            QueryBuilderService("core_task_assignee_histories").where("task_id", id).delete()
            QueryBuilderService("core_task_status_histories").where("task_id", id).delete()
            QueryBuilderService("crm_opportunity_tasks").where("task_id", id).delete()
            
            # Step 2: Delete the main task
            QueryBuilderService("core_tasks").where("id", id).delete()

        return ResponseService.response("SUCCESS", {"deleted_task_id": id}, Message.DATA_DELETED)

    except IntegrityError:
        return ResponseService.response("ERROR", None, "Task cannot be deleted due to foreign key constraints.")

    except Exception as e:
        return ResponseService.response("ERROR", {"error": str(e)}, "Task deletion failed due to an unexpected error.")

@csrf_exempt
@api_view(["PATCH", "PUT"])
def update_task_status_methods(request, id):
    

    if request.method == "PATCH":
        
        return update_task_status(request,id)

    elif request.method == "PUT":
        
        return update_task_status_simple(request, id)

   

def update_task_status(request, id):
    """ Update Task Status with Sorting & History"""

    action = ActionService.getAction("Task", "UPDATE")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    data = request.data

    rules = {
        "source_status_id": "required|integer|exists:core_task_status,id",
        "destination_status_id": "required|integer|exists:core_task_status,id",
        "update_task_id": "required|integer|exists:core_tasks,id",
        "prev_task_id": "exists:core_tasks,id",
        "next_task_id": "exists:core_tasks,id",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    update_task_id = data["update_task_id"]
    destination_status_id = data["destination_status_id"]
    prev_task_id = data.get("prev_task_id")
    next_task_id = data.get("next_task_id")

    changed_by_id = request.user.id if hasattr(request, "user") and request.user and request.user.id else 1

    # Fetch the source and destination status names
    source_status = QueryBuilderService("core_task_status").where("id", data["source_status_id"]).first()
    destination_status = QueryBuilderService("core_task_status").where("id", destination_status_id).first()

    if not source_status or not destination_status:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    source_status_name = source_status["name"]
    destination_status_name = destination_status["name"]


    QueryBuilderService("core_tasks").where("id", update_task_id).update(
        {"task_status_id": destination_status_id}
    )

    
    prev_task = QueryBuilderService("core_tasks").where("id", prev_task_id).first() if prev_task_id else None
    next_task = QueryBuilderService("core_tasks").where("id", next_task_id).first() if next_task_id else None
    update_task = QueryBuilderService("core_tasks").where("id", update_task_id).first()

    if not update_task:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    
    prev_sort_index = float(prev_task["sort_index"]) if prev_task and prev_task["sort_index"] is not None else 0.0
    next_sort_index = float(next_task["sort_index"]) if next_task and next_task["sort_index"] is not None else prev_sort_index + 1.0

    
    if prev_task and next_task:
        new_sort_index = (prev_sort_index + next_sort_index) / 2
    elif not prev_task and next_task:
        new_sort_index = next_sort_index / 2
    elif prev_task and not next_task:
        new_sort_index = prev_sort_index + 1
    else:
        new_sort_index = 1  # Default if no tasks exist

    
    QueryBuilderService("core_tasks").where("id", update_task_id).update(
        {"sort_index": new_sort_index}
    )

    
    # Fetch source and destination status names
    source_status = QueryBuilderService("core_task_status").where("id", data["source_status_id"]).select("name").first()
    destination_status = QueryBuilderService("core_task_status").where("id", destination_status_id).select("name").first()

    source_status_name = source_status["name"] if source_status else f"Status({data['source_status_id']})"
    destination_status_name = destination_status["name"] if destination_status else f"Status({destination_status_id})"

    history_data = {
        "task_id": update_task_id,
        "task_status_id": destination_status_id,
        "changed_by_id": changed_by_id,
        "remark": f"Task status changed from {source_status_name} to {destination_status_name}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    QueryBuilderService("core_task_status_histories").insert(history_data)

    

    
    updated_task = (
        QueryBuilderService("core_tasks")
        .leftJoin("core_task_status", "core_task_status.id", "core_tasks.task_status_id")  #  Join Task Status
        .leftJoin("core_users", "core_users.id", "core_tasks.assigned_to_id")  #  Join Assigned User
        .select(
            "core_tasks.id",
            "core_tasks.code",
            "core_tasks.task",
            "core_tasks.description",
            "core_tasks.task_status_id",
            "core_tasks.sort_index",
            "core_tasks.assigned_to_id",
            "core_tasks.assigned_date",
            "core_tasks.start_date",
            "core_tasks.due_date",
            "core_task_status.name AS task_status_name",  #  Task Status Name
            "core_task_status.color AS task_status_color",  #  Task Status Color
            "core_users.display_name AS assigned_user_name",  #  Assigned User Name
            "core_users.email AS assigned_user_email",  #  Assigned User Email
            "core_users.contact_no AS assigned_user_contact"  #  Assigned User Contact
        )
        .where("core_tasks.id", update_task_id)
        .first()
    )

    opportunity_task = QueryBuilderService("crm_opportunity_tasks").where("task_id", update_task_id).first()
    if not opportunity_task:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    opportunity_id = opportunity_task["opportunity_id"]

    opportunity = QueryBuilderService("crm_opportunities").where("id", opportunity_id).first()
    if not opportunity:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)
    entity_id = opportunity["entity_id"]


    # Log the activity using ActivityService
    ActivityService.store_activity(
        request=request,
        entity_id=entity_id,
        activity=f"Task status updated from {source_status_name} to {destination_status_name}"
    )

    if updated_task and opportunity:
        # Optionally, fetch stage details too
        stage = QueryBuilderService("crm_opportunity_statuses").where("id", opportunity.get("stage_id")).first()

        updated_task["opportunity"] = {
            "id": opportunity["id"],
            "title": opportunity["title"],
            "code": opportunity["code"],
            "stage_color": stage["color"] if stage else None,
            "stage_type": stage["type"] if stage else None,
            "stage_name": stage["name"] if stage else None
        }
    else:
        updated_task["opportunity"] = None


    return ResponseService.response("SUCCESS", updated_task, Message.DATA_UPDATED)




def update_task_status_simple(request, id):
    """ Update Task Status and Log the Change in core_task_status_histories """

    # Check if the user has the authority to update the task
    action = ActionService.getAction("Task", "UPDATE")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    try:
        # Parse the request data
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON format"}, Error.VALIDATION_ERROR)

    # Define validation rules
    rules = {
        "status_id": "required|integer|exists:core_task_status,id",
    }

    # Validate the input data
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Fetch the existing task
    existing_task = QueryBuilderService("core_tasks").where("id", id).first()
    if not existing_task:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Get the current and new status IDs
    current_status_id = existing_task.get("task_status_id")
    new_status_id = data.get("status_id")

    # Check if the status is actually being updated
    if current_status_id == new_status_id:
        return ResponseService.response("SUCCESS", None, "Task status is already up-to-date.")

    # Fetch the current and new status names
    current_status = QueryBuilderService("core_task_status").where("id", current_status_id).first()
    new_status = QueryBuilderService("core_task_status").where("id", new_status_id).first()

    current_status_name = current_status["name"] if current_status else "Unknown"
    new_status_name = new_status["name"] if new_status else "Unknown"

    # Update the task status
    QueryBuilderService("core_tasks").where("id", id).update({"task_status_id": new_status_id})

    # Log the status change in the core_task_status_histories table
    history_data = {
        "task_id": id,
        "task_status_id": new_status_id,
        "changed_by_id": request.user.id if request.user.is_authenticated else None,
        "remark": f"Task status changed from {current_status_name} to {new_status_name}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    QueryBuilderService("core_task_status_histories").insert(history_data)

    

    # Fetch the updated task with additional details
    updated_task = (
        QueryBuilderService("core_tasks")
        .leftJoin("core_task_status", "core_task_status.id", "core_tasks.task_status_id")  # Join Task Status
        .leftJoin("core_users", "core_users.id", "core_tasks.assigned_to_id")  # Join Assigned User
        .select(
            "core_tasks.id",
            "core_tasks.code",
            "core_tasks.task",
            "core_tasks.description",
            "core_tasks.task_status_id",
            "core_tasks.sort_index",
            "core_tasks.assigned_to_id",
            "core_tasks.assigned_date",
            "core_tasks.start_date",
            "core_tasks.due_date",
            "core_task_status.name AS task_status_name",  # Task Status Name
            "core_task_status.color AS task_status_color",  # Task Status Color
            "core_users.display_name AS assigned_user_name",  # Assigned User Name
            "core_users.email AS assigned_user_email",  # Assigned User Email
            "core_users.contact_no AS assigned_user_contact"  # Assigned User Contact
        )
        .where("core_tasks.id", id)
        .first()
    )

    opportunity_task = QueryBuilderService("crm_opportunity_tasks").where("task_id", updated_task["id"]).first()
    if opportunity_task:
        opportunity_id = opportunity_task.get("opportunity_id")
        opportunity = QueryBuilderService("crm_opportunities").where("id", opportunity_id).first()

        if opportunity:
            entity_id = opportunity.get("entity_id")
            ActivityService.store_activity(
                request=request,
                entity_id=entity_id,
                activity=f"Task status updated from {current_status_name} to {new_status_name}"
            )

    return ResponseService.response("SUCCESS", updated_task, Message.DATA_UPDATED)

@csrf_exempt
@api_view(["GET", "POST"])
def task_interactions(request, id):
    """ Handle GET (List All) and POST (Create) Interactions for a Task"""

    if request.method == "GET":
        action = ActionService.getAction("Task", "VIEW")
    else:
        action = ActionService.getAction("Task", "CREATE")

    has_authority = AuthService.hasAuthority(request , action)
    if not has_authority:
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    return get_all_task_interactions(request, id) if request.method == "GET" else store_task_interaction(request, id)


def get_all_task_interactions(request, id):
    """ Get All Interactions for a Specific Task"""

    all_columns = ["core_intractions.*","core_channels.name AS channel_name","crm_opportunity_statuses.color As opportunity_status_color","crm_opportunity_statuses.name As opportunity_status",
                   "core_contacts.name AS contact_neme", "core_contacts.primary_contact As contact_primary", "core_users.display_name As contact_by_name"]
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    ids = request.GET.get("ids", None)
    allowed_filters = []
    search_columns = [
        "core_intractions.notes",
        "core_contacts.name",
        "core_channels.name",
        "core_users.display_name"
    ]

    allowed_sorting_columns = ["notes"]

    data = QueryBuilderService("core_intractions")\
        .leftJoin("core_channels", "core_channels.id", "core_intractions.channel_id")\
        .leftJoin("crm_opportunity_statuses","crm_opportunity_statuses.id","core_intractions.opportunity_status_id")\
        .leftJoin("core_contacts","core_contacts.id","core_intractions.contact_id")\
        .leftJoin("core_users","core_users.id","core_intractions.contact_by_id")\
        .select(*all_columns)\
        .where("task_id", id)\
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)

    if ids:
        data = data.whereIn("id", ids.split(",")).get()
    else:
        data = data.paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def store_task_interaction(request, id):
    """ Store Task Interaction """

    # Check if the user has permission
    action = ActionService.getAction("Task_Interaction", "CREATE")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    try:
        data = json.loads(request.body.decode("utf-8"))  # Decode request body safely
    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR", {"error": "Invalid JSON format"}, Error.VALIDATION_ERROR
        )

    # Define Validation Rules
    rules = {
        "channel_id": "required|exists:core_channels,id",
        "date": "required|date_format:%Y-%m-%d",  # Required Date field
        "opportunity_status_id": "exists:crm_opportunity_statuses,id",
        "customer_id": "exists:core_customers,id",
        "contact_id": "exists:core_contacts,id",
        "opportunity_id": "exists:crm_opportunities,id",
        "notes": "max:500"
    }

    # Validate input data
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Ensure task exists
    task_data = QueryBuilderService("core_tasks").where("id", id).first()
    if not task_data:
        return ResponseService.response("NOT_FOUND", {"task_id": "Task not found"}, Error.NOT_FOUND)

    # Convert empty string values ("") to None (NULL in DB)
    nullable_fields = [
        "opportunity_status_id",
        "customer_id",
        "contact_id",
        "opportunity_id",
        "notes",
    ]
    for field in nullable_fields:
        if field in data and data[field] == "":
            data[field] = None

    # Assign values from task if not provided in request
    data["task_id"] = id
    data["contact_id"] = data.get("contact_id") or task_data.get("contact_id")

    if not data.get("opportunity_id"):
        mapping = QueryBuilderService("crm_opportunity_tasks").where("task_id", id).first()
        data["opportunity_id"] = mapping.get("opportunity_id") if mapping else None

    # 2. If customer missing, take from resolved opportunity
    if not data.get("customer_id") and data.get("opportunity_id"):
        opp = QueryBuilderService("crm_opportunities").where("id", data.get("opportunity_id")).first()
    data["customer_id"] = opp.get("customer_id") if opp else None

    data["contact_by_id"] = request.user.id if request.user.is_authenticated else 1  # Default to admin user
    # Create Entity for Interaction
    entity = EntityService.store("Interaction", request)
    if not entity or "id" not in entity:
        return ResponseService.response("ERROR", None, "Failed to create entity")
    data["entity_id"] = entity["id"]

    # Store Interaction
    new_interaction = QueryBuilderService("core_intractions").insert(data)

    # Prepare response data
    response_data = {
        "id": new_interaction.get("id"),
        "date": new_interaction.get("date"),  # Return Date
        "task_id": new_interaction.get("task_id"),
        "channel_id": new_interaction.get("channel_id"),
        "contact_id": new_interaction.get("contact_id"),
        "customer_id": new_interaction.get("customer_id"),
        "opportunity_id": new_interaction.get("opportunity_id"),
        "contact_by_id": new_interaction.get("contact_by_id"),
        "opportunity_status_id": new_interaction.get("opportunity_status_id"),
        "notes": new_interaction.get("notes"),
        "entity_id": new_interaction.get("entity_id"),
    }

    return ResponseService.response("SUCCESS", response_data, Message.DATA_CREATED)

@csrf_exempt
@api_view(["GET", "PUT", "DELETE"])
def single_task_interaction(request, id, int_id):
    """ Handle GET (Retrieve), PUT (Update), DELETE (Remove) for a Single Interaction"""

    if request.method == "GET":
        action = ActionService.getAction("Task", "VIEW")
    elif request.method == "PUT":
        action = ActionService.getAction("Task", "UPDATE")
    else:
        action = ActionService.getAction("Task", "DELETE")

    has_authority = AuthService.hasAuthority(request , action)
    if not has_authority:
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    if request.method == "GET":
        return get_single_task_interaction(int_id)
    elif request.method == "PUT":
        return update_task_interaction(request, id, int_id)
    else:
        return delete_task_interaction(int_id)


def get_single_task_interaction(int_id):
    """ Get a Single Interaction by ID"""

    data = QueryBuilderService("core_intractions").where("id", int_id).first()

    if not data:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Fetch Entity Data using EntityService
    entity_data = EntityService.get_entity_with_notes_and_docs(data["entity_id"])

    # Add entity details to response
    data["entity"] = entity_data if entity_data else {}

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


def update_task_interaction(request, id, int_id):
    """ Update a Specific Task Interaction"""

    try:
        data = json.loads(request.body.decode("utf-8")) if request.body else {}
    except json.JSONDecodeError:
        return ResponseService.response("VALIDATION_ERROR", {"error": "Invalid JSON format"}, Error.VALIDATION_ERROR)

    # Define Validation Rules
    rules = {
        "channel_id": "exists:core_channels,id",
        "contact_by_id": "exists:core_users,id",
        "notes": "nullable",
        "opportunity_status_id": "nullable|exists:crm_opportunity_statuses,id",
        "customer_id": "nullable|exists:core_customers,id",
        "contact_id": "nullable|exists:core_contacts,id",
        "opportunity_id": "nullable|exists:crm_opportunities,id",
    }

    # Validate input data
    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    # Convert empty string values ("") to None (NULL in DB)
    nullable_fields = [
        "opportunity_status_id",
        "customer_id",
        "contact_id",
        "opportunity_id",
        "notes",
    ]
    for field in nullable_fields:
        if field in data and data[field] == "":
            data[field] = None

    # Ensure Interaction Exists Before Updating
    existing_interaction = QueryBuilderService("core_intractions").where("id", int_id).first()
    if not existing_interaction:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Update Data
    updated_data = QueryBuilderService("core_intractions").where("id", int_id).update(data)

    if updated_data:
        return ResponseService.response("SUCCESS", updated_data, Message.DATA_UPDATED)
    else:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


def delete_task_interaction(int_id):
    """ Delete a Specific Task Interaction"""

    deleted_data = QueryBuilderService("core_intractions").where("id", int_id).delete()

    if deleted_data:
        return ResponseService.response("SUCCESS", deleted_data, Message.DATA_DELETED)
    else:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

from django.core.paginator import Paginator


@csrf_exempt
@api_view(["GET"])
def task_assignees(request):
    """ Get All Task Assignees related to Opportunity Tasks"""

    action = ActionService.getAction("Task", "VIEW")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    return get_all_task_assignees(request)


def get_all_task_assignees(request):
    """ Fetch all Unique Task Assignees Assigned to Opportunity Tasks """

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "").strip()
    sort_dir = request.GET.get("sort_dir", "desc")

    sort_column = f"{'-' if sort_dir == 'desc' else ''}{sort_by}" if sort_by else None

    # Step 1: Get unique user IDs from tasks linked to opportunity tasks
    user_ids = Task.objects.filter(
        opportunity_tasks__opportunity__isnull=False
    ).values_list("assigned_to_id", flat=True).distinct()

    # Step 2: Fetch core_users
    queryset = User.objects.filter(id__in=user_ids)

    if search_string:
        queryset = queryset.filter(
            Q(display_name__icontains=search_string) |
            Q(email__icontains=search_string)
        )

    if sort_column:
        queryset = queryset.order_by(sort_column)

    queryset = queryset.distinct()

    # Step 3: Paginate
    paginator = Paginator(queryset, limit)
    paginated_qs = paginator.get_page(page)
    data = list(paginated_qs.object_list.values())

    return ResponseService.response("SUCCESS", {
        "total_records": paginator.count,
        "per_page": limit,
        "current_page": page,
        "last_page": paginator.num_pages,
        "data": data
    }, Message.DATA_FETCHED)




# @csrf_exempt
# @api_view(["GET"])
# def task_assignees(request):
#     """ Get All Task Assignees related to Opportunity Tasks"""

#     action = ActionService.getAction("Task", "VIEW")
#     if not AuthService.hasAuthority(request , action):
#         return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

#     return get_all_task_assignees(request)


# def get_all_task_assignees(request):
#     """ Fetch all Unique Task Assignees Assigned to Opportunity Tasks"""

    
#     all_columns = ["core_users.*",]
#     filter_json = request.GET.get("filter", {})
#     search_string = request.GET.get("search", "")
#     page = int(request.GET.get("page", 1))
#     limit = int(request.GET.get("limit", 10))
#     sort_by = request.GET.get("sort_by", "core_users.id")  # Sorting by User ID to ensure uniqueness
#     sort_dir = request.GET.get("sort_dir", "desc")
#     allowed_filters = []
#     search_columns = ["core_users.display_name", "core_users.email"]
#     allowed_sorting_columns = ["core_users.display_name"]

    
#     data = (
#         QueryBuilderService("core_users")
#         .leftJoin("core_tasks", "core_tasks.assigned_to_id", "core_users.id")  # Join Task → User
#         .leftJoin("crm_opportunity_tasks", "crm_opportunity_tasks.task_id", "core_tasks.id")  # Join OpportunityTask → Task
#         .select(*all_columns)
#         .whereNotNull("crm_opportunity_tasks.opportunity_id")  # Ensure it's linked to an opportunity
#         # .groupBy("user.id")  
#         .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
#         .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
#     )

#     return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def task_statuses(request):
    """ Get All Task Statuses"""
    action = ActionService.getAction("Task", "VIEW")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    return get_all_task_statuses(request)


def get_all_task_statuses(request):
    """ Fetch all Task Statuses"""
    all_columns = ["*"]
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "id")
    sort_dir = request.GET.get("sort_dir", "desc")
    assigned_to = request.GET.get("assigned_to", None)
    allowed_filters = ["type"]
    search_columns = ["name", "description"]
    allowed_sorting_columns = ["name", "type"]

    data = QueryBuilderService("core_task_status") \
        .select(*all_columns) \
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
        .get()
    
    
    # loop the data and add param task_count to each status
    for status in data:
        status["total_task_count"] = 0

        if assigned_to is not None:
            status["total_task_count"] = QueryBuilderService("core_tasks") \
                                        .where("task_status_id", status["id"]) \
                                        .where("assigned_to_id", assigned_to) \
                                        .count()

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def get_task_status_by_id(request, task_status_id):
    """ Fetch a Single Task Status by ID"""
    action = ActionService.getAction("Task", "VIEW")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    status = QueryBuilderService("core_task_status").where("id", task_status_id).first()
    
    if not status:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    # Add total task count for this status
    status["total_task_count"] = QueryBuilderService("core_tasks") \
        .where("task_status_id", task_status_id) \
        .count()

    return ResponseService.response("SUCCESS", status, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["PATCH"])
def update_task_assignee(request, id):
    """ Update Task Assignee"""

    action = ActionService.getAction("Task", "UPDATE")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    return process_task_assignee_update(request, id)


def process_task_assignee_update(request, id):
    """ Process Task Assignee Update"""

    data = request.data

    rules = {
        "assigned_to": "required|integer|exists:core_users,id",
    }

    errors = ValidatorService.validate(data, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

    
    assigned_by_id = request.user.id if request.user.is_authenticated else None

    existing_task = QueryBuilderService("core_tasks").where("id", id).first()
    if not existing_task:
        return ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

    old_assigned_to = existing_task.get("assigned_to_id")
    new_assigned_to = data.get("assigned_to")

    
    update_data = {"assigned_to_id": new_assigned_to}
    updated_assignee = QueryBuilderService("core_tasks").where("id", id).update(update_data)

    
    if old_assigned_to and old_assigned_to != new_assigned_to:
        # Fetch user display names
        old_user = QueryBuilderService("core_users").where("id", old_assigned_to).select("display_name").first()
        new_user = QueryBuilderService("core_users").where("id", new_assigned_to).select("display_name").first()

        old_name = old_user["display_name"] if old_user else f"User({old_assigned_to})"
        new_name = new_user["display_name"] if new_user else f"User({new_assigned_to})"

        history_data = {
            "task_id": id,
            "changed_by_id": assigned_by_id,
            "from_assigned_id": old_assigned_to,
            "to_assigned_id": new_assigned_to,
            "remark": f"Task reassigned from {old_name} to {new_name}",
            "created_at": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        }
        QueryBuilderService("core_task_assignee_histories").insert(history_data)


    return ResponseService.response("SUCCESS", updated_assignee, Message.DATA_UPDATED)

# @csrf_exempt
# @api_view(["GET"])
# def task_interactions(request, id):
#     """ Get All Task Interactions"""

#     data = QueryBuilderService("crm_task_interactions").where("task_id", id).get()
#     return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)


# @csrf_exempt
# @api_view(["POST"])
# def store_task_interaction(request, id):
#     """ Store Task Interaction"""

#     action = ActionService.getAction("TaskInteraction", "CREATE")
#     if not AuthService.hasAuthority(request , action):
#         return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

#     data = request.data

    
#     rules = {
#         "customer_id": "required|integer|exists:customer,id",
#         "opportunity_id": "required|integer|exists:crm_opportunities,id",
#         "contact_id": "required|integer|exists:contact,id",
#     }

#     errors = ValidatorService.validate(data, rules)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)

#     new_interaction = QueryBuilderService("interactions").insert(data)
#     return ResponseService.response("SUCCESS", new_interaction, "default_create_success_msg")


# @csrf_exempt
# @api_view(["GET", "POST", "DELETE"])
# def single_task_interaction(request, id, int_id):
#     """ Get, Update, or Delete Task Interaction"""

#     if request.method == "GET":
#         data = QueryBuilderService("crm_task_interactions").where("id", int_id).first()
#         return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED) if data else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

#     elif request.method == "POST":
#         action = ActionService.getAction("TaskInteraction", "UPDATE")
#         if not AuthService.hasAuthority(request , action):
#             return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

#         data = request.data
#         updated_interaction = QueryBuilderService("crm_task_interactions").where("id", int_id).update(data)

#         return ResponseService.response(
#             "SUCCESS", updated_interaction, "default_update_success_msg"
#         ) if updated_interaction else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)

#     elif request.method == "DELETE":
#         action = ActionService.getAction("TaskInteraction", "DELETE")
#         if not AuthService.hasAuthority(request , action):
#             return ResponseService.response("FORBIDDEN", None, Error.UN_AUTHORIZED)

#         deleted_interaction = QueryBuilderService("crm_task_interactions").where("id", int_id).delete()
#         return ResponseService.response(
#             "SUCCESS", deleted_interaction, "default_delete_success_msg"
#         ) if deleted_interaction else ResponseService.response("NOT_FOUND", None, Error.NOT_FOUND)


@csrf_exempt
@api_view(["GET"])
def task_status_histories(request, id):
    """ Get All Task Status Histories"""

   
    action = ActionService.getAction("Task", "VIEW")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    return get_all_task_status_histories(request, id)


def get_all_task_status_histories(request, id):
    """ Fetch all Task Status Histories with Additional Details"""

    # Select required columns, including joined table columns
    all_columns = [
        "core_task_status_histories.id",
        "core_task_status_histories.task_id",
        "core_task_status_histories.task_status_id",
        "core_task_status.name as task_status_name",  # From joined task_status table
        "core_task_status.color as task_status_color",
        "core_task_status_histories.changed_by_id",
        "core_users.display_name as changed_by_name",  # From joined users table
        "core_task_status_histories.created_at",
        "core_task_status_histories.remark"
    ]

    # Retrieve filters and pagination parameters
    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by", "core_task_status_histories.id")
    sort_dir = request.GET.get("sort_dir", "desc")

    allowed_filters = ["core_task_status_histories.remark"]
    search_columns = ["core_task_status_histories.remark"]
    allowed_sorting_columns = ["core_task_status_histories.created_at"]

    # Query with LEFT JOIN
    data = (
        QueryBuilderService("core_task_status_histories")
        .select(*all_columns)
        .leftJoin("core_task_status", "core_task_status.id","core_task_status_histories.task_status_id" )  # Join task_status table
        .leftJoin("core_users","core_users.id", "core_task_status_histories.changed_by_id", )  # Join users table
        .where("core_task_status_histories.task_id", id)
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)

@csrf_exempt
@api_view(["GET"])
def task_assignee_histories(request, id):
    """ Get All Task Assignee Histories with User Details"""

   
    action = ActionService.getAction("Task", "VIEW")
    if not AuthService.hasAuthority(request , action):
        return ResponseService.response("FORBIDDEN", None, Error.FORBIDDEN)

    
    rules = {"id": "required|integer|exists:core_tasks,id"}
    errors = ValidatorService.validate({"id": id}, rules)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, Error.VALIDATION_ERROR)
    
    # ----------------QueryBuilderService----------------

    filter_json = request.GET.get("filter", {})
    search_string = request.GET.get("search", "")
    page = int(request.GET.get("page", 1))
    limit = int(request.GET.get("limit", 10))
    sort_by = request.GET.get("sort_by")
    sort_dir = request.GET.get("sort_dir", "desc")
    # Normalize empty values to defaults
    sort_by = "core_task_assignee_histories.id" if sort_by in [None, ""] else sort_by
    sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
    allowed_sorting_columns = ["core_task_assignee_histories.id", "core_task_assignee_histories.created_at"]

    allowed_filters = ["remark"]
    search_columns = ["remark"]

    # Fetch Task Assignee Histories with User Info
    data = (
        QueryBuilderService("core_task_assignee_histories")
        .leftJoin("core_users AS changed_by", "changed_by.id", "core_task_assignee_histories.changed_by_id")  # User who made the change
        .leftJoin("core_users AS from_assigned", "from_assigned.id", "core_task_assignee_histories.from_assigned_id")  # Previous assignee
        .leftJoin("core_users AS to_assigned", "to_assigned.id", "core_task_assignee_histories.to_assigned_id")  # New assignee
        .select(
            "core_task_assignee_histories.*",
            "changed_by.display_name AS changed_by_first_name",
            "changed_by.picture AS changed_by_picture",
            "from_assigned.display_name AS from_assigned_first_name",
            "from_assigned.picture AS from_assigned_picture",
            "to_assigned.display_name AS to_assigned_first_name",
            "to_assigned.picture AS to_assigned_picture",
        )
        .where("core_task_assignee_histories.task_id", id)
        .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
        .orderBy(sort_by, sort_dir)
        .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
    )

    return ResponseService.response("SUCCESS", data, Message.DATA_FETCHED)




def to_iso_datetime(date_obj):
    if date_obj:
        dt = datetime.combine(date_obj, time.min)
        return dt.isoformat() + "Z"
    return None

@api_view(["GET"])
def assignee_calendar_view(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    assignee_id = request.GET.get("assignee_id", None)

    filters = Q()

    if start_date and end_date:
        filters &= Q(start_date__range=[start_date, end_date])  # Only start_date filter
    elif start_date:
        filters &= Q(start_date__gte=start_date)
    elif end_date:
        filters &= Q(start_date__lte=end_date)

    if assignee_id:
        filters &= Q(assigned_to_id=assignee_id)

    tasks = Task.objects.filter(filters).values(
        "id", "task", "start_date", "due_date"
    )

    formatted_tasks = [
        {
            "id": task["id"],
            "title": task["task"],
            "start": to_iso_datetime(task["start_date"]),
            "end": to_iso_datetime(task["start_date"])
        }
        for task in tasks
    ]

    return ResponseService.response(
        "SUCCESS",
        formatted_tasks,
        Message.DATA_FETCHED
    )