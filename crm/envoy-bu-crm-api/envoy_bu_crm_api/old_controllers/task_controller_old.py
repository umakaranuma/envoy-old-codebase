# from rest_framework.decorators import api_view
# from django.core.paginator import Paginator
# from envoy_bu_crm_api.task.models import Task
# from envoy_bu_crm_api.task.models.task_config import TaskConfig 
# from envoy_bu_crm_api.task.models.task_status import TaskStatus
# from core.models import User 
# from mServices.ValidatorService import ValidatorService
# import json
# import mServices.ResponseService as ResponseService
# from django.core.exceptions import ValidationError
# from django.db.models import Q
# from datetime import datetime




# @api_view(["POST"])
# def store_task(request):
   
#     print("Task creation started...")

#     data = json.loads(request.body)

   
#     rules = {
#         "task": "required|max:250",
#         "description": "max:500",
#         "assigned_to": "required|exists:core.User,id",
#         "task_status": "required|exists:envoy_bu_crm_api.task.TaskStatus,id",
#         "task_config": "required|exists:envoy_bu_crm_api.task.TaskConfig,id",
#         "start_date": "required|date",
#         "due_date": "required|date",
#     }

#     custom_messages = {
#         "task.required": "Task name cannot be empty.",
#         "task.max": "Task name cannot exceed 250 characters.",
#         "description.max": "Description cannot exceed 500 characters.",
#         "assigned_to.required": "Assigned user is required.",
#         "assigned_to.exists": "Assigned user does not exist.",
#         "task_status.required": "Task status is required.",
#         "task_status.exists": "Task status does not exist.",
#         "task_config.required": "Task configuration is required.",
#         "task_config.exists": "Task configuration does not exist.",
#         "start_date.required": "Start date is required.",
#         "start_date.date": "Start date must be a valid date.",
#         "due_date.required": "Due date is required.",
#         "due_date.date": "Due date must be a valid date.",
#         "due_date.after": "Due date must be after start date.",
#     }

#     try:
        
#         errors = ValidatorService.validate(data, rules, custom_messages)
#         if errors:
#             return ResponseService.response(
#                 "VALIDATION_ERROR", errors, "Validation Error"
#             )

        
#         start_date = datetime.strptime(data["start_date"], "%Y-%m-%d")
#         due_date = datetime.strptime(data["due_date"], "%Y-%m-%d")

#         if due_date <= start_date:
#             return ResponseService.response(
#                 "VALIDATION_ERROR",
#                 {"error": "Due date must be after Start date."},
#                 "Validation Error"
#             )

        
#         assigned_user = User.objects.filter(id=data["assigned_to"]).first()
#         task_config = TaskConfig.objects.filter(id=data["task_config"]).first()
#         task_status = TaskStatus.objects.filter(id=data["task_status"]).first()

#         if not assigned_user or not task_config or not task_status:
#             return ResponseService.response(
#                 "VALIDATION_ERROR",
#                 {"error": "Invalid foreign key reference."},
#                 "Validation Error"
#             )

       
#         task = Task.objects.create(
#             task=data["task"],
#             description=data.get("description", ""),
#             assigned_to=assigned_user,
#             task_status=task_status,
#             task_config=task_config,
#             start_date=start_date,
#             due_date=due_date,
#         )

#         print("Task created successfully.")

#         return ResponseService.response(
#             "SUCCESS",
#             {
#                 "id": task.id,
#                 "task": task.task,
#                 "description": task.description,
#                 "assigned_to": task.assigned_to_id,
#                 "task_status": task.task_status_id,
#                 "task_config": task.task_config_id,
#                 "start_date": task.start_date.strftime("%Y-%m-%d"),
#                 "due_date": task.due_date.strftime("%Y-%m-%d"),
#             },
#             "Task created successfully!"
#         )

#     except ValidationError as e:
#         return ResponseService.response(
#             "VALIDATION_ERROR", e.message_dict, "Validation Error"
#         )

#     except Exception as e:
#         return ResponseService.response(
#             "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
#         )

# @api_view(["GET"])
# def get_tasks(request):
#     try:
#         # Extract filters from query parameters
#         task_status_id = request.GET.get("task_status_id")
#         assigned_to = request.GET.get("assigned_to")
#         start_date = request.GET.get("start_date")
#         end_date = request.GET.get("end_date")

#         # Pagination params
#         page = int(request.GET.get("page", 1))
#         per_page = int(request.GET.get("per_page", 10))

#         # Base QuerySet
#         tasks_queryset = Task.objects.all()

#         # Apply filters dynamically
#         filters = Q()
#         if task_status_id:
#             filters &= Q(task_status_id=task_status_id)
#         if assigned_to:
#             filters &= Q(assigned_to_id=assigned_to)
#         if start_date:
#             filters &= Q(start_date__gte=start_date)
#         if end_date:
#             filters &= Q(end_date__lte=end_date)

#         # Apply filters to QuerySet
#         tasks_queryset = tasks_queryset.filter(filters).order_by("id")

#         # Pagination
#         paginator = Paginator(tasks_queryset, per_page)
#         paginated_tasks = paginator.get_page(page)

#         # Serialize response
#         data = [
#             {
#                 "id": task.id,
#                 "title": task.title,
#                 "description": task.description,
#                 "task_status": task.task_status.name if task.task_status else None,
#                 "assigned_to": task.assigned_to.get_full_name() if task.assigned_to else None,
#                 "start_date": task.start_date,
#                 "end_date": task.end_date,
#             }
#             for task in paginated_tasks
#         ]

#         response_data = {
#             "current_page": page,
#             "last_page": paginator.num_pages,
#             "total_records": paginator.count,
#             "count": len(paginated_tasks),
#             "data": data,
#         }

#         return ResponseService.response(
#             "SUCCESS",
#             result=response_data,
#             message="Tasks retrieved successfully!"
#         )

#     except ValidationError as e:
#         return ResponseService.response(
#             "VALIDATION_ERROR", e.message_dict, "Validation Error"
#         )

#     except Exception as e:
#         return ResponseService.response(
#             "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
#         )
