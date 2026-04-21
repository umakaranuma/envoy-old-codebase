from django.db import models




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






