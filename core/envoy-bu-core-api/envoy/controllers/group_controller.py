from rest_framework.decorators import api_view
import json
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator

import mServices.ResponseService as ResponseService
from mServices.ValidatorService import ValidatorService

from envoy.models.contact_group import ContactGroup
from envoy.models.group_contact import GroupContact
from envoy.models.contact import Contact
from envoy.utils import get_message 
import mServices.QueryBuilderService as QueryBuilderService


# --------------------------------------------------------
# --------------------------------------------------------
# --------------------------------------------------------
# GET /groups & POST /groups - List all groups or create a new group
@api_view(["GET", "POST"])
def get_groups(request):
    if request.method == "GET":
        return list_groups(request)
    elif request.method == "POST":
        return create_group(request)


# --------------------------------------------------------
def list_groups(request):
    try:
        # page = int(request.GET.get("page", 1))
        # per_page = int(request.GET.get("per_page", 10))

        # groups_queryset = ContactGroup.objects.all().order_by("id")
        # paginator = Paginator(groups_queryset, per_page)
        # paginated_groups = paginator.get_page(page)

# -----------QueryBuilderService----------------
        all_columns = ['core_contact_groups.id','core_contact_groups.name','core_contact_groups.description']
        filter_json = request.GET.get('filter', {}) 
        search_string = request.GET.get('search', '')
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        role_detail = ContactGroup.objects.all().order_by("id")
        paginator = Paginator(role_detail, limit)
        sort_by = request.GET.get('sort_by', 'id')
        sort_dir = request.GET.get('sort_dir', 'desc')
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_filters = ["name", "description"]
        search_columns = ["name", "description"]
        allowed_sorting_columns = ["id", "name", "description"]

        query = QueryBuilderService("core_contact_groups")\
                .select(*all_columns) \
                .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
                .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) \

        # data = [
        #     {
        #         "id": group.id,
        #         "name": group.name,
        #         "description": group.description,
        #     }
        #     for group in paginated_groups
        # ]

        # response_data = {
        #     "current_page": page,
        #     "last_page": paginator.num_pages,
        #     "total_records": paginator.count,
        #     "count": len(paginated_groups),
        #     "data": data,
        #     
        # }

        # response_data = {
        #     "current_page": page,
        #     "last_page": paginator.num_pages,
        #     "total_records": paginator.count,
        #     "count": limit,
        #     "data": query,
        # }

        return ResponseService.response(
            "SUCCESS",
            query,
            get_message("RETRIEVED", entity="Groups"),
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR",
            e.message_dict,
            get_message("VALIDATION_ERROR", entity="Groups"),
        )

    except ValueError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            {"pagination": ["Invalid pagination parameters"]},
            get_message("INVALID_REQUEST", entity="Groups"),
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            {"error": str(e)},
            get_message("SERVER_ERROR", entity="Groups"), 
        )


# --------------------------------------------------------
def create_group(request):
    try:
        data = json.loads(request.body)

        rules = {
            "name": "required|max:255",
            "contacts": "required|array",
        }

        custom_messages = {
            "name.required": "Group name cannot be empty.",
            "contacts.required": "Contacts list is required.",
            "contacts.array": "Contacts must be a list.",
        }

        # Validate data using ValidatorService
        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        contact_ids = data["contacts"]

        # Ensure all contact IDs are integers
        if not all(isinstance(contact_id, int) for contact_id in contact_ids):
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"contacts": ["All contact IDs must be integers."]},
                "Validation Error",
            )

        # Fetch existing contacts
        existing_contacts = Contact.objects.filter(id__in=contact_ids)
        existing_contact_ids = set(existing_contacts.values_list("id", flat=True))

        # Identify missing contacts
        missing_contacts = set(contact_ids) - existing_contact_ids
        if missing_contacts:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"contacts": [f"Invalid contact IDs: {list(missing_contacts)}"]},
                "Validation Error",
            )

        # Create Group
        group = ContactGroup.objects.create(
            name=data["name"],
            description=data.get("description", ""),
        )

        # Assign contacts to the group
        GroupContact.objects.bulk_create(
            [
                GroupContact(group=group, contact=contact)
                for contact in existing_contacts
            ]
        )

        response_data = {
            "id": group.id,
            "name": group.name,
            "contacts": list(
                existing_contacts.values("id", "name", "email", "primary_contact")
            ),
        }

        return ResponseService.response(
            "SUCCESS", response_data, "default_create_success_msg"
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


# --------------------------------------------------------
# --------------------------------------------------------
# GET /groups/{id}, POST /groups/{id}, DELETE /groups/{id} - Retrieve, Update, or Delete a group
@api_view(["GET", "POST", "DELETE"])
def get_single_group(request, id):
    if request.method == "GET":
        return get_group(request, id)
    elif request.method == "POST":
        return update_group(request, id)
    elif request.method == "DELETE":
        return delete_group(request, id)



def get_group(request, id):
    try:
       
        response_data = (
            QueryBuilderService("core_contact_groups")
            .select("core_contact_groups.id", "core_contact_groups.name", "core_contact_groups.description")
            .where("core_contact_groups.id", id)
            .first()
        )

        if not response_data:
            return ResponseService.response(
                "NOT_FOUND", None, f"Group with ID {id} does not exist"
            )

        return ResponseService.response(
            "SUCCESS", response_data, "Group retrieved successfully!"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )



def update_group(request, id):
    try:
        group = ContactGroup.objects.get(id=id)
        data = json.loads(request.body)

        rules = {
            "name": "required|max:255",
            "description": "max:255",
        }
        custom_messages = {
            "name.required": "Group name cannot be empty.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        group.name = data["name"]
        group.description = data.get("description", group.description)
        group.save()

        response_data = {
            "id": group.id,
            "name": group.name,
            "description": group.description, 
        }

        return ResponseService.response(
            "SUCCESS", response_data, "default_update_success_msg"
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def delete_group(request, id):
    try:
        rules = {"group_id": "required|exists:core_contact_groups,id"}

        custom_messages = {
            "group_id.required": "Group ID is required.",
            "group_id.exists": "Group with the given ID does not exist.",
        }

        errors = ValidatorService.validate({"group_id": id}, rules, custom_messages)
        if errors:
            return ResponseService.response(
                "VALIDATION_ERROR", errors, "Validation Error"
            )

        group = ContactGroup.objects.get(id=id)
        group.delete()

        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


@api_view(["GET", "POST", "DELETE"])
def get_group_contact(request, id):
    if request.method == "GET":
        return get_group_contacts(request, id)
    elif request.method == "POST":
        return store_group_contacts(request, id)
    elif request.method == "DELETE":
        return delete_group_contacts(request, id)



def store_group_contacts(request, id):
    try:
        group = ContactGroup.objects.get(id=id)
        data = json.loads(request.body)

        rules = {"contacts": "required|array"}
        custom_messages = {
            "contacts.required": "Contacts list is required.",
            "contacts.array": "Contacts must be a list.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        contact_ids = data["contacts"]
        existing_contacts = Contact.objects.filter(id__in=contact_ids)
        existing_contact_ids = set(existing_contacts.values_list("id", flat=True))

        # Validate missing contacts
        missing_contacts = set(contact_ids) - existing_contact_ids
        if missing_contacts:
            return ResponseService.response(
                "VALIDATION_ERROR",
                {"contacts": [f"Invalid contact IDs: {list(missing_contacts)}"]},
                "Validation Error",
            )

        # Avoid duplicates
        existing_group_contacts = set(GroupContact.objects.filter(group=group).values_list("contact_id", flat=True))
        new_contact_ids = existing_contact_ids - existing_group_contacts

        if new_contact_ids:
            GroupContact.objects.bulk_create(
                [GroupContact(group=group, contact=Contact.objects.get(id=cid)) for cid in new_contact_ids]
            )

        return ResponseService.response("SUCCESS", None, "default_create_success_msg")

    except ContactGroup.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, f"Group with ID {id} does not exist")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



def get_group_contacts(request, id):
    try:
        
        # group = ContactGroup.objects.get(id=id)

        # contacts = Contact.objects.filter(groupcontact__group=group).order_by("id")  
        # contact_data = list(
        #     contacts.values(
        #         "id",
        #         "name",
        #         "email",
        #         "address",
        #         "primary_contact",
        #         "secondary_contact",
        #         "remarks",
        #         "picture",
        #     )
        # )

        # final_response = {
        #     "total_records": contacts.count(),  
        #     "data": contact_data,
        # }

        # -------------------QueryBuilderService-------------------
        
        group = ContactGroup.objects.get(id=id)  

        all_columns = [
            "core_contacts.*",
        ]

        filter_json = request.GET.get('filter', {}) 
        search_string = request.GET.get('search', '')
        allowed_filters = ["core_contacts.name", "core_contacts.email", "core_contacts.address"]
        search_columns = ["core_contacts.name", "core_contacts.email", "core_contacts.address"]
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        sort_by = request.GET.get('sort_by', 'id')
        sort_dir = request.GET.get('sort_dir', 'desc')
        sort_by = "id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir
        allowed_sorting_columns = ["core_contacts.id", "core_contacts.name", "core_contacts.email", "core_contacts.address"]

        response_data = QueryBuilderService("core_contacts")\
            .select(*all_columns) \
            .where("core_group_contacts.group_id", id) \
            .leftJoin("core_group_contacts", "core_group_contacts.contact_id", "core_contacts.id") \
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns) \
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir) 

        response_data = response_data if response_data else []

        # final_response = {
        #     # "total_records": len(response_data),  # Count the number of contacts
        #     "data": response_data,
        # }


        return ResponseService.response(
            "SUCCESS", response_data, "Group contacts retrieved successfully!"
        )

    except ContactGroup.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", None, f"Group with ID {id} does not exist"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def delete_group_contacts(request, id):
    try:
        group = ContactGroup.objects.get(id=id)
        data = json.loads(request.body)

        rules = {"contacts": "required|array"}
        errors = ValidatorService.validate(data, rules, {"contacts.required": "Contacts list is required."})
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        contact_ids = data["contacts"]
        deleted_count, _ = GroupContact.objects.filter(group=group, contact_id__in=contact_ids).delete()

        if deleted_count == 0:
            return ResponseService.response("NOT_FOUND", None, "No matching contacts found in the group")

        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except ContactGroup.DoesNotExist:
        return ResponseService.response("NOT_FOUND", None, f"Group with ID {id} does not exist")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



@api_view(["GET"])
def get_assignable_contacts(request, id):
    try:
        
        if not ContactGroup.objects.filter(id=id).exists():
            return ResponseService.response("NOT_FOUND", None, f"Group with ID {id} does not exist")

        
        assigned_contacts = list(GroupContact.objects.filter(group_id=id).values_list("contact_id", flat=True))

        all_columns = [
            "*"
        ]
        filter_json = request.GET.get("filter", {})
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "id")
        sort_dir = request.GET.get("sort_dir", "desc")
        allowed_filters = ["name", "email", "address"]
        search_columns = ["name", "email", "primary_contact", "address"]
        allowed_sorting_columns = ["name", "email", "address"]

        
        query = QueryBuilderService("core_contacts").select(*all_columns).where("show_in_list",1)

        
        if assigned_contacts:
            query = query.whereNotIn("core_contacts.id", assigned_contacts)

        
        query = (
            query.apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", query, "Available contacts retrieved successfully")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
