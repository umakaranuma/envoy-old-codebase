
from mServices import QueryBuilderService

class ActionService:
    @staticmethod
    def getAction(entity, action):
        data = QueryBuilderService("core_actions")\
                .where("entity",entity) \
                .where("action",action) \
                .first()
        print("ActionService.getAction →", data)
        
        return data
                