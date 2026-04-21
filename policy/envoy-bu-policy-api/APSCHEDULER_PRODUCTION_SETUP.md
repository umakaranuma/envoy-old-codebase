# Django APScheduler Setup for Production

## Overview
This setup replaces Celery Beat with Django APScheduler for production task scheduling. The original Celery tasks are preserved and wrapped for APScheduler execution.

## What's Been Implemented

### 1. **Dependencies Added**
- `django-apscheduler` added to `requirements.txt`
- Added to `INSTALLED_APPS` in settings

### 2. **APScheduler Configuration**
- **Settings**: `envoy_bu_policy_api/settings/base.py`
- **Tasks**: `envoy_bu_policy_api/policy/apscheduler_tasks.py`
- **Management Commands**: `test_apscheduler_tasks.py`, `run_apscheduler.py`

### 3. **Scheduled Tasks**
- **Policy Status Update**: Every 12 hours
- **Credit Age Update**: Daily (24 hours)

## Production Deployment Options

### Option 1: Management Command (Recommended)
```bash
# Run the scheduler in production
python manage.py run_apscheduler

# Test tasks manually
python manage.py test_apscheduler_tasks --task=both
```

### Option 2: Systemd Service
Create `/etc/systemd/system/apscheduler.service`:
```ini
[Unit]
Description=Django APScheduler
After=network.target

[Service]
Type=simple
User=your-app-user
Group=your-app-group
WorkingDirectory=/path/to/envoy-bu-policy-api
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python manage.py run_apscheduler
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
systemctl daemon-reload
systemctl enable apscheduler
systemctl start apscheduler
systemctl status apscheduler
```

### Option 3: Docker Container
Add to your `docker-compose.yml`:
```yaml
services:
  apscheduler:
    build: .
    command: python manage.py run_apscheduler
    volumes:
      - .:/app
    depends_on:
      - db
    restart: unless-stopped
```

### Option 4: Kubernetes Deployment
Create `k8s-apscheduler-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: apscheduler
  namespace: your-namespace
spec:
  replicas: 1
  selector:
    matchLabels:
      app: apscheduler
  template:
    metadata:
      labels:
        app: apscheduler
    spec:
      containers:
      - name: apscheduler
        image: your-app-image:latest
        command:
        - python
        - manage.py
        - run_apscheduler
        env:
        - name: DJANGO_SETTINGS_MODULE
          value: "envoy_bu_policy_api.settings.production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "200m"
```

## Testing Commands

### Test Individual Tasks
```bash
# Test policy status update only
python manage.py test_apscheduler_tasks --task=policy-status

# Test credit age update only
python manage.py test_apscheduler_tasks --task=credit-age

# Test both tasks
python manage.py test_apscheduler_tasks --task=both
```

### Test Scheduler
```bash
# Test scheduler (runs jobs once and exits)
python manage.py run_apscheduler --test

# Run scheduler in production mode
python manage.py run_apscheduler
```

## Monitoring

### Check Task Execution
```bash
# Check policy statuses
python manage.py check_policy_statuses

# Check recent updates
python manage.py check_policy_statuses --detailed
```

### Log Monitoring
```bash
# Monitor APScheduler logs
tail -f /var/log/django/app.log | grep -i "apscheduler"

# Monitor task execution
tail -f /var/log/django/app.log | grep -i "policy status update"
```

## Configuration Details

### Settings Configuration
```python
# APScheduler settings in base.py
APSCHEDULER_DATETIME_FORMAT = "N j, Y, f:s a"
APSCHEDULER_RUN_NOW_TIMEOUT = 25
SCHEDULER_DEFAULT = True

APSCHEDULER_JOB_DEFAULTS = {
    'coalesce': False,
    'max_instances': 1,
    'misfire_grace_time': 15,
}
```

### Task Schedule
- **Policy Status Update**: Every 12 hours (43200 seconds)
- **Credit Age Update**: Every 24 hours (86400 seconds)
- **Misfire Grace Time**: 5 minutes (300 seconds)
- **Max Instances**: 1 (prevents overlapping executions)

## Migration from Celery Beat

### What's Preserved
- ✅ Original Celery tasks (`envoy_bu_policy_api/policy/tasks.py`)
- ✅ Celery configuration (for manual execution)
- ✅ Task logic and functionality

### What's Changed
- ❌ Celery Beat scheduling (replaced with APScheduler)
- ✅ APScheduler wrapper functions
- ✅ New management commands
- ✅ Production-ready deployment options

## Troubleshooting

### Common Issues

1. **Task Not Running**
   ```bash
   # Check if scheduler is running
   ps aux | grep "run_apscheduler"
   
   # Test tasks manually
   python manage.py test_apscheduler_tasks --task=both
   ```

2. **Database Connection Issues**
   ```bash
   # Test database connection
   python manage.py shell -c "from django.db import connection; connection.ensure_connection()"
   ```

3. **Permission Issues**
   ```bash
   # Fix permissions
   chown -R app-user:app-group /path/to/envoy-bu-policy-api
   ```

### Log Analysis
```bash
# Check for errors
grep -i "error" /var/log/django/app.log | grep -i apscheduler

# Check task execution times
grep -i "policy status update" /var/log/django/app.log | tail -10
```

## Benefits Over Celery Beat

1. **No Redis Dependency**: Works without message broker
2. **Simpler Deployment**: Single process, no separate beat process
3. **Better Integration**: Native Django integration
4. **Easier Monitoring**: Standard Django logging
5. **Database Persistence**: Jobs stored in Django database

## Quick Start for DevOps

1. **Install Dependencies**:
   ```bash
   pip install django-apscheduler
   ```

2. **Test Tasks**:
   ```bash
   python manage.py test_apscheduler_tasks --task=both
   ```

3. **Deploy Scheduler**:
   ```bash
   # Option A: Direct command
   python manage.py run_apscheduler
   
   # Option B: Systemd service
   systemctl start apscheduler
   
   # Option C: Docker
   docker-compose up apscheduler
   ```

4. **Monitor**:
   ```bash
   # Check status
   python manage.py check_policy_statuses
   
   # Monitor logs
   tail -f /var/log/django/app.log
   ```

## Expected Results

After deployment, you should see:
- ✅ Scheduler process running
- ✅ Tasks executing every 12/24 hours
- ✅ Policy statuses updating automatically
- ✅ Log messages confirming task execution

The system will automatically:
- Update EXPIRED policies (past expiry date)
- Update DUE_FOR_RENEWAL policies (within 30 days of expiry)
- Update credit ages for all policies
