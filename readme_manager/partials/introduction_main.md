# Django Starter | Production-Ready Django Boilerplate

A comprehensive Django starter project featuring modern best practices, multiple integrations, and enterprise-ready architecture. Clone it, configure it, and start building your application immediately.

## Project Features

1. **Account Management:** Complete authentication with email verification, password reset, profile management, and account deletion.
2. **Social Authentication (OAuth):** One-click sign-in via Google, GitHub, Facebook, Twitter/X (OAuth 2.0), and LinkedIn (OpenID Connect) using django-allauth. Includes account page UI to connect/disconnect providers.
3. **Real-Time WebSocket Notifications:** Push notifications via Django Channels with toast UI, notification bell with badge, and auto-reconnecting WebSocket client.
4. **Professional HTML Email Templates:** Branded activation, welcome, password reset, and social-connected emails sent via Mailjet REST API with plain-text fallbacks.
5. **PostgreSQL Database:** Production-grade relational database with migrations and connection pooling.
6. **AWS S3/MinIO Storage:** Flexible 3-tier file storage (public/protected/private) supporting both AWS S3 and self-hosted MinIO with signed URLs.
7. **Redis Integration:** High-performance caching, session storage, Celery message broker, and Channels layer backend.
8. **MailJet Email Service:** Transactional emails via both Mailjet REST API (direct) and django-anymail backend.
9. **Docker Containerization:** Fully containerized with Docker Compose for local development.
10. **Kubernetes Deployment:** Production-ready K8s manifests with ConfigMaps, Secrets, and Rancher-compatible service definitions.
11. **CI/CD Pipeline:** Automated build, test, and deployment with Jenkins (separate build and deploy Jenkinsfiles).
12. **Notes Application:** Full-featured CRUD app demonstrating all Django Generic Class-Based Views — ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, RedirectView, and TemplateView — with categories, tags, comments, pinning, archiving, and version history.
13. **Elasticsearch Search:** Full-text search with autocomplete suggestions, analytics dashboard, index management, and cluster health monitoring.
14. **Kafka Event Streaming:** Real-time event publishing and consumption with Apache Kafka, including event dashboard and analytics views.
15. **RabbitMQ Messaging:** Priority-based message queue system for async notifications with dashboard and message history.
16. **Commands Dashboard:** Web UI for management command execution, scheduling, metrics collection, data import/export, and command log tracking — with 19 built-in management commands.
17. **REST API:** Complete Django REST Framework API with session/basic authentication, Swagger/OpenAPI docs (drf-spectacular), ReDoc, throttling, filtering, and API key management.
18. **Celery Task Queue:** Background task processing with real-time WebSocket progress tracking via custom Celery progress app and Flower monitoring.
19. **Comprehensive Testing:** Automated test generation with django-test-enforcer, Playwright UI tests, pytest with parallel execution (xdist), and full coverage reporting.
20. **Error Tracking:** Sentry integration for production error monitoring and alerting.
21. **Service Health Checks:** 11 management commands to verify database, cache, email, storage, Elasticsearch, Kafka, RabbitMQ, Celery, Flower, and Harbor connectivity.

## Why Use This Starter?

- 🚀 **Production-Ready:** Battle-tested configurations for real-world deployments
- 🔧 **Fully Configured:** All integrations pre-wired and working out of the box
- 📦 **Modular Design:** Enable/disable features based on your needs
- 🔐 **Social Auth:** 5 OAuth providers configured and ready to use
- 🧪 **Test Coverage:** Built-in testing infrastructure with 100% view coverage
- 📡 **Real-Time:** WebSocket notifications and Celery progress tracking
- 📖 **Well Documented:** Comprehensive documentation and code comments

Can be cloned and used as a base project for any Django application.