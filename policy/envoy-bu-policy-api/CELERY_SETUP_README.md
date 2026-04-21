# Celery Setup for Policy Status Updates (Production)

This setup replaces the SQL script (`UPDATE_POLICY_STATUSES.sql`) with a Celery-based scheduled task system optimized for production without Redis dependency.

## Files Created/Modified

1. **`envoy_bu_policy_api/__init__.py`** - Imports Celery app
2. **`envoy_bu_policy_api/policy/tasks.py`** - Contains scheduled tasks
3. **`envoy_bu_policy_api/settings/base.py`** - Celery configuration
4. **`envoy_bu_policy_api/management/commands/test_celery_tasks.py`** - Test command

## Tasks

### `update_policy_statuses`
- **Schedule**: Every 12 hours (43200 seconds)
- **Purpose**: Updates policy statuses based on expiry dates
- **Actions**:
  - Sets policies to `EXPIRED` if past expiry date
  - Sets policies to `DUE_FOR_RENEWAL` if within 30 days of expiry
  - Ensures required statuses exist in database
- **Logging**: Debug-level logging for production monitoring

## Production Configuration

### No Redis Required
- Uses `CELERY_TASK_ALWAYS_EAGER = True` for synchronous execution
- Tasks run directly within Django process
- No external dependencies (Redis, RabbitMQ, etc.)

### Automatic Execution
- Task runs every 12 hours automatically
- No manual intervention required
- Integrated with Django application lifecycle

## Testing

### Test Task Manually
```bash
# Test policy status update task directly
python manage.py test_celery_tasks --task=test-direct

# Test task queuing (if needed)
python manage.py test_celery_tasks --task=policy-status
```

## Production Deployment

### 1. Standard Django Deployment
```bash
# Deploy Django application normally
python manage.py migrate
python manage.py collectstatic
python manage.py runserver  # or use WSGI server
```

### 2. Task Execution
- Tasks run automatically every 12 hours
- No separate worker processes needed
- Integrated with Django application

### 3. Monitoring
- Check Django logs for task execution
- Monitor database for status updates
- Task logs include update counts and errors

## Logs

Tasks will log their progress in Django logs:
```
INFO: Starting policy status update task...
INFO: Updated 5 policies to EXPIRED status
INFO: Updated 12 policies to DUE_FOR_RENEWAL status
INFO: Policy status update completed: 5 expired, 12 due for renewal
```

## Benefits over SQL Script

1. **Production Ready**: No external dependencies
2. **Integrated**: Runs within Django application
3. **Logging**: Proper logging and error handling
4. **Maintainable**: Easy to modify schedule or add new tasks
5. **Safe**: Uses Django database connections
6. **Automated**: Runs every 12 hours without manual intervention
7. **Scalable**: Can be easily modified for different schedules

## Schedule Modification

To change the schedule, update `CELERY_BEAT_SCHEDULE` in `settings/base.py`:

```python
CELERY_BEAT_SCHEDULE = {
    "update-policy-statuses-every-12-hours": {
        "task": "envoy_bu_policy_api.policy.tasks.update_policy_statuses",
        "schedule": 43200.0,  # Change this value (seconds)
    },
}
```

Common schedule values:
- Every 6 hours: `21600.0`
- Every 12 hours: `43200.0`
- Every 24 hours: `86400.0`
- Every 2 days: `172800.0`
