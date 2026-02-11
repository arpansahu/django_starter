Installing Pre requisites
```bash
  pip install -r requirements.txt
```

Create .env File and don't forget to add .env to gitignore
```bash
  cp env.example .env
  # Edit .env and add your values for all required variables
```

### Required Environment Variables

```bash
# Core
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=*
DOMAIN=localhost:8016
PROTOCOL=http

# Database
DATABASE_URL=postgres://user:pass@localhost:5432/django_starter

# Redis (used for cache, Celery broker, and Channels layer)
REDIS_CLOUD_URL=redis://localhost:6379

# Email (Mailjet)
MAIL_JET_API_KEY=your-mailjet-api-key
MAIL_JET_API_SECRET=your-mailjet-api-secret

# Storage (S3/MinIO)
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
BUCKET_TYPE=MINIO
USE_S3=True

# Social Authentication (OAuth) — all optional, only configure providers you need
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GITHUB_CLIENT_ID=
GITHUB_CLIENT_SECRET=
FACEBOOK_APP_ID=
FACEBOOK_APP_SECRET=
TWITTER_API_KEY=
TWITTER_API_SECRET=
LINKEDIN_CLIENT_ID=
LINKEDIN_CLIENT_SECRET=

# Elasticsearch (optional)
ELASTICSEARCH_HOST=https://localhost:9200
ELASTICSEARCH_USER=elastic
ELASTICSEARCH_PASSWORD=

# Kafka (optional)
KAFKA_BOOTSTRAP_SERVERS=
KAFKA_SECURITY_PROTOCOL=SASL_SSL
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=
KAFKA_SASL_PASSWORD=

# RabbitMQ (optional)
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Sentry (optional)
SENTRY_DSH_URL=
SENTRY_ENVIRONMENT=development

# Flower (Celery monitoring)
FLOWER_ADMIN_USERNAME=admin
FLOWER_ADMIN_PASS=admin
```

Making Migrations and Migrating them.
```bash
  python manage.py makemigrations
  python manage.py migrate
```

Creating Super User
```bash
  python manage.py createsuperuser
```

### Setting up Social Authentication (OAuth)

Configure OAuth callback URLs in each provider's developer console:

| Provider | Callback URL |
|----------|-------------|
| Google | `http://localhost:8016/accounts/google/login/callback/` |
| GitHub | `http://localhost:8016/accounts/github/login/callback/` |
| Facebook | `http://localhost:8016/accounts/facebook/login/callback/` |
| Twitter/X | `http://localhost:8016/accounts/twitter/login/callback/` |
| LinkedIn | `http://localhost:8016/accounts/linkedin_oauth2/login/callback/` |

For production, replace `http://localhost:8016` with `https://yourdomain.com`.

See `docs/OAUTH_SETUP.md` for detailed setup instructions for each provider.

Installing Redis On Local (For ubuntu) for other Os Please refer to their website https://redis.io/
```bash
  curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
  sudo apt-get update
  sudo apt-get install redis
  sudo systemctl restart redis.service
```
to check if its running or not
```bash
  sudo systemctl status redis
```

Run Server (choose one)
```bash
  # Development server (no WebSocket support)
  python manage.py runserver 8016

  # ASGI server with WebSocket support (recommended for real-time features)
  daphne -b 127.0.0.1 -p 8016 django_starter.asgi:application

  # Production WSGI server
  gunicorn --bind 0.0.0.0:[PROJECT_DOCKER_PORT] [JENKINS PROJECT NAME].wsgi
```

Run Celery Worker (for background tasks)
```bash
  celery -A django_starter worker -l info
```

Run Flower (Celery monitoring dashboard)
```bash
  celery -A django_starter flower --port=8054
```

Verify All Services
```bash
  python manage.py test_all_services
```

Use these CACHE settings

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_CLOUD_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

[STATIC_FILES]

## Custom Django Management Commands

[DJANGO_COMMANDS]