
import mServices.QueryBuilderService as QueryBuilderService

class SettingService:
    @staticmethod
    def getSettingKeyValue(key):
        setting_key = QueryBuilderService("core_setting_keys")\
                        .where("name",key)\
                        .first()
        
        if setting_key:
            setting_value = QueryBuilderService("core_setting_global")\
                                .where("setting_key_id",setting_key['id'])\
                                .first()
        

            if setting_value:    
                return setting_value['value']   
            else:
                return None
        else:
            return None