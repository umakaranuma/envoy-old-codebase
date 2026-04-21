from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Test APScheduler tasks execution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            choices=['policy-status', 'credit-age', 'both'],
            default='both',
            help='Which task to test (policy-status, credit-age, or both)'
        )

    def handle(self, *args, **options):
        task_type = options['task']
        
        self.stdout.write('=== APScheduler Task Testing ===')
        
        if task_type in ['policy-status', 'both']:
            self.test_policy_status_task()
            
        if task_type in ['credit-age', 'both']:
            self.test_credit_age_task()
            
        self.stdout.write(
            self.style.SUCCESS('APScheduler task testing completed!')
        )

    def test_policy_status_task(self):
        """
        Test the policy status update task
        """
        self.stdout.write('\n1. Testing Policy Status Update Task...')
        
        try:
            from envoy_bu_policy_api.policy.apscheduler_tasks import update_policy_statuses_apscheduler
            
            self.stdout.write('   Running policy status update task...')
            update_policy_statuses_apscheduler()
            
            self.stdout.write(
                self.style.SUCCESS('   ✓ Policy status update task completed successfully')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Policy status update task failed: {e}')
            )

    def test_credit_age_task(self):
        """
        Test the credit age update task
        """
        self.stdout.write('\n2. Testing Credit Age Update Task...')
        
        try:
            from envoy_bu_policy_api.policy.apscheduler_tasks import update_credit_ages_apscheduler
            
            self.stdout.write('   Running credit age update task...')
            update_credit_ages_apscheduler()
            
            self.stdout.write(
                self.style.SUCCESS('   ✓ Credit age update task completed successfully')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'   ✗ Credit age update task failed: {e}')
            )
