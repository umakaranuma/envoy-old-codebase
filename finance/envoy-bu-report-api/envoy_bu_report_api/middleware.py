
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import InvalidToken
from django.urls import resolve, Resolver404
from mServices.ResponseService import ResponseService

from envoy_bu_report_api.custom_auth_check import CustomJWTAuthentication

# from mServices.ValidatorService import ValidatorService 

class MainAppJWTAuthMiddleware:
    """
    Middleware to enforce authentication using JWT tokens issued by the main application.
    """

    PUBLIC_ENDPOINTS = [
        # Define endpoints that do not require authentication
          
    ]

    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = CustomJWTAuthentication()  #  Use CustomJWTAuthentication

    def __call__(self, request):
        try:
            setattr(request, "_dont_enforce_csrf_checks", True)  #  Disable CSRF for APIs

            #  Validate the requested endpoint
            try:
                resolved_path = resolve(request.path_info).route  #  Get the resolved path
            except Resolver404:
                return ResponseService.response(
                    "NOT_FOUND",
                    {"endpoint": ["Invalid API endpoint. Please check the URL."]},
                    "NOT FOUND"
                )

            #  Allow public endpoints without authentication
            if resolved_path in self.PUBLIC_ENDPOINTS:
                return self.get_response(request)

            #  Authenticate using JWT token
            try:
                # print(f"Attempting authentication for path: {request.path_info}")
                # print(f"Authorization header: {request.headers.get('Authorization', 'None')}")
                auth_result = self.jwt_auth.authenticate(request)
                # print(f"Auth result: {auth_result}")
            except InvalidToken as e:
                    # print(f"InvalidToken exception: {e}")
                return ResponseService.response(
                    "UNAUTHORIZED",
                    {"token": ["Invalid token. It might be expired or corrupted."]},
                    "UNAUTHORIZED"
                )
            except AuthenticationFailed as e:
                # print(f"AuthenticationFailed exception: {e}")
                return ResponseService.response(
                    "UNAUTHORIZED",
                    {"token": ["Authentication failed. Token is not valid."]},
                    "UNAUTHORIZED"
                )

            if auth_result is None:
                # print("Auth result is None - no token provided")
                request.user = None
                return ResponseService.response(
                    "UNAUTHORIZED",
                    {"token": ["Authentication required. Missing or invalid token."]},
                    "UNAUTHORIZED"
                )

            user_data, _ = auth_result  
            request.user = user_data  

        except Exception as e:
            request.user = None
            return ResponseService.response(
                "INTERNAL_SERVER_ERROR",
                {"error": str(e)},
                "Server Error"
            )

        return self.get_response(request)
