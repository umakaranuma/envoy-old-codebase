import requests
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import logging

# Initialize Logger
logger = logging.getLogger(__name__)

EXTERNAL_API_URL = settings.EXTERNAL_API_URL


@api_view(["POST"])
def authenticate_user(request):
    try:
        data = request.data
        user_token = data.get("idp_access_token")

        if not user_token:
            return Response(
                {"error": "idp_access_token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {"Authorization": f"Bearer {user_token}"}
        response = requests.get(EXTERNAL_API_URL, headers=headers)

        if response.status_code != 200:
            logger.error(f"External API Error: {response.status_code} - {response.text}")
            return Response(
                {"error": "Invalid Credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Validate User (Assuming request.user is already authenticated)
        if not request.user.is_authenticated:
            return Response(
                {"error": "User authentication failed."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(request.user)
        access_token = refresh.access_token

        return Response(
            {
                "message": "Login successful",
                "access_token": str(access_token),
            },
            status=status.HTTP_200_OK,
        )

    except requests.RequestException as e:
        logger.error(f"External API Request Failed: {str(e)}")
        return Response(
            {"error": "Failed to connect to external authentication service."},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return Response(
            {"error": "Something went wrong. Please try again later."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
