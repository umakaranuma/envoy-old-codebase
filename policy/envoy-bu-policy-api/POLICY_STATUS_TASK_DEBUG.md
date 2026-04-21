# Policy Status Task Debugging Guide

## Issue: Policy Status Task Not Working in QA/Production

The Celery policy status task should run every 12 hours to update policy statuses, but it's not working in your QA environment.

## Current Setup Analysis

Your current setup uses:
- `CELERY_TASK_ALWAYS_EAGER = True` (tasks run synchronously, no Redis needed)
- Celery Beat schedule configured for every 12 hours
- Two tasks: `update_policy_statuses` and `update_credit_ages`

## Debugging Steps

### 1. Test Task Manually (Immediate Check)

Run this command to test the task directly:

```bash
python manage.py test_celery_tasks --task=test-direct
```

This will:
- Execute the task immediately
- Show you exactly what it's doing
- Display any errors
- Show how many policies were updated

### 2. Check if Celery Beat is Running

The task is scheduled via Celery Beat, but with `CELERY_TASK_ALWAYS_EAGER = True`, the beat scheduler needs to be running.

**Check if Celery Beat is running:**
```bash
# Check if there's a celery beat process
ps aux | grep celery

# Or check if it's in your process list
ps -ef | grep celery
```

### 3. Check Django Logs

Look for these log messages in your application logs:
```
"Starting policy status update task..."
"Policy status update completed: X expired, Y due for renewal"
```

### 4. Check Database for Status Updates

Query your database to see if statuses are being updated:

```sql
-- Check recent status updates
SELECT 
    pb.id,
    pb.brokerage_policy_id,
    pb.policy_expiry_date,
    pb.status_id,
    cs.name as status_name,
    pb.updated_at
FROM crmp_policy_base pb
LEFT JOIN core_status cs ON pb.status_id = cs.id
WHERE pb.updated_at > DATE_SUB(NOW(), INTERVAL 1 DAY)
ORDER BY pb.updated_at DESC;

-- Check policies that should be EXPIRED
SELECT 
    pb.id,
    pb.brokerage_policy_id,
    pb.policy_expiry_date,
    cs.name as current_status,
    DATEDIFF(NOW(), pb.policy_expiry_date) as days_expired
FROM crmp_policy_base pb
LEFT JOIN core_status cs ON pb.status_id = cs.id
WHERE pb.policy_expiry_date < CURDATE()
AND cs.name != 'EXPIRED';

-- Check policies that should be DUE_FOR_RENEWAL
SELECT 
    pb.id,
    pb.brokerage_policy_id,
    pb.policy_expiry_date,
    cs.name as current_status,
    DATEDIFF(pb.policy_expiry_date, NOW()) as days_until_expiry
FROM crmp_policy_base pb
LEFT JOIN core_status cs ON pb.status_id = cs.id
WHERE pb.policy_expiry_date >= CURDATE()
AND DATE_SUB(pb.policy_expiry_date, INTERVAL 30 DAY) <= CURDATE()
AND cs.name != 'DUE_FOR_RENEWAL';
```

### 5. Verify Required Statuses Exist

Make sure the required statuses exist in your database:

```sql
SELECT * FROM core_status WHERE module = 'policy_status' AND name IN ('ACTIVE', 'DUE_FOR_RENEWAL', 'EXPIRED');
```

## Common Issues & Solutions

### Issue 1: Celery Beat Not Running
**Problem:** With `CELERY_TASK_ALWAYS_EAGER = True`, you still need to start Celery Beat for scheduling.

**Solution:** Start Celery Beat in your production environment:
```bash
# In your production environment
celery -A envoy_bu_policy_api beat --loglevel=info
```

### Issue 2: Missing Status Records
**Problem:** Required statuses don't exist in the database.

**Solution:** The task should create them automatically, but you can run:
```bash
python manage.py test_celery_tasks --task=test-direct
```

### Issue 3: Timezone Issues
**Problem:** Server timezone might not match Django timezone.

**Solution:** Check your timezone settings:
```python
# In Django shell
from django.utils import timezone
print(timezone.now())
```

### Issue 4: Database Connection Issues
**Problem:** Task can't connect to database.

**Solution:** Check database connectivity and permissions.

## Production Deployment Options

### Option 1: Kubernetes CronJob (Recommended)
Since you don't want to use Redis, use Kubernetes CronJob instead of Celery Beat:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: policy-status-update
spec:
  schedule: "0 */12 * * *"  # Every 12 hours
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: policy-status-task
            image: your-app-image
            command:
            - python
            - manage.py
            - test_celery_tasks
            - --task=test-direct
          restartPolicy: OnFailure
```

### Option 2: System Cron Job
Add to your server's crontab:
```bash
# Run every 12 hours
0 */12 * * * cd /path/to/your/app && python manage.py test_celery_tasks --task=test-direct
```

### Option 3: Keep Celery Beat (Current)
If you want to keep using Celery Beat, ensure it's running:
```bash
# Start celery beat (should be in your deployment)
celery -A envoy_bu_policy_api beat --loglevel=info --pidfile=/tmp/celerybeat.pid
```

## Commands for Developers

### Immediate Testing
```bash
# Test the task right now
python manage.py test_celery_tasks --task=test-direct

# Check if required statuses exist
python manage.py shell -c "from envoy_bu_policy_api.policy.tasks import ensure_statuses_exist; from django.db import connection; ensure_statuses_exist(connection.cursor())"

# Check current policy statuses
python manage.py shell -c "
from envoy_bu_policy_api.policy.models.crmp_policy_base import PolicyBase
from core_models.models import Status
import datetime

# Check policies that should be expired
expired_policies = PolicyBase.objects.filter(policy_expiry_date__lt=datetime.date.today())
print(f'Policies that should be EXPIRED: {expired_policies.count()}')

# Check current status distribution
from django.db.models import Count
status_counts = PolicyBase.objects.values('status__name').annotate(count=Count('id'))
for status in status_counts:
    print(f'{status[\"status__name\"]}: {status[\"count\"]}')
"
```

### Monitoring
```bash
# Check if Celery Beat is running
ps aux | grep celery

# Check recent logs for task execution
tail -f /path/to/your/logs/django.log | grep "policy status"

# Monitor database changes
watch -n 60 "mysql -u user -p database -e 'SELECT COUNT(*) as total, status_id FROM crmp_policy_base GROUP BY status_id;'"
```

## Next Steps

1. **Run the manual test** to see if the task works at all
2. **Check your deployment** to ensure Celery Beat is running
3. **Consider switching to Kubernetes CronJob** for better control
4. **Monitor the logs** to see if tasks are being triggered
5. **Check database** to verify if any updates are happening

The most likely issue is that Celery Beat is not running in your QA/production environment, even though the configuration is correct.
