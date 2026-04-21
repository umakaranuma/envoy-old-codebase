
import mServices.QueryBuilderService as QueryBuilderService
import math
from services.CodeService import CodeService
from datetime import date

class TaskService:
    @staticmethod
    def saveOppourinityTask(oppournity_id,stage_id,sales_agent_id = None):
        task_config = QueryBuilderService("crm_task_configs")\
                        .where("opportunity_status_id",stage_id)\
                        .orderBy("sort_index",'asc')\
                        .get()
        
        # Get task status by type "task_todo" (maintains task based on type)
        task_status = QueryBuilderService("core_task_status")\
                        .where("type", "task_todo")\
                        .first()
        
        if task_config and task_status:
            sales_agent_task = QueryBuilderService("core_tasks") \
                                        .where('task_status_id',task_status["id"]) \
                                        .orderBy('sort_index','DESC') \
                                        .first()
            
            sort_index = 0
            if sales_agent_task:
                sort_index = math.ceil(sales_agent_task["sort_index"])

            for config in task_config:
                task = QueryBuilderService("core_tasks").insert({
                    "code":CodeService.createTaskCode(),
                    "task":config["task"],
                    "assigned_date":date.today(),
                    "sort_index":sort_index,
                    "assigned_to_id":sales_agent_id,
                    "task_status_id":task_status["id"],
                })

                sort_index = sort_index +1

                QueryBuilderService("crm_opportunity_tasks").insert({
                    "opportunity_id" : oppournity_id,
                    "task_id" : task["id"],
                    "task_config_id" : config["id"],
                })
        
       