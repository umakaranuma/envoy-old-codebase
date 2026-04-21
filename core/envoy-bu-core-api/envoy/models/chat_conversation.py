import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone

from envoy.models.user import User
from envoy.models.service_provider import ServiceProvider


def generate_conversation_code() -> str:
    """Generate a short, human-friendly unique code for conversations."""
    while True:
        code = uuid.uuid4().hex[:10].upper()
        if not ChatConversation.objects.filter(code=code).exists():
            return code


class ChatConversation(models.Model):
    POLICY = "POLICY"
    QUOTATION = "QUOTATION"
    ENDORSEMENT = "ENDORSEMENT"
    TYPE_CHOICES = [(POLICY, "POLICY"), (QUOTATION, "QUOTATION"), (ENDORSEMENT, "ENDORSEMENT")]

    id = models.AutoField(primary_key=True, unique=True, blank=False, null=False)
    code = models.CharField(max_length=32, unique=True, blank=False, null=False)
    type_based_id = models.CharField(max_length=64, blank=True, null=True, db_index=True)
    insurer = models.ForeignKey(
        ServiceProvider, on_delete=models.SET_NULL, null=True, blank=True, related_name="chat_conversations"
    )
    gmail_thread_id = models.CharField(max_length=128, blank=True, null=True, db_index=True)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, blank=False, null=False, db_index=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_conversations_created",
    )
    created_at = models.DateTimeField(default=timezone.now, blank=False, null=False, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_chat_conversations"
        
        
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_conversation_code()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} [{self.type}] ({self.type_based_id or '-'}/{self.insurer_id or '-'})"
