from django.core.management.base import BaseCommand
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Run APScheduler scheduler for production task scheduling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test',
            action='store_true',
            help='Test the scheduler by running jobs once and exiting'
        )

    def handle(self, *args, **options):
        test_mode = options['test']
        
        if test_mode:
            self.stdout.write('Testing APScheduler jobs...')
            self.test_apscheduler_jobs()
        else:
            self.stdout.write('Starting APScheduler scheduler...')
            self.run_apscheduler_scheduler()

    def test_apscheduler_jobs(self):
        """
        Test APScheduler jobs by running them once
        """
        try:
            from envoy_bu_policy_api.policy.apscheduler_tasks import (
                update_policy_statuses_apscheduler,
                update_credit_ages_apscheduler
            )
            
            self.stdout.write('Testing policy status update job...')
            update_policy_statuses_apscheduler()
            self.stdout.write(
                self.style.SUCCESS('✓ Policy status update job completed')
            )
            
            self.stdout.write('Testing credit age update job...')
            update_credit_ages_apscheduler()
            self.stdout.write(
                self.style.SUCCESS('✓ Credit age update job completed')
            )
            
            self.stdout.write(
                self.style.SUCCESS('All APScheduler jobs tested successfully!')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error testing APScheduler jobs: {e}')
            )

    def run_apscheduler_scheduler(self):
        """
        Run the APScheduler scheduler in blocking mode
        """
        try:
            from envoy_bu_policy_api.policy.apscheduler_tasks import run_apscheduler_scheduler
            
            self.stdout.write('Starting APScheduler scheduler...')
            self.stdout.write('Press Ctrl+C to stop')
            
            # This will block and run the scheduler
            run_apscheduler_scheduler()
            
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('APScheduler scheduler stopped by user')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error running APScheduler scheduler: {e}')
            )
