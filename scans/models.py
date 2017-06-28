from __future__ import unicode_literals

from django.db import models
from django.utils import timezone


class Collection(models.Model):
    owner = models.ForeignKey('auth.User')
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    storage_size = models.IntegerField(null=True)
    number_uploads = models.IntegerField(null=True)
    created_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

class Filexml(models.Model):
    owner_file = models.ForeignKey(Collection, on_delete=models.CASCADE)
    file_xml = models.FileField(upload_to="documents/")
    file_size = models.IntegerField(null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)

class Host(models.Model):
    owner_host = models.ForeignKey(Collection, on_delete=models.CASCADE)

    ip = models.CharField(max_length=15)
    hostname = models.TextField(null=True)
    so = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    organization = models.TextField(null=True)
    isp = models.TextField(null=True)
    traceroute = models.TextField(null=True)
    file_id = models.IntegerField(null=True)

    def __str__(self):
        return self.ip

class Port(models.Model):
    ip = models.ForeignKey(Host, on_delete=models.CASCADE)
    port = models.IntegerField()
    protocol = models.CharField(max_length=3)
    status = models.CharField(max_length=8)
    service = models.CharField(max_length=100)
    banner = models.TextField(null=True)

