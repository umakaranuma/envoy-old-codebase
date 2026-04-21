# from django.db import models

# from envoy_bu_crm_api.task.models.Opportunity import Opportunity
# from envoy_bu_crm_api.task.models.TaskConfig import TaskConfig



# class Channel(models.Model):
#     name = models.CharField(max_length=255)
#     entity = models.CharField(max_length=50)  # Example: Task, Contact

#     def __str__(self):
#         return self.name


# class SalesStatus(models.Model):
#     LEAD = "LEAD"
#     PROSPECT = "PROSPECT"
#     QUALIFIED = "QUALIFIED"
#     WON = "WON"
#     LOSS = "LOSS"

#     STATUS_CHOICES = [
#         (LEAD, "Lead"),
#         (PROSPECT, "Prospect"),
#         (QUALIFIED, "Qualified"),
#         (WON, "Won"),
#         (LOSS, "Loss"),
#     ]

#     name = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     status = models.CharField(max_length=50)
#     type = models.CharField(max_length=20, choices=STATUS_CHOICES)

#     def __str__(self):
#         return f"{self.name} - {self.type}"


# class User(models.Model):
#     id = models.AutoField(primary_key=True, unique=True, blank=False)
#     title = models.CharField(max_length=100, null=True)
#     first_name = models.CharField(max_length=80, null=True)
#     last_name = models.CharField(max_length=80, null=True)
#     display_name = models.CharField(max_length=80, blank=False)
#     email = models.EmailField(max_length=254, blank=False)
#     contact_no = models.CharField(max_length=80, null=True)
#     picture = models.TextField(max_length=300, null=True)
#     idp_user_id = models.CharField(max_length=255)
#     role_id = models.ForeignKey("core.Role", on_delete=models.RESTRICT, blank=False)
#     entity_id = models.ForeignKey("core.Entity", on_delete=models.RESTRICT, blank=False)

#     def __str__(self):
#         return self.first_name


# class Entity(models.Model):
#     id = models.AutoField(primary_key=True, unique=True, blank=False)
#     type = models.CharField(max_length=100)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now_add=True)
#     created_by_id = models.ForeignKey(
#         "core.User",
#         on_delete=models.RESTRICT,
#         related_name="created_entities",
#         null=True,
#         blank=True,
#     )
#     updated_by_id = models.ForeignKey(
#         "core.User",
#         on_delete=models.RESTRICT,
#         related_name="updated_entities",
#         null=True,
#         blank=True,
#     )

#     def __str__(self):
#         return self.type


# class Role(models.Model):
#     id = models.AutoField(primary_key=True)
#     entity_id = models.ForeignKey(
#         Entity, on_delete=models.RESTRICT, null=True, blank=True
#     )
#     name = models.CharField(max_length=255)
#     description = models.CharField(max_length=320)
#     system_role = models.CharField(max_length=50, null=True)

#     def __str__(self):
#         return self.name


# class Customer(models.Model):
#     CATEGORY_CHOICES = [("Corporate", "Corporate"), ("Individual", "Individual")]

#     id = models.AutoField(primary_key=True)
#     category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
#     title = models.CharField(max_length=20)
#     name = models.CharField(max_length=255)
#     picture = models.TextField(null=True, blank=True)
#     contact_no = models.CharField(max_length=20, null=True, blank=True)
#     email = models.CharField(max_length=255, null=True, blank=True)
#     remarks = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.name




# ###  Task Status Model
# class TaskStatus(models.Model):
#     STATUS_CHOICES = [
#         ('Todo', 'Todo'),
#         ('Inprogress', 'Inprogress'),
#         ('Done', 'Done'),
#     ]

#     id = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=255)
#     description = models.TextField(null=True, blank=True)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)
#     type = models.CharField(max_length=20, choices=STATUS_CHOICES)

#     def __str__(self):
#         return f"{self.name} - {self.status}"

# ###  Task Model
# class Task(models.Model):
#     id = models.AutoField(primary_key=True)
#     code = models.CharField(max_length=20, null=True, blank=True)
#     opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, blank=True)
#     task = models.CharField(max_length=250)
#     task_config = models.ForeignKey(TaskConfig, on_delete=models.RESTRICT, related_name='tasks')
#     description = models.TextField(null=True, blank=True)
#     assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
#     assigned_date = models.DateTimeField(null=True, blank=True)
#     start_date = models.DateTimeField(null=True, blank=True)
#     due_date = models.DateTimeField(null=True, blank=True)
#     task_status = models.ForeignKey(TaskStatus, on_delete=models.CASCADE)
#     order = models.IntegerField(null=True, blank=True)

#     def __str__(self):
#         return f"Task {self.id} - {self.task}"

# ###  Task Status History Model
# class TaskStatusHistory(models.Model):
#     id = models.AutoField(primary_key=True)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="status_histories")
#     task_status = models.ForeignKey(TaskStatus, on_delete=models.CASCADE)
#     created_at = models.DateTimeField(auto_now_add=True)
#     changed_by = models.ForeignKey(User, on_delete=models.RESTRICT)
#     remark = models.TextField(null=True, blank=True)

#     def __str__(self):
#         return f"Task {self.task.id} - Status {self.task_status.name}"

# ###  Task Assignee History Model
# class TaskAssigneeHistory(models.Model):
#     id = models.AutoField(primary_key=True)
#     task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="assignee_histories")
#     from_assigned = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="from_assignee_histories")
#     to_assigned = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="to_assignee_histories")
#     remark = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     changed_by = models.ForeignKey(User, on_delete=models.RESTRICT)

#     def __str__(self):
#         return f"Task {self.task.id} - Changed Assignee"

# class Opportunity(models.Model):
#     id = models.AutoField(primary_key=True)

#     def __str__(self):
#         return f"Opportunity {self.id}"
