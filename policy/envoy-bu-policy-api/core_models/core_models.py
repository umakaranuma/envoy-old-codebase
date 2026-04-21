from django.utils import timezone
from django.db import models


class Entity(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(
        "core_models.User",
        on_delete=models.RESTRICT,
        related_name="entities_created",
        null=True,
        blank=True,
        default=None,
    )
    updated_by = models.ForeignKey(
        "core_models.User",
        on_delete=models.RESTRICT,
        related_name="entities_updated",
        null=True,
        blank=True,
        default=None,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_entities"
        managed = False

    def __str__(self):
        return f"Entity {self.id} - {self.type}"


# ----------------------------------------


class Module(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=25, unique=True)
    key = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=320, blank=True, null=True)

    class Meta:
        db_table = "core_modules"
        managed = False

    def __str__(self):
        return f"{self.name} ({self.key})"


# -----------------------------------------


class Action(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.CharField(max_length=50, blank=False, null=False)
    action = models.CharField(max_length=50, blank=False, null=False)
    remarks = models.CharField(max_length=320, blank=True, null=True)
    can_be_permission = models.BooleanField(default=False)
    module = models.ForeignKey(
        Module, on_delete=models.RESTRICT, blank=False, null=False
    )

    class Meta:
        db_table = "core_actions"
        managed = False

    def __str__(self):
        return f"Action: {self.entity} - {self.action}"


# -----------------------------------------


class Role(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.ForeignKey(
        Entity,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=320, null=True, blank=True)
    system_role = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "core_roles"
        managed = False

    def __str__(self):
        return self.name

    def get_permissions(self):
        return Action.objects.filter(roleauthority__role_id=self.id).select_related(
            "roleauthority"
        )


# -----------------------------------------


class User(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    title = models.CharField(max_length=100, null=True)
    first_name = models.CharField(max_length=80, null=True)
    last_name = models.CharField(max_length=80, null=True)
    display_name = models.CharField(max_length=80, blank=False)
    email = models.EmailField(max_length=254, blank=False)
    contact_no = models.CharField(max_length=80, null=True)
    picture = models.TextField(max_length=300, null=True)
    idp_user_id = models.CharField(max_length=255)
    role = models.ForeignKey(
        Role, on_delete=models.RESTRICT, blank=False, related_name="users"
    )

    entity = models.ForeignKey(Entity, on_delete=models.RESTRICT)

    @property
    def is_authenticated(self):
        return True

    class Meta:
        db_table = "core_users"
        managed = False

    def __str__(self):
        return self.first_name


# ----------------------------------------


class TaskStatus(models.Model):
    class StatusType(models.TextChoices):
        TODO = "Todo", "To Do"
        IN_PROGRESS = "Inprogress", "In Progress"
        DONE = "Done", "Done"

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=80, unique=True, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(
        max_length=20, choices=StatusType.choices, blank=False, null=False
    )
    color = models.CharField(max_length=100, default="#eeeeef", blank=False, null=False)
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "core_task_status"
        managed = False

    def __str__(self):
        return f"{self.name} - {self.type}"


class Task(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    code = models.CharField(max_length=20, blank=False, null=False)
    task = models.CharField(max_length=250, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    assigned_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    task_status = models.ForeignKey(
        TaskStatus, on_delete=models.RESTRICT, related_name="tasks"
    )
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "core_tasks"
        managed = False

    def __str__(self):
        return f"{self.task} - {self.task_status.name if self.task_status else 'No Status'}"


# ----------------------------------------


class Channel(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "core_channels"
        managed = False

    def __str__(self):
        return self.name


# ----------------------------------------


class RoleAuthority(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    class Meta:
        db_table = "core_role_authorities"
        managed = False

    def __str__(self):
        return f"{self.role_id.name} - {self.action_id.action}"


# ----------------------------------------


class Contact(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False)  # Required
    email = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    primary_contact = models.CharField(
        max_length=20, blank=False, null=True
    )  # Required
    secondary_contact = models.CharField(max_length=20, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    picture = models.TextField(blank=True, null=True)
    duplicated_contact = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="duplicates",
    )

    class Meta:
        db_table = "core_contacts"
        managed = False

    def __str__(self):
        return self.name


# ----------------------------------------


class Customer(models.Model):
    CORPORATE = "Corporate"
    PERSONAL = "Personal"
    ACCOUNT_TYPE_CHOICES = [(CORPORATE, "Corporate"), (PERSONAL, "Personal")]

    id = models.AutoField(primary_key=True, unique=True, blank=False)
    code = models.CharField(
        max_length=6, unique=True, blank=False
    )  # Required, Auto-generated 6-digit code
    type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    logo = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )
    primary_contact = models.ForeignKey(
        Contact, on_delete=models.RESTRICT, null=False, related_name="primary_accounts"
    )

    entity = models.ForeignKey(
        Entity, on_delete=models.RESTRICT, null=True, related_name="customers"
    )

    class Meta:
        db_table = "core_customers"
        managed = False


# ----------------------------------------


class EntityActivity(models.Model):
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="activities",
        null=False,
        blank=False,
    )
    activity = models.TextField(null=False, blank=False)
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, default=None
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_entity_activities"
        managed = False

    def __str__(self):
        return f"{self.entity} - Activity"


# -------------------------------------------


class CustomerAdditionalContact(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=200, blank=False, null=False)
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name="additional_contacts"
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, related_name="customer_contacts"
    )
    is_primary = models.BooleanField(default=False, blank=False, null=False)

    class Meta:
        db_table = "core_customer_contacts"
        managed = False

    def __str__(self):
        return f"{self.title} ({self.customer})"


# ----------------------------------------


class Intraction(models.Model):
    """Model representing interactions in the CRM system"""

    id = models.AutoField(primary_key=True)
    channel = models.ForeignKey(Channel, on_delete=models.RESTRICT)
    contact = models.ForeignKey(
        Contact, on_delete=models.CASCADE, null=True, blank=True
    )
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, null=True, blank=True
    )
    opportunity_id = models.IntegerField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    contact_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    opportunity_status_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "core_intractions"
        managed = False

    def __str__(self):
        return f"Intraction {self.id} - Channel: {self.channel}"


# ----------------------------------------


class Currency(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    symbol = models.CharField(max_length=10, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    decimal_digits = models.IntegerField(blank=False, null=False)
    rounding = models.IntegerField(blank=False, null=False)
    code = models.CharField(
        max_length=100, unique=True, blank=False, null=False
    )  # Unique

    class Meta:
        db_table = "core_currencies"
        managed = False

    def __str__(self):
        return f"{self.name} ({self.symbol})"


# ----------------------------------------


class Form(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = "core_forms"
        managed = False

    def __str__(self):
        return self.title


# ----------------------------------------
class FormSubmission(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    # attribute = models.ForeignKey(FormAttribute, on_delete=models.CASCADE, related_name="submissions")
    # value = models.TextField()

    class Meta:
        db_table = "core_form_submissions"
        managed = False

    def __str__(self):
        return f"Submission for {self.form.title}"


# ------------------------------------------


class FormAttribute(models.Model):
    TEXT = "TEXT"
    TYPE_CHOICES = [
        (TEXT, "Text"),
    ]

    id = models.AutoField(primary_key=True, unique=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="attributes")
    title = models.CharField(max_length=255, unique=True, blank=False, null=False)
    type = models.CharField(
        max_length=10, choices=TYPE_CHOICES, blank=False, null=False
    )
    attribute_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "core_form_attributes"
        managed = False

    def __str__(self):
        return f"{self.form.title} - {self.title}"


# -----------------------------------------


class FormSubmissionValue(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    form_submission = models.ForeignKey(
        FormSubmission, on_delete=models.CASCADE, related_name="formsubmissions"
    )
    attribute = models.ForeignKey(
        FormAttribute, on_delete=models.CASCADE, related_name="formattributes"
    )
    value = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = "core_form_submission_values"
        managed = False

    def __str__(self):
        return f"Value for {self.attribute.name} in {self.form_submission.form.title}"


# ----------------------------------------


class Product(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(
        max_length=100, unique=True, blank=False, null=False
    )  # Unique

    class Meta:
        db_table = "core_products"
        managed = False

    def __str__(self):
        return self.name

class VendorProduct(models.Model):

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    class Meta:
        db_table = "core_vendor_products"
        managed = False

    def __str__(self):
        return self.name


class Status(models.Model):

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=80, unique=True, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(max_length=50, blank=False, null=True)
    module = models.CharField(max_length=200, blank=True, null=True)
    color = models.CharField(max_length=100, default="#eeeeef", blank=False, null=False)
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "core_status"
        verbose_name = "Status"
        managed = False

    def __str__(self):
        return self.id


class CoreTemplate(models.Model):
    TYPE_CHOICES = [
        ("single_form", "Single Form"),
        ("multi_step_form", "Multi Step Form"),
    ]
    title = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "core_templates"
        managed = False


class CoreFormElement(models.Model):
    CATEGORY_CHOICES = [
        ("input_individual", "Input Individual"),
        ("input_group", "Input Group"),
        ("display", "Display"),
    ]
    title = models.CharField(max_length=200)
    element_group = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    code = models.CharField(max_length=200)
    description = models.CharField(max_length=250, null=True, blank=True)
    group = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, db_column="group_id"
    )
    group_element_order_number = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "core_form_elements"
        managed = False


class CoreFormSubmission(models.Model):
    form = models.ForeignKey(
        CoreTemplate, on_delete=models.CASCADE, db_column="form_id"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column="user_id")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id', null=True, blank=True)

    class Meta:
        db_table = "core_form_submissionss"
        managed = False


class CoreFormCustomFormStep(models.Model):
    form = models.ForeignKey(
        CoreTemplate, on_delete=models.CASCADE, db_column="form_id"
    )
    title = models.CharField(max_length=200)
    step_number = models.FloatField()
    description = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "core_form_custom_form_steps"
        managed = False


class CoreFormCustomFormPanel(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    form = models.ForeignKey(
        CoreTemplate, on_delete=models.CASCADE, db_column="form_id"
    )
    step = models.ForeignKey(
        CoreFormCustomFormStep,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="step_id",
    )
    order_number = models.FloatField(default=1.0, )

    class Meta:
        db_table = "core_form_custom_form_panels"
        managed = False


class CoreFormCustomFormElement(models.Model):
    label = models.CharField(max_length=200, null=True, blank=True)
    step = models.ForeignKey(
        CoreFormCustomFormStep,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="step_id",
    )
    panel = models.ForeignKey(
        CoreFormCustomFormPanel,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        db_column="panel_id",
    )
    element = models.ForeignKey(
        CoreFormElement, on_delete=models.CASCADE, db_column="element_id"
    )
    is_required = models.BooleanField(default=False)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, db_column="parent_id"
    )
    order_number = models.FloatField(null=True, blank=True)
    column_size = models.IntegerField()
    category = models.CharField(max_length=200, null=True, blank=True)
    code = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        db_table = "core_form_custom_form_elements"
        managed = False


class CoreFormSubmissionValue(models.Model):
    form_submission = models.ForeignKey(
        CoreFormSubmission, on_delete=models.CASCADE, db_column="form_submission_id"
    )
    custom_form_element = models.ForeignKey(
        CoreFormCustomFormElement,
        on_delete=models.CASCADE,
        db_column="custom_form_element_id",
    )
    form_element = models.ForeignKey(
        CoreFormElement, on_delete=models.CASCADE, db_column="form_element_id"
    )
    value = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "core_form_submission_valuess"
        managed = False


# --------------------------------------------------------
# class ServiceProvider(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=250, unique=True)
#     description = models.CharField(max_length=250, blank=True, null=True)
#     logo = models.CharField(max_length=250, blank=True, null=True)
#     status = models.CharField(max_length=50)
#     email = models.CharField(max_length=250, blank=True, null=True)

#     class Meta:
#         db_table = "crmq_service_providers"
#         managed = False


# --------------------------------------------------------

#--------------------------------------------------------
# class ServiceProvider(models.Model):
#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=250, unique=True)
#     description = models.CharField(max_length=250, blank=True, null=True)
#     logo = models.CharField(max_length=250, blank=True, null=True)
#     status = models.CharField(max_length=50)
#     email = models.CharField(max_length=250, blank=True, null=True)
    
#     class Meta:
#         db_table = "core_service_providers"
#         managed = False
#--------------------------------------------------------

class OpportunityType(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_types"
        managed = False


# --------------------------------------------------------
class OpportunityFormConfig(models.Model):
    ONBOARDING = "onboarding"
    QUOTATION_REQUEST = "quotation_request"
    CLAIM = "claim"
    CLAIM_EVALUATION = "claim_evaluation"

    DATA_GATHERING_CHOICES = [
        (ONBOARDING, "Onboarding"),
        (QUOTATION_REQUEST, "Quotation Request"),
        (CLAIM, "Claim"),
        (CLAIM_EVALUATION, "Claim Evaluation"),
    ]

    title = models.CharField(max_length=255)
    opportunity_type = models.ForeignKey(OpportunityType, on_delete=models.CASCADE)
    data_gethering_type = models.CharField(
        max_length=255, choices=DATA_GATHERING_CHOICES
    )
    form = models.ForeignKey(
        CoreTemplate,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
        related_name="opportunity_form_config",
    )

    class Meta:
        db_table = "crm_opportunity_form_config"
        managed = False


class Team(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    leader_id = models.BigIntegerField(blank=True, null=True)
    manager_id = models.BigIntegerField(blank=True, null=True)
    detector_id = models.BigIntegerField(blank=True, null=True)
    status = models.CharField( max_length=20, blank=True, null=True, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "core_teams"
        managed = False

    def __str__(self):
        return self.name




#--------------------------------------------------------

class ServiceProvider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_provider')
    name = models.CharField(max_length=255)
    logo = models.TextField(blank=True, null=True) 
    address = models.TextField()
    contact_no = models.CharField(max_length=20)
    email = models.EmailField()
    website = models.URLField(blank=True, null=True)
    fax_no = models.CharField(max_length=20, blank=True, null=True)

    # Audit fields
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.ForeignKey(Status,on_delete=models.RESTRICT,blank=False,  null=True,related_name="service_provider_status")
    description = models.CharField(max_length=200, null=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='service_provider_created',
        null=True,
        blank=True
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='service_provider_updated',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = "core_service_providers"
        managed = False



#--------------------------------------------------------
class ProductDocumentType(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    is_mandatory = models.BooleanField(default=False)
    vendor_product_id = models.BigIntegerField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    

    class Meta:
        db_table = "core_product_document_types"
        managed = False

    def __str__(self):
        return self.name
    
#-------------------------------------------------

class ProductGroup(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "core_product_groups"
        managed = False

    def __str__(self):
        return self.name
    
#-------------------------------------------------
class GmailCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, help_text="User who owns this Gmail credential")
    system_email = models.EmailField(unique=True)
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.CharField(max_length=255, default="https://oauth2.googleapis.com/token")
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    token_expiry = models.DateTimeField()

    class Meta:
        db_table = 'core_gmailcredential'
        verbose_name = 'Gmail Credential'
        verbose_name_plural = 'Gmail Credentials'
        managed = False

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
        managed = False

    def __str__(self):
        return f"Email to {self.to_email} - {self.status} ({self.created_at})"
