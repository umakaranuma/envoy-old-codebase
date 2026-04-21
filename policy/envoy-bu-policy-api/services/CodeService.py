
import mServices.QueryBuilderService as QueryBuilderService

class CodeService:
    @staticmethod
    def createOpporunityCode():
        # create crm_opportunities table data count +1 code start with ORD- and 6 digit number
        count = QueryBuilderService("crm_opportunities")\
                    .select('id')\
                    .count()
        
        return "ORD-" + str(count + 1).zfill(6)
    
    def createTaskCode():
        # create crm_opportunities table data count +1 code start with ORD- and 6 digit number
        count = QueryBuilderService("core_tasks")\
                    .select('id')\
                    .count()
        
        return str(count + 1).zfill(6)