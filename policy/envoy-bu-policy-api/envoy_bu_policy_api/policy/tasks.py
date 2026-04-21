from celery import shared_task
from django.db import connection
from django.utils import timezone
import logging
import traceback
from datetime import datetime
from core_models.core_models import Status

logger = logging.getLogger(__name__)

# Create a separate logger for task execution logs
task_logger = logging.getLogger('policy_tasks')

@shared_task
def update_policy_statuses():
    """
    Scheduled task to update policy statuses based on expiry dates.
    Runs every 12 hours to check and update:
    - EXPIRED: Policies past their expiry date
    - DUE_FOR_RENEWAL: Policies within 30 days of expiry
    """
    task_start_time = datetime.now()
    task_id = f"policy_status_update_{task_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        task_logger.info(f"[TASK_START] {task_id} - Policy Status Update Task Started")
        task_logger.info(f"[TASK_INFO] {task_id} - Start Time: {task_start_time.isoformat()}")
        
        with connection.cursor() as cursor:
            # Step 1: Ensure required statuses exist
            task_logger.info(f"[TASK_STEP] {task_id} - Step 1: Ensuring required statuses exist")
            ensure_statuses_exist(cursor)
            
            # Step 2: Get status IDs
            task_logger.info(f"[TASK_STEP] {task_id} - Step 2: Getting status IDs")
            status_ids = get_status_ids(cursor)
            if not all(status_ids.values()):
                task_logger.error(f"[TASK_ERROR] {task_id} - Failed to get required status IDs: {status_ids}")
                return
            
            task_logger.info(f"[TASK_INFO] {task_id} - Status IDs retrieved: {status_ids}")
            
            # Step 3: Update EXPIRED policies
            task_logger.info(f"[TASK_STEP] {task_id} - Step 3: Updating EXPIRED policies")
            expired_count = update_expired_policies(cursor, status_ids)
            
            # Step 4: Update DUE_FOR_RENEWAL policies
            task_logger.info(f"[TASK_STEP] {task_id} - Step 4: Updating DUE_FOR_RENEWAL policies")
            due_renewal_count = update_due_for_renewal_policies(cursor, status_ids)
            
            task_end_time = datetime.now()
            duration = (task_end_time - task_start_time).total_seconds()
            
            task_logger.info(f"[TASK_SUCCESS] {task_id} - Policy Status Update Completed Successfully")
            task_logger.info(f"[TASK_RESULT] {task_id} - Results: {expired_count} expired, {due_renewal_count} due for renewal")
            task_logger.info(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
            task_logger.info(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
            
    except Exception as e:
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        error_traceback = traceback.format_exc()
        
        task_logger.error(f"[TASK_FAILED] {task_id} - Policy Status Update Task Failed")
        task_logger.error(f"[TASK_ERROR] {task_id} - Error: {str(e)}")
        task_logger.error(f"[TASK_TRACEBACK] {task_id} - Traceback: {error_traceback}")
        task_logger.error(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.error(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        raise

@shared_task
def update_credit_ages():
    """
    Scheduled task to update credit age for all issued policies.
    Credit age = days overdue AFTER credit period ends (payment not made)
    
    Formula:
    - Credit period starts from policy_effective_date (issue date)
    - Credit period end = policy_effective_date + credit_period_days
    - Credit age = max(0, current_date - credit_period_end_date)
    - Credit age = 0 if fully paid
    
    Runs daily at midnight.
    """
    task_start_time = datetime.now()
    task_id = f"credit_age_update_{task_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        task_logger.info(f"[TASK_START] {task_id} - Credit Age Update Task Started")
        task_logger.info(f"[TASK_INFO] {task_id} - Start Time: {task_start_time.isoformat()}")
        
        from envoy_bu_policy_api.policy.models.crmp_issued_policies import IssuedPolicy
        
        # Get all issued policies
        task_logger.info(f"[TASK_STEP] {task_id} - Fetching all issued policies")
        policies = IssuedPolicy.objects.all()
        total_policies = policies.count()
        task_logger.info(f"[TASK_INFO] {task_id} - Total policies to process: {total_policies}")
        
        updated_count = 0
        error_count = 0
        changed_count = 0
        
        for index, policy in enumerate(policies, 1):
            try:
                old_credit_age = policy.credit_age_days
                policy.update_credit_age()
                new_credit_age = policy.credit_age_days
                
                if old_credit_age != new_credit_age:
                    changed_count += 1
                    task_logger.info(
                        f"[TASK_CHANGE] {task_id} - Policy {policy.brokerage_policy_id}: "
                        f"Credit age updated from {old_credit_age} to {new_credit_age} days"
                    )
                    
                    # Send payment due notification when credit age goes above 0
                    if old_credit_age == 0 and new_credit_age > 0:
                        try:
                            from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
                            from mServices import QueryBuilderService
                            from datetime import datetime, timedelta
                            
                            # Get policy details for notification
                            policy_details = (
                                QueryBuilderService("crmp_issued_policies as ip")
                                .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
                                .leftJoin("core_customers as c", "c.id", "pb.customer_id")
                                .leftJoin("core_vendor_products as vp", "vp.id", "pb.product_id")
                                .leftJoin("crmf_invoices as inv", "inv.issued_policy_id", "ip.id")
                                .select(
                                    "ip.brokerage_policy_id",
                                    "ip.premium_amount",
                                    "ip.policy_effective_date",
                                    "ip.credit_period_days",
                                    "c.id as customer_id",
                                    "c.name as customer_name",
                                    "vp.name as product_name",
                                    "inv.outstanding_amount",
                                    "inv.due_date"
                                )
                                .where("ip.id", policy.id)
                                .first()
                            )
                            
                            if policy_details and policy_details.get("customer_id"):
                                # Calculate payment date (policy effective date + credit period)
                                policy_effective_date = policy_details.get("policy_effective_date")
                                credit_period_days = policy_details.get("credit_period_days", 0)
                                
                                if policy_effective_date:
                                    if isinstance(policy_effective_date, str):
                                        from datetime import datetime
                                        policy_effective_date = datetime.strptime(policy_effective_date, '%Y-%m-%d').date()
                                    
                                    payment_date = policy_effective_date + timedelta(days=credit_period_days)
                                else:
                                    payment_date = "N/A"
                                
                                # Get due amount (outstanding amount or premium amount)
                                due_amount = policy_details.get("outstanding_amount") or policy_details.get("premium_amount", "0.00")
                                
                                # Create payment link
                                payment_link = f"/payments/policy/{policy.id}"
                                
                                # Format detailed message
                                detailed_message = NotificationService.format_payment_due_message(
                                    policy_number=policy_details.get("brokerage_policy_id", "N/A"),
                                    product_name=policy_details.get("product_name", "Unknown Product"),
                                    due_amount=str(due_amount),
                                    payment_date=str(payment_date),
                                    credit_age_days=new_credit_age,
                                    payment_link=payment_link
                                )
                                
                                # Prepare payment data for metadata
                                payment_data = {
                                    "policy_id": policy.id,
                                    "brokerage_policy_id": policy_details.get("brokerage_policy_id"),
                                    "due_amount": str(due_amount),
                                    "payment_date": str(payment_date),
                                    "credit_age_days": new_credit_age,
                                    "product_name": policy_details.get("product_name")
                                }
                                
                                # Prepare links for metadata
                                links = [
                                    {"title": "Make Payment", "url": payment_link},
                                    {"title": "View Policy", "url": f"/policies/{policy.id}"}
                                ]
                                
                                # Generate detailed notification
                                NotificationService.generate_detailed_notification(
                                    type_code="payment_due",
                                    title="Payment Due Reminder",
                                    detailed_message=detailed_message,
                                    customer_id=policy_details.get("customer_id"),
                                    user_id=None,  # System notification
                                    payment_data=payment_data,
                                    links=links
                                )
                                
                                task_logger.info(f"[NOTIFICATION] {task_id} - Payment due notification sent for policy {policy.brokerage_policy_id}")
                            else:
                                task_logger.warning(f"[NOTIFICATION] {task_id} - Could not send payment due notification - missing policy details for policy {policy.id}")
                                
                        except Exception as notify_e:
                            task_logger.error(f"[NOTIFICATION_ERROR] {task_id} - Error sending payment due notification for policy {policy.id}: {str(notify_e)}")
                            # Don't fail the entire task for notification errors
                
                updated_count += 1
                
                # Log progress every 100 policies
                if index % 100 == 0:
                    task_logger.info(f"[TASK_PROGRESS] {task_id} - Processed {index}/{total_policies} policies")
                
            except Exception as e:
                error_count += 1
                task_logger.error(
                    f"[TASK_ERROR] {task_id} - Error updating credit age for policy {policy.id} "
                    f"({policy.brokerage_policy_id}): {str(e)}"
                )
        
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        
        task_logger.info(f"[TASK_SUCCESS] {task_id} - Credit Age Update Completed Successfully")
        task_logger.info(f"[TASK_RESULT] {task_id} - Results: {updated_count} processed, {changed_count} changed, {error_count} errors")
        task_logger.info(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.info(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        return {
            'success': True,
            'updated_count': updated_count,
            'changed_count': changed_count,
            'error_count': error_count,
            'duration': duration
        }
        
    except Exception as e:
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        error_traceback = traceback.format_exc()
        
        task_logger.error(f"[TASK_FAILED] {task_id} - Credit Age Update Task Failed")
        task_logger.error(f"[TASK_ERROR] {task_id} - Error: {str(e)}")
        task_logger.error(f"[TASK_TRACEBACK] {task_id} - Traceback: {error_traceback}")
        task_logger.error(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.error(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        raise

@shared_task
def send_payment_reminders():
    """
    Scheduled task to send payment reminders before policy end date.
    Sends reminders for policies that are approaching their end date but still have outstanding payments.
    
    Runs daily to check for policies needing payment reminders.
    """
    task_start_time = datetime.now()
    task_id = f"payment_reminder_{task_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        task_logger.info(f"[TASK_START] {task_id} - Payment Reminder Task Started")
        task_logger.info(f"[TASK_INFO] {task_id} - Start Time: {task_start_time.isoformat()}")
        
        from envoy_bu_policy_api.policy.models.crmp_issued_policies import IssuedPolicy
        from mServices import QueryBuilderService
        from datetime import timedelta
        
        # Get policies that are within 30 days of expiry and have outstanding payments
        reminder_date = datetime.now().date() + timedelta(days=30)
        
        policies_needing_reminders = (
            QueryBuilderService("crmp_issued_policies as ip")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .leftJoin("core_customers as c", "c.id", "pb.customer_id")
            .leftJoin("core_vendor_products as vp", "vp.id", "pb.product_id")
            .leftJoin("crmf_invoices as inv", "inv.issued_policy_id", "ip.id")
            .select(
                "ip.id",
                "ip.brokerage_policy_id",
                "ip.end_date",
                "ip.premium_amount",
                "ip.policy_effective_date",
                "ip.credit_period_days",
                "c.id as customer_id",
                "c.name as customer_name",
                "vp.name as product_name",
                "inv.outstanding_amount",
                "inv.due_date"
            )
            .where("ip.end_date", "<=", reminder_date)
            .where("ip.end_date", ">", datetime.now().date())
            .where("inv.outstanding_amount", ">", 0)
            .get()
        )
        
        total_policies = len(policies_needing_reminders)
        task_logger.info(f"[TASK_INFO] {task_id} - Found {total_policies} policies needing payment reminders")
        
        notifications_sent = 0
        error_count = 0
        
        for policy_data in policies_needing_reminders:
            try:
                from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
                
                # Calculate payment date (policy effective date + credit period)
                policy_effective_date = policy_data.get("policy_effective_date")
                credit_period_days = policy_data.get("credit_period_days", 0)
                
                if policy_effective_date:
                    if isinstance(policy_effective_date, str):
                        from datetime import datetime
                        policy_effective_date = datetime.strptime(policy_effective_date, '%Y-%m-%d').date()
                    
                    payment_date = policy_effective_date + timedelta(days=credit_period_days)
                else:
                    payment_date = "N/A"
                
                # Get outstanding amount
                outstanding_amount = policy_data.get("outstanding_amount") or policy_data.get("premium_amount", "0.00")
                
                # Create payment link
                payment_link = f"/payments/policy/{policy_data['id']}"
                
                # Format detailed message
                detailed_message = NotificationService.format_payment_reminder_message(
                    policy_number=policy_data.get("brokerage_policy_id", "N/A"),
                    product_name=policy_data.get("product_name", "Unknown Product"),
                    amount=str(outstanding_amount),
                    payment_date=str(payment_date),
                    payment_link=payment_link
                )
                
                # Prepare payment data for metadata
                payment_data = {
                    "policy_id": policy_data["id"],
                    "brokerage_policy_id": policy_data.get("brokerage_policy_id"),
                    "amount": str(outstanding_amount),
                    "payment_date": str(payment_date),
                    "end_date": str(policy_data.get("end_date")),
                    "product_name": policy_data.get("product_name")
                }
                
                # Prepare links for metadata
                links = [
                    {"title": "Make Payment", "url": payment_link},
                    {"title": "View Policy", "url": f"/policies/{policy_data['id']}"}
                ]
                
                # Generate detailed notification
                NotificationService.generate_detailed_notification(
                    type_code="payment_reminder",
                    title="Upcoming Payment Reminder",
                    detailed_message=detailed_message,
                    customer_id=policy_data.get("customer_id"),
                    user_id=None,  # System notification
                    payment_data=payment_data,
                    links=links
                )
                
                notifications_sent += 1
                task_logger.info(f"[NOTIFICATION] {task_id} - Payment reminder sent for policy {policy_data.get('brokerage_policy_id')}")
                
            except Exception as notify_e:
                error_count += 1
                task_logger.error(f"[NOTIFICATION_ERROR] {task_id} - Error sending payment reminder for policy {policy_data.get('id')}: {str(notify_e)}")
        
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        
        task_logger.info(f"[TASK_SUCCESS] {task_id} - Payment Reminder Task Completed Successfully")
        task_logger.info(f"[TASK_RESULT] {task_id} - Results: {notifications_sent} notifications sent, {error_count} errors")
        task_logger.info(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.info(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        return {
            'success': True,
            'notifications_sent': notifications_sent,
            'error_count': error_count,
            'duration': duration
        }
        
    except Exception as e:
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        error_traceback = traceback.format_exc()
        
        task_logger.error(f"[TASK_FAILED] {task_id} - Payment Reminder Task Failed")
        task_logger.error(f"[TASK_ERROR] {task_id} - Error: {str(e)}")
        task_logger.error(f"[TASK_TRACEBACK] {task_id} - Traceback: {error_traceback}")
        task_logger.error(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.error(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        raise

@shared_task
def send_renewal_reminders():
    """
    Scheduled task to send policy renewal reminders.
    Sends reminders for policies that are approaching their expiry date.
    
    Runs daily to check for policies needing renewal reminders.
    """
    task_start_time = datetime.now()
    task_id = f"renewal_reminder_{task_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        task_logger.info(f"[TASK_START] {task_id} - Renewal Reminder Task Started")
        task_logger.info(f"[TASK_INFO] {task_id} - Start Time: {task_start_time.isoformat()}")
        
        from mServices import QueryBuilderService
        from datetime import timedelta
        
        # Get policies that are within 30 days of expiry
        reminder_date = datetime.now().date() + timedelta(days=30)
        
        policies_needing_renewal = (
            QueryBuilderService("crmp_issued_policies as ip")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .leftJoin("core_customers as c", "c.id", "pb.customer_id")
            .leftJoin("core_vendor_products as vp", "vp.id", "pb.product_id")
            .select(
                "ip.id",
                "ip.brokerage_policy_id",
                "ip.end_date",
                "c.id as customer_id",
                "c.name as customer_name",
                "vp.name as product_name"
            )
            .where("ip.end_date", "<=", reminder_date)
            .where("ip.end_date", ">", datetime.now().date())
            .get()
        )
        
        total_policies = len(policies_needing_renewal)
        task_logger.info(f"[TASK_INFO] {task_id} - Found {total_policies} policies needing renewal reminders")
        
        notifications_sent = 0
        error_count = 0
        
        for policy_data in policies_needing_renewal:
            try:
                from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
                
                # Create renewal link
                renewal_link = f"/policies/{policy_data['id']}/renew"
                
                # Normalize expiry date to YYYY-MM-DD
                raw_end = policy_data.get("end_date")
                if hasattr(raw_end, "strftime"):
                    expiry_str = raw_end.strftime("%Y-%m-%d")
                else:
                    expiry_str = str(raw_end).split(" ")[0] if raw_end else ""

                # Format detailed message
                detailed_message = NotificationService.format_renewal_reminder_message(
                    policy_number=policy_data.get("brokerage_policy_id", "N/A"),
                    product_name=policy_data.get("product_name", "Unknown Product"),
                    expiry_date=expiry_str,
                    renewal_link=renewal_link
                )
                
                # Prepare policy data for metadata
                policy_data_meta = {
                    "policy_id": policy_data["id"],
                    "brokerage_policy_id": policy_data.get("brokerage_policy_id"),
                    "expiry_date": expiry_str,
                    "product_name": policy_data.get("product_name")
                }
                
                # Prepare links for metadata
                links = [
                    {"title": "Renew Policy", "url": renewal_link},
                    {"title": "View Policy", "url": f"/policies/{policy_data['id']}"}
                ]
                
                # Generate detailed notification
                NotificationService.generate_detailed_notification(
                    type_code="policy_renewal",
                    title="Policy Renewal Reminder",
                    detailed_message=detailed_message,
                    customer_id=policy_data.get("customer_id"),
                    user_id=None,  # System notification
                    policy_data=policy_data_meta,
                    links=links
                )
                
                notifications_sent += 1
                task_logger.info(f"[NOTIFICATION] {task_id} - Renewal reminder sent for policy {policy_data.get('brokerage_policy_id')}")
                
            except Exception as notify_e:
                error_count += 1
                task_logger.error(f"[NOTIFICATION_ERROR] {task_id} - Error sending renewal reminder for policy {policy_data.get('id')}: {str(notify_e)}")
        
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        
        task_logger.info(f"[TASK_SUCCESS] {task_id} - Renewal Reminder Task Completed Successfully")
        task_logger.info(f"[TASK_RESULT] {task_id} - Results: {notifications_sent} notifications sent, {error_count} errors")
        task_logger.info(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.info(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        return {
            'success': True,
            'notifications_sent': notifications_sent,
            'error_count': error_count,
            'duration': duration
        }
        
    except Exception as e:
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        error_traceback = traceback.format_exc()
        
        task_logger.error(f"[TASK_FAILED] {task_id} - Renewal Reminder Task Failed")
        task_logger.error(f"[TASK_ERROR] {task_id} - Error: {str(e)}")
        task_logger.error(f"[TASK_TRACEBACK] {task_id} - Traceback: {error_traceback}")
        task_logger.error(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.error(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        raise

def ensure_statuses_exist(cursor=None):
    """Ensure required statuses exist in core_status table using type+module as immutable lookup"""
    
    # Required policy statuses with immutable type+module
    statuses = [
        ("DUE FOR RENEWAL", "policyStatus", "pol_due_renewal", "policy", "#175CD3", 3),
        ("EXPIRED", "policyStatus", "policy_expired", "policy", "#344054", 4),
        ("ACTIVE", "policyStatus", "policy_active", "policy", "#067647", 2),
    ]
    
    for name, desc, typ, mod, color, idx in statuses:
        Status.objects.update_or_create(
            type=typ,
            module=mod,
            defaults={
                "name": name,
                "description": desc,
                "color": color,
                "sort_index": idx
            }
        )

def get_status_ids(cursor):
    """Get status IDs for use in updates"""
    cursor.execute("""
        SELECT 
            (SELECT id FROM core_status WHERE type = 'policy_active' AND module = 'policy') as active_id,
            (SELECT id FROM core_status WHERE type = 'pol_due_renewal' AND module = 'policy') as due_renewal_id,
            (SELECT id FROM core_status WHERE type = 'policy_expired' AND module = 'policy') as expired_id,
            (SELECT id FROM core_status WHERE type = 'policy_cancelled' AND module = 'policy') as cancelled_id
    """)
    
    result = cursor.fetchone()
    return {
        'active': result[0],
        'due_renewal': result[1], 
        'expired': result[2],
        'cancelled': result[3]
    }

def update_expired_policies(cursor, status_ids):
    """Update policies that have passed their expiry date to EXPIRED status (date-driven only)"""
    # Only update ACTIVE or DUE_FOR_RENEWAL policies to EXPIRED
    # Exclude cancelled policies - they should remain cancelled
    active_id = status_ids.get('active')
    due_renewal_id = status_ids.get('due_renewal')
    cancelled_id = status_ids.get('cancelled')
    
    if active_id and due_renewal_id:
        if cancelled_id:
            cursor.execute("""
                UPDATE crmp_policy_base
                SET status_id = %s
                WHERE policy_expiry_date < CURDATE()
                  AND status_id IN (%s, %s)
                  AND status_id != %s
            """, [status_ids['expired'], active_id, due_renewal_id, cancelled_id])
        else:
            cursor.execute("""
                UPDATE crmp_policy_base
                SET status_id = %s
                WHERE policy_expiry_date < CURDATE()
                  AND status_id IN (%s, %s)
                  AND status_id NOT IN (SELECT id FROM core_status WHERE type = 'policy_cancelled' AND module = 'policy')
            """, [status_ids['expired'], active_id, due_renewal_id])
    else:
        logger.warning("Active or Due Renewal status ID not found - skipping EXPIRED updates")
        return 0
    
    expired_count = cursor.rowcount
    logger.info(f"Updated {expired_count} policies to EXPIRED status")
    return expired_count

def update_due_for_renewal_policies(cursor, status_ids):
    """Update policies to DUE_FOR_RENEWAL when within 30 days BEFORE expiry (date-driven only)"""
    # Only update ACTIVE policies to DUE_FOR_RENEWAL
    # Exclude cancelled, renewed, and other terminal statuses - they should remain in their current status
    active_id = status_ids.get('active')
    cancelled_id = status_ids.get('cancelled')
    
    if active_id:
        if cancelled_id:
            cursor.execute("""
                UPDATE crmp_policy_base
                SET status_id = %s
                WHERE policy_expiry_date >= CURDATE()
                  AND DATE_SUB(policy_expiry_date, INTERVAL 30 DAY) <= CURDATE()
                  AND status_id = %s
                  AND status_id != %s
            """, [status_ids['due_renewal'], active_id, cancelled_id])
        else:
            cursor.execute("""
                UPDATE crmp_policy_base
                SET status_id = %s
                WHERE policy_expiry_date >= CURDATE()
                  AND DATE_SUB(policy_expiry_date, INTERVAL 30 DAY) <= CURDATE()
                  AND status_id = %s
                  AND status_id NOT IN (SELECT id FROM core_status WHERE type = 'policy_cancelled' AND module = 'policy')
            """, [status_ids['due_renewal'], active_id])
    else:
        logger.warning("Active status ID not found - skipping DUE_FOR_RENEWAL updates")
        return 0
    
    due_renewal_count = cursor.rowcount
    logger.info(f"Updated {due_renewal_count} policies to DUE_FOR_RENEWAL status")
    return due_renewal_count

@shared_task
def send_policy_expiration_warnings():
    """
    Scheduled task to send policy expiration warning notifications.
    Sends warnings for policies expiring within 7 days.
    Runs daily.
    """
    task_start_time = datetime.now()
    task_id = f"policy_expiration_warning_{task_start_time.strftime('%Y%m%d_%H%M%S')}"
    
    try:
        task_logger.info(f"[TASK_START] {task_id} - Policy Expiration Warning Task Started")
        task_logger.info(f"[TASK_INFO] {task_id} - Start Time: {task_start_time.isoformat()}")
        
        from mServices import QueryBuilderService
        from envoy_bu_policy_api.finance.controllers.utils.NotificationService import NotificationService
        
        # Get policies expiring within 7 days
        task_logger.info(f"[TASK_STEP] {task_id} - Fetching policies expiring within 7 days")
        
        expiring_policies = (
            QueryBuilderService("crmp_issued_policies as ip")
            .leftJoin("crmp_policy_base as pb", "pb.id", "ip.policy_base_id")
            .leftJoin("core_customers as c", "c.id", "pb.customer_id")
            .leftJoin("core_vendor_products as vp", "vp.id", "pb.product_id")
            .select(
                "ip.id as policy_id",
                "ip.brokerage_policy_id",
                "ip.end_date as expiry_date",
                "c.id as customer_id",
                "vp.name as product_name"
            )
            .where("ip.end_date", ">=", "CURDATE()")
            .where("ip.end_date", "<=", "DATE_ADD(CURDATE(), INTERVAL 7 DAY)")
            .get()
        )
        
        total_policies = len(expiring_policies)
        task_logger.info(f"[TASK_INFO] {task_id} - Found {total_policies} policies expiring within 7 days")
        
        notifications_sent = 0
        error_count = 0
        
        for policy in expiring_policies:
            try:
                # Format expiry date
                expiry_date = policy.get("expiry_date")
                if expiry_date:
                    if hasattr(expiry_date, 'strftime'):
                        expiry_date_str = expiry_date.strftime("%Y-%m-%d")
                    else:
                        expiry_date_str = str(expiry_date)
                else:
                    expiry_date_str = "Unknown"
                
                # Create renewal link
                renewal_link = f"/policies/{policy.get('policy_id')}/renew"
                
                # Format detailed message
                detailed_message = NotificationService.format_policy_expiration_warning_message(
                    policy_id=policy.get("brokerage_policy_id", "N/A"),
                    product_name=policy.get("product_name", "Unknown Product"),
                    expiry_date=expiry_date_str,
                    renewal_link=renewal_link
                )
                
                # Prepare policy data for metadata
                policy_data = {
                    "policy_id": policy.get("policy_id"),
                    "brokerage_policy_id": policy.get("brokerage_policy_id"),
                    "product_name": policy.get("product_name", "Unknown Product"),
                    "expiry_date": expiry_date_str
                }
                
                # Generate detailed notification
                NotificationService.generate_detailed_notification(
                    type_code="policy_expiration_warning",
                    title="Policy Expiration Warning",
                    detailed_message=detailed_message,
                    customer_id=policy.get("customer_id"),
                    user_id=None,
                    policy_data=policy_data,
                    links=[{"title": "Renew Policy", "url": renewal_link}]
                )
                
                notifications_sent += 1
                task_logger.info(f"[TASK_SUCCESS] {task_id} - Sent expiration warning for policy {policy.get('brokerage_policy_id')}")
                
            except Exception as e:
                error_count += 1
                task_logger.error(f"[TASK_ERROR] {task_id} - Failed to send warning for policy {policy.get('policy_id')}: {str(e)}")
        
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        
        task_logger.info(f"[TASK_SUCCESS] {task_id} - Policy Expiration Warning Task Completed Successfully")
        task_logger.info(f"[TASK_RESULT] {task_id} - Results: {notifications_sent} notifications sent, {error_count} errors")
        task_logger.info(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.info(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        return {
            'success': True,
            'notifications_sent': notifications_sent,
            'error_count': error_count,
            'duration': duration
        }
        
    except Exception as e:
        task_end_time = datetime.now()
        duration = (task_end_time - task_start_time).total_seconds()
        error_traceback = traceback.format_exc()
        
        task_logger.error(f"[TASK_FAILED] {task_id} - Policy Expiration Warning Task Failed")
        task_logger.error(f"[TASK_ERROR] {task_id} - Error: {str(e)}")
        task_logger.error(f"[TASK_TRACEBACK] {task_id} - Traceback: {error_traceback}")
        task_logger.error(f"[TASK_TIMING] {task_id} - Duration: {duration:.2f} seconds")
        task_logger.error(f"[TASK_END] {task_id} - End Time: {task_end_time.isoformat()}")
        
        raise
