# app/models.py
from django.db import models
from django.contrib.auth.models import User

class GmailCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who owns this Gmail credential")
    system_email = models.EmailField(unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.CharField(max_length=255, default="https://oauth2.googleapis.com/token")
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    token_expiry = models.DateTimeField()
    last_history_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Last processed Gmail historyId for Pub/Sub push sync",
    )

    class Meta:
        db_table = 'core_gmailcredential'
        verbose_name = 'Gmail Credential'
        verbose_name_plural = 'Gmail Credentials'

    def __str__(self):
        return f"Gmail Credential for {self.system_email} (User: {self.user.id})"


class EmailMessage(models.Model):
    """
    Model to store email message details for sending emails via Gmail API
    """
    # Email details
    to_email = models.EmailField()
    
    # Gmail thread and conversation details
    thread_id = models.CharField(max_length=100, blank=True, null=True, help_text="Gmail thread ID for replies")
    conversation_id = models.CharField(max_length=100, blank=True, null=True)
    conversation_code = models.CharField(max_length=100, blank=True, null=True)
    first_message_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID of the first message in the thread")
    type_based_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID of the send message quotation or policy")
    insurer_id = models.CharField(max_length=100, blank=True, null=True, help_text="ID of the insurer for this perticular mail")
    
    # User and system details
    user_id = models.IntegerField()
    from_email = models.EmailField(help_text="Sender email address")
    
    # Status and tracking
    status = models.CharField(
        max_length=20, 
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
            ('draft', 'Draft')
        ],
        default='pending'
    )
    
    # Gmail message details (after sending)
    gmail_message_id = models.CharField(max_length=100, blank=True, null=True)
    gmail_thread_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    
    # Error tracking
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'core_emailmessage'
        verbose_name = 'Email Message'
        verbose_name_plural = 'Email Messages'
        ordering = ['-created_at']

    def __str__(self):
        return f"Email to {self.to_email} - {self.status} ({self.created_at})"
