# APScheduler Logging Configuration Guide

## 📊 **Current Setup: File-Only Logging**

The task logs are now configured to write **only to files**, not to the terminal console.

### **What You See:**
- ✅ **Terminal**: Clean output with only Django startup logs and command results
- ✅ **File**: All task execution details in `logs/task_execution.log`
- ✅ **No Spam**: Task logs don't clutter your terminal

## 🔧 **Logging Configuration Options**

### **Current: File-Only Logging**
```python
'policy_tasks': {
    'handlers': ['task_file'],  # File only - no console
    'level': 'INFO',
    'propagate': False,
},
'apscheduler_tasks': {
    'handlers': ['task_file'],  # File only - no console
    'level': 'INFO',
    'propagate': False,
},
```

### **Alternative: Console + File Logging**
If you want logs in both terminal AND file:
```python
'policy_tasks': {
    'handlers': ['task_file', 'console'],  # Both file and console
    'level': 'INFO',
    'propagate': False,
},
'apscheduler_tasks': {
    'handlers': ['task_file', 'console'],  # Both file and console
    'level': 'INFO',
    'propagate': False,
},
```

### **Alternative: Console-Only Logging**
If you want logs only in terminal:
```python
'policy_tasks': {
    'handlers': ['console'],  # Console only - no file
    'level': 'INFO',
    'propagate': False,
},
'apscheduler_tasks': {
    'handlers': ['console'],  # Console only - no file
    'level': 'INFO',
    'propagate': False,
},
```

## 📁 **Log File Locations**

- **Task Execution Logs**: `logs/task_execution.log`
- **Django Logs**: `logs/django.log`

##  **Monitoring Commands**

### **View Logs in Real-Time**
```bash
# Windows PowerShell
Get-Content logs\task_execution.log -Wait -Tail 10

# Windows CMD
type logs\task_execution.log
```

### **Filter Logs**
```bash
# Find task starts
findstr "TASK_START" logs\task_execution.log

# Find task results
findstr "TASK_RESULT" logs\task_execution.log

# Find errors
findstr "TASK_FAILED" logs\task_execution.log
```

## 🎯 **Benefits of File-Only Logging**

1. **Clean Terminal**: No log spam in your development console
2. **Persistent Logs**: All task history saved to files
3. **Better Monitoring**: DevOps can monitor logs separately
4. **Performance**: No console I/O overhead during task execution
5. **Log Rotation**: Files can be rotated and archived

## 📊 **Log Format in Files**

```
[INFO] 2025-10-17 11:04:09,687 - [TASK_START] policy_status_update_20251017_110409 - Policy Status Update Task Started
[INFO] 2025-10-17 11:04:09,687 - [TASK_INFO] policy_status_update_20251017_110409 - Start Time: 2025-10-17T11:04:09.687847
[INFO] 2025-10-17 11:04:09,688 - [TASK_STEP] policy_status_update_20251017_110409 - Step 1: Ensuring required statuses exist
[INFO] 2025-10-17 11:04:10,020 - [TASK_SUCCESS] policy_status_update_20251017_110409 - Policy Status Update Completed Successfully
[INFO] 2025-10-17 11:04:10,020 - [TASK_RESULT] policy_status_update_20251017_110409 - Results: 317 expired, 22 due for renewal
[INFO] 2025-10-17 11:04:10,020 - [TASK_TIMING] policy_status_update_20251017_110409 - Duration: 0.33 seconds
[INFO] 2025-10-17 11:04:10,020 - [TASK_END] policy_status_update_20251017_110409 - End Time: 2025-10-17T11:04:10.020523
```

## ✅ **Summary**

**Current Configuration**: Task logs go to files only, keeping your terminal clean while providing comprehensive logging for DevOps monitoring.

**To Change**: Modify the `handlers` in `envoy_bu_policy_api/settings/base.py` as shown above.
