"""
Management command to debug APScheduler job execution
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Debug APScheduler job execution and scheduling'

    def add_arguments(self, parser):
        parser.add_argument(
            '--test-short',
            action='store_true',
            help='Test with short intervals (1 minute)'
        )

    def handle(self, *args, **options):
        self.stdout.write("=== APScheduler Job Debug ===")
        
        # Check current jobs in database
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, next_run_time, job_state FROM django_apscheduler_djangojob")
            jobs = cursor.fetchall()
            
            self.stdout.write(f"\n1. Current Jobs in Database: {len(jobs)}")
            for job in jobs:
                job_id, next_run, job_state = job
                self.stdout.write(f"   - Job ID: {job_id}")
                self.stdout.write(f"   - Next Run: {next_run}")
                
                # Parse job state to get trigger info
                import pickle
                try:
                    state = pickle.loads(job_state)
                    trigger = state.get('trigger', {})
                    if 'interval' in trigger:
                        interval = trigger['interval']
                        self.stdout.write(f"   - Interval: {interval}")
                except:
                    self.stdout.write(f"   - Job State: (unable to parse)")
            
            # Check execution history
            cursor.execute("SELECT COUNT(*) FROM django_apscheduler_djangojobexecution")
            exec_count = cursor.fetchone()[0]
            self.stdout.write(f"\n2. Execution History: {exec_count} records")
            
            if exec_count > 0:
                cursor.execute("""
                    SELECT job_id, status, run_time, duration 
                    FROM django_apscheduler_djangojobexecution 
                    ORDER BY run_time DESC LIMIT 5
                """)
                executions = cursor.fetchall()
                self.stdout.write("   Recent executions:")
                for exec_record in executions:
                    job_id, status, run_time, duration = exec_record
                    self.stdout.write(f"   - {job_id}: {status} at {run_time} (duration: {duration})")
        
        # Test with short intervals if requested
        if options['test_short']:
            self.stdout.write("\n3. Testing with Short Intervals (1 minute)...")
            
            try:
                from envoy_bu_policy_api.policy.apscheduler_tasks import (
                    update_policy_statuses_apscheduler,
                    update_credit_ages_apscheduler
                )
                
                # Create a test scheduler
                scheduler = BlockingScheduler()
                scheduler.add_jobstore(DjangoJobStore(), "default")
                
                # Add test jobs with 1-minute intervals
                scheduler.add_job(
                    update_policy_statuses_apscheduler,
                    trigger=IntervalTrigger(minutes=1),
                    id='test_policy_status',
                    name='Test Policy Status Update',
                    replace_existing=True,
                    max_instances=1,
                    misfire_grace_time=30,
                )
                
                scheduler.add_job(
                    update_credit_ages_apscheduler,
                    trigger=IntervalTrigger(minutes=1),
                    id='test_credit_age',
                    name='Test Credit Age Update',
                    replace_existing=True,
                    max_instances=1,
                    misfire_grace_time=30,
                )
                
                self.stdout.write("   ✓ Test jobs added with 1-minute intervals")
                self.stdout.write("   ⚠️  Note: This will run for 2 minutes then stop")
                
                # Start scheduler for 2 minutes
                import threading
                import time
                
                def run_scheduler():
                    scheduler.start()
                
                scheduler_thread = threading.Thread(target=run_scheduler)
                scheduler_thread.daemon = True
                scheduler_thread.start()
                
                # Wait 2 minutes
                time.sleep(120)
                
                scheduler.shutdown()
                self.stdout.write("   ✓ Test completed")
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"   ✗ Test failed: {str(e)}"))
        
        # Check if jobs should have run by now
        self.stdout.write("\n4. Job Schedule Analysis:")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, next_run_time 
                FROM django_apscheduler_djangojob 
                WHERE next_run_time < NOW()
            """)
            overdue_jobs = cursor.fetchall()
            
            if overdue_jobs:
                self.stdout.write(f"   ⚠️  {len(overdue_jobs)} jobs are overdue:")
                for job in overdue_jobs:
                    self.stdout.write(f"   - {job[0]}: should have run at {job[1]}")
            else:
                self.stdout.write("   ✓ No overdue jobs")
        
        self.stdout.write("\n=== Debug Complete ===")
        self.stdout.write("To test with short intervals: python manage.py debug_apscheduler --test-short")
