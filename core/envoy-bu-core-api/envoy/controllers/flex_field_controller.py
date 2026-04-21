from rest_framework.decorators import api_view
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from mServices.QueryBuilderService import QueryBuilderService

@api_view(["GET"])
def get_flex_fields_by_entity(request, entity):
    """
    Retrieve all flex fields for the given entity type.
    Example: GET /flex-fields/config/CUSTOMER
    """
    try:
        return fetch_flex_fields(request, entity)

    except Exception as e:
        return ResponseService.response(
            "INTERNAL_SERVER_ERROR", {"error": str(e)}, "Server Error"
        )


def fetch_flex_fields(request, entity):
    """
    Handles retrieving all flex fields for the given entity.
    """
    # Validation Rule: Ensure 'entity' is not empty and exists in the DB
    rules = {"entity": "required|exists:core_flex_fields,entity_type"}
    errors = ValidatorService.validate({"entity": entity}, rules)

    if errors:
        return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")

    # Check if the entity exists in the database
    flex_fields = QueryBuilderService("core_flex_fields") \
        .select("id", "field_code", "field_label", "data_type", "default_value", "is_mandatory", "is_enabled", "is_fixed") \
        .where("entity_type", entity) \
        .get()

    return ResponseService.response(
        "SUCCESS", flex_fields, "Flex fields fetched successfully."
    )
