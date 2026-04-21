from rest_framework.decorators import api_view
from envoy.models import CoreUserBankDetail
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json

@api_view(["GET", "POST"])
def user_bank_detail_view(request):
    if request.method == "GET":
        return list_user_bank_details(request)
    elif request.method == "POST":
        return create_user_bank_detail(request)


def list_user_bank_details(request):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["user_id", "service_provider_id","bank_name", "bank_branch"]
        search_columns = ["account_holder_name", "bank_name", "bank_branch", "account_number"]
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["id", "user_id","service_provider_id","bank_name", "account_holder_name", "account_number"]

        all_columns = ["id", "user_id", "service_provider_id", "account_holder_name", "bank_name", "bank_branch",
                       "account_number", "iban_swift_code", "payment_gateway_url", "created_at", "updated_at"]

        query = (
            QueryBuilderService("core_user_bank_details")
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "data_retrieved_successfully")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def create_user_bank_detail(request):
    try:
        data = json.loads(request.body)

        rules = {
            "user_id": "nullable|exists:core_users,id",
            "service_provider_id": "nullable|exists:core_service_providers,id",
            "account_holder_name": "required|max:255",
            "bank_name": "required|max:100",
            "bank_branch": "required|max:100",
            "account_number": "required|max:50",
            "iban_swift_code": "nullable|max:50",
            "payment_gateway_url": "nullable|max:100"
        }

        custom_messages = {
            "account_holder_name.required": "Account holder name is required.",
            "bank_name.required": "Bank name is required.",
            "bank_branch.required": "Bank branch is required.",
            "account_number.required": "Account number is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)

        # Custom logic to ensure only one of user_id or service_provider_id is provided
        if not data.get("user_id") and not data.get("service_provider_id"):
            errors["user_or_service_provider"] = ["Either user_id or service_provider_id is required."]
        elif data.get("user_id") and data.get("service_provider_id"):
            errors["user_or_service_provider"] = ["Provide only one of user_id or service_provider_id, not both."]

        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        CoreUserBankDetail.objects.create(
            user_id=data.get("user_id"),
            service_provider_id=data.get("service_provider_id"),
            account_holder_name=data["account_holder_name"],
            bank_name=data["bank_name"],
            bank_branch=data["bank_branch"],
            account_number=data["account_number"],
            iban_swift_code=data.get("iban_swift_code"),
            payment_gateway_url=data.get("payment_gateway_url")
        )

        return ResponseService.response("SUCCESS", None, "default_create_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(["GET", "PUT", "DELETE"])
def user_bank_detail(request, id):
    if request.method == "GET":
        return get_user_bank_detail(request, id)
    elif request.method == "PUT":
        return update_user_bank_detail(request, id)
    elif request.method == "DELETE":
        return delete_user_bank_detail(request, id)


def get_user_bank_detail(request, id):
    try:
        bank = CoreUserBankDetail.objects.get(id=id)
        data = {
            "id": bank.id,
            "user_id": bank.user_id,
            "user_name": bank.user.display_name if bank.user else None,
            "service_provider_id": bank.service_provider_id,
            "service_provider_name": bank.service_provider.name if bank.service_provider else None,
            "account_holder_name": bank.account_holder_name,
            "bank_name": bank.bank_name,
            "bank_branch": bank.bank_branch,
            "account_number": bank.account_number,
            "iban_swift_code": bank.iban_swift_code,
            "payment_gateway_url": bank.payment_gateway_url,
        }
        return ResponseService.response("SUCCESS", data, "data_retrieved_successfully")
    except CoreUserBankDetail.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def update_user_bank_detail(request, id):
    try:
        bank = CoreUserBankDetail.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "account_holder_name": "required|max:255",
            "bank_name": "required|max:100",
            "bank_branch": "required|max:100",
            "account_number": "required|max:50",
            "iban_swift_code": "nullable|max:50",
            "service_provider_id": "nullable|exists:envoy_serviceprovider,id",
            "payment_gateway_url": "nullable|max:100"
        }

        custom_messages = {
            "account_holder_name.required": "Account holder name is required.",
            "bank_name.required": "Bank name is required.",
            "bank_branch.required": "Bank branch is required.",
            "account_number.required": "Account number is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        bank.account_holder_name = data["account_holder_name"]
        bank.bank_name = data["bank_name"]
        bank.bank_branch = data["bank_branch"]
        bank.account_number = data["account_number"]
        bank.iban_swift_code = data.get("iban_swift_code", "")
        bank.service_provider_id = data.get("service_provider_id")
        bank.payment_gateway_url = data.get("payment_gateway_url")
        bank.save()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")
    except CoreUserBankDetail.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

def delete_user_bank_detail(request, id):
    try:
        bank = CoreUserBankDetail.objects.get(id=id)
        bank.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except CoreUserBankDetail.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "data_not_found")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
