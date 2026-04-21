from django.core.management.base import BaseCommand

from envoy.models.status import Status

class Command(BaseCommand):
    help = 'Seed statuses into the database'

    def handle(self, *args, **kwargs):
        statuses = [
            ("Draft", "#d3d3d3"),
            ("Submitted", "#6495ed"),
            ("Processing", "#ffa500"),
            ("Approved", "#228b22"),
            ("Settled", "#20b2aa"),
            ("Rejected", "#dc143c"),
        ]

        for index, (name, color) in enumerate(statuses, start=1):
            Status.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'{name} status for Claim',
                    'type': 'Claim Status',
                    'module': 'Claim',
                    'color': color,
                    'sort_index': index
                }
            )
        self.stdout.write(self.style.SUCCESS('Statuses seeded successfully.'))


# from django.core.management.base import BaseCommand
# from core.models import Status


# STATUS_DATA = [
#     {
#         "name": "Draft",
#         "description": "Draft status for Claim",
#         "type": "Claim Status",
#         "module": "Claim",
#         "color": "#d3d3d3",
#         "sort_index": 1
#     },
#     {
#         "name": "Submitted",
#         "description": "Submitted status for Claim",
#         "type": "Claim Status",
#         "module": "Claim",
#         "color": "#6495ed",
#         "sort_index": 2
#     },
#     {
#         "name": "Processing",
#         "description": "Processing status for Claim",
#         "type": "Claim Status",
#         "module": "Claim",
#         "color": "#ffa500",
#         "sort_index": 3
#     },
#     {
#         "name": "Approved",
#         "description": "Approved status for Claim",
#         "type": "Claim Status",
#         "module": "Claim",
#         "color": "#228b22",
#         "sort_index": 4
#     },
#     {
#         "name": "Settled",
#         "description": "Settled status for Claim",
#         "type": "Claim Status",
#         "module": "Claim",
#         "color": "#20b2aa",
#         "sort_index": 5
#     },
#     {
#         "name": "Rejected",
#         "description": "Rejected status for Claim",
#         "type": "Claim Status",
#         "module": "Claim",
#         "color": "#dc143c",
#         "sort_index": 6
#     }
# ]


# class Command(BaseCommand):
#     help = 'Seed statuses into the database'

#     def handle(self, *args, **kwargs):
#         for status in STATUS_DATA:
#             Status.objects.get_or_create(
#                 name=status['name'],
#                 defaults=status
#             )
#         self.stdout.write(self.style.SUCCESS('Statuses seeded successfully.'))
