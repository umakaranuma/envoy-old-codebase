import requests
from pydantic import BaseModel, EmailStr, ValidationError
from typing import List, Literal, Optional, Union

# Pydantic model for validating email data
class EmailItem(BaseModel):
    recipient_email: EmailStr
    subject: str
    body: str
    priority: Literal["high", "medium", "low"]
    links: Optional[List[Union[str, dict]]] = []

# Simple response formatter
class ResponseService:
    @staticmethod
    def response(status, data=None, message=""):
        return {
            "status": status,
            "data": data,
            "message": message
        }

# Core email sending service
class SendMail:
    def __init__(self):
        self.api_key = "456"
        self.application_name = 'envoy'
        self.url = f"https://notifier.utilities.apptimus.lk/api/{self.application_name}/email/simple"

    def send_email(self, email_data: List[dict]):
        try:
            # Validate input data
            validated_emails = [EmailItem(**item) for item in email_data]

            payload = {
                "api_key": self.api_key,
                "email_data": [email.dict() for email in validated_emails]
            }

            response = requests.post(self.url, json=payload)
            return response.json()

        except ValidationError as ve:
            errors = ", ".join(err['msg'] for err in ve.errors())
            return ResponseService.response('VALIDATION_ERROR', None, errors)

        except Exception as e:
            return ResponseService.response('INTERNAL_SERVER_ERROR', None, str(e))



# Example usage:
# send_mail = SendMail()
# result = send_mail.send_email([
#     {
#         "recipient_email": "test@example.com",
#         "subject": "Hello",
#         "body": "This is a test",
#         "priority": "high",
#         "links": ["https://example.com"]
#     }
# ])
# print(result)

