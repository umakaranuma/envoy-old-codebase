from rest_framework.decorators import api_view
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ResponseService as ResponseService
from mServices.ValidatorService import ValidatorService

from envoy.models.form_cust_form_el_opt import CoreFormCustomFormElementOption
from envoy.models.form_custom_elements import CoreFormCustomFormElement
from envoy.models.form_custom_form_setup import CoreFormCustomFormStep
from envoy.models.form_dis_el_values import CoreFormDisplayElementValue
from envoy.models.form_elements import CoreFormElement
from envoy.models.form_group_el_op import CoreFormGroupElementOption
from envoy.models.form_panels import CoreFormCustomFormPanel
from envoy.models.form_submission_values import CoreFormSubmissionValue
from envoy.models.form_submissions import CoreFormSubmission
from envoy.models.form_templetes import CoreTemplate
from envoy.constants import Error
from services.ActionService import ActionService
from services.AuthService import AuthService
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction



@api_view(["GET", "POST"])
def template_list(request):

    if request.method == "GET":
        return list_templates(request)

    return create_template(request)


def list_templates(request):
    try:
        # Parameters from request
        filter_json = request.GET.get("filters", '{}')
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by")
        sort_dir = request.GET.get("sort_dir")
        
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        # Configuration
        table_name = "core_templates"
        all_columns = [
            "core_templates.id",
            "core_templates.title",
            "core_templates.type",
            "core_templates.description"
        ]
        allowed_filters = ["title", "type"]
        search_columns = ["title", "description"]
        allowed_sorting_columns = ["title", "type", "id"]

        # Build query
        query = (
            QueryBuilderService(table_name)
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "Templates retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



def create_template(request):
    try:
        data = request.data

        rules = {
            "title": "required|max:200|unique:core_templates,title",
            "type": "required|in:single_form,multi_step_form",
            "description": "max:250"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.unique": "Template with this title already exists.",
            "type.required": "Form type is required.",
            "type.in": "Type must be 'single_form' or 'multi_step_form'."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        template = CoreTemplate.objects.create(
            title=data["title"],
            type=data["type"],
            description=data.get("description", None)
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "id": template.id,
                "title": template.title,
                "type": template.type,
                "description": template.description,
            },
            "default_create_success_msg"
        )
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "PUT", "DELETE"])
def template_detail(request, id):
    try:
        template = CoreTemplate.objects.get(id=id)
    except CoreTemplate.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Template not found.")

    if request.method == "GET":
        return get_template_detail(template)

    elif request.method == "PUT":
        return update_template(request, template)

    elif request.method == "DELETE":
        return delete_template(template)


def get_template_detail(template):
    try:
        template_data = {
            "id": template.id,
            "name": template.title,
            "description": template.description,
            "type": template.type,
        }

        # Steps
        steps = (
            QueryBuilderService("core_form_custom_form_steps")
            .select("*")
            .where("form_id", template.id)
            .get()
        )

        # Panels
        panels = (
            QueryBuilderService("core_form_custom_form_panels")
            .select("*")
            .where("form_id", template.id)
            .orderBy("order_number")
            .get()
        )

        panel_ids = [panel["id"] for panel in panels]

        # Elements ordered by order_number
        elements_query = (
            QueryBuilderService("core_form_custom_form_elements as ele")
            .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id")
            .select(
                "ele.*",
                # "fe.code as element_code",
                # "fe.group_id as group_id",
            )
            .whereIn("ele.panel_id", panel_ids if panel_ids else [0])
            .orderBy("ele.order_number")
            .get()
        )

        element_ids = [e["id"] for e in elements_query]

        # Fetch element values in bulk
        values_data = (
            QueryBuilderService("core_form_display_element_values")
            .select("element_id", "value")
            .whereIn("element_id", element_ids if element_ids else [0])
            .get()
        )
        values_dict = {v["element_id"]: v["value"] for v in values_data}

        elements = []
        for element in elements_query:
            # Get options for element
            options = (
                QueryBuilderService("core_form_custom_form_element_options")
                .select("*")
                .where("element_id", element["id"])
                .get()
            )
            # Attach value to element
            element["value"] = values_dict.get(element["id"], None)
            element["options"] = options
            elements.append(element)

        result = {
            "template": template_data,
            "steps": steps,
            "panels": panels,
            "elements": elements
        }

        return ResponseService.response("SUCCESS", result, "Template details retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def update_template(request, template):
    try:
        data = request.data
        if not isinstance(data, dict):
            return ResponseService.response("VALIDATION_ERROR", {}, "Invalid data format. JSON object expected.")

        rules = {
            "title": f"required|max:200|unique:core_templates,title,{template.id}",
            "type": "required|in:single_form,multi_step_form",
            "description": "max:250"
        }

        custom_messages = {
            "title.required": "Title is required.",
            "title.unique": "Template with this title already exists.",
            "type.required": "Form type is required.",
            "type.in": "Type must be 'single_form' or 'multi_step_form'."
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        template.title = data["title"]
        template.type = data["type"]
        template.description = data.get("description", None)
        template.save()

        return ResponseService.response(
            "SUCCESS",
            {
                "id": template.id,
                "title": template.title,
                "type": template.type,
                "description": template.description,
            },
            "default_update_success_msg"
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_template(template):
    try:
        if CoreFormSubmission.objects.filter(form=template).exists():
            return ResponseService.response(
                "CONFLICT",
                [],
                "template_cannot_be_deleted"
            )

        template.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "POST"])
def form_steps(request, id):
    if request.method == "GET":
        return list_form_steps(request, id)
    elif request.method == "POST":
        return create_form_step(request, id)



def list_form_steps(request, id):
    try:
        filter_json = request.GET.get("filters", '{}')
        search_string = request.GET.get("search", "")
        sort_by = request.GET.get("sort_by", "step_number")
        sort_dir = request.GET.get("sort_dir", "desc")

        all_columns = [
            "core_form_custom_form_steps.id",
            "core_form_custom_form_steps.title",
            "core_form_custom_form_steps.step_number",
            "core_form_custom_form_steps.description"
        ]
        allowed_filters = ["title"]
        search_columns = ["title", "description"]
        allowed_sorting_columns = ["step_number", "title"]

        query = (
            QueryBuilderService("core_form_custom_form_steps")
            .select(*all_columns)
            .where("form_id", id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .orderBy(sort_by, sort_dir)
            .get()  # This is your correct method
        )
        # Add form_id to each step

        return ResponseService.response("SUCCESS", query, "Form steps retrieved successfully.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def create_form_step(request, id):
    data = request.data

    rules = {
        "title": "required|max:200",
        "description": "max:250"
    }

    custom_messages = {
        "title.required": "Title is required.",
    }

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        form = CoreTemplate.objects.get(id=id)
    except CoreTemplate.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form template not found.")

    # Step: Calculate highest step_number for the form (like sort_index)
    highest_step = (
        QueryBuilderService("core_form_custom_form_steps")
        .where("form_id", id)
        .orderBy("step_number", "desc")
        .select("step_number")
        .first()
    )
    last_step_number = highest_step["step_number"] if highest_step and highest_step["step_number"] is not None else 0
    new_step_number = last_step_number + 1

    step = CoreFormCustomFormStep.objects.create(
        form=form,
        title=data["title"],
        step_number=new_step_number,
        description=data.get("description", None)
    )

    return ResponseService.response(
        "SUCCESS",
        {
            "id": step.id,
            "title": step.title,
            "step_number": step.step_number,
            "description": step.description,
        },
        "Form step created successfully."
    )

@api_view(["GET", "PATCH", "DELETE"])
def form_step_detail(request, id, step_id):
    if request.method == "GET":
        return get_form_step(request, id, step_id)
    elif request.method == "PATCH":
        return update_form_step(request, id, step_id)
    elif request.method == "DELETE":
        return delete_form_step(request, id, step_id)


def get_form_step(request, id, step_id):
    try:
        step = CoreFormCustomFormStep.objects.get(id=step_id, form_id=id)
        data = {
            "id": step.id,
            "title": step.title,
            "step_number": step.step_number,
            "description": step.description
        }
        return ResponseService.response("SUCCESS", data, "Form step retrieved successfully.")
    except CoreFormCustomFormStep.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form step not found.")



def update_form_step(request, id, step_id):
    data = request.data

    rules = {
        "title": "required|max:200",
        "description": "max:250",
        "prev_step_id": "nullable|exists:core_form_custom_form_steps,id",
        "next_step_id": "nullable|exists:core_form_custom_form_steps,id"
    }

    custom_messages = {
        "title.required": "Title is required.",
    }

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        step = CoreFormCustomFormStep.objects.get(id=step_id, form_id=id)
    except CoreFormCustomFormStep.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form step not found.")

    # Safe and strict dynamic step_number calculation like sort_index logic
    prev_step = CoreFormCustomFormStep.objects.filter(id=data.get("prev_step_id"), form_id=id).first() if data.get("prev_step_id") else None
    next_step = CoreFormCustomFormStep.objects.filter(id=data.get("next_step_id"), form_id=id).first() if data.get("next_step_id") else None

    prev_number = float(prev_step.step_number) if prev_step else 0.0
    next_number = float(next_step.step_number) if next_step else prev_number + 1.0

    if prev_step and next_step:
        new_step_number = (prev_number + next_number) / 2
    elif next_step:
        new_step_number = next_number / 2
    elif prev_step:
        new_step_number = prev_number + 1
    else:
        # No references passed, fallback to 1 (clean fallback, never keep old step_number blindly)
        new_step_number = 1.0

    # Update step
    step.title = data["title"]
    step.step_number = new_step_number
    step.description = data.get("description", None)
    step.save()

    return ResponseService.response(
        "SUCCESS",
        {
            "id": step.id,
            "title": step.title,
            "step_number": step.step_number,
            "description": step.description,
        },
        "default_update_success_msg"
    )


def delete_form_step(request, id, step_id):
    try:
        step = CoreFormCustomFormStep.objects.get(id=step_id, form_id=id)

        # Get all panels in this step
        panels = CoreFormCustomFormPanel.objects.filter(step_id=step.id)

        for panel in panels:
            # Get all elements in the panel
            elements = CoreFormCustomFormElement.objects.filter(panel_id=panel.id)

            # Delete all form submission values associated with these elements
            for element in elements:
                CoreFormSubmissionValue.objects.filter(custom_form_element_id=element.id).delete()

            # Delete the elements
            elements.delete()

        # Delete all panels
        panels.delete()

        # Delete the step
        step.delete()

        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except CoreFormCustomFormStep.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form step not found.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



@api_view(['POST'])
def create_form_panel(request, id):
    data = request.data

    try:
        form = CoreTemplate.objects.get(id=id)
    except CoreTemplate.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form template not found.")

    # Base rules
    rules = {
        "title": "max:200",
    }

    # If multi_step_form, require step_id
    if form.type == 'multi_step_form':
        rules["step_id"] = "required|exists:core_form_custom_form_steps,id"

    custom_messages = {
        "step_id.exists": "The specified step does not exist."
    }

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    # Only fetch step if multi_step_form and step_id is provided
    step = None
    if form.type == 'multi_step_form' and data.get("step_id"):
        try:
            step = CoreFormCustomFormStep.objects.get(id=data["step_id"], form=form)
        except CoreFormCustomFormStep.DoesNotExist:
            return ResponseService.response("NOT_FOUND", None, "Form step not found.")

    # Calculate highest order_number like step_number
    highest_panel = (
        QueryBuilderService("core_form_custom_form_panels")
        .where("form_id", id)
        .orderBy("order_number", "desc")
        .select("order_number")
        .first()
    )
    last_order_number = highest_panel["order_number"] if highest_panel and highest_panel["order_number"] is not None else 0
    new_order_number = last_order_number + 1

    panel = CoreFormCustomFormPanel.objects.create(
        form=form,
        step=step,
        title=data.get("title", None),
        order_number=new_order_number
    )

    return ResponseService.response(
        "SUCCESS",
        {
            "id": panel.id,
            "title": panel.title,
            "step_id": panel.step.id if panel.step else None,
            "order_number": panel.order_number
        },
        "default_create_success_msg"
    )


@api_view(['POST'])
def duplicate_form_panel(request, id, panel_id):
    try:
        # Validate Panel Exists
        original_panel = CoreFormCustomFormPanel.objects.filter(id=panel_id, form_id=id).first()
        if not original_panel:
            return ResponseService.response("NOT_FOUND", None, "Original panel not found.")

        # Fetch panels to calculate next panel & order_number
        panels = (
            QueryBuilderService("core_form_custom_form_panels")
            .where("form_id", id)
            .orderBy("order_number", "asc")
            .get()
        )

        prev_number = float(original_panel.order_number) if original_panel.order_number else 0.0
        next_number = None

        # Identify next panel after the given panel_id
        found_original = False
        for panel in panels:
            if found_original:
                next_number = float(panel["order_number"]) if panel["order_number"] is not None else None
                break
            if panel["id"] == panel_id:
                found_original = True

        next_number = next_number if next_number is not None else prev_number + 1.0
        new_order_number = (prev_number + next_number) / 2

        # Duplicate Panel
        duplicated_panel = CoreFormCustomFormPanel.objects.create(
            title=f"{original_panel.title} (Copy)",
            form=original_panel.form,
            step=original_panel.step,
            order_number=new_order_number
        )

        # Duplicate Elements & their Options, Values
        elements = CoreFormCustomFormElement.objects.filter(panel=original_panel)

        for element in elements:
            # Duplicate Element
            new_element = CoreFormCustomFormElement.objects.create(
                label=element.label,
                step=element.step,
                panel=duplicated_panel,
                element=element.element,
                is_required=element.is_required,
                order_number=element.order_number,
                column_size=element.column_size,
                parent=element.parent,
                category=element.category,
                code=element.code
            )

            # Duplicate Options
            options = CoreFormCustomFormElementOption.objects.filter(element=element)
            CoreFormCustomFormElementOption.objects.bulk_create([
                CoreFormCustomFormElementOption(element=new_element, option_value=opt.option_value)
                for opt in options
            ])

            # Duplicate Values
            values = CoreFormDisplayElementValue.objects.filter(element=element)
            CoreFormDisplayElementValue.objects.bulk_create([
                CoreFormDisplayElementValue(element=new_element, value=val.value)
                for val in values
            ])

       # Fetch duplicated elements with joined code and attached options/values
        elements_query = (
            QueryBuilderService("core_form_custom_form_elements as ele")
            .leftJoin("core_form_elements as fe", "fe.id", "ele.element_id")
            .select("ele.*", "fe.code as element_code")
            .where("ele.panel_id", duplicated_panel.id)
            .get()
        )

        element_ids = [e["id"] for e in elements_query]

        # Fetch display values in bulk
        values_dict = {
            v["element_id"]: v["value"]
            for v in QueryBuilderService("core_form_display_element_values")
            .select("element_id", "value")
            .whereIn("element_id", element_ids if element_ids else [0])
            .get()
        }

        # Attach options and value to each element
        elements = []
        for element in elements_query:
            options = (
                QueryBuilderService("core_form_custom_form_element_options")
                .select("*")
                .where("element_id", element["id"])
                .get()
            )
            element["options"] = options
            element["value"] = values_dict.get(element["id"], None)
            elements.append(element)

        # Final Response in consistent structure
        result = {
            "panel": {
                "id": duplicated_panel.id,
                "title": duplicated_panel.title,
                "step_id": duplicated_panel.step.id if duplicated_panel.step else None,
                "order_number": duplicated_panel.order_number,
            },
            "elements": elements
        }
        return ResponseService.response("SUCCESS", result, "default_create_success_msg")


    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET"])
def list_form_panels_by_step(request, id, step_id):
    try:
        # Validate form exists
        form = CoreTemplate.objects.filter(id=id).first()
        if not form:
            return ResponseService.response("NOT_FOUND", None, "Form template not found.")

        # Validate step exists and belongs to form
        step = CoreFormCustomFormStep.objects.filter(id=step_id, form_id=id).first()
        if not step:
            return ResponseService.response("NOT_FOUND", None, "Form step not found for this form.")

        # Fetch panels filtered by form and step, ordered by order_number
        panels = (
            QueryBuilderService("core_form_custom_form_panels")
            .select("id", "title", "order_number", "step_id")
            .where("form_id", id)
            .where("step_id", step_id)
            .orderBy("order_number", "asc")
            .get()
        )

        return ResponseService.response("SUCCESS", panels, "default_get_success_msg")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")




@api_view(['POST', 'GET'])
def form_element(request, id):
    if request.method == 'POST':
        return create_form_element(request, id)
    elif request.method == 'GET':
        return get_all_form_elements(request, id, )



def create_form_element(request, id):
    data = request.data

    try:
        form = CoreTemplate.objects.get(id=id)
    except CoreTemplate.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form template not found.")

    # Validation rules
    rules = {
        "label": "nullable|max:200",
        "panel_id": "required|exists:core_form_custom_form_panels,id",
        "element_id": "required|exists:core_form_elements,id",
        "is_required": "boolean",
        "column_size": "required|integer",
        "options": "array",
        "category": "required|in:input_individual,input_group,display",
        "code": "required|string",
        "parent_id": "nullable|exists:core_form_custom_form_elements,id"
    }

    if form.type == 'multi_step_form':
        rules["step_id"] = "required|exists:core_form_custom_form_steps,id"

    custom_messages = {
        "step_id.exists": "The specified step does not exist.",
        "element_id.required": "Element ID is required.",
        "element_id.exists": "The specified element does not exist.",
        "column_size.required": "Column size is required.",
        "column_size.integer": "Column size must be an integer.",
        "category.required": "Category is required.",
        "category.in": "Invalid category value.",
        "code.required": "Code is required.",
        "options.array": "Options must be an array."
    }

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    step = None
    if form.type == 'multi_step_form' and data.get("step_id"):
        step = CoreFormCustomFormStep.objects.filter(id=data["step_id"], form=form).first()
        if not step:
            return ResponseService.response("NOT_FOUND", None, "Form step not found.")

    panel = CoreFormCustomFormPanel.objects.filter(id=data["panel_id"], form=form).first()
    if not panel:
        return ResponseService.response("NOT_FOUND", None, "Form panel not found.")

    parent = None
    if data.get("parent_id"):
        parent = CoreFormCustomFormElement.objects.filter(id=data["parent_id"]).first()

    highest_element = (
        QueryBuilderService("core_form_custom_form_elements")
        .where("panel_id", panel.id)
        .orderBy("order_number", "desc")
        .select("order_number")
        .first()
    )
    last_order_number = highest_element["order_number"] if highest_element and highest_element["order_number"] is not None else 0
    new_order_number = last_order_number + 1

    try:
        with transaction.atomic():
            element = CoreFormCustomFormElement.objects.create(
                label=data.get("label"),
                step=step,
                panel=panel,
                element_id=data["element_id"],
                is_required=data.get("is_required", False),
                order_number=new_order_number,
                column_size=data["column_size"],
                parent=parent,
                category=data["category"],
                code=data["code"]
            )

            options = data.get("options", [])
            if options:
                CoreFormCustomFormElementOption.objects.bulk_create([
                    CoreFormCustomFormElementOption(element=element, option_value=opt)
                    for opt in options
                ])

            value = data.get("value")
            if value:
                CoreFormDisplayElementValue.objects.create(element=element, value=value)

            saved_options = list(CoreFormCustomFormElementOption.objects.filter(element=element).values())

            element_code = (
                QueryBuilderService("core_form_custom_form_elements as el")
                .leftJoin("core_form_elements as fe", "fe.id", "el.element_id")
                .select("fe.code")
                .where("el.id", element.id)
                .first()
            )["code"] if element else None

        return ResponseService.response(
            "SUCCESS",
            {
                "id": element.id,
                "label": element.label,
                "element_id": element.element.id,
                "step_id": element.step.id if element.step else None,
                "panel_id": element.panel.id if element.panel else None,
                "order_number": element.order_number,
                "column_size": element.column_size,
                "is_required": element.is_required,
                "category": element.category,
                "code": element.code,
                "parent_id": element.parent.id if element.parent else None,
                "options": saved_options,
                "value": value,
                "element_code": element_code
            },
            "default_create_success_msg"
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Transaction Failed. Rollback done.")





def get_all_form_elements(request, form_id):
    try:
        # Step 1: Fetch all elements associated with the form
        elements = (
            QueryBuilderService("core_form_custom_form_elements as el")
            .leftJoin("core_form_custom_form_steps as step", "step.id", "el.step_id")
            .leftJoin("core_form_custom_form_panels as panel", "panel.id", "el.panel_id")
            .leftJoin("core_form_elements as fe", "fe.id", "el.element_id")
            .select(
                "el.id",
                "el.label",
                "el.element_id",
                "fe.code as element_code",
                "fe.category as element_category",
                "el.step_id",
                "el.panel_id",
                "el.order_number",
                "el.column_size",
                "el.is_required"
            )
            .where("panel.form_id", form_id)
            .get()
        )

        filtered_elements = []

        # Step 2: Filter out display/input_group elements and append options/values
        for element in elements:
            if element.get("element_category") in ["display", "input_group"]:
                continue

            element_id = element["id"]

            options = (
                QueryBuilderService("core_form_custom_form_element_options")
                .select("*")
                .where("element_id", element_id)
                .get()
            )

            value_obj = (
                QueryBuilderService("core_form_display_element_values")
                .select("value")
                .where("element_id", element_id)
                .first()
            )

            element["options"] = options
            element["value"] = value_obj["value"] if value_obj else None

            filtered_elements.append(element)

        return ResponseService.response("SUCCESS", filtered_elements, "default_get_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



@api_view(['GET'])
def list_form_elements_grouped(request):
    try:
        filter_json = request.GET.get("filters", '{}')
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 1000))
        sort_by = request.GET.get("sort_by", "element_group")
        sort_dir = request.GET.get("sort_dir", "desc")

        table = "core_form_elements"
        all_columns = [
            "core_form_elements.id",
            "core_form_elements.title",
            "core_form_elements.code",
            "core_form_elements.category",
            "core_form_elements.element_group",
            "core_form_elements.description",
            "core_form_elements.group_element_order_number",
            "core_form_elements.group_id"
        ]
        allowed_filters = ["category", "element_group"]
        search_columns = ["title", "code", "description", "element_group"]
        allowed_sorting_columns = ["id", "title", "element_group"]

        query = (
            QueryBuilderService(table)
            .select(*all_columns)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        grouped_elements = {}
        non_grouped_elements = {}

        for elem in query["data"]:
            options = []
            if elem["category"] == "input_group":
                options = list(CoreFormGroupElementOption.objects.filter(element_id=elem["id"]).values("id", "option_value"))
            elem["options"] = options

            # Check by group_id column
            if elem.get("group_id"):
                # Group under group_elements by element_group
                group_name = elem.get("element_group") or "Ungrouped"
                grouped_elements.setdefault(group_name, []).append(elem)
            else:
                # Group under elements by element_group (even if element_group is present but no group_id)
                group_name = elem.get("element_group") or "Ungrouped"
                non_grouped_elements.setdefault(group_name, []).append(elem)

        result = {
            "elements": [
                {"group": group, "elements": elements}
                for group, elements in non_grouped_elements.items()
            ],
            "group_elements": [
                elem for elements in grouped_elements.values() for elem in elements
            ]

        }

        return ResponseService.response("SUCCESS", result, "default_get_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(['PATCH', 'DELETE'])
def form_panel_detail(request, id, panel_id):

    if request.method == 'PATCH':
        return update_form_panel(request,id, panel_id)

    elif request.method == 'DELETE':
        return delete_form_panel(request, id, panel_id)




def update_form_panel(request, id, panel_id):
    data = request.data

    # Fetch the form to determine the type
    try:
        form = CoreTemplate.objects.get(id=id)
    except CoreTemplate.DoesNotExist:
        return ResponseService.response("NOT_FOUND", {"form_id": "Form not found."}, "Invalid form ID.")

    # Define base validation rules
    rules = {
        "title": "max:200",
        "prev_panel_id": "nullable|exists:core_form_custom_form_panels,id",
        "next_panel_id": "nullable|exists:core_form_custom_form_panels,id"
    }

    # Conditionally add 'step_id' validation if the form is not 'single_form'
    if form.type != 'single_form':
        rules["step_id"] = "required|exists:core_form_custom_form_steps,id"

    custom_messages = {
        "step_id.exists": "Step does not exist."
    }

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        panel = CoreFormCustomFormPanel.objects.get(id=panel_id, form_id=id)
    except CoreFormCustomFormPanel.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "default_not_found_msg")

    step = None
    if data.get("step_id"):
        try:
            step = CoreFormCustomFormStep.objects.get(id=data["step_id"], form_id=id)
        except CoreFormCustomFormStep.DoesNotExist:
            return ResponseService.response("NOT_FOUND", None, "Step not found.")

    # Dynamic order_number calculation
    prev_panel = CoreFormCustomFormPanel.objects.filter(id=data.get("prev_panel_id"), form_id=id).first() if data.get("prev_panel_id") else None
    next_panel = CoreFormCustomFormPanel.objects.filter(id=data.get("next_panel_id"), form_id=id).first() if data.get("next_panel_id") else None

    prev_number = float(prev_panel.order_number) if prev_panel else 0.0
    next_number = float(next_panel.order_number) if next_panel else prev_number + 1.0

    if prev_panel and next_panel:
        new_order_number = (prev_number + next_number) / 2
    elif next_panel:
        new_order_number = next_number / 2
    elif prev_panel:
        new_order_number = prev_number + 1
    else:
        new_order_number = panel.order_number  # fallback

    # Apply updates
    panel.title = data.get("title", panel.title)
    panel.step = step
    panel.order_number = new_order_number
    panel.save()

    return ResponseService.response(
        "SUCCESS",
        {
            "id": panel.id,
            "title": panel.title,
            "step_id": panel.step.id if panel.step else None,
            "order_number": panel.order_number
        },
        "default_update_success_msg"
    )


def delete_form_panel(request, id, panel_id):
    try:
        panel = CoreFormCustomFormPanel.objects.get(id=panel_id, form_id=id)
        elements = CoreFormCustomFormElement.objects.filter(panel_id=panel.id)
        for element in elements:
            CoreFormSubmissionValue.objects.filter(custom_form_element_id=element.id).delete()
        elements.delete()
        panel.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except CoreFormCustomFormPanel.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form panel not found.")
    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")

@api_view(['GET', 'PATCH', 'DELETE'])
def form_element_detail(request, id, element_id):
    if request.method == 'GET':
        return get_form_element(request, id, element_id)
    elif request.method == 'PATCH':
        return update_form_element(request, id, element_id)
    elif request.method == 'DELETE':
        return delete_form_element(request, id, element_id)



def get_form_element(request, id, element_id):
    try:
        element_data = (
            QueryBuilderService("core_form_custom_form_elements as el")
            .leftJoin("core_form_custom_form_steps as step", "step.id", "el.step_id")
            .leftJoin("core_form_custom_form_panels as panel", "panel.id", "el.panel_id")
            .leftJoin("core_form_elements as fe", "fe.id", "el.element_id")
            .select(
                "el.id",
                "el.label",
                "el.element_id",
                "fe.code as element_code",
                "el.step_id",
                "el.panel_id",
                "el.order_number",
                "el.column_size",
                "el.is_required"
            )
            .where("el.id", element_id)
            .where("panel.form_id", id)
            .first()
        )

        if not element_data:
            return ResponseService.response("NOT_FOUND", None, "Form element not found.")

        # Fetch options
        options = (
            QueryBuilderService("core_form_custom_form_element_options")
            .select("*")
            .where("element_id", element_id)
            .get()
        )

        # Fetch value (single value expected)
        value_obj = (
            QueryBuilderService("core_form_display_element_values")
            .select("value")
            .where("element_id", element_id)
            .first()
        )
        element_data["options"] = options
        element_data["value"] = value_obj["value"] if value_obj else None

        return ResponseService.response("SUCCESS", element_data, "Form element retrieved successfully.")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")




def update_form_element(request, id, element_id):
    data = request.data

    # Fetch form to check type
    try:
        form = CoreTemplate.objects.get(id=id)
    except CoreTemplate.DoesNotExist:
        return ResponseService.response("NOT_FOUND", {"form_id": "Form not found."}, "Invalid form ID.")

    # Base validation rules
    rules = {
        "label": "nullable|max:200",
        "panel_id": "nullable|exists:core_form_custom_form_panels,id",
        "element_id": "required|exists:core_form_elements,id",
        "is_required": "boolean",
        "column_size": "required|integer",
        "prev_element_id": "nullable|exists:core_form_custom_form_elements,id",
        "next_element_id": "nullable|exists:core_form_custom_form_elements,id",
        "options": "array",
        "value": "nullable|string"
    }

    # Conditionally add step_id validation for multi_step_form
    if form.type != 'single_form':
        rules["step_id"] = "required|exists:core_form_custom_form_steps,id"
    else:
        rules["step_id"] = "nullable|exists:core_form_custom_form_steps,id"

    custom_messages = {
        "element_id.required": "Element ID is required.",
        "column_size.required": "Column size is required."
    }

    errors = ValidatorService.validate(data, rules, custom_messages)
    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    try:
        element = CoreFormCustomFormElement.objects.get(id=element_id, panel__form_id=id)
    except CoreFormCustomFormElement.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form element not found.")

    # Step & Panel assignment
    step = CoreFormCustomFormStep.objects.filter(id=data.get("step_id"), form_id=id).first() if data.get("step_id") else element.step
    panel = CoreFormCustomFormPanel.objects.filter(id=data.get("panel_id"), form_id=id).first() if data.get("panel_id") else element.panel

    if data.get("panel_id") and not panel:
        return ResponseService.response("NOT_FOUND", None, "Panel not found.")

    # Calculate order_number
    prev_element = CoreFormCustomFormElement.objects.filter(id=data.get("prev_element_id"), panel_id=panel.id).first() if data.get("prev_element_id") else None
    next_element = CoreFormCustomFormElement.objects.filter(id=data.get("next_element_id"), panel_id=panel.id).first() if data.get("next_element_id") else None

    prev_number = float(prev_element.order_number) if prev_element else 0.0
    next_number = float(next_element.order_number) if next_element else prev_number + 1.0

    if prev_element and next_element:
        new_order_number = (prev_number + next_number) / 2
    elif next_element:
        new_order_number = next_number / 2
    elif prev_element:
        new_order_number = prev_number + 1
    else:
        new_order_number = element.order_number

    # Update element
    element.label = data.get("label", element.label)
    element.step = step
    element.panel = panel
    element.element_id = data.get("element_id", element.element.id)
    element.is_required = data.get("is_required", element.is_required)
    element.order_number = new_order_number
    element.column_size = data["column_size"]
    element.save()

    # Update options if provided
    if "options" in data:
        CoreFormCustomFormElementOption.objects.filter(element=element).delete()
        CoreFormCustomFormElementOption.objects.bulk_create([
            CoreFormCustomFormElementOption(element=element, option_value=opt)
            for opt in data["options"]
        ])
    updated_options = list(CoreFormCustomFormElementOption.objects.filter(element=element).values())

    # Update or create value
    if "value" in data:
        CoreFormDisplayElementValue.objects.update_or_create(
            element=element,
            defaults={"value": data["value"] if isinstance(data["value"], str) else ""}
        )

    # Fetch element code
    element_info = (
        QueryBuilderService("core_form_custom_form_elements as el")
        .leftJoin("core_form_elements as fe", "fe.id", "el.element_id")
        .select("fe.code")
        .where("el.id", element.id)
        .first()
    )
    element_code = element_info["code"] if element_info else None

    value_obj = CoreFormDisplayElementValue.objects.filter(element=element).first()
    element_value = value_obj.value if value_obj else None

    return ResponseService.response(
        "SUCCESS",
        {
            "id": element.id,
            "label": element.label,
            "element_id": element.element.id,
            "step_id": element.step.id if element.step else None,
            "panel_id": element.panel.id if element.panel else None,
            "order_number": element.order_number,
            "column_size": element.column_size,
            "is_required": element.is_required,
            "options": updated_options,
            "value": element_value,
            "element_code": element_code
        },
        "default_update_success_msg"
    )


def delete_form_element(request, id, element_id):
    try:
        element = CoreFormCustomFormElement.objects.get(id=element_id, panel__form_id=id)
        element.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")
    except CoreFormCustomFormElement.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, "Form element not found.")
