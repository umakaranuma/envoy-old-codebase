import json
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from envoy.models.entity import Entity
from envoy.models.entity_document import EntityDocument
import mServices.ResponseService as ResponseService
import mServices.QueryBuilderService as QueryBuilderService
import mServices.ValidatorService as ValidatorService


@api_view(["GET", "POST"])
def entity_documents(request, id):
    """Handle GET (List all) and POST (Create) operations for Entity Documents"""
    if request.method == "GET":
        return get_entity_documents(request, id)
    elif request.method == "POST":
        return create_entity_document(request, id)


def get_entity_documents(request, id):
    """Retrieve all documents for a given entity"""
    try:
        entity_exists = Entity.objects.filter(id=id).exists()
        if not entity_exists:
            return ResponseService.response("NOT_FOUND", None, "Entity not found")

        # Fetch documents using QueryBuilderService
        documents = (
            QueryBuilderService("core_entity_docs")
            .select("*")
            .where("entity_id", id)
            .get()
        )

        return ResponseService.response("SUCCESS", documents, "Entity documents fetched successfully!")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def create_entity_document(request, id):
    """Create a document for an entity"""
    try:
        entity = Entity.objects.filter(id=id).first()
        if not entity:
            return ResponseService.response("NOT_FOUND", None, "Entity not found")

        data = json.loads(request.body)

        # Validation rules
        rules = {
            "doc": "required",
            "name":"required",
            "type":"required",
        }
        custom_messages = {
            "doc.required": "Document content cannot be empty.",
            "name.required":"Name field cannot be empty",
            "type.required": "type field cannot be empty",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        # Create the entity document
        document = EntityDocument.objects.create(
            entity = entity,
            doc = data.get("doc", ""),
            name = data.get("name",""),
            type = data.get("type",""),
        )

        return ResponseService.response(
            "SUCCESS",
            {
                "id": document.id,
                "doc": document.doc,
                "name": document.name,
                "type": document.type,
                "entity_id": document.entity.id,
            },
            "default_create_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


@api_view(["GET", "PUT", "DELETE"])
def entity_document_detail(request, id, doc_id):
    """Handle GET, PUT, and DELETE operations for Entity Documents"""
    if request.method == "GET":
        return get_entity_document_detail(request, id, doc_id)
    elif request.method == "PUT":
        return update_entity_document(request, id, doc_id)
    elif request.method == "DELETE":
        return delete_entity_document(request, id, doc_id)


def get_entity_document_detail(request, id, doc_id):
    """Retrieve a single document for an entity"""
    try:
        document = (
            QueryBuilderService("core_entity_docs")
            .select("id", "doc")
            .where("id", doc_id)
            .where("entity_id", id)
            .first()
        )

        if not document:
            return ResponseService.response("NOT_FOUND", None, "Document not found")

        return ResponseService.response("SUCCESS", document, "Document details fetched successfully!")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def update_entity_document(request, id, doc_id):
    """Update an existing document"""
    try:
        document = EntityDocument.objects.filter(id=doc_id, entity_id=id).first()
        if not document:
            return ResponseService.response("NOT_FOUND", None, "Document not found")

        data = json.loads(request.body)

        # Validation rules
        rules = {
            "doc": "required",
        }
        custom_messages = {
            "doc.required": "Document content cannot be empty.",
        }

        errors = ValidatorService.validate(data, rules, custom_messages)
        if errors:
            return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

        document.doc = data.get("doc", document.doc)
        document.save()

        return ResponseService.response("SUCCESS", None, "default_update_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")


def delete_entity_document(request, id, doc_id):
    """Delete a document"""
    try:
        document = EntityDocument.objects.filter(id=doc_id, entity_id=id).first()
        if not document:
            return ResponseService.response("NOT_FOUND", None, "Document not found")

        document.delete()
        return ResponseService.response("SUCCESS", None, "default_delete_success_msg")

    except Exception as e:
        return ResponseService.response("INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error")
