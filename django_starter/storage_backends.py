# storage_backends.py
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = settings.AWS_STATIC_LOCATION
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME  # Ensure the correct bucket name is passed

class PublicMediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME  # Ensure the correct bucket name is passed
    file_overwrite = False

class PrivateMediaStorage(S3Boto3Storage):
    location = settings.PRIVATE_MEDIA_LOCATION
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME  # Ensure the correct bucket name is passed
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
