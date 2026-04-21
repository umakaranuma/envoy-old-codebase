# Global message format constants
MESSAGES = {
    "SUCCESS": "{{entity}} has been saved successfully",
    "RETRIEVED": "{{entity}} retrieved successfully",
    "UPDATED": "{{entity}} updated successfully",
    "DELETED": "{{entity}} deleted successfully",
    "NOT_FOUND": "{{entity}} with id {{id}} does not exist.",
    "VALIDATION_ERROR": "Validation failed for {{entity}}.",
    "SERVER_ERROR": "An error occurred while processing {{entity}}.",
    "INVALID_REQUEST": "Invalid request parameters for {{entity}}.",
}

class Error:
    UN_AUTHORIZED = "unauthorized"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "data_not_found"
    CONFLICT = "Conflict"
    INTERNAL_SERVER_ERROR = "internal_server_error"
    FORBIDDEN = "forbidden"
    DEFAULT = "default"
    OPPORTUNITY_FORM_CONFLICT =  "opportunity_form_conflict_error_msg"
    DEFAULT_CONFLICT_MSG = "default_delete_conflict_msg"
    TASK_TYPE_DELETE_CONFLICT=  "task_type_delete_conflict_msg"
    TEMPLATE_DELETE_ERROR_MSG = "template_delete_error_msg"

class Message:
    DATA_FETCHED = "default_fetch_success_msg"
    DATA_CREATED = "default_create_success_msg"
    DATA_UPDATED = "default_update_success_msg"
    DATA_DELETED = "default_delete_success_msg"
    DATA_NOT_FOUND = "default_not_found_success.msg"
    EMAIL_SENT= "email_sent"
    NO_PENDING_APPROVALS = "no_pending_approvals"
    PDF_GENERATED = "pdf_generated_successfully"
    

