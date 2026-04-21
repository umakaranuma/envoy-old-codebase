from rest_framework.decorators import api_view
from rest_framework.response import Response
from envoy.models.global_setting import GlobalSetting
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
import mServices.QueryBuilderService as QueryBuilderService
import json


#  --------------------------------------------------------
# /settings/{key} - Retrieve a single setting
@api_view(["GET", "PATCH"])
def fetch_settings(request, key):
    if request.method == "GET":
        return get_setting(request, key)
    elif request.method == "PATCH":
        return update_setting(request, key)


def get_setting(request, key):

    try:
        # Step 1: Get the `setting_key_id` from `SettingKey`
        setting_key = (
            QueryBuilderService("core_setting_keys")
            .select("id")
            .where("name", key)
            .first()
        )

        # If the key is not found, return a "NOT_FOUND" response
        if not setting_key:
            return ResponseService.response(
                "NOT_FOUND", None, f"Setting '{key}' not found"
            )

        setting_key_id = setting_key["id"]  # Extract the ID

        # Step 2: Find corresponding `GlobalSetting` entry
        setting = (
            QueryBuilderService("core_setting_global")
            .select("id", "value", "setting_key_id")
            .where("setting_key_id", setting_key_id)
            .first()
        )

        # If no matching setting is found, return a "NOT_FOUND" response
        if not setting:
            return ResponseService.response(
                "NOT_FOUND", None, f"Setting for key '{key}' not found in GlobalSetting"
            )

        # Step 3: Format the response
        result = {
            "id": setting["id"],
            "value": setting["value"],
            "setting_key_id": setting["setting_key_id"],
        }

        return ResponseService.response(
            "SUCCESS",
            result,
            "Setting fetched successfully.",
              
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            "An unexpected error occurred."
        )




def update_setting(request, key):
    try:
        data = json.loads(request.body)

        # Validation Rules
        rules = {"value": "required|max:200"}
        custom_messages = {"value.required": "Value cannot be empty."}

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        setting = GlobalSetting.objects.filter(setting_key__name=key).first()
        if not setting:
            return ResponseService.response(
                "NOT_FOUND", None, f"Setting '{key}' not found"
            )

        setting.value = data["value"]
        setting.save()

        return ResponseService.response(
            "SUCCESS",
            message="default_update_success_msg",
            result={"key": setting.setting_key.name, "value": setting.value},
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )


# --------------------------------------------------------
#  GET /settings?keys=key1,key2 - Retrieve multiple settings
@api_view(["GET"])
def get_multiple_settings(request):
    try:
        keys = request.GET.get("keys")

        # print(keys)
        if not keys:
            return ResponseService.response(
                "VALIDATION_ERROR", {"keys": ["Keys parameter is required."]}, "Validation Error"
            )

        key_list = keys.split(",")

        # settings = GlobalSetting.objects.filter(setting_key__name__in=key_list).values(
        #     "setting_key__name", "value"
        # )

        # result = {setting["setting_key__name"]: setting["value"] for setting in settings}

        # ------------QueryBuilderService----------------

        all_columns = ["core_setting_keys.id","core_setting_keys.name AS setting_key_name", "core_setting_global.value"]
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        sort_by = request.GET.get('sort_by','id')
        sort_dir = request.GET.get('sort_dir', 'desc')
        allowed_sorting_columns = ["core_setting_keys.name"]
        filter_json = request.GET.get('filter', '{}')
        filter_json = json.loads(filter_json) if isinstance(filter_json, str) else filter_json 
        search_string = request.GET.get('search', '')
        allowed_filters = ["core_setting_keys.name"]
        search_columns = ["core_setting_keys.name"]
        allowed_sorting_columns = ["core_setting_keys.name"]

        settings = QueryBuilderService("core_setting_global") \
            .select(*all_columns) \
            .leftJoin("core_setting_keys", "core_setting_keys.id", "core_setting_global.setting_key_id") \
            .whereIn("core_setting_keys.name", key_list) \
            .get()
            
        # settings = QueryBuilderService("core_setting_global") \
        #     .select(*all_columns) \
        #     .leftJoin("settingkey", "settingkey.id", "globalsetting.setting_key_id") \
        #     .whereIn("settingkey.name", key_list) \
        #     .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
        #     .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \


        result = {setting["setting_key_name"]: setting["value"] for setting in settings}

        missing_keys = list(set(key_list) - set(result.keys()))

        if missing_keys:
            return ResponseService.response(
                "NOT_FOUND",
                message=f"Some keys were not found: {', '.join(missing_keys)}",
                result={"missing_keys": key_list},
            )
        
        result  = {
            "data" : result
        }

        return ResponseService.response(
            "SUCCESS",
            message="Settings fetched successfully.",
            result=result,
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "An unexpected error occurred."
        )



