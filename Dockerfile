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

# Copy supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose necessary ports
EXPOSE 8016 8054

# Start supervisord to manage the processes
# Note: For Kubernetes deployments, migrations are handled by Jenkins (see Jenkinsfile-deploy)
#       For Docker Compose deployments, migrations run here on container startup
CMD python manage.py migrate --noinput && python manage.py collectstatic --noinput && supervisord -c /etc/supervisor/conf.d/supervisord.conf
