from rest_framework.decorators import api_view
from envoy.models.entity_note import EntityNote
from envoy.models.entity import Entity
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService
import json


@api_view(["GET","POST"])
def entity_notes(request,id):
    if request.method == "GET":
        return get_entity_notes(request, id)
    elif request.method =="POST":
        return create_entity_note(request,id)

def get_entity_notes(request, id):
    """Retrieve all notes for a given entity with search, filter, sort, and pagination"""
    try:
        entity_exists = Entity.objects.filter(id=id).exists()
        if not entity_exists:
            return ResponseService.response("NOT_FOUND", None, "Entity not found")

        # Define request parameters
        filter_json = request.GET.get("filters", '{}')
        search_string = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        limit = int(request.GET.get("limit", 10))
        sort_by = request.GET.get("sort_by", "notes.id")
        sort_dir = request.GET.get("sort_dir", "desc")
        # Normalize empty values to defaults
        sort_by = "notes.id" if sort_by in [None, ""] else sort_by
        sort_dir = "desc" if sort_dir in [None, ""] else sort_dir

        allowed_filters = ["added_by_id"]
        search_columns = ["notes.notes", "core_users.display_name","notes.added_at"]
        allowed_sorting_columns = ["notes.id", "notes.added_on", "core_users.display_name"]

        # Build query using QueryBuilderService
        data = (
            QueryBuilderService("core_entity_notes as notes")
            .leftJoin("core_users", "core_users.id", "notes.added_by_id")
            .select(
                "notes.*",
                "core_users.display_name as added_by_name",
                "core_users.picture as added_by_picture"
            )
            .where("notes.entity_id", id)
            .apply_conditions(filter_json, allowed_filters, search_string, search_columns)
            .paginate(page, limit, allowed_sorting_columns, sort_by, sort_dir)
        )

        return ResponseService.response("SUCCESS", data, "Entity notes fetched successfully!")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



def create_entity_note(request, id):
    """Create a note for an entity"""
    try:
        entity = Entity.objects.filter(id=id).first()
        if not entity:
            return ResponseService.response("NOT_FOUND", None, "Entity not found")

        data = json.loads(request.body)

        # Validation rules
        rules = {
            "is_high_priority": "boolean",
            "notes": "required",
        }
        custom_messages = {
            "notes.required": "Notes cannot be empty.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Create the entity note
        note = EntityNote.objects.create(
            entity=entity,
            is_high_priority=data.get("is_high_priority", False),
            notes=data.get("notes", ""),
            added_by=request.user if request.user.is_authenticated else None,
        )

        return ResponseService.response(
            "SUCCESS", {"id": note.id}, "default_create_success_msg"
        )

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET","PUT","DELETE"])
def entity_note_detail(request, id, notes_id):
    if request.method == "GET":
        return get_entity_note_detail(request, id, notes_id)
    elif request.method == "PUT":
        return update_entity_note(request, id, notes_id)
    elif request.method == "DELETE":
        return delete_entity_note(request, id, notes_id)
    
    
def get_entity_note_detail(request, id, notes_id):
    """Retrieve a single note for an entity"""
    try:
        note = (
            QueryBuilderService("core_entity_notes")
            .select("id", "is_high_priority", "notes")
            .where("id", notes_id)
            .where("entity_id", id)
            .first()
        )

        if not note:
            return ResponseService.response("NOT_FOUND", None, "Note not found")

        return ResponseService.response("SUCCESS", note, "Note details fetched successfully!")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



def update_entity_note(request, id, notes_id):
    """Update an existing note"""
    try:
        note = EntityNote.objects.filter(id=notes_id, entity_id=id).first()
        if not note:
            return ResponseService.response("NOT_FOUND", None, "Note not found")

        data = json.loads(request.body)

        # Validation rules
        rules = {
            "is_high_priority": "boolean",
            "notes": "required",
        }
        custom_messages = {
            "notes.required": "Notes cannot be empty.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        note.is_high_priority = data.get("is_high_priority", note.is_high_priority)
        note.notes = data.get("notes", note.notes)
        note.save()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")



def delete_entity_note(request, id, notes_id):
    """Delete a note"""
    try:
        note = EntityNote.objects.filter(id=notes_id, entity_id=id).first()
        if not note:
            return ResponseService.response("NOT_FOUND", None, "Note not found")

        note.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
