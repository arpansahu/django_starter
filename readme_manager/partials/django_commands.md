### Service Health Check Commands

1. **test_all_services** — Run all service health checks for the Django Starter application.
```bash
python manage.py test_all_services
```

2. **test_db** — Test if the database is working properly by performing CRUD operations.
```bash
python manage.py test_db
```

3. **test_cache** — Test if the caching system (Redis) is working correctly with set/get operations and expiration validation.
```bash
python manage.py test_cache
```

4. **test_email** — Test if the email service (MailJet) is configured and working properly.
```bash
python manage.py test_email
```

5. **test_storage** — Test if MinIO/S3 storage is working properly.
```bash
python manage.py test_storage
```

6. **test_elasticsearch** — Test if Elasticsearch is working properly.
```bash
python manage.py test_elasticsearch
```

7. **test_kafka** — Test if Kafka is working properly.
```bash
python manage.py test_kafka
```

8. **test_rabbitmq** — Test if RabbitMQ is working properly.
```bash
python manage.py test_rabbitmq
```

9. **test_celery** — Test if Celery is working properly.
```bash
python manage.py test_celery
```

10. **test_flower** — Test if Flower (Celery monitoring) is accessible.
```bash
python manage.py test_flower
```

11. **test_harbor** — Test if Harbor Docker Registry is working properly.
```bash
python manage.py test_harbor
```

### Commands App — Management Commands Dashboard

12. **send_notifications** — Send notifications via email, SMS, or webhook.
```bash
python manage.py send_notifications
```

13. **health_check** — Perform comprehensive system health checks.
```bash
python manage.py health_check
```

14. **run_scheduled_tasks** — Run scheduled tasks that are due for execution.
```bash
python manage.py run_scheduled_tasks
```

15. **generate_report** — Generate reports from command execution data.
```bash
python manage.py generate_report
```

16. **collect_metrics** — Collect system metrics and store them in the database.
```bash
python manage.py collect_metrics
```

17. **cleanup_old_data** — Clean up old data based on retention policies.
```bash
python manage.py cleanup_old_data
```

18. **import_data** — Import data from CSV, JSON, or API sources.
```bash
python manage.py import_data
```

19. **export_data** — Export data to CSV, JSON, or Excel formats.
```bash
python manage.py export_data
```