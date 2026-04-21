from rest_framework.decorators import api_view
from django.core.exceptions import ObjectDoesNotExist
from envoy.models import Reason  # Adjust this import path to your project structure
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json


@api_view(["GET", "POST"])
def reasons_view(request):
    if request.method == "GET":
        return list_reasons(request)
    elif request.method == "POST":
        return create_reason(request)


def list_reasons(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["reason", "type_id"]
        search_columns = ["reason", "type_id", "description"]
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "core_reasons.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["core_reasons.id", "reason", "type_id"]

        all_columns = ["core_reasons.id", "reason", "type_id", "allows_custom_reason", "description", "crmp_endorsement_types.name as type"]

        query = (
            QueryBuilderService("core_reasons")
            .leftJoin("crmp_endorsement_types", "core_reasons.type_id", "crmp_endorsement_types.id")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "Reasons retrieved successfully!")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def create_reason(request):
    try:
        data = json.loads(request.body)

        rules = {
            "reason": "required|max:255|unique:core_reasons,reason",
            "type_id": "required|exists:crmp_endorsement_types,id",
            "allows_custom_reason": "boolean",
            "description": "nullable|max:500"
        }

        custom_messages = {
            "reason.required": "Reason is required.",
            "reason.max": "Reason cannot exceed 255 characters.",
            "type_id.required": "Type is required.",
            "type_id.exists": "Type does not exist.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        reason = Reason.objects.create(
            reason=data["reason"],
            type_id=data["type_id"],
            allows_custom_reason=data.get("allows_custom_reason", False),
            description=data.get("description", "")
        )

        try:
            # Get the endorsement type name from type_id
            endorsement_type = (
                QueryBuilderService("crmp_endorsement_types")
                .select("name")
                .where("id", data.get("type_id"))
                .first()
            )
            
            if endorsement_type:
                type_name = endorsement_type["name"]
                if type_name == "Additions" or type_name == "Refund" or type_name == "Cancellations" or type_name == "Non-Financials":
                    print("type_name", type_name)
                    endorsement_type_id = data.get("type_id")
                
                print("endorsement_type_id", endorsement_type_id)
                
                # Generate code based on type
                type_mapping = {
                    "Additions": "ADD",
                    "Refund": "REF", 
                    "Cancellations": "CAN",
                    "Non-Financials": "NF"
                }
                
                prefix = type_mapping.get(type_name, "UNK")
                
                # Get the next sequence number for this type
                existing_codes = QueryBuilderService("crmp_endorsement_reason_codes")\
                    .select("code")\
                    .where("endorsement_type_id", endorsement_type_id)\
                    .get()
                
                if existing_codes:
                    # Find the highest number for this prefix
                    max_num = 0
                    for code_obj in existing_codes:
                        code_str = code_obj.get("code", "")
                        if code_str.startswith(prefix):
                            try:
                                num_part = int(code_str[3:])  # Extract number part after prefix
                                max_num = max(max_num, num_part)
                            except ValueError:
                                continue
                    next_num = max_num + 1
                else:
                    next_num = 1
                
                # Generate code with zero-padded number
                code = f"{prefix}{next_num:02d}"
                
                print("Generated code:", code)
                print("endorsement_type_id:", endorsement_type_id)
                print("description:", data.get("reason"))
                
                endorsement_reason_code = (
                    QueryBuilderService("crmp_endorsement_reason_codes")
                    .insert({
                        "code": code, 
                        "endorsement_type_id": endorsement_type_id, 
                        "description": data.get("reason")
                    })
                )

                print("endorsement_reason_code", endorsement_reason_code)

        except Exception as e:
            print("Error in endorsement reason code creation:", str(e))
            import traceback
            traceback.print_exc()

        return ResponseService.response("SUCCESS", None, "default_create_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET"])
def endorsement_types(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        all_columns = ["id", "name"]

        filter_json = request.GET.get("filter", {})
        allowed_filters = ["name"]
        search_string = request.GET.get("search", "")
        search_columns = ["name"]
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["id", "name"]

        data = QueryBuilderService("crmp_endorsement_types").select(*all_columns).apply_conditions(filter_json, allowed_filters, search_string, search_columns).paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        return ResponseService.response("SUCCESS", data, "Endorsement types retrieved successfully!")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "PUT", "DELETE"])
def reason_detail(request, id):
    if request.method == "GET":
        return get_reason(request, id)
    elif request.method == "PUT":
        return update_reason(request, id)
    elif request.method == "DELETE":
        return delete_reason(request, id)


def get_reason(request, id):
    try:
        # reason = Reason.objects.get(id=id)
        # data = {
        #     "id": reason.id,
        #     "reason": reason.reason,
        #     "type_id": reason.type_id,
        #     "allows_custom_reason": reason.allows_custom_reason,
        #     "description": reason.description,
        # }

        all_columns = ["core_reasons.id", "reason", "type_id", "allows_custom_reason", "description", "crmp_endorsement_types.name as type"]
        data = (
            QueryBuilderService("core_reasons")
            .leftJoin("crmp_endorsement_types", "core_reasons.type_id", "crmp_endorsement_types.id")
            .select(*all_columns)
            .where("core_reasons.id", id)
            .first()
        )

        return ResponseService.response("SUCCESS", data, "Reason retrieved successfully!")
    except Reason.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Reason not found")


def update_reason(request, id):
    try:
        reason = Reason.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "reason": f"required|max:255|unique:core_reasons,reason,{id}",
            "type_id": "required|exists:crmp_endorsement_types,id",
            "allows_custom_reason": "boolean",
            "description": "nullable|max:500"
        }

        custom_messages = {
            "reason.required": "Reason is required.",
            "type_id.required": "Type is required.",
            "type_id.exists": "Type does not exist.",
            "reason.max": "Reason cannot exceed 255 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Store the old reason description before updating
        old_reason_description = reason.reason

        reason.reason = data["reason"]
        reason.type_id = data["type_id"]
        reason.allows_custom_reason = data.get("allows_custom_reason", False)
        reason.description = data.get("description", "")
        reason.save()

        try:
            # Get the endorsement type name from type_id
            endorsement_type = (
                QueryBuilderService("crmp_endorsement_types")
                .select("name")
                .where("id", data.get("type_id"))
                .first()
            )
            
            if endorsement_type:
                type_name = endorsement_type["name"]
                if type_name == "Additions" or type_name == "Refund" or type_name == "Cancellations" or type_name == "Non-Financials":
                    print("type_name", type_name)
                    endorsement_type_id = data.get("type_id")
                
                    print("endorsement_type_id", endorsement_type_id)
                    
                    # Find existing endorsement reason code by old description
                    existing_reason_code = (
                        QueryBuilderService("crmp_endorsement_reason_codes")
                        .select("id", "code")
                        .where("description", old_reason_description)
                        .first()
                    )
                    
                    if existing_reason_code:
                        # Update existing endorsement reason code
                        update_result = (
                            QueryBuilderService("crmp_endorsement_reason_codes")
                            .where("id", existing_reason_code["id"])
                            .update({
                                "description": data.get("reason"),
                                "endorsement_type_id": endorsement_type_id
                            })
                        )
                        print("Updated endorsement reason code:", update_result)
                    else:
                        # Generate new code if no existing record found
                        type_mapping = {
                            "Additions": "ADD",
                            "Refund": "REF", 
                            "Cancellations": "CAN",
                            "Non-Financials": "NF"
                        }
                        
                        prefix = type_mapping.get(type_name, "UNK")
                        
                        # Get the next sequence number for this type
                        existing_codes = QueryBuilderService("crmp_endorsement_reason_codes")\
                            .select("code")\
                            .where("endorsement_type_id", endorsement_type_id)\
                            .get()
                        
                        if existing_codes:
                            # Find the highest number for this prefix
                            max_num = 0
                            for code_obj in existing_codes:
                                code_str = code_obj.get("code", "")
                                if code_str.startswith(prefix):
                                    try:
                                        num_part = int(code_str[3:])  # Extract number part after prefix
                                        max_num = max(max_num, num_part)
                                    except ValueError:
                                        continue
                            next_num = max_num + 1
                        else:
                            next_num = 1
                        
                        # Generate code with zero-padded number
                        code = f"{prefix}{next_num:02d}"
                        
                        print("Generated new code:", code)
                        
                        # Create new endorsement reason code
                        endorsement_reason_code = (
                            QueryBuilderService("crmp_endorsement_reason_codes")
                            .insert({
                                "code": code, 
                                "endorsement_type_id": endorsement_type_id, 
                                "description": data.get("reason")
                            })
                        )
                        print("Created new endorsement reason code:", endorsement_reason_code)

        except Exception as e:
            print("Error in endorsement reason code update:", str(e))
            import traceback
            traceback.print_exc()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
    except Reason.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Reason not found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_reason(request, id):
    try:
        reason = Reason.objects.get(id=id)
        reason.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except Reason.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Reason not found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
