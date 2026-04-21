from django.urls import path
from envoy_bu_crm_api.task.controllers import task_controller
from envoy_bu_crm_api.task.controllers.task_config_controller import *
from envoy_bu_crm_api.sales.controllers.common_controller import *
urlpatterns = [
    path("tasks", task_controller.tasks, name="get_all_tasks"),  # Get All Tasks
    path(
        "tasks/<int:id>", task_controller.single_task, name="single_task"
    ),  # Get Single Task
    # path('tasks', task_controller.create_task, name='create_task'),  # Create Task
    # path('tasks/<int:id>', task_controller.update_task, name='update_task'),  # Update Task
    # path('tasks/<int:id>', task_controller.delete_task, name='delete_task'),  # Delete Task
    path(
        "tasks/<int:id>/status",
        task_controller.update_task_status_methods,
        name="update_task_status",
    ),  # Update Task Status
    path(
        "tasks-assignees", task_controller.task_assignees, name="task_assignees"
    ),  # Get Task Assignees
    path(
        "tasks-statuses", task_controller.task_statuses, name="task_statuses"
    ),  # Get Task Statuses
    path("tasks-statuses/<int:task_status_id>/", task_controller.get_task_status_by_id, name="task_status_detail"),
    # Task Status & Assignee Histories
    path(
        "tasks/<int:id>/status-histories",
        task_controller.task_status_histories,
        name="task_status_histories",
    ),  # Get Task Status History
    path(
        "tasks/<int:id>/assignee-histories",
        task_controller.task_assignee_histories,
        name="task_assignee_histories",
    ),  # Get Task Assignee History
    path(
        "tasks/<int:id>/assignee",
        task_controller.update_task_assignee,
        name="update_task_assignee",
    ),  # Update Task Assignee  
    # Task Config Endpoints
    path('task-configs', task_configs, name='get_all_task_configs'),  # Get All Task Configs
    path('task-configs/<int:id>', single_task_config, name='single_task_config'),  # Get Single Task Config
    path('task-configs/order', update_task_config_order, name='update_task_config_order'),  # Update Order
    path('task-types', task_types, name= "task_types"),
    path('task-types/<int:id>', single_task_type, name= "single_task_type"),
    path("tasks/<int:id>/interactions", task_controller.task_interactions, name="task_interactions"),
    path("tasks/<int:id>/interactions/<int:int_id>", task_controller.single_task_interaction, name="single_task_interaction"),
    path('tasks/opportunities/many', get_opportunity_tasks, name='get_opportunity_tasks'),
    path("tasks/assignee/calendar", task_controller.assignee_calendar_view, name='assignee_calendar_view'),
    # path('tasks/<int:id>/interactions/<int:int_id>', task_controller.update_task_interaction, name='update_task_interaction'),  # Update Task Interaction
    # path('tasks/<int:id>/interactions/<int:int_id>', task_controller.delete_task_interaction, name='delete_task_interaction'),  # Delete Task Interaction
    # path('api/tasks', task_controller.store_task, name='all-tasks'),
    # path('api/task-configs', TaskConfigController.get_task_configs, name='get-task-configs'),
    # path('api/task-configs/<int:id>', TaskConfigController.task_config_detail, name='task_config_detail'),
    # path('api/task-configs/order', TaskConfigController.update_task_config_order, name='task_config_order'),
]
