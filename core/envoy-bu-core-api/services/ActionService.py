
from mServices import QueryBuilderService

class ActionService:
    @staticmethod
    def getAction(entity, action):
        data = QueryBuilderService("actions")\
                .where("entity",entity) \
                .where("action",action) \
                .first()
        
        return data
                