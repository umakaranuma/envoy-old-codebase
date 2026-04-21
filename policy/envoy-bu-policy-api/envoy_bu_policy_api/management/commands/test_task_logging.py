"""
Management command to test task logging functionality
"""

from django.core.management.base import BaseCommand
import logging
from datetime import datetime

class Command(BaseCommand):
    help = 'Test task logging functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--task',
            type=str,
            choices=['policy_status', 'credit_age', 'both'],
            default='both',
            help='Which task to test (default: both)'
        )

    def handle(self, *args, **options):
        task_type = options['task']
        
        self.stdout.write(f"Testing task logging for: {task_type}")
        self.stdout.write(f"Test started at: {datetime.now().isoformat()}")
        
        # Test the task loggers
        task_logger = logging.getLogger('policy_tasks')
        scheduler_logger = logging.getLogger('apscheduler_tasks')
        
        if task_type in ['policy_status', 'both']:
            self.stdout.write("Testing policy status task logging...")
            
            # Test task logger
            task_logger.info("[TEST] Testing policy task logger")
            task_logger.info("[TEST_INFO] Policy status task test started")
            task_logger.info("[TEST_STEP] Step 1: Testing status updates")
            task_logger.info("[TEST_RESULT] Test completed successfully")
            task_logger.info("[TEST_END] Policy status task test ended")
            
            # Test scheduler logger
            scheduler_logger.info("[TEST] Testing policy scheduler logger")
            scheduler_logger.info("[SCHEDULER_START] Test scheduler task started")
            scheduler_logger.info("[SCHEDULER_SUCCESS] Test scheduler task completed")
            scheduler_logger.info("[SCHEDULER_END] Test scheduler task ended")
        
        if task_type in ['credit_age', 'both']:
            self.stdout.write("Testing credit age task logging...")
            
            # Test task logger
            task_logger.info("[TEST] Testing credit age task logger")
            task_logger.info("[TEST_INFO] Credit age task test started")
            task_logger.info("[TEST_STEP] Step 1: Testing credit age updates")
            task_logger.info("[TEST_PROGRESS] Processed 100/500 policies")
            task_logger.info("[TEST_RESULT] Test completed successfully")
            task_logger.info("[TEST_END] Credit age task test ended")
            
            # Test scheduler logger
            scheduler_logger.info("[TEST] Testing credit age scheduler logger")
            scheduler_logger.info("[SCHEDULER_START] Test credit age scheduler started")
            scheduler_logger.info("[SCHEDULER_SUCCESS] Test credit age scheduler completed")
            scheduler_logger.info("[SCHEDULER_END] Test credit age scheduler ended")
        
        self.stdout.write(
            self.style.SUCCESS(
                f"Task logging test completed for: {task_type}\n"
                f"Check logs/task_execution.log for detailed output"
            )
        )
