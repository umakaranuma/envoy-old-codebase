# from django.db import models


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
