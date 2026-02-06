# Django Starter Architecture - Service Dependencies

## Current Issue: Why Celery Tasks Don't Work

```
┌─────────────────────────────────────────────────────────────────┐
│  WHAT YOU'RE CURRENTLY RUNNING                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Terminal:                                                       │
│  $ python manage.py runserver 8001                              │
│                                                                  │
│  ┌──────────────────────┐                                       │
│  │  Django Server       │  ✅ Running                           │
│  │  (port 8001)         │                                       │
│  └──────────────────────┘                                       │
│           │                                                      │
│           │ Queues tasks to Redis                               │
│           ▼                                                      │
│  ┌──────────────────────┐                                       │
│  │      Redis           │  ✅ Running (external)                │
│  │  Message Broker      │                                       │
│  └──────────────────────┘                                       │
│           │                                                      │
│           │ Tasks waiting... ⏳                                  │
│           ▼                                                      │
│  ┌──────────────────────┐                                       │
│  │  Celery Worker       │  ❌ NOT RUNNING                       │
│  │  (Process tasks)     │                                       │
│  └──────────────────────┘                                       │
│                                                                  │
│  RESULT: Tasks stay in PENDING forever!                         │
│          Progress bar never moves!                              │
└─────────────────────────────────────────────────────────────────┘
```

## What You NEED to Run

```
┌─────────────────────────────────────────────────────────────────┐
│  COMPLETE SETUP - ALL SERVICES                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Run this:                                                       │
│  $ ./start_dev.sh                                               │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                                                            │ │
│  │  ┌──────────────────┐      ┌──────────────────┐          │ │
│  │  │ Django Server    │      │ Celery Worker    │          │ │
│  │  │ (port 8001)      │◄────►│ Process Tasks    │          │ │
│  │  │                  │      │                  │          │ │
│  │  │ • Handles HTTP   │      │ • Executes       │          │ │
│  │  │ • WebSockets     │      │   long_running   │          │ │
│  │  │ • Queues tasks   │      │ • Updates        │          │ │
│  │  │                  │      │   progress       │          │ │
│  │  └──────────────────┘      └──────────────────┘          │ │
│  │           │                          │                    │ │
│  │           └──────────┬───────────────┘                    │ │
│  │                      │                                    │ │
│  │                      ▼                                    │ │
│  │           ┌──────────────────┐                           │ │
│  │           │      Redis       │                           │ │
│  │           │  Message Broker  │                           │ │
│  │           │   + Cache        │                           │ │
│  │           └──────────────────┘                           │ │
│  │                      │                                    │ │
│  │                      │                                    │ │
│  │                      ▼                                    │ │
│  │           ┌──────────────────┐                           │ │
│  │           │     Flower       │                           │ │
│  │           │   (port 8054)    │                           │ │
│  │           │   Monitoring     │                           │ │
│  │           └──────────────────┘                           │ │
│  │                                                            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  RESULT: ✅ Tasks execute                                       │
│          ✅ Progress updates in real-time                       │
│          ✅ Monitoring available                                │
└─────────────────────────────────────────────────────────────────┘
```

## How Tasks Flow

```
User clicks "Start Task" button
         │
         ▼
┌────────────────────────┐
│  Django View           │
│  start_task()          │
│                        │
│  task = long_running   │
│         _task.delay()  │
└────────────────────────┘
         │
         │ Returns task_id immediately
         │
         ▼
┌────────────────────────┐
│  Redis Broker          │
│  Task queued           │
│  Status: PENDING       │
└────────────────────────┘
         │
         │ ❌ If no Celery worker:
         │    Task stays here forever!
         │
         │ ✅ If Celery worker running:
         │    Task picked up immediately
         │
         ▼
┌────────────────────────┐
│  Celery Worker         │
│  Processes task        │
│                        │
│  for i in range(100):  │
│    progress.set(i)     │
│    time.sleep(0.1)     │
└────────────────────────┘
         │
         │ Updates progress via WebSocket
         │
         ▼
┌────────────────────────┐
│  WebSocket Connection  │
│  /ws/progress/task_id/ │
│                        │
│  Pushes updates to     │
│  browser               │
└────────────────────────┘
         │
         ▼
┌────────────────────────┐
│  Browser               │
│  Progress bar updates  │
│  0% → 50% → 100%       │
└────────────────────────┘
```

## Service Startup Options

### Option 1: Development Script (Recommended)
```bash
./start_dev.sh
```

**Starts:**
- Django dev server (foreground)
- Celery worker (background)
- Flower (background)

### Option 2: Manual (Educational)
```bash
# Terminal 1
celery -A django_starter worker -l info

# Terminal 2
celery -A django_starter flower --port=8054

# Terminal 3
python manage.py runserver 8001
```

### Option 3: Supervisor (Production-like)
```bash
./start_all_services.sh
```

**Starts:**
- Daphne (ASGI server)
- Celery worker
- Flower
(All managed by supervisord)

## Quick Diagnostic

**Is Celery worker running?**
```bash
ps aux | grep celery
# Should show celery worker process

celery -A django_starter inspect active
# Should show active workers
```

**Check via Flower:**
```
Open http://localhost:8054
Look for workers in dashboard
```

**Test a task:**
```bash
python manage.py shell

>>> from django_starter.tasks import demo_task
>>> result = demo_task.delay()
>>> result.id
'abc123...'
>>> result.status
'SUCCESS'  # If worker is running
'PENDING'  # If worker is NOT running
```

## Summary

**Key Takeaway:**

```
Django Server ALONE = ❌ Tasks don't execute
Django + Celery Worker = ✅ Full functionality
```

Always use `./start_dev.sh` for development to ensure all services are running!
