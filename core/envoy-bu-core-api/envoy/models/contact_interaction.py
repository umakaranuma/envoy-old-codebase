# from django.db import models
# from .contact import Contact


# class ContactInteraction(models.Model):
#     contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
#     channel = models.ForeignKey(
#         "envoy.Channel", on_delete=models.RESTRICT, null=True, blank=True
#     )
#     notes = models.TextField()
#     # task = models.ForeignKey("Task", on_delete=models.SET_NULL, null=True, blank=True)
#     contact_by = models.ForeignKey(
#         "envoy.User", on_delete=models.RESTRICT, null=True, blank=True
#     )
#     sales_status = models.ForeignKey(
#         "envoy.SalesStatus", on_delete=models.SET_NULL, null=True, blank=True
#     )

#     def __str__(self):
#         return f"Interaction with {self.contact.name} via {self.channel}"
