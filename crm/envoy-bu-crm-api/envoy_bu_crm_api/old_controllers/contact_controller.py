# from django.http import JsonResponse
# from rest_framework.decorators import api_view
# import json
# from envoy_bu_crm_api.models.contact import Contact
# from envoy_bu_crm_api.models.contact_interaction import ContactInteraction
# import mServices.ResponseService as ResponseService
# from mServices.ValidatorService import ValidatorService
# from django.core.exceptions import ValidationError
# from django.core.paginator import Paginator

# # GET
# # /contacts - List All Contacts or POST
# # /contacts - Create a New Contact
# @api_view(["GET", "POST"])
# def get_contacts(request):
#     if request.method == "GET":
#         try:
#             page = int(request.GET.get("page", 1))
#             per_page = int(request.GET.get("per_page", 10))

#             contacts = Contact.objects.all()
#             paginator = Paginator(contacts, per_page)

#             page_contacts = paginator.get_page(page)

#             data = [
#                 {
#                     "id": contact.id,
#                     "title": contact.title,
#                     "name": contact.name,
#                     "email": contact.email,
#                     "address": contact.address,
#                     "primary_contact": contact.primary_contact,
#                     "secondary_contact": contact.secondary_contact,
#                     "remarks": contact.remarks,
#                     "picture": contact.picture,
#                 }
#                 for contact in page_contacts
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
#             "name": "required|min:3|max:50",
#             "email": "required|email",
#             "primary_contact": "required",
#         }

#         custom_messages = {
#             "name.required": "Name cannot be empty.",
#             "email.required": "Email cannot be empty.",
#             "primary_contact.required": "Primary contact cannot be empty.",
#         }

#         try:
#             validator = ValidatorService(data, rules, custom_messages)
#             validator.validate()
#             validated_data = data
#             # validator.get_validated_data()

#             contact = Contact.objects.create(
#                 title=validated_data.get("title", ""),
#                 name=validated_data["name"],
#                 email=validated_data["email"],
#                 address=validated_data.get("address", ""),
#                 primary_contact=validated_data["primary_contact"],
#                 secondary_contact=validated_data.get("secondary_contact", ""),
#                 remarks=validated_data.get("remarks", ""),
#                 picture=validated_data.get("picture", ""),
#             )

#             return JsonResponse(
#                 {
#                     "message": "Contact created successfully!",
#                     "data": {
#                         "id": contact.id,
#                         "title": contact.title,
#                         "name": contact.name,
#                         "email": contact.email,
#                         "address": contact.address,
#                         "primary_contact": contact.primary_contact,
#                         "secondary_contact": contact.secondary_contact,
#                         "remarks": contact.remarks,
#                         "picture": contact.picture,
#                     },
#                 }
#             )
#         except ValidationError as e:
#             return ResponseService.response(
#                 "VALIDATION_ERROR", e.message_dict, "Validation Error"
#             )


# # Handles GET, PUT, DELETE requests for a single contact by ID
# @api_view(["GET", "PUT", "DELETE"])
# def contact_detail(request, id):
#     try:
#         contact = Contact.objects.get(id=id)

#         if request.method == "GET":
#             data = {
#                 "id": contact.id,
#                 "title": contact.title,
#                 "name": contact.name,
#                 "email": contact.email,
#                 "address": contact.address,
#                 "primary_contact": contact.primary_contact,
#                 "secondary_contact": contact.secondary_contact,
#                 "remarks": contact.remarks,
#                 "picture": contact.picture,
#             }
#             return JsonResponse({"data": data})

#         elif request.method == "PUT":
#             data = json.loads(request.body)

#             rules = {
#                 "name": "required|min:3|max:50",
#                 "email": "required|email",
#                 "primary_contact": "required",
#             }

#             custom_messages = {
#                 "name.required": "Name cannot be empty.",
#                 "email.required": "Email cannot be empty.",
#                 "primary_contact.required": "Primary contact cannot be empty.",
#             }

#             validator = ValidatorService(data, rules, custom_messages)
#             validator.validate()
#             # validated_data = validator.get_validated_data()
#             validated_data = data

#             contact.title = validated_data.get("title", contact.title)
#             contact.name = validated_data["name"]
#             contact.email = validated_data["email"]
#             contact.address = validated_data.get("address", contact.address)
#             contact.primary_contact = validated_data["primary_contact"]
#             contact.secondary_contact = validated_data.get(
#                 "secondary_contact", contact.secondary_contact
#             )
#             contact.remarks = validated_data.get("remarks", contact.remarks)
#             contact.picture = validated_data.get("picture", contact.picture)
#             contact.save()

#             return JsonResponse(
#                 {
#                     "message": "Contact updated successfully!",
#                     "data": {
#                         "id": contact.id,
#                         "title": contact.title,
#                         "name": contact.name,
#                         "email": contact.email,
#                         "address": contact.address,
#                         "primary_contact": contact.primary_contact,
#                         "secondary_contact": contact.secondary_contact,
#                         "remarks": contact.remarks,
#                         "picture": contact.picture,
#                     },
#                 }
#             )

#         elif request.method == "DELETE":
#             contact.delete()
#             return JsonResponse(
#                 {"message": f"Contact with id {id} deleted successfully!"}
#             )

#     except Contact.DoesNotExist:
#         return ResponseService.response(
#             "NOT_FOUND", f"Contact with id {id} does not exist", "Not Found"
#         )
#     except ValidationError as e:
#         return ResponseService.response(
#             "VALIDATION_ERROR", e.message_dict, "Validation Error"
#         )


# # Handles GET contacts/<int:contact_id>/interactions
# @api_view(["GET"])
# def get_contact_interactions(request, contact_id):
#     try:
#         page = int(request.GET.get("page", 1))
#         per_page = int(request.GET.get("per_page", 10))

#         try:
#             contact = Contact.objects.get(id=contact_id)
#         except Contact.DoesNotExist:
#             return JsonResponse(
#                 {"error": "CONTACT_NOT_FOUND", "message": "Contact not found."},
#                 status=404,
#             )

#         interactions = ContactInteraction.objects.filter(
#             contact=contact
#         ).select_related("channel", "sales_status", "contact_by")
#         paginator = Paginator(interactions, per_page)

#         page_interactions = paginator.get_page(page)

#         data = [
#             {
#                 "id": interaction.id,
#                 "notes": interaction.notes,
#                 "channel": interaction.channel.name if interaction.channel else None,
#                 "contact_by": (
#                     interaction.contact_by.username if interaction.contact_by else None
#                 ),
#                 "sales_status": (
#                     interaction.sales_status.name if interaction.sales_status else None
#                 ),
#                 "sales_status_type": (
#                     interaction.sales_status.type if interaction.sales_status else None
#                 ),
#                 "contact_name": (
#                     interaction.contact.name if interaction.contact else None
#                 ),
#             }
#             for interaction in page_interactions
#         ]

#         return JsonResponse(
#             {
#                 "page": page,
#                 "total_pages": paginator.num_pages,
#                 "total_count": paginator.count,
#                 "data": data,
#             },
#             safe=False,
#         )

#     except ValidationError as e:
#         return JsonResponse(
#             {
#                 "error": "VALIDATION_ERROR",
#                 "message": e.message_dict,
#                 "details": "Validation Error",
#             },
#             status=400,
#         )


# # Handles GET contacts/<int:contact_id>/interactions/<int:interaction_id>
# @api_view(["GET"])
# def get_contact_interaction(request, contact_id, interaction_id):
#     try:
#         try:
#             contact = Contact.objects.get(id=contact_id)
#         except Contact.DoesNotExist:
#             return JsonResponse(
#                 {"error": "CONTACT_NOT_FOUND", "message": "Contact not found."},
#                 status=404,
#             )

#         try:
#             interaction = ContactInteraction.objects.get(
#                 contact=contact, id=interaction_id
#             )
#         except ContactInteraction.DoesNotExist:
#             return JsonResponse(
#                 {
#                     "error": "INTERACTION_NOT_FOUND",
#                     "message": "Interaction not found for this contact.",
#                 },
#                 status=404,
#             )

#         data = {
#             "id": interaction.id,
#             "notes": interaction.notes,
#             "channel": interaction.channel.name if interaction.channel else None,
#             "contact_by": (
#                 interaction.contact_by.username if interaction.contact_by else None
#             ),
#             "sales_status": (
#                 interaction.sales_status.name if interaction.sales_status else None
#             ),
#             "sales_status_type": (
#                 interaction.sales_status.type if interaction.sales_status else None
#             ),
#             "contact_name": interaction.contact.name if interaction.contact else None,
#         }

#         return JsonResponse(data)

#     except ValidationError as e:
#         return JsonResponse(
#             {
#                 "error": "VALIDATION_ERROR",
#                 "message": e.message_dict,
#                 "details": "Validation Error",
#             },
#             status=400,
#         )
