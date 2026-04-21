from rest_framework.decorators import api_view
import json
from envoy.models.customer import Customer
from envoy.models.contact import Contact
from envoy.models.contact_group import ContactGroup
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
from mServices.ValidatorService import ValidatorService
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404

from envoy.models.group_contact import GroupContact
from envoy.models.interaction import Intraction
from envoy.models.customer_additional_contact import CustomerAdditionalContact
from django.db.models import Q


@api_view(["GET", "POST"])
def get_contacts(request):
    if request.method == "GET":
        try:
            # page = int(request.GET.get("page", 1))  # Default page = 1
            # per_page = int(request.GET.get("per_page", 10))  # Default per_page = 10

            # contacts = Contact.objects.all().order_by("id")
            # paginator = Paginator(contacts, per_page)
            # page_obj = paginator.get_page(page)

            # data = [
            #     {
            #         "id": contact.id,
            #         "name": contact.name,
            #         "email": contact.email,
            #         "address": contact.address,
            #         "primary_contact": contact.primary_contact,
            #         "secondary_contact": contact.secondary_contact,
            #         "remarks": contact.remarks,
            #         "picture": contact.picture,
            #         "duplicated_contact_id": contact.duplicated_contact_id.id if contact.duplicated_contact_id else None
            #     }
            #     for contact in page_obj
            # ]

            # response_data = {
            #     "current_page": page_obj.number,
            #     "total_pages": paginator.num_pages,
            #     "total_records": paginator.count,
            #     "per_page": per_page,
            #     "count": len(data),
            #     "data": data,
            # }

            # -----------------------QueryBuilderService--------------------------------

            all_columns = [
                "id",
                "name",
                "email",
                "address",
                "primary_contact",
                "secondary_contact",
                "remarks",
                "picture",
                "duplicated_contact_id",
                "website_url",
            ]

            # Fetch Query Parameters and Ensure Proper JSON Parsing
            filter_json = request.GET.get("filter", "{}")
            search_string = request.GET.get("search", "{}")

            try:
                filter_json = json.loads(filter_json) if filter_json.strip() else {}
                search_string = request.GET.get("search", "").strip()  #  Ensure it defaults to an empty string

            except json.JSONDecodeError:
                return ResponseService.response(
                    "VALIDATION_ERROR",
                    {"search": [{"error_type": "invalid_json", "tokens": {"_attribute": "search"}}]},
                    "Validation Error"
                )

            ids = request.GET.get("ids", None)
            page = int(request.GET.get("page", 1))
            limit = int(request.GET.get("limit", 10))
            sort_by = request.GET.get("sort_by")
            sort_dir = request.GET.get("sort_dir")
        
            sort_by = "id" if sort_by in [None, ""] else sort_by
            sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

            allowed_filters = [
                "name",
                "email",
                "address",
                "primary_contact",
                "secondary_contact",
                "remarks",
            ]
            search_columns = [
                "name",
                "email",
                "address",
                "primary_contact",
                "secondary_contact",
                "remarks",
            ]
            allowed_sorting_columns = [
                "id",
                "name",
                "email",
                "address",
                "primary_contact",
                "secondary_contact",
                "remarks",
                "picture",
            ]

            #  Fetch Contacts
            query = (
                QueryBuilderService("core_contacts")
                .select(*all_columns)
                .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
                # .where("show_in_list", True)
            )

            
            if ids:
                query = query.whereIn("id", ids.split(","))
                contacts = query.get()
            else:
                query = query.whereNull("duplicated_contact_id") \
                            .where("show_in_list", True)\
                            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
                contacts = query

            

            

            return ResponseService.response(
                "SUCCESS",
                message="Contacts fetched successfully.",
                result=contacts,
            )

        except ValidationError as e:
            return ResponseService.response("VALIDATION_ERROR", e.message_dict, "Validation Error")

        except Exception as e:
            return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


    elif request.method == "POST":
        try:
            data = json.loads(request.body)

            # Validation Rules
            rules = {
                "name": "required|max:255",
                "primary_contact": "required|max:20",
                "email": "email|max:255",
                "address": "max:255",
                "secondary_contact": "max:20",
                "remarks": "",  
                "picture": "",
                "website_url": "url"
            }

            custom_messages = {
                "name.required": "Name cannot be empty.",
                "name.max": "Name cannot exceed 255 characters.",
                "primary_contact.required": "Primary contact number is required.",
                "primary_contact.max": "Primary contact number cannot exceed 20 characters.",
                "email.email": "Invalid email format.",
                "email.max": "Email cannot exceed 255 characters.",
                "address.max": "Address cannot exceed 255 characters.",
                "secondary_contact.max": "Secondary contact cannot exceed 20 characters.",
                "website_url.url": "Invalid URL format.",
            }

            errors = ValidatorService.validate(data, rules, custom_messages)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

            
            contact = Contact.objects.create(
                name=data["name"],
                primary_contact=data["primary_contact"],
                email=data.get("email", None),
                address=data.get("address", None),
                secondary_contact=data.get("secondary_contact", None),
                remarks=data.get("remarks", None),
                picture=data.get("picture", None),
                website_url=data.get("website_url", None),
                
            )


            
            return ResponseService.response(
                "SUCCESS",
                {
                    "id": contact.id,
                    "name": contact.name,
                    "primary_contact": contact.primary_contact,
                    "email": contact.email,
                    "address": contact.address,
                    "secondary_contact": contact.secondary_contact,
                    "remarks": contact.remarks,
                    "picture": contact.picture,
                    "website_url": contact.website_url,
                },
                "default_create_success_msg",
            )

        except ValidationError as e:
            return ResponseService.response("VALIDATION_ERROR", e.message_dict, "Validation Error")

        except json.JSONDecodeError:
            return ResponseService.response(
                "INVALID_JSON", {"error": "Invalid JSON format"}, "Invalid JSON"
            )

        except Exception as e:
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": str(e)},
                "An unexpected error occurred.",
            )


# Handles GET, PUT, DELETE requests for a single contact by ID
@api_view(["GET", "PUT", "DELETE"])
def contact_detail(request, id):
    try:
        contact = Contact.objects.get(id=id)

        if request.method == "GET":
            merged_contacts = Contact.objects.filter(duplicated_contact_id=id).values(
                "id",
                "name",
                "email",
                "address",
                "primary_contact",
                "secondary_contact",
                "remarks",
                "picture",
            )

            
            data = {
                "id": contact.id,
                "name": contact.name,
                "email": contact.email,
                "address": contact.address,
                "primary_contact": contact.primary_contact,
                "secondary_contact": contact.secondary_contact,
                "remarks": contact.remarks,
                "picture": contact.picture if contact.picture else None,
                "merged_contacts": list(merged_contacts),  
            }

            return ResponseService.response(
                "SUCCESS", message="Contact fetched successfully.", result=data
            )

        elif request.method == "PUT":
            data = json.loads(request.body)

            rules = {
                "name": "required|max:255",
                "email": "email",
                "primary_contact": "required",
            }

            custom_messages = {
                "name.required": "Name cannot be empty.",
                "primary_contact.required": "Primary contact cannot be empty.",
            }
            errors = ValidatorService.validate(data, rules, custom_messages)
            if errors:
                return ResponseService.response(
                    "VALIDATION_ERROR", errors, "Validation Error"
                )
            validated_data = data

            contact.name = validated_data["name"]
            contact.email = validated_data["email"]
            contact.address = validated_data.get("address", contact.address)
            contact.primary_contact = validated_data["primary_contact"]
            contact.secondary_contact = validated_data.get(
                "secondary_contact", contact.secondary_contact
            )
            contact.remarks = validated_data.get("remarks", contact.remarks)
            contact.picture = validated_data.get("picture", contact.picture)
            contact.save()

            return ResponseService.response(
                "SUCCESS",
                None,
                # {
                #     "id": contact.id,
                #     "name": contact.name,
                #     "email": contact.email,
                #     "address": contact.address,
                #     "primary_contact": contact.primary_contact,
                #     "secondary_contact": contact.secondary_contact,
                #     "remarks": contact.remarks,
                #     "picture": contact.picture,
                # },
                "default_update_success_msg",
            )

        elif request.method == "DELETE":
            # Comprehensive checks for contact usage in other tables
            usage_errors = []
            
            # Check if contact is used as primary_contact in Customer
            if Customer.objects.filter(primary_contact=contact).exists():
                usage_errors.append("primary contact for customers")
            
            # Check if contact is used in CustomerAdditionalContact
            if hasattr(contact, 'customer_contacts') and contact.customer_contacts.exists():
                usage_errors.append("additional contact for customers")
            
            # Check if contact is used in GroupContact
            if GroupContact.objects.filter(contact=contact).exists():
                usage_errors.append("contact groups")
            
            # Check if contact is used in Intraction
            if Intraction.objects.filter(contact=contact).exists():
                usage_errors.append("interactions")
            
            # Check if contact is duplicated_contact for other contacts
            if hasattr(contact, 'duplicates') and contact.duplicates.exists():
                usage_errors.append("as duplicated contact for other contacts")
            
            # If contact is used anywhere, return error
            if usage_errors:
                return ResponseService.response(
                    "CONFLICT",
                    [],
                    "contact_delete_conflict_msg",
                )

            contact.delete()
            return ResponseService.response(
                "SUCCESS",
                message="default_delete_success_msg",
                result=None,
            )


    except Contact.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", f"Contact with id {id} does not exist", "Not Found"
        )
    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )


# Handles GET contacts/<int:contact_id>/interactions
@api_view(["GET"])
def get_contact_interactions(request, contact_id):
    try:

        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="Contact not found.",
                result="Contact not found.",
            )

        # interactions = ContactInteraction.objects.filter(
        #     contact=contact
        # ).select_related("channel", "sales_status", "contact_by")

        # total_records = interactions.count()

        # data = [
        #     {
        #         "id": interaction.id,
        #         "notes": interaction.notes,
        #         "channel": interaction.channel.name if interaction.channel else None,
        #         "contact_by": (
        #             interaction.contact_by.first_name
        #             if interaction.contact_by
        #             else None
        #         ),
        #         "sales_status": (
        #             interaction.sales_status.name if interaction.sales_status else None
        #         ),
        #         "sales_status_type": (
        #             interaction.sales_status.type if interaction.sales_status else None
        #         ),
        #         "contact_name": (
        #             interaction.contact.name if interaction.contact else None
        #         ),
        #     }
        #     for interaction in interactions
        # ]

      # --------------------QueryBuilderService--------------------------------

        all_columns = [
            "core_intractions.*",
            "core_channels.name as channel_name",
            "core_users.display_name as contact_by_name",
            "core_contacts.name as contact_name", 
            "oppo.title as opportunity_title",
            "oppo.type as opportunity_type",
            "oppo_status.name as opportunity_status_name",
            "oppo_status.type as opportunity_status_type",
            "oppo_status.color as opportunity_status_color",
        ]

        query = (QueryBuilderService("core_intractions")
                 .select(*all_columns)
                 .leftJoin("core_channels", "core_channels.id", "core_intractions.channel_id")
                 .leftJoin("core_contacts", "core_contacts.id", "core_intractions.contact_id")
                 .leftJoin("core_users", "core_users.id", "core_intractions.contact_by_id")
                 .leftJoin("crm_opportunities as oppo", "oppo.id", "core_intractions.opportunity_id")
                 .leftJoin("crm_opportunity_statuses as oppo_status", "oppo_status.id", "core_intractions.opportunity_status_id")
                 .where("core_intractions.contact_id", contact_id)
                 .get()
                 )
        
        print ("query",query)

        # response_data = {
        #     # "total": total_records,
        #     "data": query,
        # }

        return ResponseService.response(
            "SUCCESS",
            message="Contact interactions fetched successfully.",
            result=query,
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR",
            message="Error fetching contact interactions.",
            result=str(e),
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            message="Server Error",
            result={"error": str(e)},
        )


# Handles GET contacts/<int:contact_id>/interactions/<int:interaction_id>
@api_view(["GET"])
def get_contact_interaction(request, contact_id, interaction_id):
    try:
        try:
            contact = Contact.objects.get(id=contact_id)
        except Contact.DoesNotExist:
            return ResponseService.response(
                "VALIDATION_ERROR", message="Contact not found."
            )

        # Build query with JOINs and filters
        all_columns = [
            "core_intractions.*",
            "core_channels.name as channel_name",
            "core_users.display_name as contact_by_name",
            "core_contacts.name as contact_name",
            "oppo.title as opportunity_title",
            "oppo.type as opportunity_type",
            "oppo_status.name as opportunity_status_name",
            "oppo_status.type as opportunity_status_type",
            "oppo_status.color as opportunity_status_color",
        ]

        query = (
            QueryBuilderService("core_intractions")
            .select(*all_columns)
            .leftJoin("core_channels", "core_channels.id", "core_intractions.channel_id")
            .leftJoin("core_contacts", "core_contacts.id", "core_intractions.contact_id")
            .leftJoin("core_users", "core_users.id", "core_intractions.contact_by_id")
            .leftJoin("crm_opportunities as oppo", "oppo.id", "core_intractions.opportunity_id")
            .leftJoin("crm_opportunity_statuses as oppo_status", "oppo_status.id", "core_intractions.opportunity_status_id")
            .where("core_intractions.contact_id", contact_id)
            .where("core_intractions.id", interaction_id)
            .first()
        )

        if not query:
            return ResponseService.response(
                "VALIDATION_ERROR", message="Interaction not found for this contact."
            )

        return ResponseService.response(
            "SUCCESS", message="Contact interaction fetched successfully.", result=query
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", message="Validation error.", result=str(e)
        )
    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", message="Server Error", result={"error": str(e)}
        )


@api_view(["GET"])
def get_contact_ids(request):
    ids = request.GET.get("ids", "")

    if not ids:
        return ResponseService.response(
            "VALIDATION_ERROR",
            message="No IDs provided. Please provide a comma-separated list of IDs.",
        )

    ids_list = ids.split(",")

    try:
        ids_list = [int(id) for id in ids_list]
    except ValueError:
        return ResponseService.response(
            "VALIDATION_ERROR",
            message="Invalid IDs format. Please provide a comma-separated list of valid integer IDs.",
        )

    # Fetch direct matches
    direct_contacts = Contact.objects.filter(id__in=ids_list)

    if not direct_contacts.exists():
        return ResponseService.response(
            "VALIDATION_ERROR",
            message="No contacts found for the provided IDs.",
        )

    valid_ids = list(direct_contacts.values_list("id", flat=True))
    invalid_ids = set(ids_list) - set(valid_ids)

    if invalid_ids:
        return ResponseService.response(
            "VALIDATION_ERROR",
            message=f"Invalid IDs: {', '.join(map(str, invalid_ids))}.",
        )

    result = set(direct_contacts)

    # Include any contacts where duplicated_contact_id is in the given list
    merged_contacts = Contact.objects.filter(duplicated_contact_id__in=valid_ids)
    result.update(merged_contacts)

    contacts_data = [
        {
            "id": contact.id,
            "name": contact.name,
            "email": contact.email,
            "primary_contact": contact.primary_contact,
            "secondary_contact": contact.secondary_contact,
            "remarks": contact.remarks,
            "picture": contact.picture,
        }
        for contact in result
    ]

    return ResponseService.response(
        "SUCCESS",
        message="Contacts fetched successfully.",
        result=contacts_data,
    )

@api_view(["POST","DELETE"])
def merge_contact_api(request):

    if request.method == 'POST':
        return merge_contacts(request)
    
    elif request.method == 'DELETE':
        return unmerge_contact(request)
 



def merge_contacts(request):
    try:
        data = json.loads(request.body)

        rules = {
            "contact_ids": "required|array",
            "primary_contact_id": "required|integer",
        }

        custom_messages = {
            "contact_ids.required": "Contact IDs are required.",
            "contact_ids.array": "Contact IDs must be a list of integers.",
            "primary_contact_id.required": "Primary contact ID is required.",
            "primary_contact_id.integer": "Primary contact ID must be an integer.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        contact_ids = set(data.get("contact_ids", []))
        primary_contact_id = data["primary_contact_id"]

        # Ensure the primary contact ID is in the provided list
        contact_ids.add(primary_contact_id)

        # Get all contacts whose ID is in the list or whose duplicated_contact_id is in the list
        related_contacts = Contact.objects.filter(
            Q(id__in=contact_ids) | Q(duplicated_contact_id__in=contact_ids)
        )

        if not related_contacts.exists():
            return ResponseService.response(
                "VALIDATION_ERROR",
                message="No related contacts found.",
            )

        # Extract IDs to update (excluding the primary contact itself)
        ids_to_update = list(
            related_contacts.exclude(id=primary_contact_id).values_list("id", flat=True)
        )

        # Perform update
        Contact.objects.filter(id__in=ids_to_update).update(
            duplicated_contact_id=primary_contact_id
        )

        # Ensure the primary contact itself is not marked as duplicate
        Contact.objects.filter(id=primary_contact_id).update(duplicated_contact_id=None)

        return ResponseService.response(
            "SUCCESS",
            message="contacts_merged_successfully",
            result={"primary_contact_id": primary_contact_id},
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred while merging contacts.",
            result={"error": str(e)},
        )
    


def unmerge_contact(request):
    try:
        data = json.loads(request.body)
        contact_id = data.get("contact_id")

        if not contact_id:
            return ResponseService.response(
                "VALIDATION_ERROR",
                "contact_id is required."
            )

        contact = Contact.objects.filter(id=contact_id).first()
        if not contact:
            return ResponseService.response(
                "NOT_FOUND",
                f"Contact with ID {contact_id} not found."
            )

        contact.duplicated_contact_id = None
        contact.save()

        return ResponseService.response(
            "SUCCESS",
            message="contact_unmerged_successfully",
            result={"contact_id": contact_id}
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR",
            message="Server Error",
            result={"error": str(e)}
        )



@api_view(["GET"])
def get_contact_relations(request, id):
    try:
        contact = Contact.objects.get(id=id)
        
        related_accounts = Customer.objects.filter(primary_contact_id=contact).values("id", "name")

        
        related_group_ids = GroupContact.objects.filter(contact=contact).values_list("group_id", flat=True)
        related_groups = ContactGroup.objects.filter(id__in=related_group_ids).values("id", "name")

       
        related_contacts = Contact.objects.filter(duplicated_contact_id=contact)

        response_data = {
            "id": contact.id,
            "name": contact.name,
            "email": contact.email,
            "primary_contact": contact.primary_contact,
            "data": list(
                    related_contacts.values(
                        "id",
                        "name",
                        "email",
                        "primary_contact",
                        "secondary_contact",
                        "remarks",
                        "picture",
                    )
                ),
            
        }

        return ResponseService.response(
            "SUCCESS", response_data, "Contact relations retrieved successfully!"
        )

    except Contact.DoesNotExist:
        return ResponseService.response(
            "NOT_FOUND", None, f"Contact with ID {id} does not exist"
        )

    except ValidationError as e:
        return ResponseService.response(
            "VALIDATION_ERROR", e.message_dict, "Validation Error"
        )

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )
