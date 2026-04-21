from django.core.paginator import Paginator
from django.http import JsonResponse
from rest_framework.decorators import api_view
from envoy.models.form import Form
from envoy.models.form_atribute import FormAttribute
import json
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
from mServices.ValidatorService import ValidatorService


@api_view(["GET", "POST"])
def forms_view(request):
    if request.method == "GET":
        return list_forms(request)
    elif request.method == "POST":
        return create_form(request)


def list_forms(request):
    try:
        # ----------------QueryBuilderService--------------------------------

        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["title", "description"]
        search_columns = ["title", "description"]
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["title", "description"]

        all_columns = ["core_forms.id", "core_forms.title", "core_forms.description"]
        query = (
            QueryBuilderService("core_forms")
            .select(*all_columns)
            .apply_conditions(
                filter_json, allowed_filters, search_string, search_columns
            )
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        # response_data = {
        #     "current_page": page,
        #     "total_records": len(query),
        #     "count": limit,
        #     "data": query,
        # }

        return ResponseService.response(
            "SUCCESS", query, "Forms retrieved successfully!"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def create_form(request):
    try:
        data = json.loads(request.body)

        rules = {"title": "required|max:255", "description": "max:500"}

        custom_messages = {
            "title.required": "Title is required.",
            "title.max": "Title cannot exceed 255 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        form = Form.objects.create(
            title=data["title"], description=data.get("description", "")
        )

        return ResponseService.response(
            "SUCCESS",
            None,
            # {"id": form.id, "title": form.title, "description": form.description},
            "default_create_success_msg",
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


@api_view(["GET", "PUT", "DELETE"])
def form_detail(request, id):
    if request.method == "GET":
        return get_form(request, id)
    elif request.method == "PUT":
        return update_form(request, id)
    elif request.method == "DELETE":
        return delete_form(request, id)


def get_form(request, id):
    try:
        form = Form.objects.get(id=id)
        data = {"id": form.id, "title": form.title, "description": form.description}
        return ResponseService.response("SUCCESS", data, "Form retrieved successfully!")

    except Form.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form not found")


def update_form(request, id):
    try:
        form = Form.objects.get(id=id)
        data = json.loads(request.body)

        rules = {"title": "required|max:255", "description": "max:500"}

        custom_messages = {
            "title.required": "Title is required.",
            "title.max": "Title cannot exceed 255 characters.",
            "description.max": "Title cannot exceed 500 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        form.title = data["title"]
        form.description = data.get("description", form.description)
        form.save()

        return ResponseService.response(
            "SUCCESS",
            None,
            # {"id": form.id, "title": form.title},
            "default_update_success_msg",
        )

    except Form.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form not found")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def delete_form(request, id):
    try:
        # Validation
        rules = {
            "id": "required|exists:core_forms,id"
        }
        custom_messages = {
            "id.required": "Form ID is required.",
            "id.exists": "The specified form does not exist.",
        }

        errors = ValidatorService.validate({"id": id}, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        form = Form.objects.filter(id=id).first()
        if not form:
            return ResponseService.response("NOT_FOUND", None, "Form not found")

        # Check related submissions
        submission_ids = list(
            QueryBuilderService("core_form_submissions")
            .select("id")
            .where("form_id", id)
            .get()
        )

        if submission_ids:
            submission_ids = [sub["id"] for sub in submission_ids]

            # Delete related submission values
            QueryBuilderService("core_form_submission_values") \
                .whereIn("form_submission_id", submission_ids) \
                .delete()

            # Delete form submissions
            QueryBuilderService("core_form_submissions") \
                .whereIn("id", submission_ids) \
                .delete()

        # Delete form attributes
        QueryBuilderService("core_form_attributes") \
            .where("form_id", id) \
            .delete()

        # Delete form group mappings
        QueryBuilderService("core_form_group_forms") \
            .where("form_id", id) \
            .delete()

        # Finally, delete the form itself
        form.delete()

        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



@api_view(["GET", "POST"])
def form_attributes_view(request, id):
    if request.method == "GET":
        return get_form_attributes(request, id)
    elif request.method == "POST":
        return create_form_attribute(request, id)


def get_form_attributes(request, id):
    try:
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        search_string = request.GET.get("search", "")
        filter_json = request.GET.get("filter", {})

        allowed_filters = ["title", "type"]
        search_columns = ["title", "type"]
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_sorting_columns = ["title", "type"]

        all_columns = ["core_form_attributes.id", "core_form_attributes.title", "core_form_attributes.type"]
        query = (
            QueryBuilderService("core_form_attributes")
            .select(*all_columns)
            .where("form_id", id)
            .apply_conditions(
                filter_json, allowed_filters, search_string, search_columns
            )
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

       

        return ResponseService.response(
            "SUCCESS", query, "Attributes retrieved successfully!"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def create_form_attribute(request, id):
    try:
        form = Form.objects.get(id=id)
        data = json.loads(request.body)

        rules = {"title": "required|max:255", "type": "required|max:10"}

        custom_messages = {
            "title.required": "Title is required.",
            "title.max": "Title cannot exceed 255 characters.",
            "type.required": "Type is required.",
            "title.max": "Type cannot exceed 10 characters.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        attribute = FormAttribute.objects.create(
            form=form, title=data["title"], type=data["type"]
        )

        return ResponseService.response(
            "SUCCESS",
            None
            # {"id": attribute.id, "title": attribute.title}
            ,
            "default_create_success_msg",
        )

    except Form.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form not found")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


@api_view(["GET", "PUT", "DELETE"])
def form_attribute_detail(request, id, attribute_id):
    if request.method == "GET":
        return get_form_attribute(request, id, attribute_id)
    elif request.method == "PUT":
        return update_form_attribute(request, id, attribute_id)
    elif request.method == "DELETE":
        return delete_form_attribute(request, id, attribute_id) 

 
def get_form_attribute(request, id, attribute_id):
    try:
        attribute = FormAttribute.objects.get(id=attribute_id, form_id=id)
        data = {"id": attribute.id, "title": attribute.title, "type": attribute.type}
        return ResponseService.response(
            "SUCCESS", data, "Attribute retrieved successfully!"
        )

    except FormAttribute.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Attribute not found")


def update_form_attribute(request, id, attribute_id):
    try:
        attribute = FormAttribute.objects.get(id=attribute_id, form_id=id)
        data = json.loads(request.body)

        rules = {"title": "required|max:255", "type": "required"}

        custom_messages = {
            "title.required": "Title is required.",
            "title.max": "Title cannot exceed 255 characters.",
            "type.required": "Type is required.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        attribute.title = data.get("title", attribute.title)
        attribute.type = data.get("type", attribute.type)
        attribute.save()

        return ResponseService.response(
            "SUCCESS",
            None,
            # {"id": attribute.id, "title": attribute.title},
            "default_update_success_msg",
        )

    except FormAttribute.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Attribute not found")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def delete_form_attribute(request, id, attribute_id):
    try:
        # Step 1: Ensure the attribute is linked to the given form
        attribute = FormAttribute.objects.filter(id=attribute_id, form_id=id).first()

        if not attribute:
            return ResponseService.response("NOT_FOUND", None, "Attribute not associated with this form")

        # Step 2: Remove the attribute association from core_form_attributes
        QueryBuilderService("core_form_attributes")\
            .where("id", attribute_id)\
            .where("form_id", id)\
            .delete()

        return ResponseService.response("SUCCESS", None, "attribute_removed_from_form_successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
