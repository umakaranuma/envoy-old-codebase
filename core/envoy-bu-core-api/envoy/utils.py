from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import requests
from django.conf import settings
from django.template.loader import render_to_string
from .constants import MESSAGES


def get_serializer(serializer_path):
    module_path, class_name = serializer_path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[class_name])
    return getattr(module, class_name)


class CommonPagination(PageNumberPagination):
    page_size_query_param = "page_size"  # Allows dynamic page size
    all_records_query_param = "all"  # Custom parameter to fetch all records

    def paginate_queryset(self, queryset, request, view=None):
        """
        Disable pagination if 'all=true' is passed in the query parameters.
        """
        if request.query_params.get(self.all_records_query_param) == "true":
            return None  # Disable pagination
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        """
        Custom response to include current page, last page, total records, and count.
        """
        if data is None:
            return Response(
                {
                    "current_page": 1,
                    "last_page": 1,
                    "total_records": 0,
                    "count": 0,
                    "data": [],
                }
            )
        return Response(
            {
                "current_page": self.page.number,
                "last_page": self.page.paginator.num_pages,
                "total_records": self.page.paginator.count,
                "count": len(data),
                "data": data,
            }
        )


def send_invitation_email(invitation,role, template_name, subject):
    frontend_url = settings.BROKERAGE_FRONTEND_BASE_URL
    # invitation_link = (
    #     f"{frontend_url}/user-invitation?"
    #     f"invitation={invitation.uid}"
    #     f"&name={invitation.name}"
    #     f"&email={invitation.email}"
    #     f"&role_id={role.id}"
    #     f"&role_name={role.name}"
    # )
    invitation_link = f"{frontend_url}/user-invitation?invitation={invitation.uid},name={invitation.name},email={invitation.email},role_id={role.id},role_name={role.name}"
    print("invitation_link:", invitation_link)
    email_content = render_to_string(
        template_name, {"invitation_link": invitation_link}
    )

    email_payload = {
        "mailer_details": {
            "MAIL_MAILER": settings.MAIL_MAILER,
            "MAIL_HOST": settings.MAIL_HOST,
            "MAIL_PORT": settings.MAIL_PORT,
            "MAIL_USERNAME": settings.MAIL_USERNAME,
            "MAIL_PASSWORD": settings.MAIL_PASSWORD,
            "MAIL_FROM_ADDRESS": settings.MAIL_FROM_ADDRESS,
            "MAIL_FROM_NAME": settings.MAIL_FROM_NAME,
        },
        "email_content": email_content,
        "email": invitation.email,
        "subject": subject,
    }

    email_api_url = settings.EMAIL_SENDING_API_URL
    if not email_api_url:
        return False, "EMAIL_SENDING_API_URL is not configured in settings."

    try:
        response = requests.post(email_api_url, json=email_payload, timeout=5)
        print('email_api_url', email_api_url)
        print('payload', email_payload)
        print('response', response)
        print('response text', response.text)

        if response.status_code != 200:
            return False, f"Failed to send email: {response.text}"

    except requests.RequestException as e:
        return False, str(e)


    # try:
    #     response = requests.post(email_api_url, json=email_payload, timeout=5)
    #     print('email_api_url', email_api_url)
    #     print('payload', email_payload)
    #     print('response', response)
    #     print('response text', response.text)

    #     if response.status_code != 200:
    #         return False, "Failed to send email"

    # except requests.RequestException as e:
    #     return False, str(e)

    return True, None


def send_customer_invitation_email(invitation, template_name, subject):
    frontend_url = settings.CUSTOMER_FRONTEND_BASE_URL
    if not frontend_url:
        return False, "CUSTOMER_FRONTEND_BASE_URL is not configured in settings"
    
    invitation_link = f"{frontend_url}/invitation?portal_id={invitation.portal_id}&email={invitation.email}&idp_customer_id={invitation.idp_customer_id}&token={invitation.token}&is_enrolled={invitation.is_enrolled}&invitation={invitation.uid}"

    email_content = render_to_string(
        template_name, {"invitation_link": invitation_link}
    )

    email_payload = {
        "mailer_details": {
            "MAIL_MAILER": settings.MAIL_MAILER,
            "MAIL_HOST": settings.MAIL_HOST,
            "MAIL_PORT": settings.MAIL_PORT,
            "MAIL_USERNAME": settings.MAIL_USERNAME,
            "MAIL_PASSWORD": settings.MAIL_PASSWORD,
            "MAIL_FROM_ADDRESS": settings.MAIL_FROM_ADDRESS,
            "MAIL_FROM_NAME": settings.MAIL_FROM_NAME,
        },
        "email_content": email_content,
        "email": invitation.email,
        "subject": subject,
    }

    email_api_url = settings.EMAIL_SENDING_API_URL

    try:
        response = requests.post(email_api_url, json=email_payload, timeout=5)
        print('email_api_url', email_api_url)
        print('payload', email_payload)
        print('response', response)
        print('response text', response.text)

        if response.status_code != 200:
            return False, f"Failed to send email: {response.text}"

    except requests.RequestException as e:
        return False, str(e)

    return True, None



def get_message(message_key, entity="", **kwargs):
    """
    Fetches the message from constants and replaces placeholders dynamically.

    :param message_key: Key from MESSAGES dict (e.g., "SUCCESS", "NOT_FOUND").
    :param entity: Entity name (e.g., "Group", "User").
    :param kwargs: Additional placeholders (e.g., id=5).
    :return: Formatted message string.
    """
    message_template = MESSAGES.get(message_key, "Message not found.")
    message = message_template.replace("{{entity}}", entity)

    # Replace additional placeholders dynamically
    for key, value in kwargs.items():
        message = message.replace(f"{{{{{key}}}}}", str(value))

    return message
