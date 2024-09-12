from django.db import models
# from django_starter.storage_backends import PublicMediaStorage, PrivateMediaStorage
from django_starter.models import AbstractBaseModel

class PublicFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/public/')

    def __str__(self):
        return self.title


class PrivateFile(models.Model):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/private/')

    def __str__(self):
        return self.title