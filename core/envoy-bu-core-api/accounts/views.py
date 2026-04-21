from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.conf import settings
import json
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from django.core.exceptions import ValidationError
from envoy.models.user import User

EXTERNAL_API_URL = settings.EXTERNAL_API_URL
DB_DATABASE = settings.DB_DATABASE

class LoginView(APIView):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response("VALIDATION_ERROR", None, "Invalid JSON format")

        # Define validation rules
        rules = {"idp_access_token": "required"}
        custom_messages = {"idp_access_token.required": "IDP Access Token cannot be empty."}

        try:
            errors = ValidatorService.validate(data, rules, custom_messages)
            if errors:
                return ResponseService.response("VALIDATION_ERROR", errors, "Validation Error")
        except ValidationError:
            return ResponseService.response("VALIDATION_ERROR", None, "Invalid input format")

        user_token = data.get("idp_access_token")

        headers = {
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(EXTERNAL_API_URL, headers=headers)

        # Log the full IDP response for debugging
        print("IDP Response:", response.status_code, response.text)

        try:
            response_data = response.json()
        except ValueError:
            return ResponseService.response("UNAUTHORIZED", None, "IDP response is not valid JSON")

        # Ensure the response is successful
        if response.status_code != 200 or not response_data.get("is_success"):
            return ResponseService.response("UNAUTHORIZED", None, "Invalid or expired IDP token")

        # Extract user details correctly
        result_data = response_data.get("result", {})

        user_id = result_data.get("id")
        name = result_data.get("name")
        email = result_data.get("email")

        if not user_id or not email:
            print("Missing required fields in IDP response:", result_data)  # Debugging
            return ResponseService.response("UNAUTHORIZED", None, "Invalid IDP response format")

        # Fetch the user by idp_user_id
        user = User.objects.filter(idp_user_id=user_id).first()

        if not user:
            # User not found
            return ResponseService.response(
                "CONFLICT",
                None,
                "user_not_found",
                "user_not_found"
            )

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Send request to external api/access endpoint after successful login
        try:
            access_payload = {
                "access_token": access_token,
                "idp_user_id": str(user_id),
                "email": email,
                "name": name
            }
            
            # Construct the base URL from the current request for the external endpoint
            # base_url = request.build_absolute_uri('/').rstrip('/')
            base_url = "https://dev-chat-app.apptimus.lk"
            access_url = f"{base_url}/api/access"
            
            # Make the external API call to api/access endpoint
            access_response = requests.post(
                access_url,
                json=access_payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Log the external access endpoint response for debugging
            print("External Access Endpoint Response:", access_response.status_code, access_response.text)
            
        except Exception as e:
            # Log the error but don't fail the login process
            print(f"Error calling external api/access endpoint: {str(e)}")

        return ResponseService.response(
            "SUCCESS",
            result={
                "access_token": access_token,
                "DB_DATABASE":DB_DATABASE,
                "user": {
                    "id": user.id,
                    "first_name": user.first_name,
                    "display_name": user.display_name,
                    "email": user.email,
                    "idp_user_id": user.idp_user_id,
                    "picture": user.picture,
                    "cover_pic": user.cover_pic,
                    "title": user.title,
                    "contact_no": user.contact_no,
                    "email": user.email,
                    "role": {
                        "id": user.role.id if user.role else None,
                        "name": user.role.name if user.role else None,
                    },
                    "entity": {
                        "id": user.entity.id if user.entity else None,
                        "type": user.entity.type if user.entity else None,
                    },
                }
            },
            message="Login successfully!",
        )
