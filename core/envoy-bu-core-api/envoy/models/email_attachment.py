import os
from django.db import models
from django.utils import timezone
from .email_message import EmailChatMessage


def attachment_upload_path(instance, filename):
    """Generate file path for attachments"""
    # Create path like: attachments/conversation_id/message_id/filename
    return f'attachments/{instance.email_message.conversation.id}/{instance.email_message.id}/{filename}'


class EmailAttachment(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False, null=False)
    email_message = models.ForeignKey(
        EmailChatMessage, on_delete=models.CASCADE, related_name="attachments"
    )
    file_name = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=attachment_upload_path, blank=True, null=True)  # Actual file storage
    file_url = models.TextField(blank=True, null=True)  # Legacy field
    content_type = models.TextField(blank=True, null=True)
    size_bytes = models.BigIntegerField(default=0)
    gmail_attachment_id = models.CharField(max_length=512, blank=True, null=True)
    is_image = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now, blank=False, null=False)

    class Meta:
        db_table = "core_email_attachments"
        indexes = [
            models.Index(fields=['email_message']),
            models.Index(fields=['gmail_attachment_id']),
        ]

    def __str__(self):
        return self.file_name or f"Attachment#{self.id}"
