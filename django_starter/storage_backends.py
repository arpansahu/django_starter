from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = settings.AWS_STATIC_LOCATION
    addressing_style = getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'auto')
    signature_version = getattr(settings, 'AWS_S3_SIGNATURE_VERSION', 's3v4')
    verify = getattr(settings, 'AWS_S3_VERIFY', True)

class PublicMediaStorage(S3Boto3Storage):
    location = settings.AWS_PUBLIC_MEDIA_LOCATION
    file_overwrite = False
    addressing_style = getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'auto')
    signature_version = getattr(settings, 'AWS_S3_SIGNATURE_VERSION', 's3v4')
    verify = getattr(settings, 'AWS_S3_VERIFY', True)

class ProtectedMediaStorage(S3Boto3Storage):
    """Files accessible only to authenticated users"""
    location = settings.AWS_PROTECTED_MEDIA_LOCATION
    file_overwrite = False
    addressing_style = getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'auto')
    signature_version = getattr(settings, 'AWS_S3_SIGNATURE_VERSION', 's3v4')
    verify = getattr(settings, 'AWS_S3_VERIFY', True)

class PrivateMediaStorage(S3Boto3Storage):
    """Files accessible only to specific users (with signed URLs)"""
    location = settings.AWS_PRIVATE_MEDIA_LOCATION
    default_acl = 'private'
    file_overwrite = False
    custom_domain = False
    querystring_auth = True  # Enable signed URLs
    querystring_expire = 3600  # URLs expire in 1 hour
    addressing_style = getattr(settings, 'AWS_S3_ADDRESSING_STYLE', 'auto')
    signature_version = getattr(settings, 'AWS_S3_SIGNATURE_VERSION', 's3v4')
    verify = getattr(settings, 'AWS_S3_VERIFY', True)