from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken

from core_models.core_models import User


class UserProxy:
    """ A simple proxy user object to provide required attributes like `is_authenticated`. """
    def __init__(self, user_data):
        self.id = user_data.get("id")
        self.email = user_data.get("email")
        self.role = user_data.get("role")

    @property
    def is_authenticated(self):
        return True  # All JWT-authenticated users should be considered authenticated.

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except (AuthenticationFailed, InvalidToken) as e:
            raise AuthenticationFailed({"message": "Invalid authentication token.", "error": str(e)})

        user_id = validated_token.get("user_id")
        user = User.objects.select_related("role").filter(id=user_id).first()

        if not user:
            raise AuthenticationFailed("User not found.")

        return (user, validated_token)