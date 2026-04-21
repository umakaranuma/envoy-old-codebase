# from rest_framework.decorators import api_view
# from envoy.models.form_submissions import CoreFormSubmission
# from envoy.models.form_custom_elements import CoreFormCustomFormElement
# from envoy.models.form_elements import CoreFormElement
# from envoy.models.form_templetes import CoreTemplate
# from envoy.models.user import User
# from envoy.models.form_submission_values import CoreFormSubmissionValue

# from mServices.ValidatorService import ValidatorService
# from mServices.ResponseService import ResponseService
# from mServices.QueryBuilderService import QueryBuilderService

# from django.db import transaction


# @api_view(["GET", "POST"])
# def form_submission_list(request):
#     if request.method == "GET":
#         return list_form_submissions(request)
#     else:
#         return create_form_submission(request)


# def list_form_submissions(request):
#     try:
#         page = int(request.GET.get("page", 1))
#         limit = int(request.GET.get("limit", 10))

#         all_columns = [
#             "core_form_submissionss.id",
#             "core_form_submissionss.form_id",
#             "core_form_submissionss.user_id",
#         ]
#         allowed_sorting_columns = ["id"]

#         query = (
#             QueryBuilderService("core_form_submissionss")
#             .select(*all_columns)
#             .paginate(page, limit, allowed_sorting_columns, "id", "desc")
#         )

#         return ResponseService.response("SUCCESS", query, "Submissions retrieved successfully.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


# def create_form_submission(request):
#     data = request.data

#     rules = {
#         "form_id": "required|exists:core_templates,id",
#         "user_id": "required|exists:core_users,id",
#         "values": "required|array"
#     }
 
#     custom_messages = {
#         "form_id.required": "Form ID is required.",
#         "user_id.required": "User ID is required.",
#         "values.required": "At least one value is required."
#     }

#     errors = ValidatorService.validate(data, rules, custom_messages)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#     try:
#         with transaction.atomic():
#             submission = CoreFormSubmission.objects.create(
#                 form_id=data["form_id"],
#                 user_id=data["user_id"]
#             )

#             values = data["values"]
#             value_objects = []
#             for val in values:
#                 value_objects.append(CoreFormSubmissionValue(
#                     submission=submission,
#                     custom_form_element_id=val["custom_form_element"],
#                     form_element_id=val["form_element"],
#                     value=val.get("value", "")
#                 ))

#             CoreFormSubmissionValue.objects.bulk_create(value_objects)

#         return ResponseService.response("SUCCESS", {
#             "id": submission.id
#         }, "Submission created successfully.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


# @api_view(["GET", "PUT", "DELETE"])
# def form_submission_detail(request, id):
#     try:
#         submission = CoreFormSubmission.objects.get(id=id)
#     except CoreFormSubmission.DoesNotExist:
#         return ResponseService.response("NOT_FOUND", None, "Submission not found.")

#     if request.method == "GET":
#         return get_form_submission(submission)

#     elif request.method == "PUT":
#         return update_form_submission(request, submission)

#     elif request.method == "DELETE":
#         return delete_form_submission(submission)


# def get_form_submission(submission):
#     try:
#         values = list(CoreFormSubmissionValue.objects.filter(submission=submission).values(
#             "id", "custom_form_element_id", "form_element_id", "value"
#         ))

#         return ResponseService.response("SUCCESS", {
#             "id": submission.id,
#             "form_id": submission.form_id,
#             "user_id": submission.user_id,
#             "values": values
#         }, "Submission retrieved successfully.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


# def update_form_submission(request, submission):
#     data = request.data

#     rules = {
#         "form_id": "required|exists:core_templates,id",
#         "user_id": "required|exists:users,id",
#         "values": "required|array"
#     }

#     errors = ValidatorService.validate(data, rules)
#     if errors:
#         return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

#     try:
#         with transaction.atomic():
#             submission.form_id = data["form_id"]
#             submission.user_id = data["user_id"]
#             submission.save()

#             # Clear old values
#             CoreFormSubmissionValue.objects.filter(submission=submission).delete()

#             # Add new values
#             new_values = [
#                 CoreFormSubmissionValue(
#                     submission=submission,
#                     custom_form_element_id=val["custom_form_element"],
#                     form_element_id=val["form_element"],
#                     value=val.get("value", "")
#                 )
#                 for val in data["values"]
#             ]
#             CoreFormSubmissionValue.objects.bulk_create(new_values)

#         return ResponseService.response("SUCCESS", {"id": submission.id}, "Submission updated successfully.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


# def delete_form_submission(submission):
#     try:
#         submission.delete()
#         return ResponseService.response("SUCCESS", None, "Submission deleted successfully.")
#     except Exception as e:
#         return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
