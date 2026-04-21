# APScheduler Auto-Start Setup - Production Ready

## ✅ **SOLUTION: Safe BackgroundScheduler Auto-Start**

The scheduler now **automatically starts with Django** - no separate process needed!

## 🎯 **How It Works**

1. **Environment Variable Control**: `APSCHEDULER_AUTO_START=true`
2. **Auto-Start**: BackgroundScheduler starts when Django loads
3. **Safety**: Only starts if enabled, prevents double-start
4. **Non-Blocking**: Uses BackgroundScheduler (doesn't block Django)

## 🚀 **Production Deployment**

### **Step 1: Set Environment Variable**
```bash
# In your production environment
export APSCHEDULER_AUTO_START=true

# Or in Docker
ENV APSCHEDULER_AUTO_START=true

# Or in Kubernetes
env:
- name: APSCHEDULER_AUTO_START
  value: "true"
```

### **Step 2: Run Database Migration**
```bash
python manage.py migrate django_apscheduler
```

### **Step 3: Deploy Normally**
```bash
# Just start your Django app normally
python manage.py runserver
# OR
gunicorn envoy_bu_policy_api.wsgi:application
# OR
docker-compose up
```

**That's it!** The scheduler will start automatically.

## 📋 **Verification Commands**

### **Check Scheduler Status**
```bash
python manage.py check_apscheduler
```

**Expected Output:**
```
=== APScheduler Status Check ===

1. Configuration Check:
   Auto-start enabled: True
   ✓ APScheduler will start automatically with Django

2. Scheduler Status:
   ✓ Scheduler is running
   Active jobs: 2
     - Update Policy Statuses (ID: policy_status_update)
     - Update Credit Ages (ID: credit_age_update)
```

### **Test Tasks**
```bash
python manage.py test_apscheduler_tasks --task=both
```

### **Check Policy Statuses**
```bash
python manage.py check_policy_statuses
```

## 🔧 **Configuration Details**

### **Environment Variables**
- `APSCHEDULER_AUTO_START=true` - Enable auto-start
- `APSCHEDULER_AUTO_START=false` - Disable auto-start (default)

### **Scheduled Tasks**
- **Policy Status Update**: Every 12 hours
- **Credit Age Update**: Daily (24 hours)

### **Safety Features**
- ✅ Only starts if environment variable is set
- ✅ Prevents multiple scheduler instances
- ✅ Non-blocking BackgroundScheduler
- ✅ Graceful error handling
- ✅ Database persistence

## 📊 **What Happens Automatically**

1. **Django Starts** → PolicyConfig.ready() called
2. **Check Environment** → APSCHEDULER_AUTO_START=true?
3. **Create Scheduler** → BackgroundScheduler with jobs
4. **Start Scheduler** → Runs in background
5. **Execute Tasks** → Every 12/24 hours automatically

## 🎯 **Benefits**

- ✅ **No Separate Process**: Runs with Django
- ✅ **No Manual Commands**: Starts automatically
- ✅ **Production Ready**: Safe and reliable
- ✅ **Easy Deployment**: Just set environment variable
- ✅ **Monitoring**: Standard Django logging

## 🚨 **Important Notes**

### **Environment Variable Required**
```bash
# MUST set this in production
export APSCHEDULER_AUTO_START=true
```

### **Database Migration Required**
```bash
# Run this once
python manage.py migrate django_apscheduler
```

### **Single Instance Only**
- Only one Django instance should have auto-start enabled
- In multi-instance deployments, enable on one instance only

##  **Troubleshooting**

### **Scheduler Not Starting**
```bash
# Check environment variable
echo $APSCHEDULER_AUTO_START

# Check logs
tail -f /var/log/django/app.log | grep -i apscheduler
```

### **Database Issues**
```bash
# Check if tables exist
python manage.py shell -c "from django_apscheduler.models import DjangoJob; print(DjangoJob.objects.count())"
```

### **Manual Control**
```bash
# Start manually
python manage.py check_apscheduler --start

# Stop manually
python manage.py check_apscheduler --stop
```

## 📞 **For DevOps Team**

### **Quick Setup**
1. Set `APSCHEDULER_AUTO_START=true` in environment
2. Run `python manage.py migrate django_apscheduler`
3. Deploy Django app normally
4. Verify with `python manage.py check_apscheduler`

### **No Additional Commands Needed**
- ❌ No `python manage.py run_apscheduler`
- ❌ No separate process management
- ❌ No systemd services
- ✅ Just set environment variable and deploy!

## 🎉 **Result**

Your scheduled tasks will now run automatically:
- **Policy Status Update**: Every 12 hours
- **Credit Age Update**: Daily
- **No manual intervention required**
- **Runs with your Django application**
