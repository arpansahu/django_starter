FROM python:3.10.7

WORKDIR /app

# Copy only requirements.txt first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Install supervisord
RUN apt-get update && apt-get install -y supervisor

# Copy the rest of the application
COPY . .

# Expose necessary ports
EXPOSE 8016 8054

# Start processes
CMD python manage.py collectstatic --noinput && \
    daphne -b 0.0.0.0 -p 8016 django_starter.asgi:application & \
    celery -A django_starter.celery worker -l info -n django_starter_worker & \
    celery -A django_starter flower --port=8054