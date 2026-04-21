from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Check APScheduler status and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start',
            action='store_true',
            help='Start the scheduler if not running'
        )
        parser.add_argument(
            '--stop',
            action='store_true',
            help='Stop the scheduler if running'
        )

    def handle(self, *args, **options):
        start_scheduler = options['start']
        stop_scheduler = options['stop']
        
        self.stdout.write('=== APScheduler Status Check ===')
        
        # Check configuration
        self.check_configuration()
        
        # Check scheduler status
        self.check_scheduler_status()
        
        # Handle start/stop commands
        if start_scheduler:
            self.start_scheduler()
        elif stop_scheduler:
            self.stop_scheduler()

    def check_configuration(self):
        """
        Check APScheduler configuration
        """
        self.stdout.write('\n1. Configuration Check:')
        
        try:
            from django.conf import settings
            
            auto_start = getattr(settings, 'APSCHEDULER_AUTO_START', False)
            self.stdout.write(f"   Auto-start enabled: {auto_start}")
            
            if auto_start:
                self.stdout.write(
                    self.style.SUCCESS("   ✓ APScheduler will start automatically with Django")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("   ⚠ APScheduler auto-start is disabled")
                )
                self.stdout.write("   To enable: Set APSCHEDULER_AUTO_START=true in environment")
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ✗ Configuration error: {e}")
            )

    def check_scheduler_status(self):
        """
        Check if scheduler is running
        """
        self.stdout.write('\n2. Scheduler Status:')
        
        try:
            from envoy_bu_policy_api.policy.scheduler import is_scheduler_running, get_scheduler
            
            scheduler = get_scheduler()
            is_running = is_scheduler_running()
            
            if scheduler is None:
                self.stdout.write("   Status: Not initialized")
                self.stdout.write("   Reason: Auto-start disabled or error during initialization")
            elif is_running:
                self.stdout.write(
                    self.style.SUCCESS("   ✓ Scheduler is running")
                )
                
                # Show job information
                jobs = scheduler.get_jobs()
                self.stdout.write(f"   Active jobs: {len(jobs)}")
                for job in jobs:
                    self.stdout.write(f"     - {job.name} (ID: {job.id})")
                    
            else:
                self.stdout.write(
                    self.style.WARNING("   ⚠ Scheduler is not running")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ✗ Status check error: {e}")
            )

    def start_scheduler(self):
        """
        Start the scheduler
        """
        self.stdout.write('\n3. Starting Scheduler:')
        
        try:
            from envoy_bu_policy_api.policy.scheduler import start_scheduler
            
            if start_scheduler():
                self.stdout.write(
                    self.style.SUCCESS("   ✓ Scheduler started successfully")
                )
            else:
                self.stdout.write(
                    self.style.WARNING("   ⚠ Scheduler start failed or already running")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ✗ Error starting scheduler: {e}")
            )

    def stop_scheduler(self):
        """
        Stop the scheduler
        """
        self.stdout.write('\n3. Stopping Scheduler:')
        
        try:
            from envoy_bu_policy_api.policy.scheduler import stop_scheduler
            
            stop_scheduler()
            self.stdout.write(
                self.style.SUCCESS("   ✓ Scheduler stopped successfully")
            )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"   ✗ Error stopping scheduler: {e}")
            )
