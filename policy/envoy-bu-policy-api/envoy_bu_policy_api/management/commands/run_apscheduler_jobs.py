"""
Management command to run APScheduler jobs immediately for testing
"""

from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime

class Command(BaseCommand):
    help = 'Run APScheduler jobs immediately for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--job',
            type=str,
            choices=['policy_status', 'credit_age', 'both'],
            default='both',
            help='Which job to run (default: both)'
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=5,
            help='Test interval in minutes (default: 5)'
        )

    def handle(self, *args, **options):
        job_type = options['job']
        interval_minutes = options['interval']
        
        self.stdout.write(f"=== Running APScheduler Jobs Immediately ===")
        self.stdout.write(f"Job: {job_type}")
        self.stdout.write(f"Test Interval: {interval_minutes} minutes")
        self.stdout.write(f"Started at: {datetime.now().isoformat()}")
        
        try:
            from envoy_bu_policy_api.policy.apscheduler_tasks import (
                update_policy_statuses_apscheduler,
                update_credit_ages_apscheduler
            )
            
            # Create a test scheduler
            scheduler = BlockingScheduler()
            scheduler.add_jobstore(DjangoJobStore(), "default")
            
            jobs_added = []
            
            if job_type in ['policy_status', 'both']:
                scheduler.add_job(
                    update_policy_statuses_apscheduler,
                    trigger=IntervalTrigger(minutes=interval_minutes),
                    id='test_policy_status',
                    name='Test Policy Status Update',
                    replace_existing=True,
                    max_instances=1,
                    misfire_grace_time=60,
                )
                jobs_added.append('Policy Status Update')
                self.stdout.write(f"✓ Added Policy Status job (every {interval_minutes} minutes)")
            
            if job_type in ['credit_age', 'both']:
                scheduler.add_job(
                    update_credit_ages_apscheduler,
                    trigger=IntervalTrigger(minutes=interval_minutes),
                    id='test_credit_age',
                    name='Test Credit Age Update',
                    replace_existing=True,
                    max_instances=1,
                    misfire_grace_time=60,
                )
                jobs_added.append('Credit Age Update')
                self.stdout.write(f"✓ Added Credit Age job (every {interval_minutes} minutes)")
            
            # Run jobs immediately first
            self.stdout.write(f"\n=== Running Jobs Immediately ===")
            
            if job_type in ['policy_status', 'both']:
                self.stdout.write("Running Policy Status Update...")
                try:
                    update_policy_statuses_apscheduler()
                    self.stdout.write(self.style.SUCCESS("✓ Policy Status Update completed"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"✗ Policy Status Update failed: {str(e)}"))
            
            if job_type in ['credit_age', 'both']:
                self.stdout.write("Running Credit Age Update...")
                try:
                    update_credit_ages_apscheduler()
                    self.stdout.write(self.style.SUCCESS("✓ Credit Age Update completed"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"✗ Credit Age Update failed: {str(e)}"))
            
            # Check execution records
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM django_apscheduler_djangojobexecution")
                exec_count = cursor.fetchone()[0]
                self.stdout.write(f"\n=== Execution Records ===")
                self.stdout.write(f"Total executions: {exec_count}")
                
                if exec_count > 0:
                    cursor.execute("""
                        SELECT job_id, status, run_time, duration 
                        FROM django_apscheduler_djangojobexecution 
                        ORDER BY run_time DESC LIMIT 3
                    """)
                    executions = cursor.fetchall()
                    self.stdout.write("Recent executions:")
                    for exec_record in executions:
                        job_id, status, run_time, duration = exec_record
                        self.stdout.write(f"  - {job_id}: {status} at {run_time} (duration: {duration})")
            
            self.stdout.write(f"\n=== Test Complete ===")
            self.stdout.write(f"Jobs tested: {', '.join(jobs_added)}")
            self.stdout.write(f"Completed at: {datetime.now().isoformat()}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error: {str(e)}"))
            import traceback
            self.stdout.write(traceback.format_exc())
