## What is Python ?
Python is a high-level, general-purpose programming language. Its design philosophy emphasizes code readability with the
use of significant indentation. Python is dynamically typed and garbage-collected. It supports multiple programming 
paradigms, including structured, object-oriented and functional programming.

## What is Django ?
Django is a Python-based free and open-source web framework that follows the model-template-view architectural pattern.

## What is Django REST Framework ?
Django REST Framework (DRF) is a powerful and flexible toolkit for building Web APIs in Django. It provides serialization, 
authentication, viewsets, routers, throttling, filtering, and pagination out of the box, making it easy to build 
RESTful APIs that follow best practices.

## What is drf-spectacular ?
drf-spectacular is an OpenAPI 3.0 schema generation library for Django REST Framework. It auto-generates Swagger UI 
and ReDoc documentation from your API views and serializers, providing interactive API documentation for developers.

## What is Redis ?
Redis is an in-memory data structure project implementing a distributed, in-memory key-value database with optional durability. 
The most common Redis use cases are session cache, full-page cache, queues, leader boards and counting, publish-subscribe, and much more. In this project, Redis is used as a cache backend, Celery message broker, and Django Channels layer.

## What is Celery ?
Celery is an asynchronous task queue/job queue based on distributed message passing. It is focused on real-time operation 
but supports scheduling as well. In this project, Celery handles background task processing with real-time WebSocket 
progress tracking via a custom progress recorder.

## What is Flower ?
Flower is a real-time web-based monitoring tool for Celery. It provides detailed information about the state of workers, 
tasks, and queues. It allows you to monitor task progress, view task details, and control worker pools from a web interface.

## What is Django Channels ?
Django Channels extends Django to handle WebSockets, HTTP2, and other protocols beyond traditional HTTP. It builds on 
ASGI (Asynchronous Server Gateway Interface) and enables real-time features like push notifications, live updates, 
and chat systems. In this project, Channels powers real-time notification delivery and Celery task progress updates.

## What is Daphne ?
Daphne is an HTTP, HTTP2, and WebSocket protocol server for ASGI and ASGI-HTTP, developed as part of the Django Channels 
project. It serves as the production-ready ASGI server for Django applications that need WebSocket support.

## What is PostgreSQL ?
PostgreSQL is a powerful, open-source object-relational database system with a strong reputation for reliability, 
feature robustness, and performance. It supports advanced data types, full-text search, and JSON storage.

## What is Elasticsearch ?
Elasticsearch is a distributed, RESTful search and analytics engine built on Apache Lucene. It provides full-text 
search, structured search, analytics, and logging capabilities. In this project, it powers the search app with 
autocomplete suggestions, index management, cluster health monitoring, and search analytics.

## What is Apache Kafka ?
Apache Kafka is an open-source distributed event streaming platform used for high-performance data pipelines, 
streaming analytics, data integration, and mission-critical applications. In this project, Kafka handles real-time 
event publishing and consumption with an event dashboard and analytics views.

## What is RabbitMQ ?
RabbitMQ is an open-source message broker that implements the Advanced Message Queuing Protocol (AMQP). It supports 
multiple messaging patterns including point-to-point, publish-subscribe, and request-reply. In this project, 
RabbitMQ powers priority-based async notifications with a dashboard and message history.

## What is MinIO ?
MinIO is a high-performance, S3-compatible object storage system. It is designed for large-scale data infrastructure 
and provides an API compatible with Amazon S3. In this project, MinIO serves as self-hosted object storage for 
public, protected, and private file uploads.

## What is Docker ?
Docker is a platform for developing, shipping, and running applications inside lightweight, portable containers. 
Containers package an application with all its dependencies, ensuring it runs consistently across different environments.

## What is Kubernetes ?
Kubernetes is an open-source container orchestration platform that automates deploying, scaling, and managing 
containerized applications. In this project, K8s manifests, ConfigMaps, Secrets, and service definitions are 
provided for production deployment.

## What is Jenkins ?
Jenkins is an open-source automation server that enables continuous integration and continuous delivery (CI/CD). 
This project includes separate Jenkinsfiles for build and deploy pipelines.

## What is Nginx ?
Nginx is a high-performance HTTP server and reverse proxy. In this project, Nginx handles SSL termination, 
HTTP-to-HTTPS redirection, WebSocket proxying, and reverse proxying to the application server.

## What is Harbor ?
Harbor is an open-source container image registry that provides role-based access control, image scanning, 
and replication. It is used in this project to store Docker images built by the CI/CD pipeline.

## What is Sentry ?
Sentry is an application monitoring platform that provides real-time error tracking and performance monitoring. 
It helps developers identify, triage, and resolve issues in production applications.

## What is django-allauth ?
django-allauth is a comprehensive Django authentication library that handles account registration, login, 
social authentication, email verification, and account management. In this project, it provides OAuth sign-in 
via Google, GitHub, Facebook, Twitter/X (OAuth 2.0), and LinkedIn (OpenID Connect), with a custom adapter 
for sending branded welcome emails and WebSocket notifications on social signup.

## What is Mailjet ?
Mailjet is a cloud-based email delivery service for sending transactional and marketing emails. In this project, 
it is used both as a direct REST API (via mailjet-rest) for custom email sends and as a Django email backend 
(via django-anymail) for allauth-triggered emails.

## What is Playwright ?
Playwright is a framework for end-to-end testing of web applications. It supports Chromium, Firefox, and 
WebKit browsers and provides APIs for automating browser interactions. In this project, Playwright is used 
for UI integration tests alongside pytest.

## What is Pytest ?
Pytest is a mature full-featured Python testing tool. It supports fixtures, parameterization, markers, and 
plugins. Combined with pytest-django, pytest-xdist (parallel execution), and coverage, it forms the testing 
backbone of this project.