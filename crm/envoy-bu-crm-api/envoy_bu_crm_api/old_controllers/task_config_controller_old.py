from rest_framework.decorators import api_view
from django.core.paginator import Paginator
from envoy_bu_crm_api.models import TaskConfig
from mServices.ValidatorService import ValidatorService
import json
import mServices.ResponseService as ResponseService
from django.core.exceptions import ValidationError
from envoy_bu_crm_api.task.models import TaskConfig

task_rules = {
    "task": "required|max:250",
    "code": "required|unique:taskconfig,code|max:80",
    "task_type": "required|exists:envoy_bu_crm_api.TaskType,id",
    "assigned_stage": "required|exists:envoy_bu_crm_api.OpportunityStatus,id",
    "expected_days": "required|integer",
    "order": "required|integer",
}

task_custom_messages = {
    "task.required": "Task cannot be empty.",
    "task.max": "Task cannot exceed 250 characters.",
    "code.required": "Code cannot be empty.",
    "code.unique": "Code must be unique.",
    "code.max": "Code cannot exceed 80 characters.",
    "task_type.required": "Task type is required.",
    "task_type.exists": "The selected task type does not exist.",
    "assigned_stage.required": "Assigned stage is required.",
    "assigned_stage.exists": "The selected assigned stage does not exist.",
    "expected_days.required": "Expected days cannot be empty.",
    "expected_days.integer": "Expected days must be an integer.",
    "order.required": "Order is required.",
    "order.integer": "Order must be an integer."
}
        
@api_view(["GET", "POST"])
def get_task_configs(request):
    if request.method == "GET":
        try:
            page = int(request.GET.get("page", 1))
            per_page = int(request.GET.get("per_page", 10))

            task_configs = TaskConfig.objects.all()
            paginator = Paginator(task_configs, per_page)

            page_task_configs = paginator.get_page(page)

            data = [
                {
                    "id": task_config.id,
                    "task": task_config.task,
                    "code": task_config.code,
                    "task_type": task_config.task_type.name,
                    "assigned_stage": task_config.assigned_stage.name,
                    "expected_days": task_config.expected_days,
                    "reminder_expected_days": task_config.reminder_expected_days,
                    "order": task_config.order,
                }
                for task_config in page_task_configs
            ]

            response_data = {
                "current_page": page,
                "last_page": paginator.num_pages,
                "total_records": paginator.count,
                "count": len(page_task_configs),
                "data": data,
            }

            return ResponseService.response(
                "SUCCESS",
                message="TaskConfigs fetched successfully.",
                result=response_data,
            )
        except Exception as e:
            return ResponseService.response(
                "VALIDATION_ERROR", str(e), "An error occurred while fetching TaskConfigs."
            )

    elif request.method == "POST":
        data = json.loads(request.body)
        try:
            errors = ValidatorService.validate(data, task_rules, task_custom_messages)
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )

            validated_data = data

            task_config = TaskConfig.objects.create(
                task=validated_data["task"],
                code=validated_data["code"],
                task_type_id=validated_data["task_type"],
                assigned_stage_id=validated_data["assigned_stage"],
                expected_days=validated_data["expected_days"],
                reminder_expected_days=validated_data.get("reminder_expected_days", None),
                order=validated_data.get("order", None),
            )

            return ResponseService.response(
                "SUCCESS",
                {
                    "task": task_config.task,
                    "code": task_config.code,
                    "task_type": task_config.task_type.name,
                    "assigned_stage": task_config.assigned_stage.name,
                    "expected_days": task_config.expected_days,
                    "reminder_expected_days": task_config.reminder_expected_days,
                    "order": task_config.order,
                },
                "TaskConfig created successfully!",
            )

        except Exception as e:
            return ResponseService.response(
                "VALIDATION_ERROR", str(e), "An error occurred while creating TaskConfig."
            )

# Handles GET, PUT, DELETE requests for a single task configuration by ID
@api_view(["GET", "PUT", "DELETE"])
def task_config_detail(request, id):
    try:
        task_config = TaskConfig.objects.get(id=id)

        if request.method == "GET":
            data = {
                "id": task_config.id,
                "task": task_config.task,
                "code": task_config.code,
                "task_type": task_config.task_type.name,
                "assigned_stage": task_config.assigned_stage.name,
                "expected_days": task_config.expected_days,
                "reminder_expected_days": task_config.reminder_expected_days,
                "order": task_config.order,
            }
            return ResponseService.response(
                "SUCCESS", message="TaskConfig fetched successfully.", result=data
            )

        elif request.method == "PUT":
            data = json.loads(request.body)

            errors = ValidatorService.validate(data, task_rules, task_custom_messages)
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )

            validated_data = data

            task_config.task = validated_data["task"]
            task_config.code = validated_data["code"]
            task_config.task_type_id = validated_data["task_type"]
            task_config.assigned_stage_id = validated_data["assigned_stage"]
            task_config.expected_days = validated_data["expected_days"]
            task_config.reminder_expected_days = validated_data.get(
                "reminder_expected_days", task_config.reminder_expected_days
            )
            task_config.order = validated_data.get("order", task_config.order)
            task_config.save()

            return ResponseService.response(
                "SUCCESS",
                {
                    "id": task_config.id,
                    "task": task_config.task,
                    "code": task_config.code,
                    "task_type": task_config.task_type.name,
                    "assigned_stage": task_config.assigned_stage.name,
                    "expected_days": task_config.expected_days,
                    "reminder_expected_days": task_config.reminder_expected_days,
                    "order": task_config.order,
                },
                "TaskConfig updated successfully!",
            )

        elif request.method == "DELETE":
            task_config.delete()
            return ResponseService.response(
                "SUCCESS",
                message=f"TaskConfig with id {id} deleted successfully!",
                result=None,
            )

    except TaskConfig.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", f"TaskConfig with id {id} does not exist", "Not Found"
        )
    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

@api_view([ "POST"])
def update_task_config_order(request):
    try:
        data = json.loads(request.body)
        
        task_rules = {
            "order": "required|array",
            # "order.*": "integer|exists:taskconfig,id",
        }

        task_custom_messages = {
            "order.required": "Order list cannot be empty.",
            "order.array": "Order must be an array.",
            # "order.min": "At least one TaskConfig ID is required.",
            # "order.*.integer": "Each TaskConfig ID must be an integer.",
            # "order.*.exists": "Some TaskConfig IDs do not exist.",
        }

        errors = ValidatorService.validate(data, task_rules, task_custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        order_list = data.get("order", [])

        for index, task_config_id in enumerate(order_list, start=1):
            TaskConfig.objects.filter(id=task_config_id).update(order=index)

        return ResponseService.response(
            "SUCCESS", None, "TaskConfig order updated successfully"
        )

    except json.JSONDecodeError:
        return ResponseService.response(
            "VALIDATION_ERROR", {"error": "Invalid JSON format"}, "Validation Error"
        )
    except Exception as e:
        return ResponseService.response(
            "ERROR", {"error": str(e)}, "An unexpected error occurred"
        )
