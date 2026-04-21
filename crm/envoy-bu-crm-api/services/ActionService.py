
from mServices import QueryBuilderService

class ActionService:
    @staticmethod
    def getAction(entity, action):
        try:
            data = (
                QueryBuilderService("core_actions")
                .where("entity", entity)
                .where("action", action)
                .first()
            )
            print("ActionService.getAction →", data)
            return data
        except Exception as exc:
            # Fail open: if actions table is missing or query fails, don't block requests
            print(f"ActionService.getAction error: {str(exc)} | entity={entity}, action={action}")
            return None
                