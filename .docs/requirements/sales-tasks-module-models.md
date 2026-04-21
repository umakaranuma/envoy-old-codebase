# Sales & Tasks Modules — Django Models Documentation

**Modules:** `envoy_bu_crm_api/sales`, `envoy_bu_crm_api/task`
**Version:** 1.2
**Status:** Draft

---

## 1. Architecture Overview

This project contains **two Django apps**: `sales` and `task`. There is no separate `core` Django app.

The `core_*` database tables are owned and managed externally. This project references them by declaring `managed = False` models inside `sales/models/core_models.py`. Django will never create, alter, or drop these tables.

### Rules

| Rule | Detail |
|---|---|
| `sales/models/core_models.py` | The only place in the project that declares `managed = False` models for every `core_*` table needed — including `Status`, `User`, `Customer`, `Contact`, etc. |
| No migrations for `core_*` tables | `managed = False` prevents Django from touching these tables |
| `task` module owns `Task`, `TaskType`, `TaskConfig` | All three are fully managed (`managed = True`) with their own migrations under the `task` app |
| `sales` module owns `Opportunity`, `OpportunityTask`, `OpportunityStatus`, `OpportunityHealth` | Fully managed with their own migrations |
| **`Task` is NOT in `core_models.py`** | `Task` is owned by the `task` module, lives in `task/models/task.py`, table `crm_tasks` |
| **`TaskConfig.opportunity_status` → `Status`** | Points to the shared `Status` model (`core_status` table, `managed=False` in `sales/models/core_models.py`), not to `OpportunityStatus` |
| All statuses in one table | `core_status` is the single status table for the entire platform. There is **no separate `TaskStatus` model**. The `type` field discriminates between status sets |

---

## 2. Directory Structure

```
envoy_bu_crm_api/
│
├── sales/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── core_models.py          # managed=False mirrors of all core_* tables
│   │   ├── opportunity_status.py   # managed=True  — crm_opportunity_statuses
│   │   ├── opportunity_health.py   # managed=True  — crm_opportunity_health
│   │   ├── opportunity.py          # managed=True  — crm_opportunities
│   │   └── opportunity_task.py     # managed=True  — crm_opportunity_tasks
│   ├── controllers/
│   ├── urls.py
│   └── ...
│
└── task/
    ├── models/
    │   ├── __init__.py
    │   ├── task.py                 # managed=True  — crm_tasks  ← owned by task module
    │   ├── task_type.py            # managed=True  — crm_task_types
    │   └── task_config.py          # managed=True  — crm_task_configs
    ├── controllers/
    ├── urls.py
    └── ...
```

---

## 3. `sales/models/core_models.py`

All `managed = False` models live in this single file. Other modules import from here — they never redeclare these models. `Task` is **not** in this file.

```python
# sales/models/core_models.py

from django.db import models


# ─────────────────────────────────────────────────────────────────────────────
# Status
# Table: core_status
#
# Single status table for ALL modules across the platform.
# Use the `type` field to filter for the correct status set:
#
#   Task statuses:        task_todo | task_inprogress | task_done
#   Quotation statuses:   quotation_draft | quotation_sent | ...
#   Policy statuses:      policy_active | policy_expired | ...
#   Customer statuses:    customer_requested | customer_approved | ...
#
# There is NO separate TaskStatus model. Always use this model.
# ─────────────────────────────────────────────────────────────────────────────

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
        managed = False

    def __str__(self):
        return f"{self.name} ({self.type})"


# ─────────────────────────────────────────────────────────────────────────────
# Entity
# Table: core_entity
# ─────────────────────────────────────────────────────────────────────────────

class Entity(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(
        "User", on_delete=models.RESTRICT,
        related_name="entities_created", null=True, blank=True, default=None
    )
    updated_by = models.ForeignKey(
        "User", on_delete=models.RESTRICT,
        related_name="entities_updated", null=True, blank=True, default=None
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_entity"
        managed = False

    def __str__(self):
        return f"Entity {self.id} - {self.type}"


# ─────────────────────────────────────────────────────────────────────────────
# Module & Action
# Tables: core_modules, core_actions
# ─────────────────────────────────────────────────────────────────────────────

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


class Action(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.CharField(max_length=50, blank=False, null=False)
    action = models.CharField(max_length=50, blank=False, null=False)
    remarks = models.CharField(max_length=320, blank=True, null=True)
    can_be_permission = models.BooleanField(default=False)
    module = models.ForeignKey(Module, on_delete=models.RESTRICT, blank=False, null=False)

    class Meta:
        db_table = "core_actions"
        managed = False

    def __str__(self):
        return f"{self.entity} - {self.action}"


# ─────────────────────────────────────────────────────────────────────────────
# Role & RoleAuthority
# Tables: core_roles, core_role_authorities
# ─────────────────────────────────────────────────────────────────────────────

class Role(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.ForeignKey(Entity, on_delete=models.RESTRICT, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=320, null=True, blank=True)
    system_role = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = "core_roles"
        managed = False

    def __str__(self):
        return self.name

    def get_permissions(self):
        return Action.objects.filter(
            roleauthority__role_id=self.id
        ).select_related("roleauthority")


class RoleAuthority(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)

    class Meta:
        db_table = "core_role_authorities"
        managed = False

    def __str__(self):
        return f"{self.role.name} - {self.action.action}"


# ─────────────────────────────────────────────────────────────────────────────
# User
# Table: core_users
# ─────────────────────────────────────────────────────────────────────────────

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
    entity = models.ForeignKey(Entity, on_delete=models.RESTRICT)

    @property
    def is_authenticated(self):
        return True

    class Meta:
        db_table = "core_users"
        managed = False

    def __str__(self):
        return self.display_name


# ─────────────────────────────────────────────────────────────────────────────
# Contact
# Table: core_contacts
# ─────────────────────────────────────────────────────────────────────────────

class Contact(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False)
    email = models.CharField(max_length=255, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    primary_contact = models.CharField(max_length=20, blank=False, null=True)
    secondary_contact = models.CharField(max_length=20, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    picture = models.TextField(blank=True, null=True)
    duplicated_contact = models.ForeignKey(
        "self", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="duplicates"
    )

    class Meta:
        db_table = "core_contacts"
        managed = False

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Customer
# Table: core_customers
# ─────────────────────────────────────────────────────────────────────────────

class Customer(models.Model):
    CORPORATE = "Corporate"
    PERSONAL = "Personal"
    ACCOUNT_TYPE_CHOICES = [(CORPORATE, "Corporate"), (PERSONAL, "Personal")]

    id = models.AutoField(primary_key=True, unique=True, blank=False)
    code = models.CharField(max_length=6, unique=True, blank=False)
    type = models.CharField(max_length=50, choices=ACCOUNT_TYPE_CHOICES)
    name = models.CharField(max_length=200)
    logo = models.TextField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        "self", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="children"
    )
    primary_contact = models.ForeignKey(
        Contact, on_delete=models.RESTRICT,
        null=False, related_name="primary_accounts"
    )
    entity = models.ForeignKey(
        Entity, on_delete=models.RESTRICT,
        null=True, related_name="customers"
    )

    class Meta:
        db_table = "core_customers"
        managed = False

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Channel
# Table: core_channels
# ─────────────────────────────────────────────────────────────────────────────

class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        db_table = "core_channels"
        managed = False

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Currency
# Table: core_currencies
# ─────────────────────────────────────────────────────────────────────────────

class Currency(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    symbol = models.CharField(max_length=10, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    decimal_digits = models.IntegerField(blank=False, null=False)
    rounding = models.IntegerField(blank=False, null=False)
    code = models.CharField(max_length=100, unique=True, blank=False, null=False)

    class Meta:
        db_table = "core_currencies"
        managed = False

    def __str__(self):
        return f"{self.name} ({self.symbol})"


# ─────────────────────────────────────────────────────────────────────────────
# Country
# Table: core_countries
# ─────────────────────────────────────────────────────────────────────────────

class Country(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)

    class Meta:
        db_table = "core_countries"
        ordering = ["name"]
        managed = False

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# Product
# Table: core_products
# ─────────────────────────────────────────────────────────────────────────────

class Product(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(max_length=100, blank=False, null=False)
    category_id = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "core_products"
        managed = False

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# ProductGroup
# Table: core_product_groups
# ─────────────────────────────────────────────────────────────────────────────

class ProductGroup(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE,
        related_name="product_groups",
        null=True, blank=True, db_column="currency_id"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "core_product_groups"
        managed = False

    def __str__(self):
        return self.name


# ─────────────────────────────────────────────────────────────────────────────
# VendorProducts
# Table: core_vendor_products
# ─────────────────────────────────────────────────────────────────────────────

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
```

---

## 4. `sales/models/opportunity_status.py`

**Table:** `crm_opportunity_statuses` | **Managed:** Yes

CRM pipeline stages (e.g. Prospect, Qualified, Won, Lost). Separate from `core_status`.

```python
# sales/models/opportunity_status.py

from django.db import models


class OpportunityStatus(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, blank=False, null=False)
    description = models.CharField(max_length=320, blank=True, null=True)
    color = models.CharField(max_length=100, default="#eeeeef")
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_statuses"

    def __str__(self):
        return self.name
```

---

## 5. `sales/models/opportunity_health.py`

**Table:** `crm_opportunity_health` | **Managed:** Yes

```python
# sales/models/opportunity_health.py

from django.db import models


class OpportunityHealth(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, blank=False, null=False)
    color = models.CharField(max_length=100, default="#eeeeef")
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_health"

    def __str__(self):
        return self.name
```

---

## 6. `sales/models/opportunity.py`

**Table:** `crm_opportunities` | **Managed:** Yes

```python
# sales/models/opportunity.py

from django.db import models

from envoy_bu_crm_api.sales.models.core_models import (
    Channel, Contact, Country, Currency,
    Customer, Entity, Product, ProductGroup, User, VendorProducts,
)
from envoy_bu_crm_api.sales.models.opportunity_health import OpportunityHealth
from envoy_bu_crm_api.sales.models.opportunity_status import OpportunityStatus


class Opportunity(models.Model):
    CORPORATE = "Corporate"
    PERSONAL = "Personal"
    TYPE_CHOICES = [
        (CORPORATE, "Corporate"),
        (PERSONAL, "Personal"),
    ]
    TRANSACTION_TYPE_CHOICES = [
        ("new", "New"),
        ("renewal", "Renewal"),
    ]

    entity = models.ForeignKey(Entity, on_delete=models.RESTRICT)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL,
        null=True, blank=True, db_column="contact_id"
    )
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, blank=True, null=True)
    last_contacted_date = models.DateField(blank=True, null=True)
    campaign_id = models.BigIntegerField(blank=True, null=True)
    stage = models.ForeignKey(OpportunityStatus, on_delete=models.RESTRICT)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    current_health = models.ForeignKey(
        OpportunityHealth, on_delete=models.SET_NULL,
        blank=True, null=True, related_name="opportunities"
    )
    sales_agent = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="sales_agent_opportunities"
    )
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="created_opportunities"
    )
    account_manager = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="account_manager_opportunities"
    )
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT)
    sort_index = models.FloatField(blank=True, null=True)
    lead_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    sale_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(
        max_length=20, choices=TRANSACTION_TYPE_CHOICES, blank=True, null=True
    )
    issued_policy_id = models.BigIntegerField(blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Product when product_type is 'product'"
    )
    product_group = models.ForeignKey(
        ProductGroup, on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Product group when product_type is 'group'"
    )

    class Meta:
        db_table = "crm_opportunities"

    def __str__(self):
        return self.title
```

---

## 7. `sales/models/opportunity_task.py`

**Table:** `crm_opportunity_tasks` | **Managed:** Yes

Junction model linking a `Task` to an `Opportunity`. Uses a string FK `"task.Task"` to avoid circular imports.

```python
# sales/models/opportunity_task.py

from django.db import models


class OpportunityTask(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(
        "task.Task", on_delete=models.RESTRICT, related_name="opportunity_tasks"
    )
    opportunity = models.ForeignKey(
        "sales.Opportunity", on_delete=models.CASCADE
    )
    task_config = models.ForeignKey(
        "task.TaskConfig", on_delete=models.SET_NULL, blank=True, null=True
    )

    class Meta:
        db_table = "crm_opportunity_tasks"

    def __str__(self):
        return f"OpportunityTask: {self.opportunity} → {self.task}"
```

---

## 8. `sales/models/__init__.py`

```python
# sales/models/__init__.py

# Unmanaged mirrors of external core_* tables
from .core_models import (
    Status,
    Entity,
    Module,
    Action,
    Role,
    RoleAuthority,
    User,
    Contact,
    Customer,
    Channel,
    Currency,
    Country,
    Product,
    ProductGroup,
    VendorProducts,
)

# Sales-owned managed models
from .opportunity_status import OpportunityStatus
from .opportunity_health import OpportunityHealth
from .opportunity import Opportunity
from .opportunity_task import OpportunityTask
```

---

## 9. `task/models/task.py`

**Table:** `crm_tasks` | **Managed:** Yes

Owned by the `task` module. `status` points to the shared `Status` model (`core_status` table, `managed=False`) via a string FK to `"sales.Status"`.

```python
# task/models/task.py

from django.db import models


class Task(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    code = models.CharField(max_length=20, blank=False, null=False)
    task = models.CharField(max_length=250, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(
        "sales.User", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="assigned_tasks"
    )
    assigned_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    # Points to core_status (managed=False in sales/models/core_models.py)
    # Filter task statuses by type: task_todo | task_inprogress | task_done
    status = models.ForeignKey(
        "sales.Status", on_delete=models.RESTRICT, related_name="tasks"
    )
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_tasks"

    def __str__(self):
        return f"{self.task} - {self.status.name if self.status else 'No Status'}"
```

---

## 10. `task/models/task_type.py`

**Table:** `crm_task_types` | **Managed:** Yes

```python
# task/models/task_type.py

from django.db import models


class TaskType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = "crm_task_types"

    def __str__(self):
        return self.name
```

---

## 11. `task/models/task_config.py`

**Table:** `crm_task_configs` | **Managed:** Yes

`opportunity_status` points to the shared `Status` model (`core_status` table, `managed=False`) via `"sales.Status"`. Filter by the relevant opportunity `type` codes when querying.

```python
# task/models/task_config.py

from django.db import models


class TaskConfig(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.CharField(max_length=250, blank=False, null=False)
    code = models.CharField(max_length=80, unique=True, blank=False, null=False)
    task_type = models.ForeignKey(
        "task.TaskType",
        on_delete=models.RESTRICT,
        related_name="task_configs"
    )
    # Points to core_status (managed=False in sales/models/core_models.py)
    # This references the opportunity stage status, not a task status
    opportunity_status = models.ForeignKey(
        "sales.Status",
        on_delete=models.RESTRICT,
        related_name="task_configs"
    )
    expected_days = models.IntegerField(default=1, blank=True, null=True)
    reminder_expected_days = models.IntegerField(blank=True, null=True)
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_task_configs"

    def __str__(self):
        return self.code
```

---

## 12. `task/models/__init__.py`

```python
# task/models/__init__.py

from .task import Task
from .task_type import TaskType
from .task_config import TaskConfig
```

---

## 13. Complete Model Reference

### `sales` App

| Model | File | Table | Managed |
|---|---|---|---|
| `Status` | `core_models.py` | `core_status` | No |
| `Entity` | `core_models.py` | `core_entity` | No |
| `Module` | `core_models.py` | `core_modules` | No |
| `Action` | `core_models.py` | `core_actions` | No |
| `Role` | `core_models.py` | `core_roles` | No |
| `RoleAuthority` | `core_models.py` | `core_role_authorities` | No |
| `User` | `core_models.py` | `core_users` | No |
| `Contact` | `core_models.py` | `core_contacts` | No |
| `Customer` | `core_models.py` | `core_customers` | No |
| `Channel` | `core_models.py` | `core_channels` | No |
| `Currency` | `core_models.py` | `core_currencies` | No |
| `Country` | `core_models.py` | `core_countries` | No |
| `Product` | `core_models.py` | `core_products` | No |
| `ProductGroup` | `core_models.py` | `core_product_groups` | No |
| `VendorProducts` | `core_models.py` | `core_vendor_products` | No |
| `OpportunityStatus` | `opportunity_status.py` | `crm_opportunity_statuses` | **Yes** |
| `OpportunityHealth` | `opportunity_health.py` | `crm_opportunity_health` | **Yes** |
| `Opportunity` | `opportunity.py` | `crm_opportunities` | **Yes** |
| `OpportunityTask` | `opportunity_task.py` | `crm_opportunity_tasks` | **Yes** |

### `task` App

| Model | File | Table | Managed | Notes |
|---|---|---|---|---|
| `Task` | `task.py` | `crm_tasks` | **Yes** | `status` → `"sales.Status"` (core_status) |
| `TaskType` | `task_type.py` | `crm_task_types` | **Yes** | |
| `TaskConfig` | `task_config.py` | `crm_task_configs` | **Yes** | `opportunity_status` → `"sales.Status"` (core_status) |

---

## 14. FK String Reference Summary

Because `task` depends on `sales` (for `Status` and `User`), all cross-app FKs use string references to avoid circular imports.

| Model | Field | String FK | Resolves To |
|---|---|---|---|
| `Task` | `assigned_to` | `"sales.User"` | `core_users` (managed=False) |
| `Task` | `status` | `"sales.Status"` | `core_status` (managed=False) |
| `TaskConfig` | `task_type` | `"task.TaskType"` | `crm_task_types` (managed=True) |
| `TaskConfig` | `opportunity_status` | `"sales.Status"` | `core_status` (managed=False) |
| `OpportunityTask` | `task` | `"task.Task"` | `crm_tasks` (managed=True) |
| `OpportunityTask` | `task_config` | `"task.TaskConfig"` | `crm_task_configs` (managed=True) |

---

## 15. Status Type Code Reference

`core_status` is the single status table for the entire platform. Filter by `type` — never create a separate status model.

| Status Group | `type` values | Referenced By |
|---|---|---|
| Task | `task_todo`, `task_inprogress`, `task_done` | `Task.status` |
| Quotation | `quotation_draft`, `quotation_sent`, `quotation_inprogress`, `quotation_rejected`, `quotation_pending`, `quotation_confirmed`, `quotation_expired` | Quotation module |
| Policy | `policy_requested`, `pol_pending_iss`, `policy_active`, `pol_due_renewal`, `policy_expired`, `pol_renewal_progress`, `policy_cancelled`, `policy_renewed` | Policy module |
| Customer | `customer_requested`, `customer_approved`, `customer_rejected` | Customer module |
| Payment | `payment_pending`, `pay_partially_paid`, `payment_paid`, `payment_failed`, `payment_refunded` | Payment module |

**Example — filtering task statuses at query time:**

```python
from envoy_bu_crm_api.sales.models.core_models import Status

# All task statuses ordered by sort index
task_statuses = Status.objects.filter(type__startswith="task_").order_by("sort_index")

# Fetch a specific status by its type code
todo_status = Status.objects.get(type="task_todo")
```

---

## 16. `INSTALLED_APPS` Order

`sales` must appear before `task` because `task` models reference `"sales.Status"` and `"sales.User"` via string FKs.

```python
# settings/base.py

INSTALLED_APPS = [
    ...
    "envoy_bu_crm_api.sales",   # Must come first — task references sales.Status and sales.User
    "envoy_bu_crm_api.task",    # References sales.Status, sales.User, and task.TaskType
    ...
]
```

---

*Document prepared for the Envoy CRM backend. Subject to revision as the module evolves.*
