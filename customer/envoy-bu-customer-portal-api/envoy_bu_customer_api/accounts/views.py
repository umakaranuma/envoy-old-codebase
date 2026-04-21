import re
from unittest import result
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
import requests
from django.conf import settings
import json
from mServices.ResponseService import ResponseService
from mServices.ValidatorService import ValidatorService
from django.core.exceptions import ValidationError
from mServices.QueryBuilderService import QueryBuilderService
from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes

from envoy_bu_customer_api.custom_auth_user import CustomAuthUser
from envoy_bu_customer_api.customer.customer_services.login_history_service import log_customer_login

EXTERNAL_API_URL = settings.EXTERNAL_API_URL
User = get_user_model()

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return ResponseService.response("VALIDATION_ERROR", None, "Invalid JSON format")

        # Define validation rules
        rules = {"idp_access_token": "required",
                 }
        custom_messages = {"idp_access_token.required": "IDP Access Token cannot be empty.",
                           }

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

        print("headers" , headers)
        
        if not EXTERNAL_API_URL:
            raise Exception("EXTERNAL_API_URL is not set in settings!")

        response = requests.get(EXTERNAL_API_URL, headers=headers)
        print("response" , response)

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

        # Fetch the customer by idp_customer_id
        customer = (
            QueryBuilderService('core_customers')
            .leftJoin('core_contacts', 'core_contacts.id', 'core_customers.primary_contact_id')
            .where('core_customers.idp_customer_id', user_id)
            .where('core_contacts.email', email)
            .select(
                'core_customers.id as customer_id',
                'core_customers.name',
                'core_customers.idp_customer_id',
                'core_customers.type',
                'core_contacts.email',
                'core_customers.code',
                'core_customers.logo',
                'core_contacts.picture',
                'core_customers.entity_id',
                'core_customers.portal_id',
                'core_customers.type',

            )
            .first()
        )

        if not customer:
            return ResponseService.response(
                "CONFLICT",
                None,
                "customer_not_found"
            )
        
        print("customer" , customer)

        # Generate a dummy JWT token (since no Django user model is used)
        user, created = User.objects.get_or_create(username=email, defaults={"email": email, "first_name": name or ""})
        refresh = RefreshToken.for_user(user)
        refresh['customer_id'] = customer.get("customer_id")
        refresh['name'] = customer.get("name")
        refresh['email'] = email
        refresh['idp_customer_id'] = customer.get("idp_customer_id")
        refresh['type'] = customer.get("type")
        refresh['code'] = customer.get("code")

        tokens = get_tokens_for_user(user, customer.get("customer_id"))
        access_token = tokens['access']

        print("Setting request.user to CustomAuthUser:", result_data)
        request.user = CustomAuthUser(result_data)

        print("customer_details", request.user, type(request.user))

        # Log customer login history
        device = request.META.get('HTTP_USER_AGENT')
        ip = get_client_ip(request)
        # ip = "123.231.96.132"
        location = get_location_from_ip(ip)
        log_customer_login(customer_id=customer.get("customer_id"), device=device, ip=ip, location=location, email=email)

        entity_id = customer.get("entity_id")
        agent = (
            QueryBuilderService("core_users")
            .leftJoin('crm_opportunities','crm_opportunities.sales_agent_id','core_users.id')
            .select("display_name","core_users.email as email","contact_no","core_users.id","picture","cover_pic")
            .where("crm_opportunities.customer_id",customer.get('customer_id'))
            .first()
        )

        print("agent",agent)
        
        if not agent:

            agent = (
                QueryBuilderService("core_users")
                .leftJoin('core_entities','core_entities.created_by_id',"core_users.id")
                .select("display_name","email","contact_no","core_users.id")
                .where("core_entities.id",entity_id)
                .first()
            )

            print("agent",agent)

        
        is_enrolled =    (QueryBuilderService("core_customers").where("id", customer.get("customer_id")).update({"is_enrolled": True})) 
            
        print("is_enrolled",is_enrolled)



        return ResponseService.response(
            "SUCCESS",
            # 
            result={
                "access_token": access_token,
                "customer": {
                    "id": customer.get("customer_id"),
                    "portal_id": customer.get('portal_id'),
                    "type" : customer.get('type'),
                    "name": customer.get("name"),
                    "email": email,
                    "idp_customer_id": customer.get("idp_customer_id"),
                    "type": customer.get("type"),
                    "code": customer.get("code"),
                    "logo":customer.get('logo'),
                    "picture":customer.get('picture')
                    # Add more fields as needed from core_customers
                },
                "agent" : {
                 "id":agent.get('id',''),
                 "display_name":agent.get('display_name',''),
                 "email":agent.get('email',''),
                 "contact":agent.get('contact',''),
                 "logo":agent.get('picture',''),
                 "picture":agent.get('cover_pic',''),
                }

            },
            message="login_successfully!",
        )

def get_tokens_for_user(user, customer_id):
    refresh = RefreshToken.for_user(user)
    refresh['customer_id'] = customer_id
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def get_location_from_ip(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                return f"{data.get('city', 'city1')}, {data.get('regionName', 'regionName1')}, {data.get('country', 'country1')}"
            print("get_location_from_ip",data)
    except Exception:
        pass
    return None

def get_client_ip(request):
    # Try to get the real client IP if behind a proxy/load balancer
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def quotations(request):
    customer_id = None
    if request.auth:
        customer_id = request.auth.get('customer_id')
    print("customer_id", customer_id)
    # Now use customer_id to filter data
