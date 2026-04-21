"""
Management command to verify APScheduler is working correctly
"""

from django.core.management.base import BaseCommand
from django.db import connection
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Verify APScheduler is working correctly'

    def handle(self, *args, **options):
        self.stdout.write("=== APScheduler Verification ===")
        
        # Check database tables
        with connection.cursor() as cursor:
            # Check jobs
            cursor.execute("SELECT COUNT(*) FROM django_apscheduler_djangojob")
            job_count = cursor.fetchone()[0]
            
            # Check executions
            cursor.execute("SELECT COUNT(*) FROM django_apscheduler_djangojobexecution")
            exec_count = cursor.fetchone()[0]
            
            self.stdout.write(f"\n1. Database Status:")
            self.stdout.write(f"   - Jobs defined: {job_count}")
            self.stdout.write(f"   - Executions recorded: {exec_count}")
            
            # Check job schedules
            cursor.execute("""
                SELECT id, next_run_time 
                FROM django_apscheduler_djangojob 
                ORDER BY next_run_time
            """)
            jobs = cursor.fetchall()
            
            self.stdout.write(f"\n2. Job Schedule:")
            current_time = datetime.now()
            for job_id, next_run in jobs:
                if next_run:
                    next_run_dt = next_run
                    time_until = next_run_dt - current_time
                    hours_until = time_until.total_seconds() / 3600
                    
                    if hours_until < 0:
                        status = "OVERDUE"
                        color = self.style.ERROR
                    elif hours_until < 1:
                        status = f"SOON ({hours_until:.1f}h)"
                        color = self.style.WARNING
                    else:
                        status = f"OK ({hours_until:.1f}h)"
                        color = self.style.SUCCESS
                    
                    self.stdout.write(f"   - {job_id}: {color(status)} - Next run: {next_run}")
                else:
                    self.stdout.write(f"   - {job_id}: {self.style.ERROR('NO SCHEDULE')}")
            
            # Check recent executions
            if exec_count > 0:
                cursor.execute("""
                    SELECT job_id, status, run_time, duration 
                    FROM django_apscheduler_djangojobexecution 
                    ORDER BY run_time DESC LIMIT 3
                """)
                executions = cursor.fetchall()
                
                self.stdout.write(f"\n3. Recent Executions:")
                for exec_record in executions:
                    job_id, status, run_time, duration = exec_record
                    status_color = self.style.SUCCESS if status == 'Executed' else self.style.ERROR
                    self.stdout.write(f"   - {job_id}: {status_color(status)} at {run_time} (duration: {duration})")
            else:
                self.stdout.write(f"\n3. Recent Executions: {self.style.WARNING('No executions yet')}")
        
        # Overall status
        self.stdout.write(f"\n4. Overall Status:")
        if job_count >= 2 and exec_count >= 0:
            self.stdout.write(self.style.SUCCESS("   ✓ APScheduler is configured correctly"))
            self.stdout.write(self.style.SUCCESS("   ✓ Jobs are scheduled"))
            if exec_count > 0:
                self.stdout.write(self.style.SUCCESS("   ✓ Jobs have executed"))
            else:
                self.stdout.write(self.style.WARNING("   ⚠ Jobs haven't executed yet (wait for scheduled time)"))
        else:
            self.stdout.write(self.style.ERROR("   ✗ APScheduler configuration issues"))
        
        # Next steps
        self.stdout.write(f"\n5. Next Steps:")
        if exec_count == 0:
            self.stdout.write("   - Wait for scheduled execution times")
            self.stdout.write("   - Or test manually: python manage.py run_apscheduler_jobs --job=both")
        else:
            self.stdout.write("   - Monitor logs: Get-Content logs\\task_execution.log -Wait -Tail 10")
            self.stdout.write("   - Check status: python manage.py check_apscheduler")
        
        self.stdout.write(f"\n=== Verification Complete ===")
