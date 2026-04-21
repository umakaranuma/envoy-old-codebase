"""
Django Policy App Configuration
"""

import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class PolicyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'envoy_bu_policy_api.policy'
    
    def ready(self):
        """
        Called when Django starts up
        Auto-start APScheduler if enabled
        """
        try:
            from envoy_bu_policy_api.policy.scheduler import start_scheduler
            
            # Start scheduler automatically
            if start_scheduler():
                logger.info("APScheduler auto-started successfully")
            else:
                logger.info("APScheduler auto-start skipped (disabled or already running)")
                
        except Exception as e:
            logger.error(f"Failed to auto-start APScheduler: {str(e)}")
