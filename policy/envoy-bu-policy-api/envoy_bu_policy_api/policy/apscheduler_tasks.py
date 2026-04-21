"""
Django APScheduler Tasks
Wrapper functions for Celery tasks to be used with APScheduler in production
"""

import logging
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from django.conf import settings
from datetime import datetime

logger = logging.getLogger(__name__)

# Create a separate logger for APScheduler execution logs
scheduler_logger = logging.getLogger('apscheduler_tasks')

def update_policy_statuses_apscheduler():
    """
    APScheduler wrapper for update_policy_statuses Celery task
    Runs every 12 hours to update policy statuses based on expiry dates
    """
    scheduler_start_time = datetime.now()
    scheduler_id = f"apscheduler_policy_status_{scheduler_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        scheduler_logger.info(f"[SCHEDULER_START] {scheduler_id} - APScheduler Policy Status Update Task Started")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Start Time: {scheduler_start_time.isoformat()}")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Trigger: Every 1 hour")
        
        # Import and call the original Celery task function directly
        from envoy_bu_policy_api.policy.tasks import update_policy_statuses
        
        # Call the task function directly (since CELERY_TASK_ALWAYS_EAGER = True)
        scheduler_logger.info(f"[SCHEDULER_STEP] {scheduler_id} - Calling Celery task function")
        update_policy_statuses()
        
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.info(f"[SCHEDULER_SUCCESS] {scheduler_id} - APScheduler Policy Status Update Completed Successfully")
        scheduler_logger.info(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.info(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
    except Exception as e:
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.error(f"[SCHEDULER_FAILED] {scheduler_id} - APScheduler Policy Status Update Failed")
        scheduler_logger.error(f"[SCHEDULER_ERROR] {scheduler_id} - Error: {str(e)}")
        scheduler_logger.error(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.error(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
        raise

def update_credit_ages_apscheduler():
    """
    APScheduler wrapper for update_credit_ages Celery task
    Runs daily to update credit age for all issued policies
    """
    scheduler_start_time = datetime.now()
    scheduler_id = f"apscheduler_credit_age_{scheduler_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        scheduler_logger.info(f"[SCHEDULER_START] {scheduler_id} - APScheduler Credit Age Update Task Started")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Start Time: {scheduler_start_time.isoformat()}")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Trigger: Every 2 hours")
        
        # Import and call the original Celery task function directly
        from envoy_bu_policy_api.policy.tasks import update_credit_ages
        
        # Call the task function directly (since CELERY_TASK_ALWAYS_EAGER = True)
        scheduler_logger.info(f"[SCHEDULER_STEP] {scheduler_id} - Calling Celery task function")
        result = update_credit_ages()
        
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.info(f"[SCHEDULER_SUCCESS] {scheduler_id} - APScheduler Credit Age Update Completed Successfully")
        if result:
            scheduler_logger.info(f"[SCHEDULER_RESULT] {scheduler_id} - Task Result: {result}")
        scheduler_logger.info(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.info(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
    except Exception as e:
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.error(f"[SCHEDULER_FAILED] {scheduler_id} - APScheduler Credit Age Update Failed")
        scheduler_logger.error(f"[SCHEDULER_ERROR] {scheduler_id} - Error: {str(e)}")
        scheduler_logger.error(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.error(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
        raise

def send_payment_reminders_apscheduler():
    """
    APScheduler wrapper for send_payment_reminders Celery task
    Runs daily to send payment reminders before policy end date
    """
    scheduler_start_time = datetime.now()
    scheduler_id = f"apscheduler_payment_reminder_{scheduler_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        scheduler_logger.info(f"[SCHEDULER_START] {scheduler_id} - APScheduler Payment Reminder Task Started")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Start Time: {scheduler_start_time.isoformat()}")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Trigger: Daily")
        
        # Import and call the original Celery task function directly
        from envoy_bu_policy_api.policy.tasks import send_payment_reminders
        
        # Call the task function directly (since CELERY_TASK_ALWAYS_EAGER = True)
        scheduler_logger.info(f"[SCHEDULER_STEP] {scheduler_id} - Calling Celery task function")
        result = send_payment_reminders()
        
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.info(f"[SCHEDULER_SUCCESS] {scheduler_id} - APScheduler Payment Reminder Completed Successfully")
        if result:
            scheduler_logger.info(f"[SCHEDULER_RESULT] {scheduler_id} - Task Result: {result}")
        scheduler_logger.info(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.info(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
    except Exception as e:
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.error(f"[SCHEDULER_FAILED] {scheduler_id} - APScheduler Payment Reminder Failed")
        scheduler_logger.error(f"[SCHEDULER_ERROR] {scheduler_id} - Error: {str(e)}")
        scheduler_logger.error(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.error(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
        raise

def send_renewal_reminders_apscheduler():
    """
    APScheduler wrapper for send_renewal_reminders Celery task
    Runs daily to send policy renewal reminders
    """
    scheduler_start_time = datetime.now()
    scheduler_id = f"apscheduler_renewal_reminder_{scheduler_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        scheduler_logger.info(f"[SCHEDULER_START] {scheduler_id} - APScheduler Renewal Reminder Task Started")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Start Time: {scheduler_start_time.isoformat()}")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Trigger: Daily")
        
        # Import and call the original Celery task function directly
        from envoy_bu_policy_api.policy.tasks import send_renewal_reminders
        
        # Call the task function directly (since CELERY_TASK_ALWAYS_EAGER = True)
        scheduler_logger.info(f"[SCHEDULER_STEP] {scheduler_id} - Calling Celery task function")
        result = send_renewal_reminders()
        
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.info(f"[SCHEDULER_SUCCESS] {scheduler_id} - APScheduler Renewal Reminder Completed Successfully")
        if result:
            scheduler_logger.info(f"[SCHEDULER_RESULT] {scheduler_id} - Task Result: {result}")
        scheduler_logger.info(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.info(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
    except Exception as e:
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.error(f"[SCHEDULER_FAILED] {scheduler_id} - APScheduler Renewal Reminder Failed")
        scheduler_logger.error(f"[SCHEDULER_ERROR] {scheduler_id} - Error: {str(e)}")
        scheduler_logger.error(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.error(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
        raise

def send_policy_expiration_warnings_apscheduler():
    """
    APScheduler wrapper for send_policy_expiration_warnings Celery task
    Runs daily to send policy expiration warning notifications
    """
    scheduler_start_time = datetime.now()
    scheduler_id = f"apscheduler_expiration_warning_{scheduler_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        scheduler_logger.info(f"[SCHEDULER_START] {scheduler_id} - APScheduler Policy Expiration Warning Task Started")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Start Time: {scheduler_start_time.isoformat()}")
        scheduler_logger.info(f"[SCHEDULER_INFO] {scheduler_id} - Trigger: Daily")
        
        # Import and call the original Celery task function directly
        from envoy_bu_policy_api.policy.tasks import send_policy_expiration_warnings
        
        # Call the task function directly (since CELERY_TASK_ALWAYS_EAGER = True)
        scheduler_logger.info(f"[SCHEDULER_STEP] {scheduler_id} - Calling Celery task function")
        result = send_policy_expiration_warnings()
        
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.info(f"[SCHEDULER_SUCCESS] {scheduler_id} - APScheduler Policy Expiration Warning Completed Successfully")
        if result:
            scheduler_logger.info(f"[SCHEDULER_RESULT] {scheduler_id} - Task Result: {result}")
        scheduler_logger.info(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.info(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
    except Exception as e:
        scheduler_end_time = datetime.now()
        duration = (scheduler_end_time - scheduler_start_time).total_seconds()
        
        scheduler_logger.error(f"[SCHEDULER_FAILED] {scheduler_id} - APScheduler Policy Expiration Warning Failed")
        scheduler_logger.error(f"[SCHEDULER_ERROR] {scheduler_id} - Error: {str(e)}")
        scheduler_logger.error(f"[SCHEDULER_TIMING] {scheduler_id} - Duration: {duration:.2f} seconds")
        scheduler_logger.error(f"[SCHEDULER_END] {scheduler_id} - End Time: {scheduler_end_time.isoformat()}")
        
        raise

def setup_apscheduler_jobs():
    """
    Setup APScheduler jobs for production scheduling
    This function should be called during Django startup
    """
    try:
        # Get the default scheduler
        scheduler = getattr(settings, 'SCHEDULER', None)
        
        if scheduler is None:
            logger.warning("APScheduler not configured. Jobs will not be scheduled.")
            return
        
        # Add policy status update job (every 1 hour for testing)
        scheduler.add_job(
            update_policy_statuses_apscheduler,
            trigger=IntervalTrigger(hours=1),  # Changed from 12 hours to 1 hour
            id='policy_status_update',
            name='Update Policy Statuses',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        # Add credit age update job (every 2 hours for testing)
        scheduler.add_job(
            update_credit_ages_apscheduler,
            trigger=IntervalTrigger(hours=2),  # Changed from 24 hours to 2 hours
            id='credit_age_update',
            name='Update Credit Ages',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        # Add payment reminder job (daily)
        scheduler.add_job(
            send_payment_reminders_apscheduler,
            trigger=IntervalTrigger(hours=24),  # Daily
            id='payment_reminders',
            name='Send Payment Reminders',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        # Add renewal reminder job (daily)
        scheduler.add_job(
            send_renewal_reminders_apscheduler,
            trigger=IntervalTrigger(hours=24),  # Daily
            id='renewal_reminders',
            name='Send Renewal Reminders',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        # Add policy expiration warning job (daily)
        scheduler.add_job(
            send_policy_expiration_warnings_apscheduler,
            trigger=IntervalTrigger(hours=24),  # Daily
            id='policy_expiration_warnings',
            name='Send Policy Expiration Warnings',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        logger.info("APScheduler jobs configured successfully")
        logger.info("- Policy status update: Every 1 hour")
        logger.info("- Credit age update: Every 2 hours")
        logger.info("- Payment reminders: Daily")
        logger.info("- Renewal reminders: Daily")
        logger.info("- Policy expiration warnings: Daily")
        
    except Exception as e:
        logger.error(f"Error setting up APScheduler jobs: {str(e)}")
        raise

def run_apscheduler_scheduler():
    """
    Run the APScheduler scheduler in blocking mode
    This should be used in production instead of Celery Beat
    """
    try:
        logger.info("Starting APScheduler scheduler...")
        
        # Create scheduler with Django job store
        scheduler = BlockingScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # Add jobs
        scheduler.add_job(
            update_policy_statuses_apscheduler,
            trigger=IntervalTrigger(hours=12),
            id='policy_status_update',
            name='Update Policy Statuses',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,
        )
        
        scheduler.add_job(
            update_credit_ages_apscheduler,
            trigger=IntervalTrigger(hours=24),
            id='credit_age_update',
            name='Update Credit Ages',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,
        )
        
        logger.info("APScheduler scheduler started with jobs:")
        logger.info("- Policy status update: Every 12 hours")
        logger.info("- Credit age update: Daily")
        
        # Start the scheduler (this will block)
        scheduler.start()
        
    except KeyboardInterrupt:
        logger.info("APScheduler scheduler stopped by user")
    except Exception as e:
        logger.error(f"Error running APScheduler scheduler: {str(e)}")
        raise
