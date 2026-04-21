from django.core.management.base import BaseCommand
from envoy_bu_policy_api.policy.tasks import update_policy_statuses

class Command(BaseCommand):
    help = 'Test policy status update task'

    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            choices=['policy-status', 'test-direct'],
            default='test-direct',
            help='Which task to run (policy-status or test-direct)'
        )

    def handle(self, *args, **options):
        task_type = options['task']
        
        if task_type == 'policy-status':
            self.stdout.write('Running policy status update task...')
            try:
                result = update_policy_statuses.delay()
                self.stdout.write(
                    self.style.SUCCESS(f'Policy status update task queued with ID: {result.id}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to queue policy status task: {e}')
                )
                
        elif task_type == 'test-direct':
            self.stdout.write('Testing policy status update task directly...')
            try:
                # Test policy status update task directly
                update_policy_statuses()
                self.stdout.write(
                    self.style.SUCCESS('Policy status update task executed successfully!')
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error executing task directly: {e}')
                )
        
        self.stdout.write(
            self.style.WARNING('Note: Task runs every 12 hours automatically!')
        )