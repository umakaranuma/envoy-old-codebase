"""
Django APScheduler Auto-Start Configuration
Safe BackgroundScheduler that starts automatically with Django
"""

import logging
import os
from django.conf import settings
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from envoy_bu_policy_api.policy.apscheduler_tasks import (
    update_policy_statuses_apscheduler,
    update_credit_ages_apscheduler,
    send_payment_reminders_apscheduler,
    send_renewal_reminders_apscheduler,
    send_policy_expiration_warnings_apscheduler
)

logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler = None

def get_scheduler():
    """
    Get or create the global scheduler instance
    """
    global _scheduler
    
    if _scheduler is None:
        # Check if auto-start is enabled
        auto_start = os.getenv('APSCHEDULER_AUTO_START', 'false').lower() in ('true', '1', 'yes')
        
        if not auto_start:
            logger.info("APScheduler auto-start disabled (set APSCHEDULER_AUTO_START=true to enable)")
            return None
            
        try:
            # Configure job stores
            jobstores = {
                'default': DjangoJobStore()
            }
            
            # Configure executors
            executors = {
                'default': ThreadPoolExecutor(20),
            }
            
            # Configure job defaults
            job_defaults = getattr(settings, 'APSCHEDULER_JOB_DEFAULTS', {
                'coalesce': False,
                'max_instances': 1,
                'misfire_grace_time': 15,
            })
            
            # Create BackgroundScheduler (non-blocking)
            _scheduler = BackgroundScheduler(
                jobstores=jobstores,
                executors=executors,
                job_defaults=job_defaults,
                timezone=getattr(settings, 'TIME_ZONE', 'UTC')
            )
            
            # Add jobs
            add_scheduled_jobs(_scheduler)
            
            logger.info("APScheduler BackgroundScheduler created successfully")
            
        except Exception as e:
            logger.error(f"Error creating APScheduler: {str(e)}")
            _scheduler = None
            
    return _scheduler

def add_scheduled_jobs(scheduler):
    """
    Add scheduled jobs to the scheduler
    """
    try:
        # Add policy status update job (every 1 hour for testing)
        scheduler.add_job(
            update_policy_statuses_apscheduler,
            trigger='interval',
            hours=1,  # Changed from 12 hours to 1 hour
            id='policy_status_update',
            name='Update Policy Statuses',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        # Add credit age update job (every 2 hours for testing)
        scheduler.add_job(
            update_credit_ages_apscheduler,
            trigger='interval',
            hours=2,  # Changed from 24 hours to 2 hours
            id='credit_age_update',
            name='Update Credit Ages',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        # Add payment reminder job (daily)
        scheduler.add_job(
            send_payment_reminders_apscheduler,
            trigger='interval',
            hours=24,  # Daily
            id='payment_reminders',
            name='Send Payment Reminders',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        # Add renewal reminder job (daily)
        scheduler.add_job(
            send_renewal_reminders_apscheduler,
            trigger='interval',
            hours=24,  # Daily
            id='renewal_reminders',
            name='Send Renewal Reminders',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        # Add policy expiration warning job (daily)
        scheduler.add_job(
            send_policy_expiration_warnings_apscheduler,
            trigger='interval',
            hours=24,  # Daily
            id='policy_expiration_warnings',
            name='Send Policy Expiration Warnings',
            replace_existing=True,
            max_instances=1,
            misfire_grace_time=300,  # 5 minutes
        )
        
        logger.info("APScheduler jobs added:")
        logger.info("- Policy status update: Every 1 hour")
        logger.info("- Credit age update: Every 2 hours")
        logger.info("- Payment reminders: Daily")
        logger.info("- Renewal reminders: Daily")
        logger.info("- Policy expiration warnings: Daily")
        
    except Exception as e:
        logger.error(f"Error adding scheduled jobs: {str(e)}")
        raise

def start_scheduler():
    """
    Start the scheduler if it exists and isn't already running
    """
    global _scheduler
    
    scheduler = get_scheduler()
    if scheduler is None:
        return False
        
    if scheduler.running:
        logger.info("APScheduler is already running")
        return True
        
    try:
        scheduler.start()
        logger.info("APScheduler BackgroundScheduler started successfully")
        return True
    except Exception as e:
        logger.error(f"Error starting APScheduler: {str(e)}")
        return False

def stop_scheduler():
    """
    Stop the scheduler if it's running
    """
    global _scheduler
    
    if _scheduler is None or not _scheduler.running:
        return
        
    try:
        _scheduler.shutdown()
        logger.info("APScheduler BackgroundScheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping APScheduler: {str(e)}")

def is_scheduler_running():
    """
    Check if the scheduler is running
    """
    global _scheduler
    return _scheduler is not None and _scheduler.running
