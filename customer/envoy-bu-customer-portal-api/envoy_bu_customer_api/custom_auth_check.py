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

        # Extract all customer fields from the token
        user_data = {
            "id": validated_token.get("customer_id"),
            "name": validated_token.get("name"),
            "email": validated_token.get("email"),
            "idp_customer_id": validated_token.get("idp_customer_id"),
            "type": validated_token.get("type"),
            "code": validated_token.get("code"),
        }

        if not user_data["id"]:
            raise AuthenticationFailed("Customer ID not found in token.")

        return (user_data, validated_token)