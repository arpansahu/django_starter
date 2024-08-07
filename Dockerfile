FROM python:3.10.7

WORKDIR /app

COPY requirements.txt requirements.txt

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8016

CMD bash -c "python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8016 django_starter.wsgi"