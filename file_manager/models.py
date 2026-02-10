from django.db import models
from django_starter.storage_backends import PublicMediaStorage, ProtectedMediaStorage, PrivateMediaStorage
from django_starter.models import AbstractBaseModel

class PublicFile(models.Model):
    """Files accessible to everyone (no authentication needed)"""
    title = models.CharField(max_length=255)
    file = models.FileField(storage=PublicMediaStorage, upload_to='documents/public/')

    def __str__(self):
        return self.title


class ProtectedFile(models.Model):
    """Files accessible only to authenticated users"""
    title = models.CharField(max_length=255)
    file = models.FileField(storage=ProtectedMediaStorage, upload_to='documents/protected/')
    uploaded_by = models.ForeignKey('user_account.Account', on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class PrivateFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(storage=PrivateMediaStorage, upload_to='documents/private/')

    def __str__(self):
        return self.title
    
    def get_signed_url(self, expiration=3600):
        """
        Generate a pre-signed URL for private file access
        expiration: URL validity in seconds (default 1 hour)
        """
        from botocore.exceptions import ClientError
        try:
            url = self.file.storage.url(self.file.name, parameters={'ResponseContentDisposition': f'inline; filename="{self.title}"'})
            return url
        except ClientError as e:
            return None