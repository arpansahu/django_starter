# Service Health Checks

Comprehensive health monitoring for all Django Starter services.

## Overview

This app provides management commands to verify that all critical infrastructure services are operational:

- **Database** (PostgreSQL) - CRUD operations
- **Cache** (Redis) - Read/write/expiration
- **Celery** - Workers and task queue
- **Flower** - Monitoring dashboard
- **Storage** (MinIO/S3) - File operations

## Quick Start

### Run All Health Checks
```bash
python manage.py test_all_services
```

### Individual Service Checks

**Database**
```bash
python manage.py test_db
```
Verifies PostgreSQL connectivity and CRUD operations.

**Cache**
```bash
python manage.py test_cache
```
Tests Redis cache with set/get/expiration/cleanup (includes 12-second wait for expiration test).

**Celery**
```bash
python manage.py test_celery
```
Checks Celery workers, broker connectivity, and task queuing.

**Flower**
```bash
python manage.py test_flower
# Or with custom URL
python manage.py test_flower --url http://flower.example.com:5555
```
Verifies Flower monitoring dashboard accessibility.

**Storage**
```bash
python manage.py test_storage
```
Tests MinIO/S3 storage backends (public, private, static) with read/write/delete operations.

## Health Check Output

### Success Example
```
======================================================================
Starting All Service Health Checks
======================================================================

----------------------------------------------------------------------
Testing: Database (PostgreSQL)
----------------------------------------------------------------------
✓ Successfully created test entry
✓ Successfully retrieved test entry
✓ Successfully updated test entry
✓ Successfully deleted test entry
Database test completed successfully

----------------------------------------------------------------------
Testing: Cache (Redis)
----------------------------------------------------------------------
✓ Initial cache set: test_value
✓ Cache has expired as expected
✓ Cache is working correctly

======================================================================
Health Check Summary
======================================================================
Database (PostgreSQL)..................... ✅ PASSED
Cache (Redis)............................. ✅ PASSED
Celery Workers............................ ✅ PASSED
Storage (MinIO/S3)........................ ✅ PASSED
Flower Monitoring......................... ⚠️  WARNING
======================================================================

🎉 All services are healthy!
```

### Warning/Failure Indicators
- ✅ **PASSED** - Service is fully operational
- ⚠️  **WARNING** - Service accessible but with warnings (e.g., slow response, authentication required)
- ❌ **FAILED** - Service not accessible or errors occurred

## Use Cases

### Development
Run individual checks during development to verify service connectivity:
```bash
# Check if Redis is running
python manage.py test_cache

# Verify Celery workers are processing tasks
python manage.py test_celery
```

### CI/CD Pipeline
Add to Jenkins/GitHub Actions to verify environment before deployment:
```bash
# In Jenkinsfile or .github/workflows
python manage.py test_all_services
```

### Production Monitoring
Schedule regular health checks via cron or monitoring system:
```bash
# Crontab example - every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py test_all_services
```

### Pre-deployment Verification
Verify all services before going live:
```bash
# Run full health check suite
python manage.py test_all_services

# Check specific critical services
python manage.py test_db
python manage.py test_storage
```

## Test Model

The app includes a `TestModel` used for database health checks:

```python
class TestModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

This model is created/updated/deleted during `test_db` command execution and cleaned up automatically.

## Testing

The app includes 30 comprehensive tests covering:
- Model operations
- Command execution
- Service connectivity
- Error handling
- Integration scenarios

Run tests:
```bash
python manage.py test check_service_health
```

## Configuration

Health checks use existing Django settings:

**Database**
- `DATABASES['default']`

**Cache**
- `CACHES['default']` or `REDIS_CLOUD_URL`

**Celery**
- `CELERY_BROKER_URL`
- `CELERY_RESULT_BACKEND`

**Storage**
- `AWS_STORAGE_BUCKET_NAME`
- `AWS_S3_ENDPOINT_URL`
- `BUCKET_TYPE` (MINIO or AWS)

**Flower**
- Default: `http://localhost:5555`
- Override with `--url` parameter

## Troubleshooting

### Database Test Fails
```
Error: relation "check_service_health_testmodel" does not exist
```
**Solution**: Run migrations
```bash
python manage.py migrate
```

### Cache Test Fails
```
Error: Connection refused
```
**Solution**: Verify Redis is running
```bash
# Check Redis connection
redis-cli ping
# Should return: PONG
```

### Celery Test Shows "No workers"
```
Warning: No active Celery workers found
```
**Solution**: Start Celery workers
```bash
celery -A django_starter worker -l info
```

### Storage Test Fails
```
Error: Access Denied
```
**Solution**: Check AWS/MinIO credentials in settings
```bash
# Verify credentials
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

### Flower Test Connection Refused
```
Error: Connection refused. Is Flower running?
```
**Solution**: Start Flower
```bash
celery -A django_starter flower
```

## Best Practices

1. **Run before deployment** - Verify all services operational
2. **Automate in CI/CD** - Fail builds if health checks fail
3. **Monitor regularly** - Schedule periodic checks
4. **Check after updates** - Verify services after infrastructure changes
5. **Use in debugging** - Isolate service issues quickly

## Integration Examples

### Jenkins Pipeline
```groovy
stage('Health Check') {
    steps {
        sh 'python manage.py test_all_services'
    }
}
```

### GitHub Actions
```yaml
- name: Health Check
  run: python manage.py test_all_services
```

### Docker Healthcheck
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python manage.py test_db && python manage.py test_cache
```

## Future Enhancements

Potential additions:
- Email notifications on failures
- Metrics export (Prometheus format)
- Response time tracking
- Historical health data
- Web dashboard for health status
- Slack/Discord webhook integrations
