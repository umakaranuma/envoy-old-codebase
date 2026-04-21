
import mServices.QueryBuilderService as QueryBuilderService

class EntityService:
    """Service for managing entity-related operations"""
    
    @staticmethod
    def store_entity(entity, request):
        """ Store an Entity with Authenticated User as Created By and Updated By """

        user = request.user if request.user.is_authenticated else None

        if not user:
            return None  # Prevent storing without an authenticated user

        data = {
            "type": entity,
            "created_by_id": user.id,  # Assign the authenticated user's ID
            "updated_by_id": user.id,  # Same user for both at creation
            "approvel_status": False,
        }

        new_data = QueryBuilderService("core_entities").insert(data)
        return new_data

    

    @staticmethod
    def get_entity_with_notes_and_docs(entity_id):
        """Retrieve entity details along with its notes and documents"""
        
        entity = (
        QueryBuilderService("core_entities as e")
        .leftJoin("core_users as created_by", "created_by.id", "e.created_by_id")  # Left Join for Created By
        .leftJoin("core_users as updated_by", "updated_by.id", "e.updated_by_id")  # Left Join for Updated By
        .select(
            "e.*",
            "created_by.display_name AS created_by_name",
            "created_by.picture AS created_by_profile",
            "updated_by.display_name AS updated_by_name",
            "updated_by.picture AS updated_by_profile"
        )
        .where("e.id", entity_id)
        .first()
    )


        if not entity:
            return None  # Return None if the entity does not exist

        # Fetch Notes
        notes = (
            QueryBuilderService("core_entity_notes")
            .select("*")
            .where("entity_id", entity_id)
            .get()
        )

        # Fetch Documents
        documents = (
            QueryBuilderService("core_entity_docs")
            .select("*")
            .where("entity_id", entity_id)
            .get()
        )

        # Return the formatted entity data
        return {
            "id": entity["id"],
            "type": entity["type"],
            "created_by_id": entity["created_by_id"],
            "created_by_name": entity["created_by_name"],
            "created_by_profile": entity["created_by_profile"],
            "updated_by_id": entity["updated_by_id"],
            "updated_by_name": entity["updated_by_name"],
            "updated_by_profile": entity["updated_by_profile"],
            "created_at": entity["created_at"],
            "notes": notes if notes else [],
            "documents": documents if documents else []
        }
