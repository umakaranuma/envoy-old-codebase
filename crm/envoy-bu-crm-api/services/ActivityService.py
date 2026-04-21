


from envoy_bu_crm_api.sales.models.core_models import Entity, EntityActivity


class ActivityService:
    @staticmethod
    def store_activity(request, entity_id, activity):
        """
        Store an activity entry linked to an entity.

        Parameters:
            request: The DRF request object (to extract logged-in user)
            entity_id (int): ID of the entity to associate the activity with
            activity (str): The activity description

        Returns:
            EntityActivity instance if created successfully, else None
        """
        entity = Entity.objects.filter(id=entity_id).first()
        if not entity:
            return None

        user = request.user if request.user.is_authenticated else None

        return EntityActivity.objects.create(
            entity_id=entity.id,
            activity=activity,
            added_by_id=user.id  # 'added_at' is automatically filled
        )
