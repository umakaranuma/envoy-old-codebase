from django.db import transaction
from envoy.models.entity import Entity
from envoy.models.flex_field import FlexField
from envoy.models.flex_value import FlexValue

class EntityService:

    @staticmethod
    @transaction.atomic
    def store(action, data=None, user=None):
        entity_type = action.get("entity")
        if not entity_type:
            raise ValueError("Entity type is required")

        # Create the entity
        entity = Entity.objects.create(
            type=entity_type,
            created_by=user,
            updated_by=user
        )

        # Store flex field values
        EntityService.store_flex_field_value(action, entity, data or {})

        return entity

    @staticmethod
    @transaction.atomic
    def update(action, entity_id, data=None, user=None):
        try:
            entity = Entity.objects.get(id=entity_id)
        except Entity.DoesNotExist:
            return None

        # Update the 'updated_by' field
        entity.updated_by = user
        entity.save()

        # Update flex values
        EntityService.update_flex_field_value(action, entity, data or {})

        return entity

    # @staticmethod
    # def store_flex_field_value(action, entity, data):
    #     entity_type = action.get("entity")
    #     if not entity_type:
    #         raise ValueError("Entity type is required in action")

    #     # Delete existing flex values
    #     FlexValue.objects.filter(entity=entity).delete()

    #     # Get enabled flex fields
    #     flex_fields = FlexField.objects.filter(entity_type=entity_type, is_enabled=True)

    #     flex_data = {}

    #     for field in flex_fields:
    #         code = field.field_code
    #         field_id = str(field.id)

    #         if code in data and data[code] not in [None, ""]:
    #             flex_data[field_id] = data[code]

    #         elif field.is_mandatory:
    #             raise ValueError(f"{field.field_label or code} is required.")

    #     # Only store if there's valid flex data
    #     if flex_data:
    #         FlexValue.objects.create(
    #             entity=entity,
    #             flex_values=flex_data
    #         )
    @staticmethod
    def store_flex_field_value(action, entity, data):
        entity_type = action.get("entity")
        if not entity_type:
            raise ValueError("Entity type is required in action")

        # Delete existing flex values for entity
        FlexValue.objects.filter(entity=entity).delete()

        flex_fields = FlexField.objects.filter(entity_type=entity_type, is_enabled=True)
        flex_field_map = {str(field.id): field for field in flex_fields}

        valid_flex_data = {}

        for field_id, value in data.items():
            field = flex_field_map.get(str(field_id))
            if not field:
                continue  # Skip unknown fields

            if value in [None, ""] and field.is_mandatory:
                raise ValueError(f"{field.field_label or field.field_code} is required.")

            # Store the value even if it's an empty string
            valid_flex_data[str(field_id)] = value

        # Ensure flex_values is not null
        FlexValue.objects.create(
            entity=entity,
            flex_values=valid_flex_data
        )


    @staticmethod
    def update_flex_field_value(action, entity, data):
        entity_type = action.get("entity")
        if not entity_type:
            raise ValueError("Entity type is required in action")

        flex_fields = FlexField.objects.filter(entity_type=entity_type, is_enabled=True)
        flex_field_map = {str(field.id): field for field in flex_fields}

        valid_flex_data = {}

        for field_id, field in flex_field_map.items():
            input_value = data.get(str(field_id))

            # Validation for required fields
            if input_value in [None, ""] and field.is_mandatory:
                raise ValueError(f"{field.field_label or field.field_code} is required.")

            # Store the value even if it's an empty string
            valid_flex_data[str(field_id)] = input_value

        # Ensure flex_values is not null
        flex_value_obj, created = FlexValue.objects.get_or_create(entity=entity)
        flex_value_obj.flex_values = valid_flex_data
        flex_value_obj.save()
