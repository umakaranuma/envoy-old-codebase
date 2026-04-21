from rest_framework_simplejwt.authentication import JWTAuthentication
from envoy.models.user import User

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Override the default method to avoid checking `is_active`.
        """
        user_id = validated_token.get("user_id")

        if not user_id:
            return None

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

        return user
