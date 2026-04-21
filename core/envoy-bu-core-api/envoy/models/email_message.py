from django.db import models
from django.utils import timezone
from .chat_conversation import ChatConversation


class EmailChatMessage(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False, null=False)
    conversation = models.ForeignKey(
        ChatConversation, on_delete=models.CASCADE, related_name="messages"
    )
    gmail_message_id = models.CharField(max_length=128, unique=True, blank=True, null=True)
    gmail_thread_id = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    first_message_id = models.CharField(max_length=64, blank=True, null=True)
    from_email = models.TextField(blank=True, null=True)
    to_email = models.TextField(blank=True, null=True)
    subject = models.TextField(blank=True, null=True)
    body = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True, db_index=True)
    is_seen = models.BooleanField(
        default=False,
        help_text="True when the user has seen this message (e.g. opened the conversation).",
    )

    class Meta:
        db_table = "core_email_messages"
        indexes = [
            models.Index(fields=['conversation', 'sent_at']),
            models.Index(fields=['conversation', 'id']),
            models.Index(fields=['gmail_message_id']),
        ]
        ordering = ["sent_at", "id"]

    def __str__(self):
        return f"Email#{self.id} conv={self.conversation_id} subj={self.subject or ''}"
