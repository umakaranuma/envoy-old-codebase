from django.db import models





class Entity(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey('core_models.User', on_delete=models.RESTRICT, related_name="entities_created",null=True, blank=True, default=None
    )
    updated_by = models.ForeignKey('core_models.User', on_delete=models.RESTRICT, related_name="entities_updated",null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_entities"
        managed = False

    def __str__(self):
        return f"Entity {self.id} - {self.type}"

#----------------------------------------


class EntityDocument(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="documents")
    doc = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=False)  
    type = models.CharField(max_length=255, blank=False)

    class Meta:
        db_table = "core_entity_docs"
        managed = False

    def __str__(self):
        return f"Document for Entity {self.entity.id}"

#-----------------------------------------

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


#-----------------------------------------

class Action(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.CharField(max_length=50,blank=False, null=False)
    action = models.CharField(max_length=50,blank=False, null=False)
    remarks = models.CharField(max_length=320, blank=True, null=True)
    can_be_permission = models.BooleanField(default=False)
    module = models.ForeignKey(Module,on_delete=models.RESTRICT, blank=False, null=False)

    class Meta:
        db_table = "core_actions"
        managed = False

    def __str__(self):
        return f"Action: {self.entity} - {self.action}"



#-----------------------------------------

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.ForeignKey(
        Entity, on_delete=models.RESTRICT, null=True, blank=True,
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
        return Action.objects.filter(roleauthority__role_id=self.id).select_related("roleauthority")
    
#-----------------------------------------



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
    role = models.ForeignKey(Role, on_delete=models.RESTRICT, blank=False, related_name="users")

    entity = models.ForeignKey(
        Entity, on_delete=models.RESTRICT
    )

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
    type = models.CharField(max_length=20, choices=StatusType.choices, blank=False, null=False)
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
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    assigned_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    task_status = models.ForeignKey(TaskStatus, on_delete=models.RESTRICT, related_name="tasks")
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
    primary_contact = models.CharField(max_length=20, blank=False,null=True)  # Required
    secondary_contact = models.CharField(max_length=20, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    picture = models.TextField(blank=True, null=True)
    duplicated_contact = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="duplicates"
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
    code = models.CharField(max_length=6, unique=True, blank=False)  # Required, Auto-generated 6-digit code
    type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    logo = models.TextField(blank=True, null=True) 
    remarks = models.TextField(blank=True, null=True) 
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children"
    )
    primary_contact = models.ForeignKey(
        Contact, on_delete=models.RESTRICT, null=False, related_name="primary_accounts"
    )
    
    entity = models.ForeignKey(Entity, on_delete=models.RESTRICT, null=True, related_name="customers")


    class Meta:
        db_table = "core_customers"
        managed = False



# ----------------------------------------


class EntityActivity(models.Model):
    entity = models.ForeignKey(Entity,on_delete=models.CASCADE,related_name="activities",null=False, blank=False)
    activity = models.TextField(null=False, blank=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, default=None
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_entity_activities"
        managed = False

    def __str__(self):
        return f"{self.entity} - Activity"

#-------------------------------------------


class CustomerAdditionalContact(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=200, blank=False, null=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="additional_contacts")
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, related_name="customer_contacts")
    is_primary = models.BooleanField(default=False,blank=False, null=False)

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
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    opportunity_id = models.IntegerField( null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    contact_by = models.ForeignKey(User, on_delete=models.RESTRICT)
    opportunity_status_id = models.IntegerField( null=True, blank=True)

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
    code = models.CharField(max_length=100, unique=True, blank=False, null=False)  # Unique

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
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="submissions",)
    # attribute = models.ForeignKey(FormAttribute, on_delete=models.CASCADE, related_name="submissions")
    # value = models.TextField()

    class Meta:
        db_table = "core_form_submissions"
        managed = False

    def __str__(self):
        return f"Submission for {self.form.title}"


#------------------------------------------


class FormAttribute(models.Model):
    TEXT = "TEXT"
    TYPE_CHOICES = [
        (TEXT, "Text"),
    ]

    id = models.AutoField(primary_key=True, unique=True)
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name="attributes")
    title = models.CharField(max_length=255,unique=True, blank=False, null=False)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,blank=False, null=False)
    attribute_name = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "core_form_attributes"
        managed = False

    def __str__(self):
        return f"{self.form.title} - {self.title}"

#-----------------------------------------


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
    code = models.CharField(max_length=100, unique=True, blank=False, null=False)  # Unique

    class Meta:
        db_table = "core_products"
        managed = False

    def __str__(self):
        return self.name

class Status(models.Model):

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=80, unique=True, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(max_length=20, blank=False, null=True)
    module = models.CharField(max_length=200, blank=True, null=True)
    color = models.CharField(max_length=100, default="#eeeeef", blank=False, null=False)
    sort_index = models.FloatField(blank=True, null=True)


    class Meta:
        db_table = "core_status"
        verbose_name = 'Status'
        managed = False

    def __str__(self):
        return self.name if self.name else str(self.id)






class CoreTemplate(models.Model):
    TYPE_CHOICES = [
        ('single_form', 'Single Form'),
        ('multi_step_form', 'Multi Step Form'),
    ]
    title = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "core_templates"
        managed = False




class CoreFormElement(models.Model):
    CATEGORY_CHOICES = [
        ('input_individual', 'Input Individual'),
        ('input_group', 'Input Group'),
        ('display', 'Display'),
    ]
    title = models.CharField(max_length=200)
    element_group = models.CharField(max_length=200, null=True, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    code = models.CharField(max_length=200)
    description = models.CharField(max_length=250, null=True, blank=True)
    group = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, db_column='group_id')
    group_element_order_number = models.FloatField(null=True, blank=True)

    class Meta:
        db_table = "core_form_elements"
        managed = False





class CoreFormSubmission(models.Model):
    form = models.ForeignKey(CoreTemplate, on_delete=models.CASCADE, db_column='form_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, db_column='customer_id', null=True, blank=True)

    class Meta:
        db_table = "core_form_submissionss"
        managed = False


class CoreFormCustomFormStep(models.Model):
    form = models.ForeignKey(CoreTemplate, on_delete=models.CASCADE, db_column='form_id')
    title = models.CharField(max_length=200)
    step_number = models.FloatField()
    description = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "core_form_custom_form_steps"
        managed = False


class CoreFormCustomFormPanel(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    form = models.ForeignKey(CoreTemplate, on_delete=models.CASCADE, db_column='form_id')
    step = models.ForeignKey(CoreFormCustomFormStep, null=True, blank=True, on_delete=models.SET_NULL, db_column='step_id')
    order_number = models.FloatField(default=1.0) 

    class Meta:
        db_table = "core_form_custom_form_panels"
        managed = False

class CoreFormCustomFormElement(models.Model):
    label = models.CharField(max_length=200, null=True, blank=True)
    step = models.ForeignKey(CoreFormCustomFormStep, null=True, blank=True, on_delete=models.SET_NULL, db_column='step_id')
    panel = models.ForeignKey(CoreFormCustomFormPanel, null=True, blank=True, on_delete=models.SET_NULL, db_column='panel_id')
    element = models.ForeignKey(CoreFormElement, on_delete=models.CASCADE, db_column='element_id')
    is_required = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, db_column='parent_id')
    order_number = models.FloatField(null=True, blank=True)
    column_size = models.IntegerField()
    category = models.CharField(max_length=200,null=True, blank=True)
    code = models.CharField(max_length=200,null=True, blank=True)

    class Meta:
        db_table = "core_form_custom_form_elements"
        managed = False

class CoreFormSubmissionValue(models.Model):
    form_submission = models.ForeignKey(CoreFormSubmission, on_delete=models.CASCADE, db_column='form_submission_id')
    custom_form_element = models.ForeignKey(CoreFormCustomFormElement, on_delete=models.CASCADE, db_column='custom_form_element_id')
    form_element = models.ForeignKey(CoreFormElement, on_delete=models.CASCADE, db_column='form_element_id')
    value = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "core_form_submission_valuess"
        managed = False


#--------------------------------------------------------
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
#--------------------------------------------------------

class OpportunityType(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_types"
        managed = False


#--------------------------------------------------------
class OpportunityFormConfig(models.Model):
    ONBOARDING = "onboarding"
    QUOTATION_REQUEST = "quotation_request"
    CLAIM = "claim"
    CLAIM_EVALUATION = "claim_evaluation"
    CUSTOMER_POLICY = "customer_policy"
    CUSTOMER_QUOTATION = "customer_quotation"

    DATA_GATHERING_CHOICES = [
        (ONBOARDING, "Onboarding"),
        (QUOTATION_REQUEST, "Quotation Request"),
        (CLAIM, "Claim"),
        (CLAIM_EVALUATION, "Claim Evaluation"),
        (CUSTOMER_POLICY, "Customer Policy"),
        (CUSTOMER_QUOTATION, "Customer Quotation"),
    ]

    title = models.CharField(max_length=255)
    opportunity_type = models.ForeignKey(OpportunityType, on_delete=models.CASCADE)
    data_gethering_type = models.CharField(max_length=255, choices=DATA_GATHERING_CHOICES)
    form = models.ForeignKey(CoreTemplate, on_delete=models.RESTRICT,null=True, blank=True, related_name="opportunity_form_config")

    class Meta:
        db_table = "crm_opportunity_form_config"
        managed = False




#--------------------------------------------------------
class VendorProducts(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(max_length=100, blank=True, null=True)  
    category_id = models.BigIntegerField(blank=True, null=True)
    vendor_id = models.BigIntegerField(blank=True, null=True)
    coverage_level = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    currency_id = models.BigIntegerField(blank=True, null=True)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    added_by = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    docs = models.CharField(max_length=255, blank=True, null=True)
    entity_id = models.BigIntegerField(blank=True, null=True)
    

    class Meta:
        db_table = "core_vendor_products"
        managed = False

    def __str__(self):
        return self.name
    
#--------------------------------------------------------
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

#--------------------------------------------------------
from django.db import models

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
    


#--------------------------------------------------------
class ProductCoverage(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    coverage_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    excess_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    limitation=models.CharField(max_length=255, blank=True, null=True)
    is_mandatory = models.BooleanField(default=False)
    vendor_product_id = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        db_table = "core_product_coverages"
        managed = False

    def __str__(self):
        return self.name


#--------------------------------------------------------
#--------------------------------------------------------
class RequestType(models.Model):
    name = models.CharField(max_length=255)  
    description = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name

    class Meta:
        db_table = "crmp_request_types"
        managed = False


#--------------------------------------------------------  
class PaymentPlan(models.Model):
    name = models.CharField(max_length=255)  # Name of the payment plan (e.g., Monthly, Annually)
    description = models.TextField(blank=True, null=True)  
    duration_months = models.IntegerField() 
    def __str__(self):
        return self.name

    class Meta:
        db_table = "crmp_payment_plans" 
        managed = False 


#--------------------------------------------------------


class CoverageType(models.Model):
    name = models.CharField(max_length=255)  
    description = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name

    class Meta:
        db_table = "crmp_coverage_types"
        managed = False

#---------------------------------------------------------


class PolicyBase(models.Model):
    risk_details_form = models.ForeignKey("core_models.Form", related_name="request_policy_risk_details", on_delete=models.CASCADE, blank=True, null=True)
    risk_type = models.ForeignKey("core_models.OpportunityType", related_name="request_policy_risk_type", on_delete=models.CASCADE, blank=True, null=True)
    insurer = models.ForeignKey("core_models.ServiceProvider", related_name="request_policy_insurer", on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey("core_models.Customer", related_name="request_policy_customer", on_delete=models.CASCADE, blank=True, null=True)
    lead = models.ForeignKey("core_models.Opportunity", related_name='request_by', on_delete=models.CASCADE,null=True, blank=True)
    request_by = models.ForeignKey("core_models.User", related_name="request_policy_by", on_delete=models.CASCADE, blank=True, null=True)
    premium_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    quotation_document_size = models.BigIntegerField(blank=True, null=True)
    quotation_document = models.URLField(blank=True, null=True) 
    quotation_document_name = models.CharField(max_length=255, blank=True, null=True)
    request_type = models.ForeignKey(RequestType, on_delete=models.CASCADE)
    product = models.ForeignKey("core_models.VendorProducts", related_name="request_policy_product", on_delete=models.CASCADE, blank=True, null=True)
    payment_mode =  models.ForeignKey(PaymentPlan, related_name="request_policy_policy_plan", on_delete=models.CASCADE, blank=True, null=True)
    coverage_type = models.ForeignKey(CoverageType, related_name="request_policy_coverage_type", on_delete=models.CASCADE, blank=True, null=True)
    sum_insured = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    quotation_issued_date = models.DateField(blank=True, null=True)  
    quotation_expiry_date = models.DateField(blank=True, null=True) 
    policy_start_date = models.DateField() 
    policy_expiry_date = models.DateField() 
    quotation_notes = models.TextField(blank=True, null=True)
    product_group = models.ForeignKey("core_models.ProductGroup", on_delete=models.CASCADE, null=True, blank=True)
    status = models.ForeignKey("core_models.Status", on_delete=models.CASCADE, blank=True, null=True, db_column="status_id")
    sales_agent = models.ForeignKey(
        "core_models.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_agent_policy_base"
    )
    account_manager = models.ForeignKey(
        "core_models.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_manager_policy_base"
    )
    class Meta:
        db_table = "crmp_policy_base"
        managed = False

    def __str__(self):
        return f"Policy {self.policy_request_id} "


#--------------------------------------------------------



class RequestPolicy(models.Model):
    policy_request_id = models.CharField(max_length=255,unique=True)
    policy_request_date = models.DateField(auto_now_add=True)
    status=models.ForeignKey("core_models.Status",related_name="request_policy_status",on_delete=models.CASCADE,default=1)
    entity = models.ForeignKey(Entity, related_name='request_entity', on_delete=models.CASCADE,default=1)
    policy_base=models.ForeignKey(PolicyBase, related_name='policy_reqyst_base', on_delete=models.CASCADE)
    class Meta:
        db_table = "crmp_request_policies"
        managed = False

    def __str__(self):
        return f"Policy {self.policy_request_id} "


    


#--------------------------------------------------------
class IssuedPolicy(models.Model):
    # Policy details 
    brokerage_policy_id = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
    credit_period_days = models.IntegerField()
    credit_age_days = models.IntegerField()
    insurer_invoice_id = models.CharField(max_length=255, blank=False, null=False)  # Insurer Invoice ID
    insurer_policy_id = models.CharField(max_length=255, blank=True, null=True,)  # Insurer Invoice ID
    sum_insured = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    premium_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    policy_effective_date = models.DateField(blank=True, null=True)
    policy_document = models.URLField(blank=True, null=True) 
    policy_document_name = models.CharField(max_length=255, blank=True, null=True)
    policy_request = models.ForeignKey(RequestPolicy, related_name='policy_req', on_delete=models.CASCADE,blank=True,null=True)
    entity = models.ForeignKey(Entity, related_name='policy_entity', on_delete=models.CASCADE,default=1)
    remarks = models.TextField(blank=True, null=True)
    policy_base=models.ForeignKey(PolicyBase, related_name='policy_issued_base', on_delete=models.CASCADE)
    invoice_document = models.URLField(blank=True, null=True) 
    invoice_document_name = models.CharField(max_length=255, blank=True, null=True)
    initial_premium_amount=models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
    is_renewal = models.BooleanField(default=False,null=True,blank=True)
    class Meta:
        db_table = "crmp_issued_policies"
        managed = False

    def __str__(self):
        return f"Policy {self.brokerage_policy_id}"

#--------------------------------------------------------


from django.db import models
from django.utils import timezone

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