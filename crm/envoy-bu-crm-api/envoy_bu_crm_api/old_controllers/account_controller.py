# from django.http import JsonResponse
# from rest_framework.decorators import api_view
# from django.core.exceptions import ValidationError
# from django.core.paginator import Paginator
# import json

# from envoy_bu_crm_api.models import Account
# import mServices.ResponseService as ResponseService
# from mServices.ValidatorService import ValidatorService


# @api_view(["GET", "POST"])
# def get_accounts(request):
#     if request.method == "GET":
#         try:
#             page = int(request.GET.get("page", 1))
#             per_page = int(request.GET.get("per_page", 10))

#             accounts = Account.objects.all()
#             paginator = Paginator(accounts, per_page)
#             page_accounts = paginator.get_page(page)

#             data = [
#                 {
#                     "id": account.id,
#                     "code": account.code,
#                     "type": account.type,
#                     "name": account.name,
#                     "br_no": account.br_no,
#                     "address": account.address,
#                     "email": account.email,
#                     "primary_contact": account.primary_contact,
#                     "secondary_contact": account.secondary_contact,
#                     "logo": account.logo,
#                     "website": account.website,
#                     "no_of_employees": account.no_of_employees,
#                     "remarks": account.remarks,
#                     "parent_id": account.parent_id.id if account.parent_id else None,
#                     "primary_contact_id": account.primary_contact_id.id,
#                 }
#                 for account in page_accounts
#             ]

#             return JsonResponse(
#                 {
#                     "data": data,
#                     "page": page,
#                     "total_pages": paginator.num_pages,
#                     "total_count": paginator.count,
#                 }
#             )

#         except ValidationError as e:
#             return ResponseService.response(
#                 "VALIDATION_ERROR", e.message_dict, "Validation Error"
#             )

#     elif request.method == "POST":
#         data = json.loads(request.body)

#         rules = {
#             "code": "required|unique:accounts,code",
#             "type": "required",
#             "name": "required|min:3|max:200",
#             "email": "required|email",
#             "primary_contact": "required",
#         }

#         custom_messages = {
#             "code.required": "Code is required.",
#             "type.required": "Type is required.",
#             "name.required": "Name is required.",
#             "email.required": "Email is required.",
#             "primary_contact.required": "Primary contact is required.",
#         }

#         try:
#             validator = ValidatorService(data, rules, custom_messages)
#             validator.validate()
#             validated_data = data

#             account = Account.objects.create(
#                 code=validated_data["code"],
#                 type=validated_data["type"],
#                 name=validated_data["name"],
#                 br_no=validated_data.get("br_no", ""),
#                 address=validated_data.get("address", ""),
#                 email=validated_data["email"],
#                 primary_contact=validated_data["primary_contact"],
#                 secondary_contact=validated_data.get("secondary_contact", ""),
#                 logo=validated_data.get("logo", ""),
#                 website=validated_data.get("website", ""),
#                 no_of_employees=validated_data.get("no_of_employees"),
#                 remarks=validated_data.get("remarks", ""),
#                 parent_id_id=validated_data.get("parent_id"),
#                 primary_contact_id_id=validated_data["primary_contact_id"],
#             )

#             return JsonResponse(
#                 {
#                     "message": "Account created successfully!",
#                     "data": {
#                         "id": account.id,
#                         "code": account.code,
#                         "type": account.type,
#                         "name": account.name,
#                         "br_no": account.br_no,
#                         "address": account.address,
#                         "email": account.email,
#                         "primary_contact": account.primary_contact,
#                         "secondary_contact": account.secondary_contact,
#                         "logo": account.logo,
#                         "website": account.website,
#                         "no_of_employees": account.no_of_employees,
#                         "remarks": account.remarks,
#                         "parent_id": account.parent_id.id if account.parent_id else None,
#                         "primary_contact_id": account.primary_contact_id.id,
#                     },
#                 }
#             )
#         except ValidationError as e:
#             return ResponseService.response(
#                 "VALIDATION_ERROR", e.message_dict, "Validation Error"
#             )


# @api_view(["GET", "PUT", "DELETE"])
# def account_detail(request, id):
#     try:
#         account = Account.objects.get(id=id)

#         if request.method == "GET":
#             data = {
#                 "id": account.id,
#                 "code": account.code,
#                 "type": account.type,
#                 "name": account.name,
#                 "br_no": account.br_no,
#                 "address": account.address,
#                 "email": account.email,
#                 "primary_contact": account.primary_contact,
#                 "secondary_contact": account.secondary_contact,
#                 "logo": account.logo,
#                 "website": account.website,
#                 "no_of_employees": account.no_of_employees,
#                 "remarks": account.remarks,
#                 "parent_id": account.parent_id.id if account.parent_id else None,
#                 "primary_contact_id": account.primary_contact_id.id,
#             }
#             return JsonResponse({"data": data})

#         elif request.method == "PUT":
#             data = json.loads(request.body)

#             rules = {
#                 "name": "required|min:3|max:200",
#                 "email": "required|email",
#                 "primary_contact": "required",
#             }

#             custom_messages = {
#                 "name.required": "Name is required.",
#                 "email.required": "Email is required.",
#                 "primary_contact.required": "Primary contact is required.",
#             }

#             validator = ValidatorService(data, rules, custom_messages)
#             validator.validate()
#             validated_data = data

#             account.code = validated_data.get("code", account.code)
#             account.type = validated_data.get("type", account.type)
#             account.name = validated_data["name"]
#             account.br_no = validated_data.get("br_no", account.br_no)
#             account.address = validated_data.get("address", account.address)
#             account.email = validated_data["email"]
#             account.primary_contact = validated_data["primary_contact"]
#             account.secondary_contact = validated_data.get("secondary_contact", account.secondary_contact)
#             account.logo = validated_data.get("logo", account.logo)
#             account.website = validated_data.get("website", account.website)
#             account.no_of_employees = validated_data.get("no_of_employees", account.no_of_employees)
#             account.remarks = validated_data.get("remarks", account.remarks)
#             account.parent_id_id = validated_data.get("parent_id", account.parent_id_id)
#             account.primary_contact_id_id = validated_data.get("primary_contact_id", account.primary_contact_id_id)
#             account.save()

#             return JsonResponse(
#                 {
#                     "message": "Account updated successfully!",
#                     "data": {
#                         "id": account.id,
#                         "code": account.code,
#                         "type": account.type,
#                         "name": account.name,
#                         "br_no": account.br_no,
#                         "address": account.address,
#                         "email": account.email,
#                         "primary_contact": account.primary_contact,
#                         "secondary_contact": account.secondary_contact,
#                         "logo": account.logo,
#                         "website": account.website,
#                         "no_of_employees": account.no_of_employees,
#                         "remarks": account.remarks,
#                         "parent_id": account.parent_id.id if account.parent_id else None,
#                         "primary_contact_id": account.primary_contact_id.id,
#                     },
#                 }
#             )

#         elif request.method == "DELETE":
#             account.delete()
#             return JsonResponse(
#                 {"message": f"Account with id {id} deleted successfully!"}
#             )

#     except Account.DoesNotExist:
#         return ResponseService.response(
#             "NOT_FOUND", f"Account with id {id} does not exist", "Not Found"
#         )
#     except ValidationError as e:
#         return ResponseService.response(
#             "VALIDATION_ERROR", e.message_dict, "Validation Error"
#         )
