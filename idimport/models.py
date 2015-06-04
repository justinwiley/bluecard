import os
from uuid import uuid4
from django.db import models
from django.utils.deconstruct import deconstructible

@deconstructible
class PathAndRename(object):

    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

imports_path = PathAndRename("/imports")

class Customer(models.Model):
    name = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "ID %s - %s : %s" % (self.id, self.name, self.created)

class Document(models.Model):
    customer = models.ForeignKey(Customer)
    image = models.FileField(upload_to=imports_path)
    status = models.CharField(max_length=30, default='imported')
    batch_id = models.CharField(max_length=12, default=None)
    job_id = models.CharField(max_length=12, default=None)
    value1 = models.CharField(max_length=250, default=None)
    value2 = models.CharField(max_length=250, default=None)
    current = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "ID - %s status %s image %s (customer %s) - created: %s" % (self.id, self.status, self.image, self.customer_id, self.created)
