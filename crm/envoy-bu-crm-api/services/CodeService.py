
import mServices.QueryBuilderService as QueryBuilderService

class CodeService:
    @staticmethod
    def createOpporunityCode():
        # Get the last ID from crm_opportunities table and generate code from that
        last_opportunity = QueryBuilderService("crm_opportunities")\
                    .select('id')\
                    .orderBy('id', 'desc')\
                    .first()
        
        # If no records exist, start with 1, otherwise use last_id + 1
        last_id = last_opportunity.get('id') if last_opportunity else 0
        next_id = last_id + 1
        
        # Generate the code
        return "ORD-" + str(next_id).zfill(6)
    
    def createTaskCode():
        # create crm_opportunities table data count +1 code start with ORD- and 6 digit number
        count = QueryBuilderService("core_tasks")\
                    .select('id')\
                    .count()
        
        return str(count + 1).zfill(6)